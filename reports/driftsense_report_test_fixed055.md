# IRIS report

95% percentile cluster bootstrap; thresholds fixed; rates are fractions. Missing poses count as infinite error and fail all tolerance checks. Empty denominators and single-class AUCs are NaN; zero-division rejection scores are 0. Undefined bootstrap replicates are excluded; valid replicate counts are in JSON. JSON null means NaN; Infinity strings mean unbounded error.

Bootstrap: 2000; seed: 20261010; clusters: 600.

## Counts

| Metric | shipped |
| --- | --- |
| n_present | 478 [459, 497] |
| n_absent | 122 [103, 141] |

## Localisation

| Metric | shipped |
| --- | --- |
| success@1 | 0.556 [0.512, 0.601] |
| loc_only@1 | 0.636 [0.592, 0.68] |
| success@3 | 0.711 [0.669, 0.753] |
| loc_only@3 | 0.854 [0.821, 0.886] |
| success@5 | 0.759 [0.721, 0.798] |
| loc_only@5 | 0.908 [0.881, 0.934] |
| gross_rate | 0.0816 [0.0582, 0.108] |
| err_px_p50 | 0.63 [0.542, 0.741] |
| err_px_p90 | 4.52 [3.53, 42.2] |
| err_px_p95 | 181 [48.7, 289] |

## Scale and rotation

| Metric | shipped |
| --- | --- |
| pose_all_n | 478 [459, 497] |
| scale_pct_all_median | 0.705 [0.617, 0.786] |
| scale_pct_all_p90 | 2.28 [2.07, 2.78] |
| scale_pct_all_within1 | 0.64 [0.595, 0.683] |
| scale_pct_all_within2 | 0.864 [0.832, 0.894] |
| scale_pct_all_within5 | 0.96 [0.941, 0.977] |
| rotation_deg_all_median | 0.163 [0.147, 0.182] |
| rotation_deg_all_p90 | 0.5 [0.447, 0.564] |
| rotation_deg_all_within0.25 | 0.659 [0.616, 0.701] |
| rotation_deg_all_within0.5 | 0.9 [0.872, 0.926] |
| rotation_deg_all_within1 | 0.981 [0.969, 0.992] |
| pose_within5_n | 363 [340, 387] |
| scale_pct_within5_median | 0.629 [0.519, 0.714] |
| scale_pct_within5_p90 | 1.87 [1.66, 2.14] |
| scale_pct_within5_within1 | 0.694 [0.646, 0.742] |
| scale_pct_within5_within2 | 0.912 [0.88, 0.941] |
| scale_pct_within5_within5 | 0.997 [0.992, 1] |
| rotation_deg_within5_median | 0.148 [0.12, 0.164] |
| rotation_deg_within5_p90 | 0.447 [0.416, 0.504] |
| rotation_deg_within5_within0.25 | 0.689 [0.641, 0.737] |
| rotation_deg_within5_within0.5 | 0.926 [0.898, 0.951] |
| rotation_deg_within5_within1 | 0.992 [0.981, 1] |

## Rejection and AUC

| Metric | shipped |
| --- | --- |
| absent_accepted | 0 [0, 0] |
| present_declined | 112 [93, 130] |
| absent_declined | 122 [103, 141] |
| precision | 0.521 [0.457, 0.587] |
| recall | 1 [1, 1] |
| F1 | 0.685 [0.628, 0.739] |
| auroc_present | 0.978 [0.967, 0.987] |
| correct_match_auc | 0.976 [0.961, 0.988] |

## Runtime

| Metric | shipped |
| --- | --- |
| runtime_median | 8.76 [8.61, 8.88] |
| runtime_p90 | 10.2 [10.1, 10.4] |
| runtime_p95 | 10.7 [10.4, 10.9] |
| runtime_max | 11.7 [11.4, 11.7] |

## Strata: shipped

### sev_q1

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 108 [90, 127] |
| success@1 | 0.796 [0.711, 0.87] |
| success@3 | 0.852 [0.779, 0.915] |
| success@5 | 0.87 [0.8, 0.929] |
| gross_rate | 0.0463 [0.0099, 0.0883] |
| err_px_p50 | 0.349 [0.286, 0.46] |

### sev_q2

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 128 [109, 148] |
| success@1 | 0.711 [0.628, 0.79] |
| success@3 | 0.883 [0.824, 0.935] |
| success@5 | 0.898 [0.844, 0.947] |
| gross_rate | 0.0469 [0.0147, 0.0877] |
| err_px_p50 | 0.474 [0.36, 0.63] |

### sev_q3

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 127 [108, 147] |
| success@1 | 0.472 [0.388, 0.557] |
| success@3 | 0.693 [0.615, 0.769] |
| success@5 | 0.764 [0.692, 0.836] |
| gross_rate | 0.0787 [0.0339, 0.13] |
| err_px_p50 | 0.738 [0.577, 1.04] |

### sev_q4

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 115 [96, 134] |
| success@1 | 0.252 [0.176, 0.33] |
| success@3 | 0.409 [0.322, 0.5] |
| success@5 | 0.496 [0.404, 0.581] |
| gross_rate | 0.157 [0.0948, 0.228] |
| err_px_p50 | 1.23 [1.12, 1.78] |

### absent

| Metric | Value [95% CI] |
| --- | --- |
| n_absent | 122 [103, 141] |
| absent_accepted | 0 [0, 0] |
| absent_declined | 122 [103, 141] |
