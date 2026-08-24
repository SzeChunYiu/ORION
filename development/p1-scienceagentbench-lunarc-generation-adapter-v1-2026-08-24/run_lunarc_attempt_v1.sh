#!/usr/bin/env bash
#SBATCH --job-name=p1_sab_gen_v1
#SBATCH --account=lu2026-2-51
#SBATCH --partition=gpua40i
#SBATCH --gres=gpu:a40:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00

# One invocation is exactly one task/arm/attempt. This wrapper captures bounded
# in-job scheduler metadata and invokes one externally frozen driver. It does
# not claim exclusivity; post-job scontrol+sacct evidence must still be finalized.

set -Eeuo pipefail
set -C
umask 077

usage() {
  cat >&2 <<'EOF'
usage: run_lunarc_attempt_v1.sh \
  --run-plan ABSOLUTE_PATH --task-id ID --arm RR|OS|NR --attempt 1|2|3 \
  --driver ABSOLUTE_PATH --adapter-module ABSOLUTE_PATH --output-dir ABSOLUTE_PATH

The frozen driver must accept the same named arguments plus:
  --slurm-identity-json ABSOLUTE_PATH
and must use GenerationAttemptCapture.call_model for every model operation.
EOF
  exit 2
}

RUN_PLAN=
TASK_ID=
ARM_ID=
ATTEMPT=
DRIVER=
ADAPTER_MODULE=
OUTPUT_DIR=
while (($#)); do
  case "$1" in
    --run-plan) [[ $# -ge 2 ]] || usage; RUN_PLAN=$2; shift 2 ;;
    --task-id) [[ $# -ge 2 ]] || usage; TASK_ID=$2; shift 2 ;;
    --arm) [[ $# -ge 2 ]] || usage; ARM_ID=$2; shift 2 ;;
    --attempt) [[ $# -ge 2 ]] || usage; ATTEMPT=$2; shift 2 ;;
    --driver) [[ $# -ge 2 ]] || usage; DRIVER=$2; shift 2 ;;
    --adapter-module) [[ $# -ge 2 ]] || usage; ADAPTER_MODULE=$2; shift 2 ;;
    --output-dir) [[ $# -ge 2 ]] || usage; OUTPUT_DIR=$2; shift 2 ;;
    *) usage ;;
  esac
done

[[ -n "$RUN_PLAN" && "$RUN_PLAN" = /* && -f "$RUN_PLAN" ]] || usage
[[ "$TASK_ID" =~ ^([1-9]|[1-9][0-9]|10[0-2])$ ]] || usage
[[ "$ARM_ID" =~ ^(RR|OS|NR)$ ]] || usage
[[ "$ATTEMPT" =~ ^[123]$ ]] || usage
[[ -n "$DRIVER" && "$DRIVER" = /* && -f "$DRIVER" ]] || usage
[[ -n "$ADAPTER_MODULE" && "$ADAPTER_MODULE" = /* && -f "$ADAPTER_MODULE" ]] || usage
[[ -n "$OUTPUT_DIR" && "$OUTPUT_DIR" = /* ]] || usage
: "${SLURM_JOB_ID:?must run as one SLURM allocation or array element}"
: "${SLURM_CLUSTER_NAME:?SLURM_CLUSTER_NAME is required}"
[[ "$SLURM_CLUSTER_NAME" =~ ^[a-z][a-z0-9]*(-[a-z0-9]+)*$ ]] || usage
[[ "$SLURM_JOB_ID" =~ ^[1-9][0-9]*$ ]] || usage
ARRAY_JOB_ID=${SLURM_ARRAY_JOB_ID:-}
ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID:-}
if [[ -n "$ARRAY_JOB_ID" || -n "$ARRAY_TASK_ID" ]]; then
  [[ "$ARRAY_JOB_ID" =~ ^[1-9][0-9]*$ ]] || usage
  [[ "$ARRAY_TASK_ID" =~ ^(0|[1-9][0-9]*)$ ]] || usage
  CANONICAL_JOB_ID="${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
else
  CANONICAL_JOB_ID=$SLURM_JOB_ID
fi
command -v scontrol >/dev/null
command -v sha256sum >/dev/null
command -v python3 >/dev/null

mkdir -m 700 -- "$OUTPUT_DIR"
SNAPSHOT="$OUTPUT_DIR/SCONTROL_IN_JOB_V1.txt"
IDENTITY="$OUTPUT_DIR/SLURM_IDENTITY_AND_SNAPSHOT_V1.json"
FAILURE="$OUTPUT_DIR/JOB_WRAPPER_CANNOT_CHECK_V1.json"

failure_sidecar() {
  local rc=$1
  local failed_line=$2
  local failed_command=$3
  set +e
  python3 - "$FAILURE" "$TASK_ID" "$ARM_ID" "$ATTEMPT" "$SLURM_CLUSTER_NAME" \
    "$CANONICAL_JOB_ID" "$rc" "$failed_line" "$failed_command" <<'PY'
import hashlib
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
command_hash = hashlib.sha256(sys.argv[9].encode("utf-8", errors="replace")).hexdigest()
receipt = {
    "schema_version": "orion.p1.scienceagentbench.lunarc-attempt-wrapper-cannot-check.v1",
    "authority": "JOB_WRAPPER_FAILURE_METADATA_ONLY",
    "status": "CANNOT_CHECK",
    "task_id": sys.argv[2],
    "arm_id": sys.argv[3],
    "attempt": int(sys.argv[4]),
    "slurm_cluster": sys.argv[5],
    "slurm_job_id": sys.argv[6],
    "exit_code": int(sys.argv[7]),
    "failed_line": int(sys.argv[8]),
    "failed_command_sha256": command_hash,
    "runner_v2_record_emitted": False,
    "official_evaluator_invoked": False,
    "official_outcomes_opened": False,
    "scientific_authority_delta": "NONE",
}
try:
    fd = path.open("x", encoding="utf-8")
except FileExistsError:
    pass
else:
    with fd:
        json.dump(receipt, fd, sort_keys=True, separators=(",", ":"))
        fd.write("\n")
PY
  exit "$rc"
}
trap 'failure_sidecar "$?" "$LINENO" "$BASH_COMMAND"' ERR

# The raw scheduler snapshot is evidence input, not proof by itself. The final
# adapter requires a separately retained post-job sacct record and config hash.
scontrol show job -dd "$SLURM_JOB_ID" > "$SNAPSHOT"
test -s "$SNAPSHOT"
SNAPSHOT_SHA256=$(sha256sum "$SNAPSHOT" | awk '{print $1}')

python3 - "$IDENTITY" "$SLURM_CLUSTER_NAME" "$CANONICAL_JOB_ID" \
  "$ARRAY_JOB_ID" "$ARRAY_TASK_ID" "$SNAPSHOT_SHA256" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
array_job = sys.argv[4] or None
array_task = sys.argv[5] or None
if (array_job is None) != (array_task is None):
    raise SystemExit("array job/task identity must be jointly present or absent")
payload = {
    "slurm_job_identity": {
        "cluster": sys.argv[2],
        "job_id": sys.argv[3],
        "array_job_id": array_job,
        "array_task_id": array_task,
    },
    "slurm_in_job_snapshot_sha256": sys.argv[6],
    "allocation_status": "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION",
    "environment_only_exclusivity_claimed": False,
}
with path.open("x", encoding="utf-8") as handle:
    json.dump(payload, handle, sort_keys=True, separators=(",", ":"))
    handle.write("\n")
PY

# Exactly one driver process and one tuple. The driver owns model/server details
# but must route every generation operation through the supplied adapter module.
python3 "$DRIVER" \
  --adapter-module "$ADAPTER_MODULE" \
  --run-plan "$RUN_PLAN" \
  --task-id "$TASK_ID" \
  --arm "$ARM_ID" \
  --attempt "$ATTEMPT" \
  --slurm-identity-json "$IDENTITY" \
  --output-dir "$OUTPUT_DIR"

test -s "$OUTPUT_DIR/ATTEMPT_CAPTURE_V1.json"
printf '%s\n' \
  "P1_SAB_LUNARC_ATTEMPT_CAPTURED__TASK_${TASK_ID}__ARM_${ARM_ID}__ATTEMPT_${ATTEMPT}__ALLOCATION_FINALIZATION_PENDING__NO_OUTCOMES_OPENED"
