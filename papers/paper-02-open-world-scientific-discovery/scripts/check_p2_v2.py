#!/usr/bin/env python3
"""Fail-closed validator for Paper-2 V2 widening artifacts.

This checker validates authority/provenance structure, not scientific outcomes.
A passing result means the widening surface is internally consistent and cannot
promote claims by prose alone.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "protocol"
MANUSCRIPT = ROOT / "manuscript"

EXPECTED_LADDER = [
    "P2_NARROWED",
    "P2_EXTERNAL_MECHANISM_SUPPORTED",
    "P2_EXTERNAL_DISCOVERY_SUPPORTED",
    "P2_OPEN_WORLD_STOPPING_SUPPORTED",
    "P2_TRANSFER_SUPPORTED",
]
EXPECTED_STAGES = {
    "QUERY_DERIVATION", "INDEX_COVERAGE", "CANDIDATE_GENERATION", "RANKING",
    "SCREENING", "IDENTITY", "ROUTE_STOP", "TASK_STOP", "CENSORED", "BUDGET",
    "EVALUATOR", "OTHER",
}
EXPECTED_RESIDUALS = {
    "earned_route_independence",
    "route_local_vs_task_global_authority",
    "unavailable_or_censored_routes_remain_open_obligations",
    "content_identity_separate_from_question_conditioned_read_state",
}
REQUIRED_DONORS = {
    "SAGE", "AgentIR", "SIEVE", "HALT", "MiCP", "DeepControl", "Search-R1"
}


def _load(name: str) -> dict:
    return json.loads((PROTOCOL / name).read_text(encoding="utf-8"))


def validate() -> list[str]:
    errors: list[str] = []
    registry = _load("P2_V2_SYSTEM_REGISTRY.json")
    hostile = _load("P2_V2_HOSTILE_AUTHORITY_CASES.json")
    promotion = _load("P2_V2_PROMOTION_STATE.json")

    if registry.get("status") != "FROZEN_DEVELOPMENT_SURFACE":
        errors.append("system registry is not frozen")
    if registry.get("claim_ladder") != EXPECTED_LADDER:
        errors.append("claim ladder changed or reordered")
    if set(registry.get("failure_stage_enum", [])) != EXPECTED_STAGES:
        errors.append("failure-stage taxonomy drifted")
    if set(registry.get("candidate_orion_residuals", [])) != EXPECTED_RESIDUALS:
        errors.append("ORION residual set drifted")

    invariants = registry.get("promotion_invariants", {})
    if not invariants or not all(invariants.values()):
        errors.append("every promotion invariant must remain true")

    systems = registry.get("development_systems", {})
    max_system = systems.get("ORION_MAX_COMPOSED", [])
    if not max_system:
        errors.append("ORION_MAX_COMPOSED missing")
    for required in (
        "typed_closure_authority",
        "censoring_obligations",
        "earned_route_independence",
        "conformal_coverage_signal_where_task_valid",
    ):
        if required not in max_system:
            errors.append(f"max composed system lost {required}")

    if promotion.get("authorized_terminal") not in EXPECTED_LADDER:
        errors.append("promotion state has unknown authorized terminal")
    if promotion.get("target_terminal") != "P2_TRANSFER_SUPPORTED":
        errors.append("V2 target is no longer maximal transfer support")
    if not promotion.get("confirmatory_external_complete", False):
        if promotion.get("authorized_terminal") != "P2_NARROWED":
            errors.append("external claim promoted before confirmatory completion")
    if promotion.get("development_complete", False) and not promotion.get("current_blockers"):
        errors.append("completed development must still expose any external/transfer blockers")

    cases = hostile.get("cases", [])
    ids = [case.get("id") for case in cases]
    if len(cases) < 12 or len(ids) != len(set(ids)):
        errors.append("hostile suite must contain >=12 uniquely named cases")
    for case in cases:
        if not case.get("forbidden") or not case.get("required"):
            errors.append(f"hostile case incomplete: {case.get('id')}")

    donor_matrix = (PROTOCOL / "P2_V2_DONOR_COMPOSITION_MATRIX_2026-08-17.md").read_text(encoding="utf-8")
    missing_donors = sorted(d for d in REQUIRED_DONORS if d not in donor_matrix)
    if missing_donors:
        errors.append("donor matrix missing: " + ", ".join(missing_donors))
    if "External superiority/transfer language remains gated" not in donor_matrix:
        errors.append("donor matrix lost external-claim gate")

    main = (MANUSCRIPT / "main.tex").read_text(encoding="utf-8")
    authority = (MANUSCRIPT / "sections" / "acquisition_authority.tex").read_text(encoding="utf-8")
    if r"\input{sections/acquisition_authority}" not in main:
        errors.append("main manuscript does not include acquisition-authority section")
    if r"\texttt{CANNOT\_CHECK}" not in main:
        errors.append("manuscript lost explicit CANNOT_CHECK external gate")
    if r"\input{figures/P2-7_acquisition_authority}" not in authority:
        errors.append("authority section does not include P2-7 architecture figure")
    for phrase in (
        "Acquisition is not closure",
        "typed obligation state",
        "cannot by itself delete an unresolved",
        "donor-composable",
        "MiCP",
    ):
        if phrase not in authority:
            errors.append(f"authority section missing concept: {phrase}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"P2_V2_INVALID: {error}")
        return 1
    print("P2_V2_VALID: widening surface is structurally fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
