#!/usr/bin/env bash
#SBATCH -A hep2023-1-3
#SBATCH -p hep
#SBATCH -J dav-sweep
#SBATCH -n 1
#SBATCH -c 1
#SBATCH -t 24:00:00
#SBATCH --array=0-727%400
#SBATCH -o logs/sweep_%A_%a.out
#SBATCH -e logs/sweep_%A_%a.err
#
# One or more work units per array task.  Each task is single-threaded by design: the search is a
# depth-first tree walk with a per-node reachability table, which parallelises across units far
# better than within one.  Packing many small serial units is what the array is for.
#
# SUBMIT VIA ./submit.sh -- it sets RANK/LEN/PRUNE/NSHARD/NTASK/SPLIT, sizes the array to NTASK
# and overrides the walltime above.  The -t and --array directives here are only defaults for a
# bare sbatch; submit.sh replaces both.  Editing them without editing NSHARD silently loses
# coverage, which is the one failure mode that turns "no witness exists" into "we did not look
# everywhere".  collect.py checks for it.
#
# NSHARD is the number of work units and is what coverage is proved against.  NTASK is how many
# array tasks share them out; a task handles every unit congruent to its index mod NTASK.  The two
# are decoupled so NSHARD can exceed the cluster's MaxArraySize.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"

[ -f CALIBRATED.ok ] || { echo "refusing to run: CALIBRATED.ok absent, run 01_calibrate first"; exit 4; }

: "${RANK:?set RANK}" "${LEN:?set LEN}" "${PRUNE:?set PRUNE}" "${NSHARD:?set NSHARD}"
NTASK="${NTASK:-$NSHARD}"
SPLIT="${SPLIT:-0}"
P=3
Q=$(( RANK * (P-1) ))
[ "$PRUNE" -eq $(( LEN - Q - 1 )) ] || { echo "FATAL: PRUNE=$PRUNE must be L-q-1=$(( LEN - Q - 1 ))"; exit 3; }
[ "$SLURM_ARRAY_TASK_COUNT" -eq "$NTASK" ] || {
    echo "FATAL: array has $SLURM_ARRAY_TASK_COUNT tasks but NTASK=$NTASK -- coverage would be partial"; exit 3; }
[ "$NSHARD" -ge "$NTASK" ] || { echo "FATAL: NSHARD=$NSHARD must be >= NTASK=$NTASK"; exit 3; }
# Legacy sharding cannot exceed N-1 units; the enumerator also refuses, this is the early check.
if [ "$SPLIT" -eq 0 ]; then
    N=$(( P ** RANK ))
    [ "$NSHARD" -le $(( N - 1 )) ] || {
        echo "FATAL: NSHARD=$NSHARD exceeds the legacy ceiling of N-1=$(( N - 1 )); set SPLIT>RANK"; exit 3; }
fi

OUT=results/r${RANK}_L${LEN}
mkdir -p "$OUT" logs
SCRATCH="${SNIC_TMP:-${TMPDIR:-/tmp}}"
SPLITARG=()
[ "$SPLIT" -gt 0 ] && SPLITARG=(--splitdepth "$SPLIT")

for (( SHARD=SLURM_ARRAY_TASK_ID; SHARD<NSHARD; SHARD+=NTASK )); do
    DEST="$OUT/shard_${SHARD}.txt"
    # Idempotent: a completed unit is never redone, so a resubmission after a walltime kill only
    # picks up the units that did not finish.
    if grep -q '^RESULT' "$DEST" 2>/dev/null; then echo "unit $SHARD already complete"; continue; fi
    TMP="$SCRATCH/shard_${SHARD}.$$"
    srun ./bin/enum_sym "$P" "$RANK" "$LEN" "$PRUNE" \
         --shard "$SHARD" "$NSHARD" "${SPLITARG[@]}" > "$TMP"
    mv "$TMP" "$DEST"          # atomic: a half-written unit never looks complete
    # grep exits 1 on zero matches, which is the EXPECTED outcome for a sweep that proves a
    # negative -- under `set -e` that made every empty unit's task exit nonzero and look failed.
    NW=$(grep -c '^packing<=1:' "$DEST" || true)
    echo "unit $SHARD witnesses=${NW:-0}"
    grep '^RESULT' "$DEST" || true
done
