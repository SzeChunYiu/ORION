#!/usr/bin/env python3
"""Regression for A3_RANK3_SHARED_DONOR_NEGATIVE_EVEN_V1.md.

The all-prime authority is the symbolic proof.  This script checks the exact
occurrence identities on a bounded hostile range and uses explicit exceptions,
so `python -O` does not remove any validation.
"""

from math import isqrt


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def primes_upto(n):
    out = []
    for x in range(2, n + 1):
        prime = True
        for q in range(2, isqrt(x) + 1):
            if x % q == 0:
                prime = False
                break
        if prime:
            out.append(x)
    return out


def run(limit=401):
    doubling_rows = 0
    boundary_rows = 0
    negative_even_certificates = 0
    scalar_two_certificates = 0

    for p in primes_upto(limit):
        if p < 11 or p == 3:
            continue

        H = (p - 1) // 2
        m = p + H
        epsilon = p % 3
        require(epsilon in (1, 2), f"bad epsilon p={p}")
        Q = (p - epsilon) // 3

        # The proved type-three multi-copy ceiling used by the theorem.
        for c in range(1, H // 2 + 1):
            for d in (1, 2):
                S = c + d

                # Shared-donor doubling: check every interior multiplicity row,
                # without imposing the stronger coefficient-atom filters.
                for r in range(H + 1, p):
                    t = m - S - r
                    if not (H + 1 <= t <= p - 1):
                        continue

                    q = (c - 1) // 3
                    E = q
                    z = 2 * c - 3 * q
                    w = 2 * d + 3 * q
                    R = 2 * r - p
                    T = 2 * t - p

                    require(0 <= E <= p - 1, "doubling saturated capacity")
                    require(0 <= z <= c + 3, "doubling s capacity")
                    require(0 <= w <= p - 3 + d, "doubling g capacity")
                    require(1 <= R <= r and 1 <= T <= t, "doubling new capacity")
                    require(3 * E + z == 2 * c, "doubling s identity")
                    require(w - 3 * E == 2 * d, "doubling g identity")

                    length = 2 * E + z + w + R + T
                    require(length == p - 1 + 2 * q, "doubling length identity")
                    require(length < m, "doubling must be short")
                    doubling_rows += 1

                # Boundary strip and the general negative-even theorem.
                for k in range(S):
                    r = H - k
                    t = p - S + k
                    if not (1 <= r <= t <= p - 1):
                        continue
                    require(c + d + r + t == m, "boundary length")
                    boundary_rows += 1

                    for J in range(2, p, 2):
                        tau = (-J) % 3
                        L = (J + tau) // 3
                        E = Q - L * c
                        z = tau * c + epsilon
                        w = p - J * S - tau * c - epsilon

                        hypotheses = (
                            E >= 0
                            and z <= c + 3
                            and w >= 0
                            and (J + 1) * k + J // 2 <= H
                            and (J + 1) * (S - k) <= p
                            and p + 2 * Q - 2 * L * c + J // 2 < m
                        )
                        if not hypotheses:
                            continue

                        R = J // 2 + J * k
                        T = J * (S - k)

                        require(0 <= E <= p - 1, "negative-even saturated capacity")
                        require(0 <= z <= c + 3, "negative-even s capacity")
                        require(0 <= w <= p - 3 + d, "negative-even g capacity")
                        require(1 <= R <= r and 1 <= T <= t, "negative-even new capacity")
                        require(R % p == ((p - J) * r) % p, "negative-even x residue")
                        require(T % p == ((p - J) * t) % p, "negative-even y residue")
                        require((3 * E + z + J * c) % p == 0, "negative-even s identity")
                        require((w - 3 * E + J * d) % p == 0, "negative-even g identity")

                        length = 2 * E + z + w + R + T
                        closed = p + 2 * Q - 2 * L * c + J // 2
                        require(length == closed, "negative-even closed score")
                        require(length < m, "negative-even must be short")

                        negative_even_certificates += 1
                        if J == 2:
                            require(tau == 1 and L == 1, "J=2 parameters")
                            require(closed == p + 2 * Q - 2 * c + 1, "J=2 score")
                            scalar_two_certificates += 1

    # Positive controls freeze that each lane was actually exercised.
    require(doubling_rows > 100000, "doubling regression unexpectedly small")
    require(boundary_rows > 100000, "boundary regression unexpectedly small")
    require(negative_even_certificates > 100000, "certificate regression unexpectedly small")
    require(scalar_two_certificates > 10000, "J=2 regression unexpectedly small")

    print(
        "A3 shared-donor negative-even regression GREEN",
        f"doubling={doubling_rows}",
        f"boundary={boundary_rows}",
        f"negative_even={negative_even_certificates}",
        f"J2={scalar_two_certificates}",
    )


if __name__ == "__main__":
    run()
