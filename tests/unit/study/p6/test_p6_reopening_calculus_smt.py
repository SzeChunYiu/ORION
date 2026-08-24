"""Tests for P6's mechanized reopening calculus.

The point of this module is that a check can look like a check and test nothing,
so these tests are written to fail if that happens here. Each theorem must be
discharged, the differential must run on a corpus where reopening actually
happens, and the vacuity demonstration must still detect the vacuity it was
written to demonstrate.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from orion.programme.mechanized import ProofOutcome, Theorem, discharge
from orion.study.p6 import reopening_calculus_smt as calc

REPO_ROOT = Path(__file__).resolve().parents[4]

z3 = pytest.importorskip("z3", reason="the reopening calculus needs the z3 solver")


@pytest.fixture(scope="module")
def proofs() -> tuple:
    return calc.prove_all()


class TestTheorems:
    def test_every_theorem_is_discharged(self, proofs: tuple) -> None:
        assert [(r.theorem.name, r.outcome.value) for r in proofs if not r.discharged] == []

    def test_every_declared_theorem_is_attempted(self, proofs: tuple) -> None:
        assert {r.theorem.name for r in proofs} == {t.name for t in calc.THEOREMS}

    def test_completeness_needs_the_well_founded_rank(self) -> None:
        """The rank clause is load-bearing; without it the closure is not least.

        Transitive closure is not first-order definable, so an axiomatisation
        without a decreasing rank admits models where two reachability facts
        justify each other in a cycle. This pins that the axiom is doing work
        rather than decorating the module.
        """

        vocab = calc._vocabulary()
        full = calc._closure_axioms(vocab)
        without_rank = [axiom for index, axiom in enumerate(full) if index not in (3, 4)]
        solver = vocab["z3"]
        n, s = solver.Consts("wn ws", vocab["Node"])
        left, right = solver.Consts("wl wr", vocab["Node"])
        no_edges = solver.ForAll([left, right], solver.Not(vocab["Edge"](left, right)))
        # With no edges at all, nothing but a changed node reaches anything.
        claim = solver.Implies(
            solver.And(vocab["Reach"](s, n), s != n), solver.BoolVal(False)
        )
        with_axiom = discharge(
            Theorem(name="WITH", statement="s", why_it_matters="w"),
            [*full, no_edges],
            claim,
            timeout_ms=15000,
        )
        without_axiom = discharge(
            Theorem(name="WITHOUT", statement="s", why_it_matters="w"),
            [*without_rank, no_edges],
            claim,
            timeout_ms=15000,
        )
        assert with_axiom.outcome is ProofOutcome.PROVED
        assert without_axiom.outcome is not ProofOutcome.PROVED


class TestAgainstTheCommittedModel:
    def test_committed_descendants_matches_the_specification(self) -> None:
        """Exhaustive over every 3-node graph, cyclic ones included."""

        report = calc.differential_against_finite_model(REPO_ROOT, node_count=3)
        assert report.disagreements == ()
        assert report.agreed

    def test_the_differential_corpus_actually_reopens_something(self) -> None:
        """Agreement on a corpus where nothing is ever reopened proves nothing."""

        report = calc.differential_against_finite_model(REPO_ROOT, node_count=3)
        assert report.positive_trials > 0
        assert report.exercised_both_verdicts


class TestTheCommittedCheckIsNoLongerVacuous:
    def test_both_mutations_are_killed_by_the_committed_check(self) -> None:
        """The alarm fired, and this is the state it fired about.

        This test used to assert the opposite, and said so: "if this test ever
        fails, the committed check has become non-vacuous and this module's
        framing needs revisiting -- which is worth being told about." On
        2026-08-22 it failed. ``check_reopening`` had asserted that a set
        difference does not intersect what was removed from it, then that a
        variable equals the expression it was assigned, both of which hold for
        any ``descendants``; it now compares its retained set against a
        specification built from an independently computed transitive closure,
        and both mutants die.

        Kept rather than deleted, and inverted rather than relaxed: a repair that
        removes the test that would notice it regressing has not been checked.
        """

        report = calc.committed_check_is_vacuous(REPO_ROOT, node_count=3)
        assert report["is_vacuous"] is False
        assert report["mutations_survived"] == []
        assert report["baseline"] == [25, 1400]

    def test_our_own_differential_kills_what_the_committed_check_survives(self) -> None:
        """The replacement must detect exactly what the original missed."""

        import importlib

        model = calc.load_executable_model(
            REPO_ROOT / calc.EXECUTABLE_MODEL, "p6_vacuity_contrast"
        )
        original = model.descendants
        try:
            model.descendants = lambda node_count, edges, changed: frozenset()
            # Re-run the differential against the sabotaged implementation by
            # calling the reference directly, since the differential loads its
            # own module instance.
            broken = 0
            for edges in (((0, 1),), ((0, 1), (1, 2))):
                expected = calc._reference_reopened(3, edges, frozenset({0}))
                actual = model.descendants(3, edges, frozenset({0}))
                if frozenset(actual) != expected:
                    broken += 1
            assert broken == 2, "the reference specification failed to notice a constant"
        finally:
            model.descendants = original
        _ = importlib


class TestTheRunner:
    def test_the_runner_is_reachable_as_a_module(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "orion.study.p6.reopening_calculus_smt", "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
            env={
                "PYTHONPATH": "src",
                "PATH": "/usr/bin:/bin:/usr/local/bin",
                # The interpreter binary needs its own runtime loader path.
                # A Python installed outside a default prefix (an HPC module,
                # pyenv, some conda layouts) keeps libpython there, and
                # scrubbing this kills the child with exit 127 before Python
                # starts. Carrying it does not weaken the isolation this env
                # is for: it is the loader's path, not an import path.
                **{
                    key: value
                    for key, value in os.environ.items()
                    if key in ("LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH")
                },
            },
        )
        assert completed.returncode == 0, completed.stderr
        assert "orion-p6-reopening-calculus" in completed.stdout

    def test_main_requires_argv(self) -> None:
        import inspect

        assert inspect.signature(calc.main).parameters["argv"].default is inspect.Parameter.empty


class TestScope:
    def test_the_report_states_what_it_does_not_license(self) -> None:
        report = calc.build_report(REPO_ROOT, node_count=3)
        text = " ".join(str(item) for item in report["not_licensed"])
        assert "155" in text
        assert "independent formal review" in text
        assert report["all_discharged"] is True
