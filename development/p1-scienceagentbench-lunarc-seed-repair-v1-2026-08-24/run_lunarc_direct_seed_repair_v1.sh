#!/usr/bin/env bash
#SBATCH --job-name=p1_sab_seed_v1
#SBATCH --account=lu2026-2-51
#SBATCH --partition=gpua40i
#SBATCH --gres=gpu:a40:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --output=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_seed_repair_v1_20260824/run/slurm-%j.out
#SBATCH --error=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_seed_repair_v1_20260824/run/slurm-%j.err

set -Eeuo pipefail
umask 077

ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_seed_repair_v1_20260824
CODE="$ROOT/code"
RUN="$ROOT/run/job-${SLURM_JOB_ID}"
MODEL="$ROOT/model/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf"
MODEL_BYTES=18556689568
MODEL_SHA256=fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad
OLLAMA_SHA256=d0758d38ac5882a2c68fd930d0c1220af1952469fa9f30c268746d4021709bf4
SERVER_SHA256=234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b
CUDA_BACKEND_SHA256=fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb
OLLAMA_TAG_COMMIT=d67ad83426633195089509347ffd4fe795120198
LLAMA_CPP_VERSION=b10434
LLAMA_CPP_COMMIT=7e4c0a96880dae4fc4268ad441f8a6446bd5460a
HOST=127.0.0.1
PORT=11472
BASE_URL="http://${HOST}:${PORT}"

mkdir -p "$RUN"
failure_receipt() {
  local rc=$1
  local failed_command=$2
  local failed_line=$3
  python3 - "$RUN" "$rc" "$failed_command" "$failed_line" <<'PY'
import json
import os
import pathlib
import sys
import time

run = pathlib.Path(sys.argv[1])
receipt = {
    "schema": "orion.p1.scienceagentbench.lunarc-direct-seed-job-failure.v1",
    "status": "FAIL_UNPLANNED_COMMAND",
    "exit_code": int(sys.argv[2]),
    "failed_command": sys.argv[3],
    "failed_line": int(sys.argv[4]),
    "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
    "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "scientific_authority_delta": "NONE",
}
(run / "JOB_FAILURE_V1.json").write_text(
    json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n"
)
PY
}
trap 'failure_receipt "$?" "$BASH_COMMAND" "$LINENO"' ERR
module purge
module load ollama/0.32.14
OLLAMA_BIN=$(command -v ollama)
LIB=/sw/pkg/ollama/0.32.14/lib/ollama
SERVER="$LIB/llama-server"
CUDA_BACKEND="$LIB/cuda_v13/libggml-cuda.so"
export LD_LIBRARY_PATH="$LIB:$LIB/cuda_v13${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export GGML_BACKEND_PATH="$CUDA_BACKEND"
export HTTP_PROXY= HTTPS_PROXY= ALL_PROXY= http_proxy= https_proxy= all_proxy=
export NO_PROXY=127.0.0.1,localhost no_proxy=127.0.0.1,localhost

test "$(stat -c %s "$MODEL")" = "$MODEL_BYTES"
test "$(sha256sum "$MODEL" | awk '{print $1}')" = "$MODEL_SHA256"
test "$(sha256sum "$OLLAMA_BIN" | awk '{print $1}')" = "$OLLAMA_SHA256"
test "$(sha256sum "$SERVER" | awk '{print $1}')" = "$SERVER_SHA256"
test "$(sha256sum "$CUDA_BACKEND" | awk '{print $1}')" = "$CUDA_BACKEND_SHA256"
SERVER_VERSION_OUTPUT=$("$SERVER" --version 2>&1)
grep -q 'commit 7e4c0a968' <<< "$SERVER_VERSION_OUTPUT"

{
  echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "job_id=$SLURM_JOB_ID"
  echo "ollama_module=ollama/0.32.14"
  echo "ollama_tag_commit=$OLLAMA_TAG_COMMIT"
  echo "llama_cpp_version=$LLAMA_CPP_VERSION"
  echo "llama_cpp_commit=$LLAMA_CPP_COMMIT"
  echo "ollama_bin=$OLLAMA_BIN"
  echo "llama_server=$SERVER"
  echo "ggml_backend_path=$GGML_BACKEND_PATH"
  "$OLLAMA_BIN" --version 2>&1 || true
  "$SERVER" --version 2>&1 || true
  nvidia-smi
} > "$RUN/ENVIRONMENT.txt"

