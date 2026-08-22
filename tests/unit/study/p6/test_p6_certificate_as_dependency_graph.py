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
                "coordinates_support_the_certificate",
                {
                    "CERTIFICATE_WITHDRAWN_BY_ANY_DAMAGE",
                    "PARTIAL_REPAIR_LEAVES_CERTIFICATE_REOPENED",
                },
            ),
            (
                "coordinates_do_not_support_each_other",
                {
                    "CERTIFICATE_DAMAGE_REOPENS_NOTHING",
                    "UNDAMAGED_COORDINATES_ARE_NOT_REOPENED",
                    "CERTIFICATE_SUPPORTS_NOTHING_IS_DERIVED",
                },
            ),
        ],
    )
    def test_which_theorem_each_condition_carries_is_pinned(
        self, condition: str, expected_lost: set[str], load_bearing: dict
    ) -> None:
        # Pinned rather than merely counted: a condition that starts carrying a
        # different theorem has changed meaning, and a non-empty set of losses
        # would hide that.
        assert set(load_bearing["theorems_lost_by_dropping"][condition]) == expected_lost

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


class TestTheGraphCarriesTheCount:
    def test_every_wrong_graph_moves_the_discriminating_count(
        self, sensitivity: dict
    ) -> None:
        assert sensitivity["every_wrong_graph_changes_the_failure_count"] is True
        assert set(sensitivity["variants_that_change_the_failure_count"]) == set(
            sensitivity["variants"]
        )

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
