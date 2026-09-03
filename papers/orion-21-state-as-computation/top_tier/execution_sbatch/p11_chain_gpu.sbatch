#!/usr/bin/env bash
#SBATCH -J p11chain
#SBATCH -A lu2026-2-51
#SBATCH -p gpua40
#SBATCH -t 23:00:00
#SBATCH -n 1
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH --gres=gpu:a40:1
#SBATCH --exclude=cg14
#SBATCH -o /home/scyiu/orion-p11-campaign/logs/chain_%j.out
# Idempotent post-compile chain on one GPU node:
#   1. compile finalize        -> receipts/COMPILATION_RECEIPT_V1.json
#   2. registry reveal         -> receipts/REGISTRY_FREEZE_V1.json
#   3. tuning (LOBO, gpt lane) -> receipts/TUNING_FREEZE_V1.json
#   4. manifest emission       -> receipts/EXECUTION_MANIFEST_V1.json (needs all 3
#      lanes VERIFIED; refuses otherwise — rerun after the claude probe if needed)
# Each step is skipped when its receipt already exists, so reruns are cheap.
set -uo pipefail
export P11_BASE=/home/scyiu/orion-p11-campaign
export HOME=/home/scyiu
module load nodejs/20.9.0 2>/dev/null || true
export PATH=/home/scyiu/orion-p11-campaign/npm-prefix/bin:$PATH
command -v codex && codex --version
command -v claude && claude --version || true
mkdir -p $P11_BASE/logs
PORT=$((11800 + SLURM_JOB_ID % 200))
LOCAL_MODELS="${TMPDIR:-/local/slurmtmp.${SLURM_JOB_ID}}/ollama-models"
mkdir -p "$LOCAL_MODELS"
cp -r $P11_BASE/ollama/models/. "$LOCAL_MODELS/"
export OLLAMA_MODELS="$LOCAL_MODELS"
export OLLAMA_HOST="127.0.0.1:$PORT"
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_KEEP_ALIVE=30m
export OLLAMA_FLASH_ATTENTION=1
export P11_OLLAMA_URL="http://127.0.0.1:$PORT"
$P11_BASE/ollama/bin/ollama serve > $P11_BASE/logs/ollama_chain_${SLURM_JOB_ID}.log 2>&1 &
OPID=$!
for i in $(seq 1 120); do curl -s "http://127.0.0.1:$PORT/api/tags" >/dev/null 2>&1 && break; sleep 2; done
curl -s "http://127.0.0.1:$PORT/api/tags" | head -c 200; echo
cd $P11_BASE/scripts
R=$P11_BASE/receipts

step() { echo "=== [$(date +%H:%M:%S)] $1 ==="; }

step "1 compile finalize"
if [ -f $R/COMPILATION_RECEIPT_V1.json ]; then echo skip; else
  python3 p11_external_compile_v1.py finalize || exit 11
fi

step "2 registry reveal"
if [ -f $R/REGISTRY_FREEZE_V1.json ]; then echo skip; else
  python3 p11_external_registry_builder_v1.py --reveal-fresh || exit 12
fi

step "3 tuning (LOBO)"
if [ -f $R/TUNING_FREEZE_V1.json ]; then echo skip; else
  export P11_TUNE_THREADS=8
  python3 p11_external_tune_v1.py || exit 13
fi

step "4 manifest emission"
if [ -f $R/EXECUTION_MANIFEST_V1.json ]; then echo skip; else
  python3 p11_external_manifest_v1.py || exit 14   # refuses while claude lane unverified
fi

step "chain complete"
kill $OPID 2>/dev/null || true
