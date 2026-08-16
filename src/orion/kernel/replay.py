"""Deterministic historical replay of protected transition envelopes.

Replay consumes the immutable ledger and a frozen versioned mechanics seed. It
does not resolve evidence, query current registries, read current protected
support, or run any evaluator. Authorized historical transitions are verified
against the authority/support projections embedded in their own envelope and
then reproduced by the pure reducer.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import (
    HandoffField,
    MechanicDimension,
    MetricDirection,
    MetricKind,
    MetricSpec,
)

from .assurance import (
    AppraisalSignatureStatus,
    AppraisalVerdict,
    VerifierAppraisal,
    verify_appraisal_signature,
)
from .authority_state import (
    AuthorityObjectKind,
    AuthorityObjectStatus,
    AuthorityRegistration,
    AuthorityState,
    AuthorityStatusEvent,
    SupportState,
)
from .authorization import (
    AuthorizationDecision,
    AuthorizationSignatureStatus,
    AuthorizationVerdict,
    TransitionAuthorization,
    restore_transition_authorization,
    verify_authorization_signature,
)
from .store import EntryKind, LedgerEntry, LedgerStore, LegacyLedgerRequiresMigration
from .support import DependencyStatus, DependencyStatusEvent, SupportSet
from .transaction import TRANSITION_TRANSACTION_SCHEMA_VERSION
from .protected_identity import protected_projection_hash
from .transition import (
    REDUCER_VERSION,
    WORKFLOW_VERSION,
    LedgerExpectation,
    ProgramProjection,
    canonical_digest,
)
from .transition_reducer import (
    TransitionOperation,
    TransitionOperationKind,
    TransitionPlan,
    TransitionResidual,
    TransitionResidualKind,
    canonical_transition_plan_payload,
    reduce_transition,
)


class ReplayFailure(RuntimeError):
    pass


class ReplayStatus(str, Enum):
    EMPTY = "EMPTY"
    REPLAYED = "REPLAYED"
    MIGRATION_REQUIRED = "MIGRATION_REQUIRED"


@dataclass(frozen=True)
class ProtectedReplayReport:
    status: ReplayStatus
    projection: ProgramProjection
    transaction_ids: tuple[str, ...]
    authorized_transaction_ids: tuple[str, ...]
    nonauthorized_transaction_ids: tuple[str, ...]

    @property
    def evaluator_calls(self) -> int:
        return 0


def _expectation(raw: Mapping[str, Any]) -> LedgerExpectation:
    return LedgerExpectation(
        raw.get("ledger_head"),
        str(raw["research_state_hash"]),
        str(raw["authority_revision"]),
        str(raw["support_revision"]),
    )


def _metric(raw: Mapping[str, Any]) -> MetricSpec:
    return MetricSpec(
        metric_id=str(raw["metric_id"]),
        description=str(raw["description"]),
        kind=MetricKind(str(raw["kind"])),
        direction=MetricDirection(str(raw["direction"])),
        unit=str(raw["unit"]),
        required_for_handoff=bool(raw["required_for_handoff"]),
        threshold_semantics=str(raw["threshold_semantics"]),
        uncertainty_semantics=str(raw["uncertainty_semantics"]),
    )


def _record(raw: Mapping[str, Any]) -> AnswerRecord:
    record = AnswerRecord(
        record_id=str(raw["record_id"]),
        mechanic_id=str(raw["mechanic_id"]),
        dimension=MechanicDimension(str(raw["dimension"])),
        lane=str(raw["lane"]),
        evidence_refs=tuple(str(item) for item in raw.get("evidence_refs", ())),
        evidence_bindings=tuple(
            (str(item[0]), str(item[1])) for item in raw.get("evidence_bindings", ())
        ),
        payload=tuple(
            (str(item[0]), tuple(str(value) for value in item[1]))
            for item in raw.get("payload", ())
        ),
        handoff_payload=tuple(
            HandoffField(
                field_id=str(item["field_id"]),
                description=str(item["description"]),
                schema_ref=str(item["schema_ref"]),
                required=bool(item["required"]),
            )
            for item in raw.get("handoff_payload", ())
        ),
        metric_payload=tuple(_metric(item) for item in raw.get("metric_payload", ())),
        waiver_reason=str(raw.get("waiver_reason", "")),
        supersedes=str(raw.get("supersedes", "")),
    )
    return record


def _residual(raw: Mapping[str, Any]) -> TransitionResidual:
    return TransitionResidual(
        TransitionResidualKind(str(raw["kind"])),
        str(raw.get("mechanic_id", "")),
        str(raw.get("dimension", "")),
        str(raw.get("record_id", "")),
        str(raw.get("note", "")),
    )


def _operation(raw: Mapping[str, Any]) -> TransitionOperation:
    record_raw = raw.get("record")
    return TransitionOperation(
        operation_index=int(raw["operation_index"]),
        kind=TransitionOperationKind(str(raw["kind"])),
        record=_record(record_raw) if isinstance(record_raw, Mapping) else None,
        mechanic_id=str(raw.get("mechanic_id", "")),
        dimension=str(raw.get("dimension", "")),
        reason=str(raw.get("reason", "")),
    )


def _plan(raw: Mapping[str, Any]) -> TransitionPlan:
    if str(raw["workflow_version"]) != WORKFLOW_VERSION:
        raise ReplayFailure("unknown historical workflow version")
    if str(raw["reducer_version"]) != REDUCER_VERSION:
        raise ReplayFailure("unknown historical reducer version")
    operations = tuple(_operation(item) for item in raw.get("operations", ()))
    residuals = tuple(_residual(item) for item in raw.get("residuals", ()))
    expectation = _expectation(raw["expectation"])
    payload = canonical_transition_plan_payload(
        expectation=expectation,
        pre_state_hash=str(raw["pre_state_hash"]),
        proposed_post_state_hash=str(raw["proposed_post_state_hash"]),
        operations=operations,
        residuals=residuals,
        evidence_snapshot_hash=str(raw["evidence_snapshot_hash"]),
        execution_receipt_hash=(
            str(raw["execution_receipt_hash"])
            if raw.get("execution_receipt_hash") is not None
            else None
        ),
    )
    transition_id = canonical_digest(payload, domain="orion.transition-plan.v1")
    if transition_id != str(raw["transition_id"]):
        raise ReplayFailure("historical transition plan identity mismatch")
    return TransitionPlan(
        transition_id,
        expectation,
        str(raw["pre_state_hash"]),
        str(raw["proposed_post_state_hash"]),
        str(raw["workflow_version"]),
        str(raw["reducer_version"]),
        operations,
        residuals,
        str(raw["evidence_snapshot_hash"]),
        str(raw["execution_receipt_hash"])
        if raw.get("execution_receipt_hash") is not None
        else None,
    )


def _authority_state(raw: Mapping[str, Any]) -> AuthorityState:
    registrations = tuple(
        AuthorityRegistration(
            registration_id=str(item["registration_id"]),
            kind=AuthorityObjectKind(str(item["kind"])),
            artifact_hash=str(item["artifact_hash"]),
            epoch_id=str(item["epoch_id"]),
            metadata_hash=str(item["metadata_hash"]),
            public_key_hex=str(item.get("public_key_hex", "")),
        )
        for item in raw.get("registrations", ())
    )
    history = tuple(
        AuthorityStatusEvent(
            event_id=str(item["event_id"]),
            registration_id=str(item["registration_id"]),
            status=AuthorityObjectStatus(str(item["status"])),
            observed_at=int(item["observed_at"]),
            reason=str(item["reason"]),
        )
        for item in raw.get("status_history", ())
    )
    state = AuthorityState(registrations, history, int(raw["status_time"]))
    if state.revision != str(raw["revision"]):
        raise ReplayFailure("historical authority-state revision mismatch")
    return state


def _support_state(raw: Mapping[str, Any]) -> SupportState:
    state = SupportState(
        tuple(
            SupportSet(
                str(item["support_set_id"]),
                tuple(str(value) for value in item["dependency_ids"]),
            )
            for item in raw.get("support_sets", ())
        ),
        tuple(
            DependencyStatusEvent(
                str(item["event_id"]),
                str(item["dependency_id"]),
                DependencyStatus(str(item["status"])),
                int(item["observed_at"]),
                str(item["reason"]),
            )
            for item in raw.get("dependency_history", ())
        ),
        int(raw["status_time"]),
    )
    if state.revision != str(raw["revision"]):
        raise ReplayFailure("historical support-state revision mismatch")
    evaluation = raw.get("evaluation")
    if isinstance(evaluation, Mapping) and state.evaluation.verdict.value != str(
        evaluation.get("verdict")
    ):
        raise ReplayFailure("historical support evaluation mismatch")
    return state


def _appraisal(raw: Mapping[str, Any]) -> VerifierAppraisal:
    return VerifierAppraisal(
        appraisal_id=str(raw["appraisal_id"]),
        subject_hash=str(raw["subject_hash"]),
        transition_id=str(raw["transition_id"]),
        evidence_snapshot_hash=str(raw["evidence_snapshot_hash"]),
        registration_commitment=str(raw["registration_commitment"]),
        verifier_id=str(raw["verifier_id"]),
        evaluation_epoch_id=str(raw["evaluation_epoch_id"]),
        verdict=AppraisalVerdict(str(raw["verdict"])),
        reason_codes=tuple(str(item) for item in raw["reason_codes"]),
        signature=str(raw["signature"]),
    )


def _decision(raw: Mapping[str, Any]) -> AuthorizationDecision:
    return AuthorizationDecision(
        str(raw["authorization_id"]),
        str(raw["transition_id"]),
        str(raw["subject_hash"]),
        AuthorizationVerdict(str(raw["verdict"])),
        tuple(str(item) for item in raw["reason_codes"]),
        _expectation(raw["expectation"]),
        str(raw["authority_revision"]),
        str(raw["support_revision"]),
        str(raw["authorization_key_registration_id"]),
    )


def _authorization(raw: Mapping[str, Any] | None) -> TransitionAuthorization | None:
    if raw is None:
        return None
    return restore_transition_authorization(
        authorization_id=str(raw["authorization_id"]),
        transition_id=str(raw["transition_id"]),
        subject_hash=str(raw["subject_hash"]),
        verdict=AuthorizationVerdict(str(raw["verdict"])),
        reason_codes=tuple(str(item) for item in raw["reason_codes"]),
        expectation=_expectation(raw["expectation"]),
        authority_revision=str(raw["authority_revision"]),
        support_revision=str(raw["support_revision"]),
        authorization_key_registration_id=str(raw["authorization_key_registration_id"]),
        signature=str(raw["signature"]),
    )


def _verify_historical_authority(
    raw: Mapping[str, Any],
    *,
    plan: TransitionPlan,
) -> AuthorizationVerdict:
    authority = _authority_state(raw["authority_state"])
    support = _support_state(raw["support_state"])
    appraisal = _appraisal(raw["appraisal"])
    decision = _decision(raw["decision"])
    authorization = _authorization(raw.get("authorization"))

    if decision.transition_id != plan.transition_id:
        raise ReplayFailure("historical decision transition mismatch")
    if decision.authority_revision != authority.revision:
        raise ReplayFailure("historical decision authority revision mismatch")
    if decision.support_revision != support.revision:
        raise ReplayFailure("historical decision support revision mismatch")
    evaluator = authority.registration(appraisal.verifier_id)
    if evaluator is None or evaluator.kind is not AuthorityObjectKind.EVALUATOR:
        raise ReplayFailure("historical evaluator registration missing")
    if appraisal.registration_commitment != evaluator.commitment:
        raise ReplayFailure("historical evaluator commitment mismatch")
    if (
        verify_appraisal_signature(
            appraisal, registered_public_key_hex=evaluator.public_key_hex
        ).status
        is not AppraisalSignatureStatus.VALID
    ):
        raise ReplayFailure("historical appraisal signature invalid")

    if decision.verdict is AuthorizationVerdict.AUTHORIZED:
        if authorization is None:
            raise ReplayFailure("authorized historical decision lacks sealed authorization")
        if (
            verify_authorization_signature(authorization, authority_state=authority)
            is not AuthorizationSignatureStatus.VALID
        ):
            raise ReplayFailure("historical authorization signature invalid")
    elif authorization is not None and authorization.authorizes_state_change:
        raise ReplayFailure("non-authorized historical decision carries state-change receipt")
    return decision.verdict


def _raw_transaction(entry: LedgerEntry) -> tuple[str, Mapping[str, Any]]:
    if entry.kind is not EntryKind.TRANSITION:
        raise LegacyLedgerRequiresMigration("historical loose rows require migration quarantine")
    transaction_id = str(entry.payload.get("transaction_id", ""))
    raw = entry.payload.get("transaction")
    if not transaction_id or not isinstance(raw, Mapping):
        raise ReplayFailure("transition ledger row lacks canonical envelope")
    if str(raw.get("schema_version")) != TRANSITION_TRANSACTION_SCHEMA_VERSION:
        raise ReplayFailure("unknown transition transaction schema")
    recomputed = canonical_digest(raw, domain="orion.transition-transaction.v1")
    if recomputed != transaction_id:
        raise ReplayFailure("transition transaction identity mismatch")
    return transaction_id, raw


def replay_protected_ledger(
    store: LedgerStore,
    *,
    seed_projection: ProgramProjection,
) -> ProtectedReplayReport:
    entries = store.entries()
    if not entries:
        return ProtectedReplayReport(ReplayStatus.EMPTY, seed_projection, (), (), ())
    if any(entry.kind is not EntryKind.TRANSITION for entry in entries):
        raise LegacyLedgerRequiresMigration(
            "protected replay consumes only committed TRANSITION envelopes"
        )

    projection = seed_projection
    transaction_ids: list[str] = []
    authorized: list[str] = []
    nonauthorized: list[str] = []
    for entry in entries:
        transaction_id, raw = _raw_transaction(entry)
        plan = _plan(raw["plan"])
        if plan.pre_state_hash != protected_projection_hash(projection):
            raise ReplayFailure("historical transition pre-state mismatch")
        snapshot = raw.get("evidence_snapshot")
        if not isinstance(snapshot, Mapping):
            raise ReplayFailure("historical evidence snapshot missing")
        if str(snapshot.get("snapshot_id")) != plan.evidence_snapshot_hash:
            raise ReplayFailure("historical evidence snapshot identity mismatch")
        verdict = _verify_historical_authority(raw, plan=plan)
        expected_post = (
            plan.proposed_post_state_hash
            if verdict is AuthorizationVerdict.AUTHORIZED
            else plan.pre_state_hash
        )
        if str(raw.get("committed_post_state_hash")) != expected_post:
            raise ReplayFailure("historical committed post-state mismatch")
        if verdict is AuthorizationVerdict.AUTHORIZED:
            reduction = reduce_transition(projection, plan)
            if reduction.hash != expected_post:
                raise ReplayFailure("historical pure reduction mismatch")
            projection = reduction.projection
            authorized.append(transaction_id)
        else:
            nonauthorized.append(transaction_id)
        transaction_ids.append(transaction_id)
    return ProtectedReplayReport(
        ReplayStatus.REPLAYED,
        projection,
        tuple(transaction_ids),
        tuple(authorized),
        tuple(nonauthorized),
    )


__all__ = [
    "ProtectedReplayReport",
    "ReplayFailure",
    "ReplayStatus",
    "replay_protected_ledger",
]
