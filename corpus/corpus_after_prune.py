#!/usr/bin/env python3
"""For each of the 15 corner-robust converters: is it in the LaMAGIC corpus
(a) as discovered, and (b) after deleting only the devices measured to carry
exactly zero current (classify_15.json, 0 V ammeter in series, I_rms < 10 mA)?

(b) is the number the paper needs: a circuit that becomes a training topology
once its dead devices are removed is not a new topology, it is a training
topology with decoration that the structural validity gate admits and the
novelty score rewards.
"""
import os as _os, sys as _sys
_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
_sys.path.insert(0, _os.path.join(_ROOT, "converter"))
import os, sys
import sys, json, collections, time
sys.path.insert(0, os.path.join(_ROOT, "converter"))
import numpy as np, torch
from decode import to_netlist, canonical, DecodeError, EDGE_TERM_PLUS

D = os.path.join(_ROOT, "corpus", "lamagic_graphs") + "/"
OUT = os.path.join(_ROOT, "results", "conv_validation_0918")

def iter_graphs(pt):
    data, slices = torch.load(pt)
    nx_slc, ei_slc = slices["x"], slices["edge_index"]
    for i in range(len(nx_slc) - 1):
        off = int(nx_slc[i]); x = data.x[off:int(nx_slc[i+1])]
        es, ee = int(ei_slc[i]), int(ei_slc[i+1]); ei = data.edge_index[:, es:ee].numpy()
        nt = x.argmax(1).numpy(); n = len(nt)
        E = np.zeros((n, n), dtype=int); E[ei[0], ei[1]] = EDGE_TERM_PLUS
        yield nt, E

t0 = time.time()
ref = collections.Counter(); ref_split = {}
for split in ("train", "val", "test"):
    for nt, E in iter_graphs(D + split + ".pt"):
        try: nl = to_netlist(nt, E)
        except DecodeError: continue
        c = canonical(nl); ref[c] += 1; ref_split.setdefault(c, set()).add(split)
print(f"corpus: {len(ref)} distinct topologies ({time.time()-t0:.0f}s)")

C = json.load(open(f"{OUT}/classify_15.json"))["circuits"]
parse = lambda s: [tuple(t.split()) for t in s.split("; ")]
rows = []
for c in C:
    full = parse(c["netlist"])
    pruned = [d for d in full if d[0] not in c["inert"]]
    cf, cp = canonical(full), canonical(pruned)
    rows.append(dict(label=c["label"], ndev=len(full), inert=c["inert"],
                     pruned_netlist="; ".join(" ".join(d) for d in pruned),
                     in_corpus=cf in ref, in_corpus_count=ref.get(cf, 0),
                     pruned_in_corpus=cp in ref, pruned_count=ref.get(cp, 0),
                     pruned_splits=sorted(ref_split.get(cp, []))))
json.dump(rows, open(f"{OUT}/corpus_after_prune.json", "w"), indent=1)

L = ["# Corpus membership of the 15, before and after pruning zero-current devices", "",
     f"Corpus: {len(ref)} distinct LaMAGIC topologies (train + val + test), WL-canonical with rails fixed.",
     "A device is pruned only if its measured I_rms is 0 (< 10 mA = 1 % of the 1 A load current).", "",
     "| # | devices | in corpus as discovered | zero-current devices pruned | in corpus after pruning | copies in corpus |",
     "|---|---|---|---|---|---|"]
for r in rows:
    L.append(f"| {r['label']} | {r['ndev']} | {'**YES**' if r['in_corpus'] else 'no'} | "
             f"{', '.join(r['inert']) or '--'} | {'**YES**' if r['pruned_in_corpus'] else 'no'} | "
             f"{r['pruned_count'] or '--'} |")
n1 = sum(r["in_corpus"] for r in rows); n2 = sum(r["pruned_in_corpus"] for r in rows)
L += ["", f"**{n1}/15 in the corpus as discovered; {n2}/15 in the corpus once zero-current devices are removed.**",
      "", "## Pruned netlists", "", "| # | pruned netlist | in corpus |", "|---|---|---|"]
for r in rows:
    L.append(f"| {r['label']} | `{r['pruned_netlist']}` | {'YES' if r['pruned_in_corpus'] else 'no'} |")
open(f"{OUT}/corpus_after_prune.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
