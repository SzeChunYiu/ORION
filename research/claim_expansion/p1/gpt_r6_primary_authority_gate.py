from __future__ import annotations

import argparse
import json
from pathlib import Path


def _candidate_rows(result: dict[str, object]) -> list[dict[str, object]]:
    rows = [
        member
        for pair in result.get("pair_rows", [])
        for member in pair["outcomes"].values()
    ]
    rows.extend(row["outcome"] for row in result.get("unresolved_rows", []))
    return rows


def _assessment_receipts_fail_closed(result: dict[str, object]) -> bool:
    for row in _candidate_rows(result):
        for arm_key in ("base_native", "ard_native"):
            arm = row[arm_key]
            status = str(arm["responsibility_status"])
            assessments = tuple(str(value) for value in arm["assessment_statuses"])
            if not assessments:
                return False
            if status == "IDENTIFIED":
                if any(value != "ADMISSIBLE" for value in assessments):
                    return False
            elif any(value == "ADMISSIBLE" for value in assessments):
                return False
    return True


def apply_authority_gate(result: dict[str, object]) -> dict[str, object]:
    if not result.get("policy_outcomes_generated"):
        return result

    checks = dict(result["checks"])
    pair_class = {
        str(key): float(value)
        for key, value in dict(result["substantive_class_pair_differences"]).items()
    }
    checks["pair_class_noninferiority"] = all(
        value >= -0.10 for value in pair_class.values()
    )
    checks["minimum_three_nonnegative_pair_classes"] = sum(
        value >= 0.0 for value in pair_class.values()
    ) >= 3
    checks["all_48_native_rows_executed"] = (
        int(result.get("n_episodes", -1)) == 48
        and int(result.get("native_invalid_rows", -1)) == 0
        and int(result.get("candidate_metadata_leakage_rows", -1)) == 0
    )
    checks["mechanic_assessment_receipts_fail_closed"] = _assessment_receipts_fail_closed(
        result
    )
    result["checks"] = checks
    result["terminal"] = (
        "P1_R6_PRIMARY_PASS_PENDING_2019_REPLICATION"
        if all(checks.values())
        else "P1_R6_PRIMARY_NOT_SUPPORTED"
    )
    result["authority_gate"] = {
        "schema": "P1U.R6PrimaryAuthorityGate.v1",
        "frozen_before_primary_outcome": True,
        "pair_class_floor": -0.10,
        "minimum_nonnegative_pair_classes": 3,
        "requires_fail_closed_mechanic_assessments": True,
        "promotion_authorized": False,
        "merge_authorized": False,
        "replication_required_for_positive_primary": True,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = apply_authority_gate(json.loads(args.input.read_text()))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
