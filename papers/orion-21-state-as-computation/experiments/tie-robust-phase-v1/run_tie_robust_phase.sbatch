#!/bin/bash
# ORION-21 / TIE_ROBUST_PHASE v1 — registered LUNARC scientific execution.
# This batch entry point does not alter the frozen protocol. It emits the raw
# transcript directory, RESULT.json, and an independent checker report.
#SBATCH --job-name=o21-tie-robust
#SBATCH --account=lu2026-2-51
#SBATCH --partition=lu48
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=16:00:00
#SBATCH --output=/projects/hep/fs9/scratch/scyiu-orion-ci/tie-robust-logs/%x-%j.out
#SBATCH --error=/projects/hep/fs9/scratch/scyiu-orion-ci/tie-robust-logs/%x-%j.err

set -uo pipefail
BASE=/projects/hep/fs9/scratch/scyiu-orion-ci/ORION
cd "$BASE"
export ORION_SOURCE_COMMIT=$(git rev-parse HEAD)
export PYTHONHASHSEED=0 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
PYTHON="$BASE/.venv/bin/python"
EXP=papers/orion-21-state-as-computation/experiments/tie-robust-phase-v1
RUN_ROOT=/projects/hep/fs9/scratch/scyiu-orion-ci/tie-robust-logs/run-${SLURM_JOB_ID}
mkdir -p "$RUN_ROOT"

"$PYTHON" "$EXP/run_tie_robust_phase.py" --output-dir "$RUN_ROOT"
RUN_RC=$?

"$PYTHON" "$EXP/independent_checker/check_tie_robust_phase.py" \
  "$RUN_ROOT/RESULT.json" \
  --protocol "$EXP/PROTOCOL.json" \
  --expected "$EXP/EXPECTED_TERMINALS.json" \
  > "$RUN_ROOT/CHECKER_REPORT.json"
CHECK_RC=$?

sha256sum "$RUN_ROOT/RESULT.json" "$RUN_ROOT/CHECKER_REPORT.json" | tee "$RUN_ROOT/SHA256SUMS"
tar -C "$RUN_ROOT" -czf "$RUN_ROOT/transcript.tar.gz" transcript
sha256sum "$RUN_ROOT/transcript.tar.gz" >> "$RUN_ROOT/SHA256SUMS"

echo "SOURCE_COMMIT: $ORION_SOURCE_COMMIT"
echo "RUN_ROOT: $RUN_ROOT"
echo "RUN_RC: $RUN_RC"
echo "CHECK_RC: $CHECK_RC"
cat "$RUN_ROOT/CHECKER_REPORT.json"

# Distinguish checked-green, scientific CANNOT_CHECK, and checker disagreement.
if [[ "$RUN_RC" -eq 3 || "$CHECK_RC" -eq 3 ]]; then
  exit 3
fi
if [[ "$RUN_RC" -ne 0 || "$CHECK_RC" -ne 0 ]]; then
  exit 2
fi
exit 0
