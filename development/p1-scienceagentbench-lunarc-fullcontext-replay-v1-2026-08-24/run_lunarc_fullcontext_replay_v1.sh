#!/usr/bin/env bash
#SBATCH --job-name=p1_sab_fullctx_v1
#SBATCH --account=lu2026-2-51
#SBATCH --partition=gpua40
#SBATCH --gres=gpu:a40:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_fullcontext_replay_v1_20260824/run/slurm-%j.out
#SBATCH --error=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_fullcontext_replay_v1_20260824/run/slurm-%j.err

set -Eeuo pipefail
umask 077

ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_fullcontext_replay_v1_20260824
CODE="$ROOT/code"
PROMPTS="$ROOT/prompts"
RUN="$ROOT/run/job-${SLURM_JOB_ID}"
MODEL="$ROOT/model/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf"
MODEL_BYTES=18556689568
MODEL_SHA256=fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad
OLLAMA_SHA256=d0758d38ac5882a2c68fd930d0c1220af1952469fa9f30c268746d4021709bf4
SERVER_SHA256=234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b
CUDA_BACKEND_SHA256=fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb
HOST=127.0.0.1
PORT=11473
BASE_URL="http://${HOST}:${PORT}"

mkdir -p "$RUN"
STARTED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
RUN_STARTED_EPOCH=$(date +%s)
failure_receipt() {
  local rc=$1 failed_command=$2 failed_line=$3
  python3 - "$RUN" "$rc" "$failed_command" "$failed_line" <<'PY'
import json, os, pathlib, sys, time
run = pathlib.Path(sys.argv[1])
receipt = {
    "schema": "orion.p1.scienceagentbench.fullcontext-replay-job-failure.v1",
    "status": "FAIL_UNPLANNED_COMMAND",
    "exit_code": int(sys.argv[2]),
    "failed_command": sys.argv[3],
    "failed_line": int(sys.argv[4]),
    "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
    "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "scientific_authority_delta": "NONE",
}
(run / "JOB_FAILURE_V1.json").write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n")
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
export OLLAMA_NO_CLOUD=1
export HTTP_PROXY= HTTPS_PROXY= ALL_PROXY= http_proxy= https_proxy= all_proxy=
export NO_PROXY=127.0.0.1,localhost no_proxy=127.0.0.1,localhost

test "$(stat -c %s "$MODEL")" = "$MODEL_BYTES"
test "$(sha256sum "$MODEL" | awk '{print $1}')" = "$MODEL_SHA256"
test "$(sha256sum "$OLLAMA_BIN" | awk '{print $1}')" = "$OLLAMA_SHA256"
test "$(sha256sum "$SERVER" | awk '{print $1}')" = "$SERVER_SHA256"
test "$(sha256sum "$CUDA_BACKEND" | awk '{print $1}')" = "$CUDA_BACKEND_SHA256"
test "$(stat -c %s "$PROMPTS/short.prompt")" = 186
test "$(sha256sum "$PROMPTS/short.prompt" | awk '{print $1}')" = afb432d64085e79f36da380ce0dbc79aa8b5efe221921da06d511480947b4a3b
test "$(stat -c %s "$PROMPTS/long.prompt")" = 90575
test "$(sha256sum "$PROMPTS/long.prompt" | awk '{print $1}')" = 6c52c9055c03367832e9e61c31f49489194cecd94e732fbc7ca59caeb40cf918
SERVER_VERSION_OUTPUT=$("$SERVER" --version 2>&1)
grep -q 'commit 7e4c0a968' <<< "$SERVER_VERSION_OUTPUT"

{
  echo "utc=$STARTED_UTC"
  echo "host=$(hostname)"
  echo "job_id=$SLURM_JOB_ID"
  echo "ollama_module=ollama/0.32.14"
  echo "llama_cpp_version=b10434"
  echo "llama_cpp_commit=7e4c0a96880dae4fc4268ad441f8a6446bd5460a"
  echo "ollama_bin=$OLLAMA_BIN"
  echo "llama_server=$SERVER"
  echo "ggml_backend_path=$GGML_BACKEND_PATH"
  echo "OLLAMA_NO_CLOUD=$OLLAMA_NO_CLOUD"
  "$OLLAMA_BIN" --version 2>&1 || true
  "$SERVER" --version 2>&1 || true
  nvidia-smi
} > "$RUN/ENVIRONMENT.txt"

{
  sha256sum "$MODEL" "$OLLAMA_BIN" "$SERVER" "$CUDA_BACKEND"
  sha256sum "$PROMPTS/short.prompt" "$PROMPTS/long.prompt"
  find "$CODE" -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum
} > "$RUN/PRE_RUN_SHA256SUMS"

cat > "$RUN/FROZEN_SERVER_GEOMETRY.txt" <<EOF
host=$HOST
port=$PORT
ctx_size=32768
parallel_slots=1
continuous_batching=false
threads=8
threads_batch=8
batch_size=512
ubatch_size=512
cache_type_k=f16
cache_type_v=f16
flash_attention=on
n_gpu_layers=all
context_shift=false
cache_prompt=false
condition_order=short_pr1130_replay,long_pr1130_six_marker
request_order=101,202,101,202,101,202
EOF

SERVER_PID=none
TELEMETRY_PID=none
cleanup_processes() {
  set +e
  if [[ "$SERVER_PID" != none ]]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  SERVER_PID=none
  if [[ "$TELEMETRY_PID" != none ]]; then
    kill "$TELEMETRY_PID" 2>/dev/null || true
    wait "$TELEMETRY_PID" 2>/dev/null || true
  fi
  TELEMETRY_PID=none
}
trap cleanup_processes EXIT

nvidia-smi --query-gpu=timestamp,index,uuid,name,driver_version,memory.used,memory.total,utilization.gpu,power.draw --format=csv,noheader,nounits -lms 200 \
  > "$RUN/GPU_TELEMETRY.csv" 2> "$RUN/GPU_TELEMETRY.err" &
TELEMETRY_PID=$!

"$SERVER" \
  --model "$MODEL" --host "$HOST" --port "$PORT" \
  --ctx-size 32768 --parallel 1 --no-cont-batching \
  --threads 8 --threads-batch 8 --batch-size 512 --ubatch-size 512 \
  --cache-type-k f16 --cache-type-v f16 --flash-attn on \
  --n-gpu-layers all --no-context-shift --metrics --slots \
  > "$RUN/server.log" 2>&1 &
SERVER_PID=$!
READY=false
for _ in $(seq 1 600); do
  if curl --noproxy '*' -fsS "$BASE_URL/health" > "$RUN/health.json"; then
    READY=true
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    tail -100 "$RUN/server.log" >&2 || true
    exit 1
  fi
  sleep 1
done
test "$READY" = true
ss -lntp | grep ":${PORT}" > "$RUN/socket.txt"
grep -q "127.0.0.1:${PORT}" "$RUN/socket.txt"

set +e
python3 "$CODE/direct_fullcontext_replay_v1.py" \
  --protocol "$CODE/FROZEN_FULLCONTEXT_REPLAY_PROTOCOL_V1.json" \
  --short-prompt "$PROMPTS/short.prompt" \
  --long-prompt "$PROMPTS/long.prompt" \
  --base-url "$BASE_URL" \
  --output-dir "$RUN/results" \
  > "$RUN/harness.stdout" 2> "$RUN/harness.stderr"
HARNESS_RC=$?
set -e

cleanup_processes
python3 "$CODE/summarize_gpu_telemetry_v1.py" \
  --telemetry "$RUN/GPU_TELEMETRY.csv" \
  --receipt "$RUN/GPU_ENERGY_RECEIPT_V1.json"
nvidia-smi > "$RUN/NVIDIA_SMI_AFTER.txt"
FINISHED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
RUN_FINISHED_EPOCH=$(date +%s)

python3 "$CODE/build_job_receipt_v1.py" \
  --run-dir "$RUN" \
  --harness-rc "$HARNESS_RC" \
  --job-id "$SLURM_JOB_ID" \
  --started-utc "$STARTED_UTC" \
  --finished-utc "$FINISHED_UTC" \
  --wall-seconds "$((RUN_FINISHED_EPOCH - RUN_STARTED_EPOCH))"

(
  cd "$RUN"
  find . -type f ! -name REMOTE_RUN_SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > REMOTE_RUN_SHA256SUMS
)

trap - EXIT
cleanup_processes
exit "$HARNESS_RC"
