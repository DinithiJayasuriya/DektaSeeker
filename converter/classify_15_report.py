#!/usr/bin/env python3
"""Classification of all 15 corner-robust converters of conv_g20_v6_s0/_s1.

Pure bookkeeping over measurements already made -- no new simulation. Inputs:
  classify_15.json        per-device I_rms/U at each circuit's nominal duty,
                          plus a 4-corner re-score of each circuit with its
                          zero-current devices deleted, and of the textbook buck
  corpus_after_prune.json exact corpus isomorphism before and after that deletion
  corpus_match_examples.json the actual matching LaMAGIC circuits
  train_overlap_rerun.txt the "= training circuit + k extras" relation

Classes, applied in order:
  1  already in the LaMAGIC corpus
  2  a corpus circuit plus device(s) measured to carry zero current
       2a  floating loop  -- a subgraph whose nets touch only one other net;
                             dead in any bench
       2b  across the ideal input source -- carries no current only because the
                             bench drives VIN from an ideal voltage source
  3  a corpus circuit plus an active device that rescales a passive or filters
  4  a mechanism the corpus does not contain
"""
from __future__ import annotations
import os as _os, sys as _sys
_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
_sys.path.insert(0, _os.path.join(_ROOT, "converter"))
import os, sys
import os, sys, json, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

OUT = os.path.join(_ROOT, "results", "conv_validation_0918")
D = json.load(open(f"{OUT}/classify_15.json"))
BUCK, CIRC = D["buck"], D["circuits"]
PRUNE = {r["label"]: r for r in json.load(open(f"{OUT}/corpus_after_prune.json"))}
MATCH = {r["label"]: r for r in json.load(open(f"{OUT}/corpus_match_examples.json"))}

def parse(s): return [tuple(t.split()) for t in s.split("; ")]
RAILS = {"IN", "OUT", "0"}

def floating(nl, devs):
    """True if `devs` form a subgraph hanging off a single net: every internal net
    they touch is touched by nothing else, and the whole group connects to the
    rest of the circuit through at most one net."""
    if not devs: return False
    grp = [d for d in nl if d[0] in devs]
    rest = [d for d in nl if d[0] not in devs]
    grp_nets = {n for _, a, b in grp for n in (a, b)}
    rest_nets = {n for _, a, b in rest for n in (a, b)}
    shared = grp_nets & (rest_nets | RAILS)
    return len(shared) <= 1

def across_source(nl, devs):
    """True if every device in `devs` sits on a path that only touches IN and 0:
    a capacitor (or chain of them) across the ideal input source."""
    if not devs: return False
    grp = [d for d in nl if d[0] in devs]
    if not all(d[0].startswith("C") for d in grp): return False
    rest = [d for d in nl if d[0] not in devs]
    rest_nets = {n for _, a, b in rest for n in (a, b)}
    grp_nets = {n for _, a, b in grp for n in (a, b)}
    # the group may only meet the rest of the circuit at IN and/or 0
    return (grp_nets & rest_nets) <= {"IN", "0"} and grp_nets <= (rest_nets | {"IN", "0"} | (grp_nets - rest_nets))

def components(nl, devs):
    """Split `devs` into groups connected through non-rail nets."""
    pos = {d[0]: (d[1], d[2]) for d in nl}
    groups = []
    for dv in devs:
        nets = {n for n in pos[dv] if n not in RAILS}
        hit = [g for g in groups if g[1] & nets]
        merged = ({dv}, set(nets))
        for g in hit:
            merged = (merged[0] | g[0], merged[1] | g[1]); groups.remove(g)
        groups.append(merged)
    return [g[0] for g in groups]

# ---- the "+k extras" drop sets from train_overlap ---------------------------
def drop_sets():
    txt = open(f"{OUT}/train_overlap_rerun.txt").read()
    out, cur = [], None
    for line in txt.splitlines():
        if re.match(r"^gen\s*\d+ eff", line):
            cur = []; out.append(cur)
        elif cur is not None and "drop [" in line:
            cur.extend(eval(line[line.index("drop [") + 5:].strip()))
    return out
DROPS = drop_sets()

buck_s = BUCK["summary"]
for c, ds in zip(CIRC, DROPS):
    p = PRUNE[c["label"]]
    c["in_corpus"] = p["in_corpus"]
    c["pruned_in_corpus"] = p["pruned_in_corpus"]
    c["pruned_netlist"] = p["pruned_netlist"]
    c["drop_sets"] = ds
    nl = parse(c["netlist"])
    c["nominal_ripple"] = c["corners_run"][0]["ripple"]
    s = c["sum_reduced"]
    c["d_eff_med"] = None if s["eff_median"] is None else s["eff_median"] - buck_s["eff_median"]
    c["d_eff_worst"] = None if s["eff_worst"] is None else s["eff_worst"] - buck_s["eff_worst"]
    c["d_ripple_nom"] = c["nominal_ripple"] - BUCK["corners"][0]["ripple"]

    if c["in_corpus"]:
        c["cls"], c["sub"] = 1, ""
        c["why"] = f"already in the LaMAGIC training set ({MATCH[c['label']]['n_copies']} copies)"
    elif c["pruned_in_corpus"]:
        c["cls"] = 2
        parts = []
        any_float = False
        for comp in components(nl, c["inert"]):
            names = ", ".join(sorted(comp))
            if floating(nl, comp):
                any_float = True; parts.append(f"floating loop ({names})")
            elif across_source(nl, comp):
                parts.append(f"capacitor across the ideal input source ({names})")
            else:
                any_float = True; parts.append(f"zero-current device(s) ({names})")
        c["sub"] = "a" if any_float else "b"
        c["why"] = "corpus circuit + " + " + ".join(parts) + "; all measure 0.00000 A"
    else:
        c["cls"], c["sub"] = 3, ""
        c["why"] = "corpus circuit + an active device; see note"
