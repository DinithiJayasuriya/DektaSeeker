#!/usr/bin/env python3
"""Simulate a converter netlist on the 48 V -> 3 V @ 10 A bench (ngspice), at all 4 operating corners.

Only needs python3 (stdlib) + ngspice on PATH. Uses bench.py / spec.py copied unchanged from the search code
(protocol_v90/converter), with the v90 operating point set below, so numbers should match the figure.

Examples (run from the multistage_converters/ folder):
  python3 tools/run_design.py netlists/c_F7.net                       # 4 corners, prints a table
  python3 tools/run_design.py netlists/*.net --json results/all.json  # everything, save results
  python3 tools/run_design.py netlists/c_F7.net --corner 0 --decks spice/   # also write the SPICE deck per corner
  python3 tools/run_design.py netlists/c_F7.net --corner 0 --waves results/waves_c   # dump waveforms (CSV-like text)
  python3 tools/run_design.py netlists/c_F7.net --remove C1s2,L1s2    # removal test: delete devices (open circuit)
  python3 tools/run_design.py netlists/c_F7.net --short C1s2          # removal test: replace a device by a wire
  python3 tools/run_design.py netlists/c_F7.net --duty 0.13 --corner 0  # fixed duty, no duty search
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

# ---- v90 operating point (= provenance/problem_v90.json, exported exactly like protocol_v90/run_camp.sh) -------------
ENV = dict(CONV_VIN=48.0, CONV_ROUT=3.0 / 10.0, CONV_RATING_MAX=60.0, CONV_DCR=0.002, CONV_ESR=0.002, CONV_RON=0.005,
           CONV_MIN_DUTY_RESPONSE=0, CONV_DUTY_MIN=0.1, CONV_EQUAL_COPPER=1,
           CONV_FSW=500e3, CONV_L=2.2e-6, CONV_C=47e-6, CONV_COUT=47e-6)
for k, v in ENV.items():
    os.environ.setdefault(k, str(v))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench  # noqa: E402  (reads the env above at import)
import spec   # noqa: E402

SHEET = dict(target_vout=3.0, tol=0.05, ripple_frac=0.05, eff_floor=0.90, refine_steps=2, rating_max=60.0,
             min_duty_response=0.0)   # = rsi/judge.py EV_CFG["sheet"]


def read_netlist(path):
    out = []
    for ln in Path(path).read_text().splitlines():
        t = ln.split("#")[0].split()
        if len(t) == 3:
            out.append(tuple(t))
    return out


def edit(nl, remove=(), short=()):
    nl = [d for d in nl if d[0] not in set(remove)]
    for name in short:
        hit = [d for d in nl if d[0] == name]
        if not hit:
            sys.exit(f"--short: no device {name}")
        _, a, b = hit[0]
        keep, gone = (a, b) if a in ("0", "IN", "OUT") or b not in ("0", "IN", "OUT") else (b, a)
        nl = [(d, keep if x == gone else x, keep if y == gone else y) for d, x, y in nl if d != name]
    return nl


def name_map(nl):
    """bench.py renames devices in order: switches S1.., inductors L1.., caps C1..; nodes get an 'n' prefix."""
    m, ns = {}, {"S": 0, "L": 0, "C": 0}
    for d, a, b in nl:
        k = d[0]; ns[k] += 1
        m[d] = f"{k}{ns[k]}"
    return m


def corner(args):
    nl, ci, duty = args
    p = {k: v for k, v in spec.CORNERS[ci].items() if k != "name"} or None
    if duty is not None:
        r = bench.evaluate(nl, duty, timeout_s=180, params=p)
        return dict(name=spec.CORNERS[ci]["name"], feasible=None, reason=r.reason, duty=duty, vout=r.vout, eff=r.eff,
                    ripple=r.ripple, stress_max=r.stress_max, stress_dev=r.stress_dev, stress=r.stress)
    s = spec.evaluate_topology(nl, spec.SpecSheet(**SHEET), timeout_s=180, params=spec.CORNERS[ci])
    return dict(name=spec.CORNERS[ci]["name"], feasible=bool(s.feasible), reason=s.reason, duty=s.duty, vout=s.vout,
                eff=s.eff, ripple=s.ripple, stress_max=s.stress_max, stress_dev=s.stress_dev,
                sweep=[list(x) for x in s.sweep])


def deck_text(nl, duty, ci, waves=None):
    p = {k: v for k, v in spec.CORNERS[ci].items() if k != "name"} or None
    txt = bench.build_deck(nl, duty, "unused", params=p)
    m = name_map(nl)
    head = "* corner=%s duty=%.4f\n* device map (netlist -> deck): %s\n* nodes: IN->VIN, OUT->VOUT, 0->0, X->nX\n" % (
        spec.CORNERS[ci]["name"], duty, ", ".join(f"{k}->{v}" for k, v in m.items()))
    txt = txt.replace("* LaMAGIC-style converter, bench.py\n", "* converter deck, bench.py (v90 48V->3V)\n" + head, 1)
    if waves:
        Ls = [v.lower() for v in m.values() if v[0] == "L"]
        nodes = sorted({bench._net(x) for _, a, b in nl for x in (a, b)} - {"0"})
        sav = "save all " + " ".join(f"@{l}[i]" for l in Ls)
        txt = re.sub(r"^(tran .*)$", sav + r"\n\1", txt, count=1, flags=re.M)
        vec = " ".join([f"v({n})" for n in nodes] + [f"@{l}[i]" for l in Ls] + ["i(vin)"])
        txt = txt.replace("quit\n.endc", f"set wr_singlescale\nset wr_vecnames\nwrdata {waves} {vec}\nquit\n.endc")
    return txt


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("netlists", nargs="+")
    ap.add_argument("--corner", type=int, action="append", help="0 nominal, 1 heavy_load, 2 light_load, 3 low_line_tol (default all)")
    ap.add_argument("--duty", type=float, help="fixed duty (skip the duty search)")
    ap.add_argument("--remove", default="", help="comma list of devices to delete (open)")
    ap.add_argument("--short", default="", help="comma list of devices to replace by a wire")
    ap.add_argument("--decks", help="directory: write the ngspice deck used at each corner's chosen duty")
    ap.add_argument("--waves", help="file prefix: re-run each corner at its duty and dump waveforms (last 20 periods)")
    ap.add_argument("--json", help="write all results here")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    cs = a.corner or [0, 1, 2, 3]
    rm = [x for x in a.remove.split(",") if x]; sh = [x for x in a.short.split(",") if x]
    jobs, keys = [], []
    for f in a.netlists:
        nl = edit(read_netlist(f), rm, sh)
        for ci in cs:
            jobs.append((nl, ci, a.duty)); keys.append((f, ci))
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(corner, jobs))
    out = {}
    for (f, ci), r, (nl, _, _) in zip(keys, res, jobs):
        out.setdefault(Path(f).stem, {"netlist": f, "removed": rm, "shorted": sh, "corners": []})["corners"].append(r)
        tag = f"{Path(f).stem}_{r['name']}"
        if r["duty"] == r["duty"] and (a.decks or a.waves):
            if a.decks:
                Path(a.decks).mkdir(parents=True, exist_ok=True)
                Path(a.decks, tag + ".cir").write_text(deck_text(nl, r["duty"], ci))
            if a.waves:
                w = os.path.abspath(f"{a.waves}_{tag}.txt")
                Path(w).parent.mkdir(parents=True, exist_ok=True)
                with tempfile.TemporaryDirectory() as td:
                    dk = Path(td, "w.cir"); dk.write_text(deck_text(nl, r["duty"], ci, waves=w))
                    subprocess.run([bench.NGSPICE, "-b", str(dk)], capture_output=True, text=True, timeout=600)
                print("waveforms ->", w)
    for k, v in out.items():
        print(f"\n== {k}" + (f"  removed={rm}" if rm else "") + (f"  shorted={sh}" if sh else ""))
        print(f"  {'corner':13s} {'ok':>3s} {'duty':>6s} {'Vout':>6s} {'eff%':>6s} {'ripple mV':>9s} {'max|Vds|':>8s}  note")
        for c in v["corners"]:
            ok = "-" if c["feasible"] is None else ("Y" if c["feasible"] else "N")
            e = 100 * c["eff"] if c["eff"] == c["eff"] else float("nan")
            print(f"  {c['name']:13s} {ok:>3s} {c['duty']:6.3f} {c['vout']:6.3f} {e:6.2f} {1e3 * c['ripple']:9.3f} "
                  f"{c['stress_max']:8.1f}  {c['reason'] or ''} {('worst sw ' + c['stress_dev']) if c['stress_dev'] else ''}")
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(out, indent=1, default=str))
        print("\nwrote", a.json)


if __name__ == "__main__":
    main()
