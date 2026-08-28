#!/usr/bin/env bash
#SBATCH --job-name=o02-r23-node87
#SBATCH --partition=lu48
#SBATCH --account=lu2026-2-51
#SBATCH --nodelist=cn087
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --output=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO02R24/.codex-run/r24-diag/slurm-%A_%a.out
#SBATCH --error=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO02R24/.codex-run/r24-diag/slurm-%A_%a.err
#SBATCH --array=0-1
set -euo pipefail
B=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO02R24
D=$B/papers/orion-02-fiberguard-finite-fibre/rounds/r24-arm-conditional-fibres-revival
SUBJECT=/projects/hep/fs9/scratch/scyiu-orion-ci/pmlb-src
PY=/projects/hep/fs9/scratch/scyiu-orion-ci/ORION/.venv/bin/python
cd $B
test "$(git rev-parse HEAD)" = 65e319b436cbb1d6fc98b2d462be5e89925a3caa
test "$(git -C $SUBJECT rev-parse HEAD)" = 7c1f4bdc00136dc2e55c87fa6b8ba6e8af6d1a68
if [ "$SLURM_ARRAY_TASK_ID" = 0 ]; then
  unset PYTHONHASHSEED OPENBLAS_NUM_THREADS OMP_NUM_THREADS MKL_NUM_THREADS NUMEXPR_NUM_THREADS || true
  tag=original-env
else
  export PYTHONHASHSEED=0 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  tag=single-thread
fi
$PY $D/diagnose_r23_parent_replay_r24.py --subject-repo $SUBJECT --fresh-parent-output $D/R23_PARENT_DIAGNOSTIC_JOB_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}_${tag}.fresh.json --diagnostic-output $D/R23_PARENT_DIAGNOSTIC_JOB_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}_${tag}.receipt.json
