#!/usr/bin/env bash
#SBATCH --job-name=o02-r23-k2
#SBATCH --partition=lu48
#SBATCH --account=lu2026-2-51
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --output=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO02/papers/orion-02-fiberguard-finite-fibre/rounds/r23-density-backoff-revival/ORION02_R23_JOB_%j.out
#SBATCH --error=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO02/papers/orion-02-fiberguard-finite-fibre/rounds/r23-density-backoff-revival/ORION02_R23_JOB_%j.err
set -euo pipefail

W=/projects/hep/fs9/scratch/scyiu-orion-ci/wtO02
D=$W/papers/orion-02-fiberguard-finite-fibre/rounds/r23-density-backoff-revival
SUBJECT=/projects/hep/fs9/scratch/scyiu-orion-ci/pmlb-src
cd "$W"

test "$(git branch --show-current)" = claude/science-orion02-20260827
test "$(git rev-parse HEAD)" = d15a1de9d25ab751613eee8b2a1fe296732118b3
unexpected=$(git status --porcelain | grep -Ev '^\?\? papers/orion-02-fiberguard-finite-fibre/rounds/r23-density-backoff-revival/ORION02_R23_(EXECUTION\.slurm|JOB_[0-9]+\.(out|err))$' || true)
test -z "$unexpected"

export PYTHONUNBUFFERED=1
bash "$D/run_fiberguard_pmlb_proposal_ordering_r23_twice.sh" "$SUBJECT"
