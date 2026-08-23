#!/usr/bin/env python3
"""Check a returned clean-room replay receipt against the P6 V3 contract.

The P6 external blocker asks for a custodian who is not the candidate to replay
the frozen bundle and return a signed receipt. A receipt is only worth anything
if a returned one can be rejected, so this is written as a rejector first:

* a custodian who is the candidate, or who reused the candidate's execution
  unit, fails -- that is the whole point of the blocker;
* a receipt missing any contracted step fails, and silence is never a pass;
* any output digest that does not match the frozen contract fails;
* a receipt this tool cannot read exits 3, never 0.

Usage: verify_clean_room_receipt_v1.py CONTRACT.json PACKET.json RECEIPT.json
Exit codes: 0 accepted, 2 rejected, 3 CANNOT_CHECK.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CANDIDATE_IDENTITIES = {
    "orion",
    "orion-programme",
    "szechunyiu",
    "billy10384@gmail.com",
}


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: verify_clean_room_receipt_v1.py CONTRACT.json PACKET.json RECEIPT.json")
        return 3
    try:
        contract = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        packet = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        receipt = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "error": str(exc)}))
        return 3

    rejections: list[str] = []

    custodian = str(receipt.get("custodian_identity", "")).strip()
    if not custodian:
        rejections.append("NO_CUSTODIAN_IDENTITY")
    elif custodian.lower() in CANDIDATE_IDENTITIES:
        rejections.append(f"CUSTODIAN_IS_THE_CANDIDATE:{custodian}")
    if receipt.get("reused_candidate_execution_unit") is not False:
        rejections.append("EXECUTION_UNIT_REUSE_NOT_DENIED")
    if not receipt.get("signature"):
        rejections.append("UNSIGNED")
    if receipt.get("replayed_commit") != packet.get("pinned_commit"):
        rejections.append(
            f"WRONG_COMMIT:{receipt.get('replayed_commit')}!={packet.get('pinned_commit')}"
        )

    contracted = [step["command"] for step in packet["steps"]]
    reported = {step.get("command"): step for step in receipt.get("steps", [])}
    for command in contracted:
        step = reported.get(command)
        if step is None:
            rejections.append(f"STEP_NOT_REPORTED:{command}")
        elif step.get("exit_code") != 0:
            rejections.append(f"STEP_FAILED:{command}:exit={step.get('exit_code')}")

    expected = {
        item["path"]: item["sha256"]
        for item in contract["raw_inputs"] + contract["raw_outputs"]
    }
    observed = {item.get("path"): item.get("sha256") for item in receipt.get("digests", [])}
    for path, want in expected.items():
        got = observed.get(path)
        if got is None:
            rejections.append(f"DIGEST_NOT_REPORTED:{path}")
        elif got != want:
            rejections.append(f"DIGEST_MISMATCH:{path}")

    verdict = "REJECTED" if rejections else "ACCEPTED_AS_INDEPENDENT_CLEAN_ROOM_REPLAY"
    print(
        json.dumps(
            {
                "schema": "orion.p6.clean-room-receipt-verdict.v1",
                "verdict": verdict,
                "custodian": custodian or None,
                "steps_contracted": len(contracted),
                "steps_reported": len(reported),
                "digests_contracted": len(expected),
                "digests_reported": len(observed),
                "rejections": rejections,
                "grants": (
                    "Independent reproduction of the bounded formal artifact, and nothing else. "
                    "No empirical extension and no scientific authority beyond the artifact."
                    if not rejections
                    else "Nothing."
                ),
            },
            indent=2,
        )
    )
    return 2 if rejections else 0


if __name__ == "__main__":
    sys.exit(main())
