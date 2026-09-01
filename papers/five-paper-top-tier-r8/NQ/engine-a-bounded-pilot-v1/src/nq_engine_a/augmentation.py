from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from functools import cache
from itertools import permutations

from .canonical import canonical_multiset
from .factorization import FactorizationStatus, find_disjoint_zero_sums
from .group import GroupSpec, InputError, Vector


class AugmentationStatus(StrEnum):
    COMPLETE = "COMPLETE"
    CANNOT_CHECK_RESOURCE_BOUND = "CANNOT_CHECK_RESOURCE_BOUND"


class ConstraintDecision(StrEnum):
    ALLOW = "ALLOW"
    PRUNE_SHORT_ZERO_SUM = "PRUNE_SHORT_ZERO_SUM"
    PRUNE_K_DISJOINT = "PRUNE_K_DISJOINT"
    CANNOT_CHECK_RESOURCE_BOUND = "CANNOT_CHECK_RESOURCE_BOUND"


@dataclass(frozen=True, slots=True)
class ConstraintProfile:
    short_zero_sum_cutoff: int | None = None
    forbid_k_disjoint: int | None = None
    max_factor_states: int | None = None

    def __post_init__(self) -> None:
        for value, name in (
            (self.short_zero_sum_cutoff, "short_zero_sum_cutoff"),
            (self.forbid_k_disjoint, "forbid_k_disjoint"),
            (self.max_factor_states, "max_factor_states"),
        ):
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int) or value < 1
            ):
                raise InputError(f"{name} must be a positive integer or null")
        if self.forbid_k_disjoint is None and self.max_factor_states is not None:
            raise InputError("max_factor_states requires forbid_k_disjoint")


@dataclass(frozen=True, slots=True)
class AugmentationCoverage:
    status: AugmentationStatus
    target_length: int
    levels_completed: int
    parents_expanded: int
    extension_orbit_representatives: int
    candidate_edges: int
    canonical_parent_rejections: int
    duplicate_children_collapsed: int
    pruned_short_zero_sum: int
    pruned_k_disjoint: int

    @property
    def full_target_coverage(self) -> bool:
        return (
            self.status is AugmentationStatus.COMPLETE
            and self.levels_completed == self.target_length
        )

    def to_dict(self) -> dict[str, int | str | bool | list[str]]:
        return {
            "schema_version": "nq-engine-a-augmentation-coverage-v1",
            "status": self.status.value,
            "independence_terminal": "CANNOT_CHECK",
            "exposure_markers": [
                "EXPECTED_OUTCOME_EXPOSURE",
                "ENGINE_B_EXPOSURE_IN_PRIOR_CONTEXT__CANNOT_CHECK",
            ],
            "target_length": self.target_length,
            "levels_completed": self.levels_completed,
            "parents_expanded": self.parents_expanded,
            "extension_orbit_representatives": self.extension_orbit_representatives,
            "candidate_edges": self.candidate_edges,
            "canonical_parent_rejections": self.canonical_parent_rejections,
            "duplicate_children_collapsed": self.duplicate_children_collapsed,
            "pruned_short_zero_sum": self.pruned_short_zero_sum,
            "pruned_k_disjoint": self.pruned_k_disjoint,
            "full_target_coverage": self.full_target_coverage,
        }


@dataclass(frozen=True, slots=True)
class AugmentationRun:
    levels: tuple[tuple[tuple[Vector, ...], ...], ...]
    coverage: AugmentationCoverage

    @property
    def records(self) -> tuple[tuple[Vector, ...], ...]:
        if not self.coverage.full_target_coverage:
            raise RuntimeError("target level is partial and cannot be consumed as complete")
        return self.levels[self.coverage.target_length]


@cache
def _canonical_cached(spec: GroupSpec, sequence: tuple[Vector, ...]) -> tuple[Vector, ...]:
    return canonical_multiset(spec, sequence)


def canonical_parent(spec: GroupSpec, sequence: object) -> tuple[Vector, ...] | None:
    vectors = spec.validate_sequence(sequence)
    if not vectors:
        return None
    canonical = _canonical_cached(spec, tuple(vectors))
    return _canonical_cached(spec, canonical[:-1])


def _span_elements(spec: GroupSpec, rank: int) -> tuple[Vector, ...]:
    return tuple(
        vector for vector in spec.elements() if all(coordinate == 0 for coordinate in vector[rank:])
    )


