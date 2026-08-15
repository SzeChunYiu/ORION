from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path

from .model import DimensionWaiver, HandoffField, MechanicCell, MechanicDimension

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
    MechanicDimension.DEPENDENCIES: ("dependency_ids",),
    MechanicDimension.REOPEN: ("reopen_triggers",),
    MechanicDimension.SEARCH_COVERAGE: ("search_coverage_obligations",),
    MechanicDimension.PARENT_DISCIPLINE: ("parent_domain_hypotheses",),
    MechanicDimension.SATURATION: ("saturation_criteria",),
    MechanicDimension.EMPIRICAL_OPEN: ("empirical_open_coordinates",),
}


class AnswerResidualKind:
    UNKNOWN_MECHANIC = "UNKNOWN_MECHANIC"
    NO_EVIDENCE = "NO_EVIDENCE"
    CONFLICTING_ANSWERS = "CONFLICTING_ANSWERS"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"
    AUDIT_REGRESSION = "AUDIT_REGRESSION"


@dataclass(frozen=True)
class AnswerRecord:
    """One persisted proposal that a mechanic dimension question has an answer.

    A record is proposal-only data. Applying it is a separate mechanical
    transition (`apply_answer_records`) with its own fail-closed validation;
    an applied record clears the dimension's provisional marker, a waiver
    record converts the question into an audited waiver instead.
    """

    record_id: str
    mechanic_id: str
    dimension: MechanicDimension
    lane: str
    evidence_refs: tuple[str, ...] = ()
    payload: tuple[tuple[str, tuple[str, ...]], ...] = ()
    handoff_payload: tuple[HandoffField, ...] = ()
    waiver_reason: str = ""
    supersedes: str = ""

    def __post_init__(self) -> None:
        if not self.record_id.strip() or not self.mechanic_id.strip() or not self.lane.strip():
            raise ValueError("answer record identity, mechanic and lane are required")
        has_content = bool(self.payload) or bool(self.handoff_payload)
        if has_content == bool(self.waiver_reason.strip()):
            raise ValueError("an answer record carries either content payload or a waiver reason")
        if self.handoff_payload and self.dimension is not MechanicDimension.HANDOFF:
            raise ValueError("handoff payload is only valid for the HANDOFF dimension")
        if self.payload:
            allowed = _STRING_FIELDS_BY_DIMENSION.get(self.dimension)
            if allowed is None:
                raise ValueError(f"dimension {self.dimension.value} requires a structured payload path")
            for field_name, values in self.payload:
                if field_name not in allowed:
                    raise ValueError(f"field {field_name} is not writable for dimension {self.dimension.value}")
                if not values or any(not item.strip() for item in values):
                    raise ValueError("payload values must be non-empty strings")


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

    @property
    def content_applied_count(self) -> int:
        return len(self.applied_record_ids) - len(self.waiver_record_ids)


def _sorted_records(records: tuple[AnswerRecord, ...]) -> tuple[AnswerRecord, ...]:
    return tuple(sorted(records, key=lambda item: (item.mechanic_id, item.dimension.value, item.record_id)))


def _resolve_supersession(
    group: tuple[AnswerRecord, ...],
) -> tuple[AnswerRecord | None, tuple[AnswerRecord, ...]]:
    """Return (tip, superseded) if the group forms one linear supersession chain."""

    by_id = {item.record_id: item for item in group}
    superseded_ids = {item.supersedes for item in group if item.supersedes}
    if any(identifier not in by_id for identifier in superseded_ids):
        return None, ()
    tips = [item for item in group if item.record_id not in superseded_ids]
    if len(tips) != 1:
        return None, ()
    ordered = tuple(item for item in group if item is not tips[0])
    return tips[0], ordered


