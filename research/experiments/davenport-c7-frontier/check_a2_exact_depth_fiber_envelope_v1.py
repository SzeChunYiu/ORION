#!/usr/bin/env python3
"""Regression for the exact a=2 representation-depth fiber envelope."""
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


def depth(p: int, P: int, Q: int, C: int) -> int:
    H = (p - 1) // 2
    u = H + 1
    values: list[int] = []
    for k in (0, 1, 2):
        g_count = (C - k) % p
        if g_count > p - 2:
            continue
        values.append((P - k * u) % p + (Q - k * u) % p + g_count + k)
    assert values
    return min(values)


def closed_K(p: int, w: int) -> tuple[int, int, int, int]:
    H = (p - 1) // 2
    if w <= H - 1:
        return (
            p + w,
            p + w - 1,
            p + w - 2,
            p - 1 if w == 0 else p + w - 2,
        )
    if w == H:
        return p + H, H, H, p + H - 2
    if w <= p - 2:
        return p + w, w, w - 1, w - 1
    return p - 1, p - 1, p - 2, p - 2


def closed_M(p: int, w: int, C: int) -> int:
    H = (p - 1) // 2
    if w <= H - 1:
        if C <= 2:
            return p + w
        if C <= p - 2:
            return p + w + C - 2
        return 2 * p - 2 if w == 0 else 2 * p + w - 3
    if w == H:
        if C == 0:
            return p + H
        if C <= p - 2:
            return H + C
        return 2 * p + H - 3
    if w <= p - 2:
        if C == 0:
            return p + w
        if C <= 2:
            return w + 1
        return w + C - 1
    if C == 0:
        return p - 1
    if C <= 2:
        return p
    return p + C - 2


def mutated_M(p: int, w: int, C: int) -> int:
    """Hostile mutation: treats the middle fiber as an ordinary low fiber."""
    H = (p - 1) // 2
    if w == H and 1 <= C <= p - 2:
        return p + w + C - 2
    return closed_M(p, w, C)


def direct_K(p: int, w: int) -> tuple[int, int, int, int]:
    H = (p - 1) // 2
    u = H + 1
    maxima = [-1, -1, -1, -1]
    for P in range(p):
        Q = (w - P) % p
        S0 = P + Q
        S1 = (P - u) % p + (Q - u) % p
        S2 = (P - 1) % p + (Q - 1) % p
        values = (
            min(S0, S2 + p),
            min(S0, S1),
            min(S0, S1, S2),
            min(S1, S2),
        )
        maxima = [max(a, b) for a, b in zip(maxima, values)]
    return tuple(maxima)  # type: ignore[return-value]


def broad_witness_regression() -> tuple[int, int]:
    primes = 0
    witnesses = 0
    for p in range(5, 1010):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        u = H + 1
        for w in range(p):
            candidates: list[tuple[int, int]] = []
            if w <= H - 1:
                candidates.append((w + 1, p - 1))
                candidates.append((0, w))
            elif w == H:
                candidates.append((H + 1, p - 1))
                candidates.append((0, H))
            elif w <= p - 2:
                candidates.append((w + 1, p - 1))
                candidates.append((w - H, H))
                candidates.append((0, w))
            else:
                candidates.append((0, p - 1))
                candidates.append((H, H))

            attained = [-1, -1, -1, -1]
            for P, Q in candidates:
                assert (P + Q) % p == w
                S0 = P + Q
                S1 = (P - u) % p + (Q - u) % p
                S2 = (P - 1) % p + (Q - 1) % p
                vals = (
                    min(S0, S2 + p),
                    min(S0, S1),
                    min(S0, S1, S2),
                    min(S1, S2),
                )
                attained = [max(a, b) for a, b in zip(attained, vals)]
            assert tuple(attained) == closed_K(p, w), (p, w, attained, closed_K(p, w))
            witnesses += len(candidates)
    return primes, witnesses


def broad_K_regression() -> tuple[int, int, str]:
    primes = 0
    fibers = 0
    transcript = hashlib.sha256()
    for p in range(5, 402):
        if not is_prime(p):
            continue
        primes += 1
        for w in range(p):
            got = direct_K(p, w)
            want = closed_K(p, w)
            assert got == want, (p, w, got, want)
            fibers += 1
            transcript.update(f"{p},{w},{got}\n".encode())
    return primes, fibers, transcript.hexdigest()


def bounded_full_regression() -> tuple[int, int, int, str, int]:
    primes = 0
    fibers = 0
    points = 0
    mutation_disagreements = 0
    transcript = hashlib.sha256()
    for p in range(5, 102):
        if not is_prime(p):
            continue
        primes += 1
        for w in range(p):
            for C in range(p):
                got = max(depth(p, P, (w - P) % p, C) for P in range(p))
                want = closed_M(p, w, C)
                assert got == want, (p, w, C, got, want)
                fibers += 1
                points += p
                if mutated_M(p, w, C) != got:
                    mutation_disagreements += 1
                transcript.update(f"{p},{w},{C},{got}\n".encode())
    assert mutation_disagreements > 0
    return primes, fibers, points, transcript.hexdigest(), mutation_disagreements


def endpoint_mutation_regression() -> int:
    disagreements = 0
    for p in range(5, 1010):
        if not is_prime(p):
            continue
        # Hostile endpoint mutation: use the generic low-fiber formula at w=0,C=p-1.
        wrong = 2 * p - 3
        right = closed_M(p, 0, p - 1)
        assert right == 2 * p - 2
        assert wrong != right
        disagreements += 1
    return disagreements


def main() -> None:
    witnesses = broad_witness_regression()
    broad = broad_K_regression()
    bounded = bounded_full_regression()
    endpoint = endpoint_mutation_regression()
    print(json.dumps({
        "status": "A2_EXACT_DEPTH_FIBER_ENVELOPE_GREEN",
        "witness_primes_through_1009": witnesses[0],
        "explicit_witness_pairs_checked": witnesses[1],
        "broad_primes_through_401": broad[0],
        "broad_pair_sum_fibers": broad[1],
        "broad_K_transcript_sha256": broad[2],
        "full_primes_through_101": bounded[0],
        "full_depth_fibers": bounded[1],
        "full_depth_points": bounded[2],
        "full_M_transcript_sha256": bounded[3],
        "middle_fiber_mutation_disagreements": bounded[4],
        "double_zero_endpoint_mutation_disagreements": endpoint,
        "authority": "threshold/carry theorem with explicit witnesses; exhaustive checks are regression and hostile controls",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
