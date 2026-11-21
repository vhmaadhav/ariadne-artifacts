# E11: alternative decoders on confirmation and real, tau = 0.2617101

Kernel `<kaggle-account>/ariadne-e11-alt-decoders` (CPU, COMPLETE 21 Nov). `netnative` (network score only, no native verification) and `netselect` (network selection, native stages kept). Paired deltas use `noexit` (e4 predictions, same thresholds) and 2000 cluster draws, seed 20261010.

| split | variant | success@1 | success@5 [95% CI] | median err (px) | wrong repeat (>20 px) | absent accepted | present declined | accepted-decision error | F1 | paired delta success@5 vs noexit [95% CI] |
|---|---|---|---|---|---|---|---|---|---|---|
| confirm (400: 323/77) | noexit | 0.706 | 0.913 [0.883, 0.942] | 0.47 | 0.068 | 9/77 | 9/323 | 0.087 | 0.883 | -- |
| | netnative | 0.430 | 0.944 [0.917, 0.968] | 1.10 | 0.046 | 18/77 | 1/323 | 0.103 | 0.861 | +3.1 [+0.9, +5.6] |
| | netselect | 0.712 | 0.935 [0.907, 0.960] | 0.47 | 0.046 | 10/77 | 6/323 | 0.077 | 0.893 | +2.2 [+0.6, +4.0] |
| real (800: 640/160) | noexit | 0.869 | 0.908 [0.873, 0.938] | 0.09 | 0.089 | 10/160 | 22/640 | 0.075 | 0.904 | -- |
| | netnative | 0.484 | 0.894 [0.856, 0.928] | 1.03 | 0.105 | 117/160 | 5/640 | 0.239 | 0.414 | -1.4 [-2.7, -0.5] |
| | netselect | 0.859 | 0.892 [0.853, 0.927] | 0.10 | 0.105 | 6/160 | 38/640 | 0.061 | 0.875 | -1.6 [-3.0, -0.5] |

## Does the test trade-off replicate?
Test (600) showed netnative and netselect with higher success@5, worse precision and worse rejection.
- **Confirmation: replicates.** Both raise success@5 (+3.1 and +2.2 points, intervals above zero). netnative accepts 18 of 77 absent (against 9) and has accepted-decision error 0.103 (against 0.087). netselect accepts 10 of 77 and has error 0.077, which is lower than noexit. Its rejection is only slightly worse, and its F1 is higher (0.893 against 0.883).
- **Real: does not replicate.** Both lower success@5 (-1.4 and -1.6 points, intervals below zero). netnative collapses: 117 of 160 absent accepted, F1 0.41. netselect accepts fewer absent references than noexit (6 against 10) but declines more present pairs (38 against 22).
- Net: the "higher success@5" part holds on confirmation but not on real. The "worse rejection" part holds for netnative on both splits, but not for netselect on real.

Ambiguity: netnative's success@1 is 0.43 (confirm) and 0.48 (real), against 0.71 and 0.87 for noexit, and its median error is about 1.0 to 1.1 px. The shipped native stages are what give sub-pixel precision.

Files: `pred_{confirm,real}_{netnative,netselect}.csv`, `kaggle_run.json`, `VARIANTS.md`, `kernel_log.txt`, `logs/`.
