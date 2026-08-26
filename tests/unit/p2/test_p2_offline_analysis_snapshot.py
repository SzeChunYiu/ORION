"""Freeze the P2 offline publication snapshot after the run manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from orion.study.p2.corpus import canonical_bytes
from orion.study.p2.freeze import load_manifest, load_suite, verify
from orion.study.p2.offline_analysis import (
    DEFAULT_SEEDS,
    achieved_precision_tier,
    run_offline_companion,
)
from orion.study.p2.offline_systems import ALL_SYSTEMS

PAPER = Path("papers/orion-12-open-world-scientific-discovery")
MANIFEST = PAPER / "protocol" / "OFFLINE_RUN_MANIFEST_V1.json"
MANIFEST_SHA = PAPER / "protocol" / "OFFLINE_RUN_MANIFEST_V1.sha256"
EXPECTED = PAPER / "evidence" / "offline_results" / "RESULTS_SUMMARY_V1.json"
_SYSTEM_FIELDS = (
    "mean_complete_gold_recall",
    "mean_precision",
    "premature_task_closure_rate",
    "mean_duplicate_processing_rate",
    "mean_legitimate_reread_count",
    "mean_marginal_relevant_gain_after_first_route",
    "mean_route_pair_overlap",
    "mean_routes_used",
    "pass_rate",
    "fail_rate",
    "cannot_check_rate",
    "invalid_rate",
    "status_counts",
    "failure_counts",
)


def _manifest_hash() -> str:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    computed = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    recorded = MANIFEST_SHA.read_text(encoding="utf-8").split()[0]
    assert computed == recorded
    assert payload["outcome_accessed_before_freeze"] is False
    return computed


def _publication_projection(summary: dict) -> dict:
    systems = summary["systems"]
    return {
        "schema_version": "orion.p2.offline-publication-summary.v1",
        "analysis_authority": summary["analysis_authority"],
        "authority_reason": summary["authority_reason"],
        "frozen_run": {
            "n_tasks": summary["n_tasks"],
            "n_repeats": summary["n_repeats"],
            "n_systems": summary["n_systems"],
            "n_result_records": summary["n_result_records"],
            "record_digest_sha256": summary["record_digest_sha256"],
            "raw_artifact_hash_list_digest_sha256": summary[
                "raw_artifact_hash_list_digest_sha256"
            ],
        },
        "achieved_precision": summary["achieved_precision"],
        "headline": {
            "strongest_confirmatory_baseline": summary[
                "strongest_confirmatory_baseline"
            ],
            "orion_minus_strongest_baseline_recall": summary[
                "orion_minus_strongest_baseline_recall"
            ],
            "orion_minus_strongest_baseline_premature_closure": summary[
                "orion_minus_strongest_baseline_premature_closure"
            ],
        },
        "systems": {
            name: {field: values[field] for field in _SYSTEM_FIELDS}
            for name, values in systems.items()
        },
        "mechanism_checks": {
            "route_independence": {
                "orion_recall": systems["orion_full"]["mean_complete_gold_recall"],
                "ablated_recall": systems["no_route_independence_check"][
                    "mean_complete_gold_recall"
                ],
                "orion_premature_closure_rate": systems["orion_full"][
                    "premature_task_closure_rate"
                ],
                "ablated_premature_closure_rate": systems[
                    "no_route_independence_check"
                ]["premature_task_closure_rate"],
            },
            "question_conditioned_read_ledger": {
                "orion_extraction_shift_legitimate_rereads": systems["orion_full"][
                    "by_case_family"
                ]["extraction_question_shift"]["mean_legitimate_reread_count"],
                "ablated_extraction_shift_legitimate_rereads": systems[
                    "no_question_conditioned_read_ledger"
                ]["by_case_family"]["extraction_question_shift"][
                    "mean_legitimate_reread_count"
                ],
            },
            "route_task_stop_separation": {
                "orion_recall": systems["orion_full"]["mean_complete_gold_recall"],
                "ablated_recall": systems["route_stop_can_close_task"][
                    "mean_complete_gold_recall"
                ],
                "orion_premature_closure_rate": systems["orion_full"][
                    "premature_task_closure_rate"
                ],
                "ablated_premature_closure_rate": systems[
                    "route_stop_can_close_task"
                ]["premature_task_closure_rate"],
            },
            "unavailable_route_open_state": {
                "orion_cannot_check_rate": systems["orion_full"]["cannot_check_rate"],
                "ablated_cannot_check_rate": systems["no_unavailable_route_open_state"][
                    "cannot_check_rate"
                ],
                "ablated_premature_closure_failures": systems[
                    "no_unavailable_route_open_state"
                ]["failure_counts"].get("premature_closure", 0),
                "orion_unavailable_case_recall": systems["orion_full"][
                    "by_case_family"
                ]["unavailable_route"]["mean_complete_gold_recall"],
                "ablated_unavailable_case_recall": systems[
                    "no_unavailable_route_open_state"
                ]["by_case_family"]["unavailable_route"][
                    "mean_complete_gold_recall"
                ],
            },
            "coverage_diagnostic_non_authority": {
                "orion_recall": systems["orion_full"]["mean_complete_gold_recall"],
                "ablated_recall": systems["coverage_diagnostic_controls_stopping"][
                    "mean_complete_gold_recall"
                ],
                "ablated_premature_closure_rate": systems[
                    "coverage_diagnostic_controls_stopping"
                ]["premature_task_closure_rate"],
            },
            "content_identity_dedup": {
                "orion_duplicate_processing_rate": systems["orion_full"][
                    "mean_duplicate_processing_rate"
                ],
                "ablated_duplicate_processing_rate": systems[
                    "no_content_identity_dedup"
                ]["mean_duplicate_processing_rate"],
                "orion_pass_rate": systems["orion_full"]["pass_rate"],
                "ablated_pass_rate": systems["no_content_identity_dedup"]["pass_rate"],
                "ablated_budget_exhaustion_failures": systems[
                    "no_content_identity_dedup"
                ]["failure_counts"].get("budget_exhausted", 0),
            },
        },
    }


def test_offline_archive_is_reproducible_and_matches_committed_snapshot() -> None:
    report = verify()
    assert report.ok, report.problems
    suite = load_suite()
    archive = run_offline_companion(
        suite.world,
        suite.tasks,
        run_manifest_hash=_manifest_hash(),
    )
    # Read from the manifest rather than written here as a literal: the suite's task
    # count is host-owned and moved once already to meet the frozen power
    # commitment, and an arithmetic literal turns that into an unrelated test
    # failure instead of a check on the archive's shape.
    manifest = load_manifest()
    expected_runs = manifest["task_count"] * len(DEFAULT_SEEDS) * len(ALL_SYSTEMS)
    assert len(archive.outcomes) == expected_runs
    assert archive.summary["n_result_records"] == expected_runs
    assert not any(item.record["status"] == "INVALID" for item in archive.outcomes)
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    assert _publication_projection(archive.summary) == expected


def test_offline_archive_carries_the_achieved_precision_the_plan_committed_to() -> None:
    """The family must state its achieved tier, and must not promote a primary.

    Reaching the committed N lifts the `DESCRIPTIVE_ONLY` label, which is one of the
    six conditions the frozen decision rule requires. This asserts the distinction
    holds in the artifact: tier reported, promotion withheld.
    """

    manifest = load_manifest()
    achieved = achieved_precision_tier(manifest["task_count"])

    assert achieved["committed_tier"] == "TIER_B_committed"
    assert achieved["committed_required_n"] == 385
    assert manifest["task_count"] >= achieved["committed_required_n"]
    assert achieved["committed_tier_met"] is True
    assert achieved["achieved_tier"] == "TIER_B_committed"
    assert achieved["achieved_tier_half_width"] == 0.05
    assert achieved["primary_promoted"] is False

    committed = json.loads(EXPECTED.read_text(encoding="utf-8"))
    assert committed["analysis_authority"] == "TIER_B_committed"
    assert committed["achieved_precision"]["primary_promoted"] is False
    # Half-widths must come from the bootstrap, never from the planning table.
    assert committed["achieved_precision"]["bootstrap"]["half_width_source"] == (
        "observed_percentile_bootstrap"
    )
    for key in (
        "orion_complete_gold_recall",
        "strongest_baseline_complete_gold_recall",
        "paired_orion_minus_strongest_baseline_recall",
    ):
        interval = committed["achieved_precision"][key]
        assert interval["n"] == manifest["task_count"]
        assert interval["ci_low"] <= interval["mean"] <= interval["ci_high"]


def test_below_the_inferential_floor_the_family_stays_descriptive_only() -> None:
    """The no-alarm and alarm cases for the tier classifier, on both sides.

    A tier function that only ever returns the tier this run achieved would pass the
    test above while silently having lost the floor that makes a small family
    descriptive. Both directions are asserted.
    """

    assert achieved_precision_tier(96)["achieved_tier"] == "DESCRIPTIVE_ONLY"
    assert achieved_precision_tier(96)["achieved_tier_half_width"] is None
    assert achieved_precision_tier(96)["committed_tier_met"] is False
    assert achieved_precision_tier(97)["achieved_tier"] == "TIER_D_minimum_inferential"
    assert achieved_precision_tier(171)["achieved_tier"] == "TIER_C_reduced"
    assert achieved_precision_tier(384)["achieved_tier"] == "TIER_C_reduced"
    assert achieved_precision_tier(385)["achieved_tier"] == "TIER_B_committed"
    assert achieved_precision_tier(1068)["achieved_tier"] == "TIER_A_full"
    # Never promoted, at any N.
    for n_tasks in (96, 97, 385, 1068, 100_000):
        assert achieved_precision_tier(n_tasks)["primary_promoted"] is False
