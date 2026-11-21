# IRIS report

95% percentile cluster bootstrap; thresholds fixed; rates are fractions. Missing poses count as infinite error and fail all tolerance checks. Empty denominators and single-class AUCs are NaN; zero-division rejection scores are 0. Undefined bootstrap replicates are excluded; valid replicate counts are in JSON. JSON null means NaN; Infinity strings mean unbounded error.

Bootstrap: 2000; seed: 20261010; clusters: 600.

Threshold loftr: 0.39346934028736658; chosen on disjoint dev labels.

## Counts

| Metric | loftr |
| --- | --- |
| n_present | 478 [459, 497] |
| n_absent | 122 [103, 141] |

## Localisation

| Metric | loftr |
| --- | --- |
| success@1 | 0.0314 [0.0172, 0.0484] |
| loc_only@1 | 0.0335 [0.0189, 0.0508] |
| success@3 | 0.0335 [0.0189, 0.051] |
| loc_only@3 | 0.0544 [0.0357, 0.0763] |
| success@5 | 0.0335 [0.0189, 0.051] |
| loc_only@5 | 0.0586 [0.0388, 0.0812] |
| gross_rate | 0.937 [0.914, 0.958] |
| err_px_p50 | 403 [378, 426] |
| err_px_p90 | 757 [694, 786] |
| err_px_p95 | 859 [792, 902] |

## Scale and rotation

| Metric | loftr |
| --- | --- |
| pose_all_n | 478 [459, 497] |
| scale_pct_all_median | 41 [38.1, 44.8] |
| scale_pct_all_p90 | 88.3 [82.7, 90.4] |
| scale_pct_all_within1 | 0.0628 [0.0419, 0.086] |
| scale_pct_all_within2 | 0.0962 [0.0708, 0.124] |
| scale_pct_all_within5 | 0.167 [0.136, 0.202] |
| rotation_deg_all_median | 1.56 [1.3, 1.99] |
| rotation_deg_all_p90 | 61.3 [32.6, 77] |
| rotation_deg_all_within0.25 | 0.13 [0.101, 0.16] |
| rotation_deg_all_within0.5 | 0.236 [0.199, 0.274] |
| rotation_deg_all_within1 | 0.402 [0.357, 0.446] |
| pose_within5_n | 16 [9, 24] |
| scale_pct_within5_median | 1.17 [0.334, 2.22] |
| scale_pct_within5_p90 | 3.53 [2.03, 4.45] |
| scale_pct_within5_within1 | 0.375 [0.143, 0.632] |
| scale_pct_within5_within2 | 0.625 [0.375, 0.857] |
| scale_pct_within5_within5 | 1 [1, 1] |
| rotation_deg_within5_median | 0.495 [0.31, 0.708] |
| rotation_deg_within5_p90 | 0.98 [0.661, 1.09] |
| rotation_deg_within5_within0.25 | 0.25 [0.0588, 0.471] |
| rotation_deg_within5_within0.5 | 0.5 [0.25, 0.75] |
| rotation_deg_within5_within1 | 0.938 [0.8, 1] |

## Rejection and AUC

| Metric | loftr |
| --- | --- |
| absent_accepted | 4 [1, 8] |
| present_declined | 426 [404, 447] |
| absent_declined | 118 [100, 137] |
| precision | 0.217 [0.183, 0.251] |
| recall | 0.967 [0.933, 0.992] |
| F1 | 0.354 [0.308, 0.399] |
| auroc_present | 0.617 [0.564, 0.666] |
| correct_match_auc | 0.883 [0.818, 0.941] |

## Runtime

| Metric | loftr |
| --- | --- |
| runtime_median | 5.2 [5.2, 5.21] |
| runtime_p90 | 5.27 [5.26, 5.28] |
| runtime_p95 | 5.3 [5.28, 5.31] |
| runtime_max | 5.85 [5.44, 5.85] |

## Strata: loftr

### sev_q1

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 108 [90, 127] |
| success@1 | 0.102 [0.0505, 0.163] |
| success@3 | 0.111 [0.0571, 0.177] |
| success@5 | 0.111 [0.0571, 0.177] |
| gross_rate | 0.843 [0.768, 0.907] |
| err_px_p50 | 329 [288, 394] |

### sev_q2

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 128 [109, 148] |
| success@1 | 0.0312 [0.00714, 0.0643] |
| success@3 | 0.0312 [0.00714, 0.0643] |
| success@5 | 0.0312 [0.00714, 0.0643] |
| gross_rate | 0.93 [0.881, 0.97] |
| err_px_p50 | 398 [348, 438] |

### sev_q3

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 127 [108, 147] |
| success@1 | 0 [0, 0] |
| success@3 | 0 [0, 0] |
| success@5 | 0 [0, 0] |
| gross_rate | 0.984 [0.959, 1] |
| err_px_p50 | 412 [361, 449] |

### sev_q4

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 115 [96, 134] |
| success@1 | 0 [0, 0] |
| success@3 | 0 [0, 0] |
| success@5 | 0 [0, 0] |
| gross_rate | 0.983 [0.953, 1] |
| err_px_p50 | 455 [393, 501] |

### absent

| Metric | Value [95% CI] |
| --- | --- |
| n_absent | 122 [103, 141] |
| absent_accepted | 4 [1, 8] |
| absent_declined | 118 [100, 137] |
