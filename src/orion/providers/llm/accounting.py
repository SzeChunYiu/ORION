from __future__ import annotations

import json
from dataclasses import dataclass

from .base import LLMProvider, LLMRequest, LLMResponse


@dataclass(frozen=True)
class LLMCallObservation:
    task: str
    problem_id: str
    completed: bool


class AccountingLLMProvider:
    """Transparent LLM wrapper that records attempted calls by frozen problem id."""

    def __init__(self, delegate: LLMProvider) -> None:
        self._delegate = delegate
        self._observations: list[LLMCallObservation] = []

    @staticmethod
    def _problem_id(request: LLMRequest) -> str:
        try:
            payload = json.loads(request.user)
        except json.JSONDecodeError:
            return ""
        if not isinstance(payload, dict):
            return ""
        problem = payload.get("problem")
        if not isinstance(problem, dict):
            return ""
        problem_id = problem.get("problem_id")
        return problem_id if isinstance(problem_id, str) else ""

    def complete(self, request: LLMRequest) -> LLMResponse:
        problem_id = self._problem_id(request)
        index = len(self._observations)
        self._observations.append(
            LLMCallObservation(request.task, problem_id, completed=False)
        )
        try:
            response = self._delegate.complete(request)
        except Exception:
            raise
        else:
            self._observations[index] = LLMCallObservation(
                request.task, problem_id, completed=True
            )
            return response

    def observations(self) -> tuple[LLMCallObservation, ...]:
        return tuple(self._observations)

    def attempted_calls_for_problem(self, problem_id: str) -> int:
        return sum(
            observation.problem_id == problem_id
            for observation in self._observations
        )


__all__ = ["AccountingLLMProvider", "LLMCallObservation"]
