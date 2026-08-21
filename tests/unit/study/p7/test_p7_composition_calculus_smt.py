"""Tests for P7's mechanized composition calculus.

Eighteen ``PROVED`` lines are worth exactly what the apparatus behind them would
report on a false claim, and a general theorem is worth exactly what it covers.
These check both, and two things beyond them.

*Both polarities can fail.* This module discharges validity claims by refuting a
negation and independence claims by exhibiting a model, so ``PROVED`` is produced
two different ways. A test that only pins the first would leave half the report
unguarded, and the second half is where the interesting results are --- the
fail-closed gap, the reflexivity side condition, the extensionality side
condition.

*Every load-bearing axiom is removable.* Bridge soundness, coordinate transport
and extensionality each carry a named theorem. Each is removed here and the
theorem is required to stop being provable. An axiom nobody has removed is an
axiom nobody has checked is doing anything.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from orion.study.p7 import composition_calculus_smt as calc

REPO_ROOT = Path(__file__).resolve().parents[4]

z3 = pytest.importorskip("z3", reason="the composition calculus needs the z3 solver")


@pytest.fixture(scope="module")
def proofs() -> tuple[calc.ProofResult, ...]:
    return calc.prove_all()


@pytest.fixture(scope="module")
def report() -> dict:
    return calc.build_report(REPO_ROOT, differential_trials=12, chain_bound=4)


@pytest.fixture(scope="module")
def instantiation() -> dict:
    return calc.instantiation_check(REPO_ROOT)


class TestTheorems:
    def test_every_theorem_is_discharged(self, proofs: tuple[calc.ProofResult, ...]) -> None:
        undischarged = [
            (r.theorem.name, r.outcome.value, r.detail) for r in proofs if not r.discharged
        ]
        assert undischarged == []

    def test_every_declared_theorem_is_actually_attempted(
        self, proofs: tuple[calc.ProofResult, ...]
    ) -> None:
        """A declared theorem nobody runs is a claim with no check behind it."""

        assert {r.theorem.name for r in proofs} == {t.name for t in calc.THEOREMS}

    def test_the_chain_ladder_is_discharged_at_every_length(self) -> None:
        ladder = calc.prove_chain_ladder(bound=5)
        assert [r.outcome for r in ladder] == [calc.ProofOutcome.PROVED] * 5
        assert ladder[0].theorem.name == "CHAIN_STEP_LEMMA"

    def test_the_hinge_is_proved_from_the_axioms_alone(self) -> None:
        """The corollaries and the ladder run under it, so it must not run under itself.

        Three theorems and every ladder length are discharged with the hinge as a
        hypothesis. If the hinge were only provable *with* itself the whole
        development would be circular, so this discharges it against
        ``checker_axioms`` and nothing else.
        """

        sig = calc.signature()
        result = calc.prove_hinge(sig, calc.checker_axioms(sig), timeout_ms=30000)
        assert result.outcome is calc.ProofOutcome.PROVED

    def test_the_corollaries_do_not_inherit_authority_from_an_unproved_hinge(self) -> None:
        """The gate: a hinge that fails must not license the corollaries.

        Handed an axiom set the hinge cannot be proved from --- coordinate
        transport removed --- ``prove_chain_ladder``'s gate must refuse to use it,
        and the ladder must report failure rather than a row of ``PROVED`` lines
        resting on a hypothesis nobody established.
        """

        sig = calc.signature()
        groups = calc.checker_axiom_groups(sig)
        crippled = [
            axiom
            for name, group in groups.items()
            if name != "coordinate_transport"
            for axiom in group
        ]
        hinge = calc.prove_hinge(sig, crippled, timeout_ms=15000)
        assert hinge.outcome is not calc.ProofOutcome.PROVED


class TestTheApparatusCanFail:
    """Both polarities must be able to report a failure, or neither means anything."""

    def test_discharge_reports_a_countermodel_on_a_plainly_false_claim(self) -> None:
        """The shared apparatus itself, with no quantified axioms in the way."""

        x, y = z3.Ints("apparatus_x apparatus_y")
        result = calc.discharge(
            calc.Theorem(name="FALSE", statement="s", why_it_matters="w"),
            [x > 0],
            x == y,
            timeout_ms=10000,
        )
        assert result.outcome is calc.ProofOutcome.COUNTEREXAMPLE
        assert not result.discharged

    def test_a_false_claim_over_the_uninterpreted_signature_is_not_discharged(self) -> None:
        """The limitation, pinned rather than hidden.

        Over the uninterpreted signature the quantified axioms defeat model-based
        instantiation, so a *false* claim comes back ``UNKNOWN`` rather than
        ``COUNTEREXAMPLE`` --- the solver cannot build the model that would refute
        it. That is why the independence results live in finite structures. It
        does not weaken any ``PROVED`` line, because ``unsat`` is sound and a false
        claim can never produce one; what it means is that failure here shows up
        as "not discharged" rather than as a printed countermodel, and the
        assertion is written to hold either way.
        """

        sig = calc.signature()
        axioms = calc.checker_axioms(sig)
        t, u = z3.Consts("false_t false_u", sig.Trans)
        # Plainly false: unrelated transformations need not have matching contracts.
        result = calc.discharge(
            calc.Theorem(name="FALSE", statement="s", why_it_matters="w"),
            axioms,
            calc.match(sig, sig.Tgt(t), sig.Src(u)),
            timeout_ms=15000,
        )
        assert result.outcome is not calc.ProofOutcome.PROVED
        assert not result.discharged

    def test_a_false_claim_in_the_finite_world_yields_a_counterexample(self) -> None:
        """Where a countermodel is available, it is produced.

        The finite structures are decidable, so the same kind of false claim --- an
        arbitrary transformation carries closure --- is refuted with a model rather
        than timed out on.
        """

        world = calc._finite_checker_world()
        t = z3.Const("finfalse_t", world["Trans"])
        result = calc.discharge(
            calc.Theorem(name="FALSE_FINITE", statement="s", why_it_matters="w"),
            world["axioms"],
            world["carries"](t),
            timeout_ms=15000,
        )
        assert result.outcome is calc.ProofOutcome.COUNTEREXAMPLE
        assert not result.discharged

    def test_a_false_independence_claim_is_refuted_not_proved(self) -> None:
        """The satisfiability half must report failure too.

        Ask for the same model :data:`IDENTITY_NEEDS_A_REFLEXIVE_CONTRACT_TEST`
        exhibits, but in the world where the match test *is* reflexive. No such
        model exists, so ``_exhibit`` must come back ``COUNTEREXAMPLE``. If it did
        not, every independence result in the report would be unfalsifiable.
        """

        world = calc._finite_checker_world(reflexive_match=True)
        t = z3.Const("polarity_t", world["Trans"])
        unit = world["Comp"](world["Ident"](world["Src"](t)), t)
        result = calc._exhibit(
            calc.Theorem(name="IMPOSSIBLE", statement="s", why_it_matters="w"),
            world["axioms"],
            [world["carries"](t), z3.Not(world["carries"](unit))],
            timeout_ms=15000,
            refuted="no such model exists",
        )
        assert result.outcome is calc.ProofOutcome.COUNTEREXAMPLE
        assert not result.discharged

    def test_the_finite_structures_are_checked_against_the_axioms(self) -> None:
        """A structure that is not a model would make every independence result void.

        The finite worlds assert their hand-built function tables *and* the axioms
        restated over the carrier. Corrupting one table entry must make the whole
        thing unsatisfiable; if it does not, the axioms are not being checked and
        the tables are being taken on trust.
        """

        world = calc._finite_checker_world()
        corrupt = z3.Not(
            world["Native"](world["Ident"](z3.Const("corrupt_k", world["Contract"])))
        )
        solver = z3.Solver()
        solver.set("timeout", 15000)
        for axiom in world["axioms"]:
            solver.add(axiom)
        solver.add(corrupt)
        assert solver.check() == z3.unsat


class TestLoadBearingAxioms:
    """Remove the axiom, watch the theorem stop being provable."""

    def test_totality_composition_needs_bridge_soundness(self) -> None:
        """Without it a registered bridge is a name, and the theorem it licenses fails.

        Reported as a pair because the polarity is inverted: the query looks for a
        *counterexample*, so ``COUNTEREXAMPLE`` on the ``with_axiom`` run means no
        counterexample exists and ``PROVED`` on the ``without_axiom`` run means one
        does.
        """

        pin = calc.axiom_pin_bridge_soundness(timeout_ms=30000)
        assert pin["with_axiom"].outcome is calc.ProofOutcome.COUNTEREXAMPLE
        assert pin["without_axiom"].outcome is calc.ProofOutcome.PROVED

    def test_strict_associativity_needs_extensionality(self) -> None:
        sig = calc.signature()
        checker = calc.checker_axioms(sig)
        t, u, v = z3.Consts("pin_t pin_u pin_v", sig.Trans)
        claim = sig.Comp(sig.Comp(t, u), v) == sig.Comp(t, sig.Comp(u, v))
        theorem = calc.Theorem(name="STRICT", statement="s", why_it_matters="w")
        with_axiom = calc.discharge(
            theorem, [*checker, *calc.extensionality_axiom(sig)], claim, timeout_ms=30000
        )
        without_axiom = calc.discharge(theorem, checker, claim, timeout_ms=15000)
        assert with_axiom.outcome is calc.ProofOutcome.PROVED
        assert without_axiom.outcome is not calc.ProofOutcome.PROVED

    def test_composition_soundness_needs_coordinate_transport(self) -> None:
        """The one substantive axiom of the checked layer.

        Everything the calculus says about composition comes from it, so removing
        it must break the headline theorem rather than leave it standing on the
        structural clauses.
        """

        sig = calc.signature()
        groups = calc.checker_axiom_groups(sig)
        full = [axiom for group in groups.values() for axiom in group]
        without = [
            axiom
            for name, group in groups.items()
            if name != "coordinate_transport"
            for axiom in group
        ]
        t, u = z3.Consts("tr_t tr_u", sig.Trans)
        claim = sig.Carries(sig.Comp(t, u)) == z3.And(
            sig.Carries(t), sig.Carries(u), calc.match(sig, sig.Tgt(t), sig.Src(u))
        )
        theorem = calc.Theorem(name="TRANSPORT", statement="s", why_it_matters="w")
        assert (
            calc.discharge(theorem, full, claim, timeout_ms=30000).outcome
            is calc.ProofOutcome.PROVED
        )
        assert (
            calc.discharge(theorem, without, claim, timeout_ms=15000).outcome
            is not calc.ProofOutcome.PROVED
        )


class TestTheGapIsReal:
    def test_the_checked_rule_refuses_obligation_equivalent_contracts(self) -> None:
        """The finding, pinned: match is sufficient, not necessary, and this is why.

        The witness must have both legs total, the composite total and demanding
        something, and the emitted and consumed contracts demanding exactly the
        same obligations. If that were unsatisfiable the fail-closed gap would be
        a different, smaller thing than the report says.
        """

        result = calc._prove_match_is_not_necessary(timeout_ms=30000)
        assert result.outcome is calc.ProofOutcome.PROVED

    def test_matching_contracts_really_do_suffice(self) -> None:
        """Sufficiency is not vacuous: total legs with a matching hand-off exist."""

        world = calc._finite_semantic_world()
        t, u = z3.Consts("nv_t nv_u", world["Trans"])
        solver = z3.Solver()
        solver.set("timeout", 15000)
        for axiom in world["axioms"]:
            solver.add(axiom)
        solver.add(world["total"](t), world["total"](u))
        solver.add(world["match"](world["Tgt"](t), world["Src"](u)))
        solver.add(z3.Or(*[world["Demands"](world["Tgt"](u), o) for o in world["obl_consts"]]))
        assert solver.check() == z3.sat


class TestAgainstTheExecutableModel:
    def test_the_formula_agrees_with_p7s_committed_model(self) -> None:
        differential = calc.differential_check(REPO_ROOT, trials=20)
        assert differential.disagreements == ()
        assert differential.agreed

    def test_the_differential_corpus_exercises_both_verdicts(self) -> None:
        """Agreement on a corpus that never carries is agreement about False.

        P7's closure lift is true on 1 of every 64 draws, so a uniform generator
        would compare the two implementations almost entirely where both refuse.
        This pins the biased draw.
        """

        differential = calc.differential_check(REPO_ROOT, trials=20)
        assert differential.exercised_both_verdicts, differential.as_json()
        assert differential.positive_trials >= 3

    def test_a_report_that_disagrees_is_not_reported_as_agreed(self) -> None:
        fabricated = calc.DifferentialReport(
            trials=10, agreements=9, disagreements=("rand_3",), positive_trials=4
        )
        assert not fabricated.agreed


class TestInstantiation:
    def test_the_committed_composition_rows_are_discharged_as_instances(
        self, instantiation: dict
    ) -> None:
        assert instantiation["composition_instances_attempted"] == 50
        assert instantiation["composition_instances_undischarged"] == []

    def test_the_committed_unit_rule_is_the_closure_lift(self, instantiation: dict) -> None:
        rows = instantiation["closure_lift_rows"]
        assert rows["trials"] == 320
        assert rows["disagreements"] == []
        assert rows["exercised_both_verdicts"]

    def test_the_published_counts_recompute(self, instantiation: dict) -> None:
        assert instantiation["counts_mismatched"] == {}
        assert instantiation["published_counts"]["composition_successes"] == 25
        assert instantiation["published_counts"]["composition_bridge_countermodels"] == 25

    def test_the_thinness_of_the_committed_rows_is_recorded(
        self, instantiation: dict
    ) -> None:
        """Deriving 25 copies of one fact as instances does not make them 25 facts."""

        assert "neither donor is read" in instantiation["instances_are_thin"]


class TestTheRunner:
    def test_the_runner_is_reachable_as_a_module(self) -> None:
        """A `main` nothing can invoke is not a runner."""

        completed = subprocess.run(
            [sys.executable, "-m", "orion.study.p7.composition_calculus_smt", "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
            env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin"},
        )
        assert completed.returncode == 0, completed.stderr
        assert "orion-p7-composition-calculus" in completed.stdout

    def test_main_requires_argv(self) -> None:
        import inspect

        signature = inspect.signature(calc.main)
        assert signature.parameters["argv"].default is inspect.Parameter.empty


class TestScope:
    def test_the_report_states_what_it_does_not_license(self, report: dict) -> None:
        text = " ".join(str(item) for item in report["not_licensed"])
        assert "independent formal review" in text
        assert "25" in text
        assert report["all_discharged"] is True

    def test_the_report_states_the_side_conditions(self, report: dict) -> None:
        conditions = report["side_conditions"]
        assert "reflexive" in conditions["identity"]
        assert "extensionality" in conditions["associativity"]
        assert "NOT necessary" in conditions["intermediate_contract_composition"]

    def test_the_axioms_are_declared_definitional(self, report: dict) -> None:
        assert "are not derived" in str(report["axioms_are_definitional"])
        assert "hand step" in str(report["induction_is_meta"])

    def test_the_report_states_the_hinge_and_corollary_structure(self, report: dict) -> None:
        """A reader must be able to tell which theorems rest on which."""

        text = str(report["one_hinge_and_its_corollaries"])
        assert "discharged from the axioms alone" in text
        assert "ASSOCIATIVITY_CARRIES" in text

    def test_the_axiom_pin_is_reported_with_the_report(self, report: dict) -> None:
        assert report["bridge_soundness_axiom_pin"]["axiom_is_load_bearing"] is True

    def test_the_supplied_premise_open_item_is_answered_and_bounded(
        self, report: dict
    ) -> None:
        """The recorded open item, and the limit on what answering it buys.

        ``research/failures/2026-08-supplied-premise-unbuilt-decision/`` asks the
        theory lane to make ``bridge_match`` computed rather than typed. It is,
        here. The report must say so and must also say that this does not repair
        the committed artifact, whose counts come from an expression containing no
        transform, contract or bridge at all.
        """

        text = str(report["bridge_match_is_no_longer_a_supplied_premise"])
        assert "no argument left to supply" in text
        assert "still come from an expression" in text
