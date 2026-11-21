"""Unit tests for logistic_accept on synthetic data (no project data)."""
import json
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import logistic_accept as la  # noqa: E402


def _synthetic(n=800, seed=3):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 5))
    w_true = np.array([2.0, -1.0, 1.5, 0.0, -0.5])
    p = 1 / (1 + np.exp(-(X @ w_true - 0.2)))
    y = (rng.random(n) < p).astype(int)
    return X, y


def test_fit_recovers_signs_and_generalises():
    X, y = _synthetic()
    mean, std = la.standardise_fit(X[:600])
    w, b = la.fit_logistic((X[:600] - mean) / std, y[:600], lam=1e-3)
    assert w[0] > 0 and w[1] < 0 and w[2] > 0
    s = la.logistic_scores(X[600:], mean, std, w, b)
    assert la.auroc(s, y[600:]) > 0.85


def test_l2_shrinks_weights():
    X, y = _synthetic()
    mean, std = la.standardise_fit(X)
    Z = (X - mean) / std
    w_small, _ = la.fit_logistic(Z, y, lam=0.01)
    w_big, _ = la.fit_logistic(Z, y, lam=1000.0)
    assert np.linalg.norm(w_big) < np.linalg.norm(w_small)


def test_nan_feature_rows_are_declined():
    X, y = _synthetic(50)
    mean, std = la.standardise_fit(X)
    w, b = la.fit_logistic((X - mean) / std, y)
    X2 = X.copy()
    X2[3, 2] = np.nan
    s = la.logistic_scores(X2, mean, std, w, b)
    assert s[3] == -np.inf and np.isfinite(s[4])


def test_auroc_matches_pairwise_definition():
    rng = np.random.default_rng(5)
    s = np.round(rng.normal(size=60), 1)  # ties on purpose
    y = rng.integers(0, 2, size=60)
    pos, neg = s[y == 1], s[y == 0]
    pairs = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (pos.size * neg.size)
    assert math.isclose(la.auroc(s, y), pairs, rel_tol=1e-12)


def test_f1_threshold_separates_perfect_scores():
    s = np.r_[np.linspace(0.6, 0.9, 20), np.linspace(0.1, 0.4, 20)]
    y = np.r_[np.ones(20, int), np.zeros(20, int)]
    t = la.choose_threshold(s, y, "f1")
    assert 0.4 < t <= 0.6


def test_err_rule_respects_accepted_error_budget():
    rng = np.random.default_rng(7)
    s = rng.random(400)
    y = (s + 0.3 * rng.normal(size=400) > 0.5).astype(int)
    alpha = 0.05
    t = la.choose_threshold(s, y, "err", alpha)
    acc = s >= t
    assert acc.sum() > 0
    assert (1 - y[acc]).mean() <= alpha + 1e-12


def test_err_rule_declines_everything_when_impossible():
    s = np.linspace(0, 1, 10)
    y = np.zeros(10, int)
    assert la.choose_threshold(s, y, "err", 0.05) == math.inf


def test_out_of_fold_is_deterministic():
    X, y = _synthetic(200)
    a = la.out_of_fold(X, y, 1.0)
    b = la.out_of_fold(X, y, 1.0)
    assert np.array_equal(a, b) and np.isfinite(a).all()


def test_fit_rejects_more_than_five_features():
    try:
        la.fit_logistic(np.zeros((10, 6)), np.zeros(10))
    except ValueError:
        return
    raise AssertionError("six features must be rejected")


if __name__ == "__main__":
    failures = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except AssertionError as exc:
                failures += 1
                print("FAIL", name, exc)
    raise SystemExit(1 if failures else 0)
