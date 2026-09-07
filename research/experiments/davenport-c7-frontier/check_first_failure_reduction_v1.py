#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from math import ceil
from typing import Iterator, List, Tuple

EXPECTED_SHA256 = "37f152e4074a10edeedc14ea52207fb189bcc000dcb2901c4bb182defe91d68c"
P7_CORRIDORS = {
    (8, 10, 19), (9, 9, 19), (9, 10, 18),
    (9, 11, 17), (9, 12, 16), (10, 10, 17),
}


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


def signatures(total: int, parts: int, lo: int, hi: int) -> Iterator[Tuple[int, ...]]:
    current: List[int] = []
    def visit(left: int, slots: int, lower: int):
        if slots == 0:
            if left == 0:
                yield tuple(current)
            return
        if left < slots * lower or left > slots * hi:
            return
        for value in range(lower, min(hi, left // slots) + 1):
            current.append(value)
            yield from visit(left - value, slots - 1, value)
            current.pop()
    yield from visit(total, parts, lo)


def griesmer_rhs(d: int, p: int) -> int:
    return d + ceil(d / p) + ceil(d / (p * p))


def shortfree_code_cap(p: int) -> int:
    return 62 if p == 5 else 3 * p * p - 3 * p - 3


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-prime", type=int, default=401)
    args = ap.parse_args()
    primes = [p for p in range(5, args.max_prime + 1) if is_prime(p)]
    prime_records = []

    for p in primes:
        M = (5 * p - 5) // 2
        assert 3 * p - 2 - p == 2 * p - 2 < M
        L = shortfree_code_cap(p)
        plane_cap = 3 * p - 3
        d = L - plane_cap
        assert griesmer_rhs(d, p) <= L
        d_bad = L + 1 - plane_cap
        assert griesmer_rhs(d_bad, p) > L + 1
        K = min(M + 1, (L - M - 1) // p)
        if p == 5:
            assert K == 10
        elif p == 7:
            assert K == 15
        else:
            assert p >= 11 and K == (5 * p - 3) // 2
        arc_cutoff = 2 * p - 4
        N = p * (arc_cutoff + 1) + M + 1
        assert ceil(N / (p - 1)) >= 2 * p + 2
        pair_count = 0
        for m in range(3, K + 1):
            qmax = min(M // (m - 1), L - p * m - M)
            assert qmax >= 1
            for q in range(1, qmax + 1):
                assert M - (m - 1) * q >= 0
                assert p * m + M + q <= L
                pair_count += 1
        prime_records.append({
            "p": p, "M": M, "shortfree_code_cap": L,
            "first_failure_level_cap": K, "arc_only_level_cap": arc_cutoff,
            "first_failure_mq_pairs": pair_count,
        })

    canonical = {}
    totals = {}
    p7_rows = []
    for p in (5, 7):
        M = (5 * p - 5) // 2
        L = shortfree_code_cap(p)
        K = min(M + 1, (L - M - 1) // p)
        rows = []
        distribution = {}
        for m in range(3, K + 1):
            qmax = min(M // (m - 1), L - p * m - M)
            for q in range(1, qmax + 1):
                current = list(signatures(M + q, m, q, 2 * p - 2))
                if current:
                    for row in current:
                        assert all(value >= q for value in row)
                        for omitted in range(m):
                            assert sum(row) - row[omitted] <= M
                    distribution[f"{m},{q}"] = len(current)
                    payload = [{"m": m, "q": q, "e": row} for row in current]
                    rows.extend(payload)
                    if p == 7:
                        p7_rows.extend(payload)
        canonical[str(p)] = {"K": K, "dist": distribution, "rows": rows}
        totals[p] = len(rows)

    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(encoded).hexdigest()
    assert digest == EXPECTED_SHA256, digest
    assert totals == {5: 71, 7: 321}

    short_removed = [row for row in p7_rows if min(row["e"]) > 5]
    assert len(short_removed) == 8
    pruned = []
    corridor_removed = 0
    for row in p7_rows:
        if min(row["e"]) > 5:
            continue
        if row["m"] == 3 and row["q"] == 1:
            lengths = tuple(7 + e for e in row["e"])
            if lengths not in P7_CORRIDORS:
                corridor_removed += 1
                continue
        pruned.append(row)
    assert corridor_removed == 13
    assert len(pruned) == 300

    print(json.dumps({
        "status": "FINITE_FIRST_FAILURE_REDUCTION_GREEN",
        "checked_primes": len(primes),
        "largest_prime": primes[-1] if primes else None,
        "p5_first_failure_signatures": totals[5],
        "p7_first_failure_signatures": totals[7],
        "p7_short_atom_removed": len(short_removed),
        "p7_corridor_removed": corridor_removed,
        "p7_donor_pruned_signatures": len(pruned),
        "canonical_sha256": digest,
        "first_prime_records": prime_records[:3],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