def _linear_image_from_bases(
    spec: GroupSpec,
    vector: Vector,
    source_basis: tuple[Vector, ...],
    target_basis: tuple[Vector, ...],
) -> Vector:
    coordinates = spec.coordinates_in_basis(vector, source_basis)
    image = spec.zero
    for scalar, target in zip(coordinates, target_basis, strict=True):
        image = spec.add(image, spec.scalar_mul(scalar, target))
    return image


@cache
def _intrinsic_stabilizer_actions(
    spec: GroupSpec, parent: tuple[Vector, ...]
) -> tuple[tuple[Vector, ...], ...]:
    rank = spec.rank(parent)
    span_elements = _span_elements(spec, rank)
    if rank == 0:
        return (span_elements,)
    support = tuple(sorted(set(parent) - {spec.zero}))
    source_basis = next(basis for basis in permutations(support, rank) if spec.rank(basis) == rank)
    actions: set[tuple[Vector, ...]] = set()
    for target_basis in permutations(support, rank):
        if spec.rank(target_basis) != rank:
            continue
        mapped_parent = tuple(
            sorted(
                _linear_image_from_bases(spec, vector, source_basis, target_basis)
                for vector in parent
            )
        )
        if mapped_parent != parent:
            continue
        actions.add(
            tuple(
                _linear_image_from_bases(spec, vector, source_basis, target_basis)
                for vector in span_elements
            )
        )
    if not actions:
        raise RuntimeError("identity action missing from intrinsic stabilizer")
    return tuple(sorted(actions))


def extension_orbits(
    spec: GroupSpec, canonical_parent_record: object
) -> tuple[frozenset[Vector], ...]:
    parent = spec.validate_sequence(canonical_parent_record)
    if tuple(parent) != _canonical_cached(spec, tuple(parent)):
        raise InputError("extension orbits require a canonical parent")
    rank = spec.rank(parent)
    span_elements = _span_elements(spec, rank)
    actions = _intrinsic_stabilizer_actions(spec, tuple(parent))
    unseen = set(span_elements)
    orbits: list[frozenset[Vector]] = []
    positions = {vector: index for index, vector in enumerate(span_elements)}
    while unseen:
        seed = min(unseen)
        index = positions[seed]
        orbit = frozenset(action[index] for action in actions)
        orbits.append(orbit)
        unseen -= orbit
    if rank < spec.d:
        outside = frozenset(
            vector
            for vector in spec.elements()
            if any(coordinate != 0 for coordinate in vector[rank:])
        )
        orbits.append(outside)
    return tuple(sorted(orbits, key=min))


def extension_orbit_representatives(
    spec: GroupSpec, canonical_parent_record: object
) -> tuple[Vector, ...]:
    return tuple(min(orbit) for orbit in extension_orbits(spec, canonical_parent_record))


def has_short_zero_sum(spec: GroupSpec, sequence: object, cutoff: object) -> bool:
    vectors = spec.validate_sequence(sequence)
    if isinstance(cutoff, bool) or not isinstance(cutoff, int) or cutoff < 1:
        raise InputError("cutoff must be a positive integer")
    limit = min(cutoff, len(vectors))
    reachable: list[set[Vector]] = [set() for _ in range(limit + 1)]
    reachable[0].add(spec.zero)
    for vector in vectors:
        for weight in range(limit, 0, -1):
            reachable[weight].update(
                spec.add(partial_sum, vector) for partial_sum in reachable[weight - 1]
            )
            if spec.zero in reachable[weight]:
                return True
    return False


def evaluate_constraints(
    spec: GroupSpec, sequence: object, profile: ConstraintProfile
) -> ConstraintDecision:
    vectors = spec.validate_sequence(sequence)
    if profile.short_zero_sum_cutoff is not None and has_short_zero_sum(
        spec, vectors, profile.short_zero_sum_cutoff
    ):
        return ConstraintDecision.PRUNE_SHORT_ZERO_SUM
    if profile.forbid_k_disjoint is not None:
        result = find_disjoint_zero_sums(
            spec,
            vectors,
            profile.forbid_k_disjoint,
            max_states=profile.max_factor_states,
        )
        if result.status is FactorizationStatus.CANNOT_CHECK_RESOURCE_BOUND:
            return ConstraintDecision.CANNOT_CHECK_RESOURCE_BOUND
        if result.status is FactorizationStatus.POSITIVE:
            return ConstraintDecision.PRUNE_K_DISJOINT
    return ConstraintDecision.ALLOW


