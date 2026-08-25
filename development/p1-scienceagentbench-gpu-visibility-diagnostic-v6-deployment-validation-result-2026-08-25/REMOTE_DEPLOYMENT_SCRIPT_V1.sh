#!/usr/bin/bash
set -Eeuo pipefail
umask 077

ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-gpu-visibility-v6-20260825
RUN=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v6-20260825
OUTPUT=$RUN/evidence
LOG=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-gpu-visibility-v6-20260825-submit-logs
LANE=$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v6-2026-08-25
ENTRY=$LANE/run_gpu_visibility_diagnostic_v1.sh
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3

for pair in ROOT:$ROOT RUN:$RUN OUTPUT:$OUTPUT LOG:$LOG; do
  label=${pair%%:*}
  path=${pair#*:}
  if [[ -e "$path" || -L "$path" ]]; then
    printf 'P1_V6_DEPLOYMENT_ABSENCE_FAIL label=%s path=%s\n' "$label" "$path"
    exit 1
  fi
  printf 'P1_V6_DEPLOYMENT_ABSENT label=%s path=%s\n' "$label" "$path"
done

/usr/bin/mkdir -m 0700 -- "$ROOT"
/usr/bin/tar -xpf - -C "$ROOT"

/usr/bin/find "$ROOT" -type f -exec /usr/bin/chmod 0400 -- {} +
/usr/bin/chmod 0500 -- "$ENTRY"
/usr/bin/find "$ROOT" -depth -type d -exec /usr/bin/chmod 0500 -- {} +

[[ "$(/usr/bin/stat -Lc '%a' -- "$ENTRY")" == 500 ]]
[[ -z "$(/usr/bin/find "$ROOT" -type f ! -path "$ENTRY" -printf '%m\n' | /usr/bin/awk '$1 != "400" {print; exit}')" ]]
[[ -z "$(/usr/bin/find "$ROOT" -type d -printf '%m\n' | /usr/bin/awk '$1 != "500" {print; exit}')" ]]
[[ "$(/usr/bin/stat -Lc '%a' -- "$LANE/BODY_FREE_DIAGNOSTIC_EXPORT_MANIFEST_V1.json")" == 400 ]]
[[ "$(/usr/bin/stat -Lc '%a' -- "$LANE/SHA256SUMS")" == 400 ]]
printf 'P1_V6_DEPLOYMENT_MODE_SEAL_PASS regular=0400 entry=0500 directories=0500\n'

cd "$LANE"
/usr/bin/bash -n run_gpu_visibility_diagnostic_v1.sh
for label_and_command in \
  "normal|$PY -B validate_gpu_visibility_diagnostic_v1.py" \
  "optimized|$PY -O -B validate_gpu_visibility_diagnostic_v1.py" \
  "isolated|$PY -I -S -B validate_gpu_visibility_diagnostic_v1.py" \
  "exact_system_isolated|/usr/bin/python3 -I -S -B validate_gpu_visibility_diagnostic_v1.py"
do
  label=${label_and_command%%|*}
  command=${label_and_command#*|}
  output=$(eval "$command" 2>&1)
  terminal=$(printf '%s\n' "$output" | /usr/bin/tail -1)
  printf 'P1_V6_DEPLOYMENT_VALIDATION label=%s terminal=%s\n' "$label" "$terminal"
done
/usr/bin/sha256sum -c SHA256SUMS
printf 'P1_V6_DEPLOYMENT_DIRECT_VALIDATION_PASS\n'

[[ ! -e "$RUN" && ! -L "$RUN" ]]
[[ ! -e "$OUTPUT" && ! -L "$OUTPUT" ]]
/usr/bin/mkdir -m 0700 -- "$LOG"
[[ "$(/usr/bin/stat -Lc '%a' -- "$LOG")" == 700 ]]
printf 'P1_V6_DEPLOYMENT_READY root=%s log=%s run_absent=true output_absent=true merge_commit=79865e469c79f656bcca92044975eeb6895bb283 archive_sha256=2f8773ff5637d6ec19c92bb1fccf0103be95f8640db5bf0b9c7b4351500537ff\n' "$ROOT" "$LOG"

/usr/bin/rm -f -- "$0"
