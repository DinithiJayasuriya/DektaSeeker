#!/usr/bin/env python3
"""mech_verify.json -> mech_verify.md (+ fig_mech_sweeps.png). Run with the digress python."""
import os as _os, sys as _sys
_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
_sys.path.insert(0, _os.path.join(_ROOT, "converter"))
import os, sys
import json, os, sys, statistics as st
import numpy as np
OUT = os.path.join(_ROOT, "results", "conv_mech_verify")
R = json.load(open(f"{OUT}/mech_verify.json"))
PC = json.load(open(os.path.join(_ROOT, "results", "conv_parent_compare", "parent_compare.json")))
md = []
def P(*a): md.append(" ".join(str(x) for x in a))

def elem(rec, dev):
    for e in rec["elements"]:
        if e["dev"] == dev: return e
def kind_loss(rec):
    d = {}
    for e in rec["elements"]: d[e["kind"]] = d.get(e["kind"], 0) + e["p_loss"]
    d["Cout ESR"] = rec["loss_cout_esr"]; return d

P("# Mechanism verification, conv_g20_v6_s0 children vs nearest training parents (2026-09-13)\n")
P("All waveform numbers are from the bench's own ngspice deck (VIN 100 V, 100 kHz, L 500 µH / DCR 0.25 Ω, C 10 µF / ESR 30 mΩ, "
  "Cout 10 µF, ideal SW switches Ron 50 mΩ / Roff 1 MΩ), last 20 of 2,000 periods, at the child's refined nominal duty, with a 0 V probe "
  "source in series with every switch and capacitor. **Switching loss is not modelled** (ideal switch model, 1 ns edges): the loss table is "
  "conduction + ESR only, and it closes against Pin − Pout to <1 mW. I_load = 1 A at nominal (50 V / 50 Ω). U = fraction of the period with |i| > 1 % I_load. "
  "Δ columns are child − parent; Δη/Δripple/Δfeasible use the 4-corner re-simulation of parent_compare.md (duty re-refined per circuit and corner).\n")

# ---------------- 1. compact mechanism table
P("## 1. Mechanism-verification table\n")
P("| design | added element | active? (U, I_rms/I_load) | Δη median (pp) | Δη worst-corner (pp) | Δripple nominal | Δfeasible corners | peak stress on added element | verdict |")
P("|---|---|---|---|---|---|---|---|---|")
VERDICT = {"a": "trade-off: +η from halved winding loss, ripple ×2 (still 0.13 % Vout)",
           "b": "NO: zero current (sits across the ideal source); redundant",
           "c": "ripple suppression only; merges into the bench output cap",
           "d": "YES: new energy-transfer path (parent is not a converter without it), but 6.5 A / 7.2 A peaks on C1 / Sa1 at 1 A load"}
def summ4(cs):
    effs = [100 * c["eff"] for c in cs]; return st.median(effs), min(effs), sum(c["feasible"] for c in cs)
for k in "abcd":
    m = R[k]["meta"]; ch = R[k]["probe"]["child"]["nominal"]; e = elem(ch, m["added"])
    cm, cw, cf = summ4(PC[k]["child"]); pm, pw, pf = summ4(PC[k]["parent"])
    drip = 1000 * (PC[k]["child"][0]["ripple"] - PC[k]["parent"][0]["ripple"])
    active = "yes" if e["util"] > 0.2 and e["i_rms_over_iload"] > 0.05 else ("weak" if e["util"] > 0.05 else "no")
    P(f"| {k} | {m['added']} ({e['kind']}) | {active} (U {e['util']:.2f}, {e['i_rms_over_iload']:.2f}) | {cm-pm:+.2f} | {cw-pw:+.2f} | {drip:+.0f} mV | {cf-pf:+d} | "
      f"{e['v_peak']:.1f} V, {e['i_peak']:.2f} A pk | {VERDICT[k]} |")

