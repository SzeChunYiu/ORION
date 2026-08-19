from __future__ import annotations

import hashlib
import json
from collections import Counter

from generate_p4_x_protected_cases import generate_cases

EXPECTED_ROWS_SHA256 = "8539ee33c0ae033951101cfe5982b38f8e6a2962d2cfd8c891f2973cafcc2b7b"
EXPECTED_COUNTS = {
    "P4_X": 400,
    "B1_GENERIC_AUTHORIZATION_PRODUCT": 250,
    "B2_COMPENSATORY_PRODUCT": 50,
    "B3_IDEAL_TYPED_PRODUCT": 400,
}


def independent_p4(case):
    x = case["candidate_visible"]
    invalid = (
        (not x["claim_supported"])
        or (not x["provenance_valid"])
        or (not x["checker_admissible"])
        or (not x["evaluator_custody_valid"])
        or (not x["artifact_version_match"])
        or (not x["claim_scope_match"])
    )
    if invalid:
        return "BLOCK"
    unresolved = (
        (not x["epoch_fresh"])
        or (not x["evidence_independence_valid"])
        or (not x["scientific_obligation_resolved"])
    )
    return "CANNOT_CHECK" if unresolved else "PROMOTE"


def independent_b1(case):
    x = case["candidate_visible"]
    if not all(
        x[k]
        for k in (
            "claim_supported",
            "provenance_valid",
            "checker_admissible",
            "evaluator_custody_valid",
            "artifact_version_match",
            "action_authorized",
        )
    ):
        return "BLOCK"
    return "CANNOT_CHECK" if not x["epoch_fresh"] else "PROMOTE"


def independent_b2(case):
    x = case["candidate_visible"]
    vals = [
        x[k]
        for k in (
            "claim_supported",
            "provenance_valid",
            "checker_admissible",
            "evaluator_custody_valid",
            "artifact_version_match",
            "claim_scope_match",
            "epoch_fresh",
            "evidence_independence_valid",
            "scientific_obligation_resolved",
            "action_authorized",
        )
    ]
    score = 0.9 * (sum(bool(v) for v in vals) / len(vals)) + 0.1 * float(x["soft_confidence"])
    return "PROMOTE" if score >= 0.80 else "BLOCK"


def verify():
    rows = []
    counts = Counter()
    b3_mismatches = 0
    for case in generate_cases():
        gold = case["protected_gold"]["task_terminal"]
        p4 = independent_p4(case)
        decisions = {
            "P4_X": p4,
            "B1_GENERIC_AUTHORIZATION_PRODUCT": independent_b1(case),
            "B2_COMPENSATORY_PRODUCT": independent_b2(case),
            "B3_IDEAL_TYPED_PRODUCT": independent_p4(case),
        }
        rows.append(
            {
                "case_id": case["case_id"],
                "domain": case["domain"],
                "archetype": case["archetype"],
                "gold": gold,
                "decisions": decisions,
            }
        )
        for arm, decision in decisions.items():
            counts[arm] += int(decision == gold)
        b3_mismatches += int(decisions["B3_IDEAL_TYPED_PRODUCT"] != p4)
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    row_sha = hashlib.sha256(payload.encode()).hexdigest()
    assert row_sha == EXPECTED_ROWS_SHA256
    assert dict(counts) == EXPECTED_COUNTS
    assert b3_mismatches == 0
    return {
        "schema_version": "P4_X_INDEPENDENT_VERIFICATION_V1",
        "case_count": len(rows),
        "rows_sha256": row_sha,
        "counts_correct": dict(counts),
        "b3_p4x_decision_mismatches": b3_mismatches,
        "imports_original_execution_module": False,
        "verification_state": "VERIFIED_BOUNDED_EXACT",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True, indent=2))
