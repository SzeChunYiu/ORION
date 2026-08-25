#!/bin/bash
set -euo pipefail

root=$(pwd)
expected_runner_sha=$(env -u PYTHONPATH python3 -c "import json; print(json.load(open('EXECUTION_PROTOCOL.json'))['inputs']['runner_sha256'])")
actual_runner_sha=$(sha256sum run_reference.sh | awk '{print $1}')
test "$actual_runner_sha" = "$expected_runner_sha"
echo "ORION_RUNNER_HASH_GREEN sha256=$actual_runner_sha"

test "$(sha256sum source.tar.gz | awk '{print $1}')" = "$(cat SOURCE_SHA256)"
rm -rf source private-venv
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
print("ORION_PRIVATE_ENVIRONMENT_GREEN")
PY
env -u PYTHONPATH private-venv/bin/python -m pip freeze --all > PRIVATE_ENVIRONMENT_FREEZE.txt

PYTHONPATH=source/src private-venv/bin/python - <<'PY'
import json
from orion.discovery.execution_takeover import validate_frozen_protocol

validate_frozen_protocol(json.load(open("EXECUTION_PROTOCOL.json")))
print("ORION_FROZEN_PROTOCOL_HASH_GREEN")
PY

cd source
cp research/orion-discovery-v3/FINITE_REFERENCE_RECEIPT_V1.json "$root/expected-finite-receipt.json"
PYTHONPATH=src "$root/private-venv/bin/python" scripts/check_orion_discovery_v3.py
PYTHONPATH=src "$root/private-venv/bin/python" scripts/check_orion_execution_takeover.py
PYTHONPATH=src "$root/private-venv/bin/python" -m pytest -q \
  tests/unit/discovery/test_frontier_dominance.py \
  tests/unit/discovery/test_execution_takeover.py
PYTHONPATH=src "$root/private-venv/bin/python" scripts/run_frontier_dominance_census_v1.py
cmp "$root/expected-finite-receipt.json" research/orion-discovery-v3/FINITE_REFERENCE_RECEIPT_V1.json
"$root/private-venv/bin/python" -m compileall -q \
  src/orion/discovery/frontier_dominance.py \
  src/orion/discovery/execution_takeover.py \
  scripts/check_orion_discovery_v3.py \
  scripts/check_orion_execution_takeover.py \
  scripts/freeze_orion_execution_job.py \
  scripts/package_orion_slurm_job.py \
  scripts/run_frontier_dominance_census_v1.py
cd "$root"

env -u PYTHONPATH private-venv/bin/python - <<'PY'
import cryptography
import defusedxml
import hashlib
import json
import os
import platform
import pygments
import pytest

protocol = json.load(open("EXECUTION_PROTOCOL.json"))
receipt = {
    "schema": "orion.discovery.v3.lunarc-engineering-reference-receipt.v1",
    "job_id": protocol["job_id"],
    "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
    "slurm_node": os.environ.get("SLURMD_NODENAME"),
    "source_git_sha": protocol["source_git_sha"],
    "protocol_sha256": protocol["protocol_sha256"],
    "submission_key": os.environ["ORION_SUBMISSION_KEY"],
    "runner_sha256": hashlib.sha256(open("run_reference.sh", "rb").read()).hexdigest(),
    "source_archive_sha256": hashlib.sha256(open("source.tar.gz", "rb").read()).hexdigest(),
    "environment": {
        "python": platform.python_version(),
        "cryptography": cryptography.__version__,
        "defusedxml": defusedxml.__version__,
        "pygments": pygments.__version__,
        "pytest": pytest.__version__,
        "platform": platform.platform(),
        "install_pythonpath": "UNSET",
        "repository_runtime_pythonpath": "source/src",
    },
    "checks": {
        "runner_hash": 0,
        "private_environment": 0,
        "frozen_protocol_hash": 0,
        "structure": 0,
        "takeover_manifest": 0,
        "hostile_tests": 0,
        "finite_census": 0,
        "finite_receipt_byte_comparison": 0,
        "compileall": 0,
    },
    "terminal": "ENGINEERING_REFERENCE_CHECK_ONLY_GREEN",
    "scientific_authority": "NONE",
    "paper_authority_delta": "NONE",
    "external_novelty": "CANNOT_CHECK",
}
with open("ENGINEERING_REFERENCE_RECEIPT.json", "x") as handle:
    json.dump(receipt, handle, sort_keys=True, indent=2)
    handle.write("\n")
print("ORION_LUNARC_ENGINEERING_REFERENCE_GREEN")
PY
