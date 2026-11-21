# IRIS report

95% percentile cluster bootstrap; thresholds fixed; rates are fractions. Missing poses count as infinite error and fail all tolerance checks. Empty denominators and single-class AUCs are NaN; zero-division rejection scores are 0. Undefined bootstrap replicates are excluded; valid replicate counts are in JSON. JSON null means NaN; Infinity strings mean unbounded error.

Bootstrap: 2000; seed: 20261010; clusters: 600.

Threshold zncc_ms: 0.36530551314353943; chosen on disjoint dev labels.

Threshold shipped: 0.26171010732650757; chosen on disjoint dev labels.

## Counts

| Metric | zncc_ms | shipped |
| --- | --- | --- |
| n_present | 478 [459, 497] | 478 [459, 497] |
| n_absent | 122 [103, 141] | 122 [103, 141] |

## Localisation

| Metric | zncc_ms | shipped |
| --- | --- | --- |
| success@1 | 0.282 [0.243, 0.324] | 0.636 [0.592, 0.68] |
| loc_only@1 | 0.291 [0.25, 0.334] | 0.636 [0.592, 0.68] |
| success@3 | 0.41 [0.367, 0.456] | 0.845 [0.81, 0.878] |
| loc_only@3 | 0.431 [0.387, 0.477] | 0.854 [0.821, 0.886] |
| success@5 | 0.437 [0.393, 0.483] | 0.895 [0.867, 0.922] |
| loc_only@5 | 0.46 [0.416, 0.506] | 0.908 [0.881, 0.934] |
| gross_rate | 0.523 [0.475, 0.568] | 0.0816 [0.0582, 0.108] |
| err_px_p50 | 30.9 [4.66, 50.3] | 0.63 [0.542, 0.741] |
| err_px_p90 | 580 [487, 628] | 4.52 [3.53, 42.2] |
| err_px_p95 | 710 [634, 773] | 181 [48.7, 289] |

## Scale and rotation

| Metric | zncc_ms | shipped |
| --- | --- | --- |
| pose_all_n | 478 [459, 497] | 478 [459, 497] |
| scale_pct_all_median | 0.882 [0.788, 0.998] | 0.705 [0.617, 0.786] |
| scale_pct_all_p90 | 18.8 [15.4, 23.2] | 2.28 [2.07, 2.78] |
| scale_pct_all_within1 | 0.546 [0.501, 0.591] | 0.64 [0.595, 0.683] |
| scale_pct_all_within2 | 0.743 [0.703, 0.782] | 0.864 [0.832, 0.894] |
| scale_pct_all_within5 | 0.831 [0.797, 0.865] | 0.96 [0.941, 0.977] |
| rotation_deg_all_median | 0.149 [0.133, 0.171] | 0.163 [0.147, 0.182] |
| rotation_deg_all_p90 | 0.494 [0.423, 0.561] | 0.5 [0.447, 0.564] |
| rotation_deg_all_within0.25 | 0.665 [0.623, 0.707] | 0.659 [0.616, 0.701] |
| rotation_deg_all_within0.5 | 0.906 [0.878, 0.93] | 0.9 [0.872, 0.926] |
| rotation_deg_all_within1 | 0.981 [0.968, 0.992] | 0.981 [0.969, 0.992] |
| pose_within5_n | 209 [187, 233] | 428 [406, 449] |
| scale_pct_within5_median | 0.593 [0.51, 0.668] | 0.633 [0.532, 0.714] |
| scale_pct_within5_p90 | 2.02 [1.59, 2.25] | 1.92 [1.67, 2.15] |
| scale_pct_within5_within1 | 0.713 [0.651, 0.772] | 0.685 [0.64, 0.729] |
| scale_pct_within5_within2 | 0.895 [0.851, 0.933] | 0.904 [0.875, 0.931] |
| scale_pct_within5_within5 | 0.995 [0.985, 1] | 0.995 [0.988, 1] |
| rotation_deg_within5_median | 0.134 [0.115, 0.167] | 0.156 [0.133, 0.173] |
| rotation_deg_within5_p90 | 0.42 [0.38, 0.486] | 0.481 [0.421, 0.529] |
| rotation_deg_within5_within0.25 | 0.679 [0.615, 0.74] | 0.682 [0.637, 0.726] |
| rotation_deg_within5_within0.5 | 0.943 [0.909, 0.972] | 0.916 [0.89, 0.942] |
| rotation_deg_within5_within1 | 1 [1, 1] | 0.988 [0.977, 0.998] |

