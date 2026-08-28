#!/bin/bash
#SBATCH -A hep2023-1-3
#SBATCH -p hep
#SBATCH --qos=normal
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH -t 00:05:00
#SBATCH -J o6-neg-coverage
#SBATCH -o /projects/hep/fs9/users/scyiu/orion-revival-r1/run-506b84e6c47558764b95f4482ce6691bb3757723-v2/logs/o06-%j.out
#SBATCH -e /projects/hep/fs9/users/scyiu/orion-revival-r1/run-506b84e6c47558764b95f4482ce6691bb3757723-v2/logs/o06-%j.err
set -euo pipefail
unset PYTHONPATH PYTHONHOME
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /projects/hep/fs9/users/scyiu/orion-revival-r1/stage-506b84e6c47558764b95f4482ce6691bb3757723-v2
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 papers/orion-06-recursive-recovery/revival/verify_orion06_negative_coverage.py   --root /projects/hep/fs9/users/scyiu/orion-revival-r1/stage-506b84e6c47558764b95f4482ce6691bb3757723-v2 --output /projects/hep/fs9/users/scyiu/orion-revival-r1/run-506b84e6c47558764b95f4482ce6691bb3757723-v2/o06/ORION06_NEGATIVE_COVERAGE_AUDIT.json
