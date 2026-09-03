#!/bin/bash
#SBATCH -J p12-claude-tune
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 08:00:00
#SBATCH -N 1
#SBATCH --tasks-per-node=1
#SBATCH -D /projects/hep/fs9/users/scyiu/orion-a2-p12
#SBATCH -o logs/p12-claude-tune-%j.out
#SBATCH --begin=2026-09-04T03:05:00
# Claude-lane tuning, scheduled after the account usage window reset
# (2026-09-04 03:00 Europe/Stockholm, per MODEL_IDENTITY_FREEZE_V1.json).
# Fresh same-day echo FIRST (ordering rule); the lane-scoped gate in the
# driver then refuses to run unless the claude echo passed on this date.
set -x
P12BASE=/projects/hep/fs9/users/scyiu/orion-a2-p12
export PATH=$HOME/.local/bin:$P12BASE/miniconda3/bin:$PATH
module load nodejs/20.9.0
# Same PYTHONPATH hygiene as the other jobs: the module system's EasyBuild
# python3.11 site-packages must not leak into the driver or lane subprocesses.
unset PYTHONPATH
export PYTHONNOUSERSITE=1
cd "$P12BASE/worktree/papers/orion-22-adaptive-state-reasoning/top_tier" || exit 20

# No `|| exit` on the echo step on purpose: it probes BOTH lanes, and only the
# claude lane's same-day result gates this job (the driver's lane-scoped gate
# is the authority; a codex-side echo failure must not block the claude lane).
"$P12BASE/miniconda3/bin/conda" run -n sci-agent --no-capture-output python campaign_tuning_driver_v1.py --echo-check
"$P12BASE/miniconda3/bin/conda" run -n sci-agent --no-capture-output python campaign_tuning_driver_v1.py \
  --run --lane claude-fable-5-claudecli \
  --parquet "$P12BASE/a2-deps/sab_verified.parquet"
RC=$?
echo "P12_CLAUDE_TUNING_RC=$RC"
echo P12_CLAUDE_TUNING_DONE
exit $RC
