#!/usr/bin/env python3
"""Task 2: is the 97 % conduction of C1 in converter (a) real, or an artifact of
the ideal-switch model?

Reported in results/conv_mech_verify/mech_verify.md, case (d) = converter (a):
    C1 | C | I_rms 1.467 A | I_peak 6.460 A | U 0.97 | P_loss 64.4 mW
and read as "new energy-transfer path: C1 is the freewheel path for L0".

The bench switch is an ngspice SW: a voltage-controlled resistor, ron 50 mOhm /
roff 1 MOhm, with NO body diode, NO Coss and no reverse blocking. Two things in
that model could manufacture the number:

  (1) roff. If the 1 MOhm off-state leakage were carrying appreciable current the
      split between Sa1 and C1 would move with roff.
  (2) no body diode. Every real switch a designer would put at Sa1 -- MOSFET or
      diode-rectifier -- has an intrinsic antiparallel diode. If that diode can
      carry the inductor current from n8 to OUT, it, not C1, is the freewheel
      path, and C1's 97 % conduction is an artifact of a device model with no
      reverse path. The LaMAGIC representation has no device polarity, so the
      topology does NOT fix which way that diode faces: both orientations are
      legal realisations of the same discovered graph and both are tested.

      The diode is added to Sa1 ONLY. Adding one to every switch in a single
      global orientation shorts IN to ground through Sa0 + the Sb0 diode, which
      is a statement about that convention, not about this circuit; leaving the
      other switches ideal keeps Sa1 the only thing that changed.

Part A re-measures the waveforms under each switch model at the child's duty.
Part B re-scores child and parent on all 4 corners under each switch model, by
monkeypatching bench.evaluate, so feasibility is judged the same way the run did.

Diode: .model D(is=1e-12 rs=0.02 n=1.5 cjo=200p) -- ~0.8 V at 1 A, an ordinary
600 V-class Si body diode.
"""
from __future__ import annotations
import os as _os, sys as _sys
_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
_sys.path.insert(0, _os.path.join(_ROOT, "converter"))
import os, sys
import os, sys, json, re, tempfile, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
import numpy as np
import bench, spec
from mech_verify import element_stats

OUT = os.path.join(_ROOT, "results", "conv_validation_0918")
os.makedirs(OUT, exist_ok=True)
NG = bench.NGSPICE
SHEET = spec.SpecSheet(eff_floor=0.9)

CHILD  = "Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8; C1 OUT n8"
PARENT = "Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8"
DUTY   = 0.5052                      # the child's refined nominal duty (mech_verify)
DMODEL = ".model DMOD D(is=1e-12 rs=0.02 n=1.5 cjo=200p)"

# switch models: (label, roff, diode orientation)
#   orient None = ideal SW, as the run used
#   orient "ab" = body diode anode at the netlist's FIRST node, cathode at the second
#   orient "ba" = the reverse. For "Sa1 OUT n8", "ba" is the one that can carry
#                 inductor current n8 -> OUT, i.e. the freewheel direction.
MODELS = {
 "ideal_roff1e6": dict(roff=1e6, diodes={},              desc="as run: ideal SW, no body diode"),
 "ideal_roff1e4": dict(roff=1e4, diodes={},              desc="ideal SW, 100x leakier off-state"),
 "ideal_roff1e9": dict(roff=1e9, diodes={},              desc="ideal SW, 1000x tighter off-state"),
 "diode_Sa1_ab":  dict(roff=1e6, diodes={"Sa1": "ab"},   desc="Sa1 is a real switch, body diode OUT->n8 (blocks the freewheel direction)"),
 "diode_Sa1_ba":  dict(roff=1e6, diodes={"Sa1": "ba"},   desc="Sa1 is a real switch, body diode n8->OUT (conducts the freewheel direction)"),
}

def parse(s): return [tuple(t.split()) for t in s.split("; ")]

# --------------------------------------------------------------------------- decks
def _sw_lines(dev, a, b, n, orient, probe):
    """Switch n with optional antiparallel body diode (orient None = none).
    probe=True inserts 0 V ammeters so switch and diode currents are separable."""
    ph = "PA" if dev.startswith("Sa") else "PB"
    L = []
    if probe:
        L += [f"S{n} {a} sx{n} {ph} 0 SWMOD", f"VS{n} sx{n} {b} 0"]
    else:
        L += [f"S{n} {a} {b} {ph} 0 SWMOD"]
    if orient:
        an, ca = (a, b) if orient == "ab" else (b, a)
        if probe:
            L += [f"D{n} {an} dx{n} DMOD", f"VD{n} dx{n} {ca} 0"]
        else:
            L += [f"D{n} {an} {ca} DMOD"]
    return L

