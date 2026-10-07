#!/usr/bin/env python3
"""Cumulative build-up parent -> child for figure converters c and d (companion to ablate_added_devices.py),
plus 'wire' controls where the essential bridge is replaced by a plain connection. Same scoring.
Output: results/conv_validation_0918/ablate_added_chain.{json,md}"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
import spec
from ablate_added_devices import TAB, OUT, ADDED, parse, fmt, job, median, short

tab = json.load(open(TAB))
CHAINS = {"c": [["C0", "Sb1"], ["Sa0"], ["L1"], ["C1"]],
          "d": [["L2"], ["C0", "Sb0"], ["Sa0"], ["L1"]]}
V = {}
for k, steps in CHAINS.items():
    child = parse(tab[f"{k}|disc"]["netlist"]); added = ADDED[k]
    cur = [d for d in child if d[0] not in added]; have = []
    V[(k, "chain", "parent")] = fmt(cur)
    for st in steps:
        have += st
        V[(k, "chain", "+" + ",".join(have))] = fmt([d for d in child if d[0] not in added or d[0] in have])
# wire controls: bridge C0-S replaced by a wire (C0 shorted, S shorted), rest as parent
for k, S in (("c", "Sb1"), ("d", "Sb0")):
    child = parse(tab[f"{k}|disc"]["netlist"]); added = ADDED[k]
    keep = [d for d in child if d[0] not in added or d[0] in ("C0", S)]
    w = short(short(keep, "C0"), S)
    V[(k, "wire", f"parent + wire for C0-{S}")] = fmt(w)
    if k == "d":
        keep = [d for d in child if d[0] not in added or d[0] in ("C0", S, "L2")]
        V[(k, "wire", f"parent + L2 + wire for C0-{S}")] = fmt(short(short(keep, "C0"), S))
jobs = [(k, t, ci) for k, t in V.items() for ci in range(len(spec.CORNERS))]
with Pool(min(48, len(jobs))) as p:
    res = p.map(job, jobs)
out = {}
for k, ci, r in res:
    out.setdefault(k, dict(netlist=V[k], corners=[None] * 4))["corners"][ci] = r
L = ["| circuit | variant | netlist | corners | eff median (all) % | Vout nom | fail |", "|---|---|---|---|---|---|---|"]
for key, v in out.items():
    cs = v["corners"]; fe = [c for c in cs if c["feasible"]]
    v["feasible_corners"] = len(fe); v["eff_all_median"] = median([c["eff"] for c in cs if c["eff"] is not None])
    L.append(f"| {key[0]} | {key[2]} | `{v['netlist']}` | {len(fe)}/4 | {v['eff_all_median']:.2f} | {cs[0]['vout']:.2f} | "
             f"{'; '.join(sorted({c['reason'] for c in cs if not c['feasible']}))[:90]} |")
json.dump({"|".join(k): v for k, v in out.items()}, open(f"{OUT}/ablate_added_chain.json", "w"), indent=1)
open(f"{OUT}/ablate_added_chain.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
