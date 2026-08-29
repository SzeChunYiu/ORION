#!/usr/bin/env python3
"""Is ORION-04's one-shot authorization machine-verifiable, and is its replay list intact?

`TOP_TIER_ATOMIC_GAP_LEDGER_V2` lists, among ORION-04's `immediate_safe_actions`, "audit
the one-shot authorization schema for machine-verifiable presence and scope". Its
`collision_rule` is stricter than it sounds: *do not spend the one-shot until the
authority record is machine-verifiable*. So this audit gates a resource that can be spent
exactly once.

This audits the existing gate rather than replacing it. `submission_gate.py` already
implements the verification; what was missing is a check that its replay list cannot
silently drift from the record that publishes it.

Two independent lists exist:
  * `CONSUMED_KEYS` inside `submission_gate.py` — what the gate refuses
  * `forbidden_keys` inside `AWAITING_NEW_ONE_SHOT_AUTHORIZATION.json` — what the record
    tells an operator is already spent

Nothing previously compared them. If they diverge, a key the record calls spent could
still pass the gate, or the record could understate what has been consumed. Both are
one-way errors on a one-shot resource.

Exit codes
  0  AUDIT_PASS      schema verifiable and the two replay lists agree
  1  AUDIT_FAIL      a required guard is missing or the lists disagree
  3  CANNOT_CHECK    an input is absent, so nothing is concluded
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

EXIT_PASS, EXIT_FAIL, EXIT_CANNOT_CHECK = 0, 1, 3

BASE = ("papers/orion-04-rooted-completion-certificates/evidence/"
        "crb-full-replay/successor-v1")
GATE = f"{BASE}/engine_b/submission_gate.py"
RECORD = f"{BASE}/AWAITING_NEW_ONE_SHOT_AUTHORIZATION.json"

# Properties the gate must enforce for the authorization to be machine-verifiable.
# Each is a substring of the refusal the gate raises, so the audit tracks the gate's
# own vocabulary rather than a restatement of it.
REQUIRED_GUARDS = {
    "exact_field_set": "authorization fields are not exact",
    "consumed_key_refusal": "authorization reuses a consumed or terminal key",
    "schema_pin": "authorization schema mismatch",
    "one_shot_status": "authorization status is not a one-shot execution request",
    "subject_binding": "authorization subject mismatch",
    "key_derivation": "authorization nonduplication key derivation mismatch",
    "malformed_key": "authorization nonduplication key is malformed",
    "scope_pin": "authorization declared scopes or denominators mismatch",
}


def _repo_root(start: str) -> str:
    d = os.path.abspath(start)
    while d != "/":
        # .git is a directory in a clone and a FILE inside a git worktree.
        if os.path.exists(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return os.path.abspath(start)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", default="")
    args = ap.parse_args()
    root = _repo_root(os.path.dirname(os.path.abspath(__file__)))

    gate_p, rec_p = os.path.join(root, GATE), os.path.join(root, RECORD)
    missing = [p for p in (gate_p, rec_p) if not os.path.isfile(p)]
    if missing:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": "INPUT_ABSENT",
                          "missing": [os.path.relpath(p, root) for p in missing]}))
        return EXIT_CANNOT_CHECK

    gate = open(gate_p, encoding="utf-8").read()
    record = json.load(open(rec_p, encoding="utf-8"))

    guards = {name: (msg in gate) for name, msg in REQUIRED_GUARDS.items()}
    absent = sorted(n for n, ok in guards.items() if not ok)

    m = re.search(r"CONSUMED_KEYS\s*=\s*(?:frozenset\()?\{(.*?)\}", gate, re.S)
    gate_keys = set(re.findall(r'"([0-9a-f]{64})"', m.group(1))) if m else set()
    record_keys = set(record.get("forbidden_keys") or [])

    only_record = sorted(record_keys - gate_keys)
    only_gate = sorted(gate_keys - record_keys)
    lists_agree = gate_keys == record_keys and bool(gate_keys)

    # The record must not claim a live authorization while none is present.
    live_claimed = bool(record.get("live_authorization_file_present"))
    executed = bool(record.get("execution_performed"))
    rounds = ((record.get("science_authority") or {}).get("d4_rounds_consumed"))

    out = {
        "checker": "orion04_authorization_schema_audit_v1",
        "gate": GATE,
        "record": RECORD,
        "guards_present": guards,
        "guards_absent": absent,
        "replay_lists": {
            "gate_consumed_keys": len(gate_keys),
            "record_forbidden_keys": len(record_keys),
            "only_in_record": only_record,
            "only_in_gate": only_gate,
            "agree": lists_agree,
        },
        "record_state": {
            "live_authorization_file_present": live_claimed,
            "execution_performed": executed,
            "d4_rounds_consumed": rounds,
            "terminal": record.get("terminal"),
        },
        "claim_scope": (
            "Audits whether the one-shot authorization is machine-verifiable and whether "
            "the gate's replay list matches the published record. Does not authorize "
            "anything, does not evaluate the D4 claim, and grants no authority."
        ),
        "grants_authority": "NONE",
    }
    ok = not absent and lists_agree
    out["status"] = "AUDIT_PASS" if ok else "AUDIT_FAIL"
    print(json.dumps(out, indent=2))
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(out, fh, indent=2)
            fh.write("\n")
    return EXIT_PASS if ok else EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
