from __future__ import annotations

from orion.core.problem import Problem
from orion.core.residuals import Residual
from orion.core.state import OrionState
from orion.engine.contracts import OperatorResult
from orion.engine.cycle import CycleOperator, Transition
from orion.providers.reasoner.base import Diagnosis, ResearchReasoner


class DiagnoseOperator:
    operator_id = "DIAGNOSE.v1"

    def __init__(self, reasoner: ResearchReasoner) -> None:
        self._reasoner = reasoner

    def run(self, residual: Residual, problem: Problem, state: OrionState) -> OperatorResult[Diagnosis]:
        diagnosis = self._reasoner.diagnose(residual, problem, state)
        transition = Transition(
            operator=CycleOperator.DIAGNOSE,
            input_epoch=state.epoch,
            output_epoch=state.epoch,
            residual_ids=(residual.residual_id,),
        )
        return OperatorResult(state, diagnosis, transition)
