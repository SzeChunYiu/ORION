#!/usr/bin/env bash
#SBATCH --job-name=p1_sab_tok_v1
#SBATCH --account=lu2026-2-51
#SBATCH --partition=gpua40i
#SBATCH --gres=gpu:a40:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:20:00
#SBATCH --output=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_exact_tokenizer_probe_v1_20260824/slurm-%j.out
#SBATCH --error=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_exact_tokenizer_probe_v1_20260824/slurm-%j.err

set -Eeuo pipefail
umask 077

ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_exact_tokenizer_probe_v1_20260824
RUN="$ROOT/job-${SLURM_JOB_ID}"
MODEL=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_exact_model_v1_20260824/model/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf
MODEL_BYTES=18556689568
MODEL_SHA256=fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad
LIB=/sw/pkg/ollama/0.32.14/lib/ollama
SERVER="$LIB/llama-server"
BACKEND="$LIB/cuda_v13/libggml-cuda.so"
SERVER_SHA256=234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b
BACKEND_SHA256=fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb
LLAMA_CPP_VERSION=b10434
LLAMA_CPP_COMMIT=7e4c0a96880dae4fc4268ad441f8a6446bd5460a
HOST=127.0.0.1
PORT=11479
STARTED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
SERVER_PID=
CLEANUP_DONE=false
mkdir -m 700 "$RUN"

failure_receipt() {
  local rc=$1
  local command=$2
  local line=$3
  python3 - "$RUN" "$rc" "$command" "$line" <<'PY'
import hashlib, json, os, pathlib, sys, time
run=pathlib.Path(sys.argv[1])
record={
  "schema":"orion.p1.scienceagentbench.exact-gguf-tokenizer-probe-failure.v1",
  "status":"CANNOT_CHECK_TOKENIZER_PROBE_FAILED",
  "exit_code":int(sys.argv[2]),
  "failed_command_sha256":hashlib.sha256(sys.argv[3].encode("utf-8",errors="replace")).hexdigest(),
  "failed_line":int(sys.argv[4]),
  "slurm_job_id":os.environ.get("SLURM_JOB_ID"),
  "utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
  "protected_inputs_opened":False,
  "generation_invoked":False,
  "official_outcomes_opened":False,
  "cost_status":"CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE",
  "scientific_authority_delta":"NONE",
}
(run/"JOB_FAILURE_V1.json").write_text(json.dumps(record,sort_keys=True,separators=(",",":"))+"\n")
PY
}

cleanup_server() {
  set +e
  if [[ -n "$SERVER_PID" ]]; then
    kill -TERM -- "-$SERVER_PID" 2>/dev/null
    for _ in $(seq 1 60); do
      kill -0 -- "-$SERVER_PID" 2>/dev/null || break
      sleep 0.25
    done
    if kill -0 -- "-$SERVER_PID" 2>/dev/null; then
      kill -KILL -- "-$SERVER_PID" 2>/dev/null
    fi
    wait "$SERVER_PID" 2>/dev/null
  fi
  local group_absent=true
  if [[ -n "$SERVER_PID" ]] && kill -0 -- "-$SERVER_PID" 2>/dev/null; then
    group_absent=false
  fi
  python3 - "$RUN" "$HOST" "$PORT" "$group_absent" <<'PY'
import json, pathlib, socket, sys
run=pathlib.Path(sys.argv[1]); host=sys.argv[2]; port=int(sys.argv[3]); group_absent=sys.argv[4]=="true"
listener_absent=False
try:
    with socket.create_connection((host,port),timeout=1.0):
        listener_absent=False
except OSError:
    listener_absent=True
record={
  "schema":"orion.p1.scienceagentbench.exact-gguf-tokenizer-cleanup.v1",
  "status":"PASS_PROCESS_GROUP_AND_LISTENER_ABSENT" if group_absent and listener_absent else "CANNOT_CHECK",
  "process_group_absent":group_absent,
  "loopback_listener_absent":listener_absent,
  "production_admissibility":"CANNOT_CHECK",
  "scientific_authority_delta":"NONE",
}
(run/"CLEANUP_V1.json").write_text(json.dumps(record,sort_keys=True,separators=(",",":"))+"\n")
PY
  CLEANUP_DONE=true
  SERVER_PID=
  set -e
}

