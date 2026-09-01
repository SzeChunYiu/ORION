"""The guard lifted in #1995/#2011/#2020 has to bite, and to bite differently.

A helper that separates a refutation from a timeout is worth nothing unless it
actually fails on both and actually distinguishes them in the message. The
no-alarm case is here too: a guard that fires on a clean list would have been
switched off the first time it cried wolf.
"""

from __future__ import annotations

import pytest

from orion.programme.mechanized import ProofOutcome, ProofResult, Theorem
from orion.programme.proof_assertions import assert_all_discharged


def _result(name: str, outcome: ProofOutcome) -> ProofResult:
    return ProofResult(
        theorem=Theorem(name=name, statement="a statement", why_it_matters="it is a fixture"),
        outcome=outcome,
        detail="fixture",
    )


def test_a_clean_list_raises_nothing() -> None:
    """The no-alarm case. Without it the guard could be vacuously strict."""

    assert_all_discharged(
        [_result("A", ProofOutcome.PROVED), _result("B", ProofOutcome.PROVED)],
        what="two proved theorems",
    )


def test_an_empty_list_raises_nothing() -> None:
    assert_all_discharged([], what="nothing at all")


def test_a_countermodel_fails_and_says_it_is_a_refutation() -> None:
    with pytest.raises(AssertionError) as excinfo:
        assert_all_discharged(
            [_result("A", ProofOutcome.PROVED), _result("REFUTED", ProofOutcome.COUNTEREXAMPLE)],
            what="a refuted list",
        )
    message = str(excinfo.value)
    assert "REFUTED" in message
    assert "countermodel" in message
    assert "does not go away by re-running" in message
    assert "UNKNOWN" not in message, "a refutation must not be reported as a timeout"


def test_an_unknown_fails_and_says_the_prover_gave_up() -> None:
    with pytest.raises(AssertionError) as excinfo:
        assert_all_discharged(
            [_result("A", ProofOutcome.PROVED), _result("TIMED_OUT", ProofOutcome.UNKNOWN)],
            what="an undecided list",
        )
    message = str(excinfo.value)
    assert "TIMED_OUT" in message
    assert "UNKNOWN" in message
    assert "contended" in message
    assert "countermodel" not in message, "a timeout must not be reported as a refutation"


def test_a_refutation_is_reported_before_a_timeout_when_both_are_present() -> None:
    """Both fail. When both happen the refutation is the one worth reading first,
    because a timeout may vanish on a re-run and a countermodel will not."""

    with pytest.raises(AssertionError) as excinfo:
        assert_all_discharged(
            [
                _result("REFUTED", ProofOutcome.COUNTEREXAMPLE),
                _result("TIMED_OUT", ProofOutcome.UNKNOWN),
            ],
            what="a list with both",
        )
    message = str(excinfo.value)
    assert "REFUTED" in message
    assert "TIMED_OUT" not in message


def test_the_label_reaches_the_message() -> None:
    """Three call sites share this helper, so the failure must name which one."""

    with pytest.raises(AssertionError, match="the P6 commutation-kernel Z3 cross-check"):
        assert_all_discharged(
            [_result("X", ProofOutcome.UNKNOWN)],
            what="the P6 commutation-kernel Z3 cross-check",
        )
