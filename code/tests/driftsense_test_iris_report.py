"""Hand-computed IRIS examples, independent of repository datasets."""
import json
import time

import numpy as np
import pandas as pd
import pytest

from scripts import iris_report as report


def toy():
    n = 12
    man = pd.DataFrame({
        "pair_id": [f"p{i}" for i in range(n)], "split": "test",
        "reference_path": "ref.png", "search_path": "search.png",
        "found": [1]*8+[0]*4, "gt_x": [0.]*8+[-1.]*4,
        "gt_y": [0.]*8+[-1.]*4, "gt_scale": [10.]*8+[np.nan]*4,
        "gt_rot_deg": [179.]+[0.]*7+[np.nan]*4,
        "label_convention": "center", "stratum": ["easy"]*4+["hard"]*4+["absent"]*4,
        "group_id": [f"g{i % 3}" for i in range(n)], "source": "synthetic",
    })
    score = [.9, .8, .7, .6, .4, .3, .2, .1, .65, .35, .15, .05]
    pred = pd.DataFrame({
        "pair_id": man.pair_id, "method": "A", "found": np.array(score) >= .5,
        "score": score, "x": [0., 1., 2., 3., 5., 6., 21., 0.]+[0.]*4,
        "y": 0., "theta": [-179., 0., .25, .5, 1., 5., 10., .75]+[np.nan]*4,
        "scale": [10., 10.1, 10.2, 10.5, 11., 12., 10., 10.4]+[np.nan]*4,
        "seconds": np.arange(1, n+1, dtype=float), "status": "ok",
    })
    pred["found"] = pred.found.astype(int)
    other = pred.copy()
    other["method"] = "B"
    other["found"] = 1
    return man, pd.concat([pred, other], ignore_index=True)


def files(tmp_path, man=None, pred=None):
    default_man, default_pred = toy()
    man = default_man if man is None else man
    pred = default_pred if pred is None else pred
    m, p = tmp_path/"manifest.csv", tmp_path/"pred.csv"
    man.to_csv(m, index=False)
    pred.to_csv(p, index=False)
    return m, p


def test_hand_computed_metrics(tmp_path):
    m, p = files(tmp_path)
    man, methods = report.load_inputs(m, [p])
    result = report.build_report(man, methods, bootstrap=30, ref="A")
    a = result["methods"]["A"]["metrics"]
    expected = {
        "n_present": 8, "n_absent": 4, "success@1": 2/8, "success@3": 4/8,
        "success@5": 4/8, "loc_only@1": 3/8, "loc_only@3": 5/8,
        "loc_only@5": 6/8, "gross_rate": 1/8, "err_px_p50": 2.5,
        "err_px_p90": 10.5, "err_px_p95": 15.75,
        "absent_accepted": 1, "present_declined": 4, "absent_declined": 3,
        "precision": 3/7, "recall": 3/4, "F1": 6/11,
        "auroc_present": 23/32, "correct_match_auc": 29/36,
        "scale_pct_all_median": 3, "scale_pct_all_p90": 13,
        "scale_pct_all_within1": 3/8, "scale_pct_all_within2": 4/8,
        "scale_pct_all_within5": 6/8,
        "rotation_deg_all_median": .875, "rotation_deg_all_p90": 6.5,
        "rotation_deg_all_within0.25": 2/8, "rotation_deg_all_within0.5": 3/8,
        "rotation_deg_all_within1": 5/8,
        "pose_within5_n": 4, "scale_pct_within5_median": 1.5,
        "scale_pct_within5_p90": 4.1, "scale_pct_within5_within1": 2/4,
        "scale_pct_within5_within2": 3/4, "scale_pct_within5_within5": 1,
        "rotation_deg_within5_median": .375, "rotation_deg_within5_p90": 1.55,
        "rotation_deg_within5_within0.25": 2/4,
        "rotation_deg_within5_within0.5": 3/4, "rotation_deg_within5_within1": 3/4,
        "runtime_median": 6.5, "runtime_p90": 10.9, "runtime_p95": 11.45,
        "runtime_max": 12,
    }
    for key, value in expected.items():
        assert a[key]["value"] == pytest.approx(value), key
    assert report.errors(methods["A"])[2][0] == 2  # 179 to -179 wraps
    b = result["methods"]["B"]["metrics"]
    assert b["F1"]["value"] == 0
    assert b["success@1"]["value"] == 3/8
    diffs = result["differences"]["B"]
    assert diffs["success@1"]["value"] == 1/8
    assert diffs["success@5"]["value"] == 2/8
    assert diffs["F1"]["value"] == -6/11
    assert diffs["err_px_p50"]["lo"] == diffs["err_px_p50"]["hi"] == 0
    assert result["methods"]["A"]["strata"]["hard"]["success@5"]["value"] == 0


