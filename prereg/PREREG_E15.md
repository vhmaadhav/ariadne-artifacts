# E15 pre-registration: fresh, untouched test of the frozen pipeline and the uniqueness gate

Date: 21 Nov 2026. Written before any E15 data exists. The coordinator commits this file to GitHub first. No E15 data is generated, no Kaggle kernel is pushed, and no E15 run starts before that commit. Once committed, this file is not edited. Any change needs a new dated pre-registration (E15b) and is reported.

## 1. Purpose

A fresh test, on data that no threshold, gate, tile, seed or rule was chosen from, of:

- the frozen shipped pipeline, `noexit` variant, decided by the min rule at tau = 0.2617101 (headline rule);
- the same pipeline at the E10 err5 threshold, tau = 0.3108282387256622 (comparison rule);
- the E14 uniqueness gate on top of the min rule at tau = 0.2617101 (gate rule).

Every threshold, the margin definition, the data and the analysis are fixed here. Nothing is refitted on E15 data.

## 2. Frozen inputs (unchanged from earlier experiments)

- Pipeline: the shipped `driftsense` `noexit` variant with the feature-logging patch (`code/patches/log_hypotheses.patch`), as in `iris27-code-v2`. Weights `driftsense.pt`, sha256 `e6506b7c3b2ccfd47f9337e9b95df20d0fb2b14a6d45b0a1c892d60464a71ca8`.
- Score: `a` = the `score` column of the `noexit` prediction CSV, which is `min(s_net, zncc_med3)`. It equals the feature field `confidence` (E14 found zero mismatches).
- Frozen renderer: `overlay/scripts/iris_make_real.py` from driftsense-iris27, sha256 `169a85e5d0b816dcdd78d4176191a8c682a3bbdf018d5dcee44684e28009017f`. The E15 kernels import this file verbatim.
- Edmond tile helper: `overlay/tools/edmond_remote_zip.py`, sha256 `2d15ad47ab2a796ca7efbfc5db82671c7e4228b9f76de6238523da4dac941ffd`.

## 3. Frozen constants and decision rules

Constants (exact values, from `results/e10/threshold_dev_large.json` and `results/e14_uniqueness_gate/gate_results.json`):

| name | value | origin |
|---|---|---|
| tau_main | 0.2617101 | dev-150 threshold (max rejection F1) |
| tau_err5 | 0.3108282387256622 | E10 dev-800, lowest threshold with accepted-decision error <= 5% |
| delta_net | 0.09562161564826965 | E14 dev-150, smallest margin threshold with dev accepted-decision error <= 5% (gate_results.json, `delta_err5`) |

Margin definition (exact, from `code/e14_uniqueness_gate.py`, function `margins`), network variant only:

1. Let i be `selected_index` in the feature row for the pair, and h_i the i-th entry of `hypotheses`.
2. If i < 0 or i >= len(hypotheses), the margin is -infinity. The gate then declines the pair.
3. Winner score w = `network_score` of h_i. Winner location (wx, wy) = (`coarse_x_native`, `coarse_y_native`) of h_i.
4. Competitor c = the largest first element v over the entries [v, x, y] of `net_offpeak` in h_i whose Euclidean distance from (wx, wy) is strictly greater than 20 px. If no entry qualifies, c = 0.
5. Margin m_net = w - c.

The ZNCC margin variant of E14 is not part of E15.

Rules. Let a be the score and A_R the set of accepted pairs.

- **R1 (min rule, headline):** accept iff a >= 0.2617101.
- **R2 (min rule, err5):** accept iff a >= 0.3108282387256622.
- **R3 (gate):** accept iff a >= 0.2617101 AND m_net >= 0.09562161564826965.

No rule is refitted, re-chosen or changed after E15 data exists.

## 4. Data (all generated or built after this commit)

### 4A. Synthetic set (A)

