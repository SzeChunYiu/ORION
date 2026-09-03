#!/bin/bash
#SBATCH -J p11ow7cpu
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 02:00:00
#SBATCH -n 1
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH -o /home/scyiu/orion-p11-campaign/logs/ow7_%j.out
set -x
echo NODE=$(hostname) CORES=$SLURM_CPUS_PER_TASK GPU=$CUDA_VISIBLE_DEVICES
command -v zstd || module load zstd 2>/dev/null || true
command -v zstd && zstd --version
mkdir -p ~/orion-p11-campaign/ollama
cd ~/orion-p11-campaign/ollama
if [ ! -x bin/ollama ]; then
  curl -fL --retry 3 -o ollama.tar.zst https://github.com/ollama/ollama/releases/download/v0.33.2/ollama-linux-amd64.tar.zst
  ls -la ollama.tar.zst
  tar --zstd -xf ollama.tar.zst && rm -f ollama.tar.zst
  ls -la bin/ lib/ 2>/dev/null | head -8
fi
./bin/ollama --version || true
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_MODELS=/home/scyiu/orion-p11-campaign/ollama/models
export OLLAMA_NUM_PARALLEL=2
mkdir -p $OLLAMA_MODELS
nohup ./bin/ollama serve > /home/scyiu/orion-p11-campaign/logs/ollama_serve_${SLURM_JOB_ID}.log 2>&1 &
for i in $(seq 1 60); do curl -s http://127.0.0.1:11434/ >/dev/null && break; sleep 2; done
curl -s http://127.0.0.1:11434/ ; echo
./bin/ollama pull llama3.1:8b 2>&1 | tail -3
./bin/ollama pull bge-m3 2>&1 | tail -3
./bin/ollama list
echo ---GENERATE_ECHO_BEGIN
python3 - << ECHOEOF
import json, time, urllib.request
payload = json.dumps({"model":"llama3.1:8b","prompt":"Reply with exactly: P11OPENPROBE","stream":False,"options":{"num_ctx":2048,"temperature":0.6,"top_p":0.9,"seed":42}}).encode()
t0=time.time()
req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=payload, headers={"Content-Type":"application/json"})
r = json.loads(urllib.request.urlopen(req, timeout=600).read())
print("ECHO_PROBE out=", repr(r.get("response","")[:80]), "secs=", round(time.time()-t0,1))
ECHOEOF
echo ---GENERATE_ECHO_END
echo ---MAP_TIMING_BEGIN
python3 - << PYEOF
import json, time, urllib.request
seg = "word " * 2000
prompt = "Extract durable facts from the segment. Output ONLY a numbered list, max 12 lines.\n\nSEGMENT:\n" + seg
payload = json.dumps({"model":"llama3.1:8b","prompt":prompt,"stream":False,"options":{"num_ctx":4096,"temperature":0.6,"top_p":0.9,"seed":42}}).encode()
t0=time.time()
req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=payload, headers={"Content-Type":"application/json"})
r = json.loads(urllib.request.urlopen(req, timeout=3600).read())
print("MAP_TIMING in=", r.get("prompt_eval_count"), "out=", r.get("eval_count"), "secs=", round(time.time()-t0,1))
PYEOF
echo ---MAP_TIMING_END
echo ---EMBED_BEGIN
curl -s http://127.0.0.1:11434/api/embed -d "{\"model\": \"bge-m3\", \"input\": \"hello world\"}" | head -c 120; echo
echo ---EMBED_END
nproc; nproc --query-gpu=name,memory.used,memory.total --format=csv 2>/dev/null | head -3
