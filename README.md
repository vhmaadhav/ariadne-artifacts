# Drift-Sense: evaluation artifacts (IRIS 27)

Evaluation artifacts for **Drift-Sense: Cross-Magnification Reference Localisation with Rejection in Repeating SEM Layouts**
by Maadhav V H, Sachin A S and Nakul T (IRIS 27). Released with the paper.

This repository holds the ground-truth manifests, the per-pair prediction CSVs for every method and variant in the paper,
the report and acceptance-rule code, and the reports. It contains **no images and no model weights**.
Every number in the paper's tables can be recomputed from the CSVs here with `code/evaluation/iris_report.py`
(and `code/analysis/e6_analysis.py` for the acceptance rules), without a GPU, the generator or the images.

## Contents

| Folder | Files | What |
|---|---|---|
| `manifests/` | 10 CSV, 4 freeze files | Ground truth per pair: pair id, split, `found` (present/absent), pose `gt_x, gt_y, gt_scale, gt_rot_deg`, label convention, severity/stratum. Synthetic dev (150), synthetic test (600 = 3 seeds x 200), synthetic confirmation (400 = 2 seeds x 200), real tiles (800), larger dev split (800), E8 unfiltered absent set (160). |
| `manifests/freeze/` | 4 | sha256 lists and frozen-run records for the confirmation and larger dev sets (image hashes; the images are not included). |
| `manifests/real_tiles_used.tsv` | 1 | The 40 real SEM tiles used (20 M1, 20 M2). |
| `predictions/driftsense/` | 30 CSV | Drift-Sense outputs: `shipped` and `noexit` variants on each split, the ablations (`ablations/`), the alternative decoders (`alt_decoders/`), a second-host rerun (`second_host/`), and the latency run. |
| `predictions/zncc/`, `predictions/loftr/`, `predictions/sift/` | 11 CSV, 1 JSON | Baselines: exhaustive ZNCC search, LoFTR (outdoor), SIFT + RANSAC and SIFT + LightGlue (both tuned on dev only). |
| `predictions/acceptance/` | 18 | EVT and logistic acceptance outputs (test, real, confirmation), their thresholds, the fitted logistic model, the rule, and the risk-coverage table. |
| `reports/` | 30 | Report files (JSON and Markdown) written by `iris_report.py` and the summaries of each experiment. |
| `runtime/` | 3 | Per-stage latency of the E7 run and its parity check. |
| `code/evaluation/` | 6 | `iris_report.py` (metrics, bootstrap, re-thresholding), `iris_eval.py`, `iris_baselines.py`, `iris_tune_baselines.py`, `iris_make_real.py`, `summarize_report.py`. |
| `code/acceptance/` | 3 | `evt_accept.py`, `logistic_accept.py` (acceptance rules), `log_hypotheses.py` (feature rows). |
| `code/baselines/` | 2 | `loftr_baseline.py` (LoFTR wrapper), `run_zncc_test.sh`. |
| `code/analysis/` | 4 | `e6_analysis.py` (acceptance-rule table), `e8_analyze.py`, `e10_eval.py`, `plot_riskcoverage.py` (Figure 2). |
| `code/tests/`, `code/patches/` | 8, 2 | Unit tests (not re-run in this layout) and the two patches applied to the public pipeline. |
| `docs/` | 4 | `FREEZE.md` (frozen configuration), `iris_spec.md` (metric definitions and conventions), `VARIANTS.md` (decode settings of each variant), `confirm_set_generation.md` (how the confirmation set was generated). |

## Table and figure map

Pair sets: **synthetic test** = `manifests/synthetic_test600.csv` (478 present, 122 absent); **real** = `manifests/real800.csv` (640 present, 160 absent); **confirmation** = `manifests/synthetic_confirm400.csv` (323 present, 77 absent); **dev** = `manifests/synthetic_dev150.csv`.
Thresholds: Drift-Sense tau = 0.2617101 (from dev); `shipped` = tau 0.55. Bootstrap: 2000 cluster resamples, seed 20261010 (the clusters are pairs).

