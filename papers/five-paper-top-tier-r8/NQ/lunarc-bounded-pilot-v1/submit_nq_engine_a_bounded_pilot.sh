#!/bin/bash
set -euo pipefail

REPOSITORY="https://github.com/SzeChunYiu/ORION.git"
SOURCE_COMMIT="ce3ad440337c1bd413a8e5202c94a67374721403"
SOURCE_TREE="75230e3fdb53822139817ff744925d63220c193a"
AUTHORIZATION_PATH="papers/five-paper-top-tier-r8/NQ/lunarc-bounded-pilot-v1/LUNARC_AUTHORIZATION_PACKET.json"
ENGINE_PATH="papers/five-paper-top-tier-r8/NQ/engine-a-bounded-pilot-v1"
LUNARC_PATH="papers/five-paper-top-tier-r8/NQ/lunarc-bounded-pilot-v1"
RUNNER_PATH="papers/five-paper-top-tier-r8/NQ/lunarc-bounded-pilot-v1/run_nq_engine_a_bounded_pilot.slurm"
RUNNER_SHA256="26a8a32155ac204454d4f7ee68f898f706f21c15a817e7035052b6aae69e2ff7"
SUBMIT_SCRIPT_PATH="papers/five-paper-top-tier-r8/NQ/lunarc-bounded-pilot-v1/submit_nq_engine_a_bounded_pilot.sh"
SOURCE_MANIFEST_SHA256="b343b580411b87028b87af321e0b3ae44add4d066fe695c44cefb0527fac8045"
PROTOCOL_SHA256="059970ec26cd0767028a75aae92de70e53fbb0cb9f7439cff7696cc237351f69"
LOCAL_RECEIPT_SHA256="9c2380ccf5805f2fd3a47eaff757d0a113130a2a8728794c6ddb6b03e4c3e5d4"
NON_DUPLICATION_KEY="5bbd43879aedf49bf9ac5e80ee1cc7b5b7f835675c5850e186b2de6b95f62307"
REMOTE_OUTPUT_ROOT="/home/scyiu/orion-nq-engine-a-bounded-pilot/${NON_DUPLICATION_KEY}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel)"
LOCAL_SUBMIT_SCRIPT="${REPO_ROOT}/${SUBMIT_SCRIPT_PATH}"
LOCAL_AUTHORIZATION_PACKET="${SCRIPT_DIR}/LUNARC_AUTHORIZATION_PACKET.json"

packet_field() {
  python3 - "${LOCAL_AUTHORIZATION_PACKET}" "$1" <<'PY'
import json
import sys

value = json.loads(open(sys.argv[1], encoding="utf-8").read())
for part in sys.argv[2].split("."):
    value = value[part]
if not isinstance(value, str):
    raise SystemExit(f"packet field {sys.argv[2]} must be a string")
print(value)
PY
}

SUBMIT_SOURCE_COMMIT="$(packet_field submit_script_binding.commit)"
SUBMIT_SOURCE_TREE="$(packet_field submit_script_binding.tree)"
SUBMIT_SOURCE_PATH="$(packet_field submit_script_binding.path)"
SUBMIT_SOURCE_BLOB="$(packet_field submit_script_binding.git_blob)"
SUBMIT_SOURCE_SHA256="$(packet_field submit_script_binding.sha256)"

test "${SUBMIT_SOURCE_PATH}" = "${SUBMIT_SCRIPT_PATH}"
test "$(shasum -a 256 "${LOCAL_SUBMIT_SCRIPT}" | awk '{print $1}')" = \
  "${SUBMIT_SOURCE_SHA256}"
test "$(git -C "${REPO_ROOT}" rev-parse "${SUBMIT_SOURCE_COMMIT}^{tree}")" = \
  "${SUBMIT_SOURCE_TREE}"
test "$(git -C "${REPO_ROOT}" rev-parse "${SUBMIT_SOURCE_COMMIT}:${SUBMIT_SOURCE_PATH}")" = \
  "${SUBMIT_SOURCE_BLOB}"
test "$(git -C "${REPO_ROOT}" show "${SUBMIT_SOURCE_COMMIT}:${SUBMIT_SOURCE_PATH}" | shasum -a 256 | awk '{print $1}')" = \
  "${SUBMIT_SOURCE_SHA256}"

AUTHORIZATION_COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
AUTHORIZATION_TREE="$(git -C "${REPO_ROOT}" rev-parse 'HEAD^{tree}')"
AUTHORIZATION_SHA256="$(shasum -a 256 "${LOCAL_AUTHORIZATION_PACKET}" | awk '{print $1}')"
test "$(git -C "${REPO_ROOT}" rev-parse "${AUTHORIZATION_COMMIT}:${SUBMIT_SCRIPT_PATH}")" = \
  "${SUBMIT_SOURCE_BLOB}"
test "$(git -C "${REPO_ROOT}" rev-parse "${AUTHORIZATION_COMMIT}:${AUTHORIZATION_PATH}")" = \
  "$(git -C "${REPO_ROOT}" hash-object "${LOCAL_AUTHORIZATION_PACKET}")"
git -C "${REPO_ROOT}" merge-base --is-ancestor \
  "${SUBMIT_SOURCE_COMMIT}" "${AUTHORIZATION_COMMIT}"
git -C "${REPO_ROOT}" diff --quiet HEAD -- \
  "${SUBMIT_SCRIPT_PATH}" "${AUTHORIZATION_PATH}"
