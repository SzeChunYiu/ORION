import hashlib
from types import SimpleNamespace

import pytest

from orion.self_orion.development_trial import (
    FrozenObservedFailureCase,
    ShadowDevelopmentTrialRunner,
)
from orion.self_orion.issue_state import DevelopmentIssue
from orion.self_orion.self_driving import SelfDrivingCycleStatus


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def _issue():
    issue = DevelopmentIssue(
        issue_id="issue:retrieval-route-miss",
        title="Relevant parent-domain source family was missed",
        symptom_signature="present-but-missed:parent-domain",
        failure_episode_ids=("episode:failure:one",),
        evidence_ids=("evidence:observed-failure",),
    )
    issue = issue.propose_causes(("cause:routing", "cause:saturation"))
    return issue.support_cause(
        "cause:routing",
        discriminator_evidence_ids=("evidence:frozen-discriminator",),
    )


def _case():
    return FrozenObservedFailureCase(
        case_id="phase2:development:one",
        mechanic_id="SEARCH.QUERY.v0",
        subject_revision_hash=_digest("subject"),
        evaluation_epoch_id="epoch:frozen",
        split_id="split:fresh-transfer",
        issue=_issue(),
        observed_failure_artifact_hash=_digest("failure-artifact"),
        discriminator_artifact_hash=_digest("discriminator-artifact"),
        observed_failure_before_discriminator=True,
        discriminator_frozen_before_candidate=True,
        negative_alternative_ids=("candidate:failed-a", "candidate:harmful-b"),
    )


def _cycle(*, status=SelfDrivingCycleStatus.HOST_PROMOTION_RECOMMENDED):
    assurance = SimpleNamespace(
        receipt_id="assurance:one",
        evaluator_artifact_hash=_digest("evaluator"),
        evaluation_epoch_id="epoch:frozen",
        development_delta=0.3,
        fresh_assurance_delta=0.1,
        blocking_invariants_passed=True,
        evaluator_frozen_before_candidate=True,
        fresh_split=True,
        resource_matched=True,
    )
    execution = SimpleNamespace(
        receipt_id="execution:one",
        candidate_revision_hash=_digest("candidate"),
        artifact_ids=("artifact:candidate",),
    )
    proposal = SimpleNamespace(proposal_id="proposal:one")
    control = SimpleNamespace(
        proposal=proposal,
        execution=execution,
        assurance=assurance,
        verdict=SimpleNamespace(value="RECOMMEND_HOST_PROMOTION"),
        reasons=(),
        self_merge_authorized=False,
    )
    investigation = SimpleNamespace(
        mechanic_id="SEARCH.QUERY.v0",
        problem_id="self-orion:observed-failure",
        evidence_ids=("evidence:diagnosis",),
        residual_ids=("residual:routing",),
        mechanic_episode_ids=("episode:mechanic:one",),
    )
    return SimpleNamespace(
        status=status,
        change_control=control if status is not SelfDrivingCycleStatus.RESEARCH_OPEN else None,
        investigation=investigation,
        self_merge_authorized=False,
    )


class _Controller:
    def __init__(self, cycle):
        self.cycle = cycle
        self.calls = []

    def run_cycle(self, *, limit, evaluation_epoch_id, split_id):
        self.calls.append((limit, evaluation_epoch_id, split_id))
        return (self.cycle,)


def test_observed_failure_case_requires_competing_hypotheses_and_discriminator():
    issue = DevelopmentIssue(
        issue_id="issue:bad",
        title="bad",
        symptom_signature="failure",
        failure_episode_ids=("episode:one",),
    )
    with pytest.raises(ValueError, match="competing responsibility hypotheses"):
        FrozenObservedFailureCase(
            "case:bad",
            "SEARCH.QUERY.v0",
            _digest("subject"),
            "epoch",
            "split",
            issue,
            _digest("failure"),
            _digest("discriminator"),
            True,
            True,
            ("candidate:negative",),
        )


def test_shadow_development_trial_records_intervention_and_preserves_nonpromotion():
    controller = _Controller(_cycle())
    report = ShadowDevelopmentTrialRunner(controller).run(_case())

    assert controller.calls == [(1, "epoch:frozen", "split:fresh-transfer")]
    assert report.process_demonstrated
    assert report.host_promotion_recommended
    assert report.candidate_improved
    assert not report.self_merge_authorized
    assert len(report.updated_issue.interventions) == 1
    outcome = report.updated_issue.interventions[0]
    assert outcome.fresh_transfer
    assert "candidate:failed-a" in outcome.note
    assert "candidate:harmful-b" in outcome.note
    assert len(report.artifact_hash) == 64


def test_shadow_development_trial_rejects_prebaked_or_unfrozen_discriminator_chronology():
    case = _case()
    bad = FrozenObservedFailureCase(
        case.case_id,
        case.mechanic_id,
        case.subject_revision_hash,
        case.evaluation_epoch_id,
        case.split_id,
        case.issue,
        case.observed_failure_artifact_hash,
        case.discriminator_artifact_hash,
        False,
        False,
        case.negative_alternative_ids,
    )
    report = ShadowDevelopmentTrialRunner(_Controller(_cycle())).run(bad)
    assert not report.process_demonstrated
    assert "discriminator_preceded_observed_failure" in report.blockers
    assert "discriminator_not_frozen_before_candidate" in report.blockers


def test_research_open_does_not_count_as_consequential_development_cycle():
    report = ShadowDevelopmentTrialRunner(
        _Controller(_cycle(status=SelfDrivingCycleStatus.RESEARCH_OPEN))
    ).run(_case())
    assert not report.process_demonstrated
    assert "development_cycle_stopped_before_candidate_execution" in report.blockers
    assert "development_cycle_missing_change_control" in report.blockers