def build(netlist, duty, model, params=None, probe=False, wr_path=None):
    P = dict(VIN=bench.VIN, ROUT=bench.ROUT, FSW=bench.FSW, L=bench.L_VAL, C=bench.C_VAL,
             COUT=bench.COUT, RON=bench.RON, ROFF=model["roff"], DCR=bench.DCR, ESR=bench.ESR)
    if params: P.update({k: float(v) for k, v in params.items() if k in P})
    T = 1.0 / P["FSW"]; ton = max(duty * T, 1e-9)
    L = ["* switch-model check", f"Vin VIN 0 DC {P['VIN']}",
         f"Vpa PA 0 PULSE(0 1 0 1n 1n {ton:.9g} {T:.9g})",
         f"Vpb PB 0 PULSE(1 0 0 1n 1n {ton:.9g} {T:.9g})",
         f".model SWMOD SW(ron={P['RON']} roff={P['ROFF']} vt=0.5 vh=0.01)", DMODEL]
    elems = []; ns = nl = nc = 0
    for dev, a, b in netlist:
        a, b = bench._net(a), bench._net(b)
        if dev.startswith("S"):
            ns += 1
            orient = model["diodes"].get(dev)
            L += _sw_lines(dev, a, b, ns, orient, probe)
            if probe:
                elems.append((dev, "S", a, b, f"i(vs{ns})"))
                if orient:
                    an, ca = (a, b) if orient == "ab" else (b, a)
                    elems.append((f"D_{dev}", "D", an, ca, f"i(vd{ns})"))
        elif dev.startswith("L"):
            nl += 1
            L += [f"L{nl} {a} lx{nl} {P['L']}", f"RL{nl} lx{nl} {b} {P['DCR']}"]
            if probe: elems.append((dev, "L", a, b, f"i(l{nl})"))
        elif dev.startswith("C"):
            nc += 1
            if probe:
                L += [f"C{nc} {a} cx{nc} {P['C']}", f"VC{nc} cx{nc} cy{nc} 0", f"RC{nc} cy{nc} {b} {P['ESR']}"]
                elems.append((dev, "C", a, b, f"i(vc{nc})"))
            else:
                L += [f"C{nc} {a} cx{nc} {P['C']}", f"RC{nc} cx{nc} {b} {P['ESR']}"]
        else:
            raise ValueError(dev)
    if ns == 0: raise ValueError("no switches")
    L.append(f"Rout VOUT 0 {P['ROUT']}")
    if probe:
        L += [f"Cout VOUT co_x {P['COUT']}", "VCo co_x co_y 0", f"RCo co_y 0 {P['ESR']}"]
    else:
        L += [f"Cout VOUT co_x {P['COUT']}", f"RCo co_x 0 {P['ESR']}"]
    T_end = bench.SETTLE_PERIODS * T; T_start = T_end - bench.MEASURE_PERIODS * T
    L.append(".options gmin=1e-12 reltol=1e-3 abstol=1e-9 vntol=1e-6 itl1=200 itl4=100")
    L += [".control", "set noaskquit"]
    if probe:
        nodes = sorted({n for e in elems for n in (e[2], e[3]) if n != "0"} | {"VIN", "VOUT"})
        vecs = ["v(VOUT)", "i(vin)", "i(vco)"] + [e[4] for e in elems] + [f"v({n})" for n in nodes]
        L += ["set wr_singlescale", "set wr_vecnames",
              f"tran {T/bench.PTS_PER_PERIOD:.9g} {T_end:.9g} {T_start:.9g} {T/bench.PTS_PER_PERIOD:.9g}",
              f"wrdata {wr_path} " + " ".join(vecs)]
    else:
        L += [f"tran {T/bench.PTS_PER_PERIOD:.9g} {T_end:.9g} {T_start:.9g} {T/bench.PTS_PER_PERIOD:.9g}",
              f"let pout = v(VOUT)*v(VOUT)/{P['ROUT']}", f"let pin = -{P['VIN']}*i(vin)",
              f"meas tran vout_avg AVG v(VOUT) from={T_start:.9g} to={T_end:.9g}",
              f"meas tran pout_avg AVG pout from={T_start:.9g} to={T_end:.9g}",
              f"meas tran pin_avg  AVG pin  from={T_start:.9g} to={T_end:.9g}",
              f"meas tran vout_max MAX v(VOUT) from={T_start:.9g} to={T_end:.9g}",
              f"meas tran vout_min MIN v(VOUT) from={T_start:.9g} to={T_end:.9g}"]
    L += ["quit", ".endc", ".end"]
    return "\n".join(L) + "\n", elems, P

