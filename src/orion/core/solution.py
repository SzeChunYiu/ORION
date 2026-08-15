from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SolutionStatus(str, Enum):
    SOLVED_VERIFIED = "SOLVED_VERIFIED"
    PROVISIONAL = "PROVISIONAL"
    BLOCKED = "BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class Solution:
    problem_id: str
    status: SolutionStatus
    answer: str
    evidence_ids: tuple[str, ...] = ()
    residual_ids: tuple[str, ...] = ()
    iterations: int = 0
    trace_id: str | None = None

    def __post_init__(self) -> None:
        if not self.problem_id.strip() or not self.answer.strip():
            raise ValueError("solution requires problem identity and a nonempty answer")
        if self.iterations < 0:
            raise ValueError("solution iterations cannot be negative")
        if self.status is SolutionStatus.SOLVED_VERIFIED and not self.evidence_ids:
            raise ValueError("verified solution requires evidence")
