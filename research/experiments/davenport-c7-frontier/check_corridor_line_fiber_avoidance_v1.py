#!/usr/bin/env python3
r"""Exact C7 line-fiber check induced by maximal-atom proper-subsum avoidance.

For a zero-sumfree scalar multiset A in F_7^* on one projective direction,
define

    R(A) = F_7^* \ (Sigma_{>=2}(A) union -Sigma_{>=1}(A)).

Every scalar used by the maximal atom on that direction must lie in R(A).
This checker enumerates all unordered zero-sumfree scalar multisets of lengths
1,...,6 and freezes the complete detailed map and aggregate table.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from itertools import combinations_with_replacement
from typing import Dict, Iterable, List, Sequence, Set, Tuple

P = 7
EXPECTED_DETAIL_SHA256 = "d8f81eb780c8ecc9671de0f02e13879decf846d0607c5295225f61838895bcf4"
EXPECTED = {
    1: {"multisets": 6, "scale_orbits": 1, "max_allowed": 5, "distribution": {5: 6}},
    2: {"multisets": 18, "scale_orbits": 3, "max_allowed": 3, "distribution": {2: 6, 3: 12}},
    3: {"multisets": 30, "scale_orbits": 5, "max_allowed": 1, "distribution": {0: 6, 1: 24}},
    4: {"multisets": 24, "scale_orbits": 4, "max_allowed": 1, "distribution": {0: 12, 1: 12}},
    5: {"multisets": 12, "scale_orbits": 2, "max_allowed": 1, "distribution": {0: 6, 1: 6}},
    6: {"multisets": 6, "scale_orbits": 1, "max_allowed": 0, "distribution": {0: 6}},
}


def subsums_by_size(sequence: Sequence[int]) -> Dict[int, Set[int]]:
    out: Dict[int, Set[int]] = {size: set() for size in range(1, len(sequence) + 1)}
    for mask in range(1, 1 << len(sequence)):
        size = 0
        total = 0
        for index, value in enumerate(sequence):
            if mask & (1 << index):
                size += 1
                total = (total + value) % P
        out[size].add(total)
    return out


def allowed_scalars(sequence: Sequence[int]) -> Set[int]:
    by_size = subsums_by_size(sequence)
    nonempty = set().union(*by_size.values())
    if 0 in nonempty:
        raise ValueError("allowed_scalars requires a zero-sumfree sequence")
    at_least_two: Set[int] = set()
    for size in range(2, len(sequence) + 1):
        at_least_two.update(by_size[size])
    negative_nonempty = {(-value) % P for value in nonempty}
    return set(range(1, P)) - at_least_two - negative_nonempty


def canonical_under_scaling(sequence: Sequence[int]) -> Tuple[int, ...]:
    return min(tuple(sorted((scalar * value) % P for value in sequence)) for scalar in range(1, P))


def main() -> int:
    detail: List[dict] = []
    aggregate: Dict[int, dict] = {}

    for length in range(1, P):
        distribution: Counter[int] = Counter()
        scale_orbits: Set[Tuple[int, ...]] = set()
        max_allowed = -1
        count = 0

        for sequence in combinations_with_replacement(range(1, P), length):
            by_size = subsums_by_size(sequence)
            nonempty = set().union(*by_size.values())
            if 0 in nonempty:
                continue

            allowed = allowed_scalars(sequence)
            count += 1
            max_allowed = max(max_allowed, len(allowed))
            distribution[len(allowed)] += 1
            scale_orbits.add(canonical_under_scaling(sequence))
            detail.append({"sequence": list(sequence), "allowed": sorted(allowed)})

            # Scaling covariance is an independent structural invariant of R(A).
            for scalar in range(1, P):
                scaled = tuple(sorted((scalar * value) % P for value in sequence))
                expected_scaled_allowed = {(scalar * value) % P for value in allowed}
                assert allowed_scalars(scaled) == expected_scaled_allowed

            # The corridor-strength statement: once the line contains at least
            # three V-terms, every surviving U-scalar is already a V-scalar.
            if length >= 3:
                assert allowed <= set(sequence)

        row = {
            "multisets": count,
            "scale_orbits": len(scale_orbits),
            "max_allowed": max_allowed,
            "distribution": dict(sorted(distribution.items())),
        }
        assert row == EXPECTED[length], (length, row, EXPECTED[length])
        aggregate[length] = row

    encoded = json.dumps(detail, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    assert digest == EXPECTED_DETAIL_SHA256, digest
    assert len(detail) == 96

    output = {
        "prime": P,
        "zero_sumfree_multisets": len(detail),
        "detail_sha256": digest,
        "by_line_occupancy": aggregate,
        "corridor_consequence": {
            "occupancy_3_to_5": "at most one allowed scalar, and it is already in the short atom support",
            "occupancy_6": "no allowed scalar",
        },
    }
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
