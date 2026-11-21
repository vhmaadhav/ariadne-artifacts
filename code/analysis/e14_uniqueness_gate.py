"""E14 (EXPLORATORY, post hoc): uniqueness gate on top of the min rule.

Rule tested:  accept iff a >= tau AND margin >= delta
  a       = prediction-CSV score = min(s_net, zncc_med3)   (the min rule)
  margin  = winner score minus the strongest competing site outside a 20 px exclusion
    net   : winner = selected network_score; competitors = net_offpeak [score, x, y]
            with distance > 20 px from the selected network location (coarse_*_native)
    zncc  : winner = selected native zncc;   competitors = zncc_peaks [value, x, y]
            with distance > 20 px from the selected snap (x_snap, y_snap)
  No competitor in the logged list -> competitor score 0.
  Selected index -1 (no hypothesis) -> margin = -inf (declined by the gate).

delta is chosen on the dev split only: smallest delta (over the candidate grid) with
dev accepted-decision error <= 5 %; also the dev F1-maximising delta. Then applied
unchanged to test, confirmation, real and the E8 unfiltered-absent set.

Dev split: the 800-pair large dev has no per-pair feature rows (only pred CSV), so the
150-pair dev (results/e4/a) is used as the fitting split. See SUMMARY.md.

Metrics follow code/e10_eval.py. Accepted-decision error = accepted pairs that are
absent, or present with error > 5 px, divided by accepted. Accepted wrong repeats =
present, accepted, error > 20 px. Cluster bootstrap by group_id (tile for E8),
2000 draws, seed 20261010, paired draws for gate vs min rule.
"""
import csv, json, math, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEV_ROOT = ROOT.parent / "driftsense-iris27" / "manifests"
R = ROOT / "results"
OUT = R / "e14_uniqueness_gate"
OUT.mkdir(parents=True, exist_ok=True)

TAU_MAIN = 0.2617101
TAU_ERR5 = 0.3108282387256622
EXCL = 20.0
B = 2000
SEED = 20261010

SPLITS = {
    "dev150": dict(man=DEV_ROOT / "manifest_dev.csv",
                   pred=R / "e4/a/results/ariadne/E4/pred_dev_noexit.csv",
                   feat=R / "e4/a/results/ariadne/E4/feat_dev_noexit.jsonl", group="group_id"),
    "test600": dict(man=R / "e2/inputs/manifest_test_600.csv",
                    pred=R / "e4/a/results/ariadne/E4/pred_test_noexit.csv",
                    feat=R / "e4/a/results/ariadne/E4/feat_test_noexit.jsonl", group="group_id"),
    "confirm400": dict(man=R / "e5/manifest_confirm.csv",
                       pred=R / "e4/c/results/ariadne/E5_confirm/pred_confirm_noexit.csv",
                       feat=R / "e4/c/results/ariadne/E5_confirm/feat_confirm_noexit.jsonl", group="group_id"),
    "real800": dict(man=DEV_ROOT / "manifest_real.csv",
                    pred=R / "e4/b/results/ariadne/E4/pred_real_noexit.csv",
                    feat=R / "e4/b/results/ariadne/E4/feat_real_noexit.jsonl", group="group_id"),
    "e8_absent": dict(man=R / "e8/build_manifest.csv",
                      pred=R / "e8/pred_absent_unfiltered_noexit.csv",
                      feat=R / "e8/feat_absent_unfiltered_noexit.jsonl", group="tile"),
}


def read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def margins(row):
    """Return (margin_net, margin_zncc) for one feature row."""
    idx = int(row["selected_index"])
    hyps = row["hypotheses"]
    if idx < 0 or idx >= len(hyps):
        return -math.inf, -math.inf
    h = hyps[idx]
    wx, wy = h["coarse_x_native"], h["coarse_y_native"]
    comp_net = 0.0
    for v, x, y in h["net_offpeak"]:
        if math.hypot(x - wx, y - wy) > EXCL:
            comp_net = max(comp_net, v)
    m_net = h["network_score"] - comp_net
    sx, sy = h["x_snap"], h["y_snap"]
    comp_z = 0.0
    for v, x, y in h["zncc_peaks"]:
        if math.hypot(x - sx, y - sy) > EXCL:
            comp_z = max(comp_z, v)
    m_z = h["zncc"] - comp_z
    return m_net, m_z


