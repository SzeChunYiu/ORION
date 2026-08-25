#!/bin/bash
#SBATCH --job-name=P2-DES-01
#SBATCH --account=lu2026-2-51
#SBATCH --partition=lu
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/home/scyiu/orion-executions/P2-DES-01/logs/%x_%j.out
#SBATCH --error=/home/scyiu/orion-executions/P2-DES-01/logs/%x_%j.err

set -euo pipefail
umask 077

: "${SOURCE_TAR:?SOURCE_TAR is required}"
: "${SOURCE_SHA256:?SOURCE_SHA256 is required}"
: "${FREEZE_SHA256:?FREEZE_SHA256 is required}"
: "${SUBJECT_SHA:?SUBJECT_SHA is required}"
: "${FREEZE_COMMIT:?FREEZE_COMMIT is required}"
: "${IMPLEMENTATION_SHA:?IMPLEMENTATION_SHA is required}"

ROOT="${SNIC_TMP:-/tmp}/${USER}/p2-des-01-${SLURM_JOB_ID}"
SOURCE_DIR="${ROOT}/source"
DATA_DIR="${ROOT}/data/trec-covid"
OUTPUT_DIR="${ROOT}/output"
REMOTE_RESULT="/home/scyiu/orion-executions/P2-DES-01/${SLURM_JOB_ID}"
mkdir -p "${SOURCE_DIR}" "${DATA_DIR}/qrels" "${OUTPUT_DIR}" "${REMOTE_RESULT}"

printf '%s  %s\n' "${SOURCE_SHA256}" "${SOURCE_TAR}" | sha256sum -c -
tar -xzf "${SOURCE_TAR}" -C "${SOURCE_DIR}"

# Compact job-local staging.  The shared data source and dirty remote ORION
# checkout are read-only; this job writes only below SNIC_TMP and REMOTE_RESULT.
cp /home/scyiu/orion-work/trec/trec-covid/corpus.jsonl "${DATA_DIR}/corpus.jsonl"
cp /home/scyiu/orion-work/trec/trec-covid/queries.jsonl "${DATA_DIR}/queries.jsonl"
cp /home/scyiu/orion-work/trec/trec-covid/qrels/test.tsv "${DATA_DIR}/qrels/test.tsv"

export PYTHONDONTWRITEBYTECODE=1
python3 "${SOURCE_DIR}/run_p2_des_01.py" \
  --data-root "${DATA_DIR}" \
  --output-dir "${OUTPUT_DIR}" \
  --freeze "${SOURCE_DIR}/FREEZE_V1.json" \
  --expected-freeze-sha256 "${FREEZE_SHA256}" \
  --subject-sha "${SUBJECT_SHA}" \
  --freeze-commit "${FREEZE_COMMIT}" \
  --implementation-sha "${IMPLEMENTATION_SHA}" \
  --source-archive-sha256 "${SOURCE_SHA256}"

cp -a "${OUTPUT_DIR}/." "${REMOTE_RESULT}/"
tar -C "${OUTPUT_DIR}" -czf "${REMOTE_RESULT}/P2-DES-01_RESULT_ARCHIVE_V1.tar.gz" .
sha256sum "${REMOTE_RESULT}/P2-DES-01_RESULT_ARCHIVE_V1.tar.gz" \
  > "${REMOTE_RESULT}/P2-DES-01_RESULT_ARCHIVE_V1.tar.gz.sha256"
sha256sum "${REMOTE_RESULT}"/*.json > "${REMOTE_RESULT}/SHA256SUMS"
printf 'P2_DES_01_REMOTE_PACKET_READY %s\n' "${REMOTE_RESULT}"

