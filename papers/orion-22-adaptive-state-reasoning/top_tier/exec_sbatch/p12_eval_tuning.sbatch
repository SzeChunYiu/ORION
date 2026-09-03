#!/bin/bash
#SBATCH -J p12-eval-tune
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 2-00:00:00
#SBATCH -N 1
#SBATCH --tasks-per-node=1
#SBATCH -D /projects/hep/fs9/users/scyiu/orion-a2-p12
#SBATCH -o logs/p12-eval-tune-%j.out
# Evaluates every TUNING-phase run record that exists (codex lane complete
# 2026-09-03 on billy-old; claude lane joins after its scheduled tuning job).
# Resumable: existing eval records are skipped; missing run records are
# skipped silently. Judge calls run through the frozen codex lane shim.
set -x
P12BASE=/projects/hep/fs9/users/scyiu/orion-a2-p12
export PATH=$HOME/.local/bin:$P12BASE/miniconda3/bin:$PATH
module load nodejs/20.9.0
cd "$P12BASE/worktree/papers/orion-22-adaptive-state-reasoning/top_tier" || exit 20

"$P12BASE/miniconda3/bin/conda" run -n sci-agent --no-capture-output python campaign_eval_driver_v1.py \
  --phase tuning \
  --parquet "$P12BASE/a2-deps/sab_verified.parquet" \
  --repo "$P12BASE/a2-deps/ScienceAgentBench"
RC=$?
echo "P12_EVAL_TUNING_RC=$RC"
if [ "$RC" -eq 0 ]; then
  "$P12BASE/miniconda3/bin/conda" run -n sci-agent --no-capture-output python campaign_eval_driver_v1.py \
    --phase tuning --emit-matrix
  echo "P12_EVAL_TUNING_MATRIX_RC=$?"
fi
echo P12_EVAL_TUNING_DONE
