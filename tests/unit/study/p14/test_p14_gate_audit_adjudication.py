"""The audit must say the question was answered, and must not let that clear it.

P14A's seven gates all read `FAIL` and none of them is going to move: two no
admissible world reaches, five every admissible world satisfies. Read alone that
says a paper failed, which is not what happened -- the question was answered at
P14A's own unedited thresholds on P14C's benchmark, and a reader of the audit had
no way to know. An audit reporting only the half that blocks is the same shape as
one reporting only the half that passes.

So the adjudication is reported, and reported is all it is. P14A's verdict is
retained and still blocks: a successor re-asks the question, it does not repair
the frozen protocol.
"""

from __future__ import annotations

import json
from pathlib import Path

from orion.programme.records import Outcome
from orion.study.p14 import gate_audit

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_the_audit_carries_the_adjudication() -> None:
    status = gate_audit.adjudication_status(REPO_ROOT)
    assert status["present"] is True
    assert status["terminal"].startswith("P14A_SUPERIORITY_GATES_UNMEASURABLE")
    assert status["p14a_gates_unattainable"] is True
    assert status["p14a_terminal_had_one_reachable_value"] is True
    assert status["p14c_terminal_had_two_reachable_values"] is True
    assert status["answers_the_unmeasurable_gates"] is True
    assert status["edits_no_frozen_result"] is True


def test_the_adjudication_does_not_clear_the_audit() -> None:
    """The load-bearing half. A successor must never turn a frozen FAIL green."""

    report = gate_audit.audit_p14a_governance_terminal()
    assert report["adjudication"]["present"] is True
    assert report["outcome"] is Outcome.FAIL
    assert report["outcome"].blocks


def test_the_reported_thresholds_are_read_from_the_receipt_not_restated() -> None:
    """A summary that drifts from its source is worse than no summary."""

    committed = json.loads(
        (REPO_ROOT / gate_audit.ADJUDICATION).read_text(encoding="utf-8")
    )
    status = gate_audit.adjudication_status(REPO_ROOT)
    assert status["terminal"] == committed["terminal"]
    assert (
        status["p14a_thresholds_met_on_p14c"]
        == committed["inherited_p14a_thresholds_on_p14c"]["met"]
    )


def test_a_missing_adjudication_is_said_rather_than_assumed(tmp_path: Path) -> None:
    """Absence must read as absence, not as an unanswered question quietly dropped."""

    status = gate_audit.adjudication_status(tmp_path)
    assert status["present"] is False
    assert "nothing on record says the question was answered" in status["detail"]


def test_the_rendered_report_states_both_halves() -> None:
    report = gate_audit.audit_p14a_governance_terminal()
    rendered = gate_audit._render(report)
    assert "does not roll up" in rendered
    assert "still blocks" in rendered
    assert "outcome: FAIL" in rendered
