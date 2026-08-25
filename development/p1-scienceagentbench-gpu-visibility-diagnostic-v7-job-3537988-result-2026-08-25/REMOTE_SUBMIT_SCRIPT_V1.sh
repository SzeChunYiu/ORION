#!/usr/bin/bash
set -Eeuo pipefail
umask 077
BASE=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824
ROOT=$BASE/repo-gpu-visibility-v7-20260825
RUN=$BASE/live-gpu-visibility-v7-20260825
OUTPUT=$RUN/evidence
LOG=$BASE/live-gpu-visibility-v7-20260825-submit-logs
LANE=$ROOT/development/p1-scienceagentbench-gpu-visibility-diagnostic-v7-2026-08-25
ENTRY=$LANE/run_gpu_visibility_diagnostic_v1.sh
[[ -d "$ROOT" && ! -L "$ROOT" && "$(/usr/bin/stat -Lc %a -- "$ROOT")" == 500 ]]
[[ -f "$ENTRY" && ! -L "$ENTRY" && "$(/usr/bin/stat -Lc %a -- "$ENTRY")" == 500 ]]
[[ -d "$LOG" && ! -L "$LOG" && "$(/usr/bin/stat -Lc %a -- "$LOG")" == 700 ]]
[[ ! -e "$RUN" && ! -L "$RUN" ]]
[[ ! -e "$OUTPUT" && ! -L "$OUTPUT" ]]
(cd "$LANE" && /usr/bin/sha256sum -c SHA256SUMS >/dev/null)
if /usr/bin/env | /usr/bin/grep -q ^SBATCH_; then
  printf "%s\n" "P1_V7_SUBMISSION_FAIL inherited SBATCH_* environment is forbidden"
  exit 1
fi
submit_line=$(/usr/bin/sbatch --export=NIL \
  --chdir="$ROOT" \
  --output="$LOG/slurm-%j.out" \
  --error="$LOG/slurm-%j.err" \
  "$ENTRY")
[[ "$submit_line" =~ ^Submitted[[:space:]]batch[[:space:]]job[[:space:]]([1-9][0-9]*)$ ]]
job=${BASH_REMATCH[1]}
printf "P1_V7_SUBMISSION_PASS job=%s line=%s zero_argv=true run_absent=true output_absent=true\n" "$job" "$submit_line"
/usr/bin/squeue -j "$job" --format="%.10i %.24j %.9T %.10M %.6D %.24R %.8q"
