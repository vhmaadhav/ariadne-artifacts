"""E15 evaluation, pre-registered in docs/PREREG_E15.md. Read-only on prediction files.

Every threshold and constant is read ONLY from the JSON given with --thresholds (a copy of the
pre-registration). This file contains no numeric threshold.

Subcommands
  set      evaluate one set (synth or real) under rules R1, R2, R3; writes a JSON.
  combine  apply H1 to H4 to the two set JSONs; writes a verdict JSON.

Exit codes: 0 ok; 2 validation or pre-registration mismatch (the kernel must fail); 1 other error.
"""
import argparse
import csv
import hashlib
import json
import math
import sys

import numpy as np

NAN = float("nan")
PAIR_KEY = "pair_id"
REQUIRED = [
    "tau_main", "tau_err5", "delta_net", "margin_excl_px", "wrong_repeat_px", "decision_tol_px",
    "success_ks", "boot_B", "boot_seed", "h1_band", "h3_cross_max", "expected", "real_tile_ids",
    "rule_names", "prereg_sha256",
]
RULES = ("R1", "R2", "R3")


class ValidationError(Exception):
    """Data or pre-registration mismatch. The kernel must stop."""


# ---------- thresholds ----------

def load_thresholds(path):
    with open(path, encoding="utf-8") as fh:
        th = json.load(fh)
    missing = [k for k in REQUIRED if k not in th]
    if missing:
        raise ValidationError(f"thresholds file missing keys {missing}")
    for k in ("tau_main", "tau_err5", "delta_net"):
        if not isinstance(th[k], (int, float)) or not math.isfinite(th[k]):
            raise ValidationError(f"threshold {k} is not a finite number")
    return th


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------- margin (E14 definition, network variant) ----------

def network_margin(feat, excl_px):
    """m_net = winner network_score minus the largest off-peak network score more than excl_px away.

    Mirrors margins() in code/e14_uniqueness_gate.py. Selected index outside the hypothesis list gives -inf.
    """
    idx = int(feat["selected_index"])
    hyps = feat["hypotheses"]
    if idx < 0 or idx >= len(hyps):
        return -math.inf
    h = hyps[idx]
    wx, wy = float(h["coarse_x_native"]), float(h["coarse_y_native"])
    comp = 0.0
    for v, x, y in h["net_offpeak"]:
        if math.hypot(float(x) - wx, float(y) - wy) > excl_px:
            comp = max(comp, float(v))
    return float(h["network_score"]) - comp


# ---------- reading and alignment ----------

