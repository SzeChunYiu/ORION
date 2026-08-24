#!/usr/bin/env bash
#SBATCH --job-name=p1_sab_ow_v1
#SBATCH --account=lu2026-2-51
#SBATCH --partition=gpua40i
#SBATCH --gres=gpu:a40:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_openweight_v1_20260824/run/slurm-%j.out
#SBATCH --error=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_openweight_v1_20260824/run/slurm-%j.err

set -Eeuo pipefail
umask 077

ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_openweight_v1_20260824
CODE="$ROOT/code"
RUN="$ROOT/run/job-${SLURM_JOB_ID}"
MODEL_FILE="$ROOT/model/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf"
MODEL_EXPECTED_SHA256=fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad
MODEL_EXPECTED_BYTES=18556689568
MODEL_NAME=orion-qwen3-coder-30b-a3b-q4km:sha-fadc3e5f
OLLAMA_EXPECTED_SHA256=d0758d38ac5882a2c68fd930d0c1220af1952469fa9f30c268746d4021709bf4
mkdir -p "$RUN/raw" "$RUN/ollama-models"

failure_receipt() {
  rc=$1
  failed_command=$2
  failed_line=$3
  python3 - "$RUN" "$rc" "$failed_command" "$failed_line" <<'PY'
import json, pathlib, sys, time
root=pathlib.Path(sys.argv[1]); rc=int(sys.argv[2]); command=sys.argv[3]; line=int(sys.argv[4])
(root/'JOB_FAILURE_V1.json').write_text(json.dumps({
  'schema':'orion.p1.scienceagentbench.lunarc-openweight-job-failure.v1',
  'status':'FAIL','exit_code':rc,'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
  'slurm_job_id':__import__('os').environ.get('SLURM_JOB_ID'),'failed_command':command,'failed_line':line,
}, sort_keys=True, separators=(',',':'))+'\n')
PY
  exit "$rc"
}
trap 'failure_receipt "$?" "$BASH_COMMAND" "$LINENO"' ERR

module purge
module load ollama/0.32.14
OLLAMA_BIN=$(command -v ollama)
{
  echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "job_id=$SLURM_JOB_ID"
  echo "ollama_bin=$OLLAMA_BIN"
  ollama --version 2>&1 || true
  nvidia-smi
} > "$RUN/ENVIRONMENT.txt"

