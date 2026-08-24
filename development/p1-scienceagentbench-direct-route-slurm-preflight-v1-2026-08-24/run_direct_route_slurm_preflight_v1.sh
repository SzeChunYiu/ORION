#!/usr/bin/env bash
#SBATCH --job-name=p1_sab_direct_preflight_v1
#SBATCH --account=lu2026-2-51
#SBATCH --partition=gpua40i
#SBATCH --gres=gpu:a40:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00

# One invocation stages, attests, and captures exactly one task/arm/attempt.
# This launcher grants no task, evaluator, outcome, production, or merge authority.
set -Eeuo pipefail
umask 077
HERE=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
exec python3 "$HERE/direct_route_slurm_preflight_v1.py" supervise "$@"
