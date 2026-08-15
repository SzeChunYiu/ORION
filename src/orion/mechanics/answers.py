from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path

from orion.core.evidence import EvidenceRecord, evidence_record_fingerprint

from .model import (
    HandoffField,
    MechanicCell,
    MechanicDimension,
    MetricDirection,
    MetricKind,
    MetricSpec,
)

_STRING_FIELDS_BY_DIMENSION: dict[MechanicDimension, tuple[str, ...]] = {
    MechanicDimension.INPUTS: ("input_ids",),
    MechanicDimension.OUTPUTS: ("output_ids",),
    MechanicDimension.STATE: ("state_ids",),
    MechanicDimension.OBSERVABILITY: ("observable_ids",),
    MechanicDimension.ACTIONS: ("action_ids",),
    MechanicDimension.TRANSITION_MODEL: ("transition_semantics",),
    MechanicDimension.MATHEMATICS: ("mathematical_semantics",),
    MechanicDimension.INVARIANTS: ("invariant_ids", "constraint_ids"),
    MechanicDimension.OBJECTIVE: ("objective_ids",),
    MechanicDimension.OPTIMIZATION: ("optimization_rules",),
    MechanicDimension.UNCERTAINTY: ("uncertainty_semantics",),
    MechanicDimension.RESOURCES: ("resource_coordinates",),
    MechanicDimension.FAILURE: ("failure_signatures", "falsifiers"),
    MechanicDimension.DIAGNOSIS: ("diagnosis_rules",),
    MechanicDimension.STORAGE: ("storage_contracts",),
    MechanicDimension.PROVENANCE: ("provenance_contracts",),
    MechanicDimension.VERIFICATION: ("verification_contracts",),
    MechanicDimension.AUTHORITY_SECURITY: ("authority_boundaries",),
    MechanicDimension.ENGINEERING: ("engineering_contracts",),
    MechanicDimension.DEPENDENCIES: ("dependency_ids", "external_dependency_contract_ids"),
    MechanicDimension.REOPEN: ("reopen_triggers",),
    MechanicDimension.SEARCH_COVERAGE: ("search_coverage_obligations",),
    MechanicDimension.PARENT_DISCIPLINE: ("parent_domain_hypotheses",),
    MechanicDimension.SATURATION: ("saturation_criteria",),
    MechanicDimension.EMPIRICAL_OPEN: ("empirical_open_coordinates",),
}


class AnswerResidualKind:
    UNKNOWN_MECHANIC = "UNKNOWN_MECHANIC"
    NO_EVIDENCE = "NO_EVIDENCE"
    EVIDENCE_UNRESOLVED = "EVIDENCE_UNRESOLVED"
    EVIDENCE_MISMATCH = "EVIDENCE_MISMATCH"
    UNAUTHORIZED_WAIVER = "UNAUTHORIZED_WAIVER"
    CONFLICTING_ANSWERS = "CONFLICTING_ANSWERS"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"
    AUDIT_REGRESSION = "AUDIT_REGRESSION"


