#!/usr/bin/env python3
"""Finite controls for the FiberGuard safe-feature cover theorem R10.

The analytic theorem owns all-size authority. This verifier generates finite
exact action-safe sets, base fibres, and candidate features, then compares:

1. direct enumeration of all static feature subsets whose refined fibres have
   nonempty epsilon-safe action intersections; and
2. feature subsets covering every inclusion-minimal action conflict.

It also includes a higher-order three-action conflict that pair-only audits miss.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
from pathlib import Path
from typing import Iterable, Sequence

SCHEMA = "ORION.FiberGuard.SafeFeatureCover.R10.v1"
SEED = 20260826


def safe_intersection(rows: Iterable[set[int]], actions: Sequence[int]) -> set[int]:
    out = set(actions)
    for row in rows:
        out.intersection_update(row)
    return out


def minimal_conflicts(
    base: Sequence[int], safe_sets: Sequence[set[int]], actions: Sequence[int]
) -> list[tuple[int, ...]]:
    by_fibre: dict[int, list[int]] = {}
    for i, y in enumerate(base):
        by_fibre.setdefault(y, []).append(i)
    conflicts: list[tuple[int, ...]] = []
    for indices in by_fibre.values():
        for size in range(1, min(len(actions), len(indices)) + 1):
            for w in itertools.combinations(indices, size):
                if safe_intersection((safe_sets[i] for i in w), actions):
                    continue
                if all(
                    safe_intersection((safe_sets[i] for i in w if i != removed), actions)
                    for removed in w
                ):
                    conflicts.append(w)
    return conflicts


def selected_features_safe(
    base: Sequence[int],
    safe_sets: Sequence[set[int]],
    actions: Sequence[int],
    features: Sequence[Sequence[int]],
    selected: Sequence[int],
) -> bool:
    fibres: dict[tuple[int, ...], list[int]] = {}
    for i, y in enumerate(base):
        key = (y,) + tuple(features[j][i] for j in selected)
        fibres.setdefault(key, []).append(i)
    return all(
        safe_intersection((safe_sets[i] for i in indices), actions)
        for indices in fibres.values()
    )


def selected_features_cover(
    conflicts: Sequence[tuple[int, ...]],
    features: Sequence[Sequence[int]],
    selected: Sequence[int],
) -> bool:
    for w in conflicts:
        if not any(len({features[j][i] for i in w}) > 1 for j in selected):
            return False
    return True


def optimum_cost(
    predicate,
    feature_count: int,
    costs: Sequence[int],
) -> int | None:
    best = math.inf
    for mask in range(1 << feature_count):
        selected = [j for j in range(feature_count) if (mask >> j) & 1]
        if predicate(selected):
            best = min(best, sum(costs[j] for j in selected))
    return None if math.isinf(best) else int(best)


def run() -> dict[str, object]:
    rng = random.Random(SEED)
    generated_cases = 1000
    subset_equivalence_checks = 0
    optimum_mismatches = 0
    conflict_size_violations = 0
    cases_with_higher_order_conflict = 0
    maximum_conflict_size = 0
    total_conflicts = 0

    for _ in range(generated_cases):
        action_count = rng.randint(1, 4)
        actions = list(range(action_count))
        state_count = rng.randint(1, 8)
        fibre_count = rng.randint(1, 3)
        base = [rng.randrange(fibre_count) for _ in range(state_count)]

        safe_sets: list[set[int]] = []
        for _state in range(state_count):
            mask = rng.randint(1, (1 << action_count) - 1)
            safe_sets.append({a for a in actions if (mask >> a) & 1})

        feature_count = rng.randint(0, 6)
        features: list[list[int]] = []
        costs: list[int] = []
        for _feature in range(feature_count):
            value_count = rng.randint(1, 3)
            features.append([rng.randrange(value_count) for _ in range(state_count)])
            costs.append(rng.randint(1, 5))

        conflicts = minimal_conflicts(base, safe_sets, actions)
        total_conflicts += len(conflicts)
        if conflicts:
            maximum_conflict_size = max(maximum_conflict_size, max(map(len, conflicts)))
        if any(len(w) > action_count for w in conflicts):
            conflict_size_violations += 1
        if any(len(w) > 2 for w in conflicts):
            cases_with_higher_order_conflict += 1

        for mask in range(1 << feature_count):
            selected = [j for j in range(feature_count) if (mask >> j) & 1]
            direct = selected_features_safe(base, safe_sets, actions, features, selected)
            cover = selected_features_cover(conflicts, features, selected)
            subset_equivalence_checks += 1
            if direct != cover:
                raise AssertionError({
                    "base": base,
                    "safe_sets": [sorted(x) for x in safe_sets],
                    "features": features,
                    "selected": selected,
                    "conflicts": conflicts,
                    "direct": direct,
                    "cover": cover,
                })

        direct_opt = optimum_cost(
            lambda selected: selected_features_safe(base, safe_sets, actions, features, selected),
            feature_count,
            costs,
        )
        cover_opt = optimum_cost(
            lambda selected: selected_features_cover(conflicts, features, selected),
            feature_count,
            costs,
        )
        if direct_opt != cover_opt:
            optimum_mismatches += 1

    assert conflict_size_violations == 0
    assert optimum_mismatches == 0

    # Higher-order hostile control: every pair has a safe action, the triple does not.
    actions = [0, 1, 2]
    base = [0, 0, 0]
    safe_sets = [{1, 2}, {0, 2}, {0, 1}]
    triple_conflicts = minimal_conflicts(base, safe_sets, actions)
    assert triple_conflicts == [(0, 1, 2)]
    assert all(
        safe_intersection((safe_sets[i] for i in pair), actions)
        for pair in itertools.combinations(range(3), 2)
    )
    assert not safe_intersection(safe_sets, actions)

    # Tightness of the |A| bound for m=4.
    actions4 = [0, 1, 2, 3]
    base4 = [0, 0, 0, 0]
    safe4 = [set(actions4) - {i} for i in actions4]
    tight = minimal_conflicts(base4, safe4, actions4)
    assert tight == [(0, 1, 2, 3)]

    result: dict[str, object] = {
        "schema": SCHEMA,
        "status": "PASS",
        "seed": SEED,
        "generated_cases": generated_cases,
        "feature_subset_equivalence_checks": subset_equivalence_checks,
        "total_minimal_conflicts": total_conflicts,
        "maximum_conflict_size_in_generated_panel": maximum_conflict_size,
        "cases_with_higher_order_conflict": cases_with_higher_order_conflict,
        "conflict_size_bound_violations": conflict_size_violations,
        "optimum_cost_mismatches": optimum_mismatches,
        "three_action_pairwise_insufficiency_control": "PASS",
        "four_action_tightness_control": "PASS",
        "authority": {
            "all_size_theorem_from_computation": False,
            "all_size_theorem_from_displayed_proof": True,
            "finite_implementation_controls": True,
            "generic_set_cover_novelty": False,
            "external_solver_selection_value": False,
        },
    }
    payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    result["content_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def main() -> None:
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    Path(__file__).with_name("SAFE_FEATURE_COVER_R10_RESULTS.json").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
