from __future__ import annotations

from dataclasses import dataclass

from orion.core.problem import Problem
from orion.core.search import SearchQuery
from orion.engine.mechanical_planner import MechanicalFirstPlanner, MechanicalResearchPlan
from orion.engine.mechanical_questions import MechanicalProblemContext
from orion.experience.model import TaskEpisode
from orion.providers.experience.base import ExperienceStore


@dataclass(frozen=True)
class MechanicalControlResult:
    plan: MechanicalResearchPlan
    episode_count: int


class MechanicalControlRuntime:
    """Model-free control/question surface for ORION.

    It derives research-control questions and provider-neutral search queries from
    typed state plus immutable experience. Semantic models may supply supplemental
    queries, but are not required for the control plan itself.
    """

    def __init__(self, *, experience_store: ExperienceStore | None = None) -> None:
        self._planner = MechanicalFirstPlanner()
        self._experience_store = experience_store

    def plan(
        self,
        problem: Problem,
        context: MechanicalProblemContext,
        *,
        supplemental_queries: tuple[SearchQuery, ...] = (),
    ) -> MechanicalControlResult:
        episodes: tuple[TaskEpisode, ...] = ()
        if self._experience_store is not None:
            episodes = tuple(
                item for item in self._experience_store.episodes() if item.task_id == problem.problem_id
            )
        plan = self._planner.plan(
            problem,
            context,
            episodes=episodes,
            supplemental_queries=supplemental_queries,
        )
        return MechanicalControlResult(plan=plan, episode_count=len(episodes))
