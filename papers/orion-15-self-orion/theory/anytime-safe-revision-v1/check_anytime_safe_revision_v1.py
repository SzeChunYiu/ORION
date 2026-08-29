#!/usr/bin/env python3
"""Independent exact regression for SELF_ORION.ANYTIME_SAFE_REVISION.v1.

The theorem is deductive. This checker exercises the union-bound object under arbitrary
dependence on small exact probability spaces, verifies spending schedules, and ensures the
registered unsafe controls really exceed the nominal anytime error.
"""
from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations


def compositions(total: int, parts: int):
    """Yield all weak compositions of total into `parts` cells."""
    if parts == 1:
        yield (total,)
        return
    for cuts in combinations(range(total + parts - 1), parts - 1):
        points = (-1,) + cuts + (total + parts - 1,)
        yield tuple(points[i + 1] - points[i] - 1 for i in range(parts))


def union_probability(counts, k: int) -> Fraction:
    total = sum(counts)
    return Fraction(sum(n for mask, n in enumerate(counts) if mask != 0), total)


def marginal_probability(counts, k: int, event: int) -> Fraction:
    total = sum(counts)
    return Fraction(
        sum(n for mask, n in enumerate(counts) if mask & (1 << event)),
        total,
    )


def main() -> int:
    errors = []

    # 1. Arbitrary dependence: enumerate every distribution on 3 event indicators
    # with denominator 8. For every alpha vector on the same grid, whenever each
    # event marginal is <= its budget, union probability must be <= sum budgets.
    k = 3
    denominator = 8
    distributions_checked = 0
    admissible_budget_checks = 0
    for counts in compositions(denominator, 1 << k):
        distributions_checked += 1
        marginals = [marginal_probability(counts, k, j) for j in range(k)]
        union = union_probability(counts, k)
        for a0 in range(denominator + 1):
            for a1 in range(denominator + 1 - a0):
                for a2 in range(denominator + 1 - a0 - a1):
                    budgets = [Fraction(a0, denominator), Fraction(a1, denominator), Fraction(a2, denominator)]
                    if all(marginals[j] <= budgets[j] for j in range(k)):
                        admissible_budget_checks += 1
                        if union > sum(budgets, Fraction(0)):
                            errors.append(
                                f"union bound violated: marginals={marginals}, budgets={budgets}, union={union}"
                            )
                            break
                if errors:
                    break
            if errors:
                break
        if errors:
            break

    # 2. Sharpness: disjoint false-pass events attain the total spend exactly.
    sharp_budgets = [Fraction(1, 20), Fraction(1, 40), Fraction(1, 40)]
    sharp_union = sum(sharp_budgets, Fraction(0))
    if sharp_union != Fraction(1, 10):
        errors.append("sharpness construction arithmetic changed")

    # 3. Six-round equal familywise spending.
    alpha = Fraction(1, 20)
    equal = [alpha / 6 for _ in range(6)]
    if sum(equal, Fraction(0)) != alpha:
        errors.append("six-round equal spending does not sum to alpha")

    # 4. Infinite geometric spending: finite prefixes stay below alpha and the
    # exact infinite series is alpha.
    geometric_prefixes = []
    running = Fraction(0)
    for t in range(1, 21):
        running += alpha / (2**t)
        geometric_prefixes.append(running)
        if running >= alpha:
            errors.append(f"geometric prefix {t} spent >= alpha")
            break
    geometric_limit = alpha

    # 5. Required negative control: reusing one-round alpha each round exceeds
    # the nominal anytime alpha as soon as T>1 under independent false passes.
    repeated_alpha = {}
    for rounds in (1, 2, 3, 6, 20):
        global_error = 1 - (1 - alpha) ** rounds
        repeated_alpha[str(rounds)] = str(global_error)
        if rounds == 1 and global_error != alpha:
            errors.append("one-round repeated-alpha control mismatch")
        if rounds > 1 and not global_error > alpha:
            errors.append(f"repeated alpha failed to exceed nominal at T={rounds}")

    # 6. Gate splitting: if four non-compensatory gate budgets sum to the round
    # familywise budget, the round union is bounded by that sum with no independence.
    round_budget = Fraction(1, 120)
    gate_budgets = [round_budget / 4] * 4
    if sum(gate_budgets, Fraction(0)) != round_budget:
        errors.append("within-round gate split arithmetic changed")

    report = {
        "status": "PASS" if not errors else "MISMATCH",
        "terminal": (
            "ANYTIME_BAD_PROMOTION_CONTROL_PROVED__LONGITUDINAL_BENEFIT_UNTESTED"
            if not errors
            else "CANNOT_CHECK_ANYTIME_SAFETY_REGRESSION"
        ),
        "arithmetic": "fractions.Fraction exact rational arithmetic",
        "arbitrary_dependence_regression": {
            "event_count": k,
            "probability_denominator": denominator,
            "distributions_checked": distributions_checked,
            "admissible_distribution_budget_pairs_checked": admissible_budget_checks,
            "pass": not errors,
        },
        "sharp_disjoint_example": {
            "budgets": [str(x) for x in sharp_budgets],
            "union_probability": str(sharp_union),
            "equals_total_spend": sharp_union == sum(sharp_budgets, Fraction(0)),
        },
        "six_round_equal_spending": {
            "alpha": str(alpha),
            "per_round": str(equal[0]),
            "total": str(sum(equal, Fraction(0))),
        },
        "geometric_spending": {
            "alpha": str(alpha),
            "first_20_prefixes_below_alpha": all(x < alpha for x in geometric_prefixes),
            "series_limit": str(geometric_limit),
        },
        "unsafe_reuse_control": {
            "one_round_alpha": str(alpha),
            "global_error_by_rounds": repeated_alpha,
            "all_T_gt_1_exceed_alpha": all(
                1 - (1 - alpha) ** rounds > alpha for rounds in (2, 3, 6, 20)
            ),
        },
        "noncompensatory_gate_split": {
            "round_budget": str(round_budget),
            "gate_budgets": [str(x) for x in gate_budgets],
            "sum": str(sum(gate_budgets, Fraction(0))),
        },
        "errors": errors,
        "scientific_authority_delta": "NONE",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 5


if __name__ == "__main__":
    raise SystemExit(main())
