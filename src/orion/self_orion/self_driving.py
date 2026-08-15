from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.core.solution import SolutionStatus
from orion.providers.development.base import DevelopmentChangeProvider
from orion.runtime.runtime import OrionRuntime
from orion.self_orion.change_control import (
    ChangeControlResult,
    ChangeControlVerdict,
    ProtectedDevelopmentEvaluator,
    SandboxCandidateRunner,
    SelfOrionChangeController,
    change_request_from_investigation,
)
from orion.self_orion.development_driver import DevelopmentDriveReport, SelfOrionDevelopmentDriver
from orion.self_orion.development_fibre import DevelopmentFibre, compile_development_fibre
from orion.self_orion.research_loop import DevelopmentInvestigationResult, ShadowSelfOrionResearchLoop


class SelfDrivingCycleStatus(str, Enum):
    RESEARCH_OPEN = "RESEARCH_OPEN"
    CHANGE_REJECTED = "CHANGE_REJECTED"
    CHANGE_CANDIDATE = "CHANGE_CANDIDATE"
    HOST_PROMOTION_RECOMMENDED = "HOST_PROMOTION_RECOMMENDED"


@dataclass(frozen=True)
class SelfDrivingCycleResult:
    development_state: DevelopmentDriveReport
    investigation: DevelopmentInvestigationResult
    fibre: DevelopmentFibre
    change_control: ChangeControlResult | None
    status: SelfDrivingCycleStatus
    reasons: tuple[str, ...]

    @property
    def self_merge_authorized(self) -> bool:
        return False


def investigation_supports_change(investigation: DevelopmentInvestigationResult) -> tuple[bool, tuple[str, ...]]:
    """Decide whether research evidence licenses entering implementation search.

    A failure/uncertainty is not automatically a software defect. CANNOT_CHECK and
    BLOCKED stop at research/diagnosis unless a later evidence-producing run narrows
    responsibility. A change proposal also requires evidence and a material residual.
    """

    reasons: list[str] = []
    if investigation.solution_status in {SolutionStatus.CANNOT_CHECK, SolutionStatus.BLOCKED}:
        reasons.append("research_not_decision_sufficient")
    if not investigation.evidence_ids:
        reasons.append("no_evidence_for_change")
    if not investigation.residual_ids:
        reasons.append("no_material_residual_for_change")
    return (not reasons, tuple(reasons))


class ShadowSelfDrivingController:
    """End-to-end Shadow development loop.

    Flow:
      local/RAKL structural absorption -> empirical work selection -> ORION research
      -> development fibre compilation -> evidence-gated change request -> coding
      proposal -> isolated candidate execution -> protected fresh assurance -> host
      promotion recommendation.

    The controller has no merge primitive and no authority to rewrite its evaluator.
    """

    def __init__(
        self,
        *,
        driver: SelfOrionDevelopmentDriver,
        research_loop: ShadowSelfOrionResearchLoop,
        change_controller: SelfOrionChangeController,
        base_revision: str,
    ) -> None:
        if not base_revision.strip():
            raise ValueError("base revision is required")
        self._driver = driver
        self._research_loop = research_loop
        self._change_controller = change_controller
        self._base_revision = base_revision

    @classmethod
    def from_components(
        cls,
        *,
        runtime: OrionRuntime,
        development_provider: DevelopmentChangeProvider,
        sandbox_runner: SandboxCandidateRunner,
        protected_evaluator: ProtectedDevelopmentEvaluator,
        base_revision: str,
    ) -> ShadowSelfDrivingController:
        """Compose the full Shadow driver from host-supplied workers/boundaries."""

        driver = SelfOrionDevelopmentDriver()
        return cls(
            driver=driver,
            research_loop=ShadowSelfOrionResearchLoop(runtime, driver=driver),
            change_controller=SelfOrionChangeController(
                provider=development_provider,
                runner=sandbox_runner,
                evaluator=protected_evaluator,
            ),
            base_revision=base_revision,
        )

    def run_cycle(
        self,
        *,
        limit: int = 1,
        evaluation_epoch_id: str = "self-orion:shadow-evaluation-unfrozen",
        split_id: str = "self-orion:shadow-development",
    ) -> tuple[SelfDrivingCycleResult, ...]:
        if limit < 1:
            raise ValueError("cycle limit must be positive")
        development_state = self._driver.drive_local_transfer()
        if not development_state.can_drive_next_work_mechanically:
            raise RuntimeError("structural development frontier is still open")
        cells = self._driver.local_transfer_cells()
        investigations = self._research_loop.run_next(
            limit=limit,
            evaluation_epoch_id=evaluation_epoch_id,
            split_id=split_id,
        )
        results: list[SelfDrivingCycleResult] = []
        for investigation in investigations:
            fibre = compile_development_fibre(investigation.mechanic_id, cells)
            ready, research_reasons = investigation_supports_change(investigation)
            if not ready:
                results.append(
                    SelfDrivingCycleResult(
                        development_state=development_state,
                        investigation=investigation,
                        fibre=fibre,
                        change_control=None,
                        status=SelfDrivingCycleStatus.RESEARCH_OPEN,
                        reasons=research_reasons,
                    )
                )
                continue
            request = change_request_from_investigation(
                investigation,
                fibre,
                base_revision=self._base_revision,
            )
            control = self._change_controller.evaluate_change(request)
            status = {
                ChangeControlVerdict.REJECT: SelfDrivingCycleStatus.CHANGE_REJECTED,
                ChangeControlVerdict.CANDIDATE_ONLY: SelfDrivingCycleStatus.CHANGE_CANDIDATE,
                ChangeControlVerdict.RECOMMEND_HOST_PROMOTION: SelfDrivingCycleStatus.HOST_PROMOTION_RECOMMENDED,
            }[control.verdict]
            results.append(
                SelfDrivingCycleResult(
                    development_state=development_state,
                    investigation=investigation,
                    fibre=fibre,
                    change_control=control,
                    status=status,
                    reasons=control.reasons,
                )
            )
        return tuple(results)


__all__ = [
    "SelfDrivingCycleResult",
    "SelfDrivingCycleStatus",
    "ShadowSelfDrivingController",
    "investigation_supports_change",
]
