#!/usr/bin/env python3
"""Reproduce the primary-artifact calculations used by the V2 science-gap register.

Standard-library only. The script deliberately treats projects/task families as the
independent units and does not promote within-project decisions to replications.
"""
from __future__ import annotations

import json
import math


def binom_prob(n: int, k: int, p: float) -> float:
    return math.comb(n, k) * p**k * (1.0 - p) ** (n - k)


def binom_upper(n: int, k: int, p: float) -> float:
    return sum(binom_prob(n, j, p) for j in range(k, n + 1))


def binom_cdf(n: int, k: int, p: float) -> float:
    return sum(binom_prob(n, j, p) for j in range(k + 1))


def clopper_pearson(x: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    if x == 0:
        lo = 0.0
    else:
        a, b = 0.0, 1.0
        for _ in range(200):
            mid = (a + b) / 2.0
            if binom_upper(n, x, mid) < alpha / 2.0:
                a = mid
            else:
                b = mid
        lo = (a + b) / 2.0
    if x == n:
        hi = 1.0
    else:
        a, b = 0.0, 1.0
        for _ in range(200):
            mid = (a + b) / 2.0
            if binom_cdf(n, x, mid) > alpha / 2.0:
                a = mid
            else:
                b = mid
        hi = (a + b) / 2.0
    return lo, hi


def exact_mcnemar(main_wins: int, baseline_wins: int) -> dict[str, float | int]:
    discordant = main_wins + baseline_wins
    one_sided = binom_upper(discordant, main_wins, 0.5)
    two_sided = min(1.0, 2.0 * one_sided)
    return {
        "discordant_pairs": discordant,
        "one_sided_p": one_sided,
        "two_sided_p": two_sided,
    }


def perfect_separator(rows: list[dict[str, float | str]], feature: str) -> dict[str, object]:
    sound = [float(row[feature]) for row in rows if row["observed"] == "sound"]
    unsound = [float(row[feature]) for row in rows if row["observed"] == "unsound"]
    lower = max(sound)
    upper = min(unsound)
    return {
        "perfect": lower < upper,
        "threshold_interval": {"lower_exclusive": lower, "upper_inclusive": upper},
    }


def main() -> int:
    # Source: papers/orion-17-epistemic-navigation-open-worlds/theory/
    # density-prospective-v1/{STAMPED_PREDICTIONS,HELD_OUT_DENSITY,HELD_OUT_RESULT}.*
    calibration = [
        {"project": "flask", "modules": 24, "edges": 19, "observed": "sound"},
        {"project": "numpy", "modules": 426, "edges": 1076, "observed": "unsound"},
        {"project": "scipy", "modules": 813, "edges": 2156, "observed": "unsound"},
    ]
    held_out = [
        {"project": "requests", "modules": 19, "edges": 16, "observed": "sound"},
        {"project": "networkx", "modules": 583, "edges": 1245, "observed": "unsound"},
        {"project": "django", "modules": 906, "edges": 3336, "observed": "unsound"},
        {"project": "tornado", "modules": 74, "edges": 412, "observed": "unsound"},
        {"project": "sympy", "modules": 1566, "edges": 13622, "observed": "unsound"},
    ]
    threshold = 1.5
    predictions = []
    for row in held_out:
        density = row["edges"] / row["modules"]
        prediction = "unsound" if density >= threshold else "sound"
        predictions.append({"project": row["project"], "prediction": prediction,
                            "observed": row["observed"], "correct": prediction == row["observed"]})
    correct = sum(int(row["correct"]) for row in predictions)
    assert (correct, len(held_out)) == (5, 5)

    rows = []
    for source in calibration + held_out:
        row = dict(source)
        row["density"] = row["edges"] / row["modules"]
        rows.append(row)
    separators = {name: perfect_separator(rows, name) for name in ("density", "modules", "edges")}
    assert all(result["perfect"] for result in separators.values())

    one_sided_project_p = binom_upper(5, 5, 0.5)
    two_sided_project_p = min(1.0, 2.0 * one_sided_project_p)
    project_ci = clopper_pearson(5, 5)
    assert math.isclose(one_sided_project_p, 0.03125)
    assert math.isclose(two_sided_project_p, 0.0625)
    assert math.isclose(project_ci[0], 0.47817624989501856, rel_tol=1e-12)

    successor_alpha = binom_upper(20, 15, 0.5)
    successor_power_at_08 = binom_upper(20, 15, 0.8)
    assert math.isclose(successor_alpha, 0.020694732666015625)
    assert math.isclose(successor_power_at_08, 0.8042077854595495)

    # Source: ORION-05 R6O fixed-matching controls and all-matchings campaign runner.
    # Each tuple is (fixed support-one, fixed support-two, all support-one, all support-two).
    controls = {
        "r6o-16": (6, 5, 4, 4),
        "r6o-17": (6, 5, 5, 5),
        "r6o-19": (6, 5, 6, 6),
    }
    assert all((v[0], v[1]) != (v[2], v[3]) for v in controls.values())
    assert all(v[2] == v[3] for v in controls.values())

    # Sources: ORION-19 P9 transport receipt; ORION-24 P14C adjudication receipts.
    orion19 = exact_mcnemar(4, 0)
    orion24 = exact_mcnemar(4, 0)
    for result in (orion19, orion24):
        assert math.isclose(float(result["one_sided_p"]), 0.0625)
        assert math.isclose(float(result["two_sided_p"]), 0.125)

    output = {
        "status": "PASS",
        "audited_base": "703b87db22dce3981f13b407b56f4a656310632f",
        "orion17": {
            "predictions": predictions,
            "project_level_one_sided_p": one_sided_project_p,
            "project_level_two_sided_p": two_sided_project_p,
            "project_accuracy_exact_95_ci": project_ci,
            "perfect_separators": separators,
            "within_project_certificate_decisions": {
                "count": 1671821,
                "authority": "descriptive_only",
            },
            "successor_20_project_gate": {
                "density_wins_required": 15,
                "minimum_wins_in_each_10_project_stratum": 7,
                "one_sided_alpha": successor_alpha,
                "power_if_density_win_probability_is_0_8": successor_power_at_08,
            },
            "terminal": "PROSPECTIVE_RULE_SUPPORTED__UNIQUE_MECHANISM_NOT_IDENTIFIED",
        },
        "orion05": {
            "fixed_matching_count": 1,
            "campaign_matching_count": 15,
            "controls": controls,
            "terminal": "CONTROL_DOMAIN_MISMATCH_IDENTIFIED__CURRENT_CENSUS_REMAINS_CANNOT_CHECK",
        },
        "orion19": orion19,
        "orion24": {**orion24, "all_discordances_in_stratum": "RETAIN_NEGATIVE"},
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
