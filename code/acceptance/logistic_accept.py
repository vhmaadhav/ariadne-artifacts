"""Calibrated acceptance: L2 logistic model on <= 5 features (contribution 2b),
plus the shared dev-only threshold rules used for the EVT score too.

Target: present AND err <= 5 px (a correct match). Fit on dev only. The
threshold is chosen on dev out-of-fold scores (5 folds, seed 20261010) by one of:
  f1   maximise F1 of the correct-match class;
  err  largest accepted set whose error rate (accepted but not correct / accepted)
       is <= alpha.

CLI (paths relative to the working copy; see RUN_BRIEF.md, step E6):
  logistic_accept.py fit --dev-features F --dev-manifest M --out MODEL.json
  logistic_accept.py predict --score logistic --model MODEL.json --features F
      --manifest M --base-pred P --method logistic --out PRED.csv
  logistic_accept.py predict --score evt --dev-features DF --dev-manifest DM
      --features F --manifest M --base-pred P --rule err --alpha 0.05
      --method evt --out PRED.csv
Prediction CSVs use the iris_spec.md schema, so iris_report.py can read them.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evt_accept import evt_row_score  # noqa: E402
from log_hypotheses import FEATURE_NAMES, five_features  # noqa: E402

SEED = 20261010
TOLERANCE_PX = 5.0
PRED_FIELDS = ["pair_id", "method", "found", "score", "x", "y", "theta", "scale",
               "seconds", "status"]


# ---------------------------------------------------------------- data ----
def read_manifest(path) -> dict:
    with open(path, newline="", encoding="utf-8-sig") as handle:
        return {r["pair_id"]: r for r in csv.DictReader(handle)}


def read_rows(path) -> list[dict]:
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def labels(rows, manifest) -> tuple[np.ndarray, np.ndarray]:
    """(correct, err_px) per row. correct = present and err <= 5 px."""
    correct, err = [], []
    for r in rows:
        m = manifest[r["pair_id"]]
        present = int(m["found"]) == 1
        e = math.hypot(r["x"] - float(m["gt_x"]), r["y"] - float(m["gt_y"])) if present else math.inf
        err.append(e)
        correct.append(int(present and e <= TOLERANCE_PX))
    return np.asarray(correct), np.asarray(err)


def feature_matrix(rows) -> np.ndarray:
    return np.asarray([[five_features(r)[k] for k in FEATURE_NAMES] for r in rows], dtype=float)


# ------------------------------------------------------------ model -------
def _sigmoid(z):
    return 0.5 * (1.0 + np.tanh(0.5 * z))


def fit_logistic(X: np.ndarray, y: np.ndarray, lam: float = 1.0, iters: int = 100) -> tuple[np.ndarray, float]:
    """Newton (IRLS) for L2-penalised logistic regression. The intercept is not penalised."""
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    if X.ndim != 2 or X.shape[1] > 5:
        raise ValueError("X must be (n, <=5)")
    A = np.hstack([np.ones((X.shape[0], 1)), X])
    P = lam * np.eye(A.shape[1])
    P[0, 0] = 0.0
    beta = np.zeros(A.shape[1])
    for _ in range(iters):
        p = _sigmoid(A @ beta)
        grad = A.T @ (p - y) + P @ beta
        W = p * (1 - p)
        hess = A.T @ (A * W[:, None]) + P
        step = np.linalg.solve(hess, grad)
        beta -= step
        if np.max(np.abs(step)) < 1e-10:
            break
    return beta[1:], float(beta[0])


def standardise_fit(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    return mean, np.where(std > 1e-12, std, 1.0)


def logistic_scores(X, mean, std, w, b) -> np.ndarray:
    """Probability of a correct match; rows with any NaN feature get -inf (declined)."""
    X = np.asarray(X, float)
    Z = (X - mean) / std
    s = _sigmoid(Z @ np.asarray(w) + b)
    s[~np.all(np.isfinite(Z), axis=1)] = -np.inf
    return s


# ------------------------------------------------------- metrics / rules --
def auroc(score, y) -> float:
    s = np.asarray(score, float)
    y = np.asarray(y, int)
    keep = np.isfinite(s)
    s, y = s[keep], y[keep]
    pos, neg = s[y == 1], s[y == 0]
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    allv = np.concatenate([pos, neg])
    order = np.argsort(allv, kind="stable")
    ranks = np.empty(allv.size)
    ranks[order] = np.arange(1, allv.size + 1)
    for v in np.unique(allv):  # average ranks over ties
        idx = allv == v
        ranks[idx] = ranks[idx].mean()
    return float((ranks[:pos.size].sum() - pos.size * (pos.size + 1) / 2) / (pos.size * neg.size))


def choose_threshold(score, y, rule: str = "f1", alpha: float = 0.05) -> float:
    """Dev threshold t (accept when score >= t). Returns +inf if nothing qualifies."""
    s = np.asarray(score, float)
    y = np.asarray(y, int)
    keep = np.isfinite(s)
    s, y = s[keep], y[keep]
    if s.size == 0:
        return math.inf
    order = np.argsort(-s, kind="stable")
    s, y = s[order], y[order]
    tp = np.cumsum(y)
    k = np.arange(1, s.size + 1)
    fp = k - tp
    P = int(y.sum())
    last = np.r_[s[1:] != s[:-1], True]  # only cut between distinct score values
    if rule == "f1":
        f1 = np.where(P + k > 0, 2 * tp / np.maximum(P + k, 1), 0.0)
        cand = np.flatnonzero(last)
        best = cand[np.argmax(f1[cand])]
    elif rule == "err":
        err = fp / k
        ok = np.flatnonzero(last & (err <= alpha))
        if ok.size == 0:
            return math.inf
        best = ok[-1]
    else:
        raise ValueError("rule must be f1 or err")
    return float(s[best])


def out_of_fold(X, y, lam: float, folds: int = 5) -> np.ndarray:
    """Dev-only 5-fold out-of-fold probabilities (standardised inside each fold)."""
    n = X.shape[0]
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(n)
    scores = np.full(n, -np.inf)
    for f in range(folds):
        test = perm[f::folds]
        train = np.setdiff1d(perm, test)
        mean, std = standardise_fit(X[train])
        w, b = fit_logistic((X[train] - mean) / std, y[train], lam=lam)
        scores[test] = logistic_scores(X[test], mean, std, w, b)
    return scores


# ------------------------------------------------------------- CLI --------
def _dev_xy(features, manifest):
    rows = read_rows(features)
    man = read_manifest(manifest)
    rows = [r for r in rows if r["pair_id"] in man]
    y, _ = labels(rows, man)
    return rows, feature_matrix(rows), y


def cmd_fit(args) -> None:
    rows, X, y = _dev_xy(args.dev_features, args.dev_manifest)
    keep = np.all(np.isfinite(X), axis=1)
    if keep.sum() < len(keep):
        print(f"dropping {int((~keep).sum())} dev rows with undefined features", file=sys.stderr)
    X, y = X[keep], y[keep]
    oof = out_of_fold(X, y, args.lam)
    thr = choose_threshold(oof, y, args.rule, args.alpha)
    mean, std = standardise_fit(X)
    w, b = fit_logistic((X - mean) / std, y, lam=args.lam)
    model = {"features": list(FEATURE_NAMES), "mean": mean.tolist(), "std": std.tolist(),
             "w": w.tolist(), "b": b, "lam": args.lam, "rule": args.rule, "alpha": args.alpha,
             "threshold": thr, "threshold_source": "dev out-of-fold (5 folds, seed 20261010)",
             "dev_n": int(len(y)), "dev_correct": int(y.sum()),
             "dev_oof_auroc": auroc(oof, y)}
    Path(args.out).write_text(json.dumps(model, indent=2), encoding="utf-8")
    print(json.dumps({k: model[k] for k in ("threshold", "dev_n", "dev_correct", "dev_oof_auroc")}))


def evt_score(row: dict) -> float:
    """Monotone map of -log10(NFA) into (-1, 1), as iris_report requires; NaN if undefined."""
    v = evt_row_score(row)["log10_nfa"]
    return float(np.tanh(-v / 10.0)) if math.isfinite(v) else float("nan")


def _scores_for(args, rows):
    if args.score == "logistic":
        m = json.loads(Path(args.model).read_text(encoding="utf-8"))
        X = feature_matrix(rows)
        s = logistic_scores(X, np.asarray(m["mean"]), np.asarray(m["std"]),
                            np.asarray(m["w"]), m["b"])
        return s, float(m["threshold"]), m
    dev_rows, _, dev_y = _dev_xy(args.dev_features, args.dev_manifest)
    dev_s = np.asarray([evt_score(r) for r in dev_rows], dtype=float)
    thr = choose_threshold(dev_s, dev_y, args.rule, args.alpha)
    s = np.asarray([evt_score(r) for r in rows], dtype=float)
    return s, thr, {"rule": args.rule, "alpha": args.alpha, "score_map": "tanh(-log10(NFA)/10)"}


def cmd_predict(args) -> None:
    rows = read_rows(args.features)
    man = read_manifest(args.manifest)
    rows = [r for r in rows if r["pair_id"] in man]
    base = {}
    with open(args.base_pred, newline="", encoding="utf-8") as handle:
        for r in csv.DictReader(handle):
            base[r["pair_id"]] = r
    missing = [r["pair_id"] for r in rows if r["pair_id"] not in base]
    if missing:
        raise ValueError(f"{len(missing)} feature rows have no base prediction, e.g. {missing[:3]}")
    scores, thr, meta = _scores_for(args, rows)
    with open(args.out, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=PRED_FIELDS)
        writer.writeheader()
        for r, s in sorted(zip(rows, scores), key=lambda t: t[0]["pair_id"]):
            b = base[r["pair_id"]]
            found = int(np.isfinite(s) and s >= thr)
            writer.writerow({"pair_id": r["pair_id"], "method": args.method, "found": found,
                             "score": float(s) if np.isfinite(s) else 0.0,
                             "x": b["x"], "y": b["y"], "theta": b["theta"], "scale": b["scale"],
                             "seconds": b["seconds"], "status": b["status"]})
    Path(args.out + ".threshold.json").write_text(
        json.dumps({"method": args.method, "score": args.score, "threshold": thr, **meta}, indent=2),
        encoding="utf-8")
    print(f"{args.method}: {len(rows)} rows, threshold {thr:.6g}, written {args.out}")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fit")
    f.add_argument("--dev-features", required=True)
    f.add_argument("--dev-manifest", required=True)
    f.add_argument("--out", required=True)
    f.add_argument("--rule", choices=["f1", "err"], default="f1")
    f.add_argument("--alpha", type=float, default=0.05)
    f.add_argument("--lam", type=float, default=1.0)
    f.set_defaults(func=cmd_fit)
    q = sub.add_parser("predict")
    q.add_argument("--score", choices=["logistic", "evt"], required=True)
    q.add_argument("--model")
    q.add_argument("--dev-features")
    q.add_argument("--dev-manifest")
    q.add_argument("--features", required=True)
    q.add_argument("--manifest", required=True)
    q.add_argument("--base-pred", required=True)
    q.add_argument("--method", required=True)
    q.add_argument("--rule", choices=["f1", "err"], default="f1")
    q.add_argument("--alpha", type=float, default=0.05)
    q.add_argument("--out", required=True)
    q.set_defaults(func=cmd_predict)
    args = p.parse_args(argv)
    if args.cmd == "predict" and args.score == "logistic" and not args.model:
        p.error("--model is required for --score logistic")
    if args.cmd == "predict" and args.score == "evt" and not (args.dev_features and args.dev_manifest):
        p.error("--dev-features and --dev-manifest are required for --score evt")
    args.func(args)


if __name__ == "__main__":
    main()