- Seeds 711111 and 712222, 200 pairs each, with the same phase-2 mixture as E5: `generate_dataset.py --phase2 --num-pairs 200 --seed S --workers 4` (upstream commit 5145c39), then `tools/make_iris_manifest.py`. Expected total 400 pairs. Clusters for the bootstrap are the canvas (`group_id`).
- Freeze before any run: sha256 of every generated file and of the canonical manifest is written to `FROZEN.txt` and `sha256sum -c` must be clean. Pipeline evaluation starts only after the freeze passes.
- Present and absent counts are whatever the generator produces. They are recorded, not fixed.

### 4B. Real set (B): 40 new Edmond tiles

- Source: Edmond zip, doi 10.17617/3.HY5SYN (CC BY 4.0), members `dataset/sems/m1/semNNNN.png` and `dataset/sems/m2/semNNNN.png`. Per-layer sorted lists: M1 has 327 tiles (sem0000 to sem0326), M2 has 321 (sem0000 to sem0320). Stems are contiguous, checked from the zip central directory.
- Selection rule: in each layer's sorted list, take every 16th tile starting at index 13 (indices 13, 29, ..., 317). That gives 20 tiles per layer, 40 in total.
- Disjointness from the 40 frozen tiles: the frozen set is every 16th tile starting at index 5 (sem0005 to sem0309 in both layers, 20 per layer). Index 13 is not congruent to 5 mod 16, so the sets cannot overlap. Checked by set intersection, empty for both layers.

Tile ids (the kernel checks that these equal the rule above and are disjoint from the frozen set):

- M1 (20): m1_sem0013, m1_sem0029, m1_sem0045, m1_sem0061, m1_sem0077, m1_sem0093, m1_sem0109, m1_sem0125, m1_sem0141, m1_sem0157, m1_sem0173, m1_sem0189, m1_sem0205, m1_sem0221, m1_sem0237, m1_sem0253, m1_sem0269, m1_sem0285, m1_sem0301, m1_sem0317
- M2 (20): m2_sem0013, m2_sem0029, m2_sem0045, m2_sem0061, m2_sem0077, m2_sem0093, m2_sem0109, m2_sem0125, m2_sem0141, m2_sem0157, m2_sem0173, m2_sem0189, m2_sem0205, m2_sem0221, m2_sem0237, m2_sem0253, m2_sem0269, m2_sem0285, m2_sem0301, m2_sem0317

Pairs per tile (20 pairs, 480 in total):

- 4 present pairs, condition A (clean search frame), and 4 present pairs, condition B (search frame with the frozen nuisance: blur sigma 0.7, gain 0.9, offset 8, N(0, 8) noise, clip and round). This keeps the frozen 50/50 mixture. The brief said "8 present pairs per tile"; the A/B split is this pre-registration's choice and is stated here, not left to the kernel.
- 2 absent pairs, same layer: reference from one of the other 19 tiles of the same layer, drawn uniformly. **No NCC filter.**
- 2 absent pairs, cross layer: reference from one of the 20 new tiles of the other layer, drawn uniformly. **No NCC filter.**

Per pair, the reference tile index is drawn once (absent pairs only; present pairs use their own tile). Then each attempt draws, in this order, z ~ U(8, 12), theta ~ U(-5, 5), q = (2047.5, 1767.5) + U(-50, 50)^2, c ~ U(100, 899)^2, and, for absent pairs, u ~ U over the safe interior of the reference. For present pairs, u = q + (z/4) R(-theta) (c - b), with b = (499.5, 499.5). An attempt is rejected, and redrawn, if either the reference or the search footprint is unsafe (8 px support, as in the frozen builder). Rendering is the frozen renderer. Present labels: found = 1, (gt_x, gt_y) = c, `label_convention` = center, gt_scale = z, gt_rot_deg = theta. Absent labels: found = 0.

RNG: `numpy.random.default_rng(20261122)`. Tiles are processed in the order m1 (sorted), then m2 (sorted). Within a tile the order is A x4, B x4, same-layer absent x2, cross-layer absent x2. The B nuisance noise is drawn after geometry is accepted.

