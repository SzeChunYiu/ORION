from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path

from orion.discovery.recursive_atom_calculus_closure import (
    AtomStudyDisposition,
    NegativeHistoryCategory,
    RecursionStopReason,
    RecursiveAtomCalculusTerminal,
    build_recursive_atom_calculus_closure_report,
    classify_interaction_witness,
    interaction_witness_cases,
    post_map_saturation_rounds,
)
from orion.transfer.v2.bounded_epistemic_study import (
    BoundedEpistemicAtomStudy,
    analyze_contract_interaction,
)


ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "extensions" / "orion-jump-recursive-atoms"
OWNERSHIP_MAP = RESEARCH / "ATOM_OWNERSHIP_MAP_V1.json"
EXPECTED = RESEARCH / "RECURSIVE_ATOM_CALCULUS_EXPECTED_V1.json"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_recursive_atom_calculus_matches_frozen_plus_hostile_amended_expectations() -> None:
    ownership = _load(OWNERSHIP_MAP)
    expected = _load(EXPECTED)
    report = build_recursive_atom_calculus_closure_report(ownership)

    assert report.candidate_coordinate_count == expected["ownership_map"][
        "candidate_coordinates"
    ]
    assert report.candidate_transformation_count == expected["ownership_map"][
        "candidate_transformations"
    ]
    assert report.existing_owner_count == expected["ownership_map"][
        "existing_orion_owners"
    ]
    assert report.generic_new_atoms_claimed == expected["ownership_map"][
        "generic_new_atoms_claimed"
    ]
    assert report.ownership_missing_rows == ()

    assert report.post_map_round_count == expected["post_map_saturation"]["rounds"]
    assert report.post_map_material_change_round_ids == ()
    assert expected["post_map_saturation"]["round_1_material_change"] is False
    assert expected["post_map_saturation"]["round_2_material_change"] is False

    assert report.common_result_disposition_count == expected["protocol"][
        "common_result_dispositions"
    ]
    assert report.recursion_stop_reason_count == expected["protocol"][
        "recursion_stop_reasons"
    ]
    assert report.negative_history_category_count == expected["protocol"][
        "negative_history_categories"
    ]
    assert report.interaction_witness_count == expected["protocol"][
        "interaction_witness_cases"
    ] == 5
    assert report.interaction_mismatched_case_ids == ()

    assert report.terminal.value == expected["candidate_terminal"]
    assert report.terminal is RecursiveAtomCalculusTerminal.RECURSIVE_ATOM_STUDY_CALCULUS_FROZEN
    assert report.all_checks_passed is True
    assert report.grants_scientific_atom_authority is False
    assert report.grants_jump_authority is False
    assert report.grants_novelty_authority is False
    assert report.grants_issue_closure_authority is False


def test_common_packet_has_decomposition_interaction_stop_and_no_atom_coordinates() -> None:
    names = {field.name for field in fields(BoundedEpistemicAtomStudy)}

    assert {
        "positive_case_ids",
        "no_atom_control_ids",
        "parent_baseline_ids",
        "decomposition_hypotheses",
        "interaction_hypotheses",
        "recursion_stop_rules",
        "evaluator_id",
        "authority_owner_id",
        "protected_field_ids",
        "outcome_accessed",
    } <= names


def test_interaction_protocol_distinguishes_five_registered_dispositions() -> None:
    actual = {
        case.case_id: classify_interaction_witness(case)
        for case in interaction_witness_cases()
    }

    assert actual == {
        "independent-left-effect": AtomStudyDisposition.ATOM_INCREMENTAL_VALUE,
        "interaction-only-synergy": AtomStudyDisposition.INTERACTION_ONLY,
        "redundant-equivalent-children": AtomStudyDisposition.REDUNDANT_EQUIVALENT,
        "shared-standalone-value-lossy-combination": AtomStudyDisposition.OVERREACH_HARMFUL,
        "observationally-non-identifiable-children": AtomStudyDisposition.NON_IDENTIFIABLE,
    }


def test_shared_standalone_value_with_lossy_combination_is_not_no_incremental_value() -> None:
    case = next(
        item
        for item in interaction_witness_cases()
        if item.case_id == "shared-standalone-value-lossy-combination"
    )
    report = analyze_contract_interaction(
        left_atom_id=case.left_atom_id,
        right_atom_id=case.right_atom_id,
        left_reachable_contract_ids=case.left_delta_contract_ids,
        right_reachable_contract_ids=case.right_delta_contract_ids,
        combined_reachable_contract_ids=case.combined_delta_contract_ids,
    )

    assert report.shared_individual_contract_ids == ("shared-a", "shared-b")
    assert report.lost_in_combination_contract_ids == ("shared-b",)
    assert report.left_only_contract_ids == ()
    assert report.right_only_contract_ids == ()
    assert classify_interaction_witness(case) is AtomStudyDisposition.OVERREACH_HARMFUL


def test_post_map_rounds_only_reinforce_frozen_ownership_families() -> None:
    ownership = _load(OWNERSHIP_MAP)
    known_ids = {
        row["id"] for row in ownership["candidate_coordinates"]
    } | {
        row["id"] for row in ownership["candidate_transformations"]
    }

    assert len(post_map_saturation_rounds()) == 2
    for round_record in post_map_saturation_rounds():
        round_record.verify()
        assert round_record.material_change is False
        assert set(round_record.mapped_family_ids) <= known_ids


def test_ownership_map_does_not_self_promote_candidate_coordinates() -> None:
    ownership = _load(OWNERSHIP_MAP)

    assert ownership["generic_new_atoms_claimed"] == 0
    assert all(
        row["generic_orion_atom_claim"] is False
        for row in ownership["candidate_coordinates"]
    )


def test_common_vocabulary_preserves_fail_closed_and_negative_outcomes() -> None:
    assert {
        AtomStudyDisposition.SUBSUMED,
        AtomStudyDisposition.INTERACTION_ONLY,
        AtomStudyDisposition.NON_IDENTIFIABLE,
        AtomStudyDisposition.NO_INCREMENTAL_VALUE,
        AtomStudyDisposition.CANNOT_CHECK,
        AtomStudyDisposition.OVERREACH_HARMFUL,
    } <= set(AtomStudyDisposition)
    assert len(tuple(AtomStudyDisposition)) == 10
    assert len(tuple(RecursionStopReason)) == 7
    assert len(tuple(NegativeHistoryCategory)) == 8
    assert NegativeHistoryCategory.DONOR_SUBSUMPTION in NegativeHistoryCategory
    assert NegativeHistoryCategory.UNRESOLVED_OR_NON_IDENTIFIABLE in NegativeHistoryCategory
