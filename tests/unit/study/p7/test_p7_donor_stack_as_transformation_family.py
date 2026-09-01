"""Tests for P7's donor stack read as a transformation family in the proved calculus.

The claim under test is a *corollary* claim, which is the easiest kind to fake:
two procedures that count the same thing agree whether or not one follows from
the other. So these are not "do the numbers come out" tests. They are:

* does the interpretation carry the proof --- drop a frame condition and a named
  theorem must go;
* is the count produced by P7's own committed functions rather than by a rule
  this lane wrote --- break ``compose`` and the count must break with it, and the
  break is verified to have landed before it is relied on;
* does the interpretation carry the count --- and where it does not, is the fact
  that it does not recorded rather than smoothed. Two wrong readings reproduce
  both published numbers exactly, and the test pins which ones and what catches
  them instead.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.study.p7 import donor_stack_as_transformation_family as ds

REPO_ROOT = Path(__file__).resolve().parents[4]

z3 = pytest.importorskip("z3", reason="the interpretation is discharged by Z3")


@pytest.fixture(scope="module")
def proofs() -> tuple:
    return ds.prove_all()


@pytest.fixture(scope="module")
def counts() -> dict:
    return ds.recompute_published_counts(REPO_ROOT)


@pytest.fixture(scope="module")
def load_bearing() -> dict:
    return ds.frame_conditions_are_load_bearing()


@pytest.fixture(scope="module")
def argument_space() -> dict:
    return ds.argument_space_under_the_interpretation(REPO_ROOT)


@pytest.fixture(scope="module")
def sensitivity() -> dict:
    return ds.counts_are_sensitive_to_the_interpretation(REPO_ROOT)


class TestTheInterpretationIsProved:
    def test_every_theorem_is_discharged(self, proofs: tuple) -> None:
        assert [r.theorem.name for r in proofs if not r.discharged] == []

    def test_no_theorem_is_recorded_unknown(self, proofs: tuple) -> None:
        # UNKNOWN is not PROVED. Collapsing the two is how a timeout becomes a
        # result, and every drop run below produces genuine UNKNOWNs, so the
        # distinction is not hypothetical here.
        assert [r.theorem.name for r in proofs if r.outcome.value == "UNKNOWN"] == []

    def test_the_theorem_list_and_the_proofs_agree(self, proofs: tuple) -> None:
        assert [r.theorem.name for r in proofs] == [t.name for t in ds.THEOREMS]

    def test_the_unreached_argument_triples_have_a_theorem_each(self, proofs: tuple) -> None:
        # The six triples the shipped loop never evaluates are exactly the ones
        # where a leg fails. If either of these ever stops being discharged, the
        # blocker's first ask is no longer answered.
        discharged = {r.theorem.name for r in proofs if r.discharged}
        assert "A_LEFT_LEG_THAT_DOES_NOT_CARRY_REFUSES" in discharged
        assert "A_RIGHT_LEG_THAT_DOES_NOT_CARRY_REFUSES" in discharged


class TestTheFrameConditionsCarryTheProof:
    def test_every_condition_loses_at_least_one_theorem_when_dropped(
        self, load_bearing: dict
    ) -> None:
        assert load_bearing["inert_conditions"] == []
        assert load_bearing["every_condition_carries_a_theorem"] is True

    @pytest.mark.parametrize(
        ("condition", "expected_lost"),
        [
            (
                "handoffs_are_never_contract_identities",
                {
                    "UNBRIDGED_DONOR_HANDOFF_REFUSES",
                    "SELF_COMPOSITION_STILL_NEEDS_A_BRIDGE",
                    "DISTINCT_HANDOFFS_CAN_DIFFER_IN_VERDICT",
                    "UNBRIDGED_REFUSAL_IS_NOT_VACUOUS",
                    "NO_IDENTITY_IS_A_DONOR_IS_DERIVED",
                    "COMPOSITE_HANDOFFS_INHERIT_SEPARATION_IS_DERIVED",
                    "A_THREE_DONOR_CHAIN_NEEDS_EVERY_BRIDGE",
                },
            ),
            (
                "distinct_donors_have_distinct_endpoints",
                {"THE_HANDOFF_IDENTIFIES_THE_DONOR_PAIR"},
            ),
            (
                "the_donor_stack_is_inhabited",
                {"UNBRIDGED_REFUSAL_IS_NOT_VACUOUS", "BRIDGED_SUCCESS_IS_NOT_VACUOUS"},
            ),
        ],
    )
    def test_which_theorem_each_condition_carries_is_pinned(
        self, condition: str, expected_lost: set[str], load_bearing: dict
    ) -> None:
        # Pinned rather than merely counted: a condition that starts carrying a
        # different theorem has changed meaning, and a non-empty set of losses
        # would hide that.
        #
        # A bare equality cannot say WHY a theorem left the set. "The condition no
        # longer carries it" and "the countermodel search gave up on it" are
        # different worlds, and only the first is about the science. The module
        # already separates them -- `theorems_the_search_gave_up_on` is right there
        # in the report -- so use it rather than letting a contended runner report a
        # frame condition as carrying one theorem fewer (#2020, fourth of the class).
        refuted = set(load_bearing["theorems_refuted_by_dropping"][condition])
        gave_up = set(load_bearing.get("theorems_the_search_gave_up_on", {}).get(condition, []))

        undecided = (expected_lost - refuted) & gave_up
        assert not undecided, (
            f"dropping {condition!r}: the countermodel search gave up on {sorted(undecided)} "
            f"within {load_bearing['refutation_timeout_ms']}ms across world sizes "
            f"{load_bearing['world_sizes_tried']}. That is the search running out, not the "
            "condition ceasing to carry the theorem -- these searches settle on an unloaded "
            "machine. Re-run before reading anything else into it."
        )
        assert refuted == expected_lost, (
            f"dropping {condition!r} refuted {sorted(refuted)}, expected {sorted(expected_lost)}. "
            "No theorem in the difference is one the search gave up on, so this is a real "
            "change in what the condition carries."
        )

    def test_the_second_condition_is_the_one_the_counts_cannot_see(
        self, load_bearing: dict, sensitivity: dict
    ) -> None:
        # The two facts have to line up or the module is telling two stories.
        # The counts miss `distinct_donors_have_distinct_endpoints`, and the
        # theorem that condition carries is what catches the readings they miss.
        assert load_bearing["theorems_refuted_by_dropping"][
            "distinct_donors_have_distinct_endpoints"
        ] == ["THE_HANDOFF_IDENTIFIES_THE_DONOR_PAIR"]
        assert sensitivity["counts_alone_identify_the_interpretation"] is False

    def test_every_loss_is_a_countermodel_not_a_timeout(self, load_bearing: dict) -> None:
        # The correction. This measurement first counted any theorem that stopped
        # being discharged, which reported ten losses of which eight were UNKNOWN
        # -- and one condition's entire weight was a single UNKNOWN. Every entry
        # must now be backed by an actual countermodel.
        assert "actual countermodel" in load_bearing["criterion"]
        for condition, refuted in load_bearing["theorems_refuted_by_dropping"].items():
            sizes = load_bearing["world_size_the_refutation_needed"][condition]
            assert set(sizes) == set(refuted), condition

    def test_the_unbounded_search_alone_would_have_been_wrong(
        self, load_bearing: dict
    ) -> None:
        # Eight of the ten come back UNKNOWN without a bounded world, and one
        # condition would have shown no refutation at all.
        unknowns = load_bearing["left_unknown_by_the_unbounded_search"]
        assert sum(len(v) for v in unknowns.values()) >= 6
        assert unknowns["distinct_donors_have_distinct_endpoints"] == [
            "THE_HANDOFF_IDENTIFIES_THE_DONOR_PAIR"
        ]

    def test_a_single_small_world_would_also_have_been_wrong(
        self, load_bearing: dict
    ) -> None:
        # The mistake in the other direction, and the reason the sizes escalate.
        # The second condition's countermodel does not exist below five elements,
        # so a search capped at four would have called a load-bearing condition
        # inert.
        needed = load_bearing["world_size_the_refutation_needed"][
            "distinct_donors_have_distinct_endpoints"
        ]
        # Not pinned to exactly five: which size first yields a model varies a
        # little with the solver's search. What is stable, and what matters, is
        # that nothing is found below five -- so a search capped at four would
        # have called a load-bearing condition inert.
        assert needed["THE_HANDOFF_IDENTIFIES_THE_DONOR_PAIR"] >= 5
        assert max(load_bearing["world_sizes_tried"]) >= 5

    def test_a_bounded_world_is_only_used_to_refute(self) -> None:
        # Soundness rests on direction. If a bound ever reached a proof query
        # the theorems would only hold in small universes.
        import inspect

        source = inspect.getsource(ds.prove_all)
        assert "bound" not in source
        assert "REFUTATION_WORLD_SIZES" not in source

    def test_the_drop_budget_has_measured_headroom(self, load_bearing: dict) -> None:
        # No longer what load-bearing is measured by -- that is now a bounded
        # countermodel -- but still worth keeping: it says an unknown in the
        # unbounded drop runs is not a rushed proof.
        #
        # This bound is deliberately weaker than the one it replaces, and the
        # weakening is the fix (#1995). The old form required a 50x headroom
        # (`slowest * 1000 < drop_timeout_ms / 50`), which is a statement about how
        # fast the host is, not about how hard the formula is: the identical proof
        # measured 854ms on a contended CI runner against a 60ms bound and failed,
        # while passing on the runs either side of it. Nothing in the module
        # justified 50 over any other number.
        #
        # What the claim actually needs is that a discharged proof was not truncated
        # by the budget, and 2x headroom is the defensible form of that. The module
        # already computes the ratio in consistent units, so use its number rather
        # than re-deriving it here and risking a seconds/milliseconds slip.
        factor = load_bearing["headroom_factor"]
        assert factor is not None, "no proof was discharged, so no headroom was measured"
        assert factor >= 2.0, (
            f"the slowest discharged proof used more than half the drop budget "
            f"(headroom factor {factor}). Either the budget is too tight to call an "
            f"unbounded UNKNOWN a hard formula, or this host is heavily contended."
        )

    def test_the_bounded_runs_are_timed_separately(self, load_bearing: dict) -> None:
        # The headroom number backs a claim about the drop budget. The bounded
        # refutation runs answer a different question under a different budget,
        # and folding them together would turn the ratio into one between two
        # unrelated things -- which is exactly what broke this test once.
        assert "slowest_bounded_refutation_seconds" in load_bearing
        assert load_bearing["refutation_timeout_ms"] > load_bearing["drop_timeout_ms"]

    def test_an_unknown_condition_is_refused(self) -> None:
        with pytest.raises(ValueError, match="unknown frame condition"):
            ds.prove_all(drop="no_such_condition")

    def test_the_two_inert_candidates_are_derived_and_not_assumed(
        self, load_bearing: dict
    ) -> None:
        # Both were written as frame conditions first and both came back inert.
        # "Came back inert" is re-measured on every run rather than recorded as
        # history: the candidates are added back to the axiom set and nothing
        # may become newly provable. If either reappears as a frame condition,
        # or starts buying a theorem, this says so.
        assert "no_identity_is_a_donor" not in ds.FRAME_CONDITION_IDS
        assert "composite_handoffs_are_separated_too" not in ds.FRAME_CONDITION_IDS
        assert set(ds.CANDIDATE_CONDITION_IDS) == {
            "no_identity_is_a_donor",
            "composite_handoffs_are_separated_too",
        }
        assert load_bearing["theorems_gained_by_adding_the_candidates"] == []
        assert load_bearing["the_rejected_candidates_are_inert"] is True
        names = {t.name for t in ds.THEOREMS}
        assert "NO_IDENTITY_IS_A_DONOR_IS_DERIVED" in names
        assert "COMPOSITE_HANDOFFS_INHERIT_SEPARATION_IS_DERIVED" in names


class TestThePublishedCountsAreAnInstance:
    def test_both_counts_are_reproduced(self, counts: dict) -> None:
        assert counts["composition_successes"] == 25
        assert counts["composition_bridge_countermodels"] == 25
        assert counts["counts_reproduced"] is True
        assert counts["success_failures"] == []
        assert counts["countermodel_failures"] == []

    def test_the_donor_pair_now_enters_the_function(self, counts: dict) -> None:
        # The whole point of the interpretation. Twenty-five distinct hand-offs,
        # one per ordered donor pair, rather than one argument reused.
        assert counts["distinct_handoffs_visited"] == 25

    def test_the_published_counts_still_reach_only_two_triples(self, counts: dict) -> None:
        # This is the honest residue and it is asserted rather than left implicit.
        # Reproducing 25 and 25 needs two uniform registries over an all-carrying
        # stack, so the recomputation reaches (1,1,0) and (1,1,1) and nothing else.
        assert counts["argument_triples_reached"] == [[1, 1, 0], [1, 1, 1]]
        assert counts["argument_triples_possible"] == 8

    def test_the_refinement_multiplier_is_measured_not_asserted(self, counts: dict) -> None:
        # 155 and 1,055 are the other half of P7's artifact and are not this
        # module's subject, but the same question is being asked of the
        # composition rows, so the answer for these is measured rather than
        # claimed: run the committed carries at one donor and at five.
        multiplier = counts["the_refinement_counts_are_a_separate_object"]
        assert multiplier["full_refinement_successes_at_one_donor"] == 31
        assert multiplier["proper_subset_failures_at_one_donor"] == 211
        assert multiplier["full_refinement_successes_at_the_committed_stack"] == 155
        assert multiplier["proper_subset_failures_at_the_committed_stack"] == 1055
        assert multiplier["the_donor_axis_is_a_multiplier"] is True

    def test_the_counts_come_from_the_committed_implementation(self) -> None:
        model_path = REPO_ROOT / ds.EXECUTABLE_MODEL
        assert model_path.is_file()
        source = model_path.read_text(encoding="utf-8")
        assert "def compose(" in source
        assert "def carries(" in source

    def test_a_broken_compose_breaks_the_count(self, monkeypatch) -> None:
        from orion.programme import mechanized

        real_loader = mechanized.load_executable_model
        landed: list[bool] = []

        def loading_a_broken_model(path, name):
            module = real_loader(path, name)
            module.compose = lambda c1, c2, bridge_match: True
            # A perturbation test that passes against an unperturbed object is
            # worthless, and `from x import f` binds by value, so the patch is
            # verified to have landed on the object the count will actually use.
            landed.append(module.compose(True, True, False) is True)
            return module

        monkeypatch.setattr(
            ds, "load_executable_model", loading_a_broken_model, raising=True
        )
        broken = ds.recompute_published_counts(REPO_ROOT)
        assert landed and all(landed), "the perturbation never reached the model"
        assert broken["composition_bridge_countermodels"] == 0
        assert broken["counts_reproduced"] is False

    def test_a_broken_carries_breaks_the_count(self, monkeypatch) -> None:
        from orion.programme import mechanized

        real_loader = mechanized.load_executable_model
        landed: list[bool] = []

        def loading_a_broken_model(path, name):
            module = real_loader(path, name)
            module.carries = lambda native_valid, closure: False
            landed.append(module.carries(True, (True,) * 5) is False)
            return module

        monkeypatch.setattr(
            ds, "load_executable_model", loading_a_broken_model, raising=True
        )
        broken = ds.recompute_published_counts(REPO_ROOT)
        assert landed and all(landed), "the perturbation never reached the model"
        assert broken["composition_successes"] == 0
        assert broken["counts_reproduced"] is False


class TestTheArgumentSpaceTheShippedLoopNeverReaches:
    def test_all_eight_triples_are_reached(self, argument_space: dict) -> None:
        assert argument_space["argument_triples_reached"] == 8
        assert argument_space["unreached"] == []
        assert argument_space["every_triple_reached"] is True

    def test_the_differential_is_informative_not_one_sided(
        self, argument_space: dict
    ) -> None:
        # Agreement on a corpus where every row refuses is agreement about the
        # constant False. Both verdicts have to occur for this to say anything.
        differential = argument_space["differential"]
        assert differential["disagreements"] == []
        assert differential["informative"] is True
        assert 0 < differential["positive_trials"] < differential["trials"]

    def test_a_broken_compose_is_caught_by_the_differential(self) -> None:
        from orion.programme.mechanized import load_executable_model

        model = load_executable_model(
            REPO_ROOT / ds.EXECUTABLE_MODEL, "p7_argument_space_perturbed"
        )
        # Ignore the hand-off entirely: exactly the failure the 25 countermodels
        # are supposed to rule out.
        model.compose = lambda c1, c2, bridge_match: bool(c1 and c2)
        assert model.compose(True, True, False) is True, "the perturbation did not land"
        broken = ds.argument_space_under_the_interpretation(REPO_ROOT, model=model)
        assert broken["differential"]["disagreements"]
        assert broken["differential"]["agreed"] is False


class TestWhatTheCountsCanAndCannotIdentify:
    """The counts pin one frame condition and are blind to the other."""

    def test_the_counts_do_not_identify_the_interpretation(self, sensitivity: dict) -> None:
        assert sensitivity["counts_alone_identify_the_interpretation"] is False
        assert set(sensitivity["wrong_assignments_the_counts_cannot_distinguish"]) == {
            "one_input_and_one_output_contract",
            "one_shared_output_contract",
        }

    def test_every_indistinguishable_reading_is_caught_by_the_handoff_count(
        self, sensitivity: dict
    ) -> None:
        # This is the load-bearing assertion of the module. A reading that
        # escaped both the counts and the theorems would leave the donor
        # indexing genuinely undetermined, which is the terminal's whole subject.
        assert sensitivity["every_indistinguishable_assignment_is_caught_by_a_theorem"] is True
        for name in sensitivity["wrong_assignments_the_counts_cannot_distinguish"]:
            assert sensitivity["variants"][name]["distinct_handoffs_visited"] < 25, name
        assert sensitivity["variants"]["separated_handoffs"]["distinct_handoffs_visited"] == 25

    @pytest.mark.parametrize(
        ("assignment", "expected_countermodels"),
        [
            ("one_shared_contract", 0),
            ("endomorphic_donors", 20),
            ("pipeline_chained", 21),
        ],
    )
    def test_the_countermodel_count_is_the_first_frame_condition(
        self, assignment: str, expected_countermodels: int, sensitivity: dict
    ) -> None:
        # Every reading in which some donor's target contract is some donor's
        # source contract loses countermodels, one per hand-off that matches by
        # equality. 25 countermodels *is* the frame condition, which is why it is
        # not a choice this lane made.
        variant = sensitivity["variants"][assignment]
        assert variant["composition_bridge_countermodels"] == expected_countermodels

    def test_the_success_count_discriminates_no_contract_assignment(
        self, sensitivity: dict
    ) -> None:
        # 25 successes comes out of every reading tried, because a registry that
        # bridges everything satisfies the match test whatever the contracts are.
        for name, variant in sensitivity["variants"].items():
            assert variant["composition_successes"] == 25, name
        assert "Nothing about the contracts" in sensitivity["what_the_success_count_tests"]

    def test_the_discriminating_registry_is_named_and_was_not_shipped(
        self, sensitivity: dict
    ) -> None:
        assert sensitivity["registries_that_would_separate_the_indistinguishable_assignments"]
        assert "P7 shipped neither" in sensitivity["what_pins_the_donor_indexing"]


class TestTheReport:
    def test_the_report_is_clean_and_names_its_limits(self) -> None:
        report = ds.build_report(REPO_ROOT, date="2026-08-22")
        assert report["all_discharged"] is True
        assert report["published_counts"]["counts_reproduced"] is True
        frames = report["frame_conditions"]
        # Two ways this can be False, and they are not the same news. An inert
        # condition is a finding about the axiom and does not go away by
        # re-running; a condition whose countermodel search did not settle is a
        # fact about the search, and this file's own docstring records a
        # load-bearing condition being reported inert for exactly that reason.
        assert frames["inert_conditions"] == [], (
            f"frame conditions carry nothing: {frames['inert_conditions']}. Every "
            "search settled, so this is a finding about the axioms."
        )
        assert frames["conditions_left_undecided"] == [], (
            f"the countermodel search did not settle for {frames['conditions_left_undecided']} "
            f"(gave up on {frames.get('theorems_the_search_gave_up_on')}). That is not a "
            "finding that they are inert --- these searches succeed on an idle machine, so "
            "re-run before reading it as anything else."
        )
        assert frames["every_condition_carries_a_theorem"] is True
        assert report["argument_space"]["every_triple_reached"] is True
        assert any(
            "more than two of compose's eight" in item for item in report["not_licensed"]
        )
        assert any("25 successes tests the interpretation" in item for item in report["not_licensed"])
        assert any("31 " in item and "211 " in item for item in report["not_licensed"])
        assert any("independent review" in item for item in report["not_licensed"])

    def test_the_date_is_supplied_not_read_from_the_clock(self) -> None:
        assert ds.build_report(REPO_ROOT, date="1999-01-01")["date"] == "1999-01-01"

    def test_the_cli_requires_a_date(self) -> None:
        with pytest.raises(SystemExit):
            ds.main(["--repo-root", str(REPO_ROOT)])

    def test_the_cli_writes_the_artifact(self, tmp_path: Path) -> None:
        out = tmp_path / "report.json"
        code = ds.main(
            ["--repo-root", str(REPO_ROOT), "--date", "2026-08-22", "--output", str(out)]
        )
        assert code == 0
        written = json.loads(out.read_text(encoding="utf-8"))
        assert written["record"] == "P7_DONOR_STACK_AS_TRANSFORMATION_FAMILY"
        assert len(written["theorems"]) == len(ds.THEOREMS)

    def test_the_committed_artifact_is_named_and_unchanged(self) -> None:
        # The module claims not to have repaired the committed result. That claim
        # is only meaningful if the file it names is the one still on disk with
        # its literal-argument loop intact.
        committed = REPO_ROOT / ds.EXECUTABLE_MODEL
        source = committed.read_text(encoding="utf-8")
        assert "assert compose(c1, c2, True)" in source
        assert "assert not compose(c1, c2, False)" in source


class TestTheUndecidedDistinctionItself:
    """The CI failure this guards against, exercised directly.

    Run 33511788834 reported the frame condition `handoffs_are_never_contract_identities`
    carrying six theorems instead of seven, on a PR that touches no p7 file. The
    missing one had landed in the search's give-up set. These two cases prove the
    assertion can tell that from a real change, without waiting for a slow runner.
    """

    CONDITION = "handoffs_are_never_contract_identities"
    EXPECTED = {"A", "B"}

    def _assert(self, report: dict) -> None:
        refuted = set(report["theorems_refuted_by_dropping"][self.CONDITION])
        gave_up = set(report.get("theorems_the_search_gave_up_on", {}).get(self.CONDITION, []))
        undecided = (self.EXPECTED - refuted) & gave_up
        assert not undecided, (
            f"dropping {self.CONDITION!r}: the countermodel search gave up on "
            f"{sorted(undecided)} within {report['refutation_timeout_ms']}ms across world "
            f"sizes {report['world_sizes_tried']}. That is the search running out, not the "
            "condition ceasing to carry the theorem."
        )
        assert refuted == self.EXPECTED, (
            f"dropping {self.CONDITION!r} refuted {sorted(refuted)}, expected "
            f"{sorted(self.EXPECTED)}. No theorem in the difference is one the search gave "
            "up on, so this is a real change in what the condition carries."
        )

    def _report(self, refuted: list[str], gave_up: list[str]) -> dict:
        return {
            "theorems_refuted_by_dropping": {self.CONDITION: refuted},
            "theorems_the_search_gave_up_on": {self.CONDITION: gave_up},
            "refutation_timeout_ms": 40000,
            "world_sizes_tried": [3, 4, 5],
        }

    def test_a_timeout_is_reported_as_the_search_running_out(self) -> None:
        with pytest.raises(AssertionError, match="the search running out"):
            self._assert(self._report(refuted=["A"], gave_up=["B"]))

    def test_a_real_change_is_reported_as_a_real_change(self) -> None:
        with pytest.raises(AssertionError, match="real change in what the condition carries"):
            self._assert(self._report(refuted=["A"], gave_up=[]))

    def test_the_expected_set_raises_nothing(self) -> None:
        self._assert(self._report(refuted=["A", "B"], gave_up=[]))
