#!/bin/bash
#SBATCH -J a4-dev-cdx
#SBATCH -A lu2026-2-51
#SBATCH -t 1-00:00:00
#SBATCH -N 1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH -o /projects/hep/fs9/users/scyiu/orion-a4/logs/devbase-codex-%j.out
# ORION A4: development-partition base-condition run, codex lane (gpt-5.5).
# Usage: sbatch a4_devbase_codex.sbatch <single|multi>
# Calibration-grade (dev partition only). In-job echo gate fires BEFORE the
# first study call; on echo failure the job cancels itself.
set -x
hostname
date -u +%Y-%m-%dT%H:%M:%SZ
module load nodejs/20.9.0
DEP=/home/scyiu/orion-a4-preflight
PROJ=/projects/hep/fs9/users/scyiu/orion-a4
HARNESS=$DEP/a4-harness
DATASET=${1:-multi}
mkdir -p $PROJ/receipts $PROJ/logs

# codex lane install (idempotent; operator pin)
mkdir -p $DEP/a4-codex-lane
cd $DEP/a4-codex-lane
[ -f package.json ] || npm init -y >/dev/null
timeout 600 npm install --no-audit --no-fund @openai/codex@0.129.0-alpha.15
./node_modules/.bin/codex --version
export A4_CODEX_BIN=$DEP/a4-codex-lane/node_modules/.bin/codex

# job-local bridge
export A4_BRIDGE_PORT=8765
export A4_BRIDGE_FAMILY=codex
export A4_BRIDGE_CWD=${TMPDIR:-/tmp}
nohup $DEP/sag-venv/bin/python $HARNESS/a4_cli_bridge_v1.py \
  > $PROJ/logs/bridge-devbase-codex-$SLURM_JOB_ID.log 2>&1 &
BRIDGE_PID=$!
for i in $(seq 1 30); do curl -sf http://127.0.0.1:8765/ >/dev/null && break; sleep 1; done
curl -s http://127.0.0.1:8765/; echo

# same-day in-job echo receipt (precondition: echo BEFORE first study call)
export A4_ECHO_ENDPOINT=http://127.0.0.1:8765/v1/chat/completions
export A4_ECHO_MODEL=gpt-5.5
export A4_ECHO_TOKEN=A4_CODEX_DEVBASE_ECHO_OK
export A4_ECHO_TESTS=plain
export A4_ECHO_OUTDIR=$PROJ/receipts
$DEP/sag-venv/bin/python $HARNESS/a4_echo_probe.py
PROBE_RC=$?
if [ $PROBE_RC -ne 0 ]; then
  echo "ECHO_GATE_FAILED - cancelling before any study call"
  kill $BRIDGE_PID 2>/dev/null
  scancel $SLURM_JOB_ID
  sleep 60
fi

# dev-partition base-condition run (resume-safe: skips traced cases)
export A4_LANE_BASE_URL=http://127.0.0.1:8765/v1
cd $DEP/SciAgentGYM
timeout 85000 $DEP/sag-venv/bin/python $HARNESS/a4_dev_base_run_v1.py \
  --model gpt-5.5 --dataset $DATASET
RUN_RC=$?
cd $DEP

# deterministic scorer over this model's traces
TRACES=$(find $DEP/SciAgentGYM/data_analysis/tracetoanalyze/traces \
  -path "*/gpt-5.5/*_trace.json" | sort)
if [ -n "$TRACES" ]; then
  $DEP/sag-venv/bin/python $HARNESS/a4_deterministic_scorer_v1.py $TRACES \
    > $PROJ/receipts/devbase-codex-$DATASET-$SLURM_JOB_ID.score.json \
    2> $PROJ/receipts/devbase-codex-$DATASET-$SLURM_JOB_ID.score.err
  echo "SCORER_RC=$?"
else
  echo "NO_TRACES_FOUND"
fi

kill $BRIDGE_PID 2>/dev/null
date -u +%Y-%m-%dT%H:%M:%SZ
echo "A4_DEVBASE_CODEX_DONE dataset=$DATASET run_rc=$RUN_RC"
