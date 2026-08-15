from __future__ import annotations

from dataclasses import dataclass, replace

from orion.core.problem import Problem
from orion.core.state import OrionState
from orion.engine.contracts import OperatorResult
from orion.engine.cycle import CycleOperator, Transition


@dataclass(frozen=True)
class Frame:
    frame_id: str
    question: str
    scope: str
    success_criteria: tuple[str, ...]


class FrameOperator:
    operator_id = "FRAME.v1"

    def run(self, problem: Problem, state: OrionState) -> OperatorResult[Frame]:
        frame = Frame(
            frame_id=f"frame:{problem.problem_id}:{state.epoch}",
            question=problem.question,
            scope=problem.scope,
            success_criteria=problem.success_criteria,
        )
        universe = state.search_universe.activate_domains(problem.initial_domain_ids)
        next_state = replace(state, search_universe=universe)
        transition = Transition(
            operator=CycleOperator.FRAME,
            input_epoch=state.epoch,
            output_epoch=state.epoch,
            changed_coordinates=("FRAME",) if problem.initial_domain_ids else (),
        )
        return OperatorResult(next_state, frame, transition)
