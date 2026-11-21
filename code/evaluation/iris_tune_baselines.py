"""DEV-only SIFT grid. Smoke with --limit; resume bounded full runs with --resume."""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import os
from pathlib import Path
import sys
import time

# Apply limits before numerical libraries are imported.
os.environ["IRIS_THREADS"] = "3"
for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[name] = "3"
os.environ["TORCH_HOME"] = (Path.cwd() / ".torch_home").as_posix()
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import iris_baselines as baseline
import numpy as np

MANIFEST = Path("data/iris/manifest_dev.csv")
REPORT = Path("results/iris/baseline_tuning_dev.md")
PRESETS = Path(baseline.PRESET_PATH)
MARKER = "<!-- iris-tuning-checkpoint\n"


def grid():
    configurations = []
    for method in ("sift_ransac", "sift_lightglue"):
        ratios = (.8, .9, 1.) if method == "sift_ransac" else (.8,)
        for contrast, upsample, ratio in itertools.product((.04, .02, .01), (1, 2), ratios):
            configurations.append(dict(method=method, options=dict(
                contrastThreshold=contrast, edgeThreshold=10, upsample=upsample,
                ratio=ratio, ransac_thr=3., min_inliers=4), records=[]))
    return configurations


def score(config, rows):
    records = config["records"]
    present = sum(int(r["found"]) for r in rows[:len(records)])
    errors = [r["error"] for r in records if r["error"] is not None]
    return dict(n=len(records), present=present,
                success5=sum(r["success5"] for r in records) / present if present else None,
                success3=sum(r["success3"] for r in records) / present if present else None,
                median_error=float(np.median(errors)) if errors else None,
                seconds=float(np.median([r["seconds"] for r in records])) if records else None,
                failures=sum(r["status"] != "ok" for r in records), valid=len(errors))


def ranked(configs, rows):
    return sorted(configs, key=lambda c: (-(score(c, rows)["success5"] or 0.),
                                          score(c, rows)["seconds"] if c["records"] else math.inf))


def table(configs, rows):
    lines = ["| method | contrastThreshold | edgeThreshold | upsample | ratio | ransac_thr | min_inliers | pairs | present | valid present poses | success@5 | success@3 | median valid error px | median seconds | errors |",
             "| " + " | ".join(["---"] * 15) + " |"]
    for config in ranked(configs, rows):
        s, o = score(config, rows), config["options"]
        error = "undefined" if s["median_error"] is None else f'{s["median_error"]:.6f}'
        fmt = lambda value: "undefined" if value is None else f"{value:.6f}"
        values = [config["method"], o["contrastThreshold"], o["edgeThreshold"], o["upsample"],
                  o["ratio"] if config["method"] == "sift_ransac" else "own matcher",
                  o["ransac_thr"], o["min_inliers"], s["n"], s["present"], s["valid"],
                  fmt(s["success5"]), fmt(s["success3"]), error,
                  fmt(s["seconds"]), s["failures"]]
        lines.append("| " + " | ".join(map(str, values)) + " |")
    return "\n".join(lines)


