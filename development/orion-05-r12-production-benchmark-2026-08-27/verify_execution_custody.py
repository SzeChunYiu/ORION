#!/usr/bin/env python3
"""Verify immutable ORION-05 R12 failure, result, and comparison custody."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ROUND = ROOT / "development" / "orion-05-r12-production-benchmark-2026-08-27"
ATTEMPT_1 = ROUND / "attempt-1-job-3549585"
ATTEMPT_2 = ROUND / "attempt-2-job-3549607"
CANONICAL = (
    ROOT
    / "papers"
    / "orion-05-tare-expressivity"
    / "rounds"
    / "r12-production-benchmark"
    / "result"
)
STATUS = ROOT / "papers" / "orion-05-tare-expressivity" / "ORION05_R12_ROUND2_STATUS.json"
MACHINE_FIELDS = {"cpu_ns", "peak_rss_kib", "pid", "verification_ns", "wall_ns"}


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_meta(path: Path, expected: dict[str, Any]) -> None:
    assert path.is_file(), path
    assert path.stat().st_size == expected["bytes"], path
    assert digest(path) == expected["sha256"], path


def rows(path: Path) -> dict[str, dict[str, Any]]:
    parsed = [json.loads(line) for line in path.read_text().splitlines() if line]
    indexed = {row["attempt_id"]: row for row in parsed}
    assert len(indexed) == len(parsed)
    return indexed


def main() -> int:
    custody = load(ROUND / "EXECUTION_CUSTODY.json")
    comparison_path = ROUND / "ATTEMPT1_ATTEMPT2_COMPARISON.json"
    comparison = load(comparison_path)
    status = load(STATUS)

    for name, expected in custody["attempt_1"]["files"].items():
        check_meta(ATTEMPT_1 / name, expected)
    for name, expected in custody["attempt_2"]["files"].items():
        check_meta(ATTEMPT_2 / name, expected)
    for name, expected in custody["canonical_result"]["files"].items():
        check_meta(CANONICAL / name, expected)
        assert (CANONICAL / name).read_bytes() == (ATTEMPT_2 / name).read_bytes()
    check_meta(comparison_path, custody["comparison"])

    for line in (CANONICAL / "SHA256SUMS").read_text().splitlines():
        expected, raw_name = line.split(None, 1)
        path = CANONICAL / Path(raw_name).name
        assert digest(path) == expected, path

    first = rows(ATTEMPT_1 / "RAW_ATTEMPTS.jsonl")
    second = rows(ATTEMPT_2 / "RAW_ATTEMPTS.jsonl")
    assert first.keys() == second.keys()
    differences: dict[str, int] = {}
    for attempt_id in sorted(first):
        for key in sorted(set(first[attempt_id]) | set(second[attempt_id])):
            if first[attempt_id].get(key) != second[attempt_id].get(key):
                differences[key] = differences.get(key, 0) + 1
    assert set(differences) <= MACHINE_FIELDS
    assert differences == comparison["comparison"]["observed_different_field_counts"]
    assert len(first) == comparison["comparison"]["attempt_count_each"] == 120

    sys.path.insert(0, str(ROOT))
    from papers.orion_05_r12_production_benchmark import verify_result_bundle

    result = verify_result_bundle(CANONICAL)
    failure = load(ATTEMPT_1 / "FAILURE_RECEIPT.json")
    environment = load(ATTEMPT_2 / "BENCHMARK_ENVIRONMENT.json")
    assert result["terminal"] == status["terminal"] == custody["science_terminal"]
    assert result["rounds"] == {"consumed": 2, "maximum": 3, "science_status": "OPEN"}
    assert result["attempt_counts"] == {"completed": 108, "errors": 0, "timeouts": 12, "total": 120}
    assert result["full_subject"]["support_two_timeouts"] == 6
    assert result["full_subject"]["unrestricted_complete"] is True
    assert result["decision"]["positive_rule_satisfied"] is False
    assert failure["terminal"] == custody["attempt_1"]["disposition"]
    assert failure["authority"]["round2_consumed_by_this_wrapper_failure"] is False
    assert environment["commit"] == custody["frozen_chain"]["defect_only_repair_commit"]
    assert not custody["protected_task3_touched"]
    assert not status["protected_task3_touched"]
    print(custody["custody_terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
