"""Local, read-only metrics on existing prediction CSVs (no new runs). Cluster bootstrap by group_id, 2000, seed 20261010."""
import argparse, json, sys
import numpy as np, pandas as pd

def load(man_path, pred_path, method):
    man = pd.read_csv(man_path, dtype={"pair_id": str, "group_id": str})
    pred = pd.read_csv(pred_path, dtype={"pair_id": str, "method": str})
    pred = pred[pred["method"] == method]
    df = man.merge(pred, on="pair_id", how="inner", validate="one_to_one", suffixes=("_gt", ""))
    assert len(df) == len(man), (len(df), len(man), method, pred_path)
    present = df["found_gt"].to_numpy() == 1
    err = np.hypot(df.x.to_numpy() - df.gt_x.to_numpy(), df.y.to_numpy() - df.gt_y.to_numpy())
    err = np.where(np.isfinite(err), err, np.inf)
    return df, df.score.to_numpy(float), present, err, df.group_id.to_numpy()

def metrics(score, present, err, tau):
    acc = score >= tau
    absent = ~present
    n_p, n_a = present.sum(), absent.sum()
    n_acc = acc.sum()
    wrong = (absent & acc) | (present & acc & (err > 5))
    tp = (absent & ~acc).sum(); fp = (present & ~acc).sum(); fn = (absent & acc).sum()
    return {
        "success@1": (present & acc & (err <= 1)).sum() / n_p,
        "success@5": (present & acc & (err <= 5)).sum() / n_p,
        "median_err_px": float(np.median(err[present])),
        "wrong_repeat_>20px": (present & (err > 20)).sum() / n_p,
        "absent_accepted": f"{fn}/{n_a}",
        "present_declined": f"{fp}/{n_p}",
        "accepted_decision_error": wrong.sum() / n_acc if n_acc else float("nan"),
        "accepted": int(n_acc),
        "F1": 2 * tp / (2 * tp + fp + fn),
    }

def boot_success(score, present, err, tau, groups, B=2000, seed=20261010, other=None):
    rng = np.random.default_rng(seed)
    uniq, codes = np.unique(groups, return_inverse=True)
    k = len(uniq)
    acc = score >= tau
    hit = (present & acc & (err <= 5)).astype(float)
    pres = present.astype(float)
    sums_h = np.bincount(codes, weights=hit, minlength=k)
    sums_p = np.bincount(codes, weights=pres, minlength=k)
    vals = []
    for _ in range(B):
        idx = rng.integers(0, k, k)
        vals.append(sums_h[idx].sum() / sums_p[idx].sum())
    return np.percentile(vals, [2.5, 97.5])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--method", default="noexit")
    ap.add_argument("--tau", type=float, nargs="+", required=True)
    ap.add_argument("--ref", default=None, help="reference pred file for paired delta (same method name = --ref-method)")
    ap.add_argument("--ref-method", default="noexit")
    a = ap.parse_args()
    df, score, present, err, groups = load(a.manifest, a.pred, a.method)
    out = {}
    for t in a.tau:
        m = metrics(score, present, err, t)
        lo, hi = boot_success(score, present, err, t, groups)
        m["success@5_CI"] = [round(lo, 3), round(hi, 3)]
        if a.ref:
            rdf, rscore, rpresent, rerr, _ = load(a.manifest, a.ref, a.ref_method)
            assert (rdf.pair_id.to_numpy() == df.pair_id.to_numpy()).all()
            d_hit = ((present & (score >= t) & (err <= 5)).astype(float) - (rpresent & (rscore >= t) & (rerr <= 5)).astype(float))
            uniq, codes = np.unique(groups, return_inverse=True)
            rng = np.random.default_rng(20261010)
            bs = []
            sp = np.bincount(codes, weights=present.astype(float), minlength=len(uniq))
            sd = np.bincount(codes, weights=d_hit, minlength=len(uniq))
            for _ in range(2000):
                idx = rng.integers(0, len(uniq), len(uniq))
                bs.append(sd[idx].sum() / sp[idx].sum())
            m["delta_success@5_vs_ref"] = round(float(d_hit.sum() / present.sum()), 4)
            m["delta_CI"] = [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]
        out[f"tau={t:.7f}"] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}
    print(json.dumps(out, indent=1))
