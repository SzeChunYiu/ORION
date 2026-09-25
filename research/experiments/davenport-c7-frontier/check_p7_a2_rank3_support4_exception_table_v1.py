#!/usr/bin/env python3
"""Exact p=7 a=2 rank-three support-four exception-table proof."""
from __future__ import annotations

import hashlib
import json
from itertools import product
from typing import Iterable

P = 7
ZERO = (0, 0, 0)
E1 = (1, 0, 0)
E2 = (0, 1, 0)
S = (0, 0, 1)
G = (3, 3, 1)
U_SUPPORT = {E1, E2, S, G}
U_CAPS = (6, 6, 2, 5)
ROWS = (
    (1, 1, 2, 6),
    (1, 1, 3, 5),
    (1, 1, 4, 4),
    (2, 1, 1, 6),
    (2, 1, 2, 5),
    (2, 1, 3, 4),
)

Vec = tuple[int, int, int]
Row = tuple[int, int, int, int]


def add(*vectors: Vec) -> Vec:
    return tuple(sum(v[i] for v in vectors) % P for i in range(3))  # type: ignore[return-value]


def mul(k: int, v: Vec) -> Vec:
    return tuple((k * x) % P for x in v)  # type: ignore[return-value]


def neg(v: Vec) -> Vec:
    return mul(-1, v)


def det(a: Vec, b: Vec, c: Vec) -> int:
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    ) % P


def weighted_sum(counts: Iterable[int], values: Iterable[Vec]) -> Vec:
    out = ZERO
    for count, value in zip(counts, values):
        out = add(out, mul(count, value))
    return out


def occurrence_depth_table() -> dict[Vec, int]:
    """Shortest bounded representation over the actual 19 occurrences of U."""
    terms = [E1] * 6 + [E2] * 6 + [S] * 2 + [G] * 5
    inf = 10**9
    depth: dict[Vec, int] = {ZERO: 0}
    for term in terms:
        nxt = dict(depth)
        for value, cost in depth.items():
            target = add(value, term)
            nxt[target] = min(nxt.get(target, inf), cost + 1)
        depth = nxt
    assert len(depth) == P**3
    return depth


def closed_depth(value: Vec) -> int:
    """Independent formula cross-check; not used to classify candidates."""
    u = 4
    best = 10**9
    for g_count in range(6):
        s_count = (value[2] - g_count) % P
        if s_count > 2:
            continue
        e1_count = (value[0] + u * g_count) % P
        e2_count = (value[1] + u * g_count) % P
        best = min(best, e1_count + e2_count + s_count + g_count)
    assert best < 10**9
    return best


def primitive_row(row: Row) -> bool:
    c, d, r, t = row
    for q in range(2, P):
        residues = ((q * c) % P, (q * d) % P, (q * r) % P, (q * t) % P)
        if all(value <= cap for value, cap in zip(residues, row)):
            return False
    return True


def solve_y(row: Row, x: Vec) -> Vec:
    c, d, r, t = row
    rhs = weighted_sum((c, d, r), (S, G, x))
    return mul(-pow(t, -1, P), rhs)


def structural_candidates(row: Row) -> list[tuple[Vec, Vec]]:
    out: list[tuple[Vec, Vec]] = []
    for x in product(range(P), repeat=3):
        if x == ZERO or x in U_SUPPORT or det(S, G, x) == 0:
            continue
        y = solve_y(row, x)
        if y == ZERO or y in U_SUPPORT or y == x:
            continue
        c, d, r, t = row
        assert weighted_sum((c, d, r, t), (S, G, x, y)) == ZERO
        assert det(S, G, x) != 0
        out.append((x, y))
    return out


def power_compatible(depth: dict[Vec, int], value: Vec, multiplicity: int) -> bool:
    for q in range(1, multiplicity + 1):
        qv = mul(q, value)
        if depth[qv] < q:
            return False
        if depth[neg(qv)] < 10 - q:
            return False
    return True