# ---------------- 2. per-element tables
P("\n## 2. Per-element currents, stress, loss (nominal, child duty)\n")
P("Added element in **bold**. i_mean of a capacitor is the charge-balance check (should be ≈ 0).\n")
for k in "abcd":
    m = R[k]["meta"]
    P(f"### ({k}) {m['title']} — child D = {m['duty']:.4f}\n")
    for role in ("child", "parent"):
        rec = R[k]["probe"][role]["nominal"]
        P(f"**{role}**: Vout {rec['vout']:.2f} V, η {100*rec['eff']:.2f} %, ripple {1000*rec['ripple']:.0f} mV, Pin {rec['pin']:.3f} W, total loss {1000*rec['loss_pin_minus_pout']:.0f} mW"
          + ("  (parent at the CHILD's duty: not re-refined)" if role == "parent" else ""))
        P("")
        P("| element | kind | I_rms A | I_peak A | I_mean A | I_rms/I_load | U | V_peak V | P_loss mW |")
        P("|---|---|---|---|---|---|---|---|---|")
        for e in rec["elements"]:
            b = "**" if (role == "child" and e["dev"] == m["added"]) else ""
            P(f"| {b}{e['dev']}{b} | {e['kind']} | {e['i_rms']:.3f} | {e['i_peak']:.3f} | {e['i_mean']:+.4f} | {e['i_rms_over_iload']:.2f} | {e['util']:.2f} | {e['v_peak']:.1f} | {1000*e['p_loss']:.1f} |")
        P("")

P("Notes. (d) parent at the child's duty: when Sa1 opens there is no path for the inductor current, so the ideal model produces an unbounded "
  "voltage spike (8×10⁵ V through Roff = 1 MΩ) and the per-element losses are numerically meaningless; that spike IS the reason the parent is not a converter. "
  "(d) child: C1 is charged to ≈ Vout and is discharged through Sa1 every time Sa1 closes; the only limit is Ron + ESR = 80 mΩ, hence the 6.5 A / 7.2 A peaks and the "
  "149 mW + 64 mW extra loss that put (d) 0.4 pp below the textbook buck. A real design would need a snubber or a resonant inductor here.\n")
# ---------------- 3. loss breakdown by kind
P("## 3. Loss breakdown by element kind (mW, nominal, child duty)\n")
P("| design | | switches | inductors | capacitors ESR | Cout ESR | total | Pin − Pout |")
P("|---|---|---|---|---|---|---|---|")
for k in "abcd":
    for role in ("child", "parent"):
        rec = R[k]["probe"][role]["nominal"]; d = kind_loss(rec)
        P(f"| {k if role=='child' else ''} | {role} | {1000*d.get('S',0):.1f} | {1000*d.get('L',0):.1f} | {1000*d.get('C',0):.1f} | {1000*d['Cout ESR']:.1f} | {1000*(rec['loss_elements']+rec['loss_cout_esr']):.1f} | {1000*rec['loss_pin_minus_pout']:.1f} |")
rec = R["ref"]["probe"]["child"]["nominal"]; d = kind_loss(rec)
P(f"| ref | textbook buck | {1000*d.get('S',0):.1f} | {1000*d.get('L',0):.1f} | {1000*d.get('C',0):.1f} | {1000*d['Cout ESR']:.1f} | {1000*(rec['loss_elements']+rec['loss_cout_esr']):.1f} | {1000*rec['loss_pin_minus_pout']:.1f} |")

# ---------------- 4. load transient
P("\n## 4. Load-step transient (R_out 50 → 25 Ω at 20 ms, back to 50 Ω at 28 ms; fixed duty, open loop)\n")
P("| design | | step UP: undershoot V | overshoot V | settle to 1 % ms | step DOWN: overshoot V | undershoot V | settle ms | ΔVout steady (open-loop droop) V |")
P("|---|---|---|---|---|---|---|---|---|")
for k in list("abcd") + ["ref"]:
    for role in ("child", "parent"):
        if role not in R[k]["transient"]: continue
        tr = R[k]["transient"][role]; u, dn = tr["step_up"], tr["step_down"]
        P(f"| {k if role=='child' else ''} | {role} | {u['undershoot']:.2f} | {u['overshoot']:.2f} | {1000*u['settle_1pct_s']:.2f} | {dn['overshoot']:.2f} | {dn['undershoot']:.2f} | {1000*dn['settle_1pct_s']:.2f} | {u['v_post']-u['v_pre']:+.2f} |")

