#!/usr/bin/env python3
"""Exact compressed verifier for the X1-K D4(C_5^3) lower-bound witness.

Authority boundary
------------------
This verifies only three explicit multisets built from six fixed vector types.
It does not prove an upper bound for D_4(C_5^3), does not establish novelty, and
does not replace independent replay.

For a multiplicity box, every submultiset is uniquely described by its six
count coordinates.  We enumerate every nonzero count vector whose weighted
sum in F_5^3 is zero, then compute the maximum number of pairwise-disjoint
zero-sum submultisets in two different ways:

1. recursive memoized packing on the remaining multiplicity vector;
2. forward reachable layers of aggregate used multiplicities.

Both traversals are exact because disjointness is exactly componentwise
addition bounded by the source multiplicities.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import product
import json

MODULUS = 5
TYPE_NAMES = ("e1", "e2", "e3", "a", "b", "c")
TYPE_VECTORS = (
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 1, 0),  # a
    (1, 0, 1),  # b
    (0, 1, 1),  # c
)

ROWS = (
    {
        "row": "d3_established_control",
        "multiplicities": (4, 4, 9, 2, 2, 3),
        "expected_max_disjoint_zero_sums": 2,
        "role": "known-answer control: established 24-term D3 lower witness",
    },
    {
        "row": "d4_proposed_lower_witness",
        "multiplicities": (4, 4, 14, 2, 2, 3),
        "expected_max_disjoint_zero_sums": 3,
        "role": "proposed length-29 witness; max=3 implies D4(C_5^3)>=30",
    },
    {
        "row": "d4_anti_always_negative_neighbor",
        "multiplicities": (4, 4, 15, 2, 2, 3),
        "expected_max_disjoint_zero_sums": 4,
        "role": "length-30 near-neighbor that must be accepted as having four disjoint zero-sums",
    },
)

CountVector = tuple[int, ...]


def weighted_sum(counts: CountVector) -> tuple[int, int, int]:
    return tuple(
        sum(counts[i] * TYPE_VECTORS[i][coordinate] for i in range(len(TYPE_VECTORS)))
        % MODULUS
        for coordinate in range(3)
    )


def zero_sum_count_vectors(bounds: CountVector) -> tuple[CountVector, ...]:
    """Enumerate every nonempty zero-sum submultiset in count-vector form."""

    zero_sums: list[CountVector] = []
    ranges = tuple(range(bound + 1) for bound in bounds)
    for counts in product(*ranges):
        if not any(counts):
            continue
        candidate = tuple(int(value) for value in counts)
        if weighted_sum(candidate) == (0, 0, 0):
            zero_sums.append(candidate)
    return tuple(zero_sums)


def subtract_if_fits(remaining: CountVector, used: CountVector) -> CountVector | None:
    if any(used[i] > remaining[i] for i in range(len(remaining))):
        return None
    return tuple(remaining[i] - used[i] for i in range(len(remaining)))


def recursive_max_packing(
    bounds: CountVector, zero_sums: tuple[CountVector, ...]
) -> tuple[int, tuple[CountVector, ...], dict[str, int]]:
    """Exact maximum packing by recursion on remaining source multiplicities."""

    @lru_cache(maxsize=None)
    def solve(remaining: CountVector) -> tuple[int, CountVector | None]:
        best = 0
        best_choice: CountVector | None = None
        for zero_sum in zero_sums:
            next_remaining = subtract_if_fits(remaining, zero_sum)
            if next_remaining is None:
                continue
            candidate = 1 + solve(next_remaining)[0]
            if candidate > best:
                best = candidate
                best_choice = zero_sum
        return best, best_choice

    remaining = bounds
    optimum = solve(remaining)[0]
    packing: list[CountVector] = []
    while True:
        _, choice = solve(remaining)
        if choice is None:
            break
        packing.append(choice)
        next_remaining = subtract_if_fits(remaining, choice)
        assert next_remaining is not None
        remaining = next_remaining

    info = solve.cache_info()
    return (
        optimum,
        tuple(packing),
        {"hits": info.hits, "misses": info.misses, "states": info.currsize},
    )


def forward_max_packing(
    bounds: CountVector, zero_sums: tuple[CountVector, ...]
) -> tuple[int, tuple[int, ...]]:
    """Independent forward traversal of aggregate resource-use layers.

    Layer k is the set of aggregate count vectors obtainable as the sum of k
    nonempty zero-sum count vectors while staying componentwise within bounds.
    The largest nonempty layer is the maximum disjoint packing number.
    """

    reachable: set[CountVector] = {tuple(0 for _ in bounds)}
    layer_sizes: list[int] = []
    largest_nonempty_layer = 0

    for layer in range(1, sum(bounds) + 2):
        next_reachable: set[CountVector] = set()
        for aggregate in reachable:
            for zero_sum in zero_sums:
                total = tuple(aggregate[i] + zero_sum[i] for i in range(len(bounds)))
                if all(total[i] <= bounds[i] for i in range(len(bounds))):
                    next_reachable.add(total)
        layer_sizes.append(len(next_reachable))
        if not next_reachable:
            break
        largest_nonempty_layer = layer
        reachable = next_reachable

    return largest_nonempty_layer, tuple(layer_sizes)


def named_count_vector(counts: CountVector) -> dict[str, int]:
    return {name: counts[i] for i, name in enumerate(TYPE_NAMES) if counts[i]}


def evaluate_row(row: dict[str, object]) -> dict[str, object]:
    bounds = tuple(int(value) for value in row["multiplicities"])  # type: ignore[arg-type]
    expected = int(row["expected_max_disjoint_zero_sums"])
    zero_sums = zero_sum_count_vectors(bounds)

    recursive_value, recursive_packing, cache = recursive_max_packing(bounds, zero_sums)
    forward_value, forward_layer_sizes = forward_max_packing(bounds, zero_sums)

    assert recursive_value == forward_value, (
        row["row"],
        recursive_value,
        forward_value,
    )
    assert recursive_value == expected, (row["row"], recursive_value, expected)

    aggregate = tuple(
        sum(piece[i] for piece in recursive_packing) for i in range(len(bounds))
    )
    assert all(aggregate[i] <= bounds[i] for i in range(len(bounds)))
    assert all(weighted_sum(piece) == (0, 0, 0) for piece in recursive_packing)

    return {
        "row": row["row"],
        "role": row["role"],
        "length": sum(bounds),
        "multiplicities": named_count_vector(bounds),
        "zero_sum_count_vectors": len(zero_sums),
        "recursive_max_disjoint_zero_sums": recursive_value,
        "forward_max_disjoint_zero_sums": forward_value,
        "forward_layer_sizes_including_first_empty": list(forward_layer_sizes),
        "recursive_cache": cache,
        "one_maximum_packing": [named_count_vector(piece) for piece in recursive_packing],
        "expected": expected,
        "status": "PASS",
    }


def main() -> None:
    results = [evaluate_row(dict(row)) for row in ROWS]
    payload = {
        "schema": "ORION.RG.X1K.D4LowerWitnessReplay.v1",
        "authority": {
            "explicit_witness_only": True,
            "d4_upper_bound_authority": False,
            "novelty_claim": False,
            "independent_replay_still_required": True,
        },
        "group": "C_5^3",
        "type_vectors": {name: list(TYPE_VECTORS[i]) for i, name in enumerate(TYPE_NAMES)},
        "rows": results,
        "consequence_if_replayed": (
            "The length-29 row has maximum zero-sum packing number 3, so it has "
            "no four pairwise-disjoint nonempty zero-sums and proves D_4(C_5^3)>=30."
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
