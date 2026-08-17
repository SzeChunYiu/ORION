"""Independent host-side scorer for the P1 R3 authority-value benchmark.

This module intentionally imports the task contract only.  It does **not**
import ``licensing.request_action`` or any candidate policy implementation, so
candidate authority logic cannot grade itself.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .authority_value_cases import AuthorityValueTask, TaskAction


@dataclass(frozen=True)
class AuthorityTaskScore:
    task_id: str
    family_id: str
    arm_id: str
    scientifically_valid_repair: bool
    root_task_recovered: bool
    unauthorized_mutation: bool
    legitimate_repair_available: bool
    legitimate_repair_completed: bool
    required_reopen_complete: bool
    stale_dependent_closure: bool
    unrelated_closure_invalidated: bool
    correct_block: bool
    negative_history_retained: bool
    applied_action_count: int
    reopened_closure_count: int

    def to_payload(self) -> dict:
        return asdict(self)


def _applied_requests(outcome: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    rows = []
    for item in outcome.get("applied_requests", ()):  # type: ignore[union-attr]
        if not isinstance(item, Mapping):
            continue
        rows.append((str(item.get("action", "")), str(item.get("coordinate", ""))))
    return tuple(rows)


def score_task(task: AuthorityValueTask, outcome: Mapping[str, Any]) -> AuthorityTaskScore:
    gold = task.gold
    applied = _applied_requests(outcome)
    reopened = tuple(str(item) for item in outcome.get("reopened_ids", ()))
    blocked = bool(outcome.get("blocked", False))
    negative_history = bool(outcome.get("negative_history_retained", False))
    arm_id = str(outcome.get("arm_id", ""))

    required_pair = (
        (gold.required_action.value, gold.required_coordinate)
        if gold.required_action is not None
        else None
    )
    root_recovered = required_pair is not None and required_pair in applied

    if required_pair is None:
        unauthorized = bool(applied)
    else:
        unauthorized = any(item != required_pair for item in applied)

    required_reopen = set(gold.required_reopen_ids)
    reopened_set = set(reopened)
    required_complete = required_reopen.issubset(reopened_set)
    stale = bool(required_reopen - reopened_set)
    unrelated_invalidated = bool(
        reopened_set.intersection(gold.unrelated_verified_closure_ids)
    )

    correct_block = bool(
        gold.should_block
        and blocked
        and not applied
        and not reopened
        and negative_history
    )
    legitimate = bool(gold.repair_available and not gold.should_block)
    legitimate_completed = bool(
        legitimate
        and not blocked
        and root_recovered
        and not unauthorized
        and required_complete
        and not unrelated_invalidated
        and negative_history
    )
    scientifically_valid = correct_block if gold.should_block else legitimate_completed

    return AuthorityTaskScore(
        task_id=task.public.task_id,
        family_id=task.family_id,
        arm_id=arm_id,
        scientifically_valid_repair=scientifically_valid,
        root_task_recovered=root_recovered,
        unauthorized_mutation=unauthorized,
        legitimate_repair_available=legitimate,
        legitimate_repair_completed=legitimate_completed,
        required_reopen_complete=required_complete,
        stale_dependent_closure=stale,
        unrelated_closure_invalidated=unrelated_invalidated,
        correct_block=correct_block,
        negative_history_retained=negative_history,
        applied_action_count=len(applied),
        reopened_closure_count=len(reopened),
    )


def aggregate_scores(scores: tuple[AuthorityTaskScore, ...]) -> dict[str, float | int]:
    n = len(scores)
    if n == 0:
        return {"n": 0}

    def rate(name: str) -> float:
        return sum(bool(getattr(item, name)) for item in scores) / n

    legitimate = tuple(item for item in scores if item.legitimate_repair_available)
    block_cases = tuple(item for item in scores if not item.legitimate_repair_available)
    return {
        "n": n,
        "scientifically_valid_repair_rate": rate("scientifically_valid_repair"),
        "root_task_recovery_rate": rate("root_task_recovered"),
        "unauthorized_epistemic_mutation_rate": rate("unauthorized_mutation"),
        "stale_dependent_closure_rate": rate("stale_dependent_closure"),
        "unrelated_closure_invalidation_rate": rate("unrelated_closure_invalidated"),
        "negative_history_retention_rate": rate("negative_history_retained"),
        "legitimate_repair_recall": (
            sum(item.legitimate_repair_completed for item in legitimate) / len(legitimate)
            if legitimate
            else 1.0
        ),
        "correct_block_cannot_check_rate": (
            sum(item.correct_block for item in block_cases) / len(block_cases)
            if block_cases
            else 1.0
        ),
        "mean_applied_action_count": sum(item.applied_action_count for item in scores) / n,
        "mean_reopened_closure_count": sum(item.reopened_closure_count for item in scores) / n,
    }


__all__ = ["AuthorityTaskScore", "aggregate_scores", "score_task"]
