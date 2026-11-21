# IRIS report

95% percentile cluster bootstrap; thresholds fixed; rates are fractions. Missing poses count as infinite error and fail all tolerance checks. Empty denominators and single-class AUCs are NaN; zero-division rejection scores are 0. Undefined bootstrap replicates are excluded; valid replicate counts are in JSON. JSON null means NaN; Infinity strings mean unbounded error.

Bootstrap: 2000; seed: 20261010; clusters: 40.

Threshold shipped: 0.2617101; explicit fixed threshold; selection provenance unknown.

Threshold noexit: 0.2617101; explicit fixed threshold; selection provenance unknown.

## Counts

| Metric | shipped | noexit |
| --- | --- | --- |
| n_present | 640 [640, 640] | 640 [640, 640] |
| n_absent | 160 [160, 160] | 160 [160, 160] |

## Localisation

| Metric | shipped | noexit |
| --- | --- | --- |
| success@1 | 0.869 [0.83, 0.906] | 0.869 [0.83, 0.906] |
| loc_only@1 | 0.872 [0.836, 0.906] | 0.872 [0.836, 0.906] |
| success@3 | 0.9 [0.864, 0.934] | 0.9 [0.864, 0.934] |
| loc_only@3 | 0.903 [0.869, 0.934] | 0.903 [0.869, 0.934] |
| success@5 | 0.908 [0.873, 0.938] | 0.908 [0.873, 0.938] |
| loc_only@5 | 0.911 [0.88, 0.939] | 0.911 [0.88, 0.939] |
| gross_rate | 0.0891 [0.0609, 0.12] | 0.0891 [0.0609, 0.12] |
| err_px_p50 | 0.0915 [0.0736, 0.127] | 0.0915 [0.0736, 0.127] |
| err_px_p90 | 2.07 [0.941, 316] | 2.07 [0.941, 316] |
| err_px_p95 | 432 [258, 626] | 432 [258, 626] |

## Scale and rotation

| Metric | shipped | noexit |
| --- | --- | --- |
| pose_all_n | 640 [640, 640] | 640 [640, 640] |
| scale_pct_all_median | 0.229 [0.196, 0.27] | 0.229 [0.196, 0.27] |
| scale_pct_all_p90 | 1.22 [0.89, 2.22] | 1.22 [0.89, 2.22] |
| scale_pct_all_within1 | 0.875 [0.833, 0.914] | 0.875 [0.833, 0.914] |
| scale_pct_all_within2 | 0.928 [0.895, 0.956] | 0.928 [0.895, 0.956] |
| scale_pct_all_within5 | 0.967 [0.944, 0.986] | 0.967 [0.944, 0.986] |
| rotation_deg_all_median | 0.061 [0.0527, 0.0716] | 0.061 [0.0527, 0.0716] |
| rotation_deg_all_p90 | 0.275 [0.213, 0.361] | 0.275 [0.213, 0.361] |
| rotation_deg_all_within0.25 | 0.887 [0.853, 0.919] | 0.887 [0.853, 0.919] |
| rotation_deg_all_within0.5 | 0.956 [0.936, 0.973] | 0.956 [0.936, 0.973] |
| rotation_deg_all_within1 | 0.984 [0.975, 0.994] | 0.984 [0.975, 0.994] |
| pose_within5_n | 581 [559, 600] | 581 [559, 600] |
| scale_pct_within5_median | 0.206 [0.18, 0.239] | 0.206 [0.18, 0.239] |
| scale_pct_within5_p90 | 0.815 [0.661, 0.977] | 0.815 [0.661, 0.977] |
| scale_pct_within5_within1 | 0.935 [0.907, 0.959] | 0.935 [0.907, 0.959] |
| scale_pct_within5_within2 | 0.985 [0.972, 0.995] | 0.985 [0.972, 0.995] |
| scale_pct_within5_within5 | 0.997 [0.991, 1] | 0.997 [0.991, 1] |
| rotation_deg_within5_median | 0.0539 [0.0485, 0.0619] | 0.0539 [0.0485, 0.0619] |
| rotation_deg_within5_p90 | 0.171 [0.157, 0.219] | 0.171 [0.157, 0.219] |
| rotation_deg_within5_within0.25 | 0.947 [0.927, 0.964] | 0.947 [0.927, 0.964] |
| rotation_deg_within5_within0.5 | 0.991 [0.981, 0.998] | 0.991 [0.981, 0.998] |
| rotation_deg_within5_within1 | 0.997 [0.991, 1] | 0.997 [0.991, 1] |

