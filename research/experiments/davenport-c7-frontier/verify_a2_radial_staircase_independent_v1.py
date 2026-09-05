#!/usr/bin/env python3
"""Independent full-capacity and hostile replay of the a=2 radial staircase."""
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
    lower = max(D - c - 2, 0)
    return D + 2 * ((lower + 1) // 2)


def mutated_floor_cost(c: int, D: int) -> int:
    """Hostile mutation: round the parity surcharge down instead of up."""
    lower = max(D - c - 2, 0)
    return D + 2 * (lower // 2)


def exact_oracle(p: int, c: int, D: int) -> tuple[int, int, int]:
    """Minimize directly over bounded counts of g and literal s."""
    inverse_two = (p + 1) // 2
    best = 10**18
    best_q = -1
    best_z = -1
    for q in range(p - 1):  # 0 <= q <= p-2 copies of g
        z = (D - q) % p
        if z > c + 2:
            continue
        cost = z + q + 2 * ((inverse_two * q) % p)
        if cost < best:
            best, best_q, best_z = cost, q, z
    assert best < 10**18
    return best, best_q, best_z


def broad_symbolic_replay() -> dict[str, int]:
    primes = 0
    parity_checks = 0
    feasibility_checks = 0
    mutation_disagreements = 0

    for p in range(5, 1010):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        inverse_two = H + 1

        for q in range(p - 1):
            if q % 2 == 0:
                assert (inverse_two * q) % p == q // 2
            else:
                j = (q - 1) // 2
                assert (inverse_two * q) % p == H + 1 + j
                assert 2 * ((inverse_two * q) % p) == p + q
            parity_checks += 1

        # Replay every possible lower endpoint L=max(D-c-2,0) without
        # redundantly traversing all formal pairs when L=0.
        for D in range(p):
            for lower in range(max(D - (p - 3) - 2, 0), max(D - 2, 0) + 1):
                q0 = 2 * ((lower + 1) // 2)
                z0 = D - q0
                c = D - lower - 2 if lower > 0 else max(D - 2, 0)
                assert 0 <= c <= p - 3
                assert q0 % 2 == 0
                assert 0 <= q0 <= p - 2
                assert q0 <= D
                assert 0 <= z0 <= c + 2
                assert (
                    z0 + q0 + 2 * ((inverse_two * q0) % p)
                    == closed_cost(c, D)
                )
                assert closed_cost(c, D) < D + p
                feasibility_checks += 1
                if mutated_floor_cost(c, D) != closed_cost(c, D):
                    mutation_disagreements += 1

    result = {
        "primes_through_1009": primes,
        "parity_checks": parity_checks,
        "feasibility_checks": feasibility_checks,
        "floor_mutation_disagreements": mutation_disagreements,
    }
    assert result == {
        "primes_through_1009": 167,
        "parity_checks": 76964,
        "feasibility_checks": 25066528,
        "floor_mutation_disagreements": 12513856,
    }
    return result


def full_capacity_oracle_replay() -> dict[str, int | str]:
    primes = 0
    rows = 0
    even_optimizers = 0
    mutation_disagreements = 0
    transcript = hashlib.sha256()

    for p in range(5, 102):
        if not is_prime(p):
            continue
        primes += 1
        for c in range(p - 2):  # full formal range 0 <= c <= p-3
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

    result: dict[str, int | str] = {
        "primes_through_101": primes,
        "rows": rows,
        "even_optimizers": even_optimizers,
        "floor_mutation_disagreements": mutation_disagreements,
        "transcript_sha256": transcript.hexdigest(),
    }
    assert result == {
        "primes_through_101": 24,
        "rows": 73672,
        "even_optimizers": 73672,
        "floor_mutation_disagreements": 17858,
        "transcript_sha256": "a1775e11ae11f91b54766349013754aff9d0e159d72770cc32156414db8d6371",
    }
    return result


def doubled_target_replay() -> int:
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
    assert checks == 38396
    return checks


def main() -> None:
    print(json.dumps({
        "status": "A2_RADIAL_STAIRCASE_INDEPENDENT_AUDIT_GREEN",
        "broad_symbolic_replay": broad_symbolic_replay(),
        "full_capacity_oracle_replay": full_capacity_oracle_replay(),
        "doubled_target_checks": doubled_target_replay(),
        "authority": "independent verification and hostile mutation audit only; canonical theorem authority remains the integration-lane arithmetic proof",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
