#!/usr/bin/env bash
#SBATCH -A YOUR_PROJECT_HERE
#SBATCH -p cosmos
#SBATCH -J dav-sweep
#SBATCH -n 1
#SBATCH -c 1
#SBATCH -t 24:00:00
#SBATCH --array=0-727%400
#SBATCH -o logs/sweep_%A_%a.out
#SBATCH -e logs/sweep_%A_%a.err
#
# One shard per array task.  Each task is single-threaded by design: the search is a depth-first
# tree walk with a per-node reachability table, which parallelises across shards far better than
# within one.  Packing many small serial tasks is what the array is for.
#
# SUBMIT VIA ./submit.sh -- it sets RANK/LEN/PRUNE/NSHARD and sizes the array to match.  Editing
# --array here without editing NSHARD silently loses coverage, which is the one failure mode that
# turns "no witness exists" into "we did not look everywhere".  collect.py checks for it.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"

[ -f CALIBRATED.ok ] || { echo "refusing to run: CALIBRATED.ok absent, run 01_calibrate first"; exit 4; }

: "${RANK:?set RANK}" "${LEN:?set LEN}" "${PRUNE:?set PRUNE}" "${NSHARD:?set NSHARD}"
P=3
Q=$(( RANK * (P-1) ))
[ "$PRUNE" -eq $(( LEN - Q - 1 )) ] || { echo "FATAL: PRUNE=$PRUNE must be L-q-1=$(( LEN - Q - 1 ))"; exit 3; }
[ "$SLURM_ARRAY_TASK_COUNT" -eq "$NSHARD" ] || {
    echo "FATAL: array has $SLURM_ARRAY_TASK_COUNT tasks but NSHARD=$NSHARD -- coverage would be partial"; exit 3; }

OUT=results/r${RANK}_L${LEN}
mkdir -p "$OUT" logs
SHARD=$SLURM_ARRAY_TASK_ID
DEST="$OUT/shard_${SHARD}.txt"

# Idempotent: a completed shard is never redone, so a resubmission after a walltime kill only
# picks up the shards that did not finish.
if grep -q '^RESULT' "$DEST" 2>/dev/null; then echo "shard $SHARD already complete"; exit 0; fi

SCRATCH="${SNIC_TMP:-${TMPDIR:-/tmp}}"
TMP="$SCRATCH/shard_${SHARD}.$$"
srun ./bin/enum_sym "$P" "$RANK" "$LEN" "$PRUNE" --shard "$SHARD" "$NSHARD" > "$TMP"
mv "$TMP" "$DEST"          # atomic: a half-written shard never looks complete
grep -c '^packing<=1:' "$DEST" | xargs -I{} echo "shard $SHARD witnesses={}"
grep '^RESULT' "$DEST"
