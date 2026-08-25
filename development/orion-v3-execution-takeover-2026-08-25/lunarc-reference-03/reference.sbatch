#!/bin/bash
#SBATCH -A hep2023-1-3
#SBATCH -p hep
#SBATCH -N 1
#SBATCH -n 2
#SBATCH --mem=8192M
#SBATCH -t 15
#SBATCH -J v3-engineering-reference-03
#SBATCH -o logs/reference-%j.out
#SBATCH -e logs/reference-%j.err
set -euo pipefail
export ORION_SUBMISSION_KEY=624063fe5fe2653d871ae341f5471978a0b507e6d3beb716eb63427cec14b693
bash run_reference.sh
