#!/usr/bin/env python3
"""Arithmetic and finite-signature checks for PACKING_DEFECT_CORE_FORMALISM_V1.

The all-prime statements are proved symbolically in the Markdown note. This
program is a regression receipt for indexing, parity, support-complement
inequalities, and the exact p=7,q=1 excess-signature slice.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from typing import Dict, Iterable, Iterator, List, Sequence, Tuple


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def partitions_bounded(total: int, parts: int, maximum: int, minimum: int = 1) -> Iterator[Tuple[int, ...]]:
    """Yield nondecreasing bounded partitions with exactly ``parts`` entries."""

    current: List[int] = []

    def visit(left: int, slots: int, lower: int) -> Iterator[Tuple[int, ...]]:
        if slots == 0:
            if left == 0:
                yield tuple(current)
            return
        if left < slots * lower or left > slots * maximum:
            return
        upper = min(maximum, left // slots)
        for value in range(lower, upper + 1):
            current.append(value)
            yield from visit(left - value, slots - 1, value)
            current.pop()

    yield from visit(total, parts, minimum)


def corridor_triples() -> List[Tuple[int, int, int]]:
    """Reproduce the six p=7 atom corridors from their declared donor bounds."""

    out = set()
    total = 37
    max_atom = 19

    # shortest atom 8; its 29-term complement has a dividing atom <=10
    a = 8
    for b in range(a, max_atom + 1):
        c = total - a - b
        if b <= c <= max_atom and b <= 10:
            out.add((a, b, c))

    # shortest atom 9; its 28-term complement has a dividing atom <=12
    a = 9
    for b in range(a, max_atom + 1):
        c = total - a - b
        if b <= c <= max_atom and b <= 12:
            out.add((a, b, c))

    # shortest atom 10; its 27-term complement has a dividing atom <=10
    a = 10
    for b in range(a, max_atom + 1):
        c = total - a - b
        if b <= c <= max_atom and b <= 10:
            out.add((a, b, c))

    return sorted(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-prime", type=int, default=401)
    parser.add_argument("--max-m", type=int, default=80)
    parser.add_argument("--max-q", type=int, default=80)
    args = parser.parse_args()

    primes = [p for p in range(5, args.max_prime + 1) if is_prime(p)]
    checked = 0

    for p in primes:
        assert p % 2 == 1
        M = (5 * p - 5) // 2
        D1 = 3 * p - 2
        D2 = (9 * p - 5) // 2
        assert D2 - 2 * p == M
        assert D1 - p == 2 * p - 2 <= M

        for m in range(3, args.max_m + 1):
            for q in range(1, args.max_q + 1):
                N = p * m + M + q

                # Supports through m+2 fail by raw coordinate capacity.
                cap_m2 = (m + 2) * (p - 1)
                assert N - cap_m2 == m + (p - 1) // 2 + q
                assert N > cap_m2

                # At support m+3, capacity either already fails or the exact
                # p-complement lemma embeds a forbidden short zero-sum.
                s = m + 3
                delta = s * (p - 1) - N
                assert delta == (p - 1) // 2 - m - q
                if delta < 0:
                    assert s * (p - 1) < N
                else:
                    complement_length = s + delta
                    assert complement_length == (p + 5) // 2 - q
                    assert 1 <= complement_length <= p
                    assert 2 * delta <= p - 2

                # Direction-capacity identity.
                quotient, remainder = divmod(N, p - 1)
                direction_floor = quotient + (1 if remainder else 0)
                assert direction_floor == -(-N // (p - 1))
                assert direction_floor >= m + 3
                checked += 1

    # Exact p=7 terminal-core excess signatures at q=1.
    p = 7
    M = 15
    total_excess = M + 1
    max_excess = 2 * p - 2
    signatures_by_m: Dict[int, List[Tuple[int, ...]]] = {}
    for m in range(3, total_excess + 1):
        rows = list(partitions_bounded(total_excess, m, max_excess))
        # The D2 pair condition is automatic in this q=1 slice, but assert it.
        for row in rows:
            assert all(row[i] + row[j] <= M for i in range(len(row)) for j in range(i + 1, len(row)))
        if rows:
            signatures_by_m[m] = rows

    distribution = {m: len(rows) for m, rows in signatures_by_m.items()}
    expected_distribution = {
        3: 19,
        4: 33,
        5: 37,
        6: 35,
        7: 28,
        8: 22,
        9: 15,
        10: 11,
        11: 7,
        12: 5,
        13: 3,
        14: 2,
        15: 1,
        16: 1,
    }
    assert distribution == expected_distribution
    assert sum(distribution.values()) == 219

    triple_excesses = signatures_by_m[3]
    assert len(triple_excesses) == 19
    atom_triples = sorted(tuple(p + e for e in row) for row in triple_excesses)
    expected_corridors = [
        (8, 10, 19),
        (9, 9, 19),
        (9, 10, 18),
        (9, 11, 17),
        (9, 12, 16),
        (10, 10, 17),
    ]
    assert corridor_triples() == expected_corridors
    assert all(row in atom_triples for row in expected_corridors)

    canonical = {
        "p7_q1_signature_distribution": distribution,
        "p7_q1_total_signatures": 219,
        "p7_m3_raw_signatures": atom_triples,
        "p7_m3_donor_corridors": expected_corridors,
    }
    digest = hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    print(
        json.dumps(
            {
                "status": "PACKING_DEFECT_CORE_ARITHMETIC_GREEN",
                "checked_primes": len(primes),
                "max_prime": primes[-1] if primes else None,
                "symbolic_parameter_cases": checked,
                "p7_q1_total_signatures": 219,
                "p7_m3_raw_signatures": 19,
                "p7_m3_donor_corridors": 6,
                "canonical_sha256": digest,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
