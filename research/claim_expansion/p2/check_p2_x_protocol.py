from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "P2_X_PROTOCOL_V1.md"
SCHEMA = ROOT / "P2_X_CASE_V1.schema.json"
REGISTRY = ROOT / "P2_X_BASELINE_REGISTRY_V1.json"

EXPECTED_ARMS = {
    "B1_DONOR_COMPLETE_AVAILABLE_ROUTE_PRODUCT",
    "B2_GLOBAL_SUFFICIENCY_AGGREGATOR",
    "B3_IDEAL_TYPED_ROUTE_PRODUCT",
    "P2X_FAIL_CLOSED_ROUTE_AUTHORITY",
}
EXPECTED_DOMAINS = {
    "SCIENTIFIC_LITERATURE",
    "WEB_API_EVIDENCE",
    "DATASET_REGISTRY",
    "CODE_ARTIFACT_REPOSITORY",
    "EXPERIMENT_MEASUREMENT_ROUTE",
}
EXPECTED_ARCHETYPES = {
    "ALL_OBLIGATIONS_DISCHARGED",
    "AVAILABLE_ROUTE_STOPS_OTHER_OPEN",
    "MATERIAL_ROUTE_UNAVAILABLE",
    "MATERIAL_ROUTE_CENSORED",
    "PROVIDER_INVALID",
    "DUPLICATE_ROUTE_COVERAGE",
    "ACQUIRED_NOT_QUESTION_PROCESSED",
    "LOW_UTILITY_HARD_ROUTE_OPEN",
}
EXPECTED_ROUTE_STATES = {"AVAILABLE", "UNAVAILABLE", "CENSORED", "PROVIDER_INVALID"}
EXPECTED_ROUTE_TERMINALS = {"ROUTE_STOP", "ROUTE_CONTINUE", "ROUTE_CANNOT_CHECK"}
EXPECTED_TASK_TERMINALS = {"TASK_STOP", "CONTINUE", "CANNOT_CHECK"}
PROTECTED_FIELDS = {
    "route_decisions",
    "task_terminal",
    "unresolved_route_decision_changing",
    "provenance_commitment",
}


def validate_protocol(protocol: str, schema: dict[str, Any], registry: dict[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if "PROTOCOL_FROZEN__NO_PROTECTED_OUTCOMES_ACCESSED" not in protocol:
        errors.append("missing_preoutcome_freeze_marker")
    if "Current result: `CANNOT_CHECK`." not in protocol:
        errors.append("protocol_result_not_cannot_check")
    for phrase in (
        "`UNAVAILABLE`, `CENSORED`, or `PROVIDER_INVALID` material routes are `ROUTE_CANNOT_CHECK`",
        "Task `TASK_STOP` requires every material route obligation to be discharged",
        "Route-local `ROUTE_STOP` never implies `TASK_STOP` by itself.",
    ):
        if phrase not in protocol:
            errors.append(f"missing_authority_rule:{phrase[:24]}")

    if registry.get("result_authority") != "CANNOT_CHECK":
        errors.append("registry_result_not_cannot_check")
    arms = registry.get("arms", [])
    arm_ids = {arm.get("id") for arm in arms if isinstance(arm, dict)}
    if arm_ids != EXPECTED_ARMS:
        errors.append("arm_ids_drift")
    by_id = {arm.get("id"): arm for arm in arms if isinstance(arm, dict)}
    b3 = by_id.get("B3_IDEAL_TYPED_ROUTE_PRODUCT", {})
    if b3.get("expected_relation_to_p2x") != "EXTENSIONAL_TIE_IF_IDENTICAL_SEMANTICS":
        errors.append("b3_equivalence_boundary_missing")
    if b3.get("significance_test") is not False:
        errors.append("b3_significance_forbidden")
    p2x = by_id.get("P2X_FAIL_CLOSED_ROUTE_AUTHORITY", {})
    if p2x.get("result_authority") != "CANNOT_CHECK":
        errors.append("p2x_result_not_cannot_check")

    primary = registry.get("primary_hypothesis", {})
    if primary.get("minimum_absolute_escd_gain") != 0.10:
        errors.append("primary_margin_drift")
    if primary.get("paired_bootstrap_95ci_lower_bound_requirement") != 0.0:
        errors.append("primary_ci_rule_drift")
    scale = registry.get("protected_scale", {})
    if (
        scale.get("domains"),
        scale.get("archetypes_per_domain"),
        scale.get("variants_per_archetype"),
        scale.get("total_cases"),
    ) != (5, 8, 10, 400):
        errors.append("protected_scale_drift")
    nonreg = registry.get("non_regression", {})
    expected_nonreg = {
        "clean_task_stop_margin": -0.02,
        "false_task_closure_target": 0,
        "unnecessary_cannot_check_clean_target": 0,
        "minimum_per_domain_escd_difference": -0.05,
    }
    for key, value in expected_nonreg.items():
        if nonreg.get(key) != value:
            errors.append(f"nonreg_drift:{key}")

    if schema.get("additionalProperties") is not False:
        errors.append("schema_top_level_open")
    props = schema.get("properties", {})
    if set(props.get("domain", {}).get("enum", [])) != EXPECTED_DOMAINS:
        errors.append("domain_enum_drift")
    if set(props.get("archetype", {}).get("enum", [])) != EXPECTED_ARCHETYPES:
        errors.append("archetype_enum_drift")
    candidate = props.get("candidate_visible", {})
    protected = props.get("protected_gold", {})
    if candidate.get("additionalProperties") is not False:
        errors.append("candidate_visible_open")
    if protected.get("additionalProperties") is not False:
        errors.append("protected_gold_open")
    for name in sorted(set(candidate.get("properties", {})) & PROTECTED_FIELDS):
        errors.append(f"protected_leak:{name}")
    if not PROTECTED_FIELDS <= set(protected.get("required", [])):
        errors.append("protected_required_fields_missing")
    route = (
        candidate.get("properties", {})
        .get("routes", {})
        .get("items", {})
    )
    route_props = route.get("properties", {})
    if set(route_props.get("state", {}).get("enum", [])) != EXPECTED_ROUTE_STATES:
        errors.append("route_state_enum_drift")
    required_route = {
        "route_id",
        "material",
        "state",
        "evidence_coverage_complete",
        "decision_sufficient",
        "utility_stop",
        "finite_certificate_complete",
        "content_items",
    }
    if set(route.get("required", [])) != required_route:
        errors.append("route_required_fields_drift")
    content = route_props.get("content_items", {}).get("items", {})
    if set(content.get("required", [])) != {"content_id", "question_processed"}:
        errors.append("content_processing_contract_drift")
    route_decisions = protected.get("properties", {}).get("route_decisions", {})
    if set(route_decisions.get("additionalProperties", {}).get("enum", [])) != EXPECTED_ROUTE_TERMINALS:
        errors.append("route_terminal_enum_drift")
    if set(protected.get("properties", {}).get("task_terminal", {}).get("enum", [])) != EXPECTED_TASK_TERMINALS:
        errors.append("task_terminal_enum_drift")
    return tuple(errors)


def load_committed() -> tuple[str, dict[str, Any], dict[str, Any]]:
    return PROTOCOL.read_text(), json.loads(SCHEMA.read_text()), json.loads(REGISTRY.read_text())


def main() -> int:
    errors = validate_protocol(*load_committed())
    if errors:
        print("\n".join(errors))
        return 1
    print("P2_X_PROTOCOL_V1_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
