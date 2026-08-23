#!/usr/bin/env python3
"""Exact confirmatory checker for the Freeze--Schmid C_5^3, k=3 lower witness.

This checker was committed after an exploratory calculation found that the
standard 24-term Theorem-4.1 witness is insertion-saturated.  It is therefore
confirmatory/replay code, not a prospective discovery instrument.

It uses only primitive addition in (Z/5Z)^3 and exhaustive submultiset packing.
No solver/heuristic result is trusted.
"""
from __future__ import annotations

import json
from itertools import product

P = 5


def add(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple((x + y) % P for x, y in zip(a, b))  # type: ignore[return-value]


def smul(n: int, a: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple((n * x) % P for x in a)  # type: ignore[return-value]


def zero_subcounts(
    vectors: tuple[tuple[int, int, int], ...], counts: tuple[int, ...]
) -> tuple[tuple[int, ...], ...]:
    out: list[tuple[int, ...]] = []
    for sub in product(*(range(c + 1) for c in counts)):
        if not any(sub):
            continue
        total = (0, 0, 0)
        for n, v in zip(sub, vectors):
            total = add(total, smul(n, v))
        if total == (0, 0, 0):
            out.append(tuple(sub))
    return tuple(out)


def has_three_disjoint_zero_sums(
    vectors: tuple[tuple[int, int, int], ...], counts: tuple[int, ...]
) -> bool:
    zeros = zero_subcounts(vectors, counts)
    for a in zeros:
        rem1 = tuple(c - x for c, x in zip(counts, a))
        for b in zeros:
            if not all(x <= r for x, r in zip(b, rem1)):
                continue
            rem2 = tuple(r - x for r, x in zip(rem1, b))
            for c in zeros:
                if all(x <= r for x, r in zip(c, rem2)):
                    return True
    return False


def main() -> None:
    e1 = (1, 0, 0)
    e2 = (0, 1, 0)
    e3 = (0, 0, 1)

    # Theorem 4.1, r=s=3, t=1, p=5, k=3.  Use the injection
    # {1,2}->1, {1,3}->2, {2,3}->3, so
    # g1=e1+e2, g2=e1+e3, g3=e2+e3.
    g1 = (1, 1, 0)
    g2 = (1, 0, 1)
    g3 = (0, 1, 1)
    base_vectors = (e1, e2, e3, g1, g2, g3)
    # T=(g1 g2 g3)^2 g3 and S=T*e1^4*e2^4*e3^4*e3^5.
    base_counts = (4, 4, 9, 2, 2, 3)
    assert sum(base_counts) == 24

    base_has_three = has_three_disjoint_zero_sums(base_vectors, base_counts)
    if base_has_three:
        raise AssertionError("Freeze--Schmid lower witness unexpectedly has 3 zero sums")

    failures: list[tuple[int, int, int]] = []
    group = tuple(product(range(P), repeat=3))
    for x in group:
        if x in base_vectors:
            idx = base_vectors.index(x)
            counts = list(base_counts)
            counts[idx] += 1
            has_three = has_three_disjoint_zero_sums(base_vectors, tuple(counts))
        else:
            has_three = has_three_disjoint_zero_sums(
                base_vectors + (x,), base_counts + (1,)
            )
        if not has_three:
            failures.append(x)

    result = {
        "schema": "ORION.RG.X1F.FreezeSchmidInsertionSaturation.v1",
        "group": "C_5^3",
        "k": 3,
        "base_length": sum(base_counts),
        "base_has_three_disjoint_zero_sums": base_has_three,
        "extensions_checked": len(group),
        "extension_failures": [list(x) for x in failures],
        "all_one_term_extensions_have_three_disjoint_zero_sums": not failures,
        "claim_ceiling": "BOUNDED_EXACT_CONFIRMATORY_ONLY",
        "d3_exact_authority": False,
        "novelty_authority": False,
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
