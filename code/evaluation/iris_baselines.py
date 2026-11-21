"""CPU IRIS baselines. Use --out - for CSV on stdout without creating files.

Only SIFT-LightGlue uses pretrained weights, from the existing offline cache.
No presence threshold is calibrated here: found means a pose was produced.
"""
from __future__ import annotations

import argparse
import csv
import math
import json
import multiprocessing as mp
import os
from pathlib import Path
import sys
import time

# Set numerical-library limits before importing them. The CLI/worker replaces
# these with --threads before computation; Torch is imported lazily.
for _thread_var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_thread_var] = os.environ.get("IRIS_THREADS", "4")

import cv2
import numpy as np

SEED = 20261010
METHODS = ("zncc_ms", "sift_ransac", "sift_lightglue",
           "sift_ransac_tuned", "sift_lightglue_tuned")
PRESET_PATH = "results/iris/baseline_presets.json"
FIELDS = "pair_id method found score x y theta scale seconds status".split()
_MODEL = None


def to_label_convention(x, y, convention):
    if convention not in ("edge", "center"):
        raise ValueError(f"Unknown label convention: {convention}")
    shift = 0.5 if convention == "edge" else 0.0
    return float(x + shift), float(y + shift)


def read_gray(path):
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise OSError(f"Cannot read image: {path}")
    return image


def pose_template(reference, z, theta):
    """Area reduction, padded rotation, exact crop with invariant centre."""
    h, w = reference.shape
    base = cv2.resize(reference, (max(1, round(w / z)), max(1, round(h / z))),
                      interpolation=cv2.INTER_AREA)
    if theta == 0:
        return base, np.ones(base.shape, np.uint8)
    h, w = base.shape
    pad = math.ceil(math.hypot(h, w))
    padded = cv2.copyMakeBorder(base, pad, pad, pad, pad, cv2.BORDER_CONSTANT)
    mask = cv2.copyMakeBorder(np.ones(base.shape, np.float32), pad, pad, pad, pad,
                              cv2.BORDER_CONSTANT)
    matrix = cv2.getRotationMatrix2D(((w - 1) / 2 + pad, (h - 1) / 2 + pad),
                                     float(theta), 1.0)
    size = (w + 2 * pad, h + 2 * pad)
    rotated = cv2.warpAffine(padded, matrix, size, flags=cv2.INTER_LINEAR)
    valid = cv2.warpAffine(mask, matrix, size, flags=cv2.INTER_LINEAR)
    crop = np.s_[pad:pad + h, pad:pad + w]
    return rotated[crop].copy(), (valid[crop] >= 1 - 1e-6).astype(np.uint8)


def parabola(left, peak, right):
    denom = left - 2 * peak + right
    if not np.isfinite([left, peak, right]).all() or denom >= -1e-12:
        return 0.0
    return float(np.clip(0.5 * (left - right) / denom, -0.5, 0.5))


def no_pose():
    return dict(found=0, score=0.0, x=np.nan, y=np.nan, theta=np.nan, scale=np.nan)


def zncc_ms(reference, search, convention="center"):
    best = None

    def sweep(scales, angles):
        nonlocal best
        for z in scales:
            for theta in angles:
                template, mask = pose_template(reference, float(z), float(theta))
                h, w = template.shape
                if h > search.shape[0] or w > search.shape[1]:
                    continue
                values = template[mask.astype(bool)]
                if len(values) < 4 or np.std(values) < 1e-6:
                    continue
                kwargs = {} if mask.all() else {"mask": mask}
                corr = cv2.matchTemplate(search, template, cv2.TM_CCOEFF_NORMED, **kwargs)
                corr[~np.isfinite(corr)] = -np.inf
                index = int(np.argmax(corr))
                iy, ix = np.unravel_index(index, corr.shape)
                score = float(corr[iy, ix])
                if np.isfinite(score) and (best is None or score > best["score"]):
                    dx = parabola(*corr[iy, ix - 1:ix + 2]) if 0 < ix < corr.shape[1] - 1 else 0
                    dy = parabola(*corr[iy - 1:iy + 2, ix]) if 0 < iy < corr.shape[0] - 1 else 0
                    best = dict(score=score, x=ix + (w - 1) / 2 + dx,
                                y=iy + (h - 1) / 2 + dy, scale=float(z), theta=float(theta))

    sweep(np.linspace(8, 12, 17), np.linspace(-5, 5, 11))
    if best is None:
        return no_pose()
    z, theta = best["scale"], best["theta"]
    sweep([v for v in z + np.arange(-5, 6) * 0.05 if 8 <= v <= 12],
          [v for v in theta + np.arange(-4, 5) * 0.25 if -5 <= v <= 5])
    best["x"], best["y"] = to_label_convention(best["x"], best["y"], convention)
    best.update(found=1, score=float(np.clip(best["score"], 0, 1)))
    return best


