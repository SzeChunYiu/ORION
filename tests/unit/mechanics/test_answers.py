from __future__ import annotations

import json
import random

import pytest

from orion.mechanics.answers import (
    AnswerRecord,
    AnswerResidualKind,
    apply_answer_records,
    audit_answer_application,
    load_answer_records,
)
from orion.mechanics.model import HandoffField, MechanicDimension
from orion.mechanics.program import current_program_cells, observe_mechanics_program


def _record(**overrides):
    base = dict(
        record_id="rec-1",
        mechanic_id="FRAME.QUESTION.v0",
        dimension=MechanicDimension.MATHEMATICS,
        lane="claude",
        evidence_refs=("rakl:publication/papers/paper-01-epistemic-mechanics/sections/02_compatibility_authority.tex@bd4ce50f",),
        payload=(("mathematical_semantics", ("question relevance is a declared decision-coordinate map",)),),
    )
    base.update(overrides)
    return AnswerRecord(**base)


def _open_questions(cells):
    return observe_mechanics_program(cells).open_question_count


def test_content_answer_closes_exactly_one_question():
    cells = current_program_cells()
    before = _open_questions(cells)
    updated, report = apply_answer_records(cells, (_record(),))
    after = _open_questions(updated)
    assert report.applied_record_ids == ("rec-1",)
    assert not report.residuals
    assert before - after == 1
    cell = next(item for item in updated if item.mechanic_id == "FRAME.QUESTION.v0")
    assert MechanicDimension.MATHEMATICS not in cell.provisional_dimensions
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
    updated_a, report_a = apply_answer_records(cells, tuple(records))
    updated_b, report_b = apply_answer_records(cells, tuple(shuffled))
    assert updated_a == updated_b
    assert report_a == report_b


def test_conflicting_answers_apply_nothing_and_emit_residual():
    cells = current_program_cells()
    before = _open_questions(cells)
    records = (
        _record(),
        _record(record_id="rec-9", payload=(("mathematical_semantics", ("a different incompatible formalism",)),)),
    )
    updated, report = apply_answer_records(cells, records)
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
    updated, report = apply_answer_records(cells, records)
    assert report.applied_record_ids == ("rec-2",)
    cell = next(item for item in updated if item.mechanic_id == "FRAME.QUESTION.v0")
    assert "refined decision-coordinate map" in cell.mathematical_semantics
    assert "question relevance is a declared decision-coordinate map" not in cell.mathematical_semantics


def test_content_answer_without_evidence_is_rejected():
    cells = current_program_cells()
    before = _open_questions(cells)
    updated, report = apply_answer_records(cells, (_record(evidence_refs=()),))
    assert not report.applied_record_ids
    assert [item.kind for item in report.residuals] == [AnswerResidualKind.NO_EVIDENCE]
    assert _open_questions(updated) == before


def test_waiver_closes_question_and_is_reported_separately():
    cells = current_program_cells()
    before = _open_questions(cells)
    record = _record(payload=(), waiver_reason="dimension is owned by the parent cell's contract in this decomposition")
    updated, report = apply_answer_records(cells, (record,))
    after = _open_questions(updated)
    assert report.applied_record_ids == ("rec-1",)
    assert report.waiver_record_ids == ("rec-1",)
    assert report.content_applied_count == 0
    assert before - after == 1
    cell = next(item for item in updated if item.mechanic_id == "FRAME.QUESTION.v0")
    assert MechanicDimension.MATHEMATICS in cell.waived_dimensions


def test_unknown_mechanic_is_a_typed_residual():
    cells = current_program_cells()
    updated, report = apply_answer_records(cells, (_record(mechanic_id="NOT.A.CELL.v0"),))
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
    updated, report = apply_answer_records(cells, (record,))
    assert report.applied_record_ids == ("rec-1",)
    cell = next(item for item in updated if item.mechanic_id == "FRAME.QUESTION.v0")
    assert any(field.field_id == "active-question" for field in cell.handoff_fields)
    assert MechanicDimension.HANDOFF not in cell.provisional_dimensions


def test_audit_flags_unattributable_closure():
    _, report = apply_answer_records(current_program_cells(), (_record(),))
    residuals = audit_answer_application(10, 5, report)
    assert [item.kind for item in residuals] == [AnswerResidualKind.AUDIT_REGRESSION]


def test_audit_flags_regression_without_residual():
    _, report = apply_answer_records(current_program_cells(), (_record(),))
    residuals = audit_answer_application(10, 12, report)
    assert [item.kind for item in residuals] == [AnswerResidualKind.AUDIT_REGRESSION]


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
        "evidence_refs": ["rakl:some/path@bd4ce50f"],
        "payload": {"mathematical_semantics": ["a persisted formal contract"]},
    }
    (lane_dir / "FRAME.QUESTION.v0.jsonl").write_text(json.dumps(row) + "\n")
    records = load_answer_records(tmp_path)
    assert len(records) == 1
    assert records[0].lane == "claude"
    updated, report = apply_answer_records(current_program_cells(), records)
    assert report.applied_record_ids == ("rec-file-1",)
    cell = next(item for item in updated if item.mechanic_id == "FRAME.QUESTION.v0")
    assert "a persisted formal contract" in cell.mathematical_semantics
