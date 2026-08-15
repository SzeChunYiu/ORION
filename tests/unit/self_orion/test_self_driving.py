from types import SimpleNamespace

from orion.core.solution import SolutionStatus
from orion.self_orion.change_control import ChangeControlVerdict
from orion.self_orion.development_driver import SelfOrionDevelopmentDriver
from orion.self_orion.research_loop import DevelopmentInvestigationResult
from orion.self_orion.self_driving import (
    SelfDrivingCycleStatus,
    ShadowSelfDrivingController,
    investigation_supports_change,
)


class _ResearchLoop:
    def __init__(self, status=SolutionStatus.PROVISIONAL, evidence=("evidence:diagnosis",), residuals=("method-residual",)):
        self.status = status
        self.evidence = evidence
        self.residuals = residuals

    def run_next(self, *, limit, evaluation_epoch_id, split_id):
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


class _ChangeController:
    def __init__(self, verdict=ChangeControlVerdict.RECOMMEND_HOST_PROMOTION):
        self.verdict = verdict
        self.calls = 0

    def evaluate_change(self, request):
        self.calls += 1
        return SimpleNamespace(verdict=self.verdict, reasons=(), request=request)


def _controller(research=None, change=None):
    return ShadowSelfDrivingController(
        driver=SelfOrionDevelopmentDriver(),
        research_loop=research or _ResearchLoop(),
        change_controller=change or _ChangeController(),
        base_revision="main:a5e1ed8",
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


def test_assembled_controller_derives_shadow_self_driving_architecture_readiness():
    controller = _controller()
    evidence = controller.architecture_evidence()
    assert evidence.structural_questions_closed
    assert evidence.graph_integrity_passed
    assert evidence.self_merge_absent
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
