#!/usr/bin/env python3
"""Regression for the exact a=2 radial-excess parity staircase."""
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


def closed_cost(c: int, D: int) -> int:
    L = max(D - c - 2, 0)
    return D + 2 * ((L + 1) // 2)


def mutated_floor_cost(c: int, D: int) -> int:
    """Hostile mutation: rounds the parity surcharge down instead of up."""
    L = max(D - c - 2, 0)
    return D + 2 * (L // 2)


def exact_oracle(p: int, c: int, D: int) -> tuple[int, int, int]:
    u = (p + 1) // 2
    best = 10**18
    best_q = -1
    best_z = -1
    for q in range(p - 1):  # 0 <= q <= p-2
        z = (D - q) % p
        if z > c + 2:
            continue
        cost = z + q + 2 * ((u * q) % p)
        if cost < best:
            best, best_q, best_z = cost, q, z
    assert best < 10**18
    return best, best_q, best_z


def broad_symbolic_regression() -> tuple[int, int, int, int]:
    primes = 0
    parity_checks = 0
    feasibility_checks = 0
    mutation_disagreements = 0
    for p in range(5, 1010):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        u = (p + 1) // 2

        # The inverse-of-two residue law is the load-bearing arithmetic step.
        for q in range(p - 1):
            if q % 2 == 0:
                assert (u * q) % p == q // 2
            else:
                j = (q - 1) // 2
                assert (u * q) % p == H + 1 + j
                assert 2 * ((u * q) % p) == p + q
            parity_checks += 1

        # Every possible positive lower endpoint L=D-c-2 is replayed without
        # redundantly iterating all (c,D) pairs. L=0 covers the literal range.
        for D in range(p):
            for L in range(max(D - (p - 3) - 2, 0), max(D - 2, 0) + 1):
                q0 = 2 * ((L + 1) // 2)
                assert q0 % 2 == 0
                assert 0 <= q0 <= p - 2
                assert q0 <= D
                z0 = D - q0
                # For L>0, c is forced by L=D-c-2. For L=0 choose c=max(D-2,0).
                c = D - L - 2 if L > 0 else max(D - 2, 0)
                assert 0 <= c <= p - 3
                assert 0 <= z0 <= c + 2
                assert z0 + q0 + 2 * ((u * q0) % p) == closed_cost(c, D)
                assert closed_cost(c, D) < D + p
                feasibility_checks += 1
                if mutated_floor_cost(c, D) != closed_cost(c, D):
                    mutation_disagreements += 1

    assert mutation_disagreements > 0
    return primes, parity_checks, feasibility_checks, mutation_disagreements


def bounded_oracle_regression() -> tuple[int, int, int, int, str]:
    primes = 0
    rows = 0
    even_optimizers = 0
    mutation_disagreements = 0
    transcript = hashlib.sha256()

    for p in range(5, 102):
        if not is_prime(p):
            continue
        primes += 1
        for c in range(p - 2):  # full theorem range 0 <= c <= p-3
            for D in range(p):
                best, q, z = exact_oracle(p, c, D)
                formula = closed_cost(c, D)
                assert best == formula, (p, c, D, best, formula, q, z)
                assert q % 2 == 0
                assert q == 2 * ((max(D - c - 2, 0) + 1) // 2)
                assert z == D - q
                rows += 1
                even_optimizers += 1
                if mutated_floor_cost(c, D) != best:
                    mutation_disagreements += 1
                transcript.update(f"{p},{c},{D},{best},{q},{z}\n".encode())

    assert mutation_disagreements > 0
    return primes, rows, even_optimizers, mutation_disagreements, transcript.hexdigest()


def doubled_target_regression() -> int:
    checks = 0
    for p in range(5, 1010):
        if not is_prime(p):
            continue
        H = (p - 1) // 2
        cmax = 2 * (H // 2)
        for c in range(1, cmax + 1):
            cost = closed_cost(c, 2 * c)
            expected = 2 if c == 1 else (3 * c - 2 if c % 2 == 0 else 3 * c - 1)
            assert cost == expected
            checks += 1
    return checks


def main() -> None:
    broad = broad_symbolic_regression()
    bounded = bounded_oracle_regression()
    doubled = doubled_target_regression()
    result = {
        "status": "A2_EXACT_RADIAL_EXCESS_GREEN",
        "broad_primes_through_1009": broad[0],
        "broad_parity_checks": broad[1],
        "broad_feasibility_checks": broad[2],
        "broad_floor_mutation_disagreements": broad[3],
        "oracle_primes_through_101": bounded[0],
        "oracle_full_capacity_rows": bounded[1],
        "oracle_even_optimizers": bounded[2],
        "oracle_floor_mutation_disagreements": bounded[3],
        "oracle_transcript_sha256": bounded[4],
        "doubled_target_checks": doubled,
        "authority": "symbolic parity theorem; bounded full-capacity oracle is regression and mutation control",
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
