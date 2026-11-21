"""Per-pair evidence rows for calibrated rejection (ariadne E4).

`feature_row` turns one `locate_phase2(..., return_hypotheses=True)` result into
a JSON-serialisable dict. One JSON line per pair goes to `--features-out` in
scripts/iris_eval.py (patch: patches/log_hypotheses.patch). The prediction CSV
is unchanged, so the features can be joined to it on pair_id.

Row schema (all coordinates are in the manifest's label convention unless the
key says `native_edge`, which is the internal pixel-edge frame):

  pair_id, method            str
  x, y, theta, scale         float   final pose (as in the prediction CSV)
  score, confidence          float   network score and shipped confidence
  zncc_med3, winner_margin   float   confidence term and pose-contest margin
  rigid_x, rigid_y           float   native_edge rigid answer before row correction
  n_hypotheses               int     pose hypotheses evaluated
  selected_index             int     index into `hypotheses` (-1 if none)
  hypotheses                 list    one dict per evaluated hypothesis:
      scale, theta           float   pose of the hypothesis
      pose_peak              float   coarse probe peak (pose search)
      network_score          float   network peak height (selects the candidate)
      peak_ratio             float   runner-up / winner network peak (locate)
      psr, apce              float   peak-quality statistics on the network map
      coarse_x_native,
      coarse_y_native        float   network location mapped to native_edge
      x_snap, y_snap         float   native ZNCC snap (native_edge, before polish)
      zncc                   float   native ZNCC at the snap
      rank, band             float   verifier scores (instrumentation only)
      selected               bool    True for the hypothesis that won
      net_offpeak            list    top-10 [score, x, y] off-peak maxima of the
                                     network map (x, y native_edge, cell centres)
      net_peak_cell          [i, j]  winning response cell
      zncc_peaks             list    top-50 [value, x, y] off-disc maxima of the
                                     full-frame native ZNCC surface (native_edge)
      zncc_n_sites           int     number of off-disc local maxima (disc = 16 px)
      zncc_n_local_max       int     all local maxima of that surface

The 5 features for the logistic model (`five_features`) are:
  net_score     = selected network_score
  net_margin    = 1 - selected peak_ratio
  native_zncc   = selected zncc
  pose_margin   = winner_margin
  loc_agree     = log1p(distance in px between the selected network location and
                  the rigid native answer)
"""
from __future__ import annotations

import math

FEATURE_NAMES = ("net_score", "net_margin", "native_zncc", "pose_margin", "loc_agree")


def _f(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def feature_row(pair_id: str, res: dict, method: str = "noexit") -> dict:
    """Flatten one locate_phase2 result (return_hypotheses=True) into a JSON row."""
    hyps = list(res.get("hypotheses", []))
    sel = next((i for i, h in enumerate(hyps) if h.get("selected")), -1)
    rows = []
    for h in hyps:
        rows.append({
            "scale": _f(h.get("scale")), "theta": _f(h.get("theta")),
            "pose_peak": _f(h.get("pose_peak")), "network_score": _f(h.get("network_score")),
            "peak_ratio": _f(h.get("peak_ratio")), "psr": _f(h.get("psr")),
            "apce": _f(h.get("apce")),
            "coarse_x_native": _f(h.get("coarse_x_native")),
            "coarse_y_native": _f(h.get("coarse_y_native")),
            "x_snap": _f(h.get("x_snap")), "y_snap": _f(h.get("y_snap")),
            "zncc": _f(h.get("zncc")), "rank": _f(h.get("rank")), "band": _f(h.get("band")),
            "selected": bool(h.get("selected", False)),
            "net_offpeak": [[_f(v) for v in p] for p in h.get("net_offpeak", [])],
            "net_peak_cell": [int(v) for v in h.get("net_peak_cell", [])],
            "zncc_peaks": [[_f(v) for v in p] for p in h.get("zncc_peaks", [])],
            "zncc_n_sites": int(h.get("zncc_n_sites", -1)),
            "zncc_n_local_max": int(h.get("zncc_n_local_max", -1)),
        })
    return {
        "pair_id": str(pair_id), "method": method,
        "x": _f(res.get("x")), "y": _f(res.get("y")), "theta": _f(res.get("theta")),
        "scale": _f(res.get("scale")), "score": _f(res.get("score")),
        "confidence": _f(res.get("confidence")), "zncc_med3": _f(res.get("zncc_med3")),
        "winner_margin": _f(res.get("winner_margin")),
        "rigid_x": _f(res.get("rigid_x")), "rigid_y": _f(res.get("rigid_y")),
        "n_hypotheses": int(res.get("n_hypotheses", len(hyps))),
        "selected_index": sel,
        "hypotheses": rows,
    }


def five_features(row: dict) -> dict:
    """The five logistic features (see module docstring). NaN when undefined."""
    nan = float("nan")
    idx = int(row.get("selected_index", -1))
    hyps = row.get("hypotheses", [])
    if idx < 0 or idx >= len(hyps):
        return {name: nan for name in FEATURE_NAMES}
    sel = hyps[idx]
    dist = math.hypot(sel["coarse_x_native"] - row["rigid_x"],
                      sel["coarse_y_native"] - row["rigid_y"])
    return {
        "net_score": sel["network_score"],
        "net_margin": 1.0 - sel["peak_ratio"],
        "native_zncc": sel["zncc"],
        "pose_margin": row["winner_margin"],
        "loc_agree": math.log1p(dist) if math.isfinite(dist) else nan,
    }
