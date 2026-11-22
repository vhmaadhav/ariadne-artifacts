# E18 scorer summary (exploratory, post-registration)

Command (run from repo root, 2026-11-22):

    python3 -X utf8 -B -I code/e18_eval.py --config <paths.json> --tau-e17 0.36530551314353943 --out results/e18/eval_e18.json

- Frozen ZNCC tau = 0.36530551314353943 (E16 value, used as the ZNCC acceptance rule).
- Drift-Sense R1 tau = 0.2617101; DS R3 gate delta = 0.09562161564826965 (code/e15_thresholds.json).
- TAU_E17 was NOT available. The required `--tau-e17` flag was filled with the frozen tau as a placeholder.
  Every `ZNCC_E17_tau` column and `I_*_E17_tau` / `AB_*_E17_tau` contrast is therefore a duplicate of the frozen-tau value and carries no information. Ignore them.
- Cluster bootstrap by tile, B = 2000, seed 20261010. Intervals are 95% percentile CIs.
- Paths: outputs under results/e18/ariadne-e18-{ds-mid,ds-high,zncc-mid-a,zncc-mid-b,zncc-high-a,zncc-high-b}/. Undistorted set from results/e15_real and results/e16.

## Headline (400 pairs per condition; success@5 over present pairs, 320 present)

| condition | rule | success@5 [95% CI] | success@1 | absent accepted (cross, 80) | coverage |
|---|---|---|---|---|---|
| mid | DS R1 | 0.909 [0.863, 0.950] | 0.772 | 0.125 [0.063, 0.188] | 0.782 |
| mid | ZNCC frozen tau | 0.984 [0.963, 1.000] | 0.516 | 0.988 [0.963, 1.000] | 0.995 |
| high | DS R1 | 0.866 [0.819, 0.906] | 0.722 | 0.100 [0.038, 0.163] | 0.777 |
| high | ZNCC frozen tau | 0.934 [0.897, 0.966] | 0.309 | 0.988 [0.963, 1.000] | 0.995 |
| undistorted (E15 real) | DS R1 | 0.913 [0.863, 0.953] | 0.881 | 0.100 [0.038, 0.175] | 0.785 |
| undistorted (E15 real) | ZNCC frozen tau | 0.984 [0.959, 1.000] | 0.978 | 0.988 [0.963, 1.000] | 0.995 |

Paired success@5 difference (ZNCC frozen minus DS R1), CI from the same bootstrap draw:
- mid: +0.075 [0.047, 0.109]
- high: +0.069 [0.041, 0.100]
- undistorted: +0.072 [0.041, 0.109]

Interaction contrasts (success@5, (ZNCC minus DS) at level minus same on undistorted):
- I_mid = +0.003 [-0.028, 0.034]
- I_high = -0.003 [-0.034, 0.025]
- AB (undistorted, condition B minus A) = +0.031 [-0.025, 0.088]

Reading: under both distortion levels the ZNCC success@5 lead over DS R1 stays at about +0.07. The interaction contrasts include 0, so the distortion does not separate the two methods' advantage from the undistorted advantage.

Caveat, important for interpretation: the frozen ZNCC rule accepts about 99% of cross-layer absent pairs (no rejection). Its success@5 is therefore a localisation score, not a decision score. Its success@1 falls from 0.978 (undistorted) to 0.516 (mid) and 0.309 (high). DS R1 rejects about 88-90% of absent pairs. The two rules are not comparable on the decision side.

Other metrics (wrong repeats, median error, accepted-decision error, F1, loc-only@5, DS R3 gate) are in results/e18/eval_e18.json under levels.{mid,high,undistorted}.

Freeze and distortion checks: each kernel's base freeze check reports PASS (961 files, 0 missing, 0 extra, 0 hash mismatch). The "freeze_real missing from summary" failure was a name mismatch in the kernel's REQUIRED list (the step is recorded as freeze_check_real), not a failed check. The REQUIRED entry was removed locally (not re-pushed). The distorted-set sha256 check passed for all four levels.
