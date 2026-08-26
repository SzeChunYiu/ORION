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
        monkeypatch.setattr(cg, "verify_countermodel_certificate", undecided)

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
    def test_only_the_pinned_small_countermodel_certificates_are_checked(self) -> None:
        """Load-bearing evidence is certificate verification, not model discovery."""

        from types import SimpleNamespace

        calls: list[dict] = []

        def proved(**_kwargs):
            return tuple(SimpleNamespace(theorem=t, discharged=True) for t in cg.THEOREMS)

        def checked(_axioms, _claim, _cert, **kwargs):
            calls.append(kwargs)
            return cg.RefutationSearch.COUNTERMODEL

        report = cg._measure_frame_conditions(
            timeout_ms=1,
            repeats=2,
            proof_runner=proved,
            countermodel_search=checked,
        )

        assert len(calls) == len(cg.FRAME_CONDITION_IDS) * 2
        assert [call["certificate"].theorem for call in calls[::2]] == [
            "CERTIFICATE_WITHDRAWN_BY_ANY_DAMAGE",
            "CERTIFICATE_SUPPORTS_NOTHING_IS_DERIVED",
            "CERTIFICATE_WITHDRAWN_BY_ANY_DAMAGE",
        ]
        assert [call["certificate"].world_size for call in calls[::2]] == [2, 1, 1]
        assert report["every_condition_carries_a_theorem"] is True

    def test_every_condition_loses_at_least_one_theorem_when_dropped(
        self, load_bearing: dict
    ) -> None:
        assert load_bearing["inert_conditions"] == []
        assert load_bearing["every_condition_carries_a_theorem"] is True

    @pytest.mark.parametrize(
        ("condition", "expected_theorem"),
        [
            (
                "coordinates_support_the_certificate",
                "CERTIFICATE_WITHDRAWN_BY_ANY_DAMAGE",
            ),
            (
                "coordinates_do_not_support_each_other",
                "CERTIFICATE_SUPPORTS_NOTHING_IS_DERIVED",
            ),
            (
                "the_certificate_is_not_a_coordinate",
                "CERTIFICATE_WITHDRAWN_BY_ANY_DAMAGE",
            ),
        ],
    )
    def test_which_explicit_certificate_each_condition_carries(
        self, condition: str, expected_theorem: str, load_bearing: dict
    ) -> None:
        core = set(load_bearing["theorems_refuted_on_every_run"][condition])
        assert core == {expected_theorem}

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

    def test_the_explicit_certificates_really_refute_their_named_theorems(self) -> None:
        for condition, certificate in cg.FRAME_COUNTERMODEL_CERTIFICATES.items():
            query = next(
                item for item in cg._drop_queries(condition) if item[0] == certificate.theorem
            )
            _theorem, axioms, claim, cert = query
            assert (
                cg.verify_countermodel_certificate(
                    axioms,
                    claim,
                    cert,
                    certificate=certificate,
                    timeout_ms=1000,
                )
                is cg.RefutationSearch.COUNTERMODEL
            ), condition

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

        monkeypatch.setattr(cg, "load_executable_model", loading_a_broken_model, raising=True)
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

    def test_every_indistinguishable_graph_is_refuted_by_a_theorem(self, sensitivity: dict) -> None:
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

    def test_leaving_the_reachability_class_moves_the_count(self, sensitivity: dict) -> None:
        variants = sensitivity["variants"]
        assert (
            variants["one_coordinate_does_not_support_the_certificate"]["proper_subset_failures"]
            == 975
        )
        for name in ("edges_reversed", "no_support_edges"):
            assert variants[name]["proper_subset_failures"] == 0, name

    def test_the_restoration_count_is_reported_as_non_discriminating(
        self, sensitivity: dict
    ) -> None:
        # 155 comes out of every wrong graph too. Saying so is the point: half
        # the published result tests nothing about the interpretation.
        for name, variant in sensitivity["variants"].items():
            assert variant["full_restorations"] == 155, name
        assert (
            "does not depend on the graph"
            in (sensitivity["the_restoration_count_does_not_discriminate"])
        )


