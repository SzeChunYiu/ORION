from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from itertools import product
from math import isqrt

Vector = tuple[int, ...]
Matrix = tuple[tuple[int, ...], ...]


class InputError(ValueError):
    """The mathematical input is outside the declared finite-group schema."""


def _is_prime(value: int) -> bool:
    if value < 2:
        return False
    return all(value % divisor != 0 for divisor in range(2, isqrt(value) + 1))


@dataclass(frozen=True, slots=True)
class GroupSpec:
    p: int
    d: int

    def __post_init__(self) -> None:
        if isinstance(self.p, bool) or not isinstance(self.p, int) or not _is_prime(self.p):
            raise InputError("p must be a prime integer")
        if isinstance(self.d, bool) or not isinstance(self.d, int) or self.d < 1:
            raise InputError("d must be a positive integer")

    @property
    def order(self) -> int:
        return self.p**self.d

    @property
    def zero(self) -> Vector:
        return (0,) * self.d

    def validate_vector(self, vector: object) -> Vector:
        if not isinstance(vector, (list, tuple)) or len(vector) != self.d:
            raise InputError(f"vector must be an array of length {self.d}")
        if any(
            isinstance(x, bool) or not isinstance(x, int) or not 0 <= x < self.p for x in vector
        ):
            raise InputError(f"vector coordinates must be integers in [0,{self.p})")
        return tuple(vector)

    def validate_sequence(self, sequence: object) -> tuple[Vector, ...]:
        if not isinstance(sequence, (list, tuple)):
            raise InputError("sequence must be a list or tuple of vectors")
        return tuple(self.validate_vector(vector) for vector in sequence)

    def elements(self) -> Iterator[Vector]:
        yield from product(range(self.p), repeat=self.d)

    def encode(self, vector: object) -> int:
        valid = self.validate_vector(vector)
        encoded = 0
        for coordinate in valid:
            encoded = encoded * self.p + coordinate
        return encoded

    def decode(self, encoded: object) -> Vector:
        if (
            isinstance(encoded, bool)
            or not isinstance(encoded, int)
            or not 0 <= encoded < self.order
        ):
            raise InputError(f"encoding must be an integer in [0,{self.order})")
        coordinates = [0] * self.d
        remainder = encoded
        for index in range(self.d - 1, -1, -1):
            coordinates[index] = remainder % self.p
            remainder //= self.p
        return tuple(coordinates)

    def add(self, left: object, right: object) -> Vector:
        a = self.validate_vector(left)
        b = self.validate_vector(right)
        return tuple((x + y) % self.p for x, y in zip(a, b, strict=True))

    def sum_vectors(self, vectors: Iterable[object]) -> Vector:
        total = self.zero
        for vector in vectors:
            total = self.add(total, vector)
        return total

    def scalar_mul(self, scalar: int, vector: object) -> Vector:
        if isinstance(scalar, bool) or not isinstance(scalar, int):
            raise InputError("scalar must be an integer")
        valid = self.validate_vector(vector)
        return tuple((scalar * x) % self.p for x in valid)

    def matvec(self, matrix: object, vector: object) -> Vector:
        valid = self.validate_vector(vector)
        if not isinstance(matrix, tuple) or len(matrix) != self.d:
            raise InputError("matrix must be a tuple of d rows")
        rows: list[tuple[int, ...]] = []
        for row in matrix:
            if not isinstance(row, tuple) or len(row) != self.d:
                raise InputError("matrix must be square with tuple rows")
            if any(isinstance(x, bool) or not isinstance(x, int) for x in row):
                raise InputError("matrix entries must be integers")
            rows.append(row)
        return tuple(
            sum(entry * x for entry, x in zip(row, valid, strict=True)) % self.p for row in rows
        )

    def rank(self, vectors: Iterable[object]) -> int:
        rows = [list(self.validate_vector(vector)) for vector in vectors]
        if not rows:
            return 0
        rank = 0
        for column in range(self.d):
            pivot = next((r for r in range(rank, len(rows)) if rows[r][column] % self.p), None)
            if pivot is None:
                continue
            rows[rank], rows[pivot] = rows[pivot], rows[rank]
            inverse = pow(rows[rank][column] % self.p, -1, self.p)
            rows[rank] = [(entry * inverse) % self.p for entry in rows[rank]]
            for r in range(len(rows)):
                if r == rank:
                    continue
                factor = rows[r][column] % self.p
                if factor:
                    rows[r] = [
                        (entry - factor * pivot_entry) % self.p
                        for entry, pivot_entry in zip(rows[r], rows[rank], strict=True)
                    ]
            rank += 1
            if rank == len(rows):
                break
        return rank

    def coordinates_in_basis(self, vector: object, basis: Sequence[object]) -> tuple[int, ...]:
        valid = self.validate_vector(vector)
        basis_vectors = tuple(self.validate_vector(item) for item in basis)
        width = len(basis_vectors)
        if width == 0:
            if valid != self.zero:
                raise InputError("nonzero vector is not in the empty span")
            return ()
        if width > self.d or self.rank(basis_vectors) != width:
            raise InputError("basis must be linearly independent")
        equations = [
            [basis_vectors[column][row] for column in range(width)] + [valid[row]]
            for row in range(self.d)
        ]
        pivot_row = 0
        pivot_rows: list[int] = []
        for column in range(width):
            pivot = next(
                (r for r in range(pivot_row, self.d) if equations[r][column] % self.p), None
            )
            if pivot is None:
                raise InputError("basis unexpectedly lost rank")
            equations[pivot_row], equations[pivot] = equations[pivot], equations[pivot_row]
            inverse = pow(equations[pivot_row][column] % self.p, -1, self.p)
            equations[pivot_row] = [(entry * inverse) % self.p for entry in equations[pivot_row]]
            for r in range(self.d):
                if r == pivot_row:
                    continue
                factor = equations[r][column] % self.p
                if factor:
                    equations[r] = [
                        (entry - factor * pivot_entry) % self.p
                        for entry, pivot_entry in zip(
                            equations[r], equations[pivot_row], strict=True
                        )
                    ]
            pivot_rows.append(pivot_row)
            pivot_row += 1
        if any(
            all(row[c] % self.p == 0 for c in range(width)) and row[-1] % self.p
            for row in equations
        ):
            raise InputError("vector is outside the basis span")
        return tuple(equations[row][-1] % self.p for row in pivot_rows)
