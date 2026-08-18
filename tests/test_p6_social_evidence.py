from __future__ import annotations

import pytest

from orion.transfer.v2.social_evidence import (
    ContributionCreditStatus,
    ContributionState,
    SocialEvidenceIndependenceStatus,
    TruthfulnessState,
    assess_contribution_credit,
    assess_social_evidence_independence,
    build_social_contribution,
    build_social_evidence_record,
)


def report(
    report_id: str,
    agent_id: str,
    *,
    direct=(),
    upstream=(),
    truthfulness: TruthfulnessState = TruthfulnessState.SATISFIED,
):
    return build_social_evidence_record(
        report_id=report_id,
        agent_id=agent_id,
        claim_id="claim:social",
        direct_observation_ids=direct,
        upstream_source_ids=upstream,
        truthfulness_state=truthfulness,
    )


def contribution(name: str, state: ContributionState):
    return build_social_contribution(
        contribution_id=f"contrib:{name}",
        contributor_id=name,
        outcome_id="outcome:demo",
        state=state,
        evidence_ids=(f"evidence:{name}",),
    )


def test_different_agents_with_shared_upstream_source_are_correlated() -> None:
    left = report("r1", "agent:a", direct=("obs:a",), upstream=("source:shared",))
    right = report("r2", "agent:b", direct=("obs:b",), upstream=("source:shared",))

    assessment = assess_social_evidence_independence((left, right))

    assert assessment.status is SocialEvidenceIndependenceStatus.CORRELATED
    assert assessment.shared_upstream_source_ids == ("source:shared",)
    assert assessment.grants_claim_authority is False


def test_disjoint_registered_provenance_can_be_bounded_independent() -> None:
    left = report("r1", "agent:a", direct=("obs:a",), upstream=("source:a",))
    right = report("r2", "agent:b", direct=("obs:b",), upstream=("source:b",))

    assessment = assess_social_evidence_independence((left, right))

    assert assessment.status is SocialEvidenceIndependenceStatus.INDEPENDENT
    assert assessment.shared_upstream_source_ids == ()
    assert assessment.shared_direct_observation_ids == ()


def test_missing_provenance_or_unresolved_truthfulness_stays_unresolved() -> None:
    missing = report("r1", "agent:a", direct=("obs:a",), upstream=())
    unresolved = report(
        "r2",
        "agent:b",
        direct=("obs:b",),
        upstream=("source:b",),
        truthfulness=TruthfulnessState.UNRESOLVED,
    )

    assessment = assess_social_evidence_independence((missing, unresolved))

    assert assessment.status is SocialEvidenceIndependenceStatus.UNRESOLVED


def test_violated_truthfulness_is_unreliable_even_with_disjoint_sources() -> None:
    bad = report(
        "r1",
        "agent:a",
        direct=("obs:a",),
        upstream=("source:a",),
        truthfulness=TruthfulnessState.VIOLATED,
    )
    clean = report("r2", "agent:b", direct=("obs:b",), upstream=("source:b",))

    assessment = assess_social_evidence_independence((bad, clean))

    assert assessment.status is SocialEvidenceIndependenceStatus.UNRELIABLE


def test_hidden_possible_contributor_prevents_exclusive_credit() -> None:
    visible = contribution("visible", ContributionState.OBSERVED)
    hidden = contribution("hidden", ContributionState.UNRESOLVED)

    credit = assess_contribution_credit((visible, hidden))

    assert credit.status is ContributionCreditStatus.UNRESOLVED
    assert credit.exclusive_contributor_id is None
    assert credit.grants_scientific_authority is False


def test_multiple_observed_contributors_are_shared() -> None:
    left = contribution("left", ContributionState.OBSERVED)
    right = contribution("right", ContributionState.OBSERVED)

    credit = assess_contribution_credit((left, right))

    assert credit.status is ContributionCreditStatus.SHARED
    assert set(credit.observed_contributor_ids) == {"left", "right"}


def test_one_observed_and_all_others_absent_supports_bounded_exclusive_credit() -> None:
    visible = contribution("visible", ContributionState.OBSERVED)
    absent = contribution("other", ContributionState.ABSENT)

    credit = assess_contribution_credit((visible, absent))

    assert credit.status is ContributionCreditStatus.EXCLUSIVE_SUPPORTED
    assert credit.exclusive_contributor_id == "visible"
    assert credit.grants_scientific_authority is False


def test_cross_claim_social_reports_are_rejected() -> None:
    first = report("r1", "agent:a", direct=("obs:a",), upstream=("source:a",))
    second = build_social_evidence_record(
        report_id="r2",
        agent_id="agent:b",
        claim_id="claim:other",
        direct_observation_ids=("obs:b",),
        upstream_source_ids=("source:b",),
        truthfulness_state=TruthfulnessState.SATISFIED,
    )

    with pytest.raises(ValueError, match="claim-relative"):
        assess_social_evidence_independence((first, second))
