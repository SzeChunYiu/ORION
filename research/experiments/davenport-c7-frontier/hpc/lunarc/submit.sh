#!/usr/bin/env bash
# Submit one sweep with a consistent (rank, length, prune, shard-count) tuple.
#
#   ./submit.sh 6          D_2(C_3^6): is it 20?   728 shards
#   ./submit.sh 7          D_2(C_3^7): is it 22 or 23?   2186 shards
#
# The prune depth and the array size are derived here, never typed twice.
set -euo pipefail
cd "$(dirname "$0")"
RANK=${1:?usage: submit.sh <rank 6|7>}
P=3
case "$RANK" in
  6) LEN=20 ;;   # construction gives D_2 >= 20; a clean sweep at L=20 makes it exactly 20
  7) LEN=22 ;;   # construction gives D_2 >= 22, the closed form predicts 23; L=22 separates them
  *) echo "rank must be 6 or 7"; exit 2 ;;
esac
Q=$(( RANK * (P-1) ))
PRUNE=$(( LEN - Q - 1 ))
NSHARD=$(( P**RANK - 1 ))       # shard on the first free term: one class per nonzero element
LAST=$(( NSHARD - 1 ))
echo "rank=$RANK length=$LEN prune=<=$PRUNE shards=$NSHARD"
sbatch --array=0-${LAST}%400 \
       --export=ALL,RANK=$RANK,LEN=$LEN,PRUNE=$PRUNE,NSHARD=$NSHARD \
       02_sweep.sbatch
