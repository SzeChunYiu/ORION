from __future__ import annotations

from dataclasses import replace

from orion.core.claims import ClaimAuthority
from orion.core.problem import Problem
from orion.core.residuals import Residual, ResidualKind, Responsibility
from orion.core.state import OrionState
from orion.engine.contracts import OperatorResult
from orion.engine.cycle import CycleOperator, Transition


class DetectOperator:
    operator_id = "DETECT.v1"

    def run(self, problem: Problem, state: OrionState) -> OperatorResult[tuple[Residual, ...]]:
        residuals: list[Residual] = []

        unsearched_domains = tuple(
            domain
            for domain in state.search_universe.candidate_domain_ids
            if domain not in state.search_universe.searched_domain_ids
        )
        if unsearched_domains:
            residuals.append(
                Residual(
                    residual_id=f"residual:search-coverage:{state.epoch}",
                    kind=ResidualKind.SEARCH_COVERAGE_FAILURE,
                    description=(
                        "Absorbed knowledge exposed relevant domains that have not yet been searched: "
                        + ", ".join(unsearched_domains)
                    ),
                    candidate_responsibilities=(Responsibility.SEARCH, Responsibility.ROUTING),
                    metadata=(("domain_ids", ",".join(unsearched_domains)),),
                )
            )
        else:
            verified = [claim for claim in state.knowledge.claims if claim.authority is ClaimAuthority.VERIFIED]
            if not verified:
                residuals.append(
                    Residual(
                        residual_id=f"residual:missing-evidence:{state.epoch}",
                        kind=ResidualKind.MISSING_EVIDENCE,
                        description="No verified claim currently supports an answer.",
                        candidate_responsibilities=(Responsibility.EVIDENCE,),
                    )
                )

        claim_ids = {claim.claim_id for claim in state.knowledge.claims}
        for claim in state.knowledge.claims:
            for other in claim.contradicts_claim_ids:
                if other in claim_ids:
                    residuals.append(
                        Residual(
                            residual_id=f"residual:contradiction:{claim.claim_id}:{other}",
                            kind=ResidualKind.CONTRADICTION,
                            description=f"Claims {claim.claim_id} and {other} are marked contradictory.",
                            candidate_responsibilities=(Responsibility.REPRESENTATION, Responsibility.EVIDENCE),
                        )
                    )

        knowledge = replace(state.knowledge, residuals=tuple(residuals))
        next_state = replace(state, knowledge=knowledge)
        transition = Transition(
            operator=CycleOperator.DETECT,
            input_epoch=state.epoch,
            output_epoch=state.epoch,
            residual_ids=tuple(residual.residual_id for residual in residuals),
            changed_coordinates=("K.RESIDUALS",),
        )
        return OperatorResult(next_state, tuple(residuals), transition)
