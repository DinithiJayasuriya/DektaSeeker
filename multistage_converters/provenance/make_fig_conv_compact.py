"""fig:conv-48v (four 48 V -> 3 V converters), compact version in the paper's common figure format.

Same circuits, drawers and numbers as protocol_v90/figures/plot_converters_advantage_fig7.py (left untouched; this file
imports its drawers and primitive overrides). Changes: STIX serif bold text everywhere (like Figs. 2-6/8), tighter
spacing below each circuit, (a)-(d) at the bottom-left instead of the black #1-#4 tags, one compact text block.

  <python with schemdraw 0.19> figs/source/make_fig_conv_compact.py      (from the project root)

Writes figs/fig_conv_compact.{png,pdf}.
"""
import sys
from pathlib import Path

SRC = Path("/mnt/ssd1/dinithi/CCT_Generation/Deltaseeker_dpo/rsi_v6/protocol_v90/figures")
sys.path.insert(0, str(SRC))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import schemdraw

import plot_converters_advantage_fig7 as F7      # applies the fig7 primitive overrides (hump inductors, open OUT)  # noqa: E402

OUT = Path(__file__).resolve().parents[1]
INK, RED, GREY = "#111111", "#c0392b", "#4a4f5a"
STAGE_C = "#1b2f6e"   # dashed stage boxes (dark blue, distinct from the red highlights)
CFS = 15           # one font size for every text element (component labels, result line, detail line, panel label)
FS = CFS
schemdraw.config(fontsize=CFS, lw=2.4, font="STIXGeneral")
plt.rcParams.update({"font.family": "serif", "font.serif": ["STIXGeneral"], "mathtext.fontset": "stix",
                     "font.weight": "bold"})
for m in (F7.B, F7.V4, F7.R1, F7.NR, F7.A):
    if hasattr(m, "FS"):
        m.FS = CFS


# ---- (a) redrawn with shorter wire runs (same components, same connections, same red highlight) so its width
#      matches (c) and both rows have equal length. Mirrors V4.sc21(bus_cap=False) + A.st_mid_flycap + V4.st_buck.
BOUNDS = {}   # panel -> x positions where each generated stage starts/ends (recorded by the drawers below)
GAP_EXTRA = 0.5   # staged figure only: extra plain wire after each capped bus, so the stage boxes have a clean gap
# Measured average bus voltages (nominal point, v90 48 V -> 3 V bench exported as in protocol_v90/run_camp.sh, rsi/judge_sys._bus_check
# on the unreduced 'core' netlists of reduction/final_all48_1114.json records 129 / 28 / 24 / 27; all pass "every stage converts").
VCHAIN = {"a": [48, 24, 7.1, 3], "b": [48, 22, 3], "c": [48, 6.1, 3], "d": [48, 25, 3]}
STRIP = 0.75      # height of the conversion strip at the bottom of each stage box


def f9_staged(d):      # = plot_converters_advantage.f9, recording the stage boundary
    A, V4 = F7.A, F7.V4
    x1 = V4.hybrid_flycap(d); A.wire(d, [(x1, 4), (x1 + GAP_EXTRA, 4)]); x1 += GAP_EXTRA
    out = V4.st_buck(d, x1, hi="Sa1", lo="Sb0"); A.load(d, out)
    BOUNDS["b"] = [0.0, x1, out[0] + 1.0]


def f7_staged(d):      # = plot_converters_advantage.f7
    A, NR = F7.A, F7.NR
    x1 = NR.buck1(d); A.wire(d, [(x1, 4), (x1 + GAP_EXTRA, 4)]); x1 += GAP_EXTRA
    out = NR.st_f7(d, x1); A.load(d, out)
    BOUNDS["c"] = [0.0, x1, out[0] + 1.0]


def f8_staged(d):      # = plot_converters_advantage.f8
    A, V4, R1 = F7.A, F7.V4, F7.R1
    x1 = R1.current_fed(d); A.wire(d, [(x1, 4), (x1 + GAP_EXTRA, 4)]); x1 += GAP_EXTRA
    out = V4.st_buck(d, x1, hi="Sa1", lo="Sb0"); A.load(d, out)
    BOUNDS["d"] = [0.0, x1, out[0] + 1.0]


