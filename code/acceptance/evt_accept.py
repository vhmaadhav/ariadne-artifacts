"""Per-pair calibrated acceptance by extreme-value significance (contribution 2a).

For one pair, the winning correlation peak is compared with the off-peak local
maxima of the same surface (mostly periodic decoys). The top-K off-peak maxima
are fitted with a Gumbel law (maxima). The winner's exceedance probability p
under that law, and NFA = p * N (N = number of off-peak candidate sites), give
an a-contrario score: a small NFA means the winner is unlikely to be a decoy.

Approximation, stated in the paper: the Gumbel is fitted to the upper tail (top
K local maxima), not to all sites, so p is an approximation of the tail.

Pure functions, numpy only. scipy is used for the MLE when installed; a numpy
fallback is always available. No file I/O.
"""
from __future__ import annotations

import math

import numpy as np

try:  # optional
    from scipy import stats as _scipy_stats
except ImportError:  # pragma: no cover - depends on the environment
    _scipy_stats = None

EULER_GAMMA = 0.5772156649015329


def _window_reduce(a: np.ndarray, r: int, op, init: float) -> np.ndarray:
    """Separable (2r+1)x(2r+1) window reduction; out-of-image cells use `init`."""
    h, w = a.shape
    padded = np.pad(a, r, mode="constant", constant_values=init)
    cols = np.full((h + 2 * r, w), init)
    for dj in range(2 * r + 1):
        cols = op(cols, padded[:, dj:dj + w])
    out = np.full((h, w), init)
    for di in range(2 * r + 1):
        out = op(out, cols[di:di + h, :])
    return out


def local_maxima(surface, nms_radius: int = 2) -> np.ndarray:
    """(row, col) of cells equal to the maximum of their (2r+1)^2 window.

    A flat window is not a maximum (so background plateaus are ignored) and
    non-finite cells never are. Sorted by value, strongest first.
    """
    s = np.asarray(surface, dtype=np.float64)
    if s.ndim != 2:
        raise ValueError("surface must be 2-D")
    r = int(nms_radius)
    if r < 0:
        raise ValueError("nms_radius must be >= 0")
    win_max = _window_reduce(s, r, np.maximum, -np.inf)
    win_min = _window_reduce(s, r, np.minimum, np.inf)
    ii, jj = np.nonzero((s >= win_max) & (win_max > win_min) & np.isfinite(s))
    order = np.argsort(-s[ii, jj], kind="stable")
    return np.column_stack([ii, jj])[order]


def _floor(x: np.ndarray) -> float:
    """Smallest scale used for degenerate samples (all values equal)."""
    return 1e-6 * max(1.0, float(np.abs(x).mean()))


def _gumbel_mle_numpy(x: np.ndarray) -> tuple[float, float]:
    """MLE for the maximum-Gumbel law by bisection on the profile equation.

    beta = mean(x) - sum(x exp(-x/beta)) / sum(exp(-x/beta)),
    mu = -beta * log(mean(exp(-x/beta))). Shifted by min(x) for stability.
    """
    c = float(x.min())
    xs = x - c
    m = float(xs.mean())
    spread = max(float(xs.std()), _floor(x))

    def residual(beta: float) -> float:
        w = np.exp(-xs / beta)
        return beta - (m - float(np.sum(xs * w) / np.sum(w)))

    lo, hi = 1e-8 * spread, 1e3 * spread
    if residual(lo) > 0 or residual(hi) < 0:  # no bracket: fall back to moments
        return _gumbel_mom(x)
    for _ in range(200):
        mid = math.sqrt(lo * hi)  # bisection in log scale
        if residual(mid) > 0:
            hi = mid
        else:
            lo = mid
        if hi / lo < 1 + 1e-12:
            break
    beta = math.sqrt(lo * hi)
    mu = c - beta * math.log(float(np.mean(np.exp(-xs / beta))))
    return mu, beta


def _gumbel_mom(x: np.ndarray) -> tuple[float, float]:
    """Method of moments: beta = s sqrt(6)/pi, mu = mean - gamma * beta."""
    beta = float(x.std(ddof=1)) * math.sqrt(6.0) / math.pi
    beta = max(beta, _floor(x))
    return float(x.mean()) - EULER_GAMMA * beta, beta


