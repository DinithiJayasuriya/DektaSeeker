#!/usr/bin/env python3
"""Task 1: targeted control for discovered converter (a) (= mech_verify case "d",
= discovered.json conv_g20_v6_s0 #09, parent LaMAGIC train #10271).

Child:  Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8; C1 OUT n8
The added C1 sits in PARALLEL with the series switch Sa1, between the inductor
node n8 and OUT. The paper reads this branch as a "new freewheel path".

Control asked for: replace the whole Sa1 || C1 branch with the corresponding
simple connection -- i.e. wire n8 straight to OUT and delete both devices -- and
ask whether the good behaviour survives. If it does, the branch is not supplying
a mechanism; it is a detour around a wire.

Every variant is scored the way the run scored circuits: spec.evaluate_topology
with eff_floor=0.9, duty re-refined per circuit and per corner, all 4 corners.
"""
from __future__ import annotations
import os as _os, sys as _sys
_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
_sys.path.insert(0, _os.path.join(_ROOT, "converter"))
import os, sys
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
import bench, spec

OUT = os.path.join(_ROOT, "results", "conv_validation_0918")
os.makedirs(OUT, exist_ok=True)
SHEET = spec.SpecSheet(eff_floor=0.9)

VARIANTS = {
 "child":        ("(a) as discovered: L0 -> n8, branch Sa1 || C1 to OUT",
                  "Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8; C1 OUT n8"),
 "short_branch": ("CONTROL: Sa1 || C1 branch replaced by a wire (n8 == OUT)",
                  "Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 OUT"),
 "parent":       ("parent #10271: C1 deleted, Sa1 alone in series",
                  "Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8"),
 "c1_only":      ("Sa1 deleted, C1 alone in series",
                  "Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; C1 OUT n8"),
 "buck_ref":     ("textbook buck (discovered.json s0 #02, corpus circuit)",
                  "Sa0 n3 IN; Sb0 n3 0; L0 OUT n3; C0 0 IN"),
}

def parse(s): return [tuple(t.split()) for t in s.split("; ")]

def job(a):
    key, txt, ci = a
    corner = spec.CORNERS[ci]
    s = spec.evaluate_topology(parse(txt), SHEET, timeout_s=180.0, params=corner)
    return key, ci, dict(corner=corner["name"], feasible=bool(s.feasible), reason=s.reason,
                         duty=s.duty, vout=s.vout, eff=100.0 * s.eff, ripple=1e3 * s.ripple,
                         n_sims=s.n_sims)

if __name__ == "__main__":
    jobs = [(k, v[1], ci) for k, v in VARIANTS.items() for ci in range(len(spec.CORNERS))]
    with Pool(min(24, len(jobs))) as p:
        res = p.map(job, jobs)
    out = {k: dict(desc=VARIANTS[k][0], netlist=VARIANTS[k][1], ndev=len(parse(VARIANTS[k][1])),
                   corners=[None] * len(spec.CORNERS)) for k in VARIANTS}
    for k, ci, r in res:
        out[k]["corners"][ci] = r
    for k, v in out.items():
        cs = v["corners"]; fe = [c for c in cs if c["feasible"]]
        effs = sorted(c["eff"] for c in fe)
        v["feasible_corners"] = len(fe)
        v["eff_median"] = (effs[len(effs)//2] if len(effs) % 2 else 0.5*(effs[len(effs)//2-1]+effs[len(effs)//2])) if fe else None
        v["eff_worst"] = min(effs) if fe else None
        v["ripple_max_mV"] = max(c["ripple"] for c in cs) if fe else None
    json.dump(out, open(f"{OUT}/ablate_branch_a.json", "w"), indent=1)

    L = ["# Converter (a): control for the Sa1 || C1 branch",
         "",
         "Circuit (a) = conv_g20_v6_s0 discovered #09 = mech_verify case \"d\"; parent LaMAGIC train #10271.",
         "All rows: spec.evaluate_topology, eff_floor 0.9, duty re-refined per circuit and per corner,",
         "4 corners (nominal / heavy load / light load / low line + -20% passives).",
         "",
         "| variant | devices | feasible corners | eff median % | eff worst % | ripple max mV |",
         "|---|---|---|---|---|---|"]
    for k in ("child", "short_branch", "parent", "c1_only", "buck_ref"):
        v = out[k]
        f = lambda x, n=2: "--" if x is None else f"{x:.{n}f}"
        L.append(f"| `{k}` -- {v['desc']} | {v['ndev']} | **{v['feasible_corners']}/4** | "
                 f"{f(v['eff_median'])} | {f(v['eff_worst'])} | {f(v['ripple_max_mV'],0)} |")
    L += ["", "## Per-corner detail", ""]
    for k in ("child", "short_branch", "parent", "c1_only", "buck_ref"):
        v = out[k]
        L += [f"### `{k}`  `{v['netlist']}`", "",
              "| corner | feasible | duty | Vout V | eff % | ripple mV | reason |", "|---|---|---|---|---|---|---|"]
        for c in v["corners"]:
            L.append(f"| {c['corner']} | {'yes' if c['feasible'] else 'NO'} | {c['duty']:.4f} | "
                     f"{c['vout']:.2f} | {c['eff']:.2f} | {c['ripple']:.0f} | {c['reason'] or ''} |")
        L.append("")
    open(f"{OUT}/ablate_branch_a.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L[:14]))