# ---------------- 5. load / line sweep
P("\n## 5. Load and line sweep (duty re-refined to 50 V at each point; η % / ripple mV)\n")
tags = [("load_R200", "0.25× load (200 Ω)"), ("load_R100", "0.5× (100 Ω)"), ("load_R50", "1× (50 Ω)"), ("load_R33.333", "1.5× (33 Ω)"), ("line_V90", "VIN 90 V"), ("line_V110", "VIN 110 V")]
P("| design | | " + " | ".join(t[1] for t in tags) + " |")
P("|---|---|" + "---|" * len(tags))
for k in list("abcd") + ["ref"]:
    for role in ("child", "parent"):
        if role not in R[k]["spec"]: continue
        cells = []
        for tg, _ in tags:
            s = R[k]["spec"][role][tg]
            cells.append((f"{100*s['eff']:.2f} / {1000*s['ripple']:.0f}" if s["feasible"] else f"FAIL ({s['reason'][:22]})"))
        P(f"| {k if role=='child' else ''} | {role} | " + " | ".join(cells) + " |")

P("Note: (c) child at 0.25× load reads 99.99 %, which is unphysical (≈1 mW loss at 12.5 W); the same bench family produced a 122 % child during the run. "
  "Treat light-load efficiencies from the duty-refined sweep as ±0.3 pp; the fixed-duty probe numbers in §2 are the reliable ones.\n")
# ---------------- 6. tolerance grid
P("\n## 6. Component-tolerance grid: L ±10 %, C (and Cout) ±20 %, Ron ×0.5 / ×2 → 8 combinations, duty re-refined\n")
P("| design | | feasible / 8 | η min–max % | ripple max mV | worst combination |")
P("|---|---|---|---|---|---|")
for k in list("abcd") + ["ref"]:
    for role in ("child", "parent"):
        if role not in R[k]["spec"]: continue
        tol = {t: s for t, s in R[k]["spec"][role].items() if t.startswith("tol_")}
        nf = sum(s["feasible"] for s in tol.values()); effs = [100 * s["eff"] for s in tol.values() if s["feasible"]]
        worst = min(tol.items(), key=lambda kv: (kv[1]["feasible"], kv[1]["eff"]))[0].replace("tol_", "")
        P(f"| {k if role=='child' else ''} | {role} | {nf}/8 | {min(effs):.2f}–{max(effs):.2f} | {max(1000*s['ripple'] for s in tol.values() if s['feasible']):.0f} | {worst} |"
          if effs else f"| {k if role=='child' else ''} | {role} | {nf}/8 | – | – | all fail |")

# ---------------- 7. value sweeps
P("\n## 7. Does the gain depend on a tuned value? (fixed child duty, nominal corner)\n")
P("(d) C1 value sweep, child:\n")
P("| C1 | Vout V | η % | ripple mV | i_C1 rms A | i_Sa1 rms A | U(C1) | U(Sa1) |")
P("|---|---|---|---|---|---|---|---|")
for tg in ["nominal"] + [f"C1x{s}" for s in (0.1, 0.25, 0.5, 2.0, 4.0, 10.0)]:
    rec = R["d"]["probe"]["child"].get(tg)
    if not rec or "error" in rec: P(f"| {tg} | error |"); continue
    c1, s1 = elem(rec, "C1"), elem(rec, "Sa1"); lab = "10 µF (as run)" if tg == "nominal" else f"{10*float(tg[3:]):g} µF"
    P(f"| {lab} | {rec['vout']:.2f} | {100*rec['eff']:.2f} | {1000*rec['ripple']:.0f} | {c1['i_rms']:.3f} | {s1['i_rms']:.3f} | {c1['util']:.2f} | {s1['util']:.2f} |")
P("\n(a) L1 value sweep, child:\n")
P("| L1 | Vout V | η % | ripple mV | i_L0 rms A | i_L1 rms A |")
P("|---|---|---|---|---|---|")
for tg in ["L1x0.5", "nominal", "L1x2.0"]:
    rec = R["a"]["probe"]["child"][tg]; lab = "500 µH (as run)" if tg == "nominal" else f"{500*float(tg[3:]):g} µH"
    P(f"| {lab} | {rec['vout']:.2f} | {100*rec['eff']:.2f} | {1000*rec['ripple']:.0f} | {elem(rec,'L0')['i_rms']:.3f} | {elem(rec,'L1')['i_rms']:.3f} |")

# ---------------- 8. equivalent-circuit reductions
P("\n## 8. Equivalent-circuit reductions (fixed child duty, nominal corner)\n")
P("| design | variant | Vout V | η % | ripple mV | reading |")
P("|---|---|---|---|---|---|")
def row(k, role, tag, label, note):
    rec = R[k]["probe"][role].get(tag)
    if not rec or "error" in rec: P(f"| {k} | {label} | error | | | {rec.get('error','')[:60] if rec else 'missing'} |"); return
    P(f"| {k} | {label} | {rec['vout']:.2f} | {100*rec['eff']:.2f} | {1000*rec['ripple']:.0f} | {note} |")
