# IRIS report

95% percentile cluster bootstrap; thresholds fixed; rates are fractions. Missing poses count as infinite error and fail all tolerance checks. Empty denominators and single-class AUCs are NaN; zero-division rejection scores are 0. Undefined bootstrap replicates are excluded; valid replicate counts are in JSON. JSON null means NaN; Infinity strings mean unbounded error.

Bootstrap: 2000; seed: 20261010; clusters: 400.

Threshold noexit: 0.2617101; explicit fixed threshold; selection provenance unknown.

## Counts

| Metric | noexit | evt | logistic |
| --- | --- | --- | --- |
| n_present | 323 [308, 338] | 323 [308, 338] | 323 [308, 338] |
| n_absent | 77 [62, 92] | 77 [62, 92] | 77 [62, 92] |

## Localisation

| Metric | noexit | evt | logistic |
| --- | --- | --- | --- |
| success@1 | 0.706 [0.658, 0.757] | 0.375 [0.325, 0.427] | 0.672 [0.62, 0.723] |
| loc_only@1 | 0.712 [0.664, 0.763] | 0.712 [0.664, 0.763] | 0.712 [0.664, 0.763] |
| success@3 | 0.885 [0.851, 0.92] | 0.471 [0.415, 0.524] | 0.848 [0.808, 0.886] |
| loc_only@3 | 0.895 [0.86, 0.927] | 0.895 [0.86, 0.927] | 0.895 [0.86, 0.927] |
| success@5 | 0.913 [0.883, 0.942] | 0.486 [0.432, 0.54] | 0.87 [0.831, 0.906] |
| loc_only@5 | 0.923 [0.892, 0.95] | 0.923 [0.892, 0.95] | 0.923 [0.892, 0.95] |
| gross_rate | 0.0681 [0.0423, 0.096] | 0.0681 [0.0423, 0.096] | 0.0681 [0.0423, 0.096] |
| err_px_p50 | 0.468 [0.418, 0.549] | 0.468 [0.418, 0.549] | 0.468 [0.418, 0.549] |
| err_px_p90 | 3.45 [2.02, 7.33] | 3.45 [2.02, 7.33] | 3.45 [2.02, 7.33] |
| err_px_p95 | 128 [5.15, 315] | 128 [5.15, 315] | 128 [5.15, 315] |

## Scale and rotation

| Metric | noexit | evt | logistic |
| --- | --- | --- | --- |
| pose_all_n | 323 [308, 338] | 323 [308, 338] | 323 [308, 338] |
| scale_pct_all_median | 0.593 [0.502, 0.757] | 0.593 [0.502, 0.757] | 0.593 [0.502, 0.757] |
| scale_pct_all_p90 | 2.37 [2.09, 2.83] | 2.37 [2.09, 2.83] | 2.37 [2.09, 2.83] |
| scale_pct_all_within1 | 0.622 [0.57, 0.676] | 0.622 [0.57, 0.676] | 0.622 [0.57, 0.676] |
| scale_pct_all_within2 | 0.858 [0.819, 0.895] | 0.858 [0.819, 0.895] | 0.858 [0.819, 0.895] |
| scale_pct_all_within5 | 0.966 [0.946, 0.984] | 0.966 [0.946, 0.984] | 0.966 [0.946, 0.984] |
| rotation_deg_all_median | 0.147 [0.127, 0.175] | 0.147 [0.127, 0.175] | 0.147 [0.127, 0.175] |
| rotation_deg_all_p90 | 0.539 [0.485, 0.639] | 0.539 [0.485, 0.639] | 0.539 [0.485, 0.639] |
| rotation_deg_all_within0.25 | 0.693 [0.645, 0.744] | 0.693 [0.645, 0.744] | 0.693 [0.645, 0.744] |
| rotation_deg_all_within0.5 | 0.87 [0.833, 0.905] | 0.87 [0.833, 0.905] | 0.87 [0.833, 0.905] |
| rotation_deg_all_within1 | 0.981 [0.966, 0.994] | 0.981 [0.966, 0.994] | 0.981 [0.966, 0.994] |
| pose_within5_n | 295 [278, 312] | 157 [138, 176] | 281 [263, 298] |
| scale_pct_within5_median | 0.565 [0.485, 0.68] | 0.593 [0.497, 0.789] | 0.565 [0.481, 0.679] |
| scale_pct_within5_p90 | 2.18 [1.87, 2.36] | 2.18 [1.86, 2.69] | 2.15 [1.86, 2.34] |
| scale_pct_within5_within1 | 0.644 [0.592, 0.701] | 0.631 [0.556, 0.706] | 0.648 [0.595, 0.705] |
| scale_pct_within5_within2 | 0.885 [0.847, 0.921] | 0.879 [0.824, 0.928] | 0.886 [0.849, 0.923] |
| scale_pct_within5_within5 | 1 [1, 1] | 1 [1, 1] | 1 [1, 1] |
| rotation_deg_within5_median | 0.143 [0.122, 0.168] | 0.142 [0.109, 0.167] | 0.137 [0.115, 0.153] |
| rotation_deg_within5_p90 | 0.522 [0.468, 0.616] | 0.562 [0.472, 0.706] | 0.526 [0.471, 0.627] |
| rotation_deg_within5_within0.25 | 0.715 [0.666, 0.765] | 0.732 [0.665, 0.801] | 0.712 [0.661, 0.765] |
| rotation_deg_within5_within0.5 | 0.885 [0.847, 0.921] | 0.866 [0.814, 0.919] | 0.883 [0.843, 0.919] |
| rotation_deg_within5_within1 | 0.986 [0.973, 0.997] | 0.987 [0.967, 1] | 0.986 [0.971, 0.997] |