def _coverage(
    *,
    status: AugmentationStatus,
    target_length: int,
    levels_completed: int,
    counters: dict[str, int],
) -> AugmentationCoverage:
    return AugmentationCoverage(
        status=status,
        target_length=target_length,
        levels_completed=levels_completed,
        parents_expanded=counters["parents_expanded"],
        extension_orbit_representatives=counters["extension_orbit_representatives"],
        candidate_edges=counters["candidate_edges"],
        canonical_parent_rejections=counters["canonical_parent_rejections"],
        duplicate_children_collapsed=counters["duplicate_children_collapsed"],
        pruned_short_zero_sum=counters["pruned_short_zero_sum"],
        pruned_k_disjoint=counters["pruned_k_disjoint"],
    )


def generate_canonical_classes(
    spec: GroupSpec,
    target_length: object,
    *,
    profile: ConstraintProfile | None = None,
    max_candidate_edges: int | None = None,
) -> AugmentationRun:
    if isinstance(target_length, bool) or not isinstance(target_length, int) or target_length < 0:
        raise InputError("target_length must be a nonnegative integer")
    if max_candidate_edges is not None and (
        isinstance(max_candidate_edges, bool)
        or not isinstance(max_candidate_edges, int)
        or max_candidate_edges < 1
    ):
        raise InputError("max_candidate_edges must be a positive integer or null")
    constraints = ConstraintProfile() if profile is None else profile
    if not isinstance(constraints, ConstraintProfile):
        raise InputError("profile must be a ConstraintProfile")
    levels: list[tuple[tuple[Vector, ...], ...]] = [((),)]
    counters = {
        "parents_expanded": 0,
        "extension_orbit_representatives": 0,
        "candidate_edges": 0,
        "canonical_parent_rejections": 0,
        "duplicate_children_collapsed": 0,
        "pruned_short_zero_sum": 0,
        "pruned_k_disjoint": 0,
    }
    for next_length in range(1, target_length + 1):
        candidates: set[tuple[Vector, ...]] = set()
        for parent in levels[-1]:
            counters["parents_expanded"] += 1
            representatives = extension_orbit_representatives(spec, parent)
            counters["extension_orbit_representatives"] += len(representatives)
            for representative in representatives:
                if (
                    max_candidate_edges is not None
                    and counters["candidate_edges"] >= max_candidate_edges
                ):
                    coverage = _coverage(
                        status=AugmentationStatus.CANNOT_CHECK_RESOURCE_BOUND,
                        target_length=target_length,
                        levels_completed=next_length - 1,
                        counters=counters,
                    )
                    return AugmentationRun(tuple(levels), coverage)
                counters["candidate_edges"] += 1
                child = _canonical_cached(spec, (*parent, representative))
                if canonical_parent(spec, child) != parent:
                    counters["canonical_parent_rejections"] += 1
                    continue
                if child in candidates:
                    counters["duplicate_children_collapsed"] += 1
                candidates.add(child)
        accepted: list[tuple[Vector, ...]] = []
        for child in sorted(candidates):
            decision = evaluate_constraints(spec, child, constraints)
            if decision is ConstraintDecision.CANNOT_CHECK_RESOURCE_BOUND:
                coverage = _coverage(
                    status=AugmentationStatus.CANNOT_CHECK_RESOURCE_BOUND,
                    target_length=target_length,
                    levels_completed=next_length - 1,
                    counters=counters,
                )
                return AugmentationRun(tuple(levels), coverage)
            if decision is ConstraintDecision.PRUNE_SHORT_ZERO_SUM:
                counters["pruned_short_zero_sum"] += 1
                continue
            if decision is ConstraintDecision.PRUNE_K_DISJOINT:
                counters["pruned_k_disjoint"] += 1
                continue
            accepted.append(child)
        levels.append(tuple(accepted))
    coverage = _coverage(
        status=AugmentationStatus.COMPLETE,
        target_length=target_length,
        levels_completed=target_length,
        counters=counters,
    )
    return AugmentationRun(tuple(levels), coverage)
