#!/usr/bin/env bash
#SBATCH --job-name=p1_sab_rr1_preflight_v1
#SBATCH --account=lu2026-2-51
#SBATCH --partition=gpua40i
#SBATCH --gres=gpu:a40:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --signal=B:TERM@120

# Frozen for task 1, arm RR, attempt 1, seed 101. This launcher does not submit
# itself and grants no evaluation, outcome, production, scientific, or merge
# authority. Protected packet bodies and all live outputs remain outside Git.
set -Eeuo pipefail
umask 077
unset HF_TOKEN HUGGING_FACE_HUB_TOKEN OPENAI_API_KEY ANTHROPIC_API_KEY \
  AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN \
  GOOGLE_APPLICATION_CREDENTIALS AZURE_OPENAI_API_KEY GITHUB_TOKEN \
  SSH_AUTH_SOCK || true
HERE=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
exec python3 "$HERE/protected_rr1_direct_route_v1.py" supervise "$@"
