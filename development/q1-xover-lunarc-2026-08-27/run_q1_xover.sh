#!/bin/bash
# Q1-XOVER LUNARC runner (frozen protocol: research/extensions/orion-q/Q1_XOVER_PROTOCOL_V1.md)
# Invariants mirrored from development/orion-v3-execution-takeover-2026-08-25/lunarc-reference-03:
#   - sha256-verified source.tar.gz (hash recorded in SUBMISSION.json before submission)
#   - job-local venv (env -u PYTHONPATH python3 -m venv), pinned numpy==2.3.5
#   - outputs written with mode "x" at the job root
set -euo pipefail

root=$(pwd)

expected_source_sha=$(env -u PYTHONPATH python3 -c "import json; print(json.load(open('SUBMISSION.json'))['source_archive_sha256'])")
actual_source_sha=$(sha256sum source.tar.gz | awk '{print $1}')
test "$actual_source_sha" = "$expected_source_sha"
echo "ORION_Q1XOVER_SOURCE_HASH_GREEN sha256=$actual_source_sha"

rm -rf source private-venv r6r-cache
mkdir -p source logs
tar -xzf source.tar.gz -C source

env -u PYTHONPATH python3 -m venv private-venv
env -u PYTHONPATH private-venv/bin/python -m pip install \
  --disable-pip-version-check \
  --no-cache-dir \
  --quiet \
  'numpy==2.3.5'
env -u PYTHONPATH private-venv/bin/python - <<'PY'
import numpy

assert numpy.__version__ == "2.3.5"
print("ORION_Q1XOVER_ENV_GREEN numpy", numpy.__version__)
PY
env -u PYTHONPATH private-venv/bin/python -m pip freeze --all > PRIVATE_ENVIRONMENT_FREEZE.txt

export Q1XOVER_OUT_DIR="$root"
export ORIONQ_R6R_CACHE="$root/r6r-cache"
cd source/research/extensions/orion-q
env -u PYTHONPATH "$root/private-venv/bin/python" q1_crossover_evaluation.py
echo "ORION_Q1XOVER_RUN_COMPLETE"
