#!/usr/bin/env python3
"""Regenerate P7 V2 contracts and their bounded reference-policy trace."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from papers.candidates.reproducibility_generators_v3 import (  # noqa: E402
    canonical_record,
    compare_or_write,
    load_jsonl,
    regenerate_jsonl,
    sha256_bytes,
    sha256_file,
)

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "instances_v1.jsonl"
SCHEMA = HERE / "instances_v2.schema.json"
OUTPUT = HERE / "instances_v2.jsonl"
TRACE = HERE / "navigation_trace_v2.json"


def oracle(case: dict[str, object]) -> str:
    if case["topology_change_required"] is True:
        return "REFRAME"
    if case["family"] in {"unknown_coverage", "censored_route"} or case["censored_regions"]:
        return "CANNOT_CHECK"
    if case["family"] == "deceptive_route_diversity":
        return "ROUTE_STOP"
    return "TASK_STOP"


def records() -> list[dict[str, object]]:
    cases = load_jsonl(SOURCE)
    terminals = Counter(str(case.get("expected_terminal")) for case in cases)
    if len(cases) != 8:
        raise ValueError("P7 V2 freezes exactly eight authored contract cases")
    if set(terminals) != {"TASK_STOP", "ROUTE_STOP", "REFRAME", "CANNOT_CHECK"}:
        raise ValueError("P7 terminal coverage is incomplete")
    if not any(case.get("negative_control") is True for case in cases):
        raise ValueError("P7 requires a harmful-reframe negative control")
    for case in cases:
        observed = oracle(case)
        if observed != case.get("expected_terminal"):
            raise ValueError(f"P7 reference oracle disagrees for {case.get('id')}")
    return cases


def trace_payload(cases: list[dict[str, object]], output_bytes: bytes) -> bytes:
    rows = []
    for case in cases:
        observed = oracle(case)
        rows.append(
            {
                "case_id": case["id"],
                "raw_input_sha256": sha256_bytes(canonical_record(case)),
                "decision_opportunities_registered": 1,
                "decision_opportunities_evaluated": 1,
                "observed_terminal": observed,
                "expected_terminal": case["expected_terminal"],
                "trace": [
                    "LOAD_FROZEN_CONTRACT",
                    "EVALUATE_REFERENCE_POLICY",
                    f"TERMINAL:{observed}",
                ],
            }
        )
    payload = {
        "schema_version": "orion.p7.reference-policy-trace.v2",
        "authority_scope": "REFERENCE_POLICY_PREFLIGHT_ONLY",
        "live_agent_executed": False,
        "independent_replay": False,
        "independent_unit": "one authored P7 contract case",
        "case_opportunities_registered": len(cases),
        "case_opportunities_evaluated": len(rows),
        "zero_opportunity_pass_prohibited": True,
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": sha256_file(SOURCE),
        "generated_dataset": OUTPUT.relative_to(ROOT).as_posix(),
        "generated_dataset_sha256": sha256_bytes(output_bytes),
        "rows": rows,
    }
    if not rows or payload["case_opportunities_evaluated"] != payload["case_opportunities_registered"]:
        raise ValueError("P7 trace has zero or missing decision opportunities")
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    cases = records()
    output_bytes = regenerate_jsonl(
        source=SOURCE,
        schema_path=SCHEMA,
        target=OUTPUT,
        records=cases,
        check=args.check,
    )
    compare_or_write(TRACE, trace_payload(cases, output_bytes), check=args.check)
    print("P7 V2 GENERATOR+TRACE: MATCH" if args.check else "P7 V2 GENERATOR+TRACE: WROTE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
