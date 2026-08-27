from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from papers.orion_05_r12_production_benchmark import (
    adjudicate_rows,
    attempt_schedule,
    load_protocol,
    load_subject_panels,
    project_key,
    rss_to_kib,
)


def test_protocol_subject_targets_reconstruct_consistently() -> None:
    protocol = load_protocol()
    panels = load_subject_panels(protocol)

    assert set(panels) == {"H4", "N2"}
    assert panels["H4"]["n_qubits"] == 8
    assert panels["N2"]["n_qubits"] == 12
    assert panels["H4"]["selected_matching_indices"] == (0, 7, 14)
    assert panels["N2"]["selected_matching_indices"] == (0, 7, 14)
    assert len(panels["H4"]["target_by_index"]) == 6
    assert len(panels["N2"]["target_by_index"]) == 6
    assert panels["H4"]["all_matching_target_maps_consistent"] is True
    assert panels["N2"]["all_matching_target_maps_consistent"] is True


def test_projection_retains_only_least_significant_coordinates() -> None:
    assert project_key((0b1101, 0b1011), 1) == (1, 1)
    assert project_key((0b1101, 0b1011), 2) == (1, 3)
    assert project_key((0b1101, 0b1011), 4) == (13, 11)
    with pytest.raises(ValueError):
        project_key((1, 1), 0)


def test_schedule_has_three_completed_panel_repeats_and_one_scale_probe() -> None:
    protocol = load_protocol()
    schedule = attempt_schedule(protocol)
    correctness = [row for row in schedule if row["projection"] in (1, 2)]
    scale_sparse = [
        row
        for row in schedule
        if row["projection"] in (3, "FULL_SUBJECT") and row["algorithm"] == "support_two"
    ]
    scale_dp = [
        row
        for row in schedule
        if row["projection"] in (3, "FULL_SUBJECT") and row["algorithm"] == "unrestricted_dp"
    ]
    assert len(correctness) == 2 * 3 * 2 * 2 * 3
    assert len(scale_sparse) == 2 * 3 * 2
    assert len(scale_dp) == 2 * 3 * 2 * 3
    assert len({row["attempt_id"] for row in schedule}) == len(schedule)


def _success_row(subject: str, matching_index: int, projection, algorithm: str, repeat: int):
    from papers.orion_05_r12_production_benchmark import _attempt_id

    metric = 100 if algorithm == "unrestricted_dp" else 70
    spec = {
        "subject": subject,
        "matching_index": matching_index,
        "projection": projection,
        "algorithm": algorithm,
        "repeat": repeat,
    }
    return {
        "attempt_id": _attempt_id(spec),
        "subject": subject,
        "matching_index": matching_index,
        "projection": projection,
        "algorithm": algorithm,
        "repeat": repeat,
        "status": "COMPLETED",
        "cost": 7,
        "witness_valid": True,
        "wall_ns": metric,
        "cpu_ns": metric,
        "peak_rss_kib": metric,
        "verification_ns": metric,
    }


def _complete_rows(protocol):
    rows = []
    for spec in attempt_schedule(protocol):
        rows.append(
            _success_row(
                spec["subject"],
                spec["matching_index"],
                spec["projection"],
                spec["algorithm"],
                spec["repeat"],
            )
        )
        if spec["algorithm"] == "support_two" and spec["projection"] in (3, "FULL_SUBJECT"):
            for repeat in (1, 2):
                rows.append(
                    _success_row(
                        spec["subject"], spec["matching_index"], spec["projection"], spec["algorithm"], repeat
                    )
                )
    return rows


def test_adjudication_emits_positive_only_for_complete_pareto_improvement() -> None:
    protocol = load_protocol()
    result = adjudicate_rows(protocol, _complete_rows(protocol), source_bindings_ok=True)
    assert result["terminal"] == "ORION05_R12_PRODUCTION_EXACT_SEARCH_VALUE_PASS"
    assert result["rounds"]["consumed"] == 2


def test_adjudication_preserves_timeout_as_null_not_positive() -> None:
    protocol = load_protocol()
    rows = _complete_rows(protocol)
    victim = next(
        row
        for row in rows
        if row["algorithm"] == "support_two" and row["projection"] == "FULL_SUBJECT"
    )
    rows = [row for row in rows if not (
        row["subject"] == victim["subject"]
        and row["matching_index"] == victim["matching_index"]
        and row["projection"] == victim["projection"]
        and row["algorithm"] == victim["algorithm"]
    )]
    timeout = copy.deepcopy(victim)
    timeout.update({"repeat": 0, "status": "TIMEOUT", "cost": None, "witness_valid": None})
    rows.append(timeout)
    result = adjudicate_rows(protocol, rows, source_bindings_ok=True)
    assert result["terminal"] == "ORION05_R12_EXACT_BUT_NO_PRODUCTION_VALUE"
    assert result["full_subject"]["support_two_timeouts"] == 1