row("a", "child", "nominal", "child: L0 ∥ L1 (2 × 500 µH, 2 × 0.25 Ω)", "")
row("a", "parent", "nominal", "parent: single 500 µH", "")
row("a", "parent", "merged_L0=250uH_DCR0.125", "parent with L0 = 250 µH, DCR 0.125 Ω (exact parallel equivalent)", "≡ child ⇒ the child IS a buck with half L and half DCR")
row("a", "parent", "merged_L0=250uH_DCR0.25", "parent with L0 = 250 µH, DCR 0.25 Ω", "same ripple as child, parent's η ⇒ the η gain is the DCR halving, not the inductance")
row("b", "child", "nominal", "child", "")
row("b", "child", "C0_open", "child with C0 removed (= parent)", "identical ⇒ C0 redundant")
row("c", "child", "nominal", "child: C0 across OUT (+ bench Cout)", "")
row("c", "parent", "nominal", "parent (bench Cout only)", "")
row("c", "parent", "merged_Cout=20uF", "parent with bench Cout = 20 µF", "≡ child ⇒ C0 merges into the output cap")
row("c", "child", "Sb1_open", "child with idle Sb1 removed", "identical ⇒ Sb1 is dead (inherited from the parent)")
row("d", "child", "nominal", "child: L → OUT via Sa1 ∥ C1", "")
row("d", "parent", "nominal", "parent: C1 removed", "no freewheel path")
row("d", "child", "C1_shorted", "child with C1 shorted", "= plain buck")
row("d", "child", "Sa1_open", "child with Sa1 removed (L → C1 → OUT only)", "Vout = 0: a series capacitor blocks DC, so Sa1 is the DC path and C1 the freewheel path; both needed")

open(f"{OUT}/mech_verify.md", "w").write("\n".join(md) + "\n")
print("\n".join(md))

# ---------------- figure
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(2, 4, figsize=(17, 7.2))
loads = [(0.25, "load_R200"), (0.5, "load_R100"), (1.0, "load_R50"), (1.5, "load_R33.333")]
for j, k in enumerate("abcd"):
    ax = axs[0, j]
    for role, col, ls in (("child", "#b3261e", "-"), ("parent", "#1a1a1a", "--")):
        xs = [l for l, tg in loads if R[k]["spec"][role][tg]["feasible"]]
        ys = [100 * R[k]["spec"][role][tg]["eff"] for l, tg in loads if R[k]["spec"][role][tg]["feasible"]]
        ax.plot(xs, ys, ls, marker="o", color=col, label=f"{role}")
    xs = [l for l, tg in loads]; ax.plot(xs, [100 * R["ref"]["spec"]["child"][tg]["eff"] for _, tg in loads], ":", color="#888", label="textbook buck")
    ax.set_title(f"({k}) {R[k]['meta']['title']}", fontsize=9.5, loc="left"); ax.set_xlabel("load / rated"); ax.set_ylabel("efficiency %")
    ax.set_xticks([0.25, 0.5, 1.0, 1.5]); ax.grid(alpha=.3)
    if k == "d": ax.text(0.3, 60, "parent: infeasible at every load", fontsize=8, color="#1a1a1a")
    if j == 0: ax.legend(fontsize=8)
    ax2 = axs[1, j]
    for role, col in (("child", "#b3261e"), ("parent", "#1a1a1a")):
        tr = R[k]["transient"][role]["trace"]; t = 1000 * np.array(tr["t"]); v = np.array(tr["v"])
        ax2.plot(t, v, color=col, lw=1.0, label=role, alpha=0.9 if role == "child" else 0.7)
    ax2.set_xlabel("time ms (load ×2 at 20 ms, back at 28 ms)"); ax2.set_ylabel("Vout V"); ax2.grid(alpha=.3)
    if k == "d": ax2.set_ylim(0, 60); ax2.text(20.5, 5, "parent never reaches 50 V", fontsize=8)
    else: ax2.set_ylim(44, 56)
    if j == 0: ax2.legend(fontsize=8)
fig.suptitle("Child (red) vs nearest training parent (black): efficiency vs load with duty re-refined per point (top) and open-loop load-step response at fixed duty (bottom)", fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig(f"{OUT}/fig_mech_sweeps.png", dpi=160); print("fig saved")