OPTS_DEFAULT = ".options gmin=1e-12 reltol=1e-3 abstol=1e-9 vntol=1e-6 itl1=200 itl4=100"
OPTS_GEAR    = OPTS_DEFAULT + " method=gear"

def run_probe(netlist, duty, model, params=None, timeout=900):
    """Trapezoidal first -- byte-identical to the decks the run and mech_verify
    used -- and only if that fails to converge, retry with gear integration.
    Which decks needed the retry is recorded in the output."""
    last = None
    for opts in (OPTS_DEFAULT, OPTS_GEAR):
        with tempfile.TemporaryDirectory() as td:
            wr = os.path.join(td, "w.txt"); deck = os.path.join(td, "c.sp")
            text, elems, P = build(netlist, duty, model, params=params, probe=True, wr_path=wr)
            open(deck, "w").write(text.replace(OPTS_DEFAULT, opts))
            try:
                pr = subprocess.run([NG, "-b", deck], capture_output=True, text=True, timeout=timeout)
            except subprocess.TimeoutExpired:
                last = "timeout"; continue
            if not os.path.exists(wr):
                last = (pr.stdout + pr.stderr)[-300:]; continue
            with open(wr) as f: hdr = f.readline().split()
            data = np.loadtxt(wr, skiprows=1)
            return ({h.lower(): data[:, i] for i, h in enumerate(hdr)}, elems, P,
                    "" if opts is OPTS_DEFAULT else "gear")
    return None, elems, P, last

def evaluate_bd(netlist, duty, timeout_s=90.0, params=None, _model=None):
    """bench.evaluate with the chosen switch model. Same parsing, same Result."""
    with tempfile.TemporaryDirectory() as td:
        deck = os.path.join(td, "c.sp")
        try:
            text, _, _ = build(netlist, duty, _model, params=params, probe=False)
        except ValueError as e:
            return bench.Result(False, reason=str(e))
        for opts in (OPTS_DEFAULT, OPTS_GEAR):
            open(deck, "w").write(text.replace(OPTS_DEFAULT, opts))
            try:
                p = subprocess.run([NG, "-b", deck], capture_output=True, text=True, timeout=timeout_s)
            except subprocess.TimeoutExpired:
                continue
            txt = (p.stdout or "") + (p.stderr or "")
            vals = dict(re.findall(r"^\s*(vout_avg|pout_avg|pin_avg|vout_max|vout_min)\s*=\s*([-\d.eE+]+)",
                                   txt, re.M | re.I))
            if all(k in vals for k in ("vout_avg", "pout_avg", "pin_avg")):
                break
        else:
            return bench.Result(False, reason="timeout")
        if not all(k in vals for k in ("vout_avg", "pout_avg", "pin_avg")):
            return bench.Result(False, reason="no measurement: " + txt[-120:].replace("\n", " "))
        vout, pout, pin = float(vals["vout_avg"]), float(vals["pout_avg"]), float(vals["pin_avg"])
        ripple = float(vals.get("vout_max", "nan")) - float(vals.get("vout_min", "nan"))
        if any(v != v for v in (vout, pout, pin)):
            return bench.Result(False, reason="nan measurement")
        return bench.Result(True, vout=vout, eff=(pout / pin if pin > 1e-9 else 0.0), ripple=ripple)

# --------------------------------------------------------------------------- jobs
def job_probe(a):
    mkey, role, txt = a
    cols, elems, P, note = run_probe(parse(txt), DUTY, MODELS[mkey])
    if cols is None: return mkey, role, dict(error=note)
    st = element_stats(cols, elems, P); st["integration"] = note or "trap"
    return mkey, role, st

def job_spec(a):
    mkey, role, txt, ci = a
    model = MODELS[mkey]
    bench.evaluate = lambda nl, d, timeout_s=90.0, params=None: evaluate_bd(nl, d, timeout_s, params, model)
    s = spec.evaluate_topology(parse(txt), SHEET, timeout_s=180.0, params=spec.CORNERS[ci])
    return mkey, role, ci, dict(corner=spec.CORNERS[ci]["name"], feasible=bool(s.feasible),
                                reason=s.reason, duty=s.duty, vout=s.vout, eff=100.0 * s.eff,
                                ripple=1e3 * s.ripple)

