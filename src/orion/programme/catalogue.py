"""The Phase-4 anti-collapse battery.

Assembled here rather than in ``orion.kernel.checks``: that package is discovered
by ``pkgutil`` in ``orion.kernel.registry`` and adding a module to it is a
shared-registry edit in effect. Registration is queued as a follow-up for the
lane that owns that wave.

The battery mirrors the registry's discipline anyway — globally unique ids, and
every check naming the negative fixture that shows it rejecting something.
:func:`validate_catalogue` enforces both, so a check added without a fixture
fails at import-time in the tests rather than passing quietly forever.
"""

from __future__ import annotations

from orion.programme.checks_diversity import DIVERSITY_CHECKS
from orion.programme.checks_evidence import EVIDENCE_CHECKS
from orion.programme.hostile import HostileCheck, HostileCheckReport, run_hostile_checks
from orion.programme.programme_state import ProgrammeState

ALL_CHECKS: tuple[HostileCheck, ...] = (*EVIDENCE_CHECKS, *DIVERSITY_CHECKS)

ALL_CHECK_IDS: tuple[str, ...] = tuple(check.check_id for check in ALL_CHECKS)


def validate_catalogue(checks: tuple[HostileCheck, ...] = ALL_CHECKS) -> tuple[str, ...]:
    """Return deduplicated defects in the battery itself."""

    errors: list[str] = []
    seen: set[str] = set()
    fixtures: set[str] = set()
    for check in checks:
        if check.check_id in seen:
            errors.append(f"duplicate check id '{check.check_id}'")
        seen.add(check.check_id)
        if check.negative_fixture_id in fixtures:
            errors.append(
                f"check '{check.check_id}' reuses negative fixture"
                f" '{check.negative_fixture_id}'; a shared fixture does not show"
                " this check failing"
            )
        fixtures.add(check.negative_fixture_id)
        if not check.check_id.startswith("HC-"):
            errors.append(f"check id '{check.check_id}' does not use the HC- prefix")
    return tuple(dict.fromkeys(errors))


def run_anti_collapse_battery(state: ProgrammeState) -> HostileCheckReport:
    """Run the full battery. The report blocks unless every check passes."""

    return run_hostile_checks(state, ALL_CHECKS)


__all__ = [
    "ALL_CHECKS",
    "ALL_CHECK_IDS",
    "run_anti_collapse_battery",
    "validate_catalogue",
]
