#!/usr/bin/env python3
"""Fail-closed design checker for ORION11.OBJECTIVE_TASK_TRANSFER.v1."""
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
    total = 0.0
    for a in range(6, 11):
        for b in range(6, 11):
            for c in range(6, 11):
                if a + b + c >= 21:
                    total += binom_pmf(10, a, p) * binom_pmf(10, b, p) * binom_pmf(10, c, p)
    return total


def validate(p: dict) -> None:
    assert p["schema_version"] == "orion11.objective-task-transfer.v1"
    assert p["identity"] == "ORION11.OBJECTIVE_TASK_TRANSFER.v1"
    assert p["status"] == "DESIGN_ONLY__NO_PROTECTED_OUTCOME_AUTHORITY"
    assert p["scientific_authority_delta"] == "NONE"

    history = p["historical_evidence_policy"]
    assert history["old_2880_records"] == "instrument_validation_only"
    assert history["faithful_comparator_negative_history_retained"] is True
    assert history["historical_records_count_toward_confirmatory_n"] is False

    domains = p["domains"]
    assert [d["id"] for d in domains] == ["DEFECTS4J", "LEAN", "REPRO_WORKFLOW"]
    assert all(d["families"] == 10 for d in domains)
    assert p["minimum_total_families"] == 30

    freeze = p["candidate_freeze"]
    assert freeze["before_arm_execution"] is True
    assert freeze["post_outcome_replacement"] is False
    assert freeze["organization_duplicates_count_as_independent_families"] is False
    assert len(p["required_transition_fields"]) >= 5

    arms = p["arms"]
    assert [a["id"] for a in arms] == [
        "A0_STALE_STATE",
        "A1_MATCHED_RANDOM_MUTATION",
        "A2_TARGETED_MUTATION",
        "A3_GLOBAL_RESET",
    ]
    a1 = arms[1]
    assert a1["must_match_A2_mutation_count_and_type"] is True
    assert a1["must_ignore_dependency_impact"] is True

    parity = p["information_parity"]
    for key in (
        "same_task_bytes",
        "same_change_bytes",
        "same_declared_dependency_information",
        "same_verifier_interface_description",
        "same_resource_ceiling",
    ):
        assert parity[key] is True
    assert parity["gold_dependency_labels_for_A2"] is False
    assert parity["gold_leak_terminal"] == "CANNOT_CHECK_INFORMATION_PARITY"

    assert p["inference_unit"] == "family"
    assert p["within_family_transitions_are_independent_replicates"] is False
    assert p["cost_breaks_primary_A2_vs_A1_tie"] is False
    assert p["A2_vs_A1_lexicographic_order"] == [
        "fewer_unsafe_acceptances",
        "more_objectively_correct_recoveries_if_tied",
        "fewer_protected_invariant_violations_if_tied",
        "otherwise_tie",
    ]

    a3 = p["A2_vs_A3"]
    assert a3["requires_correctness_noninferiority"] is True
    assert a3["requires_strictly_less_median_realized_work"] is True
    assert a3["noninferiority_margin_frozen_per_domain_before_outcomes"] is True
    assert a3["work_metric_frozen_per_domain_before_outcomes"] is True

    gate = p["promotion_gate"]
    assert gate["overall_family_wins_min"] == 21
    assert gate["overall_families"] == 30
    assert gate["per_domain_wins_min"] == 6
    assert gate["per_domain_families"] == 10
    assert gate["domains"] == 3
    assert gate["known_negative_controls_must_fire"] is True
    assert gate["A2_vs_A3_gate_must_pass_every_domain"] is True
    assert gate["unresolved_information_or_oracle_custody_blocker_allowed"] is False
    assert abs(gate["fair_coin_joint_null_probability"] - joint_gate_probability(0.5)) < 1e-15
    assert abs(gate["power_at_independent_family_win_probability_0_8"] - joint_gate_probability(0.8)) < 1e-15

    assert len(p["adverse_outcomes_retained"]) >= 5
    assert {
        "OBJECTIVE_MULTI_FAMILY_TARGETING_SUPPORT",
        "NO_TARGETING_ADVANTAGE",
        "CANNOT_CHECK_INSUFFICIENT_INDEPENDENT_FAMILIES",
        "CANNOT_CHECK_INFORMATION_PARITY",
        "CANNOT_CHECK_EXTERNAL_ORACLE",
        "ADVERSE_GLOBAL_RESET_CORRECTNESS_SUPERIOR",
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
        lambda x: x["historical_evidence_policy"].__setitem__("historical_records_count_toward_confirmatory_n", True),
        lambda x: x["candidate_freeze"].__setitem__("post_outcome_replacement", True),
        lambda x: x["candidate_freeze"].__setitem__("organization_duplicates_count_as_independent_families", True),
        lambda x: x["arms"][1].__setitem__("must_match_A2_mutation_count_and_type", False),
        lambda x: x["information_parity"].__setitem__("gold_dependency_labels_for_A2", True),
        lambda x: x.__setitem__("inference_unit", "transition"),
        lambda x: x.__setitem__("cost_breaks_primary_A2_vs_A1_tie", True),
        lambda x: x["promotion_gate"].__setitem__("overall_family_wins_min", 20),
        lambda x: x["promotion_gate"].__setitem__("per_domain_wins_min", 5),
        lambda x: x["A2_vs_A3"].__setitem__("requires_correctness_noninferiority", False),
    ]
    for mutation in mutations:
        expect_reject(p, mutation)

    print(
        "ORION11_OBJECTIVE_TASK_TRANSFER_V1_PASS "
        f"null={joint_gate_probability(0.5):.17f} "
        f"power_p80={joint_gate_probability(0.8):.16f} "
        f"hostile_mutations={len(mutations)} outcomes_accessed=NONE"
    )


if __name__ == "__main__":
    main()
