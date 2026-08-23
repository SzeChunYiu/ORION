#!/usr/bin/env python3
"""Linear stage of the prospectively frozen X1-B k=4 bilinear min-rank test.

Protocol: X1B_K4_GLOBAL_BILINEAR_MINRANK_PROTOCOL.md

This stage reconstructs the six previously committed quotient obstruction
orbits, enumerates all disjoint zero-sum pairs, and row-reduces the affine
symmetric-matrix edge system over F_5. It does not attempt rank minimization on
consistent affine spaces.
"""
from __future__ import annotations

from hashlib import sha256
import json

PREFIX = "ORIONRG_X1B_K4_BILINEAR_LINEAR="
P = 5

ORBIT_SPECS = {
    "942777": [
        ((1, 1, 2), 1), ((1, 2, 1), 2), ((1, 2, 2), 2),
        ((2, 0, 1), 2), ((2, 0, 2), 2), ((2, 2, 0), 2), ((2, 2, 2), 2),
    ],
    "1470123": [
        ((1, 1, 2), 1), ((1, 2, 1), 2), ((1, 2, 2), 2),
        ((2, 0, 0), 2), ((2, 0, 1), 2), ((2, 2, 0), 2), ((2, 2, 2), 2),
    ],
    "130007745": [
        ((1, 1, 1), 1), ((1, 1, 2), 1), ((1, 2, 1), 1), ((1, 2, 2), 2),
        ((2, 0, 1), 2), ((2, 0, 2), 2), ((2, 1, 0), 2), ((2, 2, 0), 2),
    ],
    "130165209": [
        ((1, 1, 1), 1), ((1, 1, 2), 1), ((1, 2, 1), 2), ((1, 2, 2), 2),
        ((2, 0, 1), 2), ((2, 0, 2), 2), ((2, 1, 0), 1), ((2, 2, 0), 2),
    ],
    "942621": [
        ((0, 2, 2), 1), ((1, 1, 2), 2), ((1, 2, 0), 2), ((1, 2, 2), 2),
        ((2, 0, 0), 2), ((2, 1, 2), 2), ((2, 2, 0), 2),
    ],
    "938409": [
        ((0, 2, 2), 2), ((1, 1, 2), 2), ((1, 2, 1), 2), ((1, 2, 2), 2),
        ((2, 0, 0), 1), ((2, 0, 1), 2), ((2, 1, 0), 2),
    ],
}

VAR_INDEX = {}
_index = 0
for i in range(13):
    for j in range(i, 13):
        VAR_INDEX[(i, j)] = _index
        _index += 1
assert _index == 91


def positions(spec):
    out = []
    for value, multiplicity in spec:
        out.extend([value] * multiplicity)
    if len(out) != 13:
        raise AssertionError("orbit spec must expand to 13 positions")
    return tuple(out)


def zero_sum_masks(pos):
    masks = []
    for mask in range(1, 1 << 13):
        total = [0, 0, 0]
        for index, value in enumerate(pos):
            if (mask >> index) & 1:
                for coordinate in range(3):
                    total[coordinate] = (total[coordinate] + value[coordinate]) % 3
        if total == [0, 0, 0]:
            masks.append(mask)
    return tuple(masks)


def disjoint_edges(masks):
    edges = []
    for index, left in enumerate(masks):
        for right in masks[index + 1 :]:
            if left & right == 0:
                edges.append((left, right))
    return tuple(edges)


def edge_equation(left, right):
    row = [0] * 91
    for i in range(13):
        if not ((left >> i) & 1):
            continue
        for j in range(13):
            if not ((right >> j) & 1):
                continue
            key = (i, j) if i <= j else (j, i)
            row[VAR_INDEX[key]] = (row[VAR_INDEX[key]] + 1) % P
    return row


def rref_affine(rows):
    matrix = [[value % P for value in row] + [1] for row in rows]
    nvars = 91
    rank = 0
    pivots = []
    for column in range(nvars):
        pivot = next(
            (r for r in range(rank, len(matrix)) if matrix[r][column] % P),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inv = pow(matrix[rank][column] % P, -1, P)
        matrix[rank] = [(value * inv) % P for value in matrix[rank]]
        for r in range(len(matrix)):
            if r == rank or matrix[r][column] % P == 0:
                continue
            factor = matrix[r][column] % P
            matrix[r] = [
                (matrix[r][c] - factor * matrix[rank][c]) % P
                for c in range(nvars + 1)
            ]
        pivots.append(column)
        rank += 1

    inconsistent = any(
        all(row[c] == 0 for c in range(nvars)) and row[nvars] != 0
        for row in matrix
    )
    free = [column for column in range(nvars) if column not in pivots]

    particular = None
    basis = []
    if not inconsistent:
        particular = [0] * nvars
        for r, column in enumerate(pivots):
            particular[column] = matrix[r][nvars]
        for free_column in free:
            vector = [0] * nvars
            vector[free_column] = 1
            for r, pivot_column in enumerate(pivots):
                vector[pivot_column] = (-matrix[r][free_column]) % P
            basis.append(vector)

    return {
        "equation_rank": rank,
        "inconsistent": inconsistent,
        "affine_dimension": 0 if inconsistent else len(free),
        "particular": particular,
        "nullspace_basis": basis,
    }


def main():
    outcomes = []
    for code, spec in ORBIT_SPECS.items():
        pos = positions(spec)
        masks = zero_sum_masks(pos)
        edges = disjoint_edges(masks)
        linear = rref_affine([edge_equation(left, right) for left, right in edges])
        outcomes.append(
            {
                "canonical_code": code,
                "zero_sum_mask_count": len(masks),
                "disjoint_pair_edge_count": len(edges),
                **linear,
            }
        )

    summary_rows = [
        {
            "canonical_code": row["canonical_code"],
            "zero_sum_mask_count": row["zero_sum_mask_count"],
            "disjoint_pair_edge_count": row["disjoint_pair_edge_count"],
            "equation_rank": row["equation_rank"],
            "inconsistent": row["inconsistent"],
            "affine_dimension": row["affine_dimension"],
        }
        for row in outcomes
    ]
    digest = sha256(
        json.dumps(summary_rows, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    payload = {
        "schema": "ORION.RG.X1B.K4GlobalBilinearLinearStage.v1",
        "evidence_status": "PROSPECTIVE_FROZEN_PROTOCOL_EXECUTION",
        "symmetric_variable_count": 91,
        "orbit_outcomes": outcomes,
        "affine_inconsistent_orbit_count": sum(row["inconsistent"] for row in outcomes),
        "affine_consistent_orbit_count": sum(not row["inconsistent"] for row in outcomes),
        "summary_digest": digest,
        "rank_stage_complete": False,
        "c15_theorem_authority": False,
        "novelty_authority": False,
        "scientific_authority": False,
    }
    print(PREFIX + json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
