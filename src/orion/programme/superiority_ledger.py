"""The P1-P10 superiority ledger: what evidence is on record against each terminal.

The ledger is the observation surface. It holds no judgement of its own --- every
verdict comes from :func:`orion.programme.superiority.adjudicate` or from the
battery in ``orion.programme.checks_superiority`` --- and it is deliberately
separate from the gate registry so that the terminals can be frozen once while
the evidence against them moves.

Serialization is here rather than in a script because a ledger that can only be
written by hand drifts from the registry the moment a gate is added.
:func:`ledger_from_payload` refuses a payload it cannot bind: an unknown gate id,
an unknown paper, a gate list that disagrees with
``orion.programme.superiority_terminals``. Refusing is the point --- a ledger
that silently dropped the evidence it could not parse would report a cleaner
programme than the one that exists.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from orion.programme.superiority import (
    SUPERIORITY_LEDGER_SCHEMA,
    Actionability,
    ClaimScope,
    EvidenceGrade,
    GateBlocker,
    GateEvidence,
    PaperSuperiorityRecord,
    PaperTerminalStatus,
    PredecessorArtifact,
    ResponsibilityClass,
)
from orion.programme.superiority_terminals import PAPER_GATES, PAPER_ISSUES


class LedgerBindingError(ValueError):
    """A payload could not be bound to the frozen registry."""


@dataclass(frozen=True)
class SuperiorityLedger:
    """Every paper's terminals and the evidence recorded against them."""

    ledger_id: str
    frozen_at: str
    papers: tuple[PaperSuperiorityRecord, ...]

    def __post_init__(self) -> None:
        for name in ("ledger_id", "frozen_at"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"superiority ledger {name} is required")
        seen: set[str] = set()
        for paper in self.papers:
            if paper.paper_id in seen:
                raise ValueError(f"superiority ledger repeats paper {paper.paper_id}")
            seen.add(paper.paper_id)

    @property
    def paper_ids(self) -> tuple[str, ...]:
        return tuple(paper.paper_id for paper in self.papers)

    @property
    def missing_paper_ids(self) -> tuple[str, ...]:
        """Registered papers this ledger says nothing about."""

        present = set(self.paper_ids)
        return tuple(paper_id for paper_id in PAPER_GATES if paper_id not in present)

    def paper(self, paper_id: str) -> PaperSuperiorityRecord | None:
        for record in self.papers:
            if record.paper_id == paper_id:
                return record
        return None

    def terminals(self) -> dict[str, PaperTerminalStatus]:
        return {paper.paper_id: paper.terminal() for paper in self.papers}


def _require_mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise LedgerBindingError(f"{label} must be a mapping")
    return value


