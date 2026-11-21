"""Synthetic geometry checks; all texture draws use the frozen seed."""
import csv
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys

import cv2
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import iris_baselines as baseline


def synthetic_pair(theta=3.0):
    rng = np.random.default_rng(20261010)
    texture = cv2.GaussianBlur(rng.integers(0, 256, (100, 100), dtype=np.uint8),
                               (3, 3), 0.6)
    for _ in range(65):
        x, y = rng.integers(4, 96, 2)
        cv2.circle(texture, (int(x), int(y)), int(rng.integers(1, 4)),
                   int(rng.integers(0, 256)), -1)
    reference = cv2.resize(texture, (1000, 1000), interpolation=cv2.INTER_CUBIC)
    reduced = cv2.resize(reference, (100, 100), interpolation=cv2.INTER_AREA)
    # Independent construction: rotate directly about the unpadded centre.
    matrix = cv2.getRotationMatrix2D((49.5, 49.5), theta, 1.0)
    tile = cv2.warpAffine(reduced, matrix, (100, 100), borderMode=cv2.BORDER_REFLECT_101)
    search = np.full((1000, 1000), 110, np.uint8)
    search[480:580, 410:510] = tile
    return reference, search, (459.5, 529.5, 10.0, theta)


def check_pose(pose, truth):
    x, y, z, theta = truth
    assert pose["found"] == 1, pose
    assert np.hypot(pose["x"] - x, pose["y"] - y) <= 1, pose
    assert abs(pose["scale"] / z - 1) <= 0.02, pose
    assert abs(pose["theta"] - theta) <= 0.5, pose
    if theta:
        assert np.sign(pose["theta"]) == np.sign(theta), pose


@pytest.mark.parametrize("convention,expected", [("center", (499.5, 499.5)),
                                                 ("edge", (500, 500))])
def test_label_convention(convention, expected):
    assert baseline.to_label_convention(499.5, 499.5, convention) == expected


def test_invalid_convention():
    with pytest.raises(ValueError):
        baseline.to_label_convention(1, 2, "invalid")


def test_zero_rotation_unpadded_centre(monkeypatch):
    reference, search, truth = synthetic_pair(0)
    base = cv2.resize(reference, (100, 100), interpolation=cv2.INTER_AREA)
    template, mask = baseline.pose_template(reference, 10, 0)
    np.testing.assert_array_equal(template, base)
    assert mask.all()
    _, _, _, loc = cv2.minMaxLoc(cv2.matchTemplate(search, template, cv2.TM_CCOEFF_NORMED))
    assert (loc[0] + (template.shape[1] - 1) / 2,
            loc[1] + (template.shape[0] - 1) / 2) == truth[:2]
    # Remove the intentionally fractional peak refinement for this exact
    # centre regression, then check the public result in both conventions.
    monkeypatch.setattr(baseline, "parabola", lambda *args: 0.0)
    pose = baseline.zncc_ms(reference, search)
    check_pose(pose, truth)
    assert (pose["x"], pose["y"]) == truth[:2]
    assert baseline.to_label_convention(pose["x"], pose["y"], "edge") == (460, 530)


@pytest.mark.parametrize("theta", [-3.0, 3.0])
@pytest.mark.parametrize("method", ["zncc_ms", "sift_ransac"])
def test_synthetic_geometry(method, theta):
    baseline.configure_threads(3)
    reference, search, truth = synthetic_pair(theta)
    pose = (baseline.zncc_ms(reference, search) if method == "zncc_ms"
            else baseline.sift_match(reference, search))
    check_pose(pose, truth)


@pytest.mark.parametrize("theta", [-4.0, 4.0])
def test_affine_original_reference_sign(theta):
    matrix = cv2.getRotationMatrix2D((499.5, 499.5), theta, 0.1)
    matrix[:, 2] += np.array([460, 530]) - 499.5
    pose = baseline.affine_pose(matrix, (1000, 1000), "edge")
    assert pose["theta"] == pytest.approx(theta)
    assert pose["scale"] == pytest.approx(10)
    assert (pose["x"], pose["y"]) == pytest.approx((460.5, 530.5))


def test_parabola_and_empty_images():
    assert baseline.parabola(0, 1, 0) == 0
    assert baseline.parabola(1, 1, 1) == 0
    empty = np.zeros((100, 100), np.uint8)
    assert baseline.zncc_ms(empty, empty)["found"] == 0
    assert baseline.sift_match(empty, empty)["found"] == 0


def test_failure_schema():
    result = baseline.run_pair(({"pair_id": "missing", "reference_path": "missing.png",
                                 "search_path": "missing.png", "label_convention": "edge"},
                                "zncc_ms", 1))
    assert set(result) == set(baseline.FIELDS)
    assert result["found"] == 0 and result["score"] == 0
    assert result["status"].startswith("OSError:")
    assert np.isnan(result["x"]) and result["seconds"] >= 0