def sift_features(image, max_keypoints=None, *, contrastThreshold=0.04,
                  edgeThreshold=10, upsample=1):
    if not isinstance(upsample, int) or upsample < 1:
        raise ValueError("upsample must be a positive integer")
    if not np.isfinite([contrastThreshold, edgeThreshold]).all() or contrastThreshold <= 0 or edgeThreshold <= 0:
        raise ValueError("SIFT contrastThreshold and edgeThreshold must be positive and finite")
    original_shape = image.shape
    if upsample != 1:
        image = cv2.resize(image, (image.shape[1] * upsample, image.shape[0] * upsample),
                           interpolation=cv2.INTER_CUBIC)
    detector = cv2.SIFT_create(nfeatures=max_keypoints or 0,
                               contrastThreshold=contrastThreshold, edgeThreshold=edgeThreshold)
    keypoints, descriptors = detector.detectAndCompute(image, None)
    if max_keypoints and len(keypoints) > max_keypoints:
        order = sorted(range(len(keypoints)), key=lambda i: keypoints[i].response,
                       reverse=True)[:max_keypoints]
        keypoints = [keypoints[i] for i in order]
        descriptors = descriptors[order]
    if descriptors is None:
        descriptors = np.empty((0, 128), np.float32)
    descriptors = descriptors.astype(np.float32)
    descriptors /= np.maximum(descriptors.sum(axis=1, keepdims=True), 1e-6)
    descriptors = np.sqrt(descriptors)
    descriptors /= np.maximum(np.linalg.norm(descriptors, axis=1, keepdims=True), 1e-6)
    return dict(keypoints=np.array([k.pt for k in keypoints], np.float32).reshape(-1, 2) / upsample,
                descriptors=descriptors, scales=np.array([k.size for k in keypoints], np.float32) / upsample,
                oris=np.deg2rad(np.array([k.angle for k in keypoints], np.float32)),
                image_size=np.array(original_shape[::-1], np.float32))


def ratio_matches(a, b, *, ratio=0.8):
    if not np.isfinite(ratio) or not 0 < ratio <= 1:
        raise ValueError("ratio must be in (0, 1]")
    minimum = 1 if ratio == 1 else 2
    if len(a["descriptors"]) < minimum or len(b["descriptors"]) < minimum:
        return np.empty((0, 2), np.int64)
    matcher = cv2.BFMatcher(cv2.NORM_L2)
    def nearest(first, second):
        if ratio == 1:
            return {p.queryIdx: p.trainIdx for p in matcher.match(first, second)}
        return {p[0].queryIdx: p[0].trainIdx for p in matcher.knnMatch(first, second, k=2)
                if len(p) == 2 and p[0].distance < ratio * p[1].distance}
    forward = nearest(a["descriptors"], b["descriptors"])
    reverse = nearest(b["descriptors"], a["descriptors"])
    return np.array([(i, j) for i, j in forward.items() if reverse.get(j) == i],
                    np.int64).reshape(-1, 2)


