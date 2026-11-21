# E2: ZNCC baseline vs Drift-Sense on all 600 test pairs

Source: `report_test600.md` / `.json` (iris_report.py overlay, 2000 cluster bootstrap, seed 20261010, 600 clusters = pairs).
Pairs: test_s1 (frozen split-1 ZNCC, `driftsense-iris27/results/kaggle/zncc`), test_s2 and test_s3 (Kaggle `ariadne-e2-zncc-test-s23`, v1, COMPLETE, 0 failed rows).
Present 478, absent 122.
Thresholds: fixed, chosen on disjoint dev labels and re-derived with the script: zncc_ms 0.3653055 (same as split-1), Drift-Sense (shipped) 0.2617101 (same as split-1).
Drift-Sense = `shipped` variant, `driftsense-iris27/results/kaggle/core/pred_test_shipped.csv`.

| Metric (95% CI) | ZNCC (zncc_ms) | Drift-Sense (shipped) |
| --- | --- | --- |
| success@1 | 0.282 [0.243, 0.324] | 0.636 [0.592, 0.680] |
| success@3 | 0.410 [0.367, 0.456] | 0.845 [0.810, 0.878] |
| success@5 | 0.437 [0.393, 0.483] | 0.895 [0.867, 0.922] |
| loc-only@5 | 0.460 [0.416, 0.506] | 0.908 [0.881, 0.934] |
| wrong-repeat rate (gross_rate) | 0.523 [0.475, 0.568] | 0.082 [0.058, 0.108] |
| median error, px (p50) | 30.9 [4.66, 50.3] | 0.63 [0.54, 0.74] |
| p90 error, px | 580 [487, 628] | 4.52 [3.53, 42.2] |
| rejection F1 | 0.521 [0.439, 0.597] | 0.856 [0.806, 0.898] |
| presence AUROC | 0.770 [0.722, 0.814] | 0.978 [0.967, 0.987] |
| absent accepted (of 122) | 59 [45, 74] | 9 [4, 15] |
| present declined (of 478) | 57 [43, 72] | 29 [19, 40] |

Paired difference, ZNCC minus Drift-Sense (same 600 pairs): success@5 -0.458 [-0.503, -0.411]; F1 -0.335 [-0.421, -0.252]; p50 error +30.2 px [4.04, 49.7].

Notes
- Drift-Sense uses the dev-chosen 0.2617 threshold, not the 0.55 repo default (0.55 not reported here).
- Wrong-repeat rate is the report's `gross_rate`: present pairs with centre error > 20 px, as a fraction of the 478 present pairs (iris_report.py line 143 divides by n_present).
- Headline: on all 600 test pairs the ZNCC baseline is far below Drift-Sense on localisation, error and rejection, with the same gap as on split-1.