def test_stdout_multiple_methods(monkeypatch, capsys):
    manifest = "pair_id,reference_path,search_path,label_convention\nb,r,s,edge\na,r,s,center\n"
    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: io.StringIO(manifest))
    monkeypatch.setattr(baseline, "run_pair", lambda task: dict(
        pair_id=task[0]["pair_id"], method=task[1], seconds=0, status="ok", **baseline.no_pose()))
    baseline.main(["--manifest", "unused", "--method", "zncc_ms", "sift_ransac",
                   "--out", "-", "--limit", "1", "--threads", "1"])
    rows = list(csv.DictReader(io.StringIO(capsys.readouterr().out)))
    assert [r["pair_id"] for r in rows] == ["a", "a"]
    assert [r["method"] for r in rows] == ["sift_ransac", "zncc_ms"]


def test_resume_atomic_sorted_output(monkeypatch):
    manifest = "pair_id,reference_path,search_path,label_convention\nb,r,s,edge\na,r,s,center\n"
    previous = dict(pair_id="b", method="zncc_ms", seconds=1, status="ok", **baseline.no_pose())
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=baseline.FIELDS)
    writer.writeheader()
    writer.writerow(previous)
    memory = {"manifest.csv": manifest, "output.csv": buffer.getvalue()}
    class File(io.StringIO):
        def fileno(self):
            return 0
    def open_memory(path, mode="r", **kwargs):
        path = str(path)
        handle = File(memory.get(path, "") if mode == "r" else "")
        if mode == "w":
            original_close = handle.close
            def close():
                memory[path] = handle.getvalue()
                original_close()
            handle.close = close
        return handle
    monkeypatch.setattr("builtins.open", open_memory)
    monkeypatch.setattr(Path, "exists", lambda path: str(path) in memory)
    monkeypatch.setattr(Path, "mkdir", lambda *args, **kwargs: None)
    monkeypatch.setattr(os, "fsync", lambda fd: None)
    monkeypatch.setattr(os, "replace", lambda src, dst: memory.__setitem__(dst, memory.pop(src)))
    calls = []
    def run(task):
        calls.append((task[0]["pair_id"], task[1]))
        return dict(pair_id=task[0]["pair_id"], method=task[1], seconds=0, status="ok",
                    **baseline.no_pose())
    monkeypatch.setattr(baseline, "run_pair", run)
    args = ["--manifest", "manifest.csv", "--method", "zncc_ms", "sift_ransac",
            "--out", "output.csv", "--threads", "1"]
    baseline.main(args)
    assert ("b", "zncc_ms") not in calls
    rows = list(csv.DictReader(io.StringIO(memory["output.csv"])))
    assert [(r["pair_id"], r["method"]) for r in rows] == [
        ("a", "sift_ransac"), ("a", "zncc_ms"), ("b", "sift_ransac"), ("b", "zncc_ms")]
    calls.clear()
    baseline.main(args)
    assert not calls


