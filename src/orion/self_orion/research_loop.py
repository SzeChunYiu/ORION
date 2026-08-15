from __future__ import annotations

from dataclasses import dataclass

from orion.core.problem import Problem
from orion.core.solution import SolutionStatus
from orion.runtime.runtime import OrionRuntime
from orion.self_orion.development_driver import (
    DevelopmentKnowledgeClass,
    EmpiricalWorkItem,
    SelfOrionDevelopmentDriver,
)


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


def empirical_work_to_problem(item: EmpiricalWorkItem) -> Problem:
    domain_ids = {
        DevelopmentKnowledgeClass.LOCAL_ORION: ("orion", "rakl-provenance"),
        DevelopmentKnowledgeClass.RAKL_TRANSFER: ("rakl-provenance", "orion"),
        DevelopmentKnowledgeClass.EXTERNAL_RESEARCH: ("parent-disciplines", "scientific-literature"),
        DevelopmentKnowledgeClass.LIVE_EVIDENCE: ("orion-live-evaluation",),
        DevelopmentKnowledgeClass.PROTECTED_ASSURANCE: ("evaluation-governance", "protected-assurance"),
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


class ShadowSelfOrionResearchLoop:
    """Choose and execute Self-ORION research work without self-promotion authority."""

    def __init__(self, runtime: OrionRuntime, *, driver: SelfOrionDevelopmentDriver | None = None) -> None:
        self._runtime = runtime
        self._driver = driver or SelfOrionDevelopmentDriver()

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
                )
            )
        return tuple(results)


__all__ = ["DevelopmentInvestigationResult", "ShadowSelfOrionResearchLoop", "empirical_work_to_problem"]
