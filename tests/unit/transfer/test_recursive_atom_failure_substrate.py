from __future__ import annotations

import pytest

from orion.transfer.v2.bounded_epistemic_study import (
    ReachabilityDeltaStatus,
    ReachabilityStatus,
    analyze_contract_interaction,
    build_atom_study,
    build_reachability_witness,
    build_resource_bound,
    compare_reachability,
)
from orion.transfer.v2.failure_knowledge import (
    FailureApplicabilityStatus,
    assess_failure_applicability,
    build_failure_knowledge,
)


def test_resource_bound_is_canonical_and_nonnegative() -> None:
    left = build_resource_bound({"tool_calls": 4, "compute": 10.0})
    right = build_resource_bound({"compute": 10, "tool_calls": 4.0})
    assert left.digest == right.digest
    assert left.resources == (("compute", 10.0), ("tool_calls", 4.0))
    with pytest.raises(ValueError, match="non-negative"):
        build_resource_bound({"compute": -1})


def test_reachability_witness_is_evaluator_bound_and_content_addressed() -> None:
    bound = build_resource_bound({"steps": 8})
    witness = build_reachability_witness(
        regime_id="R0",
        contract_id="C.bridge",
        resource_bound=bound,
        status=ReachabilityStatus.UNREACHABLE,
        witness_ids=("exhaustive-enumeration-v1",),
        evaluator_id="independent-evaluator-A",
        protected=True,
    )
    witness.verify()
    assert witness.grants_scientific_authority is False
    assert witness.evaluator_id == "independent-evaluator-A"
    with pytest.raises(ValueError, match="evaluator"):
        build_reachability_witness(
            regime_id="R0",
            contract_id="C.bridge",
            resource_bound=bound,
            status=ReachabilityStatus.UNREACHABLE,
            witness_ids=("proof",),
            evaluator_id="",
        )


def test_reachability_delta_distinguishes_unresolved_from_old_unreachable() -> None:
    bound = build_resource_bound({"steps": 8})
    old = build_reachability_witness(
        regime_id="R0",
        contract_id="C1",
        resource_bound=bound,
        status=ReachabilityStatus.UNRESOLVED,
        witness_ids=("search-incomplete",),
        evaluator_id="eval",
    )
    new = build_reachability_witness(
        regime_id="R1",
        contract_id="C1",
        resource_bound=bound,
        status=ReachabilityStatus.REACHABLE,
        witness_ids=("construction",),
        evaluator_id="eval",
    )
    report = compare_reachability(old, new)
    assert report.status is ReachabilityDeltaStatus.OLD_UNRESOLVED_NEW_REACHABLE
    assert "UNRESOLVED" in report.reasons[0]
    assert report.grants_atom_necessity is False


def test_atom_study_is_preoutcome_and_positive_controls_are_disjoint() -> None:
    study = build_atom_study(
        atom_id="ATOM.TENSION",
        parent_atom_ids=("JUMP",),
        structure_version="orion.structure.v1",
        target_contract_ids=("C1", "C2"),
        resource_bound=build_resource_bound({"tool_calls": 3}),
        positive_case_ids=("p1", "p2"),
        no_atom_control_ids=("n1",),
        parent_baseline_ids=("surprise", "mdl"),
        ablation_or_replacement_ids=("no-tension-state",),
        decomposition_hypotheses=("logical", "unification"),
        interaction_hypotheses=("tension+thought-experiment",),
        recursion_stop_rules=("NON_IDENTIFIABLE", "SUBSUMED"),
        evaluator_id="host-evaluator",
        authority_owner_id="P4/P8-host",
        protected_field_ids=("gold-tension",),
        outcome_accessed=False,
    )
    study.verify()
    assert study.grants_scientific_authority is False
    with pytest.raises(ValueError, match="outcome"):
        build_atom_study(
            atom_id="ATOM.TENSION",
            structure_version="v1",
            target_contract_ids=("C1",),
            resource_bound=build_resource_bound({"steps": 1}),
            positive_case_ids=("p1",),
            no_atom_control_ids=("n1",),
            parent_baseline_ids=("b",),
            evaluator_id="e",
            authority_owner_id="a",
            outcome_accessed=True,
        )
    with pytest.raises(ValueError, match="overlap"):
        build_atom_study(
            atom_id="ATOM.TENSION",
            structure_version="v1",
            target_contract_ids=("C1",),
            resource_bound=build_resource_bound({"steps": 1}),
            positive_case_ids=("same",),
            no_atom_control_ids=("same",),
            parent_baseline_ids=("b",),
            evaluator_id="e",
            authority_owner_id="a",
        )