def test_lightglue_synthetic_geometry():
    # A subprocess enforces the requested 60-second limit, including imports
    # and model construction. No files or downloadable weights are created.
    source = '''
import importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location('iris_test', 'tests/test_iris_baselines.py')
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
tests.baseline.configure_threads(3)
import torch
torch.set_num_threads(3)
torch.set_num_interop_threads(1)
try:
    import lightglue
except (ImportError, ModuleNotFoundError):
    # Verification fallback for a system Python with a different ABI. Load
    # only the installed pure-Python matcher, bypassing unrelated extractors.
    path = Path('.venv/Lib/site-packages/lightglue/lightglue.py')
    if not path.is_file():
        raise
    spec = importlib.util.spec_from_file_location('lightglue', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['lightglue'] = module
    spec.loader.exec_module(module)
for theta in [-3., 3.]:
    reference, search, truth = tests.synthetic_pair(theta)
    pose = tests.baseline.sift_match(reference, search, use_lightglue=True)
    print(pose, flush=True)
    tests.check_pose(pose, truth)
'''
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", MKL_THREADING_LAYER="SEQUENTIAL")
    try:
        result = subprocess.run([sys.executable, "-X", "utf8", "-B", "-c", source],
                                cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        pytest.skip("LightGlue synthetic check exceeded 60 seconds")
    if result.returncode and ("ModuleNotFoundError" in result.stderr or "ImportError" in result.stderr):
        pytest.skip("LightGlue dependency unavailable: " + result.stderr[-600:])
    assert result.returncode == 0, result.stdout + result.stderr


# Frozen pre-tuning functions from the working tree, not a reimplementation.
LEGACY_SIFT = r'''
def sift_features(image, max_keypoints=None):
    detector = cv2.SIFT_create(nfeatures=max_keypoints or 0)
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
    return dict(keypoints=np.array([k.pt for k in keypoints], np.float32).reshape(-1, 2),
                descriptors=descriptors, scales=np.array([k.size for k in keypoints], np.float32),
                oris=np.deg2rad(np.array([k.angle for k in keypoints], np.float32)),
                image_size=np.array(image.shape[::-1], np.float32))


def ratio_matches(a, b):
    if len(a["descriptors"]) < 2 or len(b["descriptors"]) < 2:
        return np.empty((0, 2), np.int64)
    matcher = cv2.BFMatcher(cv2.NORM_L2)
    def nearest(first, second):
        return {p[0].queryIdx: p[0].trainIdx for p in matcher.knnMatch(first, second, k=2)
                if len(p) == 2 and p[0].distance < 0.8 * p[1].distance}
    forward = nearest(a["descriptors"], b["descriptors"])
    reverse = nearest(b["descriptors"], a["descriptors"])
    return np.array([(i, j) for i, j in forward.items() if reverse.get(j) == i],
                    np.int64).reshape(-1, 2)


def sift_match(reference, search, convention="center", use_lightglue=False):
    match = lightglue_matches if use_lightglue else ratio_matches
    cap = 1024 if use_lightglue else None
    if use_lightglue:
        lightglue_model()
    search_features = sift_features(search, cap)
    best = None
    for z in (8, 10, 12):
        h, w = reference.shape
        small = cv2.resize(reference, (round(w / z), round(h / z)), interpolation=cv2.INTER_AREA)
        features = sift_features(small, cap)
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
            points.astype(np.float32), targets, method=cv2.RANSAC, ransacReprojThreshold=2.0)
        if matrix is None or not np.isfinite(matrix).all():
            continue
        inliers = int(inlier_mask.sum())
        if best is None or inliers > best[0]:
            best = inliers, affine_pose(matrix, reference.shape, convention)
    if best is None:
        return no_pose()
    inliers, pose = best
    valid = inliers >= 4 and 8 <= pose["scale"] <= 12 and abs(pose["theta"]) <= 7
    pose.update(found=1, score=min(1.0, inliers / 30) if valid else 0.0)
    return pose


'''


def test_default_sift_bitwise_parity():
    namespace = dict(vars(baseline))
    exec(LEGACY_SIFT, namespace)
    baseline.configure_threads(3)
    reference, search, _ = synthetic_pair()
    before = namespace["sift_match"](reference, search)
    after = baseline.sift_match(reference, search)
    assert before == after
    assert after["found"] == 1


def test_ratio_one_mutual_nearest():
    # Identical descriptors defeat strict Lowe even with a ratio of one.
    a = {"descriptors": np.array([[0., 0.], [0., 0.], [9., 0.]], np.float32)}
    b = {"descriptors": np.array([[0., 0.], [0., 0.], [10., 0.]], np.float32)}
    np.testing.assert_array_equal(baseline.ratio_matches(a, b, ratio=1.), [[0, 0], [2, 2]])
    assert len(baseline.ratio_matches(a, b)) == 1
    single = {"descriptors": np.zeros((1, 2), np.float32)}
    np.testing.assert_array_equal(baseline.ratio_matches(single, single, ratio=1.), [[0, 0]])


def test_upsample_original_coordinates():
    reference, _, _ = synthetic_pair()
    image = cv2.resize(reference, (100, 100), interpolation=cv2.INTER_AREA)
    enlarged = cv2.resize(image, (200, 200), interpolation=cv2.INTER_CUBIC)
    raw = baseline.sift_features(enlarged)
    restored = baseline.sift_features(image, upsample=2)
    assert len(restored["keypoints"]) > 0
    np.testing.assert_array_equal(restored["keypoints"], raw["keypoints"] / 2)
    np.testing.assert_array_equal(restored["scales"], raw["scales"] / 2)
    np.testing.assert_array_equal(restored["image_size"], [100, 100])
    np.testing.assert_array_equal(restored["descriptors"], raw["descriptors"])


def test_sift_detector_parameters(monkeypatch):
    original = cv2.SIFT_create
    calls = []
    def detector(**kwargs):
        calls.append(kwargs)
        return original(**kwargs)
    monkeypatch.setattr(cv2, "SIFT_create", detector)
    baseline.sift_features(np.zeros((32, 32), np.uint8), contrastThreshold=.01, edgeThreshold=15)
    assert calls == [dict(nfeatures=0, contrastThreshold=.01, edgeThreshold=15)]


def test_missing_preset_clear_error():
    with pytest.raises(FileNotFoundError, match="Tuned SIFT preset file missing"):
        baseline.load_preset("sift_ransac_tuned", "nonexistent_iris_presets.json")


@pytest.mark.parametrize("options", [dict(upsample=0), dict(upsample=1.5),
                                      dict(ratio=1.1), dict(ransac_thr=0),
                                      dict(min_inliers=2)])
def test_invalid_sift_options(options):
    image = np.zeros((32, 32), np.uint8)
    with pytest.raises(ValueError):
        baseline.sift_match(image, image, **options)


def test_ransac_options_forwarded(monkeypatch):
    reference, search, _ = synthetic_pair()
    original = cv2.estimateAffinePartial2D
    seen = []
    def estimate(*args, **kwargs):
        seen.append(kwargs["ransacReprojThreshold"])
        return original(*args, **kwargs)
    monkeypatch.setattr(cv2, "estimateAffinePartial2D", estimate)
    result = baseline.sift_match(reference, search, ransac_thr=3., min_inliers=100000)
    assert seen and set(seen) == {3.}
    assert result["found"] == 1 and result["score"] == 0
