# IRIS report

95% percentile cluster bootstrap; thresholds fixed; rates are fractions. Missing poses count as infinite error and fail all tolerance checks. Empty denominators and single-class AUCs are NaN; zero-division rejection scores are 0. Undefined bootstrap replicates are excluded; valid replicate counts are in JSON. JSON null means NaN; Infinity strings mean unbounded error.

Bootstrap: 2000; seed: 20261010; clusters: 600.

Threshold qatm: 0.53346806764602661; chosen on disjoint dev labels.

## Counts

| Metric | qatm |
| --- | --- |
| n_present | 478 [459, 497] |
| n_absent | 122 [103, 141] |

## Localisation

| Metric | qatm |
| --- | --- |
| success@1 | 0 [0, 0] |
| loc_only@1 | 0 [0, 0] |
| success@3 | 0.00209 [0, 0.00654] |
| loc_only@3 | 0.00209 [0, 0.00654] |
| success@5 | 0.00418 [0, 0.0106] |
| loc_only@5 | 0.00418 [0, 0.0106] |
| gross_rate | 0.987 [0.977, 0.996] |
| err_px_p50 | 670 [633, 714] |
| err_px_p90 | 974 [954, 1e+03] |
| err_px_p95 | 1.05e+03 [1.01e+03, 1.08e+03] |

## Scale and rotation

| Metric | qatm |
| --- | --- |
| pose_all_n | 478 [459, 497] |
| scale_pct_all_median | 12.2 [9.86, 14.1] |
| scale_pct_all_p90 | 27.9 [26.6, 30.1] |
| scale_pct_all_within1 | 0.259 [0.222, 0.299] |
| scale_pct_all_within2 | 0.366 [0.322, 0.411] |
| scale_pct_all_within5 | 0.418 [0.374, 0.465] |
| rotation_deg_all_median | 0.238 [0.203, 0.273] |
| rotation_deg_all_p90 | 1.07 [0.904, 1.27] |
| rotation_deg_all_within0.25 | 0.519 [0.474, 0.564] |
| rotation_deg_all_within0.5 | 0.728 [0.69, 0.767] |
| rotation_deg_all_within1 | 0.891 [0.863, 0.917] |
| pose_within5_n | 2 [0, 5] |
| scale_pct_within5_median | 0.386 [0.343, 0.429] |
| scale_pct_within5_p90 | 0.42 [0.343, 0.429] |
| scale_pct_within5_within1 | 1 [1, 1] |
| scale_pct_within5_within2 | 1 [1, 1] |
| scale_pct_within5_within5 | 1 [1, 1] |
| rotation_deg_within5_median | 0.227 [0.103, 0.35] |
| rotation_deg_within5_p90 | 0.326 [0.103, 0.35] |
| rotation_deg_within5_within0.25 | 0.5 [0, 1] |
| rotation_deg_within5_within0.5 | 1 [1, 1] |
| rotation_deg_within5_within1 | 1 [1, 1] |

## Rejection and AUC

| Metric | qatm |
| --- | --- |
| absent_accepted | 51 [38, 64] |
| present_declined | 283 [259, 308] |
| absent_declined | 71 [56, 87] |
| precision | 0.201 [0.16, 0.245] |
| recall | 0.582 [0.496, 0.667] |
| F1 | 0.298 [0.244, 0.352] |
| auroc_present | 0.489 [0.433, 0.549] |
| correct_match_auc | 0.79 [0.653, 0.92] |

## Runtime

| Metric | qatm |
| --- | --- |
| runtime_median | 1.48 [1.47, 1.49] |
| runtime_p90 | 1.59 [1.58, 1.6] |
| runtime_p95 | 1.63 [1.6, 1.64] |
| runtime_max | 1.7 [1.68, 1.7] |

## Strata: qatm

### sev_q1

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 108 [90, 127] |
| success@1 | 0 [0, 0] |
| success@3 | 0 [0, 0] |
| success@5 | 0.00926 [0, 0.0312] |
| gross_rate | 0.991 [0.969, 1] |
| err_px_p50 | 636 [586, 750] |

### sev_q2

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 128 [109, 148] |
| success@1 | 0 [0, 0] |
| success@3 | 0 [0, 0] |
| success@5 | 0 [0, 0] |
| gross_rate | 0.984 [0.958, 1] |
| err_px_p50 | 663 [576, 724] |

### sev_q3

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 127 [108, 147] |
| success@1 | 0 [0, 0] |
| success@3 | 0.00787 [0, 0.027] |
| success@5 | 0.00787 [0, 0.027] |
| gross_rate | 0.984 [0.959, 1] |
| err_px_p50 | 683 [625, 789] |

### sev_q4

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 115 [96, 134] |
| success@1 | 0 [0, 0] |
| success@3 | 0 [0, 0] |
| success@5 | 0 [0, 0] |
| gross_rate | 0.991 [0.97, 1] |
| err_px_p50 | 677 [603, 751] |

### absent

| Metric | Value [95% CI] |
| --- | --- |
| n_absent | 122 [103, 141] |
| absent_accepted | 51 [38, 64] |
| absent_declined | 71 [56, 87] |
