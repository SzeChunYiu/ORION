"""Anti-collapse check framework. Fails closed by construction.

Three properties are load-bearing:

1. **Three outcomes.** ``PASS`` / ``FAIL`` / ``CANNOT_CHECK``. A check that
   cannot evaluate its own precondition returns ``CANNOT_CHECK``, never ``PASS``.
2. **CANNOT_CHECK blocks.** At report level it is indistinguishable from
   ``FAIL``. "Could not check" is not "checked and fine".
3. **An empty report blocks.** A report with no results is blocked, so failing
   to run the battery cannot be mistaken for passing it.

Each check declares ``negative_fixture_id``: the test that shows this check
demonstrably rejecting something. This mirrors the discipline
``orion.kernel.registry`` enforces on discriminating checks — a check that has
never exhibited a failing case of its own is not demonstrably failable. These
checks are deliberately **not** registered into ``orion.kernel.checks``: that
package is auto-discovered, and adding to it is a shared-registry edit.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from orion.programme.identity import HOSTILE_CHECK_REPORT_SCHEMA, seal
from orion.programme.programme_state import ProgrammeState
from orion.programme.records import Outcome


@dataclass(frozen=True)
class CheckResult:
    """Outcome of one check, with the reason it reached that outcome."""

    check_id: str
    outcome: Outcome
    reason: str
    findings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("a check result must state its reason")

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks


@dataclass(frozen=True)
class HostileCheck:
    """One anti-collapse check.

    ``failure_class`` names the collapse mode, so a firing check joins directly
    onto method-layer negative history.
    """

    check_id: str
    title: str
    failure_class: str
    negative_fixture_id: str
    evaluate: Callable[[ProgrammeState], CheckResult]

    def __post_init__(self) -> None:
        for name in ("check_id", "title", "failure_class", "negative_fixture_id"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"hostile check {name} is required")

    def run(self, state: ProgrammeState) -> CheckResult:
        """Run the check. Any exception is an inability to check, not a pass."""

        try:
            result = self.evaluate(state)
        except Exception as error:  # noqa: BLE001 - an unevaluable check must block
            return CheckResult(
                check_id=self.check_id,
                outcome=Outcome.CANNOT_CHECK,
                reason=f"check raised {type(error).__name__}: {error}",
            )
        if result.check_id != self.check_id:
            return CheckResult(
                check_id=self.check_id,
                outcome=Outcome.CANNOT_CHECK,
                reason="check returned a result for a different check id",
            )
        return result


@dataclass(frozen=True)
class HostileCheckReport:
    """Aggregate verdict. Blocking is the default; passing is the exception."""

    results: tuple[CheckResult, ...]
    expected_check_ids: tuple[str, ...] = ()

    @property
    def blocking_check_ids(self) -> tuple[str, ...]:
        return tuple(result.check_id for result in self.results if result.blocks)

    @property
    def missing_check_ids(self) -> tuple[str, ...]:
        present = {result.check_id for result in self.results}
        return tuple(item for item in self.expected_check_ids if item not in present)

    @property
    def blocked(self) -> bool:
        """True unless every expected check ran and every result passed."""

        if not self.results:
            return True
        return bool(self.blocking_check_ids) or bool(self.missing_check_ids)

    @property
    def grants_phase4_closure(self) -> bool:
        """Always ``False``.

        A clean anti-collapse battery is a precondition for closure, never a
        grant of it. Closure authority sits with the external host, and this
        property exists so that no caller can mistake a green report for it.
        """

        return False

    def to_payload(self) -> dict[str, Any]:
        return seal(
            {
                "schema_version": HOSTILE_CHECK_REPORT_SCHEMA,
                "blocked": self.blocked,
                "grants_phase4_closure": False,
                "expected_check_ids": list(self.expected_check_ids),
                "missing_check_ids": list(self.missing_check_ids),
                "results": [
                    {
                        "check_id": result.check_id,
                        "outcome": result.outcome.value,
                        "reason": result.reason,
                        "findings": list(result.findings),
                    }
                    for result in self.results
                ],
            }
        )


def run_hostile_checks(
    state: ProgrammeState,
    checks: Sequence[HostileCheck],
) -> HostileCheckReport:
    """Run every check. The report is blocked unless all of them pass."""

    results = tuple(check.run(state) for check in checks)
    return HostileCheckReport(
        results=results,
        expected_check_ids=tuple(check.check_id for check in checks),
    )


def passed(check_id: str, reason: str) -> CheckResult:
    return CheckResult(check_id=check_id, outcome=Outcome.PASS, reason=reason)


def failed(check_id: str, reason: str, findings: tuple[str, ...] = ()) -> CheckResult:
    return CheckResult(
        check_id=check_id, outcome=Outcome.FAIL, reason=reason, findings=findings
    )


def cannot_check(check_id: str, reason: str) -> CheckResult:
    return CheckResult(check_id=check_id, outcome=Outcome.CANNOT_CHECK, reason=reason)


__all__ = [
    "CheckResult",
    "HostileCheck",
    "HostileCheckReport",
    "cannot_check",
    "failed",
    "passed",
    "run_hostile_checks",
]
