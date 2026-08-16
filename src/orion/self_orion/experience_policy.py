from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from orion.experience.model import EpisodeOutcome, TaskEpisode
from orion.self_orion.development_driver import EmpiricalWorkItem


@dataclass(frozen=True)
class MechanicExperienceStatistic:
    mechanic_id: str
    matched_episode_ids: tuple[str, ...]
    successes: int
    partial_successes: int
    failures: int
    blocked: int
    cannot_check: int
    mean_cost_units: float
    smoothed_success_rate: float
    smoothed_failure_rate: float


@dataclass(frozen=True)
class ExperienceConditionedWork:
    work: EmpiricalWorkItem
    statistic: MechanicExperienceStatistic
    exploration_bonus: float
    adjusted_priority: float
    reasons: tuple[str, ...]


def mechanic_experience_statistic(
    mechanic_id: str,
    episodes: tuple[TaskEpisode, ...],
) -> MechanicExperienceStatistic:
    matched = tuple(item for item in episodes if item.mechanic_id == mechanic_id)
    successes = sum(item.outcome is EpisodeOutcome.SUCCESS for item in matched)
    partial = sum(item.outcome is EpisodeOutcome.PARTIAL_SUCCESS for item in matched)
    failures = sum(item.outcome is EpisodeOutcome.FAILURE for item in matched)
    blocked = sum(item.outcome is EpisodeOutcome.BLOCKED for item in matched)
    cannot = sum(item.outcome is EpisodeOutcome.CANNOT_CHECK for item in matched)
    costs = tuple(item.cost_units for item in matched if item.cost_units is not None)
    mean_cost = sum(costs) / len(costs) if costs else 0.0
    n = len(matched)
    success_rate = (successes + 0.5 * partial + 1.0) / (n + 2.0)
    failure_rate = (failures + blocked + cannot + 0.5 * partial + 1.0) / (n + 2.0)
    return MechanicExperienceStatistic(
        mechanic_id=mechanic_id,
        matched_episode_ids=tuple(item.episode_id for item in matched),
        successes=successes,
        partial_successes=partial,
        failures=failures,
        blocked=blocked,
        cannot_check=cannot,
        mean_cost_units=mean_cost,
        smoothed_success_rate=success_rate,
        smoothed_failure_rate=failure_rate,
    )


def rank_empirical_work_with_experience(
    work_items: tuple[EmpiricalWorkItem, ...],
    episodes: tuple[TaskEpisode, ...],
) -> tuple[ExperienceConditionedWork, ...]:
    """Use experience as a scheduling prior, never as method/scientific authority.

    Repeated failures increase investigation priority; repeated successes lower it
    slightly; underexplored mechanics receive an exploration bonus. This is an
    auditable bootstrap heuristic reconstructed from RAKL experience_policy, not a
    learned optimal controller.
    """

    ranked: list[ExperienceConditionedWork] = []
    cache: dict[str, MechanicExperienceStatistic] = {}
    for work in work_items:
        stat = cache.setdefault(
            work.mechanic_id,
            mechanic_experience_statistic(work.mechanic_id, episodes),
        )
        n = len(stat.matched_episode_ids)
        exploration = 1.0 / sqrt(n + 1.0)
        adjusted = (
            float(work.priority)
            + 2.0 * stat.smoothed_failure_rate
            - 1.0 * stat.smoothed_success_rate
            + exploration
        )
        ranked.append(
            ExperienceConditionedWork(
                work=work,
                statistic=stat,
                exploration_bonus=exploration,
                adjusted_priority=adjusted,
                reasons=(
                    f"base_priority:{work.priority}",
                    f"matched_episodes:{n}",
                    f"smoothed_success_rate:{stat.smoothed_success_rate:.6f}",
                    f"smoothed_failure_rate:{stat.smoothed_failure_rate:.6f}",
                    "experience_changes_scheduling_priority_only",
                ),
            )
        )
    ranked.sort(key=lambda item: (-item.adjusted_priority, item.work.mechanic_id, item.work.work_id))
    return tuple(ranked)


__all__ = [
    "ExperienceConditionedWork",
    "MechanicExperienceStatistic",
    "mechanic_experience_statistic",
    "rank_empirical_work_with_experience",
]
