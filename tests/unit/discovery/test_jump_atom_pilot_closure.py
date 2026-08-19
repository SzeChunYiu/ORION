from __future__ import annotations

import json
from pathlib import Path

from orion.discovery.concept_candidate import build_concept_candidate
from orion.discovery.jump_atom_pilot_closure import (
    J1Recommendation,
    J2Operation,
    J2Recommendation,
    J3Recommendation,
    J3Transformation,
    build_jump_atom_pilot_closure_report,
    j1_opportunity_pairs,
    j2_operation_cases,
    j3_transformation_cases,
    reachable_j2_contracts,
    reachable_j3_contracts,
)
from orion.discovery.thought_experiment import ExecutionMode, build_thought_experiment


ROOT = Path(__file__).resolve().parents[3]
EXPECTED = (
    ROOT
    / "research"
    / "extensions"
    / "orion-jump-recursive-atoms"
    / "JUMP_ATOM_PILOT_EXPECTED_V1.json"
)


def test_jump_atom_pilot_matches_pre_frozen_counts_and_terminals() -> None:
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    report = build_jump_atom_pilot_closure_report()

    assert report.j1_pair_count == expected["j1"]["matched_opportunity_pairs"]
    assert report.j1_recommendation.value == expected["j1"]["candidate_terminal"]
    assert report.j1_recommendation is J1Recommendation.MULTIPLE_TENSION_ATOMS_REQUIRED
    assert report.j1_all_pairs_split_materiality is True
    assert report.j1_distinct_witness_family_count == 4
    assert report.j1_public_only_universal_signal_possible is False

    assert report.j2_operation_case_count == expected["j2"]["operation_cases"]
    assert report.j2_special_operator_case_count == expected["j2"]["special_operator_cases"]
    assert report.j2_recommendation.value == expected["j2"]["candidate_terminal"]
    assert report.j2_recommendation is J2Recommendation.MULTIPLE_IMAGINATION_ATOMS_REQUIRED
    assert report.j2_ordinary_intervention_control_preserved is True
    assert set(report.j2_independently_load_bearing_operations) == {
        operation.value for operation in J2Operation
    }

    assert report.j3_transformation_case_count == expected["j3"]["transformation_cases"]
    assert report.j3_recommendation.value == expected["j3"]["candidate_terminal"]
    assert report.j3_recommendation is J3Recommendation.MULTIPLE_CONCEPT_ATOMS_REQUIRED
    assert set(report.j3_independently_load_bearing_transformations) == {
        transformation.value for transformation in J3Transformation
    }

    assert report.all_checks_passed is True
    assert report.grants_scientific_authority is False
    assert report.grants_novelty_authority is False
    assert report.grants_adoption_authority is False
    assert report.grants_issue_closure_authority is False
    assert expected["authority"] == {
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_adoption_authority": False,
        "grants_issue_closure_authority": False,
    }


def test_j1_pairs_require_distinct_external_structural_witness_families() -> None:
    pairs = j1_opportunity_pairs()

    assert len({pair.pair_id for pair in pairs}) == len(pairs)
    assert len({pair.separating_witness_family for pair in pairs}) == len(pairs)
    for pair in pairs:
        pair.verify()
        assert pair.material_world is not pair.control_world
        assert pair.public_observable_ids


def test_j2_each_operation_has_an_independent_reach_effect() -> None:
    all_operations = tuple(J2Operation)
    all_reach = set(reachable_j2_contracts(all_operations))

    assert len(j2_operation_cases()) == len(all_operations)
    for operation in all_operations:
        without = tuple(item for item in all_operations if item is not operation)
        lost = all_reach - set(reachable_j2_contracts(without))
        assert lost, operation.value


def test_j2_retains_ordinary_experiment_design_as_a_no_special_operator_control() -> None:
    ordinary = next(
        case
        for case in j2_operation_cases()
        if case.case_id == "ordinary-intervention-sufficient-control"
    )

    assert ordinary.special_thought_operation is False
    assert ordinary.required_operations == (J2Operation.DIRECT_INTERVENTION,)

    proposal = build_thought_experiment(
        experiment_id="ordinary-control",
        tension_digest="tension-digest",
        operation_kind=ordinary.required_operations[0].value,
        hypothetical_setup_id="physical-intervention",
        expected_outcomes={"h1": ("left",), "h2": ("right",)},
        execution_mode=ExecutionMode.PHYSICAL,
        cost=1.0,
    )
    assert proposal.operation_kind == J2Operation.DIRECT_INTERVENTION.value
    assert proposal.grants_theory_authority is False


def test_j3_each_transformation_has_an_independent_reach_effect_and_parent() -> None:
    all_transformations = tuple(J3Transformation)
    all_reach = set(reachable_j3_contracts(all_transformations))
    cases = j3_transformation_cases()

    assert len(cases) == len(all_transformations)
    assert len({case.parent_family for case in cases}) == len(cases)
    for transformation in all_transformations:
        without = tuple(item for item in all_transformations if item is not transformation)
        lost = all_reach - set(reachable_j3_contracts(without))
        assert lost, transformation.value


def test_concept_candidate_v1_remains_an_envelope_around_a_specific_transformation() -> None:
    case = next(
        item
        for item in j3_transformation_cases()
        if item.required_transformations == (J3Transformation.BRIDGE_CORRESPONDENCE,)
    )
    candidate = build_concept_candidate(
        concept_id="bridge-candidate",
        source_regime_id="regime-a",
        transformation_steps=(case.required_transformations[0].value,),
        structural_declarations=("relation:left-right",),
        semantic_judgment_ids=("typed-bridge-semantics",),
        correspondence_map={"old-left": "new-left", "old-right": "new-right"},
        unlocked_contract_ids=(case.contract_id,),
        protected_consequence_request_ids=("protected-transfer-check",),
        lineage_ids=(case.parent_family,),
    )

    assert candidate.transformation_steps == (J3Transformation.BRIDGE_CORRESPONDENCE.value,)
    assert candidate.validity_state == "PROPOSAL_ONLY"
    assert candidate.grants_validity_authority is False
    assert candidate.grants_novelty_authority is False
    assert candidate.grants_adoption_authority is False
