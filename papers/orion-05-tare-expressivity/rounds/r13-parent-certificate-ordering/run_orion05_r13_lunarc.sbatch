#!/bin/bash
#SBATCH --job-name=o05-r13-r1
#SBATCH --account=lu2026-2-51
#SBATCH --partition=lu48
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=03:00:00
#SBATCH --output=/projects/hep/fs9/scratch/scyiu-orion-ci/r1-revival-logs/%x-%j.out
#SBATCH --error=/projects/hep/fs9/scratch/scyiu-orion-ci/r1-revival-logs/%x-%j.err
set -euo pipefail
cd /projects/hep/fs9/scratch/scyiu-orion-ci/wtR1
export ORION05_R13_SOURCE_COMMIT=$(git rev-parse HEAD)
export PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
PYTHON=/projects/hep/fs9/scratch/scyiu-orion-ci/ORION/.venv/bin/python
$PYTHON papers/orion-05-tare-expressivity/orion05_r13_parent_certificate_ordering.py --run --python $PYTHON --output-dir papers/orion-05-tare-expressivity/rounds/r13-parent-certificate-ordering/result
