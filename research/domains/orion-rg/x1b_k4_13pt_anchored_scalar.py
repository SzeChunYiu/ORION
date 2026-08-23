#!/usr/bin/env python3
"""Prospectively frozen X1-B k=4 / 13-point anchored scalar verifier.

The governing protocol was committed before any outcome at
`X1B_K4_13PT_ANCHORED_SCALAR_PROTOCOL.md`.

This program enumerates full multiplicity vectors over nonzero F_3^3, quotients
completed candidates by the full GL(3,3) action, replays every zero-sum subset
on positions, keeps exactly the 13-position residuals with packing number 2,
and tests every pair-compatible anchor against the common-RHS F_5 system forced
by the committed local-scalarization theorem.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json

ZERO = (0, 0, 0)
ELS = tuple(
    (a, b, c)
    for a in range(3)
    for b in range(3)
    for c in range(3)
    if (a, b, c) != ZERO
)
INDEX = {v: i for i, v in enumerate(ELS)}
POW3 = tuple(3**i for i in range(len(ELS)))
OPPOSITE = tuple(INDEX[tuple((-x) % 3 for x in v)] for v in ELS)
PREFIX = "ORIONRG_X1B_K4_ANCHORED="


def det3(vals):
    a, b, c, d, e, f, g, h, i = vals
    return (
        a * (e * i - f * h)
        - b * (d * i - f * g)
        + c * (d * h - e * g)
    ) % 3


def mat_vec(vals, v):
    return tuple(
        sum(vals[3 * row + col] * v[col] for col in range(3)) % 3
        for row in range(3)
    )


def gl33_maps():
    maps = []
    for vals in product(range(3), repeat=9):
        if det3(vals) == 0:
            continue
        maps.append(tuple(INDEX[mat_vec(vals, v)] for v in ELS))
    if len(maps) != 11232:
        raise AssertionError(f"unexpected GL(3,3) size: {len(maps)}")
    return tuple(maps)


def support_addition_ok(candidate_index, support):
    if OPPOSITE[candidate_index] in support:
        return False
    v = ELS[candidate_index]
    for a, b in combinations(support, 2):
        if all((ELS[a][j] + ELS[b][j] + v[j]) % 3 == 0 for j in range(3)):
            return False
    return True


def encode_multiplicity(mult):
    return sum(mult[i] * POW3[i] for i in range(len(ELS)))


def orbit_codes(mult, maps):
    out = []
    for mp in maps:
        code = 0
        for i, multiplicity in enumerate(mult):
            if multiplicity:
                code += multiplicity * POW3[mp[i]]
        out.append(code)
    return out


def canonical_candidates(maps):
    seen = set()
    representatives = []
    mult = [0] * len(ELS)
    support = []
    raw_count = 0

    def rec(index, total):
        nonlocal raw_count
        remaining = len(ELS) - index
        if total > 13 or total + 2 * remaining < 13:
            return
        if index == len(ELS):
            if total != 13:
                return
            raw_count += 1
            code = encode_multiplicity(mult)
            if code in seen:
                return
            orbit = orbit_codes(mult, maps)
            seen.update(orbit)
            representatives.append((min(orbit), tuple(mult)))
            return

        rec(index + 1, total)
        if total < 13 and support_addition_ok(index, support):
            support.append(index)
            mult[index] = 1
            rec(index + 1, total + 1)
            if total + 2 <= 13:
                mult[index] = 2
                rec(index + 1, total + 2)
            mult[index] = 0
            support.pop()

    rec(0, 0)
    if len(seen) != raw_count:
        raise AssertionError(
            f"orbit coverage mismatch: seen={len(seen)} raw={raw_count}"
        )
    return raw_count, representatives


def expand_positions(mult):
    positions = []
    for i, multiplicity in enumerate(mult):
        positions.extend([i] * multiplicity)
    if len(positions) != 13:
        raise AssertionError("candidate does not have 13 positions")
    return tuple(positions)


def zero_sum_masks(mult):
    positions = expand_positions(mult)
    masks = []
    for mask in range(1, 1 << len(positions)):
        s0 = s1 = s2 = 0
        for position, element_index in enumerate(positions):
            if (mask >> position) & 1:
                x, y, z = ELS[element_index]
                s0 = (s0 + x) % 3
                s1 = (s1 + y) % 3
                s2 = (s2 + z) % 3
        if (s0, s1, s2) == ZERO:
            masks.append(mask)
    return tuple(masks)


def pair_compatible_anchors(masks):
    rows = []
    for anchor in masks:
        partners = tuple(
            other for other in masks if other != anchor and (other & anchor) == 0
        )
        if partners:
            rows.append((anchor, partners))
    return tuple(rows)


def has_three_disjoint(masks):
    for index, a in enumerate(masks):
        for b in masks[index + 1 :]:
            if a & b:
                continue
            used = a | b
            if any((c & used) == 0 for c in masks):
                return True
    return False


def complement_system(global_masks, anchor, total_positions=13):
    complement_positions = tuple(
        position
        for position in range(total_positions)
        if ((anchor >> position) & 1) == 0
    )
    local_masks = []
    for global_mask in global_masks:
        if global_mask & anchor:
            continue
        local = 0
        for local_index, position in enumerate(complement_positions):
            if (global_mask >> position) & 1:
                local |= 1 << local_index
        if local:
            local_masks.append(local)
    return complement_positions, tuple(local_masks)


def solve_common_rhs(local_masks, nvars):
    rows = [
        [int((mask >> position) & 1) for position in range(nvars)] + [1]
        for mask in local_masks
    ]
    rank = 0
    pivots = []
    for col in range(nvars):
        pivot = next(
            (row for row in range(rank, len(rows)) if rows[row][col] % 5),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col] % 5, -1, 5)
        rows[rank] = [(value * inv) % 5 for value in rows[rank]]
        for row in range(len(rows)):
            if row == rank or rows[row][col] % 5 == 0:
                continue
            factor = rows[row][col] % 5
            rows[row] = [
                (rows[row][j] - factor * rows[rank][j]) % 5
                for j in range(nvars + 1)
            ]
        pivots.append(col)
        rank += 1

    if any(
        all(row[col] % 5 == 0 for col in range(nvars)) and row[nvars] % 5 != 0
        for row in rows
    ):
        return None, rank

    solution = [0] * nvars
    for row, col in enumerate(pivots):
        solution[col] = rows[row][-1] % 5
    for mask in local_masks:
        if sum(
            solution[position]
            for position in range(nvars)
            if (mask >> position) & 1
        ) % 5 != 1:
            raise AssertionError("constructed affine witness failed replay")
    return solution, rank


def main():
    maps = gl33_maps()
    raw_count, representatives = canonical_candidates(maps)

    admitted = []
    support_histogram = Counter()
    compatible_anchor_histogram = Counter()
    closing_anchor_histogram = Counter()

    for canonical_code, mult in representatives:
        masks = zero_sum_masks(mult)
        if any(mask.bit_count() <= 3 for mask in masks):
            raise AssertionError("short-zero-sum generator mismatch")
        anchors = pair_compatible_anchors(masks)
        if not anchors:
            continue
        if has_three_disjoint(masks):
            continue

        closing = []
        anchor_rows = []
        for anchor, partners in anchors:
            complement_positions, local_masks = complement_system(masks, anchor)
            solution, rank = solve_common_rhs(local_masks, len(complement_positions))
            row = {
                "anchor_mask": anchor,
                "anchor_size": anchor.bit_count(),
                "partner_mask": partners[0],
                "partner_count": len(partners),
                "complement_positions": list(complement_positions),
                "local_zero_sum_masks": list(local_masks),
                "rank": rank,
                "consistent": solution is not None,
                "solution": solution,
            }
            anchor_rows.append(row)
            if solution is None:
                closing.append(row)

        support_size = sum(value > 0 for value in mult)
        support_histogram[support_size] += 1
        compatible_anchor_histogram[len(anchors)] += 1
        closing_anchor_histogram[len(closing)] += 1
        admitted.append(
            {
                "canonical_code": canonical_code,
                "multiplicity": list(mult),
                "positions": [list(ELS[i]) for i in expand_positions(mult)],
                "zero_sum_mask_count": len(masks),
                "pair_compatible_anchor_count": len(anchors),
                "closing_anchor_count": len(closing),
                "anchors": anchor_rows if not closing else [],
            }
        )

    obstructions = [row for row in admitted if row["closing_anchor_count"] == 0]
    admitted_codes = sorted(row["canonical_code"] for row in admitted)
    admitted_digest = sha256(
        json.dumps(admitted_codes, separators=(",", ":")).encode()
    ).hexdigest()

    payload = {
        "schema": "ORION.RG.X1B.K4AnchoredScalar.v1",
        "evidence_status": "PROSPECTIVE_FROZEN_PROTOCOL_EXECUTION",
        "gl33_size": len(maps),
        "raw_candidate_count": raw_count,
        "canonical_no_short_zero_sum_orbit_count": len(representatives),
        "packing_exactly_two_orbit_count": len(admitted),
        "support_size_histogram": {
            str(key): value for key, value in sorted(support_histogram.items())
        },
        "pair_compatible_anchor_count_histogram": {
            str(key): value
            for key, value in sorted(compatible_anchor_histogram.items())
        },
        "closing_anchor_count_histogram": {
            str(key): value for key, value in sorted(closing_anchor_histogram.items())
        },
        "zero_closing_anchor_orbit_count": len(obstructions),
        "admitted_canonical_code_digest": admitted_digest,
        "obstructions": obstructions,
        "finite_k4_residual_closed_by_one_functional_anchor": len(obstructions) == 0,
        "c15_theorem_authority": False,
        "novelty_authority": False,
        "scientific_authority": False,
    }
    print(PREFIX + json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
