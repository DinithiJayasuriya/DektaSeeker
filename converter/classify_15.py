#!/usr/bin/env python3
"""Task 3: classify ALL 15 corner-robust converters of conv_g20_v6_s0 / _s1.

The paper accounts for 9 of them (6 inert/"redundant" additions plus the three
drawn designs). This does the bookkeeping for the whole set, on evidence rather
than on inspection of the drawings:

  1. probe every circuit at its own refined nominal duty and measure, per device,
     I_rms and U (fraction of the period with |i| > 1 % I_load);
  2. call a device INERT if it carries < 1 % of the load current (I_rms < 10 mA);
  3. delete the inert devices, then merge parallel same-kind devices, and
     canonicalise (WL colouring, rails fixed) -- does what is left reduce to the
     textbook buck?
  4. re-score the reduced circuit on all 4 corners: if the reduction is honest,
     the numbers must not move;
  5. compare every circuit's 4 corners with the textbook buck reference.

Outputs results/conv_validation_0918/classify_15.{json,md}.
"""
from __future__ import annotations
import os as _os, sys as _sys
_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
_sys.path.insert(0, _os.path.join(_ROOT, "converter"))
import os, sys
import os, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
import bench, spec
from decode import canonical
from mech_verify import run_probe, element_stats

OUT = os.path.join(_ROOT, "results", "conv_validation_0918")
os.makedirs(OUT, exist_ok=True)
RUNS = os.path.join(_ROOT, "runs") + "/"
SHEET = spec.SpecSheet(eff_floor=0.9)
INERT_A = 0.010          # 1 % of the 1 A nominal load current

BUCK = "Sa0 n3 IN; Sb0 n3 0; L0 OUT n3; C0 0 IN"     # = discovered s0 #02, corpus circuit

def parse(s): return [tuple(t.split()) for t in s.split("; ")]
def fmt(nl): return "; ".join(" ".join(d) for d in nl)

def load15():
    out = []
    for s in (0, 1):
        d = json.load(open(RUNS + f"conv_g20_v6_s{s}/discovered.json"))
        items = d if isinstance(d, list) else list(d.values())[0]
        for i, c in enumerate(items):
            nl = [tuple(l.split()) for l in c["netlist"].splitlines() if l.strip()]
            out.append(dict(label=f"s{s}#{i:02d}", seed=s, idx=i, gen=c["first_seen_gen"],
                            eff_run=c["median_gain"], novelty=c["novelty"], ndev=len(nl),
                            netlist=fmt(nl), duty=c["fit"]["corners"][0]["duty"],
                            corners_run=[dict(name=x["name"], feasible=x["feasible"],
                                              eff=100*x["eff"], ripple=1e3*x["ripple"], duty=x["duty"])
                                         for x in c["fit"]["corners"]]))
    return out

def merge_parallel(nl):
    """Collapse same-kind devices sharing a node pair. Returns (netlist, notes)."""
    groups = collections.OrderedDict()
    for dev, a, b in nl:
        kind = "Sa" if dev.startswith("Sa") else "Sb" if dev.startswith("Sb") else dev[0]
        groups.setdefault((kind, frozenset((a, b))), []).append((dev, a, b))
    out, notes = [], []
    for (kind, _), g in groups.items():
        out.append(g[0])
        if len(g) > 1:
            names = ", ".join(d[0] for d in g)
            imp = {"L": f"one L of L/{len(g)} and DCR/{len(g)}",
                   "C": f"one C of {len(g)}xC and ESR/{len(g)}",
                   "Sa": f"one Sa of Ron/{len(g)}", "Sb": f"one Sb of Ron/{len(g)}"}[kind]
            notes.append(f"{names} in parallel -> {imp}")
    return out, notes

# --------------------------------------------------------------------------- jobs
def job_probe(a):
    label, txt, duty = a
    cols, elems, P, err = run_probe(parse(txt), duty)
    if cols is None: return label, dict(error=err)
    return label, element_stats(cols, elems, P)

def job_spec(a):
    label, tag, txt, ci = a
    s = spec.evaluate_topology(parse(txt), SHEET, timeout_s=180.0, params=spec.CORNERS[ci])
    return label, tag, ci, dict(corner=spec.CORNERS[ci]["name"], feasible=bool(s.feasible),
                                reason=s.reason, duty=s.duty, vout=s.vout,
                                eff=100.0 * s.eff, ripple=1e3 * s.ripple)