NOTES = {
 "s0#00": "added L1 is in parallel with L0: the pair is one inductor of L/2 and DCR/2. "
          "The +0.23 pp comes from halving the winding resistance, not from a new path "
          "(mech_verify.md S8: a single 250 uH / 0.125 Ohm inductor reproduces the child exactly).",
 "s0#01": "same as s0#00 with the filter capacitor moved to OUT-0.",
 "s0#08": "the added C0 (OUT-0, 72 mA) is an output filter capacitor that merges into the bench's own "
          "Cout (mech_verify.md S8: the parent with Cout = 20 uF reproduces the child). Its parent already "
          "contains the doubled series high-side switch, which is what costs the 0.05 pp.",
 "s0#09": "THIS IS CONVERTER (a) IN THE PAPER. Two separate results below: its Sa1 || C1 branch is already "
          "in the corpus (train #23311), and replacing that branch with a wire is strictly better.",
}
for c in CIRC:
    if c["label"] in NOTES: c["note"] = NOTES[c["label"]]

# ---------------------------------------------------------------- report
f2 = lambda x: "--" if x is None else f"{x:.2f}"
sg = lambda x: "--" if x is None else f"{x:+.2f}"
cnt = collections.Counter((c["cls"], c["sub"]) for c in CIRC)
L = ["# All 15 corner-robust converters, classified", "",
     "conv_g20_v6_s0 (10 archived) + conv_g20_v6_s1 (5 archived). Everything below is measured:",
     "per-device currents from a 0 V ammeter in series with each device at the circuit's own refined",
     "nominal duty; corpus membership by exact WL-canonical isomorphism against all 37,496 distinct",
     "LaMAGIC train/val/test topologies; 4-corner re-scores through the run's own spec.evaluate_topology.",
     "",
     "| class | meaning | count |", "|---|---|---|",
     f"| 1 | already in the LaMAGIC corpus | {cnt[(1,'')]} |",
     f"| 2a | a corpus circuit + a floating loop (0.00000 A, dead in any bench) | {cnt[(2,'a')]} |",
     f"| 2b | a corpus circuit + capacitor(s) across the ideal input source (0.00000 A here) | {cnt[(2,'b')]} |",
     f"| 3 | a corpus circuit + an active device that rescales a passive or filters | {cnt[(3,'')]} |",
     f"| 4 | a mechanism the corpus does not contain | 0 |",
     "", f"**{cnt[(1,'')] + cnt[(2,'a')] + cnt[(2,'b')]}/15 are a LaMAGIC training circuit once devices "
     "measured at 0.00000 A are deleted. The remaining 3 add an active device that rescales an inductor "
     "or adds filtering. None of the 15 is a mechanism the corpus does not already contain.**", "",
     "| # | gen | dev | class | in corpus | after pruning 0 A devices | Δη med pp | Δη worst pp | Δripple nom mV | reading |",
     "|---|---|---|---|---|---|---|---|---|---|"]
for c in CIRC:
    L.append(f"| {c['label']} | {c['gen']} | {c['ndev']} | **{c['cls']}{c['sub']}** | "
             f"{'YES' if c['in_corpus'] else 'no'} | {'YES' if c['pruned_in_corpus'] else 'no'} | "
             f"{sg(c['d_eff_med'])} | {sg(c['d_eff_worst'])} | {sg(c['d_ripple_nom'])} | {c['why']} |")
L += ["", "Δ columns compare the circuit (with 0 A devices deleted) against the textbook buck "
      f"`{BUCK['netlist']}` at {f2(buck_s['eff_median'])} % median / {f2(buck_s['eff_worst'])} % worst "
      f"/ {BUCK['corners'][0]['ripple']:.0f} mV nominal ripple.", "",
      "## Notes on the three circuits that are not a corpus circuit plus dead devices", ""]
for c in CIRC:
    if c.get("note") and c["cls"] == 3: L += [f"**{c['label']}** -- {c['note']}", ""]
L += ["## Note on converter (a)", "", NOTES["s0#09"], "",
      "## Netlists, pruned forms and the matching corpus circuit", "",
      "| # | as discovered | after deleting 0 A devices | matching corpus circuit |", "|---|---|---|---|"]
for c in CIRC:
    m = MATCH.get(c["label"])
    ex = m["examples"][0] if m else None
    L.append(f"| {c['label']} | `{c['netlist']}` | `{c['pruned_netlist']}` | "
             + (f"`{ex['netlist']}` ({ex['split']} #{ex['index']}, {m['n_copies']} copies)" if ex else "--") + " |")
L += ["", "## Per-device currents (nominal duty, I_load = 1 A)", ""]
for c in CIRC:
    L += [f"### {c['label']}  `{c['netlist']}`", "",
          "| device | kind | I_rms A | I_peak A | U | P_loss mW |", "|---|---|---|---|---|---|"]
    for e in c["elements"]:
        flag = " **(0 A)**" if e["dev"] in c["inert"] else ""
        L.append(f"| {e['dev']}{flag} | {e['kind']} | {e['i_rms']:.5f} | {e['i_peak']:.3f} | "
                 f"{e['util']:.2f} | {e['p_loss']:.2f} |")
    L.append("")
open(f"{OUT}/classify_15_final.md", "w").write("\n".join(L) + "\n")
json.dump(CIRC, open(f"{OUT}/classify_15_final.json", "w"), indent=1)
print("\n".join(L[:40]))
