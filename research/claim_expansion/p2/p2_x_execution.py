from __future__ import annotations

from copy import deepcopy
from typing import Any

ROUTE_TERMINALS = {"ROUTE_STOP", "ROUTE_CONTINUE", "ROUTE_CANNOT_CHECK"}
TASK_TERMINALS = {"TASK_STOP", "CONTINUE", "CANNOT_CHECK"}


def route_decision(route: dict[str, Any]) -> str:
    if route["state"] != "AVAILABLE":
        return "ROUTE_CANNOT_CHECK"
    if (
        route["evidence_coverage_complete"]
        and route["decision_sufficient"]
        and route["finite_certificate_complete"]
    ):
        return "ROUTE_STOP"
    return "ROUTE_CONTINUE"


def _route_decisions(case: dict[str, Any]) -> dict[str, str]:
    return {
        route["route_id"]: route_decision(route)
        for route in case["candidate_visible"]["routes"]
    }


def _processing_complete(route: dict[str, Any]) -> bool:
    return all(item["question_processed"] for item in route["content_items"])


def decide_p2x(case: dict[str, Any]) -> dict[str, Any]:
    routes = case["candidate_visible"]["routes"]
    decisions = _route_decisions(case)
    material = [route for route in routes if route["material"]]
    if any(decisions[route["route_id"]] == "ROUTE_CANNOT_CHECK" for route in material):
        task_terminal = "CANNOT_CHECK"
    elif any(decisions[route["route_id"]] == "ROUTE_CONTINUE" for route in material):
        task_terminal = "CONTINUE"
    elif any(not _processing_complete(route) for route in material):
        task_terminal = "CONTINUE"
    else:
        task_terminal = "TASK_STOP"
    return {"route_decisions": decisions, "task_terminal": task_terminal}


def decide_b1_available_route_product(case: dict[str, Any]) -> dict[str, Any]:
    routes = case["candidate_visible"]["routes"]
    decisions = _route_decisions(case)
    available_material = [
        route for route in routes if route["material"] and route["state"] == "AVAILABLE"
    ]
    # Strong baseline: preserves the P2 content-vs-question-processing distinction.
    # Its sole systematic gap is global closure over the available-route denominator.
    if not available_material:
        task_terminal = "CANNOT_CHECK"
    elif any(decisions[route["route_id"]] == "ROUTE_CONTINUE" for route in available_material):
        task_terminal = "CONTINUE"
    elif any(not _processing_complete(route) for route in available_material):
        task_terminal = "CONTINUE"
    else:
        task_terminal = "TASK_STOP"
    return {"route_decisions": decisions, "task_terminal": task_terminal}


def decide_b2_global_sufficiency(case: dict[str, Any]) -> dict[str, Any]:
    decisions = _route_decisions(case)
    task_terminal = (
        "TASK_STOP"
        if case["candidate_visible"]["global_evidence_sufficiency"]
        else "CONTINUE"
    )
    return {"route_decisions": decisions, "task_terminal": task_terminal}


def decide_b3_ideal_typed_product(case: dict[str, Any]) -> dict[str, Any]:
    return decide_p2x(case)


ARM_FUNCTIONS = {
    "B1_DONOR_COMPLETE_AVAILABLE_ROUTE_PRODUCT": decide_b1_available_route_product,
    "B2_GLOBAL_SUFFICIENCY_AGGREGATOR": decide_b2_global_sufficiency,
    "B3_IDEAL_TYPED_ROUTE_PRODUCT": decide_b3_ideal_typed_product,
    "P2X_FAIL_CLOSED_ROUTE_AUTHORITY": decide_p2x,
}


def run_arm(case: dict[str, Any], arm_id: str) -> dict[str, Any]:
    return deepcopy(ARM_FUNCTIONS[arm_id](case))


def score_escd(case: dict[str, Any], decision: dict[str, Any]) -> int:
    gold = case["protected_gold"]
    if decision["route_decisions"] != gold["route_decisions"]:
        return 0
    if decision["task_terminal"] != gold["task_terminal"]:
        return 0
    # A protected unresolved material route may never be laundered into TASK_STOP.
    if gold["unresolved_route_decision_changing"] and decision["task_terminal"] == "TASK_STOP":
        return 0
    if decision["task_terminal"] == "TASK_STOP":
        for route in case["candidate_visible"]["routes"]:
            if route["material"] and not _processing_complete(route):
                return 0
    return 1


def false_task_closure(case: dict[str, Any], decision: dict[str, Any]) -> int:
    return int(
        decision["task_terminal"] == "TASK_STOP"
        and case["protected_gold"]["task_terminal"] != "TASK_STOP"
    )


def unnecessary_cannot_check_clean(case: dict[str, Any], decision: dict[str, Any]) -> int:
    return int(
        case["archetype"] == "ALL_OBLIGATIONS_DISCHARGED"
        and decision["task_terminal"] == "CANNOT_CHECK"
    )
