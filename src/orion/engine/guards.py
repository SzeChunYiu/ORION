from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from orion.core.problem import Problem
from orion.core.state import OrionState


@dataclass(frozen=True)
class MechanicGuardResult:
    passed: bool
    residual_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.passed and not self.residual_ids:
            raise ValueError("a rejected mechanic guard requires a residual")


class MechanicGuard(Protocol):
    """Host-installed executable guard evaluated outside learned text."""

    guard_id: str
    mechanic_id: str

    def evaluate(self, problem: Problem, state: OrionState) -> MechanicGuardResult: ...


@dataclass(frozen=True)
class CallableMechanicGuard:
    guard_id: str
    mechanic_id: str
    callback: Callable[[Problem, OrionState], MechanicGuardResult]

    def __post_init__(self) -> None:
        if not self.guard_id.startswith("guard:pattern:"):
            raise ValueError("mechanic guard id must bind a failure pattern")
        if not self.mechanic_id.strip():
            raise ValueError("mechanic guard target is required")

    def evaluate(self, problem: Problem, state: OrionState) -> MechanicGuardResult:
        return self.callback(problem, state)
