#!/usr/bin/env python3
"""Execute the frozen P8 V2 authority contract manifest.

Reference-policy contract execution only; not a real-agent efficacy benchmark.
"""
from __future__ import annotations

import json
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "benchmark" / "authority_cases_v2.jsonl"
DOMAINS = {"REFRAME", "SEARCH_STOP", "MAP_MERGE", "ASSERT", "SELF_MODIFY"}
VERDICTS = {"AUTHORIZED", "REJECT", "CANNOT_CHECK", "UNAUTHORIZED"}


def load_cases() -> list[dict]:
    return [json.loads(line) for line in MANIFEST.read_text().splitlines() if line.strip()]


def evaluate(case: dict) -> str:
    hard = set(case["hard_obligations"])
    satisfied = set(case["satisfied"])
    unknown = set(case.get("unknown_obligations", []))
    defeaters = set(case["defeaters"])
    if defeaters:
        return "REJECT"
    missing = hard - satisfied
    if missing & unknown:
        return "CANNOT_CHECK"
    if missing:
        return "UNAUTHORIZED"
    source = case["source_signal_domain"]
    target = case["domain"]
    if source != target:
        allowed = {tuple(pair) for pair in case.get("registered_coercions", [])}
        if (source, target) not in allowed:
            return "UNAUTHORIZED"
    return "AUTHORIZED"


def validate(case: dict) -> None:
    required = {
        "id", "pair_id", "domain", "action", "hard_obligations", "satisfied",
        "defeaters", "source_signal_domain", "expected_verdict", "clean_authorized",
    }
    assert required <= set(case), (case.get("id"), sorted(required - set(case)))
    assert case["domain"] in DOMAINS
    assert case["source_signal_domain"] in DOMAINS
    assert case["expected_verdict"] in VERDICTS
    for field in ("hard_obligations", "satisfied", "defeaters"):
        assert isinstance(case[field], list) and all(isinstance(x, str) for x in case[field])
    assert evaluate(case) == case["expected_verdict"], case["id"]
    assert bool(case["clean_authorized"]) == (case["expected_verdict"] == "AUTHORIZED")


def main() -> int:
    cases = load_cases()
    assert len(cases) == 17
    assert len({c["id"] for c in cases}) == 17
    for case in cases:
        validate(case)

    clean_by_domain = {c["domain"] for c in cases if c["clean_authorized"] and c["source_signal_domain"] == c["domain"]}
    assert clean_by_domain == DOMAINS
    laundering = [c for c in cases if c["id"].startswith("P8-LAUNDER-")]
    assert len(laundering) == 5 and all(c["expected_verdict"] == "UNAUTHORIZED" for c in laundering)
    assert any(c["expected_verdict"] == "CANNOT_CHECK" for c in cases)
    assert any(c.get("registered_coercions") and c["expected_verdict"] == "AUTHORIZED" for c in cases)

    print("P8 CONTRACT MANIFEST V2: PASS")
    print(f"cases: {len(cases)}")
    print(f"clean domains: {sorted(clean_by_domain)}")
    print(f"explicit laundering attacks blocked: {len(laundering)}")
    print("claim boundary: reference contract execution only; no live-agent efficacy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
