#!/usr/bin/env bash
# Submit the CR-B full-census replay under an explicit nonduplication key.
#
# Usage (on a LUNARC login node):
#   NQ_CRB_AUTHORIZED_COMMIT=<full commit sha> \
#     slurm/submit_crb_full_census.sh /absolute/path/to/repository/checkout
#
# Exit codes:
#   0  submitted (job id printed on stdout; registry and record updated)
#   73 REFUSED_DUPLICATE  the derived key is already in the submission
#                         registry, or equals the terminal Engine-A pilot key
#   74 REFUSED_QUEUED     an equivalent job is already pending or running
#                         under this account
#   64 usage / identity failure before any submission attempt
#
# The key is derived exactly as documented in FULL_REPLAY_AUTHORIZATION.json:
# sha256 over the canonical JSON of the packet with the "nonduplication_key"
# and "submission" members removed, so the key identifies the authorized
# replay content and is invariant to submission bookkeeping.

set -euo pipefail

REFUSED_DUPLICATE=73
REFUSED_QUEUED=74
USAGE=64
JOB_NAME=orion-nq-r9-crb-full
ACCOUNT=hep2023-1-3
PILOT_KEY=5bbd43879aedf49bf9ac5e80ee1cc7b5b7f835675c5850e186b2de6b95f62307

if [[ $# -ne 1 || -z "${NQ_CRB_AUTHORIZED_COMMIT:-}" ]]; then
  echo "usage: NQ_CRB_AUTHORIZED_COMMIT=<sha> $0 <repository-checkout>" >&2
  exit "${USAGE}"
fi

REPOSITORY="$1"
ENGINE_ROOT="${REPOSITORY}/papers/five-paper-top-tier-r8/NQ/lunarc-r9/replay/engine_b"
REGISTRY="${ENGINE_ROOT}/slurm/crb_submission_registry.json"
RECORD="${ENGINE_ROOT}/slurm/crb_submission_record.json"

[[ -d "${REPOSITORY}/.git" ]] || { echo "not a git checkout: ${REPOSITORY}" >&2; exit "${USAGE}"; }
HEAD_COMMIT="$(git -C "${REPOSITORY}" rev-parse HEAD)"
[[ "${HEAD_COMMIT}" = "${NQ_CRB_AUTHORIZED_COMMIT}" ]] || {
  echo "checkout HEAD ${HEAD_COMMIT} is not the authorized commit" >&2
  exit "${USAGE}"
}
git -C "${REPOSITORY}" diff --quiet
git -C "${REPOSITORY}" diff --cached --quiet
[[ -f "${ENGINE_ROOT}/FULL_REPLAY_AUTHORIZATION.json" ]] || {
  echo "authorization packet missing" >&2
  exit "${USAGE}"
}

KEY="$(python3 - "${ENGINE_ROOT}/FULL_REPLAY_AUTHORIZATION.json" <<'PY'
import hashlib
import json
import sys

packet = json.loads(open(sys.argv[1], encoding="utf-8").read())
if packet.get("schema") != "ORION.NQ.EngineB.FullReplayAuthorization.v1":
    raise SystemExit("authorization packet schema mismatch")
payload = {
    key: value
    for key, value in packet.items()
    if key not in ("nonduplication_key", "submission")
}
print(hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
PY
)"
if [[ "${KEY}" = "${PILOT_KEY}" ]]; then
  echo "REFUSED_DUPLICATE: derived key equals the terminal Engine-A pilot key" >&2
  exit "${REFUSED_DUPLICATE}"
fi

if [[ -f "${REGISTRY}" ]]; then
  python3 - "${REGISTRY}" "${KEY}" <<'PY' || exit 73
import json
import sys

registry = json.loads(open(sys.argv[1], encoding="utf-8").read())
entries = registry.get("submissions", [])
for entry in entries:
    if entry.get("nonduplication_key") == sys.argv[2]:
        print(
            f"REFUSED_DUPLICATE: key already submitted as job {entry.get('job_id')}",
            file=sys.stderr,
        )
        raise SystemExit(73)
PY
fi

if squeue --account "${ACCOUNT}" --noheader --format '%j' | grep -qx "${JOB_NAME}"; then
  echo "REFUSED_QUEUED: ${JOB_NAME} is already pending or running" >&2
  exit "${REFUSED_QUEUED}"
fi

SUBMITTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
# sbatch records SLURM_SUBMIT_DIR from the invocation directory; the job
# script resolves the repository from it, so submit from the checkout root.
cd "${REPOSITORY}"
JOB_ID="$(
  NQ_CRB_AUTHORIZED_COMMIT="${NQ_CRB_AUTHORIZED_COMMIT}" \
    sbatch --parsable \
    --job-name "${JOB_NAME}" \
    --account "${ACCOUNT}" \
    "${ENGINE_ROOT}/slurm/job_nq_r9_crb_full_census.slurm"
)"
[[ "${JOB_ID}" =~ ^[0-9]+$ ]] || { echo "sbatch did not return a job id" >&2; exit "${USAGE}"; }

python3 - "${REGISTRY}" "${RECORD}" "${KEY}" "${JOB_ID}" "${HEAD_COMMIT}" "${SUBMITTED_AT}" <<'PY'
import json
import os
import sys

registry_path, record_path, key, job_id, commit, submitted = sys.argv[1:7]
try:
    registry = json.loads(open(registry_path, encoding="utf-8").read())
except FileNotFoundError:
    registry = {
        "schema": "ORION.NQ.EngineB.CRBSubmissionRegistry.v1",
        "submissions": [],
    }
if registry.get("schema") != "ORION.NQ.EngineB.CRBSubmissionRegistry.v1":
    raise SystemExit("submission registry schema mismatch")
registry["submissions"].append(
    {
        "nonduplication_key": key,
        "job_id": int(job_id),
        "authorized_commit": commit,
        "submitted_at_utc": submitted,
    }
)
with open(registry_path, "w", encoding="utf-8") as stream:
    json.dump(registry, stream, indent=2, sort_keys=True)
    stream.write("\n")
record = {
    "schema": "ORION.NQ.EngineB.CRBSubmissionRecord.v1",
    "nonduplication_key": key,
    "job_id": int(job_id),
    "authorized_commit": commit,
    "submitted_at_utc": submitted,
    "job_name": "orion-nq-r9-crb-full",
    "account": "hep2023-1-3",
    "partition": "hep",
    "pilot_key_status": "TERMINAL_FORBIDDEN_NOT_RESUBMITTED",
}
with open(record_path, "w", encoding="utf-8") as stream:
    json.dump(record, stream, indent=2, sort_keys=True)
    stream.write("\n")
PY

echo "submitted job ${JOB_ID} under nonduplication key ${KEY}"
