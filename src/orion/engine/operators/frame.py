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
    navigation_profile: str = ""
    navigation_plan_digest: str = ""
    atomization_digest: str = ""
    donor_registry_digest: str = ""
    active_fibre_ids: tuple[str, ...] = ()
    deferred_donor_obligation_ids: tuple[str, ...] = ()


class FrameOperator:
    operator_id = "FRAME.v1"

    def run(self, problem: Problem, state: OrionState) -> OperatorResult[Frame]:
        frame = Frame(
            frame_id=f"frame:{problem.problem_id}:{state.epoch}",
            question=problem.question,
            scope=problem.scope,
            success_criteria=problem.success_criteria,
            navigation_profile=state.method.navigation_profile,
            navigation_plan_digest=state.method.navigation_plan_digest,
            atomization_digest=state.method.atomization_digest,
            donor_registry_digest=state.method.donor_registry_digest,
            active_fibre_ids=state.method.active_fibre_ids,
            deferred_donor_obligation_ids=state.method.deferred_donor_obligation_ids,
        )
        universe = state.search_universe.activate_domains(problem.initial_domain_ids)
        next_state = replace(state, search_universe=universe)
        changed = []
        if problem.initial_domain_ids:
            changed.append("W.ACTIVE_DOMAINS")
        if state.method.navigation_plan_digest:
            changed.append("M.NAVIGATION")
        transition = Transition(
            operator=CycleOperator.FRAME,
            input_epoch=state.epoch,
            output_epoch=state.epoch,
            changed_coordinates=tuple(changed),
        )
        return OperatorResult(next_state, frame, transition)
