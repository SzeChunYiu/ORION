from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from typing import Any

DOMAINS = (
    "SCIENTIFIC_LITERATURE",
    "WEB_API_EVIDENCE",
    "DATASET_REGISTRY",
    "CODE_ARTIFACT_REPOSITORY",
    "EXPERIMENT_MEASUREMENT_ROUTE",
)
ARCHETYPES = (
    "ALL_OBLIGATIONS_DISCHARGED",
    "AVAILABLE_ROUTE_STOPS_OTHER_OPEN",
    "MATERIAL_ROUTE_UNAVAILABLE",
    "MATERIAL_ROUTE_CENSORED",
    "PROVIDER_INVALID",
    "DUPLICATE_ROUTE_COVERAGE",
    "ACQUIRED_NOT_QUESTION_PROCESSED",
    "LOW_UTILITY_HARD_ROUTE_OPEN",
)
GENERATOR_ID = "P2_X_DEV_GENERATOR_V1"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _route(
    route_id: str,
    *,
    state: str = "AVAILABLE",
    complete: bool = True,
    utility: bool = True,
    processed: bool = True,
    material: bool = True,
) -> dict[str, Any]:
    return {
        "route_id": route_id,
        "material": material,
        "state": state,
        "evidence_coverage_complete": complete,
        "decision_sufficient": complete,
        "utility_stop": utility,
        "finite_certificate_complete": complete,
        "content_items": [{"content_id": f"{route_id}:item", "question_processed": processed}],
    }


def _route_decision(route: dict[str, Any]) -> str:
    if route["state"] != "AVAILABLE":
        return "ROUTE_CANNOT_CHECK"
    if (
        route["evidence_coverage_complete"]
        and route["decision_sufficient"]
        and route["finite_certificate_complete"]
    ):
        return "ROUTE_STOP"
    return "ROUTE_CONTINUE"


def build_case(domain: str, archetype: str, variant: int) -> dict[str, Any]:
    if domain not in DOMAINS or archetype not in ARCHETYPES or variant not in range(1, 6):
        raise ValueError((domain, archetype, variant))
    case_id = f"P2X-DEV-{domain}-{archetype}-V{variant:02d}"
    r1, r2, r3 = (f"{case_id}:R{i}" for i in (1, 2, 3))
    routes = [_route(r1), _route(r2), _route(r3)]
    global_sufficiency = True

    if archetype == "ALL_OBLIGATIONS_DISCHARGED":
        pass
    elif archetype == "AVAILABLE_ROUTE_STOPS_OTHER_OPEN":
        routes[1] = _route(r2, complete=False, utility=False)
        global_sufficiency = False
    elif archetype == "MATERIAL_ROUTE_UNAVAILABLE":
        routes[2] = _route(r3, state="UNAVAILABLE")
    elif archetype == "MATERIAL_ROUTE_CENSORED":
        routes[2] = _route(r3, state="CENSORED")
    elif archetype == "PROVIDER_INVALID":
        routes[2] = _route(r3, state="PROVIDER_INVALID")
    elif archetype == "DUPLICATE_ROUTE_COVERAGE":
        # R1/R2 return exactly the same content identity; R3 is the independent
        # material route still open. Duplicate observations cannot create closure.
        routes[2] = _route(r3, complete=False, utility=False)
        routes[1]["content_items"] = deepcopy(routes[0]["content_items"])
        global_sufficiency = True
    elif archetype == "ACQUIRED_NOT_QUESTION_PROCESSED":
        routes[1] = _route(r2, complete=True, processed=False)
    elif archetype == "LOW_UTILITY_HARD_ROUTE_OPEN":
        routes[2] = _route(r3, complete=False, utility=True)

    route_decisions = {route["route_id"]: _route_decision(route) for route in routes}
    material_decisions = [route_decisions[r["route_id"]] for r in routes if r["material"]]
    any_unavailable = any(decision == "ROUTE_CANNOT_CHECK" for decision in material_decisions)
    any_open = any(decision == "ROUTE_CONTINUE" for decision in material_decisions)
    processing_open = any(
        route["material"]
        and any(not item["question_processed"] for item in route["content_items"])
        for route in routes
    )
    if any_unavailable:
        terminal = "CANNOT_CHECK"
    elif any_open or processing_open:
        terminal = "CONTINUE"
    else:
        terminal = "TASK_STOP"

    return {
        "case_id": case_id,
        "domain": domain,
        "archetype": archetype,
        "generator_id": GENERATOR_ID,
        "seed_commitment": _sha(f"{case_id}:NON_AUTHORIZING_DEV"),
        "candidate_visible": {
            "routes": routes,
            "global_evidence_sufficiency": global_sufficiency,
        },
        "protected_gold": {
            "route_decisions": route_decisions,
            "task_terminal": terminal,
            "unresolved_route_decision_changing": archetype
            in {"MATERIAL_ROUTE_UNAVAILABLE", "MATERIAL_ROUTE_CENSORED", "PROVIDER_INVALID"},
            "provenance_commitment": _sha(f"{case_id}:DEV_GOLD"),
        },
        "budget": {"max_route_checks": 3, "max_tool_calls": 8},
    }


def generate_cases() -> list[dict[str, Any]]:
    return [
        build_case(domain, archetype, variant)
        for domain in DOMAINS
        for archetype in ARCHETYPES
        for variant in range(1, 6)
    ]


def main() -> int:
    cases = generate_cases()
    json.dump(
        {
            "schema_version": "P2_X_DEV_CASES_V1",
            "authority": "NON_AUTHORIZING_DEV",
            "case_count": len(cases),
            "cases": cases,
        },
        sys.stdout,
        sort_keys=True,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
