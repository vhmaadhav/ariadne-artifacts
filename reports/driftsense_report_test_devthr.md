# IRIS report

95% percentile cluster bootstrap; thresholds fixed; rates are fractions. Missing poses count as infinite error and fail all tolerance checks. Empty denominators and single-class AUCs are NaN; zero-division rejection scores are 0. Undefined bootstrap replicates are excluded; valid replicate counts are in JSON. JSON null means NaN; Infinity strings mean unbounded error.

Bootstrap: 2000; seed: 20261010; clusters: 600.

Threshold shipped: 0.26171010732650751; chosen on disjoint dev labels.

## Counts

| Metric | shipped |
| --- | --- |
| n_present | 478 [459, 497] |
| n_absent | 122 [103, 141] |

## Localisation

| Metric | shipped |
| --- | --- |
| success@1 | 0.636 [0.592, 0.68] |
| loc_only@1 | 0.636 [0.592, 0.68] |
| success@3 | 0.845 [0.81, 0.878] |
| loc_only@3 | 0.854 [0.821, 0.886] |
| success@5 | 0.895 [0.867, 0.922] |
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
| pose_within5_n | 428 [406, 449] |
| scale_pct_within5_median | 0.633 [0.532, 0.714] |
| scale_pct_within5_p90 | 1.92 [1.67, 2.15] |
| scale_pct_within5_within1 | 0.685 [0.64, 0.729] |
| scale_pct_within5_within2 | 0.904 [0.875, 0.931] |
| scale_pct_within5_within5 | 0.995 [0.988, 1] |
| rotation_deg_within5_median | 0.156 [0.133, 0.173] |
| rotation_deg_within5_p90 | 0.481 [0.421, 0.529] |
| rotation_deg_within5_within0.25 | 0.682 [0.637, 0.726] |
| rotation_deg_within5_within0.5 | 0.916 [0.89, 0.942] |
| rotation_deg_within5_within1 | 0.988 [0.977, 0.998] |

## Rejection and AUC

| Metric | shipped |
| --- | --- |
| absent_accepted | 9 [4, 15] |
| present_declined | 29 [19, 40] |
| absent_declined | 113 [95, 131] |
| precision | 0.796 [0.725, 0.862] |
| recall | 0.926 [0.879, 0.968] |
| F1 | 0.856 [0.806, 0.898] |
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
| success@1 | 0.861 [0.794, 0.924] |
| success@3 | 0.935 [0.887, 0.98] |
| success@5 | 0.954 [0.912, 0.99] |
| gross_rate | 0.0463 [0.0099, 0.0883] |
| err_px_p50 | 0.349 [0.286, 0.46] |

### sev_q2

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 128 [109, 148] |
| success@1 | 0.742 [0.661, 0.817] |
| success@3 | 0.922 [0.874, 0.965] |
| success@5 | 0.938 [0.893, 0.976] |
| gross_rate | 0.0469 [0.0147, 0.0877] |
| err_px_p50 | 0.474 [0.36, 0.63] |

### sev_q3

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 127 [108, 147] |
| success@1 | 0.567 [0.485, 0.652] |
| success@3 | 0.835 [0.763, 0.9] |
| success@5 | 0.906 [0.85, 0.955] |
| gross_rate | 0.0787 [0.0339, 0.13] |
| err_px_p50 | 0.738 [0.577, 1.04] |

### sev_q4

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 115 [96, 134] |
| success@1 | 0.383 [0.296, 0.47] |
| success@3 | 0.687 [0.6, 0.772] |
| success@5 | 0.783 [0.704, 0.852] |
| gross_rate | 0.157 [0.0948, 0.228] |
| err_px_p50 | 1.23 [1.12, 1.78] |

### absent

| Metric | Value [95% CI] |
| --- | --- |
| n_absent | 122 [103, 141] |
| absent_accepted | 9 [4, 15] |
| absent_declined | 113 [95, 131] |
