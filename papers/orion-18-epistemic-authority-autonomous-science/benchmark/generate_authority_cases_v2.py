#!/usr/bin/env python3
"""Regenerate P8 V2 contracts and the local laundering-attack replay."""

from __future__ import annotations

import argparse
import json
import sys
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
SOURCE = HERE / "authority_cases_v1.jsonl"
SCHEMA = HERE / "authority_cases_v2.schema.json"
OUTPUT = HERE / "authority_cases_v2.jsonl"
ATTACK_RESULT = (
    HERE.parent / "evidence" / "local" / "cross_capability_attack_replay_result_v2.json"
)
DOMAINS = {"REFRAME", "SEARCH_STOP", "MAP_MERGE", "ASSERT", "SELF_MODIFY"}


def evaluate(case: dict[str, object]) -> str:
    hard = set(case["hard_obligations"])
    satisfied = set(case["satisfied"])
    unknown = set(case.get("unknown_obligations", []))
    if case["defeaters"]:
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


def records() -> list[dict[str, object]]:
    cases = load_jsonl(SOURCE)
    if len(cases) != 17:
        raise ValueError("P8 V2 freezes exactly 17 authored contract cases")
    clean_domains = {
        str(case["domain"])
        for case in cases
        if case.get("clean_authorized") is True
        and case.get("source_signal_domain") == case.get("domain")
    }
    if clean_domains != DOMAINS:
        raise ValueError("P8 deny-all guard requires one clean authorization per domain")
    for case in cases:
        observed = evaluate(case)
        if observed != case.get("expected_verdict"):
            raise ValueError(f"P8 reference evaluator disagrees for {case.get('id')}")
    return cases


def attack_payload(cases: list[dict[str, object]], output_bytes: bytes) -> bytes:
    attacks = [case for case in cases if str(case["id"]).startswith("P8-LAUNDER-")]
    rows = []
    for case in attacks:
        verdict = evaluate(case)
        rows.append(
            {
                "case_id": case["id"],
                "raw_input_sha256": sha256_bytes(canonical_record(case)),
                "attack_opportunities_registered": 1,
                "attack_opportunities_evaluated": 1,
                "observed_verdict": verdict,
                "expected_verdict": case["expected_verdict"],
                "blocked": verdict == "UNAUTHORIZED",
            }
        )
    payload = {
        "schema_version": "orion.p8.local-attack-replay.v2",
        "authority_scope": "LOCAL_REFERENCE_POLICY_PREFLIGHT_ONLY",
        "grants_scientific_authority": "NONE",
        "self_authorizing": True,
        "independent_custody": False,
        "protected_labels_used": False,
        "independent_unit": "one authored laundering attack contract",
        "total_reference_cases": len(cases),
        "attack_opportunities_registered": len(attacks),
        "attack_opportunities_evaluated": len(rows),
        "attacks_blocked": sum(bool(row["blocked"]) for row in rows),
        "zero_opportunity_pass_prohibited": True,
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": sha256_file(SOURCE),
        "generated_dataset": OUTPUT.relative_to(ROOT).as_posix(),
        "generated_dataset_sha256": sha256_bytes(output_bytes),
        "rows": rows,
    }
    opportunities = payload["attack_opportunities_registered"]
    if opportunities != 5 or payload["attack_opportunities_evaluated"] != opportunities:
        raise ValueError("P8 attack replay must evaluate five registered laundering attacks")
    if payload["attacks_blocked"] != opportunities:
        raise ValueError("P8 local reference policy did not block every registered attack")
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
    compare_or_write(ATTACK_RESULT, attack_payload(cases, output_bytes), check=args.check)
    print("P8 V2 GENERATOR+ATTACK: MATCH" if args.check else "P8 V2 GENERATOR+ATTACK: WROTE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
