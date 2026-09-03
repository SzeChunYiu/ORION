#!/bin/bash
#SBATCH -J a4-dev-qwn
#SBATCH -A lu2026-2-51
#SBATCH -t 1-00:00:00
#SBATCH -N 1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH -o /projects/hep/fs9/users/scyiu/orion-a4/logs/devbase-qwen-%j.out
# ORION A4: development-partition base-condition run, qwen lane
# (qwen2.5:7b-instruct-q4_K_M via portable ollama, node-local staging).
# Calibration-grade (dev partition only). In-job echo gate fires BEFORE the
# first study call; on echo failure the job cancels itself.
set -x
hostname
date -u +%Y-%m-%dT%H:%M:%SZ
DEP=/home/scyiu/orion-a4-preflight
PROJ=/projects/hep/fs9/users/scyiu/orion-a4
HARNESS=$DEP/a4-harness
LOCAL=${TMPDIR:-/local/slurmtmp.${SLURM_JOB_ID}}
mkdir -p $PROJ/receipts $PROJ/logs

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

# same-day in-job echo receipt, gym-shaped incl. dangling tool message
export A4_ECHO_ENDPOINT=http://127.0.0.1:11434/v1/chat/completions
export A4_ECHO_MODEL=qwen2.5:7b-instruct-q4_K_M
export A4_ECHO_TOKEN=A4_QWEN_DEVBASE_ECHO_OK
export A4_ECHO_TESTS=plain,gymshape
export A4_ECHO_OUTDIR=$PROJ/receipts
$DEP/sag-venv/bin/python $HARNESS/a4_echo_probe.py
PROBE_RC=$?
if [ $PROBE_RC -ne 0 ]; then
  echo "ECHO_GATE_FAILED - cancelling before any study call"
  scancel $SLURM_JOB_ID
  sleep 60
fi

# dev-partition base-condition run (resume-safe: skips traced cases)
export A4_LANE_BASE_URL=http://127.0.0.1:11434/v1
cd $DEP/SciAgentGYM
timeout 85000 $DEP/sag-venv/bin/python $HARNESS/a4_dev_base_run_v1.py \
  --model qwen2.5:7b-instruct-q4_K_M --dataset both
RUN_RC=$?
cd $DEP

# deterministic scorer over this model's traces
TRACES=$(find $DEP/SciAgentGYM/data_analysis/tracetoanalyze/traces \
  -path "*/qwen2.5:7b-instruct-q4_K_M/*_trace.json" | sort)
if [ -n "$TRACES" ]; then
  $DEP/sag-venv/bin/python $HARNESS/a4_deterministic_scorer_v1.py $TRACES \
    > $PROJ/receipts/devbase-qwen-$SLURM_JOB_ID.score.json \
    2> $PROJ/receipts/devbase-qwen-$SLURM_JOB_ID.score.err
  echo "SCORER_RC=$?"
else
  echo "NO_TRACES_FOUND"
fi

date -u +%Y-%m-%dT%H:%M:%SZ
echo "A4_DEVBASE_QWEN_DONE run_rc=$RUN_RC"
