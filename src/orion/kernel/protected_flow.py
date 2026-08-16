"""Protected proposal-to-commit composition.

This host-owned coordinator is the only end-to-end path in this Phase-1 slice
that may turn a proposal into committed research state. Candidate-facing
kernel modules remain proposal/diagnostic surfaces and do not receive the
verifier, protected authority state, signer, or transaction store.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from orion.experience.model import TaskEpisode
from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import MechanicDimension

from .assurance import VerifierAppraisal
from .evidence import HostEvidenceSnapshot
from .host import ProtectedHostAuthorizationService
from .protected_identity import protected_projection_hash
from .store import LedgerEntry, LedgerStore, StaleTransitionExpectation
from .transaction import TransitionTransaction
from .transition import LedgerExpectation, ProgramProjection
from .transition_reducer import (
    TransitionPlan,
    TransitionReductionResult,
    plan_answer_transition,
    plan_reopen_transition,
    reduce_transition,
)


class ProtectedVerifier(Protocol):
    """Host-installed verifier; not a candidate-facing callable parameter."""

    def appraise(
        self,
        *,
        plan: TransitionPlan,
        evidence_snapshot: HostEvidenceSnapshot,
    ) -> VerifierAppraisal: ...


@dataclass(frozen=True)
class ProtectedTransitionResult:
    transaction: TransitionTransaction
    ledger_entry: LedgerEntry
    committed_projection: ProgramProjection
    reduction: TransitionReductionResult | None

    @property
    def state_changed(self) -> bool:
        return self.transaction.commits_state_change

    @property
    def self_authorized(self) -> bool:
        return False


class ProtectedTransitionCoordinator:
    """Host-owned protected transition coordinator."""

    def __init__(
        self,
        *,
        store: LedgerStore,
        host: ProtectedHostAuthorizationService,
        verifier: ProtectedVerifier,
    ) -> None:
        self._store = store
        self._host = host
        self._verifier = verifier

    def expectation_for(self, projection: ProgramProjection) -> LedgerExpectation:
        current = self._store.protected_expectation()
        if current is None:
            return LedgerExpectation(
                None,
                protected_projection_hash(projection),
                self._host.authority_revision,
                self._host.support_revision,
            )
        if current.research_state_hash != protected_projection_hash(projection):
            raise StaleTransitionExpectation(
                "research_state_hash",
                current.research_state_hash,
                protected_projection_hash(projection),
            )
        if current.authority_revision != self._host.authority_revision:
            raise StaleTransitionExpectation(
                "authority_revision",
                current.authority_revision,
                self._host.authority_revision,
            )
        if current.support_revision != self._host.support_revision:
            raise StaleTransitionExpectation(
                "support_revision",
                current.support_revision,
                self._host.support_revision,
            )
        return current

    @staticmethod
    def _validate_snapshot(
        evidence_snapshot: HostEvidenceSnapshot,
        expectation: LedgerExpectation,
    ) -> None:
        if evidence_snapshot.captured_at_authority_revision != expectation.authority_revision:
            raise StaleTransitionExpectation(
                "evidence_authority_revision",
                expectation.authority_revision,
                evidence_snapshot.captured_at_authority_revision,
            )
        if evidence_snapshot.captured_at_support_revision != expectation.support_revision:
            raise StaleTransitionExpectation(
                "evidence_support_revision",
                expectation.support_revision,
                evidence_snapshot.captured_at_support_revision,
            )

    def _commit_plan(
        self,
        *,
        projection: ProgramProjection,
        plan: TransitionPlan,
        evidence_snapshot: HostEvidenceSnapshot,
        episodes: tuple[TaskEpisode, ...],
        chronology_frozen_before_candidate: bool,
    ) -> ProtectedTransitionResult:
        appraisal = self._verifier.appraise(
            plan=plan,
            evidence_snapshot=evidence_snapshot,
        )
        host_decision = self._host.authorize(
            plan=plan,
            appraisal=appraisal,
            current_expectation=plan.expectation,
            chronology_frozen_before_candidate=chronology_frozen_before_candidate,
        )
        transaction = TransitionTransaction(
            evidence_snapshot,
            self._host.authority_state,
            self._host.support_state,
            appraisal,
            host_decision.decision,
            host_decision.authorization,
            plan,
            episodes,
            plan.residuals,
        )
        ledger_entry = self._store.append_transaction(
            transaction,
            expected=plan.expectation,
        )
        if transaction.commits_state_change:
            reduction = reduce_transition(projection, plan)
            if reduction.hash != transaction.committed_post_state_hash:
                raise RuntimeError(
                    "committed protected transition does not reproduce pure reducer post-state"
                )
            committed_projection = reduction.projection
        else:
            reduction = None
            committed_projection = projection
        return ProtectedTransitionResult(
            transaction,
            ledger_entry,
            committed_projection,
            reduction,
        )

    def commit_answer(
        self,
        *,
        projection: ProgramProjection,
        record: AnswerRecord,
        evidence_snapshot: HostEvidenceSnapshot,
        episodes: tuple[TaskEpisode, ...] = (),
        chronology_frozen_before_candidate: bool = True,
        execution_receipt_hash: str | None = None,
    ) -> ProtectedTransitionResult:
        expectation = self.expectation_for(projection)
        self._validate_snapshot(evidence_snapshot, expectation)
        plan = plan_answer_transition(
            projection,
            record,
            expectation=expectation,
            evidence_snapshot_hash=evidence_snapshot.snapshot_id,
            execution_receipt_hash=execution_receipt_hash,
        )
        return self._commit_plan(
            projection=projection,
            plan=plan,
            evidence_snapshot=evidence_snapshot,
            episodes=episodes,
            chronology_frozen_before_candidate=chronology_frozen_before_candidate,
        )

    def commit_reopen(
        self,
        *,
        projection: ProgramProjection,
        mechanic_id: str,
        dimension: MechanicDimension,
        reason: str,
        evidence_snapshot: HostEvidenceSnapshot,
        episodes: tuple[TaskEpisode, ...] = (),
        chronology_frozen_before_candidate: bool = True,
    ) -> ProtectedTransitionResult:
        """Append a verifier/host-authorized reopen without erasing history."""

        expectation = self.expectation_for(projection)
        self._validate_snapshot(evidence_snapshot, expectation)
        plan = plan_reopen_transition(
            projection,
            mechanic_id=mechanic_id,
            dimension=dimension,
            reason=reason,
            expectation=expectation,
            evidence_snapshot_hash=evidence_snapshot.snapshot_id,
        )
        return self._commit_plan(
            projection=projection,
            plan=plan,
            evidence_snapshot=evidence_snapshot,
            episodes=episodes,
            chronology_frozen_before_candidate=chronology_frozen_before_candidate,
        )


__all__ = [
    "ProtectedTransitionCoordinator",
    "ProtectedTransitionResult",
    "ProtectedVerifier",
]