| Paper item | Content | Files | Command (run from the repository root) |
|---|---|---|---|
| Table 1 (`tab:main`), column tau = 0.55 | Synthetic test, shipped threshold | `predictions/driftsense/test600_shipped.csv`; report `reports/driftsense_report_test_fixed055.*` | `python -X utf8 code/evaluation/iris_report.py --manifest manifests/synthetic_test600.csv --pred predictions/driftsense/test600_shipped.csv --out-prefix out/t1_shipped` |
| Table 1, column tau = 0.2617 | Synthetic test, dev threshold | `predictions/driftsense/test600_noexit.csv`; report `reports/driftsense_report_test_devthr.*` | `... --manifest manifests/synthetic_test600.csv --pred predictions/driftsense/test600_noexit.csv --rethreshold noexit=0.2617101 --out-prefix out/t1_devthr` |
| Table 1, column Real tiles | 800 real pairs, tau = 0.2617 | `manifests/real800.csv`, `predictions/driftsense/real800_noexit.csv`; report `reports/driftsense_report_real_thr2617.*` | `... --manifest manifests/real800.csv --pred predictions/driftsense/real800_noexit.csv --rethreshold noexit=0.2617101 --out-prefix out/t1_real` |
| Table 2 (`tab:baselines`) | Baselines on 600 test pairs | Drift-Sense: `test600_noexit.csv`; ZNCC: `predictions/zncc/test600_zncc_ms.csv` (threshold from `predictions/zncc/dev150_zncc_ms.csv`); LoFTR: `predictions/loftr/test600_loftr.csv` (threshold from `dev150_loftr.csv`); SIFT: `predictions/sift/test_sift_ransac_tuned.csv`, `test_sift_lightglue_tuned.csv` (found flags as written). Reports `reports/zncc_report_test600.*`, `loftr_report_test600.*`, `sift_report_test600.*` | `... --manifest manifests/synthetic_test600.csv --pred predictions/driftsense/test600_noexit.csv --pred predictions/zncc/test600_zncc_ms.csv --pred predictions/loftr/test600_loftr.csv --pred predictions/sift/test_sift_ransac_tuned.csv --pred predictions/sift/test_sift_lightglue_tuned.csv --rethreshold noexit=0.2617101 --rethreshold "zncc_ms=dev:manifests/synthetic_dev150.csv,predictions/zncc/dev150_zncc_ms.csv" --rethreshold "loftr=dev:manifests/synthetic_dev150.csv,predictions/loftr/dev150_loftr.csv" --out-prefix out/t2_baselines` |
| Table 3 (`tab:ablation`) | Ablations, 600 test pairs, tau = 0.2617 | `test600_noexit.csv` and `predictions/driftsense/ablations/test600_{k1,k5,netselect,nocanon,integer,netnative,nopolish,nopscale,consensus,norows,nostrip,small,wide2}.csv`; reports `reports/driftsense_report_abl_{a,b,c}.*` | `python -X utf8 code/evaluation/iris_report.py --manifest manifests/synthetic_test600.csv --pred predictions/driftsense/test600_noexit.csv --rethreshold noexit=0.2617101 $(for m in k1 k5 netselect nocanon integer netnative nopolish nopscale consensus norows nostrip small wide2; do echo --pred predictions/driftsense/ablations/test600_$m.csv --rethreshold $m=0.2617101; done) --out-prefix out/t3_ablation` |
| Table 3 rows, names | "One hypothesis" = k1; "Five hypotheses" = k5; "No canonicalisation" = nocanon; "Select by network score" = netselect; "Network-only decode" = netnative; "No drift-row correction" = norows; "0.46 M-parameter network" = small (checkpoint not included, see below) | as above, `docs/VARIANTS.md` | |
| Table 4 (`tab:accept`) | Acceptance rules on the 400 confirmation pairs | `predictions/driftsense/confirm400_noexit.csv` (min rule), `predictions/acceptance/pred_confirm_logistic.csv`, `pred_confirm_evt.csv`; report `reports/acceptance_report_confirm.*`; AURC from `code/analysis/e6_analysis.py` | `python -X utf8 code/evaluation/iris_report.py --manifest manifests/synthetic_confirm400.csv --pred predictions/driftsense/confirm400_noexit.csv --pred predictions/acceptance/pred_confirm_logistic.csv --pred predictions/acceptance/pred_confirm_evt.csv --rethreshold noexit=0.2617101 --out-prefix out/t4_confirm` and `python -X utf8 code/analysis/e6_analysis.py` (writes `./recomputed/`) |
| Figure 2 (`fig:rc`) | Risk-coverage curves, confirmation set | `predictions/acceptance/riskcoverage_all_splits.csv` | `python code/analysis/plot_riskcoverage.py` (writes `riskcoverage.pdf` next to the script) |
| Figure 1 (`fig:pipeline`) | Pipeline diagram | drawn in TikZ in the paper source; no data | not applicable |
| Confirmation text (Section 5, "Fresh Confirmation Set") | Same numbers as Table 4, min rule | as Table 4; per-seed manifests `manifests/synthetic_confirm_seed710505.csv`, `..._seed710606.csv` | as Table 4 |
| Runtime text (Section 5, "Runtime") | Median and p95 time per pair | `predictions/driftsense/latency100_shipped.csv` (5.04 s run), `runtime/e7_latency_pairs.csv` and `runtime/e7_latency_summary.json` (E7 run) | Median and p95 of the `seconds` column; not part of `iris_report`. Not recomputed in our check |
| Second-host agreement text | 598 of 600 test decisions within 0.5 px | `predictions/driftsense/second_host/test600_noexit.csv` vs `test600_noexit.csv`; `reports/summary_e4_CHECK.md` | Compare the `x`, `y` columns by `pair_id`. Not recomputed in our check |
| Larger dev split and E8 (not in the tables) | Threshold check on 800 dev pairs; unfiltered absent set (160) | `predictions/driftsense/dev_large800_noexit.csv`, `manifests/dev_large800.csv`, `reports/dev_large_threshold.json`; `predictions/driftsense/e8_absent160_noexit.csv`, `manifests/e8_absent_unfiltered160.csv`, `reports/e8_absent_unfiltered_metrics.json` | `code/analysis/e10_eval.py --manifest manifests/dev_large800.csv --pred predictions/driftsense/dev_large800_noexit.csv --tau 0.2617101`. `code/analysis/e8_analyze.py` expects the E8 folder layout of the original run and is included for reference. Not recomputed in our check |

