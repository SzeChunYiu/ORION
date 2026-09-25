#!/usr/bin/env python3
"""Primary replay for the a=2 light-share c=4 elimination."""
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


def radial_cost_certified(D: int) -> int:
    return {5: 5, 6: 6, 7: 9, 10: 14}[D]


def boundary_witness(p: int, d: int) -> tuple[str, int] | None:
    """Return (kind,multiplier); None is the sole p=13,d=0 exact resonance."""
    mod = p % 8
    k = (p - mod) // 8

    if d == 0:
        if mod == 1:
            return "kill", 6 * k + 2
        if mod == 3:
            return "nonatom", 4 * k + 2
        if mod == 5:
            if p == 13:
                return None
            return "nonatom", 2 * k + 2
        assert mod == 7
        return "nonatom", 2 * k + 2

    if d == 1:
        if mod in (1, 3):
            return "kill", 2 * k + 2
        return "nonatom", 2 * k + 2

    if d == 2:
        if mod == 1:
            return "nonatom", 2 * k + 1
        if mod == 3:
            return "nonatom", 2 * k + 1
        if mod == 5:
            if p == 13:
                return "kill", 8
            return "kill", 2 * k + 3
        assert mod == 7
        return "nonatom", 4 * k + 4

    assert d == 3
    if mod == 1:
        return "kill", 4 * k + 3
    if mod == 3:
        return "kill", 4 * k + 3
    if mod == 5:
        if p == 13:
            return "kill", 11
        return "kill", 2 * k + 3
    assert mod == 7
    return "kill", 2 * k + 3


def symbolic_replay(limit: int = 1009) -> dict[str, int]:
    primes = 0
    killed = 0
    nonatom = 0
    resonances: list[tuple[int, int, int, int]] = []

    for p in range(7, limit + 1, 2):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        if 4 > 2 * (H // 2):
            continue
        primes += 1
        m = 3 * H + 1
        for d in range(4):
            r = H - 3 + d
            t = 2 * H - d
            spec = boundary_witness(p, d)
            if spec is None:
                resonances.append((p, 4, r, t))
                continue

            kind, n = spec
            D = 4 * n % p
            A = r * n % p
            B = t * n % p
            assert A <= r and B <= t, (p, d, kind, n, D, A, B, r, t)

            if kind == "nonatom":
                assert D <= 4
                assert D + A + B > 0
                assert (D, A, B) != (4, r, t)
                nonatom += 1
            else:
                cost = radial_cost_certified(D)
                assert cost + A + B < m, (p, d, n, D, A, B, cost, m)
                killed += 1

    assert resonances == [(13, 4, 3, 12)]
    return {
        "eligible_primes_through_1009": primes,
        "symbolic_kill_rows": killed,
        "symbolic_nonatom_rows": nonatom,
        "scalar_resonances": len(resonances),
    }


P = 13
ZERO = (0, 0, 0)
S = (0, 0, 1)
INV2 = pow(2, -1, P)


def add(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple((a[i] + b[i]) % P for i in range(3))


def mul(k: int, a: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(k * a[i] % P for i in range(3))


def neg(a: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple((-v) % P for v in a)


def rho_a2_p13(target: tuple[int, int, int]) -> int:
    """Closed support-four depth formula by the number q of g copies."""
    best = 10**9
    for q in range(P - 1):  # g multiplicity is 11
        z = (target[2] - q) % P
        if z > 2:
            continue
        e1 = (target[0] + INV2 * q) % P
        e2 = (target[1] + INV2 * q) % P
        best = min(best, e1 + e2 + z + q)
    assert best < 10**9
    return best


def exact_p13_resonance() -> dict[str, int]:
    m = 19
    structural = 0
    singleton = 0
    hist: Counter[int] = Counter()

    for a in range(1, P):
        for b in range(1, P):
            if a == b:
                continue
            for c0 in range(P):
                structural += 1
                x = (a, b, c0)
                y = (3 * a % P, 3 * b % P, (4 + 3 * c0) % P)

                if 1 + rho_a2_p13(neg(x)) >= m and 1 + rho_a2_p13(neg(y)) >= m:
                    singleton += 1

                best = 10**9
                for i in range(5):
                    for j in range(4):
                        for k in range(13):
                            length = i + j + k
                            if length == 0 or length == m:
                                continue
                            sigma = add(add(mul(i, S), mul(j, x)), mul(k, y))
                            score = length + rho_a2_p13(neg(sigma))
                            best = min(best, score)
                hist[best] += 1

    expected = {
        3: 4,
        4: 18,
        5: 58,
        6: 132,
        7: 246,
        8: 352,
        9: 420,
        10: 272,
        11: 124,
        12: 40,
        13: 44,
        14: 6,
    }
    assert structural == 1716
    assert singleton == 78
    assert dict(sorted(hist.items())) == expected
    exact_survivors = sum(v for score, v in hist.items() if score >= 19)
    mutation_survivors = sum(v for score, v in hist.items() if score >= 14)
    assert exact_survivors == 0
    assert mutation_survivors == 6

    return {
        "p13_structural": structural,
        "p13_singleton_survivors": singleton,
        "p13_exact_survivors": exact_survivors,
        "p13_threshold14_mutation_survivors": mutation_survivors,
    }


def main() -> None:
    out = {
        "status": "A2_LIGHT_SUPPORT3_C4_PRIMARY_GREEN",
        **symbolic_replay(),
        **exact_p13_resonance(),
        "theorem": "a=2 first-corridor exact-support6 light-share support3 companions have shared multiplicity !=4 for every prime p>=7",
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
