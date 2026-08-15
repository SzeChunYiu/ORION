import pytest

from orion.engine.cycle import CycleOperator, Transition
from orion.engine.trace import SolveTrace, TraceEvent
from orion.mechanics import MechanicReceipt, MechanicRunStatus


def _receipt(**changes):
    values = {
        "receipt_id": "receipt:search",
        "mechanic_id": "SEARCH.v1",
        "status": MechanicRunStatus.PARTIAL,
        "action_ids": ("SEARCH",),
        "handoff_values": (("changed_coordinates", "W.SEARCHED"),),
        "residual_ids": ("coverage-open",),
        "failure_signature": ("search_incomplete",),
        "evidence_ids": ("e:1",),
        "evidence_bindings": (("e:1", "a" * 64),),
        "provenance_ids": ("certificate:1",),
    }
    values.update(changes)
    return MechanicReceipt(**values)


def _transition():
    return Transition(
        CycleOperator.SEARCH,
        input_epoch=0,
        output_epoch=1,
        evidence_ids=("e:1",),
        residual_ids=("coverage-open",),
        scientific_authority_certificate_ids=("certificate:1",),
        changed_coordinates=("W.SEARCHED",),
    )


@pytest.mark.parametrize(
    ("change", "message"),
    (
        ({"residual_ids": ("erased",)}, "residual mismatch"),
        (
            {
                "evidence_ids": ("e:2",),
                "evidence_bindings": (("e:2", "b" * 64),),
            },
            "evidence mismatch",
        ),
        ({"provenance_ids": ("certificate:other",)}, "provenance mismatch"),
        (
            {"handoff_values": (("changed_coordinates", "K.CLAIMS"),)},
            "handoff mismatch",
        ),
    ),
)
def test_trace_event_rejects_receipt_transition_substitution(change, message):
    with pytest.raises(ValueError, match=message):
        TraceEvent(
            CycleOperator.SEARCH,
            1,
            "fixture",
            _transition(),
            _receipt(**change),
            "1" * 64,
            "2" * 64,
        )


def test_trace_event_rejects_backward_transition():
    transition = Transition(CycleOperator.SEARCH, input_epoch=2, output_epoch=1)
    receipt = MechanicReceipt(
        "receipt:backward",
        "SEARCH.v1",
        MechanicRunStatus.SUCCEEDED,
        action_ids=("SEARCH",),
        handoff_values=(("changed_coordinates", ""),),
    )
    with pytest.raises(ValueError, match="cannot move backward"):
        TraceEvent(
            CycleOperator.SEARCH,
            1,
            "backward",
            transition,
            receipt,
            "1" * 64,
            "2" * 64,
        )


def test_solve_trace_rejects_discontinuous_state_chain():
    first_transition = Transition(CycleOperator.FRAME, 0, 1)
    second_transition = Transition(CycleOperator.SEARCH, 7, 8)
    first = TraceEvent(
        CycleOperator.FRAME,
        1,
        "frame",
        first_transition,
        MechanicReceipt(
            "receipt:frame",
            "FRAME.v1",
            MechanicRunStatus.SUCCEEDED,
            action_ids=("FRAME",),
            handoff_values=(("changed_coordinates", ""),),
        ),
        "a" * 64,
        "b" * 64,
    )
    second = TraceEvent(
        CycleOperator.SEARCH,
        8,
        "search",
        second_transition,
        MechanicReceipt(
            "receipt:search-2",
            "SEARCH.v1",
            MechanicRunStatus.SUCCEEDED,
            action_ids=("SEARCH",),
            handoff_values=(("changed_coordinates", ""),),
        ),
        "c" * 64,
        "d" * 64,
    )
    with pytest.raises(ValueError, match="state-hash chain"):
        SolveTrace("trace:broken", (first, second))
