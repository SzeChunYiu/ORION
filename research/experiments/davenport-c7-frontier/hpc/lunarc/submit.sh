#!/usr/bin/env bash
# Submit one sweep with a consistent (rank, length, prune, split depth, shard-count) tuple.
#
#   ./submit.sh 6          D_2(C_3^6): is it 20?          728 work units, one per array task
#   ./submit.sh 7          D_2(C_3^7): is it 22 or 23?  5000 work units over 1000 array tasks
#
# Everything below is derived from the rank, never typed twice.
#
# WHY RANK 7 IS SPLIT DIFFERENTLY.  Legacy sharding splits on the first free term, so it admits at
# most N-1 = 3^r - 1 non-empty units -- 2186 at rank 7, and that is a hard ceiling, not a default.
# Worse, those units are wildly unbalanced: measured at rank 7, shards 4, 5, 13, 17 and 40 each
# exceed 300 s with no bound established, while 137, 733, 1500 and 2185 finish in under a second.
# A unit that cannot finish inside one job never finishes at all, because resubmission only skips
# units that already wrote a RESULT line.
#
# So rank 7 splits at depth 10 instead, where there are 662,129 subtrees to hand out (measured),
# and deals them round-robin across 5000 units.  Each unit then holds ~1/5000 of the total work
# drawn from all over the tree rather than one monolithic subtree.  The cost is that every unit
# re-walks the tree above depth 10 first, which is ~55 s -- about 76 core-hours in total, a few
# percent of the sweep, and the reason depth 11 is not used (that walk alone exceeds two minutes).
set -euo pipefail
cd "$(dirname "$0")"
RANK=${1:?usage: submit.sh <rank 6|7>}
P=3
case "$RANK" in
  6) LEN=20; SPLIT=0;  NSHARD=$(( P**RANK - 1 )); NTASK=$NSHARD; TLIMIT=24:00:00   ;;
  7) LEN=22; SPLIT=10; NSHARD=5000;               NTASK=1000;    TLIMIT=4-00:00:00 ;;
  *) echo "rank must be 6 or 7"; exit 2 ;;
esac
Q=$(( RANK * (P-1) ))
PRUNE=$(( LEN - Q - 1 ))
LAST=$(( NTASK - 1 ))
PER=$(( (NSHARD + NTASK - 1) / NTASK ))
echo "rank=$RANK length=$LEN prune=<=$PRUNE splitdepth=$SPLIT units=$NSHARD tasks=$NTASK (~$PER per task) walltime=$TLIMIT"
sbatch --array=0-${LAST}%400 \
       --time="$TLIMIT" \
       --export=ALL,RANK=$RANK,LEN=$LEN,PRUNE=$PRUNE,NSHARD=$NSHARD,NTASK=$NTASK,SPLIT=$SPLIT \
       02_sweep.sbatch
