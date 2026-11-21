"""LoFTR baseline for the IRIS task (learned dense matcher, kornia). UNTESTED.

Nothing in this file has been executed. The kornia call signature and the
checkpoint name are written from memory of kornia 0.8.x and must be checked with
a 3-pair smoke run before any full run (RUN_BRIEF.md, step E3).

Method (adapted to the task, not the paper's original protocol):
  for each candidate zoom z in ZOOMS and rotation theta in ROTATIONS:
      template = reference shrunk by z and rotated by theta (iris_baselines.pose_template,
                 the same canonicalisation the ZNCC baseline uses)
      matches  = LoFTR(template, search)
      similarity A (scale, rotation, translation) = RANSAC on the matches
      inliers  = RANSAC inlier count
  winner = candidate with the most inliers.
  pose: centre of the template mapped by A; scale = z / s_A; theta = theta + angle(A).
  score = 1 - exp(-inliers / 20), a monotone map of the inlier count into [0, 1)
          (ordering is exactly the inlier count). found = inliers >= MIN_INLIERS.
  The dev threshold is applied afterwards by scripts/iris_report.py --rethreshold.

Output: the iris_spec.md prediction CSV (pair_id, method, found, score, x, y, theta,
scale, seconds, status). Resumable, sorted by pair_id.

Run from the working copy root (where scripts/iris_baselines.py lives):
  IRIS_WORKDIR=. python -X utf8 /path/to/ariadne/code/baselines/loftr_baseline.py \
      --manifest data/iris/manifest_dev.csv --out results/iris/pred_dev_loftr.csv --device cuda
"""
from __future__ import annotations

import argparse
import csv
import math
import os
from pathlib import Path
import sys
import time

import cv2
import numpy as np

WORKDIR = Path(os.environ.get("IRIS_WORKDIR", ".")).resolve()
sys.path.insert(0, str(WORKDIR / "scripts"))
import iris_baselines as ib  # noqa: E402  (pose_template, read_gray, to_label_convention, FIELDS)

METHOD = "loftr"
ZOOMS = (8.0, 10.0, 12.0)
ROTATIONS = (-5.0, 0.0, 5.0)
RANSAC_PX = 3.0          # reprojection threshold in search pixels (fixed a priori)
MIN_INLIERS = 8          # found = 1 at or above this count (report applies the dev threshold)
TAU = 20.0               # score = 1 - exp(-inliers / TAU)
CHECKPOINT = "outdoor"   # kornia.feature.LoFTR pretrained checkpoint (UNVERIFIED name)


def load_matcher(device: str):
    import kornia  # pinned: kornia==0.8.3
    return kornia.feature.LoFTR(pretrained=CHECKPOINT).to(device).eval()


def _pad32(img: np.ndarray) -> np.ndarray:
    h, w = img.shape
    out = np.zeros((-(-h // 32) * 32, -(-w // 32) * 32), np.float32)
    out[:h, :w] = img / 255.0
    return out  # zero padding on the bottom/right does not move coordinates


def loftr_matches(model, template: np.ndarray, search: np.ndarray, device: str):
    import torch
    with torch.no_grad():
        t = torch.from_numpy(_pad32(template))[None, None].to(device)
        s = torch.from_numpy(_pad32(search))[None, None].to(device)
        out = model({"image0": t, "image1": s})
    k0 = out["keypoints0"].float().cpu().numpy().reshape(-1, 2)
    k1 = out["keypoints1"].float().cpu().numpy().reshape(-1, 2)
    return k0, k1


def candidate(model, reference, search, z, theta, device):
    template, _ = ib.pose_template(reference, z, theta)
    h, w = template.shape
    if h > search.shape[0] or w > search.shape[1] or min(h, w) < 8:
        return None
    k0, k1 = loftr_matches(model, template, search, device)
    if len(k0) < 4:
        return None
    A, inliers = cv2.estimateAffinePartial2D(k0, k1, method=cv2.RANSAC,
                                             ransacReprojThreshold=RANSAC_PX,
                                             maxIters=5000, confidence=0.999)
    if A is None:
        return None
    s_a = math.hypot(A[0, 0], A[1, 0])
    if not s_a > 0:
        return None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    x, y = A[0, 0] * cx + A[0, 1] * cy + A[0, 2], A[1, 0] * cx + A[1, 1] * cy + A[1, 2]
    # cv2 angle of the residual rotation (same sign convention as getRotationMatrix2D).
    residual = math.degrees(math.atan2(A[0, 1], A[0, 0]))
    return {"inliers": int(inliers.sum()), "x": float(x), "y": float(y),
            "scale": float(z / s_a), "theta": float(theta + residual)}


def locate(model, reference, search, convention, device) -> dict:
    best = None
    for z in ZOOMS:
        for theta in ROTATIONS:
            c = candidate(model, reference, search, z, theta, device)
            if c is not None and (best is None or c["inliers"] > best["inliers"]):
                best = c
    if best is None:
        return dict(found=0, score=0.0, x=float("nan"), y=float("nan"),
                    theta=float("nan"), scale=float("nan"))
    x, y = ib.to_label_convention(best["x"], best["y"], convention)
    return dict(found=int(best["inliers"] >= MIN_INLIERS),
                score=float(1.0 - math.exp(-best["inliers"] / TAU)),
                x=x, y=y, theta=best["theta"], scale=best["scale"])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--device", default="cuda")
    p.add_argument("--threads", type=int, default=4)
    p.add_argument("--limit", type=int)
    args = p.parse_args(argv)
    import torch
    torch.set_num_threads(args.threads)
    device = args.device if (args.device != "cuda" or torch.cuda.is_available()) else "cpu"
    with open(args.manifest, newline="", encoding="utf-8") as h:
        rows = sorted(csv.DictReader(h), key=lambda r: r["pair_id"])
    if args.limit is not None:
        rows = rows[:args.limit]
    done = set()
    existing = []
    if Path(args.out).exists() and Path(args.out).stat().st_size:
        with open(args.out, newline="", encoding="utf-8") as h:
            existing = list(csv.DictReader(h))
        done = {r["pair_id"] for r in existing}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    model = load_matcher(device)
    with open(args.out, "a", newline="", encoding="utf-8") as h:
        writer = csv.DictWriter(h, fieldnames=ib.FIELDS)
        if h.tell() == 0:
            writer.writeheader()
        for r in rows:
            if r["pair_id"] in done:
                continue
            started = time.perf_counter()
            pred = dict(pair_id=r["pair_id"], method=METHOD, found=0, score=0.0,
                        x=float("nan"), y=float("nan"), theta=float("nan"),
                        scale=float("nan"), seconds=0.0, status="ok")
            try:
                ref = ib.read_gray(r["reference_path"])
                srch = ib.read_gray(r["search_path"])
                pred.update(locate(model, ref, srch, r["label_convention"], device))
            except Exception as error:  # a failing pair is still written
                pred["status"] = f"{type(error).__name__}: {error}"
            pred["seconds"] = time.perf_counter() - started
            writer.writerow(pred)
            h.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
