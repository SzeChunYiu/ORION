#!/bin/bash
#SBATCH --job-name=o11-replay-v1
#SBATCH --account=lu2026-2-51
#SBATCH --partition=lu48
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:15:00
#SBATCH --output=/projects/hep/fs9/scratch/scyiu-orion-ci/orion11-lunarc-replay-v1/logs/%x-%j.out
#SBATCH --error=/projects/hep/fs9/scratch/scyiu-orion-ci/orion11-lunarc-replay-v1/logs/%x-%j.err

set -euo pipefail
umask 077

: "${SOURCE_TAR:?SOURCE_TAR is required}"
: "${SOURCE_ARCHIVE_SHA256:?SOURCE_ARCHIVE_SHA256 is required}"
: "${SOURCE_COMMIT:?SOURCE_COMMIT is required}"
: "${PROTOCOL_SHA256:?PROTOCOL_SHA256 is required}"
: "${JOB_SCRIPT_SHA256:?JOB_SCRIPT_SHA256 is required}"
: "${PYTHON_BIN:?PYTHON_BIN is required}"

BASE=/projects/hep/fs9/scratch/scyiu-orion-ci/orion11-lunarc-replay-v1
ROOT="${SNIC_TMP:-/tmp}/${USER}/orion11-replay-${SLURM_JOB_ID}"
SOURCE_DIR="${ROOT}/source"
OUTPUT_DIR="${ROOT}/output"
REMOTE_RESULT="${BASE}/results/${SLURM_JOB_ID}"
PROTOCOL_REL=papers/orion-11-recursive-epistemic-reconstruction/revival/r1-negative-revival-audit/lunarc-replay-v1/LUNARC_REPLAY_PROTOCOL_V1.json
DRIVER_REL=papers/orion-11-recursive-epistemic-reconstruction/revival/r1-negative-revival-audit/lunarc-replay-v1/run_orion11_lunarc_replay_v1.py
JOB_REL=papers/orion-11-recursive-epistemic-reconstruction/revival/r1-negative-revival-audit/lunarc-replay-v1/run_orion11_lunarc_replay_v1.sbatch

mkdir -p "${SOURCE_DIR}" "${REMOTE_RESULT}"
printf '%s  %s\n' "${SOURCE_ARCHIVE_SHA256}" "${SOURCE_TAR}" | sha256sum -c -
tar -xzf "${SOURCE_TAR}" -C "${SOURCE_DIR}"
printf '%s  %s\n' "${PROTOCOL_SHA256}" "${SOURCE_DIR}/${PROTOCOL_REL}" | sha256sum -c -
printf '%s  %s\n' "${JOB_SCRIPT_SHA256}" "${SOURCE_DIR}/${JOB_REL}" | sha256sum -c -
test -x "${PYTHON_BIN}"

set +e
env -u PYTHONHOME \
  PYTHONPATH="${SOURCE_DIR}/src${PYTHONPATH:+:${PYTHONPATH}}" \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONHASHSEED=0 \
  "${PYTHON_BIN}" "${SOURCE_DIR}/${DRIVER_REL}" \
    --repo-root "${SOURCE_DIR}" \
    --protocol "${SOURCE_DIR}/${PROTOCOL_REL}" \
    --expected-protocol-sha256 "${PROTOCOL_SHA256}" \
    --source-commit "${SOURCE_COMMIT}" \
    --source-archive-sha256 "${SOURCE_ARCHIVE_SHA256}" \
    --outdir "${OUTPUT_DIR}"
driver_rc=$?
set -e

if [[ -d "${OUTPUT_DIR}" ]]; then
  cp -a "${OUTPUT_DIR}/." "${REMOTE_RESULT}/"
fi
printf '%s\n' "${driver_rc}" > "${REMOTE_RESULT}/DRIVER_EXIT_CODE.txt"
(
  cd "${REMOTE_RESULT}"
  find . -type f ! -name SHA256SUMS -print0 \
    | sort -z \
    | xargs -0 sha256sum > SHA256SUMS
)
printf 'ORION11_LUNARC_REPLAY_PACKET %s DRIVER_EXIT=%s\n' "${REMOTE_RESULT}" "${driver_rc}"
exit "${driver_rc}"
