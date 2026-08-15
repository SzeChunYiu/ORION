from __future__ import annotations

import json
import random

import pytest

from orion.core.evidence import EvidenceRecord, evidence_record_fingerprint
from orion.mechanics.answers import (
    AnswerApplicationReport,
    AnswerRecord,
    AnswerResidualKind,
    apply_answer_records,
    audit_answer_application,
    load_answer_records,
)
from orion.mechanics.model import HandoffField, MechanicDimension
from orion.mechanics.program import current_program_cells, observe_mechanics_program

_EVIDENCE_REF = (
    "rakl:publication/papers/paper-01-epistemic-mechanics/"
    "sections/02_compatibility_authority.tex@bd4ce50f"
)
_EVIDENCE_RECORD = EvidenceRecord(
    evidence_id=_EVIDENCE_REF,
    content="pinned RAKL compatibility-authority excerpt",
    source_uri="git+https://github.com/SzeChunYiu/RAKL@bd4ce50f",
    domain_ids=("epistemic-mechanics",),
)
_EVIDENCE_DIGEST = evidence_record_fingerprint(_EVIDENCE_RECORD)


def _record(**overrides):
    base = {
        "record_id": "rec-1",
        "mechanic_id": "FRAME.QUESTION.v0",
        "dimension": MechanicDimension.MATHEMATICS,
        "lane": "claude",
        "evidence_refs": (_EVIDENCE_REF,),
        "evidence_bindings": ((_EVIDENCE_REF, _EVIDENCE_DIGEST),),
        "payload": (("mathematical_semantics", ("question relevance is a declared decision-coordinate map",)),),
    }
    base.update(overrides)
    return AnswerRecord(**base)


def _apply(cells, records, *, evidence_records=None):
    if evidence_records is None:
        evidence_records = {_EVIDENCE_REF: _EVIDENCE_RECORD}
    return apply_answer_records(
        cells,
        records,
        evidence_records=evidence_records,
    )


def _open_questions(cells):
    return observe_mechanics_program(cells).open_question_count


def test_content_answer_closes_exactly_one_question():
    cells = current_program_cells()
    before = _open_questions(cells)
    updated, report = _apply(cells, (_record(),))
    after = _open_questions(updated)
    assert report.applied_record_ids == ("rec-1",)
    assert not report.residuals
    assert before - after == 1
    cell = next(item for item in updated if item.mechanic_id == "FRAME.QUESTION.v0")
    assert MechanicDimension.MATHEMATICS not in cell.provisional_dimensions
    assert report.evidence_bindings == (
        ("rec-1", _EVIDENCE_REF, _EVIDENCE_DIGEST),
    )
    assert audit_answer_application(before, after, report) == ()


def test_application_is_order_independent():
    cells = current_program_cells()
    records = [
        _record(),
        _record(
            record_id="rec-2",
            mechanic_id="SEARCH.QUERY.v0",
            dimension=MechanicDimension.STATE,
            payload=(("state_ids", ("active-residual-target-set",)),),
        ),
        _record(
            record_id="rec-3",
            mechanic_id="SEARCH.QUERY.v0",
            dimension=MechanicDimension.VERIFICATION,
            payload=(("verification_contracts", ("query provenance replays to identical route ids",)),),
        ),
    ]
    shuffled = records[:]
    random.Random(7).shuffle(shuffled)
    updated_a, report_a = _apply(cells, tuple(records))
    updated_b, report_b = _apply(cells, tuple(shuffled))
    assert updated_a == updated_b
    assert report_a == report_b


def test_conflicting_answers_apply_nothing_and_emit_residual():
    cells = current_program_cells()
    before = _open_questions(cells)
    records = (
        _record(),
        _record(record_id="rec-9", payload=(("mathematical_semantics", ("a different incompatible formalism",)),)),
    )
    updated, report = _apply(cells, records)
    assert not report.applied_record_ids
    assert [item.kind for item in report.residuals] == [AnswerResidualKind.CONFLICTING_ANSWERS]
    assert _open_questions(updated) == before


def test_linear_supersession_applies_the_tip():
    cells = current_program_cells()
    records = (
        _record(),
        _record(
            record_id="rec-2",
            supersedes="rec-1",
            payload=(("mathematical_semantics", ("refined decision-coordinate map",)),),
        ),
    )
    updated, report = _apply(cells, records)
    assert report.applied_record_ids == ("rec-2",)
    cell = next(item for item in updated if item.mechanic_id == "FRAME.QUESTION.v0")
    assert "refined decision-coordinate map" in cell.mathematical_semantics
    assert "question relevance is a declared decision-coordinate map" not in cell.mathematical_semantics


