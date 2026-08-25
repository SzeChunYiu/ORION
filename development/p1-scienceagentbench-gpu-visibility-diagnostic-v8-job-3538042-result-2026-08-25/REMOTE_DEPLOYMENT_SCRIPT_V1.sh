#!/usr/bin/bash
set -Eeuo pipefail
umask 077

BASE=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824
MERGE=123a75b5663a77290741ae7f5c24490954118f4d
ARCHIVE=$BASE/.p1-v8-selective-$MERGE.tar
ARCHIVE_BYTES=450560
ARCHIVE_SHA256=ef795324bda3293e74c19b4999c08bd5d250770be2f08983fa56d79a653691a2
ROOT=$BASE/repo-gpu-visibility-v8-20260825
RUN=$BASE/live-gpu-visibility-v8-20260825
OUTPUT=$RUN/evidence
LOG=$BASE/live-gpu-visibility-v8-20260825-submit-logs
V6_ROOT=$BASE/repo-gpu-visibility-v6-20260825
V6_SCRIPT=$BASE/.p1-v6-deploy-79865e46.sh
PRESERVED_V7_ROOT=$BASE/repo-gpu-visibility-v7-20260825
PRESERVED_V7_RUN=$BASE/live-gpu-visibility-v7-20260825
PRESERVED_V7_LOG=$BASE/live-gpu-visibility-v7-20260825-submit-logs
V8_LANE=$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v8-2026-08-25
V5_RESULT_LANE=$ROOT/development/p1-scienceagentbench-backend-canonical-map-discriminator-v5-job-3537915-result-2026-08-25
V6_FAILURE_LANE=$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v6-deployment-validation-result-2026-08-25
V7_RESULT_LANE=$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v7-job-3537988-result-2026-08-25
ENTRY=$V8_LANE/run_gpu_visibility_diagnostic_v1.sh
VALIDATOR=$V8_LANE/validate_gpu_visibility_diagnostic_v1.py
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
EXPECTED_TERMINAL="P1_SAB_GPU_VISIBILITY_DIAGNOSTIC_V1_SYNTHETIC_VALIDATION_PASS tests=51 protected_bodies=0 task_routes=0 tokenize=0 completion=0 generation=0 jobs=0 outcomes=0 production_admissibility=CANNOT_CHECK scientific_authority=NONE"

fail() {
  printf "P1_V8_DEPLOYMENT_FAIL reason=%s\n" "$1"
  exit 1
}

[[ -d "$V6_ROOT" && ! -L "$V6_ROOT" ]] || fail V6_ROOT_NOT_PRESERVED
[[ -f "$V6_SCRIPT" && ! -L "$V6_SCRIPT" ]] || fail V6_SCRIPT_NOT_PRESERVED
printf "P1_V8_V6_PRESERVATION_PASS root=%s script=%s\n" "$V6_ROOT" "$V6_SCRIPT"
[[ -d "$PRESERVED_V7_ROOT" && ! -L "$PRESERVED_V7_ROOT" ]] || fail V7_ROOT_NOT_PRESERVED
[[ -d "$PRESERVED_V7_LOG" && ! -L "$PRESERVED_V7_LOG" ]] || fail V7_LOG_NOT_PRESERVED
[[ ! -e "$PRESERVED_V7_RUN" && ! -L "$PRESERVED_V7_RUN" ]] || fail V7_RUN_CUSTODY_DRIFT
printf "P1_V8_V7_PRESERVATION_PASS root=%s log=%s run_absent=true\n" "$PRESERVED_V7_ROOT" "$PRESERVED_V7_LOG"

[[ -f "$ARCHIVE" && ! -L "$ARCHIVE" ]] || fail ARCHIVE_INVALID
[[ "$(/usr/bin/stat -Lc %s -- "$ARCHIVE")" == "$ARCHIVE_BYTES" ]] || fail ARCHIVE_BYTES_MISMATCH
[[ "$(/usr/bin/sha256sum "$ARCHIVE" | /usr/bin/awk "{print \$1}")" == "$ARCHIVE_SHA256" ]] || fail ARCHIVE_HASH_MISMATCH
member_count=$(/usr/bin/tar -tf "$ARCHIVE" | /usr/bin/wc -l | /usr/bin/tr -d " ")
regular_count=$(/usr/bin/tar -tvf "$ARCHIVE" | /usr/bin/awk "substr(\$1,1,1)==\"-\"{n++} END{print n+0}")
[[ "$member_count" == 55 && "$regular_count" == 50 ]] || fail ARCHIVE_MEMBER_COUNT_MISMATCH
while IFS= read -r member; do
  case "$member" in
    /*|../*|*/../*|*/..|..) fail ARCHIVE_PATH_TRAVERSAL ;;
  esac
done < <(/usr/bin/tar -tf "$ARCHIVE")
if /usr/bin/tar -tvf "$ARCHIVE" | /usr/bin/awk "substr(\$1,1,1)!=\"-\" && substr(\$1,1,1)!=\"d\"{bad=1} END{exit !bad}"; then
  fail ARCHIVE_NONREGULAR_MEMBER