def f57_compact(d, extra=0.0):
    A, V4, R = F7.A, F7.V4, F7.RED
    sw, ind, cap, wire, dot, gnd, tag = A.sw, A.ind, A.cap, A.wire, A.dot, A.gnd, A.tag
    s1, s2 = 2.0, 2.0                                       # stage 1 (2:1 SC): was 2.4 / 2.4
    V4.vin(d)
    sw(d, (0, 4), "right", s1, "Sa0", loc="top"); dot(d, (s1, 4))
    sw(d, (s1, 4), "right", s2, "Sb0", loc="top"); dot(d, (s1 + s2, 4))
    cap(d, (s1, 4), "down", 2, "C0", loc="bot"); dot(d, (s1, 2))
    sw(d, (s1, 2), "down", 2, "Sb1", loc="bot"); gnd(d, (s1, 0))
    sw(d, (s1, 2), "right", s2, "Sa1", loc="bot"); wire(d, [(s1 + s2, 2), (s1 + s2, 4)])
    xb = s1 + s2 + 0.8                                      # was +1.2
    wire(d, [(s1 + s2, 4), (xb, 4)]); tag(d, (xb, 4.55), "bus")
    x0 = xb + 0.5; wire(d, [(xb, 4), (x0, 4)])              # was +0.8
    a = x0 + 2.0; b = a + 2.4                               # stage 2 (flying cap): was 2.4 / 2.8
    sw(d, (x0, 4), "right", 2.0, "Sa0", c=R, loc="top"); dot(d, (a, 4), R)
    sw(d, (a, 4), "right", 2.4, "Sb0", c=R, loc="top")
    cap(d, (a, 4), "down", 2, "C0", c=R, loc="bot"); dot(d, (a, 2), R)
    sw(d, (a, 2), "down", 2, "Sb1", c=R, loc="bot"); gnd(d, (a, 0), R)
    ind(d, (a, 2), "right", 2.4, "L0", c=R, loc="bot"); wire(d, [(b, 2), (b, 4)], R)
    dot(d, (b, 4)); wire(d, [(b, 4), (b + 0.8, 4)])         # was +1.0
    cap(d, (b + 0.8, 4), "down", 4, "C2", loc="bot"); gnd(d, (b + 0.8, 0)); dot(d, (b + 0.8, 4))
    tag(d, (b + 0.8, 4.55), "bus2")
    x2 = b + 1.3 + extra; wire(d, [(b + 0.8, 4), (x2, 4)])          # was +1.6
    sw(d, (x2, 4), "right", 2.0, "Sa0", loc="top"); c3 = x2 + 2.0; dot(d, (c3, 4))   # stage 3 (buck): was 2.4 / 3.0 (now 2.0 / 2.4)
    sw(d, (c3, 4), "down", 4, "Sb0", loc="bot"); gnd(d, (c3, 0))
    ind(d, (c3, 4), "right", 2.4, "L0", loc="top")
    A.load(d, (c3 + 2.4, 4))
    BOUNDS["a"] = [0.0, x0, x2, c3 + 2.4 + 1.0]     # 2:1 SC | flying-cap middle | buck (generator stages)