Totals: 320 present (160 A, 160 B), 80 same-layer absent, 80 cross-layer absent.

## 5. Metrics

Let P be the present pairs, Ab the absent pairs (Ab_same and Ab_cross on the real set; all absent pairs on the synthetic set), N the number of pairs, and err the Euclidean distance between the predicted (x, y) and the ground truth (absent pairs: err = infinity). For a rule R with accepted set A:

- success@k, k in {1, 5}: |P and A and err <= k| / |P|. This matches the `success@r` of `iris_report`, where "found" means accepted.
- accepted wrong repeats (count): |P and A and err > 20|. Rate: that count / |A|.
- accepted-decision error: |(Ab and A) or (P and A and err > 5)| / |A|. This matches E10.
- absent accepted, by stratum: |Ab_s and A| / |Ab_s| for s = same-layer and cross-layer (real set), or all absent (synthetic set).
- coverage: |A| / N.
- F1 (rejection, absent as positive): 2TP / (2TP + FP + FN), with TP = |Ab and not A|, FP = |P and not A|, FN = |Ab and A|.
- presence AUROC: area under the ROC curve of a for P (positive) against Ab (negative), by the Mann-Whitney rank formula with tied ranks averaged. The score is rule-independent, so it is reported once per set.

Bootstrap: cluster bootstrap with B = 2000 and seed 20261010. Clusters: canvas (synthetic set) or tile (real set, 40 clusters). Draw `idx = numpy.random.default_rng(20261010).integers(0, K, size=(2000, K))` once per set. The same `idx` is used for every rule, every metric and the paired differences. Each replicate recomputes each metric from the resampled clusters (ratio of summed numerators and denominators). The 95% CI is the 2.5 and 97.5 percentiles over finite replicates. The paired difference R3 - R1 uses the same replicates.

## 6. Hypotheses and pass criteria

- **H1 (synthetic, R1):** the success@5 point estimate lies in [0.867, 0.942]. That is the range of the 95% CIs seen on the test set (0.867 to 0.922, E2) and the confirmation set (0.883 to 0.942, E5). Pass if the point estimate is in range. The bootstrap CI is reported as well.
- **H2 (synthetic and real, R3 minus R1):** the paired bootstrap CI of the difference in accepted wrong repeats (count) has an upper bound below 0 on both sets. Pass only if both sets pass. A CI with a lower bound above 0 is a fail and is reported as an increase.
- **H3 (real, R1):** the cross-layer absent accept rate, point estimate, is at most 0.10.
- **H4 (real, R1, descriptive, no pass or fail):** the same-layer unfiltered absent accept rate, point estimate and 95% CI.

Other results (all rules, all metrics, the synthetic absent accept rate, F1, AUROC, coverage, paired differences for every metric) are reported as descriptive results with their CIs. They do not change any hypothesis verdict.

## 7. Reporting commitment

Every result is reported whatever the outcome: each hypothesis verdict, every rule and metric with its CI, failed or discarded runs, freeze or kernel errors, and any change of seed or tile. A failed kernel is fixed and rerun only with the same seeds and tile list, and the failure is reported. Analyses beyond this file are labelled exploratory. No rule, tile, seed, pair, threshold or pass criterion is changed after the E15 data exists.

## 8. Provenance

- This file is committed before any E15 generation. Its sha256 is written into `code/e15_thresholds.json` (field `prereg_sha256`) before the kernels are pushed. The coordinator checks it against the committed file.
- `code/e15_eval.py` reads every threshold and constant only from `code/e15_thresholds.json`. That JSON is copied from sections 3, 4B and 6. A unit test compares the JSON with the values in this file.
- The kernels ship in the private dataset `maadhavvh/ariadne-e15-eval` (`e15_eval.py`, `e15_thresholds.json`, `edmond_remote_zip.py`, `iris_make_real.py`), plus the code dataset `maadhavvh/iris27-code-v2`.
