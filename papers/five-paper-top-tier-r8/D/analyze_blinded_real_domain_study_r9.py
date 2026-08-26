#!/usr/bin/env python3
"""Preregistered paired analysis for the D real-domain study.

The script consumes a JSON file with paired false-authorization and false-denial
2x2 tables plus frozen materiality thresholds. It performs an exact two-sided
McNemar/binomial test and a conditional exact interval obtained by inverting
binomial tails on the discordant pairs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

SCHEMA = "ORION.D.RealDomainPairedAnalysisR9.v1"


def exact_two_sided_mcnemar(typed_only_error: int, erased_only_error: int) -> float:
    if typed_only_error < 0 or erased_only_error < 0:
        raise ValueError("discordant counts must be nonnegative")
    discordant = typed_only_error + erased_only_error
    if discordant == 0:
        return 1.0
    tail = min(typed_only_error, erased_only_error)
    probability = sum(Fraction(math.comb(discordant, index), 2**discordant) for index in range(tail + 1))
    return float(min(Fraction(1, 1), 2 * probability))


def binomial_cdf(k: int, n: int, p: float) -> float:
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    # Start at probability of zero successes and update by a stable recurrence.
    term = (1.0 - p) ** n
    total = term
    ratio = p / (1.0 - p)
    for successes in range(0, k):
        term *= (n - successes) / (successes + 1) * ratio
        total += term
    return min(1.0, max(0.0, total))


def solve_decreasing_cdf(k: int, n: int, target: float) -> float:
    low, high = 0.0, 1.0
    for _ in range(100):
        middle = (low + high) / 2.0
        value = binomial_cdf(k, n, middle)
        if value > target:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def clopper_pearson(successes: int, trials: int, level: float = 0.95) -> tuple[float, float]:
    if not (0 <= successes <= trials):
        raise ValueError("successes must lie in [0,trials]")
    if not (0.0 < level < 1.0):
        raise ValueError("level must lie in (0,1)")
    if trials == 0:
        return 0.0, 1.0
    alpha = 1.0 - level
    if successes == 0:
        lower = 0.0
    else:
        # P_p[X <= successes-1] = 1-alpha/2.
        lower = solve_decreasing_cdf(successes - 1, trials, 1.0 - alpha / 2.0)
    if successes == trials:
        upper = 1.0
    else:
        # P_p[X <= successes] = alpha/2.
        upper = solve_decreasing_cdf(successes, trials, alpha / 2.0)
    return lower, upper


def analyze_table(table: dict[str, int], level: float = 0.95) -> dict[str, Any]:
    required = {"both_correct", "typed_only_error", "erased_only_error", "both_error"}
    if set(table) != required:
        raise ValueError(f"paired table must contain exactly {sorted(required)}")
    if any(not isinstance(value, int) or value < 0 for value in table.values()):
        raise ValueError("paired table counts must be nonnegative integers")
    total = sum(table.values())
    typed_only = table["typed_only_error"]
    erased_only = table["erased_only_error"]
    discordant = typed_only + erased_only
    effect = 0.0 if total == 0 else (erased_only - typed_only) / total
    conditional_lower, conditional_upper = clopper_pearson(erased_only, discordant, level)
    discordant_fraction = 0.0 if total == 0 else discordant / total
    effect_interval = {
        "level": level,
        "lower": discordant_fraction * (2.0 * conditional_lower - 1.0),
        "upper": discordant_fraction * (2.0 * conditional_upper - 1.0),
        "method": "conditional exact Clopper-Pearson interval on erased-only share among discordant pairs, transformed to paired error-rate difference",
    }
    return {
        "total": total,
        "discordant": discordant,
        "typed_only_error": typed_only,
        "erased_only_error": erased_only,
        "typed_error_rate": 0.0 if total == 0 else (typed_only + table["both_error"]) / total,
        "erased_error_rate": 0.0 if total == 0 else (erased_only + table["both_error"]) / total,
        "effect_erased_minus_typed": effect,
        "exact_two_sided_mcnemar_p": exact_two_sided_mcnemar(typed_only, erased_only),
        "effect_interval": effect_interval,
        "conditional_erased_only_probability_interval": {
            "level": level,
            "lower": conditional_lower,
            "upper": conditional_upper,
            "method": "Clopper-Pearson",
        },
    }


def validate_inputs(data: dict[str, Any]) -> None:
    required = {
        "schema",
        "false_authorization_table",
        "false_denial_table",
        "out_of_model_cases",
        "typed_correct_abstentions",
        "erased_correct_abstentions",
        "minimum_material_false_authorization_reduction",
        "maximum_tolerated_false_denial_increase",
        "minimum_typed_correct_abstention_rate",
        "minimum_discordant_pairs",
        "confidence_level",
    }
    missing = required - set(data)
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")
    if data["schema"] != "ORION.D.RealDomainPairedAnalysisInputR9.v1":
        raise ValueError("unexpected input schema")
    for field in (
        "minimum_material_false_authorization_reduction",
        "maximum_tolerated_false_denial_increase",
        "minimum_typed_correct_abstention_rate",
        "confidence_level",
    ):
        if not isinstance(data[field], (int, float)):
            raise ValueError(f"{field} must be numeric")
    for field in ("out_of_model_cases", "typed_correct_abstentions", "erased_correct_abstentions", "minimum_discordant_pairs"):
        if not isinstance(data[field], int) or data[field] < 0:
            raise ValueError(f"{field} must be a nonnegative integer")


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    validate_inputs(data)
    level = float(data["confidence_level"])
    false_authorization = analyze_table(data["false_authorization_table"], level)
    false_denial = analyze_table(data["false_denial_table"], level)
    out_of_model = data["out_of_model_cases"]
    typed_abstention_rate = 1.0 if out_of_model == 0 else data["typed_correct_abstentions"] / out_of_model
    erased_abstention_rate = 1.0 if out_of_model == 0 else data["erased_correct_abstentions"] / out_of_model
    materiality_gate = (
        false_authorization["effect_erased_minus_typed"]
        >= float(data["minimum_material_false_authorization_reduction"])
    )
    false_denial_gate = (
        false_denial["effect_erased_minus_typed"]
        >= -float(data["maximum_tolerated_false_denial_increase"])
    )
    abstention_gate = typed_abstention_rate >= float(data["minimum_typed_correct_abstention_rate"])
    informative = (
        false_authorization["discordant"] >= data["minimum_discordant_pairs"]
        and false_denial["discordant"] >= data["minimum_discordant_pairs"]
    )
    return {
        "schema": SCHEMA,
        "false_authorization": false_authorization,
        "false_denial": false_denial,
        "out_of_model": {
            "cases": out_of_model,
            "typed_correct_abstention_rate": typed_abstention_rate,
            "erased_correct_abstention_rate": erased_abstention_rate,
        },
        "frozen_gates": {
            "minimum_material_false_authorization_reduction": data["minimum_material_false_authorization_reduction"],
            "maximum_tolerated_false_denial_increase": data["maximum_tolerated_false_denial_increase"],
            "minimum_typed_correct_abstention_rate": data["minimum_typed_correct_abstention_rate"],
            "minimum_discordant_pairs": data["minimum_discordant_pairs"],
            "materiality_gate_met": materiality_gate,
            "false_denial_gate_met": false_denial_gate,
            "abstention_gate_met": abstention_gate,
            "informative_discordance_gate_met": informative,
        },
        "authority": {
            "paired_analysis_only": True,
            "validates_blinding_or_gold_labels": False,
            "selects_study_terminal": False,
            "grants_production_safety_authority": False,
            "grants_journal_authority": False,
        },
    }


def self_test() -> dict[str, Any]:
    assert exact_two_sided_mcnemar(0, 0) == 1.0
    assert exact_two_sided_mcnemar(0, 5) == 0.0625
    assert exact_two_sided_mcnemar(1, 5) == 0.21875
    symmetric = analyze_table({"both_correct": 10, "typed_only_error": 3, "erased_only_error": 3, "both_error": 2})
    assert symmetric["effect_erased_minus_typed"] == 0.0
    one_sided = analyze_table({"both_correct": 10, "typed_only_error": 0, "erased_only_error": 6, "both_error": 0})
    assert one_sided["effect_erased_minus_typed"] == 0.375
    assert abs(one_sided["exact_two_sided_mcnemar_p"] - 0.03125) < 1e-15
    for successes, trials in ((0, 1), (1, 1), (2, 10), (8, 10), (50, 100)):
        lower, upper = clopper_pearson(successes, trials)
        assert 0.0 <= lower <= upper <= 1.0
        assert lower <= successes / trials <= upper
    return {
        "schema": "ORION.D.RealDomainPairedAnalysisSelfTestR9.v1",
        "status": "PASS",
        "mcnemar_controls": 5,
        "interval_controls": 5,
        "terminal": "D_REAL_DOMAIN_PAIRED_ANALYSIS_SELF_TEST_PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", help="preregistered paired-analysis input JSON")
    parser.add_argument("--output", help="output JSON path")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        result = self_test()
    else:
        if not args.input:
            parser.error("input JSON is required unless --self-test is used")
        input_path = Path(args.input)
        data = json.loads(input_path.read_text(encoding="utf-8"))
        result = analyze(data)
        result["input"] = {
            "path": str(input_path),
            "sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
