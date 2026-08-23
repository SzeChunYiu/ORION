#!/usr/bin/env python3
"""Exploratory X1-B k=3 scalar-residual classification.

IMPORTANT EVIDENCE STATUS
-------------------------
This script records an exploratory derivation whose aggregate outcome was seen
before this file was frozen.  It is NOT a prospective theorem receipt.  A
separate independently written confirmatory verifier is required before the
result can be used as theorem evidence.

Mathematical question
---------------------
Classify 10-term multisets A over F_3^3 satisfying the exact residual gates
forced by a hypothetical C_15^3 counterexample in the k=3 branch:

* no nonempty zero-sum of length <= 3;
* no two disjoint nonempty zero-sum subsequences.

For each such A, test whether there exists f:A->F_5 such that

    sum_{a in B} f(a) = 1

for EVERY nonempty zero-sum subsequence B of A.

The common RHS can be normalized to 1 because X1-B local scalarization gives a
common NONZERO scalar value.

Symmetry
--------
We enumerate supports modulo GL(3,3), then multiplicity-two choices modulo the
support stabilizer.  Because no 3-term zero sum survives, each element occurs at
most twice.  Because every 9 distinct points in F_3^3 contain a zero-sum of
length <=3, support size is in {5,6,7,8} for a 10-term surviving multiset.
"""
from __future__ import annotations

from itertools import combinations, product
import json

P3 = 3
P5 = 5
ZERO = (0, 0, 0)
ELS = [
    (a, b, c)
    for a in range(3)
    for b in range(3)
    for c in range(3)
    if (a, b, c) != ZERO
]
INDEX = {v: i for i, v in enumerate(ELS)}


def add(*vectors):
    return tuple(sum(coords) % 3 for coords in zip(*vectors))


def neg(v):
    return tuple((-x) % 3 for x in v)


def det3(m):
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    return (
        a * (e * i - f * h)
        - b * (d * i - f * g)
        + c * (d * h - e * g)
    ) % 3


def mat_vec(m, v):
    return tuple(sum(m[r][c] * v[c] for c in range(3)) % 3 for r in range(3))


def gl33_maps():
    maps = []
    for vals in product(range(3), repeat=9):
        m = (vals[0:3], vals[3:6], vals[6:9])
        if det3(m) == 0:
            continue
        maps.append(tuple(INDEX[mat_vec(m, v)] for v in ELS))
    assert len(maps) == 11232
    return tuple(maps)


def support_families():
    opposite = {INDEX[v]: INDEX[neg(v)] for v in ELS}
    bad_third = {}
    for i in range(len(ELS)):
        for j in range(i + 1, len(ELS)):
            k = INDEX.get(neg(add(ELS[i], ELS[j])))
            if k is not None:
                bad_third[(i, j)] = k

    out = {s: [] for s in range(5, 9)}

    def rec(chosen, start, target):
        if len(chosen) == target:
            out[target].append(tuple(chosen))
            return
        needed = target - len(chosen)
        for i in range(start, len(ELS) - needed + 1):
            if opposite[i] in chosen:
                continue
            if any(
                bad_third.get((min(a, b), max(a, b))) == i
                for a, b in combinations(chosen, 2)
            ):
                continue
            chosen.append(i)
            rec(chosen, i + 1, target)
            chosen.pop()

    for size in out:
        rec([], 0, size)
    return out


def orbit_representatives(rows, maps):
    remaining = set(rows)
    reps = []
    while remaining:
        row = next(iter(remaining))
        orbit = {tuple(sorted(mp[i] for i in row)) for mp in maps}
        remaining.difference_update(orbit)
        reps.append(row)
    return reps


def multiplicity_orbits(support, doubled_count, maps):
    support_set = set(support)
    stabilizer = [mp for mp in maps if {mp[i] for i in support} == support_set]
    remaining = set(combinations(support, doubled_count))
    reps = []
    while remaining:
        row = next(iter(remaining))
        orbit = {tuple(sorted(mp[i] for i in row)) for mp in stabilizer}
        remaining.difference_update(orbit)
        reps.append(row)
    return reps, len(stabilizer)