@dataclass(frozen=True)
class AnswerRecord:
    """One persisted proposal that a mechanic dimension question has an answer.

    A record is proposal-only data. Applying it is a separate mechanical
    transition (`apply_answer_records`) with its own fail-closed validation.
    Content answers must bind every evidence reference to a host-owned immutable
    EvidenceRecord fingerprint. Waiver proposals are never authority-bearing in V0.
    """

    record_id: str
    mechanic_id: str
    dimension: MechanicDimension
    lane: str
    evidence_refs: tuple[str, ...] = ()
    evidence_bindings: tuple[tuple[str, str], ...] = ()
    payload: tuple[tuple[str, tuple[str, ...]], ...] = ()
    handoff_payload: tuple[HandoffField, ...] = ()
    metric_payload: tuple[MetricSpec, ...] = ()
    waiver_reason: str = ""
    supersedes: str = ""

    def __post_init__(self) -> None:
        if not self.record_id.strip() or not self.mechanic_id.strip() or not self.lane.strip():
            raise ValueError("answer record identity, mechanic and lane are required")
        content_paths = sum(bool(item) for item in (self.payload, self.handoff_payload, self.metric_payload))
        if (content_paths > 0) == bool(self.waiver_reason.strip()):
            raise ValueError("an answer record carries content payload or a waiver reason, never both/neither")
        if content_paths > 1:
            raise ValueError("an answer record uses exactly one structured payload path")
        if self.handoff_payload and self.dimension is not MechanicDimension.HANDOFF:
            raise ValueError("handoff payload is only valid for the HANDOFF dimension")
        if self.metric_payload and self.dimension is not MechanicDimension.METRICS:
            raise ValueError("metric payload is only valid for the METRICS dimension")
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise ValueError("answer evidence references must be unique")
        binding_ids = [reference for reference, _ in self.evidence_bindings]
        if len(set(binding_ids)) != len(binding_ids):
            raise ValueError("answer evidence bindings must have unique references")
        if set(binding_ids) != set(self.evidence_refs):
            raise ValueError("answer records must content-bind every evidence reference")
        for _, digest in self.evidence_bindings:
            if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
                raise ValueError("answer evidence bindings require SHA-256 hashes")
        if self.payload:
            allowed = _STRING_FIELDS_BY_DIMENSION.get(self.dimension)
            if allowed is None:
                raise ValueError(f"dimension {self.dimension.value} requires a structured payload path")
            for field_name, values in self.payload:
                if field_name not in allowed:
                    raise ValueError(f"field {field_name} is not writable for dimension {self.dimension.value}")
                if not values or any(not item.strip() for item in values):
                    raise ValueError("payload values must be non-empty strings")
        metric_ids = [item.metric_id for item in self.metric_payload]
        if len(set(metric_ids)) != len(metric_ids):
            raise ValueError("metric answer payload ids must be unique")


@dataclass(frozen=True)
class AnswerResidual:
    kind: str
    mechanic_id: str
    dimension: MechanicDimension | None
    record_ids: tuple[str, ...]
    note: str


@dataclass(frozen=True)
class AnswerApplicationReport:
    applied_record_ids: tuple[str, ...]
    waiver_record_ids: tuple[str, ...]
    residuals: tuple[AnswerResidual, ...]
    evidence_bindings: tuple[tuple[str, str, str], ...] = ()

    @property
    def content_applied_count(self) -> int:
        return len(self.applied_record_ids) - len(self.waiver_record_ids)


def _sorted_records(records: tuple[AnswerRecord, ...]) -> tuple[AnswerRecord, ...]:
    return tuple(sorted(records, key=lambda item: (item.mechanic_id, item.dimension.value, item.record_id)))


def _resolve_supersession(group: tuple[AnswerRecord, ...]) -> tuple[AnswerRecord | None, tuple[AnswerRecord, ...]]:
    """Return (tip, superseded) if the group forms one linear supersession chain."""

    by_id = {item.record_id: item for item in group}
    if len(by_id) != len(group):
        return None, ()
    superseded_ids = {item.supersedes for item in group if item.supersedes}
    if any(identifier not in by_id for identifier in superseded_ids):
        return None, ()
    roots = [item for item in group if not item.supersedes]
    if len(roots) != 1:
        return None, ()
    successor_counts = {identifier: sum(item.supersedes == identifier for item in group) for identifier in by_id}
    if any(count > 1 for count in successor_counts.values()):
        return None, ()
    tips = [item for item in group if item.record_id not in superseded_ids]
    if len(tips) != 1:
        return None, ()
    visited: list[AnswerRecord] = []
    current = tips[0]
    while True:
        if current in visited:
            return None, ()
        visited.append(current)
        if not current.supersedes:
            break
        current = by_id[current.supersedes]
    if len(visited) != len(group) or visited[-1] is not roots[0]:
        return None, ()
    return tips[0], tuple(visited[1:])


