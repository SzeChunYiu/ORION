"""OBSERVE -> DIAGNOSE -> DISCRIMINATE -> PROPOSE -> FREEZE -> OPTIMIZE -> PROTECTED_COMPARE -> ADMIT/REJECT."""
from __future__ import annotations

import pytest

from orion.goal_evolution.process import (
    ProcessRefusal,
    ProcessStage,
    admit_or_reject,
    diagnose,
    discriminate,
    freeze_revision,
    observe,
    optimize,
    propose_objective_revision,
    protected_compare,
    start_session,
)
from orion.goal_evolution.protocol import PROTOCOL_ID
from orion.goal_evolution.revision import ObjectiveRevisionStatus, ResponsibilityClass, current_status

_SHA_A = "a" * 64
_SHA_B = "b" * 64
_SHA_C = "c" * 64
_SHA_D = "d" * 64
_SHA_E = "e" * 64


def _legal_proposal(**overrides):
    payload = {
        "new_version_id": "obj:v2",
        "new_definition": "maximize validated coverage under retained safety constraints",
        "new_code_hash": _SHA_B,
        "mapping": (("coverage_count", "validated_coverage"),),
        "predicted_tradeoffs": ("lower raw count, higher validity",),
        "evaluator_hash": _SHA_C,
        "rewards_output_hash": None,
        "dropped_constraints": (),
        "accessed_protected_metric": False,
        "claims_global_positive": False,
        "changes_denominator": False,
    }
    payload.update(overrides)
    return payload


def _session_ready_to_propose(*, responsibility=ResponsibilityClass.OBJECTIVE):
    session = start_session(
        operational_objective_id="obj:v1",
        operational_definition="maximize retrieved item count",
        operational_code_hash=_SHA_A,
        constraints=("retain_false_merge_safety", "retain_integrity_check"),
        evaluator_hash=_SHA_C,
        scientific_intent_ref="intent:hidden:coverage-integrity",
    )
    session = observe(
        session,
        observations=("proxy saturates on invalid items", "implementation unit tests pass"),
    )
    session = diagnose(
        session,
        hypotheses=(
            ResponsibilityClass.OBJECTIVE,
            ResponsibilityClass.IMPLEMENTATION,
            ResponsibilityClass.MEASUREMENT_SPECIFICATION,
        ),
    )
    return discriminate(
        session,
        assigned_responsibility=responsibility,
        evidence_ids=("disc:validity-gap",),
        predicted_if_objective="known-good implementation still over-counts invalid items",
        predicted_if_implementation="known-good implementation restores validity under the same objective",
        observed="known-good implementation still over-counts invalid items",
        discriminator_hash=_SHA_D,
        accessed_protected_intent=False,
    )


def test_process_enforces_stage_order() -> None:
    session = start_session(
        operational_objective_id="obj:v1",
        operational_definition="maximize retrieved item count",
        operational_code_hash=_SHA_A,
        constraints=("retain_false_merge_safety",),
        evaluator_hash=_SHA_C,
        scientific_intent_ref="intent:hidden:coverage-integrity",
    )
    assert session.stage is ProcessStage.OBSERVE
    with pytest.raises(ProcessRefusal, match="stage_out_of_order"):
        diagnose(session, hypotheses=(ResponsibilityClass.OBJECTIVE,))
    session = observe(session, observations=("score is poor",))
    with pytest.raises(ProcessRefusal, match="stage_out_of_order"):
        propose_objective_revision(session, **_legal_proposal())


def test_poor_candidate_result_under_old_objective_is_not_sufficient_to_propose() -> None:
    session = start_session(
        operational_objective_id="obj:v1",
        operational_definition="maximize retrieved item count",
        operational_code_hash=_SHA_A,
        constraints=("retain_false_merge_safety",),
        evaluator_hash=_SHA_C,
        scientific_intent_ref="intent:hidden:coverage-integrity",
    )
    session = observe(session, observations=("candidate_score_poor",))
    session = diagnose(
        session,
        hypotheses=(ResponsibilityClass.OBJECTIVE, ResponsibilityClass.IMPLEMENTATION),
    )
    with pytest.raises(ProcessRefusal, match="poor_score_insufficient_for_proposal"):
        discriminate(
            session,
            assigned_responsibility=ResponsibilityClass.OBJECTIVE,
            evidence_ids=("score:poor",),
            predicted_if_objective="score remains poor under known-good implementation",
            predicted_if_implementation="known-good implementation restores the score",
            observed="candidate_score_poor",
            discriminator_hash=_SHA_D,
            accessed_protected_intent=False,
        )


def test_discriminator_must_identify_objective_or_measurement_before_proposal_is_legal() -> None:
    session = _session_ready_to_propose(responsibility=ResponsibilityClass.IMPLEMENTATION)
    with pytest.raises(ProcessRefusal, match="responsibility_not_objective_or_measurement"):
        propose_objective_revision(session, **_legal_proposal())
    session = _session_ready_to_propose(responsibility=ResponsibilityClass.OBJECTIVE)
    session = propose_objective_revision(session, **_legal_proposal())
    assert session.stage is ProcessStage.FREEZE
    assert _current_revision_status(session) is ObjectiveRevisionStatus.PROPOSED


def _current_revision_status(session):
    return current_status(session.archive, session.revision_id)


def test_freeze_optimize_protected_compare_cannot_admit_without_protected_intent() -> None:
    session = _session_ready_to_propose()
    session = propose_objective_revision(session, **_legal_proposal())
    session = freeze_revision(session)
    assert _current_revision_status(session) is ObjectiveRevisionStatus.ADMITTED_FOR_TEST
    session = optimize(session, optimizer_receipt_hash=_SHA_E)
    compare = protected_compare(session)
    assert compare.status == "CANNOT_CHECK"
    session = admit_or_reject(session, compare)
    assert session.scientific_terminal == "CANNOT_CHECK"
    assert session.current_operational_version_id == "obj:v1"
    assert _current_revision_status(session) is ObjectiveRevisionStatus.ADMITTED_FOR_TEST
    with pytest.raises(ProcessRefusal, match="cannot_claim_supported"):
        session.claim_terminal("PROTECTED_GOAL_EVOLUTION_SUPPORTED")
    assert session.protocol_id == PROTOCOL_ID
