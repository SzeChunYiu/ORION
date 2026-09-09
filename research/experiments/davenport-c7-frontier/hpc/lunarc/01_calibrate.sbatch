#!/usr/bin/env bash
#SBATCH -A YOUR_PROJECT_HERE
#SBATCH -p cosmos
#SBATCH -J dav-calib
#SBATCH -n 1
#SBATCH -c 1
#SBATCH -t 04:00:00
#SBATCH -o logs/calib.out
#SBATCH -e logs/calib.err
#
# THE GATE.  A search that returns zero proves nothing unless it can return non-zero, and a
# symmetry-reduced search that is unsound returns zero for the wrong reason.  This job re-decides
# every D_2(C_3^r) value we already know, from BOTH sides, with the orbit prune ON.  Nothing else
# in this directory may run until it writes CALIBRATED.ok.
#
# The prune depth is forced: with q = r(p-1), the complement lemma puts every block of a
# packing-<=1 sequence of length L at >= L - q, so the search may exclude zero-sums of length
# <= L-q-1 and no more.  Getting s wrong silently changes the problem.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
mkdir -p logs
BIN=./bin/enum_sym
fail=0

check () {  # p r L s expectation
    local p=$1 r=$2 L=$3 s=$4 exp=$5
    local q=$(( r * (p-1) ))
    if [ "$s" -ne $(( L - q - 1 )) ]; then
        echo "FATAL: s=$s is not L-q-1=$(( L - q - 1 )) for p=$p r=$r L=$L"; exit 3
    fi
    local out found
    out=$("$BIN" "$p" "$r" "$L" "$s" | grep RESULT)
    found=$(echo "$out" | grep -o 'found=[0-9]*' | cut -d= -f2)
    case "$exp" in
        witness) [ "$found" -gt 0 ] && echo "PASS $p^$r L=$L: found=$found (witness expected)" \
                                    || { echo "FAIL $p^$r L=$L: found=0 but a witness must exist"; fail=1; } ;;
        none)    [ "$found" -eq 0 ] && echo "PASS $p^$r L=$L: found=0 (none can exist)" \
                                    || { echo "FAIL $p^$r L=$L: found=$found but none can exist"; fail=1; } ;;
    esac
}

echo "== calibration: the orbit prune must reproduce every known value, both directions =="
check 3 3 10 3 witness      # D_2(C_3^3) = 11: length 10 witnesses exist
check 3 3 11 4 none         # ... and length 11 has none
check 3 4 13 4 witness      # D_2(C_3^4) = 14
check 3 4 14 5 none
check 3 5 16 5 witness      # D_2(C_3^5) = 17
check 3 5 17 6 none

if [ "$fail" -ne 0 ]; then
    echo; echo "CALIBRATION FAILED.  Do not run any sweep.  The orbit prune is unsound or the"
    echo "build is wrong; bisect with --nosym, which recovers the parent search exactly."
    exit 1
fi
date -u +"calibrated %Y-%m-%dT%H:%M:%SZ" > CALIBRATED.ok
echo; echo "CALIBRATION PASSED.  CALIBRATED.ok written."
