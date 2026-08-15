from orion.core.problem import Problem
from orion.engine.mechanical_questions import MechanicalProblemContext, ProblemQuestionKind
from orion.runtime.mechanical_control import MechanicalControlRuntime


def test_mechanical_control_runtime_plans_without_llm_or_retrieval_provider():
    runtime = MechanicalControlRuntime()
    result = runtime.plan(
        Problem("task:no-llm", "What should ORION investigate next?"),
        MechanicalProblemContext(),
    )
    kinds = {item.kind for item in result.plan.questions}
    assert ProblemQuestionKind.PARENT_DISCIPLINE in kinds
    assert ProblemQuestionKind.SEARCH_COVERAGE in kinds
    assert ProblemQuestionKind.VERIFICATION in kinds
    assert result.plan.mechanical_queries
    assert result.episode_count == 0
