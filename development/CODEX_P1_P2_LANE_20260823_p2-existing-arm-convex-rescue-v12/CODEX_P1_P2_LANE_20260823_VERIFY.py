#!/usr/bin/env python3
"""Exact, outcome-free verification of the P2 V12 convex-rescue boundary.

This script reads the already sealed P2 V10 result and protocol.  It does not
fit a model, open a new label, rerun an arm, or alter any upstream artifact.
It proves that ex-ante complete-arm randomization among the three already
reported V10 arms cannot meet the two registered primary mean gates, even in
expectation.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V10 = ROOT / "development/p2-title-emphasis-conflict-resolved-v10-2026-08-23"
V11 = ROOT / "development/p2-safe-residual-envelope-theory-v11-2026-08-23"

INPUTS = {
    "v10_result": (
        V10 / "RESULT_V10.json",
        "c69e5634b8d0e82a1fa393dbae276d728e9a2f7ba4c9db81a27c0329e2e66742",
    ),
    "v10_protocol": (
        V10 / "PROTOCOL_FREEZE_V10.json",
        "e5b40d165d76f017296ee7915f3d07ec9fed27b7c9bbbe106a0a00e318cab72c",
    ),
    "v11_theory": (
        V11 / "THEORY.md",
        "a3c9107ad152766efc2a08d722657d550781f1f181f47f3ceeba041c0a710176",
    ),
    "v11_receipt": (
        V11 / "THEORY_RECEIPT_V11.json",
        "1694e2f33bc195eb848e7ec93d3fd31793c936db96f62d43d17d09b5dac8dd6f",
    ),
}

TERMINAL = (
    "CODEX_P1_P2_LANE_20260823_P2_V12_EXISTING_ARM_CONVEX_RESCUE_"
    "IMPOSSIBLE__PRIMARY_GATE_HULL_DISJOINT__EXACT_U4_REMAINS_FALLBACK__"
    "P2_TOP_TIER_READINESS_UNCHANGED"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mean(values: list[float]) -> float:
    return math.fsum(values) / len(values)


def close(a: float, b: float, tol: float = 2e-15) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tol)


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object, expected: object) -> None:
        checks.append(
            {
                "name": name,
                "passed": bool(passed),
                "observed": observed,
                "expected": expected,
            }
        )

    input_receipt: dict[str, dict[str, object]] = {}
    for name, (path, expected_hash) in INPUTS.items():
        observed_hash = sha256(path)
        input_receipt[name] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": observed_hash,
            "bytes": path.stat().st_size,
        }
        check(
            f"input_hash::{name}",
            observed_hash == expected_hash,
            observed_hash,
            expected_hash,
        )

    result = json.loads(INPUTS["v10_result"][0].read_text())
    protocol = json.loads(INPUTS["v10_protocol"][0].read_text())
    tau = float(protocol["unchanged_gates"]["G3_MEAN_DELTA_CRE20"].split(">=")[1])
    tau_r10 = float(protocol["unchanged_gates"]["G4_MEAN_DELTA_R10"].split(">=")[1])
    check("equal_primary_thresholds", close(tau, tau_r10), tau_r10, tau)

    controller_rows = list(result["controller_delta_by_review"].values())
    title_rows = list(result["title_only_delta_by_review"].values())
    check("seven_review_units", len(controller_rows) == 7, len(controller_rows), 7)
    check("same_review_keys", set(result["controller_delta_by_review"]) == set(result["title_only_delta_by_review"]), sorted(result["controller_delta_by_review"]), sorted(result["title_only_delta_by_review"]))

    def arm_summary(rows: list[dict[str, float]]) -> dict[str, object]:
        return {
            "mean_cre20": mean([row["cre20"] for row in rows]),
            "mean_r10": mean([row["recall_at_010"] for row in rows]),
            "mean_wss95": mean([row["wss_at_95"] for row in rows]),
            "positive_cre20_reviews": sum(row["cre20"] > 0 for row in rows),
            "positive_r10_reviews": sum(row["recall_at_010"] > 0 for row in rows),
            "worst_r10": min(row["recall_at_010"] for row in rows),
        }

    summaries = {
        "EXACT_U4": {
            "mean_cre20": 0.0,
            "mean_r10": 0.0,
            "mean_wss95": 0.0,
            "positive_cre20_reviews": 0,
            "positive_r10_reviews": 0,
            "worst_r10": 0.0,
        },
        "TITLE_ONLY_U4": arm_summary(title_rows),
        "U4_PLUS_TITLE_A250": arm_summary(controller_rows),
    }

    aggregate = result["aggregate_controller_delta_vs_u4"]
    check("reconstruct_controller_mean_cre20", close(summaries["U4_PLUS_TITLE_A250"]["mean_cre20"], aggregate["cre20"]), summaries["U4_PLUS_TITLE_A250"]["mean_cre20"], aggregate["cre20"])
    check("reconstruct_controller_mean_r10", close(summaries["U4_PLUS_TITLE_A250"]["mean_r10"], aggregate["recall_at_010"]), summaries["U4_PLUS_TITLE_A250"]["mean_r10"], aggregate["recall_at_010"])
    check("reconstruct_controller_mean_wss95", close(summaries["U4_PLUS_TITLE_A250"]["mean_wss95"], aggregate["wss_at_95"]), summaries["U4_PLUS_TITLE_A250"]["mean_wss95"], aggregate["wss_at_95"])
    check("reconstruct_controller_positive_cre20", summaries["U4_PLUS_TITLE_A250"]["positive_cre20_reviews"] == result["strictly_positive_review_counts"]["cre20"], summaries["U4_PLUS_TITLE_A250"]["positive_cre20_reviews"], result["strictly_positive_review_counts"]["cre20"])
    check("reconstruct_controller_positive_r10", summaries["U4_PLUS_TITLE_A250"]["positive_r10_reviews"] == result["strictly_positive_review_counts"]["recall_at_010"], summaries["U4_PLUS_TITLE_A250"]["positive_r10_reviews"], result["strictly_positive_review_counts"]["recall_at_010"])
    check("reconstruct_controller_worst_r10", close(summaries["U4_PLUS_TITLE_A250"]["worst_r10"], result["worst_review_delta_r10"]), summaries["U4_PLUS_TITLE_A250"]["worst_r10"], result["worst_review_delta_r10"])

    reconstructed_gates = {
        "G1_BINDING": bool(result["binding_receipt"]["passed"]),
        "G2_SOURCE_CONTENT_AND_POPULATION": bool(result["population_receipt"]["passed"]),
        "G3_MEAN_DELTA_CRE20": summaries["U4_PLUS_TITLE_A250"]["mean_cre20"] >= tau,
        "G4_MEAN_DELTA_R10": summaries["U4_PLUS_TITLE_A250"]["mean_r10"] >= tau,
        "G5_MEAN_DELTA_WSS95": summaries["U4_PLUS_TITLE_A250"]["mean_wss95"] >= 0.0,
        "G6_POSITIVE_CRE20_SIGN": summaries["U4_PLUS_TITLE_A250"]["positive_cre20_reviews"] >= 6,
        "G7_POSITIVE_R10_SIGN": summaries["U4_PLUS_TITLE_A250"]["positive_r10_reviews"] >= 6,
        "G8_WORST_REVIEW_R10_HARM": summaries["U4_PLUS_TITLE_A250"]["worst_r10"] >= -0.05,
        "G9_ABSOLUTE_WORK_SAVING": min(result["absolute_controller_wss95_by_review"].values()) > 0.0,
    }
    for gate, observed in reconstructed_gates.items():
        check(f"reconstruct_gate::{gate}", observed == result["gates"][gate], observed, result["gates"][gate])

    # Convex-hull certificate.  A complete-arm randomization with probabilities
    # p_j has expected mean vector sum_j p_j mu_j.  Each coordinate is bounded
    # above by its largest vertex coordinate.
    cre_upper = max(float(v["mean_cre20"]) for v in summaries.values())
    r10_upper = max(float(v["mean_r10"]) for v in summaries.values())
    check("convex_hull_cre20_upper_below_gate", cre_upper < tau, cre_upper, tau)
    check("convex_hull_r10_upper_below_gate", r10_upper < tau, r10_upper, tau)

    hull_certificate = {
        "arm_vertices": summaries,
        "primary_gate_threshold": tau,
        "coordinatewise_hull_upper_bounds": {
            "mean_cre20": cre_upper,
            "mean_r10": r10_upper,
        },
        "strict_shortfalls_from_gate": {
            "mean_cre20": tau - cre_upper,
            "mean_r10": tau - r10_upper,
        },
        "proof": (
            "For any p in the three-arm probability simplex, each expected "
            "primary mean is a convex combination of the corresponding arm "
            "means and is therefore no larger than the largest vertex value. "
            "Both vertex maxima are strictly below the registered threshold."
        ),
        "closed_rescue_class": (
            "EX_ANTE_GLOBAL_COMPLETE_ARM_RANDOMIZATION_OVER_EXACT_U4_"
            "TITLE_ONLY_U4_AND_U4_PLUS_TITLE_A250__EXPECTED_METRIC_RELAXATION"
        ),
        "not_closed": [
            "new score-level alpha or representation search",
            "review- or row-conditioned arm selection",
            "a new learner or balancer",
            "a lawful non-simulable signal or new acquisition support",
            "source-disjoint independent confirmation",
            "joint acquisition-authority evaluation",
        ],
    }

    all_passed = all(item["passed"] for item in checks)
    receipt = {
        "identity": "CODEX_P1_P2_LANE_20260823_P2_V12_CONVEX_RESCUE_RECEIPT",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "STATIC_EXACT_REANALYSIS_OF_ALREADY_SEALED_PUBLIC_V10_ARM_METRICS",
        "inputs": input_receipt,
        "checks": checks,
        "checks_passed": sum(bool(item["passed"]) for item in checks),
        "checks_total": len(checks),
        "all_passed": all_passed,
        "hull_certificate": hull_certificate,
        "blocker_delta": {
            "closed": 1 if all_passed else 0,
            "closed_identity": "P2_EXISTING_ARM_POSTHOC_CONVEX_RESCUE" if all_passed else None,
            "top_tier_blockers_closed": 0,
            "p2_readiness_before": "NOT_SUBMISSION_READY",
            "p2_readiness_after": "NOT_SUBMISSION_READY",
            "superiority": "CANNOT_CHECK",
        },
        "execution_counts": {
            "new_labels_opened": 0,
            "new_model_fits": 0,
            "new_arm_executions": 0,
            "new_comparator_executions": 0,
            "pytest": 0,
            "repository_ci": 0,
        },
        "terminal": TERMINAL if all_passed else "CODEX_P1_P2_LANE_20260823_P2_V12_VALIDATION_FAILED",
    }

    out = HERE / "CODEX_P1_P2_LANE_20260823_RESULT.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "all_passed": all_passed,
        "checks": f"{receipt['checks_passed']}/{receipt['checks_total']}",
        "cre20_hull_upper": cre_upper,
        "r10_hull_upper": r10_upper,
        "threshold": tau,
        "terminal": receipt["terminal"],
    }, indent=2))
    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
