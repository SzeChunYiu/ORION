import hashlib
import json
from types import SimpleNamespace

import pytest

from orion.core.solution import SolutionStatus
from orion.self_orion.change_control import ChangeControlVerdict
from orion.self_orion.development_trial import (
    FrozenObservedFailureCase,
    ShadowDevelopmentTrialReport,
)
from orion.self_orion.development_trial_io import (
    load_development_trial_report_v2,
    write_development_trial_report_v2,
)
from orion.self_orion.issue_state import (
    DevelopmentIssue,
    InterventionOutcome,
    InterventionOutcomeKind,
)
from orion.self_orion.self_driving import SelfDrivingCycleStatus


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def _canonical_hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _report() -> ShadowDevelopmentTrialReport:
    issue = DevelopmentIssue(
        issue_id="issue:route-miss",
        title="Parent-domain route missed",
        symptom_signature="present-but-missed:parent-domain",
        failure_episode_ids=("episode:failure",),
        evidence_ids=("evidence:failure",),
    ).propose_causes(("cause:routing", "cause:saturation"))
    issue = issue.support_cause(
        "cause:routing",
        discriminator_evidence_ids=("evidence:discriminator",),
    )
    case = FrozenObservedFailureCase(
        case_id="case:one",
        mechanic_id="SEARCH.QUERY.v0",
        subject_revision_hash=_digest("subject"),
        evaluation_epoch_id="epoch:frozen",
        split_id="split:fresh",
        issue=issue,
        observed_failure_artifact_hash=_digest("observed-failure"),
        discriminator_artifact_hash=_digest("discriminator"),
        observed_failure_before_discriminator=True,
        discriminator_frozen_before_candidate=True,
        negative_alternative_ids=("candidate:failed",),
    )
    investigation = SimpleNamespace(
        work_id="phase2-observed-failure:case:one",
        mechanic_id=case.mechanic_id,
        problem_id="self-orion:observed-failure:case:one",
        solution_status=SolutionStatus.PROVISIONAL,
        evidence_ids=("evidence:failure", "evidence:discriminator", "evidence:diagnosis"),
        residual_ids=("residual:routing",),
        root_episode_id="episode:investigation",
        mechanic_episode_ids=("episode:mechanic",),
        proposal_only=True,
        development_issue_id=issue.issue_id,
        observed_failure_artifact_hash=case.observed_failure_artifact_hash,
        candidate_cause_ids=issue.candidate_cause_ids,
        supported_cause_id=issue.supported_cause_id,
        discriminator_artifact_hash=case.discriminator_artifact_hash,
        discriminator_evidence_ids=issue.discriminator_evidence_ids,
        source_failure_episode_ids=issue.failure_episode_ids,
        negative_alternative_ids=case.negative_alternative_ids,
    )
    request = SimpleNamespace(
        request_id="change:case:one",
        mechanic_id=case.mechanic_id,
        base_revision="main:subject",
        evidence_ids=investigation.evidence_ids,
        failure_episode_ids=("episode:failure", "episode:mechanic"),
        development_issue_id=issue.issue_id,
        observed_failure_artifact_hash=case.observed_failure_artifact_hash,
        candidate_cause_ids=issue.candidate_cause_ids,
        supported_cause_id=issue.supported_cause_id,
        discriminator_artifact_hash=case.discriminator_artifact_hash,
        discriminator_evidence_ids=issue.discriminator_evidence_ids,
        negative_alternative_ids=case.negative_alternative_ids,
        observed_failure_bound=True,
    )
    proposal = SimpleNamespace(
        proposal_id="proposal:one",
        request_id=request.request_id,
        base_revision=request.base_revision,
        patch_artifact_hash=_digest("patch"),
    )
    execution = SimpleNamespace(
        receipt_id="execution:one",
        candidate_revision_hash=_digest("candidate"),
        artifact_ids=("artifact:candidate",),
    )
    assurance = SimpleNamespace(
        receipt_id="assurance:one",
        evaluator_artifact_hash=_digest("evaluator"),
        evaluation_epoch_id=case.evaluation_epoch_id,
        development_delta=0.2,
        fresh_assurance_delta=0.1,
        blocking_invariants_passed=True,
        evaluator_frozen_before_candidate=True,
        fresh_split=True,
        resource_matched=True,
    )
    control = SimpleNamespace(
        request=request,
        proposal=proposal,
        execution=execution,
        assurance=assurance,
        verdict=ChangeControlVerdict.RECOMMEND_HOST_PROMOTION,
        reasons=(),
        self_merge_authorized=False,
    )
    cycle = SimpleNamespace(
        status=SelfDrivingCycleStatus.HOST_PROMOTION_RECOMMENDED,
        investigation=investigation,
        change_control=control,
        self_merge_authorized=False,
    )
    outcome = InterventionOutcome(
        intervention_id="intervention:one",
        candidate_id=proposal.proposal_id,
        kind=InterventionOutcomeKind.IMPROVED,
        evidence_ids=(assurance.receipt_id, execution.receipt_id),
        episode_ids=("episode:failure", "episode:mechanic"),
        fresh_transfer=True,
        note="causally bound Phase-2 trial",
    )
    return ShadowDevelopmentTrialReport(
        case=case,
        cycle=cycle,
        updated_issue=issue.record_intervention(outcome),
        blockers=(),
    )


def test_development_trial_v2_roundtrips_and_recomputes_process(tmp_path):
    report = _report()
    path = tmp_path / "development-v2.json"
    write_development_trial_report_v2(report, path)
    loaded = load_development_trial_report_v2(path)
    assert loaded.artifact_hash == report.artifact_hash
    assert loaded.process_demonstrated
    assert loaded.blockers == ()
    assert loaded.case.subject_revision_hash == report.case.subject_revision_hash
    assert (
        loaded.cycle.change_control.assurance.evaluator_artifact_hash
        == report.cycle.change_control.assurance.evaluator_artifact_hash
    )
    assert not loaded.self_merge_authorized


def test_development_trial_v2_rejects_rehashed_wrong_failure_identity(tmp_path):
    path = tmp_path / "development-v2.json"
    write_development_trial_report_v2(_report(), path)
    raw = json.loads(path.read_text())
    raw["artifact_payload"]["case"]["observed_failure_artifact_hash"] = _digest(
        "substituted-failure"
    )
    raw["artifact_hash"] = _canonical_hash(raw["artifact_payload"])
    without_document = dict(raw)
    without_document.pop("document_hash")
    raw["document_hash"] = _canonical_hash(without_document)
    path.write_text(json.dumps(raw))

    loaded = load_development_trial_report_v2(path)
    assert not loaded.process_demonstrated
    assert "development_cycle_failure_artifact_mismatch" in loaded.blockers
    assert "development_request_failure_artifact_mismatch" in loaded.blockers


def test_phase2_closure_loader_rejects_legacy_development_v1(tmp_path):
    path = tmp_path / "development-v1.json"
    path.write_text(json.dumps({"schema": "ShadowDevelopmentTrialReport.v1"}))
    with pytest.raises(ValueError, match="ShadowDevelopmentTrialReport.v2"):
        load_development_trial_report_v2(path)
