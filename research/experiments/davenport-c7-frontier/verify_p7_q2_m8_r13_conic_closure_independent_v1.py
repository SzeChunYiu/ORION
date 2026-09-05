#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter

P = 7
EXPECTED_CANDIDATES = 5166
EXPECTED_DIGEST = "0eb3a99b0bb1c30595f9b6b58e74b980c094c5d5754a50f726d82aed4711d82c"


def normalize(v):
    v = tuple(x % P for x in v)
    for x in v:
        if x:
            inv = pow(x, -1, P)
            return tuple((y * inv) % P for y in v)
    raise ValueError


def cross(a, b):
    return normalize((
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b)) % P


def main() -> int:
    points = sorted({
        normalize((a, b, c))
        for a in range(P)
        for b in range(P)
        for c in range(P)
        if (a, b, c) != (0, 0, 0)
    })
    conic = sorted({normalize((1, t, t * t)) for t in range(P)} | {(0, 0, 1)})
    conic_set = set(conic)
    off = [x for x in points if x not in conic_set]
    assert len(points) == 57 and len(conic) == 8 and len(off) == 49

    lines = points[:]
    line_index = {line: i for i, line in enumerate(lines)}
    line_conic_count = [sum(dot(c, line) == 0 for c in conic) for line in lines]
    assert Counter(line_conic_count) == Counter({2: 28, 1: 8, 0: 21})

    off_line_membership = [
        {li for li, line in enumerate(lines) if dot(x, line) == 0}
        for x in off
    ]

    pair_line = {}
    for a in range(len(off)):
        for b in range(a + 1, len(off)):
            pair_line[(a, b)] = line_index[cross(off[a], off[b])]

    # Independent cover: inspect all C(49,5) subsets and reject them by the
    # three possible ways a fixed conic plus five off-points could create a
    # four-secant. This does not use the primary recursive line capacities.
    candidates = []
    for candidate in itertools.combinations(range(49), 5):
        bad = False

        # Two off-points may not lie on a conic secant (2+2 would be four).
        for a, b in itertools.combinations(candidate, 2):
            li = pair_line[(a, b)]
            if line_conic_count[li] == 2:
                bad = True
                break
        if bad:
            continue

        # Three off-points may not lie on a tangent/secant.
        for a, b, c in itertools.combinations(candidate, 3):
            li = pair_line[tuple(sorted((a, b)))]
            if li in off_line_membership[c] and line_conic_count[li] >= 1:
                bad = True
                break
        if bad:
            continue

        # Four off-points may not be collinear even on an external line.
        for quad in itertools.combinations(candidate, 4):
            a, b = quad[:2]
            li = pair_line[tuple(sorted((a, b)))]
            if all(li in off_line_membership[x] for x in quad[2:]):
                bad = True
                break
        if not bad:
            candidates.append(candidate)

    assert len(candidates) == EXPECTED_CANDIDATES
    canonical = [[off[i] for i in row] for row in candidates]
    digest = hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert digest == EXPECTED_DIGEST, digest

    conic_index = {x: i for i, x in enumerate(conic)}
    secant_pair = {}
    for li, line in enumerate(lines):
        pair = [i for i, c in enumerate(conic) if dot(c, line) == 0]
        if len(pair) == 2:
            secant_pair[li] = tuple(pair)
    assert len(secant_pair) == 28

    secants_through = [
        [li for li in off_line_membership[i] if li in secant_pair]
        for i in range(49)
    ]

    # Precompute each saturated secant's multiplicative conic-scalar ratio.
    # If D = alpha*C_a + beta*C_b, then lambda_b/lambda_a = beta/alpha.
    ratio = {}
    for oi, d in enumerate(off):
        for li in secants_through[oi]:
            a, b = secant_pair[li]
            solutions = []
            for alpha in range(1, P):
                for beta in range(1, P):
                    value = tuple(
                        (alpha * conic[a][k] + beta * conic[b][k]) % P
                        for k in range(3)
                    )
                    if value == d:
                        solutions.append((alpha, beta))
            assert len(solutions) == 1
            alpha, beta = solutions[0]
            ratio[(oi, a, b)] = beta * pow(alpha, -1, P) % P

    inconsistent = 0
    covered_all = 0
    for candidate in candidates:
        adjacency = [[] for _ in range(8)]
        covered = set()
        for oi in candidate:
            for li in secants_through[oi]:
                a, b = secant_pair[li]
                r = ratio[(oi, a, b)]
                adjacency[a].append((b, r))
                adjacency[b].append((a, pow(r, -1, P)))
                covered.update((a, b))
        if len(covered) == 8:
            covered_all += 1

        values = [None] * 8
        contradiction = False
        for start in range(8):
            if values[start] is not None:
                continue
            values[start] = 1
            stack = [start]
            while stack and not contradiction:
                u = stack.pop()
                for v, r in adjacency[u]:
                    proposed = values[u] * r % P
                    if values[v] is None:
                        values[v] = proposed
                        stack.append(v)
                    elif values[v] != proposed:
                        contradiction = True
                        break
            if contradiction:
                break
        if contradiction:
            inconsistent += 1

    assert covered_all == EXPECTED_CANDIDATES
    assert inconsistent == EXPECTED_CANDIDATES

    print(json.dumps({
        "status": "P7_Q2_M8_R13_CONIC_CLOSURE_INDEPENDENT_GREEN",
        "candidate_extensions": len(candidates),
        "candidate_sha256": digest,
        "all_conic_directions_covered": covered_all,
        "ratio_inconsistent_candidates": inconsistent,
        "enumeration_method": "direct C(49,5) pair-triple-quadruple filter",
        "compatibility_method": "multiplicative secant-ratio cycle propagation",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
