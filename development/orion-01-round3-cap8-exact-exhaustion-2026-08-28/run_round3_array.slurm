#!/bin/bash
#SBATCH --job-name=o01-r3-cap8
#SBATCH --account=hep2023-1-3
#SBATCH --partition=hep
#SBATCH --array=0-7%4
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --time=4-00:00:00
#SBATCH --output=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO01/.codex-run/orion01-r3/slurm-%A_%a.out
#SBATCH --error=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO01/.codex-run/orion01-r3/slurm-%A_%a.err
set -euo pipefail
W=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO01
D=$W/development/orion-01-round3-cap8-exact-exhaustion-2026-08-28
O=$W/.codex-run/orion01-r3
PY=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO01-venv/bin/python
mkdir -p "$O"
"$PY" "$D/run_orion01_round3_cap8.py" --task-index "$SLURM_ARRAY_TASK_ID" --output "$O/task${SLURM_ARRAY_TASK_ID}.run1.json"
"$PY" "$D/run_orion01_round3_cap8.py" --task-index "$SLURM_ARRAY_TASK_ID" --output "$O/task${SLURM_ARRAY_TASK_ID}.run2.json"
cmp "$O/task${SLURM_ARRAY_TASK_ID}.run1.json" "$O/task${SLURM_ARRAY_TASK_ID}.run2.json"
sha256sum "$O/task${SLURM_ARRAY_TASK_ID}.run1.json" "$O/task${SLURM_ARRAY_TASK_ID}.run2.json"
