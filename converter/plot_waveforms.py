#!/usr/bin/env python3
"""Switching waveforms for one converter from circuits/discovered_converters_table.json.

Answers "how does this circuit switch?": gate drives, switching-node voltage,
every inductor / capacitor / switch current, and Vout, over the last N periods
of the settled transient. Uses the same ngspice probe deck as mech_verify.py.

Usage (from this folder):
    python plot_waveforms.py a            # discovered circuit of panel (a) = D1
    python plot_waveforms.py a --parent   # its nearest LaMAGIC parent
    python plot_waveforms.py b --periods 4 --out ../results/waveforms
    python plot_waveforms.py --netlist "Sb0 n1 0; L0 n1 OUT; Sa0 IN n1; C0 IN OUT" --duty 0.5

Keys a..d follow the table JSON and the paper figure (left-to-right, top-to-bottom):
    a = conv_g20_v6_s0 #00  (D1, +L1)         b = conv_g20_v6_s0 #09  (D2, +C1)
    c = conv_fnov_rule_s0 #00 (D3)             d = conv_fnov_rule_s0 #01 (D4)
Needs matplotlib (conda env `analog`), numpy, ngspice on PATH.
"""
import os as _os, sys as _sys
_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
_sys.path.insert(0, _os.path.join(_ROOT, "converter"))
import os, sys, json, argparse
import numpy as np
import bench
import mech_verify as mv

TAB = os.path.join(_ROOT, "circuits", "discovered_converters_table.json")


def load_case(key, parent):
    tab = json.load(open(TAB))
    row = tab[f"{key}|{'train' if parent else 'disc'}"]
    corners = eval(row["corners"]) if isinstance(row["corners"], str) else row["corners"]
    duty = corners[0].get("duty", 0.5)          # nominal corner's refined duty
    return row["netlist"], duty, row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("key", nargs="?", help="a|b|c|d from the table JSON")
    ap.add_argument("--parent", action="store_true", help="plot the nearest LaMAGIC parent instead")
    ap.add_argument("--netlist", help="explicit netlist 'Sa0 IN n1; Sb0 n1 0; ...'")
    ap.add_argument("--duty", type=float, default=None)
    ap.add_argument("--periods", type=int, default=3)
    ap.add_argument("--out", default=os.path.join(_ROOT, "results", "waveforms"))
    a = ap.parse_args()

    if a.netlist:
        netlist, duty, name = a.netlist, a.duty or 0.5, "custom"
    else:
        if a.key not in "abcd":
            ap.error("key must be a, b, c or d (or give --netlist)")
        netlist, duty, row = load_case(a.key, a.parent)
        if a.duty is not None:
            duty = a.duty
        name = f"{a.key}_{'parent' if a.parent else 'discovered'}"
    nl = mv.parse(netlist)
    T = 1.0 / bench.FSW
    t_end = bench.SETTLE_PERIODS * T
    cols, elems, P, err = mv.run_probe(nl, duty, t_start=t_end - a.periods * T, t_end=t_end,
                                       pts=400)
    if cols is None:
        sys.exit(f"ngspice failed: {err}")
    stats = mv.element_stats(cols, elems, P)
    print(f"{name}: {netlist}")
    print(f"  duty {duty:.4f}  Vout {stats['vout']:.2f} V  eff {100*stats['eff']:.2f} %  "
          f"ripple {1e3*stats['ripple']:.0f} mV")
    for e in stats["elements"]:
        print(f"  {e['dev']:<4} Irms {e['i_rms']:.3f} A  Ipk {e['i_peak']:.3f} A  "
              f"util {e['util']:.2f}  Vpk {e['v_peak']:.1f} V  loss {1e3*e['p_loss']:.1f} mW")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = (cols["time"] - cols["time"][0]) * 1e6          # us from window start
    ton = duty * T
    gate_a = ((cols["time"] % T) < ton).astype(float)
    sw_nodes = sorted({e[2] for e in elems if e[1] == "S"} | {e[3] for e in elems if e[1] == "S"})
    sw_nodes = [n for n in sw_nodes if n not in ("0", "VIN", "VOUT")]

    fig, ax = plt.subplots(5, 1, figsize=(9, 11), sharex=True)
    ax[0].step(t, gate_a, where="post", label="Sa* gate (phase a)")
    ax[0].step(t, 1 - gate_a, where="post", label="Sb* gate (phase b)")
    ax[0].set_ylabel("gate"); ax[0].legend(loc="upper right", fontsize=8)
    for n in sw_nodes:
        ax[1].plot(t, mv.vnode(cols, n), label=f"v({n})")
    ax[1].plot(t, cols["v(vout)"], "k--", lw=0.8, label="v(OUT)")
    ax[1].set_ylabel("node V"); ax[1].legend(loc="upper right", fontsize=8)
    for e in elems:
        if e[1] == "L":
            ax[2].plot(t, cols[e[4]], label=f"i({e[0]})")
    ax[2].set_ylabel("inductor A"); ax[2].legend(loc="upper right", fontsize=8)
    for e in elems:
        if e[1] == "S":
            ax[3].plot(t, cols[e[4]], label=f"i({e[0]})")
    ax[3].set_ylabel("switch A"); ax[3].legend(loc="upper right", fontsize=8)
    for e in elems:
        if e[1] == "C":
            ax[4].plot(t, cols[e[4]], label=f"i({e[0]})")
    ax[4].plot(t, cols["i(vco)"], "k--", lw=0.8, label="i(Cout)")
    ax[4].set_ylabel("capacitor A"); ax[4].legend(loc="upper right", fontsize=8)
    ax[4].set_xlabel(f"time from window start (us), {a.periods} periods at {bench.FSW/1e3:.0f} kHz")
    fig.suptitle(f"{name}: {netlist}\nduty {duty:.4f}, Vout {stats['vout']:.2f} V, "
                 f"eff {100*stats['eff']:.2f} %", fontsize=9)
    fig.tight_layout()
    os.makedirs(a.out, exist_ok=True)
    png = os.path.join(a.out, f"waveforms_{name}.png")
    fig.savefig(png, dpi=150)
    json.dump({k: v for k, v in stats.items()}, open(png[:-4] + ".json", "w"), indent=1,
              default=float)
    print("  wrote", png)


if __name__ == "__main__":
    main()
