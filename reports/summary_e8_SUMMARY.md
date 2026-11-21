# E8: unfiltered real-absent evaluation

Kernel `<kaggle-account>/ariadne-e8-absent-unfiltered` (v2, Kaggle CPU, COMPLETE). Pipeline `noexit`, accept = score >= tau = 0.2617101. 160 absent pairs (40 search tiles x 4 references, 20 tiles per layer), drawn from the same-layer pool with no NCC filter. Labels are presumed absent, so every rate below is an upper bound on the false-accept rate.

## Results (tau = 0.2617101)

| Subset | Accepted | Rate | 95% CI (tile bootstrap) |
| --- | --- | --- | --- |
| Overall (n = 160) | 83 | 51.9% | [42.5, 60.6]% |
| M1 (n = 80) | 38 | 47.5% | [34.2, 60.2]% |
| M2 (n = 80) | 45 | 56.3% | [44.3, 68.2]% |

- Plain-NCC max >= 0.5: 154 of 160 pairs (these are the ones the shipped NCC filter would have removed).
- Accept rate in that filtered-out subset (n = 154): 83/154 = 53.9%.
- Accept rate in the rest (plain NCC < 0.5, n = 6): 0/6 = 0%. Six pairs cannot support a comparison.

## Accept rate at tau = 0.55

17/160 = 10.6%, 95% CI [5.6, 16.3]%. Per layer: M1 13/80, M2 4/80.

## Method

- Bootstrap: resample the 40 tiles with replacement (cluster = tile, 4 pairs each), 2000 resamples, `numpy.random.default_rng(20261010)`, fresh generator per interval, percentile 2.5 and 97.5.
- Computed locally by `results/e8/e8_analyze.py` from `pred_absent_unfiltered_noexit.csv` (score, status) and `build_manifest.csv` (tile, layer, plain_ncc_max). Output: `absent_unfiltered_metrics.json`.
- All 160 rows have status `ok`. pair_ids match between prediction and manifest.

## Caveats

- The kernel's own summary step failed (`AttributeError: 'numpy.ufunc' object has no attribute '__qualname__'` in the after-step), so the summary JSON and per-pair CSV it was meant to write do not exist. The numbers above are recomputed from the kernel's prediction CSV, not read from a kernel summary.
- The prediction CSV's `found` column equals score >= 0.55 for all 160 rows (17 positives), not score >= tau. It is not used for the tau results above.
- Presumed labels: some "absent" references may match a repeated structure in the tile, so these rates are an upper bound on false accepts.

## Files

- `pred_absent_unfiltered_noexit.csv`, `build_manifest.csv`, `feat_absent_unfiltered_noexit.jsonl` (per-pair features)
- `absent_unfiltered_metrics.json`, `e8_analyze.py`
- `kaggle_run.json`, `ariadne-e8-absent-unfiltered.log`, `logs/`

## Plain-NCC max by accept decision (measured from `build_manifest.csv` and the prediction CSV)

| Group | n | min | p25 | median | p75 | max | NCC >= 0.5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Accepted at tau | 83 | 0.562 | 0.759 | 0.831 | 0.888 | 0.980 | 83 |
| Declined at tau | 77 | 0.461 | 0.596 | 0.665 | 0.751 | 0.964 | 71 |

## Answer-to-NCC-argmax agreement: not measured

The kernel saved only the plain-NCC maximum value per pair, not its location, so the within-5-px agreement between the Drift-Sense answer and the plain-NCC argmax cannot be computed from the fetched files. Measuring it needs a re-render of the 160 pairs (not done here).
