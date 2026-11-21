# Latency, all runs (100 test pairs, serial, 4 threads, shipped pipeline)

| Run | Host | Median (s) | p95 (s) | Network share |
|---|---|---|---|---|
| Frozen (Oct) | Kaggle Xeon 2.2 GHz, 4 vCPU | 5.04 | 5.88 | n/a (RUNLOG only) |
| E7 v1 | Kaggle Xeon 2.2 GHz, 4 vCPU | 5.90 | 6.83 | 81.5% |
| E7 r2 | Kaggle Xeon 2.2 GHz, 4 vCPU | 5.51 | 6.58 | 81.6% |
| E7 r3 | Kaggle Xeon 2.2 GHz, 4 vCPU | 6.18 | 7.27 | 83.9% |
| Laptop | AMD Ryzen AI 7 350 | 3.97 | 4.72 | 80.7% |

## Kaggle runs

- **Median across the four runs:** 5.04–6.18 s, a 23% spread.
- **Same setup in every logged run:** the same Xeon (model 79, stepping 0), 2200 MHz, the same caches, and torch 2.13.0+cpu with MKL and oneDNN and 4 threads.
- **Where the spread sits:** mostly in the network stage. r3's network stage is 14% slower than r2's, while its pose probe is 3% faster.
- **Unexplained:** steal time and host load were not logged, so noisy neighbours are neither confirmed nor excluded.

## Correctness

Outputs are identical across v1, r2 and r3 on all 100 pairs. Timed and untimed runs give identical outputs on 5 pairs.

## Laptop

- **Median:** 3.97 s.
- **Not recorded:** MKL/oneDNN flags and MHz.
- **Peak Tctl:** 52 °C.
- **Supersedes:** the earlier 1.85 s figure, which came from a 6-pair smoke test under a different configuration.
