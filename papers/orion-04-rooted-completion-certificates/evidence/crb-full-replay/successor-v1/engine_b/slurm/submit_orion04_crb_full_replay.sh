#!/usr/bin/env bash
# Submit exactly one operator-attested ORION-04 CR-B replay attempt.
#
# Usage:
#   ORION04_CRB_AUTHORIZATION_PATH=/shared/reviewed-authorization.json \
#     slurm/submit_orion04_crb_full_replay.sh /absolute/repository/checkout
#
# The request must bind the exact checkout commit, source-manifest digest, a
# new nonduplication key, an unused durable root, and the shared global
# registry root. The script verifies only those bindings. The operator label
# is unverified input and cannot establish externality or scientific authority.

set -Eeuo pipefail
export PYTHONDONTWRITEBYTECODE=1

USAGE=64
REFUSED_DUPLICATE=73
REFUSED_ACTIVE=74
JOB_NAME=orion-04-crb-replay
ACCOUNT=hep2023-1-3

if [[ $# -ne 1 || -z "${ORION04_CRB_AUTHORIZATION_PATH:-}" ]]; then
  echo "usage: ORION04_CRB_AUTHORIZATION_PATH=/absolute/auth.json $0 /absolute/repository" >&2
  exit "${USAGE}"
fi

REPOSITORY="$1"
AUTHORIZATION_PATH="${ORION04_CRB_AUTHORIZATION_PATH}"
ENGINE_RELATIVE="papers/orion-04-rooted-completion-certificates/evidence/crb-full-replay/successor-v1/engine_b"
ENGINE_ROOT="${REPOSITORY}/${ENGINE_RELATIVE}"
SUCCESSOR_ROOT="${ENGINE_ROOT}/.."
SOURCE_MANIFEST="${ENGINE_ROOT}/SOURCE_MANIFEST.json"
PREBIND="${SUCCESSOR_ROOT}/GLOBAL_REGISTRY_PREBIND_V1.json"
JOB_SCRIPT="${ENGINE_ROOT}/slurm/job_orion04_crb_full_replay.slurm"

[[ "${REPOSITORY}" = /* && "${AUTHORIZATION_PATH}" = /* ]] || {
  echo "repository and authorization paths must be absolute" >&2
  exit "${USAGE}"
}
git -C "${REPOSITORY}" rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "not a git checkout: ${REPOSITORY}" >&2
  exit "${USAGE}"
}
[[ -f "${AUTHORIZATION_PATH}" && ! -L "${AUTHORIZATION_PATH}" ]] || {
  echo "AWAITING_NEW_ONE_SHOT_AUTHORIZATION: operator request missing or unsafe" >&2
  exit "${USAGE}"
}
python3 - "${REPOSITORY}" "${AUTHORIZATION_PATH}" <<'PY'
import sys
from pathlib import Path
repository = Path(sys.argv[1]).resolve()
authorization = Path(sys.argv[2]).resolve()
if authorization == repository or repository in authorization.parents:
    raise SystemExit("authorization must be external to the repository checkout")
PY

HEAD_COMMIT="$(git -C "${REPOSITORY}" rev-parse HEAD)"
git -C "${REPOSITORY}" diff --quiet
git -C "${REPOSITORY}" diff --cached --quiet
test -z "$(git -C "${REPOSITORY}" status --porcelain --untracked-files=all)"
test -z "$(find "${REPOSITORY}" -type f \( -name '*.pyc' -o -name '*.pyo' \) -print -quit)"
python3 "${ENGINE_ROOT}/build_manifest.py" --verify \
  --root "${ENGINE_ROOT}" --output "${SOURCE_MANIFEST}"
SOURCE_MANIFEST_SHA256="$(python3 - "${SOURCE_MANIFEST}" <<'PY'
import json
import sys
print(json.loads(open(sys.argv[1], encoding="utf-8").read())["manifest_sha256"])
PY
)"

VALIDATION_JSON="$(python3 "${ENGINE_ROOT}/submission_gate.py" validate \
  --authorization "${AUTHORIZATION_PATH}" --expected-commit "${HEAD_COMMIT}" \
  --source-manifest-sha256 "${SOURCE_MANIFEST_SHA256}")"
NON_DUPLICATION_KEY="$(python3 - "${VALIDATION_JSON}" <<'PY'
import json
import sys
print(json.loads(sys.argv[1])["nonduplication_key"])
PY
)"
DURABLE_ROOT="$(python3 - "${VALIDATION_JSON}" <<'PY'
import json
import sys
print(json.loads(sys.argv[1])["durable_root"])
PY
)"
GLOBAL_REGISTRY_ROOT="$(python3 - "${VALIDATION_JSON}" <<'PY'
import json
import sys
print(json.loads(sys.argv[1])["global_registry_root"])
PY
)"
python3 - "${VALIDATION_JSON}" <<'PY'
import json
import sys
receipt = json.loads(sys.argv[1])
expected = {
    "terminal": "ORION04_ONE_SHOT_REQUEST_BINDINGS_VALID",
    "operator_attestation": "USER_SUPPLIED_UNVERIFIED_BY_MACHINE",
    "machine_established_externality": False,
    "machine_established_identity": False,
    "scientific_authority_delta": "NONE",
}
for key, value in expected.items():
    if receipt.get(key) != value:
        raise SystemExit(f"one-shot request validation receipt mismatch: {key}")
PY

[[ -d "${GLOBAL_REGISTRY_ROOT}" && ! -L "${GLOBAL_REGISTRY_ROOT}" ]] || {
  echo "REFUSED_GLOBAL_REGISTRY_UNAVAILABLE: ${GLOBAL_REGISTRY_ROOT}" >&2
  exit "${USAGE}"
}
[[ ! -e "${DURABLE_ROOT}" && -d "$(dirname "${DURABLE_ROOT}")" ]] || {
  echo "REFUSED_DURABLE_ROOT_NOT_FRESH: ${DURABLE_ROOT}" >&2
  exit "${USAGE}"
}
if squeue --account "${ACCOUNT}" --noheader --format '%j' | grep -qx "${JOB_NAME}"; then
  echo "REFUSED_ACTIVE: ${JOB_NAME} is already pending or running" >&2
  exit "${REFUSED_ACTIVE}"
fi

# Reservation is atomic under flock. Every failure after this point consumes
# the new key and is written as failure custody; no retry may reuse it.
python3 "${ENGINE_ROOT}/submission_gate.py" reserve \
  --authorization "${AUTHORIZATION_PATH}" --expected-commit "${HEAD_COMMIT}" \
  --source-manifest-sha256 "${SOURCE_MANIFEST_SHA256}" \
  --global-root "${GLOBAL_REGISTRY_ROOT}" --prebind "${PREBIND}" >/dev/null || {
    echo "REFUSED_DUPLICATE_OR_ACTIVE: global reservation failed" >&2
    exit "${REFUSED_DUPLICATE}"
  }

RESERVATION_ACTIVE=1
SUBMISSION_STAGE=POST_RESERVATION_SETUP
SUBMISSION_COMMAND=post-reservation-setup
JOB_ID=""

reconcile_submission_failure() {
  local status="$?"
  if [[ "${status}" -eq 0 || "${RESERVATION_ACTIVE}" -ne 1 ]]; then
    return "${status}"
  fi
  set +e
  trap - ERR EXIT
  local reconciliation=NOT_APPLICABLE_NO_JOB_ID
  if [[ "${JOB_ID}" =~ ^[0-9]+$ ]]; then
    if scancel "${JOB_ID}"; then
      local observed
      if observed="$(squeue --noheader --jobs "${JOB_ID}" --format '%i' 2>/dev/null)"; then
        if [[ -z "${observed}" ]]; then
          reconciliation=CANCELLED_OR_ABSENT_CONFIRMED
        else
          reconciliation=CANCEL_REQUESTED_STILL_VISIBLE
        fi
      else
        reconciliation=CANNOT_CHECK_SCHEDULER
      fi
    else
      reconciliation=CANCEL_REQUEST_FAILED
    fi
  fi

  local terminalize=(
    python3 "${ENGINE_ROOT}/submission_gate.py" terminalize
    --global-root "${GLOBAL_REGISTRY_ROOT}" --prebind "${PREBIND}"
    --key "${NON_DUPLICATION_KEY}"
    --failure-stage "${SUBMISSION_STAGE}" --failure-exit-code "${status}"
    --failure-command "${SUBMISSION_COMMAND}"
    --scheduler-reconciliation "${reconciliation}"
  )
  if [[ "${JOB_ID}" =~ ^[0-9]+$ ]]; then
    terminalize+=(--job-id "${JOB_ID}")
  fi
  local registry_terminalization=TERMINALIZED
  "${terminalize[@]}" >/dev/null || registry_terminalization=FAILED_CANNOT_CHECK

  if [[ -d "${DURABLE_ROOT}" ]]; then
    local failure_receipt=(
      python3 "${ENGINE_ROOT}/replay_custody.py" submission-failure "${DURABLE_ROOT}"
      --exit-code "${status}" --stage "${SUBMISSION_STAGE}"
      --command "${SUBMISSION_COMMAND}" --nonduplication-key "${NON_DUPLICATION_KEY}"
      --scheduler-reconciliation "${reconciliation}"
      --registry-terminalization "${registry_terminalization}"
    )
    if [[ "${JOB_ID}" =~ ^[0-9]+$ ]]; then
      failure_receipt+=(--job-id "${JOB_ID}")
    fi
    "${failure_receipt[@]}" >/dev/null 2>&1 || \
      printf 'ORION04_SUBMISSION_FAILURE_RECEIPT_FALLBACK\nstatus=%s\nstage=%s\nregistry=%s\nscheduler=%s\n' \
        "${status}" "${SUBMISSION_STAGE}" "${registry_terminalization}" \
        "${reconciliation}" > "${DURABLE_ROOT}/SUBMISSION_FAILURE_FALLBACK.txt"
  fi
  exit "${status}"
}

trap reconcile_submission_failure EXIT

SUBMISSION_STAGE=DURABLE_ROOT_CREATE
SUBMISSION_COMMAND=mkdir-durable-root
mkdir -m 700 "${DURABLE_ROOT}"
AUTHORIZATION_COPY="${DURABLE_ROOT}/ONE_SHOT_AUTHORIZATION.json"
SUBMISSION_STAGE=OPERATOR_REQUEST_COPY
SUBMISSION_COMMAND=copy-and-verify-operator-request
cp "${AUTHORIZATION_PATH}" "${AUTHORIZATION_COPY}"
test "$(sha256sum "${AUTHORIZATION_PATH}" | awk '{print $1}')" = \
  "$(sha256sum "${AUTHORIZATION_COPY}" | awk '{print $1}')"

cd "${REPOSITORY}"
SUBMISSION_STAGE=SBATCH_HELD_SUBMISSION
SUBMISSION_COMMAND=sbatch-held-submission
set +e
JOB_ID="$(sbatch --parsable --hold \
  --job-name "${JOB_NAME}" --account "${ACCOUNT}" \
  --output "${DURABLE_ROOT}/SLURM_STDOUT-%j.txt" \
  --error "${DURABLE_ROOT}/SLURM_STDERR-%j.txt" \
  --export="ALL,ORION04_CRB_AUTHORIZED_COMMIT=${HEAD_COMMIT},ORION04_CRB_AUTHORIZATION_PATH=${AUTHORIZATION_COPY},ORION04_CRB_SOURCE_MANIFEST_SHA256=${SOURCE_MANIFEST_SHA256},ORION04_CRB_NON_DUPLICATION_KEY=${NON_DUPLICATION_KEY},ORION04_CRB_DURABLE_ROOT=${DURABLE_ROOT},ORION04_CRB_GLOBAL_REGISTRY_ROOT=${GLOBAL_REGISTRY_ROOT}" \
  "${JOB_SCRIPT}")"
SBATCH_STATUS=$?
set -e
if [[ "${SBATCH_STATUS}" -ne 0 || ! "${JOB_ID}" =~ ^[0-9]+$ ]]; then
  [[ "${SBATCH_STATUS}" -ne 0 ]] && exit "${SBATCH_STATUS}"
  exit "${USAGE}"
fi

SUBMISSION_STAGE=REGISTRY_BIND_HELD_JOB
SUBMISSION_COMMAND=bind-held-job-in-global-registry
python3 "${ENGINE_ROOT}/submission_gate.py" commit \
  --global-root "${GLOBAL_REGISTRY_ROOT}" --prebind "${PREBIND}" \
  --key "${NON_DUPLICATION_KEY}" --job-id "${JOB_ID}" >/dev/null
SUBMISSION_STAGE=SUBMISSION_RECORD
SUBMISSION_COMMAND=write-durable-submission-record
python3 - "${DURABLE_ROOT}/SUBMISSION_RECORD.json" "${NON_DUPLICATION_KEY}" \
  "${JOB_ID}" "${HEAD_COMMIT}" "${SOURCE_MANIFEST_SHA256}" \
  "${GLOBAL_REGISTRY_ROOT}" <<'PY'
import json
import os
import sys
from datetime import datetime, timezone
path, key, job_id, commit, source, registry = sys.argv[1:7]
record = {
    "schema": "ORION.ORION04.CRB.SubmissionRecord.v1",
    "paper_id": "ORION-04",
    "nonduplication_key": key,
    "job_id": int(job_id),
    "successor_commit": commit,
    "source_manifest_sha256": source,
    "global_registry_root": registry,
    "submitted_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "operator_attestation": "USER_SUPPLIED_UNVERIFIED_BY_MACHINE",
    "machine_established_externality": False,
    "scientific_authority_delta": "NONE",
}
temporary = f"{path}.{os.getpid()}.tmp"
with open(temporary, "w", encoding="utf-8") as stream:
    json.dump(record, stream, indent=2, sort_keys=True)
    stream.write("\n")
os.replace(temporary, path)
PY
SUBMISSION_STAGE=RELEASE_HELD_JOB
SUBMISSION_COMMAND="scontrol release ${JOB_ID}"
scontrol release "${JOB_ID}"
RESERVATION_ACTIVE=0
trap - EXIT

echo "submitted held-then-bound job ${JOB_ID} under new key ${NON_DUPLICATION_KEY}"
