# E16: ZNCC baseline on the E15 untouched sets

**Label:** post-registration baseline, threshold from the original development split. It was added after the pre-registration; `docs/PREREG_E15.md` is untouched.

**Method and comparison:**
- **Baseline:** zncc_ms, τ = 0.36530551, chosen on the original development split (see `results/e2`).
- **Paired Δ and bootstrap:** as in `code/e15_eval.py` (B = 2000, seed 20261010).
- **Drift-Sense comparison:** R1 (τ = 0.2617101).
- **Freeze checks:** PASS for both sets. The regenerated images are byte-identical to the E15 frozen lists.

## Synthetic (400 pairs, 331 present): ZNCC vs R1

| Metric | ZNCC | R1 |
|---|---|---|
| success@1 | 0.242 [0.198, 0.288] | 0.659 [0.604, 0.709] |
| success@5 | 0.384 [0.333, 0.438] | 0.870 [0.833, 0.906] |
| Accepted wrong repeats | 140 [121, 158] | 16 [9, 24] |
| Accepted-decision error | 0.606 [0.551, 0.657] | 0.091 [0.061, 0.124] |
| Absent accepted | 0.725 [0.614, 0.827] | 0.116 [0.045, 0.194] |
| Coverage | 0.805 [0.765, 0.843] | 0.793 [0.750, 0.833] |
| Rejection F1 | 0.259 [0.162, 0.352] | 0.803 [0.729, 0.865] |
| Presence AUROC | 0.585 [0.508, 0.660] | 0.977 [0.962, 0.988] |

Paired Δ success@5 (ZNCC minus R1): −0.486 [−0.539, −0.435].

## Real (480 pairs, 320 present, 40 new tiles): ZNCC vs R1

| Metric | ZNCC | R1 |
|---|---|---|
| success@1 | 0.978 [0.947, 1.000] | 0.881 [0.831, 0.925] |
| success@5 | 0.984 [0.959, 1.000] | 0.913 [0.863, 0.953] |
| Accepted wrong repeats | 3 [0, 8] | 14 [5, 24] |
| Accepted-decision error | 0.341 [0.331, 0.356] | 0.182 [0.145, 0.223] |
| Same-layer absent accepted | 1.000 [1.000, 1.000] | 0.538 [0.425, 0.650] |
| Cross-layer absent accepted | 0.988 [0.963, 1.000] | 0.100 [0.038, 0.175] |
| Coverage | 0.996 [0.990, 1.000] | 0.744 [0.717, 0.771] |
| Rejection F1 | 0.012 [0.000, 0.037] | 0.770 [0.707, 0.828] |
| Presence AUROC | 0.976 [0.953, 0.990] | 0.945 [0.920, 0.968] |

Paired Δ success@5 (ZNCC minus R1): +0.072 [+0.041, +0.109].

## Reading

- **Synthetic:** ZNCC is worse on every metric.
- **Real (imposed-pose pairs cut from one capture):** exhaustive ZNCC localises present references better than Drift-Sense and ranks presence slightly better (AUROC 0.976 vs 0.945). The two images share pixels and noise, which favours direct correlation; this is limitation (ii) of the paper.
- **Real threshold:** with its development threshold, ZNCC accepts almost every absent reference, so its decision is unusable as a presence gate. A real-calibrated threshold was not tried (single threshold, no sweep).
- **Cost:** ZNCC takes about 45 s per pair per process, against about 5 s for Drift-Sense.
