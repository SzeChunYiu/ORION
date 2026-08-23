import os
import subprocess
import sys
from pathlib import Path

from orion.core.problem import Problem
from orion.core.search import SearchQuery, SearchRouteKind
from orion.engine.mechanical_planner import MechanicalFirstPlanner
from orion.engine.mechanical_questions import (
    FAILURE_PATTERN_QUESTION_ID_SCHEME,
    MechanicalProblemContext,
    ProblemQuestionKind,
    failure_pattern_question_id,
    generate_problem_questions,
)
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
    assert f":{FAILURE_PATTERN_QUESTION_ID_SCHEME}:" in transfer[0].question_id
    assert "cause" in transfer[0].question.lower()
    assert "fresh variation" in transfer[0].question.lower()
    assert not transfer[0].route_kind


def test_uncovered_nearest_work_creates_donor_envelope_question() -> None:
    problem = Problem("task:donor-envelope", "Generalize a strong prior mechanism.")
    context = MechanicalProblemContext(
        nearest_work_donor_ids=("SAGE:2606.31478", "donor:already-enveloped"),
        enveloped_donor_ids=("donor:already-enveloped",),
    )

    questions = generate_problem_questions(problem, context)
    envelope = [item for item in questions if item.kind is ProblemQuestionKind.DONOR_ENVELOPE]

    assert len(envelope) == 1
    assert "SAGE:2606.31478" in envelope[0].question
    assert "donor:already-enveloped" not in envelope[0].question
    assert "conservative embedding" in envelope[0].question
    assert "ideal donor product" in envelope[0].question
    assert envelope[0].route_kind is SearchRouteKind.LITERATURE_BRIDGE


def test_enveloped_nearest_work_does_not_repeat_donor_envelope_question() -> None:
    problem = Problem("task:donor-envelope-closed", "Use an absorbed donor.")
    context = MechanicalProblemContext(
        nearest_work_donor_ids=("donor:closed",),
        enveloped_donor_ids=("donor:closed",),
    )

    questions = generate_problem_questions(problem, context)

    assert all(item.kind is not ProblemQuestionKind.DONOR_ENVELOPE for item in questions)


def test_failure_pattern_question_id_is_stable_across_process_hash_seeds():
    code = (
        "from orion.engine.mechanical_questions import failure_pattern_question_id;"
        "print(failure_pattern_question_id("
        "'task:parent-domain',"
        "('coverage-open','parent-domain-miss'),"
        "(('mask-b',),('mask-a',))))"
    )
    observed = []
    repository_src = str(Path(__file__).resolve().parents[3] / "src")
    for seed in ("1", "2"):
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = seed
        env["PYTHONPATH"] = os.pathsep.join(
            item for item in (repository_src, env.get("PYTHONPATH", "")) if item
        )
        observed.append(
            subprocess.check_output([sys.executable, "-c", code], env=env, text=True).strip()
        )
    local = failure_pattern_question_id(
        "task:parent-domain",
        ("parent-domain-miss", "coverage-open"),
        (("mask-a",), ("mask-b",)),
    )
    assert observed == [local, local]


def test_failure_pattern_question_id_is_canonical_and_sensitive_to_content():
    base = failure_pattern_question_id(
        "task:parent-domain",
        ("parent-domain-miss", "coverage-open"),
        (("mask-a",), ("mask-b",)),
    )
    reordered = failure_pattern_question_id(
        "task:parent-domain",
        ("coverage-open", "parent-domain-miss"),
        (("mask-b",), ("mask-a",)),
    )
    changed_signature = failure_pattern_question_id(
        "task:parent-domain",
        ("retrieval-miss", "coverage-open"),
        (("mask-a",), ("mask-b",)),
    )
    changed_variation = failure_pattern_question_id(
        "task:parent-domain",
        ("parent-domain-miss", "coverage-open"),
        (("mask-a",), ("mask-c",)),
    )

    assert base == reordered
    assert len({base, changed_signature, changed_variation}) == 3
    scheme, digest = base.rsplit(":", 2)[-2:]
    assert scheme == FAILURE_PATTERN_QUESTION_ID_SCHEME
    assert len(digest) == 64
    assert all(character in "0123456789abcdef" for character in digest)


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