test "$(stat -c %s "$MODEL_FILE")" = "$MODEL_EXPECTED_BYTES"
test "$(sha256sum "$MODEL_FILE" | awk '{print $1}')" = "$MODEL_EXPECTED_SHA256"
test "$(sha256sum "$OLLAMA_BIN" | awk '{print $1}')" = "$OLLAMA_EXPECTED_SHA256"
test "$(stat -c %s "$ROOT/tokenizer/config.json")" = 963
test "$(sha256sum "$ROOT/tokenizer/config.json" | awk '{print $1}')" = e2c8d8eea39471785cd93379d8b48241ad7dcda299013155dd02526e34a0de62
test "$(stat -c %s "$ROOT/tokenizer/generation_config.json")" = 180
test "$(sha256sum "$ROOT/tokenizer/generation_config.json" | awk '{print $1}')" = c99723ab3ba28630d26ae23def77603b540a46924895af5cf234740d3b27b51d
test "$(stat -c %s "$ROOT/tokenizer/tokenizer.json")" = 7032399
test "$(sha256sum "$ROOT/tokenizer/tokenizer.json" | awk '{print $1}')" = 19564a48c4f71a2a1b937cce34c737a1e662b171c5f5d7edf641a15cd896f07d
test "$(stat -c %s "$ROOT/tokenizer/tokenizer_config.json")" = 13055
test "$(sha256sum "$ROOT/tokenizer/tokenizer_config.json" | awk '{print $1}')" = 60f6e8cb15c98dd07300a3cc465ea662de245d2095e4245616af21b2324db3fc
{
  sha256sum "$MODEL_FILE" "$OLLAMA_BIN" "$ROOT"/tokenizer/*
  find "$CODE" -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum
} > "$RUN/PRE_RUN_SHA256SUMS"

export OLLAMA_HOST=127.0.0.1:11471
export OLLAMA_MODELS="$RUN/ollama-models"
export OLLAMA_NOHISTORY=1
export OLLAMA_NOPRUNE=1
export OLLAMA_KEEP_ALIVE=30m
export HTTP_PROXY=
export HTTPS_PROXY=
export ALL_PROXY=
export http_proxy=
export https_proxy=
export all_proxy=
export NO_PROXY=127.0.0.1,localhost
export no_proxy=127.0.0.1,localhost
env | sort > "$RUN/ENV_SORTED.txt"

"$OLLAMA_BIN" serve > "$RUN/ollama-server.log" 2>&1 &
OLLAMA_PID=$!
cleanup() {
  set +e
  kill "$TELEMETRY_PID" 2>/dev/null || true
  wait "$TELEMETRY_PID" 2>/dev/null || true
  "$OLLAMA_BIN" stop "$MODEL_NAME" >> "$RUN/cleanup.log" 2>&1 || true
  kill "$OLLAMA_PID" 2>/dev/null || true
  wait "$OLLAMA_PID" 2>/dev/null || true
  rm -rf "$RUN/ollama-models"
  echo "cleanup_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RUN/cleanup.log"
}
TELEMETRY_PID=none
trap cleanup EXIT

for _ in $(seq 1 120); do
  if curl --noproxy '*' -fsS http://127.0.0.1:11471/api/version > "$RUN/OLLAMA_API_VERSION.json"; then break; fi
  sleep 1
done
curl --noproxy '*' -fsS http://127.0.0.1:11471/api/version >/dev/null

cat > "$RUN/Modelfile" <<EOF
FROM $MODEL_FILE
PARAMETER num_ctx 32768
PARAMETER temperature 0.8
PARAMETER top_p 0.95
PARAMETER top_k 20
PARAMETER repeat_penalty 1.0
EOF
"$OLLAMA_BIN" create "$MODEL_NAME" -f "$RUN/Modelfile" > "$RUN/ollama-create.log" 2>&1
"$OLLAMA_BIN" show "$MODEL_NAME" --modelfile > "$RUN/OLLAMA_SHOW_MODELFILE.txt"
"$OLLAMA_BIN" show "$MODEL_NAME" --parameters > "$RUN/OLLAMA_SHOW_PARAMETERS.txt"
"$OLLAMA_BIN" list > "$RUN/OLLAMA_LIST.txt"
find "$RUN/ollama-models" -type f -print0 | sort -z | xargs -0 sha256sum > "$RUN/OLLAMA_STORE_SHA256SUMS"

ss -lntp > "$RUN/SOCKETS_BEFORE_GENERATION.txt" 2>&1 || true
nvidia-smi --query-gpu=timestamp,index,uuid,name,driver_version,memory.used,memory.total,utilization.gpu,power.draw --format=csv,noheader,nounits -lms 200 > "$RUN/GPU_TELEMETRY.csv" 2> "$RUN/GPU_TELEMETRY.err" &
TELEMETRY_PID=$!

python3 "$CODE/openweight_synthetic_smoke_v1.py" \
  --fixture "$CODE/SYNTHETIC_FIXTURE_V1.json" \
  --model "$MODEL_NAME" \
  --base-url http://127.0.0.1:11471 \
  --output-dir "$RUN/raw" \
  > "$RUN/harness.stdout" 2> "$RUN/harness.stderr"

kill "$TELEMETRY_PID" 2>/dev/null || true
wait "$TELEMETRY_PID" 2>/dev/null || true
TELEMETRY_PID=none
ss -lntp > "$RUN/SOCKETS_AFTER_GENERATION.txt" 2>&1 || true
"$OLLAMA_BIN" ps > "$RUN/OLLAMA_PS.txt"
nvidia-smi > "$RUN/NVIDIA_SMI_AFTER.txt"

python3 "$CODE/summarize_gpu_telemetry_v1.py" \
  --telemetry "$RUN/GPU_TELEMETRY.csv" \
  --receipt "$RUN/GPU_ENERGY_RECEIPT_V1.json"

python3 - "$RUN" <<'PY'
import hashlib, json, os, pathlib, re, sys, time
run=pathlib.Path(sys.argv[1])
smoke=json.loads((run/'raw/SMOKE_RECEIPT_V1.json').read_text())
env=(run/'ENV_SORTED.txt').read_text()
sockets=(run/'SOCKETS_BEFORE_GENERATION.txt').read_text()+"\n"+(run/'SOCKETS_AFTER_GENERATION.txt').read_text()
log=(run/'ollama-server.log').read_text(errors='replace')
listeners=[]
for line in sockets.splitlines():
    if ':11471' in line: listeners.append(line)
loopback_only=bool(listeners) and all(('127.0.0.1:11471' in x or '[::1]:11471' in x) for x in listeners)
proxy_clear=all(re.search(rf'^{name}=$',env,re.M) for name in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy'])
cloud_disabled_true='Ollama cloud disabled: true' in log
cloud_disabled_false='Ollama cloud disabled: false' in log
no_cloud_match=re.search(r'OLLAMA_NO_CLOUD:(true|false)',log)
remotes_match=re.search(r'OLLAMA_REMOTES:\[([^]]*)\]',log)
ollama_no_cloud_observed=(no_cloud_match.group(1)=='true') if no_cloud_match else None
ollama_remotes_observed=(remotes_match.group(1).split() if remotes_match and remotes_match.group(1) else [])
cloud_capability_enabled=True if cloud_disabled_false else (False if cloud_disabled_true else None)
pull_event_lines=[
 line for line in log.splitlines()
 if re.search(r'\bmsg="pulling(?: manifest| [^"]+)"',line,re.I)
]
cloud_state_complete=(
 cloud_capability_enabled is not None
 and ollama_no_cloud_observed is not None
 and remotes_match is not None
 and cloud_capability_enabled == (not ollama_no_cloud_observed)
)
model_blob=(run/'ollama-models/blobs/sha256-fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad')
route={
 'schema':'orion.p1.scienceagentbench.lunarc-openweight-route-receipt.v1',
 'status':'PASS' if smoke['status']=='PASS' and loopback_only and proxy_clear and cloud_state_complete and not pull_event_lines and model_blob.exists() else 'FAIL',
 'slurm_job_id':os.environ['SLURM_JOB_ID'],
 'model_blob_expected_sha256':'fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad',
 'ollama_content_addressed_model_blob_present':model_blob.exists(),
 'loopback_listener_only':loopback_only,'listener_lines':listeners,
 'proxy_variables_cleared':proxy_clear,
 'ollama_no_cloud_observed':ollama_no_cloud_observed,
 'ollama_remotes_observed':ollama_remotes_observed,
 'cloud_capability_enabled':cloud_capability_enabled,
 'pull_event_observed_in_retained_log':bool(pull_event_lines),
 'pull_event_lines':pull_event_lines,
 'kernel_level_egress_audit_performed':False,
 'cloud_boundary':'BOUNDARY_ONLY__CLOUD_CAPABILITY_ENABLED__NO_PULL_EVENT_OBSERVED__NO_KERNEL_EGRESS_AUDIT' if cloud_capability_enabled and not pull_event_lines else 'BOUNDARY_NOT_SATISFIED',
 'local_registry_identifier_note':'registry.ollama.ai may be a local manifest namespace and is not treated as a pull event by itself.',
 'smoke_receipt_sha256':hashlib.sha256((run/'raw/SMOKE_RECEIPT_V1.json').read_bytes()).hexdigest(),
 'cost':{'billed_usd':None,'status':'CANNOT_CHECK_PENDING_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION','gpu_seconds_and_energy_separate':True},
 'forbidden_inputs':{'protected_archive_opened':False,'benchmark_task_opened':False,'outcome_opened':False,'evaluator_opened':False,'credential_opened':False},
 'scientific_authority_delta':'NONE',
 'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
}
(run/'ROUTE_RECEIPT_V1.json').write_text(json.dumps(route,sort_keys=True,separators=(',',':'))+'\n')
if route['status']!='PASS': raise SystemExit(2)
PY

echo "P1_SAB_OPENWEIGHT_SYNTHETIC_GPU_SMOKE_PASS__JOB_${SLURM_JOB_ID}__NO_BENCHMARK_OR_PROTECTED_INPUTS" | tee "$RUN/TERMINAL.txt"
cleanup
trap - EXIT
set -Eeuo pipefail
(
  cd "$RUN"
  find . -type f ! -name REMOTE_RUN_SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > REMOTE_RUN_SHA256SUMS
)
