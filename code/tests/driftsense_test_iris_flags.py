"""IRIS switch contracts, a real-pair parity check, and the resumable CLI."""
from __future__ import annotations

import csv
import importlib.util
import math
from numbers import Real
from pathlib import Path
import subprocess
import sys

import cv2
import numpy as np
import pytest
import torch

import infer
from driftsense import matching
from scripts import iris_eval

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def smoke_pair():
    torch.set_num_threads(2)
    cv2.setNumThreads(2)
    return (infer.read_gray("data/iris/smoke/reference/00000.png"),
            infer.read_gray("data/iris/smoke/search/00000.png"))


def load_original():
    """Import the original git file alongside the working decoder."""
    source = subprocess.check_output(
        ["git", "show", "HEAD:driftsense/matching.py"], cwd=ROOT)
    path = ROOT / "results/iris/tmp_old/matching.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(source)
    spec = importlib.util.spec_from_file_location("iris_original_matching", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_identical(old, new, path="result"):
    """Use ==, never allclose; also require identical pre-existing NaN slots."""
    if isinstance(old, dict):
        assert old.keys() == new.keys(), path
        for key in old:
            assert_identical(old[key], new[key], f"{path}.{key}")
    elif isinstance(old, (tuple, list)):
        assert type(old) is type(new) and len(old) == len(new), path
        for i, (before, after) in enumerate(zip(old, new)):
            assert_identical(before, after, f"{path}[{i}]")
    elif isinstance(old, Real) and math.isnan(old):
        assert isinstance(new, Real) and math.isnan(new), path
    else:
        assert old == new, f"{path}: {old!r} != {new!r}"


def full_defaults_parity():
    """Requested proof: six smoke plus first twelve dev, no fixed pose."""
    torch.set_num_threads(4)
    cv2.setNumThreads(4)
    old = load_original()
    loaded = infer.load_model("weights/driftsense.pt")
    assert loaded is not None
    model, device = loaded
    rows = []
    for split, limit in (("smoke", 6), ("dev", 12)):
        with (ROOT / f"data/iris/manifest_{split}.csv").open(newline="", encoding="utf-8") as handle:
            rows.extend(list(csv.DictReader(handle))[:limit])
    for row in rows:
        reference = infer.read_gray(row["reference_path"])
        search = infer.read_gray(row["search_path"])
        # First check the untouched signature defaults, then register's settings.
        for kwargs in ({}, {**iris_eval.decode_kwargs("shipped"),
                            "label_convention": row["label_convention"]}):
            before = old.locate_phase2(model, reference, search, device, **kwargs)
            after = matching.locate_phase2(model, reference, search, device, **kwargs)
            assert_identical(before, after, row["pair_id"])
        print(f"exact parity: {row['pair_id']} (defaults and shipped)", flush=True)
    assert len(rows) == 18
    print("PASS: 18 pairs x 2 settings, identical keys and numeric values; matching NaNs", flush=True)


def test_defaults_parity(smoke_pair):
    model, device = infer.load_model("weights/driftsense.pt")
    old = load_original()
    # Fixed pose keeps this regression fast while exercising native stages.
    kwargs = {"pose": (11.4, 0.1), "strip_rot": True}
    before = old.locate_phase2(model, *smoke_pair, device, **kwargs)
    after = matching.locate_phase2(model, *smoke_pair, device, **kwargs)
    explicit = matching.locate_phase2(
        model, *smoke_pair, device, canonicalize=True, native_verification=True,
        subpixel="parabola", auto_early_exit=True, **kwargs)
    assert_identical(before, after)
    assert_identical(after, explicit)


def stub_decoder(monkeypatch):
    calls = {"network": [], "native": [], "polish": [], "rows": [], "strip": []}
    poses = [(9., -1., .9), (10., 0., .8), (11., 1., .7)]
    monkeypatch.setattr(matching, "pose_candidates", lambda *a, **kw: poses[:kw["k"]])

    def locate(model, reference, search, device, **kw):
        i = len(calls["network"])
        calls["network"].append((search, kw))
        return {"x": 108., "y": 655., "score": [.9, .7, .6][i],
                "peak_ratio": .5, "coarse": (108., 655.)}

    def refine(search, template, x, y, **kw):
        i = len(calls["native"])
        calls["native"].append(kw)
        return x + .25, y - .25, [.1, .9, .2, .8][min(i, 3)]

    def polish(reference, search, x, y, scale, theta):
        calls["polish"].append((scale, theta))
        return scale + .1, theta + .1, .9

    def rows(search, template, x, y, **kw):
        calls["rows"].append(kw)
        return x + .1, y

    def strip(*args):
        calls["strip"].append(args)
        return args[-1] + .1, .01

    monkeypatch.setattr(matching, "locate", locate)
    monkeypatch.setattr(matching, "refine_zncc", refine)
    monkeypatch.setattr(matching, "polish_pose", polish)
    monkeypatch.setattr(matching, "drift_row_refine", rows)
    monkeypatch.setattr(matching, "strip_rotation", strip)
    monkeypatch.setattr(matching, "denoised_zncc", lambda *a, **kw: .8)
    return calls


def test_nocanon_keeps_original_frame_and_nominal_template(monkeypatch, smoke_pair):
    calls = stub_decoder(monkeypatch)
    def forbidden(*a, **kw):
        pytest.fail("canonicalization or inverse mapping ran")
    monkeypatch.setattr(matching, "canonicalize_search", forbidden)
    monkeypatch.setattr(matching, "uncanonicalize_point", forbidden)
    res = matching.locate_phase2(None, *smoke_pair, None,
                                canonicalize=False, auto_early_exit=False)
    assert len(calls["network"]) == 3  # pose search remains
    assert len(calls["native"]) == 3
    for frame, kwargs in calls["network"]:
        assert frame is smoke_pair[1]
        assert kwargs["factor"] == matching.SCALE and kwargs["rotation_deg"] == 0
    assert res["canonical"] == (108., 655.)


def test_network_selects_score_and_keeps_native_stages(monkeypatch, smoke_pair):
    calls = stub_decoder(monkeypatch)
    res = matching.locate_phase2(None, *smoke_pair, None,
                                verification="network", auto_early_exit=False,
                                strip_rot=True)
    assert res["scale_pre_polish"] == 9.  # native ZNCC would select 10
    assert len(calls["native"]) == 3
    assert all(calls[name] for name in ("polish", "rows", "strip"))
    calls = stub_decoder(monkeypatch)
    native = matching.locate_phase2(None, *smoke_pair, None,
                                   auto_early_exit=False)
    assert native["scale_pre_polish"] == 10.


def test_nonative_skips_every_native_stage(monkeypatch, smoke_pair):
    calls = stub_decoder(monkeypatch)
    def forbidden(*a, **kw):
        pytest.fail("native verification ran")
    for name in ("refine_zncc", "polish_pose", "strip_rotation", "drift_row_refine", "denoised_zncc"):
        monkeypatch.setattr(matching, name, forbidden)
    res = matching.locate_phase2(None, *smoke_pair, None, verification="network",
                                native_verification=False, strip_rot=True,
                                refit_xy=True, auto_early_exit=False,
                                label_convention="center")
    assert len(calls["network"]) == 3
    assert res["confidence"] == res["score"] == .9
    assert res["scale"] == 9. and res["theta"] == -1.
    assert "zncc" not in res and "zncc_med3" not in res
    assert res["x"] == res["rigid_x"] - .5


def test_noexit_evaluates_all_and_preserves_explicit_gate(monkeypatch, smoke_pair):
    calls = stub_decoder(monkeypatch)
    monkeypatch.setattr(matching, "_early_exit_fires", lambda *a: True)
    matching.locate_phase2(None, *smoke_pair, None)
    assert len(calls["network"]) == 1
    calls = stub_decoder(monkeypatch)
    matching.locate_phase2(None, *smoke_pair, None, auto_early_exit=False)
    assert len(calls["network"]) == 3
    calls = stub_decoder(monkeypatch)
    matching.locate_phase2(None, *smoke_pair, None,
                          auto_early_exit=False, early_exit_zncc=.05)
    assert len(calls["network"]) == 1


def test_integer_peak_and_forwarding(monkeypatch, smoke_pair):
    reference, search = smoke_pair
    template = matching.make_template(reference, 11.4, .1)
    sea, tpl = matching.standardize(search / 255.), matching.standardize(template / 255.)
    integer = matching.refine_zncc(sea, tpl, 108., 655., subpixel="integer")
    parabola = matching.refine_zncc(sea, tpl, 108., 655., subpixel="parabola")
    assert integer != parabola
    assert integer[2] == parabola[2]
    assert (integer[0] - template.shape[1] / 2).is_integer()
    assert (integer[1] - template.shape[0] / 2).is_integer()
    calls = stub_decoder(monkeypatch)
    matching.locate_phase2(None, *smoke_pair, None, subpixel="integer",
                          refit_xy=True, auto_early_exit=False)
    assert len(calls["native"]) == 4  # three hypotheses plus polished XY refit
    assert all(call["subpixel"] == "integer" for call in calls["native"] + calls["rows"])


def test_drift_row_snap_receives_integer(monkeypatch, smoke_pair):
    original = matching.refine_zncc
    seen = []
    def spy(*args, **kwargs):
        seen.append(kwargs.get("subpixel"))
        return original(*args, **kwargs)
    monkeypatch.setattr(matching, "refine_zncc", spy)
    template = matching.make_template(smoke_pair[0], 11.4, .1)
    matching.drift_row_refine(smoke_pair[1], template, 108.18, 655.18,
                             subpixel="integer")
    assert seen == ["integer"]


@pytest.mark.parametrize("kwargs", [dict(canonicalize=False), dict(verification="network"),
                                      dict(native_verification=False), dict(subpixel="integer"),
                                      dict(auto_early_exit=False)])
def test_switch_runs_real_smoke_pair(smoke_pair, kwargs):
    model, device = infer.load_model("weights/driftsense.pt")
    res = matching.locate_phase2(model, *smoke_pair, device, pose=(11.4, .1), **kwargs)
    assert all(math.isfinite(res[key]) for key in ("x", "y", "theta", "scale", "confidence"))


def test_variants_and_generated_table():
    for name in iris_eval.VARIANTS:
        kwargs = iris_eval.decode_kwargs(name)
        assert kwargs.get("auto_early_exit", True) == (name in {"shipped", "small", "wide2"})
    assert iris_eval.decode_kwargs("shipped") == iris_eval.SHIPPED_KWARGS
    assert iris_eval.variants_table() in (ROOT / "results/iris/VARIANTS.md").read_text(encoding="utf-8")


def test_worker_exception_keeps_failure_row(monkeypatch, smoke_pair):
    monkeypatch.setattr(infer, "read_gray", lambda _: smoke_pair[0])
    monkeypatch.setattr(iris_eval, "_MODEL", (None, None))
    monkeypatch.setattr(iris_eval, "_MODEL_WEIGHTS", "stub")
    def broken(*args, **kwargs):
        raise RuntimeError("intentional test failure")
    monkeypatch.setattr(matching, "locate_phase2", broken)
    row = dict(pair_id="bad", reference_path="ref", search_path="sea", label_convention="edge")
    result = iris_eval._worker((row, "shipped", "stub", 2, .55))
    assert result["found"] == result["score"] == 0
    assert result["status"] == "RuntimeError: intentional test failure"
    assert result["seconds"] > 0
    assert all(math.isnan(result[key]) for key in ("x", "y", "theta", "scale"))


def test_cli_schema_resume_and_raw_rejected_pose(tmp_path):
    output = tmp_path / "predictions.csv"
    command = [sys.executable, "-X", "utf8", "scripts/iris_eval.py",
               "--manifest", "data/iris/manifest_smoke.csv", "--variant", "shipped",
               "--out", str(output), "--limit", "2", "--jobs", "2",
               "--threads", "2", "--threshold", "1.1"]
    subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True, timeout=120)
    with output.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == iris_eval.FIELDS
        rows = list(reader)
    assert [row["pair_id"] for row in rows] == ["smoke_00000", "smoke_00001"]
    assert all(row["found"] == "0" and row["status"] == "ok" for row in rows)
    assert all(float(row["scale"]) > 0 and float(row["x"]) > 0 for row in rows)
    before = output.read_bytes()
    subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True, timeout=30)
    assert output.read_bytes() == before
