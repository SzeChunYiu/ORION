#!/usr/bin/env python3
"""Independent multiplicity-vector verifier for the 322 -> 301 signature cover."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Iterator, List, Sequence, Tuple

P = 7
M = 15
MAX_EXCESS = 12
CORRIDORS = {
    (8, 10, 19),
    (9, 9, 19),
    (9, 10, 18),
    (9, 11, 17),
    (9, 12, 16),
    (10, 10, 17),
}
EXPECTED_RAW_BY_M = {
    3: 63,
    4: 64,
    5: 53,
    6: 43,
    7: 31,
    8: 23,
    9: 15,
    10: 11,
    11: 7,
    12: 5,
    13: 3,
    14: 2,
    15: 1,
    16: 1,
}
EXPECTED_PRUNED_BY_M = {
    3: 42,
    4: 64,
    5: 53,
    6: 43,
    7: 31,
    8: 23,
    9: 15,
    10: 11,
    11: 7,
    12: 5,
    13: 3,
    14: 2,
    15: 1,
    16: 1,
}


def multiplicity_solutions(m: int, q: int) -> Iterator[Tuple[int, ...]]:
    values = list(range(q, MAX_EXCESS + 1))
    target = M + q
    counts = [0] * len(values)

    def visit(index: int, slots_left: int, sum_left: int) -> Iterator[Tuple[int, ...]]:
        if index == len(values) - 1:
            value = values[index]
            if slots_left * value == sum_left:
                counts[index] = slots_left
                expanded = tuple(
                    v
                    for v, count in zip(values, counts)
                    for _ in range(count)
                )
                yield expanded
            return

        value = values[index]
        next_value = values[index + 1]
        max_count = min(slots_left, sum_left // value)
        for count in range(max_count + 1):
            remaining_slots = slots_left - count
            remaining_sum = sum_left - count * value
            if remaining_sum < remaining_slots * next_value:
                continue
            if remaining_sum > remaining_slots * MAX_EXCESS:
                continue
            counts[index] = count
            yield from visit(index + 1, remaining_slots, remaining_sum)
        counts[index] = 0

    yield from visit(0, m, target)


def main() -> int:
    raw: List[dict] = []

    for m in range(3, M + 2):
        q = 1
        while (m - 1) * q <= M:
            rows = list(multiplicity_solutions(m, q))
            assert len(rows) == len(set(rows))
            for excesses in rows:
                assert len(excesses) == m
                assert tuple(sorted(excesses)) == excesses
                assert sum(excesses) == M + q
                assert excesses[0] >= q
                # Independently scan every proper subset size through all masks.
                for mask in range(1, (1 << m) - 1):
                    subtotal = sum(excesses[i] for i in range(m) if mask & (1 << i))
                    assert subtotal <= M
                raw.append({"m": m, "q": q, "e": list(excesses)})
            q += 1

    raw.sort(key=lambda row: (row["m"], row["q"], row["e"]))
    raw_by_m = dict(sorted(Counter(row["m"] for row in raw).items()))
    assert raw_by_m == EXPECTED_RAW_BY_M
    assert len(raw) == 322

    short_atom_removed = [row for row in raw if all(value >= 6 for value in row["e"])]
    assert len(short_atom_removed) == 8

    pruned: List[dict] = []
    corridor_removed = 0
    for row in raw:
        if row in short_atom_removed:
            continue
        if (row["m"], row["q"]) == (3, 1):
            lengths = tuple(value + P for value in row["e"])
            if lengths not in CORRIDORS:
                corridor_removed += 1
                continue
        pruned.append(row)

    assert corridor_removed == 13
    pruned_by_m = dict(sorted(Counter(row["m"] for row in pruned).items()))
    assert pruned_by_m == EXPECTED_PRUNED_BY_M
    assert len(pruned) == 301

    canonical = {
        "raw": raw,
        "pruned": pruned,
        "raw_by_m": raw_by_m,
        "pruned_by_m": pruned_by_m,
        "short_atom_removed": short_atom_removed,
        "corridors": sorted(CORRIDORS),
    }
    digest = hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    print(
        json.dumps(
            {
                "status": "PACKING_DEFECT_MINIMAL_SIGNATURES_INDEPENDENT_GREEN",
                "method": "excess-multiplicity vectors plus full proper-subset scan",
                "raw_signatures": len(raw),
                "short_atom_removed": len(short_atom_removed),
                "corridor_removed": corridor_removed,
                "pruned_signatures": len(pruned),
                "raw_by_m": raw_by_m,
                "pruned_by_m": pruned_by_m,
                "canonical_sha256": digest,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
