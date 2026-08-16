"""Freeze the P2 offline publication snapshot after the run manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from orion.study.p2.corpus import canonical_bytes
from orion.study.p2.freeze import load_suite, verify
from orion.study.p2.offline_analysis import run_offline_companion

PAPER = Path("papers/paper-02-open-world-scientific-discovery")
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
    assert len(archive.outcomes) == 20 * 3 * 14
    assert not any(item.record["status"] == "INVALID" for item in archive.outcomes)
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    assert _publication_projection(archive.summary) == expected
