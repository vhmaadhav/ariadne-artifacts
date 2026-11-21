# E10: larger development split (800 pairs), thresholds chosen on dev only

Kernel `<kaggle-account>/ariadne-e10-dev-large` (CPU, COMPLETE 21 Nov). Dev seeds 710707 and 710808, 400 pairs each: **800 pairs, 656 present, 144 absent** (the RUNLOG planned about 160 absent; the generator gave 144).

## Freeze check
- `manifest_dev_large.csv` sha256 `8539485f...a25235f` matches its entry in `dev_large_files.sha256`. Verified locally.
- Images were not fetched (disk), so the per-image hashes were not re-checked here. The kernel reports `sha_failed 0` (`kaggle_run.json`).
- **Discrepancy:** `FROZEN.txt` says 1602 files; the sha256 list has 1603 lines and `kaggle_run.json` says 1603. Not explained.

## Thresholds (dev only)
- `tau_F1` (max rejection F1, absent positive, lowest threshold on ties) = **0.1548467**. Dev F1 0.839.
- `tau_err5` (lowest threshold with accepted-decision error <= 5%) = **0.3108282**. Dev error 4.9%.
- Both re-derived locally from the dev scores with the same rules (raw-score scan): identical values.
- Reference: 0.2617101 (the 150-pair dev choice). On the 800 dev it gives F1 0.811 and error 6.1%.

## Results (code/e10_eval.py, unchanged thresholds, e4 noexit predictions, 2000 cluster draws, seed 20261010)

| split | tau | success@5 [95% CI] | absent accepted | present declined | accepted-decision error | F1 |
|---|---|---|---|---|---|---|
| test (600: 478 / 122) | tau_F1 0.1548 | 0.904 [0.877, 0.930] | 28/122 | 12/478 | 0.126 | 0.825 |
| | tau_err5 0.3108 | 0.883 [0.852, 0.911] | 7/122 | 36/478 | 0.060 | 0.843 |
| | **0.2617** | **0.895 [0.867, 0.922]** | 9/122 | 29/478 | 0.066 | 0.856 |
| confirm (400: 323 / 77) | tau_F1 0.1548 | 0.920 [0.889, 0.947] | 18/77 | 5/323 | 0.116 | 0.837 |
| | tau_err5 0.3108 | 0.910 [0.878, 0.939] | 4/77 | 12/323 | 0.067 | 0.901 |
| | **0.2617** | **0.913 [0.883, 0.942]** | 9/77 | 9/323 | 0.087 | 0.883 |
| real (800: 640 / 160) | tau_F1 0.1548 | 0.911 [0.880, 0.939] | 51/160 | 11/640 | 0.143 | 0.779 |
| | tau_err5 0.3108 | 0.903 [0.867, 0.934] | 0/160 | 26/640 | 0.059 | 0.925 |
| | **0.2617** | **0.908 [0.873, 0.938]** | 10/160 | 22/640 | 0.075 | 0.904 |

The 0.2617 rows match the paper and E6 (test 0.895, confirm 0.913, real 0.908).

## Reading
- The F1 rule on the 800-pair dev picks 0.155, far below 0.2617. Held out, it accepts 28/122 absent on test and 51/160 on real. Its F1 falls to 0.78 on real. **The F1 rule is unstable across dev sizes**, so the 150-pair choice of 0.2617 was not confirmed by the larger split.
- The err5 rule (0.311) lowers absent acceptance on every split (7, 4, 0 against 9, 9, 10) and accepted-decision error (6.0, 6.7, 5.9 against 6.6, 8.7, 7.5). It costs 1.3, 0.3 and 0.5 points of success@5 and gives higher F1 on confirm and real but lower F1 on test (0.843 against 0.856).
- Neither alternative is clearly better on all criteria, so **0.2617 stays the headline** (see the paper, Sect. limitation iv). The err5 threshold is the more conservative operating point to report beside it.
- On the 800-pair dev, 0.2617 has accepted-decision error 6.1%, above the 5% target, and F1 0.811 against 0.839 at its own optimum.

Files: `threshold_dev_large.json`, `pred_dev_large_noexit.csv`, `manifest_dev_large.csv`, `FROZEN.txt`, `dev_large_files.sha256`, `kaggle_run.json`, `VARIANTS.md`, `kernel_log.txt`, `logs/`. Generated images were not kept (regenerable from the seeds).
