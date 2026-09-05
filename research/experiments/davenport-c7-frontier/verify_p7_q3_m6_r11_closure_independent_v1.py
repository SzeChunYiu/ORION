#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter

P = 7
EXPECTED = 4466
DIGEST = "7f858cbd83b9922d4fc0122baa2a34680216033f28bd948aa225bde055c85cce"


def normalize(v):
    v = tuple(x % P for x in v)
    for x in v:
        if x:
            inv = pow(x, -1, P)
            return tuple(y * inv % P for y in v)
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
        normalize((x, y, z))
        for x in range(P) for y in range(P) for z in range(P)
        if (x, y, z) != (0, 0, 0)
    })
    conic = sorted({normalize((1, t, t*t)) for t in range(P)} | {(0, 0, 1)})
    cset = set(conic)
    off = [x for x in points if x not in cset]
    lines = points[:]
    lidx = {line: i for i, line in enumerate(lines)}
    ccount = [sum(dot(c, line) == 0 for c in conic) for line in lines]
    assert Counter(ccount) == Counter({2: 28, 1: 8, 0: 21})

    membership = [
        {li for li, line in enumerate(lines) if dot(x, line) == 0}
        for x in off
    ]
    pair_line = {
        (i, j): lidx[cross(off[i], off[j])]
        for i in range(49) for j in range(i + 1, 49)
    }

    # Independent cover: direct C(49,3) scan. Two selected off-points may not
    # share a conic secant, and three may not share a conic tangent/secant.
    candidates = []
    for candidate in itertools.combinations(range(49), 3):
        bad = False
        for i, j in itertools.combinations(candidate, 2):
            if ccount[pair_line[(i, j)]] == 2:
                bad = True
                break
        if bad:
            continue
        i, j, k = candidate
        li = pair_line[tuple(sorted((i, j)))]
        if li in membership[k] and ccount[li] >= 1:
            continue
        candidates.append(candidate)

    assert len(candidates) == EXPECTED
    canonical = [[off[i] for i in row] for row in candidates]
    digest = hashlib.sha256(json.dumps(canonical, separators=(",", ":")).encode()).hexdigest()
    assert digest == DIGEST, digest

    cindex = {x: i for i, x in enumerate(conic)}
    secant_pair = {}
    for li, line in enumerate(lines):
        pair = [i for i, c in enumerate(conic) if dot(c, line) == 0]
        if len(pair) == 2:
            secant_pair[li] = tuple(pair)
    secants_through = [
        [li for li in membership[i] if li in secant_pair]
        for i in range(49)
    ]
    assert Counter(map(len, secants_through)) == Counter({3: 28, 4: 21})

    # Directly solve D=alpha*C_a+beta*C_b. A saturated plane requires
    # lambda_a=alpha*mu_D and lambda_b=beta*mu_D. Encode these as a labelled
    # bipartite gain graph on 8 conic variables and 3 deficient variables.
    coeff = {}
    for oi, d in enumerate(off):
        for li in secants_through[oi]:
            a, b = secant_pair[li]
            solutions = []
            for alpha in range(1, P):
                for beta in range(1, P):
                    v = tuple((alpha*conic[a][c] + beta*conic[b][c]) % P for c in range(3))
                    if v == d:
                        solutions.append((alpha, beta))
            assert len(solutions) == 1
            coeff[(oi, a, b)] = solutions[0]

    inconsistent = 0
    connected = 0
    covered_all = 0
    for candidate in candidates:
        adjacency = [[] for _ in range(11)]
        covered = set()
        for j, oi in enumerate(candidate):
            mu = 8 + j
            for li in secants_through[oi]:
                a, b = secant_pair[li]
                alpha, beta = coeff[(oi, a, b)]
                adjacency[mu].append((a, alpha))
                adjacency[a].append((mu, pow(alpha, -1, P)))
                adjacency[mu].append((b, beta))
                adjacency[b].append((mu, pow(beta, -1, P)))
                covered.update((a, b))
        if len(covered) == 8:
            covered_all += 1

        values = [None] * 11
        components = 0
        contradiction = False
        for start in range(11):
            if values[start] is not None:
                continue
            components += 1
            values[start] = 1
            stack = [start]
            while stack and not contradiction:
                u = stack.pop()
                for v, ratio in adjacency[u]:
                    proposed = values[u] * ratio % P
                    if values[v] is None:
                        values[v] = proposed
                        stack.append(v)
                    elif values[v] != proposed:
                        contradiction = True
                        break
            if contradiction:
                break
        if components == 1:
            connected += 1
        if contradiction:
            inconsistent += 1

    assert covered_all == EXPECTED
    assert connected == EXPECTED
    assert inconsistent == EXPECTED

    print(json.dumps({
        "status": "P7_Q3_M6_R11_CLOSURE_INDEPENDENT_GREEN",
        "candidate_extensions": EXPECTED,
        "candidate_sha256": digest,
        "all_conic_directions_covered": covered_all,
        "connected_gain_graphs": connected,
        "ratio_inconsistent_candidates": inconsistent,
        "enumeration_method": "direct C(49,3) line filter",
        "compatibility_method": "11-variable bipartite multiplicative gain propagation",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
