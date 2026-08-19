from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import generate_p2_x_protected_cases as generator  # noqa: E402

RESULT = HERE / "P2_X_PROTECTED_RESULT_V1.json"


def route_decision(route: dict[str, Any]) -> str:
    if route["state"] != "AVAILABLE":
        return "ROUTE_CANNOT_CHECK"
    if route["evidence_coverage_complete"] and route["decision_sufficient"] and route["finite_certificate_complete"]:
        return "ROUTE_STOP"
    return "ROUTE_CONTINUE"


def processed(route: dict[str, Any]) -> bool:
    return all(item["question_processed"] for item in route["content_items"])


def independent_p2x(case: dict[str, Any]) -> dict[str, Any]:
    routes = case["candidate_visible"]["routes"]
    decisions = {route["route_id"]: route_decision(route) for route in routes}
    material = [route for route in routes if route["material"]]
    if any(decisions[route["route_id"]] == "ROUTE_CANNOT_CHECK" for route in material):
        task = "CANNOT_CHECK"
    elif any(decisions[route["route_id"]] == "ROUTE_CONTINUE" for route in material):
        task = "CONTINUE"
    elif any(not processed(route) for route in material):
        task = "CONTINUE"
    else:
        task = "TASK_STOP"
    return {"route_decisions": decisions, "task_terminal": task}


def independent_b1(case: dict[str, Any]) -> dict[str, Any]:
    routes = case["candidate_visible"]["routes"]
    decisions = {route["route_id"]: route_decision(route) for route in routes}
    available = [route for route in routes if route["material"] and route["state"] == "AVAILABLE"]
    if not available:
        task = "CANNOT_CHECK"
    elif any(decisions[route["route_id"]] == "ROUTE_CONTINUE" for route in available):
        task = "CONTINUE"
    elif any(not processed(route) for route in available):
        task = "CONTINUE"
    else:
        task = "TASK_STOP"
    return {"route_decisions": decisions, "task_terminal": task}


def independent_b2(case: dict[str, Any]) -> dict[str, Any]:
    decisions = {route["route_id"]: route_decision(route) for route in case["candidate_visible"]["routes"]}
    return {
        "route_decisions": decisions,
        "task_terminal": "TASK_STOP" if case["candidate_visible"]["global_evidence_sufficiency"] else "CONTINUE",
    }


def score(case: dict[str, Any], decision: dict[str, Any]) -> int:
    gold = case["protected_gold"]
    if decision["route_decisions"] != gold["route_decisions"]:
        return 0
    if decision["task_terminal"] != gold["task_terminal"]:
        return 0
    if gold["unresolved_route_decision_changing"] and decision["task_terminal"] == "TASK_STOP":
        return 0
    if decision["task_terminal"] == "TASK_STOP":
        if any(route["material"] and not processed(route) for route in case["candidate_visible"]["routes"]):
            return 0
    return 1


def verify() -> dict[str, Any]:
    expected = json.loads(RESULT.read_text())
    cases = generator.generate_cases()
    pair_digest = hashlib.sha256("\n".join(f"{case['case_id']}|{case['seed_commitment']}" for case in cases).encode()).hexdigest()
    bundle_digest = hashlib.sha256(json.dumps(generator.generate_bundle(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    functions = {
        "B1_DONOR_COMPLETE_AVAILABLE_ROUTE_PRODUCT": independent_b1,
        "B2_GLOBAL_SUFFICIENCY_AGGREGATOR": independent_b2,
        "B3_IDEAL_TYPED_ROUTE_PRODUCT": independent_p2x,
        "P2X_FAIL_CLOSED_ROUTE_AUTHORITY": independent_p2x,
    }
    counts = {arm: 0 for arm in functions}
    rows = []
    for case in cases:
        decisions = {arm: function(case) for arm, function in functions.items()}
        row_scores = {arm: score(case, decision) for arm, decision in decisions.items()}
        for arm, value in row_scores.items():
            counts[arm] += value
        rows.append({"case_id": case["case_id"], "domain": case["domain"], "archetype": case["archetype"], "generator_id": case["generator_id"], "decisions": decisions, "escd": row_scores})

    row_digest = hashlib.sha256("\n".join(json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows).encode()).hexdigest()
    expected_counts = {arm: item["correct"] for arm, item in expected["arm_escd"].items()}
    b3_mismatches = sum(1 for row in rows if row["decisions"]["B3_IDEAL_TYPED_ROUTE_PRODUCT"] != row["decisions"]["P2X_FAIL_CLOSED_ROUTE_AUTHORITY"])
    checks = {
        "case_count": len(cases) == expected["n"] == 400,
        "identity_pair_digest": pair_digest == expected["protected_identity_pairs_sha256"],
        "bundle_digest": bundle_digest == expected["protected_bundle_sha256"],
        "row_digest": row_digest == expected["canonical_rows_sha256"],
        "headline_counts": counts == expected_counts,
        "b3_decision_mismatches_zero": b3_mismatches == expected["b3_equivalence"]["decision_mismatches"] == 0,
    }
    return {
        "schema_version": "P2_X_INDEPENDENT_VERIFICATION_V1",
        "independent_of_execution_module": true,
        "case_count": len(cases),
        "arm_correct": counts,
        "identity_pair_digest": pair_digest,
        "bundle_digest": bundle_digest,
        "row_digest": row_digest,
        "b3_decision_mismatches": b3_mismatches,
        "checks": checks,
        "ok": all(checks.values()),
        "terminal": "P2_X_INDEPENDENT_VERIFICATION_PASS" if all(checks.values()) else "P2_X_INDEPENDENT_VERIFICATION_FAIL",
    }


def main() -> int:
    result = verify()
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
