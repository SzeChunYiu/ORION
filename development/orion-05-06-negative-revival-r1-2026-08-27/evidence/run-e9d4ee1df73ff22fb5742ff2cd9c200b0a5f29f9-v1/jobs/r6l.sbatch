#!/bin/bash
#SBATCH -A hep2023-1-3
#SBATCH -p hep
#SBATCH --qos=normal
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH -t 00:30:00
#SBATCH -J o6-r6l-replay
#SBATCH -o /projects/hep/fs9/users/scyiu/orion-revival-r1/run-e9d4ee1df73ff22fb5742ff2cd9c200b0a5f29f9-v1/logs/r6l-%j.out
#SBATCH -e /projects/hep/fs9/users/scyiu/orion-revival-r1/run-e9d4ee1df73ff22fb5742ff2cd9c200b0a5f29f9-v1/logs/r6l-%j.err
set -euo pipefail
unset PYTHONPATH PYTHONHOME
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cd /projects/hep/fs9/users/scyiu/orion-revival-r1/stage-e9d4ee1df73ff22fb5742ff2cd9c200b0a5f29f9-v1
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 research/extensions/orion-q/max_r6l_three_tare2_shared_factor_donor.py \
  --results-json /projects/hep/fs9/users/scyiu/orion-revival-r1/run-e9d4ee1df73ff22fb5742ff2cd9c200b0a5f29f9-v1/results/R6L_FRESH_RESULTS.json
