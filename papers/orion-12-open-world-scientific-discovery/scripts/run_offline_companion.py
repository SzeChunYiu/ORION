#!/usr/bin/env python3
"""Regenerate or verify the frozen P2 offline complete-gold companion.

This is a publication-layer command.  It never changes the frozen protocol or
subject code: it reads ``OFFLINE_RUN_MANIFEST_V1.json``, verifies the committed
suite, executes the bound systems under the three bound repeat seeds, and then
projects the rich analysis summary into the compact publication summary checked
into ``evidence/offline_results``.

Examples::

    python3 papers/paper-02-open-world-scientific-discovery/scripts/run_offline_companion.py --check
    python3 papers/paper-02-open-world-scientific-discovery/scripts/run_offline_companion.py --stdout
    python3 papers/paper-02-open-world-scientific-discovery/scripts/run_offline_companion.py --write-raw /tmp/p2-offline

``--write-raw`` writes all 840 normalized result records and all rich per-run
artifacts.  Those files are regenerable evidence; the committed summary carries
cryptographic digests of both complete sets so a reproduction can be compared
without committing hundreds of generated files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from orion.study.p2.corpus import canonical_bytes
from orion.study.p2.freeze import load_suite, verify
from orion.study.p2.offline_analysis import run_offline_companion
from orion.study.p2.runner import write_artifacts, write_records

PAPER = Path(__file__).resolve().parents[1]
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


def manifest_hash() -> str:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    computed = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    recorded = MANIFEST_SHA.read_text(encoding="utf-8").split()[0]
    if computed != recorded:
        raise ValueError(f"run-manifest sidecar mismatch: {computed} != {recorded}")
    if payload.get("outcome_accessed_before_freeze") is not False:
        raise ValueError("run manifest does not preserve prospective outcome blindness")
    return computed


def publication_projection(summary: dict) -> dict:
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


def regenerate() -> tuple[dict, tuple]:
    report = verify()
    if not report.ok:
        raise ValueError("frozen suite verification failed: " + "; ".join(report.problems))
    suite = load_suite()
    archive = run_offline_companion(
        suite.world,
        suite.tasks,
        run_manifest_hash=manifest_hash(),
    )
    if any(item.record["status"] == "INVALID" for item in archive.outcomes):
        raise ValueError("frozen archive contains INVALID outcomes")
    return publication_projection(archive.summary), archive.outcomes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify committed summary")
    parser.add_argument("--stdout", action="store_true", help="print regenerated summary")
    parser.add_argument("--write-raw", type=Path, help="write JSONL records and rich artifacts")
    args = parser.parse_args(argv)

    projection, outcomes = regenerate()
    if args.stdout:
        print(json.dumps(projection, sort_keys=True, indent=2))
    if args.write_raw is not None:
        args.write_raw.mkdir(parents=True, exist_ok=True)
        count = write_records(outcomes, args.write_raw / "RESULT_RECORDS_V1.jsonl")
        written = write_artifacts(outcomes, args.write_raw / "artifacts")
        print(f"wrote {count} records and {len(written)} artifacts under {args.write_raw}")
    if args.check or (not args.stdout and args.write_raw is None):
        expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
        if projection != expected:
            print("offline publication summary drifted from the frozen run", file=sys.stderr)
            return 1
        print("offline publication summary matches the frozen 840-run archive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
