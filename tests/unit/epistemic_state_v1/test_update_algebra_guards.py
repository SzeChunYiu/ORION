from dataclasses import replace
from fractions import Fraction
import importlib.util
from pathlib import Path
import sys

import pytest


MODEL_PATH = Path(__file__).resolve().parents[3] / "src/orion/epistemic_state_v1/model.py"
SPEC = importlib.util.spec_from_file_location("orion_dynamic_state_update_guards", MODEL_PATH)
assert SPEC is not None and SPEC.loader is not None
MODEL = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODEL
SPEC.loader.exec_module(MODEL)


def coordinate(value, epoch=0):
    return MODEL.Coordinate(value, MODEL.Status.KNOWN, "scope", epoch, ("receipt",), "v1")


def state(authority=frozenset()):
    return MODEL.State(
        "subject",
        "PROMOTE",
        0,
        coordinate(Fraction(1, 2)),
        coordinate(True),
        coordinate(Fraction(1, 2)),
        frozenset({"o"}),
        frozenset({"o"}),
        coordinate(True),
        coordinate(True),
        authority,
        (
            MODEL.SupportFamily("f1", frozenset({"p1"}), frozenset({"o"})),
            MODEL.SupportFamily("f2", frozenset({"p2"}), frozenset({"o"})),
        ),
        frozenset(),
        True,
        frozenset({"m"}),
        frozenset({"n"}),
        frozenset({"e"}),
    )


def event(event_id, kind, writes, *, authorized=frozenset(), receipts=()):
    return MODEL.Event(
        event_id,
        "subject",
        kind,
        "digest",
        1,
        writes,
        authorized_coordinate_writes=authorized,
        receipt_ids=receipts,
        estimator_version="v1",
    )


def test_revocations_accumulate_and_commute():
    initial = state()
    p1 = event("r1", "revocation", {"revoked_premise_ids": frozenset({"p1"})})
    p2 = event("r2", "revocation", {"revoked_premise_ids": frozenset({"p2"})})
    forward = MODEL.replay(initial, (p1, p2))
    reverse = MODEL.replay(initial, (p2, p1))
    assert forward == reverse
    assert forward.revoked_premise_ids == frozenset({"p1", "p2"})
    assert forward.surviving_families == ()


def test_non_adjudication_event_cannot_amplify_authority():
    widening = event("w", "evidence", {"authority_scopes": frozenset({"PROMOTE"})})
    with pytest.raises(ValueError, match="unauthorized authority amplification"):
        MODEL.apply_event(state(), widening)


@pytest.mark.parametrize(
    ("authorized", "receipts"),
    ((frozenset(), ("external",)), (frozenset({"authority_scopes"}), ())),
)
def test_external_adjudication_needs_authorized_coordinate_and_receipt(authorized, receipts):
    widening = event(
        "w",
        "external_adjudication",
        {"authority_scopes": frozenset({"PROMOTE"})},
        authorized=authorized,
        receipts=receipts,
    )
    with pytest.raises(ValueError, match="unauthorized authority amplification"):
        MODEL.apply_event(state(), widening)


def test_bound_external_adjudication_can_explicitly_add_authority():
    widening = event(
        "w",
        "external_adjudication",
        {"authority_scopes": frozenset({"PROMOTE"})},
        authorized=frozenset({"authority_scopes"}),
        receipts=("external",),
    )
    assert MODEL.apply_event(state(), widening).authority_scopes == frozenset({"PROMOTE"})


def test_narrowing_never_requires_an_authority_grant_receipt():
    initial = state(frozenset({"PROMOTE"}))
    narrowing = event("n", "responsibility_change", {"authority_scopes": frozenset()})
    assert MODEL.apply_event(initial, narrowing).authority_scopes == frozenset()
