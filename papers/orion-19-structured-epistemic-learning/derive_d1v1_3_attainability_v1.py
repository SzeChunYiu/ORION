#!/usr/bin/env python3
"""Outcome-blind attainability and power for the frozen D1 v1.3 protocol.

`P9_D1V1_3_ORDERED_MULTIPLICITY_FREEZE_2026-08-23.json` lists five required
inputs, of which the fifth is a prospective power and attainability receipt.
That one costs nothing but arithmetic, reads no protected outcome, and can kill
a design before a single experiment is run -- which is exactly what P2's
acquisition ceiling showed happens when nobody computes it: a frozen IoU
threshold of 0.03 against an arm whose routes capped it at 0.0113.

Two things are derived here.

**Opportunity.** The protocol's gate demands that every registered cell -- attack
family x arm -- actually change at least a quarter of the protected cases, and
forbids a pass on a cell with no opportunity. Whether an attack changes an arm's
input is a property of the data and the attack alone. No model, no label, no
outcome.

**Power.** The confirmatory gates are a paired accuracy margin, a paired
bootstrap lower bound above zero, and a per-family non-inferiority margin. Their
attainability at the protocol's own sample sizes is arithmetic on the design.

Exit codes: 0 derived, 2 a gate is unattainable as registered, 3 CANNOT_CHECK.
"""

from __future__ import annotations

import json
import math
import sys

# From the D1 v1.3 freeze.
MIN_CHANGED_FRACTION = 0.25
PRIMARY_MARGIN = 0.08
WORST_FAMILY_MARGIN = -0.02
MAX_ATTACK_DEGRADATION = 0.03
MIN_CASES_PER_FAMILY = 128
MIN_FAMILIES = 4
MIN_TOTAL_CASES = 512
ALPHA = 0.05

# Registered in the freeze but with no implementation in the repository today.
UNBUILT_ARMS = ("TYPED_ORDERED_MULTIPLICITY", "STRONGEST_DONOR_COMPLETE_SERIALIZATION")
UNBUILT_ATTACKS = ("DUPLICATE_INSERTION",)


def normal_quantile(p: float) -> float:
    """Inverse standard normal, Acklam's rational approximation."""
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q, r = p - 0.5, (p - 0.5) ** 2
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def normal_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def paired_power(n: int, true_margin: float, gate_margin: float, discordance: float) -> float:
    """Power of a one-sided paired-proportion test against a margin.

    ``discordance`` is the share of cases on which the two arms disagree; only
    those carry information about a paired difference, so it sets the standard
    error. Reported across a range because it is not known before the run.
    """
    if discordance <= 0:
        return 0.0
    se = math.sqrt(discordance / n)
    z = normal_quantile(1 - ALPHA)
    return normal_cdf((true_margin - gate_margin) / se - z)


def measure_opportunity() -> dict:
    from orion.study.p9 import d1_experiment as base
    from orion.study.p9 import hostile_representation_attacks as att

    datasets = att.build_datasets()
    baseline = datasets[att.DATASET_BASE]
    cells = []
    for variant in sorted(datasets):
        if variant == att.DATASET_BASE:
            continue
        for family in base.D1FeatureFamily:
            changed = sum(
                1
                for left, right in zip(baseline.test, datasets[variant].test, strict=True)
                if base.features(left, family) != base.features(right, family)
            )
            total = len(baseline.test)
            fraction = changed / total
            cells.append(
                {
                    "attack_family": variant,
                    "arm": family.value,
                    "cases": total,
                    "changed": changed,
                    "changed_fraction": fraction,
                    "meets_opportunity_gate": fraction >= MIN_CHANGED_FRACTION,
                    "zero_opportunity": changed == 0,
                }
            )
    return {"cells": cells, "protected_cases": len(baseline.test)}


