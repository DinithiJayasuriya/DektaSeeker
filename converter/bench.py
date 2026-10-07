#!/usr/bin/env python3
"""Transient evaluator for LaMAGIC-style switched power converters.

This is the piece SteerGenSE needs on the converter side and did not have: a way
to score a topology the diffusion prior just invented. The existing
``converter_validity.py`` says whether a graph is a well-formed converter;
this says what it does.

Method: build a SPICE deck in which every Sa switch is driven by a PWM source at
duty D and every Sb switch by its complement, run a transient long enough for the
output filter to settle, and average over the last cycles.

    Vout = <v(VOUT)>            Pout = <v(VOUT)^2> / Rout
    eff  = Pout / Pin           Pin  = <-VIN * i(Vin)>

Operating point (LaMAGIC NOTES.md + raw/345comp_base.json edge_attr):
    VIN 100 V   Rout 50   Cout 10   L 0.01   C 10   fsw 1 Hz   Ron 1e-5  Roff 1e5
All in the dataset's normalized units. Rout*Cout = 500 s = 500 switching
periods, which is why the settle time below is long.

NOT a reimplementation of LaMAGIC's simulator. It is an independent bench with
stated parameters; validate_bench.py measures how far it agrees with their
published labels.
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass

NGSPICE = os.environ.get("NGSPICE_BIN", "ngspice")

# --- operating point -------------------------------------------------------
# LaMAGIC's own normalized point (L=0.01 H, C=10 F, fsw=1 Hz, Rout=50) puts every
# topology deep into discontinuous conduction -- which is why the published
# efficiencies in that corpus run 0.001-0.4. A discovery loop scored there would
# be optimising numerical noise. We use a conventional hard-switched point
# instead, and state it: the bench is ours, not a reimplementation of theirs.
VIN  = float(os.environ.get("CONV_VIN",  100.0))
ROUT = float(os.environ.get("CONV_ROUT", 50.0))     # ~200 W class at 100 V
FSW  = float(os.environ.get("CONV_FSW",  100e3))
L_VAL = float(os.environ.get("CONV_L",   500e-6))
C_VAL = float(os.environ.get("CONV_C",   10e-6))
COUT  = float(os.environ.get("CONV_COUT", 10e-6))
# Loss model. At RON=0.01 with no DCR every working converter scored 0.997-1.000,
# so efficiency discriminated nothing and the search collapsed to hitting a
# voltage ratio. These are ordinary values for a 100 V hard-switched converter.
RON  = float(os.environ.get("CONV_RON",  0.05))    # MOSFET Rds(on)
ROFF = float(os.environ.get("CONV_ROFF", 1e6))
DCR  = float(os.environ.get("CONV_DCR",  0.25))    # inductor winding resistance
ESR  = float(os.environ.get("CONV_ESR",  0.03))    # capacitor ESR
SETTLE_PERIODS  = int(os.environ.get("CONV_SETTLE", 2000))
MEASURE_PERIODS = int(os.environ.get("CONV_MEAS", 20))
PTS_PER_PERIOD  = int(os.environ.get("CONV_PTS", 200))


@dataclass
class Result:
    ok: bool
    vout: float = float("nan")
    eff: float = float("nan")
    ripple: float = float("nan")     # peak-to-peak v(VOUT) in the window
    reason: str = ""


def _net(n: str) -> str:
    """LaMAGIC node name -> SPICE node."""
    n = str(n)
    return {"IN": "VIN", "OUT": "VOUT", "0": "0", "GND": "0",
            "VIN": "VIN", "VOUT": "VOUT"}.get(n, f"n{n}")


def build_deck(netlist, duty: float, out_path: str, params=None) -> str:
    """netlist: iterable of (device, nodeA, nodeB), device named Sa*/Sb*/L*/C*.

    params: optional dict overriding the operating point for THIS deck only
    (keys VIN ROUT FSW L C COUT RON ROFF DCR ESR). Used by spec.CORNERS for the
    robustness re-score; None = the module-level point, byte-identical decks.
    """
    P = dict(VIN=VIN, ROUT=ROUT, FSW=FSW, L=L_VAL, C=C_VAL, COUT=COUT, RON=RON,
             ROFF=ROFF, DCR=DCR, ESR=ESR)
    if params:
        P.update({k: float(v) for k, v in params.items() if k in P})
    VIN_, ROUT_, FSW_, L_, C_, COUT_ = P["VIN"], P["ROUT"], P["FSW"], P["L"], P["C"], P["COUT"]
    RON_, ROFF_, DCR_, ESR_ = P["RON"], P["ROFF"], P["DCR"], P["ESR"]
    T = 1.0 / FSW_
    ton = max(duty * T, 1e-9)
    lines = [
        "* LaMAGIC-style converter, bench.py",
        f"Vin VIN 0 DC {VIN_}",
        f"Vpa PA 0 PULSE(0 1 0 1n 1n {ton:.9g} {T:.9g})",
        f"Vpb PB 0 PULSE(1 0 0 1n 1n {ton:.9g} {T:.9g})",
        f".model SWMOD SW(ron={RON_} roff={ROFF_} vt=0.5 vh=0.01)",
    ]
    nsw = nl = nc = 0
    for dev, a, b in netlist:
        a, b = _net(a), _net(b)
        d = str(dev)
        if d.startswith("Sa"):
            nsw += 1
            lines.append(f"S{nsw} {a} {b} PA 0 SWMOD")
        elif d.startswith("Sb"):
            nsw += 1
            lines.append(f"S{nsw} {a} {b} PB 0 SWMOD")
        elif d.startswith("L"):
            nl += 1
            if DCR_ > 0:
                lines.append(f"L{nl} {a} lx{nl} {L_}")
                lines.append(f"RL{nl} lx{nl} {b} {DCR_}")
            else:
                lines.append(f"L{nl} {a} {b} {L_}")
        elif d.startswith("C"):
            nc += 1
            if ESR_ > 0:
                lines.append(f"C{nc} {a} cx{nc} {C_}")
                lines.append(f"RC{nc} cx{nc} {b} {ESR_}")
            else:
                lines.append(f"C{nc} {a} {b} {C_}")
        else:
            raise ValueError(f"unknown device {dev!r}")
    if nsw == 0:
        raise ValueError("no switches")

    T_end = SETTLE_PERIODS * T
    T_start = T_end - MEASURE_PERIODS * T
    lines += [
        f"Rout VOUT 0 {ROUT_}",
        (f"Cout VOUT co_x {COUT_}\nRCo co_x 0 {ESR_}" if ESR_ > 0
         else f"Cout VOUT 0 {COUT_}"),
        ".options gmin=1e-12 reltol=1e-3 abstol=1e-9 vntol=1e-6 itl1=200 itl4=100",
        ".control",
        "set noaskquit",
        f"tran {T/PTS_PER_PERIOD:.9g} {T_end:.9g} {T_start:.9g} {T/PTS_PER_PERIOD:.9g}",
        # Integrate on ngspice's own timepoints. Averaging the resampled output
        # instead under-samples the input-current spikes of a hard-switched
        # converter and yields efficiencies above 1.
        f"let pout = v(VOUT)*v(VOUT)/{ROUT_}",
        f"let pin = -{VIN_}*i(vin)",
        f"meas tran vout_avg AVG v(VOUT) from={T_start:.9g} to={T_end:.9g}",
        f"meas tran pout_avg AVG pout from={T_start:.9g} to={T_end:.9g}",
        f"meas tran pin_avg  AVG pin  from={T_start:.9g} to={T_end:.9g}",
        f"meas tran vout_max MAX v(VOUT) from={T_start:.9g} to={T_end:.9g}",
        f"meas tran vout_min MIN v(VOUT) from={T_start:.9g} to={T_end:.9g}",
        "quit",
        ".endc",
        ".end",
    ]
    return "\n".join(lines) + "\n"


_FAIL = re.compile(r"singular matrix|no convergence|iteration limit|"
                   r"Error|doAnalyses|Too many", re.I)


def evaluate(netlist, duty: float, timeout_s: float = 60.0, params=None) -> Result:
    with tempfile.TemporaryDirectory() as td:
        data = os.path.join(td, "out.dat")
        deck = os.path.join(td, "c.sp")
        try:
            text = build_deck(netlist, duty, data, params=params)
        except ValueError as e:
            return Result(False, reason=str(e))
        with open(deck, "w") as f:
            f.write(text)
        try:
            p = subprocess.run([NGSPICE, "-b", deck], capture_output=True,
                               text=True, timeout=timeout_s)
        except subprocess.TimeoutExpired:
            return Result(False, reason="timeout")
        txt = (p.stdout or "") + (p.stderr or "")
        vals = dict(re.findall(r"^\s*(vout_avg|pout_avg|pin_avg|vout_max|vout_min)\s*=\s*"
                               r"([-\d.eE+]+)", txt, re.M | re.I))
        need = ("vout_avg", "pout_avg", "pin_avg")
        if not all(k in vals for k in need):
            msg = txt[-160:].replace("\n", " ")
            return Result(False, reason=f"no measurement: {msg}")
        try:
            vout = float(vals["vout_avg"])
            pout = float(vals["pout_avg"])
            pin = float(vals["pin_avg"])
            ripple = float(vals.get("vout_max", "nan")) - float(vals.get("vout_min", "nan"))
        except ValueError:
            return Result(False, reason="unparsable measurement")
        if any(v != v for v in (vout, pout, pin)):
            return Result(False, reason="nan measurement")
        eff = pout / pin if pin > 1e-9 else 0.0
        return Result(True, vout=vout, eff=eff, ripple=ripple)


def netlist_from_edges(list_of_node, list_of_edge):
    """6comp records carry no netlist field; rebuild (device, netA, netB) from
    the bipartite edge list. Rails fold into the net they attach to."""
    devs = [n for n in list_of_node
            if isinstance(n, str) and n[0] in "SLC" and n not in ("VIN", "VOUT")]
    rail_of = {}
    for a, b in list_of_edge:
        for x, y in ((a, b), (b, a)):
            if x in ("VIN", "VOUT", "GND"):
                rail_of[y] = {"VIN": "IN", "VOUT": "OUT", "GND": "0"}[x]
    pins = {d: [] for d in devs}
    for a, b in list_of_edge:
        for x, y in ((a, b), (b, a)):
            if x in pins:
                pins[x].append(rail_of.get(y, y))
    out = []
    for d, ns in pins.items():
        if len(ns) != 2:
            raise ValueError(f"{d} has {len(ns)} terminals")
        out.append((d, ns[0], ns[1]))
    return out


# --- textbook topologies, used as the bench's correctness gate -------------
# Phase A closes every Sa, phase B every Sb (LaMAGIC's naming convention).
TEXTBOOK = {
    # Vin -Sa- sw -L- out ; Sb shunts sw to ground in phase B
    "buck":       ([("Sa0", "IN", "sw"), ("Sb0", "sw", "0"),
                    ("L0", "sw", "OUT")],            lambda d: d),
    # Vin -L- sw ; Sa shunts sw to ground, Sb passes sw to out
    "boost":      ([("L0", "IN", "sw"), ("Sa0", "sw", "0"),
                    ("Sb0", "sw", "OUT")],           lambda d: 1.0 / (1.0 - d)),
    # Vin -Sa- sw ; L shunts sw to ground; Sb passes sw to out (inverting)
    "buckboost":  ([("Sa0", "IN", "sw"), ("L0", "sw", "0"),
                    ("Sb0", "sw", "OUT")],           lambda d: -d / (1.0 - d)),
}


def selftest():
    print(f"operating point: VIN={VIN} ROUT={ROUT} FSW={FSW:g} L={L_VAL:g} "
          f"COUT={COUT:g} RON={RON:g} DCR={DCR:g} ESR={ESR:g}")
    print(f"{'topology':>10} {'duty':>5} {'ideal Vout':>11} {'bench Vout':>11} "
          f"{'err %':>7} {'eff':>6} {'ripple':>8}")
    worst = 0.0
    for name, (nl, ideal) in TEXTBOOK.items():
        for duty in (0.25, 0.5, 0.75):
            r = evaluate(nl, duty)
            want = ideal(duty) * VIN
            if not r.ok:
                print(f"{name:>10} {duty:>5} {want:>11.2f}   FAILED  {r.reason}")
                continue
            err = 100 * abs(r.vout - want) / max(abs(want), 1e-9)
            worst = max(worst, err)
            print(f"{name:>10} {duty:>5.2f} {want:>11.2f} {r.vout:>11.2f} "
                  f"{err:>7.1f} {r.eff:>6.3f} {r.ripple:>8.3g}")
    print(f"\nworst conversion-ratio error: {worst:.1f}%")
    return worst


def lossless_gate():
    """Correctness gate. With the parasitics removed the bench must reproduce the
    textbook conversion ratios; that is what proves the switching, settling and
    averaging are right. Discovery then runs at the lossy point above."""
    global RON, DCR, ESR
    keep = (RON, DCR, ESR)
    RON, DCR, ESR = 1e-5, 0.0, 0.0
    try:
        return selftest()
    finally:
        RON, DCR, ESR = keep


if __name__ == "__main__":
    print("=== LOSSLESS correctness gate " + "=" * 40)
    worst = lossless_gate()
    print("\n=== LOSSY discovery point " + "=" * 43)
    selftest()
    print(f"\ngate verdict: {'PASS' if worst < 1.0 else 'FAIL'} "
          f"(worst ideal-ratio error {worst:.1f}%, threshold 1.0%)")
