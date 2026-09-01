#!/usr/bin/env python3
"""Fail-closed check for A4's external benchmark preflight.

A preflight may complete by finding a blocker.  What it may not do is convert a
public headline count into an executable confirmatory denominator while the
licensed task manifest and runner lock are unavailable.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
P = HERE / "PREFLIGHT_V1.json"


def main() -> int:
    p = json.loads(P.read_text(encoding="utf-8"))
    primary = p["primary_proposed_substrate"]
    alt = p["equivalent_external_candidate"]
    broad = p["broad_claim_gate"]
    checks = {
        "schema": p["schema"] == "ORION.A4.HiddenCauseExternalBenchmarkPreflight.v1",
        "outcome_blind": (
            p["protected_agent_runs_executed"] is False
            and p["protected_outcomes_accessed"] is False
        ),
        "no_subset_selected": p["confirmatory_subset_selected"] is False,
        "all_preflight_dimensions_present": set(p["preflight_dimensions"]) == {
            "licence", "dataset", "tools", "executable_tasks"
        },
        "primary_repo_license_gap_preserved": (
            primary["code_repository"]["root_listing_checked"] is True
            and primary["code_repository"]["root_license_file_present"] is False
            and primary["code_repository"]["license_terminal"].startswith("CANNOT_CHECK")
        ),
        "primary_dataset_gate_preserved": (
            primary["official_dataset"]["access"] == "GATED"
            and primary["official_dataset"]["file_manifest_available_to_this_preflight"] is False
            and primary["preflight_terminal"] == "NOT_SELECTABLE_FOR_CONFIRMATORY_SUBSET_YET"
        ),
        "alternative_has_nominal_scope": (
            alt["license"] == "CC-BY-4.0"
            and alt["advertised_task_count"] >= 120
            and len(alt["advertised_scientific_domain_families_at_least"]) >= 4
        ),
        "alternative_access_blocker_preserved": (
            alt["access"] == "GATED_CONTACT_INFO_AGREEMENT"
            and alt["file_manifest_available_to_this_preflight"] is False
            and alt["executable_in_current_preflight_environment"] is False
            and alt["terminal"].startswith("CANNOT_CHECK")
        ),
        "no_public_count_laundering": (
            broad["nominal_public_scope_is_large_enough"] is True
            and broad["eligible_executable_task_count_verified"] is False
            and broad["eligible_domain_count_verified_from_task_manifest"] is False
            and broad["must_not_claim_requirement_satisfied"] is True
        ),
        "preflight_completed_with_blocker": (
            p["preflight_decision"] == "COMPLETE__BLOCKER_FOUND__NO_CONFIRMATORY_SUBSET_SELECTED"
        ),
        "no_authority_delta": p["scientific_authority_delta"] == "NONE",
    }
    good = all(checks.values())
    print(json.dumps({"decision": "GREEN" if good else "REJECT", "checks": checks},
                     indent=2, sort_keys=True))
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
