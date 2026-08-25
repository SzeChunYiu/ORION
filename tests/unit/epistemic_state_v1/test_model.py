from dataclasses import replace
from fractions import Fraction
import importlib.util
from pathlib import Path
import sys

import pytest

MODEL_PATH = (
    Path(__file__).resolve().parents[3]
    / "src"
    / "orion"
    / "epistemic_state_v1"
    / "model.py"
)
SPEC = importlib.util.spec_from_file_location("orion_dynamic_state_model", MODEL_PATH)
assert SPEC is not None and SPEC.loader is not None
MODEL = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODEL
SPEC.loader.exec_module(MODEL)

Action = MODEL.Action
Coordinate = MODEL.Coordinate
Event = MODEL.Event
GainVector = MODEL.GainVector
ResearchAction = MODEL.ResearchAction
ResourceVector = MODEL.ResourceVector
State = MODEL.State
Status = MODEL.Status
SupportFamily = MODEL.SupportFamily
Terminal = MODEL.Terminal
apply_event = MODEL.apply_event
compatible_states = MODEL.compatible_states
local_saturated = MODEL.local_saturated
pareto = MODEL.pareto
promotion_policy = MODEL.promotion_policy
replay = MODEL.replay
revocation_survivors = MODEL.revocation_survivors
should_jump = MODEL.should_jump


def c(value, status=Status.KNOWN, epoch=0):
    return Coordinate(value, status, "unit", epoch, ("r",), "v1")


def state(subject="s"):
    return State(
        subject,
        "PROMOTE",
        0,
        c(Fraction(9, 10)),
        c(True),
        c(Fraction(4, 5)),
        frozenset({"o1", "o2"}),
        frozenset({"o1", "o2"}),
        c(True),
        c(True),
        frozenset({"PROMOTE"}),
        (SupportFamily("f", frozenset({"p"}), frozenset({"o1", "o2"})),),
        frozenset(),
        True,
        frozenset({"m"}),
        frozenset({"n"}),
        frozenset({"e"}),
    )


def test_noncompensatory_projection():
    policy = promotion_policy("PROMOTE")
    baseline = state()
    assert policy.project(baseline) is Terminal.ADMISSIBLE
    assert (
        policy.project(replace(baseline, evidence=c(1), identifiability=c(False)))
        is Terminal.BLOCKED
    )
    assert (
        policy.project(replace(baseline, custody_external=False))
        is Terminal.CANNOT_CHECK
    )


def test_event_idempotence_and_replay():
    baseline = state()
    event = Event(
        "e1",
        "s",
        "replication",
        "abc",
        1,
        {"evidence": c(Fraction(19, 20), epoch=1)},
    )
    once = apply_event(baseline, event)
    assert apply_event(once, event) == once
    assert replay(baseline, [event, event]) == once


def test_event_guards():
    with pytest.raises(ValueError):
        apply_event(state(), Event("e", "other", "x", "d", 1, {}))
    with pytest.raises(ValueError):
        apply_event(state(), Event("e", "s", "x", "d", 1, {"magic_score": 1}))


def test_revocation_preserves_alternative_support():
    families = (
        SupportFamily("a", frozenset({"p1"}), frozenset({"o"})),
        SupportFamily("b", frozenset({"p2"}), frozenset({"o"})),
    )
    assert [item.family_id for item in revocation_survivors(families, {"p1"})] == [
        "b"
    ]


def test_legacy_inverse_is_set_valued():
    policy = promotion_policy("PROMOTE")
    left = replace(state("a"), custody_external=False)
    right = replace(state("b"), custody_external=False)
    assert len(compatible_states((left, right), policy, Terminal.CANNOT_CHECK)) == 2


def test_pareto_keeps_tradeoffs_and_removes_dominated():
    local_coverage = ResearchAction(
        "a",
        Action.SEARCH_LOCAL,
        GainVector(
            coverage=Fraction(1, 3), cost=ResourceVector(acquisition=Fraction(1))
        ),
        "near",
        True,
    )
    discriminator = ResearchAction(
        "b",
        Action.DISCRIMINATE,
        GainVector(
            identifiability=Fraction(1),
            cost=ResourceVector(acquisition=Fraction(3)),
        ),
        "near",
        True,
    )
    dominated = ResearchAction(
        "d",
        Action.SEARCH_LOCAL,
        GainVector(
            coverage=Fraction(1, 4), cost=ResourceVector(acquisition=Fraction(2))
        ),
        "near",
        True,
    )
    assert {
        item.action_id for item in pareto((local_coverage, discriminator, dominated))
    } == {"a", "b"}


def test_remote_jump_requires_saturation_and_open_obligation():
    unresolved = replace(state(), obligations_satisfied=frozenset({"o1"}))
    local = ResearchAction(
        "l",
        Action.SEARCH_LOCAL,
        GainVector(cost=ResourceVector(acquisition=Fraction(1))),
        "near",
        True,
    )
    remote = ResearchAction(
        "r",
        Action.SEARCH_REMOTE_STRUCTURE,
        GainVector(
            obligation=Fraction(1), cost=ResourceVector(acquisition=Fraction(2))
        ),
        "music",
        False,
    )
    assert local_saturated((local, remote))
    assert should_jump(unresolved, (local, remote))
    assert not should_jump(state(), (local, remote))