def main(stages=False):
    assert F7.COL1[0][0] is F7.A.f57
    # (b) F9: positive, bench-measured comparison against the named buck->buck reference (corners_advantage_1114.json):
    #   eta above buck->buck at all 4 corners (96.86/93.97/98.34/96.82 vs 96.57/93.66/97.93/96.48 %), peak |Vds| 26 V vs 48 V.
    #   It does NOT beat the 2:1 / 4:1 SC+buck references, so the line names buck->buck explicitly.
    assert F7.COL2[0][0] is F7.A.f9
    b9 = (F7.A.f9, "η above buck→buck at all 4 corners", "η 96.8 %  ·  switches 26 V vs 48 V")
    grid = [[(f57_compact,) + tuple(F7.COL1[0][1:]), b9], [F7.COL1[1], F7.COL2[1]]]
    if stages:                                   # same circuits, drawers that record stage boundaries
        f57_staged = lambda d: f57_compact(d, extra=GAP_EXTRA)
        grid = [[(f57_staged,) + grid[0][0][1:], (f9_staged,) + grid[0][1][1:]],
                [(f7_staged,) + grid[1][0][1:], (f8_staged,) + grid[1][1][1:]]]
    bbs = [[F7.bbox(c[0]) for c in row] for row in grid]
    TXT = 2.25                                         # data units below each drawing for the two text lines
    colw = [max(bbs[r][c].xmax - bbs[r][c].xmin for r in range(2)) + 0.3 for c in range(2)]
    rowh = [max(bbs[r][c].ymax - bbs[r][c].ymin for c in range(2)) + TXT + (0.95 + STRIP if stages else 0.1) for r in range(2)]
    k = 0.42
    fig = plt.figure(figsize=(k * (sum(colw) + 0.4), k * sum(rowh)))
    gs = fig.add_gridspec(2, 2, width_ratios=colw, height_ratios=rowh, wspace=0.02, hspace=0.0)
    for n, (r, c) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
        fn, res, sub = grid[r][c]; bb = bbs[r][c]
        sym = lambda t: t.replace("≥", r"$\geq$").replace("≤", r"$\leq$").replace("→", r"$\rightarrow$")   # glyphs missing in STIX text font
        ax = fig.add_subplot(gs[r, c])
        d = schemdraw.Drawing(canvas=ax, show=False); fn(d); d.draw(show=False)
        for t in ax.texts:                              # component labels -> bold serif
            t.set_fontfamily("serif"); t.set_fontweight("bold")
        ax.set_aspect("equal"); ax.axis("off")
        x0 = bb.xmin - 0.15; ytop = bb.ymax + (0.95 if stages else 0.1)
        ax.set_xlim(x0, x0 + colw[c]); ax.set_ylim(ytop - rowh[r], ytop)
        yb = bb.ymin - 0.25 - (STRIP if stages else 0)
        if stages:                               # dashed box per generated stage; bus node + bus cap left in the gap
            from matplotlib.patches import Rectangle
            buses = sorted(t.get_position()[0] for t in ax.texts if t.get_text() in ("bus", "bus2"))
            capped = {"a": [False, True], "b": [True], "c": [True], "d": [True]}["abcd"[n]]
            x_in, x_out = bb.xmin + 0.55, bb.xmax - 1.2    # after the IN tag / before the OUT terminal line
            # text extents in data units (for placing edges in the clearest spot between labels)
            ax.apply_aspect(); rend = fig.canvas.get_renderer(); inv = ax.transData.inverted()   # final transform first
            tx = [inv.transform(t.get_window_extent(rend)) for t in ax.texts if t.get_text().strip()]
            spans = [(min(p[0][0], p[1][0]), max(p[0][0], p[1][0])) for p in tx]

            def clearest(lo, hi):
                cands = [lo + i * (hi - lo) / 60 for i in range(61)]
                score = lambda x: min([0 if a_ <= x <= z_ else min(abs(x - a_), abs(x - z_)) for a_, z_ in spans] or [9])
                return max(cands, key=score)
            edges = [x_in]
            starts = BOUNDS["abcd"[n]][1:-1]           # x where each following stage's first element begins
            for xb_, cp, st in zip(buses, capped, starts):
                edges += ([xb_ - 0.5, xb_ + 1.25] if cp
                          else [xb_ - 0.6, xb_ + 0.6])   # uncapped bus: just clear the "bus" tag
            edges += [x_out]
            y0b, y1b = bb.ymin - 0.05 - STRIP, bb.ymax + 0.55
            vc = VCHAIN["abcd"[n]]
            for k in range(len(edges) // 2):
                xa, xz = edges[2 * k], edges[2 * k + 1]
                ax.add_patch(Rectangle((xa, y0b), xz - xa, y1b - y0b, fill=False, ls=(0, (4, 3)), lw=1.6,
                                       ec=STAGE_C, zorder=0.5))
                ax.text((xa + xz) / 2, y1b, f"Stage {k + 1}", ha="center", va="center", fontsize=FS, fontweight="bold",
                        color=STAGE_C, bbox=dict(fc="white", ec="none", pad=1.5), zorder=6)
                ax.text((xa + xz) / 2, y0b + STRIP / 2, f"{vc[k]:g} V $\\rightarrow$ {vc[k + 1]:g} V", ha="center",
                        va="center", fontsize=FS, fontweight="bold", color=STAGE_C, zorder=6)
        ax.text(x0 + 0.05, yb, f"({'abcd'[n]})", fontsize=FS, fontweight="bold", color=INK, va="top", ha="left")
        ax.text(x0 + 1.25, yb, sym(res), fontsize=FS, fontweight="bold",
                color=(GREY if res == "No advantage claimed" else RED), va="top", ha="left")
        ax.text(x0 + 1.25, yb - 1.05, sym(sub), fontsize=FS, fontweight="bold", color=GREY, va="top", ha="left",
                style="italic")
    name = "fig_conv_stages" if stages else "fig_conv_compact"
    fig.savefig(OUT / f"{name}.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight", pad_inches=0.02)
    print("wrote", OUT / f"{name}.{{png,pdf}}", "size in", fig.get_size_inches().round(2))


if __name__ == "__main__":
    main(stages="--stages" in sys.argv)
