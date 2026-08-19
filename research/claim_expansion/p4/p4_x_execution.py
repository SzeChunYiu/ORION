from __future__ import annotations

from typing import Any

HARD_BLOCK = (
    "claim_supported",
    "provenance_valid",
    "checker_admissible",
    "evaluator_custody_valid",
    "artifact_version_match",
    "claim_scope_match",
)
HARD_UNRESOLVED = (
    "epoch_fresh",
    "evidence_independence_valid",
    "scientific_obligation_resolved",
)


def p4x_decision(case: dict[str, Any]) -> str:
    x = case["candidate_visible"]
    if any(not x[k] for k in HARD_BLOCK):
        return "BLOCK"
    if any(not x[k] for k in HARD_UNRESOLVED):
        return "CANNOT_CHECK"
    return "PROMOTE"


def b1_generic_authorization_product(case: dict[str, Any]) -> str:
    """Strong generic product; intentionally lacks only the disputed promotion relation."""
    x = case["candidate_visible"]
    if not x["claim_supported"]:
        return "BLOCK"
    if not x["provenance_valid"]:
        return "BLOCK"
    if not x["checker_admissible"]:
        return "BLOCK"
    if not x["evaluator_custody_valid"]:
        return "BLOCK"
    if not x["artifact_version_match"]:
        return "BLOCK"
    if not x["epoch_fresh"]:
        return "CANNOT_CHECK"
    if not x["action_authorized"]:
        return "BLOCK"
    # Generic authorization can inspect but does not bind claim scope,
    # evidence dependence, or unresolved scientific-promotion obligation
    # as separate terminal authority coordinates.
    return "PROMOTE"


def b2_compensatory_product(case: dict[str, Any]) -> str:
    x = case["candidate_visible"]
    keys = (
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
    score = sum(1.0 if x[k] else 0.0 for k in keys) / len(keys)
    score = 0.9 * score + 0.1 * float(x["soft_confidence"])
    return "PROMOTE" if score >= 0.80 else "BLOCK"


def b3_ideal_typed_product(case: dict[str, Any]) -> str:
    return p4x_decision(case)


def run_arms(case: dict[str, Any]) -> dict[str, str]:
    return {
        "P4_X": p4x_decision(case),
        "B1_GENERIC_AUTHORIZATION_PRODUCT": b1_generic_authorization_product(case),
        "B2_COMPENSATORY_PRODUCT": b2_compensatory_product(case),
        "B3_IDEAL_TYPED_PRODUCT": b3_ideal_typed_product(case),
    }
