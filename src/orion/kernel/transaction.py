"""Canonical all-or-nothing protected transition envelope.

The envelope contains every object needed to explain and historically replay one
protected transition attempt. It does not persist itself;
``LedgerStore.append_transaction`` owns the atomic write/CAS boundary.
Non-authorized attempts are still complete transactions, but their committed
post-state remains the pre-state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from orion.experience.model import TaskEpisode

from .assurance import VerifierAppraisal
from .authority_state import AuthorityState, SupportState
from .authorization import (
    AuthorizationDecision,
    AuthorizationVerdict,
    TransitionAuthorization,
)
from .evidence import HostEvidenceRecord, HostEvidenceSnapshot
from .transition import canonical_digest
from .transition_reducer import (
    TransitionPlan,
    TransitionResidual,
    canonical_transition_plan_payload,
)


TRANSITION_TRANSACTION_SCHEMA_VERSION = "orion.transition-transaction.v1"


def _role_payload(record: HostEvidenceRecord) -> list[dict[str, str]]:
    return [
        {
            "binding_id": item.binding_id,
            "evidence_ref": item.evidence_ref,
            "role_id": item.role_id,
            "obligation_id": item.obligation_id,
        }
        for item in record.role_bindings
    ]


def _evidence_record_payload(record: HostEvidenceRecord) -> dict[str, Any]:
    return {
        "schema_version": record.schema_version,
        "capture_ordinal": record.capture_ordinal,
        "ref": record.ref,
        "status": record.status.value,
        "backend_type": record.backend_type,
        "scheme": record.scheme,
        "relative_path": record.relative_path,
        "declared_digest": record.declared_digest,
        "resolved_source_revision": record.resolved_source_revision,
        "source_object_format": record.source_object_format,
        "source_reference_oid": record.source_reference_oid,
        "source_blob_oid": record.source_blob_oid,
        "source_tree_entry_mode": record.source_tree_entry_mode,
        "root_configuration_hash": record.root_configuration_hash,
        "role_bindings": _role_payload(record),
        "content_bytes_hex": record.content_bytes.hex(),
        "content_available": record.content_available,
        "content_hash": record.content_hash,
        "byte_length": record.byte_length,
        "source_device": record.source_device,
        "source_inode": record.source_inode,
        "source_size": record.source_size,
        "source_mtime_ns": record.source_mtime_ns,
        "source_ctime_ns": record.source_ctime_ns,
        "note": record.note,
        "record_hash": record.record_hash,
    }


def _snapshot_payload(snapshot: HostEvidenceSnapshot) -> dict[str, Any]:
    return {
        "schema_version": snapshot.schema_version,
        "snapshot_id": snapshot.snapshot_id,
        "root_configuration_hash": snapshot.root_configuration_hash,
        "manifest_hash": snapshot.manifest_hash,
        "captured_at_authority_revision": snapshot.captured_at_authority_revision,
        "captured_at_support_revision": snapshot.captured_at_support_revision,
        "required_obligation_ids": list(snapshot.required_obligation_ids),
        "unresolved_obligation_ids": list(snapshot.unresolved_obligation_ids),
        "capture_work_usage": [list(item) for item in snapshot.capture_work_usage],
        "capture_work_exhausted_dimensions": list(snapshot.capture_work_exhausted_dimensions),
        "records": [_evidence_record_payload(item) for item in snapshot.records],
    }


def _authority_state_payload(state: AuthorityState) -> dict[str, Any]:
    return {
        "revision": state.revision,
        "status_time": state.status_time,
        "registrations": [
            {
                "registration_id": item.registration_id,
                "kind": item.kind.value,
                "artifact_hash": item.artifact_hash,
                "epoch_id": item.epoch_id,
                "metadata_hash": item.metadata_hash,
                "public_key_hex": item.public_key_hex,
                "commitment": item.commitment,
            }
            for item in sorted(state.registrations, key=lambda item: item.registration_id)
        ],
        "status_history": [
            {
                "event_id": item.event_id,
                "registration_id": item.registration_id,
                "status": item.status.value,
                "observed_at": item.observed_at,
                "reason": item.reason,
            }
            for item in state.status_history
        ],
    }


def _support_state_payload(state: SupportState) -> dict[str, Any]:
    evaluation = state.evaluation
    return {
        "revision": state.revision,
        "status_time": state.status_time,
        "support_sets": [
            {
                "support_set_id": item.support_set_id,
                "dependency_ids": list(item.dependency_ids),
            }
            for item in sorted(state.support_sets, key=lambda item: item.support_set_id)
        ],
        "dependency_history": [
            {
                "event_id": item.event_id,
                "dependency_id": item.dependency_id,
                "status": item.status.value,
                "observed_at": item.observed_at,
                "reason": item.reason,
            }
            for item in state.dependency_history
        ],
        "evaluation": {
            "verdict": evaluation.verdict.value,
            "live_support_set_ids": list(evaluation.live_support_set_ids),
            "invalid_support_set_ids": list(evaluation.invalid_support_set_ids),
            "reasons": [
                {
                    "code": item.code.value,
                    "support_set_id": item.support_set_id,
                    "dependency_id": item.dependency_id,
                    "status": item.status.value if item.status is not None else None,
                    "message": item.message,
                }
                for item in evaluation.reasons
            ],
        },
    }


def _appraisal_payload(appraisal: VerifierAppraisal) -> dict[str, Any]:
    return {
        "appraisal_id": appraisal.appraisal_id,
        "subject_hash": appraisal.subject_hash,
        "transition_id": appraisal.transition_id,
        "evidence_snapshot_hash": appraisal.evidence_snapshot_hash,
        "registration_commitment": appraisal.registration_commitment,
        "verifier_id": appraisal.verifier_id,
        "evaluation_epoch_id": appraisal.evaluation_epoch_id,
        "verdict": appraisal.verdict.value,
        "reason_codes": list(appraisal.reason_codes),
        "signature": appraisal.signature,
    }


def _expectation_payload(expectation) -> dict[str, Any]:
    return {
        "ledger_head": expectation.ledger_head,
        "research_state_hash": expectation.research_state_hash,
        "authority_revision": expectation.authority_revision,
        "support_revision": expectation.support_revision,
    }


def _decision_payload(decision: AuthorizationDecision) -> dict[str, Any]:
    return {
        "authorization_id": decision.authorization_id,
        "transition_id": decision.transition_id,
        "subject_hash": decision.subject_hash,
        "verdict": decision.verdict.value,
        "reason_codes": list(decision.reason_codes),
        "expectation": _expectation_payload(decision.expectation),
        "authority_revision": decision.authority_revision,
        "support_revision": decision.support_revision,
        "authorization_key_registration_id": decision.authorization_key_registration_id,
    }


def _authorization_payload(
    authorization: TransitionAuthorization | None,
) -> dict[str, Any] | None:
    if authorization is None:
        return None
    return {
        "authorization_id": authorization.authorization_id,
        "transition_id": authorization.transition_id,
        "subject_hash": authorization.subject_hash,
        "verdict": authorization.verdict.value,
        "reason_codes": list(authorization.reason_codes),
        "expectation": _expectation_payload(authorization.expectation),
        "authority_revision": authorization.authority_revision,
        "support_revision": authorization.support_revision,
        "authorization_key_registration_id": authorization.authorization_key_registration_id,
        "signature": authorization.signature,
    }


def _episode_payload(episode: TaskEpisode) -> dict[str, Any]:
    return {
        "episode_id": episode.episode_id,
        "task_id": episode.task_id,
        "run_id": episode.run_id,
        "parent_run_id": episode.parent_run_id,
        "evaluation_epoch_id": episode.evaluation_epoch_id,
        "split_id": episode.split_id,
        "mechanic_id": episode.mechanic_id,
        "problem_signature": list(episode.problem_signature),
        "variation_signature": list(episode.variation_signature),
        "pre_state_hash": episode.pre_state_hash,
        "action_ids": list(episode.action_ids),
        "observation_ids": list(episode.observation_ids),
        "outcome": episode.outcome.value,
        "failure_signature": list(episode.failure_signature),
        "residual_ids": list(episode.residual_ids),
        "evidence_ids": list(episode.evidence_ids),
        "evidence_bindings": [list(item) for item in episode.evidence_bindings],
        "post_state_hash": episode.post_state_hash,
        "timestamp": episode.timestamp,
        "producer_process_lineage_hash": episode.producer_process_lineage_hash,
        "evaluator_artifact_hash": episode.evaluator_artifact_hash,
        "source_receipt_id": episode.source_receipt_id,
        "output_artifact_ids": list(episode.output_artifact_ids),
        "handoff_values": [list(item) for item in episode.handoff_values],
        "metric_observations": [
            {
                "metric_id": item.metric_id,
                "value": item.value,
                "unit": item.unit,
                "evidence_ids": list(item.evidence_ids),
                "uncertainty": item.uncertainty,
            }
            for item in episode.metric_observations
        ],
        "provenance_ids": list(episode.provenance_ids),
        "cost_units": episode.cost_units,
        "latency_seconds": episode.latency_seconds,
    }


def _residual_payload(residual: TransitionResidual) -> dict[str, Any]:
    return {
        "kind": residual.kind.value,
        "mechanic_id": residual.mechanic_id,
        "dimension": residual.dimension,
        "record_id": residual.record_id,
        "note": residual.note,
    }


def transaction_payload(transaction: "TransitionTransaction") -> dict[str, Any]:
    plan_payload = canonical_transition_plan_payload(
        expectation=transaction.plan.expectation,
        pre_state_hash=transaction.plan.pre_state_hash,
        proposed_post_state_hash=transaction.plan.proposed_post_state_hash,
        operations=transaction.plan.operations,
        residuals=transaction.plan.residuals,
        evidence_snapshot_hash=transaction.plan.evidence_snapshot_hash,
        execution_receipt_hash=transaction.plan.execution_receipt_hash,
    )
    plan_payload["transition_id"] = transaction.plan.transition_id
    return {
        "schema_version": transaction.schema_version,
        "evidence_snapshot": _snapshot_payload(transaction.evidence_snapshot),
        "authority_state": _authority_state_payload(transaction.authority_state),
        "support_state": _support_state_payload(transaction.support_state),
        "appraisal": _appraisal_payload(transaction.appraisal),
        "decision": _decision_payload(transaction.decision),
        "authorization": _authorization_payload(transaction.authorization),
        "plan": plan_payload,
        "episodes": [_episode_payload(item) for item in transaction.episodes],
        "residuals": [_residual_payload(item) for item in transaction.residuals],
        "committed_post_state_hash": transaction.committed_post_state_hash,
    }


@dataclass(frozen=True)
class TransitionTransaction:
    evidence_snapshot: HostEvidenceSnapshot
    authority_state: AuthorityState
    support_state: SupportState
    appraisal: VerifierAppraisal
    decision: AuthorizationDecision
    authorization: TransitionAuthorization | None
    plan: TransitionPlan
    episodes: tuple[TaskEpisode, ...] = ()
    residuals: tuple[TransitionResidual, ...] = ()
    schema_version: str = TRANSITION_TRANSACTION_SCHEMA_VERSION
    transaction_id: str = field(init=False)

    def __post_init__(self) -> None:
        if self.schema_version != TRANSITION_TRANSACTION_SCHEMA_VERSION:
            raise ValueError("unsupported transition transaction schema")
        if self.evidence_snapshot.snapshot_id != self.plan.evidence_snapshot_hash:
            raise ValueError("transaction evidence snapshot does not match plan")
        if self.authority_state.revision != self.decision.authority_revision:
            raise ValueError("embedded authority projection does not match decision revision")
        if self.support_state.revision != self.decision.support_revision:
            raise ValueError("embedded support projection does not match decision revision")
        if self.appraisal.transition_id != self.plan.transition_id:
            raise ValueError("transaction appraisal does not match plan transition")
        if self.decision.transition_id != self.plan.transition_id:
            raise ValueError("transaction authorization decision does not match plan")
        if self.decision.expectation != self.plan.expectation:
            raise ValueError("transaction decision and plan expectations differ")
        if (
            self.decision.authority_revision
            != self.evidence_snapshot.captured_at_authority_revision
        ):
            raise ValueError(
                "transaction authority revision differs from captured evidence occasion"
            )
        if (
            self.decision.support_revision
            != self.evidence_snapshot.captured_at_support_revision
        ):
            raise ValueError(
                "transaction support revision differs from captured evidence occasion"
            )
        if self.authorization is not None:
            if self.authorization.authorization_id != self.decision.authorization_id:
                raise ValueError("sealed authorization does not match decision")
            if self.authorization.verdict is not self.decision.verdict:
                raise ValueError("sealed authorization verdict differs from decision")
            if self.authorization.expectation != self.decision.expectation:
                raise ValueError("sealed authorization expectation differs from decision")
        if self.decision.verdict is AuthorizationVerdict.AUTHORIZED:
            if (
                self.authorization is None
                or not self.authorization.authorizes_state_change
            ):
                raise ValueError("authorized decision requires a sealed authorization")
        elif (
            self.authorization is not None
            and self.authorization.authorizes_state_change
        ):
            raise ValueError(
                "non-authorized decision cannot carry state-changing authorization"
            )
        object.__setattr__(
            self,
            "transaction_id",
            canonical_digest(
                transaction_payload(self), domain="orion.transition-transaction.v1"
            ),
        )

    @property
    def commits_state_change(self) -> bool:
        return (
            self.decision.verdict is AuthorizationVerdict.AUTHORIZED
            and self.authorization is not None
            and self.authorization.authorizes_state_change
        )

    @property
    def committed_post_state_hash(self) -> str:
        return (
            self.plan.proposed_post_state_hash
            if self.commits_state_change
            else self.plan.pre_state_hash
        )


__all__ = [
    "TRANSITION_TRANSACTION_SCHEMA_VERSION",
    "TransitionTransaction",
    "transaction_payload",
]
