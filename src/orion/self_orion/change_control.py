from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from orion.providers.development.base import (
    DevelopmentChangeProvider,
    DevelopmentChangeProposal,
    DevelopmentChangeRequest,
)
from orion.self_orion.development_fibre import DevelopmentFibre
from orion.self_orion.research_loop import DevelopmentInvestigationResult


@dataclass(frozen=True)
class CandidateExecutionReceipt:
    receipt_id: str
    proposal_id: str
    candidate_revision_hash: str
    passed_required_tests: bool
    test_result_ids: tuple[str, ...]
    failure_signatures: tuple[str, ...]
    resource_units: float
    artifact_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.receipt_id, self.proposal_id, self.candidate_revision_hash)):
            raise ValueError("candidate execution receipt identity fields are required")
        if len(self.candidate_revision_hash) != 64 or any(ch not in "0123456789abcdef" for ch in self.candidate_revision_hash):
            raise ValueError("candidate revision hash must be SHA-256")
        if self.resource_units < 0:
            raise ValueError("candidate execution resources cannot be negative")


class SandboxCandidateRunner(Protocol):
    def execute(self, proposal: DevelopmentChangeProposal) -> CandidateExecutionReceipt: ...


@dataclass(frozen=True)
class ProtectedDevelopmentAssuranceReceipt:
    receipt_id: str
    proposal_id: str
    candidate_revision_hash: str
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    development_delta: float
    fresh_assurance_delta: float
    blocking_invariants_passed: bool
    evaluator_frozen_before_candidate: bool
    fresh_split: bool
    resource_matched: bool
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        required = (self.receipt_id, self.proposal_id, self.candidate_revision_hash, self.evaluator_artifact_hash, self.evaluation_epoch_id)
        if any(not value.strip() for value in required):
            raise ValueError("assurance receipt identity/evaluator/epoch fields are required")
        for digest in (self.candidate_revision_hash, self.evaluator_artifact_hash):
            if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
                raise ValueError("assurance subject/evaluator hashes must be SHA-256")


class ProtectedDevelopmentEvaluator(Protocol):
    def evaluate(
        self,
        request: DevelopmentChangeRequest,
        proposal: DevelopmentChangeProposal,
        execution: CandidateExecutionReceipt,
    ) -> ProtectedDevelopmentAssuranceReceipt: ...


class ChangeControlVerdict(str, Enum):
    REJECT = "REJECT"
    CANDIDATE_ONLY = "CANDIDATE_ONLY"
    RECOMMEND_HOST_PROMOTION = "RECOMMEND_HOST_PROMOTION"


@dataclass(frozen=True)
class ChangeControlResult:
    request: DevelopmentChangeRequest
    proposal: DevelopmentChangeProposal
    execution: CandidateExecutionReceipt
    assurance: ProtectedDevelopmentAssuranceReceipt
    verdict: ChangeControlVerdict
    reasons: tuple[str, ...]

    @property
    def self_merge_authorized(self) -> bool:
        return False


def change_request_from_investigation(
    investigation: DevelopmentInvestigationResult,
    fibre: DevelopmentFibre,
    *,
    base_revision: str,
) -> DevelopmentChangeRequest:
    if investigation.mechanic_id != fibre.mechanic_id:
        raise ValueError("investigation and development fibre must target the same mechanic")
    required_tests = tuple(
        dict.fromkeys(
            tuple(fibre.cell.verification_contracts)
            + (f"orion:{fibre.mechanic_id}:regression", f"orion:{fibre.mechanic_id}:fresh-assurance")
        )
    )
    protected = tuple(
        dict.fromkeys(
            fibre.cell.invariant_ids
            + (
                "no scientific/method authority from provider output",
                "preserve negative/null history",
                "evaluator and fresh-assurance split frozen before candidate outcome",
                "no self-merge or evaluator rewrite",
            )
        )
    )
    failure_episode_ids = tuple(dict.fromkeys(fibre.failure_episode_ids + investigation.mechanic_episode_ids))
    return DevelopmentChangeRequest(
        request_id=f"change:{investigation.work_id}",
        mechanic_id=investigation.mechanic_id,
        problem_statement=(
            f"Use the evidence/residuals from {investigation.problem_id} to propose the smallest scoped implementation change for {investigation.mechanic_id}. "
            f"Evidence={investigation.evidence_ids}; residuals={investigation.residual_ids}."
        ),
        base_revision=base_revision,
        evidence_ids=investigation.evidence_ids,
        failure_episode_ids=failure_episode_ids,
        protected_constraints=protected,
        required_tests=required_tests,
        falsifier=(
            f"Reject the change if it fails any protected invariant, does not improve the diagnosed coordinate, regresses fresh assurance, or only overfits the visible development tests for {investigation.mechanic_id}."
        ),
    )


