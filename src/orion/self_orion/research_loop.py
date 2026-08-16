from __future__ import annotations

from dataclasses import dataclass

from orion.core.problem import Problem
from orion.core.solution import SolutionStatus
from orion.mechanics.model import MechanicDimension
from orion.mechanics.questioning import MechanicQuestion
from orion.runtime.runtime import OrionRuntime
from orion.self_orion.development_driver import (
    DevelopmentKnowledgeClass,
    EmpiricalWorkItem,
    SelfOrionDevelopmentDriver,
)
from orion.self_orion.knowledge_runtime import ShadowKnowledgeRuntime


@dataclass(frozen=True)
class DevelopmentInvestigationResult:
    work_id: str
    mechanic_id: str
    problem_id: str
    solution_status: SolutionStatus
    evidence_ids: tuple[str, ...]
    residual_ids: tuple[str, ...]
    root_episode_id: str | None
    mechanic_episode_ids: tuple[str, ...]
    proposal_only: bool
    knowledge_candidate_ids: tuple[str, ...] = ()
    knowledge_supporting_claim_ids: tuple[str, ...] = ()
    knowledge_contested_claim_pairs: tuple[tuple[str, str], ...] = ()
    knowledge_unavailable_routes: tuple[str, ...] = ()
    knowledge_coverage_fraction: float | None = None
    knowledge_residuals: tuple[str, ...] = ()


def empirical_work_to_problem(item: EmpiricalWorkItem) -> Problem:
    domain_ids = {
        DevelopmentKnowledgeClass.LOCAL_ORION: ("orion", "rakl-provenance"),
        DevelopmentKnowledgeClass.RAKL_TRANSFER: ("rakl-provenance", "orion"),
        DevelopmentKnowledgeClass.EXTERNAL_RESEARCH: (
            "parent-disciplines",
            "scientific-literature",
        ),
        DevelopmentKnowledgeClass.LIVE_EVIDENCE: ("orion-live-evaluation",),
        DevelopmentKnowledgeClass.PROTECTED_ASSURANCE: (
            "evaluation-governance",
            "protected-assurance",
        ),
    }[item.knowledge_class]
    return Problem(
        problem_id=f"self-orion:{item.work_id}",
        question=(
            f"For ORION mechanic {item.mechanic_id}, resolve or materially narrow this empirical coordinate: {item.coordinate}. "
            "Preserve exact evidence/provenance, distinguish missing evidence from refutation, and return OPEN/CANNOT_CHECK when the coordinate cannot be established."
        ),
        scope=f"Shadow Self-ORION development investigation for {item.mechanic_id}; proposal/evidence only",
        initial_domain_ids=domain_ids,
        success_criteria=(
            "produce evidence-bound findings or an explicit cannot-check/open residual",
            "preserve negative/null outcomes",
            "do not grant method/scientific promotion authority",
        ),
    )


def empirical_work_to_knowledge_question(item: EmpiricalWorkItem) -> MechanicQuestion:
    """Expose an empirical frontier item to the fixed mechanics research grammar."""

    return MechanicQuestion(
        question_id=f"{item.work_id}:knowledge",
        mechanic_id=item.mechanic_id,
        dimension=MechanicDimension.EMPIRICAL_OPEN,
        question=item.coordinate,
        blocking=False,
    )


class ShadowSelfOrionResearchLoop:
    """Choose and execute Self-ORION research work without self-promotion authority."""

    def __init__(
        self,
        runtime: OrionRuntime,
        *,
        driver: SelfOrionDevelopmentDriver | None = None,
        knowledge_runtime: ShadowKnowledgeRuntime | None = None,
    ) -> None:
        self._runtime = runtime
        self._driver = driver or SelfOrionDevelopmentDriver()
        self._knowledge_runtime = knowledge_runtime
        self._knowledge_cells = (
            {
                cell.mechanic_id: cell
                for cell in SelfOrionDevelopmentDriver().local_transfer_cells()
            }
            if knowledge_runtime is not None
            else {}
        )

    def run_next(
        self,
        *,
        limit: int = 1,
        evaluation_epoch_id: str = "self-orion:shadow-evaluation-unfrozen",
        split_id: str = "self-orion:shadow-development",
    ) -> tuple[DevelopmentInvestigationResult, ...]:
        if limit < 1:
            raise ValueError("investigation limit must be positive")
        selected = self._driver.plan_empirical_work(limit=limit)
        results: list[DevelopmentInvestigationResult] = []
        for item in selected:
            knowledge = None
            knowledge_residuals: tuple[str, ...] = ()
            if self._knowledge_runtime is not None:
                cell = self._knowledge_cells.get(item.mechanic_id)
                if cell is None:
                    knowledge_residuals = (
                        f"knowledge_mechanic_not_registered:{item.mechanic_id}",
                    )
                else:
                    knowledge = self._knowledge_runtime.investigate(
                        cell=cell,
                        question=empirical_work_to_knowledge_question(item),
                    )

            problem = empirical_work_to_problem(item)
            runtime_result = self._runtime.solve(
                problem,
                variation_signature=("self-orion-shadow", item.mechanic_id, item.work_id),
                evaluation_epoch_id=evaluation_epoch_id,
                split_id=split_id,
            )
            results.append(
                DevelopmentInvestigationResult(
                    work_id=item.work_id,
                    mechanic_id=item.mechanic_id,
                    problem_id=problem.problem_id,
                    solution_status=runtime_result.solution.status,
                    evidence_ids=runtime_result.solution.evidence_ids,
                    residual_ids=runtime_result.solution.residual_ids,
                    root_episode_id=runtime_result.experience_episode_id,
                    mechanic_episode_ids=runtime_result.mechanic_experience_episode_ids,
                    proposal_only=True,
                    knowledge_candidate_ids=(
                        knowledge.candidate_ids if knowledge is not None else ()
                    ),
                    knowledge_supporting_claim_ids=(
                        knowledge.supporting_claim_ids if knowledge is not None else ()
                    ),
                    knowledge_contested_claim_pairs=(
                        knowledge.contested_claim_pairs if knowledge is not None else ()
                    ),
                    knowledge_unavailable_routes=(
                        tuple(
                            route.value
                            for route in knowledge.packet.unavailable_routes
                        )
                        if knowledge is not None
                        else ()
                    ),
                    knowledge_coverage_fraction=(
                        knowledge.packet.coverage.coverage_fraction
                        if knowledge is not None
                        else None
                    ),
                    knowledge_residuals=knowledge_residuals,
                )
            )
        return tuple(results)


__all__ = [
    "DevelopmentInvestigationResult",
    "ShadowSelfOrionResearchLoop",
    "empirical_work_to_knowledge_question",
    "empirical_work_to_problem",
]
