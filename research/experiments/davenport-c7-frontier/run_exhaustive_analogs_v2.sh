#!/usr/bin/env bash
# Replays the exhaustive enumerations of EXHAUSTIVE_ANALOG_RESULTS_V2.md.
#   --ci   : only the fast frames (p = 3 all k <= 4; p = 5 D2 frames L=19,20)   [~3 min]
#   (none) : also the p = 5 D3 frames (L = 24, 25) — hours.
# Every frame prints "nodes=... leaves=... found=..." on stderr; found = number of symmetry-reduced
# sequences with packing number <= kmax (0 means the frame proves the corresponding upper bound).
set -euo pipefail
cd "$(dirname "$0")"
gcc -O2 -o /tmp/enum_packing_v2 tools/enum_packing_v2.c
E=/tmp/enum_packing_v2
frame () { # name p L cap s kmax expect_found extra...
  local name=$1 p=$2 L=$3 cap=$4 s=$5 kmax=$6 expect=$7; shift 7
  local out; out=$($E $p $L $cap $s $kmax "$@" 2>&1 >/dev/null | tail -1)
  local found; found=$(sed -n 's/.*found=\([0-9]*\).*/\1/p' <<<"$out")
  echo "$name: $out"
  if [ "$expect" != "-" ] && [ "$found" != "$expect" ]; then echo "MISMATCH: expected found=$expect"; exit 1; fi
}
# p = 3: D_2 = 11, D_3 = 14, D_4 = 17 (frames: length D_k - 1 witnesses / length D_k none)
frame "C_3^3 L=10 pk<=1 (D2 witnesses)"        3 10 2 3 1 529
frame "C_3^3 L=11 pk<=1 (D2 upper bound)"      3 11 2 4 1 0
frame "C_3^3 L=13 pk<=2 (D3 witnesses)"        3 13 2 2 2 7317
frame "C_3^3 L=14 pk<=2 (D3 upper bound)"      3 14 2 3 2 0
frame "C_3^3 L=16 pk<=3 (D4 witnesses)"        3 16 2 2 3 8921
frame "C_3^3 L=17 pk<=3 (D4 upper bound)"      3 17 2 3 3 0
# p = 5: D_2 = 20
frame "C_5^3 L=19 pk<=1 (D2 witnesses)"        5 19 4 6 1 7847 --planecap 14
frame "C_5^3 L=20 pk<=1 (D2 upper bound)"      5 20 4 7 1 0    --planecap 14
if [ "${1:-}" != "--ci" ]; then
  frame "C_5^3 L=25 pk<=2 (D3 upper bound)"    5 25 4 5 2 -    --planecap 18 --progress
  frame "C_5^3 L=24 pk<=2 (D3 witnesses)"      5 24 4 4 2 -    --planecap 18 --progress
fi
echo "PASS: exhaustive analogue frames replayed"
