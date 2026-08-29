#!/usr/bin/env python3
"""Fail-closed exact checks for ten ORION interpretation risks."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Sequence

GREEN = "ORION_OPERATIONAL_GAP_AUDITS_V1_GREEN"
RED = "ORION_OPERATIONAL_GAP_AUDITS_V1_RED"


def close(actual: float, expected: float, tolerance: float = 1e-12) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance):
        raise AssertionError(f"numeric mismatch: actual={actual}, expected={expected}")


def all_success_cp_lower(n: int, alpha_two_sided: float) -> float:
    if n < 1 or not 0.0 < alpha_two_sided < 1.0:
        raise ValueError("invalid all-success interval inputs")
    return (alpha_two_sided / 2.0) ** (1.0 / n)


def binomial_upper_tail(n: int, threshold: int, p: float) -> float:
    return sum(
        math.comb(n, k) * (p**k) * ((1.0 - p) ** (n - k))
        for k in range(threshold, n + 1)
    )


def exact_mcnemar(b: int, c: int) -> tuple[float, float]:
    n = b + c
    if n == 0:
        return 1.0, 1.0
    lower_tail = sum(math.comb(n, i) for i in range(0, min(b, c) + 1)) / (2**n)
    two_sided = min(1.0, 2.0 * lower_tail)
    directional = sum(math.comb(n, i) for i in range(max(b, c), n + 1)) / (2**n)
    return two_sided, directional


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def audit_records(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    audits = payload.get("audits")
    require(isinstance(audits, list), "audits must be a list")
    require(len(audits) == 10, f"expected 10 audits, found {len(audits)}")
    by_id: dict[str, dict[str, Any]] = {}
    for item in audits:
        require(isinstance(item, dict), "audit entry must be an object")
        audit_id = item.get("audit_id")
        require(isinstance(audit_id, str) and audit_id, "missing audit_id")
        require(audit_id not in by_id, f"duplicate audit_id: {audit_id}")
        require(item.get("top_tier_promotion_earned") is False, f"promotion leaked in {audit_id}")
        by_id[audit_id] = item
    return by_id


def run_checks(payload: dict[str, Any]) -> None:
    require(payload.get("schema") == "ORION.OperationalGapAudits.Result.v1", "schema mismatch")
    require(payload.get("terminal") == GREEN, "stored terminal is not green")
    require(payload.get("scientific_authority_delta") == "NONE", "authority delta must be NONE")
    require(payload.get("top_tier_promotions_earned") == 0, "portfolio promotion count must be zero")
    by_id = audit_records(payload)

    o2 = by_id["ORION-02_R24_VALIDITY_AND_CONTROL"]
    require(o2["registered_cases"] == 44 and o2["candidate_coverage"] == 44, "ORION-02 coverage drift")
    close(o2["candidate_violation_rate"], 20 / 44)
    close(o2["control_violation_rate"], 14 / 44)
    close(o2["unpaired_rate_difference"], (20 - 14) / 44)
    require(o2["paired_discordance_table_available_in_this_packet"] is False, "ORION-02 paired table invented")
    require("CANNOT_BE_RECOMPUTED" in o2["verdict"], "ORION-02 missing fail-closed paired verdict")

    o8 = by_id["ORION-08_MULTIPLICITY_SCOPE"]
    require(o8["comparison_rows"] == 12, "ORION-08 row-count drift")
    require(o8["unresolved_scoped_vs_never_mean_rows"] == 2, "ORION-08 unresolved-row drift")
    require(o8["row_level_sign_counts_in_this_packet"] is False, "ORION-08 row-level evidence invented")
    require("CANNOT_CHECK" in o8["verdict"], "ORION-08 must disclose replication boundary")

    o11 = by_id["ORION-11_HASH_VERSUS_IDENTITY"]
    require(o11["machine_rubric_id"] != o11["document_header_rubric_id"], "ORION-11 identity debt disappeared")
    require(o11["content_hash_loader_green"] is True, "ORION-11 content loader repair lost")
    require(o11["r4_retraction_must_remain"] is True, "ORION-11 R4 retraction not preserved")

    o12 = by_id["ORION-12_TERMINAL_INTERFACE_MATCHING"]
    treatment = set(o12["treatment_terminals"])
    baseline = set(o12["baseline_terminals"])
    require(o12["tasks"] == 390 and o12["baseline_count"] == 5, "ORION-12 design count drift")
    require("CANNOT_CHECK" in treatment and "CANNOT_CHECK" not in baseline, "ORION-12 terminal mismatch not reproduced")
    require(not treatment.issubset(baseline), "ORION-12 baseline unexpectedly matches treatment interface")

    o13 = by_id["ORION-13_BASELINE_AND_COORDINATE_DEGENERACY"]
    require(o13["flat_baseline_unique_outputs"] == 1, "ORION-13 flat baseline no longer constant")
    require(o13["flat_baseline_action"] == "ALWAYS_MERGE", "ORION-13 baseline action drift")
    require(o13["coordinate_count"] == 10, "ORION-13 coordinate-count drift")
    require(o13["coordinates_nonvarying_on_both_holdouts"] == 9, "ORION-13 nonvariation drift")
    require(o13["pooled_significance_test"] == "NOT_COMPUTED_BY_PROTOCOL", "ORION-13 non-computation was overwritten")

    o14 = by_id["ORION-14_FIXED_UNIVERSE_VERSUS_TRANSFER"]
    require(o14["frozen_cases"] == 360 and o14["attack_or_insufficiency_families"] == 12, "ORION-14 unit drift")
    require(o14["fresh_compile_exact_matches"] == o14["fresh_compile_total"] == 106, "ORION-14 compile exactness drift")
    require(o14["requested_reduct_rows"] == 400, "ORION-14 requested table size drift")
    require(o14["requested_reduct_artifact_status"] == "CANNOT_CHECK_ARTIFACT_ABSENT", "ORION-14 absent table was fabricated")

    o19 = by_id["ORION-19_FIVE_OF_FIVE_INTERVAL"]
    require(o19["successes"] == o19["trials"] == 5, "ORION-19 fixed-set count drift")
    close(o19["exact_clopper_pearson_lower"], all_success_cp_lower(5, o19["alpha_two_sided"]))
    require(o19["unit"] == "TASK_FAMILY", "ORION-19 inferential unit drift")

    o21 = by_id["ORION-21_EIGHT_OF_TEN_GATE_CALIBRATION"]
    require(o21["trials"] == 10 and o21["pass_threshold"] == 8, "ORION-21 gate drift")
    expected_ps = {"p=0.50": 0.50, "p=0.70": 0.70, "p=0.80": 0.80, "p=0.90": 0.90, "p=0.95": 0.95}
    for key, p in expected_ps.items():
        close(o21["binomial_pass_probabilities"][key], binomial_upper_tail(10, 8, p), 1e-10)
    require(o21["binomial_pass_probabilities"]["p=0.90"] > 0.9, "ORION-21 high-capability gate not discriminating")
    require(o21["binomial_pass_probabilities"]["p=0.70"] < 0.5, "ORION-21 moderate-band ambiguity lost")

    o22 = by_id["ORION-22_NINE_OF_NINE_INTERVAL"]
    require(o22["successes"] == o22["trials"] == 9, "ORION-22 fixed-set count drift")
    close(o22["exact_clopper_pearson_lower"], all_success_cp_lower(9, o22["alpha_two_sided"]))

    o24 = by_id["ORION-24_FOUR_ZERO_MCNEMAR"]
    two_sided, directional = exact_mcnemar(
        o24["discordant_candidate_wins"], o24["discordant_control_wins"]
    )
    close(o24["exact_mcnemar_two_sided_p"], two_sided)
    close(o24["exact_directional_p"], directional)
    close(o24["reported_rate_contrast"], 1 / 7, 1e-6)
    require(o24["same_programme_authorship"] is True, "ORION-24 authority label drift")
    require("POPULATION_SUPERIORITY_NOT_ESTABLISHED" in o24["verdict"], "ORION-24 overclaim guard lost")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check-result",
        type=Path,
        default=Path(__file__).resolve().with_name("RESULT.json"),
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        payload = json.loads(args.check_result.read_text(encoding="utf-8"))
        run_checks(payload)
        print(f"{GREEN} audits=10 promotions=0 mcnemar24=0.125")
        return 0
    except Exception as exc:
        print(f"{RED}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
