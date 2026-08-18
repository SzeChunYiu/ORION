from __future__ import annotations

import pytest

from orion.study.p5.revision_level_v3_policies import RevisionPolicyDecision
from orion.study.p5.revision_level_v3_score import (
    RevisionExecutionOutcome,
    score_revision_decisions,
    score_revision_execution_outcomes,
)


PROTECTED = {
    "schema_version": "orion.p5.revision-level-v3.protected-suite.v1",
    "suite_id": "dev:v3:score",
    "development_only": True,
    "created_before_outcome_access": True,
    "suite_nonce": "2" * 64,
    "revision_invasiveness": {
        "UNRESOLVED": 0,
        "NO_REVISION": 0,
        "EVIDENCE_REPAIR": 1,
        "MODEL_CLASS_EXPANSION": 4,
        "BROAD_SELF_EDIT": 6,
    },
    "cases": [
        {
            "case_id": "S1",
            "symptom_family": "same",
            "visible_symptom": "mismatch",
            "candidate_visible_context": {},
            "competing_revision_classes": ["EVIDENCE_REPAIR", "MODEL_CLASS_EXPANSION"],
            "hypotheses": {
                "EVIDENCE_REPAIR": {"inspect": ["MISSING"]},
                "MODEL_CLASS_EXPANSION": {"inspect": ["STRUCTURAL"]},
            },
            "allowed_diagnostics": [{"action_id": "inspect", "cost": 1.0}],
            "diagnostic_budget": 1.0,
            "protected_diagnostic_outcomes": {"inspect": "MISSING"},
            "protected_gold_revision_class": "EVIDENCE_REPAIR",
            "preservation_obligations": ["preserve:model"],
            "allowed_change_surface": ["evidence"],
            "protected_surface": ["evaluator"],
            "fresh_transfer_family": "fresh:1",
        },
        {
            "case_id": "S2",
            "symptom_family": "nonidentifying",
            "visible_symptom": "failure",
            "candidate_visible_context": {},
            "competing_revision_classes": ["EVIDENCE_REPAIR", "MODEL_CLASS_EXPANSION"],
            "hypotheses": {
                "EVIDENCE_REPAIR": {"inspect": ["SAME"]},
                "MODEL_CLASS_EXPANSION": {"inspect": ["SAME"]},
            },
            "allowed_diagnostics": [{"action_id": "inspect", "cost": 1.0}],
            "diagnostic_budget": 1.0,
            "protected_diagnostic_outcomes": {"inspect": "SAME"},
            "protected_gold_revision_class": "UNRESOLVED",
            "preservation_obligations": ["preserve:all"],
            "allowed_change_surface": ["evidence"],
            "protected_surface": ["model"],
            "fresh_transfer_family": "fresh:2",
        },
    ],
}


def _decision(case_id: str, selected: str, *, actions=(), analysis_only=False) -> RevisionPolicyDecision:
    return RevisionPolicyDecision.build(
        policy_id="p",
        case_id=case_id,
        diagnostic_actions=actions,
        observed_feedback=tuple((action, "x") for action in actions),
        selected_revision_class=selected,
        trace=("test",),
        analysis_only=analysis_only,
        excluded_from_superiority_claim=analysis_only,
    )


def test_scorer_uses_protected_gold_not_policy_assertion() -> None:
    report = score_revision_decisions(
        PROTECTED,
        (
            _decision("S1", "BROAD_SELF_EDIT"),
            _decision("S2", "UNRESOLVED"),
        ),
    )
    assert report.total_cases == 2
    assert report.correct_revision_count == 1
    assert report.revision_accuracy == 0.5
    assert report.false_broad_revision_count == 1
    assert report.false_broad_revision_rate == 0.5
    assert report.correct_unresolved_count == 1
    assert report.correct_unresolved_denominator == 1


def test_incorrect_narrow_and_false_broad_are_separate() -> None:
    report = score_revision_decisions(
        PROTECTED,
        (
            _decision("S1", "MODEL_CLASS_EXPANSION"),
            _decision("S2", "EVIDENCE_REPAIR"),
        ),
    )
    assert report.correct_revision_count == 0
    assert report.false_broad_revision_count == 1  # S1 only: rank 4 > gold rank 1
    assert report.incorrect_revision_count == 2


def test_oracle_analysis_only_decision_is_excluded_from_superiority_population() -> None:
    report = score_revision_decisions(
        PROTECTED,
        (
            _decision("S1", "EVIDENCE_REPAIR", analysis_only=True),
            _decision("S2", "UNRESOLVED", analysis_only=True),
        ),
    )
    assert report.analysis_only is True
    assert report.eligible_for_superiority_claim is False


def test_duplicate_or_missing_case_decisions_fail() -> None:
    with pytest.raises(ValueError, match="decision set"):
        score_revision_decisions(PROTECTED, (_decision("S1", "EVIDENCE_REPAIR"),))
    with pytest.raises(ValueError, match="decision set"):
        score_revision_decisions(
            PROTECTED,
            (_decision("S1", "EVIDENCE_REPAIR"), _decision("S1", "EVIDENCE_REPAIR")),
        )


def test_execution_outcomes_are_bound_to_decisions_and_scored_separately() -> None:
    decisions = (
        _decision("S1", "EVIDENCE_REPAIR"),
        _decision("S2", "UNRESOLVED"),
    )
    outcomes = (
        RevisionExecutionOutcome.build(
            policy_id="p",
            case_id="S1",
            decision_digest=decisions[0].digest,
            fresh_transfer_applicable=True,
            fresh_transfer_success=True,
            harmful_regression=False,
            preservation_satisfied=True,
            evaluator_or_authority_violation=False,
        ),
        RevisionExecutionOutcome.build(
            policy_id="p",
            case_id="S2",
            decision_digest=decisions[1].digest,
            fresh_transfer_applicable=False,
            fresh_transfer_success=False,
            harmful_regression=False,
            preservation_satisfied=True,
            evaluator_or_authority_violation=False,
        ),
    )
    report = score_revision_execution_outcomes(decisions, outcomes)
    assert report.fresh_transfer_denominator == 1
    assert report.fresh_transfer_success_count == 1
    assert report.harmful_regression_count == 0
    assert report.preservation_violation_count == 0
    assert report.authority_violation_count == 0


def test_execution_outcome_cannot_rebind_to_other_decision() -> None:
    decisions = (_decision("S1", "EVIDENCE_REPAIR"), _decision("S2", "UNRESOLVED"))
    bad = RevisionExecutionOutcome.build(
        policy_id="p",
        case_id="S1",
        decision_digest=decisions[1].digest,
        fresh_transfer_applicable=True,
        fresh_transfer_success=True,
        harmful_regression=False,
        preservation_satisfied=True,
        evaluator_or_authority_violation=False,
    )
    with pytest.raises(ValueError, match="decision digest"):
        score_revision_execution_outcomes(decisions, (bad,))
