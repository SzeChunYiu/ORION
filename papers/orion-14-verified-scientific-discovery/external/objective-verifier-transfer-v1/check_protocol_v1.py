#!/usr/bin/env python3
"""Fail-closed design checker for ORION14.OBJECTIVE_VERIFIER_TRANSFER.v1."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PROTOCOL_V1.json"


def binom_pmf(n: int, k: int, p: float) -> float:
    return math.comb(n, k) * (p ** k) * ((1.0 - p) ** (n - k))


def joint_gate_probability(p: float) -> float:
    return sum(
        binom_pmf(10, a, p) * binom_pmf(10, b, p) * binom_pmf(10, c, p)
        for a in range(6, 11)
        for b in range(6, 11)
        for c in range(6, 11)
        if a + b + c >= 21
    )


def validate(p: dict) -> None:
    assert p["schema_version"] == "orion14.objective-verifier-transfer.v1"
    assert p["identity"] == "ORION14.OBJECTIVE_VERIFIER_TRANSFER.v1"
    assert p["status"] == "DESIGN_ONLY__NO_PROTECTED_OUTCOME_AUTHORITY"
    assert p["scientific_authority_delta"] == "NONE"

    history = p["historical_evidence_policy"]
    assert history["scifact_campaign"] == "diagnostic_only__no_governance_gold"
    assert history["internal_campaigns_count_toward_external_confirmatory_n"] is False
    assert history["existing_bounded_authority_preserved"] is True

    classes = p["object_classes"]
    assert [c["id"] for c in classes] == ["DEFECTS4J_EXECUTABLE", "LEAN_KERNEL", "REPRO_WORKFLOW"]
    assert all(c["families"] == 10 for c in classes)

    req = p["family_requirements"]
    assert req["minimum_total_families"] == 30
    assert req["minimum_families_per_class"] == 10
    assert req["at_least_one_protected_valid_object"] is True
    assert req["at_least_one_protected_invalid_object"] is True
    assert req["target_invalid_objects_per_family_min"] >= 2
    assert req["target_external_invalid_objects_total_min"] >= 60
    assert req["oracle_authored_for_orion"] is False
    assert req["organization_duplicates_count_as_independent"] is False

    custody = p["freeze_and_custody"]
    for key in (
        "freeze_family_and_object_ids_before_policy_outputs",
        "freeze_source_hashes_oracle_versions_and_commands",
        "protected_oracle_outcomes_hidden_until_policy_receipts_immutable",
    ):
        assert custody[key] is True
    for key in (
        "post_outcome_object_replacement",
        "post_outcome_threshold_retuning",
        "post_outcome_class_deletion",
        "programme_aggregator_is_gold_source",
    ):
        assert custody[key] is False

    assert [a["id"] for a in p["arms"]] == [
        "B0_CHECKS_ONLY",
        "B1_MATCHED_MULTI_REVIEW",
        "B2_ORION_FULL",
    ]
    parity = p["information_parity"]
    assert parity["same_evidence_bytes"] is True
    assert parity["same_public_metadata"] is True
    assert parity["same_resource_ceiling"] is True
    assert parity["protected_oracle_labels_visible_before_decision"] is False

    assert p["primary_family_order_B2_vs_B1"] == [
        "fewer_severe_false_promotions",
        "more_protected_valid_objects_correctly_retained_if_tied",
        "fewer_unjustified_abstentions_on_valid_objects_if_tied",
        "otherwise_tie",
    ]
    assert p["cost_breaks_primary_tie"] is False

    safety = p["hard_safety_gate"]
    assert safety["B2_severe_false_promotions_max"] == 0
    assert safety["complete_frozen_invalid_set_required"] is True
    assert safety["zero_observed_means_zero_population_rate"] is False
    assert safety["exact_denominator_and_uncertainty_required"] is True
    assert safety["failure_terminal"] == "ADVERSE_EXTERNAL_FALSE_PROMOTION"

    gate = p["family_comparator_gate"]
    assert gate["overall_wins_min"] == 21
    assert gate["overall_families"] == 30
    assert gate["per_class_wins_min"] == 6
    assert gate["per_class_families"] == 10
    assert gate["classes"] == 3
    assert gate["known_positive_and_negative_controls_every_class"] is True
    assert gate["unresolved_custody_or_parity_blocker_allowed"] is False
    assert abs(gate["fair_coin_joint_null_probability"] - joint_gate_probability(0.5)) < 1e-15
    assert abs(gate["power_at_independent_family_win_probability_0_8"] - joint_gate_probability(0.8)) < 1e-15

    natural = p["natural_negative_policy"]
    assert natural["planted_controls_count_as_primary_external_negatives"] is False
    assert natural["natural_or_source_authored_invalids_required"] is True

    boundary = p["construct_boundary"]
    assert boundary["workflow_schema_or_checksum_only_counts_as_scientific_validity"] is False
    assert boundary["workflow_scientific_endpoint_requires_named_result_or_invariant_recomputation"] is True
    assert boundary["broad_scientific_truth_claimed"] is False
    assert boundary["institutional_authority_claimed"] is False

    assert p["inference_unit"] == "family"
    assert p["within_family_objects_are_independent_replicates"] is False
    assert {
        "OBJECTIVE_VERIFIER_EXTERNAL_TRANSFER_SUPPORT",
        "NO_EXTERNAL_COMPARATOR_ADVANTAGE",
        "ADVERSE_EXTERNAL_FALSE_PROMOTION",
        "CANNOT_CHECK_INSUFFICIENT_EXTERNAL_FAMILIES",
        "CANNOT_CHECK_INFORMATION_PARITY",
        "CANNOT_CHECK_EXTERNAL_ORACLE_CUSTODY",
        "CANNOT_CHECK_NO_NATURAL_EXTERNAL_NEGATIVES",
        "CANNOT_CHECK_WORKFLOW_SCIENTIFIC_ENDPOINT",
    } <= set(p["terminals"])


def expect_reject(base: dict, mutate) -> None:
    candidate = copy.deepcopy(base)
    mutate(candidate)
    try:
        validate(candidate)
    except (AssertionError, KeyError, TypeError):
        return
    raise AssertionError("hostile protocol mutation accepted")


def main() -> None:
    p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    validate(p)
    mutations = [
        lambda x: x["historical_evidence_policy"].__setitem__("internal_campaigns_count_toward_external_confirmatory_n", True),
        lambda x: x["family_requirements"].__setitem__("oracle_authored_for_orion", True),
        lambda x: x["family_requirements"].__setitem__("organization_duplicates_count_as_independent", True),
        lambda x: x["freeze_and_custody"].__setitem__("protected_oracle_outcomes_hidden_until_policy_receipts_immutable", False),
        lambda x: x["freeze_and_custody"].__setitem__("post_outcome_object_replacement", True),
        lambda x: x["hard_safety_gate"].__setitem__("B2_severe_false_promotions_max", 1),
        lambda x: x["family_comparator_gate"].__setitem__("overall_wins_min", 20),
        lambda x: x["natural_negative_policy"].__setitem__("planted_controls_count_as_primary_external_negatives", True),
        lambda x: x["construct_boundary"].__setitem__("workflow_schema_or_checksum_only_counts_as_scientific_validity", True),
        lambda x: x.__setitem__("inference_unit", "object"),
        lambda x: x.__setitem__("cost_breaks_primary_tie", True),
    ]
    for mutation in mutations:
        expect_reject(p, mutation)

    print(
        "ORION14_OBJECTIVE_VERIFIER_TRANSFER_V1_PASS "
        f"null={joint_gate_probability(0.5):.17f} "
        f"power_p80={joint_gate_probability(0.8):.16f} "
        f"hostile_mutations={len(mutations)} outcomes_accessed=NONE"
    )


if __name__ == "__main__":
    main()
