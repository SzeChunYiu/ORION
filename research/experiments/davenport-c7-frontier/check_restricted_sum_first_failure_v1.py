#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from math import ceil
from typing import Iterator, List, Tuple

EXPECTED_P7_DIGEST = "2b49f2b6f4579a27165ebe5285292a5966901f1af7793a5cf73f3e9c8d47be19"
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


def coding_cap(p: int) -> int:
    return 62 if p == 5 else 3 * p * p - 3 * p - 3


def tail_threshold(p: int, eta_upper: int) -> int:
    M = (5 * p - 5) // 2
    return max(2, ceil((eta_upper - 1 - M) / p) - 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-prime", type=int, default=401)
    args = ap.parse_args()

    checked = 0
    for p in range(5, args.max_prime + 1):
        if not is_prime(p):
            continue
        checked += 1
        M = (5 * p - 5) // 2
        qcap = (p - 1) // 2

        # Bhowmik--Schlage-Puchta front end.
        short_threshold = (3 * p - 1) // 2
        short_forcing_length = 6 * p - 3
        q_bad = qcap + 1
        assert p + q_bad - 1 >= short_threshold
        first_failure_min_length = 3 * p + M + q_bad
        assert first_failure_min_length >= 6 * p - 2 > short_forcing_length

        # Zhang short-atom input.
        assert 3 * p + M + 1 > 4 * p - 2
        atom_max = 2 * p - 2
        assert atom_max - p == p - 2

        # Complement is long enough to insert the Zhang atom.
        m = 3
        q = 1
        N = p * m + M + q
        complement = N - atom_max
        assert complement > 3 * p - 2
        m = 4
        N = p * m + M + q
        complement = N - atom_max
        assert complement > 2 * p + M  # target D_2

        # The Griesmer first-failure level cap equals the eta-tail gate using
        # eta <= coding_cap+1.
        L = coding_cap(p)
        coding_K = min(M + 1, (L - M - 1) // p)
        eta_tail_K = tail_threshold(p, L + 1)
        assert coding_K == eta_tail_K

    # p=5 exact eta control.
    assert tail_threshold(5, 33) == 4

    # p=7: coding-refined shell, then q cap, Zhang short atom, corridors.
    p = 7
    M = 15
    L = coding_cap(p)
    K = min(M + 1, (L - M - 1) // p)
    rows = []
    for m in range(3, K + 1):
        qmax = min(M // (m - 1), L - p * m - M)
        for q in range(1, qmax + 1):
            for e in signatures(M + q, m, q, 2 * p - 2):
                rows.append({"m": m, "q": q, "e": e})
    assert len(rows) == 321

    q_rows = [row for row in rows if row["q"] <= (p - 1) // 2]
    assert len(q_rows) == 300
    short_rows = [row for row in q_rows if min(row["e"]) <= p - 2]
    assert len(short_rows) == 299

    final = []
    corridor_removed = 0
    for row in short_rows:
        if row["m"] == 3 and row["q"] == 1:
            lengths = tuple(p + value for value in row["e"])
            if lengths not in P7_CORRIDORS:
                corridor_removed += 1
                continue
        final.append(row)
    assert corridor_removed == 13
    assert len(final) == 286

    encoded = json.dumps(final, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(encoded).hexdigest()
    assert digest == EXPECTED_P7_DIGEST, digest

    print(json.dumps({
        "status": "RESTRICTED_SUM_FIRST_FAILURE_GREEN",
        "checked_primes": checked,
        "p7_coding_raw": len(rows),
        "p7_after_q_cap": len(q_rows),
        "p7_after_short_atom": len(short_rows),
        "p7_corridor_removed": corridor_removed,
        "p7_current_signatures": len(final),
        "p7_digest": digest,
        "p5_eta_tail_threshold": tail_threshold(5, 33),
        "p7_griesmer_tail_threshold": tail_threshold(7, coding_cap(7) + 1),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
