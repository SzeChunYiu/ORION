"""Independent finite-field matrix-action symmetry for clean-room Engine B.

Engine A obtains canonical multisets by enumerating ordered support bases.  This
module deliberately uses a different representation: it fixes one span basis,
expresses the sequence in that coordinate system, enumerates ``GL(r, 5)`` as
literal matrices, and takes the least transformed coordinate multiset.

The implementation is intentionally bounded to rank at most two for the frozen
pre-census control prefix.  It is not the full C_5^3 census generator and must
not be used to claim orbit completeness for the target replay.
"""

from __future__ import annotations

import hashlib
from itertools import product
from typing import Iterable, Sequence

import engine_b as eb

Vector = tuple[int, int, int]
Matrix = tuple[tuple[int, ...], ...]


def _rank(vectors: Iterable[Sequence[int]]) -> int:
    rows = [list(vector) for vector in vectors if any(vector)]
    rank = 0
    for column in range(3):
        pivot = next((row for row in range(rank, len(rows)) if rows[row][column] % 5), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column] % 5, -1, 5)
        rows[rank] = [(entry * inverse) % 5 for entry in rows[rank]]
        for row in range(len(rows)):
            if row == rank:
                continue
            factor = rows[row][column] % 5
            if factor:
                rows[row] = [
                    (entry - factor * pivot_entry) % 5
                    for entry, pivot_entry in zip(rows[row], rows[rank], strict=True)
                ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def span_rank(sequence: Sequence[int]) -> int:
    return _rank(eb.decode_element(element) for element in sequence)


def _fixed_basis(vectors: tuple[Vector, ...]) -> tuple[Vector, ...]:
    basis: list[Vector] = []
    for vector in sorted(set(vectors)):
        if not any(vector):
            continue
        if _rank((*basis, vector)) > len(basis):
            basis.append(vector)
    return tuple(basis)


def _coordinates(vector: Vector, basis: tuple[Vector, ...]) -> tuple[int, ...]:
    for coefficients in product(range(5), repeat=len(basis)):
        candidate = tuple(
            sum(
                coefficient * basis_vector[index]
                for coefficient, basis_vector in zip(coefficients, basis, strict=True)
            )
            % 5
            for index in range(3)
        )
        if candidate == vector:
            return coefficients
    raise ValueError("sequence vector is outside its computed span basis")


def _matrix_rank(matrix: Matrix) -> int:
    padded = tuple(tuple(row) + (0,) * (3 - len(row)) for row in matrix)
    return _rank(padded)


def invertible_matrices(rank: int) -> tuple[Matrix, ...]:
    if type(rank) is not int or not 0 <= rank <= 2:
        raise ValueError("matrix-action control rank must be zero, one, or two")
    if rank == 0:
        return ((),)
    matrices = []
    for entries in product(range(5), repeat=rank * rank):
        matrix = tuple(tuple(entries[row * rank : (row + 1) * rank]) for row in range(rank))
        if _matrix_rank(matrix) == rank:
            matrices.append(matrix)
    return tuple(matrices)


def _matvec(matrix: Matrix, vector: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        sum(entry * coordinate for entry, coordinate in zip(row, vector, strict=True)) % 5
        for row in matrix
    )


def matrix_action_orbit(sequence: Sequence[int]) -> tuple[tuple[Vector, ...], ...]:
    values = tuple(eb._require_element(element) for element in sequence)
    vectors = tuple(eb.decode_element(element) for element in values)
    basis = _fixed_basis(vectors)
    rank = len(basis)
    if rank > 2:
        raise ValueError("rank-three matrix orbit is outside the frozen control prefix")
    coordinates = tuple(_coordinates(vector, basis) for vector in vectors)
    candidates: set[tuple[Vector, ...]] = set()
    for matrix in invertible_matrices(rank):
        transformed = []
        for coordinate in coordinates:
            image = _matvec(matrix, coordinate) if rank else ()
            transformed.append(tuple(image) + (0,) * (3 - rank))
        candidates.add(tuple(sorted(transformed)))
    return tuple(sorted(candidates))


def canonical_matrix_action(sequence: Sequence[int]) -> tuple[Vector, ...]:
    orbit = matrix_action_orbit(sequence)
    if not orbit:
        raise RuntimeError("matrix-action orbit unexpectedly empty")
    return orbit[0]


def representative_sha256(representative: Sequence[Sequence[int]]) -> str:
    return hashlib.sha256(
        eb.canonical_json_bytes([list(vector) for vector in representative])
    ).hexdigest()


def orbit_sha256(sequence: Sequence[int]) -> str:
    orbit = matrix_action_orbit(sequence)
    payload = [[list(vector) for vector in representative] for representative in orbit]
    return hashlib.sha256(eb.canonical_json_bytes(payload)).hexdigest()
