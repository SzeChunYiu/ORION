#!/usr/bin/env bash
#SBATCH --job-name=o02-r24-armfib
#SBATCH --partition=lu48
#SBATCH --account=lu2026-2-51
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --output=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO02R24/papers/orion-02-fiberguard-finite-fibre/rounds/r24-arm-conditional-fibres-revival/ORION02_R24_JOB_%j.out
#SBATCH --error=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO02R24/papers/orion-02-fiberguard-finite-fibre/rounds/r24-arm-conditional-fibres-revival/ORION02_R24_JOB_%j.err
set -euo pipefail

: "${EXPECTED_SOURCE_COMMIT:?submit with --export=ALL,EXPECTED_SOURCE_COMMIT=<frozen-commit>}"
W=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO02R24
D=$W/papers/orion-02-fiberguard-finite-fibre/rounds/r24-arm-conditional-fibres-revival
SUBJECT=/projects/hep/fs9/scratch/scyiu-orion-ci/pmlb-src
PYTHON=/projects/hep/fs9/scratch/scyiu-orion-ci/ORION/.venv/bin/python
cd "$W"

test "$(git rev-parse HEAD)" = "$EXPECTED_SOURCE_COMMIT"
unexpected=$(git status --porcelain | grep -Ev "^\?\? papers/orion-02-fiberguard-finite-fibre/rounds/r24-arm-conditional-fibres-revival/ORION02_R24_JOB_${SLURM_JOB_ID}\.(out|err)$" || true)
test -z "$unexpected"
test "$(git -C "$SUBJECT" rev-parse HEAD)" = 7c1f4bdc00136dc2e55c87fa6b8ba6e8af6d1a68
test "$(git -C "$SUBJECT" rev-parse 'HEAD^{tree}')" = ca5d36e9093c2f7360db57198c8c0586a3217a60

export PYTHONUNBUFFERED=1
export PYTHONHASHSEED=0
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHON

bash "$D/run_fiberguard_pmlb_arm_conditional_r24_twice.sh" "$SUBJECT"