on_exit() {
  local rc=$?
  local command=${BASH_COMMAND:-unknown}
  local line=${BASH_LINENO[0]:-0}
  if [[ "$CLEANUP_DONE" != true ]]; then cleanup_server || true; fi
  if (( rc != 0 )); then failure_receipt "$rc" "$command" "$line" || true; fi
}
trap on_exit EXIT

module purge
module load ollama/0.32.14
export HTTP_PROXY= HTTPS_PROXY= ALL_PROXY= http_proxy= https_proxy= all_proxy=
export NO_PROXY=127.0.0.1,localhost no_proxy=127.0.0.1,localhost
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN OPENAI_API_KEY ANTHROPIC_API_KEY AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN GOOGLE_APPLICATION_CREDENTIALS || true

test "$(stat -c %s "$MODEL")" = "$MODEL_BYTES"
MODEL_OBSERVED_SHA256=$(sha256sum "$MODEL" | awk '{print $1}')
SERVER_OBSERVED_SHA256=$(sha256sum "$SERVER" | awk '{print $1}')
BACKEND_OBSERVED_SHA256=$(sha256sum "$BACKEND" | awk '{print $1}')
test "$MODEL_OBSERVED_SHA256" = "$MODEL_SHA256"
test "$SERVER_OBSERVED_SHA256" = "$SERVER_SHA256"
test "$BACKEND_OBSERVED_SHA256" = "$BACKEND_SHA256"
SERVER_VERSION_OUTPUT=$(LD_LIBRARY_PATH="$LIB:$LIB/cuda_v13" "$SERVER" --version 2>&1)
grep -q 'commit 7e4c0a968' <<< "$SERVER_VERSION_OUTPUT"

{
  echo "model_bytes=$(stat -c %s "$MODEL")"
  echo "model_sha256=$MODEL_OBSERVED_SHA256"
  echo "llama_server_sha256=$SERVER_OBSERVED_SHA256"
  echo "cuda_backend_sha256=$BACKEND_OBSERVED_SHA256"
  echo "llama_cpp_version=$LLAMA_CPP_VERSION"
  echo "llama_cpp_commit=$LLAMA_CPP_COMMIT"
  echo "llama_server_version=$SERVER_VERSION_OUTPUT"
} > "$RUN/FROZEN_RUNTIME_HASHES.txt"

cat > "$RUN/FROZEN_TOKENIZER_GEOMETRY.json" <<EOF_GEOMETRY
{"cache_prompt":"NOT_APPLICABLE_TOKENIZE_ENDPOINT","context_shift":false,"context_tokens":32768,"continuous_batching":false,"host":"127.0.0.1","parallel_slots":1,"port":11479,"route":"POST /tokenize","server_prompt_cache_used":false}
EOF_GEOMETRY

CUDA_VISIBLE=${CUDA_VISIBLE_DEVICES:-}
setsid env -i \
  HOME="$HOME" PATH=/usr/bin:/bin LANG=C.UTF-8 \
  CUDA_VISIBLE_DEVICES="$CUDA_VISIBLE" \
  LD_LIBRARY_PATH="$LIB:$LIB/cuda_v13" GGML_BACKEND_PATH="$BACKEND" \
  HTTP_PROXY= HTTPS_PROXY= ALL_PROXY= http_proxy= https_proxy= all_proxy= \
  NO_PROXY=127.0.0.1,localhost no_proxy=127.0.0.1,localhost \
  "$SERVER" \
    --model "$MODEL" --host "$HOST" --port "$PORT" \
    --ctx-size 32768 --parallel 1 --no-cont-batching \
    --threads 8 --threads-batch 8 --batch-size 512 --ubatch-size 512 \
    --cache-type-k f16 --cache-type-v f16 --flash-attn on \
    --n-gpu-layers all --no-context-shift --metrics --slots \
    > "$RUN/llama-server.log" 2>&1 &
