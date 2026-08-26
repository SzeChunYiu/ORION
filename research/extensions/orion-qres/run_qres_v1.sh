#!/bin/bash
# V1-Q-RESOURCE-01 runner (LUNARC, hep2023-1-3 / hep partition).
#
# Job-directory contract (all paths relative to the directory sbatch runs in):
#   source.tar.gz             archive of the ORION branch tree (sha256-gated)
#   qres_expected_inputs.env  QRES_EXPECTED_SOURCE_SHA256 / QRES_EXPECTED_RUNNER_SHA256
#   run_qres_v1.sh            this runner (self-hash-gated)
#
# The frozen package research/orion-v1-freeze/ is only ever READ (it ships
# inside source.tar.gz); all outputs are written to qres-output/ outside the
# extracted tree. Integer/exact-rational discipline is enforced by the build
# script itself (exit 4 on any float leak).
set -euo pipefail
unset PYTHONPATH PYTHONHOME || true
export PATH="${HOME}/.local/bin:${PATH}"
export UV_CACHE_DIR=/projects/hep/fs9/users/scyiu/.uv-cache-takeover

root=$(pwd)

expected_runner_sha=$(sed -n 's/^QRES_EXPECTED_RUNNER_SHA256=//p' qres_expected_inputs.env)
expected_source_sha=$(sed -n 's/^QRES_EXPECTED_SOURCE_SHA256=//p' qres_expected_inputs.env)
test -n "$expected_runner_sha"
test -n "$expected_source_sha"

actual_runner_sha=$(sha256sum run_qres_v1.sh | awk '{print $1}')
test "$actual_runner_sha" = "$expected_runner_sha"
echo "ORION_QRES_RUNNER_HASH_GREEN sha256=$actual_runner_sha"

actual_source_sha=$(sha256sum source.tar.gz | awk '{print $1}')
test "$actual_source_sha" = "$expected_source_sha"
echo "ORION_QRES_SOURCE_ARCHIVE_HASH_GREEN sha256=$actual_source_sha"

rm -rf source private-venv qres-output
mkdir source
tar -xzf source.tar.gz -C source

env -u PYTHONPATH python3 -m venv private-venv
env -u PYTHONPATH private-venv/bin/python -m pip install \
  --disable-pip-version-check \
  --no-cache-dir \
  --quiet \
  'pytest==9.1.1' \
  'pygments==2.19.2' \
  'cryptography==50.0.0' \
  'defusedxml==0.7.1'
env -u PYTHONPATH private-venv/bin/python - <<'PY'
import cryptography
import defusedxml
import pygments
import pytest

assert cryptography.__version__ == "50.0.0"
assert defusedxml.__version__ == "0.7.1"
assert pygments.__version__ == "2.19.2"
assert pytest.__version__ == "9.1.1"
print("ORION_QRES_PRIVATE_ENVIRONMENT_GREEN")
PY
env -u PYTHONPATH private-venv/bin/python -m pip freeze --all > PRIVATE_ENVIRONMENT_FREEZE.txt

cd source
QRES_SLURM_JOB_ID="${SLURM_JOB_ID:-unset}" PYTHONPATH=src \
  "$root/private-venv/bin/python" \
  research/extensions/orion-qres/qres_v1_build.py \
  --repo . --out "$root/qres-output"
cd "$root"

# Receipt verification: terminal, mode-x, real slurm id, and every emitted
# output re-hashed against the receipt's sha256/bytes.
env -u PYTHONPATH private-venv/bin/python - <<'PY'
import hashlib
import json
import os

r = json.load(open("qres-output/complete/V1_Q_RESOURCE_JOB_RECEIPT_V1.json"))
assert r["terminal"] == "V1_QUANTUM_RESOURCE_ACCOUNTING_COMPLETE", r["terminal"]
assert r["execution_mode"] == "x"
assert r["slurm_job_id"] not in ("", None, "unset-local"), r["slurm_job_id"]
assert r["binding_checks_all_ok"] is True
for o in r["outputs"]:
    p = os.path.join("qres-output", o["path"])
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    assert h == o["sha256"], (p, h, o["sha256"])
    assert os.path.getsize(p) == o["bytes"], p
print("ORION_QRES_RECEIPT_GREEN slurm_job_id={}".format(r["slurm_job_id"]))
print("ORION_QRES_RECEIPT_TERMINAL {}".format(r["terminal"]))
print("ORION_QRES_NEGATIVE_TERMINAL_COUNTS {}".format(
    json.dumps(r["negative_terminal_counts"], sort_keys=True)))
print("ORION_QRES_INPUT_MANIFEST_SHA256_COMBINED {}".format(
    r["input_manifest_sha256_combined"]))
PY
echo "ORION_QRES_RUN_COMPLETE"
