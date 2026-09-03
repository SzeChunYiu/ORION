#!/bin/bash
#SBATCH -J a4-echo-qwn
#SBATCH -A lu2026-2-51
#SBATCH -t 01:00:00
#SBATCH -N 1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH -o /projects/hep/fs9/users/scyiu/orion-a4/logs/echo-qwen-%j.out
# ORION A4: same-day qwen-lane echo receipt from inside a real sbatch job,
# including the gym-shaped request (dangling tool message) straight to ollama.
set -x
hostname
date -u +%Y-%m-%dT%H:%M:%SZ
DEP=/home/scyiu/orion-a4-preflight
PROJ=/projects/hep/fs9/users/scyiu/orion-a4
HARNESS=$DEP/a4-harness
LOCAL=${TMPDIR:-/local/slurmtmp.${SLURM_JOB_ID}}
mkdir -p $PROJ/receipts $PROJ/logs

# portable ollama, node-local staging (frozen qwen lane pattern)
mkdir -p $LOCAL/ollama-models
echo STAGING_TO_LOCAL
cp -r $PROJ/ollama-models/. $LOCAL/ollama-models/
du -sh $LOCAL/ollama-models
export OLLAMA_MODELS=$LOCAL/ollama-models
export OLLAMA_LOAD_TIMEOUT=1800
cd $LOCAL
cp -r $PROJ/a4-ollama-portable ./
nohup ./a4-ollama-portable/bin/ollama serve > ollama-job.log 2>&1 &
for i in $(seq 1 30); do curl -sf http://127.0.0.1:11434/api/version > /dev/null && break; sleep 2; done
curl -s http://127.0.0.1:11434/api/version; echo
./a4-ollama-portable/bin/ollama list
echo PREWARM_START
date -u +%H:%M:%S
curl -s --max-time 900 http://127.0.0.1:11434/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model": "qwen2.5:7b-instruct-q4_K_M", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1}' | head -c 200
echo

# echo probe: plain + gym-shaped (tools + tool_choice auto + dangling tool msg)
export A4_ECHO_ENDPOINT=http://127.0.0.1:11434/v1/chat/completions
export A4_ECHO_MODEL=qwen2.5:7b-instruct-q4_K_M
export A4_ECHO_TOKEN=A4_QWEN_LUNARC_ECHO_V2_OK
export A4_ECHO_TESTS=plain,gymshape
export A4_ECHO_OUTDIR=$PROJ/receipts
$DEP/sag-venv/bin/python $HARNESS/a4_echo_probe.py
PROBE_RC=$?

date -u +%Y-%m-%dT%H:%M:%SZ
echo "A4_ECHO_QWEN_DONE rc=$PROBE_RC"
exit $PROBE_RC
