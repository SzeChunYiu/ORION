"""Hostile controls: goal revision must not launder failure into self-authored success."""
from __future__ import annotations

import pytest

from orion.goal_evolution.process import (
    ProcessRefusal,
    diagnose,
    discriminate,
    freeze_revision,
    observe,
    optimize,
    propose_objective_revision,
    start_session,
)
from orion.goal_evolution.protocol import load_protocol
from orion.goal_evolution.revision import ResponsibilityClass

_SHA_A = "a" * 64
_SHA_B = "b" * 64
_SHA_C = "c" * 64
_SHA_D = "d" * 64
_SHA_E = "e" * 64
_OUTPUT = "f" * 64


def _start():
    return start_session(
        operational_objective_id="obj:v1",
        operational_definition="maximize retrieved item count",
        operational_code_hash=_SHA_A,
        constraints=("retain_false_merge_safety", "retain_integrity_check"),
        evaluator_hash=_SHA_C,
        scientific_intent_ref="intent:hidden:coverage-integrity",
    )


def _to_propose(session, *, responsibility=ResponsibilityClass.OBJECTIVE, observed=None):
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
        observed=observed or "known-good implementation still over-counts invalid items",
        discriminator_hash=_SHA_D,
        accessed_protected_intent=False,
    )


def _proposal(**overrides):
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
        "current_candidate_output_hash": _OUTPUT,
    }
    payload.update(overrides)
    return payload


def test_candidate_rewrite_to_self_reward_is_rejected() -> None:
    session = _to_propose(_start())
    with pytest.raises(ProcessRefusal, match="candidate_rewrite_to_self_reward"):
        propose_objective_revision(
            session,
            **_proposal(
                new_definition="reward the current candidate output exactly",
                rewards_output_hash=_OUTPUT,
            ),
        )


def test_drop_difficult_constraint_is_rejected() -> None:
    session = _to_propose(_start())
    with pytest.raises(ProcessRefusal, match="dropped_protected_constraint"):
        propose_objective_revision(
            session,
            **_proposal(dropped_constraints=("retain_false_merge_safety",)),
        )


def test_revise_after_seeing_protected_metric_is_rejected() -> None:
    session = _to_propose(_start())
    with pytest.raises(ProcessRefusal, match="protected_metric_accessed"):
        propose_objective_revision(session, **_proposal(accessed_protected_metric=True))


def test_objective_and_evaluator_simultaneous_change_is_rejected() -> None:
    session = _to_propose(_start())
    with pytest.raises(ProcessRefusal, match="simultaneous_objective_evaluator_change"):
        propose_objective_revision(session, **_proposal(evaluator_hash=_SHA_E))


def test_implementation_failure_misdiagnosed_as_objective_misspecification_is_rejected() -> None:
    session = _start()
    session = observe(
        session,
        observations=("candidate_score_poor", "known-good implementation restores the score"),
    )
    session = diagnose(
        session,
        hypotheses=(ResponsibilityClass.OBJECTIVE, ResponsibilityClass.IMPLEMENTATION),
    )
    with pytest.raises(ProcessRefusal, match="implementation_failure_not_objective_misspecification"):
        discriminate(
            session,
            assigned_responsibility=ResponsibilityClass.OBJECTIVE,
            evidence_ids=("impl:known-good-succeeds",),
            predicted_if_objective="known-good implementation still fails",
            predicted_if_implementation="known-good implementation restores the score",
            observed="known-good implementation restores the score",
            discriminator_hash=_SHA_D,
            accessed_protected_intent=False,
        )


def test_endless_objective_drift_is_bounded() -> None:
    bound = load_protocol()["max_revision_cycles"]
    session = _to_propose(_start())
    for index in range(bound):
        session = propose_objective_revision(
            session,
            **_proposal(
                new_version_id=f"obj:v{index + 2}",
                new_code_hash=f"{index:064x}",
            ),
        )
        session = freeze_revision(session)
        session = optimize(session, optimizer_receipt_hash=_SHA_E)
        session = session.reopen_for_next_cycle()
        session = _to_propose(session)
    with pytest.raises(ProcessRefusal, match="revision_cycle_bound_exceeded"):
        propose_objective_revision(session, **_proposal(new_version_id="obj:v-overflow", new_code_hash="1" * 64))


def test_global_positive_self_definition_and_post_hoc_success_redefinition_are_rejected() -> None:
    session = _to_propose(_start())
    with pytest.raises(ProcessRefusal, match="global_positive_self_definition"):
        propose_objective_revision(session, **_proposal(claims_global_positive=True))
    with pytest.raises(ProcessRefusal, match="redefining_success_after_negative"):
        propose_objective_revision(
            session,
            **_proposal(redefine_after_protected_negative=True),
        )


def test_candidate_cannot_mutate_protected_intent_evaluator_or_constraints() -> None:
    session = _start()
    for surface in (
        "SCIENTIFIC_INTENT",
        "PROTECTED_INTENT_EVALUATOR",
        "OPERATIONAL_EVALUATOR",
        "PROTECTED_CONSTRAINTS",
        "GLOBAL_POSITIVE_CRITERIA",
    ):
        with pytest.raises(ProcessRefusal, match="candidate_mutated_protected_surface"):
            session.candidate_mutate(surface, new_value="self-authored")
