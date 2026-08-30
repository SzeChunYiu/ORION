#!/usr/bin/env python3
"""Independent finite regression for ORION10.UNIVERSAL_VOCABULARY_MINIMALITY.v2.

The theorem is deductive; this checker is only a finite specialization/control.
It imports no ORION module and uses exact integer/Boolean arithmetic.
"""

from __future__ import annotations

import json

BELL = {1: 1, 2: 2, 3: 5, 4: 15, 5: 52, 6: 203, 7: 877, 8: 4140}


def partitions(n: int):
    """Yield set partitions of range(n) in restricted-growth order."""
    if n == 0:
        yield ()
        return

    def rec(i: int, blocks: list[list[int]]):
        if i == n:
            yield tuple(tuple(block) for block in blocks)
            return
        for j in range(len(blocks)):
            blocks[j].append(i)
            yield from rec(i + 1, blocks)
            blocks[j].pop()
        blocks.append([i])
        yield from rec(i + 1, blocks)
        blocks.pop()

    yield from rec(1, [[0]])


def is_discrete(partition) -> bool:
    return all(len(block) == 1 for block in partition)


def factors_through(partition, cost: tuple[int, ...]) -> bool:
    """A cost factors through the partition iff it is constant on each block."""
    return all(len({cost[i] for i in block}) == 1 for block in partition)


def mixed_fibre_witness(partition, n: int) -> tuple[int, ...]:
    """Construct the theorem's binary witness for one non-discrete partition."""
    block = next(block for block in partition if len(block) > 1)
    cost = [0] * n
    cost[block[1]] = 1
    return tuple(cost)


def main() -> int:
    rows = []
    total_partitions = 0
    non_discrete_refuted = 0
    discrete_binary_costs_checked = 0

    for n, expected_bell in BELL.items():
        parts = list(partitions(n))
        assert len(parts) == expected_bell, (n, len(parts), expected_bell)

        discrete = [p for p in parts if is_discrete(p)]
        assert len(discrete) == 1

        for partition in parts:
            total_partitions += 1
            if is_discrete(partition):
                for mask in range(1 << n):
                    cost = tuple((mask >> i) & 1 for i in range(n))
                    assert factors_through(partition, cost)
                    discrete_binary_costs_checked += 1
            else:
                witness = mixed_fibre_witness(partition, n)
                assert not factors_through(partition, witness)
                non_discrete_refuted += 1

        rows.append(
            {
                "n": n,
                "partitions": len(parts),
                "universally_exact_partitions": 1,
                "non_discrete_refuted_by_binary_witness": len(parts) - 1,
            }
        )

    out = {
        "status": "PASS",
        "theorem": "universal exactness iff vocabulary is injective",
        "scope": "finite regression n=1..8; theorem itself is all-cardinality",
        "rows": rows,
        "total_partitions": total_partitions,
        "non_discrete_refuted": non_discrete_refuted,
        "discrete_binary_costs_checked": discrete_binary_costs_checked,
        "scientific_authority_delta": "NONE",
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
