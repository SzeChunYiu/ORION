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


def _sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


@dataclass(frozen=True)
class FrozenFailureInvestigationContext:
    """Exact host-frozen causal context that must drive one Shadow repair investigation."""

    work_id: str
    mechanic_id: str
    development_issue_id: str
    issue_title: str
    symptom_signature: str
    observed_failure_artifact_hash: str
    candidate_cause_ids: tuple[str, ...]
    supported_cause_id: str
    discriminator_artifact_hash: str
    discriminator_evidence_ids: tuple[str, ...]
    issue_evidence_ids: tuple[str, ...]
    failure_episode_ids: tuple[str, ...]
    negative_alternative_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        required = (
            self.work_id,
            self.mechanic_id,
            self.development_issue_id,
            self.issue_title,
            self.symptom_signature,
            self.supported_cause_id,
        )
        if any(not value.strip() for value in required):
            raise ValueError("frozen failure investigation identity/mechanic/issue/cause are required")
        if not _sha256(self.observed_failure_artifact_hash) or not _sha256(
            self.discriminator_artifact_hash
        ):
            raise ValueError("frozen failure investigation artifacts must use SHA-256")
        if len(self.candidate_cause_ids) < 2:
            raise ValueError("frozen failure investigation requires competing cause hypotheses")
        if self.supported_cause_id not in self.candidate_cause_ids:
            raise ValueError("supported cause must belong to the frozen candidate-cause set")
        if not self.discriminator_evidence_ids:
            raise ValueError("frozen failure investigation requires discriminator evidence")
        if not self.failure_episode_ids:
            raise ValueError("frozen failure investigation requires preserved failure episodes")
        if not self.negative_alternative_ids:
            raise ValueError("frozen failure investigation must retain negative/harmful alternatives")


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
    development_issue_id: str = ""
    observed_failure_artifact_hash: str = ""
    candidate_cause_ids: tuple[str, ...] = ()
    supported_cause_id: str = ""
    discriminator_artifact_hash: str = ""
    discriminator_evidence_ids: tuple[str, ...] = ()
    source_failure_episode_ids: tuple[str, ...] = ()
    negative_alternative_ids: tuple[str, ...] = ()

    @property
    def observed_failure_bound(self) -> bool:
        return bool(self.observed_failure_artifact_hash)


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


