"""Child-vs-parent corner comparison for the 4 novel converters of conv_g20_v6_s0.
Re-simulates BOTH the discovered child and its nearest LaMAGIC training parent under the run's exact
spec (eff_floor 0.90, 4 corners, duty sweep + 2 secant refinements) so the comparison is apples to apples."""
import os as _os, sys as _sys
_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
_sys.path.insert(0, _os.path.join(_ROOT, "converter"))
import os, sys
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
import spec

CASES = {
 "a": dict(title="paralleled inductors, cap IN->OUT", added="L1 (2nd inductor, parallel)", parent_id="train #9562",
           child="Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT; L1 n1 OUT",
           parent="Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT"),
 "b": dict(title="switched output capacitor", added="C0 (input cap)", parent_id="train #19363",
           child="Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 OUT; Sb1 n0 OUT; C1 n0 0",
           parent="Sb0 0 n7; Sa0 IN n7; L0 n7 OUT; Sb1 n0 OUT; C1 n0 0"),
 "c": dict(title="doubled series high-side switch", added="C0 (output cap)", parent_id="train #415",
           child="Sb0 0 n7; Sa0 n0 n7; L0 n7 OUT; C0 0 OUT; Sa1 n0 IN; Sb1 n0 OUT",
           parent="Sb0 0 n7; Sa0 n0 n7; L0 n7 OUT; Sa1 n0 IN; Sb1 n0 OUT"),
 "d": dict(title="inductor to OUT through Sa1 || C1", added="C1 (cap across Sa1)", parent_id="train #10271",
           child="Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8; C1 OUT n8",
           parent="Sb0 0 n7; Sa0 IN n7; C0 IN 0; L0 n7 n8; Sa1 OUT n8"),
 "ref": dict(title="textbook buck (train #6935)", added="-", parent_id="-",
           child="Sa0 n3 IN; Sb0 n3 0; L0 OUT n3; C0 0 IN", parent=None),
}
SHEET = spec.SpecSheet(eff_floor=0.9)

def parse(s): return [tuple(t.split()) for t in s.split("; ")]

def job(args):
    key, role, txt, ci = args
    s = spec.evaluate_topology(parse(txt), SHEET, timeout_s=90.0, params=spec.CORNERS[ci])
    return key, role, ci, dict(corner=spec.CORNERS[ci]["name"], feasible=bool(s.feasible), reason=s.reason,
                               duty=s.duty, vout=s.vout, eff=s.eff, ripple=s.ripple, duty_response=s.duty_response,
                               passthrough=bool(s.passthrough), sweep=[list(x) for x in s.sweep], n_sims=int(s.n_sims))

if __name__ == "__main__":
    jobs = []
    for k, c in CASES.items():
        for role in ("child", "parent"):
            if c[role]:
                for ci in range(len(spec.CORNERS)): jobs.append((k, role, c[role], ci))
    out = {k: dict(meta={kk: vv for kk, vv in c.items()}, child=[None]*4, parent=[None]*4) for k, c in CASES.items()}
    with Pool(min(len(jobs), 18)) as p:
        for key, role, ci, rec in p.imap_unordered(job, jobs):
            out[key][role][ci] = rec
    od = os.path.join(_ROOT, "results", "conv_parent_compare")
    json.dump(out, open(f"{od}/parent_compare.json", "w"), indent=1)
    for k, r in out.items():
        for role in ("child", "parent"):
            if r[role][0] is None: continue
            print(f"[{k}] {role:6s}", " | ".join(f"{c['corner'][:9]}: {'OK ' if c['feasible'] else 'FAIL'} D={c['duty'] if c['duty'] is not None else float('nan'):.3f} Vo={c['vout']:.2f} eff={100*c['eff']:.2f} rip={1000*c['ripple']:.0f}mV" if c['duty'] is not None else f"{c['corner'][:9]}: FAIL ({c['reason']})" for c in r[role]))
