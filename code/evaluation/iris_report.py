#!/usr/bin/env python3
"""IRIS tables with paired cluster bootstrap. See iris_spec.md for definitions.

Undefined metrics use NaN internally and JSON null. Missing raw poses count as
infinite errors, including gross failures. Infinite quantiles use JSON strings.
"""
from __future__ import annotations

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_name] = "4"

import argparse
import json
import re
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

MANIFEST = "pair_id split reference_path search_path found gt_x gt_y gt_scale gt_rot_deg label_convention stratum group_id source".split()
PRED = "pair_id method found score x y theta scale seconds status".split()
NOTES = (
    "95% percentile cluster bootstrap; thresholds fixed; rates are fractions. "
    "Missing poses count as infinite error and fail all tolerance checks. "
    "Empty denominators and single-class AUCs are NaN; zero-division rejection scores are 0. "
    "Undefined bootstrap replicates are excluded; valid replicate counts are in JSON. "
    "JSON null means NaN; Infinity strings mean unbounded error."
)


def read_csv(path, columns):
    df = pd.read_csv(path, dtype={c: str for c in ("pair_id", "method", "group_id", "stratum", "split")})
    missing = set(columns) - set(df)
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")
    for c in ("pair_id", "method", "group_id", "stratum", "split"):
        if c in df and (df[c].isna().any() or df[c].str.strip().eq("").any()):
            raise ValueError(f"{path}: empty {c}")
    if df.empty:
        raise ValueError(f"{path}: empty CSV")
    if not df.found.isin([0, 1]).all():
        raise ValueError(f"{path}: found must be 0/1")
    return df


def load_inputs(manifest, predictions):
    man = read_csv(manifest, MANIFEST)
    if man.pair_id.duplicated().any():
        raise ValueError("manifest: duplicate pair_id")
    present = man.found.eq(1)
    for c in ("gt_x", "gt_y", "gt_scale", "gt_rot_deg"):
        if not np.isfinite(man.loc[present, c]).all():
            raise ValueError(f"manifest: present {c} must be finite")
    if (man.loc[present, "gt_scale"] <= 0).any():
        raise ValueError("manifest: gt_scale must be positive")
    if not man.label_convention.isin(["edge", "center"]).all():
        raise ValueError("manifest: invalid label_convention")
    methods = {}
    for path in predictions:
        pred = read_csv(path, PRED)
        if pred.duplicated(["method", "pair_id"]).any():
            raise ValueError(f"{path}: duplicate method/pair_id")
        # Scores are the decoder's confidence: min(network score, ZNCC), and a ZNCC can be slightly
        # negative on an absent pair, so [-1, 1] is accepted (only the ordering of scores is used).
        if not (np.isfinite(pred.score).all() and pred.score.between(-1, 1).all()):
            raise ValueError(f"{path}: score must be finite in [-1,1]")
        if not (np.isfinite(pred.seconds).all() and pred.seconds.ge(0).all()):
            raise ValueError(f"{path}: seconds must be finite and nonnegative")
        for method, frame in pred.groupby("method", sort=True):
            if method in methods:
                raise ValueError(f"method collision across prediction files: {method}")
            missing = set(man.pair_id) - set(frame.pair_id)
            extra = set(frame.pair_id) - set(man.pair_id)
            if missing or extra:
                raise ValueError(f"{method}: missing pairs {sorted(missing)}; extra pairs {sorted(extra)}")
            joined = man.merge(frame, on="pair_id", how="inner", validate="one_to_one", suffixes=("_gt", ""))
            methods[method] = joined
    return man, methods


def errors(df):
    err = np.hypot(df.x.to_numpy() - df.gt_x, df.y.to_numpy() - df.gt_y)
    scale = 100 * np.abs(df.scale.to_numpy() - df.gt_scale) / df.gt_scale
    rot = np.abs((df.theta.to_numpy() - df.gt_rot_deg + 180) % 360 - 180)
    return tuple(np.where(np.isfinite(a), a, np.inf) for a in (err, scale, rot))


