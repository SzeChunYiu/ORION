from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R6 = ROOT / "research" / "claim_expansion" / "p1" / "gpt_r6"
PROTOCOL_PATH = R6 / "REPLICATION_2019_PROTOCOL_V1.json"
AUTHORITY_PATH = R6 / "REPLICATION_2019_MECHANISM_AUTHORITY_V2.json"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def test_mechanism_binding_matches_exact_frozen_substantive_families():
    protocol = _load(PROTOCOL_PATH)
    authority = _load(AUTHORITY_PATH)

    queries = protocol["queries"]
    assert isinstance(queries, list)
    substantive = [q for q in queries if q["class"] != "UNRESOLVED"]
    counts = Counter(q["class"] for q in substantive)

    assert set(authority["protected_adverse_families"]) == set(counts)
    assert counts == {
        "SEARCH_OR_EVIDENCE": 4,
        "REPRESENTATION_OR_INTERFACE": 4,
        "IMPLEMENTATION_OR_ENVIRONMENT": 4,
        "MEASUREMENT_OR_EVALUATOR": 4,
        "OBJECTIVE_OR_MODEL_CLASS": 4,
        "PROBLEM_BOUNDARY": 4,
    }
    assert len(substantive) == protocol["corpus_requirements"]["required_pair_sources"] == 24
    assert len(queries) == protocol["corpus_requirements"]["required_total_sources"] == 28


def test_behavioral_branch_is_literal_adverse_only_difference_without_new_margin():
    authority = _load(AUTHORITY_PATH)
    behavioral = authority["behavioral_branch"]
    family_rule = authority["family_membership_rule"]

    assert behavioral["minimum_different_adverse_episodes_per_passing_family"] == 1
    assert behavioral["new_effect_size_threshold_introduced"] is False
    assert behavioral["family_specific_performance_margin_introduced"] is False
    assert behavioral["controls_can_satisfy_gate"] is False
    assert behavioral["global_only_choice_difference_can_satisfy_gate"] is False
    assert family_rule["adverse_member_only"] is True
    assert family_rule["control_members_do_not_count_toward_mechanism_identification"] is True
    assert family_rule["unresolved_cases_do_not_count_toward_mechanism_identification"] is True


def test_unbound_materiality_cannot_be_posthoc_authority():
    authority = _load(AUTHORITY_PATH)
    material = authority["material_outperformance_branch"]
    terminal = authority["terminal_intersection"]

    assert material["status"] == "UNBOUND_DO_NOT_USE_FOR_2019_AUTHORITY"
    assert material["can_satisfy_mechanism_gate"] is False
    assert terminal["behavioral_mechanism_gate_required_for_positive_replication"] is True
    assert terminal["valid_complete_replication_with_behavioral_gate_false"] == "P1_R6_2019_REPLICATION_NOT_SUPPORTED"
    assert terminal["invalid_or_incomplete_mechanism_evidence"] == "P1_R6_2019_REPLICATION_CANNOT_CHECK"
    assert terminal["positive_terminal_unchanged"] == "P1_R6_2019_REPLICATION_PASS"


def test_mechanism_authority_is_frozen_before_any_2019_result_bearing_step():
    authority = _load(AUTHORITY_PATH)
    order = authority["pre_execution_order"]

    assert order["must_be_merged_before_2019_source_acquisition"] is True
    assert order["must_be_merged_before_2019_corpus_seal"] is True
    assert order["must_be_merged_before_any_2019_candidate_or_comparator_execution"] is True
    assert order["must_be_merged_before_2019_independent_scoring"] is True
    assert order["outcome_aware_operator_may_not_select_rank_or_replace_2019_sources"] is True
    assert order["source_selection_authority_remains_REPLICATION_2019_PROTOCOL_V1"] is True
    assert order["violation_terminal"] == "P1_R6_2019_REPLICATION_CANNOT_CHECK"


def test_inherited_scientific_gates_and_host_are_not_relaxed():
    protocol = _load(PROTOCOL_PATH)
    authority = _load(AUTHORITY_PATH)
    inherited = authority["inherited_replication_v1"]

    assert all(inherited[key] is False for key in (
        "queries_changed",
        "source_rules_changed",
        "source_priority_changed",
        "required_sources_changed",
        "required_episodes_changed",
        "comparator_changed",
        "host_changed",
        "generation_parameters_changed",
        "metrics_changed",
        "bootstrap_changed",
        "margins_changed",
        "safety_tolerances_changed",
        "terminal_names_changed",
    ))
    assert protocol["candidate_and_baselines"]["primary_comparator"] == "B3_HORIZON2_DONOR_COMPLETE"
    assert protocol["changed_host"]["model_id"] == "google/flan-t5-base"
    assert protocol["independent_evaluator"]["bootstrap_replicates"] == 20000
    assert protocol["frozen_outcome_requirements"]["episode_grs_orion_native_ard_minus_b3_at_least"] == 0.10
    assert protocol["frozen_outcome_requirements"]["matched_pair_macro_selectivity_difference_at_least"] == 0.10
    assert protocol["frozen_outcome_requirements"]["domain_and_class_noninferiority_floor"] == -0.10


def test_contract_cannot_retroactively_repair_2020_or_close_p1_u():
    authority = _load(AUTHORITY_PATH)
    chronology = authority["chronology"]
    terminal = authority["terminal_intersection"]

    assert chronology["replication_2019_source_acquisition_performed_by_this_change"] is False
    assert chronology["replication_2019_policy_outcome_accessed_by_this_change"] is False
    assert chronology["replication_2019_gold_accessed_by_this_change"] is False
    assert chronology["can_retroactively_grant_primary_2020_mechanism_authority"] is False
    assert terminal["positive_replication_can_retroactively_relabel_primary_2020_authority"] is False
    assert terminal["positive_replication_self_authorizes_registry_promotion"] is False
    assert terminal["positive_replication_alone_authorizes_issue_649_closure"] is False
    assert authority["issue_723_closure_authorized"] is False
    assert authority["issue_649_closure_authorized"] is False
    assert authority["promotion_authorized"] is False
