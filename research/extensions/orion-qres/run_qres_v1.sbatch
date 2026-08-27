#!/bin/bash
#SBATCH -A hep2023-1-3
#SBATCH -p hep
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --mem=8192M
#SBATCH -t 15
#SBATCH -J qres-v1-resource
#SBATCH -o logs/qres-%j.out
#SBATCH -e logs/qres-%j.err
set -euo pipefail
unset PYTHONPATH PYTHONHOME || true
export PATH="${HOME}/.local/bin:${PATH}"
export UV_CACHE_DIR=/projects/hep/fs9/users/scyiu/.uv-cache-takeover
bash run_qres_v1.sh
