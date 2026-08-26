#!/usr/bin/env bash
#SBATCH --job-name=job-c-r8-1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=02:00:00
# Submit from an external run directory with a pre-created logs/ subdirectory.
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

set -euo pipefail

REPOSITORY="${ORION_REPOSITORY:?export the exact clean ORION checkout path}"
RUN_ROOT="${SLURM_SUBMIT_DIR:?submit from an external run directory}"
CLEANROOM="${REPOSITORY}/papers/five-paper-top-tier-r8/C/cleanroom"
PACKET="${REPOSITORY}/papers/five-paper-top-tier-r8/R8_PACKET_COMMIT.json"
AUTHORIZATION="${FIBERGUARD_EXECUTION_AUTHORIZATION:?export the reviewed external authorization path}"
OUTPUT="${RUN_ROOT}/results/JOB-C-R8-1-${SLURM_JOB_ID}.json"
PYTHON_BIN="${PYTHON_BIN:-python3}"

REPOSITORY_REAL="$(cd "${REPOSITORY}" && pwd -P)"
RUN_ROOT_REAL="$(cd "${RUN_ROOT}" && pwd -P)"
case "${RUN_ROOT_REAL}/" in
  "${REPOSITORY_REAL}/"*)
    echo "run directory must be outside the exact clean repository" >&2
    exit 2
    ;;
esac
mkdir -p "${RUN_ROOT}/results" "${RUN_ROOT}/environment"

cd "${REPOSITORY}"

{
  printf 'slurm_job_id=%s\n' "${SLURM_JOB_ID}"
  printf 'repository=%s\n' "${REPOSITORY_REAL}"
  printf 'run_root=%s\n' "${RUN_ROOT_REAL}"
  git rev-parse HEAD 'HEAD^{tree}'
  git status --porcelain=v1 --untracked-files=all
  "${PYTHON_BIN}" --version
  command -v "${PYTHON_BIN}"
  uname -a
  command -v lscpu >/dev/null 2>&1 && lscpu || true
  command -v module >/dev/null 2>&1 && module list 2>&1 || true
} >"${RUN_ROOT}/environment/JOB-C-R8-1-${SLURM_JOB_ID}.txt"

# run_replay checks the packet, exact manifest, external authorization, exact
# clean HEAD/tree, and adverse authority terminals before dispatching work.
srun --cpu-bind=cores "${PYTHON_BIN}" "${CLEANROOM}/run_replay.py" \
  --mode execute \
  --manifest "${CLEANROOM}/SOURCE_MANIFEST.json" \
  --packet-file "${PACKET}" \
  --authorization-file "${AUTHORIZATION}" \
  --repository "${REPOSITORY}" \
  --output "${OUTPUT}" \
  --workers 16

"${PYTHON_BIN}" "${CLEANROOM}/verify_receipt.py" \
  --root "${CLEANROOM}" \
  --manifest "${CLEANROOM}/SOURCE_MANIFEST.json" \
  --receipt "${OUTPUT}" \
  --authorization-file "${AUTHORIZATION}"
