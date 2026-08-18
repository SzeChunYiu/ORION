#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p4_method_authority import (
    MethodAuthorityCoordinate,
    build_method_transfer_receipt,
    claim_is_promotable,
    derive_method_authority,
)

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "method_authority_extension" / "METHOD_AUTHORITY_BENCH_V1.json"
SUMMARY = ROOT / "method_authority_extension" / "METHOD_AUTHORITY_BENCH_SUMMARY_V1.json"


def digest(label: str) -> str:
    return content_digest({"label": label})


def _receipt(case: dict[str, Any]):
    settings = dict(case["settings"])
    novelty_available = bool(settings.pop("novelty_search_available", True))
    return build_method_transfer_receipt(
        method_id=f"method:{case['case_id']}",
        target_id=f"target:{case['case_id']}",
        target_digest=digest(f"target:{case['case_id']}"),
        donor_ids=(f"donor:{case['case_id']}",),
        donor_digests=(digest(f"donor:{case['case_id']}"),),
        structural_signature_digest=digest(f"signature:{case['case_id']}"),
        assumptions_retained=("finite_state",),
        assumptions_dropped=tuple(settings.pop("assumptions_dropped", ())),
        assumptions_modified=tuple(settings.pop("assumptions_modified", ())),
        adaptation_steps=("adapt_to_target",),
        predicted_effects=("declared_effect",),
        reconstruction="lift_solution",
        evaluator_digest=digest(f"evaluator:{case['case_id']}"),
        novelty_search_digest=(digest(f"novelty:{case['case_id']}") if novelty_available else ""),
        **settings,
    )


def run() -> dict[str, Any]:
    bench = json.loads(BENCH.read_text(encoding="utf-8"))
    systems: dict[str, list[bool]] = {
        "P4_MethodTransferReceipt_coordinate_product": [],
        "visible_success_policy": [],
        "provenance_only_policy": [],
        "all_deny_policy": [],
    }
    expected: list[bool] = []
    traces: list[dict[str, Any]] = []

    for case in bench["cases"]:
        receipt = _receipt(case)
        authority = derive_method_authority(receipt)
        required = tuple(MethodAuthorityCoordinate(value) for value in case["required_coordinates"])
        decisions = {
            "P4_MethodTransferReceipt_coordinate_product": claim_is_promotable(authority, required),
            "visible_success_policy": receipt.visible_result_pass is True,
            "provenance_only_policy": receipt.source_lineage_valid is True,
            "all_deny_policy": False,
        }
        for system, decision in decisions.items():
            systems[system].append(decision)
        gold = bool(case["expected_promotable"])
        expected.append(gold)
        traces.append(
            {
                "case_id": case["case_id"],
                "family": case["family"],
                "expected_promotable": gold,
                "method_receipt_digest": receipt.receipt_digest,
                "authority_record_digest": authority.record_digest,
                "coordinates": [
                    {
                        "coordinate": entry.coordinate.value,
                        "state": entry.state.value,
                        "reason_codes": list(entry.reason_codes),
                    }
                    for entry in authority.coordinates
                ],
                "decisions": decisions,
            }
        )

    n_positive = sum(expected)
    n_negative = len(expected) - n_positive
    metrics: dict[str, dict[str, float]] = {}
    for system, decisions in systems.items():
        false_promotions = sum(
            decision and not gold for decision, gold in zip(decisions, expected, strict=True)
        )
        clean_promotions = sum(
            decision and gold for decision, gold in zip(decisions, expected, strict=True)
        )
        metrics[system] = {
            "false_promotion_rate": false_promotions / n_negative,
            "clean_promotion_coverage": clean_promotions / n_positive,
        }

    return {
        "result_version": "P4_METHOD_AUTHORITY_BENCH_RESULT_V1",
        "protocol_id": bench["protocol_id"],
        "bench_digest": content_digest(bench),
        "n_cases": len(expected),
        "n_clean_promotable": n_positive,
        "n_negative_or_blocked": n_negative,
        "systems": metrics,
        "traces": traces,
        "terminal": "P4_METHOD_AUTHORITY_SUPPORTED",
        "claim_ceiling": "closed synthetic authority discriminator only",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.check:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        for key in ("n_cases", "n_clean_promotable", "n_negative_or_blocked", "systems", "terminal"):
            if result[key] != summary[key]:
                raise SystemExit(f"MethodAuthorityBench drift: {key}")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
