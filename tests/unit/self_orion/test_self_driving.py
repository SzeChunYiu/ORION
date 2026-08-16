import hashlib
from types import SimpleNamespace

from orion.core.solution import SolutionStatus
from orion.self_orion.change_control import ChangeControlVerdict
from orion.self_orion.development_driver import SelfOrionDevelopmentDriver
from orion.self_orion.research_loop import (
    DevelopmentInvestigationResult,
    FrozenFailureInvestigationContext,
)
from orion.self_orion.self_driving import (
    SelfDrivingCycleStatus,
    ShadowSelfDrivingController,
    investigation_supports_change,
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


class _ResearchLoop:
    def __init__(self, status=SolutionStatus.PROVISIONAL, evidence=("evidence:diagnosis",), residuals=("method-residual",)):
        self.status = status
        self.evidence = evidence
        self.residuals = residuals
        self.targeted_calls = []
        self.generic_calls = 0

    def run_next(self, *, limit, evaluation_epoch_id, split_id):
        self.generic_calls += 1
        return (
            DevelopmentInvestigationResult(
                work_id="empirical:SEARCH.QUERY.v0:0",
                mechanic_id="SEARCH.QUERY.v0",
                problem_id="self-orion:empirical:SEARCH.QUERY.v0:0",
                solution_status=self.status,
                evidence_ids=self.evidence,
                residual_ids=self.residuals,
                root_episode_id="episode:root",
                mechanic_episode_ids=("episode:mechanic",),
                proposal_only=True,
            ),
        )[:limit]

    def run_observed_failure(self, context, *, evaluation_epoch_id, split_id):
        self.targeted_calls.append((context, evaluation_epoch_id, split_id))
        return DevelopmentInvestigationResult(
            work_id=context.work_id,
            mechanic_id=context.mechanic_id,
            problem_id=f"self-orion:observed-failure:{context.work_id}",
            solution_status=self.status,
            evidence_ids=tuple(dict.fromkeys((*context.issue_evidence_ids, *context.discriminator_evidence_ids, *self.evidence))),
            residual_ids=self.residuals,
            root_episode_id="episode:targeted-root",
            mechanic_episode_ids=("episode:targeted-mechanic",),
            proposal_only=True,
            development_issue_id=context.development_issue_id,
            observed_failure_artifact_hash=context.observed_failure_artifact_hash,
            candidate_cause_ids=context.candidate_cause_ids,
            supported_cause_id=context.supported_cause_id,
            discriminator_artifact_hash=context.discriminator_artifact_hash,
            discriminator_evidence_ids=context.discriminator_evidence_ids,
            source_failure_episode_ids=context.failure_episode_ids,
            negative_alternative_ids=context.negative_alternative_ids,
        )


class _ChangeController:
    def __init__(self, verdict=ChangeControlVerdict.RECOMMEND_HOST_PROMOTION):
        self.verdict = verdict
        self.calls = 0
        self.requests = []

    def evaluate_change(self, request):
        self.calls += 1
        self.requests.append(request)
        return SimpleNamespace(verdict=self.verdict, reasons=(), request=request)


def _controller(research=None, change=None):
    return ShadowSelfDrivingController(
        driver=SelfOrionDevelopmentDriver(),
        research_loop=research or _ResearchLoop(),
        change_controller=change or _ChangeController(),
        base_revision="main:a5e1ed8",
    )


def _failure_context():
    return FrozenFailureInvestigationContext(
        work_id="phase2-observed-failure:one",
        mechanic_id="SEARCH.QUERY.v0",
        development_issue_id="issue:route-miss",
        issue_title="parent-domain route missed",
        symptom_signature="present-but-missed:parent-domain",
        observed_failure_artifact_hash=_digest("observed-failure"),
        candidate_cause_ids=("cause:routing", "cause:saturation"),
        supported_cause_id="cause:routing",
        discriminator_artifact_hash=_digest("discriminator"),
        discriminator_evidence_ids=("evidence:discriminator",),
        issue_evidence_ids=("evidence:failure",),
        failure_episode_ids=("episode:original-failure",),
        negative_alternative_ids=("candidate:failed",),
    )


def test_investigation_requires_evidence_residual_and_decision_sufficient_status_before_code_change():
    blocked = _ResearchLoop(status=SolutionStatus.CANNOT_CHECK).run_next(limit=1, evaluation_epoch_id="e", split_id="s")[0]
    ready, reasons = investigation_supports_change(blocked)
    assert not ready
    assert "research_not_decision_sufficient" in reasons

    no_evidence = _ResearchLoop(evidence=()).run_next(limit=1, evaluation_epoch_id="e", split_id="s")[0]
    ready, reasons = investigation_supports_change(no_evidence)
    assert not ready
    assert "no_evidence_for_change" in reasons

    supported = _ResearchLoop().run_next(limit=1, evaluation_epoch_id="e", split_id="s")[0]
    assert investigation_supports_change(supported) == (True, ())


def test_assembled_controller_derives_shadow_architecture_from_observed_surfaces():
    controller = _controller()
    evidence = controller.architecture_evidence()
    assert evidence.structural_open_questions == 0
    assert evidence.graph_defect_count == 0
    assert evidence.mechanical_work_item_count > 0
    assert evidence.component_artifact_ids
    assert evidence.protected_boundary_artifact_ids
    assert evidence.failure_history_artifact_ids
    assert not evidence.self_merge_capability_present
    assert controller.shadow_self_driving_ready


def test_self_driving_cycle_researches_proposes_evaluates_and_only_recommends_host_promotion():
    change = _ChangeController()
    controller = _controller(change=change)
    result = controller.run_cycle(limit=1, evaluation_epoch_id="epoch:frozen", split_id="split:development")[0]
    assert result.development_state.after.open_question_count == 0
    assert result.development_state.before.open_question_count > 0
    assert result.development_state.structurally_closed_questions == result.development_state.before.open_question_count
    assert result.development_state.answer_record_count == result.development_state.before.open_question_count
    assert result.status is SelfDrivingCycleStatus.HOST_PROMOTION_RECOMMENDED
    assert change.calls == 1
    assert not result.self_merge_authorized
    assert result.change_control is not None


def test_observed_failure_cycle_never_falls_back_to_generic_frontier_work():
    research = _ResearchLoop()
    change = _ChangeController()
    context = _failure_context()
    result = _controller(research=research, change=change).run_observed_failure(
        context,
        evaluation_epoch_id="epoch:frozen",
        split_id="split:fresh",
    )

    assert research.generic_calls == 0
    assert len(research.targeted_calls) == 1
    assert result.investigation.observed_failure_artifact_hash == context.observed_failure_artifact_hash
    assert result.investigation.supported_cause_id == context.supported_cause_id
    assert change.calls == 1
    request = change.requests[0]
    assert request.observed_failure_bound
    assert request.development_issue_id == context.development_issue_id
    assert request.observed_failure_artifact_hash == context.observed_failure_artifact_hash
    assert request.discriminator_artifact_hash == context.discriminator_artifact_hash
    assert "episode:original-failure" in request.failure_episode_ids
    assert request.negative_alternative_ids == context.negative_alternative_ids
    assert result.status is SelfDrivingCycleStatus.HOST_PROMOTION_RECOMMENDED
    assert not result.self_merge_authorized


def test_meta_overfit_is_not_collapsed_into_generic_candidate_status():
    change = _ChangeController(verdict=ChangeControlVerdict.META_OVERFIT)
    result = _controller(change=change).run_cycle(limit=1)[0]
    assert result.status is SelfDrivingCycleStatus.META_OVERFIT
    assert not result.self_merge_authorized


def test_cannot_check_research_stops_before_implementation_search():
    change = _ChangeController()
    controller = _controller(
        research=_ResearchLoop(status=SolutionStatus.CANNOT_CHECK, evidence=(), residuals=("provider-unavailable",)),
        change=change,
    )
    result = controller.run_cycle(limit=1)[0]
    assert result.status is SelfDrivingCycleStatus.RESEARCH_OPEN
    assert result.change_control is None
    assert change.calls == 0
    assert not result.self_merge_authorized