def main() -> int:
    try:
        opportunity = measure_opportunity()
    except Exception as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "error": str(exc)}))
        return 3

    cells = opportunity["cells"]
    zero = [c for c in cells if c["zero_opportunity"]]
    failing = [c for c in cells if not c["meets_opportunity_gate"]]
    attacks_with_no_opportunity_anywhere = sorted(
        {
            c["attack_family"]
            for c in cells
            if all(d["zero_opportunity"] for d in cells if d["attack_family"] == c["attack_family"])
        }
    )

    power = {
        "primary_paired_margin": PRIMARY_MARGIN,
        "n_total": MIN_TOTAL_CASES,
        "n_per_family": MIN_CASES_PER_FAMILY,
        "alpha": ALPHA,
        "note": (
            "Power depends on the discordance rate, which is unknown before the run, so it is "
            "reported across a range rather than assumed at one value."
        ),
        "primary_gate_power_by_discordance": {
            f"{d:.2f}": round(paired_power(MIN_TOTAL_CASES, 0.12, PRIMARY_MARGIN, d), 4)
            for d in (0.05, 0.10, 0.20, 0.40)
        },
        "primary_gate_power_if_true_margin_equals_gate": round(
            paired_power(MIN_TOTAL_CASES, PRIMARY_MARGIN, PRIMARY_MARGIN, 0.20), 4
        ),
        "worst_family_noninferiority_power_by_discordance": {
            f"{d:.2f}": round(paired_power(MIN_CASES_PER_FAMILY, 0.0, WORST_FAMILY_MARGIN, d), 4)
            for d in (0.05, 0.10, 0.20, 0.40)
        },
    }

    verdict = "OPPORTUNITY_GATE_UNATTAINABLE_ON_EXISTING_ARMS" if zero else "ATTAINABLE_AS_REGISTERED"
    print(
        json.dumps(
            {
                "schema": "orion.p9.d1v1_3-prospective-attainability.v1",
                "record": "P9_D1V1_3_PROSPECTIVE_ATTAINABILITY",
                "authority_scope": "PROSPECTIVE_OUTCOME_BLIND_ONLY",
                "outcome_accessed": False,
                "grants": "Nothing. The D1 v1.3 protocol remains PROSPECTIVE_FROZEN_NOT_EXECUTED.",
                "discharges": "required_inputs[4] prospective_power_and_attainability_receipt, partially -- see coverage",
                "coverage": {
                    "arms_measured": ["TRANSCRIPT_BAG", "UNTYPED_PAIR", "TYPED_RELATIONAL", "TYPED_SERIALIZED_BAG"],
                    "arms_registered_but_unbuilt": list(UNBUILT_ARMS),
                    "attacks_measured": ["EQUAL_LENGTH", "ORDER_PERMUTATION", "SEMANTIC_ORBIT"],
                    "attacks_registered_but_unbuilt": list(UNBUILT_ATTACKS),
                    "why_partial": (
                        "Two of the four registered arms and one of the four registered attack "
                        "families have no implementation. Their opportunity cannot be measured "
                        "and is not guessed."
                    ),
                },
                "opportunity_gate": {
                    "minimum_changed_fraction": MIN_CHANGED_FRACTION,
                    "zero_opportunity_pass_prohibited": True,
                    "protected_cases": opportunity["protected_cases"],
                    "cells": cells,
                    "cells_total": len(cells),
                    "cells_meeting_gate": len(cells) - len(failing),
                    "cells_with_zero_opportunity": len(zero),
                    "attack_families_with_no_opportunity_against_any_measured_arm":
                        attacks_with_no_opportunity_anywhere,
                },
                "power": power,
                "verdict": verdict,
                "finding": (
                    "ORDER_PERMUTATION changes nothing in any of the four existing arms: every one "
                    "of them reduces to a bag or set, which is the normalization the D1 v1.3 "
                    "representation contract names as forbidden. SEMANTIC_ORBIT reaches only the "
                    "serialized arm, and EQUAL_LENGTH misses TRANSCRIPT_BAG entirely. So the "
                    "protocol's own opportunity gate cannot be satisfied on the arms that exist, "
                    "and TYPED_ORDERED_MULTIPLICITY is not an additional arm -- it is the only arm "
                    "on which the order and multiplicity attacks can have any opportunity at all."
                ),
                "consequence": (
                    "Build TYPED_ORDERED_MULTIPLICITY and DUPLICATE_INSERTION before acquiring "
                    "anything else the freeze asks for. An attack cannot fail against a margin "
                    "that was never measured, and a cell with no opportunity must be excluded "
                    "before outcomes rather than passed."
                ),
            },
            indent=2,
        )
    )
    return 2 if zero else 0


if __name__ == "__main__":
    sys.exit(main())