{
  sha256sum "$MODEL" "$OLLAMA_BIN" "$SERVER"
  find "$LIB" -maxdepth 2 -type f \( -name 'libllama*.so*' -o -name 'libggml*.so*' -o -name 'libcublas*.so*' -o -name 'libcudart*.so*' \) -print0 \
    | sort -z | xargs -0 sha256sum
  find "$CODE" -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum
} > "$RUN/PRE_RUN_SHA256SUMS"

cat > "$RUN/FROZEN_SERVER_GEOMETRY.txt" <<EOF
host=$HOST
port=$PORT
ctx_size=4096
parallel_slots=1
continuous_batching=false
threads=8
threads_batch=8
batch_size=512
ubatch_size=512
cache_type_k=f16
cache_type_v=f16
flash_attn_primary=on
n_gpu_layers=all
context_shift=false
temperature=0.2
request_order=101,202,101,202,101,202
EOF

SERVER_PID=none
TELEMETRY_PID=none
stop_server() {
  set +e
  if [[ "$SERVER_PID" != none ]]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  SERVER_PID=none
  set -e
}
cleanup_processes() {
  set +e
  stop_server
  if [[ "$TELEMETRY_PID" != none ]]; then
    kill "$TELEMETRY_PID" 2>/dev/null || true
    wait "$TELEMETRY_PID" 2>/dev/null || true
  fi
}
trap cleanup_processes EXIT

start_server() {
  local label=$1
  local flash_attn=$2
  local cublas_workspace=$3
  local log="$RUN/server-${label}.log"
  stop_server
  if [[ "$cublas_workspace" == fixed ]]; then
    CUBLAS_WORKSPACE_CONFIG=:4096:8 "$SERVER" \
      --model "$MODEL" --host "$HOST" --port "$PORT" \
      --ctx-size 4096 --parallel 1 --no-cont-batching \
      --threads 8 --threads-batch 8 --batch-size 512 --ubatch-size 512 \
      --cache-type-k f16 --cache-type-v f16 --flash-attn "$flash_attn" \
      --n-gpu-layers all --no-context-shift --metrics --slots \
      > "$log" 2>&1 &
  else
    env -u CUBLAS_WORKSPACE_CONFIG "$SERVER" \
      --model "$MODEL" --host "$HOST" --port "$PORT" \
      --ctx-size 4096 --parallel 1 --no-cont-batching \
      --threads 8 --threads-batch 8 --batch-size 512 --ubatch-size 512 \
      --cache-type-k f16 --cache-type-v f16 --flash-attn "$flash_attn" \
      --n-gpu-layers all --no-context-shift --metrics --slots \
      > "$log" 2>&1 &
  fi
  SERVER_PID=$!
  local ready=false
  for _ in $(seq 1 300); do
    if curl --noproxy '*' -fsS "$BASE_URL/health" > "$RUN/health-${label}.json"; then
      ready=true
      break
    fi
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
      echo "server exited before ready: $label" >&2
      tail -100 "$log" >&2 || true
      return 1
    fi
    sleep 1
  done
  test "$ready" = true
  ss -lntp | grep ":${PORT}" > "$RUN/socket-${label}.txt"
  grep -q "127.0.0.1:${PORT}" "$RUN/socket-${label}.txt"
}

run_probe() {
  local label=$1
  local cache_prompt=$2
  mkdir -p "$RUN/$label"
  python3 "$CODE/direct_completion_seed_probe_v1.py" \
    --fixture "$CODE/SYNTHETIC_COMPLETION_FIXTURE_V1.json" \
    --base-url "$BASE_URL" \
    --output-dir "$RUN/$label" \
    --condition "$label" \
    --cache-prompt "$cache_prompt" \
    > "$RUN/$label/harness.stdout" 2> "$RUN/$label/harness.stderr"
}

nvidia-smi --query-gpu=timestamp,index,uuid,name,driver_version,memory.used,memory.total,utilization.gpu,power.draw --format=csv,noheader,nounits -lms 200 \
  > "$RUN/GPU_TELEMETRY.csv" 2> "$RUN/GPU_TELEMETRY.err" &
TELEMETRY_PID=$!

start_server primary_cache_off on unset
set +e
run_probe primary_cache_off false
PRIMARY_RC=$?
set -e
stop_server

start_server negative_control_cache_on on unset
run_probe negative_control_cache_on true
stop_server

