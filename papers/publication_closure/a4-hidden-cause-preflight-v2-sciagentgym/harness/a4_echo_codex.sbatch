#!/bin/bash
#SBATCH -J a4-echo-cdx
#SBATCH -A lu2026-2-51
#SBATCH -t 00:40:00
#SBATCH -N 1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH -o /projects/hep/fs9/users/scyiu/orion-a4/logs/echo-codex-%j.out
# ORION A4: same-day codex-lane echo receipt from inside a real sbatch job.
set -x
hostname
date -u +%Y-%m-%dT%H:%M:%SZ
module load nodejs/20.9.0
node --version
DEP=/home/scyiu/orion-a4-preflight
PROJ=/projects/hep/fs9/users/scyiu/orion-a4
HARNESS=$DEP/a4-harness
mkdir -p $PROJ/receipts $PROJ/logs

# codex lane install (idempotent; operator pin 0.129.0-alpha.15 forever)
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
  > $PROJ/logs/bridge-echo-codex-$SLURM_JOB_ID.log 2>&1 &
BRIDGE_PID=$!
for i in $(seq 1 30); do curl -sf http://127.0.0.1:8765/ >/dev/null && break; sleep 1; done
curl -s http://127.0.0.1:8765/; echo

# echo probe: plain + gym-shaped + big-prompt (stdin transport) -> fs9 receipts
export A4_ECHO_ENDPOINT=http://127.0.0.1:8765/v1/chat/completions
export A4_ECHO_MODEL=gpt-5.5
export A4_ECHO_TOKEN=A4_CODEX_LUNARC_ECHO_V2_OK
export A4_ECHO_TESTS=plain,gymshape,bigprompt
export A4_ECHO_OUTDIR=$PROJ/receipts
$DEP/sag-venv/bin/python $HARNESS/a4_echo_probe.py
PROBE_RC=$?

kill $BRIDGE_PID 2>/dev/null
date -u +%Y-%m-%dT%H:%M:%SZ
echo "A4_ECHO_CODEX_DONE rc=$PROBE_RC"
exit $PROBE_RC