SERVER_PID=$!

python3 - "$RUN" "$HOST" "$PORT" <<'PY'
import hashlib, http.client, json, pathlib, sys, time
run=pathlib.Path(sys.argv[1]); host=sys.argv[2]; port=int(sys.argv[3])

def request(method,path,value=None,timeout=10.0):
    body=None if value is None else json.dumps(value,allow_nan=False,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    headers={} if body is None else {"Content-Type":"application/json"}
    conn=http.client.HTTPConnection(host,port,timeout=timeout)
    try:
        conn.request(method,path,body=body,headers=headers)
        response=conn.getresponse(); raw=response.read()
    finally:
        conn.close()
    if response.status != 200:
        raise RuntimeError(f"{path} HTTP {response.status}: {raw[:500]!r}")
    return raw, json.loads(raw.decode("utf-8"))

deadline=time.monotonic()+600
last=None
while time.monotonic()<deadline:
    try:
        health_raw,health=request("GET","/health",timeout=2.0)
        slots_raw,slots=request("GET","/slots",timeout=2.0)
        if isinstance(slots,list) and len(slots)==1: break
    except Exception as exc:
        last=exc; time.sleep(0.25)
else:
    raise RuntimeError("server readiness failed") from last
props_raw,props=request("GET","/props")
(run/"HEALTH.json").write_bytes(health_raw)
(run/"SLOTS.json").write_bytes(slots_raw)
(run/"PROPS.json").write_bytes(props_raw)

prompts=[
  ("ascii","INVENTED_TOKENIZER_PROBE_ALPHA_7f91\n"),
  ("unicode","Invented café Δ 中文🙂 line\nsecond invented line.\n"),
  ("json_like","ORION invented prompt only. Attempt ordinal: 1. Canonical invented packet JSON follows:\n{\"dataset_preview\":null,\"domain\":\"synthetic\",\"instance_id\":\"SYNTHETIC-1\",\"task_inst\":\"invented\"}\n"),
  ("literal_special_marker","Invented literal marker <|im_start|> remains synthetic and opens no task.\n"),
]
modes=[
  ("completion_equivalent",True,True),
  ("plain_no_special",False,False),
]
records=[]
for label,text in prompts:
    mode_tokens={}
    for mode,add_special,parse_special in modes:
        arrays=[]; raw_hashes=[]
        request_obj={"content":text,"add_special":add_special,"parse_special":parse_special}
        request_bytes=json.dumps(request_obj,allow_nan=False,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
        for _ in range(3):
            raw,response=request("POST","/tokenize",request_obj)
            tokens=response.get("tokens")
            if not isinstance(tokens,list) or any(isinstance(x,bool) or not isinstance(x,int) for x in tokens):
                raise RuntimeError("/tokenize returned a noninteger token array")
            arrays.append(tokens); raw_hashes.append(hashlib.sha256(raw).hexdigest())
        if not all(array==arrays[0] for array in arrays[1:]):
            raise RuntimeError("/tokenize token IDs were not repeatable")
        mode_tokens[mode]=arrays[0]
        records.append({
          "prompt_label":label,
          "prompt_bytes":len(text.encode("utf-8")),
          "prompt_sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),
          "mode":mode,
          "add_special":add_special,
          "parse_special":parse_special,
          "request_sha256":hashlib.sha256(request_bytes).hexdigest(),
          "repeat_count":3,
          "repeatable_token_ids":True,
          "response_raw_sha256s":raw_hashes,
          "token_count":len(arrays[0]),
          "token_ids":arrays[0],
        })
    records.append({
      "prompt_label":label,
      "mode_comparison":"completion_equivalent_vs_plain_no_special",
      "token_arrays_identical":mode_tokens["completion_equivalent"]==mode_tokens["plain_no_special"],
    })
receipt={
  "schema":"orion.p1.scienceagentbench.exact-gguf-tokenizer-probe.v1",
  "status":"PASS_EXACT_GGUF_TOKENIZE_ROUTE_REPEATABLE",
  "route":{"method":"POST","path":"/tokenize","host":host,"port":port,"generation_invoked":False,"external_api_invoked":False},
  "geometry":{"context_tokens":32768,"parallel_slots":1,"continuous_batching":False,"context_shift":False,"cache_prompt":"NOT_APPLICABLE_TOKENIZE_ENDPOINT","server_prompt_cache_used":False,"slot_count":len(slots)},
  "model_tokenizer_metadata":{"add_bos_token":False,"add_eos_token":False},
  "records":records,
  "prompt_bodies_retained":False,
  "protected_inputs_opened":False,
  "official_tasks_opened":0,
  "generation_invoked":False,
  "official_outcomes_opened":0,
  "credentials_used":False,
  "production_admissibility":"CANNOT_CHECK",
  "scientific_authority_delta":"NONE",
}
(run/"TOKENIZER_PROBE_V1.json").write_text(json.dumps(receipt,allow_nan=False,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n")
PY

cleanup_server
POST_MODEL_SHA256=$(sha256sum "$MODEL" | awk '{print $1}')
test "$POST_MODEL_SHA256" = "$MODEL_SHA256"
FINISHED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
python3 - "$RUN" "$SLURM_JOB_ID" "$STARTED_UTC" "$FINISHED_UTC" "$MODEL_SHA256" "$SERVER_SHA256" "$BACKEND_SHA256" "$LLAMA_CPP_VERSION" "$LLAMA_CPP_COMMIT" <<'PY'
import hashlib, json, pathlib, sys
run=pathlib.Path(sys.argv[1])
probe=json.loads((run/"TOKENIZER_PROBE_V1.json").read_text())
cleanup=json.loads((run/"CLEANUP_V1.json").read_text())
record={
  "schema":"orion.p1.scienceagentbench.exact-gguf-tokenizer-job.v1",
  "status":"PASS_EXACT_GGUF_TOKENIZER_CAPABILITY" if probe["status"].startswith("PASS_") and cleanup["status"].startswith("PASS_") else "CANNOT_CHECK",
  "slurm_job_id":sys.argv[2],
  "started_utc":sys.argv[3],
  "finished_utc":sys.argv[4],
  "runtime":{"model_sha256":sys.argv[5],"llama_server_sha256":sys.argv[6],"cuda_backend_sha256":sys.argv[7],"llama_cpp_version":sys.argv[8],"llama_cpp_commit":sys.argv[9]},
  "tokenizer_probe_sha256":hashlib.sha256((run/"TOKENIZER_PROBE_V1.json").read_bytes()).hexdigest(),
  "cleanup_sha256":hashlib.sha256((run/"CLEANUP_V1.json").read_bytes()).hexdigest(),
  "production_prompt_token_ledger_capability":"SUPPORTED_WITH_EXACT_FROZEN_GGUF_AND_EXPLICIT_POST_TOKENIZE_MODE",
  "safe_tokenize_mode":{"add_special":True,"parse_special":True,"route":"POST /tokenize","repeatability_check_required":True},
  "protected_inputs_opened":False,
  "generation_invoked":False,
  "official_outcomes_opened":False,
  "external_api_invoked":False,
  "credentials_used":False,
  "cost":{"billed_usd":None,"status":"CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE"},
  "production_admissibility":"CANNOT_CHECK",
  "scientific_authority_delta":"NONE",
}
(run/"JOB_RECEIPT_V1.json").write_text(json.dumps(record,sort_keys=True,separators=(",",":"))+"\n")
PY

echo "P1_SAB_EXACT_GGUF_TOKENIZER_PROBE_PASS__JOB_${SLURM_JOB_ID}__NO_GENERATION__NO_PROTECTED_INPUTS__COST_CANNOT_CHECK"