def weighted_quantiles(values, weights, q):
    """Exact numpy linear quantiles for integer row multiplicities, without expansion."""
    if not len(values):
        return np.full(len(weights), np.nan)
    order = np.argsort(values)
    values = np.asarray(values)[order]
    cumulative = weights[:, order].cumsum(axis=1)
    total = cumulative[:, -1]
    position = np.maximum(total - 1, 0) * q
    low = np.sum(cumulative <= np.floor(position)[:, None], axis=1).clip(max=len(values)-1)
    high = np.sum(cumulative <= np.ceil(position)[:, None], axis=1).clip(max=len(values)-1)
    a, b = values[low], values[high]
    fraction = position - np.floor(position)
    result = a.copy()
    different = (a != b) & (fraction > 0)
    with np.errstate(invalid="ignore"):
        result[different] = a[different] * (1-fraction[different]) + b[different] * fraction[different]
    result[total == 0] = np.nan
    return result


def metric_arrays(df, weights, full=True, *, cluster_counts=None, cluster_codes=None):
    """Compute point estimate and bootstrap scalars in a single weighted pass."""
    present = df.found_gt.to_numpy() == 1
    found = df.found.to_numpy() == 1
    err, scale, rot = errors(df)
    out = {}

    def weighted_sum(mask):
        if cluster_counts is None:
            return weights @ mask.astype(float)
        sufficient = np.bincount(cluster_codes, weights=mask.astype(float),
                                 minlength=cluster_counts.shape[1])
        return cluster_counts @ sufficient

    def count(key, mask):
        out[key] = weighted_sum(mask)
        return out[key]

    def rate(key, mask, denominator, zero=np.nan):
        numerator = weighted_sum(mask)
        out[key] = np.divide(numerator, denominator, out=np.full(len(weights), zero), where=denominator != 0)

    def quant(key, values, mask, q):
        out[key] = weighted_quantiles(values[mask], weights[:, mask], q)

    n = count("n_present", present)
    count("n_absent", ~present)
    for r in (1, 3, 5):
        rate(f"success@{r}", present & found & (err <= r), n)
        if full:
            rate(f"loc_only@{r}", present & (err <= r), n)
    rate("gross_rate", present & (err > 20), n)
    for label, q in (("p50", .5), ("p90", .9), ("p95", .95)):
        if full or label == "p50":
            quant(f"err_px_{label}", err, present, q)
    count("absent_accepted", ~present & found)
    count("present_declined", present & ~found)
    if not full:
        return out
    for subset, mask in (("all", present), ("within5", present & found & (err <= 5))):
        denom = count(f"pose_{subset}_n", mask)
        for name, values, tolerances in (("scale_pct", scale, (1, 2, 5)), ("rotation_deg", rot, (.25, .5, 1))):
            for label, q in (("median", .5), ("p90", .9)):
                quant(f"{name}_{subset}_{label}", values, mask, q)
            for tolerance in tolerances:
                rate(f"{name}_{subset}_within{tolerance:g}", mask & (values <= tolerance), denom)
    tp = count("absent_declined", ~present & ~found)
    fp, fn = out["present_declined"], out["absent_accepted"]
    for key, numerator, denominator in (("precision", tp, tp+fp), ("recall", tp, tp+fn), ("F1", 2*tp, 2*tp+fp+fn)):
        out[key] = np.divide(numerator, denominator, out=np.zeros(len(weights)), where=denominator != 0)
    score = df.score.to_numpy()
    for key, labels in (("auroc_present", present), ("correct_match_auc", present & (err <= 5))):
        pos, neg = weighted_sum(labels), weighted_sum(~labels)
        out[key] = np.full(len(weights), np.nan)
        for i in np.flatnonzero((pos > 0) & (neg > 0)):
            out[key][i] = roc_auc_score(labels, score, sample_weight=weights[i])
    for label, q in (("median", .5), ("p90", .9), ("p95", .95), ("max", 1)):
        quant(f"runtime_{label}", df.seconds.to_numpy(), np.ones(len(df), bool), q)
    return out


def interval(array):
    valid = array[1:][~np.isnan(array[1:])]
    # Linear percentile interpolation, with explicit handling of infinity.
    bounds = [weighted_quantiles(valid, np.ones((1, len(valid)), dtype=int), q)[0]
              for q in (.025, .975)] if len(valid) else [np.nan, np.nan]
    return {"value": float(array[0]), "lo": float(bounds[0]), "hi": float(bounds[1]), "valid_bootstrap": len(valid)}


