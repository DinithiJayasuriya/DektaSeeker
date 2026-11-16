#!/usr/bin/env python3
"""Plot a waveform dump written by run_design.py --waves (needs numpy + matplotlib).

  python3 tools/plot_waves.py results/waves/waves_c_F7_nominal.txt            # -> same name .png
  python3 tools/plot_waves.py results/waves/waves_c_F7_nominal.txt --periods 3
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("file")
ap.add_argument("--periods", type=float, default=4, help="how many 2 us switching periods to show (from the end)")
a = ap.parse_args()
cols = Path(a.file).read_text().splitlines()[0].split()
X = np.loadtxt(a.file, skiprows=1)
t = X[:, 0]
keep = t >= t[-1] - a.periods * 2e-6
t = (t[keep] - t[keep][0]) * 1e6
V = [i for i, c in enumerate(cols) if c.startswith("v(") and c != "v(VIN)"]
I = [i for i, c in enumerate(cols) if c.startswith("@") or c.startswith("i(")]
fig, ax = plt.subplots(3, 1, figsize=(9, 8), sharex=True)
for i in V:
    ax[0].plot(t, X[keep, i], label=cols[i], lw=1)
ax[0].set_ylabel("node voltage (V)"); ax[0].legend(fontsize=7, ncol=4)
out = cols.index("v(VOUT)")
ax[1].plot(t, 1e3 * (X[keep, out] - X[keep, out].mean()), color="k", lw=1)
ax[1].set_ylabel("Vout - mean (mV)")
for i in I:
    ax[2].plot(t, X[keep, i], label=cols[i], lw=1)
ax[2].set_ylabel("current (A)"); ax[2].set_xlabel("time (us)"); ax[2].legend(fontsize=7, ncol=4)
fig.suptitle(Path(a.file).stem)
fig.tight_layout()
png = Path(a.file).with_suffix(".png")
fig.savefig(png, dpi=130)
print("wrote", png)
