"""Tests for the panel resolution instrument.

The claim is "this hypothesis could not have come out differently", which is
only worth anything if the instrument can also say "this one could". So the
tests are paired: every check that fires on a defect is matched by a case it
must stay quiet on, and the sharpest pair is saturation against separation --
both give a zero-width interval and they mean opposite things.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.programme.panel_resolution import (
    MetricResolution,
    duplicate_arms,
    PUBLISHED_PANELS,
    build_report,
    discriminating_control,
    inspect_metric,
    inspect_panel,
    main,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


class TestWhatAMetricCanExpress:
    def test_varying_rates_discriminate(self) -> None:
        panel = {"a": {"r": 0.1}, "b": {"r": 0.4}, "c": {"r": 0.9}}
        assert inspect_metric(panel, "r").resolution is MetricResolution.DISCRIMINATES

    def test_every_system_at_the_ceiling_is_saturated(self) -> None:
        panel = {"a": {"r": 1.0}, "b": {"r": 1.0}, "c": {"r": 1.0}}
        report = inspect_metric(panel, "r")
        assert report.resolution is MetricResolution.SATURATED
        assert report.at_extreme == 1.0
        assert "ceiling" in report.detail

    def test_every_system_at_the_floor_is_saturated(self) -> None:
        panel = {"a": {"r": 0.0}, "b": {"r": 0.0}}
        report = inspect_metric(panel, "r")
        assert report.resolution is MetricResolution.SATURATED
        assert report.at_extreme == 0.0
        assert "floor" in report.detail

    def test_every_system_at_the_same_interior_value_is_still_saturated(self) -> None:
        # Saturation is about the panel holding one value, not about which value.
        report = inspect_metric({"a": {"r": 0.37}, "b": {"r": 0.37}}, "r")
        assert report.resolution is MetricResolution.SATURATED
        assert report.at_extreme is None

    def test_a_floor_ceiling_split_is_separation_not_saturation(self) -> None:
        # The distinction the module exists to draw. Both give a zero-width
        # interval; only one of them means nothing was learned.
        report = inspect_metric({"a": {"r": 1.0}, "b": {"r": 0.0}, "c": {"r": 0.0}}, "r")
        assert report.resolution is MetricResolution.SEPARATED_WITHOUT_VARIATION
        assert "not a measure of precision" in report.detail

    def test_a_missing_rate_is_not_read_as_zero(self) -> None:
        # Defaulting an absent rate to 0.0 would manufacture the variation this
        # module exists to detect.
        report = inspect_metric({"a": {"r": 1.0}, "b": {}, "c": {"r": 1.0}}, "r")
        assert report.resolution is MetricResolution.SATURATED
        assert set(report.values) == {"a", "c"}

    def test_one_system_cannot_be_assessed(self) -> None:
        report = inspect_metric({"a": {"r": 1.0}}, "r")
        assert report.resolution is MetricResolution.CANNOT_CHECK

    def test_booleans_are_not_metrics(self) -> None:
        panel = {"a": {"ok": True, "r": 0.2}, "b": {"ok": False, "r": 0.8}}
        assert "ok" not in inspect_panel(panel)

    def test_float_noise_is_not_a_distinct_value(self) -> None:
        report = inspect_metric({"a": {"r": 1.0}, "b": {"r": 1.0 - 1e-15}}, "r")
        assert report.resolution is MetricResolution.SATURATED

    def test_a_one_case_difference_is_a_distinct_value(self) -> None:
        # Rates over 360 opportunities differ by at least 1/360. The tolerance
        # must absorb representation error and nothing larger.
        report = inspect_metric({"a": {"r": 1.0}, "b": {"r": 359 / 360}}, "r")
        assert report.resolution is MetricResolution.DISCRIMINATES


class TestTheGuardIsNotVacuous:
    def test_the_control_panel_is_entirely_clean(self) -> None:
        reports = inspect_panel(discriminating_control())
        assert reports
        assert all(
            report.resolution is MetricResolution.DISCRIMINATES for report in reports.values()
        )

    def test_the_report_says_the_control_is_clean(self) -> None:
        assert build_report(REPO_ROOT, date="2026-08-22")["control_is_clean"] is True


class TestTheCommittedPanels:
    @pytest.fixture(scope="class")
    def report(self) -> dict:
        return build_report(REPO_ROOT, date="2026-08-22")

    def test_every_registered_panel_is_on_the_branch(self, report: dict) -> None:
        for panel in report["panels"]:
            assert panel["readable"] is True, panel["artifact"]

    def test_clean_coverage_is_saturated_in_both_p4_panels(self, report: dict) -> None:
        for panel in [p for p in report["panels"] if p["paper_id"] == "P4"]:
            metric = panel["metrics"]["clean_coverage"]
            assert metric["resolution"] == MetricResolution.SATURATED.value
            assert metric["at_extreme"] == 1.0

    def test_false_promotion_discriminates_in_both_p4_panels(self, report: dict) -> None:
        # The contrast that makes the finding a finding rather than a complaint
        # about the whole panel.
        for panel in [p for p in report["panels"] if p["paper_id"] == "P4"]:
            metric = panel["metrics"]["false_promotion_rate"]
            assert metric["resolution"] == MetricResolution.DISCRIMINATES.value
            assert metric["distinct_values"] >= 5

    def test_two_v2_hypotheses_were_settled_before_any_system_ran(
        self, report: dict
    ) -> None:
        v2 = next(p for p in report["panels"] if "PUBLICATION_METRICS_V2" in p["artifact"])
        assert v2["hypotheses"]["H2"]["verdict_could_have_differed"] is False
        assert v2["hypotheses"]["H3"]["verdict_could_have_differed"] is False
        assert v2["hypotheses"]["H1"]["verdict_could_have_differed"] is True

    def test_a_pass_and_a_not_supported_are_both_affected(self, report: dict) -> None:
        # Saturation is not a bias toward optimism: it decided one PASS and one
        # NOT_SUPPORTED in the same panel.
        v2 = next(p for p in report["panels"] if "PUBLICATION_METRICS_V2" in p["artifact"])
        assert v2["hypotheses"]["H2"]["declared_status"] == "PASS"
        assert v2["hypotheses"]["H3"]["declared_status"] == "NOT_SUPPORTED"

    def test_the_later_panel_repaired_one_of_the_two(self, report: dict) -> None:
        v3 = next(p for p in report["panels"] if "PANEL_V3" in p["artifact"])
        assert v3["hypotheses"]["H3"]["verdict_could_have_differed"] is True
        assert v3["hypotheses"]["H2"]["verdict_could_have_differed"] is False

    def test_the_settled_list_names_all_three(self, report: dict) -> None:
        assert len(report["hypotheses_settled_before_any_system_ran"]) == 3


class TestTheReport:
    def test_it_names_what_it_does_not_license(self) -> None:
        report = build_report(REPO_ROOT, date="2026-08-22")
        assert any("simply easy" in item for item in report["not_licensed"])
        assert any("H1" in item for item in report["not_licensed"])

    def test_the_date_is_supplied_not_read_from_the_clock(self) -> None:
        assert build_report(REPO_ROOT, date="1999-01-01")["date"] == "1999-01-01"

    def test_the_hypothesis_to_metric_map_is_declared_not_guessed(self) -> None:
        # Deriving which metric a hypothesis rests on from the artifact is
        # exactly how a saturated guard gets excused.
        for panel in PUBLISHED_PANELS:
            assert panel["hypothesis_metrics"]
            assert set(panel["hypothesis_metrics"]) == {"H1", "H2", "H3"}

    def test_the_cli_writes_the_artifact(self, tmp_path: Path) -> None:
        out = tmp_path / "report.json"
        assert main(["--repo-root", str(REPO_ROOT), "--date", "2026-08-22", "--output", str(out)]) == 0
        written = json.loads(out.read_text(encoding="utf-8"))
        assert written["record"] == "PANEL_RESOLUTION"
        assert len(written["hypotheses_settled_before_any_system_ran"]) == 3

    def test_the_cli_fails_when_the_control_stops_being_clean(self, monkeypatch) -> None:
        monkeypatch.setattr(
            "orion.programme.panel_resolution.discriminating_control",
            lambda: {"a": {"r": 1.0}, "b": {"r": 1.0}},
        )
        assert main(["--repo-root", str(REPO_ROOT), "--date", "2026-08-22"]) == 3


class TestAblationPanels:
    """An ablation delta of zero says something about the corpus, not the coordinate."""

    @pytest.fixture(scope="module")
    def report(self) -> dict:
        return build_report(REPO_ROOT, date="2026-08-22")

    def test_p3s_ablation_panel_is_on_the_branch(self, report: dict) -> None:
        assert report["ablation_panels"]
        assert all(panel["readable"] for panel in report["ablation_panels"])

    def test_four_of_p3s_six_ablations_move_nothing(self, report: dict) -> None:
        p3 = report["ablation_panels"][0]
        assert set(p3["inert_ablations"]) == {
            "remove_construct",
            "remove_measurement",
            "remove_referent",
            "remove_temporal_context",
        }

    def test_two_of_them_do_move_something(self, report: dict) -> None:
        # Without this the finding would be "the corpus measures nothing", which
        # is a different and stronger claim than the one being made.
        p3 = report["ablation_panels"][0]
        assert set(p3["active_ablations"]) == {
            "force_compatibility_without_obstruction",
            "remove_modality_polarity_attribution_discourse",
        }

    def test_an_inert_ablation_has_a_zero_width_interval_on_every_metric(
        self, report: dict
    ) -> None:
        p3 = report["ablation_panels"][0]
        for name in p3["inert_ablations"]:
            for low, high in p3["ablations"][name]["intervals"].values():
                assert low == 0.0 and high == 0.0, name

    def test_an_active_ablation_is_not_zero_on_every_metric(self, report: dict) -> None:
        p3 = report["ablation_panels"][0]
        for name in p3["active_ablations"]:
            intervals = p3["ablations"][name]["intervals"].values()
            assert any(low != 0.0 or high != 0.0 for low, high in intervals), name

    def test_the_reading_refuses_the_dispensable_interpretation(self, report: dict) -> None:
        reading = report["ablation_panels"][0]["reading"]
        assert "not evidence that they are dispensable" in reading
        assert "about the corpus" in reading

    def test_untestable_coordinates_are_surfaced_at_the_top_level(self, report: dict) -> None:
        assert len(report["untestable_coordinates"]) == 4
        assert all(item.startswith("P3: ") for item in report["untestable_coordinates"])


class TestTheSweepDoesNotFireOnEverything:
    """P1's panel is registered because it is expected to come out clean.

    Without a real panel that passes, the P3 and P4 findings would be a sweep
    reporting its own suspicion. P1 also carries a zero-width pairwise interval
    -- ORION and the active-VOI parent both at 1.0 protected success on the
    2,402 negative controls -- and it is not a defect, because other arms on
    that same metric range down to 0.0.
    """

    @pytest.fixture(scope="module")
    def p1(self) -> dict:
        report = build_report(REPO_ROOT, date="2026-08-22")
        return next(p for p in report["panels"] if p["paper_id"] == "P1")

    def test_p1s_panel_is_on_the_branch(self, p1: dict) -> None:
        assert p1["readable"] is True
        assert p1["systems"] == 14

    def test_every_p1_hypothesis_metric_discriminates(self, p1: dict) -> None:
        for name, hypothesis in p1["hypotheses"].items():
            assert hypothesis["metric_resolution"] == MetricResolution.DISCRIMINATES.value, name
            assert hypothesis["verdict_could_have_differed"] is True, name

    def test_p1s_negative_control_can_be_failed(self, p1: dict) -> None:
        # The claim under test is "ORION makes zero unnecessary reframes on the
        # controls". That is only a result if some arm makes some, and several do.
        metric = p1["metrics"]["negative_control_unnecessary_high_level_reframe_rate"]
        assert metric["resolution"] == MetricResolution.DISCRIMINATES.value
        assert min(metric["values"].values()) == 0.0
        assert max(metric["values"].values()) == 1.0

    def test_p1_contributes_nothing_to_the_settled_list(self) -> None:
        report = build_report(REPO_ROOT, date="2026-08-22")
        assert not any(
            item.startswith("P1 ") for item in report["hypotheses_settled_before_any_system_ran"]
        )


class TestArmsThatCannotDiffer:
    """Two arms with identical values on every shared metric are one arm twice.

    Kept apart from saturation deliberately: this fires on panels whose metrics
    all discriminate. P13A's four baselines vary freely across the panel and two
    of them still agree to the last digit.
    """

    @pytest.fixture(scope="module")
    def report(self) -> dict:
        return build_report(REPO_ROOT, date="2026-08-22")

    def test_identical_arms_are_grouped(self) -> None:
        panel = {"a": {"r": 0.5, "c": 2.0}, "b": {"r": 0.5, "c": 2.0}, "d": {"r": 0.9, "c": 1.0}}
        assert duplicate_arms(panel) == [("a", "b")]

    def test_arms_that_differ_anywhere_are_not_grouped(self) -> None:
        panel = {"a": {"r": 0.5, "c": 2.0}, "b": {"r": 0.5, "c": 2.5}}
        assert duplicate_arms(panel) == []

    def test_a_metric_only_one_arm_reports_does_not_break_the_tie(self) -> None:
        # An absent metric may be an absence of measurement rather than a
        # difference, so it must not be read as one.
        panel = {"a": {"r": 0.5}, "b": {"r": 0.5, "extra": 1.0}}
        assert duplicate_arms(panel) == [("a", "b")]

    def test_arms_sharing_no_metric_are_not_grouped(self) -> None:
        assert duplicate_arms({"a": {"x": 1.0}, "b": {"y": 1.0}}) == []

    def test_booleans_are_not_compared_as_numbers(self) -> None:
        panel = {"a": {"ok": True, "r": 1.0}, "b": {"ok": False, "r": 1.0}}
        assert duplicate_arms(panel) == [("a", "b")]

    def test_the_control_panel_has_no_duplicate_arms(self) -> None:
        assert duplicate_arms(discriminating_control()) == []

    def test_p13s_two_baselines_are_the_same_policy(self, report: dict) -> None:
        p13 = next(p for p in report["panels"] if p["paper_id"] == "P13")
        assert ["PROVENANCE_ONLY", "UNQUALIFIED"] in p13["indistinguishable_arms"]

    def test_p13s_metrics_all_discriminate_anyway(self, report: dict) -> None:
        # The reason this check is separate from saturation: the panel is not
        # saturated, it just contains one policy twice.
        p13 = next(p for p in report["panels"] if p["paper_id"] == "P13")
        for name, hypothesis in p13["hypotheses"].items():
            assert hypothesis["metric_resolution"] == MetricResolution.DISCRIMINATES.value, name

    def test_p1s_budget_ablation_coincides_with_its_own_base(self, report: dict) -> None:
        # The reading that is not a defect. P1 registers "remove the intervention
        # budget" as an ablation, and it changing nothing is the result.
        p1 = next(p for p in report["panels"] if p["paper_id"] == "P1")
        assert [
            "orion_mutation_necessity",
            "orion_with_unlimited_intervention_budget",
        ] in p1["indistinguishable_arms"]

    def test_the_report_refuses_to_call_a_pair_a_defect(self, report: dict) -> None:
        assert any(
            "cannot tell them apart and does not try" in item
            for item in report["not_licensed"]
        )

    def test_four_pairs_across_three_panels(self, report: dict) -> None:
        assert len(report["arms_that_cannot_differ"]) == 4
        papers = {item.split(":")[0] for item in report["arms_that_cannot_differ"]}
        assert papers == {"P1", "P4", "P13"}
