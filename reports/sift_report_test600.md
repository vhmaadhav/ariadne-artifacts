# IRIS report

95% percentile cluster bootstrap; thresholds fixed; rates are fractions. Missing poses count as infinite error and fail all tolerance checks. Empty denominators and single-class AUCs are NaN; zero-division rejection scores are 0. Undefined bootstrap replicates are excluded; valid replicate counts are in JSON. JSON null means NaN; Infinity strings mean unbounded error.

Bootstrap: 2000; seed: 20261010; clusters: 600.

## Counts

| Metric | sift_ransac_tuned | sift_lightglue_tuned |
| --- | --- | --- |
| n_present | 478 [459, 497] | 478 [459, 497] |
| n_absent | 122 [103, 141] | 122 [103, 141] |

## Localisation

| Metric | sift_ransac_tuned | sift_lightglue_tuned |
| --- | --- | --- |
| success@1 | 0.0628 [0.0418, 0.0837] | 0 [0, 0] |
| loc_only@1 | 0.0628 [0.0418, 0.0837] | 0 [0, 0] |
| success@3 | 0.0879 [0.0632, 0.114] | 0 [0, 0] |
| loc_only@3 | 0.0879 [0.0632, 0.114] | 0 [0, 0] |
| success@5 | 0.09 [0.0647, 0.116] | 0 [0, 0] |
| loc_only@5 | 0.09 [0.0647, 0.116] | 0 [0, 0] |
| gross_rate | 0.904 [0.877, 0.93] | 0.998 [0.994, 1] |
| err_px_p50 | 478 [436, 526] | inf [inf, inf] |
| err_px_p90 | 979 [929, 1.09e+03] | inf [inf, inf] |
| err_px_p95 | 1.29e+03 [1.09e+03, 1.75e+03] | inf [inf, inf] |

## Scale and rotation

| Metric | sift_ransac_tuned | sift_lightglue_tuned |
| --- | --- | --- |
| pose_all_n | 478 [459, 497] | 478 [459, 497] |
| scale_pct_all_median | 68.6 [60.6, 75.1] | inf [inf, inf] |
| scale_pct_all_p90 | 96.2 [95.7, 97.4] | inf [inf, inf] |
| scale_pct_all_within1 | 0.0711 [0.0485, 0.095] | 0 [0, 0] |
| scale_pct_all_within2 | 0.103 [0.0761, 0.129] | 0 [0, 0] |
| scale_pct_all_within5 | 0.134 [0.104, 0.165] | 0 [0, 0] |
| rotation_deg_all_median | 69 [58.5, 85.3] | inf [inf, inf] |
| rotation_deg_all_p90 | 179 [179, 179] | inf [inf, inf] |
| rotation_deg_all_within0.25 | 0.0983 [0.0723, 0.126] | 0 [0, 0] |
| rotation_deg_all_within0.5 | 0.134 [0.105, 0.165] | 0 [0, 0] |
| rotation_deg_all_within1 | 0.197 [0.161, 0.234] | 0.00418 [0, 0.0105] |
| pose_within5_n | 43 [31, 56] | 0 [0, 0] |
| scale_pct_within5_median | 0.805 [0.532, 1.28] | nan [nan, nan] |
| scale_pct_within5_p90 | 2.94 [1.92, 4.41] | nan [nan, nan] |
| scale_pct_within5_within1 | 0.605 [0.455, 0.75] | nan [nan, nan] |
| scale_pct_within5_within2 | 0.791 [0.667, 0.903] | nan [nan, nan] |
| scale_pct_within5_within5 | 1 [1, 1] | nan [nan, nan] |
| rotation_deg_within5_median | 0.24 [0.177, 0.39] | nan [nan, nan] |
| rotation_deg_within5_p90 | 1.06 [0.839, 1.65] | nan [nan, nan] |
| rotation_deg_within5_within0.25 | 0.512 [0.361, 0.658] | nan [nan, nan] |
| rotation_deg_within5_within0.5 | 0.698 [0.553, 0.828] | nan [nan, nan] |
| rotation_deg_within5_within1 | 0.86 [0.75, 0.955] | nan [nan, nan] |

## Rejection and AUC

