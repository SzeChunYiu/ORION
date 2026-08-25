"""The boundary that makes this package scaffolding rather than a closure path.

These tests are the reason the package is safe to merge while #210 is blocked:
they assert, mechanically, that nothing here grants authority, emits the Phase-4
terminal marker, or writes to a protected surface.
"""

from __future__ import annotations

import inspect
import pkgutil
from importlib import import_module

import orion.programme as programme
from orion.programme.catalogue import ALL_CHECKS
from orion.programme.identity import verify_seal
from orion.programme.protocol import (
    BLOCKING_DEPENDENCIES,
    CONSTITUTIONAL_INVARIANTS,
    PROGRAMME_STATUS,
    REFUSED_TERMINAL_MARKER,
    TERMINAL_MARKER_WITHHELD,
    assess_programme_readiness,
    build_protocol_document,
)

_PACKAGE_MODULES = tuple(
    sorted(
        f"orion.programme.{info.name}"
        for info in pkgutil.iter_modules(programme.__path__)
    )
)


def test_readiness_never_grants_closure_or_authority() -> None:
    report = assess_programme_readiness(hostile_report_blocked=False)
    assert report.grants_phase4_closure is False
    assert report.grants_self_sustaining_authority is False
    assert report.terminal_marker == TERMINAL_MARKER_WITHHELD


def test_dependency_blockers_are_unconditional() -> None:
    report = assess_programme_readiness(hostile_report_blocked=False)
    for dependency in BLOCKING_DEPENDENCIES:
        assert f"blocked on {dependency}" in report.blockers
    assert "no protected Phase-4 longitudinal evidence exists" in report.blockers


def test_forgetting_to_run_the_battery_yields_the_blocked_answer() -> None:
    assert assess_programme_readiness().hostile_report_blocked is True


def test_no_callable_in_the_package_returns_the_terminal_marker() -> None:
    """Call every zero-argument callable and assert none emits the marker."""

    emitted: list[str] = []
    for module_name in _PACKAGE_MODULES:
        module = import_module(module_name)
        for name, member in vars(module).items():
            if name.startswith("_") or not callable(member):
                continue
            if not inspect.isfunction(member):
                continue
            signature = inspect.signature(member)
            if any(
                parameter.default is inspect.Parameter.empty
                and parameter.kind
                in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD)
                for parameter in signature.parameters.values()
            ):
                continue
            try:
                result = member()
            except (Exception, SystemExit):  # argparse refusal emits nothing
                continue
            if REFUSED_TERMINAL_MARKER in repr(result):
                emitted.append(f"{module_name}.{name}")
    assert emitted == []


def test_the_marker_appears_only_as_a_refused_constant() -> None:
    holders = [
        f"{module_name}.{name}"
        for module_name in _PACKAGE_MODULES
        for name, value in vars(import_module(module_name)).items()
        if isinstance(value, str) and value == REFUSED_TERMINAL_MARKER
    ]
    assert holders == ["orion.programme.protocol.REFUSED_TERMINAL_MARKER"]


def test_protocol_document_is_sealed_and_declares_its_own_inertness() -> None:
    document = build_protocol_document()
    assert verify_seal(document) == ()
    assert document["programme_status"] == PROGRAMME_STATUS == "PRE_REGISTRATION_SCAFFOLDING"
    assert document["authority_granted"] is False
    assert document["gates_closed"] == []
    assert document["activated_code_paths"] == []
    assert document["cycles_executed"] == 0
    assert document["evidence_status"] == "NO_PROTECTED_EVIDENCE"
    assert document["terminal_marker_state"] == TERMINAL_MARKER_WITHHELD
    assert document["blocking_dependencies"] == list(BLOCKING_DEPENDENCIES)


def test_protocol_document_is_stable_across_calls() -> None:
    assert build_protocol_document() == build_protocol_document()


def test_every_invariant_names_what_enforces_it() -> None:
    assert len(CONSTITUTIONAL_INVARIANTS) == 5
    for invariant in CONSTITUTIONAL_INVARIANTS:
        assert invariant.invariant_id.startswith("P4-INV-")
        assert invariant.statement.strip()
        assert invariant.enforced_by


def test_protocol_document_lists_the_whole_battery() -> None:
    document = build_protocol_document()
    listed = {entry["check_id"] for entry in document["anti_collapse_checks"]}
    assert listed == {check.check_id for check in ALL_CHECKS}


def test_package_declares_no_populated_programme_state() -> None:
    """No module-level ProgrammeState: a receipt for a cycle that did not run."""

    from orion.programme.programme_state import EpochSnapshot, ProgrammeState

    populated = [
        f"{module_name}.{name}"
        for module_name in _PACKAGE_MODULES
        for name, value in vars(import_module(module_name)).items()
        if isinstance(value, (ProgrammeState, EpochSnapshot))
    ]
    assert populated == []
