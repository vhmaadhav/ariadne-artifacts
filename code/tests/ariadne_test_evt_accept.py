"""Unit tests for evt_accept on synthetic arrays only (no project data)."""
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import evt_accept as ea  # noqa: E402


def _lattice(n=120, period=20, peak=1.0):
    s = np.zeros((n, n))
    for i in range(period // 2, n, period):
        for j in range(period // 2, n, period):
            s[i, j] = peak
    return s


def test_local_maxima_finds_isolated_peaks():
    s = np.zeros((30, 30))
    s[5, 5], s[20, 22] = 1.0, 0.5
    peaks = ea.local_maxima(s, nms_radius=2)
    assert peaks.shape == (2, 2)
    assert tuple(peaks[0]) == (5, 5) and tuple(peaks[1]) == (20, 22)


def test_periodic_lattice_of_equal_peaks_is_not_significant():
    # Every decoy is as tall as the winner: the winner is not distinguishable.
    s = _lattice()
    winner = (30, 30)
    res = ea.evt_accept(s, winner, exclude_radius=5, nms_radius=2)
    assert res["margin"] == 0.0
    assert res["n_sites"] == 35  # 6x6 lattice minus the winner; flat background not counted
    assert res["n_fit"] == 35
    assert 0.2 < res["p_value"] < 0.8          # analytic value: 1 - exp(-exp(-gamma)) ~ 0.43
    assert res["nfa"] > 1.0


def test_single_strong_peak_in_noise_is_significant():
    rng = np.random.default_rng(0)
    s = rng.normal(0.0, 0.1, size=(200, 200))
    s[100, 100] = 1.0
    res = ea.evt_accept(s, (100, 100), exclude_radius=10)
    assert res["margin"] > 0.5
    assert res["p_value"] < 1e-6
    assert res["nfa"] < 1e-3


def test_nfa_is_p_times_sites():
    cands = np.linspace(0.1, 0.4, 40)
    a = ea.evt_from_candidates(0.9, cands, n_sites=100)
    b = ea.evt_from_candidates(0.9, cands, n_sites=1)
    assert math.isclose(a["p_value"], b["p_value"])
    assert math.isclose(a["nfa"], 100 * a["p_value"])


def test_fit_recovers_gumbel_parameters():
    rng = np.random.default_rng(1)
    x = rng.gumbel(loc=0.3, scale=0.05, size=5000)
    for method in ("mom", "mle"):
        mu, beta = ea.fit_gumbel(x, method)
        assert abs(mu - 0.3) < 0.01, (method, mu)
        assert abs(beta - 0.05) < 0.005, (method, beta)


def test_numpy_mle_fallback_agrees_with_moments():
    rng = np.random.default_rng(2)
    x = rng.gumbel(loc=-1.0, scale=0.2, size=4000)
    mu_n, beta_n = ea._gumbel_mle_numpy(x)
    mu_m, beta_m = ea._gumbel_mom(x)
    assert abs(beta_n - 0.2) < 0.02 and abs(mu_n + 1.0) < 0.02
    assert abs(beta_n - beta_m) < 0.03


def test_degenerate_equal_samples_do_not_crash():
    mu, beta = ea.fit_gumbel(np.ones(10), "mle")
    assert np.isfinite(mu) and beta > 0


def test_gumbel_sf_is_monotone_and_bounded():
    xs = np.linspace(-1, 3, 50)
    p = [ea.gumbel_sf(x, 0.0, 1.0) for x in xs]
    assert all(0.0 <= v <= 1.0 for v in p)
    assert all(a >= b for a, b in zip(p, p[1:]))


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
