"""Tests for the P2 campaign resolution guard.

The guard's whole purpose is to catch a check that cannot fail, so the first
thing it has to survive is that accusation itself. Every test below either
shows it firing on a specific defect or shows it staying quiet on a campaign
that does not have that defect; a test that only ran it against the two real
artifacts would prove nothing, because both of those are defective.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from orion.study.p2 import comparison_resolution as cr

REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture()
def control() -> dict:
    return cr.well_resolved_control()


class TestTheGuardIsNotVacuous:
    def test_a_campaign_with_resolution_passes(self, control: dict) -> None:
        report = cr.inspect_campaign_result(control)
        assert report.resolution is cr.Resolution.HAS_RESOLUTION
        assert report.resolution_findings == ()

    def test_the_survey_reports_the_control_passing(self) -> None:
        assert cr.survey(REPO_ROOT)["control_passes"] is True


class TestTheMeasurementFloor:
    """The root diagnosis, and the one derived from the campaign's own threshold."""

    def test_a_campaign_above_its_own_threshold_is_not_at_the_floor(
        self, control: dict
    ) -> None:
        floor = cr.headline_cannot_reach_the_required_delta(control)
        assert floor["checked"] is True
        assert floor["at_floor"] is False

    def test_an_arm_below_the_required_delta_is_at_the_floor(self, control: dict) -> None:
        for arm in control["official"].values():
            arm["avg_iou"] = 0.004
        floor = cr.headline_cannot_reach_the_required_delta(control)
        assert floor["at_floor"] is True
        assert floor["best_arm_avg_iou"] == 0.004
        assert floor["required_avg_iou_delta"] == 0.03

    def test_the_threshold_comes_from_the_artifact_not_from_this_module(
        self, control: dict
    ) -> None:
        # No invented epsilon. Raise the campaign's own required delta above the
        # best arm and the same scores become a floor.
        control["scientific_rule"]["required_official_avg_iou_delta"] = 0.9
        assert cr.headline_cannot_reach_the_required_delta(control)["at_floor"] is True

    def test_a_campaign_without_a_frozen_rule_is_not_checked(self, control: dict) -> None:
        # Reporting `checked: false` is not the same as passing, and the control
        # carries a rule precisely so this path is not the one it takes.
        del control["scientific_rule"]
        floor = cr.headline_cannot_reach_the_required_delta(control)
        assert floor == {"checked": False, "at_floor": False}

    def test_the_delta_row_is_excluded_from_the_arm_scores(self, control: dict) -> None:
        control["official"]["orion_minus_primary_baseline"] = {"avg_iou": 0.99}
        floor = cr.headline_cannot_reach_the_required_delta(control)
        assert "orion_minus_primary_baseline" not in floor["arm_scores"]
        assert floor["at_floor"] is False

    def test_both_committed_campaigns_are_at_the_floor(self) -> None:
        surveyed = cr.survey(REPO_ROOT)
        for name, campaign in surveyed["campaigns"].items():
            assert campaign["floor"]["at_floor"] is True, name
            assert campaign["floor"]["best_arm_avg_iou"] < 0.005, name
            assert campaign["floor"]["required_avg_iou_delta"] == 0.03, name


class TestEachCheckFiresOnItsOwnDefect:
    def test_identical_candidates_across_arms(self, control: dict) -> None:
        control["candidate_sha256"] = {"arm_a": "a" * 64, "arm_b": "a" * 64}
        report = cr.inspect_campaign_result(control)
        assert report.resolution is cr.Resolution.ZERO_RESOLUTION
        assert any("share one candidate digest" in f for f in report.resolution_findings)

    def test_identical_evaluator_output_across_distinct_arms(self, control: dict) -> None:
        control["evaluator_output_sha256"] = {"arm_a": "c" * 64, "arm_b": "c" * 64}
        report = cr.inspect_campaign_result(control)
        assert report.resolution is cr.Resolution.ZERO_RESOLUTION
        assert any("evaluator-output digest" in f for f in report.resolution_findings)

    def test_an_all_ties_paired_split(self, control: dict) -> None:
        control["paired_distinct_question_iou"] = {
            "n": 399, "ties": 399, "wins": 0, "losses": 0,
            "ci95_low": 0.0, "ci95_high": 0.0,
        }
        report = cr.inspect_campaign_result(control)
        assert report.resolution is cr.Resolution.ZERO_RESOLUTION
        assert any("zero-width" in f for f in report.resolution_findings)

    def test_a_tight_but_earned_interval_is_not_flagged(self, control: dict) -> None:
        # The distinction the check exists to draw: an interval narrowed by
        # evidence is not an interval that was never wide.
        control["paired_distinct_question_iou"] = {
            "n": 399, "ties": 397, "wins": 1, "losses": 1,
            "ci95_low": -0.0001, "ci95_high": 0.0001,
        }
        report = cr.inspect_campaign_result(control)
        assert report.resolution is cr.Resolution.HAS_RESOLUTION

    def test_a_decreasing_at_k_curve(self, control: dict) -> None:
        control["official"]["arm_a"]["avg_max_iou_at_2"] = 0.0
        report = cr.inspect_campaign_result(control)
        assert report.non_monotone_at_k
        assert "arm_a" in report.non_monotone_at_k[0]

    def test_a_monotone_at_k_curve_is_not_flagged(self, control: dict) -> None:
        assert cr.non_monotone_at_k(control["official"]) == ()

    def test_a_flat_at_k_curve_is_not_flagged(self, control: dict) -> None:
        # Equal is not decreasing. A ceiling reached at k=1 is a real shape.
        for arm in control["official"].values():
            arm["avg_max_iou_at_2"] = arm["avg_max_iou_at_1"]
            arm["avg_max_iou_at_4"] = arm["avg_max_iou_at_1"]
        assert cr.non_monotone_at_k(control["official"]) == ()

    def test_uniformly_zero_runtime_totals(self, control: dict) -> None:
        for arm in control["official"].values():
            for field in cr.RUNTIME_TOTAL_FIELDS:
                arm[field] = 0
        report = cr.inspect_campaign_result(control)
        assert len(report.absent_runtime_totals) == 2

    def test_one_zero_total_among_others_is_not_flagged(self, control: dict) -> None:
        # A system that made no tool calls but burned tokens ran. Only uniform
        # zeros are an absence.
        control["official"]["arm_a"]["avg_tool_call_count"] = 0
        assert cr.absent_runtime_totals(control["official"]) == ()

    def test_an_artifact_without_the_blocks_cannot_be_checked(self) -> None:
        report = cr.inspect_campaign_result({"terminal": "SOMETHING"})
        assert report.resolution is cr.Resolution.CANNOT_CHECK


