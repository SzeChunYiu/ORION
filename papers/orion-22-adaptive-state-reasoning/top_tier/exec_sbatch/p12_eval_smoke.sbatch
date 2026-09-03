#!/bin/bash
#SBATCH -J p12-eval-smoke
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 01:30:00
#SBATCH -N 1
#SBATCH --tasks-per-node=1
#SBATCH -D /projects/hep/fs9/users/scyiu/orion-a2-p12
#SBATCH -o logs/p12-eval-smoke-%j.out
# ONE-cell eval smoke: validates the full upstream-evaluator path on LUNARC
# (conda run of pred program, config_conda_env pip-compile/sync, judge shim
# codex calls) before the full 68-cell tuning eval is submitted.
# Success criterion: one eval record written under eval/tuning/ with a
# boolean success_rate, exit 0, no INFRASTRUCTURE_ERROR.
set -x
P12BASE=/projects/hep/fs9/users/scyiu/orion-a2-p12
export PATH=$HOME/.local/bin:$P12BASE/miniconda3/bin:$PATH
module load nodejs/20.9.0
# Same PYTHONPATH hygiene as the other jobs (module-system EasyBuild
# python3.11 site-packages must not leak into any subprocess).
unset PYTHONPATH
export PYTHONNOUSERSITE=1
cd "$P12BASE/worktree/papers/orion-22-adaptive-state-reasoning/top_tier" || exit 20

"$P12BASE/miniconda3/bin/conda" run -n sci-agent --no-capture-output python campaign_eval_driver_v1.py \
  --phase tuning --limit 1 \
  --parquet "$P12BASE/a2-deps/sab_verified.parquet" \
  --repo "$P12BASE/a2-deps/ScienceAgentBench"
RC=$?
echo "P12_EVAL_SMOKE_RC=$RC"
ls -la eval/tuning/*/ 2>/dev/null | head -20
echo P12_EVAL_SMOKE_DONE
exit $RC
