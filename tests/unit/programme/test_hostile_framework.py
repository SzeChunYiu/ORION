"""The framework must fail closed before any individual check is even correct."""

from __future__ import annotations

import pytest

from orion.programme.catalogue import ALL_CHECKS, validate_catalogue
from orion.programme.hostile import (
    CheckResult,
    HostileCheck,
    HostileCheckReport,
    cannot_check,
    failed,
    passed,
    run_hostile_checks,
)
from orion.programme.identity import verify_seal
from orion.programme.programme_state import ProgrammeState
from orion.programme.records import Outcome

EMPTY = ProgrammeState(programme_id="empty")


def _check(check_id: str, result_factory) -> HostileCheck:
    return HostileCheck(
        check_id=check_id,
        title=check_id,
        failure_class=check_id,
        negative_fixture_id=f"fixture_{check_id}",
        evaluate=lambda state: result_factory(check_id),
    )


def test_cannot_check_blocks_exactly_as_failure_does() -> None:
    assert Outcome.CANNOT_CHECK.blocks is True
    assert Outcome.FAIL.blocks is True
    assert Outcome.PASS.blocks is False


def test_an_empty_report_blocks() -> None:
    """Not running the battery must never look like passing it."""

    assert HostileCheckReport(results=()).blocked is True


def test_a_report_missing_an_expected_check_blocks() -> None:
    report = HostileCheckReport(
        results=(passed("HC-A", "fine"),),
        expected_check_ids=("HC-A", "HC-B"),
    )
    assert report.missing_check_ids == ("HC-B",)
    assert report.blocked is True


def test_a_complete_passing_report_does_not_block() -> None:
    report = run_hostile_checks(
        EMPTY,
        (_check("HC-A", lambda cid: passed(cid, "fine")),),
    )
    assert report.blocked is False


def test_a_raising_check_becomes_cannot_check_not_pass() -> None:
    def explode(_: str) -> CheckResult:
        raise RuntimeError("evidence store unreachable")

    report = run_hostile_checks(EMPTY, (_check("HC-BOOM", explode),))
    assert report.results[0].outcome is Outcome.CANNOT_CHECK
    assert "RuntimeError" in report.results[0].reason
    assert report.blocked is True


def test_a_check_returning_someone_elses_result_is_not_trusted() -> None:
    check = _check("HC-A", lambda _cid: passed("HC-OTHER", "fine"))
    report = run_hostile_checks(EMPTY, (check,))
    assert report.results[0].outcome is Outcome.CANNOT_CHECK


def test_a_result_must_state_its_reason() -> None:
    with pytest.raises(ValueError):
        CheckResult(check_id="HC-A", outcome=Outcome.PASS, reason="  ")


def test_report_payload_is_sealed_and_never_grants_closure() -> None:
    report = run_hostile_checks(EMPTY, (_check("HC-A", lambda cid: passed(cid, "fine")),))
    payload = report.to_payload()
    assert verify_seal(payload) == ()
    assert payload["grants_phase4_closure"] is False
    assert report.grants_phase4_closure is False


def test_failed_results_carry_findings() -> None:
    result = failed("HC-A", "collapse", ("detail",))
    assert result.findings == ("detail",)
    assert result.blocks is True


def test_every_check_in_the_battery_declares_its_own_negative_fixture() -> None:
    assert validate_catalogue() == ()
    fixtures = {check.negative_fixture_id for check in ALL_CHECKS}
    assert len(fixtures) == len(ALL_CHECKS)


def test_the_battery_cannot_check_an_empty_programme() -> None:
    """Absence of evidence is reported as absence, never as a clean bill."""

    report = run_hostile_checks(EMPTY, ALL_CHECKS)
    assert {result.outcome for result in report.results} == {Outcome.CANNOT_CHECK}
    assert report.blocked is True


def test_cannot_check_helper_produces_a_blocking_result() -> None:
    assert cannot_check("HC-A", "no data").blocks is True
