"""Clean (real_A) vs noisy (real_B) subset breakdown of the E15 untouched real set.

Reads the frozen E15 real manifest, the Drift-Sense (no-exit) predictions and the E16 ZNCC
predictions; scores success@5 per stratum with DS R1 (tau 0.2617101) and ZNCC (tau 0.36530551),
and reports the paired gap ZNCC minus DS with a tile-cluster percentile bootstrap
(B = 2000, seed 20261010, clusters = group_id), matching the E15/E16 convention.
Writes results/e16/ab_breakdown.json. Run from the repo root:
    python3 -I code/e16_ab_breakdown.py
"""
import csv
import json
import math

import numpy as np

ROOT = "results/"
MANIFEST = ROOT + "e15_real/manifest_real.csv"
DS_PRED = ROOT + "e15_real/pred_real_noexit.csv"
ZNCC_PRED = ROOT + "e16/pred_real_zncc_ms.csv"
OUT = ROOT + "e16/ab_breakdown.json"
TAU_DS = 0.2617101
TAU_ZNCC = 0.36530551314353943
TOL_PX = 5.0
B = 2000
SEED = 20261010


def load(path):
    with open(path, newline="") as f:
        return {r["pair_id"]: r for r in csv.DictReader(f)}


def main():
    man = load(MANIFEST)
    ds = load(DS_PRED)
    zn = load(ZNCC_PRED)
    rows = {"real_A": [], "real_B": []}
    for pid, m in man.items():
        if int(float(m["found"])) != 1:
            continue
        gx, gy = float(m["gt_x"]), float(m["gt_y"])
        d, z = ds[pid], zn[pid]
        ok_ds = float(d["score"]) >= TAU_DS and math.hypot(float(d["x"]) - gx, float(d["y"]) - gy) <= TOL_PX
        ok_z = float(z["score"]) >= TAU_ZNCC and math.hypot(float(z["x"]) - gx, float(z["y"]) - gy) <= TOL_PX
        rows[m["stratum"]].append((m["group_id"], float(ok_ds), float(ok_z)))

    out = {"description": "E15 untouched real set, present pairs only: success@5 of DS R1 and "
                          "frozen ZNCC per stratum; gap = ZNCC minus DS.",
           "inputs": [MANIFEST, DS_PRED, ZNCC_PRED],
           "tau_ds": TAU_DS, "tau_zncc": TAU_ZNCC, "tol_px": TOL_PX,
           "bootstrap": {"B": B, "seed": SEED, "unit": "tile (group_id)", "method": "percentile"},
           "strata": {}}
    for st, sel in rows.items():
        groups = sorted(set(g for g, _, _ in sel))
        gi = {g: i for i, g in enumerate(groups)}
        g = np.array([gi[x[0]] for x in sel])
        dd = np.array([x[1] for x in sel])
        zz = np.array([x[2] for x in sel])
        K = len(groups)
        cnt = np.bincount(g, minlength=K).astype(float)
        sd = np.bincount(g, weights=dd, minlength=K)
        sz = np.bincount(g, weights=zz, minlength=K)
        idx = np.random.default_rng(SEED).integers(0, K, size=(B, K))
        gaps = [(sz[b].sum() - sd[b].sum()) / cnt[b].sum() for b in idx]
        lo, hi = np.percentile(gaps, [2.5, 97.5])
        out["strata"][st] = {
            "n_present": len(sel), "n_tiles": K,
            "success5_ds": float(dd.mean()), "success5_zncc": float(zz.mean()),
            "gap_zncc_minus_ds": float(zz.mean() - dd.mean()),
            "gap_ci95": [float(lo), float(hi)],
        }
    allsel = rows["real_A"] + rows["real_B"]
    out["all_present"] = {"n_present": len(allsel),
                          "gap_zncc_minus_ds": float(np.mean([x[2] for x in allsel]) - np.mean([x[1] for x in allsel]))}
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
