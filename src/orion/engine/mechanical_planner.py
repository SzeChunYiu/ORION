from __future__ import annotations

from dataclasses import dataclass

from orion.core.problem import Problem
from orion.core.search import SearchQuery
from orion.experience.model import TaskEpisode

from .mechanical_questions import (
    MechanicalProblemContext,
    MechanicalProblemQuestion,
    generate_problem_questions,
    search_queries_for_questions,
)


@dataclass(frozen=True)
class MechanicalResearchPlan:
    questions: tuple[MechanicalProblemQuestion, ...]
    mechanical_queries: tuple[SearchQuery, ...]
    supplemental_queries: tuple[SearchQuery, ...]
    merged_queries: tuple[SearchQuery, ...]


def _deduplicate_queries(queries: tuple[SearchQuery, ...]) -> tuple[SearchQuery, ...]:
    seen: set[tuple[str, str]] = set()
    retained: list[SearchQuery] = []
    for query in queries:
        key = (query.route_kind.value, query.text.strip().casefold())
        if key in seen:
            continue
        seen.add(key)
        retained.append(query)
    return tuple(retained)


class MechanicalFirstPlanner:
    """Deterministic ORION control planner with optional semantic supplements.

    Mechanical questions are derived from observable state and experience. An LLM or
    other semantic planner may add queries, but cannot remove required mechanical
    questions/queries or promote their answers to authority.
    """

    def plan(
        self,
        problem: Problem,
        context: MechanicalProblemContext,
        *,
        episodes: tuple[TaskEpisode, ...] = (),
        supplemental_queries: tuple[SearchQuery, ...] = (),
    ) -> MechanicalResearchPlan:
        questions = generate_problem_questions(problem, context, episodes=episodes)
        mechanical_queries = search_queries_for_questions(problem, questions)
        supplemental = _deduplicate_queries(supplemental_queries)
        merged = _deduplicate_queries(mechanical_queries + supplemental)
        return MechanicalResearchPlan(
            questions=questions,
            mechanical_queries=mechanical_queries,
            supplemental_queries=supplemental,
            merged_queries=merged,
        )
