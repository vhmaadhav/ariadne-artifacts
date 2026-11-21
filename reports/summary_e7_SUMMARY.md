# E7: per-stage latency (Kaggle CPU, serial, 100 test pairs)

Kernel `<kaggle-account>/ariadne-e7-latency` v1, COMPLETE. Source: `kaggle/kernels/ariadne-e7-latency/kernel.py`.
Configuration as in the frozen latency run: manifest_test_s1 first 100 rows, shipped decode settings, serial, 4 threads, cold model. Time is the `locate_phase2` wall time (model load excluded).

## Per-stage timing (ms per pair)

| Stage (kernel name) | Median ms | Share of total |
|---|---:|---:|
| pose_probe | 897.4 | 15.57% |
| canonicalise | 7.7 | 0.14% |
| network (`locate`) | 4785.1 | 81.54% |
| native_zncc | 0.87 | 0.02% |
| selection | 0.03 | 0.0006% |
| polish | 78.5 | 1.47% |
| strip_rotation | 24.3 | 0.44% |
| drift_rows | 5.7 | 0.11% |
| decision | 9.8 | 0.18% |
| drift_rows_remap | 0.02 | 0.0002% |
| choose_and_other | 29.0 | 0.53% |

Share = sum of the stage over 100 pairs divided by the sum of the total over 100 pairs. Stage medians do not add to the total median, because each median is taken per stage.

## Total per pair

- Median 5895.7 ms (5.90 s), p95 6834.0 ms (6.83 s), max 7178 ms, n = 100.
- Frozen latency run (same config, from RUNLOG 2026-11-20): median 5.04 s, p95 5.88 s. The E7 run is about 17% slower on the median. Cause not established; the two runs differ in Kaggle host and possibly in the wrapper overhead of the timed pass. Both numbers are kept, not averaged.

## Parity

`e7_parity.json`: `identical: true` for the first 5 pairs (s1_00000 to s1_00004). The timed pass used pass-through wrappers; the wrappers were removed and the 5 pairs rerun untimed, and the full result dicts matched exactly. Only 5 pairs were checked, as designed.

## Environment

- CPU: Intel(R) Xeon(R) CPU @ 2.20GHz (KVM, 4 vCPUs, 2 cores x 2 threads, 31 GB RAM).
- Threads: `torch.set_num_threads(4)`; in `e7_latency_summary.json`, torch threads 4 and cv2 threads 4.
- torch 2.13.0+cpu, cv2 5.0.0, numpy 2.4.6, sklearn 1.9.1, Python 3.13.18.
- Weights sha256 `e6506b7c...71ca8` (matches FREEZE.md per the kernel check).
- Note: the first line of `env.log` prints `threads 2`. That line is not produced by `kernel.py` (grep finds only `set_num_threads(4)`), and the JSON records 4. Not resolved; the JSON value is used here.

## Files

`e7_latency_pairs.csv` (100 rows, per-stage seconds, hypothesis counts, pose outputs), `e7_latency_summary.json`, `e7_parity.json`, `kaggle_run.json`, `env.log`, `pip.log`, `e7_kernel.log` (kernel stdout/stderr).
