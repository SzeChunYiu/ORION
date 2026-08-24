#!/usr/bin/env bash
#SBATCH --job-name=p1-sab-archive-v1
#SBATCH --account=lu2026-2-51
#SBATCH --partition=lu48
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=01:00:00

set -euo pipefail
umask 077

: "${ORION_SAB_REMOTE_ROOT:=/projects/hep/fs10/scratch/scyiu/orion_scienceagentbench_v1}"
ARTIFACT_ROOT="${ORION_SAB_REMOTE_ROOT}/protected-artifact-v1"
SCRIPT_ROOT="${ORION_SAB_REMOTE_ROOT}/artifact-scripts-v1"
RECEIPT_ROOT="${ORION_SAB_REMOTE_ROOT}/artifact-receipt-v1"
ARCHIVE="${ARTIFACT_ROOT}/benchmark_verified.zip"
PARTIAL="${ARCHIVE}.partial-${SLURM_JOB_ID}"
EXTRACTED="${ARTIFACT_ROOT}/benchmark_verified_extracted"
MANIFEST="${RECEIPT_ROOT}/EXTRACTED_MANIFEST_V1.jsonl"
RECEIPT="${RECEIPT_ROOT}/LUNARC_ARTIFACT_STAGE_RECEIPT_V1.json"
URL='https://buckeyemailosu-my.sharepoint.com/:u:/g/personal/chen_8336_osu_edu/IQB870QrmuqwS5Ck33cHpJfkAVt3LsMeariREIwP3AT7byA?e=3ckueC&download=1'
COOKIE_JAR="${TMPDIR}/sab-sharepoint-cookie-${SLURM_JOB_ID}"
trap 'rm -f -- "${COOKIE_JAR}"' EXIT

mkdir -p "${ARTIFACT_ROOT}" "${RECEIPT_ROOT}"
chmod 700 "${ARTIFACT_ROOT}" "${RECEIPT_ROOT}"

if [[ ! -f "${ARCHIVE}" ]]; then
  curl --proto '=https' --tlsv1.2 --location --fail --show-error --silent \
    --retry 4 --retry-all-errors --connect-timeout 30 --max-time 3600 \
    --cookie-jar "${COOKIE_JAR}" --cookie "${COOKIE_JAR}" \
    --output "${PARTIAL}" "${URL}"
  chmod 600 "${PARTIAL}"
  [[ "$(stat -c %s "${PARTIAL}")" == '1769478786' ]]
  [[ "$(sha256sum "${PARTIAL}" | cut -d' ' -f1)" == '46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610' ]]
  mv "${PARTIAL}" "${ARCHIVE}"
fi

python3 "${SCRIPT_ROOT}/stage_archive_v1.py" \
  --archive "${ARCHIVE}" \
  --extract-root "${EXTRACTED}" \
  --manifest "${MANIFEST}" \
  --receipt "${RECEIPT}" \
  --password 'scienceagentbench'

sha256sum \
  "${RECEIPT}" \
  "${SCRIPT_ROOT}/stage_archive_v1.py" \
  "${SCRIPT_ROOT}/run_lunarc_archive_stage_v1.sh" \
  >"${RECEIPT_ROOT}/REMOTE_SHA256SUMS"

printf '%s\n' 'P1_SAB_LUNARC_PROTECTED_ARTIFACT_JOB_COMPLETE__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED'
