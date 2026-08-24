"""Tests for P6's mechanized separation calculus.

A list of PROVED lines is worth only what the apparatus behind it would report
on a false claim, and a general theorem is worth only what it covers. These
check both: that each theorem is discharged, that a false claim is reported as a
countermodel, that the separation hypothesis is load-bearing rather than
decorative, and that P6's committed mechanic is genuinely an instance.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from orion.programme.mechanized import ProofOutcome, Theorem, discharge
from orion.study.p6 import separation_calculus_smt as calc

REPO_ROOT = Path(__file__).resolve().parents[4]

z3 = pytest.importorskip("z3", reason="the separation calculus needs the z3 solver")


@pytest.fixture(scope="module")
def proofs() -> tuple:
    return calc.prove_all()


class TestTheorems:
    def test_every_theorem_is_discharged(self, proofs: tuple) -> None:
        assert [(r.theorem.name, r.outcome.value) for r in proofs if not r.discharged] == []

    def test_every_declared_theorem_is_attempted(self, proofs: tuple) -> None:
        assert {r.theorem.name for r in proofs} == {t.name for t in calc.THEOREMS}

    def test_the_separation_hypothesis_is_load_bearing(self) -> None:
        """Commutation must fail without separation, or the theorem says nothing.

        A sufficient condition that is not actually needed is a condition that
        was never tested. This is the converse stated as its own theorem, and it
        is discharged by exhibiting a disagreeing model rather than by refuting
        a negation --- so it is checked here that the polarity really is that
        way round.
        """

        result = calc._prove_necessity(timeout_ms=30000)
        assert result.outcome is ProofOutcome.PROVED
        assert "both cross-read directions" in result.detail
        assert "disjoint writes" in result.detail
        assert "frame-faithful deterministic mechanics" in result.detail


class TestTheApparatusCanFail:
    def test_a_false_claim_yields_a_counterexample(self) -> None:
        x, y = z3.Ints("x y")
        result = discharge(
            Theorem(name="FALSE", statement="s", why_it_matters="w"),
            [x > 0],
            x == y,
            timeout_ms=10000,
        )
        assert result.outcome is ProofOutcome.COUNTEREXAMPLE
        assert not result.discharged


class TestInstantiation:
    def test_the_committed_mechanic_obeys_its_declared_frame(self) -> None:
        """If it did not, the general theorem would not cover the finite check."""

        report = calc.instantiation_check(REPO_ROOT, node_count=4)
        assert report.disagreements == ()
        assert report.agreed

    def test_the_instantiation_actually_perturbs_something(self) -> None:
        """Zero perturbations would be perfect agreement about nothing."""

        report = calc.instantiation_check(REPO_ROOT, node_count=4)
        assert report.positive_trials > 0
        assert report.exercised_both_verdicts

    def test_a_frame_violation_would_be_caught(self) -> None:
        """Pin the detector by handing it a mechanic that reads outside its frame."""

        from orion.programme.mechanized import DifferentialReport

        leaky = DifferentialReport(
            trials=10, agreements=9, disagreements=("flipping 3 changed it",), positive_trials=8
        )
        assert not leaky.agreed


class TestTheRunner:
    def test_the_runner_is_reachable_as_a_module(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "orion.study.p6.separation_calculus_smt", "--help"],
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
        assert "orion-p6-separation-calculus" in completed.stdout

    def test_main_requires_argv(self) -> None:
        import inspect

        assert inspect.signature(calc.main).parameters["argv"].default is inspect.Parameter.empty


class TestScope:
    def test_the_report_states_what_it_does_not_license(self) -> None:
        report = calc.build_report(REPO_ROOT, node_count=4)
        text = " ".join(str(item) for item in report["not_licensed"])
        assert "independent formal review" in text
        assert "155" in text
        assert report["all_discharged"] is True
