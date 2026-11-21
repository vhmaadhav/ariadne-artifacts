# Frozen configuration for the IRIS27 runs

- Upstream repo commit: 5145c39b8d776839eaed6e844bd01769c971748b (github.com/vhmaadhav/semicon-driftsense, 2026-09-22)
- Experiment commit (harness + default-preserving ablation switches): ff0acaa58afa8999a23e6e24e37b0db8b1ef736f
- Checkpoint weights/driftsense.pt sha256: e6506b7c3b2ccfd47f9337e9b95df20d0fb2b14a6d45b0a1c892d60464a71ca8
- driftsense/config.py defaults unchanged: SHIPPED_THRESHOLD=0.55, SHIPPED_CONFIDENCE=min_med3, SHIPPED_SUBPIXEL=parabola, SHIPPED_VERIFICATION=zncc
- Environment: Python 3.11.15 | torch 2.13.0+cpu | cv2 5.0.0 | numpy 2.4.6 | pandas 3.0.5
- Machine: AMD Ryzen AI 7 350 (8 cores / 16 threads), 15 GB RAM, Windows 11; runs use 2 processes x 4 threads
- Data (generate_dataset.py --phase2, workers 4): test_s1 seed 710101, test_s2 710202, test_s3 710303 (200 pairs each), dev seed 710404 (150 pairs)
- Manifest sha256: dev aecd05c2c51058c4068bb748d8495382718d1bdc5bdedbcfa392add1165cf9ca | test 8ab1d6083d4e936bd28476ef05ab856c9a767179b639e8449074616e8db5f0fc
- Label convention for synthetic pairs: edge (the vendored generator's pixel-edge convention)
- Bootstrap: 2000 cluster resamples, seed 20261010
- Rule: nothing is tuned on the test split; baseline thresholds come from the dev split only.
