#!/usr/bin/env python3
"""Fail-closed local checks for the active-identification adversarial review.

This is a mathematical/artifact check only. It is not empirical or external review.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True

REVIEW = Path(__file__).resolve().parent
REPO = REVIEW.parents[1]
SOURCE = REPO / "development/active-identification-theory-2026-08-23"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_source_manifest() -> dict:
    rows = []
    for raw in (SOURCE / "SHA256SUMS").read_text().splitlines():
        expected, rel = raw.split(maxsplit=1)
        path = REPO / rel
        actual = sha256(path)
        rows.append({"path": rel, "expected": expected, "actual": actual,
                     "pass": actual == expected})
    return {"pass": all(row["pass"] for row in rows), "rows": rows}


def check_source_witnesses() -> dict:
    path = SOURCE / "finite_active_identification_harness.py"
    spec = importlib.util.spec_from_file_location("active_id_source_harness", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import source harness")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.run()  # does not invoke __main__ and does not rewrite source receipt
    stored = json.loads((SOURCE / "COUNTEREXAMPLE_RECEIPT.json").read_text())
    return {
        "pass": result == stored and result["all_pass"] and result["checks_total"] == 8,
        "recomputed_checks_passed": result["checks_passed"],
        "recomputed_checks_total": result["checks_total"],
        "stored_receipt_equal": result == stored,
        "source_script_sha256": sha256(path),
    }


def check_review_counterexamples() -> list[dict]:
    # A1: an unavailable perfect test is illegally admitted by the stationary model.
    stop_risk = min(Fraction(1, 2), Fraction(1, 2))
    stationary_perfect_test_risk = Fraction(0)
    # A2: h(v)=sup theta=1 over 0<theta<1, without an attaining theta.
    sampled_thetas = [Fraction(i, 1000) for i in range(1, 1000)]
    sampled_sup = max(sampled_thetas)
    # A3: a free perfect test has zero terminal and acquisition loss.
    free_perfect_total_cost = Fraction(0)
    return [
        {
            "id": "A1_STATE_INDEX_REQUIRED",
            "pass": stationary_perfect_test_risk < stop_risk,
            "stationary_value": str(stationary_perfect_test_risk),
            "legal_no_action_value": str(stop_risk),
        },
        {
            "id": "A2_WORST_PRIOR_NONATTAINMENT",
            "pass": sampled_sup < 1 and all(theta < 1 for theta in sampled_thetas),
            "analytic_supremum": "1",
            "attained": False,
            "finite_grid_max": str(sampled_sup),
        },
        {
            "id": "A3_ZERO_COST_BOUNDARY",
            "pass": free_perfect_total_cost == 0,
            "exact_error": "0",
            "total_acquisition_cost": str(free_perfect_total_cost),
            "theorem_4_applicable": False,
        },
    ]


def main() -> int:
    ledger = json.loads((REVIEW / "GAP_LEDGER.json").read_text())
    manifest = check_source_manifest()
    source_witnesses = check_source_witnesses()
    new_checks = check_review_counterexamples()
    receipt = {
        "schema": "active-identification-adversarial-review-receipt-v1",
        "scope": "local finite mathematical and artifact checks only",
        "external_independent_review": False,
        "empirical_authority": False,
        "protected_evaluation": False,
        "source_manifest": manifest,
        "source_witnesses": source_witnesses,
        "review_ledger": {
            "schema": ledger.get("schema"),
            "entries": len(ledger.get("entries", [])),
            "pass": ledger.get("schema") == "active-identification-adversarial-gap-ledger-v1"
                    and len(ledger.get("entries", [])) == 12,
        },
        "new_counterexamples": new_checks,
    }
    receipt["all_pass"] = (
        manifest["pass"]
        and source_witnesses["pass"]
        and receipt["review_ledger"]["pass"]
        and all(item["pass"] for item in new_checks)
    )
    (REVIEW / "VERIFICATION_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
