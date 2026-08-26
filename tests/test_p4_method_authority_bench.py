from __future__ import annotations

import json
from pathlib import Path

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p4_method_authority import (
    MethodAuthorityCoordinate,
    build_method_transfer_receipt,
    claim_is_promotable,
    derive_method_authority,
)

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "orion-14-verified-scientific-discovery"
BENCH = PAPER / "method_authority_extension" / "METHOD_AUTHORITY_BENCH_V1.json"
SUMMARY = PAPER / "method_authority_extension" / "METHOD_AUTHORITY_BENCH_SUMMARY_V1.json"


def digest(label: str) -> str:
    return content_digest({"label": label})


def _receipt(case: dict[str, object]):
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
        novelty_search_digest=(
            digest(f"novelty:{case['case_id']}") if novelty_available else ""
        ),
        **settings,
    )


def _required(case: dict[str, object]) -> tuple[MethodAuthorityCoordinate, ...]:
    return tuple(MethodAuthorityCoordinate(value) for value in case["required_coordinates"])


def test_method_authority_bench_reproduces_frozen_summary():
    bench = json.loads(BENCH.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    systems = {
        "P4_MethodTransferReceipt_coordinate_product": [],
        "visible_success_policy": [],
        "provenance_only_policy": [],
        "all_deny_policy": [],
    }
    expected: list[bool] = []

    for case in bench["cases"]:
        rec = _receipt(case)
        authority = derive_method_authority(rec)
        required = _required(case)
        systems["P4_MethodTransferReceipt_coordinate_product"].append(
            claim_is_promotable(authority, required)
        )
        systems["visible_success_policy"].append(rec.visible_result_pass is True)
        systems["provenance_only_policy"].append(rec.source_lineage_valid is True)
        systems["all_deny_policy"].append(False)
        expected.append(bool(case["expected_promotable"]))

    n_positive = sum(expected)
    n_negative = len(expected) - n_positive
    assert n_positive == summary["n_clean_promotable"]
    assert n_negative == summary["n_negative_or_blocked"]

    for system_name, decisions in systems.items():
        false_promotions = sum(
            decision and not gold for decision, gold in zip(decisions, expected, strict=True)
        )
        clean_promotions = sum(
            decision and gold for decision, gold in zip(decisions, expected, strict=True)
        )
        observed = {
            "false_promotion_rate": false_promotions / n_negative,
            "clean_promotion_coverage": clean_promotions / n_positive,
        }
        assert observed == summary["systems"][system_name]

    assert summary["terminal"] == "P4_METHOD_AUTHORITY_SUPPORTED"
    assert summary["systems"]["P4_MethodTransferReceipt_coordinate_product"] == {
        "false_promotion_rate": 0.0,
        "clean_promotion_coverage": 1.0,
    }
    assert summary["systems"]["all_deny_policy"]["clean_promotion_coverage"] == 0.0


def test_benchmark_contains_required_hostile_and_clean_families():
    bench = json.loads(BENCH.read_text(encoding="utf-8"))
    families = {case["family"] for case in bench["cases"]}
    assert {
        "VALID_KNOWN_TRANSFER",
        "INVALID_TRANSFER_ASSUMPTION_DELETION",
        "STRUCTURAL_LOOKALIKE_BAD_RECONSTRUCTION",
        "USEFUL_ALREADY_KNOWN",
        "KNOWN_COMPOSITION_NOT_NEW_PRIMITIVE",
        "GENUINE_SYNTHETIC_NOVELTY",
        "VISIBLE_SUCCESS_FRESH_PROTECTED_FAILURE",
        "NOVELTY_ROUTE_UNAVAILABLE",
        "EVALUATOR_LEAKAGE",
        "CLEAN_FULLY_EVIDENCED_METHOD",
    } <= families
