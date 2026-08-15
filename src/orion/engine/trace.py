from __future__ import annotations

from dataclasses import dataclass

from orion.engine.cycle import CycleOperator, Transition
from orion.mechanics.receipt import MechanicReceipt

MECHANIC_ID_BY_OPERATOR = {
    CycleOperator.FRAME: "FRAME.v1",
    CycleOperator.SEARCH: "SEARCH.v1",
    CycleOperator.ABSORB: "ABSORB.v1",
    CycleOperator.RECONSTRUCT: "RECONSTRUCT.v1",
    CycleOperator.DETECT: "DETECT.v1",
    CycleOperator.DIAGNOSE: "DIAGNOSE.v1",
    CycleOperator.REFRAME: "REFRAME.v1",
    CycleOperator.REOPEN: "REOPEN.v1",
    CycleOperator.RECURSE: "ORION_SOLVE.v1",
    CycleOperator.SATURATE_BOUNDED: "SATURATE_BOUNDED.v3",
}


@dataclass(frozen=True)
class TraceEvent:
    operator: CycleOperator
    epoch: int
    summary: str
    transition: Transition
    receipt: MechanicReceipt
    pre_state_hash: str
    post_state_hash: str

    def __post_init__(self) -> None:
        self.transition.validate()
        if self.transition.operator is not self.operator:
            raise ValueError("trace event transition/operator mismatch")
        if self.receipt.mechanic_id != MECHANIC_ID_BY_OPERATOR[self.operator]:
            raise ValueError("trace event receipt/mechanic mismatch")
        if self.epoch != self.transition.output_epoch:
            raise ValueError("trace event epoch/transition mismatch")
        if self.receipt.residual_ids != self.transition.residual_ids:
            raise ValueError("trace event receipt/transition residual mismatch")
        if self.receipt.evidence_ids != self.transition.evidence_ids:
            raise ValueError("trace event receipt/transition evidence mismatch")
        if (
            self.receipt.provenance_ids
            != self.transition.scientific_authority_certificate_ids
        ):
            raise ValueError("trace event receipt/transition provenance mismatch")
        handoff = dict(self.receipt.handoff_values)
        if handoff.get("changed_coordinates") != ",".join(
            self.transition.changed_coordinates
        ):
            raise ValueError("trace event receipt/transition handoff mismatch")
        for digest in (self.pre_state_hash, self.post_state_hash):
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError("trace event state bindings must be SHA-256 hashes")


@dataclass(frozen=True)
class SolveTrace:
    trace_id: str
    events: tuple[TraceEvent, ...]

    def __post_init__(self) -> None:
        if not self.trace_id.strip():
            raise ValueError("solve trace identity is required")
        receipt_ids = [event.receipt.receipt_id for event in self.events]
        if len(set(receipt_ids)) != len(receipt_ids):
            raise ValueError("solve trace receipt ids must be unique")
        for previous, current in zip(self.events, self.events[1:], strict=False):
            if previous.post_state_hash != current.pre_state_hash:
                raise ValueError("solve trace state-hash chain is discontinuous")
            if previous.transition.output_epoch != current.transition.input_epoch:
                raise ValueError("solve trace epoch chain is discontinuous")

    @property
    def operator_sequence(self) -> tuple[CycleOperator, ...]:
        return tuple(event.operator for event in self.events)