## Rejection and AUC

| Metric | noexit | evt | logistic |
| --- | --- | --- | --- |
| absent_accepted | 9 [4, 15] | 2 [0, 5] | 2 [0, 5] |
| present_declined | 9 [4, 15] | 164 [145, 183] | 31 [21, 42] |
| absent_declined | 68 [53, 82] | 75 [60, 90] | 75 [60, 90] |
| precision | 0.883 [0.805, 0.947] | 0.314 [0.255, 0.372] | 0.708 [0.613, 0.791] |
| recall | 0.883 [0.809, 0.949] | 0.974 [0.932, 1] | 0.974 [0.931, 1] |
| F1 | 0.883 [0.825, 0.933] | 0.475 [0.404, 0.54] | 0.82 [0.748, 0.876] |
| auroc_present | 0.986 [0.976, 0.995] | 0.862 [0.818, 0.901] | 0.951 [0.929, 0.971] |
| correct_match_auc | 0.975 [0.96, 0.988] | 0.862 [0.821, 0.9] | 0.946 [0.919, 0.969] |

## Runtime

| Metric | noexit | evt | logistic |
| --- | --- | --- | --- |
| runtime_median | 8.88 [8.77, 9.05] | 8.88 [8.77, 9.05] | 8.88 [8.77, 9.05] |
| runtime_p90 | 10.1 [9.92, 10.2] | 10.1 [9.92, 10.2] | 10.1 [9.92, 10.2] |
| runtime_p95 | 10.4 [10.2, 10.6] | 10.4 [10.2, 10.6] | 10.4 [10.2, 10.6] |
| runtime_max | 11.2 [11, 11.2] | 11.2 [11, 11.2] | 11.2 [11, 11.2] |

## Strata: noexit

### sev_q1

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 86 [70, 102] |
| success@1 | 0.953 [0.901, 0.989] |
| success@3 | 1 [1, 1] |
| success@5 | 1 [1, 1] |
| gross_rate | 0 [0, 0] |
| err_px_p50 | 0.25 [0.208, 0.29] |

### sev_q2

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 75 [60, 91] |
| success@1 | 0.813 [0.718, 0.897] |
| success@3 | 0.973 [0.932, 1] |
| success@5 | 0.987 [0.958, 1] |
| gross_rate | 0.0133 [0, 0.0417] |
| err_px_p50 | 0.458 [0.366, 0.594] |

### sev_q3

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 85 [69, 101] |
| success@1 | 0.588 [0.478, 0.691] |
| success@3 | 0.859 [0.785, 0.927] |
| success@5 | 0.894 [0.825, 0.955] |
| gross_rate | 0.0706 [0.0225, 0.128] |
| err_px_p50 | 0.678 [0.499, 1.01] |

### sev_q4

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 77 [62, 93] |
| success@1 | 0.455 [0.341, 0.563] |
| success@3 | 0.701 [0.595, 0.797] |
| success@5 | 0.766 [0.671, 0.857] |
| gross_rate | 0.195 [0.113, 0.286] |
| err_px_p50 | 1.33 [0.826, 1.64] |