def test_interaction_analysis_keeps_synergy_separate_from_main_effects() -> None:
    report = analyze_contract_interaction(
        left_atom_id="a",
        right_atom_id="b",
        left_reachable_contract_ids=("C.left",),
        right_reachable_contract_ids=("C.right",),
        combined_reachable_contract_ids=("C.left", "C.right", "C.synergy"),
    )
    assert report.synergy_contract_ids == ("C.synergy",)
    assert report.left_only_contract_ids == ("C.left",)
    assert report.right_only_contract_ids == ("C.right",)
    assert report.grants_atom_independence_claim is False


def _failure() :
    return build_failure_knowledge(
        failure_id="F1",
        target_contract_id="C.solve",
        regime_id="R0",
        attempted_trace_ids=("try-method-m",),
        observed_failure_id="counterexample-17",
        responsibility_state_id="resp.execution-vs-method",
        excluded_condition_ids=("method-m-under-old-representation",),
        still_live_alternative_ids=("representation-repair", "different-method"),
        preserved_success_ids=("old-domain-success",),
        frozen_context={
            "representation": "rep-v1",
            "measurement": "sensor-v1",
            "objective": "goal-v1",
        },
        required_same_coordinates=("measurement", "objective"),
        reopen_on_change_coordinates=("representation",),
        evidence_ids=("evidence-1",),
        authority_owner_id="independent-failure-evaluator",
    )


def test_failure_knowledge_applies_only_under_compatible_context() -> None:
    failure = _failure()
    report = assess_failure_applicability(
        failure,
        current_context={
            "representation": "rep-v1",
            "measurement": "sensor-v1",
            "objective": "goal-v1",
        },
    )
    assert report.status is FailureApplicabilityStatus.APPLIES
    assert report.applicable_excluded_condition_ids == (
        "method-m-under-old-representation",
    )
    assert report.grants_global_prohibition is False


def test_failure_knowledge_reopens_after_declared_regime_change() -> None:
    report = assess_failure_applicability(
        _failure(),
        current_context={
            "representation": "rep-v2",
            "measurement": "sensor-v1",
            "objective": "goal-v1",
        },
    )
    assert report.status is FailureApplicabilityStatus.REOPENED
    assert report.applicable_excluded_condition_ids == ()
    assert "representation" in report.changed_coordinates


def test_failure_knowledge_does_not_apply_when_required_context_differs() -> None:
    report = assess_failure_applicability(
        _failure(),
        current_context={
            "representation": "rep-v1",
            "measurement": "sensor-v2",
            "objective": "goal-v1",
        },
    )
    assert report.status is FailureApplicabilityStatus.NOT_APPLICABLE
    assert report.applicable_excluded_condition_ids == ()
    assert "measurement" in report.changed_coordinates


def test_failure_knowledge_missing_context_stays_unresolved() -> None:
    report = assess_failure_applicability(
        _failure(),
        current_context={"representation": "rep-v1", "objective": "goal-v1"},
    )
    assert report.status is FailureApplicabilityStatus.UNRESOLVED
    assert report.applicable_excluded_condition_ids == ()
    assert "measurement" in report.missing_coordinates


def test_failure_context_roles_cannot_overlap() -> None:
    with pytest.raises(ValueError, match="overlap"):
        build_failure_knowledge(
            failure_id="F",
            target_contract_id="C",
            regime_id="R",
            attempted_trace_ids=("t",),
            observed_failure_id="x",
            responsibility_state_id="r",
            excluded_condition_ids=("e",),
            frozen_context={"representation": "v1"},
            required_same_coordinates=("representation",),
            reopen_on_change_coordinates=("representation",),
            evidence_ids=("ev",),
            authority_owner_id="host",
        )
