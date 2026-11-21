# E14: uniqueness gate on top of the min rule (EXPLORATORY / post hoc)

The confirmation set was already used once to judge the E6 rules, so this analysis is exploratory.
- Script: `code/e14_uniqueness_gate.py`.
- Numbers: `gate_results.json`.
- Data: only existing per-pair features (e4 a/b/c, e8); no new runs.

## Rule

Accept iff a = min(s_net, ρ_med) ≥ τ AND margin ≥ δ, where the margin is the winner score minus the strongest competing off-peak maximum. Two variants:
- (i) on the network response;
- (ii) on native ZNCC.

## Fitting

- **Data:** δ was fitted on the 150-pair dev split, the same split that set τ = 0.2617. The 800-pair E10 dev split has prediction CSVs only, without per-pair features.
- **Criterion:** the smallest δ with dev accepted-decision error ≤ 5%.
- **Chosen δ:** network δ = +0.0956; ZNCC δ = −0.0576. The dev max-F1 choice is no gate.
- **Effect on dev:** the min-rule error falls from 6.8% to 4.2% with the network gate.

## Network gate vs min rule, τ = 0.2617

| Split | Accepted wrong repeats (>20 px) | Success@5 (Δ, 95% CI) | Coverage | Accepted-decision error | Absent accepted |
|---|---|---|---|---|---|
| Test 600 | 17 → 6 | 0.895 → 0.877 [−0.032, −0.008] | 0.763 → 0.725 | 0.066 → 0.037 | 9 → 6 |
| Confirmation 400 | 16 → 8 | 0.913 → 0.901 [−0.025, −0.003] | 0.807 → 0.772 | 0.087 → 0.058 | 9 → 7 |
| Real 800 | 37 → 6 | 0.908 → 0.803 [−0.133, −0.078] | 0.785 → 0.650 | 0.075 → 0.012 | 10 → 0 |
| E8 unfiltered absent 160 | n/a | n/a | n/a | n/a | 83 → 23 |

## ZNCC-margin gate

- **Synthetic:** weaker. Accepted wrong repeats go from 17 to 12 on test and from 16 to 13 on confirmation.
- **Real:** cuts accepted wrong repeats from 37 to 11, with success unchanged.

## Verdict

- **Pre-registered E6 criterion:** fails it on test, confirmation and real, because success@5 drops by more than 1 point.
- **Default rule:** not adopted.
- **As an alternative operating point:** the network gate roughly halves the accepted-decision error and removes 50–84% of the accepted wrong repeats. It costs 1–2 points of success@5 on synthetic data and about 10 points on real tiles.
