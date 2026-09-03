#!/usr/bin/env bash
#SBATCH -J p11prot
#SBATCH -A lu2026-2-51
#SBATCH -p gpua40
#SBATCH -t 23:00:00
#SBATCH -n 1
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH --gres=gpu:a40:1
#SBATCH --exclude=cg14
#SBATCH -o /home/scyiu/orion-p11-campaign/logs/prot_%j.out
# Protected run: all 3 lanes x 9 arms x protected blocks, then finalize (oracle),
# assemble the final-analysis input, and run the frozen analyzer.
# Prerequisites (fail fast if missing): COMPILATION_RECEIPT, REGISTRY_FREEZE,
# TUNING_FREEZE, EXECUTION_MANIFEST (all lanes VERIFIED).
set -uo pipefail
export P11_BASE=/home/scyiu/orion-p11-campaign
export HOME=/home/scyiu
module load nodejs/20.9.0 2>/dev/null || true
export PATH=/home/scyiu/orion-p11-campaign/npm-prefix/bin:$PATH
command -v codex && codex --version
command -v claude && claude --version
export P11_RUN_THREADS=6
mkdir -p $P11_BASE/logs
PORT=$((11850 + SLURM_JOB_ID % 100))
LOCAL_MODELS="${TMPDIR:-/local/slurmtmp.${SLURM_JOB_ID}}/ollama-models"
mkdir -p "$LOCAL_MODELS"
cp -r $P11_BASE/ollama/models/. "$LOCAL_MODELS/"
export OLLAMA_MODELS="$LOCAL_MODELS"
export OLLAMA_HOST="127.0.0.1:$PORT"
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_KEEP_ALIVE=30m
export OLLAMA_FLASH_ATTENTION=1
export P11_OLLAMA_URL="http://127.0.0.1:$PORT"
$P11_BASE/ollama/bin/ollama serve > $P11_BASE/logs/ollama_prot_${SLURM_JOB_ID}.log 2>&1 &
OPID=$!
for i in $(seq 1 120); do curl -s "http://127.0.0.1:$PORT/api/tags" >/dev/null 2>&1 && break; sleep 2; done
R=$P11_BASE/receipts
for f in COMPILATION_RECEIPT_V1.json REGISTRY_FREEZE_V1.json TUNING_FREEZE_V1.json EXECUTION_MANIFEST_V1.json; do
  [ -f "$R/$f" ] || { echo "FATAL missing $f"; exit 21; }
done
cd $P11_BASE/scripts
python3 p11_external_protected_v1.py --lanes gpt-5.5-codexcli,claude-fable-5-cli,llama3.1-8b-ollama || exit 31
python3 p11_external_protected_v1.py --finalize || exit 32
python3 p11_external_assemble_v1.py || exit 33
python3 analyze_p11_external_final_v1.py ../results/FINAL_ANALYSIS_INPUT_V1.json \
  > ../results/FINAL_ANALYSIS_RESULT_V1.json || exit 34
kill $OPID 2>/dev/null || true
echo PROTECTED_CHAIN_DONE
