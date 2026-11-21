# E3: LoFTR baseline (outdoor checkpoint), full dev and test

Source: Kaggle `<kaggle-account>/ariadne-e3-loftr-full` v1, COMPLETE, T4 GPU. Same wrapper and settings as the smoke and diagnostic runs (`code/baselines/loftr_baseline.py`; MIN_INLIERS 8; no tuning). Threshold 0.3935 chosen on disjoint dev labels (F1 maximised). Files in `results/e3_full/results/` (`pred_dev_loftr.csv`: 150 rows, 14 found; `pred_test_loftr.csv`: 600 rows, 91 found, all `ok`; `report_test_loftr.{md,json}`). The real split was not run.

## Test (600 pairs: 478 present, 122 absent; bootstrap 2000, seed 20261010)

Same metrics as `results/e2/SUMMARY.md`:

| Metric (95% CI) | LoFTR | ZNCC (E2) | Drift-Sense (E2) |
|---|---|---|---|
| success@1 | 0.031 [0.017, 0.048] | 0.282 [0.243, 0.324] | 0.636 [0.592, 0.680] |
| success@3 | 0.033 [0.019, 0.051] | 0.410 [0.367, 0.456] | 0.845 [0.810, 0.878] |
| **success@5** | **0.033 [0.019, 0.051]** | 0.437 [0.393, 0.483] | 0.895 [0.867, 0.922] |
| wrong-repeat rate (gross_rate) | 0.937 [0.914, 0.958] | 0.523 [0.475, 0.568] | 0.082 [0.058, 0.108] |
| median error, px | 403 [378, 426] | 30.9 [4.66, 50.3] | 0.63 [0.54, 0.74] |
| p90 error, px | 757 [694, 786] | 580 [487, 628] | 4.52 [3.53, 42.2] |
| rejection F1 | 0.354 [0.308, 0.399] | 0.521 [0.439, 0.597] | 0.856 [0.806, 0.898] |
| presence AUROC | 0.617 [0.564, 0.666] | 0.770 [0.722, 0.814] | 0.978 [0.967, 0.987] |
| absent accepted (of 122) | 4 [1, 8] | 59 [45, 74] | 9 [4, 15] |
| present declined (of 478) | 426 [404, 447] | 57 [43, 72] | 29 [19, 40] |

LoFTR's success@5 on test is 0.033 [0.019, 0.051]: it localises almost no pair within 5 px. Its error is at the scale of the image (median 403 px), so it fails as a localiser on this task. It also rejects most present pairs at the dev threshold. Pose is poor as well: only 16 of 478 present pairs have a centre within 5 px (pose_within5_n), so scale and rotation are rarely usable. Dev-chosen threshold only, not tuned.

## Diagnostics (not part of the reported numbers)
- Diagnostic run `ariadne-e3-loftr-diag` (`results/e3_diag/`): the reference-vs-self check gives 144 inliers and 0.01 to 0.06 px error, so the wrapper geometry (template, RANSAC, pose mapping) is sound.
- The candidate nearest the ground truth reaches only 2 to 5 RANSAC inliers, below MIN_INLIERS 8. Only dev_00003 comes within 1.6 px.
- Not separated: cross-domain images (synthetic nm-scale) versus the 8 to 12x template against the 1000 px search. Not tuned.

## Notes
- Runtime about 5.2 s per pair on the T4 (median).
- `logs/loftr_test600.log` is empty (0 bytes), but the report and 600 test rows are present and checked (600 unique IDs, all `ok`).
