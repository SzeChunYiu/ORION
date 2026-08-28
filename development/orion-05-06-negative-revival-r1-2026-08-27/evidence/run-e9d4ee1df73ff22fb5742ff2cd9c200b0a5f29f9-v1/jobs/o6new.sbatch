#!/bin/bash
#SBATCH -A hep2023-1-3
#SBATCH -p hep
#SBATCH --qos=normal
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH -t 01:00:00
#SBATCH -J o6-revival-new
#SBATCH -o /projects/hep/fs9/users/scyiu/orion-revival-r1/run-e9d4ee1df73ff22fb5742ff2cd9c200b0a5f29f9-v1/logs/o6new-%j.out
#SBATCH -e /projects/hep/fs9/users/scyiu/orion-revival-r1/run-e9d4ee1df73ff22fb5742ff2cd9c200b0a5f29f9-v1/logs/o6new-%j.err
set -euo pipefail
unset PYTHONPATH PYTHONHOME
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export ORION06_REVIVAL_SOURCE_COMMIT=e9d4ee1df73ff22fb5742ff2cd9c200b0a5f29f9
cd /projects/hep/fs9/users/scyiu/orion-revival-r1/stage-e9d4ee1df73ff22fb5742ff2cd9c200b0a5f29f9-v1
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 papers/orion-06-recursive-recovery/revival/orion06_negative_revival_r1.py \
  --run-new-resources \
  --output /projects/hep/fs9/users/scyiu/orion-revival-r1/run-e9d4ee1df73ff22fb5742ff2cd9c200b0a5f29f9-v1/results/ORION06_NEW_RESOURCE_REVIVAL.json
