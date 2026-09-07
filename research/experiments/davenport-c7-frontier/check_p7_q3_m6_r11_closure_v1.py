#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter

P = 7
EXPECTED = 4466
DIGEST = "7f858cbd83b9922d4fc0122baa2a34680216033f28bd948aa225bde055c85cce"
SECANT_DIST = {9: 1204, 10: 1848, 11: 1176, 12: 238}


def normalize(v):
    v = tuple(x % P for x in v)
    for x in v:
        if x:
            inv = pow(x, -1, P)
            return tuple(y * inv % P for y in v)
    raise ValueError("zero vector")


def dot(a, b):
    return sum(x * y for x, y in zip(a, b)) % P


def cross(a, b):
    return normalize((
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ))


def rank_mod(matrix):
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
        a[r] = [x * inv % P for x in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                f = a[i][c]
                a[i] = [(a[i][j] - f * a[r][j]) % P for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def main() -> int:
    # Uniform tangent-packing arithmetic, including the target slice.
    q = 3
    a = (q - 1) // 2
    assert a == 1
    r, delta = 11, 6
    full_lower = (a + 1) * r - delta - a * (P + 2)
    assert full_lower == 7

    points = sorted({
        normalize((x, y, z))
        for x in range(P) for y in range(P) for z in range(P)
        if (x, y, z) != (0, 0, 0)
    })
    assert len(points) == 57
    pidx = {x: i for i, x in enumerate(points)}
    lines = points[:]
    line_index = {line: i for i, line in enumerate(lines)}
    line_points = [[x for x in points if dot(x, line) == 0] for line in lines]
    assert {len(x) for x in line_points} == {8}

    # Hostile finite control for the f=7 step: normalize an arbitrary
    # quadrangle contained in the full arc. Every frame-normalized 7-arc has
    # exactly one secant-free projective point.
    frame = [
        pidx[normalize((1, 0, 0))], pidx[normalize((0, 1, 0))],
        pidx[normalize((0, 0, 1))], pidx[normalize((1, 1, 1))],
    ]
    remaining = [i for i in range(57) if i not in frame]

    def line_pair(i, j):
        return line_index[cross(points[i], points[j])]

    def is_arc(indices):
        seen = set()
        for i, j in itertools.combinations(indices, 2):
            li = line_pair(i, j)
            if li in seen:
                return False
            seen.add(li)
        return True

    def secant_free(indices):
        secants = {line_pair(i, j) for i, j in itertools.combinations(indices, 2)}
        support = set(indices)
        return [
            k for k, x in enumerate(points)
            if k not in support and all(dot(x, lines[li]) != 0 for li in secants)
        ]

    arc7 = 0
    sf_dist = Counter()
    for extra in itertools.combinations(remaining, 3):
        F = frame + list(extra)
        if not is_arc(F):
            continue
        arc7 += 1
        sf_dist[len(secant_free(F))] += 1
    assert arc7 == 20
    assert sf_dist == Counter({1: 20})

    # f=8: canonical conic and three deficit-two points.
    conic = sorted({normalize((1, t, t * t)) for t in range(P)} | {(0, 0, 1)})
    cset = set(conic)
    off = [x for x in points if x not in cset]
    assert len(conic) == 8 and len(off) == 49
    conic_count = [sum(x in cset for x in row) for row in line_points]
    assert Counter(conic_count) == Counter({2: 28, 1: 8, 0: 21})
    capacities = [3 - c for c in conic_count]
    off_lines = [[li for li, line in enumerate(lines) if dot(x, line) == 0] for x in off]

    candidates = []
    counts = [0] * 57
    def visit(start, chosen):
        if len(chosen) == 3:
            candidates.append(tuple(chosen))
            return
        need = 3 - len(chosen)
        for oi in range(start, len(off) - need + 1):
            if any(counts[li] >= capacities[li] for li in off_lines[oi]):
                continue
            for li in off_lines[oi]: counts[li] += 1
            chosen.append(oi)
            visit(oi + 1, chosen)
            chosen.pop()
            for li in off_lines[oi]: counts[li] -= 1
    visit(0, [])
    assert len(candidates) == EXPECTED

    canonical = [[off[i] for i in row] for row in candidates]
    digest = hashlib.sha256(json.dumps(canonical, separators=(",", ":")).encode()).hexdigest()
    assert digest == DIGEST, digest

    cidx = {x: i for i, x in enumerate(conic)}
    secant_pair = {}
    for li, row in enumerate(line_points):
        pair = [cidx[x] for x in row if x in cset]
        if len(pair) == 2:
            secant_pair[li] = tuple(pair)
    secants_through = [[li for li in off_lines[i] if li in secant_pair] for i in range(49)]
    assert Counter(map(len, secants_through)) == Counter({3: 28, 4: 21})

    ranks = Counter()
    coverage = Counter()
    secants = Counter()
    for candidate in candidates:
        matrix = []
        covered = set()
        sat = 0
        for j, oi in enumerate(candidate):
            d = off[oi]
            for li in secants_through[oi]:
                u, v = secant_pair[li]
                covered.update((u, v))
                sat += 1
                for coord in range(3):
                    row = [0] * 11
                    row[u] = conic[u][coord]
                    row[v] = (row[v] + conic[v][coord]) % P
                    row[8 + j] = -d[coord] % P
                    matrix.append(row)
        ranks[rank_mod(matrix)] += 1
        coverage[len(covered)] += 1
        secants[sat] += 1

    assert ranks == Counter({11: EXPECTED})
    assert coverage == Counter({8: EXPECTED})
    assert dict(sorted(secants.items())) == SECANT_DIST

    print(json.dumps({
        "status": "P7_Q3_M6_R11_CLOSURE_GREEN",
        "tangent_full_lower": full_lower,
        "frame_normalized_7_arcs": arc7,
        "seven_arc_secant_free_distribution": dict(sf_dist),
        "conic_candidates": EXPECTED,
        "candidate_sha256": digest,
        "rank_11_systems": ranks[11],
        "all_conic_directions_covered": coverage[8],
        "saturated_secant_distribution": dict(sorted(secants.items())),
        "new_direction_floor": 12,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