def save(state, rows):
    complete = all(len(c["records"]) == len(rows) for c in state["configs"])
    lines = ["# SIFT baseline tuning on DEV", "",
             f"Manifest: `{MANIFEST.as_posix()}`. {len(rows)} pairs, {sum(int(r['found']) for r in rows)} present. Seed {baseline.SEED}. Test manifests and test predictions were never opened.", "",
             "System Python 3.13, CPU, one process, three computation threads, Torch interop one thread. Offline SIFT-LightGlue weights from `.torch_home`; 1024 keypoint cap. Search scales remain 8, 10, 12. All configurations use edgeThreshold=10, RANSAC threshold 3 px, minimum four inliers.", "",
             "Upsampling uses bicubic interpolation on both images before SIFT. Coordinates and keypoint sizes are divided by the factor; LightGlue receives the original image size. Ratio=1 uses mutual nearest neighbours without a Lowe test. Other ratios use mutual Lowe-filtered matches.", "",
             "Success@3 and success@5 divide found, valid poses within the tolerance by ALL present pairs, including failures. Valid means finite pose, score>0, at least the configured inliers, scale in [8,12], and |rotation|<=7 degrees. The original methods report found=1 for some invalid fits; those are failures here. Euclidean centre error and present-pair denominator follow iris_report.py. Median error uses valid present poses only, as requested, rather than the report's all-present median including infinite failures. Runtime median includes present and absent pairs and image reading; model construction is warmed up and excluded for every configuration.", "",
             "Selection sorts by descending success@5 and then ascending median seconds. No rejection threshold was selected. DEV selection scores are optimistic estimates, not held-out performance. Runtime differences can include contention from the other machine job.", "",
             f"Status: {'complete' if complete else 'partial, resume required; no presets selected'}. Accumulated grid wall time: {state['elapsed']:.3f} seconds. Smoke runs are excluded.", "",
             table(state["configs"], rows), ""]
    if complete:
        chosen = {}
        for method in ("sift_ransac", "sift_lightglue"):
            best = ranked([c for c in state["configs"] if c["method"] == method], rows)[0]
            chosen[method + "_tuned"] = best["options"]
        PRESETS.write_text(json.dumps(chosen, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        lines += ["Chosen presets, also saved in `results/iris/baseline_presets.json`:", "", "```json", json.dumps(chosen, indent=2), "```", ""]
    statuses = sorted({r["status"] for c in state["configs"] for r in c["records"] if r["status"] != "ok"})
    if statuses:
        lines += ["Pair errors: " + "; ".join(statuses), ""]
    lines += [MARKER + json.dumps(state, separators=(",", ":"), allow_nan=False) + "\n-->", ""]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="Smoke only; prints results and never writes presets or report")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-seconds", type=float, default=540., help="Bound each invocation; use --resume until complete")
    args = parser.parse_args(argv)
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    if not 0 < args.max_seconds <= 86400:
        parser.error("--max-seconds must be in (0,86400]")
    # The manifest is deliberately fixed. The driver cannot accept a test path.
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        rows = sorted(csv.DictReader(handle), key=lambda r: r["pair_id"])
    if len(rows) != 150 or any(r["split"] != "dev" for r in rows) or len({r["pair_id"] for r in rows}) != 150:
        raise ValueError("Expected 150 unique DEV pairs")
    identity = json.dumps(rows, sort_keys=True)
    if args.limit:
        rows = rows[:args.limit]
    state = dict(configs=grid(), elapsed=0., manifest=identity)
    if args.resume and args.limit is None and REPORT.exists():
        checkpoint = REPORT.read_text(encoding="utf-8").split(MARKER, 1)[1].split("\n-->", 1)[0]
        state = json.loads(checkpoint)
        if state["manifest"] != identity or [(c["method"], c["options"]) for c in state["configs"]] != [(c["method"], c["options"]) for c in grid()]:
            raise ValueError("DEV manifest or grid changed; refusing resume")
    baseline.configure_threads(3)
    import torch
    torch.set_num_threads(3)
    torch.set_num_interop_threads(1)
    # Fail early if offline dependencies/weights are unavailable.
    baseline.lightglue_model()
    start = time.perf_counter()
    previous_elapsed = state["elapsed"]
    for config in state["configs"]:
        for row in rows[len(config["records"]):]:
            result = baseline.run_pair((row, config["method"], 3, config["options"]))
            present = int(row["found"]) == 1
            valid = (result["status"] == "ok" and result["found"] == 1 and result["score"] > 0
                     and np.isfinite([result[k] for k in ("x", "y", "scale", "theta")]).all()
                     and 8 <= result["scale"] <= 12 and abs(result["theta"]) <= 7)
            error = math.hypot(result["x"] - float(row["gt_x"]), result["y"] - float(row["gt_y"])) if present and valid else None
            config["records"].append(dict(error=error, success5=error is not None and error <= 5,
                                          success3=error is not None and error <= 3,
                                          seconds=result["seconds"], status=result["status"]))
            elapsed = time.perf_counter() - start
            if args.limit is None and elapsed >= args.max_seconds:
                state["elapsed"] = previous_elapsed + elapsed
                save(state, rows)
                print(f"Paused after {elapsed:.1f}s; rerun with --resume.", flush=True)
                return
        state["elapsed"] = previous_elapsed + time.perf_counter() - start
        if args.limit is None:
            save(state, rows)
        s = score(config, rows)
        print(f"{config['method']} {config['options']}: {s}", flush=True)
    print(table(state["configs"], rows), flush=True)
    print(f"Grid wall time: {state['elapsed']:.3f}s", flush=True)


if __name__ == "__main__":
    main()
