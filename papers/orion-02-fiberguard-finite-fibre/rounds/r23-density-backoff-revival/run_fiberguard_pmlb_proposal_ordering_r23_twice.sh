#!/usr/bin/env bash
set -euo pipefail

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SUBJECT_REPO=${1:?usage: run_fiberguard_pmlb_proposal_ordering_r23_twice.sh /path/to/pinned-pmlb-repo}
PMLB_COMMIT=7c1f4bdc00136dc2e55c87fa6b8ba6e8af6d1a68
PMLB_TREE=ca5d36e9093c2f7360db57198c8c0586a3217a60

test "$(git -C "$SUBJECT_REPO" rev-parse HEAD)" = "$PMLB_COMMIT"
test "$(git -C "$SUBJECT_REPO" rev-parse 'HEAD^{tree}')" = "$PMLB_TREE"

python3 -m unittest -v \
  "$HERE/test_fiberguard_pmlb_proposal_ordering_r23.py" \
  "$HERE/test_verify_fiberguard_pmlb_proposal_ordering_r23.py"
python3 "$HERE/fiberguard_pmlb_proposal_ordering_r23.py" --self-test

TMP=$(mktemp -d "${TMPDIR:-/tmp}/orion02-r23.XXXXXX")
trap 'rm -rf "$TMP"' EXIT

run_one() {
  local label=$1
  python3 "$HERE/fiberguard_pmlb_proposal_ordering_r23.py" \
    --subject-repo "$SUBJECT_REPO" \
    --output "$TMP/${label}.result.json" \
    --corrected-parent-output "$TMP/${label}.parent.json" \
    --terminal-output "$TMP/${label}.terminal.txt" \
    --timings-output "$TMP/${label}.timings.json" \
    >"$TMP/${label}.stdout.txt" 2>"$TMP/${label}.stderr.txt"
}

run_one "run_a"
run_one "run_b"

cmp -s "$TMP/run_a.result.json" "$TMP/run_b.result.json"
cmp -s "$TMP/run_a.parent.json" "$TMP/run_b.parent.json"
cmp -s "$TMP/run_a.terminal.txt" "$TMP/run_b.terminal.txt"

python3 "$HERE/verify_fiberguard_pmlb_proposal_ordering_r23.py" \
  --result "$TMP/run_a.result.json" \
  --corrected-parent "$TMP/run_a.parent.json" \
  --terminal "$TMP/run_a.terminal.txt" \
  >"$TMP/verification.txt"

cp "$TMP/run_a.result.json" "$HERE/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_RESULTS.json"
cp "$TMP/run_a.parent.json" "$HERE/FIBERGUARD_PMLB_R22_CORRECTED_EXACT_RECEIPT.json"
cp "$TMP/run_a.terminal.txt" "$HERE/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_TERMINAL.txt"
cp "$TMP/run_a.stdout.txt" "$HERE/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_RUN_A.log"
cp "$TMP/run_b.stdout.txt" "$HERE/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_RUN_B.log"

python3 - "$TMP/run_a.timings.json" "$TMP/run_b.timings.json" \
  "$HERE/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_TIMINGS.json" <<'PY'
import json, pathlib, sys
a = json.loads(pathlib.Path(sys.argv[1]).read_text())
b = json.loads(pathlib.Path(sys.argv[2]).read_text())
out = {
    "schema": "ORION.FiberGuard.PMLBProposalOrdering.R23.TwoRunTimings.v1",
    "run_a": a,
    "run_b": b,
}
pathlib.Path(sys.argv[3]).write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n")
PY

{
  echo "R23_TWO_PROCESS_RESULT_BYTES_IDENTICAL"
  echo "R23_TWO_PROCESS_CORRECTED_PARENT_BYTES_IDENTICAL"
  echo "R23_TWO_PROCESS_TERMINAL_BYTES_IDENTICAL"
  cat "$TMP/verification.txt"
  sha256sum \
    "$HERE/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_RESULTS.json" \
    "$HERE/FIBERGUARD_PMLB_R22_CORRECTED_EXACT_RECEIPT.json" \
    "$HERE/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_TERMINAL.txt"
} >"$HERE/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_VERIFICATION.txt"

cat "$HERE/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_TERMINAL.txt"
echo "R23_TWO_RUN_VERIFY_OK"
