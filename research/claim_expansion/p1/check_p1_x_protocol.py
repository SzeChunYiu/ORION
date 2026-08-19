from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "P1_X_PROTOCOL_V1.md"
SCHEMA = ROOT / "SCIENTIFIC_REVISION_RESPONSIBILITY_CASE_V1.schema.json"
REGISTRY = ROOT / "P1_X_BASELINE_REGISTRY_V1.json"
LEDGER = ROOT / "P1_X_CLAIM_EXPANSION_LEDGER_V1.md"

EXPECTED_ARM_IDS = {
    "B1_DONOR_COMPLETE_GREEDY",
    "B2_SUCCESS_AUTHORIZES_REFRAME",
    "B3_IDEAL_TYPED_PRODUCT",
    "P1X_MINIMAL_SCIENTIFIC_ESCALATION",
}
EXPECTED_REVISION_CLASSES = {
    "EVIDENCE_REVISION",
    "EXPERIMENT_MEASUREMENT_REVISION",
    "PARAMETER_REVISION",
    "MODEL_SELECTION_REVISION",
    "MODEL_CLASS_EXPANSION",
    "REPRESENTATION_REGIME_REVISION",
    "QUESTION_OBJECTIVE_REVISION",
    "METHOD_BASIS_REVISION",
    "EXECUTION_ENVIRONMENT_REVISION",
    "EVALUATOR_AUTHORITY_REVISION",
}
EXPECTED_TERMINALS = {
    "REPAIR_LOCAL",
    "REVISE_HIGH_LEVEL",
    "REQUEST_DISCRIMINATOR",
    "UNRESOLVED",
    "CANNOT_CHECK",
    "NO_CHANGE",
}
EXPECTED_DISCRIMINATOR_STATUS = {"NOT_NEEDED", "AVAILABLE", "UNAVAILABLE"}
PROTECTED_GOLD_FIELDS = {
    "causal_responsibility_set",
    "best_intervention_set",
    "scientifically_justified_revision_set",
    "revision_evaluations",
    "ambiguity_state",
    "correct_terminal",
    "exact_reopen_set",
    "provenance_commitment",
}
EXPECTED_REVISION_EVALUATION_FIELDS = {
    "revision_id",
    "candidate_class",
    "restores_target",
    "preserves_invariants",
    "observed_reopen_set",
    "authorized",
}
EXPECTED_REVISION_PROPOSAL_FIELDS = {
    "revision_id",
    "candidate_class",
    "proposed_reopen_set",
    "declared_protected_invariants",
}


def _section(text: str, heading: str, next_heading: str | None = None) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    start += len(heading)
    if next_heading is None:
        return text[start:]
    end = text.find(next_heading, start)
    return text[start:] if end < 0 else text[start:end]


