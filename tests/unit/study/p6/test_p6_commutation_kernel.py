"""Tests for P6's kernel mechanization of the exact Theorem 7 statement.

A serialized proof is only evidence if the kernel that replays it can also
reject a proof that was never built, and a committed artifact is only evidence
if re-checking it in this checkout reproduces the recorded verdicts. These
tests pin both: the kernel's guards, the replay of the committed JSON, the
detection of tampering with it, and the cross-artifact binding audit.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from orion.programme.lcf_kernel import Kernel, KernelError, Term, Var, eq
from orion.study.p6 import commutation_kernel as ck

REPO_ROOT = Path(__file__).resolve().parents[4]
ARTIFACT = (
    REPO_ROOT
    / "papers/orion-16-formal-epistemic-structures-and-mechanics"
    / "formal/mechanized/P6_COMMUTATION_KERNEL_MECHANIZED_2026-08-24.json"
)

EXACT_CONCLUSION = (
    "forall E:Env. implies(and(mOK(E), and(nOK(E), and(nOK(applyM(E)), "
    "and(mOK(applyN(E)), indep(mEv(E), nEv(E)))))), "
    "and(eq_Sci(sci(applyN(applyM(E))), sci(applyM(applyN(E)))), "
    "heq(hist(applyN(applyM(E))), hist(applyM(applyN(E))))))"
)


def _small_kernel() -> Kernel:
    return Kernel(ck._signature())


class TestKernelGuards:
    """The replay only means something if the rules cannot be fed nonsense."""

    def test_trans_with_mismatched_middle_is_rejected(self) -> None:
        kern = _small_kernel()
        a = Var("a", "Sci")
        b = Var("b", "Sci")
        c = Var("c", "Sci")
        t_ab = kern.assume(eq("Sci", a, b))
        t_bc = kern.assume(eq("Sci", b, c))
        t_cb = kern.assume(eq("Sci", c, b))
        with pytest.raises(KernelError):
            kern.trans(t_ab, t_cb)  # ends at b, not c
        assert kern.trans(t_ab, t_bc).concl == eq("Sci", a, c)

    def test_impl_intro_rejects_a_premise_not_in_hypotheses(self) -> None:
        kern = _small_kernel()
        p = Var("p", "Bool")
        q = Var("q", "Bool")
        truth_q = kern.assume(q)
        with pytest.raises(KernelError):
            kern.impl_intro(p, truth_q)  # p was never assumed

    def test_forall_intro_rejects_a_variable_free_in_a_hypothesis(self) -> None:
        kern = _small_kernel()
        x = Var("x", "Sci")
        y = Var("y", "Sci")
        depends = kern.assume(eq("Sci", x, y))
        with pytest.raises(KernelError):
            kern.forall_intro(x, depends)

    def test_eq_mp_rejects_a_non_implication(self) -> None:
        kern = _small_kernel()
        p = Var("p", "Bool")
        with pytest.raises(KernelError):
            kern.eq_mp(kern.assume(p), kern.assume(p))


class TestTheProof:
    @pytest.fixture(scope="class")
    def result(self) -> dict:
        return ck.prove_theorem7()

    def test_the_statement_is_the_contract(self, result: dict) -> None:
        assert result["statement"].startswith(f"{ck.CONTRACT_ID}:")
        assert result["contract_id"] == ck.CONTRACT_ID

    def test_the_conclusion_is_the_exact_manuscript_statement(
        self, result: dict
    ) -> None:
        assert result["conclusion_rendered"] == EXACT_CONCLUSION

    def test_every_step_is_counted(self, result: dict) -> None:
        log = result["proof_log"]
        assert result["kernel_rule_applications"] == len(log)
        assert sum(result["kernel_rules_histogram"].values()) == len(log)
        assert set(result["kernel_rules_histogram"]) <= {
            "absurd", "and_intro", "and_left", "and_right", "assume",
            "bool_cases", "congr", "eq_mp", "forall_inst", "forall_intro",
            "impl_intro", "mp", "or_elim", "refl", "symm", "trans",
        }
        assert {step["id"] for step in log} == set(range(len(log)))

    def test_replay_from_nothing_reproduces_the_conclusion(
        self, result: dict
    ) -> None:
        replay = result["replay"]
        assert replay["replayed"] is True
        assert replay["conclusion_matches"] is True
        assert replay["residual_hypotheses_within_theory"] is True
        assert result["residual_hypotheses"] > 0  # the theory axioms remain open


class TestTheCommittedArtifact:
    """Re-check the JSON that ships with the paper, not a fresh proof."""

    @pytest.fixture(scope="class")
    def machine(self) -> dict:
        return json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def _replay(self, log: list, expected: Term):
        kern = _small_kernel()
        v = ck._Vocab()
        allowed = frozenset(formula for _, formula in ck._theory_axioms(v))
        return kern.replay(log, expected, allowed)

    def test_the_committed_proof_replays(self, machine: dict) -> None:
        from orion.programme.lcf_kernel import term_from_json

        expected = term_from_json(machine["proof_log"][-1]["concl"])
        final = self._replay(machine["proof_log"], expected)
        assert final.concl.render() == machine["conclusion_rendered"]
        assert final.concl.render() == EXACT_CONCLUSION
        assert len(final.hyps) == machine["residual_hypotheses"]
        assert machine["kernel_rule_applications"] == len(machine["proof_log"])

    def test_a_mutated_payload_is_detected(self, machine: dict) -> None:
        from orion.programme.lcf_kernel import term_from_json

        tampered = copy.deepcopy(machine["proof_log"])
        expected = term_from_json(machine["proof_log"][-1]["concl"])
        # Rewrite one recorded payload term to a different but well-formed one:
        # the re-executed rule must disagree with what was serialized.
        for step in tampered:
            if step["rule"] == "assume" and step["payload"]:
                step["payload"][0] = machine["proof_log"][-1]["concl"]
                break
        with pytest.raises(KernelError):
            self._replay(tampered, expected)

    def test_a_rerouted_input_is_detected(self, machine: dict) -> None:
        from orion.programme.lcf_kernel import term_from_json

        tampered = copy.deepcopy(machine["proof_log"])
        expected = term_from_json(machine["proof_log"][-1]["concl"])
        rerouted = [
            step for step in tampered
            if step["rule"] == "mp" and len(step["inputs"]) == 2
        ]
        assert rerouted, "no mp step to reroute"
        rerouted[0]["inputs"] = [0, 0]
        with pytest.raises(KernelError):
            self._replay(tampered, expected)

    def test_a_swapped_final_conclusion_is_detected(self, machine: dict) -> None:
        from orion.programme.lcf_kernel import ForAll, term_from_json

        expected = term_from_json(machine["proof_log"][-1]["concl"])
        # Same shape, different bound variable: the replayed proof still ends
        # at the recorded conclusion, so expecting an alpha-variant must fail.
        wrong = ForAll(Var("E2", "Env"), expected.args[0])
        with pytest.raises(KernelError):
            self._replay(machine["proof_log"], wrong)

    def test_the_z3_cross_check_is_recorded_as_proved(self, machine: dict) -> None:
        cross = machine["z3_cross_check"]
        assert cross["outcome"] == "PROVED"
        assert cross["name"] == "THEOREM7_KERNEL_STATEMENT_UNDER_Z3"
        assert "subset of the kernel's theory" in cross["statement"]

    def test_the_tcb_is_stated(self, machine: dict) -> None:
        assert "ORION-authored Python" in machine["trusted_computing_base"]
        assert machine["assumed_not_derived"]


class TestTheCrossCheck:
    def test_z3_refutes_the_negation(self) -> None:
        # A bare equality against "PROVED" makes a contended host indistinguishable
        # from a countermodel, so a slow runner retracts Theorem 7 without saying so
        # (#2011). The shared helper fails on both and reports which one happened.
        from orion.programme.mechanized import ProofResult, assert_all_discharged

        result = ck.z3_cross_check()
        assert isinstance(result, ProofResult)
        assert_all_discharged([result], what="the P6 commutation-kernel Z3 cross-check")


class TestTheBinding:
    def test_the_cross_artifact_audit_passes(self) -> None:
        import importlib.util

        checker_path = (
            REPO_ROOT
            / "papers/orion-16-formal-epistemic-structures-and-mechanics"
            / "formal/check_commutation_kernel_binding_v1.py"
        )
        spec = importlib.util.spec_from_file_location(
            "check_commutation_kernel_binding_v1", checker_path
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        report = module.audit()
        assert report["status"] == "PASS", report["errors"]
        assert report["contract_id"] == ck.CONTRACT_ID

    def test_the_old_smt_contract_stays_bound(self) -> None:
        import importlib.util

        checker_path = (
            REPO_ROOT
            / "papers/orion-16-formal-epistemic-structures-and-mechanics"
            / "formal/check_commutation_contract_binding_v1.py"
        )
        spec = importlib.util.spec_from_file_location(
            "check_commutation_contract_binding_v1", checker_path
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        report = module.audit()
        assert report["status"] == "PASS", report["errors"]


class TestScope:
    def test_the_report_states_what_it_does_not_license(self) -> None:
        report = ck.build_report()
        text = " ".join(str(item) for item in report["not_licensed"])
        assert "Lean" in text
        assert "independent" in text
        assert report["kernel_rule_applications"] > 0