def _optional_bool(value: object, label: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise LedgerBindingError(f"{label} must be a boolean or absent")
    return value


def _string_tuple(value: object, label: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise LedgerBindingError(f"{label} must be a list of strings")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise LedgerBindingError(f"{label} must contain only non-blank strings")
    return tuple(value)


def _evidence_from_payload(payload: Mapping[str, Any], known_gate_ids: set[str]) -> GateEvidence:
    gate_id = payload.get("gate_id")
    if not isinstance(gate_id, str) or gate_id not in known_gate_ids:
        raise LedgerBindingError(f"evidence names unknown gate id {gate_id!r}")

    raw_grade = payload.get("grade")
    try:
        grade = EvidenceGrade(raw_grade)
    except ValueError as error:
        raise LedgerBindingError(f"gate {gate_id} has unknown grade {raw_grade!r}") from error

    raw_scope = payload.get("declared_scope")
    if raw_scope is None:
        declared_scope = None
    else:
        try:
            declared_scope = ClaimScope(raw_scope)
        except ValueError as error:
            raise LedgerBindingError(
                f"gate {gate_id} has unknown declared_scope {raw_scope!r}"
            ) from error

    try:
        return GateEvidence(
            gate_id=gate_id,
            grade=grade,
            artifact_refs=_string_tuple(payload.get("artifact_refs"), f"{gate_id}.artifact_refs"),
            protocol_frozen_before_outcome=_optional_bool(
                payload.get("protocol_frozen_before_outcome"),
                f"{gate_id}.protocol_frozen_before_outcome",
            ),
            comparator_donor_complete=_optional_bool(
                payload.get("comparator_donor_complete"), f"{gate_id}.comparator_donor_complete"
            ),
            evaluator_custody=payload.get("evaluator_custody"),
            domains=_string_tuple(payload.get("domains"), f"{gate_id}.domains"),
            independent_implementation=_optional_bool(
                payload.get("independent_implementation"),
                f"{gate_id}.independent_implementation",
            ),
            harm_guard_gate_ids=_string_tuple(
                payload.get("harm_guard_gate_ids"), f"{gate_id}.harm_guard_gate_ids"
            ),
            declared_scope=declared_scope,
            notes=payload.get("notes", "") or "",
        )
    except ValueError as error:  # GateEvidence rejects its own malformed input
        raise LedgerBindingError(str(error)) from error


def ledger_from_payload(payload: Mapping[str, Any]) -> SuperiorityLedger:
    """Bind a JSON payload to the frozen registry, or refuse it."""

    payload = _require_mapping(payload, "ledger payload")

    schema = payload.get("schema_version")
    if schema != SUPERIORITY_LEDGER_SCHEMA:
        raise LedgerBindingError(
            f"ledger schema_version must be {SUPERIORITY_LEDGER_SCHEMA}, got {schema!r}"
        )

    raw_papers = payload.get("papers")
    if not isinstance(raw_papers, Sequence) or isinstance(raw_papers, (str, bytes)):
        raise LedgerBindingError("ledger papers must be a list")

    records: list[PaperSuperiorityRecord] = []
    for entry in raw_papers:
        entry = _require_mapping(entry, "ledger paper entry")
        paper_id = entry.get("paper_id")
        if paper_id not in PAPER_GATES:
            raise LedgerBindingError(f"ledger names unregistered paper {paper_id!r}")

        gates = PAPER_GATES[paper_id]
        known_gate_ids = {gate.gate_id for gate in gates}

        raw_evidence = entry.get("evidence")
        if raw_evidence is None:
            raw_evidence = []
        if not isinstance(raw_evidence, Sequence) or isinstance(raw_evidence, (str, bytes)):
            raise LedgerBindingError(f"paper {paper_id} evidence must be a list")

        evidence = tuple(
            _evidence_from_payload(_require_mapping(item, f"{paper_id} evidence entry"),
                                   known_gate_ids)
            for item in raw_evidence
        )
        seen_gate_ids: set[str] = set()
        for item in evidence:
            if item.gate_id in seen_gate_ids:
                raise LedgerBindingError(
                    f"paper {paper_id} records two pieces of evidence for {item.gate_id}"
                )
            seen_gate_ids.add(item.gate_id)

        raw_predecessors = entry.get("predecessor_artifacts")
        if raw_predecessors is None:
            raw_predecessors = []
        if not isinstance(raw_predecessors, Sequence) or isinstance(
            raw_predecessors, (str, bytes)
        ):
            raise LedgerBindingError(f"paper {paper_id} predecessor_artifacts must be a list")
        predecessors: list[PredecessorArtifact] = []
        for item in raw_predecessors:
            item = _require_mapping(item, f"{paper_id} predecessor entry")
            raw_pred_grade = item.get("grade")
            try:
                pred_grade = EvidenceGrade(raw_pred_grade)
            except ValueError as error:
                raise LedgerBindingError(
                    f"paper {paper_id} predecessor has unknown grade {raw_pred_grade!r}"
                ) from error
            try:
                predecessors.append(
                    PredecessorArtifact(
                        artifact_ref=item.get("artifact_ref", ""),
                        grade=pred_grade,
                        terminal=item.get("terminal", "") or "",
                        note=item.get("note", "") or "",
                    )
                )
            except ValueError as error:
                raise LedgerBindingError(str(error)) from error

        raw_blockers = entry.get("blockers")
        if raw_blockers is None:
            raw_blockers = []
        if not isinstance(raw_blockers, Sequence) or isinstance(raw_blockers, (str, bytes)):
            raise LedgerBindingError(f"paper {paper_id} blockers must be a list")
        blockers: list[GateBlocker] = []
        seen_blocker_ids: set[str] = set()
        for item in raw_blockers:
            item = _require_mapping(item, f"{paper_id} blocker entry")
            blocker_gate_id = item.get("gate_id")
            if not isinstance(blocker_gate_id, str) or blocker_gate_id not in known_gate_ids:
                raise LedgerBindingError(
                    f"blocker names unknown gate id {blocker_gate_id!r}"
                )
            if blocker_gate_id in seen_blocker_ids:
                raise LedgerBindingError(
                    f"paper {paper_id} records two blockers for {blocker_gate_id}"
                )
            seen_blocker_ids.add(blocker_gate_id)
            try:
                responsibility = ResponsibilityClass(item.get("responsibility"))
                actionability = Actionability(item.get("actionability"))
            except ValueError as error:
                raise LedgerBindingError(
                    f"blocker {blocker_gate_id} has an unknown responsibility "
                    f"or actionability: {error}"
                ) from error
            try:
                blockers.append(
                    GateBlocker(
                        gate_id=blocker_gate_id,
                        responsibility=responsibility,
                        actionability=actionability,
                        statement=item.get("statement", ""),
                        unblock=item.get("unblock", ""),
                        refs=_string_tuple(item.get("refs"), f"{blocker_gate_id}.refs"),
                    )
                )
            except ValueError as error:
                raise LedgerBindingError(str(error)) from error

        raw_scope = entry.get("declared_claim_scope")
        if raw_scope is None:
            declared_claim_scope = None
        else:
            try:
                declared_claim_scope = ClaimScope(raw_scope)
            except ValueError as error:
                raise LedgerBindingError(
                    f"paper {paper_id} has unknown declared_claim_scope {raw_scope!r}"
                ) from error

        records.append(
            PaperSuperiorityRecord(
                paper_id=paper_id,
                issue_number=PAPER_ISSUES[paper_id],
                gates=gates,
                evidence=evidence,
                predecessor_artifacts=tuple(predecessors),
                blockers=tuple(blockers),
                declared_claim_scope=declared_claim_scope,
            )
        )

    ledger_id = payload.get("ledger_id")
    frozen_at = payload.get("frozen_at")
    if not isinstance(ledger_id, str) or not isinstance(frozen_at, str):
        raise LedgerBindingError("ledger_id and frozen_at must be strings")

    try:
        return SuperiorityLedger(
            ledger_id=ledger_id, frozen_at=frozen_at, papers=tuple(records)
        )
    except ValueError as error:
        raise LedgerBindingError(str(error)) from error


def ledger_to_payload(ledger: SuperiorityLedger) -> dict[str, Any]:
    """Round-trip counterpart to :func:`ledger_from_payload`."""

    return {
        "schema_version": SUPERIORITY_LEDGER_SCHEMA,
        "ledger_id": ledger.ledger_id,
        "frozen_at": ledger.frozen_at,
        "papers": [
            {
                "paper_id": paper.paper_id,
                "issue_number": paper.issue_number,
                "declared_claim_scope": (
                    paper.declared_claim_scope.value
                    if paper.declared_claim_scope is not None
                    else None
                ),
                "predecessor_artifacts": [
                    {
                        "artifact_ref": item.artifact_ref,
                        "grade": item.grade.value,
                        "terminal": item.terminal,
                        "note": item.note,
                    }
                    for item in paper.predecessor_artifacts
                ],
                "blockers": [
                    {
                        "gate_id": item.gate_id,
                        "responsibility": item.responsibility.value,
                        "actionability": item.actionability.value,
                        "statement": item.statement,
                        "unblock": item.unblock,
                        "refs": list(item.refs),
                    }
                    for item in paper.blockers
                ],
                "evidence": [
                    {
                        "gate_id": item.gate_id,
                        "grade": item.grade.value,
                        "artifact_refs": list(item.artifact_refs),
                        "protocol_frozen_before_outcome": item.protocol_frozen_before_outcome,
                        "comparator_donor_complete": item.comparator_donor_complete,
                        "evaluator_custody": item.evaluator_custody,
                        "domains": list(item.domains),
                        "independent_implementation": item.independent_implementation,
                        "harm_guard_gate_ids": list(item.harm_guard_gate_ids),
                        "declared_scope": (
                            item.declared_scope.value if item.declared_scope is not None else None
                        ),
                        "notes": item.notes,
                    }
                    for item in paper.evidence
                ],
            }
            for paper in ledger.papers
        ],
    }


__all__ = [
    "LedgerBindingError",
    "SuperiorityLedger",
    "ledger_from_payload",
    "ledger_to_payload",
]
