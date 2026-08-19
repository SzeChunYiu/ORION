#!/usr/bin/env python3
"""Run leak-resistant V2 #501 benchmark and independent reconstruction."""

from __future__ import annotations

import json
from pathlib import Path

from orion.discovery.zero_error_jump_benchmark import (
    JumpArm,
    build_zero_error_jump_benchmark_report,
)
from orion.discovery.zero_error_jump_independent import (
    independently_verify_zero_error_jump,
)


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "ZERO_ERROR_JUMP_PROTOCOL_V2.json"
EXPECTED = HERE / "ZERO_ERROR_JUMP_EXPECTED_V2.json"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    protocol = _load(PROTOCOL)
    expected = _load(EXPECTED)
    report = build_zero_error_jump_benchmark_report(
        protocol=protocol,
        expected=expected,
    )
    independent = independently_verify_zero_error_jump(
        protocol=protocol,
        expected=expected,
    )
    payload = {
        "version": "ZeroErrorJumpReplaySummary.v2",
        "terminal": report.terminal.value,
        "all_checks_passed": report.all_checks_passed,
        "primary": {
            "seed": report.primary.seed,
            "cases": report.primary.case_count,
            "positive": report.primary.positive_count,
            "controls": report.primary.control_count,
            "strong_parent": report.primary.metric(
                JumpArm.VERIFIED_REGIME_REVISION_PARENT
            ).metric_payload(),
            "orion": report.primary.metric(JumpArm.ORION_JUMP).metric_payload(),
        },
        "replication": {
            "seed": report.replication.seed,
            "cases": report.replication.case_count,
            "positive": report.replication.positive_count,
            "controls": report.replication.control_count,
            "strong_parent": report.replication.metric(
                JumpArm.VERIFIED_REGIME_REVISION_PARENT
            ).metric_payload(),
            "orion": report.replication.metric(JumpArm.ORION_JUMP).metric_payload(),
        },
        "independent_reconstruction": {
            "expected_match": independent.expected_match,
            "terminal": independent.terminal.value,
            "parent_orion_decisions_equal_primary": independent.parent_orion_decisions_equal_primary,
            "parent_orion_decisions_equal_replication": independent.parent_orion_decisions_equal_replication,
            "parent_orion_metrics_equal_primary": independent.parent_orion_metrics_equal_primary,
            "parent_orion_metrics_equal_replication": independent.parent_orion_metrics_equal_replication,
        },
        "authority": {
            "grants_scientific_adoption": False,
            "grants_open_ended_creativity": False,
            "grants_novelty_authority": False,
            "grants_issue_closure_authority": False,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
