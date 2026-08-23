#!/usr/bin/env python3
"""Prospective fail-closed P2 comparison-resolution precondition."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

PASS_TERMINAL = "P2_COMPARISON_RESOLUTION_PRECONDITION_PASS"
FAIL_TERMINAL = "P2_COMPARISON_CANNOT_CHECK_ZERO_OR_INVALID_RESOLUTION"


def assess(summary: Mapping[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    arms = int(summary.get("arms", 0) or 0)
    if arms < 2:
        failures.append("AT_LEAST_TWO_ARMS")
    if int(summary.get("distinct_candidate_digests", 0) or 0) < 2:
        failures.append("DISTINCT_CANDIDATE_ARTIFACTS")
    if int(summary.get("distinct_evaluator_digests", 0) or 0) < 2:
        failures.append("DISTINCT_EVALUATOR_OUTPUTS")

    floor = summary.get("floor")
    if not isinstance(floor, Mapping) or floor.get("checked") is not True:
        failures.append("ABSOLUTE_SCORE_SCALE_CHECK_MISSING")
    else:
        best = floor.get("best_arm_avg_iou")
        required = floor.get("required_avg_iou_delta")
        if not isinstance(best, (int, float)) or not isinstance(required, (int, float)):
            failures.append("ABSOLUTE_SCORE_SCALE_MALFORMED")
        elif float(best) < float(required):
            failures.append("ABSOLUTE_SCORE_SCALE_REACHES_EFFECT_MARGIN")

    paired = summary.get("paired")
    if not isinstance(paired, Mapping):
        failures.append("PAIRED_SPLIT_MISSING")
    else:
        n = int(paired.get("n", 0) or 0)
        wins = int(paired.get("wins", 0) or 0)
        losses = int(paired.get("losses", 0) or 0)
        ties = int(paired.get("ties", 0) or 0)
        if n <= 0 or wins + losses <= 0:
            failures.append("PAIRED_SPLIT_HAS_DISCORDANCE")
        low = paired.get("ci95_low")
        high = paired.get("ci95_high")
        if n > 0 and ties == n and wins == 0 and losses == 0 and low == 0 and high == 0:
            failures.append("NO_ALL_TIES_ZERO_WIDTH_EQUIVALENCE")

    if summary.get("non_monotone_at_k"):
        failures.append("MONOTONE_SAMPLED_MAX_FAMILY_IF_PRESENT")
    if summary.get("sampled_family_published"):
        warnings.append("UNSEEDED_SAMPLED_FAMILY_CANNOT_AUTHORIZE_TERMINAL")
    if summary.get("absent_runtime_totals"):
        failures.append("RUNTIME_TOTALS_MEASURED")

    failures = list(dict.fromkeys(failures))
    return {
        "schema_version": "orion.p2.comparison-resolution-assessment.v1",
        "passed": not failures,
        "terminal": PASS_TERMINAL if not failures else FAIL_TERMINAL,
        "failed_checks": failures,
        "reporting_warnings": warnings,
        "scientific_authority": "NONE",
        "interpretation": (
            "instrument has measured resolution; scientific result still requires the frozen campaign rule"
            if not failures
            else "instrument cannot carry superiority, non-inferiority, or equivalence evidence"
        ),
    }


def authorize_scientific_terminal(
    summary: Mapping[str, Any], requested_terminal: str
) -> dict[str, Any]:
    gate = assess(summary)
    if not gate["passed"]:
        return {
            "requested_terminal": requested_terminal,
            "terminal": FAIL_TERMINAL,
            "authorized": False,
            "resolution_gate": gate,
        }
    return {
        "requested_terminal": requested_terminal,
        "terminal": requested_terminal,
        "authorized": True,
        "resolution_gate": gate,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--campaign", required=True)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    payload = json.loads(args.summary.read_text(encoding="utf-8"))
    summary = payload.get("campaigns", {}).get(args.campaign)
    if not isinstance(summary, Mapping):
        raise SystemExit(f"campaign not found: {args.campaign}")
    result = assess(summary)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["passed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
