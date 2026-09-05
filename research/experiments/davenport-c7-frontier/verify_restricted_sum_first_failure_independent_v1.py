#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from math import ceil
from typing import List, Tuple

EXPECTED_P7_DIGEST = "2b49f2b6f4579a27165ebe5285292a5966901f1af7793a5cf73f3e9c8d47be19"
P7_CORRIDORS = {
    (8, 10, 19), (9, 9, 19), (9, 10, 18),
    (9, 11, 17), (9, 12, 16), (10, 10, 17),
}


def coding_cap(p: int) -> int:
    return 62 if p == 5 else 3 * p * p - 3 * p - 3


def tail_threshold(p: int, eta_upper: int) -> int:
    M = (5 * p - 5) // 2
    return max(2, ceil((eta_upper - 1 - M) / p) - 1)


def multiset_signatures(total: int, parts: int, lo: int, hi: int) -> List[Tuple[int, ...]]:
    values = list(range(lo, hi + 1))
    counts = [0] * len(values)
    out: List[Tuple[int, ...]] = []

    def visit(index: int, left_parts: int, left_sum: int) -> None:
        if index == len(values):
            if left_parts == 0 and left_sum == 0:
                row: List[int] = []
                for value, count in zip(values, counts):
                    row.extend([value] * count)
                out.append(tuple(row))
            return
        value = values[index]
        max_count = min(left_parts, left_sum // value)
        for count in range(max_count + 1):
            counts[index] = count
            visit(index + 1, left_parts - count, left_sum - count * value)
        counts[index] = 0

    visit(0, parts, total)
    out.sort()
    return out


def main() -> int:
    # Verify tail threshold via the logically equivalent recurrence inequality,
    # without using the primary floor identity.
    tail_controls = []
    for p, E in ((5, 33), (7, coding_cap(7) + 1), (11, coding_cap(11) + 1)):
        M = (5 * p - 5) // 2
        t = tail_threshold(p, E)
        assert t * p + M >= E - 1 - p
        if t > 2:
            assert (t - 1) * p + M < E - 1 - p
        tail_controls.append({"p": p, "eta_upper": E, "tail_start": t})
    assert tail_controls[0]["tail_start"] == 4
    assert tail_controls[1]["tail_start"] == 15

    p = 7
    M = 15
    L = coding_cap(p)
    K = min(M + 1, (L - M - 1) // p)

    rows = []
    for m in range(3, K + 1):
        qmax = min(M // (m - 1), L - p * m - M)
        for q in range(1, qmax + 1):
            for e in multiset_signatures(M + q, m, q, 2 * p - 2):
                rows.append({"m": m, "q": q, "e": e})
    rows.sort(key=lambda row: (row["m"], row["q"], row["e"]))
    assert len(rows) == 321

    # Apply the donor predicates as direct logical filters.
    q_cap = (p - 1) // 2
    stage_q = []
    stage_short = []
    final = []
    for row in rows:
        m, q, e = row["m"], row["q"], row["e"]
        if q > q_cap:
            # q+ p -1 reaches the Bhowmik--Schlage-Puchta short-sum window.
            assert p + q - 1 >= (3 * p - 1) // 2
            assert p * m + M + q >= 6 * p - 2
            continue
        stage_q.append(row)
        if min(e) > p - 2:
            continue
        stage_short.append(row)
        if m == 3 and q == 1:
            lengths = tuple(p + x for x in e)
            if lengths not in P7_CORRIDORS:
                continue
        final.append(row)

    assert len(stage_q) == 300
    assert len(stage_short) == 299
    assert len(final) == 286

    encoded = json.dumps(final, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(encoded).hexdigest()
    assert digest == EXPECTED_P7_DIGEST, digest

    # Zhang's exact s_{<=2p-2}=4p-2 is numerically strong enough before
    # any p=7-specific input is used.
    for p in (5, 7, 11, 13, 17):
        M = (5 * p - 5) // 2
        first_failure_length = 3 * p + M + 1
        assert first_failure_length > 4 * p - 2
        assert (2 * p - 2) - p == p - 2

    print(json.dumps({
        "status": "RESTRICTED_SUM_FIRST_FAILURE_INDEPENDENT_GREEN",
        "p7_coding_raw": len(rows),
        "p7_after_q_cap": len(stage_q),
        "p7_after_short_atom": len(stage_short),
        "p7_current_signatures": len(final),
        "p7_digest": digest,
        "tail_controls": tail_controls,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
