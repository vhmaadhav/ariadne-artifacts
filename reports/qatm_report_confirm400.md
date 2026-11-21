# IRIS report

95% percentile cluster bootstrap; thresholds fixed; rates are fractions. Missing poses count as infinite error and fail all tolerance checks. Empty denominators and single-class AUCs are NaN; zero-division rejection scores are 0. Undefined bootstrap replicates are excluded; valid replicate counts are in JSON. JSON null means NaN; Infinity strings mean unbounded error.

Bootstrap: 2000; seed: 20261010; clusters: 400.

Threshold qatm: 0.53346806764602661; chosen on disjoint dev labels.

## Counts

| Metric | qatm |
| --- | --- |
| n_present | 323 [308, 338] |
| n_absent | 77 [62, 92] |

## Localisation

| Metric | qatm |
| --- | --- |
| success@1 | 0 [0, 0] |
| loc_only@1 | 0 [0, 0] |
| success@3 | 0.0031 [0, 0.00952] |
| loc_only@3 | 0.0031 [0, 0.00952] |
| success@5 | 0.0031 [0, 0.00952] |
| loc_only@5 | 0.00619 [0, 0.0159] |
| gross_rate | 0.988 [0.974, 0.997] |
| err_px_p50 | 635 [574, 677] |
| err_px_p90 | 942 [915, 998] |
| err_px_p95 | 1.02e+03 [989, 1.07e+03] |

## Scale and rotation

| Metric | qatm |
| --- | --- |
| pose_all_n | 323 [308, 338] |
| scale_pct_all_median | 8.51 [3.5, 13.2] |
| scale_pct_all_p90 | 30 [26.7, 32.9] |
| scale_pct_all_within1 | 0.269 [0.222, 0.318] |
| scale_pct_all_within2 | 0.39 [0.337, 0.445] |
| scale_pct_all_within5 | 0.471 [0.417, 0.525] |
| rotation_deg_all_median | 0.206 [0.167, 0.247] |
| rotation_deg_all_p90 | 1.41 [0.914, 2.03] |
| rotation_deg_all_within0.25 | 0.554 [0.501, 0.608] |
| rotation_deg_all_within0.5 | 0.74 [0.693, 0.785] |
| rotation_deg_all_within1 | 0.87 [0.833, 0.907] |
| pose_within5_n | 1 [0, 3] |
| scale_pct_within5_median | 0.121 [0.121, 0.121] |
| scale_pct_within5_p90 | 0.121 [0.121, 0.121] |
| scale_pct_within5_within1 | 1 [1, 1] |
| scale_pct_within5_within2 | 1 [1, 1] |
| scale_pct_within5_within5 | 1 [1, 1] |
| rotation_deg_within5_median | 0.0367 [0.0367, 0.0367] |
| rotation_deg_within5_p90 | 0.0367 [0.0367, 0.0367] |
| rotation_deg_within5_within0.25 | 1 [1, 1] |
| rotation_deg_within5_within0.5 | 1 [1, 1] |
| rotation_deg_within5_within1 | 1 [1, 1] |

## Rejection and AUC

| Metric | qatm |
| --- | --- |
| absent_accepted | 28 [18, 38] |
| present_declined | 204 [185, 223] |
| absent_declined | 49 [37, 62] |
| precision | 0.194 [0.148, 0.243] |
| recall | 0.636 [0.532, 0.747] |
| F1 | 0.297 [0.235, 0.362] |
| auroc_present | 0.504 [0.431, 0.578] |
| correct_match_auc | 0.639 [0.308, 0.955] |

## Runtime

| Metric | qatm |
| --- | --- |
| runtime_median | 1.49 [1.47, 1.5] |
| runtime_p90 | 1.61 [1.59, 1.62] |
| runtime_p95 | 1.65 [1.62, 1.66] |
| runtime_max | 1.84 [1.73, 1.84] |

## Strata: qatm

### sev_q1

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 86 [70, 102] |
| success@1 | 0 [0, 0] |
| success@3 | 0 [0, 0] |
| success@5 | 0 [0, 0] |
| gross_rate | 0.965 [0.92, 1] |
| err_px_p50 | 622 [536, 725] |

### sev_q2

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 75 [60, 91] |
| success@1 | 0 [0, 0] |
| success@3 | 0.0133 [0, 0.0448] |
| success@5 | 0.0133 [0, 0.0448] |
| gross_rate | 0.987 [0.955, 1] |
| err_px_p50 | 648 [522, 722] |

### sev_q3

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 85 [69, 101] |
| success@1 | 0 [0, 0] |
| success@3 | 0 [0, 0] |
| success@5 | 0 [0, 0] |
| gross_rate | 1 [1, 1] |
| err_px_p50 | 652 [531, 745] |

### sev_q4

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 77 [62, 93] |
| success@1 | 0 [0, 0] |
| success@3 | 0 [0, 0] |
| success@5 | 0 [0, 0] |
| gross_rate | 1 [1, 1] |
| err_px_p50 | 605 [509, 684] |

### absent

| Metric | Value [95% CI] |
| --- | --- |
| n_absent | 77 [62, 92] |
| absent_accepted | 28 [18, 38] |
| absent_declined | 49 [37, 62] |
