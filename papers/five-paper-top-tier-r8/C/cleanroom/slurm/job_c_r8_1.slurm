#!/usr/bin/env bash
#SBATCH --job-name=job-c-r8-1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=papers/five-paper-top-tier-r8/C/cleanroom/lunarc-%j.out
#SBATCH --error=papers/five-paper-top-tier-r8/C/cleanroom/lunarc-%j.err

set -euo pipefail

REPOSITORY="${SLURM_SUBMIT_DIR:?submit from the exact clean-room repository checkout}"
CLEANROOM="${REPOSITORY}/papers/five-paper-top-tier-r8/C/cleanroom"
PACKET="${REPOSITORY}/papers/five-paper-top-tier-r8/R8_PACKET_COMMIT.json"
OUTPUT="${CLEANROOM}/JOB-C-R8-1-${SLURM_JOB_ID}.json"
PYTHON_BIN="${PYTHON_BIN:-python3}"

cd "${REPOSITORY}"

# run_replay checks the packet identity before dispatching exhaustive work.
srun --cpu-bind=cores "${PYTHON_BIN}" "${CLEANROOM}/run_replay.py" \
  --mode execute \
  --manifest "${CLEANROOM}/SOURCE_MANIFEST.json" \
  --packet-file "${PACKET}" \
  --repository "${REPOSITORY}" \
  --output "${OUTPUT}" \
  --workers 16

"${PYTHON_BIN}" "${CLEANROOM}/verify_receipt.py" \
  --root "${CLEANROOM}" \
  --manifest "${CLEANROOM}/SOURCE_MANIFEST.json" \
  --receipt "${OUTPUT}"