### absent

| Metric | Value [95% CI] |
| --- | --- |
| n_absent | 77 [62, 92] |
| absent_accepted | 9 [4, 15] |
| absent_declined | 68 [53, 82] |

## Strata: evt

### sev_q1

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 86 [70, 102] |
| success@1 | 0.5 [0.4, 0.605] |
| success@3 | 0.535 [0.429, 0.639] |
| success@5 | 0.535 [0.429, 0.639] |
| gross_rate | 0 [0, 0] |
| err_px_p50 | 0.25 [0.208, 0.29] |

### sev_q2

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 75 [60, 91] |
| success@1 | 0.48 [0.364, 0.595] |
| success@3 | 0.56 [0.444, 0.675] |
| success@5 | 0.573 [0.459, 0.688] |
| gross_rate | 0.0133 [0, 0.0417] |
| err_px_p50 | 0.458 [0.366, 0.594] |

### sev_q3

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 85 [69, 101] |
| success@1 | 0.318 [0.222, 0.418] |
| success@3 | 0.471 [0.366, 0.58] |
| success@5 | 0.482 [0.378, 0.59] |
| gross_rate | 0.0706 [0.0225, 0.128] |
| err_px_p50 | 0.678 [0.499, 1.01] |

### sev_q4

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 77 [62, 93] |
| success@1 | 0.195 [0.111, 0.289] |
| success@3 | 0.312 [0.213, 0.419] |
| success@5 | 0.351 [0.244, 0.462] |
| gross_rate | 0.195 [0.113, 0.286] |
| err_px_p50 | 1.33 [0.826, 1.64] |

### absent

| Metric | Value [95% CI] |
| --- | --- |
| n_absent | 77 [62, 92] |
| absent_accepted | 2 [0, 5] |
| absent_declined | 75 [60, 90] |

## Strata: logistic

### sev_q1

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 86 [70, 102] |
| success@1 | 0.93 [0.871, 0.978] |
| success@3 | 0.965 [0.924, 1] |
| success@5 | 0.965 [0.924, 1] |
| gross_rate | 0 [0, 0] |
| err_px_p50 | 0.25 [0.208, 0.29] |

### sev_q2

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 75 [60, 91] |
| success@1 | 0.787 [0.688, 0.873] |
| success@3 | 0.947 [0.892, 0.988] |
| success@5 | 0.947 [0.892, 0.988] |
| gross_rate | 0.0133 [0, 0.0417] |
| err_px_p50 | 0.458 [0.366, 0.594] |

### sev_q3

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 85 [69, 101] |
| success@1 | 0.529 [0.424, 0.634] |
| success@3 | 0.788 [0.7, 0.87] |
| success@5 | 0.824 [0.737, 0.899] |
| gross_rate | 0.0706 [0.0225, 0.128] |
| err_px_p50 | 0.678 [0.499, 1.01] |

### sev_q4

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 77 [62, 93] |
| success@1 | 0.429 [0.318, 0.539] |
| success@3 | 0.688 [0.583, 0.79] |
| success@5 | 0.74 [0.64, 0.833] |
| gross_rate | 0.195 [0.113, 0.286] |
| err_px_p50 | 1.33 [0.826, 1.64] |

### absent

| Metric | Value [95% CI] |
| --- | --- |
| n_absent | 77 [62, 92] |
| absent_accepted | 2 [0, 5] |
| absent_declined | 75 [60, 90] |

## Paired differences against noexit

### evt minus noexit

| Metric | Difference [95% CI] |
| --- | --- |
| success@1 | -0.331 [-0.382, -0.279] |
| success@3 | -0.415 [-0.466, -0.362] |
| success@5 | -0.427 [-0.478, -0.376] |
| F1 | -0.408 [-0.483, -0.333] |
| err_px_p50 | 0 [0, 0] |

### logistic minus noexit

| Metric | Difference [95% CI] |
| --- | --- |
| success@1 | -0.0341 [-0.0545, -0.0153] |
| success@3 | -0.0372 [-0.0604, -0.0157] |
| success@5 | -0.0433 [-0.0687, -0.0211] |
| F1 | -0.0634 [-0.126, -0.00402] |
| err_px_p50 | 0 [0, 0] |
