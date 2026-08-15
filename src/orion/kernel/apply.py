from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path

from orion.mechanics.answers import (
    AnswerApplicationReport,
    AnswerRecord,
    apply_answer_records,
)
from orion.mechanics.model import MechanicCell, MechanicDimension

from .evidence import build_evidence_index, resolve_evidence_refs
from .gate import AnswerAuthority, AnswerGrading, DiscriminatingCheck, grade_answer


@dataclass(frozen=True)
class GradedApplication:
    """The result of grading a batch of answers and applying only what passed."""

    cells: tuple[MechanicCell, ...]
    gradings: tuple[AnswerGrading, ...]
    report: AnswerApplicationReport

    @property
    def verified_record_ids(self) -> tuple[str, ...]:
        return tuple(
            item.record_id
            for item in self.gradings
            if item.authority is AnswerAuthority.VERIFIED
        )

    @property
    def evidence_bound_record_ids(self) -> tuple[str, ...]:
        return tuple(
            item.record_id
            for item in self.gradings
            if item.authority is AnswerAuthority.EVIDENCE_BOUND
        )

    @property
    def refused_record_ids(self) -> tuple[str, ...]:
        return tuple(item.record_id for item in self.gradings if not item.applicable)


def _index_for(
    records: tuple[AnswerRecord, ...],
    evidence_roots: Mapping[str, Path],
    require_digest: bool,
) -> dict[str, object]:
    """Build the host-owned evidence index from what actually resolves on disk.

    `apply_answer_records` checks that each record's declared binding matches
    this index. Because the host builds the index from real artifacts rather
    than trusting the record, the two checks compose: a lane can neither cite
    evidence that does not exist nor declare a digest it did not read.
    """

    refs = tuple(dict.fromkeys(ref for record in records for ref in record.evidence_refs))
    return build_evidence_index(
        resolve_evidence_refs(refs, evidence_roots, require_digest=require_digest)
    )


def _candidate_cell(
    cells: tuple[MechanicCell, ...],
    record: AnswerRecord,
    index: Mapping[str, object],
) -> MechanicCell | None:
    """Return the target cell as it would look with only this answer applied."""

    applied, _ = apply_answer_records(cells, (record,), evidence_records=index)
    for cell in applied:
        if cell.mechanic_id == record.mechanic_id:
            return cell
    return None


def enforce_authority_provisionality(
    cells: tuple[MechanicCell, ...], gradings: tuple[AnswerGrading, ...]
) -> tuple[MechanicCell, ...]:
    """Keep every non-verified closure marked provisional.

    `apply_answer_records` clears the provisional marker for any content answer.
    That is correct for an externally verified answer and wrong for a machine's
    own proposal: it would let the loop close its audit questions by writing
    strings. Re-marking evidence-bound dimensions keeps the content, keeps the
    question open, and keeps progress measured by verification rather than by
    volume of text.
    """

    wanted: dict[str, list[MechanicDimension]] = {}
    for grading in gradings:
        if grading.authority is AnswerAuthority.EVIDENCE_BOUND:
            wanted.setdefault(grading.mechanic_id, []).append(grading.dimension)
    if not wanted:
        return cells
    updated: list[MechanicCell] = []
    for cell in cells:
        dimensions = wanted.get(cell.mechanic_id)
        if not dimensions:
            updated.append(cell)
            continue
        merged = list(cell.provisional_dimensions)
        seen = set(merged)
        for dimension in dimensions:
            if dimension in seen or dimension in cell.waived_dimensions:
                continue
            merged.append(dimension)
            seen.add(dimension)
        updated.append(replace(cell, provisional_dimensions=tuple(merged)))
    return tuple(updated)


def grade_and_apply(
    cells: tuple[MechanicCell, ...],
    records: tuple[AnswerRecord, ...],
    *,
    evidence_roots: Mapping[str, Path],
    checks: Mapping[str, DiscriminatingCheck] = {},
    require_digest: bool = True,
    round_index: int = 0,
) -> GradedApplication:
    """Grade every answer, then apply only those that earned application.

    Refused answers are not silently dropped: their gradings carry the typed
    reason, which is what a later round turns into failure episodes.
    """

    index = _index_for(records, evidence_roots, require_digest)
    gradings: list[AnswerGrading] = []
    applicable: list[AnswerRecord] = []
    for record in records:
        candidate = _candidate_cell(cells, record, index)
        if candidate is None:
            continue
        grading = grade_answer(
            record,
            candidate,
            evidence_roots=evidence_roots,
            checks=checks,
            require_digest=require_digest,
            round_index=round_index,
        )
        gradings.append(grading)
        if grading.applicable:
            applicable.append(record)

    applied_cells, report = apply_answer_records(
        cells, tuple(applicable), evidence_records=index
    )
    graded = tuple(gradings)
    final_cells = enforce_authority_provisionality(applied_cells, graded)
    return GradedApplication(cells=final_cells, gradings=graded, report=report)
