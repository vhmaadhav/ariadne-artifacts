# E13: QATM baseline (Cheng et al., CVPR 2019), all splits

Source: private Kaggle kernel run (v1), status COMPLETE, exit 0. The run log is not included; it ends with the success line and all 7 unit tests pass.
Code: `code/baselines/qatm/` (`qatm.py`, `infer.py`, `test_qatm.py`). Predictions: `predictions/qatm/`. Reports: `reports/qatm_report_*`.
The kernel output bundle (code tree, weights, images) is not included; only predictions, reports and code are.

## Row counts and run status

| Split | Rows (kernel "all ok") | Present | Absent | Expected |
| --- | --- | --- | --- | --- |
| dev (threshold only) | 150 | n/a | n/a | 150 |
| test | 600 | 478 | 122 | 600 |
| confirm | 400 | 323 | 77 | 400 |
| real | 800 | 640 | 160 | 800 |

All row counts match. The kernel exited cleanly (`E13 QATM OK`, exit 0). Runtime: median 1.48 s per pair on test (`timing.json`, total 2627 s).

## Dev threshold

- **0.5334680676460266** (QATM peak score). Rule: max rejection F1 on dev, absent positive, lowest threshold on ties. Chosen on the 150 dev pairs only.
- Reproduced locally by `iris_report.py` with the dev manifest, same value.

## Results (95% cluster bootstrap, 2000 resamples, seed 20261010)

| Metric | test (600) | confirm (400) | real (800) |
| --- | --- | --- | --- |
| success@1 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.050 [0.034, 0.067] |
| success@3 | 0.002 [0.000, 0.007] | 0.003 [0.000, 0.010] | 0.220 [0.188, 0.256] |
| success@5 | 0.004 [0.000, 0.011] | 0.003 [0.000, 0.010] | 0.253 [0.222, 0.287] |
| wrong-repeat rate (gross_rate, present pairs with error > 20 px) | 0.987 [0.977, 0.996] | 0.988 [0.974, 0.997] | 0.653 [0.617, 0.688] |
| median error, px | 670 [633, 714] | 635 [574, 677] | 437 [369, 465] |
| accepted-decision error (wrong among accepted) | 0.992 [0.979, 1.000] (244/246) | 0.993 [0.978, 1.000] (146/147) | 0.723 [0.692, 0.755] (422/584) |
| absent accepted | 51 / 122 [38, 64] | 28 / 77 [18, 38] | 110 / 160 [95, 125] |
| present declined | 283 / 478 [259, 308] | 204 / 323 [185, 223] | 166 / 640 [143, 187] |
| rejection F1 | 0.298 [0.244, 0.352] | 0.297 [0.235, 0.362] | 0.266 [0.197, 0.334] |
| presence AUROC | 0.489 [0.433, 0.549] | 0.504 [0.431, 0.578] | 0.551 [0.494, 0.612] |

Accepted-decision error and its CI come from the same paired bootstrap (`qatm_metrics_recomputed.json`, which reproduces the iris_report values). The other rows are from `reports/qatm_report_{test600,confirm400,real800}.json`.

## Paired difference versus Drift-Sense (test only)

- Drift-Sense (shipped), same 600 test pairs, threshold 0.2617101 on the score (dev-chosen): success@5 **0.895 [0.867, 0.922]**, 9 absent accepted, 29 present declined, wrong-repeat 0.082, median 0.63 px. These match `reports/summary_e2_SUMMARY.md`.
- QATM success@5 **0.004 [0.000, 0.011]**.
- Paired Δ success@5, QATM minus Drift-Sense: **-0.891 [-0.918, -0.861]** (cluster bootstrap 2000, seed 20261010, same draws as iris_report and e6).

## Reading

- QATM does not localise the target on these tiles. Success@5 is about 0.4% on test and 0.3% on confirm, against 89.5% for Drift-Sense on test. Median error is 635 to 670 px on the synthetic splits.
- On real tiles QATM gets 25.3% success@5 with 65% wrong-repeat, still far below Drift-Sense (0.908 on real, per the paper's Drift-Sense real-tile result).
- Rejection is near chance on synthetic splits (AUROC 0.49 and 0.50), and only slightly above chance on real (0.55).
- Reason for the failure: **not established by this run.** The pose front-end is shared with Drift-Sense, so the location error comes from the QATM matching step (feature grid, alpha, peak-to-location step). We did not run a diagnostic that separates these. Per-pair hypothesis diagnostics were produced by the run but are not included.

## Deviations from the method

None found between the code that ran and the notes. Checked in `code/baselines/qatm/qatm.py`: ALPHA = 25, STRIDE = 4 with average pooling of block1_conv2, torchvision VGG19 IMAGENET1K_V1 weights, cosine similarity, product score (Eq. 3), dev-only threshold. The deviations in the notes (torch port, stride-4 grid, torchvision weights, alpha 25, location from argmax and best template cell, unconstrained search cells, 100 px template, rejection by dev F1) are therefore the full list for this run.

Notes for the record: `code/baselines/qatm/qatm.py` has no licence header. Its docstring cites the paper and the official repository (cplusx/QATM, commit 89b87287). The official repo's licence was not checked in this run.
