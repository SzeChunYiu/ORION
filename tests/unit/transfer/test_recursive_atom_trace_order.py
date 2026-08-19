from __future__ import annotations

from orion.discovery.concept_candidate import build_concept_candidate
from orion.transfer.v2.bounded_epistemic_study import (
    build_atom_study,
    build_resource_bound,
)
from orion.transfer.v2.failure_knowledge import build_failure_knowledge


def test_parent_decomposition_path_preserves_order() -> None:
    study = build_atom_study(
        atom_id="ATOM.J3",
        parent_atom_ids=("JUMP", "DISCOVERY", "CONCEPT"),
        structure_version="v1",
        target_contract_ids=("C",),
        resource_bound=build_resource_bound({"steps": 2}),
        positive_case_ids=("p",),
        no_atom_control_ids=("n",),
        parent_baseline_ids=("b",),
        evaluator_id="eval",
        authority_owner_id="host",
    )
    assert study.parent_atom_ids == ("JUMP", "DISCOVERY", "CONCEPT")


def test_failure_attempt_trace_preserves_order_and_recurrence() -> None:
    failure = build_failure_knowledge(
        failure_id="F",
        target_contract_id="C",
        regime_id="R",
        attempted_trace_ids=("probe", "repair", "probe", "reject"),
        observed_failure_id="failed",
        responsibility_state_id="resp",
        excluded_condition_ids=("bad-under-R",),
        frozen_context={"representation": "R1"},
        reopen_on_change_coordinates=("representation",),
        evidence_ids=("e",),
        authority_owner_id="host",
    )
    assert failure.attempted_trace_ids == ("probe", "repair", "probe", "reject")


def test_concept_transformation_trace_preserves_order_and_recurrence() -> None:
    candidate = build_concept_candidate(
        concept_id="concept",
        source_regime_id="R0",
        transformation_steps=("RELAX", "INTRODUCE", "REFINE", "INTRODUCE"),
        structural_declarations=("X:type",),
        semantic_judgment_ids=("typing",),
        correspondence_map={"old.x": "new.x"},
        unlocked_contract_ids=("C",),
        protected_consequence_request_ids=("P",),
    )
    assert candidate.transformation_steps == (
        "RELAX",
        "INTRODUCE",
        "REFINE",
        "INTRODUCE",
    )
