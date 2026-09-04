#!/usr/bin/env python3
"""Primary ORION replay for the a=1, c=2 support-three elimination."""
from __future__ import annotations

import hashlib
import json
from typing import Iterable


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


def atom_coefficients(p: int, c: int, r: int, t: int) -> bool:
    for q in range(2, p):
        if (q * c) % p <= c and (q * r) % p <= r and (q * t) % p <= t:
            return False
    return True


def s_cost(c_residue: int) -> int:
    """Cost to realize C*s when c=2 and U supplies one additional actual s."""
    return c_residue if c_residue <= 3 else 3 * c_residue - 6


def assert_short_witness(p: int, r: int, t: int, q: int) -> int:
    h = (p - 1) // 2
    m = 3 * h + 1
    c_residue = (2 * q) % p
    r_residue = (q * r) % p
    t_residue = (q * t) % p
    assert r_residue <= r, (p, r, t, q, r_residue)
    assert t_residue <= t, (p, r, t, q, t_residue)
    length = s_cost(c_residue) + r_residue + t_residue
    assert 0 < length < m, (p, r, t, q, length, m)
    return length


def symbolic_replay(limit: int = 1009) -> dict[str, int | list[int]]:
    atom_rows = 0
    symbolic_eliminations = 0
    nonatom_rows = 0
    resonances: list[tuple[int, int, int, int]] = []

    for p in range(7, limit + 1, 2):
        if not is_prime(p):
            continue
        h = (p - 1) // 2
        max_d = (h + 1) // 2

        for d in range(max_d + 1):
            r = h - 1 + d
            t = 2 * h - d
            if r > t:
                continue

            is_atom = atom_coefficients(p, 2, r, t)

            if d >= 2:
                if not is_atom:
                    nonatom_rows += 1
                    continue
                assert_short_witness(p, r, t, 2)
                atom_rows += 1
                symbolic_eliminations += 1
                continue

            if d == 0:
                if p % 4 == 3:
                    q = h + 1
                    assert (2 * q) % p <= 2
                    assert (q * r) % p <= r
                    assert (q * t) % p <= t
                    assert not is_atom
                    nonatom_rows += 1
                else:
                    assert is_atom
                    assert_short_witness(p, r, t, h + 2)
                    atom_rows += 1
                    symbolic_eliminations += 1
                continue

            # d == 1
            assert is_atom
            atom_rows += 1
            if p % 4 == 3:
                assert_short_witness(p, r, t, h + 2)
                symbolic_eliminations += 1
            elif p == 13:
                q = h + 3
                c_residue = (2 * q) % p
                rr = (q * r) % p
                tt = (q * t) % p
                m = 3 * h + 1
                assert s_cost(c_residue) + rr + tt == m
                resonances.append((p, 2, r, t))
            else:
                assert p >= 17
                assert_short_witness(p, r, t, h + 3)
                symbolic_eliminations += 1

    assert resonances == [(13, 2, 6, 11)], resonances
    return {
        "prime_limit": limit,
        "atom_rows": atom_rows,
        "symbolic_eliminations": symbolic_eliminations,
        "nonatom_rows": nonatom_rows,
        "resonance": list(resonances[0]),
    }


P = 13
S = (1, 1, 1)


def add(x: tuple[int, int, int], y: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple((a + b) % P for a, b in zip(x, y))  # type: ignore[return-value]


def mul(k: int, x: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple((k * a) % P for a in x)  # type: ignore[return-value]


def neg(x: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple((-a) % P for a in x)  # type: ignore[return-value]


def rho_closed(x: tuple[int, int, int]) -> int:
    residue_sum = sum(x)
    return residue_sum - 2 if all(x) else residue_sum


def encoded_lines(values: Iterable[tuple[int, int, int]]) -> bytes:
    return ("".join(",".join(map(str, x)) + "\n" for x in values)).encode()


def p13_resonance_replay() -> dict[str, int | str]:
    structural = 0
    singleton_survivors: list[tuple[int, int, int]] = []
    pure_power_survivors = 0

    for a in range(P):
        for b in range(P):
            for c in range(P):
                x = (a, b, c)
                # span(s,x) avoids all three saturated axes iff the coordinates
                # of x are pairwise distinct.
                if len({a, b, c}) != 3:
                    continue
                structural += 1
                y = add(S, mul(3, x))

                if 1 + rho_closed(neg(x)) < 19 or 1 + rho_closed(neg(y)) < 19:
                    continue
                singleton_survivors.append(x)

                violated = False
                for j in range(1, 7):
                    if j + rho_closed(neg(mul(j, x))) < 19:
                        violated = True
                        break
                if not violated:
                    for k in range(1, 12):
                        if k + rho_closed(neg(mul(k, y))) < 19:
                            violated = True
                            break
                if not violated:
                    pure_power_survivors += 1

    assert structural == 1716
    assert len(singleton_survivors) == 312
    assert pure_power_survivors == 0

    digest = hashlib.sha256(encoded_lines(singleton_survivors)).hexdigest()
    assert digest == "1732d0e161660a6bae95d0c2bad1a87f9aa15b3510900236e057d29117291236"

    return {
        "p13_structural": structural,
        "p13_singleton_survivors": len(singleton_survivors),
        "p13_pure_power_survivors": pure_power_survivors,
        "p13_singleton_sha256": digest,
    }


def main() -> None:
    out = {
        "status": "A1_LIGHT_SUPPORT3_TWO_SHARE_PRIMARY_GREEN",
        **symbolic_replay(),
        **p13_resonance_replay(),
        "theorem": "a=1 first-corridor exact-support6 support3 companions have v_s(V) != 2 for every prime p>=7",
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