DIAGNOSTIC_NAMES=()
if [[ "$PRIMARY_RC" -ne 0 ]]; then
  DIAGNOSTIC_NAMES+=(diagnostic_cublas_workspace)
  start_server diagnostic_cublas_workspace on fixed
  set +e
  run_probe diagnostic_cublas_workspace false
  CUBLAS_RC=$?
  set -e
  stop_server

  DIAGNOSTIC_NAMES+=(diagnostic_flash_attn_off)
  start_server diagnostic_flash_attn_off off unset
  set +e
  run_probe diagnostic_flash_attn_off false
  FLASH_OFF_RC=$?
  set -e
  stop_server
fi

kill "$TELEMETRY_PID" 2>/dev/null || true
wait "$TELEMETRY_PID" 2>/dev/null || true
TELEMETRY_PID=none
python3 "$CODE/summarize_gpu_telemetry_v1.py" \
  --telemetry "$RUN/GPU_TELEMETRY.csv" \
  --receipt "$RUN/GPU_ENERGY_RECEIPT_V1.json"
nvidia-smi > "$RUN/NVIDIA_SMI_AFTER.txt"

python3 - "$RUN" "$PRIMARY_RC" "${DIAGNOSTIC_NAMES[*]}" <<'PY'
import hashlib
import json
import os
import pathlib
import sys
import time

run = pathlib.Path(sys.argv[1])
primary_rc = int(sys.argv[2])
diagnostic_names = [x for x in sys.argv[3].split() if x]
conditions = {}
for name in ["primary_cache_off", "negative_control_cache_on"] + diagnostic_names:
    conditions[name] = json.loads((run / name / "CONDITION_RECEIPT_V1.json").read_text())
energy = json.loads((run / "GPU_ENERGY_RECEIPT_V1.json").read_text())
receipt = {
    "schema": "orion.p1.scienceagentbench.lunarc-direct-seed-repair-job.v1",
    "status": (
        "PASS_PRIMARY_CACHE_OFF_DETERMINISTIC_AND_SEED_SENSITIVE"
        if primary_rc == 0
        else "ADVERSE_PRIMARY_CACHE_OFF_GATE_FAILURE"
    ),
    "slurm_job_id": os.environ["SLURM_JOB_ID"],
    "runtime": {
        "ollama_module": "ollama/0.32.14",
        "ollama_tag_commit": "d67ad83426633195089509347ffd4fe795120198",
        "llama_cpp_version": "b10434",
        "llama_cpp_commit": "7e4c0a96880dae4fc4268ad441f8a6446bd5460a",
        "model_sha256": "fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad",
        "llama_server_sha256": "234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b",
        "cuda_backend_sha256": "fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb",
    },
    "condition_order": ["primary_cache_off", "negative_control_cache_on"] + diagnostic_names,
    "conditions": conditions,
    "gpu_telemetry": energy,
    "cost": {
        "billed_usd": None,
        "status": "CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE",
        "gpu_seconds_and_sampled_energy_recorded_separately": True,
    },
    "forbidden_inputs": {
        "protected_archive_opened": False,
        "benchmark_task_opened": False,
        "outcome_opened": False,
        "gold_program_opened": False,
        "evaluator_opened": False,
        "rubric_opened": False,
        "credential_opened": False,
    },
    "scientific_authority_delta": "NONE",
    "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}
(run / "JOB_RECEIPT_V1.json").write_text(
    json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n"
)
PY

if [[ "$PRIMARY_RC" -eq 0 ]]; then
  TERMINAL="P1_SAB_DIRECT_SEED_REPAIR_PASS__CACHE_OFF_WITHIN_SEED_TOKEN_IDENTITY__BETWEEN_SEED_SENSITIVITY__CACHE_N_ZERO__PROMPT_N_CONSTANT__JOB_${SLURM_JOB_ID}__COST_CANNOT_CHECK__NO_BENCHMARK_OR_PROTECTED_INPUTS"
else
  TERMINAL="P1_SAB_DIRECT_SEED_REPAIR_ADVERSE__PRIMARY_CACHE_OFF_GATE_FAILURE__DIAGNOSTICS_BOUNDED__JOB_${SLURM_JOB_ID}__COST_CANNOT_CHECK__NO_BENCHMARK_OR_PROTECTED_INPUTS"
fi
echo "$TERMINAL" | tee "$RUN/TERMINAL.txt"

(
  cd "$RUN"
  find . -type f ! -name REMOTE_RUN_SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > REMOTE_RUN_SHA256SUMS
)

trap - EXIT
cleanup_processes
exit "$PRIMARY_RC"
