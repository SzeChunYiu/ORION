#!/bin/bash
# ORION-21 / P11 -- NR07 width-law falsification (lane NR-07-EXT).
#
# PRE-REGISTERED FALSIFICATION CRITERION is in the runner's module docstring and
# is echoed into the result JSON under "prereg_criterion". It is fixed before
# execution. Editing it after seeing outcomes invalidates the run.
#
#   C1 LAW_CONFIRMED_REGIME_EXTENDED  |rel err| <= 0.25 on >= 8/10 cells, monotone
#   C2 LAW_FALSIFIED_FLAT             Spearman(n_cross, ln p) <= 0
#   C3 LAW_FALSIFIED_SCALE            grows, but |rel err| > 0.25 on >= 5/10 cells
#   C4 INDETERMINATE                  anything else / any right-censored cell
#   P0 precondition                   exact replay of NR07 anchors to 1e-12, else CANNOT_CHECK
#
#SBATCH --job-name=o21-nr07-widthlaw
#SBATCH --account=lu2026-2-51
#SBATCH --partition=lu48
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=16:00:00
#SBATCH --output=/projects/hep/fs9/scratch/scyiu-orion-ci/nr07-widthlaw-logs/%x-%j.out
#SBATCH --error=/projects/hep/fs9/scratch/scyiu-orion-ci/nr07-widthlaw-logs/%x-%j.err

set -euo pipefail
BASE=/projects/hep/fs9/scratch/scyiu-orion-ci/ORION
cd "$BASE"
export ORION_SOURCE_COMMIT=$(git rev-parse HEAD)
export PYTHONHASHSEED=0 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
PYTHON="$BASE/.venv/bin/python"
EXP=papers/orion-21-state-as-computation/experiments/nr07-width-law-falsification-v1
OUT=/projects/hep/fs9/scratch/scyiu-orion-ci/nr07-widthlaw-logs/NR07_WIDTH_LAW_FALSIFICATION_RESULT_V1.json

"$PYTHON" "$EXP/run_nr07_width_law_falsification_v1.py" --output "$OUT"
echo "RESULT: $OUT"
sha256sum "$OUT"
