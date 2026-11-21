#!/usr/bin/env bash
# E2: ZNCC baseline (zncc_ms, existing overlay code) on all 600 frozen test pairs and on dev.
# Run from the working copy root (setup_workdir.sh output). Resumable; no thresholds are set here.
set -euo pipefail
PY=${PY:-.venv/bin/python}
[ -x "$PY" ] || PY=.venv/Scripts/python.exe
mkdir -p results/iris results/ariadne/E2_zncc
"$PY" -X utf8 scripts/iris_baselines.py --manifest data/iris/manifest_dev.csv \
  --method zncc_ms --out results/ariadne/E2_zncc/pred_dev_zncc_ms.csv --jobs 2 --threads 2
"$PY" -X utf8 scripts/iris_baselines.py --manifest data/iris/manifest_test.csv \
  --method zncc_ms --out results/ariadne/E2_zncc/pred_test_zncc_ms.csv --jobs 2 --threads 2
echo "E2 done. Report (dev threshold chosen on dev only):"
"$PY" -X utf8 scripts/iris_report.py --manifest data/iris/manifest_test.csv \
  --pred results/ariadne/E2_zncc/pred_test_zncc_ms.csv \
  --rethreshold "zncc_ms=dev:data/iris/manifest_dev.csv,results/ariadne/E2_zncc/pred_dev_zncc_ms.csv" \
  --out-prefix results/ariadne/E2_zncc/report_test_zncc --bootstrap 2000 --seed 20261010
