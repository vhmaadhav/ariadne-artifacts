# E4 check (features-a, features-b), fetched 14:34 IST

Files: `a/` (dev, test noexit; smoke) and `b/` (real noexit; smoke). Logs: `a/ariadne-e4-features-a.log`, `b/ariadne-e4-features-b.log`, `*/results/kaggle_run.json`. Largest file 5.5 MB (`b/results/ariadne/E4/feat_real_noexit.jsonl`), so nothing over 50 MB.

## (a) Parity gate
- PARITY_OK in both kernels: plain vs instr identical on 6/6 smoke pairs; frozen smoke max xy diff 1.3e-10 px. No `PARITY_FAILED.txt`.
- Note: the smoke compares against the frozen smoke decisions, not a Kaggle smoke file (as in RUNLOG deviation 4).

## (b) Decisions and centres vs frozen (noexit only; the kernels did not run the shipped variant)
Reference: dev and test = `driftsense-iris27/results/kaggle/core/pred_{dev,test}_noexit.csv`; real = `.../realeval/pred_real_noexit.csv`. `abl_a` has no noexit prediction file of its own; its VARIANTS.md defines noexit with the same config as core, so core is the reference used.

| split | pairs compared | found flips | centre diff > 0.5 px (found on both) | max centre diff |
|---|---|---|---|---|
| dev | 150 | 0 | 0 | 0 px |
| test | 600 | 0 | 0 | 0 px |
| real | 800 | 0 | 0 | 0 px |

Found counts match: dev 77, test 366, real 539. The files are not byte-identical to the frozen ones (md5 differs; the numbers agree), so the difference is formatting only.

## (c) Feature-file coverage
| split | rows | expected | unique IDs | duplicates | missing vs frozen IDs | extra IDs | no selection (selected_index < 0) |
|---|---|---|---|---|---|---|---|
| dev | 150 | 150 | 150 | 0 | 0 | 0 | 0 |
| test | 600 | 600 | 600 | 0 | 0 | 0 | 0 |
| real | 800 | 800 | 800 | 0 | 0 | 0 | 0 |

Columns: all rows have `pair_id, selected_index, hypotheses, rigid_x, rigid_y, winner_margin, theta, scale, x, y, score, confidence, zncc_med3, n_hypotheses`. Every hypothesis has `network_score, peak_ratio, zncc, coarse_x_native, coarse_y_native, x_snap, y_snap, zncc_peaks, zncc_n_sites`, which are the fields `five_features` and `evt_row_score` read. None are missing.

NaN rows (expected, by design): `winner_margin` is NaN exactly where `n_hypotheses == 1` (no pose contest). These rows get declined by the logistic model.
- dev: 2 of 150
- test: 15 of 600
- real: 166 of 800

## Verdict
E4 features for dev, test and real are complete and match the frozen noexit decisions and centres exactly. E4 is clear for E6 fitting on dev/test/real, once E5 is frozen as well.