fi
printf "P1_V8_ARCHIVE_PASS merge=%s bytes=%s sha256=%s members=%s regular_files=%s\n" "$MERGE" "$ARCHIVE_BYTES" "$ARCHIVE_SHA256" "$member_count" "$regular_count"

for pair in ROOT:$ROOT RUN:$RUN OUTPUT:$OUTPUT LOG:$LOG; do
  label=${pair%%:*}
  path=${pair#*:}
  if [[ -e "$path" || -L "$path" ]]; then
    fail "${label}_NOT_FRESH"
  fi
  printf "P1_V8_DEPLOYMENT_ABSENT label=%s path=%s\n" "$label" "$path"
done

/usr/bin/mkdir -m 0700 -- "$ROOT"
/usr/bin/tar -xpf "$ARCHIVE" -C "$ROOT"
[[ -z "$(/usr/bin/find "$ROOT" -type l -print -quit)" ]] || fail DEPLOYED_SYMLINK
/usr/bin/find "$ROOT" -type f -exec /usr/bin/chmod 0400 -- {} +
/usr/bin/chmod 0500 -- "$ENTRY"
/usr/bin/find "$ROOT" -depth -type d -exec /usr/bin/chmod 0500 -- {} +
[[ "$(/usr/bin/stat -Lc %a -- "$ENTRY")" == 500 ]] || fail ENTRY_MODE
[[ -z "$(/usr/bin/find "$ROOT" -type f ! -path "$ENTRY" -printf "%m\n" | /usr/bin/awk "\$1 != \"400\" {print; exit}")" ]] || fail FILE_MODE
[[ -z "$(/usr/bin/find "$ROOT" -type d -printf "%m\n" | /usr/bin/awk "\$1 != \"500\" {print; exit}")" ]] || fail DIRECTORY_MODE
printf "P1_V8_DEPLOYMENT_MODE_SEAL_PASS regular=0400 entry=0500 directories=0500\n"

for lane in "$V8_LANE" "$V5_RESULT_LANE" "$V6_FAILURE_LANE" "$V7_RESULT_LANE"; do
  (cd "$lane" && /usr/bin/sha256sum -c SHA256SUMS)
  printf "P1_V8_LANE_INTEGRITY_PASS lane=%s\n" "$lane"
done

run_validator() {
  local label=$1
  shift
  local output terminal bytes digest
  if ! output=$("$@" 2>&1); then
    printf "P1_V8_DEPLOYMENT_VALIDATION_FAIL label=%s\n%s\n" "$label" "$output"
    exit 1
  fi
  terminal=$(printf "%s\n" "$output" | /usr/bin/tail -1)
  bytes=$(printf "%s" "$output" | /usr/bin/wc -c | /usr/bin/tr -d " ")
  digest=$(printf "%s" "$output" | /usr/bin/sha256sum | /usr/bin/awk "{print \$1}")
  [[ "$terminal" == "$EXPECTED_TERMINAL" ]] || fail "VALIDATOR_${label}_TERMINAL_MISMATCH"
  printf "P1_V8_DEPLOYMENT_VALIDATION_PASS label=%s bytes=%s sha256=%s terminal=%s\n" "$label" "$bytes" "$digest" "$terminal"
}

cd "$V8_LANE"
/usr/bin/bash -n run_gpu_visibility_diagnostic_v1.sh
run_validator normal "$PY" -B validate_gpu_visibility_diagnostic_v1.py
run_validator optimized "$PY" -O -B validate_gpu_visibility_diagnostic_v1.py
run_validator isolated "$PY" -I -S -B validate_gpu_visibility_diagnostic_v1.py
run_validator exact_system_isolated /usr/bin/python3 -I -S -B validate_gpu_visibility_diagnostic_v1.py
for lane in "$V8_LANE" "$V5_RESULT_LANE" "$V6_FAILURE_LANE" "$V7_RESULT_LANE"; do
  (cd "$lane" && /usr/bin/sha256sum -c SHA256SUMS >/dev/null)
done
printf "P1_V8_DEPLOYMENT_POST_VALIDATION_INTEGRITY_PASS\n"

for pair in RUN:$RUN OUTPUT:$OUTPUT LOG:$LOG; do
  label=${pair%%:*}
  path=${pair#*:}
  [[ ! -e "$path" && ! -L "$path" ]] || fail "${label}_CREATED_DURING_VALIDATION"
  printf "P1_V8_POST_VALIDATION_ABSENT label=%s path=%s\n" "$label" "$path"
done
/usr/bin/mkdir -m 0700 -- "$LOG"
[[ "$(/usr/bin/stat -Lc %a -- "$LOG")" == 700 ]] || fail LOG_MODE
printf "P1_V8_DEPLOYMENT_READY root=%s log=%s run_absent=true output_absent=true merge=%s archive_sha256=%s\n" "$ROOT" "$LOG" "$MERGE" "$ARCHIVE_SHA256"
