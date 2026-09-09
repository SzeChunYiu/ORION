#!/usr/bin/env bash
# Build both enumerators. Run once, on a compute node or the login node.
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$(cd ../.. && pwd)          # .../research/experiments/davenport-c7-frontier
mkdir -p bin

# LUNARC uses Lmod. Adjust the toolchain to whatever `module avail GCC` offers.
module load GCC/12.3.0 2>/dev/null || echo "note: no module system, using system gcc"

CFLAGS="-O3 -march=native -funroll-loops"
gcc $CFLAGS -o bin/enum_sym  "$ROOT/tools/enum_rank_sym_v1.c"
gcc $CFLAGS -o bin/enum_ref  "$ROOT/tools/enum_rank_generic_v3.c"
echo "built:"; ls -l bin/
