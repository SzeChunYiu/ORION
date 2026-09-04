#!/usr/bin/env python3
"""Primary exact p=7 minimal-level defect-signature enumeration."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Dict, Iterator, List, Tuple

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
EXPECTED_PRUNED_BY_M = dict(EXPECTED_RAW_BY_M, **{})
EXPECTED_PRUNED_BY_M[3] = 42


def bounded_partitions(total: int, parts: int, lower: int, upper: int) -> Iterator[Tuple[int, ...]]:
    current: List[int] = []

    def visit(left: int, slots: int, floor: int) -> Iterator[Tuple[int, ...]]:
        if slots == 0:
            if left == 0:
                yield tuple(current)
            return
        if left < slots * floor or left > slots * upper:
            return
        for value in range(floor, min(upper, left // slots) + 1):
            current.append(value)
            yield from visit(left - value, slots - 1, value)
            current.pop()

    yield from visit(total, parts, lower)


def main() -> int:
    raw: List[dict] = []

    for m in range(3, M + 2):
        for q in range(1, M // (m - 1) + 1):
            for excesses in bounded_partitions(M + q, m, q, MAX_EXCESS):
                assert sum(excesses) == M + q
                assert min(excesses) >= q
                assert max(excesses) <= MAX_EXCESS
                # Every proper subset has excess at most M.  The largest one
                # omits a smallest entry, so it is enough to check this form.
                assert sum(excesses) - min(excesses) <= M
                assert all(
                    excesses[i] + excesses[j] <= M
                    for i in range(m)
                    for j in range(i + 1, m)
                )
                raw.append({"m": m, "q": q, "e": list(excesses)})

    raw.sort(key=lambda row: (row["m"], row["q"], row["e"]))
    raw_by_m = dict(sorted(Counter(row["m"] for row in raw).items()))
    assert raw_by_m == EXPECTED_RAW_BY_M
    assert len(raw) == 322

    short_atom_removed = [row for row in raw if min(row["e"]) > 5]
    assert len(short_atom_removed) == 8
    assert all(row["m"] == 3 for row in short_atom_removed)

    pruned: List[dict] = []
    corridor_removed = 0
    for row in raw:
        if min(row["e"]) > 5:
            continue
        if row["m"] == 3 and row["q"] == 1:
            atom_lengths = tuple(P + value for value in row["e"])
            if atom_lengths not in CORRIDORS:
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
                "status": "PACKING_DEFECT_MINIMAL_SIGNATURES_GREEN",
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