def test_content_answer_without_evidence_is_rejected():
    cells = current_program_cells()
    before = _open_questions(cells)
    updated, report = _apply(cells, (_record(evidence_refs=(), evidence_bindings=()),))
    assert not report.applied_record_ids
    assert [item.kind for item in report.residuals] == [AnswerResidualKind.NO_EVIDENCE]
    assert _open_questions(updated) == before


def test_waiver_without_protected_authority_is_rejected():
    cells = current_program_cells()
    before = _open_questions(cells)
    record = _record(payload=(), waiver_reason="dimension is owned by the parent cell's contract in this decomposition")
    updated, report = _apply(cells, (record,))
    assert not report.applied_record_ids
    assert not report.waiver_record_ids
    assert [item.kind for item in report.residuals] == ["UNAUTHORIZED_WAIVER"]
    assert _open_questions(updated) == before


def test_waiver_with_resolved_evidence_is_still_rejected():
    cells = current_program_cells()
    record = _record(payload=(), waiver_reason="reviewed but not authorized")
    updated, report = _apply(cells, (record,))
    assert updated == cells
    assert [item.kind for item in report.residuals] == ["UNAUTHORIZED_WAIVER"]


def test_waiver_tip_cannot_supersede_content_into_closure():
    cells = current_program_cells()
    records = (
        _record(record_id="content"),
        _record(
            record_id="waiver",
            supersedes="content",
            payload=(),
            waiver_reason="close it anyway",
        ),
    )
    updated, report = _apply(cells, records)
    assert updated == cells
    assert [item.kind for item in report.residuals] == ["UNAUTHORIZED_WAIVER"]


def test_presence_only_evidence_reference_is_rejected():
    with pytest.raises(ValueError, match="content-bind every evidence reference"):
        _record(
            evidence_refs=("fabricated://not-resolved",),
            evidence_bindings=(),
        )


def test_content_bound_but_unresolved_evidence_is_rejected():
    cells = current_program_cells()
    before = _open_questions(cells)
    updated, report = apply_answer_records(cells, (_record(),), evidence_records={})
    assert not report.applied_record_ids
    assert [item.kind for item in report.residuals] == ["EVIDENCE_UNRESOLVED"]
    assert _open_questions(updated) == before


def test_evidence_binding_must_match_resolved_content():
    cells = current_program_cells()
    before = _open_questions(cells)
    record = _record(evidence_bindings=((_EVIDENCE_REF, "0" * 64),))
    updated, report = _apply(cells, (record,))
    assert not report.applied_record_ids
    assert [item.kind for item in report.residuals] == ["EVIDENCE_MISMATCH"]
    assert _open_questions(updated) == before


def test_same_reference_with_substituted_content_is_rejected():
    cells = current_program_cells()
    substituted = EvidenceRecord(
        evidence_id=_EVIDENCE_REF,
        content="different content under the same identifier",
        source_uri=_EVIDENCE_RECORD.source_uri,
        domain_ids=_EVIDENCE_RECORD.domain_ids,
    )
    updated, report = _apply(
        cells,
        (_record(),),
        evidence_records={_EVIDENCE_REF: substituted},
    )
    assert updated == cells
    assert [item.kind for item in report.residuals] == ["EVIDENCE_MISMATCH"]


def test_disconnected_supersession_cycle_is_a_conflict():
    cells = current_program_cells()
    before = _open_questions(cells)
    records = (
        _record(record_id="base"),
        _record(record_id="tip", supersedes="base"),
        _record(record_id="cycle-a", supersedes="cycle-b"),
        _record(record_id="cycle-b", supersedes="cycle-a"),
    )
    updated, report = _apply(cells, records)
    assert not report.applied_record_ids
    assert [item.kind for item in report.residuals] == [
        AnswerResidualKind.CONFLICTING_ANSWERS
    ]
    assert _open_questions(updated) == before