def apply_answer_records(
    cells: tuple[MechanicCell, ...],
    records: tuple[AnswerRecord, ...],
) -> tuple[tuple[MechanicCell, ...], AnswerApplicationReport]:
    """Deterministically fold answer records into mechanic cells.

    Fail-closed rules: evidence-free content answers are rejected (a restated
    envelope without evidence cannot clear a provisional marker); conflicting
    same-coordinate answers from different records become a typed residual and
    neither applies; unknown mechanics become residuals rather than silent drops.
    """

    by_id = {cell.mechanic_id: cell for cell in cells}
    residuals: list[AnswerResidual] = []
    applied: list[str] = []
    waivers: list[str] = []

    groups: dict[tuple[str, MechanicDimension], list[AnswerRecord]] = {}
    for record in _sorted_records(records):
        if record.mechanic_id not in by_id:
            residuals.append(
                AnswerResidual(
                    AnswerResidualKind.UNKNOWN_MECHANIC,
                    record.mechanic_id,
                    record.dimension,
                    (record.record_id,),
                    "answer targets a mechanic that is not reachable in the current decomposition",
                )
            )
            continue
        if not record.waiver_reason and not record.evidence_refs:
            residuals.append(
                AnswerResidual(
                    AnswerResidualKind.NO_EVIDENCE,
                    record.mechanic_id,
                    record.dimension,
                    (record.record_id,),
                    "content answers require at least one evidence reference",
                )
            )
            continue
        groups.setdefault((record.mechanic_id, record.dimension), []).append(record)

    for (mechanic_id, dimension), group in sorted(
        groups.items(), key=lambda item: (item[0][0], item[0][1].value)
    ):
        tip, _ = _resolve_supersession(tuple(group))
        if tip is None:
            residuals.append(
                AnswerResidual(
                    AnswerResidualKind.CONFLICTING_ANSWERS,
                    mechanic_id,
                    dimension,
                    tuple(item.record_id for item in group),
                    "multiple live answers target one mechanic dimension without a linear supersession chain",
                )
            )
            continue
        cell = by_id[mechanic_id]
        if tip.waiver_reason:
            if dimension in cell.waived_dimensions:
                residuals.append(
                    AnswerResidual(
                        AnswerResidualKind.CONFLICTING_ANSWERS,
                        mechanic_id,
                        dimension,
                        (tip.record_id,),
                        "dimension already carries a waiver",
                    )
                )
                continue
            cell = replace(
                cell,
                waivers=(*cell.waivers, DimensionWaiver(dimension=dimension, reason=tip.waiver_reason)),
                provisional_dimensions=tuple(
                    item for item in cell.provisional_dimensions if item is not dimension
                ),
            )
            waivers.append(tip.record_id)
        else:
            updates: dict[str, tuple[str, ...]] = {}
            if tip.handoff_payload:
                existing_ids = {item.field_id for item in cell.handoff_fields}
                fresh = tuple(item for item in tip.handoff_payload if item.field_id not in existing_ids)
                cell = replace(cell, handoff_fields=(*cell.handoff_fields, *fresh))
            for field_name, values in tip.payload:
                current: tuple[str, ...] = getattr(cell, field_name)
                updates[field_name] = tuple(dict.fromkeys((*current, *values)))
            if updates:
                cell = replace(cell, **updates)
            cell = replace(
                cell,
                provisional_dimensions=tuple(
                    item for item in cell.provisional_dimensions if item is not dimension
                ),
            )
        by_id[mechanic_id] = cell
        applied.append(tip.record_id)

    report = AnswerApplicationReport(
        applied_record_ids=tuple(applied),
        waiver_record_ids=tuple(waivers),
        residuals=tuple(residuals),
    )
    return tuple(by_id[cell.mechanic_id] for cell in cells), report


def audit_answer_application(
    open_questions_before: int,
    open_questions_after: int,
    report: AnswerApplicationReport,
) -> tuple[AnswerResidual, ...]:
    """The false-progress guard for answer application.

    Closure must be attributable: the open-question count may drop by at most
    the number of applied records, waiver-driven closure is reported separately
    from content-driven closure, and any increase without a residual is a
    regression. Returns residuals; an empty tuple means the delta is licensed.
    """

    residuals: list[AnswerResidual] = []
    closed = open_questions_before - open_questions_after
    if closed < 0 and not report.residuals:
        residuals.append(
            AnswerResidual(
                AnswerResidualKind.AUDIT_REGRESSION,
                "*",
                None,
                report.applied_record_ids,
                "open questions increased without a typed residual explaining why",
            )
        )
    if closed > len(report.applied_record_ids):
        residuals.append(
            AnswerResidual(
                AnswerResidualKind.AUDIT_REGRESSION,
                "*",
                None,
                report.applied_record_ids,
                "more questions closed than answers applied; closure is not attributable",
            )
        )
    return tuple(residuals)


def load_answer_records(root: Path) -> tuple[AnswerRecord, ...]:
    """Load answer records from per-lane JSONL files under ``root``.

    Layout: ``<root>/<lane>/<mechanic_id>.jsonl`` with one JSON object per
    line. Files are read in sorted order so the result is order-independent
    of filesystem enumeration.
    """

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
                    payload=tuple(
                        (field_name, tuple(values))
                        for field_name, values in sorted(raw.get("payload", {}).items())
                    ),
                    handoff_payload=tuple(
                        HandoffField(
                            field_id=item["field_id"],
                            description=item["description"],
                            schema_ref=item["schema_ref"],
                            required=bool(item.get("required", True)),
                        )
                        for item in raw.get("handoff_payload", ())
                    ),
                    waiver_reason=raw.get("waiver_reason", ""),
                    supersedes=raw.get("supersedes", ""),
                )
            )
            del line_number
    return _sorted_records(tuple(records))
