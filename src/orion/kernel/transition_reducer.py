"""Pure, versioned mechanics transition planning and reduction.

This module is deliberately below appraisal/authorization. It accepts typed
proposal state and produces a deterministic candidate post-state. It performs
no evidence resolution, filesystem access, evaluator execution, signature
verification, clock read, registry lookup, or mutation.

A plan is therefore *not authority*. Later protected-host code may appraise and
authorize exactly this plan; without that external authorization it remains a
candidate transition only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import MechanicDimension, MetricSpec

from .protected_identity import protected_projection_hash
from .transition import (
    REDUCER_VERSION,
    WORKFLOW_VERSION,
    LedgerExpectation,
    ProgramProjection,
    answer_record_hash,
    canonical_digest,
)


class TransitionOperationKind(str, Enum):
    APPLY_ANSWER = "APPLY_ANSWER"
    IDEMPOTENT_NOOP = "IDEMPOTENT_NOOP"
    RECORDED_NOOP = "RECORDED_NOOP"
    REOPEN_COORDINATE = "REOPEN_COORDINATE"


class TransitionResidualKind(str, Enum):
    UNKNOWN_MECHANIC = "UNKNOWN_MECHANIC"
    UNAUTHORIZED_WAIVER = "UNAUTHORIZED_WAIVER"
    DUPLICATE_ID_CONFLICT = "DUPLICATE_ID_CONFLICT"
    SUPERSESSION_PARENT_MISSING = "SUPERSESSION_PARENT_MISSING"
    SUPERSESSION_PARENT_NOT_ACTIVE = "SUPERSESSION_PARENT_NOT_ACTIVE"
    SUPERSESSION_REQUIRED = "SUPERSESSION_REQUIRED"
    CROSS_COORDINATE_SUPERSESSION = "CROSS_COORDINATE_SUPERSESSION"
    PRE_STATE_MISMATCH = "PRE_STATE_MISMATCH"
    POST_STATE_MISMATCH = "POST_STATE_MISMATCH"
    INVALID_OPERATION = "INVALID_OPERATION"


@dataclass(frozen=True)
class TransitionResidual:
    kind: TransitionResidualKind
    mechanic_id: str
    dimension: str
    record_id: str
    note: str


@dataclass(frozen=True)
class TransitionOperation:
    operation_index: int
    kind: TransitionOperationKind
    record: AnswerRecord | None = None
    mechanic_id: str = ""
    dimension: str = ""
    reason: str = ""

    def __post_init__(self) -> None:
        if self.operation_index < 0:
            raise ValueError("operation_index cannot be negative")
        if self.kind is TransitionOperationKind.APPLY_ANSWER and self.record is None:
            raise ValueError("APPLY_ANSWER requires a complete AnswerRecord")
        if self.kind is TransitionOperationKind.REOPEN_COORDINATE:
            if not self.mechanic_id or not self.dimension or not self.reason:
                raise ValueError("REOPEN_COORDINATE requires mechanic, dimension and reason")


@dataclass(frozen=True)
class TransitionPlan:
    transition_id: str
    expectation: LedgerExpectation
    pre_state_hash: str
    proposed_post_state_hash: str
    workflow_version: str
    reducer_version: str
    operations: tuple[TransitionOperation, ...]
    residuals: tuple[TransitionResidual, ...]
    evidence_snapshot_hash: str
    execution_receipt_hash: str | None = None

    @property
    def grants_transition_authority(self) -> bool:
        return False


@dataclass(frozen=True)
class TransitionReductionResult:
    projection: ProgramProjection
    applied_record_ids: tuple[str, ...]
    idempotent_record_ids: tuple[str, ...]
    residuals: tuple[TransitionResidual, ...]

    @property
    def hash(self) -> str:
        return protected_projection_hash(self.projection)

    @property
    def grants_transition_authority(self) -> bool:
        return False


def _metric_payload(metric: MetricSpec) -> dict[str, Any]:
    return {
        "metric_id": metric.metric_id,
        "description": metric.description,
        "kind": metric.kind.value,
        "direction": metric.direction.value,
        "unit": metric.unit,
        "required_for_handoff": metric.required_for_handoff,
        "threshold_semantics": metric.threshold_semantics,
        "uncertainty_semantics": metric.uncertainty_semantics,
    }


def _complete_answer_payload(record: AnswerRecord) -> dict[str, Any]:
    """Bind the complete answer, including future structured fields."""

    return {
        "record_id": record.record_id,
        "legacy_record_hash": answer_record_hash(record),
        "mechanic_id": record.mechanic_id,
        "dimension": record.dimension.value,
        "lane": record.lane,
        "evidence_refs": list(record.evidence_refs),
        "evidence_bindings": [list(item) for item in record.evidence_bindings],
        "payload": [[name, list(values)] for name, values in record.payload],
        "handoff_payload": [
            {
                "field_id": item.field_id,
                "description": item.description,
                "schema_ref": item.schema_ref,
                "required": item.required,
            }
            for item in record.handoff_payload
        ],
        "metric_payload": [_metric_payload(item) for item in record.metric_payload],
        "waiver_reason": record.waiver_reason,
        "supersedes": record.supersedes,
    }


def _operation_payload(operation: TransitionOperation) -> dict[str, Any]:
    return {
        "operation_index": operation.operation_index,
        "kind": operation.kind.value,
        "record": _complete_answer_payload(operation.record) if operation.record else None,
        "mechanic_id": operation.mechanic_id,
        "dimension": operation.dimension,
        "reason": operation.reason,
    }


def canonical_transition_plan_payload(
    *,
    expectation: LedgerExpectation,
    pre_state_hash: str,
    proposed_post_state_hash: str,
    operations: tuple[TransitionOperation, ...],
    residuals: tuple[TransitionResidual, ...],
    evidence_snapshot_hash: str,
    execution_receipt_hash: str | None,
) -> dict[str, Any]:
    return {
        "workflow_version": WORKFLOW_VERSION,
        "reducer_version": REDUCER_VERSION,
        "expectation": {
            "ledger_head": expectation.ledger_head,
            "research_state_hash": expectation.research_state_hash,
            "authority_revision": expectation.authority_revision,
            "support_revision": expectation.support_revision,
        },
        "pre_state_hash": pre_state_hash,
        "proposed_post_state_hash": proposed_post_state_hash,
        "operations": [_operation_payload(item) for item in operations],
        "residuals": [
            {
                "kind": item.kind.value,
                "mechanic_id": item.mechanic_id,
                "dimension": item.dimension,
                "record_id": item.record_id,
                "note": item.note,
            }
            for item in residuals
        ],
        "evidence_snapshot_hash": evidence_snapshot_hash,
        "execution_receipt_hash": execution_receipt_hash,
    }


def _coordinate(record: AnswerRecord) -> tuple[str, MechanicDimension]:
    return record.mechanic_id, record.dimension


def _active_by_coordinate(
    projection: ProgramProjection,
) -> dict[tuple[str, MechanicDimension], AnswerRecord]:
    return {_coordinate(record): record for record in projection.active_records}


def _reopened_coordinates(
    projection: ProgramProjection,
) -> set[tuple[str, str]]:
    return {(mechanic_id, dimension) for mechanic_id, dimension, _ in projection.reopened_coordinates}


def _record_has_child(projection: ProgramProjection, record_id: str) -> bool:
    return any(record.supersedes == record_id for record in projection.records)


def _apply_answer_candidate(
    projection: ProgramProjection,
    record: AnswerRecord,
) -> tuple[ProgramProjection, TransitionOperationKind, TransitionResidual | None]:
    mechanic_ids = {cell.mechanic_id for cell in projection.seed_cells}
    if record.mechanic_id not in mechanic_ids:
        return (
            projection,
            TransitionOperationKind.RECORDED_NOOP,
            TransitionResidual(
                TransitionResidualKind.UNKNOWN_MECHANIC,
                record.mechanic_id,
                record.dimension.value,
                record.record_id,
                "answer targets a mechanic outside the frozen seed",
            ),
        )
    if record.waiver_reason:
        return (
            projection,
            TransitionOperationKind.RECORDED_NOOP,
            TransitionResidual(
                TransitionResidualKind.UNAUTHORIZED_WAIVER,
                record.mechanic_id,
                record.dimension.value,
                record.record_id,
                "waiver proposals cannot alter protected research state",
            ),
        )

    existing_by_id = {item.record_id: item for item in projection.records}
    if record.record_id in existing_by_id:
        existing = existing_by_id[record.record_id]
        if _complete_answer_payload(existing) == _complete_answer_payload(record):
            return projection, TransitionOperationKind.IDEMPOTENT_NOOP, None
        return (
            projection,
            TransitionOperationKind.RECORDED_NOOP,
            TransitionResidual(
                TransitionResidualKind.DUPLICATE_ID_CONFLICT,
                record.mechanic_id,
                record.dimension.value,
                record.record_id,
                "record id already exists with different canonical content",
            ),
        )

    coordinate = _coordinate(record)
    active = _active_by_coordinate(projection)
    current = active.get(coordinate)
    reopened = (record.mechanic_id, record.dimension.value) in _reopened_coordinates(
        projection
    )

    if record.supersedes:
        parent = existing_by_id.get(record.supersedes)
        if parent is None:
            return (
                projection,
                TransitionOperationKind.RECORDED_NOOP,
                TransitionResidual(
                    TransitionResidualKind.SUPERSESSION_PARENT_MISSING,
                    record.mechanic_id,
                    record.dimension.value,
                    record.record_id,
                    "supersession parent is absent from the frozen record graph",
                ),
            )
        if _coordinate(parent) != coordinate:
            return (
                projection,
                TransitionOperationKind.RECORDED_NOOP,
                TransitionResidual(
                    TransitionResidualKind.CROSS_COORDINATE_SUPERSESSION,
                    record.mechanic_id,
                    record.dimension.value,
                    record.record_id,
                    "supersession cannot cross mechanic/dimension coordinates",
                ),
            )

        extends_active_tip = current is not None and current.record_id == record.supersedes
        extends_reopened_leaf = (
            current is None
            and reopened
            and not _record_has_child(projection, record.supersedes)
        )
        if not (extends_active_tip or extends_reopened_leaf):
            return (
                projection,
                TransitionOperationKind.RECORDED_NOOP,
                TransitionResidual(
                    TransitionResidualKind.SUPERSESSION_PARENT_NOT_ACTIVE,
                    record.mechanic_id,
                    record.dimension.value,
                    record.record_id,
                    "supersession must extend the active tip or the historical leaf of an explicitly reopened coordinate",
                ),
            )
    elif current is not None or reopened:
        return (
            projection,
            TransitionOperationKind.RECORDED_NOOP,
            TransitionResidual(
                TransitionResidualKind.SUPERSESSION_REQUIRED,
                record.mechanic_id,
                record.dimension.value,
                record.record_id,
                "a historical coordinate exists; replacement must explicitly supersede its current or reopened leaf",
            ),
        )

    active_ids = set(projection.active_record_ids)
    if current is not None:
        active_ids.remove(current.record_id)
    active_ids.add(record.record_id)
    remaining_reopens = tuple(
        item
        for item in projection.reopened_coordinates
        if (item[0], item[1]) != (record.mechanic_id, record.dimension.value)
    )
    post = ProgramProjection(
        schema_version=projection.schema_version,
        workflow_version=projection.workflow_version,
        reducer_version=projection.reducer_version,
        seed_cells=projection.seed_cells,
        records=(*projection.records, record),
        active_record_ids=tuple(sorted(active_ids)),
        reopened_coordinates=remaining_reopens,
    )
    return post, TransitionOperationKind.APPLY_ANSWER, None


def _reopen_candidate(
    projection: ProgramProjection,
    *,
    mechanic_id: str,
    dimension: str,
    reason: str,
) -> tuple[ProgramProjection, TransitionResidual | None]:
    try:
        dimension_enum = MechanicDimension(dimension)
    except ValueError:
        return projection, TransitionResidual(
            TransitionResidualKind.INVALID_OPERATION,
            mechanic_id,
            dimension,
            "",
            "reopen uses an unknown mechanic dimension",
        )
    if mechanic_id not in {cell.mechanic_id for cell in projection.seed_cells}:
        return projection, TransitionResidual(
            TransitionResidualKind.UNKNOWN_MECHANIC,
            mechanic_id,
            dimension,
            "",
            "reopen targets a mechanic outside the frozen seed",
        )
    existing = {
        (item[0], item[1]): item for item in projection.reopened_coordinates
    }
    existing[(mechanic_id, dimension_enum.value)] = (
        mechanic_id,
        dimension_enum.value,
        reason,
    )
    records_by_id = {record.record_id: record for record in projection.records}
    active = tuple(
        record_id
        for record_id in projection.active_record_ids
        if not (
            records_by_id[record_id].mechanic_id == mechanic_id
            and records_by_id[record_id].dimension is dimension_enum
        )
    )
    return ProgramProjection(
        schema_version=projection.schema_version,
        workflow_version=projection.workflow_version,
        reducer_version=projection.reducer_version,
        seed_cells=projection.seed_cells,
        records=projection.records,
        active_record_ids=active,
        reopened_coordinates=tuple(sorted(existing.values())),
    ), None


def _reduce_operations(
    projection: ProgramProjection,
    operations: tuple[TransitionOperation, ...],
) -> TransitionReductionResult:
    current = projection
    applied: list[str] = []
    idempotent: list[str] = []
    residuals: list[TransitionResidual] = []
    for expected_index, operation in enumerate(operations):
        if operation.operation_index != expected_index:
            residuals.append(
                TransitionResidual(
                    TransitionResidualKind.INVALID_OPERATION,
                    operation.mechanic_id,
                    operation.dimension,
                    operation.record.record_id if operation.record else "",
                    "operations must be ordered and consecutively indexed",
                )
            )
            continue
        if operation.kind in {
            TransitionOperationKind.APPLY_ANSWER,
            TransitionOperationKind.IDEMPOTENT_NOOP,
            TransitionOperationKind.RECORDED_NOOP,
        }:
            if operation.record is None:
                residuals.append(
                    TransitionResidual(
                        TransitionResidualKind.INVALID_OPERATION,
                        "",
                        "",
                        "",
                        "answer operation is missing its complete record",
                    )
                )
                continue
            next_projection, actual_kind, residual = _apply_answer_candidate(
                current, operation.record
            )
            if actual_kind is not operation.kind:
                residuals.append(
                    TransitionResidual(
                        TransitionResidualKind.INVALID_OPERATION,
                        operation.record.mechanic_id,
                        operation.record.dimension.value,
                        operation.record.record_id,
                        f"record reduces as {actual_kind.value}, not declared {operation.kind.value}",
                    )
                )
                continue
            current = next_projection
            if actual_kind is TransitionOperationKind.APPLY_ANSWER:
                applied.append(operation.record.record_id)
            elif actual_kind is TransitionOperationKind.IDEMPOTENT_NOOP:
                idempotent.append(operation.record.record_id)
            if residual is not None:
                residuals.append(residual)
        elif operation.kind is TransitionOperationKind.REOPEN_COORDINATE:
            current, residual = _reopen_candidate(
                current,
                mechanic_id=operation.mechanic_id,
                dimension=operation.dimension,
                reason=operation.reason,
            )
            if residual is not None:
                residuals.append(residual)
        else:  # pragma: no cover
            residuals.append(
                TransitionResidual(
                    TransitionResidualKind.INVALID_OPERATION,
                    "",
                    "",
                    "",
                    "unknown operation kind",
                )
            )
    return TransitionReductionResult(
        current, tuple(applied), tuple(idempotent), tuple(residuals)
    )


def plan_answer_transition(
    projection: ProgramProjection,
    record: AnswerRecord,
    *,
    expectation: LedgerExpectation,
    evidence_snapshot_hash: str,
    execution_receipt_hash: str | None = None,
) -> TransitionPlan:
    pre_hash = protected_projection_hash(projection)
    if expectation.research_state_hash != pre_hash:
        residual = TransitionResidual(
            TransitionResidualKind.PRE_STATE_MISMATCH,
            record.mechanic_id,
            record.dimension.value,
            record.record_id,
            "ledger expectation research-state hash does not match the supplied projection",
        )
        operation = TransitionOperation(
            0, TransitionOperationKind.RECORDED_NOOP, record=record
        )
        post_hash = pre_hash
        residuals = (residual,)
    else:
        candidate, operation_kind, residual = _apply_answer_candidate(
            projection, record
        )
        operation = TransitionOperation(0, operation_kind, record=record)
        post_hash = protected_projection_hash(candidate)
        residuals = (residual,) if residual is not None else ()

    payload = canonical_transition_plan_payload(
        expectation=expectation,
        pre_state_hash=pre_hash,
        proposed_post_state_hash=post_hash,
        operations=(operation,),
        residuals=residuals,
        evidence_snapshot_hash=evidence_snapshot_hash,
        execution_receipt_hash=execution_receipt_hash,
    )
    return TransitionPlan(
        transition_id=canonical_digest(payload, domain="orion.transition-plan.v1"),
        expectation=expectation,
        pre_state_hash=pre_hash,
        proposed_post_state_hash=post_hash,
        workflow_version=WORKFLOW_VERSION,
        reducer_version=REDUCER_VERSION,
        operations=(operation,),
        residuals=residuals,
        evidence_snapshot_hash=evidence_snapshot_hash,
        execution_receipt_hash=execution_receipt_hash,
    )


def plan_reopen_transition(
    projection: ProgramProjection,
    *,
    mechanic_id: str,
    dimension: MechanicDimension,
    reason: str,
    expectation: LedgerExpectation,
    evidence_snapshot_hash: str,
) -> TransitionPlan:
    pre_hash = protected_projection_hash(projection)
    operation = TransitionOperation(
        0,
        TransitionOperationKind.REOPEN_COORDINATE,
        mechanic_id=mechanic_id,
        dimension=dimension.value,
        reason=reason,
    )
    candidate, residual = _reopen_candidate(
        projection, mechanic_id=mechanic_id, dimension=dimension.value, reason=reason
    )
    residuals = (residual,) if residual else ()
    post_hash = protected_projection_hash(candidate)
    payload = canonical_transition_plan_payload(
        expectation=expectation,
        pre_state_hash=pre_hash,
        proposed_post_state_hash=post_hash,
        operations=(operation,),
        residuals=residuals,
        evidence_snapshot_hash=evidence_snapshot_hash,
        execution_receipt_hash=None,
    )
    return TransitionPlan(
        canonical_digest(payload, domain="orion.transition-plan.v1"),
        expectation,
        pre_hash,
        post_hash,
        WORKFLOW_VERSION,
        REDUCER_VERSION,
        (operation,),
        residuals,
        evidence_snapshot_hash,
        None,
    )


def reduce_transition(
    projection: ProgramProjection, plan: TransitionPlan
) -> TransitionReductionResult:
    if protected_projection_hash(projection) != plan.pre_state_hash:
        return TransitionReductionResult(
            projection,
            (),
            (),
            (
                TransitionResidual(
                    TransitionResidualKind.PRE_STATE_MISMATCH,
                    "*",
                    "*",
                    "",
                    "plan pre-state does not match supplied projection",
                ),
            ),
        )
    result = _reduce_operations(projection, plan.operations)
    if result.hash != plan.proposed_post_state_hash:
        return TransitionReductionResult(
            projection,
            (),
            (),
            (
                *result.residuals,
                TransitionResidual(
                    TransitionResidualKind.POST_STATE_MISMATCH,
                    "*",
                    "*",
                    "",
                    "pure reducer output does not match the committed proposed post-state hash",
                ),
            ),
        )
    return result


def plan_batch_transition(
    projection: ProgramProjection,
    records: tuple[AnswerRecord, ...],
    *,
    expectation: LedgerExpectation,
    evidence_snapshot_hash: str,
    execution_receipt_hash: str | None = None,
) -> TransitionPlan:
    if expectation.research_state_hash != protected_projection_hash(projection):
        raise ValueError(
            "batch planning requires expectation bound to the exact pre-state"
        )
    current = projection
    operations: list[TransitionOperation] = []
    residuals: list[TransitionResidual] = []
    for index, record in enumerate(records):
        current, kind, residual = _apply_answer_candidate(current, record)
        operations.append(TransitionOperation(index, kind, record=record))
        if residual is not None:
            residuals.append(residual)
    pre_hash = protected_projection_hash(projection)
    post_hash = protected_projection_hash(current)
    payload = canonical_transition_plan_payload(
        expectation=expectation,
        pre_state_hash=pre_hash,
        proposed_post_state_hash=post_hash,
        operations=tuple(operations),
        residuals=tuple(residuals),
        evidence_snapshot_hash=evidence_snapshot_hash,
        execution_receipt_hash=execution_receipt_hash,
    )
    return TransitionPlan(
        canonical_digest(payload, domain="orion.transition-plan.v1"),
        expectation,
        pre_hash,
        post_hash,
        WORKFLOW_VERSION,
        REDUCER_VERSION,
        tuple(operations),
        tuple(residuals),
        evidence_snapshot_hash,
        execution_receipt_hash,
    )


__all__ = [
    "TransitionOperation",
    "TransitionOperationKind",
    "TransitionPlan",
    "TransitionReductionResult",
    "TransitionResidual",
    "TransitionResidualKind",
    "canonical_transition_plan_payload",
    "plan_answer_transition",
    "plan_batch_transition",
    "plan_reopen_transition",
    "reduce_transition",
]
