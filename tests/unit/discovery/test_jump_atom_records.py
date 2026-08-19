from __future__ import annotations

import pytest

from orion.discovery.concept_candidate import build_concept_candidate
from orion.discovery.epistemic_tension import (
    EvidencePresence,
    TensionStatus,
    assess_tensions,
    build_tension_candidate,
)
from orion.discovery.thought_experiment import (
    ExecutionMode,
    ProspectiveDiscriminationStatus,
    assess_prospective_discrimination,
    build_thought_experiment,
)


def _zero_error_tension():
    return build_tension_candidate(
        tension_id="T.unification",
        regime_id="R0",
        kind="UNIFICATION_DEFICIT",
        target_contract_ids=("C.cross-domain",),
        required_witness_ids=("two-local-laws", "no-bridge"),
        defeating_witness_ids=("existing-bridge",),
        discriminator_ids=("couple-domains",),
        downstream_contract_ids=("C.protected-coupled",),
    )


def test_zero_error_structural_tension_is_representable() -> None:
    tension = _zero_error_tension()
    report = assess_tensions(
        (tension,),
        evidence_presence={
            "two-local-laws": EvidencePresence.PRESENT,
            "no-bridge": EvidencePresence.PRESENT,
            "existing-bridge": EvidencePresence.ABSENT,
        },
        empirical_residual_present=False,
    )
    assert report.status is TensionStatus.IDENTIFIED
    assert report.identified_tension_id == "T.unification"
    assert report.empirical_residual_present is False
    assert report.grants_revision_authority is False


def test_multiple_live_tensions_remain_plural() -> None:
    first = _zero_error_tension()
    second = build_tension_candidate(
        tension_id="T.symmetry",
        regime_id="R0",
        kind="SYMMETRY_OPPORTUNITY",
        target_contract_ids=("C.cross-domain",),
        required_witness_ids=("symmetry-pattern",),
        defeating_witness_ids=(),
        discriminator_ids=("transform",),
        downstream_contract_ids=("C.invariant-transfer",),
    )
    report = assess_tensions(
        (first, second),
        evidence_presence={
            "two-local-laws": EvidencePresence.PRESENT,
            "no-bridge": EvidencePresence.PRESENT,
            "existing-bridge": EvidencePresence.ABSENT,
            "symmetry-pattern": EvidencePresence.PRESENT,
        },
        empirical_residual_present=False,
    )
    assert report.status is TensionStatus.PLURAL
    assert report.identified_tension_id is None
    assert report.surviving_tension_ids == ("T.symmetry", "T.unification")


def test_missing_tension_evidence_stays_unresolved() -> None:
    report = assess_tensions(
        (_zero_error_tension(),),
        evidence_presence={
            "two-local-laws": EvidencePresence.PRESENT,
            "existing-bridge": EvidencePresence.ABSENT,
        },
        empirical_residual_present=False,
    )
    assert report.status is TensionStatus.UNRESOLVED
    assert report.missing_evidence_ids == ("no-bridge",)


def test_tension_digest_is_input_order_invariant() -> None:
    left = build_tension_candidate(
        tension_id="T",
        regime_id="R",
        kind="GENERIC",
        target_contract_ids=("C2", "C1"),
        required_witness_ids=("b", "a"),
        defeating_witness_ids=("d", "c"),
        discriminator_ids=("x2", "x1"),
        downstream_contract_ids=("z2", "z1"),
    )
    right = build_tension_candidate(
        tension_id="T",
        regime_id="R",
        kind="GENERIC",
        target_contract_ids=("C1", "C2"),
        required_witness_ids=("a", "b"),
        defeating_witness_ids=("c", "d"),
        discriminator_ids=("x1", "x2"),
        downstream_contract_ids=("z1", "z2"),
    )
    assert left.digest == right.digest


def test_thought_experiment_rejects_relax_hold_overlap() -> None:
    with pytest.raises(ValueError, match="relax.*held"):
        build_thought_experiment(
            experiment_id="TE",
            tension_digest=_zero_error_tension().digest,
            operation_kind="ASSUMPTION_RELAXATION",
            relaxed_assumptions=("absolute-time",),
            held_fixed_assumptions=("absolute-time",),
            hypothetical_setup_id="setup",
            expected_outcomes={"H1": ("a",), "H2": ("b",)},
            execution_mode=ExecutionMode.SIMULATED,
            cost=1,
        )