## Rejection and AUC

| Metric | shipped | noexit |
| --- | --- | --- |
| absent_accepted | 10 [4, 17] | 10 [4, 17] |
| present_declined | 22 [11, 34] | 22 [11, 34] |
| absent_declined | 150 [143, 156] | 150 [143, 156] |
| precision | 0.872 [0.813, 0.931] | 0.872 [0.813, 0.931] |
| recall | 0.938 [0.894, 0.975] | 0.938 [0.894, 0.975] |
| F1 | 0.904 [0.865, 0.941] | 0.904 [0.865, 0.941] |
| auroc_present | 0.985 [0.975, 0.993] | 0.985 [0.975, 0.993] |
| correct_match_auc | 0.963 [0.94, 0.982] | 0.963 [0.94, 0.982] |

## Runtime

| Metric | shipped | noexit |
| --- | --- | --- |
| runtime_median | 5.8 [5.62, 5.95] | 5.96 [5.81, 6.11] |
| runtime_p90 | 8.88 [8.76, 8.94] | 8.97 [8.85, 9.06] |
| runtime_p95 | 9.13 [9.03, 9.31] | 9.3 [9.13, 9.42] |
| runtime_max | 10.3 [10.2, 10.3] | 10.4 [10.2, 10.4] |

## Strata: shipped

### real_A

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 320 [320, 320] |
| success@1 | 0.912 [0.866, 0.95] |
| success@3 | 0.916 [0.869, 0.953] |
| success@5 | 0.916 [0.869, 0.953] |
| gross_rate | 0.0813 [0.0469, 0.122] |
| err_px_p50 | 0.0742 [0.063, 0.0867] |

### real_B

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 320 [320, 320] |
| success@1 | 0.825 [0.772, 0.878] |
| success@3 | 0.884 [0.841, 0.928] |
| success@5 | 0.9 [0.863, 0.938] |
| gross_rate | 0.0969 [0.0625, 0.131] |
| err_px_p50 | 0.14 [0.091, 0.236] |

### absent

| Metric | Value [95% CI] |
| --- | --- |
| n_absent | 160 [160, 160] |
| absent_accepted | 10 [4, 17] |
| absent_declined | 150 [143, 156] |

## Strata: noexit

### real_A

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 320 [320, 320] |
| success@1 | 0.912 [0.866, 0.95] |
| success@3 | 0.916 [0.869, 0.953] |
| success@5 | 0.916 [0.869, 0.953] |
| gross_rate | 0.0813 [0.0469, 0.122] |
| err_px_p50 | 0.0742 [0.063, 0.0867] |

### real_B

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 320 [320, 320] |
| success@1 | 0.825 [0.772, 0.878] |
| success@3 | 0.884 [0.841, 0.928] |
| success@5 | 0.9 [0.863, 0.938] |
| gross_rate | 0.0969 [0.0625, 0.131] |
| err_px_p50 | 0.14 [0.091, 0.236] |

### absent

| Metric | Value [95% CI] |
| --- | --- |
| n_absent | 160 [160, 160] |
| absent_accepted | 10 [4, 17] |
| absent_declined | 150 [143, 156] |

## Paired differences against shipped

### noexit minus shipped

| Metric | Difference [95% CI] |
| --- | --- |
| success@1 | 0 [0, 0] |
| success@3 | 0 [0, 0] |
| success@5 | 0 [0, 0] |
| F1 | 0 [0, 0] |
| err_px_p50 | 0 [0, 0] |
