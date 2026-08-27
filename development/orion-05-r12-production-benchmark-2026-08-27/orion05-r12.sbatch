#!/bin/bash
#SBATCH -A hep2023-1-3
#SBATCH -p hep
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH -t 01:00:00
#SBATCH -J orion05-r12
#SBATCH -o logs/orion05-r12-%j.out
#SBATCH -e logs/orion05-r12-%j.err

set -euo pipefail
umask 077
unset PYTHONPATH PYTHONHOME
export PYTHONHASHSEED=0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

: "${ORION05_R12_SOURCE_COMMIT:?missing exact source commit}"
: "${ORION05_R12_RUN_ROOT:?missing unique run root}"

logical_pwd=$(pwd -L)
physical_pwd=$(pwd -P)
[[ "$logical_pwd" == "$ORION05_R12_RUN_ROOT" ]]
[[ "$physical_pwd" == "$ORION05_R12_RUN_ROOT" ]]
[[ "$(cat SOURCE_COMMIT.txt)" == "$ORION05_R12_SOURCE_COMMIT" ]]
[[ ! -e result ]]
mkdir -p logs

python_bin=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
"$python_bin" - <<'PY'
import numpy, sys
assert sys.version_info[:2] == (3, 11), sys.version
assert numpy.__version__ == "2.4.6", numpy.__version__
PY

"$python_bin" papers/orion_05_r12_production_benchmark.py \
  --run \
  --output-dir result \
  --python "$python_bin" \
  --workers "${SLURM_CPUS_PER_TASK}"

sha256sum \
  result/RAW_ATTEMPTS.jsonl \
  result/BENCHMARK_ENVIRONMENT.json \
  result/ORION05_R12_PRODUCTION_BENCHMARK_RESULT.json \
  > result/SHA256SUMS
chmod -R a-w result
