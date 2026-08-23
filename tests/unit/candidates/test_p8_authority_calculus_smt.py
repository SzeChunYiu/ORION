"""Tests for P8's mechanized authority calculus.

The value of a machine-checked proof is entirely in whether the sentence proved
is the sentence the paper claims, and whether a failure would actually be
reported. These tests check both: that the theorems are discharged, that the
proved formula agrees with P8's committed executable model on a corpus that
exercises both verdicts, and --- the part that is easy to skip --- that the
apparatus reports a *failure* when given a false claim, so a run of ten PROVED
lines is evidence and not decoration.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from orion.study.p8 import authority_calculus_smt as calc

REPO_ROOT = Path(__file__).resolve().parents[3]

z3 = pytest.importorskip("z3", reason="the authority calculus needs the z3 solver")


@pytest.fixture(scope="module")
def proofs() -> tuple[calc.ProofResult, ...]:
    return calc.prove_all()


class TestTheorems:
    def test_every_theorem_is_discharged(self, proofs: tuple[calc.ProofResult, ...]) -> None:
        undischarged = [(r.theorem.name, r.outcome.value, r.detail) for r in proofs if not r.discharged]
        assert undischarged == []

    def test_every_declared_theorem_is_actually_attempted(
        self, proofs: tuple[calc.ProofResult, ...]
    ) -> None:
        """A declared theorem nobody runs is a claim with no check behind it."""

        assert {r.theorem.name for r in proofs} == {t.name for t in calc.THEOREMS}

    def test_the_chain_ladder_is_discharged_at_every_length(self) -> None:
        ladder = calc.prove_chain_ladder(bound=4)
        assert [r.outcome for r in ladder] == [calc.ProofOutcome.PROVED] * 4


class TestTheApparatusCanFail:
    """Ten PROVED lines mean nothing if a false claim also prints PROVED."""

    def test_a_false_claim_yields_a_counterexample(self) -> None:
        sig = calc.signature()
        axioms = calc.closure_axioms(sig)
        d1, d2 = z3.Consts("d1 d2", sig.Domain)
        # Plainly false: unrelated domains need not reach each other.
        false_claim = sig.Reach(d1, d2)
        result = calc.discharge(
            calc.Theorem(name="FALSE", statement="s", why_it_matters="w"),
            axioms,
            false_claim,
            timeout_ms=10000,
        )
        assert result.outcome is calc.ProofOutcome.COUNTEREXAMPLE
        assert not result.discharged

    def test_no_laundering_needs_the_justification_axiom(self) -> None:
        """Dropping well-founded justification must break the theorem, not weaken it silently.

        This is the axiom that makes reachability the *least* closure. Without it
        a model can assert arbitrary reach facts, and non-laundering stops being
        provable. If this test ever passes with the axiom removed, the axiom was
        not carrying the theorem and the proof means something other than it says.
        """

        sig = calc.signature()
        full = calc.closure_axioms(sig)
        without_justification = full[:-1]
        d1, d2 = z3.Consts("nl1 nl2", sig.Domain)
        left, right = z3.Consts("cl cr", sig.Domain)
        no_conversions = z3.ForAll([left, right], z3.Not(sig.Conv(left, right)))
        claim = z3.Implies(sig.Reach(d1, d2), d1 == d2)

        with_axiom = calc.discharge(
            calc.Theorem(name="WITH", statement="s", why_it_matters="w"),
            [*full, no_conversions],
            claim,
            timeout_ms=10000,
        )
        without_axiom = calc.discharge(
            calc.Theorem(name="WITHOUT", statement="s", why_it_matters="w"),
            [*without_justification, no_conversions],
            claim,
            timeout_ms=10000,
        )
        assert with_axiom.outcome is calc.ProofOutcome.PROVED
        assert without_axiom.outcome is not calc.ProofOutcome.PROVED


class TestAgainstTheExecutableModel:
    def test_the_formula_agrees_with_p8s_committed_model(self) -> None:
        report = calc.differential_check(REPO_ROOT, trials=120)
        assert report.disagreements == ()
        assert report.agreed

    def test_the_differential_corpus_exercises_both_verdicts(self) -> None:
        """Agreement on a corpus that never authorises is agreement about False.

        The first version of this generator drew every field independently and
        authorised on none of 60 trials, so it compared the two implementations
        only where both refuse. This pins the fix.
        """

        report = calc.differential_check(REPO_ROOT, trials=120)
        assert report.exercised_both_verdicts, report.as_json()
        assert report.positive_trials >= 5

    def test_a_report_that_disagrees_is_not_reported_as_agreed(self) -> None:
        fabricated = calc.DifferentialReport(
            trials=10, agreements=9, disagreements=("trial 3",), positive_trials=4
        )
        assert not fabricated.agreed


class TestTheRunner:
    def test_the_runner_is_reachable_as_a_module(self) -> None:
        """A `main` nothing can invoke is not a runner."""

        completed = subprocess.run(
            [sys.executable, "-m", "orion.study.p8.authority_calculus_smt", "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
            env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin"},
        )
        assert completed.returncode == 0, completed.stderr
        assert "orion-p8-authority-calculus" in completed.stdout

    def test_main_requires_argv(self) -> None:
        import inspect

        signature = inspect.signature(calc.main)
        assert signature.parameters["argv"].default is inspect.Parameter.empty


class TestScope:
    def test_the_report_states_what_it_does_not_license(self) -> None:
        report = calc.build_report(REPO_ROOT, differential_trials=40)
        text = " ".join(str(item) for item in report["not_licensed"])
        assert "independent formal review" in text
        assert "39,936" in text
        assert report["all_discharged"] is True

    def test_the_axioms_are_declared_definitional(self) -> None:
        report = calc.build_report(REPO_ROOT, differential_trials=40)
        assert "not first-order definable" in str(report["axioms_are_definitional"])
        assert "meta" in str(report["induction_is_meta"]) or "hand step" in str(
            report["induction_is_meta"]
        )
