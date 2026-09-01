from __future__ import annotations

from itertools import permutations

from .group import GroupSpec, Vector


def canonical_multiset(spec: GroupSpec, sequence: object) -> tuple[Vector, ...]:
    """Return the exact lexicographic representative under GL(d,p) and permutations.

    Ordered bases are chosen from the nonzero support. Every automorphism carries such
    bases bijectively, so the minimum coordinate multiset is orbit invariant.
    """

    vectors = spec.validate_sequence(sequence)
    if not vectors:
        return ()
    support = tuple(sorted(set(vectors) - {spec.zero}))
    rank = spec.rank(support)
    if rank == 0:
        return tuple(sorted(vectors))
    best: tuple[Vector, ...] | None = None
    for basis in permutations(support, rank):
        if spec.rank(basis) != rank:
            continue
        mapped: list[Vector] = []
        for vector in vectors:
            coordinates = spec.coordinates_in_basis(vector, basis)
            mapped.append(coordinates + (0,) * (spec.d - rank))
        candidate = tuple(sorted(mapped))
        if best is None or candidate < best:
            best = candidate
    if best is None:  # defensive: support always contains a basis of its span
        raise RuntimeError("failed to find a support basis")
    return best
