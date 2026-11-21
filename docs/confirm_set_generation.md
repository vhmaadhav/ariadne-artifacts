# Confirmation set: generate and freeze (E5)

Purpose: a fresh, untouched set to confirm or refute the calibrated-rejection rules
(EVT, logistic) chosen on dev. It is generated and frozen **before any fitting**.
Nothing is fitted, tuned or looked at for thresholds on it.

Two new generator seeds, 200 pairs each: **710505** and **710606**. Both are unused
by training and by the existing splits (test_s1/s2/s3 = 710101/710202/710303,
dev = 710404; see driftsense-iris27 docs/FREEZE.md).

## 0. Preconditions

- Working copy made by `bash tools/setup_workdir.sh work` (upstream 5145c39 + ablation
  patch + overlay), venv installed. Use the same venv as the rest of the study.
- Run from the working copy root (`cd work`). `PY` below is that venv's Python.
- The generator is the vendored one (`generate_dataset.py` -> `driftsense/generate.py`).
  Do not edit it.

## 1. Generate (about 0.5 to 1 h each on 4 workers; log the wall time)

```bash
PY=.venv/bin/python        # Windows: .venv/Scripts/python.exe
$PY -X utf8 generate_dataset.py --phase2 --num-pairs 200 --seed 710505 --workers 4 \
    --output-dir data/iris/confirm_710505
$PY -X utf8 generate_dataset.py --phase2 --num-pairs 200 --seed 710606 --workers 4 \
    --output-dir data/iris/confirm_710606
```

Each run writes `reference/`, `search/` and `manifest.csv` into its output directory.
Check the counts before going on: 200 pairs per directory, and about 160 present
(absent fraction 0.2 under --phase2).

## 2. Build the canonical manifest

```bash
$PY -X utf8 tools/make_iris_manifest.py manifests/manifest_confirm.csv \
    data/iris/confirm_710505 data/iris/confirm_710606
```

This gives 400 rows, pair ids `confirm_710505_NNNNN` and `confirm_710606_NNNNN`,
split names taken from the directory names, label convention `edge`, and strata
`absent`, `sev_q1`..`sev_q4`. The printed split x stratum table must show 400 rows.

## 3. Freeze (sha256 of every file, before any run that reads the set)

```bash
find data/iris/confirm_710505 data/iris/confirm_710606 -type f | sort | xargs sha256sum \
    > manifests/confirm_files.sha256
sha256sum manifests/manifest_confirm.csv >> manifests/confirm_files.sha256
sha256sum -c manifests/confirm_files.sha256 | tail -1      # expect no FAILED lines
git rev-parse HEAD                                          # expect 5145c39b8d776839eaed6e844bd01769c971748b
git status --porcelain                                      # only the expected overlay/patch files
```

Then copy `manifests/manifest_confirm.csv` and `manifests/confirm_files.sha256` to
`ariadne/results/E5_confirm/` (the project repo), and record the date, the hostname
and the generator commit in that folder's `FROZEN.txt`. Upload the image folders as a
private Kaggle dataset only if a Kaggle run needs them (`iris27-confirm`).

Rules after the freeze:
- Do **not** regenerate, edit, drop or re-select pairs. Images are not guaranteed
  bit-identical across machines, so every later run must read these files.
- If `sha256sum -c` ever fails, stop, report it, and do not run E6 on this set.
- Nothing in E6 may read these files for fitting or thresholds. Thresholds come from
  dev only (`manifests/manifest_dev.csv` and its predictions).

## 4. What runs on the confirmation set (after the freeze)

- E4-style instrumented rerun (`noexit` with `--features-out`), see RUN_BRIEF.md step E5.
- ZNCC baseline (`zncc_ms`), cheap, for the same table.
- Frozen rules applied as they are: EVT and logistic thresholds from dev; the min rule
  at 0.2617 (dev) and at 0.55 (shipped).