class TestTheReport:
    def test_v2_records_the_adverse_ci_history(self) -> None:
        report = cg.build_report(REPO_ROOT, date="2026-08-26")
        assert report["schema_version"] == "orion.p6.certificate-as-dependency-graph.v2"
        assert {row["run_id"] for row in report["adverse_execution_history"]} == {
            32927946106,
            32946736266,
        }
        assert all(row["outcome"] == "FAIL_RETAINED" for row in report["adverse_execution_history"])
        assert report["authority"] == {
            "scope": "LOCAL_SAME_LANE_FORMAL_CERTIFICATE_CHECK",
            "self_authored": True,
            "external_independent_validation": Outcome.CANNOT_CHECK.value,
            "grants_scientific_authority": "NONE",
        }

    def test_the_report_is_clean_and_names_its_limits(self) -> None:
        report = cg.build_report(REPO_ROOT, date="2026-08-22")
        assert report["all_discharged"] is True
        assert report["published_counts"]["counts_reproduced"] is True
        assert report["frame_conditions"]["every_condition_carries_a_theorem"] is True
        assert any("155 tests the interpretation" in item for item in report["not_licensed"])
        assert any("identify the star graph" in item for item in report["not_licensed"])
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

    def test_check_output_fails_closed_without_overwriting(self, tmp_path: Path) -> None:
        receipt = tmp_path / "receipt.json"
        sentinel = '{"stale": true}\n'
        receipt.write_text(sentinel, encoding="utf-8")

        try:
            code = cg.main(
                [
                    "--repo-root",
                    str(REPO_ROOT),
                    "--date",
                    "2026-08-26",
                    "--check-output",
                    str(receipt),
                ]
            )
        except SystemExit as exc:
            code = int(exc.code)

        assert code == 4
        assert receipt.read_text(encoding="utf-8") == sentinel

    def test_reproduce_v4_checks_the_v2_receipt_without_overwriting_it(self) -> None:
        makefile = (
            REPO_ROOT / "papers/paper-06-formal-epistemic-structures-and-mechanics/Makefile"
        ).read_text(encoding="utf-8")
        assert "reproduce-v4: reproduce-v3" in makefile
        assert "P6_CERTIFICATE_AS_DEPENDENCY_GRAPH_V2_2026-08-26.json" in makefile
        assert "--check-output" in makefile

    def test_v4_contract_binds_the_actual_generator_and_authority_ceiling(self) -> None:
        import hashlib
        import tomllib

        path = (
            REPO_ROOT / "papers/paper-06-formal-epistemic-structures-and-mechanics/evidence/local/"
            "P6_LOCAL_REPLAY_CONTRACT_V4.json"
        )
        assert path.is_file()
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["schema_version"] == "orion.local-replay-contract.v4"
        assert payload["one_command"].endswith("reproduce-v4")
        assert payload["self_authorizing"] is True
        assert payload["independent_replay"] is False
        assert payload["external_independent_validation"] == Outcome.CANNOT_CHECK.value
        assert payload["grants_scientific_authority"] == "NONE"

        with (REPO_ROOT / "pyproject.toml").open("rb") as stream:
            project = tomllib.load(stream)["project"]
        assert payload["python_runtime"] == {
            "constraint": project["requires-python"],
            "constraint_source": "pyproject.toml:project.requires-python",
            "exact_interpreter_pinned": False,
        }

        entries = {row["path"]: row["sha256"] for row in payload["execution_inputs"]}
        required = {
            "pyproject.toml",
            "uv.lock",
            "src/orion/study/p6/certificate_as_dependency_graph.py",
            "src/orion/study/p6/reopening_calculus_smt.py",
            "src/orion/study/p6/lift_theories.py",
            "src/orion/programme/mechanized.py",
            "src/orion/programme/records.py",
            "tests/unit/study/p6/test_p6_certificate_as_dependency_graph.py",
        }
        assert required <= set(entries)
        bound = {}
        for key in ("execution_inputs", "raw_inputs", "raw_outputs", "historical_predecessors"):
            bound.update({row["path"]: row["sha256"] for row in payload[key]})
        for relative, expected in bound.items():
            actual = hashlib.sha256((REPO_ROOT / relative).read_bytes()).hexdigest()
            assert actual == expected, relative

        receipt = (
            REPO_ROOT / "papers/paper-06-formal-epistemic-structures-and-mechanics/formal/"
            "mechanized/P6_CERTIFICATE_AS_DEPENDENCY_GRAPH_V2_2026-08-26.json"
        )
        assert json.loads(receipt.read_text(encoding="utf-8")) == cg.build_report(
            REPO_ROOT, date="2026-08-26"
        )


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
            "verify_countermodel_certificate",
            lambda axioms, claim, cert, **k: verdict_for(claim),
        )
        return cg.frame_conditions_are_load_bearing(repeats=2)

    def test_a_search_that_gave_up_is_undecided_and_never_inert(self, monkeypatch) -> None:
        report = self._measure(monkeypatch, lambda _claim: cg.RefutationSearch.UNDECIDED)

        assert report["inert_conditions"] == []
        assert report["conditions_left_undecided"] == sorted(cg.FRAME_CONDITION_IDS)
        assert report["outcome"] == Outcome.CANNOT_CHECK.value
        assert report["every_condition_carries_a_theorem"] is False

    def test_a_certificate_that_settles_with_no_countermodel_is_invalid(self, monkeypatch) -> None:
        """One failed witness cannot be promoted into a finding of inertness."""

        report = self._measure(monkeypatch, lambda _claim: cg.RefutationSearch.NO_COUNTERMODEL)

        assert report["inert_conditions"] == []
        assert report["invalid_countermodel_certificates"] == sorted(cg.FRAME_CONDITION_IDS)
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

    def test_the_criterion_preserves_both_non_positive_outcomes(self) -> None:
        report = cg.frame_conditions_are_load_bearing(repeats=1)
        assert "invalid certificate is a failed certificate" in report["criterion"]
        assert "does not settle is CANNOT_CHECK" in report["criterion"]
