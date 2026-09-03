#!/usr/bin/env bash
#SBATCH -J p11cmp
#SBATCH -A lu2026-2-51
#SBATCH -p gpua40
#SBATCH -t 23:00:00
#SBATCH -n 1
#SBATCH -c 16
#SBATCH --mem=48G
#SBATCH --gres=gpu:a40:1
#SBATCH --exclude=cg14
#SBATCH -o /home/scyiu/orion-p11-campaign/logs/cmp_%j.out
# One job = one node-local ollama server (node-local models copy, no concurrent
# serve over the shared NFS blobs) + K sequential claim-workers on the same port.
# Task claims are atomic renames, so multiple jobs/nodes are safe.
set -uo pipefail
PORT=$((11500 + SLURM_JOB_ID % 300))
LOCAL_MODELS="${TMPDIR:-/local/slurmtmp.${SLURM_JOB_ID}}/ollama-models"
mkdir -p "$LOCAL_MODELS"
mkdir -p /home/scyiu/orion-p11-campaign/logs
echo "NODE=$(hostname) PORT=$PORT GPU=$CUDA_VISIBLE_DEVICES TMP=$LOCAL_MODELS"
if ! cp -r /home/scyiu/orion-p11-campaign/ollama/models/. "$LOCAL_MODELS/" 2>logs/cmp_${SLURM_JOB_ID}_modelcopy.err; then
  echo "FATAL: node-local models copy failed"; cat logs/cmp_${SLURM_JOB_ID}_modelcopy.err; exit 3
fi
du -sh "$LOCAL_MODELS"
export OLLAMA_MODELS="$LOCAL_MODELS"
export OLLAMA_HOST="127.0.0.1:$PORT"
export OLLAMA_NUM_PARALLEL=3
export OLLAMA_KEEP_ALIVE=30m
export OLLAMA_FLASH_ATTENTION=1
/home/scyiu/orion-p11-campaign/ollama/bin/ollama serve \
  > /home/scyiu/orion-p11-campaign/logs/ollama_cmp_${SLURM_JOB_ID}.log 2>&1 &
OPID=$!
for i in $(seq 1 120); do
  curl -s "http://127.0.0.1:$PORT/api/tags" >/dev/null 2>&1 && break
  sleep 2
done
curl -s "http://127.0.0.1:$PORT/api/tags" | head -c 200; echo
K=${P11_COMPILE_WORKERS:-3}
cd /home/scyiu/orion-p11-campaign/scripts
pids=()
for w in $(seq 1 "$K"); do
  python3 p11_external_compile_v1.py work --port "$PORT" --poll-s 5 --idle-exit-s 1800 \
    >> /home/scyiu/orion-p11-campaign/logs/cmpw_${SLURM_JOB_ID}_$w.log 2>&1 &
  pids+=($!)
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
kill "$OPID" 2>/dev/null || true
exit $rc
