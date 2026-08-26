#!/bin/bash
set -euo pipefail

REPOSITORY="https://github.com/SzeChunYiu/ORION.git"
SOURCE_COMMIT="ce3ad440337c1bd413a8e5202c94a67374721403"
SOURCE_TREE="75230e3fdb53822139817ff744925d63220c193a"
AUTHORIZATION_COMMIT="69ec8d24814dda88162b9ef12a0b506616f47a32"
AUTHORIZATION_TREE="45a69c92288e5d0bbbe16377d084a7f076f1ebb3"
AUTHORIZATION_PATH="papers/five-paper-top-tier-r8/NQ/lunarc-bounded-pilot-v1/LUNARC_AUTHORIZATION_PACKET.json"
AUTHORIZATION_SHA256="204e6492632cf8ac36c01ed8eaa9413cf4926b9a4ddf5a0e1741aad4b66b5d6f"
RUNNER_PATH="papers/five-paper-top-tier-r8/NQ/lunarc-bounded-pilot-v1/run_nq_engine_a_bounded_pilot.slurm"
RUNNER_SHA256="26a8a32155ac204454d4f7ee68f898f706f21c15a817e7035052b6aae69e2ff7"
SOURCE_MANIFEST_SHA256="b343b580411b87028b87af321e0b3ae44add4d066fe695c44cefb0527fac8045"
PROTOCOL_SHA256="059970ec26cd0767028a75aae92de70e53fbb0cb9f7439cff7696cc237351f69"
LOCAL_RECEIPT_SHA256="9c2380ccf5805f2fd3a47eaff757d0a113130a2a8728794c6ddb6b03e4c3e5d4"
NON_DUPLICATION_KEY="5bbd43879aedf49bf9ac5e80ee1cc7b5b7f835675c5850e186b2de6b95f62307"
REMOTE_OUTPUT_ROOT="/home/scyiu/orion-nq-engine-a-bounded-pilot/${NON_DUPLICATION_KEY}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_AUTHORIZATION_PACKET="${SCRIPT_DIR}/LUNARC_AUTHORIZATION_PACKET.json"
test "$(shasum -a 256 "${LOCAL_AUTHORIZATION_PACKET}" | awk '{print $1}')" = \
  "${AUTHORIZATION_SHA256}"

ssh -O check lunarc 2>/dev/null && echo "Connected" || /Users/billy/lunarc-init.sh

ssh lunarc bash -s -- \
  "${REPOSITORY}" \
  "${SOURCE_COMMIT}" \
  "${SOURCE_TREE}" \
  "${AUTHORIZATION_COMMIT}" \
  "${AUTHORIZATION_TREE}" \
  "${AUTHORIZATION_PATH}" \
  "${AUTHORIZATION_SHA256}" \
  "${RUNNER_PATH}" \
  "${RUNNER_SHA256}" \
  "${SOURCE_MANIFEST_SHA256}" \
  "${PROTOCOL_SHA256}" \
  "${LOCAL_RECEIPT_SHA256}" \
  "${NON_DUPLICATION_KEY}" \
  "${REMOTE_OUTPUT_ROOT}" <<'REMOTE_SCRIPT'
set -euo pipefail
umask 077

REPOSITORY="$1"
SOURCE_COMMIT="$2"
SOURCE_TREE="$3"
AUTHORIZATION_COMMIT="$4"
AUTHORIZATION_TREE="$5"
AUTHORIZATION_PATH="$6"
AUTHORIZATION_SHA256="$7"
RUNNER_PATH="$8"
RUNNER_SHA256="$9"
SOURCE_MANIFEST_SHA256="${10}"
PROTOCOL_SHA256="${11}"
LOCAL_RECEIPT_SHA256="${12}"
NON_DUPLICATION_KEY="${13}"
OUTPUT_ROOT="${14}"

if test -e "${OUTPUT_ROOT}"; then
  echo "Refusing duplicate: non-duplication root already exists: ${OUTPUT_ROOT}" >&2
  exit 73
fi
if squeue -h -u "${USER}" -n nq-ea-pilot | grep -q .; then
  echo "Refusing duplicate: an nq-ea-pilot job is already queued or running" >&2
  exit 74
fi

mkdir -p "$(dirname "${OUTPUT_ROOT}")"
mkdir "${OUTPUT_ROOT}"
mkdir "${OUTPUT_ROOT}/.submission-lock"
SUBMITTED=0
cleanup() {
  if test "${SUBMITTED}" = 0; then
    rm -rf "${OUTPUT_ROOT}"
  fi
}
trap cleanup EXIT

