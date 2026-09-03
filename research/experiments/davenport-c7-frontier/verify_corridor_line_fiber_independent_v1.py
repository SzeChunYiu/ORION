#!/usr/bin/env python3
"""Independent multiplicity-vector verifier for the C7 line-fiber table.

Unlike the primary checker, this program never enumerates occurrence subsets by
bit mask. It enumerates multiplicity vectors and builds bounded subset sums by
dynamic programming over the six nonzero residues.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Dict, Iterator, List, Sequence, Set, Tuple

P = 7
EXPECTED_DETAIL_SHA256 = "d8f81eb780c8ecc9671de0f02e13879decf846d0607c5295225f61838895bcf4"
EXPECTED_COUNTS = {
    1: (6, 5, {5: 6}),
    2: (18, 3, {2: 6, 3: 12}),
    3: (30, 1, {0: 6, 1: 24}),
    4: (24, 1, {0: 12, 1: 12}),
    5: (12, 1, {0: 6, 1: 6}),
    6: (6, 0, {0: 6}),
}


def multiplicity_vectors(total: int, slots: int = P - 1) -> Iterator[Tuple[int, ...]]:
    current = [0] * slots

    def visit(index: int, left: int) -> Iterator[Tuple[int, ...]]:
        if index == slots - 1:
            current[index] = left
            yield tuple(current)
            return
        for value in range(left + 1):
            current[index] = value
            yield from visit(index + 1, left - value)

    yield from visit(0, total)


def reachable_states(multiplicities: Sequence[int]) -> Set[Tuple[int, int]]:
    reachable: Set[Tuple[int, int]] = {(0, 0)}
    for residue, multiplicity in enumerate(multiplicities, start=1):
        updated: Set[Tuple[int, int]] = set()
        for length, total in reachable:
            for take in range(multiplicity + 1):
                updated.add((length + take, (total + take * residue) % P))
        reachable = updated
    return reachable


def expand(multiplicities: Sequence[int]) -> Tuple[int, ...]:
    return tuple(
        residue
        for residue, multiplicity in enumerate(multiplicities, start=1)
        for _ in range(multiplicity)
    )


def main() -> int:
    detail: List[dict] = []
    aggregate: Dict[int, dict] = {}

    for length in range(1, P):
        distribution: Counter[int] = Counter()
        count = 0
        max_allowed = -1

        for multiplicities in multiplicity_vectors(length):
            reachable = reachable_states(multiplicities)
            if any(size > 0 and total == 0 for size, total in reachable):
                continue

            all_nonempty = {total for size, total in reachable if size > 0}
            at_least_two = {total for size, total in reachable if size >= 2}
            negative_nonempty = {(-total) % P for total in all_nonempty}
            allowed = set(range(1, P)) - at_least_two - negative_nonempty
            sequence = expand(multiplicities)

            count += 1
            max_allowed = max(max_allowed, len(allowed))
            distribution[len(allowed)] += 1
            detail.append({"sequence": list(sequence), "allowed": sorted(allowed)})

            if length >= 3:
                assert allowed <= set(sequence)

        expected_count, expected_max, expected_distribution = EXPECTED_COUNTS[length]
        assert count == expected_count
        assert max_allowed == expected_max
        assert dict(sorted(distribution.items())) == expected_distribution
        aggregate[length] = {
            "multisets": count,
            "max_allowed": max_allowed,
            "distribution": dict(sorted(distribution.items())),
        }

    detail.sort(key=lambda row: (len(row["sequence"]), row["sequence"]))
    encoded = json.dumps(detail, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    assert digest == EXPECTED_DETAIL_SHA256, digest
    assert len(detail) == 96

    print(
        json.dumps(
            {
                "prime": P,
                "method": "multiplicity-vector bounded-subsum DP",
                "zero_sumfree_multisets": len(detail),
                "detail_sha256": digest,
                "by_line_occupancy": aggregate,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