def zero_sum_masks(position_elements):
    n = len(position_elements)
    masks = []
    for mask in range(1, 1 << n):
        s0 = s1 = s2 = 0
        for j, element_index in enumerate(position_elements):
            if mask >> j & 1:
                x, y, z = ELS[element_index]
                s0 = (s0 + x) % 3
                s1 = (s1 + y) % 3
                s2 = (s2 + z) % 3
        if (s0, s1, s2) == ZERO:
            masks.append(mask)
    return masks


def has_disjoint_pair(masks):
    for i, a in enumerate(masks):
        for b in masks[i + 1 :]:
            if a & b == 0:
                return True
    return False


def affine_system_consistent(masks, nvars=10):
    # Rows are incidence(mask) dot f = 1 over F_5.
    rows = []
    for mask in masks:
        rows.append([int(mask >> j & 1) for j in range(nvars)] + [1])

    rank = 0
    for col in range(nvars):
        pivot = next(
            (r for r in range(rank, len(rows)) if rows[r][col] % 5 != 0),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col] % 5, -1, 5)
        rows[rank] = [(x * inv) % 5 for x in rows[rank]]
        for r in range(len(rows)):
            if r == rank or rows[r][col] % 5 == 0:
                continue
            factor = rows[r][col] % 5
            rows[r] = [
                (rows[r][c] - factor * rows[rank][c]) % 5
                for c in range(nvars + 1)
            ]
        rank += 1

    inconsistent = any(
        all(row[c] % 5 == 0 for c in range(nvars)) and row[-1] % 5 != 0
        for row in rows
    )
    return (not inconsistent), rank


def main():
    maps = gl33_maps()
    supports = support_families()

    support_counts = {size: len(rows) for size, rows in supports.items()}
    support_orbit_counts = {}
    multiset_orbits = []
    stabilizer_rows = []

    for size in range(5, 9):
        reps = orbit_representatives(supports[size], maps)
        support_orbit_counts[size] = len(reps)
        doubled_count = 10 - size
        for support in reps:
            doubled_reps, stab_size = multiplicity_orbits(
                support, doubled_count, maps
            )
            stabilizer_rows.append((size, stab_size, len(doubled_reps)))
            for doubled in doubled_reps:
                multiset_orbits.append((support, doubled))

    surviving = []
    for support, doubled in multiset_orbits:
        doubled_set = set(doubled)
        positions = []
        for x in support:
            positions.extend([x] * (2 if x in doubled_set else 1))
        assert len(positions) == 10
        masks = zero_sum_masks(positions)
        if has_disjoint_pair(masks):
            continue
        consistent, rank = affine_system_consistent(masks)
        surviving.append(
            {
                "support_size": len(support),
                "zero_sum_subsequence_count": len(masks),
                "equal_value_system_consistent": consistent,
                "equation_rank": rank,
            }
        )

    result = {
        "schema": "ORION.RG.X1B.K3ScalarExploratory.v1",
        "evidence_status": "EXPLORATORY_DISCLOSED_BEFORE_CONFIRMATORY_FREEZE",
        "gl33_size": len(maps),
        "raw_support_counts": support_counts,
        "support_orbit_counts": support_orbit_counts,
        "multiset_orbit_count": len(multiset_orbits),
        "no_two_disjoint_zero_sum_orbit_count": len(surviving),
        "consistent_equal_value_orbit_count": sum(
            row["equal_value_system_consistent"] for row in surviving
        ),
        "inconsistent_equal_value_orbit_count": sum(
            not row["equal_value_system_consistent"] for row in surviving
        ),
        "survivor_support_size_histogram": {
            str(size): sum(row["support_size"] == size for row in surviving)
            for size in range(5, 9)
        },
        "novelty_authority": False,
        "scientific_authority": False,
        "theorem_authority": False,
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