def _evidence_residual(record: AnswerRecord, evidence_records: Mapping[str, EvidenceRecord]) -> tuple[str, str] | None:
    if not record.evidence_refs:
        return (AnswerResidualKind.NO_EVIDENCE, "content answers require at least one evidence reference")
    bindings = dict(record.evidence_bindings)
    if any(reference not in evidence_records for reference in record.evidence_refs):
        return (AnswerResidualKind.EVIDENCE_UNRESOLVED, "every evidence reference must resolve in the host-owned evidence index")
    for reference in record.evidence_refs:
        expected = bindings[reference]
        resolved = evidence_records[reference]
        if resolved.evidence_id != reference:
            return (AnswerResidualKind.EVIDENCE_UNRESOLVED, f"evidence index key does not match the resolved record identity: {reference}")
        actual = evidence_record_fingerprint(resolved)
        if actual != expected:
            return (AnswerResidualKind.EVIDENCE_MISMATCH, f"evidence content does not match the declared digest: {reference}")
    return None


def apply_answer_records(
    cells: tuple[MechanicCell, ...],
    records: tuple[AnswerRecord, ...],
    *,
    evidence_records: Mapping[str, EvidenceRecord],
) -> tuple[tuple[MechanicCell, ...], AnswerApplicationReport]:
    """Deterministically fold evidence-bound answer records into mechanic cells."""

    by_id = {cell.mechanic_id: cell for cell in cells}
    residuals: list[AnswerResidual] = []
    applied: list[str] = []
    waivers: list[str] = []
    applied_evidence_bindings: list[tuple[str, str, str]] = []
    groups: dict[tuple[str, MechanicDimension], list[AnswerRecord]] = {}
    record_id_counts = {record_id: sum(record.record_id == record_id for record in records) for record_id in {record.record_id for record in records}}

    for record in _sorted_records(records):
        if record_id_counts[record.record_id] > 1:
            residuals.append(AnswerResidual(AnswerResidualKind.CONFLICTING_ANSWERS, record.mechanic_id, record.dimension, (record.record_id,), "answer record ids must be globally unique"))
            continue
        if record.mechanic_id not in by_id:
            residuals.append(AnswerResidual(AnswerResidualKind.UNKNOWN_MECHANIC, record.mechanic_id, record.dimension, (record.record_id,), "answer targets a mechanic that is not reachable in the current decomposition"))
            continue
        groups.setdefault((record.mechanic_id, record.dimension), []).append(record)

    for (mechanic_id, dimension), group in sorted(groups.items(), key=lambda item: (item[0][0], item[0][1].value)):
        tip, _ = _resolve_supersession(tuple(group))
        if tip is None:
            residuals.append(AnswerResidual(AnswerResidualKind.CONFLICTING_ANSWERS, mechanic_id, dimension, tuple(item.record_id for item in group), "multiple live answers target one mechanic dimension without a linear supersession chain"))
            continue
        if tip.waiver_reason:
            residuals.append(AnswerResidual(AnswerResidualKind.UNAUTHORIZED_WAIVER, tip.mechanic_id, tip.dimension, (tip.record_id,), "V0 has no protected waiver authority path; waiver proposals cannot close questions"))
            continue
        evidence_failure = _evidence_residual(tip, evidence_records)
        if evidence_failure is not None:
            kind, note = evidence_failure
            residuals.append(AnswerResidual(kind, tip.mechanic_id, tip.dimension, (tip.record_id,), note))
            continue
        cell = by_id[mechanic_id]
        updates: dict[str, tuple[str, ...]] = {}
        if tip.handoff_payload:
            existing_ids = {item.field_id for item in cell.handoff_fields}
            fresh = tuple(item for item in tip.handoff_payload if item.field_id not in existing_ids)
            cell = replace(cell, handoff_fields=(*cell.handoff_fields, *fresh))
        elif tip.metric_payload:
            existing_ids = {item.metric_id for item in cell.metrics}
            fresh_metrics = tuple(item for item in tip.metric_payload if item.metric_id not in existing_ids)
            cell = replace(cell, metrics=(*cell.metrics, *fresh_metrics))
        for field_name, values in tip.payload:
            current: tuple[str, ...] = getattr(cell, field_name)
            updates[field_name] = tuple(dict.fromkeys((*current, *values)))
        if updates:
            cell = replace(cell, **updates)
        cell = replace(cell, provisional_dimensions=tuple(item for item in cell.provisional_dimensions if item is not dimension))
        by_id[mechanic_id] = cell
        applied.append(tip.record_id)
        applied_evidence_bindings.extend((tip.record_id, reference, digest) for reference, digest in tip.evidence_bindings)

    report = AnswerApplicationReport(tuple(applied), tuple(waivers), tuple(residuals), tuple(applied_evidence_bindings))
    return tuple(by_id[cell.mechanic_id] for cell in cells), report


