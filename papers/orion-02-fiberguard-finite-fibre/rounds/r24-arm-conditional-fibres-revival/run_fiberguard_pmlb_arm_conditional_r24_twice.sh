#!/usr/bin/env bash
set -euo pipefail

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SUBJECT_REPO=${1:?usage: run_fiberguard_pmlb_arm_conditional_r24_twice.sh /path/to/pinned-pmlb-repo}
PYTHON=${PYTHON:-python3}
PMLB_COMMIT=7c1f4bdc00136dc2e55c87fa6b8ba6e8af6d1a68
PMLB_TREE=ca5d36e9093c2f7360db57198c8c0586a3217a60

test "$(git -C "$SUBJECT_REPO" rev-parse HEAD)" = "$PMLB_COMMIT"
test "$(git -C "$SUBJECT_REPO" rev-parse 'HEAD^{tree}')" = "$PMLB_TREE"

"$PYTHON" -m unittest -v \
  "$HERE/test_fiberguard_pmlb_arm_conditional_r24.py" \
  "$HERE/test_verify_fiberguard_pmlb_arm_conditional_r24.py"
"$PYTHON" "$HERE/fiberguard_pmlb_arm_conditional_r24.py" --self-test

TMP=$(mktemp -d "${TMPDIR:-/tmp}/orion02-r24.XXXXXX")
FAILED_EXECUTION_DIR="$HERE/failed-executions/${SLURM_JOB_ID:-manual-$$}"

preserve_failure_artifacts() {
  local rc=$?
  trap - EXIT
  if [ "$rc" -eq 0 ]; then
    rm -rf "$TMP"
  else
    mkdir -p "$FAILED_EXECUTION_DIR"
    cp -a "$TMP"/. "$FAILED_EXECUTION_DIR"/
    printf '%s\n' "$rc" >"$FAILED_EXECUTION_DIR/WRAPPER_EXIT_CODE.txt"
    echo "R24_WRAPPER_FAILURE_ARTIFACTS $FAILED_EXECUTION_DIR" >&2
  fi
  exit "$rc"
}
trap preserve_failure_artifacts EXIT

run_one() {
  local label=$1
  "$PYTHON" "$HERE/fiberguard_pmlb_arm_conditional_r24.py" \
    --subject-repo "$SUBJECT_REPO" \
    --output "$TMP/${label}.result.json" \
    --r23-parent-output "$TMP/${label}.parent.json" \
    --terminal-output "$TMP/${label}.terminal.txt" \
    --timings-output "$TMP/${label}.timings.json" \
    >"$TMP/${label}.stdout.txt" 2>"$TMP/${label}.stderr.txt"
}

verify_one() {
  local label=$1
  "$PYTHON" "$HERE/verify_fiberguard_pmlb_arm_conditional_r24.py" \
    --result "$TMP/${label}.result.json" \
    --r23-parent "$TMP/${label}.parent.json" \
    --terminal "$TMP/${label}.terminal.txt" \
    >"$TMP/${label}.verification.txt"
}

echo RUN_A >"$TMP/STAGE.txt"
run_one "run_a"
echo RUN_B >"$TMP/STAGE.txt"
run_one "run_b"

echo BYTE_COMPARE >"$TMP/STAGE.txt"
cmp -s "$TMP/run_a.result.json" "$TMP/run_b.result.json"
cmp -s "$TMP/run_a.parent.json" "$TMP/run_b.parent.json"
cmp -s "$TMP/run_a.terminal.txt" "$TMP/run_b.terminal.txt"

echo INDEPENDENT_VERIFY_A >"$TMP/STAGE.txt"
verify_one "run_a"
echo INDEPENDENT_VERIFY_B >"$TMP/STAGE.txt"
verify_one "run_b"

echo MATERIALIZE >"$TMP/STAGE.txt"
cp "$TMP/run_a.result.json" "$HERE/FIBERGUARD_PMLB_ARM_CONDITIONAL_R24_RESULTS.json"
cp "$TMP/run_a.parent.json" "$HERE/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_PARENT.json"
cp "$TMP/run_a.terminal.txt" "$HERE/FIBERGUARD_PMLB_ARM_CONDITIONAL_R24_TERMINAL.txt"
cp "$TMP/run_a.stdout.txt" "$HERE/FIBERGUARD_PMLB_ARM_CONDITIONAL_R24_RUN_A.log"
cp "$TMP/run_b.stdout.txt" "$HERE/FIBERGUARD_PMLB_ARM_CONDITIONAL_R24_RUN_B.log"

"$PYTHON" - "$TMP/run_a.timings.json" "$TMP/run_b.timings.json" \
  "$HERE/FIBERGUARD_PMLB_ARM_CONDITIONAL_R24_TIMINGS.json" <<'PY'
import json, pathlib, sys
a = json.loads(pathlib.Path(sys.argv[1]).read_text())
b = json.loads(pathlib.Path(sys.argv[2]).read_text())
out = {
    "schema": "ORION.FiberGuard.PMLBArmConditionalBoundaryFibres.R24.TwoRunTimings.v1",
    "run_a": a,
    "run_b": b,
}
pathlib.Path(sys.argv[3]).write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n")
PY

{
  echo R24_TWO_PROCESS_RESULT_BYTES_IDENTICAL
  echo R24_TWO_PROCESS_R23_PARENT_BYTES_IDENTICAL
  echo R24_TWO_PROCESS_TERMINAL_BYTES_IDENTICAL
  echo R24_RUN_A_INDEPENDENT_VERIFIER
  cat "$TMP/run_a.verification.txt"
  echo R24_RUN_B_INDEPENDENT_VERIFIER
  cat "$TMP/run_b.verification.txt"
  sha256sum \
    "$HERE/FIBERGUARD_PMLB_ARM_CONDITIONAL_R24_RESULTS.json" \
    "$HERE/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_PARENT.json" \
    "$HERE/FIBERGUARD_PMLB_ARM_CONDITIONAL_R24_TERMINAL.txt"
} >"$HERE/FIBERGUARD_PMLB_ARM_CONDITIONAL_R24_VERIFICATION.txt"

cat "$HERE/FIBERGUARD_PMLB_ARM_CONDITIONAL_R24_TERMINAL.txt"
echo R24_TWO_RUN_VERIFY_OK
