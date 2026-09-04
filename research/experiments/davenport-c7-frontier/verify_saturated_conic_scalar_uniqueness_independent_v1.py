#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from collections import Counter


def projective_data(p: int):
    def normalize(v):
        v = tuple(x % p for x in v)
        for x in v:
            if x:
                inv = pow(x, -1, p)
                return tuple(y * inv % p for y in v)
        raise ValueError

    def dot(a, b):
        return sum(x * y for x, y in zip(a, b)) % p

    points = sorted({
        normalize((a, b, c))
        for a in range(p) for b in range(p) for c in range(p)
        if (a, b, c) != (0, 0, 0)
    })
    conic = sorted({normalize((1, t, t*t)) for t in range(p)} | {(0, 0, 1)})
    cset = set(conic)
    off = [x for x in points if x not in cset]
    lines = points[:]
    cindex = {x: i for i, x in enumerate(conic)}

    secants = []
    for d in off:
        row = []
        for li, line in enumerate(lines):
            if dot(d, line):
                continue
            pair = [i for i, c in enumerate(conic) if dot(c, line) == 0]
            if len(pair) == 2:
                row.append(tuple(pair))
        secants.append(row)

    coeff = {}
    for oi, d in enumerate(off):
        for a, b in secants[oi]:
            solutions = []
            for alpha in range(1, p):
                for beta in range(1, p):
                    v = tuple((alpha*conic[a][k] + beta*conic[b][k]) % p for k in range(3))
                    if v == d:
                        solutions.append((alpha, beta))
            assert len(solutions) == 1
            coeff[(oi, a, b)] = solutions[0]

    return conic, off, secants, coeff


def pair_compatible(p: int, data, i: int, j: int) -> bool:
    conic, off, secants, coeff = data
    selected = (i, j)
    n = len(conic) + 2
    adjacency = [[] for _ in range(n)]

    for jj, oi in enumerate(selected):
        mu = len(conic) + jj
        for a, b in secants[oi]:
            alpha, beta = coeff[(oi, a, b)]
            adjacency[mu].append((a, alpha))
            adjacency[a].append((mu, pow(alpha, -1, p)))
            adjacency[mu].append((b, beta))
            adjacency[b].append((mu, pow(beta, -1, p)))

    values = [None] * n
    for start in range(n):
        if values[start] is not None:
            continue
        values[start] = 1
        stack = [start]
        while stack:
            u = stack.pop()
            for v, ratio in adjacency[u]:
                proposed = values[u] * ratio % p
                if values[v] is None:
                    values[v] = proposed
                    stack.append(v)
                elif values[v] != proposed:
                    return False
    return True


def check_quadratic_formula(p: int, data) -> int:
    conic, off, secants, coeff = data
    checked = 0
    finite_index = {tuple((1, t, t*t)): t for t in range(p)}

    for oi, d in enumerate(off):
        d0, d1, d2 = d
        Delta = (d0*d2 - d1*d1) % p
        assert Delta != 0
        for a, b in secants[oi]:
            for endpoint, alpha in ((a, coeff[(oi, a, b)][0]), (b, coeff[(oi, a, b)][1])):
                c = conic[endpoint]
                if c[0] == 0:
                    continue
                t = c[1] % p
                Q = (d0*t*t - 2*d1*t + d2) % p
                assert Q != 0
                assert alpha == Delta * pow(Q, -1, p) % p
                checked += 1
    return checked


def main() -> int:
    rows = []
    formula_checks = 0
    for p in (5, 7, 11, 13):
        data = projective_data(p)
        formula_checks += check_quadratic_formula(p, data)
        off = data[1]
        counts = Counter()
        for i, j in itertools.combinations(range(len(off)), 2):
            counts[pair_compatible(p, data, i, j)] += 1
        rows.append({
            'p': p,
            'off_conic_points': len(off),
            'compatible_distinct_pairs': counts[True],
            'incompatible_distinct_pairs': counts[False],
        })

    expected = {
        5: (30, 270),
        7: (0, 1176),
        11: (0, 7260),
        13: (0, 14196),
    }
    for row in rows:
        assert (row['compatible_distinct_pairs'], row['incompatible_distinct_pairs']) == expected[row['p']]

    print(json.dumps({
        'status': 'SATURATED_CONIC_SCALAR_UNIQUENESS_INDEPENDENT_GREEN',
        'pair_replays': rows,
        'quadratic_coefficient_checks': formula_checks,
        'p5_hostile_control_compatible_pairs': 30,
        'p_ge_7_compatible_pairs': 0,
    }, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
