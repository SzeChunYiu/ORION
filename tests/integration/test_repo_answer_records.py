from __future__ import annotations

from pathlib import Path

from orion.mechanics.answers import (
    apply_answer_records,
    audit_answer_application,
    load_answer_records,
)
from orion.mechanics.program import current_program_cells, observe_mechanics_program

ANSWERS_ROOT = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "development"
    / "mechanic-answer-loop"
    / "answers"
)


def test_repo_answer_records_apply_cleanly():
    """The committed answer ledger must always apply to the live decomposition.

    This binds the repository's persisted answers to CI: a decomposition or
    schema change that orphans a record, a conflicting pair of records, or an
    evidence-free record fails the build instead of rotting silently — the
    ledger-staleness-by-omission failure mode this loop exists to prevent.
    """

    records = load_answer_records(ANSWERS_ROOT)
    assert records, "the answer ledger exists and is non-empty"

    cells = current_program_cells()
    before = observe_mechanics_program(cells).open_question_count
    updated, report = apply_answer_records(cells, records)
    after = observe_mechanics_program(updated).open_question_count

    assert not report.residuals, [
        (item.kind, item.mechanic_id, item.note) for item in report.residuals
    ]
    assert len(report.applied_record_ids) == len(records)
    assert audit_answer_application(before, after, report) == ()
    assert after < before


def test_repo_answer_records_close_only_targeted_questions():
    records = load_answer_records(ANSWERS_ROOT)
    cells = current_program_cells()
    before = observe_mechanics_program(cells).open_question_count
    updated, report = apply_answer_records(cells, records)
    after = observe_mechanics_program(updated).open_question_count
    targeted = {(record.mechanic_id, record.dimension) for record in records}
    assert before - after == len(targeted)
    assert report.waiver_record_ids == ()
