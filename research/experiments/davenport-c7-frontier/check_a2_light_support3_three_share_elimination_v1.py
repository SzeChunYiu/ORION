#!/usr/bin/env python3
"""Primary ORION replay for the a=2 light-share c=3 elimination."""
from __future__ import annotations

import hashlib
import json


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


def coefficient_atom(p: int, c: int, r: int, t: int) -> bool:
    return not any(
        (n * c) % p <= c and (n * r) % p <= r and (n * t) % p <= t
        for n in range(2, p)
    )


def radial_costs(p: int, c: int) -> list[int]:
    """Exact radial costs from actual s,g,e1,e2 resources in U*V."""
    u = pow(2, -1, p)
    best = [10**9] * p
    for q in range(p - 1):
        axes = (u * q) % p
        for z in range(c + 3):
            d = (z + q) % p
            best[d] = min(best[d], z + q + 2 * axes)
    return best


def symbolic_replay(limit: int = 1009) -> dict[str, int]:
    primes = 0
    rows = 0
    interior = 0
    boundary = 0
    nonatom = 0

    for p in range(11, limit + 1, 2):
        if not is_prime(p):
            continue
        primes += 1
        h = (p - 1) // 2
        m = 3 * h + 1
        radial = radial_costs(p, 3)
        assert [radial[i] for i in (4, 5, 6, 7)] == [4, 5, 8, 9]

        for d in range((h + 2) // 2 + 1):
            r = h - 2 + d
            t = 2 * h - d
            if not (r <= t <= p - 1):
                continue
            rows += 1

            if d >= 3:
                D, A, B = 6, 2 * d - 5, p - 2 * d - 2
                assert A <= r and B <= t
                assert radial[D] + A + B == p + 1 < m
                interior += 1
                continue

            if p % 6 == 1:
                k = (p - 1) // 6
                if d == 0:
                    n = 4 * k + 2
                    expected = (4, 2 * k - 3, 2 * k - 1)
                elif d == 1:
                    n = 2 * k + 2
                    expected = (5, 3 * k - 2, 2 * k - 3)
                else:
                    n = 4 * k + 3
                    expected = (7, k - 1, p - 7)
                got = ((3 * n) % p, (n * r) % p, (n * t) % p)
                assert got == expected, (p, d, got, expected)
                D, A, B = got
                assert A <= r and B <= t
                assert radial[D] + A + B < m
                boundary += 1
                continue

            assert p % 6 == 5
            k = (p + 1) // 6
            if d == 0:
                n = 2 * k
                got = ((3 * n) % p, (n * r) % p, (n * t) % p)
                assert got == (1, k - 1, 4 * k - 1)
                assert got[0] <= 3 and got[1] <= r and got[2] <= t
                assert not coefficient_atom(p, 3, r, t)
                nonatom += 1
            elif d == 1:
                n = 4 * k + 1
                expected = (5, 3 * k - 3, 4 * k - 4)
                got = ((3 * n) % p, (n * r) % p, (n * t) % p)
                assert got == expected
                D, A, B = got
                assert A <= r and B <= t
                assert radial[D] + A + B < m
                boundary += 1
            else:
                n = 2 * k + 1
                expected = (4, 2 * k - 1, p - 4)
                got = ((3 * n) % p, (n * r) % p, (n * t) % p)
                assert got == expected
                D, A, B = got
                assert A <= r and B <= t
                assert radial[D] + A + B < m
                boundary += 1

    assert (primes, rows) == (165, 19526)
    return {
        "primes_through_1009": primes,
        "multiplicity_rows": rows,
        "interior_rows": interior,
        "boundary_witness_rows": boundary,
        "nonatom_boundary_rows": nonatom,
    }


def scalar_scan(limit: int = 1009) -> dict[str, int | str]:
    residual: list[tuple[int, int, int, int]] = []
    mutation: list[tuple[int, int, int, int]] = []
    atom_rows = 0

    for p in range(7, limit + 1, 2):
        if not is_prime(p):
            continue
        h = (p - 1) // 2
        m = 3 * h + 1
        if 3 > 2 * (h // 2):
            continue
        radial = radial_costs(p, 3)

        for r in range(1, p):
            t = m - 3 - r
            if t < r or t <= 0 or t >= p or not coefficient_atom(p, 3, r, t):
                continue
            atom_rows += 1

            killed = False
            for n in range(2, p):
                D, A, B = (3 * n) % p, (r * n) % p, (t * n) % p
                if A <= r and B <= t and radial[D] + A + B < m:
                    killed = True
                    break
            if not killed:
                residual.append((p, 3, r, t))

            killed_without_synthesis = False
            for n in range(2, p):
                D, A, B = (3 * n) % p, (r * n) % p, (t * n) % p
                actual_only_cost = D if D <= 5 else 10**9
                if A <= r and B <= t and actual_only_cost + A + B < m:
                    killed_without_synthesis = True
                    break
            if not killed_without_synthesis:
                mutation.append((p, 3, r, t))

    assert residual == []
    assert atom_rows == 9826
    assert len(mutation) == 1309
    assert mutation[:8] == [
        (13, 3, 6, 10),
        (19, 3, 9, 16),
        (31, 3, 15, 28),
        (31, 3, 18, 25),
        (37, 3, 18, 34),
        (37, 3, 21, 31),
        (43, 3, 21, 40),
        (43, 3, 24, 37),
    ]
    assert mutation[-1] == (1009, 3, 603, 907)

    payload = "".join(",".join(map(str, row)) + "\n" for row in mutation).encode()
    digest = hashlib.sha256(payload).hexdigest()
    assert digest == "2e7593e3c4af58ff9781fe569253fbd94280aa6fb2ebce2bb8a60c0ca5cfa35e"

    return {
        "atom_rows_after_multicopy_ceiling": atom_rows,
        "exact_radial_residuals": 0,
        "no_synthesis_mutation_residuals": len(mutation),
        "no_synthesis_mutation_sha256": digest,
    }


def main() -> None:
    assert 2 * (((7 - 1) // 2) // 2) == 2 < 3
    out = {
        "status": "A2_LIGHT_SUPPORT3_C3_PRIMARY_GREEN",
        **symbolic_replay(),
        **scalar_scan(),
        "p7_excluded_by_light_multicopy_ceiling": True,
        "theorem": "a=2 first-corridor exact-support6 light-share support3 companions have shared multiplicity !=3 for every prime p>=7",
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
