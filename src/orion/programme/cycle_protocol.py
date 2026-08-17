"""Step-4 cycle protocol and per-cycle receipt *shapes*.

The nine cycle steps are frozen as a protocol. No cycle is executed here.
A receipt whose decision is ``PASS`` without bound evidence hashes is refused;
``CANNOT_CHECK`` is the only honest decision for a cycle that has not run.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orion.programme.activation import PREPARATORY_STATUS, UNBOUND_DIGEST
from orion.programme.identity import is_sha256, seal
from orion.programme.records import Outcome, required_text_errors

CYCLE_PROTOCOL_SCHEMA = "orion.programme.cycle-protocol.v1"
CYCLE_RECEIPT_SCHEMA = "orion.programme.cycle-receipt.v1"
CYCLE_PROTOCOL_ID = "phase4:cycle-protocol:preparatory-v1"


@dataclass(frozen=True)
class CycleStep:
    """One step of the repeated protected-research cycle."""

    step_id: str
    title: str
    custody: str
    requires_before_outcomes: bool


CYCLE_STEPS: tuple[CycleStep, ...] = (
    CycleStep("P4-C1-SELECT-QUESTION", "Select/open a research question from auditable programme state", "PROGRAMME", True),
    CycleStep("P4-C2-ATOMIZE", "Atomize object/search-universe/method uncertainties", "PROGRAMME", True),
    CycleStep("P4-C3-SEARCH-NEAREST", "Search nearest work/current evidence before invention", "PROGRAMME", True),
    CycleStep("P4-C4-FREEZE-PROTOCOL", "Freeze hypotheses/discriminators/protocol before protected outcomes", "PROGRAMME", True),
    CycleStep("P4-C5-DELEGATE", "Delegate bounded research/implementation work to internal workers", "WORKER", True),
    CycleStep("P4-C6-REPLAY-TRANSFER", "Run motivating replay and independent fresh transfer", "PROTECTED", False),
    CycleStep("P4-C7-PROTECTED-EVAL", "Run protected evaluation/assurance outside candidate custody", "PROTECTED", False),
    CycleStep("P4-C8-ARCHIVE-OUTCOMES", "Archive accepted, null, harmful and rejected outcomes", "PROGRAMME", False),
    CycleStep("P4-C9-REOPEN-GRAPH", "Update dependency graph and reopen affected knowledge states", "PROGRAMME", False),
)


@dataclass(frozen=True)
class CycleReceipt:
    """Wire shape for one cycle. Empty evidence is representable; a fake PASS is not."""

    cycle_id: str
    protocol_id: str
    decision: Outcome = Outcome.CANNOT_CHECK
    replay_receipt_hash: str = UNBOUND_DIGEST
    fresh_transfer_receipt_hash: str = UNBOUND_DIGEST
    protected_assurance_receipt_hash: str = UNBOUND_DIGEST
    archived_outcome_ids: tuple[str, ...] = ()
    reopen_event_ids: tuple[str, ...] = ()
    executed: bool = False


def cycle_protocol_payload() -> dict[str, Any]:
    return seal(
        {
            "schema_version": CYCLE_PROTOCOL_SCHEMA,
            "protocol_id": CYCLE_PROTOCOL_ID,
            "programme_status": PREPARATORY_STATUS,
            "cycles_executed": 0,
            "authority_granted": False,
            "steps": [
                {
                    "step_id": step.step_id,
                    "title": step.title,
                    "custody": step.custody,
                    "requires_before_outcomes": step.requires_before_outcomes,
                }
                for step in CYCLE_STEPS
            ],
        }
    )


def cycle_receipt_payload(receipt: CycleReceipt) -> dict[str, Any]:
    return seal(
        {
            "schema_version": CYCLE_RECEIPT_SCHEMA,
            "cycle_id": receipt.cycle_id,
            "protocol_id": receipt.protocol_id,
            "decision": receipt.decision.value,
            "executed": receipt.executed,
            "replay_receipt_hash": receipt.replay_receipt_hash,
            "fresh_transfer_receipt_hash": receipt.fresh_transfer_receipt_hash,
            "protected_assurance_receipt_hash": receipt.protected_assurance_receipt_hash,
            "archived_outcome_ids": list(receipt.archived_outcome_ids),
            "reopen_event_ids": list(receipt.reopen_event_ids),
        }
    )


def validate_cycle_protocol_payload(document: dict[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if document.get("schema_version") != CYCLE_PROTOCOL_SCHEMA:
        errors.append("cycle protocol schema_version mismatch")
    if document.get("cycles_executed") != 0:
        errors.append("cycle protocol must not claim executed cycles")
    if document.get("authority_granted") is not False:
        errors.append("cycle protocol must not grant authority")
    listed = [entry.get("step_id") for entry in document.get("steps", ())]
    expected = [step.step_id for step in CYCLE_STEPS]
    if listed != expected:
        errors.append("cycle protocol steps do not match the frozen nine-step sequence")
    return tuple(dict.fromkeys(errors))


def validate_cycle_receipt(receipt: CycleReceipt) -> tuple[str, ...]:
    errors: list[str] = list(required_text_errors(receipt.cycle_id, "cycle_id"))
    if receipt.protocol_id != CYCLE_PROTOCOL_ID:
        errors.append("cycle receipt protocol_id mismatch")
    hashes = (
        receipt.replay_receipt_hash,
        receipt.fresh_transfer_receipt_hash,
        receipt.protected_assurance_receipt_hash,
    )
    for label, value in zip(
        ("replay_receipt_hash", "fresh_transfer_receipt_hash", "protected_assurance_receipt_hash"),
        hashes,
        strict=True,
    ):
        if not is_sha256(value):
            errors.append(f"{label} must be a SHA-256 digest")
    bound = all(value != UNBOUND_DIGEST for value in hashes)
    if receipt.decision is Outcome.PASS:
        if not receipt.executed:
            errors.append("PASS is refused for a cycle that has not executed")
        if not bound:
            errors.append("PASS is refused without bound replay, fresh-transfer and assurance hashes")
    if receipt.executed and not bound:
        errors.append("an executed cycle cannot leave evaluation hashes unbound")
    if not receipt.executed and receipt.decision is not Outcome.CANNOT_CHECK:
        errors.append("a cycle that has not run must decide CANNOT_CHECK")
    return tuple(dict.fromkeys(errors))


def unexecuted_cycle_receipt(cycle_id: str = "phase4:cycle:unexecuted") -> CycleReceipt:
    return CycleReceipt(cycle_id=cycle_id, protocol_id=CYCLE_PROTOCOL_ID)


__all__ = [
    "CYCLE_PROTOCOL_ID",
    "CYCLE_PROTOCOL_SCHEMA",
    "CYCLE_RECEIPT_SCHEMA",
    "CYCLE_STEPS",
    "CycleReceipt",
    "CycleStep",
    "cycle_protocol_payload",
    "cycle_receipt_payload",
    "unexecuted_cycle_receipt",
    "validate_cycle_protocol_payload",
    "validate_cycle_receipt",
]
