#!/usr/bin/env python3
"""Risk-coverage curves on the fresh confirmation split, written to riskcoverage.pdf.

Input:  ../../results/e6/riskcoverage_all_splits.csv (columns split, method, k, coverage, risk)
Output: riskcoverage.pdf next to this script (vector PDF, fonts embedded as TrueType)
Usage:  python3 plot_riskcoverage.py   (needs matplotlib)
Only the split 'confirm' is plotted. Curves are distinguished by colour AND line style,
so the figure stays readable in black and white.
"""
import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "..", "..", "predictions", "acceptance", "riskcoverage_all_splits.csv")
OUT_PATH = os.path.join(HERE, "riskcoverage.pdf")  # Figure 2 (written next to this script)

STYLES = [
    ("noexit", "Min rule (kept)", "black", "-", "o"),
    ("logistic", "Logistic", "0.35", "--", "s"),
    ("evt", "EVT", "0.6", ":", "^"),
]

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 6.5,
    "axes.labelsize": 6.5,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 6,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

series = {m: ([], []) for m, *_ in STYLES}
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["split"] != "confirm":
            continue
        if row["method"] in series:
            series[row["method"]][0].append(float(row["coverage"]))
            series[row["method"]][1].append(float(row["risk"]))

fig, ax = plt.subplots(figsize=(2.4, 2.0))
for method, label, color, ls, marker in STYLES:
    xs, ys = series[method]
    ax.plot(xs, ys, color=color, linestyle=ls, linewidth=1.2, label=label,
            marker=marker, markevery=max(1, len(xs) // 8), markersize=3)
ax.set_xlabel("Coverage (fraction of pairs accepted)")
ax.set_ylabel("Accepted-decision error")
ax.set_xlim(0, 1.0)
ax.set_ylim(0, 0.35)
ax.grid(True, linewidth=0.3, color="0.8")
ax.legend(frameon=False, loc="upper left")
fig.tight_layout()
fig.savefig(OUT_PATH, format="pdf")
print("wrote", OUT_PATH, {m: len(v[0]) for m, v in series.items()})
