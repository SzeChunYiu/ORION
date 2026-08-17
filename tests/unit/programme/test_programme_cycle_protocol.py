"""Cycle protocol is frozen; unexecuted receipts cannot PASS."""

from __future__ import annotations

from dataclasses import replace

from orion.programme.activation import UNBOUND_DIGEST
from orion.programme.cycle_protocol import (
    CYCLE_PROTOCOL_ID,
    CYCLE_STEPS,
    CycleReceipt,
    cycle_protocol_payload,
    cycle_receipt_payload,
    unexecuted_cycle_receipt,
    validate_cycle_protocol_payload,
    validate_cycle_receipt,
)
from orion.programme.identity import verify_seal
from orion.programme.records import Outcome


def test_nine_cycle_steps_are_frozen() -> None:
    assert len(CYCLE_STEPS) == 9
    assert [step.step_id for step in CYCLE_STEPS] == [
        "P4-C1-SELECT-QUESTION",
        "P4-C2-ATOMIZE",
        "P4-C3-SEARCH-NEAREST",
        "P4-C4-FREEZE-PROTOCOL",
        "P4-C5-DELEGATE",
        "P4-C6-REPLAY-TRANSFER",
        "P4-C7-PROTECTED-EVAL",
        "P4-C8-ARCHIVE-OUTCOMES",
        "P4-C9-REOPEN-GRAPH",
    ]
    assert all(step.requires_before_outcomes for step in CYCLE_STEPS[:5])
    assert CYCLE_STEPS[4].custody == "WORKER"
    assert CYCLE_STEPS[5].custody == "PROTECTED"
    assert CYCLE_STEPS[6].custody == "PROTECTED"


def test_cycle_protocol_payload_claims_zero_executions() -> None:
    payload = cycle_protocol_payload()
    assert verify_seal(payload) == ()
    assert payload["cycles_executed"] == 0
    assert payload["authority_granted"] is False
    assert validate_cycle_protocol_payload(payload) == ()


def test_unexecuted_receipt_is_cannot_check() -> None:
    receipt = unexecuted_cycle_receipt()
    assert receipt.decision is Outcome.CANNOT_CHECK
    assert receipt.executed is False
    assert validate_cycle_receipt(receipt) == ()
    assert verify_seal(cycle_receipt_payload(receipt)) == ()


def test_pass_without_execution_is_refused() -> None:
    receipt = replace(unexecuted_cycle_receipt(), decision=Outcome.PASS)
    errors = validate_cycle_receipt(receipt)
    assert "PASS is refused for a cycle that has not executed" in errors
    assert "PASS is refused without bound replay, fresh-transfer and assurance hashes" in errors


def test_executed_receipt_with_unbound_hashes_is_refused() -> None:
    receipt = replace(unexecuted_cycle_receipt(), executed=True, decision=Outcome.CANNOT_CHECK)
    errors = validate_cycle_receipt(receipt)
    assert "an executed cycle cannot leave evaluation hashes unbound" in errors


def test_executed_pass_requires_three_bound_hashes() -> None:
    bound = "a" * 64
    receipt = CycleReceipt(
        cycle_id="phase4:cycle:fabricated-pass",
        protocol_id=CYCLE_PROTOCOL_ID,
        decision=Outcome.PASS,
        executed=True,
        replay_receipt_hash=bound,
        fresh_transfer_receipt_hash=bound,
        protected_assurance_receipt_hash=bound,
    )
    # Shape-valid if hashes are bound — but this package never constructs one.
    assert validate_cycle_receipt(receipt) == ()
    assert bound != UNBOUND_DIGEST
