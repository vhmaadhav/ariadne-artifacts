# E15: pre-registered untouched evaluation (PREREG_E15.md, commit ca78590, 21 Nov 2026 13:41 IST)

Scored exactly as pre-registered by `code/e15_eval.py`, with thresholds read from `code/e15_thresholds.json`. That file's hash is e36eb734, and its prereg_sha256 matches `docs/PREREG_E15.md`. Re-running the scorer locally reproduces both kernel JSONs exactly. Full per-rule metrics: `results/e15_synth/` and `results/e15_real/`.

## Rules

- **R1:** min rule, τ = 0.2617101.
- **R2:** min rule, τ = 0.3108282.
- **R3:** R1 AND network margin ≥ δ = 0.0956.

## Data

- **Synthetic:** seeds 711111 and 712222. 400 pairs: 331 present, 69 absent.
- **Real:** 40 new Edmond tiles, disjoint from the frozen 40. 480 pairs: 320 present (160 clean A, 160 nuisance B), 80 same-layer unfiltered absent, 80 cross-layer absent.

## Verdicts

| | Hypothesis | Result | Verdict |
|---|---|---|---|
| H1 | Synthetic success@5 (R1) within 0.867–0.942 | 0.870 [0.833, 0.906] | PASS (near the lower edge) |
| H2 | Gate reduces accepted wrong repeats on synthetic AND real | synthetic −7 [−13, −2]; real −12 [−22, −4] | PASS |
| H3 | Real cross-layer absent accept ≤ 10% at R1 | 8/80 = 0.100 [0.038, 0.175] | PASS (on the boundary) |
| H4 | Real same-layer unfiltered absent accept (R1), descriptive | 0.538 [0.425, 0.650] | — |

## Key numbers (R1 / R2 / R3)

### Synthetic

| Metric | R1 | R2 | R3 |
|---|---|---|---|
| success@1 | 0.659 | 0.647 | 0.638 |
| Accepted wrong repeats | 16 | 16 | 9 |
| Accepted-decision error | 0.092 | 0.085 | 0.064 |
| Coverage | 0.793 | 0.765 | 0.738 |
| F1 | 0.803 | 0.773 | 0.736 |
| Absent accepted | 0.116 | 0.087 | 0.073 |

### Real

| Metric | R1 | R2 | R3 |
|---|---|---|---|
| success@1 | 0.881 | 0.881 | 0.784 |
| Accepted wrong repeats | 14 | 12 | 2 |
| Accepted-decision error | 0.182 | 0.146 | 0.072 |
| Same-layer absent accepted | 0.538 | 0.425 | 0.175 |
| Cross-layer absent accepted | 0.100 | 0.050 | 0.050 |
| Coverage | 0.744 | 0.713 | 0.579 |
| F1 | 0.770 | 0.819 | 0.785 |

### Presence AUROC

- **Synthetic:** 0.977 [0.962, 0.988].
- **Real:** 0.945 [0.920, 0.968].

Success@5 for the real set and the other per-rule CIs are in the kernel JSONs.

## Deviations (plumbing only; see RUNLOG, 13:50, 17:31 and 17:41 IST)

1. **Kaggle dataset subtitle:** shortened to fit the 80-character limit.
2. **Synthetic v1:** the output directory was missing, so the run failed. Fixed in v2 by creating it first.
3. **Real v1:** a stale `edmond_remote_zip.py` shadowed the verified copy and failed the sha gate. Fixed in v2 through the import order.
4. **Real v2:** Edmond returned HTTP 503. Fixed in v3 with retry and backoff; four retries, all recovered.

The freeze files are named `FROZEN_synth.txt` and `FROZEN_real.txt`, where the PREREG says `FROZEN.txt`. `sha256 -c` passed inside the kernels (0 failures).

No threshold, seed, tile, pair count, renderer setting, metric or hypothesis was changed.