def load(name, cfg):
    man = {r["pair_id"]: r for r in read_csv(cfg["man"])}
    pred = {r["pair_id"]: r for r in read_csv(cfg["pred"]) if r["method"] == "noexit"}
    feats = {}
    with open(cfg["feat"]) as fh:
        for line in fh:
            r = json.loads(line)
            feats[r["pair_id"]] = r
    assert set(man) == set(pred) == set(feats), (name, len(man), len(pred), len(feats))
    ids = sorted(man)
    n = len(ids)
    a = np.array([float(pred[i]["score"]) for i in ids])
    px = np.array([float(pred[i]["x"]) for i in ids])
    py = np.array([float(pred[i]["y"]) for i in ids])
    feat_mismatch = sum(abs(feats[i]["confidence"] - a[k]) > 1e-9 for k, i in enumerate(ids))
    pos_mismatch = sum(abs(feats[i]["x"] - px[k]) > 1e-6 or abs(feats[i]["y"] - py[k]) > 1e-6
                       for k, i in enumerate(ids))
    present = np.array([int(float(man[i]["found"])) == 1 for i in ids])
    gx = np.array([float(man[i]["gt_x"]) for i in ids])
    gy = np.array([float(man[i]["gt_y"]) for i in ids])
    err = np.hypot(px - gx, py - gy)
    err = np.where(present, err, np.inf)
    groups = np.array([man[i][cfg["group"]] for i in ids])
    m_net = np.zeros(n); m_z = np.zeros(n); nosel = 0
    for k, i in enumerate(ids):
        m_net[k], m_z[k] = margins(feats[i])
        nosel += int(feats[i]["selected_index"]) < 0
    return dict(name=name, ids=ids, a=a, present=present, err=err, groups=groups,
                m_net=m_net, m_z=m_z, nosel=nosel, feat_mismatch=feat_mismatch,
                pos_mismatch=pos_mismatch)


def masks(d, tau, margin, delta):
    acc_min = d["a"] >= tau
    gate = acc_min & (margin >= delta)
    return acc_min, gate


def stats(d, A):
    p, e = d["present"], d["err"]
    absent = ~p
    nA = A.sum(); nP = p.sum(); nAb = absent.sum(); N = len(A)
    wrong_e10 = (absent & A) | (p & A & (e > 5))
    return dict(
        num_s5=(p & A & (e <= 5)).sum(), den_s5=nP,
        num_wr=(p & A & (e > 20)).sum(),
        num_ade=wrong_e10.sum(), den_acc=nA,
        num_abs=(absent & A).sum(), den_abs=nAb,
        num_cov=nA, den_cov=N,
    )


def ratio(num, den):
    return float(num / den) if den else float("nan")


def summary(d, A):
    s = stats(d, A)
    p, e = d["present"], d["err"]
    absent = ~p
    tp = (absent & ~A).sum(); fp = (p & ~A).sum(); fn = (absent & A).sum()
    f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else float("nan")
    return dict(
        accepted=int(s["den_acc"]), coverage=ratio(s["num_cov"], s["den_cov"]),
        success5=ratio(s["num_s5"], s["den_s5"]),
        wrong_repeats_count=int(s["num_wr"]),
        wrong_repeats_rate_of_accepted=ratio(s["num_wr"], s["den_acc"]),
        absent_accepted=int(s["num_abs"]), absent_total=int(s["den_abs"]),
        absent_accepted_rate=ratio(s["num_abs"], s["den_abs"]),
        accepted_decision_error=ratio(s["num_ade"], s["den_acc"]),
        F1_rejection=float(f1),
    )


