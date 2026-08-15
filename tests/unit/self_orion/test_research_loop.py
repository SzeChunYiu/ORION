from types import SimpleNamespace

from orion.core.solution import SolutionStatus
from orion.self_orion.development_driver import (
    DevelopmentKnowledgeClass,
    EmpiricalWorkItem,
)
from orion.self_orion.research_loop import ShadowSelfOrionResearchLoop, empirical_work_to_problem


class _Driver:
    def plan_empirical_work(self, *, limit):
        return (
            EmpiricalWorkItem(
                "empirical:SEARCH.QUERY.v0:0",
                "SEARCH.QUERY.v0",
                "fresh ORION conformance on hidden retrieval tasks",
                DevelopmentKnowledgeClass.LIVE_EVIDENCE,
                8,
                "needs evidence",
            ),
        )[:limit]


class _Runtime:
    def solve(self, problem, *, variation_signature, evaluation_epoch_id, split_id):
        assert problem.problem_id.startswith("self-orion:")
        assert variation_signature[0] == "self-orion-shadow"
        return SimpleNamespace(
            solution=SimpleNamespace(
                status=SolutionStatus.CANNOT_CHECK,
                evidence_ids=("evidence:trial",),
                residual_ids=("live-provider-needed",),
            ),
            experience_episode_id="episode:root",
            mechanic_experience_episode_ids=("episode:mechanic",),
        )


def test_empirical_work_becomes_fail_closed_scoped_problem():
    item = _Driver().plan_empirical_work(limit=1)[0]
    problem = empirical_work_to_problem(item)
    assert item.mechanic_id in problem.question
    assert "OPEN/CANNOT_CHECK" in problem.question
    assert "do not grant method/scientific promotion authority" in problem.success_criteria


def test_shadow_research_loop_selects_and_executes_next_work_but_keeps_result_proposal_only():
    result = ShadowSelfOrionResearchLoop(_Runtime(), driver=_Driver()).run_next(limit=1)[0]
    assert result.solution_status is SolutionStatus.CANNOT_CHECK
    assert result.root_episode_id == "episode:root"
    assert result.mechanic_episode_ids == ("episode:mechanic",)
    assert result.proposal_only