## Rejection and AUC

| Metric | zncc_ms | shipped |
| --- | --- | --- |
| absent_accepted | 59 [45, 74] | 9 [4, 15] |
| present_declined | 57 [43, 72] | 29 [19, 40] |
| absent_declined | 63 [49, 78] | 113 [95, 131] |
| precision | 0.525 [0.432, 0.618] | 0.796 [0.725, 0.862] |
| recall | 0.516 [0.427, 0.606] | 0.926 [0.879, 0.968] |
| F1 | 0.521 [0.439, 0.597] | 0.856 [0.806, 0.898] |
| auroc_present | 0.77 [0.722, 0.814] | 0.978 [0.967, 0.987] |
| correct_match_auc | 0.676 [0.632, 0.72] | 0.976 [0.961, 0.988] |

## Runtime

| Metric | zncc_ms | shipped |
| --- | --- | --- |
| runtime_median | 45.6 [45.3, 46] | 8.76 [8.61, 8.88] |
| runtime_p90 | 49.2 [48.7, 49.5] | 10.2 [10.1, 10.4] |
| runtime_p95 | 50.5 [49.8, 50.8] | 10.7 [10.4, 10.9] |
| runtime_max | 55.1 [52.4, 55.1] | 11.7 [11.4, 11.7] |

## Strata: zncc_ms

### sev_q1

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 108 [90, 127] |
| success@1 | 0.593 [0.495, 0.683] |
| success@3 | 0.667 [0.575, 0.753] |
| success@5 | 0.667 [0.575, 0.753] |
| gross_rate | 0.315 [0.226, 0.407] |
| err_px_p50 | 0.747 [0.558, 1.02] |

### sev_q2

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 128 [109, 148] |
| success@1 | 0.367 [0.285, 0.455] |
| success@3 | 0.461 [0.372, 0.552] |
| success@5 | 0.469 [0.379, 0.559] |
| gross_rate | 0.508 [0.42, 0.597] |
| err_px_p50 | 25.2 [1.17, 76.4] |

### sev_q3

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 127 [108, 147] |
| success@1 | 0.157 [0.0952, 0.226] |
| success@3 | 0.354 [0.275, 0.444] |
| success@5 | 0.402 [0.319, 0.496] |
| gross_rate | 0.559 [0.469, 0.644] |
| err_px_p50 | 43.3 [3.65, 76.6] |

### sev_q4

| Metric | Value [95% CI] |
| --- | --- |
| n_present | 115 [96, 134] |
| success@1 | 0.0348 [0.00813, 0.0758] |
| success@3 | 0.174 [0.106, 0.245] |
| success@5 | 0.226 [0.149, 0.307] |
| gross_rate | 0.696 [0.61, 0.778] |
| err_px_p50 | 94.2 [76.2, 164] |

### absent

| Metric | Value [95% CI] |
| --- | --- |
| n_absent | 122 [103, 141] |
| absent_accepted | 59 [45, 74] |
| absent_declined | 63 [49, 78] |

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

## Paired differences against shipped

### zncc_ms minus shipped

| Metric | Difference [95% CI] |
| --- | --- |
| success@1 | -0.354 [-0.399, -0.307] |
| success@3 | -0.435 [-0.482, -0.386] |
| success@5 | -0.458 [-0.503, -0.411] |
| F1 | -0.335 [-0.421, -0.252] |
| err_px_p50 | 30.2 [4.04, 49.7] |