class SelfOrionChangeController:
    """Run propose -> sandbox -> protected assurance; never merge automatically."""

    def __init__(
        self,
        *,
        provider: DevelopmentChangeProvider,
        runner: SandboxCandidateRunner,
        evaluator: ProtectedDevelopmentEvaluator,
    ) -> None:
        self._provider = provider
        self._runner = runner
        self._evaluator = evaluator

    def evaluate_change(self, request: DevelopmentChangeRequest) -> ChangeControlResult:
        proposal = self._provider.propose(request)
        reasons: list[str] = []
        if proposal.request_id != request.request_id:
            reasons.append("proposal_request_binding_mismatch")
        if proposal.base_revision != request.base_revision:
            reasons.append("proposal_base_revision_mismatch")
        execution = self._runner.execute(proposal)
        if execution.proposal_id != proposal.proposal_id:
            reasons.append("execution_proposal_binding_mismatch")
        assurance = self._evaluator.evaluate(request, proposal, execution)
        if assurance.proposal_id != proposal.proposal_id:
            reasons.append("assurance_proposal_binding_mismatch")
        if assurance.candidate_revision_hash != execution.candidate_revision_hash:
            reasons.append("assurance_candidate_binding_mismatch")
        if not execution.passed_required_tests:
            reasons.append("required_tests_failed")
        if not assurance.blocking_invariants_passed:
            reasons.append("blocking_invariant_failed")
        if not assurance.evaluator_frozen_before_candidate:
            reasons.append("evaluator_not_frozen")
        if not assurance.fresh_split:
            reasons.append("assurance_split_not_fresh")
        if not assurance.resource_matched:
            reasons.append("resources_not_matched")
        if assurance.development_delta <= 0:
            reasons.append("no_development_improvement")
        if assurance.fresh_assurance_delta <= 0:
            reasons.append("no_fresh_assurance_improvement")

        binding_failures = {
            "proposal_request_binding_mismatch",
            "proposal_base_revision_mismatch",
            "execution_proposal_binding_mismatch",
            "assurance_proposal_binding_mismatch",
            "assurance_candidate_binding_mismatch",
        }
        if binding_failures.intersection(reasons) or "blocking_invariant_failed" in reasons:
            verdict = ChangeControlVerdict.REJECT
        elif reasons:
            verdict = ChangeControlVerdict.CANDIDATE_ONLY
        else:
            verdict = ChangeControlVerdict.RECOMMEND_HOST_PROMOTION
        return ChangeControlResult(
            request=request,
            proposal=proposal,
            execution=execution,
            assurance=assurance,
            verdict=verdict,
            reasons=tuple(reasons),
        )


__all__ = [
    "CandidateExecutionReceipt",
    "ChangeControlResult",
    "ChangeControlVerdict",
    "ProtectedDevelopmentAssuranceReceipt",
    "ProtectedDevelopmentEvaluator",
    "SandboxCandidateRunner",
    "SelfOrionChangeController",
    "change_request_from_investigation",
]
