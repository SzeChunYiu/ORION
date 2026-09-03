#!/bin/bash
#SBATCH -J a4-prb-cld
#SBATCH -A lu2026-2-51
#SBATCH -t 01:00:00
#SBATCH -N 1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH -o /projects/hep/fs9/users/scyiu/orion-a4/logs/probe-claude-%j.out
# ORION A4: claude-lane probe under nodejs/22 (fixes the recorded EBADENGINE:
# claude-code 2.1.258 requires node >=22 while the recorded lane job loaded
# nodejs/20.9.0). Captures the lane's verbatim answer or wall banner.
set -x
hostname
date -u +%Y-%m-%dT%H:%M:%SZ
module load nodejs/22.17.1
node --version
DEP=/home/scyiu/orion-a4-preflight
PROJ=/projects/hep/fs9/users/scyiu/orion-a4
HARNESS=$DEP/a4-harness
mkdir -p $PROJ/receipts $PROJ/logs

# claude lane install on fs9 (idempotent)
CLAUDE_DIR=$PROJ/a4-claude-lane
mkdir -p $CLAUDE_DIR
cd $CLAUDE_DIR
[ -f package.json ] || npm init -y >/dev/null
timeout 900 npm install --no-audit --no-fund @anthropic-ai/claude-code@2.1.258
./node_modules/.bin/claude --version
export A4_CLAUDE_BIN=$CLAUDE_DIR/node_modules/.bin/claude

# 1) direct CLI probe, verbatim capture
DIRECT_OUT=$PROJ/receipts/claude-direct-probe-$SLURM_JOB_ID.txt
timeout 300 ./node_modules/.bin/claude -p --model claude-fable-5 \
  'Reply with exactly this token and nothing else: A4_CLAUDE_LUNARC_ECHO_V2_OK' \
  > $DIRECT_OUT 2>&1
DIRECT_RC=$?
echo "DIRECT_RC=$DIRECT_RC"
cat $DIRECT_OUT
grep -q A4_CLAUDE_LUNARC_ECHO_V2_OK $DIRECT_OUT && DIRECT_STATE=ANSWERING || DIRECT_STATE=WALLED

# 2) bridge mechanics validation (family=claude); response is whatever the
#    lane yields tonight - verbatim receipt either way
export A4_BRIDGE_PORT=8766
export A4_BRIDGE_FAMILY=claude
export A4_BRIDGE_CWD=${TMPDIR:-/tmp}
nohup $DEP/sag-venv/bin/python $HARNESS/a4_cli_bridge_v1.py \
  > $PROJ/logs/bridge-probe-claude-$SLURM_JOB_ID.log 2>&1 &
BRIDGE_PID=$!
for i in $(seq 1 30); do curl -sf http://127.0.0.1:8766/ >/dev/null && break; sleep 1; done
curl -s http://127.0.0.1:8766/; echo
export A4_ECHO_ENDPOINT=http://127.0.0.1:8766/v1/chat/completions
export A4_ECHO_MODEL=claude-fable-5
export A4_ECHO_TOKEN=A4_CLAUDE_LUNARC_ECHO_V2_OK
export A4_ECHO_TESTS=plain,gymshape
export A4_ECHO_OUTDIR=$PROJ/receipts
$DEP/sag-venv/bin/python $HARNESS/a4_echo_probe.py
PROBE_RC=$?
kill $BRIDGE_PID 2>/dev/null

# 3) state file (banner verbatim, reset time if present)
{
  echo "A4_CLAUDE_LANE_STATE — recorded_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) job=$SLURM_JOB_ID node=$(hostname)"
  echo "state=$DIRECT_STATE direct_rc=$DIRECT_RC"
  echo "--- verbatim direct output (first 40 lines) ---"
  head -40 $DIRECT_OUT
  echo "--- end verbatim ---"
} > $DEP/A4_CLAUDE_LANE_STATE.txt
cat $DEP/A4_CLAUDE_LANE_STATE.txt
date -u +%Y-%m-%dT%H:%M:%SZ
echo "A4_PROBE_CLAUDE_DONE state=$DIRECT_STATE"
