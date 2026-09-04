#!/usr/bin/env python3
"""Regression for the all-corridor maximal-pair support-six theorem."""

from __future__ import annotations

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


def partitions_n_sum(n: int, total: int, last: int = 1, maxv: int | None = None):
    """Yield nondecreasing positive n-tuples with given sum."""
    if maxv is None:
        maxv = total
    if n == 0:
        if total == 0:
            yield ()
        return
    hi = min(maxv, total // n)
    for v in range(last, hi + 1):
        rem = total - v
        if n > 1:
            if rem < (n - 1) * v or rem > (n - 1) * maxv:
                continue
        elif rem != 0:
            continue
        for tail in partitions_n_sum(n - 1, rem, v, maxv):
            yield (v,) + tail


def prescribed_scalar(p: int, a: tuple[int, ...]) -> int:
    x = max(a)
    if x <= (p - 1) // 2:
        return 1
    if 3 * x <= 2 * p:
        return 2
    return 3


def check_support5_partition(p: int, a: tuple[int, ...]) -> None:
    c = prescribed_scalar(p, a)
    m = tuple(p - x for x in a)
    r = tuple((c * x) % p for x in a)
    assert all(1 <= rr <= mm for rr, mm in zip(r, m)), (p, a, c, r, m)
    assert sum(r) < p, (p, a, c, sum(r))


def check_prime(p: int) -> dict[str, int]:
    corridors = 0
    exhaustive_partitions = 0
    max_j = (p + 1) // 4

    for j in range(1, max_j + 1):
        corridors += 1
        b = (p + 1) // 2 - j
        short_len = p + j
        long_len = p + b
        maximal_len = 3 * p - 2
        pair_len = long_len + maximal_len
        inherited_depth = p + b - 1

        assert j <= b
        assert j + b == (p + 1) // 2
        assert short_len + long_len + maximal_len == (11 * p - 3) // 2
        assert pair_len - inherited_depth == 3 * p - 1
        assert inherited_depth >= p

        # Five-support complement weight.
        A5 = 5 * p - pair_len
        assert A5 == (p + 2 * j + 3) // 2
        assert 4 * A5 <= 3 * p + 7

        if p >= 11:
            assert A5 < p
            # Symbolic envelopes used in the proof.
            assert 3 * (p - 7) <= 4 * p
            assert 3 * p - 9 < 3 * p

            if p <= 61:
                for a in partitions_n_sum(5, A5, 1, p - 1):
                    exhaustive_partitions += 1
                    check_support5_partition(p, a)
        else:
            # p=5,7 are covered by the original scalar-1 support-complement lemma.
            Delta = (p + 2 * j - 7) // 2
            assert Delta >= 0
            assert 5 + Delta <= p
            assert 2 * Delta <= p - 2

        # Exact scalar-only ceiling at support six.
        A6 = 6 * p - pair_len
        assert A6 == (3 * p + 2 * j + 3) // 2
        c6 = (p + 2 * j - 3) // 2
        a6 = (1, 1, 1, 1, c6, p - 1)
        assert sum(a6) == A6
        assert all(1 <= x <= p - 1 for x in a6)
        m6 = tuple(p - x for x in a6)

        embedded = []
        for t in range(1, p):
            r = tuple((t * x) % p for x in a6)
            if all(1 <= rr <= mm for rr, mm in zip(r, m6)):
                embedded.append((t, r))

        assert embedded == [(p - 1, m6)], (p, j, embedded)

    return {
        "corridors": corridors,
        "exhaustive_partitions": exhaustive_partitions,
    }


def main() -> None:
    primes = [p for p in range(5, 402) if is_prime(p)]
    total_corridors = 0
    total_partitions = 0

    for p in primes:
        out = check_prime(p)
        total_corridors += out["corridors"]
        total_partitions += out["exhaustive_partitions"]

    print(
        json.dumps(
            {
                "status": "MAXIMAL_PAIR_SUPPORT6_ALL_CORRIDORS_GREEN",
                "checked_primes": len(primes),
                "max_prime": primes[-1],
                "checked_corridors": total_corridors,
                "exhaustive_partition_prime_cap": 61,
                "exhaustive_partitions": total_partitions,
                "support5_scalars": [1, 2, 3],
                "support6_scalar_ceiling": "only t=p-1 embeds on frozen profile",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
