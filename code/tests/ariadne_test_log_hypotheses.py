"""Row builder and feature extraction on a synthetic locate_phase2-like result."""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import evt_accept as ea  # noqa: E402
import log_hypotheses as lh  # noqa: E402


def _result():
    hyp = {"scale": 9.5, "theta": 1.0, "pose_peak": 0.7, "score": 0.9, "network_score": 0.9,
           "peak_ratio": 0.2, "psr": 6.0, "apce": 3.0, "coarse_x_native": 500.0,
           "coarse_y_native": 400.0, "x": 501.0, "y": 401.0, "x_snap": 501.0, "y_snap": 401.0,
           "zncc": 0.8, "rank": 0.5, "band": 0.5, "dog": 0.1, "selected": True,
           "net_offpeak": [[0.5, 520.0, 400.0]], "net_peak_cell": [10, 20],
           "zncc_peaks": [[0.4, 540.0, 400.0], [0.3, 500.0, 480.0]],
           "zncc_n_sites": 2, "zncc_n_local_max": 3}
    other = dict(hyp, selected=False, zncc=0.2, network_score=0.7)
    return {"x": 501.0, "y": 401.0, "theta": 1.0, "scale": 9.5, "score": 0.9,
            "confidence": 0.8, "zncc_med3": 0.8, "winner_margin": 0.05,
            "rigid_x": 503.0, "rigid_y": 404.0, "n_hypotheses": 2,
            "hypotheses": [other, hyp]}


def test_row_is_json_serialisable_and_keeps_selection():
    row = lh.feature_row("p1", _result(), "noexit")
    line = json.dumps(row, allow_nan=True)
    back = json.loads(line)
    assert back["selected_index"] == 1
    assert back["hypotheses"][1]["selected"] is True


def test_five_features_values():
    row = json.loads(json.dumps(lh.feature_row("p1", _result())))
    f = lh.five_features(row)
    assert math.isclose(f["net_score"], 0.9)
    assert math.isclose(f["net_margin"], 0.8)
    assert math.isclose(f["native_zncc"], 0.8)
    assert math.isclose(f["pose_margin"], 0.05)
    assert math.isclose(f["loc_agree"], math.log1p(math.hypot(3.0, 4.0)))


def test_missing_selection_gives_nan_features():
    res = _result()
    for h in res["hypotheses"]:
        h["selected"] = False
    row = lh.feature_row("p2", res)
    assert row["selected_index"] == -1
    assert all(math.isnan(v) for v in lh.five_features(row).values())


def test_evt_row_score_uses_logged_zncc_peaks():
    row = lh.feature_row("p1", _result())
    out = ea.evt_row_score(row, exclude_radius=16.0)
    assert out["winner_score"] == 0.8
    assert out["n_fit"] == 2
    assert math.isclose(out["margin"], 0.8 - 0.4)


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
