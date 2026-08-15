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
