"""Tests for P7's exact-containment replacement bridge rule.

A replacement rule is worth only what its discharges are worth, and the
discharges are worth only what the apparatus reports on a false claim. These
tests pin the twelve theorems, the polarity of the possibility witnesses, the
behaviour on a false claim, and the cross-artifact binding.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from orion.programme.mechanized import ProofOutcome, Theorem, discharge
from orion.study.p7 import exact_containment as ec

REPO_ROOT = Path(__file__).resolve().parents[4]
ARTIFACT = (
    REPO_ROOT
    / "papers/orion-17-epistemic-navigation-open-worlds"
    / "formal/mechanized/P7_EXACT_CONTAINMENT_MECHANIZED_2026-08-24.json"
)

z3 = pytest.importorskip("z3", reason="the exact containment rule needs z3")


@pytest.fixture(scope="module")
def proofs() -> tuple:
    return ec.prove_all()


class TestTheorems:
    def test_every_theorem_is_discharged(self, proofs: tuple) -> None:
        assert [(r.theorem.name, r.outcome.value) for r in proofs if not r.discharged] == []

    def test_every_declared_theorem_is_attempted(self, proofs: tuple) -> None:
        assert {r.theorem.name for r in proofs} == {t.name for t in ec.THEOREMS}

    def test_the_four_required_properties_are_covered(self) -> None:
        names = {t.name for t in ec.THEOREMS}
        # soundness
        assert "EXACT_RULE_IS_SOUND" in names
        # completeness, as the three claims that earn the word
        assert {
            "EXACT_RULE_IS_NOT_DROPPABLE",
            "EXACT_RULE_SUBSUMES_THE_BRIDGE_RULE",
            "CONTAINMENT_STRICTLY_WEAKER_THAN_MATCH",
        } <= names
        # unit
        assert {
            "LEFT_IDENTITY_UNDER_EXACT_RULE",
            "RIGHT_IDENTITY_UNDER_EXACT_RULE",
            "IDENTITY_STRICT_UNDER_EXACT_RULE",
        } <= names
        # associativity
        assert {
            "ASSOCIATIVITY_OBSERVABLE_UNDER_EXACT_RULE",
            "ASSOCIATIVITY_STRICT_UNDER_EXACT_RULE",
        } <= names

    def test_the_strict_laws_rest_on_extensionality(self) -> None:
        """Strict associativity must fail without extensionality, or it was free."""

        solver = z3
        sig, contains = ec.exact_signature()
        axioms = ec.exact_calculus_axioms(sig, contains)
        t, u, v = solver.Consts("na_t na_u na_v", sig.Trans)
        claim = solver.ForAll(
            [t, u, v],
            sig.Comp(sig.Comp(t, u), v) == sig.Comp(t, sig.Comp(u, v)),
        )
        result = discharge(
            Theorem(name="FREE?", statement="s", why_it_matters="w"),
            axioms,
            claim,
            timeout_ms=15000,
        )
        # Without extensionality the equation is not derivable; the solver may
        # say UNKNOWN (over uninterpreted sorts) but must never say PROVED.
        assert result.outcome is not ProofOutcome.PROVED

    def test_the_vacuity_guard_is_a_satisfiability_query(self, proofs: tuple) -> None:
        witness = [r for r in proofs if r.theorem.name == "EXACT_CALCULUS_IS_SATISFIABLE"]
        assert witness and witness[0].discharged
        assert "vacuous" in witness[0].detail or "consistent" in witness[0].detail


class TestTheApparatusCanFail:
    def test_a_false_claim_yields_a_counterexample(self) -> None:
        x, y = z3.Ints("x y")
        result = discharge(
            Theorem(name="FALSE", statement="s", why_it_matters="w"),
            [x > 0],
            x > y,
            timeout_ms=10000,
        )
        assert result.outcome is ProofOutcome.COUNTEREXAMPLE
        assert not result.discharged

    def test_the_replacement_actually_differs_from_the_old_rule(self) -> None:
        """One clause changed, and the axiom builder must still show exactly that."""

        import inspect

        body = inspect.getsource(ec.exact_calculus_axioms)
        assert "contains(sig.Tgt(t), sig.Src(u))" in body
        assert "sig.Bridge(" not in body  # no bridge in the new transport
        assert "sig.match(" not in body  # and no call to the old test either


class TestTheCommittedArtifact:
    @pytest.fixture(scope="class")
    def machine(self) -> dict:
        return json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_the_receipt_records_every_discharge(self, machine: dict) -> None:
        assert machine["contract_id"] == ec.CONTRACT_ID
        assert machine["all_discharged"] is True
        assert machine["undischarged"] == []
        assert {t["name"] for t in machine["theorems"]} == {t.name for t in ec.THEOREMS}

    def test_the_receipt_names_the_rule_it_replaces(self, machine: dict) -> None:
        assert "Match(a,b) := a = b OR Bridge(a,b)" in machine["replaces"]

    def test_the_receipt_keeps_the_incompleteness_on_record(self, machine: dict) -> None:
        text = " ".join(str(x) for x in machine["not_licensed"])
        assert "incompleteness" in text
        assert "data-heavy" in text


class TestTheBinding:
    def test_the_cross_artifact_audit_passes(self) -> None:
        checker_path = (
            REPO_ROOT
            / "papers/orion-17-epistemic-navigation-open-worlds"
            / "formal/check_exact_containment_binding_v1.py"
        )
        spec = importlib.util.spec_from_file_location(
            "check_exact_containment_binding_v1", checker_path
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        report = module.audit()
        assert report["status"] == "PASS", report["errors"]
        assert report["contract_id"] == ec.CONTRACT_ID

    def test_the_old_calculus_is_unchanged_not_patched(self) -> None:
        """Replacing a rule must not rewrite the calculus it replaces."""

        import inspect

        from orion.study.p7 import composition_calculus_smt as cc

        # The old rule keeps its registered-bridge disjunct, verbatim.
        assert "Bridge" in inspect.getsource(cc.match)
        # And its incompleteness theorem stands under its own name.
        assert "MATCH_IS_NOT_NECESSARY" in {t.name for t in cc.THEOREMS}


class TestScope:
    def test_the_report_states_what_it_does_not_license(self) -> None:
        report = ec.build_report()
        text = " ".join(str(item) for item in report["not_licensed"])
        assert "incompleteness" in text
        assert "empirical" in text
        assert "independent formal review" in text

    def test_main_requires_argv(self) -> None:
        import inspect

        assert inspect.signature(ec.main).parameters["argv"].default is inspect.Parameter.empty
