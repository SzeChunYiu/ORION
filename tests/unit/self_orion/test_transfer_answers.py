from __future__ import annotations

from pathlib import Path

import pytest

from orion.kernel import AnswerAuthority, grade_and_apply
from orion.kernel.registry import load_registered_checks
from orion.mechanics.program import current_program_cells, observe_mechanics_program
from orion.self_orion.transfer_answers import TRANSFER_LANE, transfer_answer_records

RAKL_ROOT = Path(__file__).resolve().parents[3].parent / "RAKL"
_HAS_RAKL = (RAKL_ROOT / ".git").exists()
_needs_rakl = pytest.mark.skipif(
    not _HAS_RAKL, reason="RAKL provenance root not present in this environment"
)


def _roots() -> dict[str, Path]:
    return {"orion": Path.cwd(), "rakl": RAKL_ROOT}


@_needs_rakl
def test_the_transfer_becomes_evidence_bound_answer_records() -> None:
    report = transfer_answer_records(current_program_cells(), evidence_roots=_roots())

    assert report.records
    assert all(item.lane == TRANSFER_LANE for item in report.records)
    assert all(item.evidence_refs for item in report.records)
    assert all(
        set(dict(item.evidence_bindings)) == set(item.evidence_refs)
        for item in report.records
    )


@_needs_rakl
def test_the_lane_records_who_authored_the_answer_not_who_routed_it() -> None:
    """Relabelling another lane's work as one's own would defeat the very
    independence the gate checks. The lane is provenance, not convenience."""

    report = transfer_answer_records(current_program_cells(), evidence_roots=_roots())
    assert TRANSFER_LANE == "self-orion"
    assert not any(item.lane == "claude" for item in report.records)


@_needs_rakl
def test_unresolvable_provenance_is_counted_not_dropped() -> None:
    """Paths absent at the pinned commit are refused, and say so."""

    report = transfer_answer_records(current_program_cells(), evidence_roots=_roots())
    reasons = dict(report.skipped)
    assert any(key.startswith("evidence:") for key in reasons)
    assert any(key.startswith("structured_payload_required:") for key in reasons)


@_needs_rakl
def test_an_absent_provenance_root_yields_no_records_rather_than_unbound_ones() -> None:
    report = transfer_answer_records(
        current_program_cells(), evidence_roots={"orion": Path.cwd()}
    )
    assert report.records == ()
    assert dict(report.skipped).get("no_resolvable_evidence")


@_needs_rakl
def test_independently_laned_checks_close_questions_and_reject_most() -> None:
    """The first closures ORION has made, and the rejection rate that makes
    them meaningful.

    Answers authored by the self-orion lane, bound to RAKL sources at a pinned
    commit, judged by claude-lane checks frozen before the round and required to
    reject the host adversarial battery. A gate that passed everything would
    prove nothing; most of what is judged is refused.
    """

    cells = current_program_cells()
    before = observe_mechanics_program(cells).open_question_count
    report = transfer_answer_records(cells, evidence_roots=_roots())
    result = grade_and_apply(
        cells,
        report.records,
        evidence_roots=_roots(),
        checks=dict(load_registered_checks()),
        round_index=1,
    )
    after = observe_mechanics_program(result.cells).open_question_count

    verified = [
        item for item in result.gradings if item.authority is AnswerAuthority.VERIFIED
    ]
    judged = [item for item in result.gradings if item.check_outcome is not None]
    failed = [item for item in judged if item.check_outcome.value == "FAILED"]

    assert verified, "no answer reached verified authority"
    assert before - after == len(verified)
    assert len(failed) > len(verified), "a gate that mostly passes is not discriminating"
