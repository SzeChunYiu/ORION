from fractions import Fraction

import pytest

from orion.foundations.model import Terminal
from orion.foundations.sufficiency import (
    FiniteInterface,
    bayes_risk,
    data_processing_holds,
    is_target_sufficient,
    minimal_collision,
    synthesise_decision_rule,
)


def test_fibre_theorem_constructive_both_directions() -> None:
    states = ("a", "b", "c")
    target = {"a": Terminal.ESTABLISH, "b": Terminal.ESTABLISH, "c": Terminal.REOPEN}
    sufficient = FiniteInterface("s", {"a": 0, "b": 0, "c": 1})
    insufficient = FiniteInterface("i", {"a": 0, "b": 0, "c": 0})

    assert is_target_sufficient(states, sufficient, target)
    assert synthesise_decision_rule(states, sufficient, target) == {
        0: Terminal.ESTABLISH,
        1: Terminal.REOPEN,
    }
    assert not is_target_sufficient(states, insufficient, target)
    collision = minimal_collision(states, insufficient, target)
    assert collision is not None
    assert {collision.left_state, collision.right_state} in ({"a", "c"}, {"b", "c"})
    with pytest.raises(ValueError):
        synthesise_decision_rule(states, insufficient, target)


def test_bayes_risk_and_data_processing() -> None:
    states = ("a", "b")
    target = {"a": Terminal.ESTABLISH, "b": Terminal.REOPEN}
    probability = {"a": Fraction(1, 2), "b": Fraction(1, 2)}
    fine = FiniteInterface("fine", {"a": "a", "b": "b"})
    coarse = FiniteInterface("coarse", {"a": "x", "b": "x"})

    assert bayes_risk(states, fine, target, probability) == 0
    assert bayes_risk(states, coarse, target, probability) == Fraction(1, 2)
    assert data_processing_holds(states, fine, coarse, target, probability)


def test_answer_coded_interface_is_not_admissible() -> None:
    interface = FiniteInterface(
        "leak",
        {"a": "ESTABLISH", "b": "REOPEN"},
        protected_target_reads=frozenset({"gold"}),
    )
    assert not interface.admissible
