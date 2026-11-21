import sys, json, os
from pathlib import Path
import numpy as np
# Artifact-relative paths: run from anywhere; outputs go to ./recomputed/ (created if missing).
ROOT = Path(__file__).resolve().parents[2]
RP = str(ROOT / "code" / "evaluation")
sys.path.insert(0, RP)
from iris_report import load_inputs, errors, weighted_quantiles  # noqa

def CI(arr):
    valid = arr[1:][~np.isnan(arr[1:])]
    if len(valid) == 0:
        return [float('nan'), float('nan')]
    return [float(weighted_quantiles(valid, np.ones((1, len(valid)), dtype=int), q)[0]) for q in (.025, .975)]


PRED = ROOT / "predictions"
MAN = ROOT / "manifests"
REP = ROOT / "reports"
OUT = Path("recomputed"); OUT.mkdir(exist_ok=True)
E6 = str(PRED / "acceptance")
TAU = 0.2617101
SEED, B = 20261010, 2000
SPLITS = {
    "test": (str(MAN / "synthetic_test600.csv"), str(PRED / "driftsense/second_host/test600_noexit.csv")),
    "real": (str(MAN / "real800.csv"), str(PRED / "driftsense/second_host/real800_noexit.csv")),
    "confirm": (str(MAN / "synthetic_confirm400.csv"), str(PRED / "driftsense/confirm400_noexit.csv")),
}
METHODS = ["noexit", "logistic", "evt"]
out_summary = {}
rows_table = []
rc_rows = []
for split, (man_path, base) in SPLITS.items():
    s = split
    preds = [base, f"{E6}/pred_{s}_evt.csv", f"{E6}/pred_{s}_logistic.csv"]
    man, methods = load_inputs(man_path, preds)
    # min rule: explicit tau on noexit score (same as iris_report --rethreshold)
    df0 = methods["noexit"]
    df0 = df0.assign(found=(df0.score >= TAU).astype(int))
    methods["noexit"] = df0
    # consistency: noexit found from file vs threshold
    file_found = load_inputs(man_path, [base])[1]["noexit"].found.to_numpy()
    mismatch = int((file_found != df0.found.to_numpy()).sum())
    # bootstrap draws identical to iris_report.build_report
    groups, codes = np.unique(man.group_id, return_inverse=True)
    rng = np.random.default_rng(SEED)
    draws = rng.integers(0, len(groups), size=(B, len(groups)))
    counts = np.zeros((B + 1, len(groups)), dtype=np.int32)
    counts[0] = 1
    for i, d in enumerate(draws, 1):
        counts[i] = np.bincount(d, minlength=len(groups))
    W = counts[:, codes].astype(float)
    per = {}
    for m in METHODS:
        df = methods[m]
        assert (df.pair_id.values == man.pair_id.values).all()
        present = df.found_gt.to_numpy() == 1
        found = df.found.to_numpy() == 1
        err = errors(df)[0]
        correct = present & (err <= 5)
        succ5 = present & found & (err <= 5)
        wrong = found & ~correct
        with np.errstate(invalid="ignore", divide="ignore"):
            S5 = (W @ succ5) / (W @ present)
            AE = np.where(W @ found > 0, (W @ wrong) / (W @ found), np.nan)
        per[m] = dict(S5=S5, AE=AE, present=present, found=found, correct=correct, err=err, score=df.score.to_numpy())
        # risk-coverage over score ranking (all pairs), risk = share not correct among top-k
        order = np.argsort(-per[m]["score"], kind="stable")
        wr = (~correct[order]).astype(float)
        risk = np.cumsum(wr) / np.arange(1, len(wr) + 1)
        cov = np.arange(1, len(wr) + 1) / len(wr)
        aurc = float(risk.mean())
        k_op = int(found.sum())
        # operating point check: top-k by score equals the accepted set
        top_set = np.zeros(len(found), bool); top_set[order[:k_op]] = True
        same_set = bool((top_set == found).all())
        for k in range(len(risk)):
            rc_rows.append((s, m, k + 1, cov[k], risk[k]))
        per[m]["aurc"] = aurc; per[m]["k_op"] = k_op; per[m]["same_set"] = same_set
        per[m]["accepted_error_point"] = float(wrong.sum() / found.sum()) if found.sum() else float("nan")
        per[m]["wrong_accepted"] = int(wrong.sum())
        per[m]["accepted"] = int(found.sum())
        per[m]["absent_accepted"] = int((~present & found).sum())
        per[m]["present_declined"] = int((present & ~found).sum())
        per[m]["success5_point"] = float(succ5.sum() / present.sum())
        per[m]["gross_rate"] = float((present & (err > 20)).sum() / len(df))
    # paired differences vs min rule (same draws)
    diffs = {}
    for m in ["logistic", "evt"]:
        dS = per[m]["S5"] - per["noexit"]["S5"]
        dAE = per[m]["AE"] - per["noexit"]["AE"]
        diffs[m] = {}
        for name, arr in (("dS5", dS), ("dAE", dAE)):
            lo, hi = CI(arr)
            diffs[m][name] = dict(point=float(arr[0]), lo=lo, hi=hi)
    # report-table metrics (from iris_report json for CIs)
    rep = json.load(open(REP / f"acceptance_report_{s}.json"))
    out_summary[s] = dict(mismatch_noexit_found_vs_file=mismatch, n=len(man), present=int(per["noexit"]["present"].sum()),
                          absent=int((~per["noexit"]["present"]).sum()), diffs=diffs, methods={})
    for m in METHODS:
        mm = rep["methods"][m]["metrics"]
        ci = lambda k: mm[k]
        ae = per[m]["AE"]
        out_summary[s]["methods"][m] = dict(
            success5=ci("success@5"), success1=ci("success@1"), success3=ci("success@3"),
            accepted_error=dict(point=per[m]["accepted_error_point"], lo=CI(ae)[0], hi=CI(ae)[1]),
            wrong_accepted=per[m]["wrong_accepted"], accepted=per[m]["accepted"],
            absent_accepted=ci("absent_accepted"), present_declined=ci("present_declined"),
            F1=ci("F1"), auroc_present=ci("auroc_present"), gross_rate=ci("gross_rate"),
            aurc=per[m]["aurc"], k_op=per[m]["k_op"], rank_matches_accepted_set=per[m]["same_set"])
    print("==", s, "mismatch", mismatch, "n", len(man))
    for m in METHODS:
        mm = out_summary[s]["methods"][m]
        print(m, "S5 %.3f [%.3f,%.3f]" % (mm["success5"]["value"], mm["success5"]["lo"], mm["success5"]["hi"]), "AE", round(mm["accepted_error"]["point"], 4),
              "[%.4f,%.4f]" % (mm["accepted_error"]["lo"], mm["accepted_error"]["hi"]),
              "wrongacc", mm["wrong_accepted"], "/", mm["accepted"], "absAcc", mm["absent_accepted"]["value"],
              "presDecl", mm["present_declined"]["value"], "F1", round(mm["F1"]["value"], 3), "AUROC", round(mm["auroc_present"]["value"], 3),
              "AURC", round(mm["aurc"], 4), "k_op", mm["k_op"], "same_set", mm["rank_matches_accepted_set"])
    for m in ["logistic", "evt"]:
        d = diffs[m]
        print("diff", m, "dS5 %.4f [%.4f,%.4f]" % (d["dS5"]["point"], d["dS5"]["lo"], d["dS5"]["hi"]),
              "dAE %.4f [%.4f,%.4f]" % (d["dAE"]["point"], d["dAE"]["lo"], d["dAE"]["hi"]))

json.dump(out_summary, open(OUT / "e6_metrics.json", "w"), indent=1, default=float)
with open(OUT / "riskcoverage_all_splits.csv", "w") as fh:
    fh.write("split,method,k,coverage,risk\n")
    for r in rc_rows:
        fh.write(f"{r[0]},{r[1]},{r[2]},{r[3]:.6f},{r[4]:.6f}\n")
print("wrote e6_metrics.json and riskcoverage_all_splits.csv")
