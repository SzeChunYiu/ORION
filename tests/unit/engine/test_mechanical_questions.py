from orion.core.problem import Problem
from orion.core.search import SearchQuery, SearchRouteKind
from orion.engine.mechanical_planner import MechanicalFirstPlanner
from orion.engine.mechanical_questions import MechanicalProblemContext, ProblemQuestionKind, generate_problem_questions
from orion.experience.model import EpisodeOutcome, TaskEpisode


def _episode(episode_id: str, variation: str) -> TaskEpisode:
    return TaskEpisode(
        episode_id=episode_id,
        task_id="task:parent-domain",
        run_id=f"run:{variation}",
        parent_run_id=None,
        evaluation_epoch_id="eval:mechanical-question-fixture",
        split_id="development",
        mechanic_id="ORION_SOLVE.v1",
        problem_signature=("find missing discipline",),
        variation_signature=(variation,),
        pre_state_hash=f"pre:{variation}",
        action_ids=("SEARCH",),
        observation_ids=("no-hit",),
        outcome=EpisodeOutcome.FAILURE,
        failure_signature=("parent-domain-miss",),
        residual_ids=("coverage-open",),
        evidence_ids=(),
        evidence_bindings=(),
        post_state_hash=f"post:{variation}",
        timestamp="2026-08-15T00:00:00+00:00",
    )


def test_problem_question_engine_asks_about_evidence_domains_coverage_verification_and_saturation_without_llm():
    problem = Problem("task:mechanical", "How should this research problem be solved?")
    questions = generate_problem_questions(problem, MechanicalProblemContext())
    kinds = {item.kind for item in questions}
    assert {
        ProblemQuestionKind.EVIDENCE,
        ProblemQuestionKind.PARENT_DISCIPLINE,
        ProblemQuestionKind.SEARCH_COVERAGE,
        ProblemQuestionKind.VERIFICATION,
        ProblemQuestionKind.SATURATION_CHALLENGE,
    } <= kinds


def test_repeated_failure_variations_create_diagnosis_transfer_question_not_automatic_guard():
    problem = Problem("task:parent-domain", "Find relevant parent disciplines.")
    context = MechanicalProblemContext(
        evidence_ids=("e:1",),
        searched_domain_ids=("research-systems",),
        completed_route_kind_ids=(
            SearchRouteKind.FUNCTION_ONLY.value,
            SearchRouteKind.PARENT_DISCIPLINE.value,
            SearchRouteKind.ADVERSARIAL_OMISSION.value,
        ),
        recent_flat_rounds=2,
        verified_target=True,
    )
    questions = generate_problem_questions(
        problem,
        context,
        episodes=(_episode("ep:a", "mask-a"), _episode("ep:b", "mask-b")),
    )
    transfer = [item for item in questions if item.kind is ProblemQuestionKind.FAILURE_TRANSFER]
    assert len(transfer) == 1
    assert "cause" in transfer[0].question.lower()
    assert "fresh variation" in transfer[0].question.lower()
    assert not transfer[0].route_kind


def test_mechanical_first_planner_preserves_required_queries_before_semantic_supplements():
    problem = Problem("task:planner", "Research a difficult question.")
    supplemental = SearchQuery(
        "semantic:q1",
        "A semantic query proposed by an LLM",
        "semantic-route",
        SearchRouteKind.CURRENT_VOCABULARY,
    )
    plan = MechanicalFirstPlanner().plan(
        problem,
        MechanicalProblemContext(),
        supplemental_queries=(supplemental,),
    )
    mechanical_kinds = {item.route_kind for item in plan.mechanical_queries}
    assert SearchRouteKind.FUNCTION_ONLY in mechanical_kinds
    assert SearchRouteKind.PARENT_DISCIPLINE in mechanical_kinds
    assert SearchRouteKind.ADVERSARIAL_OMISSION in mechanical_kinds
    assert supplemental in plan.merged_queries
    assert plan.merged_queries[: len(plan.mechanical_queries)] == plan.mechanical_queries
