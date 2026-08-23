#!/usr/bin/env python3
"""Outcome-blind max-T planning simulation for the P1 R7A successor."""

from __future__ import annotations

import argparse
import json
from math import ceil, sqrt
from random import Random
from statistics import NormalDist
from typing import Any

DEFAULT_SEED = 2026082301
DEFAULT_DRAWS = 50_000
COMPARATOR_COUNT = 9
FAMILYWISE_ALPHA = 0.05
MARGIN = 0.05
TARGET_JOINT_POWER = 0.90
BALANCED_BLOCK_SIZE = 32


def simulate_critical_value(*, seed: int, draws: int) -> float:
    """Simulate the one-sided max-T critical value under independent contrasts."""

    if draws < 10_000:
        raise ValueError("at least 10000 draws are required")
    rng = Random(seed)
    maxima = [max(rng.gauss(0.0, 1.0) for _ in range(COMPARATOR_COUNT)) for _ in range(draws)]
    maxima.sort()
    index = min(draws - 1, ceil((1.0 - FAMILYWISE_ALPHA) * draws) - 1)
    return maxima[index]


def projected_joint_power(
    *, n: int, delta: float, discordance: float, critical_value: float
) -> float:
    if not 0.0 < delta <= discordance <= 1.0:
        raise ValueError("require 0 < delta <= discordance <= 1")
    standard_error = sqrt((discordance - delta**2) / n)
    single = NormalDist().cdf((delta - MARGIN) / standard_error - critical_value)
    return single**COMPARATOR_COUNT


def minimum_balanced_n(
    *, delta: float, discordance: float, critical_value: float
) -> int:
    for n in range(BALANCED_BLOCK_SIZE, 100_001, BALANCED_BLOCK_SIZE):
        if projected_joint_power(
            n=n,
            delta=delta,
            discordance=discordance,
            critical_value=critical_value,
        ) >= TARGET_JOINT_POWER:
            return n
    raise ValueError("target power not attained within 100000 source clusters")


def build_receipt(*, seed: int = DEFAULT_SEED, draws: int = DEFAULT_DRAWS) -> dict[str, Any]:
    critical = simulate_critical_value(seed=seed, draws=draws)
    sensitivity: list[dict[str, Any]] = []
    for delta in (0.15, 0.20, 0.25):
        for discordance in (0.30, 0.40, 0.50):
            if delta > discordance:
                continue
            required = minimum_balanced_n(
                delta=delta,
                discordance=discordance,
                critical_value=critical,
            )
            sensitivity.append(
                {
                    "planning_delta": delta,
                    "planning_discordance": discordance,
                    "minimum_balanced_source_clusters": required,
                    "power_at_n_384": round(
                        projected_joint_power(
                            n=384,
                            delta=delta,
                            discordance=discordance,
                            critical_value=critical,
                        ),
                        6,
                    ),
                }
            )
    planned_minimum = minimum_balanced_n(
        delta=0.20,
        discordance=0.40,
        critical_value=critical,
    )
    return {
        "schema_version": "orion.p1.r7a.max-t-power-receipt.v1",
        "claim_id": "P1.H1.R7A.MAXT_POWERED",
        "authority": "OUTCOME_BLIND_PLANNING_ONLY",
        "protected_outcomes_accessed": False,
        "simulation": {
            "seed": seed,
            "draws": draws,
            "null_model": "nine independent standard-normal paired-contrast T statistics",
            "familywise_alpha": FAMILYWISE_ALPHA,
            "comparator_count": COMPARATOR_COUNT,
            "simulated_one_sided_max_t_critical_value": round(critical, 9),
        },
        "registered_planning_point": {
            "planning_delta": 0.20,
            "superiority_margin": MARGIN,
            "planning_discordance": 0.40,
            "target_joint_power": TARGET_JOINT_POWER,
            "minimum_balanced_source_clusters": planned_minimum,
            "planned_source_clusters": 384,
            "projected_joint_power": round(
                projected_joint_power(
                    n=384,
                    delta=0.20,
                    discordance=0.40,
                    critical_value=critical,
                ),
                6,
            ),
            "minimum_is_conditional_on_stated_planning_assumptions": True,
        },
        "sensitivity": sensitivity,
        "analysis_unit": "unique_source_study_artifact_family_cluster",
        "technical_cells_are_not_independent_units": True,
        "multiplicity_family": "all_nine_registered_primary_comparator_contrasts",
        "claim_logic": "intersection_all_nine_simultaneous_lower_bounds_must_exceed_0.05",
        "grants_scientific_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--draws", type=int, default=DEFAULT_DRAWS)
    args = parser.parse_args()
    print(json.dumps(build_receipt(seed=args.seed, draws=args.draws), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
