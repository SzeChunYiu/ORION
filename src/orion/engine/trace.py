from __future__ import annotations

from dataclasses import dataclass

from orion.engine.cycle import CycleOperator, Transition


@dataclass(frozen=True)
class TraceEvent:
    operator: CycleOperator
    epoch: int
    summary: str
    transition: Transition


@dataclass(frozen=True)
class SolveTrace:
    trace_id: str
    events: tuple[TraceEvent, ...]

    @property
    def operator_sequence(self) -> tuple[CycleOperator, ...]:
        return tuple(event.operator for event in self.events)
