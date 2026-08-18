#!/usr/bin/env python3
"""Execute the frozen P7 V2 contract manifest.

The manifest is a prospective/reference contract oracle, not a learned-agent
result. It absorbs the parallel mathematical-completion lane's eight cases.
"""
from __future__ import annotations

import json
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "benchmark" / "instances_v2.jsonl"

VALID_TERMINALS = {"TASK_STOP", "ROUTE_STOP", "REFRAME", "DEFER", "CANNOT_CHECK"}


def load_cases() -> list[dict]:
    return [json.loads(line) for line in MANIFEST.read_text().splitlines() if line.strip()]


def oracle(case: dict) -> str:
    if case["topology_change_required"]:
        return "REFRAME"
    if case["family"] in {"unknown_coverage", "censored_route"} or case["censored_regions"]:
        return "CANNOT_CHECK"
    if case["family"] == "deceptive_route_diversity":
        return "ROUTE_STOP"
    return "TASK_STOP"


def validate(case: dict) -> None:
    required = {
        "id", "family", "domain", "topology_change_required",
        "mandatory_obligations", "censored_regions", "negative_control",
        "expected_terminal", "gold",
    }
    assert required <= set(case), (case.get("id"), sorted(required - set(case)))
    assert case["expected_terminal"] in VALID_TERMINALS
    assert isinstance(case["mandatory_obligations"], list) and case["mandatory_obligations"]
    assert isinstance(case["censored_regions"], list)
    assert isinstance(case["gold"], dict)
    if case["negative_control"]:
        assert not case["topology_change_required"]
    assert oracle(case) == case["expected_terminal"], case["id"]


def main() -> int:
    cases = load_cases()
    assert len(cases) == 8
    assert len({c["id"] for c in cases}) == len(cases)
    for case in cases:
        validate(case)

    by_domain = {c["domain"] for c in cases}
    assert "experimental_design" in by_domain  # non-retrieval transfer
    assert any(c["negative_control"] and c["gold"].get("reframe_harmful") for c in cases)
    assert any(c["censored_regions"] for c in cases)
    assert any(c["family"] == "hidden_useful_branch" for c in cases)
    assert any(c["family"] == "deceptive_route_diversity" for c in cases)

    print("P7 CONTRACT MANIFEST V2: PASS")
    print(f"cases: {len(cases)}")
    print(f"domains: {sorted(by_domain)}")
    print("claim boundary: reference contract execution only; no live-agent efficacy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
