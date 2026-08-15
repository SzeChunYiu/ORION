from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from orion.core.state import OrionState
from orion.engine.cycle import Transition

T = TypeVar("T")


@dataclass(frozen=True)
class OperatorResult(Generic[T]):
    state: OrionState
    output: T
    transition: Transition

    def __post_init__(self) -> None:
        self.transition.validate()
