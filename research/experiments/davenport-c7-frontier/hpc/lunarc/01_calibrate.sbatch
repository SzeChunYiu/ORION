#!/usr/bin/env bash
#SBATCH -A hep2023-1-3
#SBATCH -p hep
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

# ---------------------------------------------------------------------------------------------
# Coverage, not just soundness.  The prune decides what a single walk may skip; the SPLIT decides
# how the walk is divided.  A split that loses a subtree produces a fast, clean, entirely false
# zero -- the same failure mode as an unsound prune, from the other direction.  So verify that
# splitting reproduces the unsharded walk EXACTLY: leaves and witnesses live strictly below the
# split depth, so they must sum to the unsharded totals.  (Node counts must not: every unit
# re-walks the prefix above the split depth, so they are inflated by design.)
partition () {  # p r L s splitdepth nshard
    local P=$1 R=$2 LL=$3 S=$4 D=$5 NS=$6
    local ref rl rf sl=0 sf=0 o
    ref=$("$BIN" "$P" "$R" "$LL" "$S" | grep RESULT)
    rl=$(echo "$ref" | grep -o 'leaves=[0-9]*' | cut -d= -f2)
    rf=$(echo "$ref" | grep -o 'found=[0-9]*'  | cut -d= -f2)
    for ((i=0;i<NS;i++)); do
        o=$("$BIN" "$P" "$R" "$LL" "$S" --splitdepth "$D" --shard "$i" "$NS" | grep RESULT)
        sl=$(( sl + $(echo "$o" | grep -o 'leaves=[0-9]*' | cut -d= -f2) ))
        sf=$(( sf + $(echo "$o" | grep -o 'found=[0-9]*'  | cut -d= -f2) ))
    done
    if [ "$rl" -eq "$sl" ] && [ "$rf" -eq "$sf" ]; then
        echo "PASS $P^$R L=$LL split=$D x$NS: leaves=$sl found=$sf match the unsharded walk"
    else
        echo "FAIL $P^$R L=$LL split=$D x$NS: summed leaves=$sl found=$sf but unsharded gives leaves=$rl found=$rf"
        fail=1
    fi
}

echo
echo "== coverage: splitting the walk must partition it exactly, with nothing lost =="
partition 3 3 10 3 5 200      # witnesses present, and 200 >> the legacy ceiling N-1=26
partition 3 3 11 4 6 150      # clean negative
partition 3 4 14 5 6 250      # clean negative, 250 >> N-1=80

if [ "$fail" -ne 0 ]; then
    echo; echo "CALIBRATION FAILED.  Do not run any sweep.  The orbit prune is unsound, the"
    echo "split loses coverage, or the build is wrong; bisect with --nosym, which recovers the"
    echo "parent search exactly, and with --splitdepth 0, which recovers the undivided walk."
    exit 1
fi
date -u +"calibrated %Y-%m-%dT%H:%M:%SZ" > CALIBRATED.ok
echo; echo "CALIBRATION PASSED.  CALIBRATED.ok written."