git -C "${REPO_ROOT}" diff --cached --quiet -- \
  "${SUBMIT_SCRIPT_PATH}" "${AUTHORIZATION_PATH}"

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
  "${SUBMIT_SOURCE_COMMIT}" \
  "${SUBMIT_SOURCE_TREE}" \
  "${SUBMIT_SOURCE_PATH}" \
  "${SUBMIT_SOURCE_BLOB}" \
  "${SUBMIT_SOURCE_SHA256}" \
  "${SOURCE_MANIFEST_SHA256}" \
  "${PROTOCOL_SHA256}" \
  "${LOCAL_RECEIPT_SHA256}" \
  "${NON_DUPLICATION_KEY}" \
  "${REMOTE_OUTPUT_ROOT}" \
  "${ENGINE_PATH}" \
  "${LUNARC_PATH}" <<'REMOTE_SCRIPT'
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
SUBMIT_SOURCE_COMMIT="${10}"
SUBMIT_SOURCE_TREE="${11}"
SUBMIT_SOURCE_PATH="${12}"
SUBMIT_SOURCE_BLOB="${13}"
SUBMIT_SOURCE_SHA256="${14}"
SOURCE_MANIFEST_SHA256="${15}"
PROTOCOL_SHA256="${16}"
LOCAL_RECEIPT_SHA256="${17}"
NON_DUPLICATION_KEY="${18}"
OUTPUT_ROOT="${19}"
ENGINE_PATH="${20}"
LUNARC_PATH="${21}"

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
git -C "${SOURCE_DIR}" config remote.origin.promisor true
git -C "${SOURCE_DIR}" config remote.origin.partialclonefilter blob:none
git -C "${SOURCE_DIR}" sparse-checkout init --no-cone
git -C "${SOURCE_DIR}" sparse-checkout set --no-cone \
  "/${ENGINE_PATH}/" "/${LUNARC_PATH}/"
git -C "${SOURCE_DIR}" fetch -q --no-tags --depth=1 --filter=blob:none \
  origin "${SOURCE_COMMIT}"
test "$(git -C "${SOURCE_DIR}" rev-parse FETCH_HEAD)" = "${SOURCE_COMMIT}"
git -C "${SOURCE_DIR}" checkout -q --detach "${SOURCE_COMMIT}"
test "$(git -C "${SOURCE_DIR}" rev-parse 'HEAD^{tree}')" = "${SOURCE_TREE}"
test -z "$(git -C "${SOURCE_DIR}" status --porcelain)"
test "$(sha256sum "${SOURCE_DIR}/${RUNNER_PATH}" | awk '{print $1}')" = "${RUNNER_SHA256}"

git -C "${SOURCE_DIR}" fetch -q --no-tags --depth=1 --filter=blob:none \
  origin "${AUTHORIZATION_COMMIT}"
test "$(git -C "${SOURCE_DIR}" rev-parse FETCH_HEAD)" = "${AUTHORIZATION_COMMIT}"
test "$(git -C "${SOURCE_DIR}" rev-parse "${AUTHORIZATION_COMMIT}^{tree}")" = \
  "${AUTHORIZATION_TREE}"
AUTHORIZATION_PACKET="${OUTPUT_ROOT}/LUNARC_AUTHORIZATION_PACKET.json"
git -C "${SOURCE_DIR}" show "${AUTHORIZATION_COMMIT}:${AUTHORIZATION_PATH}" > \
  "${AUTHORIZATION_PACKET}"
test "$(sha256sum "${AUTHORIZATION_PACKET}" | awk '{print $1}')" = \
  "${AUTHORIZATION_SHA256}"
test "$(git -C "${SOURCE_DIR}" rev-parse "${AUTHORIZATION_COMMIT}:${SUBMIT_SOURCE_PATH}")" = \
  "${SUBMIT_SOURCE_BLOB}"
git -C "${SOURCE_DIR}" fetch -q --no-tags --depth=1 --filter=blob:none \
  origin "${SUBMIT_SOURCE_COMMIT}"
test "$(git -C "${SOURCE_DIR}" rev-parse FETCH_HEAD)" = "${SUBMIT_SOURCE_COMMIT}"
test "$(git -C "${SOURCE_DIR}" rev-parse "${SUBMIT_SOURCE_COMMIT}^{tree}")" = \
  "${SUBMIT_SOURCE_TREE}"
test "$(git -C "${SOURCE_DIR}" rev-parse "${SUBMIT_SOURCE_COMMIT}:${SUBMIT_SOURCE_PATH}")" = \
  "${SUBMIT_SOURCE_BLOB}"
test "$(git -C "${SOURCE_DIR}" show "${SUBMIT_SOURCE_COMMIT}:${SUBMIT_SOURCE_PATH}" | sha256sum | awk '{print $1}')" = \
  "${SUBMIT_SOURCE_SHA256}"

module load GCCcore/13.2.0
module load Python/3.11.5
cd "${SOURCE_DIR}"
JOB_ID="$(sbatch --parsable \
  --account=lu2026-2-51 \
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
export SUBMIT_SOURCE_COMMIT SUBMIT_SOURCE_TREE SUBMIT_SOURCE_PATH SUBMIT_SOURCE_BLOB
export SUBMIT_SOURCE_SHA256
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
    "submit_script_commit": os.environ["SUBMIT_SOURCE_COMMIT"],
    "submit_script_tree": os.environ["SUBMIT_SOURCE_TREE"],
    "submit_script_path": os.environ["SUBMIT_SOURCE_PATH"],
    "submit_script_git_blob": os.environ["SUBMIT_SOURCE_BLOB"],
    "submit_script_sha256": os.environ["SUBMIT_SOURCE_SHA256"],
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
