#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json

EXPECTED_SHA256 = "37f152e4074a10edeedc14ea52207fb189bcc000dcb2901c4bb182defe91d68c"
P7_CORRIDORS = {
    (8, 10, 19), (9, 9, 19), (9, 10, 18),
    (9, 11, 17), (9, 12, 16), (10, 10, 17),
}


def normalize(v: tuple[int, int, int], p: int) -> tuple[int, int, int]:
    for x in v:
        if x % p:
            inv = pow(x, -1, p)
            return tuple((y * inv) % p for y in v)
    raise ValueError("zero vector")


def projective_points(p: int) -> list[tuple[int, int, int]]:
    return sorted({
        normalize((a, b, c), p)
        for a in range(p)
        for b in range(p)
        for c in range(p)
        if (a, b, c) != (0, 0, 0)
    })


def enumerate_signatures(p: int, m: int, q: int):
    M = (5 * p - 5) // 2
    total = M + q
    values = list(range(q, 2 * p - 1))
    counts = [0] * len(values)
    out = []
    def visit(index: int, left_parts: int, left_sum: int):
        if index == len(values):
            if left_parts == 0 and left_sum == 0:
                row = []
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
    visit(0, m, total)
    return out


def shortfree_code_cap(p: int) -> int:
    return 62 if p == 5 else 3 * p * p - 3 * p - 3


def main() -> int:
    geometry = []
    for p in (5, 7, 11):
        points = projective_points(p)
        lines = list(points)
        expected = p * p + p + 1
        assert len(points) == len(lines) == expected
        point_degrees = [0] * len(points)
        line_sizes = []
        incidence_count = 0
        for line in lines:
            size = 0
            for i, point in enumerate(points):
                if sum(x * y for x, y in zip(line, point)) % p == 0:
                    size += 1
                    point_degrees[i] += 1
                    incidence_count += 1
            line_sizes.append(size)
        assert set(line_sizes) == {p + 1}
        assert set(point_degrees) == {p + 1}
        assert incidence_count == expected * (p + 1)
        geometry.append({
            "p": p, "projective_points": expected,
            "line_size": p + 1, "lines_through_point": p + 1,
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
                sigs = enumerate_signatures(p, m, q)
                if sigs:
                    sigs.sort()
                    distribution[f"{m},{q}"] = len(sigs)
                    payload = [{"m": m, "q": q, "e": e} for e in sigs]
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
    corridor_removed = 0
    pruned = []
    for row in p7_rows:
        if min(row["e"]) > 5:
            continue
        if row["m"] == 3 and row["q"] == 1:
            lengths = tuple(7 + e for e in row["e"])
            if lengths not in P7_CORRIDORS:
                corridor_removed += 1
                continue
        pruned.append(row)
    assert corridor_removed == 13 and len(pruned) == 300

    print(json.dumps({
        "status": "FIRST_FAILURE_INDEPENDENT_GREEN",
        "canonical_sha256": digest,
        "p5_signatures": totals[5],
        "p7_signatures": totals[7],
        "p7_short_atom_removed": len(short_removed),
        "p7_corridor_removed": corridor_removed,
        "p7_donor_pruned_signatures": len(pruned),
        "finite_geometry_replays": geometry,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
