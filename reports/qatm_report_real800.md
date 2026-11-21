# IRIS report

95% percentile cluster bootstrap; thresholds fixed; rates are fractions. Missing poses count as infinite error and fail all tolerance checks. Empty denominators and single-class AUCs are NaN; zero-division rejection scores are 0. Undefined bootstrap replicates are excluded; valid replicate counts are in JSON. JSON null means NaN; Infinity strings mean unbounded error.

Bootstrap: 2000; seed: 20261010; clusters: 40.

Threshold qatm: 0.53346806764602661; chosen on disjoint dev labels.

## Counts

| Metric | qatm |
| --- | --- |
| n_present | 640 [640, 640] |
| n_absent | 160 [160, 160] |

## Localisation

| Metric | qatm |
| --- | --- |
| success@1 | 0.05 [0.0344, 0.0672] |
| loc_only@1 | 0.0578 [0.0406, 0.075] |
| success@3 | 0.22 [0.188, 0.256] |
| loc_only@3 | 0.264 [0.231, 0.298] |
| success@5 | 0.253 [0.222, 0.287] |
| loc_only@5 | 0.298 [0.266, 0.331] |
| gross_rate | 0.653 [0.617, 0.688] |
| err_px_p50 | 437 [369, 465] |
| err_px_p90 | 846 [831, 869] |
| err_px_p95 | 925 [887, 966] |

## Scale and rotation

| Metric | qatm |
| --- | --- |
| pose_all_n | 640 [640, 640] |
| scale_pct_all_median | 0.568 [0.477, 0.739] |
| scale_pct_all_p90 | 24.8 [23.4, 26.4] |
| scale_pct_all_within1 | 0.591 [0.547, 0.634] |
| scale_pct_all_within2 | 0.661 [0.617, 0.703] |
| scale_pct_all_within5 | 0.725 [0.689, 0.758] |
| rotation_deg_all_median | 0.134 [0.121, 0.157] |
| rotation_deg_all_p90 | 2.43 [2.03, 2.96] |
| rotation_deg_all_within0.25 | 0.641 [0.594, 0.688] |
| rotation_deg_all_within0.5 | 0.73 [0.691, 0.766] |
| rotation_deg_all_within1 | 0.795 [0.758, 0.828] |
| pose_within5_n | 162 [142, 184] |
| scale_pct_within5_median | 0.28 [0.226, 0.383] |
| scale_pct_within5_p90 | 2.81 [1.34, 4.3] |
| scale_pct_within5_within1 | 0.827 [0.77, 0.88] |
| scale_pct_within5_within2 | 0.877 [0.82, 0.927] |
| scale_pct_within5_within5 | 0.938 [0.899, 0.971] |
| rotation_deg_within5_median | 0.0744 [0.0646, 0.105] |
| rotation_deg_within5_p90 | 0.46 [0.291, 0.623] |
| rotation_deg_within5_within0.25 | 0.796 [0.714, 0.872] |
| rotation_deg_within5_within0.5 | 0.907 [0.858, 0.949] |
| rotation_deg_within5_within1 | 0.944 [0.907, 0.976] |

## Rejection and AUC

| Metric | qatm |
| --- | --- |
| absent_accepted | 110 [95, 125] |
| present_declined | 166 [143, 187] |
| absent_declined | 50 [35, 65] |
| precision | 0.231 [0.175, 0.289] |
| recall | 0.312 [0.219, 0.406] |
| F1 | 0.266 [0.197, 0.334] |
| auroc_present | 0.551 [0.493, 0.612] |
| correct_match_auc | 0.645 [0.599, 0.688] |

## Runtime

| Metric | qatm |
| --- | --- |
| runtime_median | 1.14 [1.13, 1.16] |
| runtime_p90 | 1.61 [1.6, 1.62] |
| runtime_p95 | 1.65 [1.63, 1.65] |
| runtime_max | 1.97 [1.72, 1.97] |

## Strata: qatm

### real_A

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 320 [320, 320] |
| success@1 | 0.0563 [0.0344, 0.0781] |
| success@3 | 0.312 [0.256, 0.372] |
| success@5 | 0.362 [0.309, 0.419] |
| gross_rate | 0.537 [0.481, 0.594] |
| err_px_p50 | 253 [11.8, 397] |

### real_B

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 320 [320, 320] |
| success@1 | 0.0437 [0.025, 0.0656] |
| success@3 | 0.128 [0.1, 0.159] |
| success@5 | 0.144 [0.113, 0.175] |
| gross_rate | 0.769 [0.722, 0.816] |
| err_px_p50 | 498 [444, 556] |

### absent

| Metric | Value [95% CI] |
| --- | --- |
| n_absent | 160 [160, 160] |
| absent_accepted | 110 [95, 125] |
| absent_declined | 50 [35, 65] |