def build_report(man, methods, bootstrap=2000, seed=20261010, ref=None):
    if bootstrap < 0:
        raise ValueError("bootstrap must be nonnegative")
    if ref is not None and ref not in methods:
        raise ValueError(f"unknown reference method: {ref}")
    groups, codes = np.unique(man.group_id, return_inverse=True)
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(groups), size=(bootstrap, len(groups)))
    counts = np.zeros((bootstrap+1, len(groups)), dtype=np.int32)
    counts[0] = 1
    for i, draw in enumerate(draws, 1):
        counts[i] = np.bincount(draw, minlength=len(groups))
    weights = counts[:, codes]
    report = {"bootstrap": bootstrap, "seed": seed, "clusters": len(groups), "notes": NOTES, "methods": {}, "differences": {}}
    raw = {}
    for method, df in methods.items():
        raw[method] = metric_arrays(df, weights, cluster_counts=counts, cluster_codes=codes)
        strata = {}
        for stratum in sorted(df.stratum.unique()):
            mask = df.stratum.eq(stratum).to_numpy() & df.found_gt.eq(1).to_numpy()
            if mask.any():
                arrays = metric_arrays(df.loc[mask], weights[:, mask], full=False,
                                       cluster_counts=counts, cluster_codes=codes[mask])
                strata[stratum] = {k: interval(v) for k, v in arrays.items() if k not in ("n_absent", "absent_accepted", "present_declined")}
        absent = df.found_gt.eq(0).to_numpy()
        strata["absent"] = {k: interval(v) for k, v in metric_arrays(
            df.loc[absent], weights[:, absent], full=False,
            cluster_counts=counts, cluster_codes=codes[absent]).items()
            if k in ("n_absent", "absent_accepted")}
        strata["absent"]["absent_declined"] = interval(raw[method]["absent_declined"])
        report["methods"][method] = {"metrics": {k: interval(v) for k, v in raw[method].items()}, "strata": strata}
    if ref is not None:
        for method in methods:
            if method != ref:
                with np.errstate(invalid="ignore"):
                    report["differences"][method] = {k: interval(raw[method][k]-raw[ref][k]) for k in ("success@1", "success@3", "success@5", "F1", "err_px_p50")}
        report["reference"] = ref
    return report


def choose_dev_threshold(df):
    scores = df.score.to_numpy()
    candidates = np.append(np.unique(scores), np.nextafter(scores.max(), np.inf))
    absent = df.found_gt.to_numpy() == 0
    best, best_num, best_den = float(candidates[0]), -1, 1
    for threshold in candidates:
        declined = scores < threshold
        tp = int((absent & declined).sum())
        den = int(absent.sum() + declined.sum())
        num, den = 2*tp, max(den, 1)
        if num*best_den > best_num*den:
            best, best_num, best_den = float(threshold), num, den
    return best


def rethreshold(methods, rules, man):
    chosen = {}
    for rule in rules:
        method, setting = rule.split("=", 1)
        if method not in methods or method in chosen:
            raise ValueError(f"unknown or repeated rethreshold method: {method}")
        provenance = "explicit fixed threshold; selection provenance unknown"
        if setting.startswith("dev:"):
            dev_manifest, dev_pred = setting[4:].split(",", 1)
            dev_man, dev_methods = load_inputs(dev_manifest, [dev_pred])
            if not dev_man.split.eq("dev").all():
                raise ValueError("threshold selection requires split=dev")
            if set(dev_man.pair_id) & set(man.pair_id):
                raise ValueError("dev/test pair overlap: threshold selection would leak labels")
            if method not in dev_methods:
                raise ValueError(f"dev predictions missing method: {method}")
            threshold = choose_dev_threshold(dev_methods[method])
            provenance = "chosen on disjoint dev labels"
        else:
            threshold = float(setting)
        if not np.isfinite(threshold):
            raise ValueError("threshold must be finite")
        methods[method]["found"] = (methods[method].score >= threshold).astype(int)
        chosen[method] = {"threshold": threshold, "provenance": provenance}
        print(f"Threshold {method}: {threshold:.17g} ({provenance})")
    return chosen


def sweep(df):
    present = df.found_gt.to_numpy() == 1
    err = errors(df)[0]
    score = df.score.to_numpy()
    rows = []
    for threshold in np.unique(score):
        found = score >= threshold
        tp = int((~present & ~found).sum())
        fp, fn = int((present & ~found).sum()), int((~present & found).sum())
        row = {"threshold": threshold, "F1": 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0., "absent_accepted": fn, "present_declined": fp}
        row.update({f"success@{r}": float((present & found & (err <= r)).sum()/present.sum()) if present.any() else np.nan for r in (1, 3, 5)})
        rows.append(row)
    return pd.DataFrame(rows)


def fmt(metric):
    return f"{metric['value']:.3g} [{metric['lo']:.3g}, {metric['hi']:.3g}]"