SOURCE_DIR="${OUTPUT_ROOT}/source"
git init -q "${SOURCE_DIR}"
git -C "${SOURCE_DIR}" remote add origin "${REPOSITORY}"
git -C "${SOURCE_DIR}" fetch -q --no-tags --depth=1 origin "${SOURCE_COMMIT}"
test "$(git -C "${SOURCE_DIR}" rev-parse FETCH_HEAD)" = "${SOURCE_COMMIT}"
git -C "${SOURCE_DIR}" checkout -q --detach "${SOURCE_COMMIT}"
test "$(git -C "${SOURCE_DIR}" rev-parse 'HEAD^{tree}')" = "${SOURCE_TREE}"
test -z "$(git -C "${SOURCE_DIR}" status --porcelain)"
test "$(sha256sum "${SOURCE_DIR}/${RUNNER_PATH}" | awk '{print $1}')" = "${RUNNER_SHA256}"

git -C "${SOURCE_DIR}" fetch -q --no-tags --depth=1 origin "${AUTHORIZATION_COMMIT}"
test "$(git -C "${SOURCE_DIR}" rev-parse FETCH_HEAD)" = "${AUTHORIZATION_COMMIT}"
test "$(git -C "${SOURCE_DIR}" rev-parse "${AUTHORIZATION_COMMIT}^{tree}")" = \
  "${AUTHORIZATION_TREE}"
AUTHORIZATION_PACKET="${OUTPUT_ROOT}/LUNARC_AUTHORIZATION_PACKET.json"
git -C "${SOURCE_DIR}" show "${AUTHORIZATION_COMMIT}:${AUTHORIZATION_PATH}" > \
  "${AUTHORIZATION_PACKET}"
test "$(sha256sum "${AUTHORIZATION_PACKET}" | awk '{print $1}')" = \
  "${AUTHORIZATION_SHA256}"

module load Python/3.11.5-GCCcore-13.2.0
cd "${SOURCE_DIR}"
JOB_ID="$(sbatch --parsable \
  --partition=lu48 \
  --nodes=1 \
  --ntasks=1 \
  --cpus-per-task=1 \
  --mem=4G \
  --time=00:30:00 \
  --job-name=nq-ea-pilot \
  --output="${OUTPUT_ROOT}/slurm-%j.out" \
  --export="ALL,NQ_EXPECTED_COMMIT=${SOURCE_COMMIT},NQ_EXPECTED_TREE=${SOURCE_TREE},NQ_EXPECTED_SOURCE_MANIFEST=${SOURCE_MANIFEST_SHA256},NQ_EXPECTED_PROTOCOL=${PROTOCOL_SHA256},NQ_EXPECTED_LOCAL_RECEIPT=${LOCAL_RECEIPT_SHA256},NQ_NON_DUPLICATION_KEY=${NON_DUPLICATION_KEY},NQ_AUTHORIZATION_PACKET=${AUTHORIZATION_PACKET},NQ_AUTHORIZATION_PACKET_SHA256=${AUTHORIZATION_SHA256},NQ_OUTPUT_ROOT=${OUTPUT_ROOT}" \
  "${RUNNER_PATH}")"
SUBMITTED=1

export JOB_ID OUTPUT_ROOT SOURCE_COMMIT SOURCE_TREE AUTHORIZATION_COMMIT AUTHORIZATION_TREE
export AUTHORIZATION_SHA256 NON_DUPLICATION_KEY
python3 - <<'PY'
import json
import os
from pathlib import Path

payload = {
    "schema_version": "nq-engine-a-lunarc-submission-v1",
    "job_id": os.environ["JOB_ID"],
    "output_root": os.environ["OUTPUT_ROOT"],
    "source_commit": os.environ["SOURCE_COMMIT"],
    "source_tree": os.environ["SOURCE_TREE"],
    "authorization_commit": os.environ["AUTHORIZATION_COMMIT"],
    "authorization_tree": os.environ["AUTHORIZATION_TREE"],
    "authorization_packet_sha256": os.environ["AUTHORIZATION_SHA256"],
    "non_duplication_key": os.environ["NON_DUPLICATION_KEY"],
    "authority": "engineering_resource_pilot_only",
    "scientific_terminal": "CANNOT_CHECK",
    "full_census_authorized": False,
}
path = Path(os.environ["OUTPUT_ROOT"]) / "SUBMISSION.json"
path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
PY
printf '%s\n' "Submitted bounded NQ pilot job ${JOB_ID}"
printf '%s\n' "Output root: ${OUTPUT_ROOT}"
trap - EXIT
REMOTE_SCRIPT