def read_manifest(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    need = {PAIR_KEY, "found", "gt_x", "gt_y", "group_id", "stratum"}
    if not rows or not need <= set(rows[0]):
        raise ValidationError(f"{path}: missing columns {sorted(need - set(rows[0]) if rows else need)}")
    return rows


def read_pred(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("method") == "noexit"]
    if not rows:
        raise ValidationError(f"{path}: no noexit rows")
    return rows


def read_features(path):
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                out.append(json.loads(line))  # NaN tokens are accepted
    return out


def build(man, pred, feats, th, set_name):
    ids = [m[PAIR_KEY] for m in man]
    if len(set(ids)) != len(ids):
        raise ValidationError("manifest has duplicate pair_id")
    pmap = {}
    for p in pred:
        if p[PAIR_KEY] in pmap:
            raise ValidationError(f"duplicate prediction for {p[PAIR_KEY]}")
        pmap[p[PAIR_KEY]] = p
    fmap = {}
    for f in feats:
        if f[PAIR_KEY] in fmap:
            raise ValidationError(f"duplicate feature row for {f[PAIR_KEY]}")
        fmap[f[PAIR_KEY]] = f
    if set(pmap) != set(ids) or set(fmap) != set(ids):
        raise ValidationError(
            f"pair sets differ: manifest {len(ids)}, predictions {len(pmap)}, features {len(fmap)}")

    n = len(ids)
    a = np.empty(n); err = np.empty(n); present = np.empty(n, bool)
    m_net = np.empty(n); groups = np.empty(n, dtype=object); kind = np.empty(n, dtype=object)
    stratum = np.empty(n, dtype=object)
    excl = float(th["margin_excl_px"])
    for k, m in enumerate(man):
        pid = m[PAIR_KEY]
        p, f = pmap[pid], fmap[pid]
        if p["status"] != "ok":
            raise ValidationError(f"{pid}: prediction status {p['status']!r}")
        score = float(p["score"]); x = float(p["x"]); y = float(p["y"])
        if not (math.isfinite(score) and math.isfinite(x) and math.isfinite(y)):
            raise ValidationError(f"{pid}: non-finite prediction")
        if abs(float(f["confidence"]) - score) > 1e-9:
            raise ValidationError(f"{pid}: feature confidence differs from prediction score")
        if abs(float(f["x"]) - x) > 1e-6 or abs(float(f["y"]) - y) > 1e-6:
            raise ValidationError(f"{pid}: feature pose differs from prediction pose")
        is_present = int(float(m["found"])) == 1
        a[k] = score
        present[k] = is_present
        if is_present:
            err[k] = math.hypot(x - float(m["gt_x"]), y - float(m["gt_y"]))
            kind[k] = "present"
        else:
            err[k] = math.inf
            st = m["stratum"]
            if set_name == "real" and st.endswith("_absent_same"):
                kind[k] = "same"
            elif set_name == "real" and st.endswith("_absent_cross"):
                kind[k] = "cross"
            elif set_name == "real":
                raise ValidationError(f"{pid}: real absent pair with stratum {st!r}")
            else:
                kind[k] = "absent"
        stratum[k] = m["stratum"]
        groups[k] = m["group_id"]
        m_net[k] = network_margin(f, excl)
    return dict(ids=ids, a=a, err=err, present=present, m_net=m_net, groups=groups, kind=kind,
                stratum=stratum)


def validate_counts(d, th, set_name):
    exp = th["expected"]
    n = len(d["ids"])
    out = dict(n_pairs=n, n_present=int(d["present"].sum()), n_absent=int((~d["present"]).sum()))
    if set_name == "synth":
        if n != exp["synth_pairs"]:
            raise ValidationError(f"synthetic set has {n} pairs, expected {exp['synth_pairs']}")
        return out
    out.update(n_same=int((d["kind"] == "same").sum()), n_cross=int((d["kind"] == "cross").sum()))
    if n != exp["real_pairs"] or out["n_present"] != exp["real_present"]:
        raise ValidationError(f"real set counts {out}, expected {exp}")
    if out["n_same"] != exp["real_absent_same"] or out["n_cross"] != exp["real_absent_cross"]:
        raise ValidationError(f"real absent counts {out}, expected {exp}")
    tiles = {}
    for g, st, p in zip(d["groups"], d["stratum"], d["present"]):
        tiles.setdefault(g, []).append((st, bool(p)))
    if set(tiles) != set(th["real_tile_ids"]) or len(tiles) != len(th["real_tile_ids"]):
        raise ValidationError("real tile ids differ from the pre-registered list")
    for g, rows in tiles.items():
        count = {s: sum(1 for st, _ in rows if st == s) for s in exp["per_tile"]}
        if count != exp["per_tile"]:
            raise ValidationError(f"tile {g} has per-condition counts {count}")
    return out


# ---------- metrics from per-cluster sums ----------

def _ratio(num, den):
    num = np.asarray(num, float); den = np.asarray(den, float)
    shape = np.broadcast(num, den).shape
    out = np.full(shape, NAN)
    np.divide(num, den, out=out, where=np.broadcast_to(den > 0, shape))
    return out


def indicator_sums(d, acc, codes, K, th):
    """Per-cluster sums of each indicator. acc is the boolean accepted set for one rule."""
    P = d["present"]; Ab = ~P; err = d["err"]; kind = d["kind"]
    same = kind == "same"; cross = kind == "cross"
    k1, k5 = [float(k) for k in th["success_ks"]]
    ind = {
        "n": np.ones(len(P), bool),
        "n_present": P,
        "accepted": acc,
        "s1": P & acc & (err <= k1),
        "s5": P & acc & (err <= k5),
        "wr_count": P & acc & (err > float(th["wrong_repeat_px"])),
        "ade_count": (Ab & acc) | (P & acc & (err > float(th["decision_tol_px"]))),
        "abs_same_acc": same & acc,
        "n_abs_same": same,
        "abs_cross_acc": cross & acc,
        "n_abs_cross": cross,
        "abs_all_acc": Ab & acc,
        "n_abs": Ab,
        "tp": Ab & ~acc,
        "fp": P & ~acc,
        "fn": Ab & acc,
    }
    return {k: np.bincount(codes, weights=v.astype(float), minlength=K) for k, v in ind.items()}


def metrics_from(T):
    """T maps indicator names to totals (scalars or arrays over bootstrap replicates)."""
    out = {
        "success@1": _ratio(T["s1"], T["n_present"]),
        "success@5": _ratio(T["s5"], T["n_present"]),
        "wrong_repeats_count": np.asarray(T["wr_count"], float),
        "wrong_repeats_rate": _ratio(T["wr_count"], T["accepted"]),
        "accepted_decision_error": _ratio(T["ade_count"], T["accepted"]),
        "absent_accepted_same": _ratio(T["abs_same_acc"], T["n_abs_same"]),
        "absent_accepted_cross": _ratio(T["abs_cross_acc"], T["n_abs_cross"]),
        "absent_accepted_all": _ratio(T["abs_all_acc"], T["n_abs"]),
        "coverage": _ratio(T["accepted"], T["n"]),
        "F1_rejection": _ratio(2 * np.asarray(T["tp"], float),
                               2 * np.asarray(T["tp"], float) + T["fp"] + T["fn"]),
    }
    return out


def _avg_rank(x):
    order = np.argsort(x, kind="mergesort")
    xs = x[order]
    _, inv, counts = np.unique(xs, return_inverse=True, return_counts=True)
    csum = np.cumsum(counts)
    avg = csum - (counts - 1) / 2.0
    ranks = np.empty(len(x))
    ranks[order] = avg[inv]
    return ranks


def auroc(score, positive):
    positive = np.asarray(positive, bool)
    npos = int(positive.sum()); nneg = int((~positive).sum())
    if npos == 0 or nneg == 0:
        return NAN
    r = _avg_rank(np.asarray(score, float))
    return float((r[positive].sum() - npos * (npos + 1) / 2.0) / (npos * nneg))


def ci(vals):
    v = np.asarray(vals, float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return [None, None]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def fnum(x):
    x = float(x)
    return None if not math.isfinite(x) else x


# ---------- one set ----------

def evaluate_set(d, th, set_name):
    groups = d["groups"]
    uniq, codes = np.unique(np.asarray(groups, dtype=str), return_inverse=True)
    K = len(uniq)
    B = int(th["boot_B"])
    idx = np.random.default_rng(int(th["boot_seed"])).integers(0, K, size=(B, K))

    rules = {
        "R1": d["a"] >= th["tau_main"],
        "R2": d["a"] >= th["tau_err5"],
        "R3": (d["a"] >= th["tau_main"]) & (d["m_net"] >= th["delta_net"]),
    }
    point, boot = {}, {}
    for r, acc in rules.items():
        S = indicator_sums(d, acc, codes, K, th)
        point[r] = metrics_from({k: v.sum() for k, v in S.items()})
        reps = {k: v[idx].sum(axis=1) for k, v in S.items()}
        boot[r] = metrics_from(reps)

    names = list(point["R1"].keys())
    rule_out = {}
    for r in RULES:
        block = {"accepted": int(rules[r].sum()), "metrics": {}}
        for name in names:
            block["metrics"][name] = {"point": fnum(point[r][name]), "ci": ci(boot[r][name])}
        rule_out[f"{r}:{th['rule_names'][r]}"] = block

    paired = {}
    for name in names:
        diff_pt = point["R3"][name] - point["R1"][name]
        diff_b = boot["R3"][name] - boot["R1"][name]
        paired[name] = {"point": fnum(diff_pt), "ci": ci(diff_b)}

    # presence AUROC, rule independent; bootstrap resamples rows through the clusters
    rows_by = [np.flatnonzero(codes == k) for k in range(K)]
    au_point = auroc(d["a"], d["present"])
    au_reps = []
    for b in range(B):
        rows = np.concatenate([rows_by[k] for k in idx[b]])
        au_reps.append(auroc(d["a"][rows], d["present"][rows]))
    return dict(
        set=set_name, n_clusters=K, cluster=("tile" if set_name == "real" else "canvas"),
        rules=rule_out, paired_R3_minus_R1=paired,
        presence_auroc={"point": fnum(au_point), "ci": ci(au_reps)},
    ), point, boot


def cmd_set(args):
    th = load_thresholds(args.thresholds)
    if args.prereg:
        got = sha256_file(args.prereg)
        if got != th["prereg_sha256"]:
            raise ValidationError(f"PREREG sha256 {got} differs from thresholds {th['prereg_sha256']}")
    man = read_manifest(args.manifest)
    pred = read_pred(args.pred)
    feats = read_features(args.features)
    d = build(man, pred, feats, th, args.set)
    counts = validate_counts(d, th, args.set)
    res, _, _ = evaluate_set(d, th, args.set)
    res.update(counts=counts, prereg_sha256=th["prereg_sha256"],
               bootstrap=dict(B=int(th["boot_B"]), seed=int(th["boot_seed"]),
                              draw="default_rng(seed).integers(0, K, size=(B, K))"),
               inputs=dict(manifest=args.manifest, pred=args.pred, features=args.features))
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    r1 = res["rules"]["R1:" + th["rule_names"]["R1"]]["metrics"]
    print(f"{args.set}: N={counts['n_pairs']} success@5 R1={r1['success@5']['point']}", flush=True)


def cmd_combine(args):
    th = load_thresholds(args.thresholds)
    with open(args.synth, encoding="utf-8") as fh:
        s = json.load(fh)
    with open(args.real, encoding="utf-8") as fh:
        r = json.load(fh)
    if s["prereg_sha256"] != th["prereg_sha256"] or r["prereg_sha256"] != th["prereg_sha256"]:
        raise ValidationError("set results were produced under a different pre-registration")
    if s["set"] != "synth" or r["set"] != "real":
        raise ValidationError("combine needs the synth result first and the real result second")
    k1 = "R1:" + th["rule_names"]["R1"]
    k3 = "R3:" + th["rule_names"]["R3"]
    lo, hi = th["h1_band"]
    p1 = s["rules"][k1]["metrics"]["success@5"]
    h1 = dict(name="H1 synthetic success@5 (R1) in band", value=p1["point"], ci=p1["ci"], band=[lo, hi],
              pass_=p1["point"] is not None and lo <= p1["point"] <= hi)
    pair_s = s["paired_R3_minus_R1"]["wrong_repeats_count"]
    pair_r = r["paired_R3_minus_R1"]["wrong_repeats_count"]
    h2 = dict(name="H2 gate reduces accepted wrong repeats (paired CI upper < 0) on synth and real",
              synth=pair_s, real=pair_r,
              pass_=(pair_s["ci"][1] is not None and pair_s["ci"][1] < 0
                     and pair_r["ci"][1] is not None and pair_r["ci"][1] < 0))
    cross = r["rules"][k1]["metrics"]["absent_accepted_cross"]
    h3 = dict(name="H3 real cross-layer absent accept rate (R1) <= cap", value=cross["point"], ci=cross["ci"],
              cap=th["h3_cross_max"],
              pass_=cross["point"] is not None and cross["point"] <= th["h3_cross_max"])
    same = r["rules"][k1]["metrics"]["absent_accepted_same"]
    h4 = dict(name="H4 real same-layer unfiltered absent accept rate (R1), descriptive",
              value=same["point"], ci=same["ci"], pass_=None)
    verdict = dict(prereg_sha256=th["prereg_sha256"], H1=h1, H2=h2, H3=h3, H4=h4,
                   note="All results are reported whatever the outcome. See docs/PREREG_E15.md section 7.")
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(verdict, fh, indent=1)
    for key in ("H1", "H2", "H3"):
        print(key, "PASS" if verdict[key]["pass_"] else "FAIL", flush=True)


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("set")
    s.add_argument("--set", choices=["synth", "real"], required=True)
    s.add_argument("--manifest", required=True)
    s.add_argument("--pred", required=True)
    s.add_argument("--features", required=True)
    s.add_argument("--thresholds", required=True)
    s.add_argument("--prereg", default=None, help="PREREG_E15.md copy; its sha256 must match the thresholds")
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_set)
    c = sub.add_parser("combine")
    c.add_argument("--synth", required=True)
    c.add_argument("--real", required=True)
    c.add_argument("--thresholds", required=True)
    c.add_argument("--out", required=True)
    c.set_defaults(func=cmd_combine)
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except ValidationError as exc:
        print(f"E15 VALIDATION FAILED: {exc}", file=sys.stderr, flush=True)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
