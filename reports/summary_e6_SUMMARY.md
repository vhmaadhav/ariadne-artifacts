# E6: calibrated acceptance (logistic, EVT) vs the min rule

Fitted on dev only. Rules fixed in `results/e6/RULE.txt` before any test, real or confirmation run.
- **Min rule:** noexit score at tau = 0.2617101 (dev threshold, as in E2). Reproduces E2 Drift-Sense test success@5 0.895 [0.867, 0.922].
- **Logistic** (`code/logistic_accept.py`, L2 lam 1.0, 5 features): threshold 0.4539 by F1 on dev out-of-fold scores (dev OOF AUROC 0.969). 2 dev rows with undefined features dropped from the fit.
- **EVT** (`code/evt_accept.py`): threshold -0.2075 at the 5% accepted-error target, calibrated on dev.

Definitions. Accepted = score at or above the rule's threshold. Wrong accepted = accepted and not (present and centre error at most 5 px). Accepted-decision error = wrong accepted / accepted. Success@5 and F1 as in `iris_report`. Wrong-repeat rate = `gross_rate` (present pairs with error above 20 px, over all pairs). AURC = mean over k of the risk among the top-k pairs ranked by score (lower is better). The paired differences use the same cluster-bootstrap draws for all rules (2000 draws, seed 20261010, percentile intervals as in `iris_report`). `iris_report` only reports paired differences for success and F1, so accepted-decision error differences were computed by `results/e6/e6_analysis.py` with the same draws.

Note: the `found` column in the E4 prediction files uses the shipped 0.55 decision and differs from tau on 75 to 92 pairs per split. All min-rule numbers here apply tau = 0.2617 to the score, as the report does.

## Confirmation set (pre-registered decision set; 400 pairs, 323 present, 77 absent)

| Rule | success@1 | success@3 | success@5 [95% CI] | accepted-decision error [CI] | wrong accepted | absent accepted (of 77) | present declined (of 323) | F1 | presence AUROC | AURC |
|---|---|---|---|---|---|---|---|---|---|---|
| Min rule (noexit, tau 0.2617) | 0.706 | 0.885 | **0.913** [0.883, 0.942] | 0.087 [0.057, 0.118] | 28/323 | 9 | 9 | 0.883 [0.825, 0.933] | 0.986 [0.976, 0.995] | **0.043** |
| Logistic (f1) | 0.672 | 0.848 | 0.870 [0.831, 0.906] | 0.044 [0.023, 0.070] | 13/294 | 2 | 31 | 0.820 [0.748, 0.876] | 0.951 [0.929, 0.971] | 0.050 |
| EVT (err, 5%) | 0.375 | 0.471 | 0.486 [0.432, 0.540] | 0.025 [0.006, 0.052] | 4/161 | 2 | 164 | 0.475 [0.404, 0.540] | 0.862 [0.818, 0.901] | 0.078 |

Wrong-repeat rate (min rule) 0.068 [0.042, 0.096].

Paired difference vs the min rule (confirmation):
- Logistic: success@5 -0.043 [-0.069, -0.021]; accepted-decision error -0.043 [-0.065, -0.022].
- EVT: success@5 -0.427 [-0.478, -0.376]; accepted-decision error -0.062 [-0.095, -0.028].

**Verdict (pre-registered): neither rule beats the min rule on the confirmation set.**
- Logistic lowers accepted-decision error (0.087 to 0.044) but lowers success@5 by 4.3 points, more than the 1-point limit.
- EVT lowers accepted-decision error to 0.025 but declines 164 of 323 present pairs, so success@5 falls by 42.7 points.
- The min rule also has the lowest AURC on confirmation.

## Test (600 pairs, 478 present, 122 absent; dev rules applied unchanged)

| Rule | success@5 [CI] | accepted-decision error [CI] | wrong accepted | absent accepted (of 122) | present declined (of 478) | F1 | presence AUROC | AURC |
|---|---|---|---|---|---|---|---|---|
| Min rule | 0.895 [0.867, 0.922] | 0.066 [0.045, 0.091] | 30/458 | 9 | 29 | 0.856 | 0.978 | 0.051 |
| Logistic | 0.843 [0.809, 0.875] | 0.041 [0.023, 0.061] | 17/420 | 2 | 60 | 0.795 | 0.949 | 0.053 |
| EVT | 0.481 [0.436, 0.526] | 0.061 [0.032, 0.092] | 15/245 | 11 | 244 | 0.465 | 0.830 | 0.097 |

Paired vs min: logistic success@5 -0.052 [-0.074, -0.030], error -0.025 [-0.044, -0.009]; EVT success@5 -0.414 [-0.461, -0.370], error -0.004 [-0.039, 0.028].

## Real (800 pairs, 640 present, 160 absent; reported only, not used to choose a rule)

| Rule | success@5 [CI] | accepted-decision error [CI] | wrong accepted | absent accepted (of 160) | present declined (of 640) | F1 | presence AUROC | AURC |
|---|---|---|---|---|---|---|---|---|
| Min rule | 0.908 [0.873, 0.938] | 0.075 [0.053, 0.099] | 47/628 | 10 | 22 | 0.904 | 0.985 | 0.061 |
| Logistic | 0.644 [0.602, 0.684] | 0.078 [0.052, 0.107] | 35/447 | 4 | 197 | 0.608 | 0.727 | 0.124 |
| EVT | 0.909 [0.878, 0.938] | 0.038 [0.023, 0.053] | 23/605 | 3 | 38 | 0.885 | 0.981 | 0.045 |

Paired vs min: logistic success@5 -0.264 [-0.303, -0.227], error +0.004 [-0.012, 0.017]; EVT success@5 +0.002 [-0.003, 0.008], error -0.037 [-0.057, -0.020].

EVT meets the criterion on real (no loss of success@5, lower error) but not on confirmation, and it loses 41 points on test. The real-set gain does not replicate on the confirmation set, so it is not counted as support for EVT.

## Risk-coverage and AURC

Curves for all rules and splits: `results/e6/riskcoverage_all_splits.csv` (columns split, method, k, coverage, risk). AURC values are in the tables above. The min rule has the lowest AURC on test and confirmation. EVT has the lowest on real (0.045).

## Caveats
- The EVT accepted-error target did not transfer: dev target 5%, observed 6.1% on test, 3.8% on real, 2.5% on confirmation.
- Logistic and EVT accept far fewer pairs, so their error drops partly because they decline more present pairs.
- Interval conventions follow `iris_report` (weighted quantiles, 2000 cluster draws). Intervals for differences use the same draws for every rule.

Files: `results/e6/RULE.txt`, `logistic_model.json`, `pred_{test,real,confirm}_{logistic,evt}.csv` (+ `.threshold.json`), `report_{test,real,confirm}.{md,json}` (iris_report output), `e6_metrics.json`, `riskcoverage_all_splits.csv`, `e6_analysis.py`.