class TestTheCommittedCampaigns:
    @pytest.fixture(scope="class")
    def surveyed(self) -> dict:
        return cr.survey(REPO_ROOT)

    def test_both_published_campaigns_have_zero_resolution(self, surveyed: dict) -> None:
        assert surveyed["every_published_campaign_has_zero_resolution"] is True
        assert len(surveyed["zero_resolution_campaigns"]) == 2

    def test_v1_compared_a_system_against_itself(self, surveyed: dict) -> None:
        v1 = surveyed["campaigns"]["P2_WIDE_OPENAIRE_MATCHED_RESULT_V1.json"]
        assert v1["distinct_candidate_digests"] == 1
        assert v1["arms"] == 3

    def test_v3_arms_differ_but_their_scores_cannot(self, surveyed: dict) -> None:
        v3 = surveyed["campaigns"]["P2_WIDE_OPENAIRE_MATCHED_RESULT_V3.json"]
        assert v3["distinct_candidate_digests"] == 3
        assert v3["distinct_evaluator_digests"] == 1

    def test_both_report_a_zero_width_interval_over_399_questions(
        self, surveyed: dict
    ) -> None:
        for campaign in surveyed["campaigns"].values():
            paired = campaign["paired"]
            assert paired["n"] == 399
            assert paired["ties"] == 399
            assert paired["ci95_low"] == 0.0 and paired["ci95_high"] == 0.0

    def test_the_scorer_that_states_the_exclusion_rule_still_states_it(self) -> None:
        # The defect is that the rule lives in one scorer and the published
        # artifacts came out of another. If the rule is ever deleted from the
        # scorer, this module's finding loses its footing and should fail here.
        scorer = (
            REPO_ROOT
            / "papers/orion-12-open-world-scientific-discovery/scripts/score_wide_comparison.py"
        ).read_text(encoding="utf-8")
        assert "absent measurement wearing the costume of a number" in scorer
        assert cr.SAMPLED_FAMILY_MARKER in scorer


class TestTheTwoFindingListsSayDifferentThings:
    def test_a_reporting_slip_does_not_cost_a_campaign_its_resolution(
        self, control: dict
    ) -> None:
        # The control publishes the unseeded family, which is a reporting
        # finding. It still has resolution, and conflating the two is what made
        # this guard fail its own control the first time.
        report = cr.inspect_campaign_result(control)
        assert report.reporting_findings
        assert report.resolution_findings == ()
        assert report.resolution is cr.Resolution.HAS_RESOLUTION

    def test_findings_concatenates_both_lists_resolution_first(
        self, control: dict
    ) -> None:
        control["candidate_sha256"] = {"arm_a": "a" * 64, "arm_b": "a" * 64}
        report = cr.inspect_campaign_result(control)
        assert report.findings == report.resolution_findings + report.reporting_findings
        assert "candidate digest" in report.findings[0]


class TestTheReport:
    def test_the_report_names_what_it_does_not_license(self) -> None:
        report = cr.build_report(REPO_ROOT, date="2026-08-22")
        assert report["record"] == "P2_COMPARISON_RESOLUTION"
        assert report["control_passes"] is True
        assert any("are or are not equivalent" in item for item in report["not_licensed"])
        assert any("terminal was wrong" in item for item in report["not_licensed"])

    def test_the_date_is_supplied_not_read_from_the_clock(self) -> None:
        assert cr.build_report(REPO_ROOT, date="1999-01-01")["date"] == "1999-01-01"

    def test_the_cli_writes_the_artifact(self, tmp_path: Path) -> None:
        out = tmp_path / "report.json"
        assert cr.main(
            ["--repo-root", str(REPO_ROOT), "--date", "2026-08-22", "--output", str(out)]
        ) == 0
        written = json.loads(out.read_text(encoding="utf-8"))
        assert written["every_published_campaign_has_zero_resolution"] is True

    def test_the_cli_fails_when_the_guard_becomes_vacuous(self, monkeypatch) -> None:
        # Patched through the module, not by importing the name: rebinding a
        # name this module imported by value would leave the guard unperturbed
        # and the test would pass against an object it never changed.
        broken = copy.deepcopy(cr.well_resolved_control())
        broken["candidate_sha256"] = {"arm_a": "a" * 64, "arm_b": "a" * 64}
        monkeypatch.setattr(cr, "well_resolved_control", lambda: broken)
        assert cr.main(["--repo-root", str(REPO_ROOT), "--date", "2026-08-22"]) == 3
