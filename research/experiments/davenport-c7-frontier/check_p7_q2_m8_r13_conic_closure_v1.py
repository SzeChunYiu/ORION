#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import Counter

P = 7
EXPECTED_CANDIDATES = 5166
EXPECTED_DIGEST = "0eb3a99b0bb1c30595f9b6b58e74b980c094c5d5754a50f726d82aed4711d82c"
EXPECTED_SECANT_DISTRIBUTION = {15: 1260, 16: 1218, 17: 1680, 18: 840, 19: 168}


def normalize(v):
    v = tuple(x % P for x in v)
    for x in v:
        if x:
            inv = pow(x, -1, P)
            return tuple((y * inv) % P for y in v)
    raise ValueError("zero vector")


def dot(a, b):
    return sum(x * y for x, y in zip(a, b)) % P


def rref_rank(matrix):
    a = [[x % P for x in row] for row in matrix]
    m = len(a)
    n = len(a[0]) if a else 0
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = pow(a[r][c], -1, P)
        a[r] = [(x * inv) % P for x in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                f = a[i][c]
                a[i] = [(a[i][j] - f * a[r][j]) % P for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def main() -> int:
    points = sorted({
        normalize((a, b, c))
        for a in range(P)
        for b in range(P)
        for c in range(P)
        if (a, b, c) != (0, 0, 0)
    })
    assert len(points) == 57

    conic = sorted({normalize((1, t, t * t)) for t in range(P)} | {(0, 0, 1)})
    assert len(conic) == 8
    conic_set = set(conic)
    off = [x for x in points if x not in conic_set]
    assert len(off) == 49

    lines = points[:]  # dual normalized coefficient triples
    line_index = {line: i for i, line in enumerate(lines)}
    line_points = [[x for x in points if dot(x, line) == 0] for line in lines]
    assert {len(row) for row in line_points} == {8}
    conic_count = [sum(x in conic_set for x in row) for row in line_points]
    assert Counter(conic_count) == Counter({2: 28, 0: 21, 1: 8})

    # With the conic fixed, a 13-direction support may select at most 3-c
    # off-conic points on a line containing c conic points.
    capacities = [3 - c for c in conic_count]
    off_lines = [
        [i for i, line in enumerate(lines) if dot(x, line) == 0]
        for x in off
    ]
    assert {len(row) for row in off_lines} == {8}

    # Primary cover: recursive capacity backtracking.
    candidates = []
    counts = [0] * len(lines)

    def visit(start: int, chosen: list[int]) -> None:
        if len(chosen) == 5:
            candidates.append(tuple(chosen))
            return
        need = 5 - len(chosen)
        for idx in range(start, len(off) - need + 1):
            if any(counts[li] >= capacities[li] for li in off_lines[idx]):
                continue
            for li in off_lines[idx]:
                counts[li] += 1
            chosen.append(idx)
            visit(idx + 1, chosen)
            chosen.pop()
            for li in off_lines[idx]:
                counts[li] -= 1

    visit(0, [])
    assert len(candidates) == EXPECTED_CANDIDATES

    canonical = [[off[i] for i in row] for row in candidates]
    digest = hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert digest == EXPECTED_DIGEST, digest

    conic_index = {x: i for i, x in enumerate(conic)}
    secant_pair = {}
    for li, row in enumerate(line_points):
        pair = [conic_index[x] for x in row if x in conic_set]
        if len(pair) == 2:
            secant_pair[li] = tuple(pair)
    assert len(secant_pair) == 28

    secants_through = [
        [li for li in off_lines[i] if li in secant_pair]
        for i in range(len(off))
    ]
    assert Counter(map(len, secants_through)) == Counter({3: 28, 4: 21})

    ranks = Counter()
    secant_distribution = Counter()
    coverage_distribution = Counter()
    for candidate in candidates:
        rows = []
        covered = set()
        saturated = 0
        for j, oi in enumerate(candidate):
            d = off[oi]
            for li in secants_through[oi]:
                a, b = secant_pair[li]
                covered.update((a, b))
                saturated += 1
                for coord in range(3):
                    row = [0] * 13
                    row[a] = conic[a][coord]
                    row[b] = (row[b] + conic[b][coord]) % P
                    row[8 + j] = (-d[coord]) % P
                    rows.append(row)
        rank = rref_rank(rows)
        ranks[rank] += 1
        secant_distribution[saturated] += 1
        coverage_distribution[len(covered)] += 1

    assert ranks == Counter({13: EXPECTED_CANDIDATES})
    assert dict(sorted(secant_distribution.items())) == EXPECTED_SECANT_DISTRIBUTION
    assert coverage_distribution == Counter({8: EXPECTED_CANDIDATES})

    print(json.dumps({
        "status": "P7_Q2_M8_R13_CONIC_CLOSURE_GREEN",
        "candidate_extensions": len(candidates),
        "candidate_sha256": digest,
        "rank_13_systems": ranks[13],
        "all_conic_directions_covered": coverage_distribution[8],
        "saturated_secant_distribution": dict(sorted(secant_distribution.items())),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
