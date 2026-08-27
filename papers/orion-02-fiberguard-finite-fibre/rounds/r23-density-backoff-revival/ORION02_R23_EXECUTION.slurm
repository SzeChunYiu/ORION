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
test "$(sha256sum "$D/fiberguard_pmlb_proposal_ordering_r23.py" | cut -d' ' -f1)" = 6bb4e377462249c3630ceacc56073ba385a82805c79eda58809c42b8ee1562aa
test "$(sha256sum "$D/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_PROTOCOL.md" | cut -d' ' -f1)" = 54574ec9fa5364fb0ad8e5857678930dac3b4483f1b7a9da96829d8e6f0c447f
test "$(sha256sum "$D/verify_fiberguard_pmlb_proposal_ordering_r23.py" | cut -d' ' -f1)" = 4c8d57f8398d4575097eba16ac7fcd21e467745ad00cfa31df928358e59c6bed
test "$(sha256sum "$D/run_fiberguard_pmlb_proposal_ordering_r23_twice.sh" | cut -d' ' -f1)" = f47fb411acda6735ca636160defcdd926c98e6ed5f57967051b683d4a4203f04
unexpected=$(git status --porcelain | grep -Ev '^\?\? papers/orion-02-fiberguard-finite-fibre/rounds/r23-density-backoff-revival/ORION02_R23_(EXECUTION\.slurm|JOB_[0-9]+\.(out|err))$' || true)
test -z "$unexpected"

export PYTHONUNBUFFERED=1
bash "$D/run_fiberguard_pmlb_proposal_ordering_r23_twice.sh" "$SUBJECT"
