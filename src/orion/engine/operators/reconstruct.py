from __future__ import annotations

from dataclasses import replace

from orion.core.claims import ClaimAuthority
from orion.core.portrait import GlobalPortrait
from orion.core.problem import Problem
from orion.core.state import OrionState
from orion.engine.contracts import OperatorResult
from orion.engine.cycle import CycleOperator, Transition
from orion.providers.reasoner.base import ResearchReasoner


class ReconstructOperator:
    operator_id = "RECONSTRUCT.v1"

    def __init__(self, reasoner: ResearchReasoner) -> None:
        self._reasoner = reasoner

    def run(self, problem: Problem, state: OrionState) -> OperatorResult[GlobalPortrait]:
        summary = self._reasoner.reconstruct(problem, state)
        portrait = GlobalPortrait(
            portrait_id=f"portrait:{problem.problem_id}:{state.epoch}",
            summary=summary,
            claim_ids=tuple(claim.claim_id for claim in state.knowledge.claims),
            verified_claim_ids=tuple(
                claim.claim_id
                for claim in state.knowledge.claims
                if claim.authority is ClaimAuthority.VERIFIED
            ),
            unresolved_residual_ids=state.knowledge.residual_ids,
            source_projection_ids=state.knowledge.source_projection_ids,
            representation_mapping_ids=state.knowledge.representation_mapping_ids,
        )
        knowledge = replace(state.knowledge, portraits=(*state.knowledge.portraits, portrait))
        next_state = replace(state, knowledge=knowledge)
        transition = Transition(
            operator=CycleOperator.RECONSTRUCT,
            input_epoch=state.epoch,
            output_epoch=state.epoch,
            changed_coordinates=("K.PORTRAIT",),
        )
        return OperatorResult(next_state, portrait, transition)
