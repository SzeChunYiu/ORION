#!/usr/bin/env bash
#SBATCH --job-name=orion-nq-r8-engine-b
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=24:00:00
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err

set -euo pipefail

# The frozen terminal on allocation exhaustion is CANNOT_CHECK_RESOURCE_BOUND.
SUBJECT_COMMIT=0c451e862a0eeddac7c673813c4dc499f134b088
REPOSITORY="${SLURM_SUBMIT_DIR:?submit from the exact Engine B checkout}"
AUTHORIZED_COMMIT="${NQ_ENGINE_B_AUTHORIZED_COMMIT:?bind a separately reviewed authorization commit}"
ENGINE_ROOT="${REPOSITORY}/papers/five-paper-top-tier-r8/NQ/lunarc-r9/replay/engine_b"
INPUT_ROOT="${NQ_ENGINE_B_INPUT_ROOT:?bind the audited input bundle root}"
INPUT_MANIFEST="${NQ_ENGINE_B_INPUT_MANIFEST:?bind the audited input manifest}"
OUTPUT_ROOT="${ENGINE_ROOT}/results/${SLURM_JOB_ID}"
VENV="${SLURM_TMPDIR:?}/nq-engine-b-venv"

test "$(git -C "${REPOSITORY}" rev-parse HEAD)" = "${AUTHORIZED_COMMIT}"
git -C "${REPOSITORY}" diff --quiet
git -C "${REPOSITORY}" diff --cached --quiet
git -C "${REPOSITORY}" merge-base --is-ancestor "${SUBJECT_COMMIT}" HEAD
python3 -m venv "${VENV}"
"${VENV}/bin/python" -m pip install --disable-pip-version-check --no-input \
  --no-deps -r "${ENGINE_ROOT}/requirements.txt"
mkdir -p "${OUTPUT_ROOT}/proofs"

srun --cpu-bind=cores "${VENV}/bin/python" "${ENGINE_ROOT}/run_engine_b.py" \
  --mode execute \
  --subject-commit 0c451e862a0eeddac7c673813c4dc499f134b088 \
  --source-manifest "${ENGINE_ROOT}/SOURCE_MANIFEST.json" \
  --input-root "${INPUT_ROOT}" \
  --input-manifest "${INPUT_MANIFEST}" \
  --output "${OUTPUT_ROOT}/ENGINE_B_RECEIPT.json" \
  --certificates "${OUTPUT_ROOT}/ENGINE_B_CERTIFICATES.jsonl" \
  --proof-root "${OUTPUT_ROOT}/proofs" \
  --threads 32 \
  --max-wall-seconds 82800 \
  --solver g4

"${VENV}/bin/python" "${ENGINE_ROOT}/verify_receipt.py" \
  "${OUTPUT_ROOT}/ENGINE_B_RECEIPT.json" \
  --source-manifest "${ENGINE_ROOT}/SOURCE_MANIFEST.json"