def cluster_ci_single(d, A, B=B, seed=SEED):
    groups = d["groups"]
    uniq, codes = np.unique(groups, return_inverse=True)
    k = len(uniq)
    p = d["present"].astype(float)
    hit = (d["present"] & A & (d["err"] <= 5)).astype(float)
    sh = np.bincount(codes, weights=hit, minlength=k)
    sp = np.bincount(codes, weights=p, minlength=k)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(B):
        idx = rng.integers(0, k, k)
        if sp[idx].sum():
            vals.append(sh[idx].sum() / sp[idx].sum())
    if not vals:
        return [float("nan"), float("nan")]
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def paired_boot(d, A_gate, A_min, B=B, seed=SEED):
    """Cluster bootstrap of (gate - min) differences in each metric, same draws for both."""
    groups = d["groups"]
    uniq, codes = np.unique(groups, return_inverse=True)
    k = len(uniq)
    p, e = d["present"], d["err"]
    absent = ~p

    def per_cluster(A):
        wrong_e10 = ((absent & A) | (p & A & (e > 5))).astype(float)
        s5 = (p & A & (e <= 5)).astype(float)
        wr = (p & A & (e > 20)).astype(float)
        ab = (absent & A).astype(float)
        acc = A.astype(float)
        cnt_p = p.astype(float)
        cnt_ab = absent.astype(float)
        one = np.ones(len(A))
        cs = lambda v: np.bincount(codes, weights=v, minlength=k)
        return dict(s5=cs(s5), p=cs(cnt_p), wr=cs(wr), acc=cs(acc), ade=cs(wrong_e10),
                    ab=cs(ab), nab=cs(cnt_ab), cov=cs(acc), n=cs(one))

    G = per_cluster(A_gate); M = per_cluster(A_min)
    rng = np.random.default_rng(seed)
    diffs = {"success5": [], "wrong_repeats_count": [], "wrong_repeats_rate_of_accepted": [],
             "accepted_decision_error": [], "coverage": [], "absent_accepted_rate": []}
    for _ in range(B):
        idx = rng.integers(0, k, k)
        def ratios(X):
            return dict(
                success5=X["s5"][idx].sum() / X["p"][idx].sum() if X["p"][idx].sum() else np.nan,
                wrong_repeats_count=X["wr"][idx].sum(),
                wrong_repeats_rate_of_accepted=X["wr"][idx].sum() / X["acc"][idx].sum() if X["acc"][idx].sum() else np.nan,
                accepted_decision_error=X["ade"][idx].sum() / X["acc"][idx].sum() if X["acc"][idx].sum() else np.nan,
                coverage=X["cov"][idx].sum() / X["n"][idx].sum(),
                absent_accepted_rate=X["ab"][idx].sum() / X["nab"][idx].sum() if X["nab"][idx].sum() else np.nan,
            )
        rg = ratios(G); rm = ratios(M)
        for key in diffs:
            diffs[key].append(rg[key] - rm[key])
    out = {}
    for key, v in diffs.items():
        v = np.array(v, dtype=float)
        v = v[np.isfinite(v)]
        if len(v) == 0:
            out[key] = [float("nan"), float("nan")]
        else:
            out[key] = [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
    return out


def choose_delta(dev, tau, which):
    margin = dev["m_net"] if which == "net" else dev["m_z"]
    acc_min = dev["a"] >= tau
    cand = np.unique(margin[acc_min & np.isfinite(margin)])
    grid = [-math.inf] + list(cand)
    curve = []
    best_err_delta = None
    best_f1 = (-1.0, None)
    for dlt in grid:
        A = acc_min & (margin >= dlt)
        s = summary(dev, A)
        curve.append(dict(delta=None if dlt == -math.inf else float(dlt),
                          accepted=s["accepted"], accepted_decision_error=s["accepted_decision_error"],
                          F1=s["F1_rejection"], success5=s["success5"]))
        if best_err_delta is None and s["accepted"] > 0 and s["accepted_decision_error"] <= 0.05:
            best_err_delta = dlt
        if s["F1_rejection"] > best_f1[0] + 1e-12:
            best_f1 = (s["F1_rejection"], dlt)
    return dict(
        delta_err5=None if best_err_delta is None else (None if best_err_delta == -math.inf else float(best_err_delta)),
        delta_err5_is_no_gate=bool(best_err_delta == -math.inf) if best_err_delta is not None else False,
        delta_err5_found=best_err_delta is not None,
        delta_maxF1=None if best_f1[1] == -math.inf else float(best_f1[1]),
        delta_maxF1_is_no_gate=bool(best_f1[1] == -math.inf),
        maxF1=float(best_f1[0]), curve_len=len(grid), curve=curve,
    )


def main():
    data = {n: load(n, c) for n, c in SPLITS.items()}
    results = {"splits": {}, "delta_choice": {}, "notes": {}}
    for n, d in data.items():
        results["notes"][n] = dict(
            N=len(d["ids"]), present=int(d["present"].sum()), absent=int((~d["present"]).sum()),
            selected_index_minus1=d["nosel"], score_vs_confidence_mismatch=d["feat_mismatch"],
            xy_vs_feature_mismatch=d["pos_mismatch"])
        print(n, results["notes"][n], flush=True)
    dev = data["dev150"]
    for tau_name, tau in [("tau_0.2617", TAU_MAIN), ("tau_err5_0.3108", TAU_ERR5)]:
        for which in ["net", "zncc"]:
            key = f"{tau_name}|{which}"
            ch = choose_delta(dev, tau, which)
            results["delta_choice"][key] = {k: v for k, v in ch.items() if k != "curve"}
            results["delta_choice"][key]["dev_curve"] = ch["curve"]
            # delta: smallest with dev err<=5%; if none found, record and fall back to max-F1 delta
            delta = ch["delta_err5"] if ch["delta_err5_found"] else ch["delta_maxF1"]
            if ch["delta_err5_is_no_gate"]:
                delta = -math.inf
            results["delta_choice"][key]["delta_used"] = None if delta is None or delta == -math.inf else float(delta)
            if delta is None:
                delta = -math.inf
            results["delta_choice"][key]["delta_used_is_no_gate"] = bool(delta == -math.inf)
            results["splits"][key] = {}
            for n, d in data.items():
                margin = d["m_net"] if which == "net" else d["m_z"]
                A_min, A_gate = masks(d, tau, margin, delta)
                block = dict(min_rule=summary(d, A_min), gate=summary(d, A_gate))
                if n != "e8_absent":
                    block["success5_CI_min"] = cluster_ci_single(d, A_min)
                    block["success5_CI_gate"] = cluster_ci_single(d, A_gate)
                block["paired_gate_minus_min_CI"] = paired_boot(d, A_gate, A_min)
                results["splits"][key][n] = block
                print(key, n, "min acc", block["min_rule"]["accepted"], "gate acc", block["gate"]["accepted"],
                      "wr", block["min_rule"]["wrong_repeats_count"], "->", block["gate"]["wrong_repeats_count"], flush=True)
    (OUT / "gate_results.json").write_text(json.dumps(results, indent=1, default=float))
    print("wrote", OUT / "gate_results.json")


if __name__ == "__main__":
    main()
