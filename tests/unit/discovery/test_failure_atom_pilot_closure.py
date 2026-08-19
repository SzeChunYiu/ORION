from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path

from orion.discovery.failure_atom_pilot_closure import (
    F1Recommendation,
    F2Recommendation,
    F3Recommendation,
    NegativeApplicability,
    TransportWitnessKind,
    assess_f3_transport,
    build_failure_atom_pilot_closure_report,
    f1_indistinguishability_pairs,
    f2_parent_mappings,
    f3_transport_cases,
)
from orion.transfer.v2.failure_knowledge import (
    FailureApplicabilityStatus,
    FailureKnowledge,
    assess_failure_applicability,
    build_failure_knowledge,
)


ROOT = Path(__file__).resolve().parents[3]
EXPECTED = (
    ROOT
    / "research"
    / "extensions"
    / "orion-jump-recursive-atoms"
    / "FAILURE_ATOM_PILOT_EXPECTED_V1.json"
)


def test_failure_atom_pilot_matches_pre_frozen_counts_and_terminals() -> None:
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    report = build_failure_atom_pilot_closure_report()

    assert report.f1_pair_count == expected["f1"]["indistinguishability_pairs"]
    assert report.f1_recommendation.value == expected["f1"]["candidate_terminal"]
    assert report.f1_recommendation is F1Recommendation.MULTIPLE_FAILURE_SIGNAL_ATOMS_REQUIRED
    assert report.f1_all_pairs_split_protected_materiality is True
    assert report.f1_public_only_universal_detector_possible is False

    assert report.f2_parent_mapping_count == expected["f2"]["parent_mapping_rows"]
    assert report.f2_recommendation.value == expected["f2"]["candidate_terminal"]
    assert report.f2_recommendation is F2Recommendation.TMS_NOGOOD_PLUS_RESPONSIBILITY_SUFFICIENT
    assert report.f2_unmapped_fields == ()
    assert report.f2_new_primitive_fields == ()

    assert report.f3_transport_case_count == expected["f3"]["transport_cases"]
    assert report.f3_recommendation.value == expected["f3"]["candidate_terminal"]
    assert report.f3_recommendation is F3Recommendation.P7_TRANSPORT_SUFFICIENT
    assert report.f3_mismatched_cases == ()
    assert report.f3_semantic_transport_delegated_to_p7 is True

    assert report.all_checks_passed is True
    assert report.grants_scientific_authority is False
    assert report.grants_novelty_authority is False
    assert report.grants_issue_closure_authority is False
    assert expected["authority"] == {
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_issue_closure_authority": False,
    }


def test_f1_pairs_are_publicly_indistinguishable_but_require_distinct_semantic_sources() -> None:
    pairs = f1_indistinguishability_pairs()

    assert len({pair.pair_id for pair in pairs}) == len(pairs)
    assert len({pair.specialized_discriminator_id for pair in pairs}) == len(pairs)
    for pair in pairs:
        pair.verify()
        assert pair.world_a_materiality is not pair.world_b_materiality
        assert pair.public_observable_ids


def test_f2_parent_mapping_covers_every_failure_knowledge_field_except_digest() -> None:
    mapped = {row.field_name for row in f2_parent_mappings()}
    actual = {field.name for field in fields(FailureKnowledge)} - {"digest"}

    assert mapped == actual
    assert all(row.new_orion_primitive_required is False for row in f2_parent_mappings())


def test_f3_complete_transport_can_preserve_across_surface_change() -> None:
    semantic_rename = next(
        case
        for case in f3_transport_cases()
        if case.case_id == "semantic-preserving-rename-or-refactor"
    )

    assert semantic_rename.surface_context_changed is True
    assert semantic_rename.witness_kind is TransportWitnessKind.COMPLETE
    assert assess_f3_transport(semantic_rename) is NegativeApplicability.APPLIES


def test_failure_knowledge_v1_context_rule_is_a_conservative_fast_path_not_semantic_transport() -> None:
    failure = build_failure_knowledge(
        failure_id="failure-1",
        target_contract_id="contract-1",
        regime_id="regime-1",
        attempted_trace_ids=("attempt-1",),
        observed_failure_id="observed-1",
        responsibility_state_id="responsibility-1",
        excluded_condition_ids=("condition-1",),
        frozen_context={"representation": "chart-a", "measurement": "sensor-a"},
        evidence_ids=("evidence-1",),
        authority_owner_id="authority-1",
        required_same_coordinates=("measurement",),
        reopen_on_change_coordinates=("representation",),
    )

    unchanged = assess_failure_applicability(
        failure,
        current_context={"representation": "chart-a", "measurement": "sensor-a"},
    )
    renamed = assess_failure_applicability(
        failure,
        current_context={"representation": "chart-a-renamed", "measurement": "sensor-a"},
    )

    assert unchanged.status is FailureApplicabilityStatus.APPLIES
    assert renamed.status is FailureApplicabilityStatus.REOPENED
    assert renamed.applicable_excluded_condition_ids == ()

    # A complete P7 transport witness can later prove that a semantic-preserving
    # rename/refactor still carries the old negative conclusion.  V1 is safe to
    # reopen on the raw coordinate change; it is not the final semantic calculus.
    semantic_rename = next(
        case
        for case in f3_transport_cases()
        if case.case_id == "semantic-preserving-rename-or-refactor"
    )
    assert assess_f3_transport(semantic_rename) is NegativeApplicability.APPLIES
