import os as _os, sys as _sys
_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
_sys.path.insert(0, _os.path.join(_ROOT, "converter"))
import os, sys
import sys, json, itertools, collections, time
sys.path.insert(0, os.path.join(_ROOT, "converter"))
import numpy as np, torch
from decode import to_netlist, canonical, DecodeError, EDGE_TERM_PLUS
D=os.path.join(_ROOT, "corpus", "lamagic_graphs") + "/"
RUNS=os.path.join(_ROOT, "runs") + "/"

def iter_graphs(pt):
    data, slices = torch.load(pt)
    nx_slc, ei_slc = slices["x"], slices["edge_index"]
    for i in range(len(nx_slc)-1):
        off=int(nx_slc[i]); x=data.x[off:int(nx_slc[i+1])]
        es,ee=int(ei_slc[i]),int(ei_slc[i+1]); ei=data.edge_index[:,es:ee].numpy()
        nt=x.argmax(1).numpy(); n=len(nt); E=np.zeros((n,n),dtype=int); E[ei[0],ei[1]]=EDGE_TERM_PLUS
        yield nt, E

t0=time.time()
ref=collections.Counter(); ref_split={}
example={}
for split in ("train","val","test"):
    n_ok=n_bad=0
    for nt,E in iter_graphs(D+split+".pt"):
        try: nl=to_netlist(nt,E)
        except DecodeError: n_bad+=1; continue
        c=canonical(nl); ref[c]+=1; ref_split.setdefault(c,set()).add(split); example.setdefault(c,nl); n_ok+=1
    print(f"{split}: decoded {n_ok}, undecodable {n_bad}, distinct so far {len(ref)}  ({time.time()-t0:.0f}s)")

def parse(s):
    out=[]
    for l in s.splitlines():
        p=l.split()
        if len(p)==3: out.append((p[0],p[1],p[2]))
    return out

def sub_matches(nl, k):
    """training circuits reachable by deleting k devices"""
    hits=[]
    for drop in itertools.combinations(range(len(nl)),k):
        sub=[d for i,d in enumerate(nl) if i not in drop]
        if not sub: continue
        c=canonical(sub)
        if c in ref: hits.append(([nl[i][0] for i in drop], ref[c]))
    return hits

for s in (0,1):
    d=json.load(open(RUNS+f"conv_g20_v6_s{s}/discovered.json"))
    items=d if isinstance(d,list) else list(d.values())[0]
    print(f"\n===== seed {s}: {len(items)} discovered")
    for c in items:
        nl=parse(c["netlist"]); can=canonical(nl)
        inref=can in ref
        line=f"gen{c['first_seen_gen']:>2} eff {c['median_gain']:.2f} nov {c['novelty']:.3f} ncomp {len(nl)} | " + "; ".join(" ".join(x) for x in nl)
        print(line)
        if inref:
            print(f"     IN CORPUS  (count {ref[can]}, splits {sorted(ref_split[can])})")
        else:
            m1=sub_matches(nl,1); m2=sub_matches(nl,2) if not m1 else []
            if m1: print(f"     NOT in corpus; = training circuit + 1 extra: drop {[h[0] for h in m1]}")
            elif m2: print(f"     NOT in corpus; = training circuit + 2 extras: drop {[h[0] for h in m2][:4]}")
            else: print(f"     NOT in corpus; not a training circuit +1/+2 device either")
print("\nref distinct:",len(ref))
