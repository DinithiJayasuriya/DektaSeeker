#!/usr/bin/env python3
"""ONE-COLUMN (3.5 in) 2x2 figure of the four discovered converters, in the style of
discovered_amplifiers_1col.png (CCT_Generation/setup_tracer/scripts/make_four_amplifiers_1col.py):
bold text at one size (~7 pt printed), heavy ink lines, a numbered badge on the circuit and a two-line
legend under each circuit.

Same circuits and device names as draw_discovered_converters_4panel.py:
(a) conv_g20_v6_s0 (a)   parent train #9562  + L1
(b) conv_g20_v6_s0 (d)   parent train #10271 + C1
(c) conv_fnov_rule_s0 #00 parent train #55863 + L1, C0, Sa0, Sb1, C1
(d) conv_fnov_rule_s0 #01 parent train #4397  + L1, C0, Sa0, Sb0, L2
Numbers: discovered_converters_table.json (eff median over 4 corners; corners parent -> discovered).
Black = in the parent training circuit, red = added by the search. The test bench (V_IN source,
C_out, R_load) is left out to fit the column; Sa conducts during D, Sb during 1-D (say so in the caption).
Run:  ~/miniconda3/envs/analog/bin/python make_four_converters_1col.py
Badges = groups of added devices with ONE measured effect each, from
results/conv_validation_0918/ablate_added_{devices,chain}.md (devices added to the parent in badge order,
eff = median over the 4 corners, same scoring as the run).
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                                   # steergense_agent
INK, RED = "#1b2430", "#c0392b"                          # amplifier figure palette
GREY = "#555b63"                                         # dark grey for the corners line
BLUE, GREEN = "#1f5fa8", "#1e7b4f"                       # amplifier figure 2nd/3rd highlight colours
FS = 54                                                  # same text size as the amplifier figure
LW = 2.3 * 2.6                                           # amplifier wire weight (LW * THICK)
S_IN = 0.95                                              # inches per data unit (as amplifiers)
LEG = 1.05                                               # legend line pitch
T, YM = 3.6, 1.8                                         # top rail, mid level (ground = 0)
Y0, Y1 = -2.95, 7.95                                     # every cell: legend below ground, header on top


def wire(ax, pts, c=INK, z=2):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=c, lw=LW, solid_capstyle="round", solid_joinstyle="round", zorder=z)


def dot(ax, x, y, c=INK):
    ax.add_patch(plt.Circle((x, y), 0.13, color=c, zorder=5))


def txt(ax, x, y, s, ha="center", va="center", c=INK, italic=False):
    ax.text(x, y, s, ha=ha, va=va, fontsize=FS, fontweight="bold", color=c,
            style="italic" if italic else "normal", zorder=12)


def _ends(ax, p0, p1, blen, c):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    L = np.linalg.norm(p1 - p0); u = (p1 - p0) / L
    a, b = p0 + u * (L - blen) / 2, p1 - u * (L - blen) / 2
    wire(ax, [p0, a], c); wire(ax, [b, p1], c)
    return a, b, u, np.array([-u[1], u[0]])


def inductor(ax, p0, p1, c=INK):
    a, b, u, n = _ends(ax, p0, p1, 1.6, c)
    t = np.linspace(0, 1, 40); seg = (b - a) / 4
    for i in range(4):
        arc = a + seg * i + np.outer(t, seg) + np.outer(np.sin(np.pi * t) * 0.32, n)
        ax.plot(arc[:, 0], arc[:, 1], color=c, lw=LW, solid_capstyle="round", zorder=2)


def capacitor(ax, p0, p1, c=INK):
    a, b, u, n = _ends(ax, p0, p1, 0.26, c)
    for q in (a, b):
        wire(ax, [q - n * 0.5, q + n * 0.5], c, z=3)


def switch(ax, p0, p1, c=INK, flip=False):
    """open switch; lever from the p0 contact, tilted to the left of p0->p1 (right if flip)."""
    a, b, u, n = _ends(ax, p0, p1, 1.3, c)
    n = -n if flip else n
    wire(ax, [a, a + (b - a) * 0.97 + n * 0.45], c, z=3)
    for q in (a, b):
        ax.add_patch(plt.Circle(q, 0.13, facecolor="white", edgecolor=c, lw=0.55 * LW, zorder=4))


def ground(ax, x, y=0.0, c=INK):
    wire(ax, [(x, y), (x, y - 0.2)], c)
    for i, w in enumerate((0.5, 0.32, 0.14)):
        wire(ax, [(x - w, y - 0.2 - 0.17 * i), (x + w, y - 0.2 - 0.17 * i)], c)


def term(ax, x, y, s, side="left"):
    ax.add_patch(plt.Circle((x, y), 0.15, facecolor="white", edgecolor=INK, lw=0.8 * LW, zorder=6))
    if side == "left":
        txt(ax, x - 0.3, y, s, ha="right")
    else:
        txt(ax, x, y + 0.62, s, ha="center")


def badge(ax, x, y, n, color):
    ax.text(x, y, str(n), ha="center", va="center", fontsize=FS * 0.9, fontweight="bold", color="white",
            zorder=14, bbox=dict(boxstyle="circle,pad=0.18", facecolor=color, edgecolor="none"))


def legend(ax, x, items, corners):
    """items = [(n, text, colour)], then the parent->child corners line in italic dark grey."""
    tx = x + (0.95 if any(n for n, _, _ in items) else 0.05)
    for i, (n, t, c) in enumerate(items):
        y = -1.45 - LEG * i
        if n: badge(ax, x + 0.35, y, n, c)
        ax.text(tx, y, t, ha="left", va="center", fontsize=FS, fontweight="bold", color=c, zorder=12)
    ax.text(tx, -1.45 - LEG * len(items), corners, ha="left", va="center", fontsize=FS, fontweight="bold",
            style="italic", color=GREY, zorder=12)
    return len(items) + 1


def header(ax, x, s):
    ax.text(x, Y1 - 0.45, s, ha="left", va="center", fontsize=FS, fontweight="bold", color=INK, zorder=12)


TAB = json.loads((HERE / "discovered_converters_table.json").read_text())


def stats(k):
    p, d = TAB[f"{k}|train"], TAB[f"{k}|disc"]
    return d["eff_median"], f"Parent {p['feasible']}/4 → {d['feasible']}/4 corners"


# ------------------------------------------------------------------ (a) parallel inductor, train #9562
def draw_a(ax):
    xi, xn, sw, xo, xt = 0.9, 1.7, 4.3, 9.1, 10.4
    term(ax, xi, T, "IN"); wire(ax, [(xi, T), (xn, T)]); dot(ax, xn, T)
    switch(ax, (xn, T), (sw, T)); txt(ax, (xn + sw) / 2, T + 0.85, "Sa")
    dot(ax, sw, T); switch(ax, (sw, T), (sw, 0.25), flip=True); ground(ax, sw, 0.25)
    txt(ax, sw + 0.45, 1.9, "Sb", ha="left")
    inductor(ax, (sw, T), (xo, T)); txt(ax, (sw + xo) / 2, T - 0.8, "L0")
    wire(ax, [(sw, T), (sw, T + 1.35)], RED); inductor(ax, (sw, T + 1.35), (xo, T + 1.35), RED)
    wire(ax, [(xo, T + 1.35), (xo, T)], RED); txt(ax, (sw + xo) / 2, T + 2.05, "L1", c=RED)
    wire(ax, [(xn, T), (xn, T + 2.95)]); capacitor(ax, (xn, T + 2.95), (xo, T + 2.95))
    wire(ax, [(xo, T + 2.95), (xo, T + 1.35)]); dot(ax, xo, T + 1.35); txt(ax, (xn + xo) / 2 + 0.55, T + 3.7, "C0", ha="left")
    dot(ax, xo, T); wire(ax, [(xo, T), (xt, T)]); term(ax, xt, T, "OUT", side="top")
    e, cr = stats("a")
    n = legend(ax, -0.55, [(None, "L1: η 99.4 → 99.6 %", RED)], cr)          # 99.37 -> 99.60
    return (-0.6, 11.0, n)


# ------------------------------------------------------------------ (b) capacitor across Sa1, train #10271
def draw_b(ax):
    xi, xn, sw, n8, xo, xt = 0.9, 1.7, 4.4, 7.3, 10.1, 11.4
    term(ax, xi, T, "IN"); wire(ax, [(xi, T), (xn, T)]); dot(ax, xn, T)
    capacitor(ax, (xn, T), (xn, 0.25)); ground(ax, xn, 0.25); txt(ax, xn + 0.65, 1.9, "C0", ha="left")
    switch(ax, (xn, T), (sw, T)); txt(ax, (xn + sw) / 2, T + 0.85, "Sa")
    dot(ax, sw, T); switch(ax, (sw, T), (sw, 0.25), flip=True); ground(ax, sw, 0.25)
    txt(ax, sw + 0.45, 1.9, "Sb", ha="left")
    inductor(ax, (sw, T), (n8, T)); txt(ax, (sw + n8) / 2, T + 0.85, "L0")
    dot(ax, n8, T); switch(ax, (n8, T), (xo, T)); txt(ax, (n8 + xo) / 2, T - 0.95, "Sa1")
    wire(ax, [(n8, T), (n8, T + 1.45)], RED); capacitor(ax, (n8, T + 1.45), (xo, T + 1.45), RED)
    wire(ax, [(xo, T + 1.45), (xo, T)], RED); txt(ax, (n8 + xo) / 2 - 0.45, T + 2.3, "C1", c=RED, ha="right")
    dot(ax, xo, T); wire(ax, [(xo, T), (xt, T)]); term(ax, xt, T, "OUT", side="top")
    e, cr = stats("b")
    n = legend(ax, -0.55, [(None, "C1: Vout 29 → 50 V", RED)], cr)        # parent nominal Vout 28.8 V
    return (-0.6, 12.3, n)


# ------------------------------------------------------------------ (c) rule_s0 #00, train #55863
def draw_c(ax):
    xi, xn, n13, n15, xs, xo, xt = 0.9, 1.5, 4.0, 6.9, 7.9, 10.9, 12.2
    G1, G2, G3 = RED, BLUE, GREEN              # C0+Sb1 | Sa0 | L1, C1
    term(ax, xi, T, "IN"); wire(ax, [(xi, T), (xn, T)])
    switch(ax, (xn, T), (n13, T)); txt(ax, (xn + n13) / 2, T + 0.85, "Sb0")
    dot(ax, n13, T); switch(ax, (n13, T), (n15, T)); txt(ax, (n13 + n15) / 2, T + 0.85, "Sa2")
    dot(ax, n15, T); wire(ax, [(n15, T), (xs, T)]); dot(ax, xs, T)
    switch(ax, (xs, T), (xs, 0.25), flip=True); ground(ax, xs, 0.25); txt(ax, xs + 0.45, 1.3, "Sa1", ha="left")
    inductor(ax, (xs, T), (xo, T)); txt(ax, (xs + xo) / 2 + 0.2, T - 0.85, "L2")
    wire(ax, [(n13, T), (n13, T + 1.5)]); inductor(ax, (n13, T + 1.5), (xo, T + 1.5))
    wire(ax, [(xo, T + 1.5), (xo, T)]); txt(ax, (n13 + xo) / 2, T + 2.2, "L0")
    dot(ax, n13, T + 1.5); dot(ax, xo, T + 1.5)
    # added
    wire(ax, [(n13, T + 1.5), (n13, T + 3.0)], G3); inductor(ax, (n13, T + 3.0), (xo, T + 3.0), G3)
    wire(ax, [(xo, T + 3.0), (xo, T + 1.5)], G3); txt(ax, (n13 + xo) / 2, T + 3.7, "L1", c=G3)
    capacitor(ax, (n13, T), (n13, YM), G1); txt(ax, n13 - 0.65, 2.7, "C0", c=G1, ha="right")
    dot(ax, n13, YM, G1); switch(ax, (n13, YM), (n13, 0.25), G2); ground(ax, n13, 0.25, G2)
    txt(ax, n13 - 0.55, 0.95, "Sa0", c=G2, ha="right")
    switch(ax, (n13, YM), (n15, YM), G1, flip=True); txt(ax, (n13 + n15) / 2 + 0.2, YM + 0.8, "Sb1", c=G1)
    wire(ax, [(n15, YM), (n15, T)], G1); dot(ax, n15, YM, G1)
    dot(ax, xo, T); capacitor(ax, (xo, T), (xo, 0.25), G3); ground(ax, xo, 0.25, G3)
    txt(ax, xo + 0.65, 1.9, "C1", c=G3, ha="left")
    wire(ax, [(xo, T), (xt, T)]); term(ax, xt, T, "OUT", side="top")
    badge(ax, (n13 + n15) / 2 - 0.1, 0.75, 1, G1)
    badge(ax, 1.25, 1.85, 2, G2)
    badge(ax, (n13 + xo) / 2 + 1.35, T + 3.7, 3, G3)
    e, cr = stats("c")
    n = legend(ax, -0.5, [(1, "C0, Sb1: η 88.4 → 99.3 %", G1),   # 1/4 -> 4/4 corners
                          (2, "Sa0: η 99.3 → 99.6 %", G2),        # 99.31 -> 99.56
                          (3, "L1, C1: negligible", G3)], cr)     # 99.56 -> 99.64
    return (-0.5, 13.1, n)


# ------------------------------------------------------------------ (d) rule_s0 #01, train #4397
def draw_d(ax):
    xi, xn, n15, xr, n13, xo, xt = 0.9, 1.5, 3.9, 5.0, 7.8, 10.9, 12.2
    G1, G2, G3 = RED, BLUE, GREEN              # L2 | C0+Sb0 | Sa0, L1
    term(ax, xi, T, "IN"); wire(ax, [(xi, T), (xn, T)])
    switch(ax, (xn, T), (n15, T)); txt(ax, (xn + n15) / 2, T + 0.85, "Sb1")
    dot(ax, n15, T); switch(ax, (n15, T), (n15, 0.25)); ground(ax, n15, 0.25)
    txt(ax, n15 - 0.5, 1.9, "Sa1", ha="right")
    wire(ax, [(n15, T), (xr, T)]); dot(ax, xr, T)
    switch(ax, (xr, T), (n13, T)); txt(ax, (xr + n13) / 2 + 0.25, T + 0.85, "Sa2")
    dot(ax, n13, T); inductor(ax, (n13, T), (xo, T)); txt(ax, (n13 + xo) / 2 + 0.3, T + 0.85, "L0")
    dot(ax, xo, T); capacitor(ax, (xo, T), (xo, 0.25)); ground(ax, xo, 0.25)
    txt(ax, xo + 0.65, 1.9, "C1", ha="left")
    # added
    wire(ax, [(n13, T), (n13, T + 1.6)], G3); inductor(ax, (n13, T + 1.6), (xo, T + 1.6), G3)
    wire(ax, [(xo, T + 1.6), (xo, T)], G3); txt(ax, (n13 + xo) / 2 + 0.3, T + 2.35, "L1", c=G3)
    wire(ax, [(n15, T), (n15, T + 3.15)], G1); inductor(ax, (n15, T + 3.15), (xo, T + 3.15), G1)
    wire(ax, [(xo, T + 3.15), (xo, T + 1.6)], G1); dot(ax, xo, T + 1.6, G1)
    txt(ax, (n15 + xo) / 2, T + 3.9, "L2", c=G1)
    capacitor(ax, (n13, T), (n13, YM), G2); txt(ax, n13 + 0.65, 2.7, "C0", c=G2, ha="left")
    dot(ax, n13, YM, G2); switch(ax, (n13, YM), (n13, 0.25), G3, flip=True); ground(ax, n13, 0.25, G3)
    txt(ax, n13 + 0.45, 0.95, "Sa0", c=G3, ha="left")
    switch(ax, (xr, YM), (n13, YM), G2, flip=True); txt(ax, (xr + n13) / 2 - 0.4, YM + 0.8, "Sb0", c=G2)
    wire(ax, [(xr, YM), (xr, T)], G2); dot(ax, xr, YM, G2)
    wire(ax, [(xo, T), (xt, T)]); term(ax, xt, T, "OUT", side="top")
    badge(ax, 2.7, T + 2.35, 1, G1)
    badge(ax, (xr + n13) / 2 - 0.3, 0.75, 2, G2)
    badge(ax, n13 + 0.6, T + 2.35, 3, G3)
    e, cr = stats("d")
    n = legend(ax, -0.5, [(1, "L2: Vout 0 → 50 V", G1),           # parent ignores duty; +L2: 1/4, 88.5 %
                          (2, "C0, Sb0: η 88.5 → 99.3 %", G2),   # 1/4 -> 4/4 corners
                          (3, "Sa0, L1: η 99.3 → 99.5 %", G3)], cr)  # 99.33 -> 99.45
    return (-0.5, 13.1, n)


if __name__ == "__main__":
    rows = [[draw_a, draw_b], [draw_c, draw_d]]
    scratch = plt.figure()
    wins = [[f(scratch.add_subplot()) for f in row] for row in rows]
    plt.close(scratch)
    GAP = 0.35
    widths = [sum(w[1] - w[0] for w in r) + GAP for r in wins]
    y0s = [-1.45 - LEG * (max(w[2] for w in r) - 1) - 0.6 for r in wins]   # room for the longest legend in the row
    hs = [Y1 - y0 for y0 in y0s]
    W = max(widths)
    FH = sum(hs) + GAP
    fig = plt.figure(figsize=(S_IN * W, S_IN * FH), facecolor="white")
    for r, (row, rw) in enumerate(zip(rows, wins)):
        y = (hs[1] + GAP) if r == 0 else 0.0
        extra = W - (sum(w[1] - w[0] for w in rw) + GAP)
        x = 0.0
        for f, w in zip(row, rw):
            ww = (w[1] - w[0]) + extra / 2
            ax = fig.add_axes([x / W, y / FH, ww / W, hs[r] / FH])
            f(ax)
            ax.set_xlim(w[0], w[0] + ww); ax.set_ylim(y0s[r], Y1)
            ax.set_aspect("equal"); ax.axis("off")
            x += ww + GAP
    print("row widths", [round(v, 2) for v in widths], "-> print text size at 3.5 in: %.1f pt" % (FS * 3.5 / (S_IN * W)))
    for dst in (HERE / "discovered_converters_1col",):
        fig.savefig(dst.with_suffix(".png"), dpi=150, facecolor="white", bbox_inches="tight", pad_inches=0.03)
        fig.savefig(dst.with_suffix(".pdf"), facecolor="white", bbox_inches="tight", pad_inches=0.03)
        print("wrote", dst.with_suffix(".png"))