if __name__ == "__main__":
    pj = [(m, r, t) for m in MODELS for r, t in (("child", CHILD), ("parent", PARENT))]
    sj = [(m, r, t, ci) for m in MODELS for r, t in (("child", CHILD), ("parent", PARENT))
          for ci in range(len(spec.CORNERS))]
    with Pool(12) as p:
        probes = p.map(job_probe, pj)
        specs = p.map(job_spec, sj)

    R = {m: dict(desc=MODELS[m]["desc"], roff=MODELS[m]["roff"], diodes=MODELS[m]["diodes"],
                 probe={}, corners={"child": [None]*4, "parent": [None]*4}) for m in MODELS}
    for m, role, st in probes: R[m]["probe"][role] = st
    for m, role, ci, st in specs: R[m]["corners"][role][ci] = st
    json.dump(R, open(f"{OUT}/switch_model_check.json", "w"), indent=1)

    def dev(st, name):
        for e in st.get("elements", []):
            if e["dev"] == name: return e
        return None

    L = ["# Converter (a): is C1's 97 % conduction real, or an ideal-switch artifact?", "",
         f"Child `{CHILD}`", "", f"Parent (#10271) `{PARENT}`", "",
         f"Waveforms at the child's refined nominal duty D = {DUTY}, last 20 of 2,000 periods,",
         "0 V ammeters in series with every switch, diode and capacitor. I_load = 1 A.",
         "U = fraction of the period with |i| > 1 % I_load -- the same definition mech_verify.md uses.",
         "",
         "## A. Waveform re-measurement, child",
         "",
         "| switch model | U(C1) | I_rms(C1) A | I_peak(C1) A | U(Sa1) | I_rms(Sa1) A | I_rms(body diode of Sa1) A | Vout V | eff % | integration |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        st = R[m]["probe"]["child"]
        if "error" in st: L.append(f"| `{m}` | ERROR {st['error'][:60]} |"); continue
        c1, sa1, d1 = dev(st, "C1"), dev(st, "Sa1"), dev(st, "D_Sa1")
        L.append(f"| `{m}` -- {R[m]['desc']} | {c1['util']:.2f} | {c1['i_rms']:.3f} | {c1['i_peak']:.3f} | "
                 f"{sa1['util']:.2f} | {sa1['i_rms']:.3f} | {('%.3f' % d1['i_rms']) if d1 else '--'} | "
                 f"{st['vout']:.2f} | {100*st['eff']:.2f} | {st.get('integration','trap')} |")
    L += ["", "## B. 4-corner feasibility under each switch model", "",
          "| switch model | child feasible corners | child eff median % | parent feasible corners | parent eff median % |",
          "|---|---|---|---|---|"]
    for m in MODELS:
        row = []
        for role in ("child", "parent"):
            cs = R[m]["corners"][role]; fe = [c for c in cs if c["feasible"]]
            effs = sorted(c["eff"] for c in fe)
            med = (effs[len(effs)//2] if len(effs) % 2 else 0.5*(effs[len(effs)//2-1]+effs[len(effs)//2])) if fe else None
            row += [f"**{len(fe)}/4**", ("%.2f" % med) if med is not None else "--"]
        L.append(f"| `{m}` | " + " | ".join(row) + " |")
    L += ["", "## C. Per-element detail, child, each switch model", ""]
    for m in MODELS:
        st = R[m]["probe"]["child"]
        if "error" in st: continue
        L += [f"### `{m}` -- {R[m]['desc']}",
              f"Vout {st['vout']:.2f} V, eff {100*st['eff']:.2f} %, ripple {1e3*st['ripple']:.0f} mV, "
              f"Pin {st['pin']:.3f} W, element loss {1e3*st['loss_elements']:.1f} mW", "",
              "| element | kind | I_rms A | I_peak A | I_mean A | U | V_peak V | P_loss mW |",
              "|---|---|---|---|---|---|---|---|"]
        for e in st["elements"]:
            L.append(f"| {e['dev']} | {e['kind']} | {e['i_rms']:.3f} | {e['i_peak']:.3f} | {e['i_mean']:+.4f} | "
                     f"{e['util']:.2f} | {e['v_peak']:.1f} | {1e3*e['p_loss']:.1f} |")
        L.append("")
    open(f"{OUT}/switch_model_check.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))
