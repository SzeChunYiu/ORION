"""Tests for P6's certificate model read as an instance of the reopening semantics.

The claim under test is a *corollary* claim, which is the one that is easiest to
fake: any two enumerations that count the same thing agree, whether or not one
follows from the other. So the tests here are not "do the numbers come out". They
are: does the interpretation carry the proof (drop a frame condition and a
theorem must go), does the graph carry the count (use a wrong graph and the
discriminating count must move), and is the count produced by P6's own verified
implementation rather than by a rule this lane wrote.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.programme.records import Outcome
from orion.study.p6 import certificate_as_dependency_graph as cg

REPO_ROOT = Path(__file__).resolve().parents[4]

z3 = pytest.importorskip("z3", reason="the interpretation is discharged by Z3")


@pytest.fixture(scope="module")
def proofs() -> tuple:
    return cg.prove_all()


@pytest.fixture(scope="module")
def counts() -> dict:
    return cg.recompute_published_counts(REPO_ROOT)


@pytest.fixture(scope="module")
def load_bearing() -> dict:
    return cg.frame_conditions_are_load_bearing()


@pytest.fixture(scope="module")
def sensitivity() -> dict:
    return cg.counts_are_sensitive_to_the_interpretation(REPO_ROOT)


class TestTheInterpretationIsProved:
    def test_every_theorem_is_discharged(self, proofs: tuple) -> None:
        undischarged = [r.theorem.name for r in proofs if not r.discharged]
        assert undischarged == []

    def test_no_theorem_is_recorded_unknown(self, proofs: tuple) -> None:
        # UNKNOWN is not PROVED. Collapsing the two is how a timeout becomes a
        # result.
        assert [r.theorem.name for r in proofs if r.outcome.value == "UNKNOWN"] == []

    def test_the_theorem_list_and_the_proofs_agree(self, proofs: tuple) -> None:
        assert [r.theorem.name for r in proofs] == [t.name for t in cg.THEOREMS]

    def test_identical_proof_queries_are_evaluated_once_per_process(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A later report reuses the exact three-valued proof snapshot."""

        original = cg._queries
        calls = 0

        def counted_queries(drop=None):
            nonlocal calls
            calls += 1
            return original(drop=drop)

        monkeypatch.setattr(cg, "_queries", counted_queries)

        first = cg.prove_all(timeout_ms=1)
        second = cg.prove_all(timeout_ms=1)

        assert second is first
        assert calls == 1

    def test_omitted_and_explicit_proof_defaults_are_the_same_query(self) -> None:
        assert cg.prove_all() is cg.prove_all(timeout_ms=30000, drop=None)

    def test_identical_frame_queries_reuse_but_do_not_expose_the_snapshot(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Caching keeps CANNOT_CHECK exact and callers cannot mutate the cache."""

        from types import SimpleNamespace

        calls = 0

        def proved(**_kwargs):
            return tuple(SimpleNamespace(theorem=t, discharged=True) for t in cg.THEOREMS)

        def undecided(*_args, **_kwargs):
            nonlocal calls
            calls += 1
            return cg.RefutationSearch.UNDECIDED

        monkeypatch.setattr(cg, "prove_all", proved)
        monkeypatch.setattr(cg, "search_for_a_countermodel", undecided)

        first = cg.frame_conditions_are_load_bearing(timeout_ms=1, repeats=2)
        second = cg.frame_conditions_are_load_bearing(timeout_ms=1, repeats=2)

        assert first == second
        assert first is not second
        assert second["outcome"] == Outcome.CANNOT_CHECK.value
        assert calls == len(cg.FRAME_CONDITION_IDS) * 2

        first["conditions_left_undecided"].append("caller mutation")
        third = cg.frame_conditions_are_load_bearing(timeout_ms=1, repeats=2)
        assert "caller mutation" not in third["conditions_left_undecided"]


class TestTheFrameConditionsCarryTheProof:
    def test_every_frame_condition_has_a_constructive_countermodel(self) -> None:
        """Load-bearing authority must not depend on a timed model search."""

        assert set(cg.FRAME_CONDITION_COUNTERMODELS) == set(cg.FRAME_CONDITION_IDS)
        for condition, witness in cg.FRAME_CONDITION_COUNTERMODELS.items():
            assert cg.verify_constructive_frame_countermodel(
                condition, witness.theorem
            ), condition

    def test_constructive_countermodels_are_dispatched_before_z3_search(self) -> None:
        """Even a one-millisecond budget verifies each declared witness."""

        for condition, witness in cg.FRAME_CONDITION_COUNTERMODELS.items():
            row = next(
                item
                for item in cg._drop_queries(condition)
                if item[0] == witness.theorem
            )
            name, axioms, claim, cert = row
            assert (
                cg.search_for_a_countermodel(
                    axioms,
                    claim,
                    cert,
                    condition=condition,
                    theorem=name,
                    timeout_ms=1,
                )
                is cg.RefutationSearch.COUNTERMODEL
            )

    def test_every_condition_loses_at_least_one_theorem_when_dropped(
        self, load_bearing: dict
    ) -> None:
        assert load_bearing["inert_conditions"] == []
        assert load_bearing["every_condition_carries_a_theorem"] is True

    @pytest.mark.parametrize(
        ("condition", "expected_core"),
        [
            (
                "coordinates_support_the_certificate",
                {
                    "CERTIFICATE_WITHDRAWN_BY_ANY_DAMAGE",
                    "PARTIAL_REPAIR_LEAVES_CERTIFICATE_REOPENED",
                },
            ),
            (
                "coordinates_do_not_support_each_other",
                {"CERTIFICATE_SUPPORTS_NOTHING_IS_DERIVED"},
            ),
            (
                "the_certificate_is_not_a_coordinate",
                {
                    "CERTIFICATE_DAMAGE_REOPENS_NOTHING",
                    "CERTIFICATE_SUPPORTS_NOTHING_IS_DERIVED",
                    "CERTIFICATE_WITHDRAWN_BY_ANY_DAMAGE",
                    "PARTIAL_REPAIR_LEAVES_CERTIFICATE_REOPENED",
                    "UNDAMAGED_COORDINATES_ARE_NOT_REOPENED",
                },
            ),
        ],
    )
    def test_which_theorem_each_condition_always_carries(
        self, condition: str, expected_core: set[str], load_bearing: dict
    ) -> None:
        # The stable preregistered core, not a post-outcome choice among whichever
        # extra countermodels a timed solver happened to discover.
        core = set(load_bearing["theorems_refuted_on_every_run"][condition])
        assert core <= expected_core
        assert core

    def test_a_theorem_that_only_stops_being_provable_is_not_counted(
        self, load_bearing: dict
    ) -> None:
        # The correction this class exists for. An UNKNOWN return is a fact
        # about the search, not evidence the axiom was carrying the theorem, and
        # the first version of this measurement counted it as a loss.
        assert "unknown return is a fact about the" in load_bearing["criterion"]
        assert "not deterministic" in load_bearing["criterion"]

    def test_the_measurement_is_repeated(self, load_bearing: dict) -> None:
        assert load_bearing["repeats"] >= 3

    def test_a_bounded_countermodel_is_only_used_to_refute(self) -> None:
        # Soundness of the whole approach rests on direction: a countermodel in
        # a small universe refutes a universal claim, while failing to find one
        # there proves nothing. If the bound ever reached a proof query this
        # would be unsound, so the proof path is checked to be unbounded.
        import inspect

        source = inspect.getsource(cg.prove_all)
        assert "refute_in_a_bounded_world" not in source
        assert "REFUTATION_WORLD_SIZE" not in source

    def test_an_unknown_condition_is_refused(self) -> None:
        with pytest.raises(ValueError, match="unknown frame condition"):
            cg.prove_all(drop="no_such_condition")

    def test_the_sink_is_derived_and_not_assumed(self) -> None:
        # It was an axiom until the load-bearing check reported it inert. If it
        # ever reappears in the axiom set, this test says so.
        assert "the_certificate_is_a_sink" not in cg.FRAME_CONDITION_IDS
        assert "CERTIFICATE_SUPPORTS_NOTHING_IS_DERIVED" in {t.name for t in cg.THEOREMS}


class TestThePublishedCountsAreAnInstance:
    def test_both_counts_are_reproduced(self, counts: dict) -> None:
        assert counts["full_restorations"] == 155
        assert counts["proper_subset_failures"] == 1055
        assert counts["counts_reproduced"] is True

    def test_no_counterexample_to_restoration_or_minimality(self, counts: dict) -> None:
        assert counts["restoration_counterexamples"] == []
        assert counts["minimality_counterexamples"] == []

    def test_the_counts_come_from_the_committed_implementation(self) -> None:
        # Not from a rule defined in this module. If `descendants` is broken, the
        # count must break with it -- that is the whole reason for routing the
        # recomputation through the shipped file.
        model_path = REPO_ROOT / cg.EXECUTABLE_MODEL
        assert model_path.is_file()
        source = model_path.read_text(encoding="utf-8")
        assert "def descendants(" in source

    def test_a_broken_descendants_breaks_the_count(self, monkeypatch) -> None:
        from orion.programme import mechanized

        real_loader = mechanized.load_executable_model

        def loading_a_broken_model(path, name):
            module = real_loader(path, name)
            module.descendants = lambda node_count, edges, changed: frozenset()
            return module

        monkeypatch.setattr(
            cg, "load_executable_model", loading_a_broken_model, raising=True
        )
        broken = cg.recompute_published_counts(REPO_ROOT)
        assert broken["proper_subset_failures"] == 0
        assert broken["counts_reproduced"] is False


class TestWhatTheCountsCanAndCannotIdentify:
    """The counts confirm a reachability class; the theorems pin the graph.

    Written this way because the first version of this check tried three wrong
    graphs, watched all three collapse to zero, and concluded the counts
    identified the interpretation. They do not: three further graphs reproduce
    1,055 exactly.
    """

    def test_the_counts_do_not_identify_the_star(self, sensitivity: dict) -> None:
        assert sensitivity["counts_alone_identify_the_interpretation"] is False
        assert set(sensitivity["variants_the_counts_cannot_distinguish_from_the_star"]) == {
            "coordinates_chained_into_the_certificate",
            "star_with_coordinate_cross_edges",
            "complete_graph",
        }

    def test_every_indistinguishable_graph_is_refuted_by_a_theorem(
        self, sensitivity: dict
    ) -> None:
        # This is the load-bearing assertion of the module. A variant that
        # escaped both the counts and the theorems would leave the
        # interpretation genuinely under-determined.
        assert sensitivity["every_indistinguishable_variant_is_caught_by_a_theorem"] is True
        for name in sensitivity["variants_the_counts_cannot_distinguish_from_the_star"]:
            assert sensitivity["variants"][name]["coordinates_reopened_as_collateral"] > 0, name

    def test_the_star_itself_has_no_collateral_reopening(self, counts: dict) -> None:
        # The property the three indistinguishable graphs violate must hold of
        # the interpretation, or the discriminator discriminates against it too.
        from orion.programme.mechanized import load_executable_model

        model = load_executable_model(REPO_ROOT / cg.EXECUTABLE_MODEL, "p6_star_check")
        width = len(cg.COORDINATES)
        star = [(index, width) for index in range(width)]
        for damaged in ((0,), (0, 1), (0, 1, 2, 3, 4)):
            reopened = model.descendants(width + 1, star, frozenset(damaged))
            assert reopened == frozenset({width}), damaged

    def test_leaving_the_reachability_class_moves_the_count(
        self, sensitivity: dict
    ) -> None:
        variants = sensitivity["variants"]
        assert variants["one_coordinate_does_not_support_the_certificate"][
            "proper_subset_failures"
        ] == 975
        for name in ("edges_reversed", "no_support_edges"):
            assert variants[name]["proper_subset_failures"] == 0, name

    def test_the_restoration_count_is_reported_as_non_discriminating(
        self, sensitivity: dict
    ) -> None:
        # 155 comes out of every wrong graph too. Saying so is the point: half
        # the published result tests nothing about the interpretation.
        for name, variant in sensitivity["variants"].items():
            assert variant["full_restorations"] == 155, name
        assert "does not depend on the graph" in (
            sensitivity["the_restoration_count_does_not_discriminate"]
        )


class TestTheReport:
    def test_the_report_is_clean_and_names_its_limits(self) -> None:
        report = cg.build_report(REPO_ROOT, date="2026-08-22")
        assert report["all_discharged"] is True
        assert report["published_counts"]["counts_reproduced"] is True
        assert report["frame_conditions"]["every_condition_carries_a_theorem"] is True
        assert any("155 tests the interpretation" in item for item in report["not_licensed"])
        assert any(
            "identify the star graph" in item for item in report["not_licensed"]
        )
        assert any("independent review" in item for item in report["not_licensed"])

    def test_the_date_is_supplied_not_read_from_the_clock(self) -> None:
        assert cg.build_report(REPO_ROOT, date="1999-01-01")["date"] == "1999-01-01"

    def test_the_cli_writes_the_artifact(self, tmp_path: Path) -> None:
        out = tmp_path / "report.json"
        code = cg.main(
            ["--repo-root", str(REPO_ROOT), "--date", "2026-08-22", "--output", str(out)]
        )
        assert code == 0
        written = json.loads(out.read_text(encoding="utf-8"))
        assert written["record"] == "P6_CERTIFICATE_AS_DEPENDENCY_GRAPH"
        assert len(written["theorems"]) == len(cg.THEOREMS)


class TestASearchThatGaveUpIsNotAFinding:
    """A loaded machine must not be able to make this audit publish an inert axiom.

    ``refute_in_a_bounded_world`` returned a bool, so "no countermodel exists in
    this world" and "the solver ran out of time" were the same ``False``, and
    ``inert_conditions`` was computed from it. A full-suite run under load duly
    reported ``coordinates_do_not_support_each_other`` as carrying nothing --- a
    claim about the axiom, produced by contention.

    These drive the classifier directly rather than waiting for a busy machine,
    because a test that reproduces this only under load is not a test.
    """

    def test_the_search_reports_three_outcomes_not_two(self) -> None:
        assert set(cg.RefutationSearch) == {
            cg.RefutationSearch.COUNTERMODEL,
            cg.RefutationSearch.NO_COUNTERMODEL,
            cg.RefutationSearch.UNDECIDED,
        }

    def test_the_bool_wrapper_is_true_only_for_a_countermodel(self, monkeypatch) -> None:
        for verdict, expected in (
            (cg.RefutationSearch.COUNTERMODEL, True),
            (cg.RefutationSearch.NO_COUNTERMODEL, False),
            (cg.RefutationSearch.UNDECIDED, False),
        ):
            monkeypatch.setattr(
                cg, "search_for_a_countermodel", (lambda _v: lambda *a, **k: _v)(verdict)
            )
            assert cg.refute_in_a_bounded_world([], None, None) is expected, verdict

    def _measure(self, monkeypatch, verdict_for) -> dict:
        monkeypatch.setattr(
            cg,
            "search_for_a_countermodel",
            lambda axioms, claim, cert, **k: verdict_for(claim),
        )
        return cg.frame_conditions_are_load_bearing(repeats=2)

    def test_a_search_that_gave_up_is_undecided_and_never_inert(
        self, monkeypatch
    ) -> None:
        report = self._measure(
            monkeypatch, lambda _claim: cg.RefutationSearch.UNDECIDED
        )

        assert report["inert_conditions"] == []
        assert report["conditions_left_undecided"] == sorted(cg.FRAME_CONDITION_IDS)
        assert report["outcome"] == Outcome.CANNOT_CHECK.value
        assert report["every_condition_carries_a_theorem"] is False

    def test_a_condition_that_settles_with_no_countermodel_is_inert(
        self, monkeypatch
    ) -> None:
        """The finding the audit is entitled to make, and it must still fire."""

        report = self._measure(
            monkeypatch, lambda _claim: cg.RefutationSearch.NO_COUNTERMODEL
        )

        assert report["inert_conditions"] == sorted(cg.FRAME_CONDITION_IDS)
        assert report["conditions_left_undecided"] == []
        assert report["outcome"] == Outcome.FAIL.value

    def test_the_classification_separates_all_four_states(self) -> None:
        """The logic that was wrong twice, checked without a solver.

        ``inert`` used to be read off the stable core alone, so it swallowed two
        different things that are not findings: a condition whose searches gave
        up, and one whose refutation is real but intermittent. The second is the
        subtler error --- the union is non-empty, so the condition demonstrably
        carries a theorem, and calling it inert states the opposite of what was
        measured.
        """

        inert, undecided, intermittent = cg.classify_frame_conditions(
            always={"stable": {"T1"}, "flaky": set(), "gave_up": set(), "empty": set()},
            ever={"stable": {"T1"}, "flaky": {"T2"}, "gave_up": set(), "empty": set()},
            undecided={"stable": set(), "flaky": set(), "gave_up": {"T3"}, "empty": set()},
        )

        assert inert == ["empty"]
        assert undecided == ["gave_up"]
        assert intermittent == ["flaky"]

    def test_an_intermittent_refutation_is_never_called_inert(self) -> None:
        inert, _, intermittent = cg.classify_frame_conditions(
            always={"c": set()}, ever={"c": {"T"}}, undecided={"c": set()}
        )

        assert inert == []
        assert intermittent == ["c"]

    def test_the_criterion_states_both_directions(self) -> None:
        report = cg.frame_conditions_are_load_bearing(repeats=1)
        assert "in that direction too" in report["criterion"]
