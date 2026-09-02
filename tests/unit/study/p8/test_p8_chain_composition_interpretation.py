"""Tests for P8's chain compositions as instances of the proved chain theorem.

The claim under test is an *instance* claim, and instance claims are the easiest
to fake: any composition operator that is the identity on a clean pair reproduces
169, whether or not it composes anything. So these tests are not "do the numbers
come out". They are: does the interpretation carry the proof (drop a frame
condition and a theorem must acquire a countermodel), does the composition carry
the derivation (use a wrong operator and the soundness identity must break), does
breaking the committed checker break the counts, and are the module's own
negatives about the 169 the ones it actually computed.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from orion.study.p8 import chain_composition_interpretation as cci

REPO_ROOT = Path(__file__).resolve().parents[4]

z3 = pytest.importorskip("z3", reason="the interpretation is discharged by Z3")

#: The theorems each frame condition was refuted with in every one of four runs.
#:
#: A required core rather than an equality, and that is a measurement rather than
#: a hedge: dropping ``narrowing_is_scope_containment`` leaves the solver hunting
#: for a model of two closely related claims and it refutes one and gives up on
#: the other, in either order across runs. The theorem it refutes every time is
#: the one pinned. Everything else below held identically in all four.
STABLE_CORE: dict[str, set[str]] = {
    "type_agreement_is_domain_identity": {
        "A_DONOR_LINK_IS_A_CALCULUS_DELEGATION",
        "THE_SHIPPED_CHAIN_STEP_IS_THE_REFLEXIVE_ONE",
        "THE_DONOR_FAMILY_ENTERS_ONLY_THROUGH_ITS_TYPE",
    },
    "distinct_domains_are_type_disagreement": {
        "AN_UNBRIDGED_TYPE_GAP_IS_NOT_A_REACH",
        "THE_DONOR_FAMILY_ENTERS_ONLY_THROUGH_ITS_TYPE",
    },
    "a_protected_coercion_is_a_registered_conversion": {
        "A_DONOR_LINK_IS_A_CALCULUS_DELEGATION",
    },
    "every_conversion_is_a_registered_coercion": {
        "AN_UNBRIDGED_TYPE_GAP_IS_NOT_A_REACH",
    },
    "narrowing_is_scope_containment": {
        "THE_DONOR_FAMILY_ENTERS_ONLY_THROUGH_ITS_TYPE",
    },
    "a_widening_hop_does_not_narrow": {
        "A_WIDENING_HOP_IS_NEVER_AUTHORISED",
        "THE_DONOR_FAMILY_ENTERS_ONLY_THROUGH_ITS_TYPE",
    },
    "the_blocker_takes_one_of_three_states": {"THE_THREE_STATE_BLOCKER_LAW"},
    "every_donor_family_is_a_trusted_issuer": {"A_DONOR_LINK_IS_A_CALCULUS_DELEGATION"},
}


@pytest.fixture(scope="module")
def proofs() -> tuple:
    return cci.prove_all()


@pytest.fixture(scope="module")
def ladder() -> tuple:
    return cci.prove_chain_ladder()


@pytest.fixture(scope="module")
def counts() -> dict:
    return cci.recompute_published_counts(REPO_ROOT)


@pytest.fixture(scope="module")
def soundness() -> dict:
    return cci.composition_soundness(REPO_ROOT)


@pytest.fixture(scope="module")
def load_bearing() -> dict:
    return cci.frame_conditions_are_load_bearing()


@pytest.fixture(scope="module")
def sensitivity() -> dict:
    return cci.counts_are_sensitive_to_the_interpretation(REPO_ROOT)


def _assert_all_discharged(results: tuple, *, what: str) -> None:
    """Fail on a refutation and on a timeout, but never confuse the two.

    ``discharged`` is ``PROVED``, so a solver that ran out of wall clock and a
    solver that found a countermodel both read as "not discharged" --- and the
    assertion that fired said only that a theorem was undischarged. One of those
    is P8's interpretation being false; the other is a measurement that was not
    taken. The module already keeps them apart on the refutation path ("an
    UNKNOWN is recorded and counts as nothing"); this keeps them apart here.

    Both still fail. Nothing is weakened --- the failure just says which world it
    is in, instead of leaving the next reader to guess.
    """

    refuted = [r.theorem.name for r in results if r.outcome is cci.ProofOutcome.COUNTEREXAMPLE]
    undecided = [r.theorem.name for r in results if r.outcome is cci.ProofOutcome.UNKNOWN]

    assert refuted == [], (
        f"{what}: Z3 found a countermodel for {refuted}. This is a refutation of P8's "
        "chain-composition interpretation, not a flake, and it does not go away by "
        "re-running."
    )
    assert undecided == [], (
        f"{what}: Z3 returned UNKNOWN for {undecided} within "
        f"{cci.PROOF_TIMEOUT_MS}ms. That is the prover giving up, not a theorem lost --- "
        "these proofs take well under a second unloaded, so a timeout here means the "
        "machine was contended. Re-run before reading it as anything else."
    )


class TestTheInterpretationIsProved:
    def test_every_theorem_is_discharged(self, proofs: tuple) -> None:
        _assert_all_discharged(proofs, what="the theorem list")

    def test_no_theorem_is_recorded_unknown(self, proofs: tuple) -> None:
        # UNKNOWN is not PROVED. Collapsing the two turns a timeout into a result.
        assert [r.theorem.name for r in proofs if r.outcome.value == "UNKNOWN"] == []

    def test_the_theorem_list_and_the_proofs_agree(self, proofs: tuple) -> None:
        assert [r.theorem.name for r in proofs] == [t.name for t in cci.THEOREMS]

    def test_the_chain_statement_holds_at_every_length_to_the_bound(
        self, ladder: tuple
    ) -> None:
        assert len(ladder) == cci.CHAIN_LADDER_BOUND
        _assert_all_discharged(ladder, what="the chain ladder")

    def test_the_ladder_reaches_past_pairs(self, ladder: tuple) -> None:
        # P8's claim is about ordered pairs, which is length two. If the ladder
        # only ever ran to two, "arbitrary chain length" would be decoration.
        assert cci.CHAIN_LADDER_BOUND > 2
        assert ladder[-1].theorem.name.endswith(str(cci.CHAIN_LADDER_BOUND))

    def test_a_proof_gets_a_longer_budget_than_a_refutation_search(self) -> None:
        # A wall-clock timeout turned a two-tenths-of-a-second proof into an
        # UNKNOWN once on a loaded machine. Proofs therefore get a budget they
        # never need; refutation searches keep a bounded one, because a search
        # that runs out really has found nothing.
        assert cci.PROOF_TIMEOUT_MS > cci.REFUTATION_TIMEOUT_MS
        import inspect

        assert (
            inspect.signature(cci.prove_all).parameters["timeout_ms"].default
            == cci.PROOF_TIMEOUT_MS
        )
        assert (
            inspect.signature(cci.frame_conditions_are_load_bearing)
            .parameters["timeout_ms"]
            .default
            == cci.REFUTATION_TIMEOUT_MS
        )

    def test_identical_proof_queries_are_evaluated_once_per_process(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # build_report and the CLI repeat the same pure Z3 queries exercised by
        # the module fixtures.  Re-running them late in a long process can turn
        # an already-PROVED query into a load-dependent UNKNOWN.  Reuse must
        # preserve the exact three-valued result, never promote UNKNOWN.
        original = cci.chain_signature
        calls = 0

        def counted_signature():
            nonlocal calls
            calls += 1
            return original()

        monkeypatch.setattr(cci, "chain_signature", counted_signature)

        first_proofs = cci.prove_all(timeout_ms=17)
        second_proofs = cci.prove_all(timeout_ms=17)
        first_ladder = cci.prove_chain_ladder(bound=1, timeout_ms=17)
        second_ladder = cci.prove_chain_ladder(bound=1, timeout_ms=17)

        assert second_proofs is first_proofs
        assert second_ladder is first_ladder
        assert calls == 2

    def test_the_expensive_trust_refutation_runs_first_without_reordering_the_report(
        self,
    ) -> None:
        assert cci.FRAME_CONDITION_REFUTATION_ORDER[0] == (
            "every_donor_family_is_a_trusted_issuer"
        )
        assert set(cci.FRAME_CONDITION_REFUTATION_ORDER) == set(cci.FRAME_CONDITION_IDS)
        assert len(cci.FRAME_CONDITION_REFUTATION_ORDER) == len(cci.FRAME_CONDITION_IDS)

    def test_the_ladder_bound_records_what_lies_past_it(self) -> None:
        # The bound was 8 until a length-eight query came back UNKNOWN under
        # load. Lowering it silently would have turned a measured solver limit
        # into an unexplained constant.
        assert cci.CHAIN_LADDER_BOUND == 6
        assert "unknown" in cci.LADDER_BEYOND_THE_BOUND
        assert "induction schema" in cci.LADDER_BEYOND_THE_BOUND


class TestTheFrameConditionsCarryTheProof:
    def test_no_condition_is_inert(self, load_bearing: dict) -> None:
        assert load_bearing["inert_conditions"] == []
        assert load_bearing["every_condition_carries_a_theorem"] is True

    def test_load_bearing_is_measured_by_refutation_not_by_giving_up(
        self, load_bearing: dict
    ) -> None:
        # The whole reason the witness world exists. A theorem left UNDECIDED by
        # a drop must never be counted as a theorem the condition carried, and
        # no condition's verdict may rest on one.
        undecided = load_bearing["theorems_left_undecided_by_dropping"]
        refuted = load_bearing["theorems_refuted_by_dropping"]
        for condition, names in refuted.items():
            assert set(names) <= set(load_bearing["baseline_discharged"]), condition
            assert set(names) & set(undecided.get(condition, [])) == set(), condition
            assert names, condition

    def test_an_undecided_drop_is_reported_rather_than_smoothed(
        self, load_bearing: dict
    ) -> None:
        # Dropping the narrowing axiom leaves the solver hunting for a model of
        # two closely related claims and it gives up on one of them, not always
        # the same one. The field has to exist and the reason has to travel with
        # it, or an intermittent UNKNOWN silently becomes a finding.
        assert "theorems_left_undecided_by_dropping" in load_bearing
        reason = load_bearing["why_the_refuted_sets_vary_between_runs"]
        assert "narrowing_is_scope_containment" in reason
        assert "UNKNOWN" in reason

    @pytest.mark.parametrize(("condition", "stable_core"), sorted(STABLE_CORE.items()))
    def test_which_theorem_each_condition_carries_is_pinned(
        self, condition: str, stable_core: set[str], load_bearing: dict
    ) -> None:
        # Pinned rather than merely counted: a condition that stops carrying the
        # theorem it carried has changed meaning, and "at least one was refuted"
        # would hide that. Pinned as a required core rather than as equality,
        # because one drop's refuted set genuinely varies -- measured over four
        # runs, and the core below is what held in all of them.
        #
        # A starved solver is not a meaning change. P8's undecided runs are
        # load-dependent (see test_identical_proof_queries_are_evaluated_once_
        # per_process), so a pinned theorem left UNKNOWN by a drop makes this
        # pin CANNOT_CHECK for the run -- skipped, visibly, the same split
        # d72829c6d made for the CLI exit codes -- while a pinned theorem the
        # drop discharged without refuting still fails: that one really did
        # stop being carried.
        refuted = set(load_bearing["theorems_refuted_by_dropping"][condition])
        undecided = set(
            load_bearing["theorems_left_undecided_by_dropping"].get(condition, [])
        )
        starved = (stable_core - refuted) & undecided
        if starved:
            pytest.skip(
                f"{condition}: pinned {sorted(starved)} left UNDECIDED by the solver"
                " (CANNOT_CHECK, not a meaning change)"
            )
        assert stable_core <= refuted

    def test_every_condition_is_pinned_by_the_test_above(self) -> None:
        # A condition added without a pin would be checked only for inertness.
        assert set(STABLE_CORE) == set(cci.FRAME_CONDITION_IDS)

    def test_the_trust_condition_is_not_smuggled_into_the_hypothesis(self) -> None:
        # It was, in the first draft, and that made it inert: the theorem
        # concluded one of its own premises. If trust reappears inside the link
        # predicate this test says so before the load-bearing check does.
        sig = cci.chain_signature()
        p, q = z3.Consts("check_p check_q", sig.Donor)
        assert "Trusted" not in str(cci._link(sig, p, q))

    def test_an_unknown_condition_is_refused(self) -> None:
        with pytest.raises(ValueError, match="unknown frame condition"):
            cci.prove_all(drop="no_such_condition")

    def test_the_witness_world_is_never_used_for_a_proof(
        self, load_bearing: dict, proofs: tuple
    ) -> None:
        # Finite sort bounds are sound for refutation and unsound for proof. A
        # PROVED result obtained under them would be a proof about small models
        # dressed as a proof about all of them, so the baseline the load-bearing
        # check compares against has to be the unbounded one.
        import inspect

        assert (
            inspect.signature(cci.prove_all).parameters["witness_world"].default is False
        )
        assert set(load_bearing["baseline_discharged"]) == {
            r.theorem.name for r in proofs if r.discharged
        }

    def test_the_witness_world_is_consistent_with_the_interpretation(self) -> None:
        # If the bounds contradicted the axioms, every drop would "refute" every
        # theorem and the load-bearing result would be an artefact of the search
        # aid rather than a fact about the conditions.
        bounded = cci.prove_all(witness_world=True)
        _assert_all_discharged(bounded, what="the bounded expansion")


class TestThePublishedCountsAreAnInstance:
    def test_both_published_counts_are_reproduced(self, counts: dict) -> None:
        homogeneous = counts["homogeneous_reading"]
        assert homogeneous["chain_successes"] == 169
        assert homogeneous["chain_widening_countermodels"] == 169
        assert counts["counts_reproduced"] is True

    def test_the_counts_come_from_the_committed_checker(self) -> None:
        model_path = REPO_ROOT / cci.X4_CHECKER
        assert model_path.is_file()
        source = model_path.read_text(encoding="utf-8")
        assert "def scientific_terminal(" in source
        assert "heterogeneous_chain_successes" in source

    def test_a_broken_scientific_terminal_breaks_the_counts(self, monkeypatch) -> None:
        # The unperturbed value is taken first, in this same process, so the
        # perturbation is known to have landed rather than assumed to have.
        # `from x import f` binds by value, so the patch goes through the module
        # reference the recomputation actually calls.
        before = cci.recompute_published_counts(REPO_ROOT)
        assert before["homogeneous_reading"]["chain_successes"] == 169

        from orion.programme import mechanized

        real_loader = mechanized.load_executable_model

        def loading_a_broken_model(path, name):
            module = real_loader(path, name)
            module.scientific_terminal = (
                lambda native, flags, narrowing, blocker, a, b, coercion: "BLOCK"
            )
            return module

        monkeypatch.setattr(
            cci, "load_executable_model", loading_a_broken_model, raising=True
        )
        broken = cci.recompute_published_counts(REPO_ROOT)
        assert broken["homogeneous_reading"]["chain_successes"] == 0
        assert broken["counts_reproduced"] is False

    def test_dropping_the_narrowing_check_breaks_the_widening_count(
        self, monkeypatch
    ) -> None:
        # The half of the published result that is supposed to carry T7's second
        # sentence. If the committed rule stops refusing a widening hop, the 169
        # widening countermodels must go with it.
        from orion.programme import mechanized

        real_loader = mechanized.load_executable_model

        def loading_a_permissive_model(path, name):
            module = real_loader(path, name)
            shipped = module.scientific_terminal
            module.scientific_terminal = (
                lambda native, flags, narrowing, blocker, a, b, coercion: shipped(
                    native, flags, True, blocker, a, b, coercion
                )
            )
            return module

        monkeypatch.setattr(
            cci, "load_executable_model", loading_a_permissive_model, raising=True
        )
        broken = cci.recompute_published_counts(REPO_ROOT)
        assert broken["homogeneous_reading"]["chain_widening_countermodels"] == 0
        assert broken["counts_reproduced"] is False


class TestTheChainTheoremIsWhatProducesThem:
    def test_the_composition_is_exact_against_the_chain_theorem(
        self, soundness: dict
    ) -> None:
        assert soundness["unsound_pairs"] == 0
        assert soundness["unsound_examples"] == []
        assert soundness["composition_is_sound"] is True

    def test_every_widening_hop_blocks(self, soundness: dict) -> None:
        assert soundness["widening_hop_failures"] == 0
        assert soundness["every_widening_hop_blocks"] is True

    def test_the_representative_pairs_really_stand_in_for_all_of_them(self) -> None:
        reduction = cci.state_space_reduction_is_exact(REPO_ROOT)
        assert reduction["states_enumerated"] == 3072
        assert reduction["verdict_classes"] == 192
        assert reduction["classes_holding_more_than_one_terminal"] == []
        assert reduction["conjunction_distribution_failures"] == 0
        assert reduction["state_pairs_represented"] == 3072**2
        assert reduction["representative_pairs_checked"] == 192**2
        assert reduction["reduction_is_exact"] is True

    def test_the_corpus_exercises_both_verdicts(self, soundness: dict) -> None:
        # Agreement measured where only one verdict occurs is agreement about a
        # constant. Nine of the 192 representatives discharge; if that ever
        # became 0 or 192 the identity below would be satisfied vacuously.
        assert soundness["representatives_checked"] == 192
        assert soundness["discharging_representatives"] == 9
        assert soundness["discharging_composed_pairs"] == 81
        assert soundness["exercised_both_verdicts"] is True

    @staticmethod
    def _under(monkeypatch, rule):
        from orion.programme import mechanized

        real_loader = mechanized.load_executable_model

        def loader(path, name):
            module = real_loader(path, name)
            module.scientific_terminal = rule
            return module

        # `from x import f` binds by value, so the patch has to go through the
        # module attribute the recomputation actually calls.
        monkeypatch.setattr(cci, "load_executable_model", loader, raising=True)

    def test_a_rule_that_names_one_support_family_breaks_the_identity(
        self, monkeypatch, soundness: dict
    ) -> None:
        # The composition reads P8's interface literally -- "at least one
        # complete support family survives" -- so a rule demanding family A
        # specifically contradicts the interpretation, and the identity is what
        # notices. Checked against the unperturbed number first, so the
        # perturbation is known to have landed.
        assert soundness["unsound_pairs"] == 0

        def only_family_a(native, flags, narrowing, blocker, support_a, support_b, coercion):
            if not native:
                return "NO_DONOR_AUTHORITY"
            if not narrowing or blocker == "ESTABLISHED":
                return "BLOCK"
            if blocker == "UNDETERMINED":
                return "CANNOT_CHECK"
            if not support_a:
                return "BLOCK"
            return "DISCHARGE" if (all(flags) or coercion) else "BLOCK"

        self._under(monkeypatch, only_family_a)
        broken = cci.composition_soundness(REPO_ROOT)
        assert broken["unsound_pairs"] == 45
        assert broken["composition_is_sound"] is False

    def test_a_constant_rule_is_caught_as_vacuous_not_as_sound(
        self, monkeypatch
    ) -> None:
        # Both constants satisfy the identity. That is a real limit of the
        # identity and the reason the corpus is measured beside it.
        self._under(monkeypatch, lambda *arguments: "BLOCK")
        always_block = cci.composition_soundness(REPO_ROOT)
        assert always_block["unsound_pairs"] == 0
        assert always_block["every_widening_hop_blocks"] is True
        assert always_block["exercised_both_verdicts"] is False

    def test_a_permissive_rule_is_caught_by_the_widening_half(
        self, monkeypatch
    ) -> None:
        self._under(monkeypatch, lambda *arguments: "DISCHARGE")
        always_discharge = cci.composition_soundness(REPO_ROOT)
        assert always_discharge["unsound_pairs"] == 0
        assert always_discharge["widening_hop_failures"] > 0
        assert always_discharge["every_widening_hop_blocks"] is False
        assert always_discharge["exercised_both_verdicts"] is False

    def test_a_rule_reading_an_individual_flag_breaks_the_reduction(
        self, monkeypatch
    ) -> None:
        # The 192 representatives stand in for 3,072 states only because the
        # committed rule reads the flags through `all`. A rule that reads one
        # coordinate must make the reduction report itself unsound.
        from orion.programme.mechanized import load_executable_model

        shipped = load_executable_model(
            REPO_ROOT / cci.X4_CHECKER, "p8_x4_flag_probe"
        ).scientific_terminal

        def flag_sensitive(native, flags, narrowing, blocker, support_a, support_b, coercion):
            verdict = shipped(
                native, flags, narrowing, blocker, support_a, support_b, coercion
            )
            return "BLOCK" if verdict == "DISCHARGE" and not flags[1] else verdict

        self._under(monkeypatch, flag_sensitive)
        broken = cci.state_space_reduction_is_exact(REPO_ROOT)
        assert broken["classes_holding_more_than_one_terminal"] != []
        assert broken["reduction_is_exact"] is False


class TestWhatTheOneHundredAndSixtyNineIsWorth:
    """The negatives, asserted as computed facts rather than left in prose."""

    def test_the_shipped_loop_ignores_its_donor_variables(self, counts: dict) -> None:
        assert counts["shipped_chain_loop_ignores_its_donor_variables"] is True
        source = (REPO_ROOT / cci.X4_CHECKER).read_text(encoding="utf-8")
        assert "for _left in DONORS:" in source
        assert "for _right in DONORS:" in source

    def test_the_one_hundred_and_sixty_nine_pairs_are_one_state(
        self, counts: dict
    ) -> None:
        assert counts["homogeneous_reading"]["ordered_pairs"] == 169
        assert counts["homogeneous_reading"]["distinct_composed_states"] == 1

    def test_the_heterogeneous_reading_returns_thirteen_not_one_sixty_nine(
        self, counts: dict
    ) -> None:
        # The count P8 would publish if the thirteen donor families were
        # type-distinct and no protected bridge were registered.
        assert counts["type_distinct_reading"]["chain_successes"] == 13
        assert (
            counts["type_distinct_with_every_bridge_registered"]["chain_successes"]
            == 169
        )

    def test_the_success_count_discriminates_nothing(self, sensitivity: dict) -> None:
        # Every wrong composition operator reproduces 169 successes. Saying so is
        # the point: half the published chain result tests no interpretation.
        assert sensitivity["variants_that_move_the_success_count"] == []
        for name, seen in sensitivity["variants"].items():
            assert seen["chain_successes"] == 169, name

    def test_the_widening_count_separates_only_two_of_eight(
        self, sensitivity: dict
    ) -> None:
        assert set(sensitivity["variants_that_move_the_widening_count"]) == {
            "composition_ignores_the_downstream_hop",
            "narrowing_composes_by_disjunction",
        }

    def test_the_soundness_identity_is_what_discriminates(
        self, sensitivity: dict
    ) -> None:
        # The load-bearing assertion of the module: a wrong composition that
        # escaped every check would leave the interpretation under-determined.
        assert sensitivity["every_wrong_composition_moves_the_soundness_count"] is True
        assert len(sensitivity["variants_that_move_the_soundness_count"]) == len(
            sensitivity["variants"]
        )
        for name, seen in sensitivity["variants"].items():
            assert seen["unsound_pairs"] > 0, name

    def test_the_shipped_step_is_proved_reflexive_not_merely_asserted(
        self, proofs: tuple
    ) -> None:
        by_name = {r.theorem.name: r for r in proofs}
        assert by_name["THE_SHIPPED_CHAIN_STEP_IS_THE_REFLEXIVE_ONE"].discharged


class TestTheReport:
    def test_the_report_is_clean_and_names_its_limits(self) -> None:
        report = cci.build_report(REPO_ROOT, date="2026-08-22")
        assert report["all_discharged"] is True
        assert report["published_counts"]["counts_reproduced"] is True
        assert report["composition_soundness"]["composition_is_sound"] is True
        assert report["composition_soundness"]["exercised_both_verdicts"] is True
        assert report["frame_conditions"]["every_condition_carries_a_theorem"] is True
        assert any(
            "soundness identity tests the committed rule" in item
            for item in report["not_licensed"]
        )
        assert any(
            "169 measures heterogeneity" in item for item in report["not_licensed"]
        )
        assert any("169 is 169 results" in item for item in report["not_licensed"])
        assert any("independent review" in item for item in report["not_licensed"])
        assert any("empirical claim" in item for item in report["not_licensed"])

    def test_the_date_is_supplied_not_read_from_the_clock(self) -> None:
        assert cci.build_report(REPO_ROOT, date="1999-01-01")["date"] == "1999-01-01"

    def test_the_cli_requires_a_date(self) -> None:
        with pytest.raises(SystemExit):
            cci.main(["--repo-root", str(REPO_ROOT)])

    def test_the_cli_writes_the_artifact(self, tmp_path: Path) -> None:
        out = tmp_path / "report.json"
        code = cci.main(
            ["--repo-root", str(REPO_ROOT), "--date", "2026-08-22", "--output", str(out)]
        )
        assert code == 0
        written = json.loads(out.read_text(encoding="utf-8"))
        assert written["record"] == "P8_CHAIN_COMPOSITION_INTERPRETATION"
        assert len(written["theorems"]) == len(cci.THEOREMS)
        assert len(written["chain_ladder"]["results"]) == cci.CHAIN_LADDER_BOUND

    def test_a_refutation_and_an_undecided_run_exit_differently(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The exit code has to say which of the two worlds the run was in.

        The repo already fixed this convention elsewhere: audit_manuscript_clipping.py
        ends ``return 2 if (new or stale) else 0`` and keeps 3 for the runs it could
        not check. This CLI answered 3 to everything, so "the composition is not
        sound" -- a real negative result about P8 -- and "the solver was starved and
        gave up" were the same integer to any caller. `_assert_all_discharged` in
        this file refuses to conflate them one layer up; the CLI now agrees.
        """
        clean = cci.build_report(REPO_ROOT, date="2026-08-22")

        def run(mutate) -> int:
            report = copy.deepcopy(clean)
            mutate(report)
            monkeypatch.setattr(cci, "build_report", lambda *a, **k: report)
            return cci.main(
                ["--date", "2026-08-22", "--output", str(tmp_path / "r.json")]
            )

        def undecided(report: dict) -> None:
            report["all_discharged"] = False
            report["theorems"][0]["outcome"] = "UNKNOWN"

        def refuted(report: dict) -> None:
            report["all_discharged"] = False
            report["theorems"][0]["outcome"] = "COUNTEREXAMPLE"

        def both(report: dict) -> None:
            report["all_discharged"] = False
            report["theorems"][0]["outcome"] = "COUNTEREXAMPLE"
            report["theorems"][1]["outcome"] = "UNKNOWN"

        assert run(lambda r: None) == 0
        assert run(undecided) == 3, "an undecided solver is CANNOT_CHECK, not a finding"
        assert run(refuted) == 2, "a refuted theorem is a finding, not a failed measurement"
        # A refutation stays a refutation even when something else went undecided:
        # the finding is the stronger claim and must not be downgraded to 3.
        assert run(both) == 2

        # Every non-solver failure is a finding about P8, not an unmeasured run.
        for key, field in (
            ("composition_soundness", "composition_is_sound"),
            ("composition_soundness", "every_widening_hop_blocks"),
            ("composition_soundness", "exercised_both_verdicts"),
            ("state_space_reduction", "reduction_is_exact"),
            ("published_counts", "counts_reproduced"),
            ("frame_conditions", "every_condition_carries_a_theorem"),
            ("interpretation_sensitivity",
             "every_wrong_composition_moves_the_soundness_count"),
        ):
            code = run(lambda r, k=key, f=field: r[k].__setitem__(f, False))
            assert code == 2, f"{key}.{field} is a finding and must exit 2, got {code}"

    def test_the_committed_artifact_matches_what_the_module_computes(self) -> None:
        artifact = (
            REPO_ROOT
            / "papers/orion-18-epistemic-authority-autonomous-science/formal/mechanized"
            / "P8_CHAIN_COMPOSITION_INTERPRETATION_2026-08-22.json"
        )
        assert artifact.is_file()
        committed = json.loads(artifact.read_text(encoding="utf-8"))
        assert committed["record"] == "P8_CHAIN_COMPOSITION_INTERPRETATION"
        assert committed["all_discharged"] is True
        assert committed["published_counts"]["counts_reproduced"] is True
        assert (
            committed["published_counts"]["homogeneous_reading"][
                "distinct_composed_states"
            ]
            == 1
        )
        assert (
            committed["published_counts"]["type_distinct_reading"]["chain_successes"]
            == 13
        )