def fit_gumbel(samples, method: str = "mle") -> tuple[float, float]:
    """Fit a maximum-Gumbel law. Returns (mu, beta).

    method "mom": method of moments (no dependency).
    method "mle": scipy.stats.gumbel_r.fit when scipy is installed, else numpy.
    """
    x = np.asarray(samples, dtype=np.float64)
    x = x[np.isfinite(x)]
    if x.size < 3:
        raise ValueError("need at least 3 finite samples to fit a Gumbel law")
    if method == "mom":
        return _gumbel_mom(x)
    if method != "mle":
        raise ValueError("method must be 'mle' or 'mom'")
    if _scipy_stats is not None:
        mu, beta = _scipy_stats.gumbel_r.fit(x)
        if np.isfinite(mu) and np.isfinite(beta) and beta > 0:
            return float(mu), float(beta)
    return _gumbel_mle_numpy(x)


def gumbel_sf(x: float, mu: float, beta: float) -> float:
    """P(X >= x) for the maximum-Gumbel law, computed without cancellation."""
    z = (float(x) - mu) / beta
    return float(-math.expm1(-math.exp(-z)))


def evt_from_candidates(winner_score: float, candidate_scores, *, top_k: int = 50,
                        method: str = "mle", n_sites: int | None = None) -> dict:
    """Significance of a winner against off-peak candidate maxima.

    candidate_scores: values of the off-peak local maxima (any order; the winner
    must already be excluded). n_sites defaults to the number of candidates.
    Returns a dict with winner_score, runner_up, margin, p_value, n_sites, nfa,
    log10_nfa, mu, beta, n_fit, method. Missing values are NaN.
    """
    nan = float("nan")
    cands = np.asarray(candidate_scores, dtype=np.float64).ravel()
    cands = np.sort(cands[np.isfinite(cands)])[::-1]
    winner = float(winner_score)
    out = {"winner_score": winner, "runner_up": nan, "margin": nan, "p_value": nan,
           "n_sites": int(cands.size if n_sites is None else n_sites), "nfa": nan,
           "log10_nfa": nan, "mu": nan, "beta": nan, "n_fit": 0, "method": method}
    if cands.size:
        out["runner_up"] = float(cands[0])
        out["margin"] = winner - float(cands[0])
    sample = cands[:int(top_k)]
    out["n_fit"] = int(sample.size)
    if sample.size >= 3 and np.isfinite(winner):
        mu, beta = fit_gumbel(sample, method)
        p = gumbel_sf(winner, mu, beta)
        nfa = p * out["n_sites"]
        out.update({"p_value": p, "nfa": nfa, "mu": mu, "beta": beta,
                    "log10_nfa": math.log10(max(nfa, 1e-300))})
    return out


def evt_accept(surface, winner, *, exclude_radius: float = 16.0, nms_radius: int = 2,
               top_k: int = 50, method: str = "mle", n_sites: int | None = None) -> dict:
    """Score the winner at `winner` = (row, col) of a 2-D surface.

    Off-peak candidates are the NMS local maxima farther than `exclude_radius`
    px from the winner. Everything else is as in evt_from_candidates.
    """
    s = np.asarray(surface, dtype=np.float64)
    wr, wc = int(winner[0]), int(winner[1])
    peaks = local_maxima(s, nms_radius)
    dist = np.hypot(peaks[:, 0] - wr, peaks[:, 1] - wc)
    off = peaks[dist > exclude_radius]
    values = s[off[:, 0], off[:, 1]] if off.size else np.empty(0)
    return evt_from_candidates(float(s[wr, wc]), values, top_k=top_k, method=method,
                               n_sites=int(off.shape[0]) if n_sites is None else n_sites)


def evt_row_score(row: dict, *, exclude_radius: float = 16.0, top_k: int = 50,
                  method: str = "mle") -> dict:
    """EVT score from one logged pair (log_hypotheses.feature_row output).

    Uses the native ZNCC surface of the selected hypothesis: winner = its ZNCC,
    candidates = the logged off-disc maxima. The log excludes a 16 px disc, so
    exclude_radius may not be smaller than 16.
    """
    from_log = 16.0
    if exclude_radius < from_log:
        raise ValueError("exclude_radius below the logged disc (16 px) is not available")
    idx = int(row.get("selected_index", -1))
    hyps = row.get("hypotheses", [])
    if idx < 0 or idx >= len(hyps):
        return evt_from_candidates(float("nan"), [], top_k=top_k, method=method)
    sel = hyps[idx]
    peaks = [p for p in sel.get("zncc_peaks", [])
             if math.hypot(p[1] - sel["x_snap"], p[2] - sel["y_snap"]) > exclude_radius]
    values = [p[0] for p in peaks]
    # The logged site count uses the same 16 px disc; for a wider disc only the
    # logged top-50 list is known, so the count falls back to that list.
    n_sites = int(sel.get("zncc_n_sites", len(values))) if exclude_radius == from_log else len(values)
    return evt_from_candidates(sel["zncc"], values, top_k=top_k, method=method, n_sites=n_sites)
