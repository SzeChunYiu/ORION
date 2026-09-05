#!/usr/bin/env python3
"""Regression plus bounded discovery for exact overlap-plane lifting."""
from __future__ import annotations

import json
from collections import Counter


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


def enc(v: tuple[int, int, int], p: int) -> int:
    return (v[0] * p + v[1]) * p + v[2]


def dec(i: int, p: int) -> tuple[int, int, int]:
    return (i // (p * p), (i // p) % p, i % p)


def add(x: tuple[int, int, int], y: tuple[int, int, int], p: int) -> tuple[int, int, int]:
    return tuple((x[i] + y[i]) % p for i in range(3))


def build_u_depth(p: int, a: int) -> list[int]:
    inf = 10**9
    n = p**3
    dp = [inf] * n
    dp[0] = 0
    u = pow(a, -1, p)
    e1 = (1, 0, 0)
    e2 = (0, 1, 0)
    s = (0, 0, 1)
    g = ((-u) % p, (-u) % p, 1)
    terms = [e1] * (p - 1) + [e2] * (p - 1) + [s] * a + [g] * (p - a)
    for term in terms:
        old = dp[:]
        for i, value in enumerate(old):
            if value == inf:
                continue
            j = enc(add(dec(i, p), term, p), p)
            if value + 1 < dp[j]:
                dp[j] = value + 1
    return dp


def target(p: int, a: int, C: int, D: int) -> tuple[int, int, int]:
    u = pow(a, -1, p)
    return ((-D * u) % p, (-D * u) % p, (C + D) % p)


def nu(p: int, a: int, C: int, D: int) -> int:
    u = pow(a, -1, p)
    best = 10**9
    for z in range(a + 1):
        q = (C + D - z) % p
        if q <= p - a:
            best = min(best, z + q + 2 * ((u * (q - D)) % p))
    assert best < 10**9
    return best


def caps(p: int, a: int) -> tuple[int, int]:
    H = (p - 1) // 2
    h = (H + 1) // 2
    u = pow(a, -1, p)
    cl = 0
    for c in range(1, p - a):
        if all((u * k) % p <= p - h for k in range(a, a + c + 1)):
            cl = c
        else:
            break
    ch = 0
    for c in range(1, a):
        if all((u * k) % p <= p - h for k in range(a - c, a + 1)):
            ch = c
        else:
            break
    return cl, ch


def coefficient_atom(p: int, v: tuple[int, int, int, int]) -> bool:
    for q in range(2, p):
        residues = tuple((q * x) % p for x in v)
        if all(residues[i] <= v[i] for i in range(4)):
            return False
    return True


def formula_regression() -> int:
    checks = 0
    for p in (5, 7, 11):
        H = (p - 1) // 2
        for a in range(1, H + 1):
            dp = build_u_depth(p, a)
            for C in range(p):
                for D in range(p):
                    got = nu(p, a, C, D)
                    want = dp[enc(target(p, a, C, D), p)]
                    assert got == want, (p, a, C, D, got, want)
                    checks += 1
    return checks


def discovery(limit: int = 79) -> dict[str, object]:
    boxes = 0
    atom_boxes = 0
    killed = 0
    residual_by_a: Counter[int] = Counter()
    residual_examples: dict[int, tuple[int, ...]] = {}

    for p in range(7, limit + 1):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        m = 3 * H + 1
        for a in range(2, H + 1):
            cl, ch = caps(p, a)
            if cl == 0 or ch == 0:
                continue
            for c in range(1, cl + 1):
                for d in range(1, ch + 1):
                    rem = m - c - d
                    for r in range(1, p):
                        t = rem - r
                        if t < r or t <= 0 or t >= p:
                            continue
                        boxes += 1
                        vec = (c, d, r, t)
                        if not coefficient_atom(p, vec):
                            continue
                        atom_boxes += 1

                        dead = False
                        for q in range(2, p):
                            R = (q * r) % p
                            T = (q * t) % p
                            if R > r or T > t:
                                continue
                            C = (q * c) % p
                            D = (q * d) % p
                            if R + T + nu(p, a, C, D) <= m - 1:
                                dead = True
                                break

                        if dead:
                            killed += 1
                        else:
                            residual_by_a[a] += 1
                            residual_examples.setdefault(a, (p, a, c, d, r, t, cl, ch))

    assert boxes == 28135
    assert atom_boxes == 27104
    assert killed == 26631
    assert residual_by_a == Counter({2: 471, 3: 2})
    assert residual_examples[2] == (7, 2, 1, 1, 3, 5, 2, 1)
    assert residual_examples[3] == (13, 3, 3, 2, 2, 12, 3, 2)

    return {
        "discovery_prime_limit": limit,
        "multiplicity_boxes": boxes,
        "coefficient_atom_boxes": atom_boxes,
        "scalar_plane_killed": killed,
        "residual_by_a": dict(sorted(residual_by_a.items())),
        "first_residual_by_a": {str(k): list(v) for k, v in sorted(residual_examples.items())},
    }


def main() -> None:
    checks = formula_regression()
    out = {
        "status": "SUPPORT4_OVERLAP_PLANE_RANK3_SCALAR_GREEN",
        "formula_dp_checks": checks,
        **discovery(),
        "authority": "exact overlap-plane formula and scalar certificate are symbolic; bounded residual classification is discovery only",
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