def test_seed_and_bootstrap_matches_explicit_cluster_resampling(tmp_path):
    m, p = files(tmp_path)
    man, methods = report.load_inputs(m, [p])
    first = report.build_report(man, methods, bootstrap=50, seed=20261010, ref="A")
    second = report.build_report(man, methods, bootstrap=50, seed=20261010, ref="A")
    assert report.json_safe(first) == report.json_safe(second)
    rng = np.random.default_rng(20261010)
    groups = np.unique(man.group_id)
    medians, successes, aucs = [], [], []
    df = methods["A"]
    for draw in rng.integers(0, 3, size=(50, 3)):
        sampled = pd.concat([df.loc[df.group_id.eq(groups[i])] for i in draw])
        present = sampled.found_gt.eq(1)
        err = report.errors(sampled)[0]
        medians.append(np.median(err[present]))
        successes.append((sampled.found.eq(1).to_numpy()[present] & (err[present] <= 1)).mean())
        aucs.append(report.roc_auc_score(present, sampled.score))
    metrics = first["methods"]["A"]["metrics"]
    for key, values in (("err_px_p50", medians), ("success@1", successes), ("auroc_present", aucs)):
        assert [metrics[key]["lo"], metrics[key]["hi"]] == pytest.approx(np.quantile(values, [.025, .975]))


def test_weighted_quantiles_exact():
    values = np.array([0., 2., 9., np.inf])
    weights = np.array([[2, 1, 3, 0], [0, 0, 0, 0], [1, 0, 0, 1]])
    for q in (0, .5, .9, .95, 1):
        got = report.weighted_quantiles(values, weights, q)
        assert got[0] == pytest.approx(np.quantile(np.repeat(values, weights[0]), q))
        assert np.isnan(got[1])
        assert got[2] == (0 if q == 0 else np.inf)


def test_dev_threshold_ties_and_reject_all(tmp_path):
    df = pd.DataFrame({"score": [.1, .2, .3, .4, .5, .6], "found_gt": [0, 1, 1, 0, 1, 1]})
    # .2 and .5 both yield F1=.5. The lower threshold wins.
    assert report.choose_dev_threshold(df) == .2
    assert report.choose_dev_threshold(pd.DataFrame({"score": [.1, .9], "found_gt": [0, 0]})) == np.nextafter(.9, np.inf)
    man, pred = toy()
    m, p = files(tmp_path, man, pred)
    test_man, methods = report.load_inputs(m, [p])
    dev_man, dev_pred = toy()
    dev_man["split"] = "dev"
    dev_man["pair_id"] = "dev_" + dev_man.pair_id
    dev_pred["pair_id"] = "dev_" + dev_pred.pair_id
    dm, dp = tmp_path/"dev.csv", tmp_path/"dev_pred.csv"
    dev_man.to_csv(dm, index=False)
    dev_pred.to_csv(dp, index=False)
    chosen = report.rethreshold(methods, [f"A=dev:{dm},{dp}"], test_man)
    assert chosen["A"]["threshold"] == .7
    assert methods["A"].found.tolist() == (methods["A"].score >= .7).astype(int).tolist()
    # Test labels cannot affect the selected threshold.
    test_man["found"] = 1-test_man.found
    assert report.rethreshold(methods, [f"A=dev:{dm},{dp}"], test_man) == chosen
    dev_man["pair_id"] = man.pair_id
    dev_pred["pair_id"] = pred.pair_id
    dev_man.to_csv(dm, index=False)
    dev_pred.to_csv(dp, index=False)
    with pytest.raises(ValueError, match="overlap"):
        report.rethreshold(methods, [f"A=dev:{dm},{dp}"], test_man)


