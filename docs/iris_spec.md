# IRIS experiment spec (shared by all workers; read fully before starting)

## Where you are
- cwd = the working copy root (made by `tools/setup_workdir.sh`): a copy of the public `semicon-driftsense` repo at commit `5145c39b8d77`. It has its own `.git`; **never run git commit, checkout, reset, stash, clean or push**. Only create or edit the files your brief names.
- Python: `.venv/Scripts/python.exe` (3.11.15, torch 2.13.0+cpu, cv2 5.0.0 with SIFT, numpy 2.4.6, pandas 3.0.5, scikit-learn 1.9.1, kornia 0.8.3, `lightglue` installed). Always run `python -X utf8`. For LightGlue set `TORCH_HOME=<cwd>/.torch_home` (the SIFT-LightGlue weights are already cached there). **No network**: do not pip install anything or download anything.
- Machine: 8 cores / 16 threads, 15 GB RAM shared with other jobs. Use at most 4 threads per process and at most 2 processes. Do not run anything that takes longer than about 10 minutes in one command; if a script is long, give it `--limit` smoke options and tell me the exact full command instead of running it.
- Use forward slashes in code and paths.

## Frozen rules (scientific honesty)
1. Do not modify `weights/`, `generator/` (or any other vendored generator directory) or the default values in `driftsense/config.py`.
2. Any new option on an existing function is a keyword argument whose default reproduces the current behaviour **bit for bit**. Prove it with a parity test (old code vs new code, same inputs, identical outputs) and say how you proved it.
3. All new random draws use seed `20261010` (numpy `default_rng(20261010)` or a documented derivation of it).
4. Nothing is tuned on test splits. Thresholds for non-shipped methods come only from the dev split.
5. Never invent results. If something fails or you could not check it, say so.

## Data already on disk
- `data/iris/smoke` (6 pairs), `data/iris/dev` (150), `data/iris/test_s1`, `test_s2`, `test_s3` (200 each, may still be generating; manifests are written when a split finishes). Made by `generate_dataset.py --phase2 --seed ...` (the repo's Phase-2 stress mixture: zoom 8-12, rotation +/-5 deg, 20% absent, severity ladder 0-1, polygon scale +/-20%).
- Canonical manifests (built by `tools/make_iris_manifest.py`): `data/iris/manifest_smoke.csv`, `manifest_dev.csv`, `manifest_test.csv`. Real-image manifest: `data/iris/manifest_real.csv` (built by `scripts/iris_make_real.py`).
- Real source tiles: `data/real_raw/edmond/dataset/sems/m1|m2/semNNNN.png` (40 tiles, 4096x3536, 8-bit grayscale, CC-BY 4.0, Rothaug et al., doi 10.17617/3.HY5SYN, 14.65 nm/px, metal layers of a commercial IC) and 10 more in `data/real_raw/emsec/dataset/sems/`.

## Canonical manifest (CSV, one row per pair)
`pair_id` (str, unique across all splits), `split`, `reference_path`, `search_path` (relative to the cwd, forward slashes), `found` (0/1), `gt_x`, `gt_y` (float, -1 when absent), `gt_scale` (z, the search nm/px divided by the reference nm/px; NaN when absent), `gt_rot_deg` (CCW positive; NaN when absent), `label_convention` (`edge` or `center`), `stratum` (synthetic: `absent`, `sev_q1`..`sev_q4`; real: `real_A`, `real_B`, `real_absent`), `group_id` (resampling cluster: synthetic canvas, or real source tile), `source` (`synthetic` or `real`), optional `architecture`, `severity`.

Coordinate conventions: `edge` = the top-left corner of pixel (0,0) is (0,0), so a pixel centre is (i+0.5, j+0.5); `center` = the centre of pixel (0,0) is (0,0). `edge = center + 0.5`. The reference image is 1000x1000, so its centre is (500,500) in edge and (499.5,499.5) in center convention. The synthetic generator data use `edge`; the real pairs use `center`. `driftsense.matching.locate_phase2(..., label_convention=...)` takes either.

Geometry: the reference is `z` times finer than the search. A reference point r (pixel-centre coords) lands in the search at `s = c + (1/z) * Q_theta (r - b)` with `b=(499.5,499.5)`, `c` the match centre (GT x,y), `Q_theta = [[cos,sin],[-sin,cos]]` (visual counterclockwise rotation by theta in image coordinates, y down). The decoder reports `scale = z` (not 1/z) and `theta` in degrees, CCW positive, about the match centre.

## Prediction CSV (one row per pair per method)
`pair_id, method, found, score, x, y, theta, scale, seconds, status`
- `x,y,theta,scale` are the **raw pose of the best hypothesis even when `found=0`** (in the manifest's label convention); `found` is the method's own accept decision (`score >= threshold`); `score` in [0,1], higher means more confident the reference is present; `seconds` is wall time for that pair (single process unless stated); `status` is `ok` or an error string (a failing pair is still written, with found=0, score=0, pose NaN).
- Sorted by `pair_id`, written incrementally so a killed run can resume (skip pair ids already present).

## Metric definitions (used by `scripts/iris_report.py`)
- Present pairs only for localisation. `err_px` = Euclidean distance between raw (x,y) and (gt_x,gt_y).
- `success@r` (r in 1,3,5 px) = `found==1 and err_px<=r`, divided by ALL present pairs (a declined present pair is a failure). `loc_only@r` = `err_px<=r` ignoring `found`. Gross failure = `err_px>20`.
- Scale error % = 100*|scale-gt_scale|/gt_scale. Rotation error = |wrap to [-180,180] of (theta-gt_rot_deg)|. Report on all present pairs and on the subset `found and err_px<=5`.
- Rejection with ABSENT as the positive class: precision, recall, F1, counts of absent accepted and present declined; AUROC of `score` separating present from absent.
- Correct-match AUC: AUROC of `score` for the label `present and err_px<=5` versus everything else.
- Runtime: median, p90, p95, max of `seconds`.
- Uncertainty: cluster bootstrap over `group_id`, 2000 resamples, seed 20261010, 95% percentile intervals, thresholds held fixed; paired differences against a reference method use the same resamples.