def corner_summary(cs):
    fe = [c for c in cs if c["feasible"]]
    effs = sorted(c["eff"] for c in fe)
    med = (effs[len(effs)//2] if len(effs) % 2 else 0.5*(effs[len(effs)//2-1]+effs[len(effs)//2])) if fe else None
    return dict(n_feasible=len(fe), eff_median=med, eff_worst=(min(effs) if fe else None),
                ripple_max=(max(c["ripple"] for c in cs) if fe else None))

if __name__ == "__main__":
    C = load15()
    buck_can = canonical(merge_parallel(parse(BUCK))[0])

    # 1-2. probe every circuit at its nominal duty
    with Pool(16) as p:
        probes = dict(p.map(job_probe, [(c["label"], c["netlist"], c["duty"]) for c in C]))

    for c in C:
        st = probes[c["label"]]
        c["probe_error"] = st.get("error")
        if "error" in st:
            c["inert"] = []; c["reduced"] = c["netlist"]; continue
        c["iload"] = st["iload"]
        c["elements"] = [dict(dev=e["dev"], kind=e["kind"], i_rms=e["i_rms"], i_peak=e["i_peak"],
                              util=e["util"], p_loss=1e3*e["p_loss"]) for e in st["elements"]]
        c["inert"] = [e["dev"] for e in st["elements"] if e["i_rms"] < INERT_A]
        keep = [d for d in parse(c["netlist"]) if d[0] not in c["inert"]]
        c["reduced"] = fmt(keep)
        c["reduced_ndev"] = len(keep)
        merged, notes = merge_parallel(keep)
        c["merged"] = fmt(merged); c["merge_notes"] = notes
        c["reduces_to_buck"] = (canonical(merged) == buck_can)
        c["reduces_to_buck_without_merge"] = (canonical(keep) == buck_can)

    # 4-5. re-score the reduced circuit, and the buck reference, on all 4 corners
    jobs = [(c["label"], "reduced", c["reduced"], ci) for c in C for ci in range(4)]
    jobs += [("BUCK", "ref", BUCK, ci) for ci in range(4)]
    with Pool(24) as p:
        res = p.map(job_spec, jobs)
    got = collections.defaultdict(lambda: [None]*4)
    for label, tag, ci, r in res: got[(label, tag)][ci] = r
    for c in C:
        c["corners_reduced"] = got[(c["label"], "reduced")]
        c["sum_reduced"] = corner_summary(c["corners_reduced"])
        c["sum_run"] = corner_summary(c["corners_run"])
    buck_c = got[("BUCK", "ref")]; buck_s = corner_summary(buck_c)

    json.dump(dict(buck=dict(netlist=BUCK, corners=buck_c, summary=buck_s), circuits=C),
              open(f"{OUT}/classify_15.json", "w"), indent=1)

    # ------------------------------------------------------------------ report
    f2 = lambda x: "--" if x is None else f"{x:.2f}"
    f0 = lambda x: "--" if x is None else f"{x:.0f}"
    L = ["# All 15 corner-robust converters of conv_g20_v6 (seeds 0 and 1)", "",
         f"Reference textbook buck `{BUCK}`: {buck_s['n_feasible']}/4 corners, "
         f"eff median {f2(buck_s['eff_median'])} %, worst {f2(buck_s['eff_worst'])} %, "
         f"ripple max {f0(buck_s['ripple_max'])} mV.", "",
         f"A device is INERT if its I_rms is below {1e3*INERT_A:.0f} mA = 1 % of the 1 A nominal load current,",
         "measured at the circuit's own refined nominal duty with a 0 V ammeter in series with it.",
         "`reduced` = inert devices deleted; `merged` = parallel same-kind devices then collapsed.",
         "The reduced circuit is re-scored on all 4 corners: identical numbers confirm the deletion is free.",
         "",
         "| # | gen | nov | dev | inert devices | reduced to | eff med % (run -> reduced) | corners | vs buck (pp) |",
         "|---|---|---|---|---|---|---|---|---|"]
    for c in C:
        red = "buck" if c.get("reduces_to_buck") else f"{c.get('reduced_ndev','?')} dev, NOT buck"
        if c.get("reduces_to_buck") and not c.get("reduces_to_buck_without_merge"):
            red = "buck (after parallel merge)"
        d = (c["sum_reduced"]["eff_median"] - buck_s["eff_median"]) if c["sum_reduced"]["eff_median"] is not None else None
        L.append(f"| {c['label']} | {c['gen']} | {c['novelty']:.3f} | {c['ndev']} | "
                 f"{', '.join(c['inert']) or '--'} | {red} | "
                 f"{f2(c['sum_run']['eff_median'])} -> {f2(c['sum_reduced']['eff_median'])} | "
                 f"{c['sum_reduced']['n_feasible']}/4 | {'--' if d is None else f'{d:+.2f}'} |")
    L += ["", "## Per-circuit detail", ""]
    for c in C:
        L += [f"### {c['label']}  (seed {c['seed']}, first seen gen {c['gen']}, novelty {c['novelty']:.4f})",
              "", f"- as discovered: `{c['netlist']}`  ({c['ndev']} devices)",
              f"- inert: {', '.join(c['inert']) or 'none'}",
              f"- reduced: `{c['reduced']}`"]
        if c.get("merge_notes"): L.append(f"- parallel merge: {'; '.join(c['merge_notes'])} -> `{c['merged']}`")
        L.append(f"- reduces to the textbook buck: **{c.get('reduces_to_buck')}**"
                 + ("" if c.get("reduces_to_buck_without_merge") or not c.get("reduces_to_buck")
                    else " (only after merging parallel devices)"))
        L += ["", "| device | kind | I_rms A | I_peak A | U | P_loss mW |", "|---|---|---|---|---|---|"]
        for e in c.get("elements", []):
            flag = " *(inert)*" if e["dev"] in c["inert"] else ""
            L.append(f"| {e['dev']}{flag} | {e['kind']} | {e['i_rms']:.3f} | {e['i_peak']:.3f} | "
                     f"{e['util']:.2f} | {e['p_loss']:.1f} |")
        L += ["", "| corner | as discovered: feasible / eff % / ripple mV | reduced: feasible / eff % / ripple mV |",
              "|---|---|---|"]
        for a, b in zip(c["corners_run"], c["corners_reduced"]):
            L.append(f"| {a['name']} | {'yes' if a['feasible'] else 'NO'} / {a['eff']:.2f} / {a['ripple']:.0f} | "
                     f"{'yes' if b['feasible'] else 'NO'} / {b['eff']:.2f} / {b['ripple']:.0f} |")
        L.append("")
    open(f"{OUT}/classify_15.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L[:30]))