def test_adjudication_uses_cannot_check_for_cost_disagreement() -> None:
    protocol = load_protocol()
    rows = _complete_rows(protocol)
    sparse = next(
        row
        for row in rows
        if row["algorithm"] == "support_two" and row["projection"] == 1
    )
    sparse["cost"] = 8
    result = adjudicate_rows(protocol, rows, source_bindings_ok=True)
    assert result["terminal"] == "ORION05_R12_CANNOT_CHECK_MATCHED_PRODUCTION_VALUE"
    assert result["preconditions"]["all_shared_completed_costs_equal"] is False


def test_peak_rss_units_are_normalized_across_supported_hosts() -> None:
    assert rss_to_kib(1024, system="Linux") == 1024
    assert rss_to_kib(1024 * 1024, system="Darwin") == 1024


def _write_bundle(tmp_path, protocol, rows):
    from papers.orion_05_r12_production_benchmark import canonical_json, sha256_file

    raw = tmp_path / "RAW_ATTEMPTS.jsonl"
    raw.write_text("".join(canonical_json(row) + "\n" for row in sorted(rows, key=lambda row: row["attempt_id"])))
    environment = tmp_path / "BENCHMARK_ENVIRONMENT.json"
    environment.write_text('{"commit":"runner-test"}\n')
    result = adjudicate_rows(protocol, rows, source_bindings_ok=True)
    result.update(
        {
            "protocol_sha256": sha256_file(
                Path("papers/orion-05-tare-expressivity/rounds/r12-production-benchmark/ORION05_R12_PRODUCTION_BENCHMARK_PROTOCOL.json")
            ),
            "raw_attempts_sha256": sha256_file(raw),
            "environment_sha256": sha256_file(environment),
        }
    )
    (tmp_path / "ORION05_R12_PRODUCTION_BENCHMARK_RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )


def test_result_bundle_verifier_recomputes_the_frozen_decision(tmp_path) -> None:
    from papers.orion_05_r12_production_benchmark import verify_result_bundle

    protocol = load_protocol()
    _write_bundle(tmp_path, protocol, _complete_rows(protocol))
    verified = verify_result_bundle(tmp_path, require_current_source_bindings=False)
    assert verified["terminal"] == "ORION05_R12_PRODUCTION_EXACT_SEARCH_VALUE_PASS"


def test_result_bundle_verifier_rejects_raw_attempt_mutation(tmp_path) -> None:
    from papers.orion_05_r12_production_benchmark import verify_result_bundle

    protocol = load_protocol()
    _write_bundle(tmp_path, protocol, _complete_rows(protocol))
    with (tmp_path / "RAW_ATTEMPTS.jsonl").open("a") as handle:
        handle.write('{"attempt_id":"tampered"}\n')
    with pytest.raises(AssertionError):
        verify_result_bundle(tmp_path, require_current_source_bindings=False)


def test_archive_deployment_resolves_exact_bound_source_commit(tmp_path) -> None:
    from papers.orion_05_r12_production_benchmark import resolve_source_commit

    commit = "7fdea61e44f62b3595c4f1863fefffdd7132b68a"
    (tmp_path / "SOURCE_COMMIT.txt").write_text(commit + "\n")
    assert resolve_source_commit(tmp_path, {"ORION05_R12_SOURCE_COMMIT": commit}) == commit
    with pytest.raises(AssertionError):
        resolve_source_commit(tmp_path, {"ORION05_R12_SOURCE_COMMIT": "0" * 40})


def test_committed_round2_bundle_replays_to_frozen_null_terminal() -> None:
    from papers.orion_05_r12_production_benchmark import verify_result_bundle

    result_dir = Path(
        "papers/orion-05-tare-expressivity/rounds/r12-production-benchmark/result"
    )
    verified = verify_result_bundle(result_dir)
    assert verified["terminal"] == "ORION05_R12_EXACT_BUT_NO_PRODUCTION_VALUE"
    assert verified["rounds"] == {
        "consumed": 2,
        "maximum": 3,
        "science_status": "OPEN",
    }
    assert verified["attempt_counts"] == {
        "completed": 108,
        "errors": 0,
        "timeouts": 12,
        "total": 120,
    }


def test_attempt1_and_attempt2_have_identical_scientific_outcomes() -> None:
    from papers.orion_05_r12_production_benchmark import (
        compare_attempt_scientific_outcomes,
    )

    packet = Path("development/orion-05-r12-production-benchmark-2026-08-27")
    comparison = compare_attempt_scientific_outcomes(
        packet / "attempt-1-job-3549585" / "RAW_ATTEMPTS.jsonl",
        packet / "attempt-2-job-3549607" / "RAW_ATTEMPTS.jsonl",
    )
    assert comparison == {
        "attempt_ids_equal": True,
        "attempts_compared": 120,
        "scientific_mismatch_count": 0,
        "scientific_mismatch_attempt_ids": [],
        "status_counts": {"COMPLETED": 108, "TIMEOUT": 12},
    }