# Key: (row, x, y). Value: ((s,g,x,y)-counts, (e1,e2,s,g)-counts).
CERTIFICATES: dict[tuple[Row, Vec, Vec], tuple[Row, Row]] = {
    ((1, 1, 2, 6), (1, 2, 0), (5, 0, 2)): ((0, 0, 2, 3), (1, 0, 0, 1)),
    ((1, 1, 2, 6), (2, 1, 0), (0, 5, 2)): ((0, 0, 2, 3), (0, 1, 0, 1)),
    ((1, 1, 4, 4), (0, 4, 1), (1, 4, 2)): ((0, 0, 1, 1), (0, 0, 2, 2)),
    ((1, 1, 4, 4), (1, 4, 2), (0, 4, 1)): ((0, 0, 1, 1), (0, 0, 2, 2)),
    ((1, 1, 4, 4), (4, 0, 1), (4, 1, 2)): ((0, 0, 1, 1), (0, 0, 2, 2)),
    ((1, 1, 4, 4), (4, 1, 2), (4, 0, 1)): ((0, 0, 1, 1), (0, 0, 2, 2)),
    ((2, 1, 1, 6), (1, 5, 6), (4, 1, 2)): ((0, 0, 1, 3), (2, 0, 0, 2)),
    ((2, 1, 1, 6), (2, 5, 5), (5, 1, 1)): ((0, 0, 1, 1), (0, 1, 1, 0)),
    ((2, 1, 1, 6), (5, 1, 6), (1, 4, 2)): ((0, 0, 1, 3), (0, 2, 0, 2)),
    ((2, 1, 1, 6), (5, 2, 5), (1, 5, 1)): ((0, 0, 1, 1), (1, 0, 1, 0)),
    ((2, 1, 2, 5), (0, 2, 4), (5, 0, 2)): ((0, 0, 2, 2), (1, 0, 1, 1)),
    ((2, 1, 2, 5), (2, 0, 4), (0, 5, 2)): ((0, 0, 2, 2), (0, 1, 1, 1)),
    ((2, 1, 2, 5), (4, 6, 3), (2, 4, 1)): ((0, 0, 1, 2), (0, 1, 0, 2)),
    ((2, 1, 2, 5), (6, 4, 3), (4, 2, 1)): ((0, 0, 1, 2), (1, 0, 0, 2)),
}


def verify_certificate(key: tuple[Row, Vec, Vec], certificate: tuple[Row, Row]) -> int:
    row, x, y = key
    v_counts, u_counts = certificate
    assert all(count <= cap for count, cap in zip(v_counts, row))
    assert all(count <= cap for count, cap in zip(u_counts, U_CAPS))
    v_sum = weighted_sum(v_counts, (S, G, x, y))
    u_sum = weighted_sum(u_counts, (E1, E2, S, G))
    assert add(v_sum, u_sum) == ZERO
    length = sum(v_counts) + sum(u_counts)
    assert 1 <= length <= 8
    return length


def main() -> None:
    depth = occurrence_depth_table()
    formula_mismatches = 0
    for value in product(range(P), repeat=3):
        if depth[value] != closed_depth(value):
            formula_mismatches += 1
    assert formula_mismatches == 0

    assert all(primitive_row(row) for row in ROWS)
    transcript = hashlib.sha256()
    candidate_counts: list[int] = []
    power_counts: list[int] = []
    survivors: set[tuple[Row, Vec, Vec]] = set()

    for row in ROWS:
        candidates = structural_candidates(row)
        assert len(candidates) == 290
        candidate_counts.append(len(candidates))
        c, d, r, t = row
        del c, d
        row_survivors = []
        for x, y in candidates:
            good = power_compatible(depth, x, r) and power_compatible(depth, y, t)
            transcript.update(f"{row}|{x}|{y}|{int(good)}\n".encode())
            if good:
                key = (row, x, y)
                row_survivors.append(key)
                survivors.add(key)
        power_counts.append(len(row_survivors))

    assert candidate_counts == [290] * 6
    assert power_counts == [2, 0, 4, 4, 4, 0]
    assert survivors == set(CERTIFICATES)
    assert len(survivors) == 14
    assert transcript.hexdigest() == "d1d49b72ac57f482fa98142845d8b8d9c540aea86fb3faef71927266d9b079b6"

    certificate_lengths = sorted(verify_certificate(key, cert) for key, cert in CERTIFICATES.items())
    assert certificate_lengths == [4, 4, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8]

    # Hostile controls. Power tests alone leave 14 unresolved candidates; the
    # explicit mixed table is therefore necessary. Deleting any one table row
    # leaves exactly that candidate unaccounted for.
    assert len(survivors) == 14
    for omitted in CERTIFICATES:
        mutated = set(CERTIFICATES) - {omitted}
        assert survivors - mutated == {omitted}

    print(json.dumps({
        "status": "P7_A2_RANK3_SUPPORT4_EXCEPTION_TABLE_GREEN",
        "depth_states": len(depth),
        "depth_formula_mismatches": formula_mismatches,
        "primitive_rows": len(ROWS),
        "structural_candidates_per_row": candidate_counts,
        "structural_candidates_total": sum(candidate_counts),
        "power_survivors_per_row": power_counts,
        "power_survivors_total": len(survivors),
        "candidate_transcript_sha256": transcript.hexdigest(),
        "mixed_certificates": len(CERTIFICATES),
        "certificate_lengths": certificate_lengths,
        "max_certificate_length": max(certificate_lengths),
        "delete_one_mutations_rejected": len(CERTIFICATES),
        "authority": "occurrence-level exact depth classification plus explicit zero-sum certificates",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
