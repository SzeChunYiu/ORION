from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Problem:
    """A scoped problem presented to ORION."""

    problem_id: str
    question: str
    scope: str = ""
    initial_domain_ids: tuple[str, ...] = ()
    success_criteria: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.problem_id.strip():
            raise ValueError("problem_id is required")
        if not self.question.strip():
            raise ValueError("question is required")