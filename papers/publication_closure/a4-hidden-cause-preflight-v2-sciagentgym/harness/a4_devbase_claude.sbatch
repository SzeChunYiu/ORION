#!/bin/bash
#SBATCH -J a4-dev-cld
#SBATCH -A lu2026-2-51
#SBATCH -t 1-00:00:00
#SBATCH -N 1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH -o /projects/hep/fs9/users/scyiu/orion-a4/logs/devbase-claude-%j.out
# ORION A4: development-partition base-condition run, claude lane
# (claude-fable-5 via claude -p, nodejs/22).
# *** STAGED, NOT SUBMITTED *** A fresh same-day claude echo receipt is the
# only remaining gate: submit only after a4_probe_claude.sbatch answers with
# the echo token.
# Calibration-grade (dev partition only). In-job echo gate fires BEFORE the
# first study call; on echo failure the job cancels itself.
set -x
hostname
date -u +%Y-%m-%dT%H:%M:%SZ
module load nodejs/22.17.1
DEP=/home/scyiu/orion-a4-preflight
PROJ=/projects/hep/fs9/users/scyiu/orion-a4
HARNESS=$DEP/a4-harness
mkdir -p $PROJ/receipts $PROJ/logs

CLAUDE_DIR=$PROJ/a4-claude-lane
mkdir -p $CLAUDE_DIR
cd $CLAUDE_DIR
[ -f package.json ] || npm init -y >/dev/null
timeout 900 npm install --no-audit --no-fund @anthropic-ai/claude-code@2.1.258
./node_modules/.bin/claude --version
export A4_CLAUDE_BIN=$CLAUDE_DIR/node_modules/.bin/claude

export A4_BRIDGE_PORT=8766
export A4_BRIDGE_FAMILY=claude
export A4_BRIDGE_CWD=${TMPDIR:-/tmp}
nohup $DEP/sag-venv/bin/python $HARNESS/a4_cli_bridge_v1.py \
  > $PROJ/logs/bridge-devbase-claude-$SLURM_JOB_ID.log 2>&1 &
BRIDGE_PID=$!
for i in $(seq 1 30); do curl -sf http://127.0.0.1:8766/ >/dev/null && break; sleep 1; done
curl -s http://127.0.0.1:8766/; echo

# same-day in-job echo receipt (precondition: echo BEFORE first study call)
export A4_ECHO_ENDPOINT=http://127.0.0.1:8766/v1/chat/completions
export A4_ECHO_MODEL=claude-fable-5
export A4_ECHO_TOKEN=A4_CLAUDE_DEVBASE_ECHO_OK
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

export A4_LANE_BASE_URL=http://127.0.0.1:8766/v1
cd $DEP/SciAgentGYM
timeout 85000 $DEP/sag-venv/bin/python $HARNESS/a4_dev_base_run_v1.py \
  --model claude-fable-5 --dataset both
RUN_RC=$?
cd $DEP

TRACES=$(find $DEP/SciAgentGYM/data_analysis/tracetoanalyze/traces \
  -path "*/claude-fable-5/*_trace.json" | sort)
if [ -n "$TRACES" ]; then
  $DEP/sag-venv/bin/python $HARNESS/a4_deterministic_scorer_v1.py $TRACES \
    > $PROJ/receipts/devbase-claude-$SLURM_JOB_ID.score.json \
    2> $PROJ/receipts/devbase-claude-$SLURM_JOB_ID.score.err
  echo "SCORER_RC=$?"
else
  echo "NO_TRACES_FOUND"
fi

kill $BRIDGE_PID 2>/dev/null
date -u +%Y-%m-%dT%H:%M:%SZ
echo "A4_DEVBASE_CLAUDE_DONE run_rc=$RUN_RC"
