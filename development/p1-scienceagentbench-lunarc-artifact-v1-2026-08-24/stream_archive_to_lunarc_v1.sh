#!/usr/bin/env bash
# Stream the public archive through the verified local transport without
# retaining payload bytes on the local disk.
set -euo pipefail
umask 077

: "${ORION_SAB_REMOTE_ROOT:=/projects/hep/fs10/scratch/scyiu/orion_scienceagentbench_v1}"
URL='https://buckeyemailosu-my.sharepoint.com/:u:/g/personal/chen_8336_osu_edu/IQB870QrmuqwS5Ck33cHpJfkAVt3LsMeariREIwP3AT7byA?e=3ckueC&download=1'
REMOTE_ARCHIVE="${ORION_SAB_REMOTE_ROOT}/protected-artifact-v1/benchmark_verified.zip"
REMOTE_PARTIAL="${REMOTE_ARCHIVE}.stream-partial-$$"
COOKIE_JAR="$(mktemp /tmp/orion-sab-sharepoint-cookie.XXXXXX)"
trap 'rm -f -- "${COOKIE_JAR}"' EXIT

ssh -O check lunarc >/dev/null 2>&1 || /Users/billy/lunarc-init.sh
ssh lunarc "mkdir -p '${ORION_SAB_REMOTE_ROOT}/protected-artifact-v1' && chmod 700 '${ORION_SAB_REMOTE_ROOT}/protected-artifact-v1'"

curl --proto '=https' --tlsv1.2 --location --fail --show-error --silent \
  --retry 4 --retry-all-errors --connect-timeout 30 --max-time 3600 \
  --cookie-jar "${COOKIE_JAR}" --cookie "${COOKIE_JAR}" \
  "${URL}" \
  | ssh lunarc "cat > '${REMOTE_PARTIAL}' && chmod 600 '${REMOTE_PARTIAL}'"

ssh lunarc "
  set -eu
  test \"\$(stat -c %s '${REMOTE_PARTIAL}')\" = '1769478786'
  test \"\$(sha256sum '${REMOTE_PARTIAL}' | cut -d' ' -f1)\" = '46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610'
  mv '${REMOTE_PARTIAL}' '${REMOTE_ARCHIVE}'
"

printf '%s\n' 'P1_SAB_ARCHIVE_STREAMED_TO_LUNARC__LOCAL_PAYLOAD_NOT_RETAINED__REMOTE_SHA256_AND_BYTES_PASS'