def lightglue_model():
    global _MODEL
    if _MODEL is None:
        os.environ["TORCH_HOME"] = (Path.cwd() / ".torch_home").as_posix()
        import torch
        try:
            from lightglue import LightGlue
        except (ImportError, ModuleNotFoundError):
            # System Python ABI fallback: the matcher itself is pure Python.
            import importlib.util
            path = Path(__file__).resolve().parents[1] / ".venv/Lib/site-packages/lightglue/lightglue.py"
            if not path.is_file():
                raise
            spec = importlib.util.spec_from_file_location("lightglue", path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["lightglue"] = module
            spec.loader.exec_module(module)
            LightGlue = module.LightGlue
        filename = f"sift_lightglue_{LightGlue.version.replace('.', '-')}.pth"
        if not (Path(os.environ["TORCH_HOME"]) / "hub/checkpoints" / filename).is_file():
            raise FileNotFoundError(f"Offline LightGlue weights missing: {filename}")
        _MODEL = LightGlue(features="sift", mp=False, flash=False).cpu().float().eval()
    return _MODEL


def lightglue_matches(a, b):
    if not len(a["keypoints"]) or not len(b["keypoints"]):
        return np.empty((0, 2), np.int64)
    import torch
    model = lightglue_model()
    # The installed forward() normalizes pixel keypoints using image_size.
    # SIFT config also consumes OpenCV keypoint sizes and radian orientations.
    def tensors(features):
        return {k: torch.from_numpy(v).float().cpu()[None] for k, v in features.items()}
    with torch.inference_mode():
        result = model({"image0": tensors(a), "image1": tensors(b)})
    return result["matches"][0].cpu().numpy().reshape(-1, 2)


def affine_pose(matrix, reference_shape, convention):
    h, w = reference_shape
    centre = matrix @ np.array([(w - 1) / 2, (h - 1) / 2, 1.0])
    alpha = math.hypot(matrix[0, 0], matrix[1, 0])
    theta = math.degrees(math.atan2(matrix[0, 1], matrix[0, 0]))
    x, y = to_label_convention(*centre, convention)
    return dict(x=x, y=y, scale=1 / alpha if alpha > 0 else np.inf, theta=theta)


def sift_match(reference, search, convention="center", use_lightglue=False, *,
               contrastThreshold=0.04, edgeThreshold=10, upsample=1,
               ratio=0.8, ransac_thr=2.0, min_inliers=4):
    if not np.isfinite(ransac_thr) or ransac_thr <= 0:
        raise ValueError("ransac_thr must be positive and finite")
    if not isinstance(min_inliers, int) or min_inliers < 3:
        raise ValueError("min_inliers must be an integer >= 3")
    if not np.isfinite(ratio) or not 0 < ratio <= 1:
        raise ValueError("ratio must be in (0, 1]")
    match = lightglue_matches if use_lightglue else lambda a, b: ratio_matches(a, b, ratio=ratio)
    feature_options = dict(contrastThreshold=contrastThreshold, edgeThreshold=edgeThreshold,
                           upsample=upsample)
    cap = 1024 if use_lightglue else None
    if use_lightglue:
        lightglue_model()
    search_features = sift_features(search, cap, **feature_options)
    best = None
    for z in (8, 10, 12):
        h, w = reference.shape
        small = cv2.resize(reference, (round(w / z), round(h / z)), interpolation=cv2.INTER_AREA)
        features = sift_features(small, cap, **feature_options)
        matches = match(features, search_features)
        if len(matches) < 3:
            continue
        # Resize maps pixel centres by (p+0.5)*ratio-0.5. Fit in ORIGINAL
        # reference coordinates, so alpha and the centre include the reduction.
        points = features["keypoints"][matches[:, 0]]
        points = (points + 0.5) * np.array([w / small.shape[1], h / small.shape[0]]) - 0.5
        targets = search_features["keypoints"][matches[:, 1]]
        cv2.setRNGSeed(SEED)
        matrix, inlier_mask = cv2.estimateAffinePartial2D(
            points.astype(np.float32), targets, method=cv2.RANSAC, ransacReprojThreshold=ransac_thr)
        if matrix is None or not np.isfinite(matrix).all():
            continue
        inliers = int(inlier_mask.sum())
        if best is None or inliers > best[0]:
            best = inliers, affine_pose(matrix, reference.shape, convention)
    if best is None:
        return no_pose()
    inliers, pose = best
    valid = inliers >= min_inliers and 8 <= pose["scale"] <= 12 and abs(pose["theta"]) <= 7
    pose.update(found=1, score=min(1.0, inliers / 30) if valid else 0.0)
    return pose


def configure_threads(threads):
    for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[name] = str(threads)
    cv2.setNumThreads(threads)
    cv2.setRNGSeed(SEED)
    # Torch is loaded only when needed; its pools are set in run_pair.


def load_preset(method, path=PRESET_PATH):
    try:
        with open(path, encoding="utf-8") as handle:
            presets = json.load(handle)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Tuned SIFT preset file missing: {path}; run iris_tune_baselines.py on DEV first") from exc
    if method not in presets:
        raise ValueError(f"Missing preset for {method} in {path}")
    options = presets[method]
    expected = {"contrastThreshold", "edgeThreshold", "upsample", "ratio", "ransac_thr", "min_inliers"}
    if not isinstance(options, dict) or set(options) != expected:
        raise ValueError(f"Invalid SIFT preset for {method} in {path}")
    return dict(options)


def run_pair(task):
    row, method, threads = task[:3]
    options = dict(task[3]) if len(task) > 3 else {}
    if method.endswith("_tuned") and not options:
        options = load_preset(method)
    start = time.perf_counter()
    result = dict(pair_id=row["pair_id"], method=method, status="ok")
    try:
        configure_threads(threads)
        if method in ("sift_lightglue", "sift_lightglue_tuned"):
            import torch
            torch.set_num_threads(threads)
            if torch.get_num_interop_threads() != 1:
                torch.set_num_interop_threads(1)
        reference, search = read_gray(row["reference_path"]), read_gray(row["search_path"])
        convention = row["label_convention"]
        if method == "zncc_ms":
            pose = zncc_ms(reference, search, convention)
        else:
            pose = sift_match(reference, search, convention,
                              method in ("sift_lightglue", "sift_lightglue_tuned"), **options)
        result.update(pose)
    except Exception as exc:
        result.update(no_pose(), status=f"{type(exc).__name__}: {exc}")
    result["seconds"] = time.perf_counter() - start
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--method", choices=METHODS, nargs="+", action="extend", required=True)
    parser.add_argument("--out", required=True, help="CSV path or - for stdout")
    parser.add_argument("--jobs", type=int, default=1, choices=(1, 2))
    parser.add_argument("--threads", type=int, default=4, choices=range(1, 5))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--contrastThreshold", "--contrast-threshold", type=float, default=0.04)
    parser.add_argument("--edgeThreshold", "--edge-threshold", type=float, default=10)
    parser.add_argument("--upsample", type=int, default=1)
    parser.add_argument("--ratio", type=float, default=0.8)
    parser.add_argument("--ransac-thr", type=float, default=2.0)
    parser.add_argument("--min-inliers", type=int, default=4)
    parser.add_argument("--presets", default=PRESET_PATH)
    args = parser.parse_args(argv)
    options = {k: getattr(args, k) for k in ("contrastThreshold", "edgeThreshold", "upsample",
                                           "ratio", "ransac_thr", "min_inliers")}
    try:
        method_options = {m: load_preset(m, args.presets) if m.endswith("_tuned") else options
                          for m in args.method}
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be nonnegative")
    configure_threads(args.threads)
    with open(args.manifest, newline="", encoding="utf-8") as handle:
        rows = sorted(csv.DictReader(handle), key=lambda r: r["pair_id"])
    if len({r["pair_id"] for r in rows}) != len(rows):
        parser.error("Manifest has duplicate pair ids")
    if args.limit is not None:
        rows = rows[:args.limit]
    existing = []
    if args.out != "-" and Path(args.out).exists():
        with open(args.out, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != FIELDS:
                parser.error("Existing output has a different prediction schema")
            existing = list(reader)
    done = {(r["pair_id"], r["method"]) for r in existing}
    if len(done) != len(existing):
        parser.error("Existing output has duplicate pair/method rows")
    if args.out != "-":
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    def write_output():
        # Atomically replace a flushed sorted snapshot after every pair,
        # so a killed write leaves the previous resumable CSV intact.
        temporary = args.out + ".tmp"
        with open(temporary, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(sorted(existing, key=lambda r: (r["pair_id"], r["method"])))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, args.out)

    writer = None
    if args.out == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
        writer.writeheader()
    tasks = [(r, method, args.threads, method_options[method]) for r in rows for method in sorted(set(args.method))
             if (r["pair_id"], method) not in done]
    pool = mp.get_context("spawn").Pool(args.jobs, configure_threads, (args.threads,)) if args.jobs > 1 else None
    try:
        results = pool.imap(run_pair, tasks) if pool else map(run_pair, tasks)
        for result in results:
            if writer:
                writer.writerow(result)
                sys.stdout.flush()
            else:
                existing.append(result)
                write_output()
    finally:
        if pool:
            pool.close()
            pool.join()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
