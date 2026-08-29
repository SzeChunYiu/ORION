#!/usr/bin/env python3
"""Fail-closed design/algebra checker for ORION03.NATIVE_TYPED_MERGE_TRANSFER.v1."""
from __future__ import annotations

import copy
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PROTOCOL_V1.json"


def validate(p: dict) -> None:
    assert p["schema_version"] == "orion03.native-typed-merge-transfer.v1"
    assert p["identity"] == "ORION03.NATIVE_TYPED_MERGE_TRANSFER.v1"
    assert p["status"] == "DESIGN_ONLY__NO_NATIVE_OUTCOME_AUTHORITY"
    assert p["scientific_authority_delta"] == "NONE"
    assert p["typed_parent_witness_is_empirical_detector"] is False

    systems = p["systems"]
    assert [s["id"] for s in systems] == ["SIGSTORE_COSIGN", "TUF_PYTHON_TUF", "IN_TOTO"]
    assert all(s["families"] == 10 for s in systems)
    assert p["confirmatory_family_total"] == 30
    assert p["synthetic_controls_count_toward_confirmatory_n"] is False

    d = p["common_decisions"]
    assert d["V_T"] == "V_A_or_V_B"
    assert d["hybrid"] == "V_U_and_not_V_A_and_not_V_B"

    union = p["flat_union"]
    assert union["frozen_before_protected_verification"] is True
    assert union["only_native_consumed_typed_components"] is True
    assert union["may_weaken_threshold_without_registered_native_union_semantics"] is False
    assert union["may_delete_rules_without_registered_native_union_semantics"] is False
    assert len(union["required_receipts"]) >= 5
    assert union["no_semantic_union_terminal"] == "CANNOT_CHECK_NO_NATIVE_FLAT_UNION"

    freeze = p["candidate_freeze"]
    assert freeze["minimum_candidates_per_family"] >= 20
    assert freeze["target_candidates_per_system_min"] >= 200
    assert freeze["target_candidates_overall_min"] >= 600
    assert freeze["generator_frozen_before_native_parent_or_union_outcomes"] is True
    assert freeze["post_outcome_candidate_replacement"] is False
    assert len(freeze["required_candidate_kinds"]) >= 4

    loc = p["hybrid_localization"]
    assert loc["requires_load_bearing_contribution_from_A"] is True
    assert loc["requires_load_bearing_contribution_from_B"] is True
    assert loc["ablate_each_claimed_contribution_with_native_reverification"] is True

    assert p["inference_unit"] == "family"
    assert p["candidate_tasks_are_independent_replicates"] is False

    gate = p["cross_system_support_gate"]
    assert gate["hybrid_families_min_per_system"] == 3
    assert gate["families_per_system"] == 10
    assert gate["all_three_systems_required"] is True
    assert gate["localized_hybrid_min_per_system"] >= 1
    assert gate["source_binding_and_verifier_drift_allowed"] is False
    assert gate["malformed_controls_must_reject"] is True
    assert gate["post_outcome_family_or_candidate_deletion"] is False
    assert gate["three_of_ten_is_significance_test"] is False

    utility = p["strict_baseline_utility_gate"]
    assert utility["needless_rejection_families_min_per_supporting_system"] == 3
    assert utility["requires_parent_authorized_objects"] is True
    assert utility["cost_can_substitute_for_native_authorization_loss"] is False

    assert {
        "NATIVE_CROSS_SYSTEM_HYBRID_NONVACUITY_SUPPORTED",
        "BOUNDED_SYSTEM_SPECIFIC_HYBRID_SUPPORT",
        "NO_NATIVE_HYBRID_OBSERVED",
        "CANNOT_CHECK_NO_NATIVE_FLAT_UNION",
        "CANNOT_CHECK_LOCALIZATION",
        "ADVERSE_CONTROL_FAILURE",
    } <= set(p["terminals"])


def expect_reject(base: dict, mutate) -> None:
    candidate = copy.deepcopy(base)
    mutate(candidate)
    try:
        validate(candidate)
    except (AssertionError, KeyError, TypeError):
        return
    raise AssertionError("hostile protocol mutation accepted")


def algebra_regression() -> int:
    checks = 0
    # Exhaust all possible native Boolean decisions.  V_T is the parent-union
    # analytic target; a hybrid is by definition disjoint from it.
    for va, vb, vu in itertools.product((False, True), repeat=3):
        vt = va or vb
        hybrid = vu and not va and not vb
        assert not (hybrid and vt)
        assert vt == (va or vb)
        if hybrid:
            assert vu and not va and not vb
        checks += 1
    return checks


def main() -> None:
    p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    validate(p)
    algebra_checks = algebra_regression()
    mutations = [
        lambda x: x.__setitem__("typed_parent_witness_is_empirical_detector", True),
        lambda x: x.__setitem__("synthetic_controls_count_toward_confirmatory_n", True),
        lambda x: x["flat_union"].__setitem__("frozen_before_protected_verification", False),
        lambda x: x["flat_union"].__setitem__("may_weaken_threshold_without_registered_native_union_semantics", True),
        lambda x: x["candidate_freeze"].__setitem__("post_outcome_candidate_replacement", True),
        lambda x: x["candidate_freeze"].__setitem__("minimum_candidates_per_family", 5),
        lambda x: x["hybrid_localization"].__setitem__("requires_load_bearing_contribution_from_B", False),
        lambda x: x.__setitem__("inference_unit", "candidate_task"),
        lambda x: x["cross_system_support_gate"].__setitem__("all_three_systems_required", False),
        lambda x: x["strict_baseline_utility_gate"].__setitem__("cost_can_substitute_for_native_authorization_loss", True),
    ]
    for mutation in mutations:
        expect_reject(p, mutation)

    print(
        "ORION03_NATIVE_TYPED_MERGE_TRANSFER_V1_PASS "
        f"boolean_identity_checks={algebra_checks} hostile_mutations={len(mutations)} "
        "native_outcomes_accessed=NONE"
    )


if __name__ == "__main__":
    main()
