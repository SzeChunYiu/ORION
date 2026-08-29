#!/bin/bash
#SBATCH -A hep2023-1-3
#SBATCH -p hep
#SBATCH -N 1
#SBATCH -n 2
#SBATCH --mem=16G
#SBATCH -t 240
#SBATCH -J q1-xover
#SBATCH -o logs/q1xover-%j.out
#SBATCH -e logs/q1xover-%j.err
set -euo pipefail
unset PYTHONPATH PYTHONHOME
export PATH="$HOME/.local/bin:$PATH"
bash run_q1_xover.sh
