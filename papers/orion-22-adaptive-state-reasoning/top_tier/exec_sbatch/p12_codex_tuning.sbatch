#!/bin/bash
#SBATCH -J p12-codex-tune
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 16:00:00
#SBATCH -N 1
#SBATCH --tasks-per-node=1
#SBATCH -D /projects/hep/fs9/users/scyiu/orion-a2-p12
#SBATCH -o logs/p12-codex-tune-%j.out
# Codex-lane tuning under the AMENDED harness freeze
# (P12_HARNESS_AMENDMENT_DATASET_MOUNTPOINT_V1.json, template P12_TERMINAL_V1M).
# Rerun-from-scratch of the pre-amendment 68 cells (archived; see
# P12_TUNING_EVAL_INSTRUMENT_FINDING_V1.md).
#
# The --echo-check probe is intentionally NOT fatal here: it refreshes BOTH
# lanes' same-day echo records and exits 1 if either fails (the claude lane
# is window-gated until its scheduled job). The lane-scoped gate inside
# --run is the authority: --lane gpt-5.5-codexcli requires only the codex
# same-day echo.
set -x
P12BASE=/projects/hep/fs9/users/scyiu/orion-a2-p12
export PATH=$HOME/.local/bin:$P12BASE/miniconda3/bin:$PATH
module load nodejs/20.9.0
# Same PYTHONPATH hygiene as the other jobs (module-system EasyBuild
# python3.11 site-packages must not leak into any subprocess).
unset PYTHONPATH
export PYTHONNOUSERSITE=1
cd "$P12BASE/worktree/papers/orion-22-adaptive-state-reasoning/top_tier" || exit 20

"$P12BASE/miniconda3/bin/conda" run -n sci-agent --no-capture-output python campaign_tuning_driver_v1.py \
  --echo-check \
  --parquet "$P12BASE/a2-deps/sab_verified.parquet" \
  || echo "ECHO_PROBE_NONFATAL rc=$?"

"$P12BASE/miniconda3/bin/conda" run -n sci-agent --no-capture-output python campaign_tuning_driver_v1.py \
  --run --lane gpt-5.5-codexcli \
  --parquet "$P12BASE/a2-deps/sab_verified.parquet"
RC=$?
echo "P12_CODEX_TUNING_RC=$RC"
echo P12_CODEX_TUNING_DONE
exit $RC
