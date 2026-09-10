#!/usr/bin/env bash
# Build both enumerators. Run once, on a compute node or the login node.
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$(cd ../.. && pwd)          # .../research/experiments/davenport-c7-frontier
mkdir -p bin

# LUNARC uses Lmod. Adjust the toolchain to whatever `module avail GCC` offers.
module load GCC/12.3.0 2>/dev/null || echo "note: no module system, using system gcc"

CFLAGS="-O3 -march=native -funroll-loops"

# enum_sym is built from v2, which is the only source implementing --maxnodes/--maxsecs.  It used
# to be built from v1, which lacks them; unknown flags fell through v1's argument chain unnoticed,
# so a documented sampling command like
#     ./bin/enum_sym 3 7 22 7 --shard 17 2186 --maxnodes 5000000
# silently enumerated the FULL shard instead of stopping at the cap.  Both files now reject an
# unrecognised flag outright, so that failure cannot recur quietly.
#
# v2 differs from v1 only in row-major addtab access (a measured no-op -- addtab is symmetric,
# and --colmajor recovers v1's access pattern) plus the two caps.  The search is identical, so
# 01_calibrate.sbatch still gates it.
gcc $CFLAGS -o bin/enum_sym     "$ROOT/tools/enum_rank_sym_v2.c"
gcc $CFLAGS -o bin/enum_sym_v1  "$ROOT/tools/enum_rank_sym_v1.c"   # kept for bisection
gcc $CFLAGS -o bin/enum_ref     "$ROOT/tools/enum_rank_generic_v3.c"
echo "built:"; ls -l bin/

# Fail loudly here rather than in a sampling run that looks capped and is not.
if ! ./bin/enum_sym 3 3 10 3 --maxnodes 100 2>/dev/null | grep -q TRUNCATED; then
    echo "FATAL: bin/enum_sym does not honour --maxnodes; it is the wrong source." >&2; exit 1
fi
if ! ./bin/enum_sym 3 3 10 3 --maxsecs 0.01 2>/dev/null | grep -q RESULT; then
    echo "FATAL: bin/enum_sym does not accept --maxsecs." >&2; exit 1
fi
echo "self-check: --maxnodes and --maxsecs both honoured, and truncation is marked."