@pytest.mark.parametrize(
    "records",
    (
        (_record(record_id="tip", supersedes="missing"),),
        (_record(record_id="self", supersedes="self"),),
        (
            _record(record_id="root"),
            _record(record_id="left", supersedes="root"),
            _record(record_id="right", supersedes="root"),
        ),
        (_record(record_id="root-a"), _record(record_id="root-b")),
    ),
)
def test_non_linear_supersession_graphs_are_conflicts(records):
    cells = current_program_cells()
    updated, report = _apply(cells, records)
    assert not report.applied_record_ids
    assert [item.kind for item in report.residuals] == [
        AnswerResidualKind.CONFLICTING_ANSWERS
    ]
    assert updated == cells


def test_duplicate_record_ids_are_rejected_globally():
    cells = current_program_cells()
    records = (
        _record(record_id="duplicate"),
        _record(
            record_id="duplicate",
            mechanic_id="SEARCH.QUERY.v0",
            dimension=MechanicDimension.STATE,
            payload=(("state_ids", ("active-residual-target-set",)),),
        ),
    )
    updated, report = _apply(cells, records)
    assert not report.applied_record_ids
    assert all(
        item.kind == AnswerResidualKind.CONFLICTING_ANSWERS
        for item in report.residuals
    )
    assert updated == cells


def test_unknown_mechanic_is_a_typed_residual():
    cells = current_program_cells()
    updated, report = _apply(cells, (_record(mechanic_id="NOT.A.CELL.v0"),))
    assert [item.kind for item in report.residuals] == [AnswerResidualKind.UNKNOWN_MECHANIC]
    assert updated == cells


def test_handoff_payload_constructs_typed_fields():
    cells = current_program_cells()
    record = _record(
        dimension=MechanicDimension.HANDOFF,
        payload=(),
        handoff_payload=(
            HandoffField(
                field_id="active-question",
                description="the framed question the downstream mechanic receives",
                schema_ref="orion.core.problem.Problem",
            ),
        ),
    )
    updated, report = _apply(cells, (record,))
    assert report.applied_record_ids == ("rec-1",)
    cell = next(item for item in updated if item.mechanic_id == "FRAME.QUESTION.v0")
    assert any(field.field_id == "active-question" for field in cell.handoff_fields)
    assert MechanicDimension.HANDOFF not in cell.provisional_dimensions


def test_audit_flags_unattributable_closure():
    _, report = _apply(current_program_cells(), (_record(),))
    residuals = audit_answer_application(10, 5, report)
    assert [item.kind for item in residuals] == [AnswerResidualKind.AUDIT_REGRESSION]


def test_audit_flags_regression_without_residual():
    _, report = _apply(current_program_cells(), (_record(),))
    residuals = audit_answer_application(10, 12, report)
    assert [item.kind for item in residuals] == [AnswerResidualKind.AUDIT_REGRESSION]


def test_audit_never_licenses_waiver_driven_closure():
    report = AnswerApplicationReport(
        applied_record_ids=("waiver",),
        waiver_record_ids=("waiver",),
        residuals=(),
    )
    residuals = audit_answer_application(10, 9, report)
    assert [item.kind for item in residuals] == ["UNAUTHORIZED_WAIVER"]


def test_record_requires_content_xor_waiver():
    with pytest.raises(ValueError):
        _record(payload=(), waiver_reason="")
    with pytest.raises(ValueError):
        _record(waiver_reason="both is invalid")


def test_record_rejects_field_outside_dimension():
    with pytest.raises(ValueError):
        _record(payload=(("verification_contracts", ("wrong field for MATHEMATICS",)),))


def test_load_answer_records_round_trips(tmp_path):
    lane_dir = tmp_path / "claude"
    lane_dir.mkdir()
    row = {
        "record_id": "rec-file-1",
        "mechanic_id": "FRAME.QUESTION.v0",
        "dimension": "MATHEMATICS",
        "evidence_refs": [_EVIDENCE_REF],
        "evidence_bindings": {_EVIDENCE_REF: _EVIDENCE_DIGEST},
        "payload": {"mathematical_semantics": ["a persisted formal contract"]},
    }
    (lane_dir / "FRAME.QUESTION.v0.jsonl").write_text(json.dumps(row) + "\n")
    records = load_answer_records(tmp_path)
    assert len(records) == 1
    assert records[0].lane == "claude"
    updated, report = _apply(current_program_cells(), records)
    assert report.applied_record_ids == ("rec-file-1",)
    cell = next(item for item in updated if item.mechanic_id == "FRAME.QUESTION.v0")
    assert "a persisted formal contract" in cell.mathematical_semantics
