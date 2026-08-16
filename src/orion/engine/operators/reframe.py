from __future__ import annotations

from dataclasses import replace

from orion.core.history import NegativeHistoryEntry
from orion.core.problem import Problem
from orion.core.residuals import Residual, Responsibility
from orion.core.state import OrionState
from orion.engine.contracts import OperatorResult
from orion.engine.cycle import (
    CycleOperator,
    Transition,
    local_reframe_allowed,
    revision_allowed,
)
from orion.providers.reasoner.base import Diagnosis, ReframeProposal, ResearchReasoner


class ReframeOperator:
    operator_id = "REFRAME.v1"

    def __init__(self, reasoner: ResearchReasoner) -> None:
        self._reasoner = reasoner

    def run(
        self,
        residual: Residual,
        diagnosis: Diagnosis,
        problem: Problem,
        state: OrionState,
    ) -> OperatorResult[ReframeProposal]:
        if not revision_allowed(diagnosis.responsibilities):
            raise ValueError("reframe blocked: responsibility remains ambiguous")
        responsibility = diagnosis.responsibilities[0]
        if responsibility in {Responsibility.METHOD, Responsibility.EVALUATOR}:
            raise PermissionError("method/evaluator reframing requires the protected Self-ORION development gate")
        if not local_reframe_allowed(responsibility):
            raise ValueError(
                "reframe blocked: diagnosed responsibility requires acquisition/execution repair, "
                "not a formulation rewrite"
            )

        proposal = self._reasoner.propose_reframe(residual, diagnosis, problem, state)
        universe = state.search_universe
        changed: list[str] = []

        if proposal.add_domain_ids:
            universe = universe.activate_domains(proposal.add_domain_ids)
            changed.append("W.ACTIVE_DOMAINS")
        if proposal.add_representation_ids:
            universe = universe.add_representations(proposal.add_representation_ids)
            changed.append("W.REPRESENTATIONS")

        history_entry = NegativeHistoryEntry(
            entry_id=f"history:{residual.residual_id}:{state.epoch}",
            failure_class=residual.kind.value,
            description=(
                f"Observed residual {residual.residual_id}; diagnosis={responsibility.value}; "
                f"reframe={proposal.note or 'no prose note'}"
            ),
            residual_id=residual.residual_id,
        )
        knowledge = replace(
            state.knowledge,
            negative_history=(*state.knowledge.negative_history, history_entry),
        )
        next_state = replace(state, knowledge=knowledge, search_universe=universe)
        transition = Transition(
            operator=CycleOperator.REFRAME,
            input_epoch=state.epoch,
            output_epoch=state.epoch,
            residual_ids=(residual.residual_id,),
            changed_coordinates=tuple(changed),
        )
        return OperatorResult(next_state, proposal, transition)