def observed_failure_to_problem(context: FrozenFailureInvestigationContext) -> Problem:
    """Turn one exact observed failure into the research problem that licenses its repair."""

    causes = ", ".join(context.candidate_cause_ids)
    discriminator_evidence = ", ".join(context.discriminator_evidence_ids)
    negatives = ", ".join(context.negative_alternative_ids)
    episodes = ", ".join(context.failure_episode_ids)
    return Problem(
        problem_id=f"self-orion:observed-failure:{context.work_id}",
        question=(
            f"Diagnose and materially narrow the frozen observed failure for ORION mechanic {context.mechanic_id}. "
            f"Persistent issue={context.development_issue_id}; title={context.issue_title}; symptom={context.symptom_signature}. "
            f"Observed-failure artifact SHA-256={context.observed_failure_artifact_hash}; preserved failure episodes=[{episodes}]. "
            f"Competing causes=[{causes}]; frozen supported cause={context.supported_cause_id}. "
            f"Frozen discriminator artifact SHA-256={context.discriminator_artifact_hash}; discriminator evidence=[{discriminator_evidence}]. "
            f"Retained negative/harmful alternatives=[{negatives}]. "
            "Search current ORION/RAKL and relevant external parent-domain/nearest-work evidence for the smallest intervention that actually addresses this supported cause. "
            "Preserve competing explanations and negative history; do not reinterpret the frozen discriminator after seeing a candidate outcome."
        ),
        scope=(
            f"Failure-driven Shadow Self-ORION investigation for issue {context.development_issue_id} and mechanic {context.mechanic_id}; proposal/evidence only"
        ),
        initial_domain_ids=(
            "orion",
            "rakl-provenance",
            "parent-disciplines",
            "scientific-literature",
            "orion-live-evaluation",
            "evaluation-governance",
        ),
        success_criteria=(
            "the proposed intervention remains bound to the exact observed failure and frozen causal discriminator",
            "competing cause hypotheses and negative/harmful alternatives remain recoverable",
            "produce evidence-bound findings or an explicit cannot-check/open residual",
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


def observed_failure_to_knowledge_question(
    context: FrozenFailureInvestigationContext,
) -> MechanicQuestion:
    return MechanicQuestion(
        question_id=f"{context.work_id}:observed-failure-knowledge",
        mechanic_id=context.mechanic_id,
        dimension=MechanicDimension.EMPIRICAL_OPEN,
        question=(
            f"For observed failure {context.development_issue_id} ({context.symptom_signature}), test the frozen supported cause {context.supported_cause_id} against current ORION/RAKL and external nearest work while retaining alternatives {context.candidate_cause_ids}."
        ),
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

    def _knowledge_for_failure(
        self, context: FrozenFailureInvestigationContext
    ) -> tuple[object | None, tuple[str, ...]]:
        if self._knowledge_runtime is None:
            return None, ()
        cell = self._knowledge_cells.get(context.mechanic_id)
        if cell is None:
            return None, (f"knowledge_mechanic_not_registered:{context.mechanic_id}",)
        return (
            self._knowledge_runtime.investigate(
                cell=cell,
                question=observed_failure_to_knowledge_question(context),
            ),
            (),
        )

    def run_observed_failure(
        self,
        context: FrozenFailureInvestigationContext,
        *,
        evaluation_epoch_id: str,
        split_id: str,
    ) -> DevelopmentInvestigationResult:
        """Investigate exactly the host-frozen failure instead of selecting generic frontier work."""

        knowledge, knowledge_residuals = self._knowledge_for_failure(context)
        problem = observed_failure_to_problem(context)
        runtime_result = self._runtime.solve(
            problem,
            variation_signature=(
                "self-orion-observed-failure",
                context.mechanic_id,
                context.development_issue_id,
                context.observed_failure_artifact_hash,
                context.discriminator_artifact_hash,
            ),
            evaluation_epoch_id=evaluation_epoch_id,
            split_id=split_id,
        )
        return DevelopmentInvestigationResult(
            work_id=context.work_id,
            mechanic_id=context.mechanic_id,
            problem_id=problem.problem_id,
            solution_status=runtime_result.solution.status,
            evidence_ids=tuple(
                dict.fromkeys(
                    (
                        *context.issue_evidence_ids,
                        *context.discriminator_evidence_ids,
                        *runtime_result.solution.evidence_ids,
                    )
                )
            ),
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
                tuple(route.value for route in knowledge.packet.unavailable_routes)
                if knowledge is not None
                else ()
            ),
            knowledge_coverage_fraction=(
                knowledge.packet.coverage.coverage_fraction
                if knowledge is not None
                else None
            ),
            knowledge_residuals=knowledge_residuals,
            development_issue_id=context.development_issue_id,
            observed_failure_artifact_hash=context.observed_failure_artifact_hash,
            candidate_cause_ids=context.candidate_cause_ids,
            supported_cause_id=context.supported_cause_id,
            discriminator_artifact_hash=context.discriminator_artifact_hash,
            discriminator_evidence_ids=context.discriminator_evidence_ids,
            source_failure_episode_ids=context.failure_episode_ids,
            negative_alternative_ids=context.negative_alternative_ids,
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
    "FrozenFailureInvestigationContext",
    "ShadowSelfOrionResearchLoop",
    "empirical_work_to_knowledge_question",
    "empirical_work_to_problem",
    "observed_failure_to_knowledge_question",
    "observed_failure_to_problem",
]
