#!/bin/bash
#SBATCH --job-name=o11-r4-faithful
#SBATCH --account=lu2026-2-51
#SBATCH --partition=lu48
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=/projects/hep/fs9/scratch/scyiu-orion-ci/r4-logs/%x-%j.out
#SBATCH --error=/projects/hep/fs9/scratch/scyiu-orion-ci/r4-logs/%x-%j.err
set -euo pipefail

BASE=/projects/hep/fs9/scratch/scyiu-orion-ci
WT=$BASE/wtR4
EXP=$WT/papers/orion-11-recursive-epistemic-reconstruction/experiments/r4-faithful-comparator-v1
CONF=$WT/research/revival/p1/confirmatory/v2.2

cd "$WT"
export ORION11_R4_SOURCE_COMMIT=$(git rev-parse HEAD)
export PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1

PY=$BASE/ORION/.venv/bin/python

# Primary frozen world set.
"$PY" "$EXP/run_orion11_r4_faithful_comparator.py" \
  --world-dir "$CONF/primary" \
  --execution-freeze "$CONF/PRIMARY_EXECUTION_FREEZE_V3.json" \
  --work-dir "/local/slurmtmp.$SLURM_JOB_ID/o11r4-primary" \
  --outdir "$EXP/result/primary"

# Replication frozen world set -- same arms, independent worlds.
"$PY" "$EXP/run_orion11_r4_faithful_comparator.py" \
  --world-dir "$CONF/replication" \
  --execution-freeze "$CONF/replication/REPLICATION_EXECUTION_FREEZE.json" \
  --work-dir "/local/slurmtmp.$SLURM_JOB_ID/o11r4-replication" \
  --outdir "$EXP/result/replication" || echo "REPLICATION_ARM_NOT_RUN (freeze/world mismatch) -- primary stands alone"

cd "$EXP/result" && sha256sum primary/*.json replication/*.json > SHA256SUMS 2>/dev/null || sha256sum primary/*.json > SHA256SUMS
echo "R4 DONE commit=$ORION11_R4_SOURCE_COMMIT"