def table(rows, columns):
    escape = lambda s: str(s).replace("|", "\\|").replace("\n", " ").replace("\r", " ")
    lines = ["| " + " | ".join(map(escape, columns)) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    lines += ["| " + " | ".join(map(escape, row)) + " |" for row in rows]
    return "\n".join(lines)


def markdown(report):
    methods = report["methods"]
    keys = list(next(iter(methods.values()))["metrics"])
    groups = {"Counts": ["n_present", "n_absent"], "Localisation": [k for k in keys if k.startswith(("err_px", "success", "loc_only", "gross"))], "Scale and rotation": [k for k in keys if k.startswith(("pose_", "scale_", "rotation_"))], "Rejection and AUC": [k for k in keys if k in ("precision", "recall", "F1", "auroc_present", "correct_match_auc", "absent_accepted", "present_declined", "absent_declined")], "Runtime": [k for k in keys if k.startswith("runtime_")]}
    lines = ["# IRIS report", "", report["notes"], "", f"Bootstrap: {report['bootstrap']}; seed: {report['seed']}; clusters: {report['clusters']}.", ""]
    for method, info in report.get("thresholds", {}).items():
        lines += [f"Threshold {method}: {info['threshold']:.17g}; {info['provenance']}.", ""]
    for title, metrics in groups.items():
        lines += [f"## {title}", "", table([[k] + [fmt(v["metrics"][k]) for v in methods.values()] for k in metrics], ["Metric"]+list(methods)), ""]
    for method, item in methods.items():
        lines += [f"## Strata: {method}", ""]
        for stratum, metrics in item["strata"].items():
            lines += [f"### {stratum}", "", table([[k, fmt(v)] for k, v in metrics.items()], ["Metric", "Value [95% CI]"]), ""]
    if report["differences"]:
        lines += [f"## Paired differences against {report['reference']}", ""]
        for method, metrics in report["differences"].items():
            lines += [f"### {method} minus {report['reference']}", "", table([[k, fmt(v)] for k, v in metrics.items()], ["Metric", "Difference [95% CI]"]), ""]
    return "\n".join(lines)


def json_safe(value):
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, float) and not np.isfinite(value):
        return None if np.isnan(value) else ("Infinity" if value > 0 else "-Infinity")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--pred", action="append", required=True)
    parser.add_argument("--ref")
    parser.add_argument("--out-prefix", default="results/iris/report_test")
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261010)
    parser.add_argument("--rethreshold", action="append", default=[], metavar="METHOD=VALUE|dev:DEV_MANIFEST,DEV_PRED")
    parser.add_argument("--sweep", action="store_true")
    args = parser.parse_args(argv)
    try:
        man, methods = load_inputs(args.manifest, args.pred)
        chosen = rethreshold(methods, args.rethreshold, man)
        report = build_report(man, methods, args.bootstrap, args.seed, args.ref)
        report["thresholds"] = chosen
        prefix = Path(args.out_prefix)
        prefix.parent.mkdir(parents=True, exist_ok=True)
        if args.sweep:
            names = [re.sub(r"[^A-Za-z0-9_.-]", "_", method) for method in methods]
            if len(set(names)) != len(names):
                raise ValueError("method names collide after sweep filename sanitization")
            for (method, df), name in zip(methods.items(), names):
                verified = chosen.get(method, {}).get("provenance") == "chosen on disjoint dev labels"
                comment = "Oracle-free-of-selection analysis: operating threshold selected on disjoint dev labels; sweep values must not select a test threshold." if verified else "Selection provenance unverified: descriptive labelled sweep, not certified oracle-free-of-selection; do not select thresholds on these labels."
                with open(f"{prefix}_sweep_{name}.csv", "w", encoding="utf-8", newline="") as handle:
                    handle.write(f"# {comment}\n")
                    handle.write(f"# method={method!r}\n")
                    sweep(df).to_csv(handle, index=False)
        Path(f"{prefix}.md").write_text(markdown(report), encoding="utf-8")
        Path(f"{prefix}.json").write_text(json.dumps(json_safe(report), indent=2, allow_nan=False)+"\n", encoding="utf-8")
        columns = ["Method", "success@1", "success@3", "success@5", "F1", "err_px_p50"]
        print(table([[m]+[fmt(v["metrics"][k]) for k in columns[1:]] for m, v in report["methods"].items()], columns))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"iris_report: {exc}\n")


if __name__ == "__main__":
    main()
