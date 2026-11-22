"""E18 scorer: merge and score the distorted-search runs, mid and high, plus the undistorted E15/E16 contrasts.

Exploratory, post-registration (docs/PLAN_E18.md). Metrics come from code/e15_eval.py (same definitions as E15/E16).
Frozen constants: Drift-Sense R1 tau 0.2617101, gate delta 0.09562161564826965 (code/e15_thresholds.json);
ZNCC tau 0.36530551314353943 (results/e16/e16_baseline.json). The second ZNCC tau (TAU_E17) is required on the
command line and is recorded in PLAN_E18.md section 7 before scoring.

Usage:
  python3 -X utf8 -B code/e18_eval.py --config paths.json --tau-e17 X --out results/e18/eval_e18.json
paths.json keys: "mid", "high" (each: manifest, ds_pred, features, zncc_a_pred, zncc_a_manifest, zncc_b_pred,
zncc_b_manifest) and "undistorted" (manifest, ds_pred, features, zncc_pred). Paths are absolute or relative to cwd.
"""
import argparse
import csv
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e15_eval as E  # noqa: E402

TH = E.load_thresholds(os.path.join(HERE, "e15_thresholds.json"))
TAU_DS = float(TH["tau_main"])          # 0.2617101
DELTA = float(TH["delta_net"])          # 0.09562161564826965
TAU_ZNCC = 0.36530551314353943          # E16 baseline, original dev split
B = int(TH["boot_B"])                   # 2000
SEED = int(TH["boot_seed"])             # 20261010
K1, K5 = 1.0, 5.0
LOC_TOL = 5.0


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def check_manifest(man, label):
    n = len(man)
    pres = [m for m in man if int(float(m["found"])) == 1]
    cross = [m for m in man if m["condition"] == "cross"]
    cnt = {c: sum(1 for m in pres if m["condition"] == c) for c in ("A", "B")}
    if n != 400 or len(pres) != 320 or len(cross) != 80 or cnt != {"A": 160, "B": 160}:
        raise SystemExit(f"{label}: expected 400 pairs (320 present, 160 A, 160 B, 80 cross), got n={n} "
                         f"present={len(pres)} counts={cnt} cross={len(cross)}")
    if len({m["pair_id"] for m in man}) != n:
        raise SystemExit(f"{label}: duplicate pair_id")


def zncc_arrays(man, preds, label):
    pm = {p["pair_id"]: p for p in preds}
    if set(pm) != {m["pair_id"] for m in man} or len(pm) != len(preds):
        raise SystemExit(f"{label}: ZNCC predictions do not match manifest ids")
    a = np.empty(len(man)); x = np.empty(len(man)); y = np.empty(len(man))
    for k, m in enumerate(man):
        p = pm[m["pair_id"]]
        if p["status"] != "ok":
            raise SystemExit(f"{label}: {m['pair_id']} status {p['status']!r}")
        a[k], x[k], y[k] = float(p["score"]), float(p["x"]), float(p["y"])
        if not np.all(np.isfinite([a[k], x[k], y[k]])):
            raise SystemExit(f"{label}: {m['pair_id']} non-finite ZNCC output")
    return a, x, y


def check_parts(main, parts):
    """Part manifests (kernel outputs) must be disjoint, cover main, and carry the same search sha256."""
    sha = {m["pair_id"]: m["search_sha256"] for m in main}
    seen = []
    for label, man, pred in parts:
        ids = [m["pair_id"] for m in man]
        for m in man:
            if m["search_sha256"] != sha.get(m["pair_id"]):
                raise SystemExit(f"{label}: search sha256 differs from main manifest at {m['pair_id']}")
        p_ids = [p["pair_id"] for p in pred]
        if sorted(ids) != sorted(p_ids):
            raise SystemExit(f"{label}: prediction ids differ from part manifest")
        seen += ids
    if sorted(seen) != sorted(sha):
        raise SystemExit("ZNCC parts do not partition the 400 pairs")


def cluster_setup(man):
    groups = np.array([m["group_id"] for m in man], dtype=str)
    uniq, codes = np.unique(groups, return_inverse=True)
    K = len(uniq)
    idx = np.random.default_rng(SEED).integers(0, K, size=(B, K))
    rows_by = [np.flatnonzero(codes == k) for k in range(K)]
    return uniq, codes, K, idx, rows_by


