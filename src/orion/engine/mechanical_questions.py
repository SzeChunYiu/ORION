from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum

from orion.core.problem import Problem
from orion.core.search import SearchQuery, SearchRouteKind
from orion.experience.model import TaskEpisode


FAILURE_PATTERN_QUESTION_ID_SCHEME = "failure-pattern-sha256-v1"


class ProblemQuestionKind(str, Enum):
    EVIDENCE = "EVIDENCE"
    PARENT_DISCIPLINE = "PARENT_DISCIPLINE"
    SEARCH_COVERAGE = "SEARCH_COVERAGE"
    FAILURE_DIAGNOSIS = "FAILURE_DIAGNOSIS"
    FAILURE_TRANSFER = "FAILURE_TRANSFER"
    VERIFICATION = "VERIFICATION"
    DONOR_ENVELOPE = "DONOR_ENVELOPE"
    SATURATION_CHALLENGE = "SATURATION_CHALLENGE"


@dataclass(frozen=True)
class MechanicalProblemContext:
    evidence_ids: tuple[str, ...] = ()
    residual_ids: tuple[str, ...] = ()
    active_domain_ids: tuple[str, ...] = ()
    searched_domain_ids: tuple[str, ...] = ()
    completed_route_kind_ids: tuple[str, ...] = ()
    recent_flat_rounds: int = 0
    verified_target: bool = False
    nearest_work_donor_ids: tuple[str, ...] = ()
    enveloped_donor_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class MechanicalProblemQuestion:
    question_id: str
    kind: ProblemQuestionKind
    question: str
    route_kind: SearchRouteKind | None
    action_hint: str
    blocking: bool = True


def failure_pattern_question_id(
    problem_id: str,
    signature: tuple[str, ...],
    variations: tuple[tuple[str, ...], ...],
) -> str:
    """Return a replay-stable identity for a repeated-failure question.

    The scheme tag is part of the identifier so persisted questions remain
    interpretable if the canonicalization or digest algorithm ever changes.
    Failure-signature members and the set of observed variation signatures are
    order-insensitive, while order inside one variation signature remains
    meaningful.
    """

    if not problem_id.strip():
        raise ValueError("problem id is required for failure-pattern question identity")
    canonical = {
        "signature": sorted(signature),
        "variations": [list(item) for item in sorted(variations)],
    }
    payload = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    return f"{problem_id}:failure-pattern:{FAILURE_PATTERN_QUESTION_ID_SCHEME}:{digest}"


def _repeated_failure_groups(episodes: tuple[TaskEpisode, ...]) -> tuple[tuple[tuple[str, ...], tuple[TaskEpisode, ...]], ...]:
    groups: dict[tuple[str, ...], list[TaskEpisode]] = {}
    for episode in episodes:
        if not episode.failure_signature:
            continue
        groups.setdefault(tuple(sorted(episode.failure_signature)), []).append(episode)
    repeated: list[tuple[tuple[str, ...], tuple[TaskEpisode, ...]]] = []
    for signature, items in groups.items():
        variations = {item.variation_signature for item in items}
        if len(items) >= 2 and len(variations) >= 2:
            repeated.append((signature, tuple(items)))
    return tuple(sorted(repeated, key=lambda item: item[0]))


