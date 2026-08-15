import pytest

from orion.engine.cycle import CycleOperator, Transition
from orion.engine.trace import TraceEvent
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