def audit_answer_application(open_questions_before: int, open_questions_after: int, report: AnswerApplicationReport) -> tuple[AnswerResidual, ...]:
    residuals: list[AnswerResidual] = []
    closed = open_questions_before - open_questions_after
    if closed < 0 and not report.residuals:
        residuals.append(AnswerResidual(AnswerResidualKind.AUDIT_REGRESSION, "*", None, report.applied_record_ids, "open questions increased without a typed residual explaining why"))
    if closed > len(report.applied_record_ids):
        residuals.append(AnswerResidual(AnswerResidualKind.AUDIT_REGRESSION, "*", None, report.applied_record_ids, "more questions closed than answers applied; closure is not attributable"))
    if report.waiver_record_ids:
        residuals.append(AnswerResidual(AnswerResidualKind.UNAUTHORIZED_WAIVER, "*", None, report.waiver_record_ids, "waiver-driven closure is not licensed without a protected authority path"))
    return tuple(residuals)


def _load_metric(raw: dict[str, object]) -> MetricSpec:
    return MetricSpec(
        metric_id=str(raw["metric_id"]),
        description=str(raw["description"]),
        kind=MetricKind(str(raw["kind"])),
        direction=MetricDirection(str(raw["direction"])),
        unit=str(raw["unit"]),
        required_for_handoff=bool(raw.get("required_for_handoff", False)),
        threshold_semantics=str(raw.get("threshold_semantics", "")),
        uncertainty_semantics=str(raw.get("uncertainty_semantics", "")),
    )


def load_answer_records(root: Path) -> tuple[AnswerRecord, ...]:
    records: list[AnswerRecord] = []
    for path in sorted(root.glob("*/*.jsonl")):
        lane = path.parent.name
        for line_number, line in enumerate(path.read_text().splitlines(), start=1):
            if not line.strip():
                continue
            raw = json.loads(line)
            records.append(
                AnswerRecord(
                    record_id=raw["record_id"],
                    mechanic_id=raw["mechanic_id"],
                    dimension=MechanicDimension(raw["dimension"]),
                    lane=raw.get("lane", lane),
                    evidence_refs=tuple(raw.get("evidence_refs", ())),
                    evidence_bindings=tuple(sorted(raw.get("evidence_bindings", {}).items())),
                    payload=tuple((field_name, tuple(values)) for field_name, values in sorted(raw.get("payload", {}).items())),
                    handoff_payload=tuple(HandoffField(field_id=item["field_id"], description=item["description"], schema_ref=item["schema_ref"], required=bool(item.get("required", True))) for item in raw.get("handoff_payload", ())),
                    metric_payload=tuple(_load_metric(item) for item in raw.get("metric_payload", ())),
                    waiver_reason=raw.get("waiver_reason", ""),
                    supersedes=raw.get("supersedes", ""),
                )
            )
            del line_number
    return _sorted_records(tuple(records))


__all__ = [
    "AnswerApplicationReport",
    "AnswerRecord",
    "AnswerResidual",
    "AnswerResidualKind",
    "apply_answer_records",
    "audit_answer_application",
    "load_answer_records",
]