| Metric | sift_ransac_tuned | sift_lightglue_tuned |
| --- | --- | --- |
| absent_accepted | 122 [103, 141] | 18 [10, 26] |
| present_declined | 0 [0, 0] | 383 [359, 404] |
| absent_declined | 0 [0, 0] | 104 [86, 122] |
| precision | 0 [0, 0] | 0.214 [0.177, 0.252] |
| recall | 0 [0, 0] | 0.852 [0.788, 0.915] |
| F1 | 0 [0, 0] | 0.342 [0.291, 0.391] |
| auroc_present | 0.559 [0.542, 0.576] | 0.5 [0.5, 0.5] |
| correct_match_auc | 0.958 [0.913, 0.993] | nan [nan, nan] |

## Runtime

| Metric | sift_ransac_tuned | sift_lightglue_tuned |
| --- | --- | --- |
| runtime_median | 18 [17, 18.9] | 2.61 [2.56, 2.66] |
| runtime_p90 | 35 [32.6, 36.9] | 3.59 [3.47, 3.79] |
| runtime_p95 | 39.8 [37.6, 42.4] | 4.24 [3.9, 4.65] |
| runtime_max | 66.7 [65.6, 66.7] | 10.4 [7.2, 10.4] |

## Strata: sift_ransac_tuned

### sev_q1

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 108 [90, 127] |
| success@1 | 0.185 [0.113, 0.26] |
| success@3 | 0.204 [0.129, 0.281] |
| success@5 | 0.204 [0.129, 0.281] |
| gross_rate | 0.787 [0.707, 0.862] |
| err_px_p50 | 463 [350, 548] |

### sev_q2

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 128 [109, 148] |
| success@1 | 0.0703 [0.0296, 0.118] |
| success@3 | 0.102 [0.0531, 0.154] |
| success@5 | 0.102 [0.0531, 0.154] |
| gross_rate | 0.891 [0.833, 0.941] |
| err_px_p50 | 517 [435, 580] |

### sev_q3

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 127 [108, 147] |
| success@1 | 0.00787 [0, 0.027] |
| success@3 | 0.0236 [0, 0.0539] |
| success@5 | 0.0236 [0, 0.0539] |
| gross_rate | 0.969 [0.935, 0.993] |
| err_px_p50 | 432 [404, 527] |

### sev_q4

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 115 [96, 134] |
| success@1 | 0 [0, 0] |
| success@3 | 0.0348 [0.00813, 0.0721] |
| success@5 | 0.0435 [0.00926, 0.0849] |
| gross_rate | 0.957 [0.915, 0.991] |
| err_px_p50 | 501 [447, 571] |

### absent

| Metric | Value [95% CI] |
| --- | --- |
| n_absent | 122 [103, 141] |
| absent_accepted | 122 [103, 141] |
| absent_declined | 0 [0, 0] |

## Strata: sift_lightglue_tuned

### sev_q1

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 108 [90, 127] |
| success@1 | 0 [0, 0] |
| success@3 | 0 [0, 0] |
| success@5 | 0 [0, 0] |
| gross_rate | 1 [1, 1] |
| err_px_p50 | inf [inf, inf] |

### sev_q2

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 128 [109, 148] |
| success@1 | 0 [0, 0] |
| success@3 | 0 [0, 0] |
| success@5 | 0 [0, 0] |
| gross_rate | 0.992 [0.975, 1] |
| err_px_p50 | inf [inf, inf] |

### sev_q3

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 127 [108, 147] |
| success@1 | 0 [0, 0] |
| success@3 | 0 [0, 0] |
| success@5 | 0 [0, 0] |
| gross_rate | 1 [1, 1] |
| err_px_p50 | inf [inf, inf] |

### sev_q4

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 115 [96, 134] |
| success@1 | 0 [0, 0] |
| success@3 | 0 [0, 0] |
| success@5 | 0 [0, 0] |
| gross_rate | 1 [1, 1] |
| err_px_p50 | inf [inf, inf] |

### absent

| Metric | Value [95% CI] |
| --- | --- |
| n_absent | 122 [103, 141] |
| absent_accepted | 18 [10, 26] |
| absent_declined | 104 [86, 122] |