## How to recompute all numbers from the CSVs

Requirements: Python 3.11+, `numpy`, `pandas`, `scikit-learn` (and `matplotlib` for Figure 2). No GPU, no images, no network.

```bash
python -m venv .venv && . .venv/bin/activate
pip install numpy pandas scikit-learn matplotlib
mkdir -p out
# then run the commands in the table above (Table 1 to Table 4)
python -X utf8 code/analysis/e6_analysis.py     # acceptance-rule table, AURC, risk-coverage
python code/analysis/plot_riskcoverage.py       # Figure 2
```

`iris_report.py` reads a manifest and one or more prediction CSVs, checks that every method covers every pair exactly once, and writes `<out-prefix>.json` and `<out-prefix>.md`. The files in `reports/` were written by the same script in the original runs, so you can diff your output against them.

Notes on reading the output:
- `--rethreshold noexit=0.2617101` fixes the threshold; a `dev:` form re-derives it on dev pairs, as for ZNCC and LoFTR.
- The `found` column in the `shipped` and `noexit` files was written at the shipped threshold 0.55. The `noexit` score is what the paper re-thresholds; `e6_analysis.py` prints the count of rows where the file's `found` differs from the re-thresholded decision (`mismatch_noexit_found_vs_file` in `recomputed/e6_metrics.json`). That count is expected to be non-zero.
- Empty denominators and single-class AUCs are NaN, as documented in the report header.

**Verification.** We reran the commands above on this repository's files. Table 1 (all three columns), Table 2 (all five methods), every row of Table 3 (full pipeline, one hypothesis, network selection, network-only decoding, no drift-row correction, 0.46 M-parameter network, no canonicalisation) and Table 4 (min rule, logistic, EVT) reproduce the paper's values to the printed precision. `recomputed/riskcoverage_all_splits.csv` and `recomputed/e6_metrics.json` are byte-identical to the files in `predictions/acceptance/` and `reports/`.

## What is not included, and why

- **Images.** Both the synthetic images and the real SEM tiles are not in this repository. Synthetic images come from a generator without a licence (see below), so we release only the manifests and the seeds that produced them.
- **Generator.** The synthetic-pair generator is vendored upstream without a licence and is not redistributed. `docs/FREEZE.md` and `docs/confirm_set_generation.md` record the upstream commit, seeds and command lines, so the pairs can be regenerated by anyone who obtains the generator under its own terms. Check the sha256 lists in `manifests/freeze/` after regeneration.
- **Model weights.** Checkpoints (`driftsense.pt`, the `small` and `wide` checkpoints) live in the public Apache-2.0 repository `github.com/vhmaadhav/semicon-driftsense` (commit 5145c39, with the experiment commit ff0acaa recorded in `docs/FREEZE.md`). The `small` and `wide2` variants need their own checkpoints from that repository.
- **Real tiles.** The 40 tiles are from an open SEM dataset, CC BY 4.0, DOI `10.17617/3.HY5SYN`. Their ids are in `manifests/real_tiles_used.tsv`. Obtain the images from the DOI.
- **Scripts that need the public pipeline.** `code/evaluation/iris_eval.py`, `iris_baselines.py`, `iris_make_real.py` and the LoFTR wrapper import the `driftsense` package from the public repository and need the images to run. They are provided so the pipeline can be checked; they are not needed for the recomputation above.

## Licences

- Our code (everything under `code/`, and the CSV, JSON and Markdown outputs): Apache-2.0, see `LICENSE`.
- The patches in `code/patches/` apply to the Apache-2.0 public pipeline; they are released under Apache-2.0 too.
- `driftsense` (public repository) and the LoFTR weights from kornia (Apache-2.0), OpenCV SIFT (Apache-2.0) and LightGlue (Apache-2.0) are third-party components; their licences apply to them.
- Real tiles: CC BY 4.0 (DOI above).

## Provenance

- Synthetic seeds: test 710101, 710202, 710303 (200 pairs each); dev 710404 (150); confirmation 710505, 710606 (200 each); larger dev 710707, 710808 (400 each). Frozen configuration in `docs/FREEZE.md`; freeze lists in `manifests/freeze/`.
- Frozen decision rule: nothing is tuned on the test split; baseline thresholds come from the dev split only.
- Pre-registered criterion for the acceptance rules is described in the paper (Section 5, "Can a Better Acceptance Rule Help?").

## Citation

See `CITATION.cff`.