def validate_protocol(
    protocol_text: str,
    schema: dict[str, Any],
    registry: dict[str, Any],
    ledger_text: str,
) -> tuple[str, ...]:
    errors: list[str] = []

    # The protocol and registry are immutable pre-outcome design records.  Their
    # CANNOT_CHECK authority must remain frozen even after a separate result
    # ledger earns a bounded post-outcome disposition.
    if "PROTOCOL_FROZEN__NO_PROTECTED_OUTCOMES_ACCESSED" not in protocol_text:
        errors.append("protocol_missing_preoutcome_freeze_terminal")
    if "Current result state: `CANNOT_CHECK`." not in protocol_text:
        errors.append("protocol_result_authority_not_cannot_check")
    if "No result, novelty promotion, or manuscript broadening is authorized" not in protocol_text:
        errors.append("protocol_missing_no_promotion_guard")
    for phrase in (
        "return `REPAIR_LOCAL`",
        "return `REVISE_HIGH_LEVEL`",
        "return `REQUEST_DISCRIMINATOR`",
        "return `UNRESOLVED`",
        "return `CANNOT_CHECK`",
        "return `NO_CHANGE`",
    ):
        if phrase not in protocol_text:
            errors.append(f"protocol_terminal_mapping_missing:{phrase}")

    if registry.get("result_authority") != "CANNOT_CHECK":
        errors.append(f"registry_result_authority:{registry.get('result_authority')}")

    arms = registry.get("arms")
    if not isinstance(arms, list):
        errors.append("registry_arms_not_list")
        arms = []
    arm_ids = {arm.get("id") for arm in arms if isinstance(arm, dict)}
    if arm_ids != EXPECTED_ARM_IDS:
        errors.append("registry_arm_ids_mismatch")
    by_id = {
        arm.get("id"): arm
        for arm in arms
        if isinstance(arm, dict) and isinstance(arm.get("id"), str)
    }
    b3 = by_id.get("B3_IDEAL_TYPED_PRODUCT", {})
    if b3.get("expected_relation_to_p1x") != "EXTENSIONAL_TIE_IF_IDENTICAL_SEMANTICS":
        errors.append("b3_equivalence_boundary_missing")
    if b3.get("significance_test") is not False:
        errors.append("b3_must_not_use_significance_test")
    p1x = by_id.get("P1X_MINIMAL_SCIENTIFIC_ESCALATION", {})
    if p1x.get("result_authority") != "CANNOT_CHECK":
        errors.append(f"p1x_result_authority:{p1x.get('result_authority')}")

    primary = registry.get("primary_hypothesis", {})
    if primary.get("minimum_absolute_esrd_gain") != 0.10:
        errors.append("primary_practical_margin_drift")
    if primary.get("paired_bootstrap_95ci_lower_bound_requirement") != 0.0:
        errors.append("primary_ci_requirement_drift")

    expected_non_regression = {
        "lower_level_repair_success_margin": -0.02,
        "false_high_level_reframe_rate_margin": 0.02,
        "protected_invariant_violation_target": 0,
        "minimum_per_domain_esrd_difference": -0.05,
    }
    non_regression = registry.get("non_regression", {})
    for key, expected in expected_non_regression.items():
        if non_regression.get(key) != expected:
            errors.append(f"non_regression_drift:{key}")

    scale = registry.get("protected_scale", {})
    numeric_scale = (
        scale.get("domains"),
        scale.get("archetypes_per_domain"),
        scale.get("variants_per_archetype"),
        scale.get("total_cases"),
    )
    if not all(isinstance(x, int) and not isinstance(x, bool) for x in numeric_scale):
        errors.append("protected_scale_not_integer")
    elif numeric_scale != (5, 8, 10, 400):
        errors.append("protected_scale_drift")

    if schema.get("additionalProperties") is not False:
        errors.append("schema_top_level_not_closed")
    required = set(schema.get("required", []))
    for required_name in {"candidate_visible", "protected_gold", "revision_classes", "budget"}:
        if required_name not in required:
            errors.append(f"schema_missing_required:{required_name}")

    props = schema.get("properties", {})
    candidate = props.get("candidate_visible", {})
    protected = props.get("protected_gold", {})
    if candidate.get("additionalProperties") is not False:
        errors.append("candidate_visible_not_closed")
    if protected.get("additionalProperties") is not False:
        errors.append("protected_gold_not_closed")

    candidate_fields = set(candidate.get("properties", {}))
    for name in sorted(candidate_fields & PROTECTED_GOLD_FIELDS):
        errors.append(f"protected_gold_leaked_to_candidate_visible:{name}")

    candidate_required = set(candidate.get("required", []))
    for required_name in {"revision_proposals", "discriminator_status"}:
        if required_name not in candidate_required:
            errors.append(f"candidate_visible_missing_{required_name}")
    discriminator_enum = set(
        candidate.get("properties", {}).get("discriminator_status", {}).get("enum", [])
    )
    if discriminator_enum != EXPECTED_DISCRIMINATOR_STATUS:
        errors.append("discriminator_status_enum_drift")

    proposal = candidate.get("properties", {}).get("revision_proposals", {})
    if proposal.get("type") != "array" or proposal.get("minItems") != 1:
        errors.append("revision_proposals_not_required_nonempty_array")
    proposal_item = proposal.get("items", {})
    if proposal_item.get("additionalProperties") is not False:
        errors.append("revision_proposal_item_not_closed")
    if set(proposal_item.get("required", [])) != EXPECTED_REVISION_PROPOSAL_FIELDS:
        errors.append("revision_proposal_required_fields_drift")
    proposal_props = proposal_item.get("properties", {})
    if proposal_props.get("proposed_reopen_set", {}).get("type") != "array":
        errors.append("revision_proposal_reopen_set_not_array")
    if proposal_props.get("declared_protected_invariants", {}).get("type") != "array":
        errors.append("revision_proposal_invariants_not_array")

    protected_required = set(protected.get("required", []))
    for name in sorted(PROTECTED_GOLD_FIELDS - protected_required):
        errors.append(f"protected_gold_missing_required:{name}")

    revision_eval = protected.get("properties", {}).get("revision_evaluations", {})
    if revision_eval.get("type") != "array" or revision_eval.get("minItems") != 1:
        errors.append("revision_evaluations_not_required_nonempty_array")
    revision_eval_item = revision_eval.get("items", {})
    if revision_eval_item.get("additionalProperties") is not False:
        errors.append("revision_evaluation_item_not_closed")
    if set(revision_eval_item.get("required", [])) != EXPECTED_REVISION_EVALUATION_FIELDS:
        errors.append("revision_evaluation_required_fields_drift")
    revision_eval_props = revision_eval_item.get("properties", {})
    for boolean_field in ("restores_target", "preserves_invariants", "authorized"):
        if revision_eval_props.get(boolean_field, {}).get("type") != "boolean":
            errors.append(f"revision_evaluation_not_boolean:{boolean_field}")
    if revision_eval_props.get("observed_reopen_set", {}).get("type") != "array":
        errors.append("revision_evaluation_reopen_set_not_array")

    terminals = set(protected.get("properties", {}).get("correct_terminal", {}).get("enum", []))
    if terminals != EXPECTED_TERMINALS:
        errors.append("terminal_enum_drift")
    revision_classes = set(props.get("revision_classes", {}).get("items", {}).get("enum", []))
    if revision_classes != EXPECTED_REVISION_CLASSES:
        errors.append("revision_class_enum_drift")
    narrower_status = set(
        props.get("registered_narrower_alternatives", {})
        .get("items", {})
        .get("properties", {})
        .get("candidate_visible_status", {})
        .get("enum", [])
    )
    if narrower_status != {"UNTESTED", "FAILED", "SUCCEEDED", "CANNOT_CHECK"}:
        errors.append("counterfactual_status_enum_drift")

    # The result ledger is post-outcome and is allowed to advance independently
    # of the immutable protocol/registry.  A1/A2 are now bounded-supported by the
    # protected V2 result and independent reconstruction; A3 must remain unearned.
    a1 = _section(ledger_text, "### A1", "### A2")
    a2 = _section(ledger_text, "### A2", "### A3")
    a3 = _section(ledger_text, "### A3", "## Explicit nonclaims")
    if not a1:
        errors.append("ledger_missing_section:A1")
    elif "State: `SUPPORTED_BOUNDED_" not in a1:
        errors.append("ledger_a1_not_bounded_supported")
    if not a2:
        errors.append("ledger_missing_section:A2")
    elif "State: `SUPPORTED_BOUNDED_" not in a2:
        errors.append("ledger_a2_not_bounded_supported")
    if not a3:
        errors.append("ledger_missing_section:A3")
    elif "State: `CANNOT_CHECK`." not in a3:
        errors.append("ledger_a3_authority_not_cannot_check")
    if "no claim of inherent expressivity" not in ledger_text:
        errors.append("ledger_missing_ideal_product_boundary")

    return tuple(errors)


def load_committed_payloads() -> tuple[str, dict[str, Any], dict[str, Any], str]:
    return (
        PROTOCOL.read_text(),
        json.loads(SCHEMA.read_text()),
        json.loads(REGISTRY.read_text()),
        LEDGER.read_text(),
    )


def main() -> int:
    errors = validate_protocol(*load_committed_payloads())
    if errors:
        for error in errors:
            print(error)
        return 1
    print("P1_X_PROTOCOL_V1_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