@pytest.mark.parametrize("case", ["missing", "duplicate_pred", "duplicate_manifest", "extra", "collision"])
def test_join_rejects_bad_inputs(tmp_path, case):
    man, pred = toy()
    if case == "missing":
        pred = pred.iloc[1:]
    elif case == "duplicate_pred":
        pred = pd.concat([pred, pred.iloc[:1]])
    elif case == "duplicate_manifest":
        man = pd.concat([man, man.iloc[:1]])
    elif case == "extra":
        extra = pred.iloc[:1].copy()
        extra["pair_id"] = "unknown"
        pred = pd.concat([pred, extra])
    m, p = files(tmp_path, man, pred)
    paths = [p, p] if case == "collision" else [p]
    with pytest.raises(ValueError, match={"missing": "missing pairs", "extra": "extra pairs", "collision": "collision"}.get(case, "duplicate")):
        report.load_inputs(m, paths)


def test_missing_pose_empty_subsets_single_class(tmp_path):
    man, pred = toy()
    pred.loc[pred.pair_id.eq("p0"), ["x", "theta", "scale"]] = np.nan
    m, p = files(tmp_path, man, pred)
    _, methods = report.load_inputs(m, [p])
    df = methods["A"]
    metrics = report.metric_arrays(df, np.ones((1, 12), dtype=int))
    assert metrics["gross_rate"][0] == 2/8
    assert metrics["scale_pct_all_within1"][0] == 2/8
    df = df.loc[df.found_gt.eq(0)].copy()
    empty = report.metric_arrays(df, np.ones((1, len(df)), dtype=int))
    assert np.isnan(empty["auroc_present"][0])
    assert np.isnan(empty["correct_match_auc"][0])
    assert np.isnan(empty["err_px_p50"][0])


def test_cli_sweep_and_json(tmp_path, capsys):
    m, p = files(tmp_path)
    prefix = tmp_path/"report"
    report.main(["--manifest", str(m), "--pred", str(p), "--bootstrap", "20", "--ref", "A", "--out-prefix", str(prefix), "--sweep", "--rethreshold", "A=0.5"])
    result = json.loads(prefix.with_suffix(".json").read_text())
    assert result["methods"]["A"]["metrics"]["F1"]["value"] == 6/11
    text = prefix.with_suffix(".md").read_text()
    assert "## Scale and rotation" in text
    assert "## Paired differences against A" in text
    header = (tmp_path/"report_sweep_A.csv").read_text().splitlines()[0]
    assert "provenance unverified" in header
    swept = pd.read_csv(tmp_path/"report_sweep_A.csv", comment="#")
    assert len(swept) == 12
    at = swept.loc[swept.threshold.eq(.6)].iloc[0]
    assert at.F1 == pytest.approx(6/11)
    assert at["success@5"] == 4/8
    assert "success@1" in capsys.readouterr().out


def test_six_method_800_pair_benchmark(tmp_path):
    """Exercise the requested workload once; no brittle wall-clock assertion."""
    man, pred = toy()
    pred = pred.loc[pred.method.eq("A")]
    frames, manifests = [], []
    for i in range(67):
        m = man.copy()
        m["pair_id"] = str(i)+"_"+m.pair_id
        m["group_id"] = str(i)+"_"+m.group_id
        manifests.append(m)
        for j in range(6):
            p = pred.copy()
            p["pair_id"] = str(i)+"_"+p.pair_id
            p["method"] = f"M{j}"
            frames.append(p)
    man = pd.concat(manifests, ignore_index=True).iloc[:800]
    pred = pd.concat(frames, ignore_index=True)
    pred = pred.loc[pred.pair_id.isin(man.pair_id)]
    m, p = files(tmp_path, man, pred)
    man, methods = report.load_inputs(m, [p])
    start = time.perf_counter()
    result = report.build_report(man, methods, bootstrap=2000, ref="M0")
    print(f"800 pairs / 6 methods / 2000 replicates: {time.perf_counter()-start:.3f}s")
    assert result["methods"]["M0"]["metrics"]["F1"]["valid_bootstrap"] == 2000