def test_thought_experiment_registered_predictions_can_be_non_discriminating() -> None:
    experiment = build_thought_experiment(
        experiment_id="TE.same",
        tension_digest=_zero_error_tension().digest,
        operation_kind="FRAME_CHANGE",
        relaxed_assumptions=("observer-fixed",),
        held_fixed_assumptions=("causal-order",),
        hypothetical_setup_id="moving-observer",
        expected_outcomes={"H1": ("same",), "H2": ("same",)},
        execution_mode=ExecutionMode.FORMAL,
        cost=2,
        safety_constraints=("no-real-world-effect",),
    )
    report = assess_prospective_discrimination(experiment)
    assert report.status is ProspectiveDiscriminationStatus.NONE
    assert report.distinguishable_pairs == 0
    assert report.total_pairs == 1
    assert report.grants_theory_authority is False


def test_thought_experiment_full_discrimination_is_prospective_only() -> None:
    experiment = build_thought_experiment(
        experiment_id="TE.split",
        tension_digest=_zero_error_tension().digest,
        operation_kind="COUPLE_DOMAINS",
        relaxed_assumptions=(),
        held_fixed_assumptions=("local-laws",),
        hypothetical_setup_id="coupled-system",
        expected_outcomes={
            "H.local-only": ("inconsistent",),
            "H.bridge": ("consistent",),
        },
        execution_mode=ExecutionMode.SIMULATED,
        cost=1.5,
    )
    report = assess_prospective_discrimination(experiment)
    assert report.status is ProspectiveDiscriminationStatus.FULL
    assert report.distinguishable_pairs == report.total_pairs == 1
    assert experiment.grants_theory_authority is False


def test_concept_candidate_requires_structural_semantics_and_correspondence() -> None:
    candidate = build_concept_candidate(
        concept_id="concept.bridge-object",
        source_regime_id="R0",
        source_tension_digests=(_zero_error_tension().digest,),
        thought_experiment_digests=("thought-digest",),
        transformation_steps=("INTRODUCE_RELATION", "BRIDGE_DOMAINS"),
        structural_declarations=("BridgeObject:A<->B",),
        semantic_judgment_ids=("typing-judgment-1",),
        correspondence_map={"old.A": "new.A", "old.B": "new.B"},
        executable_artifact_id="simulator-candidate-1",
        unlocked_contract_ids=("C.cross-domain",),
        protected_consequence_request_ids=("predict-heldout-coupling",),
        lineage_ids=("analogy-donor-1",),
    )
    candidate.verify()
    assert candidate.validity_state == "PROPOSAL_ONLY"
    assert candidate.grants_validity_authority is False
    assert candidate.grants_novelty_authority is False
    assert candidate.grants_adoption_authority is False

    with pytest.raises(ValueError, match="structural"):
        build_concept_candidate(
            concept_id="bad",
            source_regime_id="R0",
            transformation_steps=("rename",),
            structural_declarations=(),
            semantic_judgment_ids=("j",),
            correspondence_map={"a": "a2"},
            unlocked_contract_ids=("C",),
            protected_consequence_request_ids=("p",),
        )
    with pytest.raises(ValueError, match="semantic"):
        build_concept_candidate(
            concept_id="bad",
            source_regime_id="R0",
            transformation_steps=("INTRODUCE",),
            structural_declarations=("X",),
            semantic_judgment_ids=(),
            correspondence_map={"a": "a2"},
            unlocked_contract_ids=("C",),
            protected_consequence_request_ids=("p",),
        )
    with pytest.raises(ValueError, match="correspondence"):
        build_concept_candidate(
            concept_id="bad",
            source_regime_id="R0",
            transformation_steps=("INTRODUCE",),
            structural_declarations=("X",),
            semantic_judgment_ids=("j",),
            correspondence_map={},
            unlocked_contract_ids=("C",),
            protected_consequence_request_ids=("p",),
        )
