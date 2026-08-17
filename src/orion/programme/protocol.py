"""Versioned Phase-4 programme protocol — pre-registration, not activation.

This module emits a machine-readable protocol document: the constitutional
invariants, the three knowledge-layer schema ids, the dependency/reopening
model, and the anti-collapse battery that a Phase-4 programme would have to
satisfy. It emits nothing else. There is no programme loop here, no cycle
runner, no receipt for work that has not happened, and no path by which any
function in this package returns the terminal marker.

Issue #210 is blocked on #209, which is blocked on #76. The document records
that fact in a field rather than a comment, so a consumer that reads only the
machine-readable form still sees it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orion.programme.catalogue import ALL_CHECKS
from orion.programme.identity import (
    DEPENDENCY_EDGE_SCHEMA,
    METHOD_KNOWLEDGE_SCHEMA,
    OBJECT_KNOWLEDGE_SCHEMA,
    PROTOCOL_SCHEMA,
    REOPEN_EVENT_SCHEMA,
    REOPEN_LEDGER_SCHEMA,
    SEARCH_UNIVERSE_KNOWLEDGE_SCHEMA,
    seal,
)

PROTOCOL_VERSION = "phase4-programme-protocol.v1"
PROGRAMME_STATUS = "PRE_REGISTRATION_SCAFFOLDING"

#: The Phase-4 terminal marker, present here only so a guard can refuse it.
#: No function in ``orion.programme`` returns this string; a test enforces that.
REFUSED_TERMINAL_MARKER = "PHASE_4_SELF_SUSTAINING_RESEARCH_PROGRAM_CLOSED"

TERMINAL_MARKER_WITHHELD = "PHASE_4_TERMINAL_MARKER_WITHHELD"

BLOCKING_DEPENDENCIES = ("#209", "#76")


@dataclass(frozen=True)
class Invariant:
    """One constitutional boundary, and the module that makes it fail closed."""

    invariant_id: str
    statement: str
    enforced_by: tuple[str, ...]


CONSTITUTIONAL_INVARIANTS: tuple[Invariant, ...] = (
    Invariant(
        invariant_id="P4-INV-1-PROTECTED-SURFACE-IMMUTABLE",
        statement=(
            "Candidate and LLM processes cannot mutate protected evaluators,"
            " held-outs, authority policy, phase rules, or programme termination"
            " criteria. This package contains no writer for any of them."
        ),
        enforced_by=(
            "orion.programme.protocol.assess_programme_readiness",
            "orion.programme.checks_evidence.HC-EVALUATOR-GAMING",
        ),
    ),
    Invariant(
        invariant_id="P4-INV-2-ABSENCE-IS-NOT-PASS",
        statement=(
            "Missing evidence remains OPEN or CANNOT_CHECK. No amount of"
            " programme pressure converts absence into a positive conclusion."
        ),
        enforced_by=(
            "orion.programme.records.Outcome",
            "orion.programme.hostile.HostileCheckReport.blocked",
            "orion.programme.checks_evidence.HC-INSUFFICIENT-PROTECTED-EVIDENCE",
        ),
    ),
    Invariant(
        invariant_id="P4-INV-3-NEGATIVE-HISTORY-IMMUTABLE",
        statement=(
            "Null, harmful and rejected directions remain immutable negative"
            " history. Supersession adds a successor; it never removes a record."
        ),
        enforced_by=(
            "orion.programme.dependency.validate_reopen_event",
            "orion.programme.checks_evidence.HC-HIDDEN-DELETION",
            "orion.study.p5.negative_history_chain (upstream chain this binds to)",
        ),
    ),
    Invariant(
        invariant_id="P4-INV-4-STATE-CHANGES-ARE-REPLAYABLE",
        statement=(
            "Every programme-level state change is content, lineage and version"
            " bound, and any prior state can be reconstructed after any reopening."
        ),
        enforced_by=(
            "orion.programme.identity.seal",
            "orion.programme.dependency.build_reopen_ledger",
            "orion.programme.dependency.verify_reopen_ledger",
        ),
    ),
    Invariant(
        invariant_id="P4-INV-5-NO-SELF-GRANTED-AUTHORITY",
        statement=(
            "Nothing in this package grants Phase-4 closure or self-sustaining"
            " authority. External authority to halt, audit, reopen and revert is"
            " unaffected by any result computed here."
        ),
        enforced_by=(
            "orion.programme.hostile.HostileCheckReport.grants_phase4_closure",
            "orion.programme.protocol.ProgrammeReadinessReport",
        ),
    ),
)


@dataclass(frozen=True)
class ProgrammeReadinessReport:
    """What the scaffolding can say, and what it structurally cannot.

    Both grant properties are constants, following the ``phase2_terminal``
    convention: a report that could compute its own authority under some
    condition is a report that can be argued into granting it.
    """

    blockers: tuple[str, ...]
    hostile_report_blocked: bool

    @property
    def grants_phase4_closure(self) -> bool:
        return False

    @property
    def grants_self_sustaining_authority(self) -> bool:
        return False

    @property
    def terminal_marker(self) -> str:
        """Always the withheld sentinel — never :data:`REFUSED_TERMINAL_MARKER`."""

        return TERMINAL_MARKER_WITHHELD


def assess_programme_readiness(
    hostile_report_blocked: bool = True,
    extra_blockers: tuple[str, ...] = (),
) -> ProgrammeReadinessReport:
    """Report Phase-4 readiness. The dependency blockers are unconditional.

    ``hostile_report_blocked`` defaults to ``True`` so that a caller who forgets
    to run the battery gets the blocked answer rather than the clean one.
    """

    blockers = [f"blocked on {item}" for item in BLOCKING_DEPENDENCIES]
    blockers.append("no protected Phase-4 longitudinal evidence exists")
    if hostile_report_blocked:
        blockers.append("anti-collapse battery is blocked or was not run")
    blockers.extend(extra_blockers)
    return ProgrammeReadinessReport(
        blockers=tuple(dict.fromkeys(blockers)),
        hostile_report_blocked=hostile_report_blocked,
    )


def build_protocol_document() -> dict[str, Any]:
    """Return the sealed, machine-readable Phase-4 programme protocol."""

    return seal(
        {
            "schema_version": PROTOCOL_SCHEMA,
            "protocol_version": PROTOCOL_VERSION,
            "programme_status": PROGRAMME_STATUS,
            "issue": "#210",
            "blocking_dependencies": list(BLOCKING_DEPENDENCIES),
            "authority_granted": False,
            "gates_closed": [],
            "activated_code_paths": [],
            "cycles_executed": 0,
            "evidence_status": "NO_PROTECTED_EVIDENCE",
            "terminal_marker_state": TERMINAL_MARKER_WITHHELD,
            "knowledge_layer_schemas": {
                "object": OBJECT_KNOWLEDGE_SCHEMA,
                "search_universe": SEARCH_UNIVERSE_KNOWLEDGE_SCHEMA,
                "method": METHOD_KNOWLEDGE_SCHEMA,
            },
            "dependency_model_schemas": {
                "edge": DEPENDENCY_EDGE_SCHEMA,
                "reopen_event": REOPEN_EVENT_SCHEMA,
                "reopen_ledger": REOPEN_LEDGER_SCHEMA,
            },
            "constitutional_invariants": [
                {
                    "invariant_id": item.invariant_id,
                    "statement": item.statement,
                    "enforced_by": list(item.enforced_by),
                }
                for item in CONSTITUTIONAL_INVARIANTS
            ],
            "anti_collapse_checks": [
                {
                    "check_id": check.check_id,
                    "title": check.title,
                    "failure_class": check.failure_class,
                    "negative_fixture_id": check.negative_fixture_id,
                }
                for check in ALL_CHECKS
            ],
        }
    )


__all__ = [
    "BLOCKING_DEPENDENCIES",
    "CONSTITUTIONAL_INVARIANTS",
    "PROGRAMME_STATUS",
    "PROTOCOL_VERSION",
    "REFUSED_TERMINAL_MARKER",
    "TERMINAL_MARKER_WITHHELD",
    "Invariant",
    "ProgrammeReadinessReport",
    "assess_programme_readiness",
    "build_protocol_document",
]
