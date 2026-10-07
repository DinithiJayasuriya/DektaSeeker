#!/usr/bin/env python3
"""Per-device effect of every device the search ADDED to the four converters in
discovered_converters_1col.png (figure panels, left-to-right, top-to-bottom):

  a  g20 (a)        parent #9562  + L1
  b  g20 (d)        parent #10271 + C1
  c  rule_s0 #00    parent #55863 + L1, C0, Sa0, Sb1, C1
  d  rule_s0 #01    parent #4397  + L1, C0, Sa0, Sb0, L2

Per added device X, three variants of the discovered child:
  del   X removed (open)                 -> is X needed?
  short X replaced by a wire (nodes merged) -> does X do more than a wire?
  add   parent + X only                  -> does X alone repair the parent?
Scored exactly like the run (and ablate_branch_a.py): spec.evaluate_topology,
eff_floor 0.9, duty re-refined per circuit and per corner, all 4 corners.
Output: results/conv_validation_0918/ablate_added_devices.{json,md}
"""
from __future__ import annotations
import os as _os, sys as _sys
_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
_sys.path.insert(0, _os.path.join(_ROOT, "converter"))
import os, sys
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
import spec

OUT = os.path.join(_ROOT, "results", "conv_validation_0918")
TAB = os.path.join(_ROOT, "circuits", "discovered_converters_table.json")
SHEET = spec.SpecSheet(eff_floor=0.9)

# child netlists from discovered_converters_table.json; parent = child minus ADDED (the figure's black part,
# in the child's own node names, so add-one variants are well defined)
ADDED = {"a": ["L1"], "b": ["C1"], "c": ["L1", "C0", "Sa0", "Sb1", "C1"], "d": ["L1", "C0", "Sa0", "Sb0", "L2"]}


def parse(s): return [tuple(t.split()) for t in s.split("; ")]


def fmt(dev): return "; ".join(" ".join(d) for d in dev)


def short(dev, name):
    x = next(d for d in dev if d[0] == name)
    a, b = x[1], x[2]
    keep, drop = (a, b) if a in ("IN", "OUT", "0") else (b, a)
    if drop in ("IN", "OUT", "0") and keep != drop:
        return None                                   # would short two terminals together
    out = []
    for d in dev:
        if d[0] == name: continue
        out.append((d[0],) + tuple(keep if n == drop else n for n in d[1:]))
    return [d for d in out if d[1] != d[2]]            # a device shorted onto itself disappears


def variants():
    tab = json.load(open(TAB))
    V = {}
    for k, added in ADDED.items():
        child = parse(tab[f"{k}|disc"]["netlist"])
        parent = [d for d in child if d[0] not in added]
        V[(k, "child", "")] = fmt(child)
        V[(k, "parent", "")] = fmt(parent)
        for x in added:
            V[(k, "del", x)] = fmt([d for d in child if d[0] != x])
            s = short(child, x)
            if s is not None: V[(k, "short", x)] = fmt(s)
            V[(k, "add", x)] = fmt(parent + [d for d in child if d[0] == x])
    return V


def job(a):
    key, txt, ci = a
    corner = spec.CORNERS[ci]
    try:
        s = spec.evaluate_topology(parse(txt), SHEET, timeout_s=180.0, params=corner)
        r = dict(feasible=bool(s.feasible), reason=s.reason, duty=s.duty, vout=s.vout,
                 eff=100.0 * s.eff, ripple=1e3 * s.ripple)
    except Exception as e:                               # noqa: BLE001
        r = dict(feasible=False, reason=f"error: {e}", duty=None, vout=None, eff=None, ripple=None)
    r["corner"] = corner["name"]
    return key, ci, r


def median(v):
    v = sorted(v); n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


if __name__ == "__main__":
    V = variants()
    jobs = [(k, t, ci) for k, t in V.items() for ci in range(len(spec.CORNERS))]
    with Pool(min(48, len(jobs))) as p:
        res = p.map(job, jobs)
    out = {}
    for k, ci, r in res:
        out.setdefault(k, dict(netlist=V[k], corners=[None] * len(spec.CORNERS)))["corners"][ci] = r
    for v in out.values():
        cs = v["corners"]; fe = [c for c in cs if c["feasible"]]
        v["feasible_corners"] = len(fe)
        v["eff_median"] = median([c["eff"] for c in fe])
        v["eff_all_median"] = median([c["eff"] for c in cs if c["eff"] is not None])
        v["vout_nom"] = cs[0]["vout"]
        v["reasons"] = sorted({c["reason"] for c in cs if not c["feasible"]})
    os.makedirs(OUT, exist_ok=True)
    json.dump({"|".join(k): v for k, v in out.items()}, open(f"{OUT}/ablate_added_devices.json", "w"), indent=1)

    f = lambda x, n=2: "--" if x is None else f"{x:.{n}f}"
    L = ["# Per-device effect of the added (red) devices, 4 figure converters", "",
         "spec.evaluate_topology, eff_floor 0.9, duty re-refined per circuit and corner, 4 corners.",
         "del = device removed from the child; short = device replaced by a wire; add = parent + that device only.", ""]
    for k in ADDED:
        L += [f"## {k}", "", "| variant | device | corners | eff median (feasible) % | eff median (all) % | Vout nom V | fail reasons |",
              "|---|---|---|---|---|---|---|"]
        for key in [x for x in V if x[0] == k]:
            v = out[key]
            L.append(f"| {key[1]} | {key[2]} | {v['feasible_corners']}/4 | {f(v['eff_median'])} | {f(v['eff_all_median'])} | "
                     f"{f(v['vout_nom'])} | {'; '.join(v['reasons'])[:120]} |")
        L.append("")
    open(f"{OUT}/ablate_added_devices.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))