def generate_problem_questions(
    problem: Problem,
    context: MechanicalProblemContext,
    *,
    episodes: tuple[TaskEpisode, ...] = (),
) -> tuple[MechanicalProblemQuestion, ...]:
    """Generate high-value research-control questions without an LLM planner."""

    questions: list[MechanicalProblemQuestion] = []
    prefix = problem.problem_id

    if not context.evidence_ids:
        questions.append(MechanicalProblemQuestion(
            f"{prefix}:evidence",
            ProblemQuestionKind.EVIDENCE,
            f"What observations, sources, measurements or known-answer artifacts would directly bear on: {problem.question}",
            SearchRouteKind.FUNCTION_ONLY,
            "search/acquire evidence before synthesizing a final answer",
        ))

    if not context.searched_domain_ids:
        questions.append(MechanicalProblemQuestion(
            f"{prefix}:parent-domain",
            ProblemQuestionKind.PARENT_DISCIPLINE,
            f"Which mature disciplines study the atomic operations needed to solve '{problem.question}', and what variables/mechanics would they add to the current formulation?",
            SearchRouteKind.PARENT_DISCIPLINE,
            "expand W_t with candidate parent disciplines, then search them",
        ))

    required_independent_routes = {
        SearchRouteKind.FUNCTION_ONLY.value,
        SearchRouteKind.PARENT_DISCIPLINE.value,
        SearchRouteKind.ADVERSARIAL_OMISSION.value,
    }
    if not required_independent_routes.issubset(set(context.completed_route_kind_ids)):
        missing = tuple(sorted(required_independent_routes - set(context.completed_route_kind_ids)))
        questions.append(MechanicalProblemQuestion(
            f"{prefix}:coverage",
            ProblemQuestionKind.SEARCH_COVERAGE,
            f"Why could the current search still miss important knowledge? Challenge the search basis using the missing independent route families: {missing}.",
            SearchRouteKind.ADVERSARIAL_OMISSION,
            "run missing route families; do not treat nearby-query flatness as coverage",
        ))

    if context.residual_ids:
        questions.append(MechanicalProblemQuestion(
            f"{prefix}:diagnose",
            ProblemQuestionKind.FAILURE_DIAGNOSIS,
            f"Which competing causes or responsibility layers could explain the open residuals {context.residual_ids}, and what discriminator would separate them before a high-impact reframe?",
            None,
            "construct competing diagnosis hypotheses and select a discriminator",
        ))

    for signature, group in _repeated_failure_groups(episodes):
        variations = tuple(sorted({item.variation_signature for item in group}))
        questions.append(MechanicalProblemQuestion(
            failure_pattern_question_id(prefix, signature, variations),
            ProblemQuestionKind.FAILURE_TRANSFER,
            f"The failure signature {signature} recurred across distinct variations {variations}. What cause hypothesis explains the recurrence, what observation could falsify it, and can a candidate guard survive replay plus a fresh variation?",
            None,
            "diagnose recurrence; propose lesson/guard candidate only after cause discrimination; keep promotion protected",
        ))

    if not context.verified_target:
        questions.append(MechanicalProblemQuestion(
            f"{prefix}:verification",
            ProblemQuestionKind.VERIFICATION,
            "What independent or protected artifact would verify that the current candidate answer satisfies the registered target without relying on the same generator that proposed it?",
            None,
            "bind a verification/evaluator obligation before final authority",
        ))

    uncovered_donors = tuple(
        sorted(set(context.nearest_work_donor_ids) - set(context.enveloped_donor_ids))
    )
    if uncovered_donors:
        questions.append(MechanicalProblemQuestion(
            f"{prefix}:donor-envelope",
            ProblemQuestionKind.DONOR_ENVELOPE,
            "Nearest work is reusable structure, not a claim perimeter. For the "
            f"uncovered donors {uncovered_donors}, extract their state, transitions, "
            "invariants, assumptions and failure regimes; reproduce them; construct "
            "a conservative embedding; then seek a boundary/equivalence theorem or "
            "strict-separation witness against the strongest information-matched "
            "ideal donor product.",
            SearchRouteKind.LITERATURE_BRIDGE,
            "absorb and reconstruct each donor before testing a generalized envelope; preserve donor priority and negative history",
        ))

    if context.recent_flat_rounds < 2:
        questions.append(MechanicalProblemQuestion(
            f"{prefix}:saturation",
            ProblemQuestionKind.SATURATION_CHALLENGE,
            "What would make the current saturation conclusion false? Which missing domain, representation, source family, failure variation, contradiction or processing-order perturbation could still change the answer?",
            SearchRouteKind.LITERATURE_BRIDGE,
            "continue heterogeneous challenge; bounded saturation requires repeated flatness after the last material change",
        ))

    return tuple(questions)


def search_queries_for_questions(problem: Problem, questions: tuple[MechanicalProblemQuestion, ...]) -> tuple[SearchQuery, ...]:
    queries: list[SearchQuery] = []
    for question in questions:
        if question.route_kind is None:
            continue
        queries.append(SearchQuery(
            query_id=f"mechanical:{question.question_id}",
            text=question.question,
            route_id=f"mechanical-route:{question.kind.value.lower()}",
            route_kind=question.route_kind,
        ))
    return tuple(queries)
