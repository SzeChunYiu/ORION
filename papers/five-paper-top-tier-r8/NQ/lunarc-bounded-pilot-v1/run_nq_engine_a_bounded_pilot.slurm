#!/bin/bash
#SBATCH --job-name=nq-ea-pilot
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:30:00

set -euo pipefail
umask 077

: "${NQ_EXPECTED_COMMIT:?missing NQ_EXPECTED_COMMIT}"
: "${NQ_EXPECTED_TREE:?missing NQ_EXPECTED_TREE}"
: "${NQ_EXPECTED_SOURCE_MANIFEST:?missing NQ_EXPECTED_SOURCE_MANIFEST}"
: "${NQ_EXPECTED_PROTOCOL:?missing NQ_EXPECTED_PROTOCOL}"
: "${NQ_EXPECTED_LOCAL_RECEIPT:?missing NQ_EXPECTED_LOCAL_RECEIPT}"
: "${NQ_NON_DUPLICATION_KEY:?missing NQ_NON_DUPLICATION_KEY}"
: "${NQ_AUTHORIZATION_PACKET:?missing NQ_AUTHORIZATION_PACKET}"
: "${NQ_AUTHORIZATION_PACKET_SHA256:?missing NQ_AUTHORIZATION_PACKET_SHA256}"
: "${NQ_OUTPUT_ROOT:?missing NQ_OUTPUT_ROOT}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
ENGINE_REL="papers/five-paper-top-tier-r8/NQ/engine-a-bounded-pilot-v1"
ENGINE_ROOT="${REPO_ROOT}/${ENGINE_REL}"
RUN_DIR="${NQ_OUTPUT_ROOT}/run-${SLURM_JOB_ID}"
mkdir -p "${RUN_DIR}"
printf '%s\n' 'CANNOT_CHECK_ENVIRONMENT' >"${RUN_DIR}/TERMINAL.txt"

test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${NQ_EXPECTED_COMMIT}"
test "$(git -C "${REPO_ROOT}" rev-parse 'HEAD^{tree}')" = "${NQ_EXPECTED_TREE}"
test -z "$(git -C "${REPO_ROOT}" status --porcelain --untracked-files=no)"
test "$(sha256sum "${ENGINE_ROOT}/SOURCE_MANIFEST.json" | awk '{print $1}')" = \
  "${NQ_EXPECTED_SOURCE_MANIFEST}"
test "$(sha256sum "${ENGINE_ROOT}/TARGET_RESOURCE_PILOT_PROTOCOL.json" | awk '{print $1}')" = \
  "${NQ_EXPECTED_PROTOCOL}"
test "$(sha256sum "${ENGINE_ROOT}/TARGET_RESOURCE_PILOT_RECEIPT.json" | awk '{print $1}')" = \
  "${NQ_EXPECTED_LOCAL_RECEIPT}"
test "$(sha256sum "${NQ_AUTHORIZATION_PACKET}" | awk '{print $1}')" = \
  "${NQ_AUTHORIZATION_PACKET_SHA256}"

python3 - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required")
PY

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="${ENGINE_ROOT}/src"
export ENGINE_ROOT RUN_DIR
python3 - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path

from nq_engine_a.manifest import canonical_json_bytes, sha256_file
from nq_engine_a.pilot import build_target_resource_pilot_receipt

engine = Path(os.environ["ENGINE_ROOT"])
run_dir = Path(os.environ["RUN_DIR"])
expected_source = os.environ["NQ_EXPECTED_SOURCE_MANIFEST"]
expected_nondup = os.environ["NQ_NON_DUPLICATION_KEY"]

observed = build_target_resource_pilot_receipt(
    engine,
    source_manifest_sha256=expected_source,
)
local = json.loads((engine / "TARGET_RESOURCE_PILOT_RECEIPT.json").read_text())

def semantic(value):
    if isinstance(value, dict):
        return {
            key: semantic(item)
            for key, item in value.items()
            if key not in {
                "elapsed_ns",
                "observed_resources",
                "future_slurm_pilot_envelope",
            }
        }
    if isinstance(value, list):
        return [semantic(item) for item in value]
    return value

if observed["non_duplication_key"] != expected_nondup:
    raise SystemExit("non-duplication key mismatch")
if semantic(observed) != semantic(local):
    raise SystemExit("LUNARC pilot semantic receipt differs from the frozen local receipt")

receipt_path = run_dir / "TARGET_RESOURCE_PILOT_RECEIPT.json"
receipt_path.write_bytes(canonical_json_bytes(observed))
metadata = {
    "schema_version": "nq-engine-a-lunarc-run-metadata-v1",
    "terminal": "COMPLETED_ENGINEERING_PILOT_ONLY__CANNOT_CHECK",
    "scientific_terminal": "CANNOT_CHECK",
    "independence_terminal": "CANNOT_CHECK",
    "exposure_markers": [
        "EXPECTED_OUTCOME_EXPOSURE",
        "ENGINE_B_EXPOSURE_IN_PRIOR_CONTEXT__CANNOT_CHECK",
    ],
    "slurm_job_id": os.environ["SLURM_JOB_ID"],
    "slurm_job_name": os.environ.get("SLURM_JOB_NAME"),
    "slurm_cpus_per_task": os.environ.get("SLURM_CPUS_PER_TASK"),
    "slurm_mem_per_node": os.environ.get("SLURM_MEM_PER_NODE"),
    "expected_commit": os.environ["NQ_EXPECTED_COMMIT"],
    "expected_tree": os.environ["NQ_EXPECTED_TREE"],
    "source_manifest_sha256": expected_source,
    "protocol_sha256": os.environ["NQ_EXPECTED_PROTOCOL"],
    "authorization_packet_sha256": os.environ["NQ_AUTHORIZATION_PACKET_SHA256"],
    "non_duplication_key": expected_nondup,
    "receipt_sha256": sha256_file(receipt_path),
    "full_census_executed": False,
    "two_engine_pass_increment": 0,
}
(run_dir / "LUNARC_RUN_METADATA.json").write_bytes(canonical_json_bytes(metadata))
PY

printf '%s  %s\n' \
  "$(sha256sum "${RUN_DIR}/TARGET_RESOURCE_PILOT_RECEIPT.json" | awk '{print $1}')" \
  'TARGET_RESOURCE_PILOT_RECEIPT.json' >"${RUN_DIR}/SHA256SUMS"
printf '%s  %s\n' \
  "$(sha256sum "${RUN_DIR}/LUNARC_RUN_METADATA.json" | awk '{print $1}')" \
  'LUNARC_RUN_METADATA.json' >>"${RUN_DIR}/SHA256SUMS"
printf '%s\n' 'COMPLETED_ENGINEERING_PILOT_ONLY__CANNOT_CHECK' >"${RUN_DIR}/TERMINAL.txt"
