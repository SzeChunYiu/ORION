from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import permutations

from .group import GroupSpec, InputError, Vector

DECLARED_P = 5
DECLARED_D = 3
STANDARD_BASIS: tuple[Vector, Vector, Vector] = (
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
)


@dataclass(frozen=True, slots=True)
class NormalizationWitness:
    """A source-support basis whose coordinate image is donor-normalized."""

    basis: tuple[Vector, Vector, Vector]
    image: tuple[Vector, ...]


def _require_declared_group(spec: GroupSpec) -> None:
    if (spec.p, spec.d) != (DECLARED_P, DECLARED_D):
        raise InputError("the frozen donor normalization is defined only for C_5^3")


def is_declared_donor_normalized(spec: GroupSpec, sequence: object) -> bool:
    """Check the frozen pointwise orbit-slice predicate.

    The multiset must contain e1,e2,e3 and their multiplicities must satisfy
    m(e1) <= m(e2) <= m(e3). Sequence order is immaterial.
    """

    _require_declared_group(spec)
    vectors = spec.validate_sequence(sequence)
    multiplicities = Counter(vectors)
    if any(multiplicities[basis_vector] == 0 for basis_vector in STANDARD_BASIS):
        return False
    return (
        multiplicities[STANDARD_BASIS[0]]
        <= multiplicities[STANDARD_BASIS[1]]
        <= multiplicities[STANDARD_BASIS[2]]
    )


def declared_donor_normalization_witnesses(
    spec: GroupSpec, sequence: object
) -> tuple[NormalizationWitness, ...]:
    """Enumerate the complete donor-normalized slice of one GL orbit.

    For every ordered independent support triple with nondecreasing source
    multiplicities, map that triple to (e1,e2,e3), sort the resulting multiset,
    and deduplicate identical images produced by different bases.
    """

    _require_declared_group(spec)
    vectors = spec.validate_sequence(sequence)
    support = tuple(sorted(set(vectors) - {spec.zero}))
    if spec.rank(support) < DECLARED_D:
        return ()
    multiplicities = Counter(vectors)
    by_image: dict[tuple[Vector, ...], tuple[Vector, Vector, Vector]] = {}
    for raw_basis in permutations(support, DECLARED_D):
        basis = (raw_basis[0], raw_basis[1], raw_basis[2])
        if spec.rank(basis) != DECLARED_D:
            continue
        if not (multiplicities[basis[0]] <= multiplicities[basis[1]] <= multiplicities[basis[2]]):
            continue
        image = tuple(sorted(spec.coordinates_in_basis(vector, basis) for vector in vectors))
        previous = by_image.get(image)
        if previous is None or basis < previous:
            by_image[image] = basis
    return tuple(
        NormalizationWitness(basis=by_image[image], image=image) for image in sorted(by_image)
    )


def declared_donor_images(spec: GroupSpec, sequence: object) -> tuple[tuple[Vector, ...], ...]:
    return tuple(
        witness.image for witness in declared_donor_normalization_witnesses(spec, sequence)
    )


def verify_normalization_witness(spec: GroupSpec, sequence: object, witness: object) -> bool:
    try:
        _require_declared_group(spec)
        vectors = spec.validate_sequence(sequence)
        if not isinstance(witness, NormalizationWitness):
            return False
        if not isinstance(witness.basis, tuple) or len(witness.basis) != DECLARED_D:
            return False
        basis = tuple(spec.validate_vector(vector) for vector in witness.basis)
        if spec.rank(basis) != DECLARED_D:
            return False
        support = set(vectors) - {spec.zero}
        if any(vector not in support for vector in basis):
            return False
        multiplicities = Counter(vectors)
        if not (multiplicities[basis[0]] <= multiplicities[basis[1]] <= multiplicities[basis[2]]):
            return False
        image = spec.validate_sequence(witness.image)
        expected = tuple(sorted(spec.coordinates_in_basis(vector, basis) for vector in vectors))
        return image == expected and is_declared_donor_normalized(spec, image)
    except (InputError, TypeError, ValueError):
        return False