def ci(vals):
    v = np.asarray(vals, float)
    v = v[np.isfinite(v)]
    return [None, None] if len(v) == 0 else [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def metric_block(d, acc, codes, K, idx, rows_by):
    """Point and bootstrap for one rule. d has present, err, kind, and the 400 rows in manifest order."""
    S = E.indicator_sums(d, acc, codes, K, TH)
    point = E.metrics_from({k: v.sum() for k, v in S.items()})
    boot = E.metrics_from({k: v[idx].sum(axis=1) for k, v in S.items()})
    P = d["present"]; err = d["err"]
    loc = np.bincount(codes, weights=(P & (err <= LOC_TOL)).astype(float), minlength=K)
    npres = np.bincount(codes, weights=P.astype(float), minlength=K)
    point["loc_only@5"] = float(loc.sum() / npres.sum())
    boot["loc_only@5"] = loc[idx].sum(axis=1) / npres[idx].sum(axis=1)
    med_pt = float(np.median(err[P]))
    med_b = []
    for b in range(B):
        rows = np.concatenate([rows_by[k] for k in idx[b]])
        pr = rows[P[rows]]
        med_b.append(float(np.median(err[pr])))
    point["median_error"] = med_pt
    boot["median_error"] = np.asarray(med_b)
    names = ["success@1", "success@5", "loc_only@5", "median_error", "wrong_repeats_count", "wrong_repeats_rate",
             "accepted_decision_error", "absent_accepted_cross", "coverage", "F1_rejection"]
    out = {"accepted": int(acc.sum())}
    for n in names:
        out[n] = {"point": E.fnum(point[n]), "ci": ci(boot[n])}
    return out, point, boot


def subset_sums(mask, codes, K, s_arr, d_present_codes=None):
    return np.bincount(codes, weights=(mask & s_arr).astype(float), minlength=K)


def level_scores(man, ds_pred, feats, z_a, z_x, z_y, codes, K, idx, rows_by, label):
    d = E.build(man, ds_pred, feats, TH, "real")
    # ZNCC view of the same pairs: same present, err, kind, groups; ZNCC position and score
    dz = dict(d)
    dz["a"] = z_a
    err_z = np.full(len(man), np.inf)
    for k, m in enumerate(man):
        if d["present"][k]:
            err_z[k] = math.hypot(z_x[k] - float(m["gt_x"]), z_y[k] - float(m["gt_y"]))
    dz["err"] = err_z
    out = {"label": label, "n": len(man), "rules": {}}
    rules = {
        "DS_R1_tau0.2617101": (d["a"] >= TAU_DS, d),
        "DS_R3_gate": ((d["a"] >= TAU_DS) & (d["m_net"] >= DELTA), d),
        "ZNCC_frozen_tau0.36530551": (z_a >= TAU_ZNCC, dz),
        "ZNCC_E17_tau": (z_a >= float(TAU_E17), dz),
    }
    pts = {}
    for name, (acc, dd) in rules.items():
        block, pt, bt = metric_block(dd, acc, codes, K, idx, rows_by)
        out["rules"][name] = block
        pts[name] = (pt, bt)
    # paired success@5 difference, ZNCC minus DS R1, same draw
    for z in ("ZNCC_frozen_tau0.36530551", "ZNCC_E17_tau"):
        pz, bz = pts[z]; pd, bd = pts["DS_R1_tau0.2617101"]
        out.setdefault("paired_success@5_" + z + "_minus_DS_R1", {
            "point": E.fnum(pz["success@5"] - pd["success@5"]),
            "ci": ci(bz["success@5"] - bd["success@5"])})
    return out, d, dz


def contrast_data(d, dz, man, codes, K, cond_mask):
    """Per-cluster counts for success@5 under DS R1 and each ZNCC threshold on a pair subset."""
    P = d["present"] & cond_mask
    ds5 = P & (d["a"] >= TAU_DS) & (d["err"] <= K5)
    zf5 = P & (dz["err"] <= K5) & (dz["a"] >= TAU_ZNCC)
    ze5 = P & (dz["err"] <= K5) & (dz["a"] >= float(TAU_E17))
    n = np.bincount(codes, weights=P.astype(float), minlength=K)
    return {"n": n,
            "ds": np.bincount(codes, weights=ds5.astype(float), minlength=K),
            "zf": np.bincount(codes, weights=zf5.astype(float), minlength=K),
            "ze": np.bincount(codes, weights=ze5.astype(float), minlength=K)}


def gap(c, zkey, idxs):
    n = c["n"][idxs].sum(axis=1)
    return (c[zkey][idxs].sum(axis=1) - c["ds"][idxs].sum(axis=1)) / n


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--tau-e17", required=True, type=float)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    global TAU_E17
    TAU_E17 = args.tau_e17
    cfg = json.load(open(args.config, encoding="utf-8"))
    res = {"tau": {"DS_R1": TAU_DS, "DS_gate_delta": DELTA, "ZNCC_frozen": TAU_ZNCC, "ZNCC_E17": TAU_E17},
           "bootstrap": {"B": B, "seed": SEED, "cluster": "tile", "draw": "default_rng(seed).integers(0, K, size=(B, K))"},
           "levels": {}}

    contrast_inputs = {}
    for level in ("mid", "high"):
        c = cfg[level]
        man = read_csv(c["manifest"]); check_manifest(man, level)
        parts = [(level + "_a", read_csv(c["zncc_a_manifest"]), read_csv(c["zncc_a_pred"])),
                 (level + "_b", read_csv(c["zncc_b_manifest"]), read_csv(c["zncc_b_pred"]))]
        check_parts(man, parts)
        zp = parts[0][2] + parts[1][2]
        z_a, z_x, z_y = zncc_arrays(man, zp, level)
        ds_pred = E.read_pred(c["ds_pred"]); feats = E.read_features(c["features"])
        uniq, codes, K, idx, rows_by = cluster_setup(man)
        out, d, dz = level_scores(man, ds_pred, feats, z_a, z_x, z_y, codes, K, idx, rows_by, level)
        res["levels"][level] = out
        cond = np.array([m["condition"] for m in man])
        contrast_inputs[level] = dict(d=d, dz=dz, codes=codes, K=K, uniq=uniq, cond=cond, man=man)

    # undistorted E15/E16 subset (400 pairs, the same ids as the E18 sets)
    u = cfg["undistorted"]
    full = read_csv(u["manifest"])
    man_u = [m for m in full if m["condition"] in ("A", "B", "cross")]
    check_manifest(man_u, "undistorted")
    ids = {m["pair_id"] for m in man_u}
    ds_all = E.read_pred(u["ds_pred"]); feats_all = E.read_features(u["features"])
    ds_u = [p for p in ds_all if p["pair_id"] in ids]
    feats_u = [f for f in feats_all if f["pair_id"] in ids]
    zp_u = [p for p in read_csv(u["zncc_pred"]) if p["pair_id"] in ids]
    z_au, z_xu, z_yu = zncc_arrays(man_u, zp_u, "undistorted")
    d_u = E.build(man_u, ds_u, feats_u, TH, "real")
    dz_u = dict(d_u); dz_u["a"] = z_au
    err_zu = np.full(len(man_u), np.inf)
    for k, m in enumerate(man_u):
        if d_u["present"][k]:
            err_zu[k] = math.hypot(z_xu[k] - float(m["gt_x"]), z_yu[k] - float(m["gt_y"]))
    dz_u["err"] = err_zu
    cond_u = np.array([m["condition"] for m in man_u])
    # undistorted per-level summary for reference
    uniq_u, codes_u, K_u, idx_u, rows_u = cluster_setup(man_u)
    und_out, _, _ = level_scores(man_u, ds_u, feats_u, z_au, z_xu, z_yu, codes_u, K_u, idx_u, rows_u, "undistorted")
    res["levels"]["undistorted"] = und_out

    # contrasts: same 40 tiles in the same sorted order for every set
    tiles_u = list(uniq_u)
    for level, ci_ in contrast_inputs.items():
        assert list(ci_["uniq"]) == tiles_u, "tile lists differ between E18 level and undistorted set"
    all_true = np.ones(len(man_u), bool)
    cu = contrast_data(d_u, dz_u, man_u, codes_u, K_u, all_true)
    cA = contrast_data(d_u, dz_u, man_u, codes_u, K_u, cond_u == "A")
    cB = contrast_data(d_u, dz_u, man_u, codes_u, K_u, cond_u == "B")
    contrasts = {}
    for zkey, label in (("zf", "frozen_tau"), ("ze", "E17_tau")):
        for level, ci_ in contrast_inputs.items():
            cl = contrast_data(ci_["d"], ci_["dz"], ci_["man"], ci_["codes"], ci_["K"], np.ones(400, bool))
            gl = gap(cl, zkey, idx_u)
            gu = gap(cu, zkey, idx_u)
            diff = gl - gu
            contrasts[f"I_{level}_{label}"] = {"point": E.fnum(gap_point(cl, cu, zkey)),
                                              "ci": ci(diff)}
        gA = gap(cA, zkey, idx_u); gB = gap(cB, zkey, idx_u)
        contrasts[f"AB_undistorted_{label}"] = {"point": E.fnum(gap_point(cB, cA, zkey)),
                                               "ci": ci(gA * 0 + (gB - gA))}
    res["contrasts_success@5"] = contrasts
    res["contrast_definition"] = ("I_level = (ZNCC-DS)_level - (ZNCC-DS)_undistorted on the same 400 pairs, "
                                  "success@5 over present pairs; AB = (ZNCC-DS)_B - (ZNCC-DS)_A on undistorted present "
                                  "pairs. Cluster bootstrap by tile, same draw.")
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    for lv in ("mid", "high", "undistorted"):
        r = res["levels"][lv]["rules"]
        print(lv, "ZNCC@frozen s@5", r["ZNCC_frozen_tau0.36530551"]["success@5"]["point"],
              "DS R1 s@5", r["DS_R1_tau0.2617101"]["success@5"]["point"], flush=True)
    return 0


def gap_point(c, base, zkey):
    """Point contrast: (zkey - ds) on c minus the same on base, over present pairs."""
    gc = (c[zkey].sum() - c["ds"].sum()) / c["n"].sum()
    gb = (base[zkey].sum() - base["ds"].sum()) / base["n"].sum()
    return gc - gb


if __name__ == "__main__":
    raise SystemExit(main())
