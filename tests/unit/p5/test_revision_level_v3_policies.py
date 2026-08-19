from __future__ import annotations

import pytest

from orion.study.p5.revision_level_v3_policies import (
    FeedbackMode,
    PolicyKind,
    ProtectedFeedbackOracle,
    run_revision_policy,
)


CASE = {
    "case_id": "V3-POL-01",
    "symptom_family": "prediction-residual",
    "visible_symptom": "prediction mismatch",
    "candidate_visible_context": {"domain": "toy"},
    "competing_revision_classes": ["EVIDENCE_REPAIR", "MODEL_CLASS_EXPANSION"],
    "hypotheses": {
        "EVIDENCE_REPAIR": {"inspect": ["MISSING_SOURCE"]},
        "MODEL_CLASS_EXPANSION": {"inspect": ["COMPLETE_EVIDENCE_MODEL_MISS"]},
    },
    "allowed_diagnostics": [{"action_id": "inspect", "cost": 1.0}],
    "diagnostic_budget": 1.0,
    "revision_invasiveness": {
        "UNRESOLVED": 0,
        "EVIDENCE_REPAIR": 1,
        "MODEL_CLASS_EXPANSION": 4,
        "BROAD_SELF_EDIT": 6,
    },
}


def _oracle(outcome: str = "MISSING_SOURCE", mode: FeedbackMode = FeedbackMode.NORMAL):
    return ProtectedFeedbackOracle(
        case_id=CASE["case_id"],
        outcome_by_action={"inspect": outcome},
        mode=mode,
        alternate_outcomes={"inspect": "COMPLETE_EVIDENCE_MODEL_MISS"},
    )


def test_full_t7_policy_uses_feedback_and_selects_supported_class() -> None:
    decision = run_revision_policy(PolicyKind.FULL_T7, CASE, _oracle())
    assert decision.selected_revision_class == "EVIDENCE_REPAIR"
    assert decision.diagnostic_actions == ("inspect",)
    assert decision.observed_feedback == (("inspect", "MISSING_SOURCE"),)
    assert decision.analysis_only is False
    assert decision.grants_scientific_authority is False
    assert decision.grants_adoption_authority is False


def test_m_open_comparator_is_explicitly_single_regime() -> None:
    decision = run_revision_policy(PolicyKind.M_OPEN_ONLY, CASE, _oracle())
    assert decision.selected_revision_class == "MODEL_CLASS_EXPANSION"
    assert decision.diagnostic_actions == ()
    assert "MECHANISM_COMPARATOR" in decision.trace


def test_direct_self_edit_is_broad_control_not_gold_class_laundering() -> None:
    decision = run_revision_policy(PolicyKind.DIRECT_SELF_EDIT, CASE, _oracle())
    assert decision.selected_revision_class == "BROAD_SELF_EDIT"
    assert decision.diagnostic_actions == ()


def test_no_feedback_breaks_evidence_responsive_policy() -> None:
    normal = run_revision_policy(PolicyKind.FULL_T7, CASE, _oracle())
    no_feedback = run_revision_policy(
        PolicyKind.FULL_T7,
        CASE,
        _oracle(mode=FeedbackMode.NONE),
    )
    assert normal.selected_revision_class == "EVIDENCE_REPAIR"
    assert no_feedback.selected_revision_class == "UNRESOLVED"
    assert no_feedback.observed_feedback == (("inspect", "NO_FEEDBACK"),)


def test_permuted_feedback_changes_full_policy_decision() -> None:
    normal = run_revision_policy(PolicyKind.FULL_T7, CASE, _oracle())
    permuted = run_revision_policy(
        PolicyKind.FULL_T7,
        CASE,
        _oracle(mode=FeedbackMode.PERMUTED),
    )
    assert normal.selected_revision_class == "EVIDENCE_REPAIR"
    assert permuted.selected_revision_class == "MODEL_CLASS_EXPANSION"


def test_always_unresolved_and_no_revision_controls_are_distinct() -> None:
    abstain = run_revision_policy(PolicyKind.ALWAYS_UNRESOLVED, CASE, _oracle())
    fixed = run_revision_policy(PolicyKind.NO_REVISION, CASE, _oracle())
    assert abstain.selected_revision_class == "UNRESOLVED"
    assert fixed.selected_revision_class == "NO_REVISION"


def test_oracle_ceiling_is_analysis_only() -> None:
    decision = run_revision_policy(
        PolicyKind.ORACLE_CEILING,
        CASE,
        _oracle(),
        protected_gold_revision_class="EVIDENCE_REPAIR",
    )
    assert decision.selected_revision_class == "EVIDENCE_REPAIR"
    assert decision.analysis_only is True
    assert decision.excluded_from_superiority_claim is True


def test_non_oracle_policy_cannot_receive_protected_gold() -> None:
    with pytest.raises(ValueError, match="protected gold"):
        run_revision_policy(
            PolicyKind.FULL_T7,
            CASE,
            _oracle(),
            protected_gold_revision_class="EVIDENCE_REPAIR",
        )


def test_policy_cannot_use_unavailable_diagnostic() -> None:
    bad_case = dict(CASE)
    bad_case["allowed_diagnostics"] = []
    bad_case["diagnostic_budget"] = 0.0
    decision = run_revision_policy(PolicyKind.FULL_T7, bad_case, _oracle())
    assert decision.diagnostic_actions == ()
    assert decision.selected_revision_class == "UNRESOLVED"


def test_policy_budget_is_hard() -> None:
    bad_case = dict(CASE)
    bad_case["diagnostic_budget"] = 0.5
    decision = run_revision_policy(PolicyKind.FULL_T7, bad_case, _oracle())
    assert decision.diagnostic_actions == ()
    assert decision.selected_revision_class == "UNRESOLVED"
