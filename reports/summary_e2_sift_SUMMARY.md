# SIFT baselines on all 600 test pairs

Source: Kaggle `<kaggle-account>/iris27-sift` (frozen, COMPLETE, 4 vCPU, 36,686 s total). Fetched: `results/pred_test_sift_{ransac,lightglue}_tuned.csv` (test_s1, test_s2, test_s3: 200 each, 600 rows, all `ok`), `results/pred_dev_*` and `results/pred_real_*`, `results/baseline_presets.json`, `results/baseline_tuning_dev.md`, `results/kaggle_run.json`, and the kernel and step logs. Pair IDs match `manifest_test_600.csv`.

Presets (dev-tuned, `baseline_presets.json`): SIFT+RANSAC contrastThreshold 0.04, upsample 2, ratio 1.0 (no Lowe test), RANSAC 3 px, min 4 inliers. SIFT+LightGlue contrastThreshold 0.04, upsample 1, ratio 0.8, LightGlue matcher, min 4 inliers.

Metrics: `iris_report.py` with the same settings as `results/e2/SUMMARY.md` (2000 cluster bootstrap, seed 20261010, 600 clusters). Found flags are the baseline's own; no threshold was applied. Source: `report_test600.{md,json}`.

| Metric (95% CI) | SIFT + RANSAC | SIFT + LightGlue |
| --- | --- | --- |
| success@5 | 0.090 [0.065, 0.116] | 0.000 [0.000, 0.000] |
| wrong-repeat rate (present pairs, > 20 px) | 0.904 [0.877, 0.930] | 0.998 [0.994, 1.000] |
| median error, px | 478 [436, 526] | inf |
| rejection F1 | 0 (found = 1 on all 600 pairs) | 0.342 [0.291, 0.391] |
| presence AUROC | 0.559 [0.542, 0.576] | 0.500 [0.500, 0.500] |
