"""Clean-room exact finite-panel audit primitives for FiberGuard R8.

This module was written from the mathematical protocol in the manuscript.  It
does not import the reference artifact.  The lane is nevertheless not blinded:
issue #1379 exposed frozen verdicts before the implementation was sealed.  All
outputs therefore retain an independence terminal of ``CANNOT_CHECK``.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


class TargetSolverDisagreement(RuntimeError):
    """Raised when the two primary exact target solvers disagree."""


class EndpointCheckerDisagreement(RuntimeError):
    """Raised when the small third endpoint checker disagrees."""


class ManifestMismatch(RuntimeError):
    """Raised when a bound source manifest no longer matches the filesystem."""


class PacketIdentityUnresolved(RuntimeError):
    """Raised when the R8 packet identity is still a placeholder."""


class PacketIdentityMismatch(RuntimeError):
    """Raised when a resolved packet identity is not bound to this checkout."""


class ExecutionAuthorizationMismatch(RuntimeError):
    """Raised when external root-review execution authority is absent or drifts."""


GRAPH_VERTICES = tuple(range(6))
GRAPH_EDGES = tuple(combinations(GRAPH_VERTICES, 2))
GRAPH_EDGE_INDEX = {edge: index for index, edge in enumerate(GRAPH_EDGES)}
VARIABLE_PAIRS = tuple(combinations(range(1, 5), 2))
SIGN_PATTERNS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
HEX_SHA1 = re.compile(r"[0-9a-f]{40}")
HEX_SHA256 = re.compile(r"[0-9a-f]{64}")
PACKET_PATH = Path("papers/five-paper-top-tier-r8/R8_PACKET_COMMIT.json")
PACKET_VALIDATOR_PATH = Path("papers/five-paper-top-tier-r8/harness/validate_r8_packet_binding.py")
PACKET_VALIDATOR_BYTES = 17030
PACKET_VALIDATOR_GIT_BLOB = "7696860dc4898e4ef101f9aa3ef7339835eb3c19"
PACKET_VALIDATOR_SHA256 = "fe27fc176553b1f06bd05808bb6ca0008c4ee6b74d6bf18265ccd97f688d5737"
PACKET_VALIDATION_FIELDS = {
    "schema",
    "terminal",
    "scientific_subject",
    "packet_publication",
    "predecessor_packet",
    "authority",
    "validated_at_checkout",
    "source_ref_status",
}
PACKET_AUTHORITY = {
    "identity_authority": "ENGINEERING_CUSTODY_ONLY",
    "scientific_disposition": "NONE",
    "paper_authority_delta": "NONE",
    "publication_readiness_delta": "NONE",
    "external_novelty": "CANNOT_CHECK",
    "grants_execution_authority": False,
    "grants_lunarc_submission": False,
}
SPARSE_CHECKOUT_PATHS = ("papers/five-paper-top-tier-r8",)
SPARSE_REQUIRED_FILES = (
    PACKET_PATH,
    Path("papers/five-paper-top-tier-r8/R8_PACKET_PUBLICATION_BINDING.json"),
    Path("papers/five-paper-top-tier-r8/R8_PACKET_COMMIT_V1_PRESERVED.json"),
    PACKET_VALIDATOR_PATH,
)


def _edge_bit(left: int, right: int) -> int:
    edge = (left, right) if left < right else (right, left)
    return 1 << GRAPH_EDGE_INDEX[edge]


def _graph_adjacency(edge_mask: int) -> tuple[int, ...]:
    if type(edge_mask) is not int or not 0 <= edge_mask < 1 << len(GRAPH_EDGES):
        raise ValueError("graph edge mask is outside the six-vertex domain")
    adjacency = [0] * 6
    for index, (left, right) in enumerate(GRAPH_EDGES):
        if edge_mask & (1 << index):
            adjacency[left] |= 1 << right
            adjacency[right] |= 1 << left
    return tuple(adjacency)


@lru_cache(maxsize=1)
def graph_masks() -> tuple[int, ...]:
    """Return the complete labeled six-vertex simple-graph domain."""

    return tuple(range(1 << len(GRAPH_EDGES)))


def graph_representation(edge_mask: int) -> tuple[tuple[int, ...], int]:
    adjacency = _graph_adjacency(edge_mask)
    degrees = tuple(sorted(neighbors.bit_count() for neighbors in adjacency))
    triangles = 0
    for first, second, third in combinations(GRAPH_VERTICES, 3):
        required = _edge_bit(first, second) | _edge_bit(first, third) | _edge_bit(second, third)
        triangles += (edge_mask & required) == required
    return degrees, triangles


def graph_chromatic_by_coloring(edge_mask: int) -> int:
    """Exact chromatic number by increasing-palette assignment search."""

    adjacency = _graph_adjacency(edge_mask)
    order = tuple(sorted(GRAPH_VERTICES, key=lambda v: (-adjacency[v].bit_count(), v)))

    def colorable(palette_size: int) -> bool:
        colors = [-1] * 6

        def assign(position: int) -> bool:
            if position == 6:
                return True
            vertex = order[position]
            forbidden = {
                colors[neighbor]
                for neighbor in GRAPH_VERTICES
                if adjacency[vertex] & (1 << neighbor) and colors[neighbor] >= 0
            }
            for color in range(palette_size):
                if color not in forbidden:
                    colors[vertex] = color
                    if assign(position + 1):
                        return True
                    colors[vertex] = -1
            return False

        return assign(0)

    for palette_size in range(1, 7):
        if colorable(palette_size):
            return palette_size
    raise AssertionError("six vertices are always six-colourable")


def graph_chromatic_by_independent_cover(edge_mask: int) -> int:
    """Exact chromatic number as a minimum independent-set cover."""

    adjacency = _graph_adjacency(edge_mask)
    independent: list[int] = []
    for subset in range(1, 1 << 6):
        if all(not (adjacency[v] & subset) for v in GRAPH_VERTICES if subset & (1 << v)):
            independent.append(subset)
    containing = {
        vertex: tuple(subset for subset in independent if subset & (1 << vertex))
        for vertex in GRAPH_VERTICES
    }

    @lru_cache(maxsize=None)
    def cover(uncovered: int) -> int:
        if not uncovered:
            return 0
        first = (uncovered & -uncovered).bit_length() - 1
        return 1 + min(cover(uncovered & ~subset) for subset in containing[first])

    return cover((1 << 6) - 1)


def _graph_clique_number(adjacency: tuple[int, ...]) -> int:
    for size in range(6, 0, -1):
        for vertices in combinations(GRAPH_VERTICES, size):
            if all(adjacency[a] & (1 << b) for a, b in combinations(vertices, 2)):
                return size
    raise AssertionError("a nonempty graph has a singleton clique")


def _graph_component_count(adjacency: tuple[int, ...]) -> int:
    unseen = (1 << 6) - 1
    count = 0
    while unseen:
        count += 1
        frontier = unseen & -unseen
        unseen &= ~frontier
        while frontier:
            vertex_bit = frontier & -frontier
            frontier &= ~vertex_bit
            vertex = vertex_bit.bit_length() - 1
            reached = adjacency[vertex] & unseen
            unseen &= ~reached
            frontier |= reached
    return count


def _graph_four_cycle_count(edge_mask: int) -> int:
    count = 0
    for a, b, c, d in combinations(GRAPH_VERTICES, 4):
        cycles = (
            ((a, b), (b, c), (c, d), (d, a)),
            ((a, b), (b, d), (d, c), (c, a)),
            ((a, c), (c, b), (b, d), (d, a)),
        )
        for edges in cycles:
            required = 0
            for left, right in edges:
                required |= _edge_bit(left, right)
            count += (edge_mask & required) == required
    return count


def graph_refinements(edge_mask: int) -> dict[str, int]:
    adjacency = _graph_adjacency(edge_mask)
    return {
        "clique_number": _graph_clique_number(adjacency),
        "component_count": _graph_component_count(adjacency),
        "four_cycle_count": _graph_four_cycle_count(edge_mask),
    }


def graph_endpoint_check(edge_mask: int) -> dict[str, object]:
    """Small third checker, intentionally independent of the primary helpers."""

    matrix = [[False] * 6 for _ in range(6)]
    cursor = 0
    for left in range(6):
        for right in range(left + 1, 6):
            present = bool(edge_mask & (1 << cursor))
            matrix[left][right] = matrix[right][left] = present
            cursor += 1
    degrees = tuple(sorted(sum(row) for row in matrix))
    triangles = sum(
        matrix[a][b] and matrix[a][c] and matrix[b][c] for a, b, c in combinations(range(6), 3)
    )
    target = None
    for palette in range(1, 7):
        if any(
            all(colors[a] != colors[b] for a, b in combinations(range(6), 2) if matrix[a][b])
            for colors in product(range(palette), repeat=6)
        ):
            target = palette
            break
    if target is None:
        raise AssertionError("endpoint graph has no coloring")
    return {"representation": (degrees, triangles), "target": target}


@lru_cache(maxsize=1)
def cover_families() -> tuple[tuple[int, ...], ...]:
    """Return all five-set families of nonempty subsets covering five elements."""

    universe = (1 << 5) - 1
    return tuple(
        family
        for family in combinations(range(1, universe + 1), 5)
        if family[0] | family[1] | family[2] | family[3] | family[4] == universe
    )


def _require_cover_family(family: Sequence[int]) -> tuple[int, ...]:
    value = tuple(family)
    if len(value) != 5 or value != tuple(sorted(value)) or len(set(value)) != 5:
        raise ValueError("cover family must contain five distinct canonical masks")
    if any(type(mask) is not int or not 1 <= mask < 1 << 5 for mask in value):
        raise ValueError("cover family contains an invalid nonempty set mask")
    if value[0] | value[1] | value[2] | value[3] | value[4] != (1 << 5) - 1:
        raise ValueError("cover family does not cover the universe")
    return value


def cover_representation(family: Sequence[int]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    value = _require_cover_family(family)
    sizes = tuple(sorted(mask.bit_count() for mask in value))
    intersections = tuple(
        sorted((left & right).bit_count() for left, right in combinations(value, 2))
    )
    return sizes, intersections


def cover_size_by_subset_search(family: Sequence[int]) -> int:
    value = _require_cover_family(family)
    universe = (1 << 5) - 1
    for size in range(1, 6):
        for selected in combinations(value, size):
            union = 0
            for mask in selected:
                union |= mask
            if union == universe:
                return size
    raise AssertionError("declared family covers the universe")


def cover_size_by_mask_dp(family: Sequence[int]) -> int:
    value = _require_cover_family(family)
    infinity = 6
    costs = [infinity] * (1 << 5)
    costs[0] = 0
    for mask in value:
        updated = costs.copy()
        for covered, cost in enumerate(costs):
            updated[covered | mask] = min(updated[covered | mask], cost + 1)
        costs = updated
    result = costs[(1 << 5) - 1]
    if result == infinity:
        raise AssertionError("declared family covers the universe")
    return result


def cover_refinements(family: Sequence[int]) -> dict[str, tuple[int, ...]]:
    value = _require_cover_family(family)
    frequencies = tuple(
        sorted(sum(bool(mask & (1 << element)) for mask in value) for element in range(5))
    )
    unions = tuple(sorted((left | right).bit_count() for left, right in combinations(value, 2)))
    triples = tuple(sorted((a & b & c).bit_count() for a, b, c in combinations(value, 3)))
    return {
        "element_frequency_multiset": frequencies,
        "pairwise_union_multiset": unions,
        "triple_intersection_multiset": triples,
    }


def cover_endpoint_check(family: Sequence[int]) -> dict[str, object]:
    """Third checker by direct Boolean selection-table enumeration."""

    value = tuple(family)
    sizes = tuple(sorted(bin(mask).count("1") for mask in value))
    intersections = tuple(
        sorted(bin(value[i] & value[j]).count("1") for i in range(5) for j in range(i + 1, 5))
    )
    target = min(
        sum(choice)
        for choice in product((0, 1), repeat=5)
        if any(choice) and _selected_union(value, choice) == 31
    )
    return {"representation": (sizes, intersections), "target": target}


def _selected_union(family: Sequence[int], choices: Sequence[int]) -> int:
    union = 0
    for mask, selected in zip(family, choices, strict=True):
        if selected:
            union |= mask
    return union


@lru_cache(maxsize=1)
def binary_clauses() -> tuple[tuple[int, int], ...]:
    clauses = []
    for left, right in VARIABLE_PAIRS:
        for left_sign, right_sign in SIGN_PATTERNS:
            clauses.append((left_sign * left, right_sign * right))
    return tuple(clauses)


@lru_cache(maxsize=1)
def cnf_formulas() -> tuple[tuple[tuple[int, int], ...], ...]:
    return tuple(combinations(binary_clauses(), 5))


def _require_formula(formula: Sequence[Sequence[int]]) -> tuple[tuple[int, int], ...]:
    value = tuple(tuple(clause) for clause in formula)
    universe = binary_clauses()
    order = {clause: index for index, clause in enumerate(universe)}
    if len(value) != 5 or len(set(value)) != 5 or any(clause not in order for clause in value):
        raise ValueError("2-CNF formula must contain five distinct declared clauses")
    if tuple(sorted(value, key=order.__getitem__)) != value:
        raise ValueError("2-CNF clauses are not in canonical order")
    return value


def cnf_representation(
    formula: Sequence[Sequence[int]],
) -> tuple[tuple[tuple[int, int], ...], tuple[int, ...]]:
    value = _require_formula(formula)
    occurrences = []
    for variable in range(1, 5):
        positive = sum(literal == variable for clause in value for literal in clause)
        negative = sum(literal == -variable for clause in value for literal in clause)
        occurrences.append((positive, negative))
    pair_counts = tuple(
        sum({abs(a), abs(b)} == {left, right} for a, b in value) for left, right in VARIABLE_PAIRS
    )
    return tuple(occurrences), pair_counts


def _literal_true(literal: int, assignment: int) -> bool:
    truth = bool(assignment & (1 << (abs(literal) - 1)))
    return truth if literal > 0 else not truth


def cnf_count_by_truth_table(formula: Sequence[Sequence[int]]) -> int:
    value = _require_formula(formula)
    return sum(
        all(_literal_true(a, assignment) or _literal_true(b, assignment) for a, b in value)
        for assignment in range(1 << 4)
    )


def cnf_count_by_clause_recursion(formula: Sequence[Sequence[int]]) -> int:
    """Exact model count by memoized residual-clause recursion."""

    initial = _require_formula(formula)

    @lru_cache(maxsize=None)
    def count(variable: int, residual: tuple[tuple[int, int], ...]) -> int:
        if not residual:
            return 1 << (5 - variable)
        if variable == 5:
            return 0
        total = 0
        for truth in (False, True):
            next_residual: list[tuple[int, int]] = []
            impossible = False
            for clause in residual:
                literals_here = [literal for literal in clause if abs(literal) == variable]
                satisfied = any((truth if literal > 0 else not truth) for literal in literals_here)
                if satisfied:
                    continue
                if all(abs(literal) <= variable for literal in clause):
                    impossible = True
                    break
                next_residual.append(clause)
            if not impossible:
                total += count(variable + 1, tuple(next_residual))
        return total

    return count(1, initial)


def _signed_pair_profiles(formula: tuple[tuple[int, int], ...]) -> tuple[tuple[int, ...], ...]:
    profiles = []
    for left, right in VARIABLE_PAIRS:
        counts = []
        for left_sign, right_sign in SIGN_PATTERNS:
            expected = (left_sign * left, right_sign * right)
            counts.append(sum(clause == expected for clause in formula))
        profiles.append(tuple(counts))
    return tuple(profiles)


def cnf_refinements(formula: Sequence[Sequence[int]]) -> dict[str, object]:
    value = _require_formula(formula)
    sign_type_counts = tuple(
        sum(sum(literal > 0 for literal in clause) == positives for clause in value)
        for positives in range(3)
    )
    profiles = _signed_pair_profiles(value)
    return {
        "global_clause_sign_type_counts": sign_type_counts,
        "unlabeled_signed_pair_profiles": tuple(sorted(profiles)),
        "labeled_signed_pair_profile": profiles,
    }


def cnf_endpoint_check(formula: Sequence[Sequence[int]]) -> dict[str, object]:
    """Third checker using a direct assignment table and direct counters."""

    value = tuple(tuple(clause) for clause in formula)
    occurrences = tuple(
        (
            sum(literal == variable for clause in value for literal in clause),
            sum(literal == -variable for clause in value for literal in clause),
        )
        for variable in range(1, 5)
    )
    pair_counts = tuple(
        sum(tuple(sorted((abs(a), abs(b)))) == pair for a, b in value) for pair in VARIABLE_PAIRS
    )
    target = 0
    for bits in product((False, True), repeat=4):
        satisfied = True
        for first, second in value:
            first_value = bits[abs(first) - 1]
            second_value = bits[abs(second) - 1]
            first_value = first_value if first > 0 else not first_value
            second_value = second_value if second > 0 else not second_value
            if not (first_value or second_value):
                satisfied = False
                break
        target += satisfied
    return {"representation": (occurrences, pair_counts), "target": target}


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _jsonable(item)
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if type(value) is float:
        if not math.isfinite(value):
            raise TypeError("non-finite floats are not canonical-JSON compatible")
        return value
    if value is None or type(value) in {str, int, bool}:
        return value
    raise TypeError(f"value is not canonical-JSON compatible: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _freeze(value: Any) -> Any:
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, dict):
        return tuple(
            (str(key), _freeze(item))
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        )
    if value is None or type(value) in {str, int, bool}:
        return value
    raise TypeError(f"value is not fibre-key compatible: {type(value).__name__}")


@dataclass
class _FibreState:
    count: int
    minimum: int
    maximum: int
    low_serialized: Any
    high_serialized: Any
    low_instance: Any
    high_instance: Any


def _update_fibre(
    fibres: dict[Any, _FibreState],
    key: Any,
    target: int,
    serialized: Any,
    instance: Any,
) -> None:
    existing = fibres.get(key)
    if existing is None:
        fibres[key] = _FibreState(1, target, target, serialized, serialized, instance, instance)
        return
    existing.count += 1
    serialized_bytes = canonical_json_bytes(serialized)
    if target < existing.minimum or (
        target == existing.minimum
        and serialized_bytes < canonical_json_bytes(existing.low_serialized)
    ):
        existing.minimum = target
        existing.low_serialized = serialized
        existing.low_instance = instance
    if target > existing.maximum or (
        target == existing.maximum
        and serialized_bytes < canonical_json_bytes(existing.high_serialized)
    ):
        existing.maximum = target
        existing.high_serialized = serialized
        existing.high_instance = instance


def _summarize_refinement(fibres: Mapping[Any, _FibreState]) -> dict[str, int]:
    diameters = [state.maximum - state.minimum for state in fibres.values()]
    return {
        "fibre_count": len(fibres),
        "ambiguous_fibre_count": sum(diameter > 0 for diameter in diameters),
        "maximum_target_diameter": max(diameters, default=0),
    }


def audit_records(
    *,
    instances: Iterable[Any],
    representation: Callable[[Any], Any],
    target_solvers: tuple[Callable[[Any], int], Callable[[Any], int]],
    candidates: Mapping[str, Callable[[Any], Any]],
    serialize_instance: Callable[[Any], Any],
    endpoint_checker: Callable[[Any], Mapping[str, Any]],
) -> dict[str, Any]:
    """Exhaust a finite panel, compare dual targets, and summarize fibres."""

    primary: dict[Any, _FibreState] = {}
    refined = {name: {} for name in sorted(candidates)}
    seen: set[bytes] = set()
    instance_count = 0
    for instance in instances:
        serialized = _jsonable(serialize_instance(instance))
        identity = canonical_json_bytes(serialized)
        if identity in seen:
            raise ValueError("duplicate instance in declared finite domain")
        seen.add(identity)
        first = target_solvers[0](instance)
        second = target_solvers[1](instance)
        if type(first) is not int or type(second) is not int:
            raise TypeError("target solvers must return exact integer values")
        if first < 0 or second < 0:
            raise ValueError("target solvers must return nonnegative values")
        if first != second:
            raise TargetSolverDisagreement(
                f"target solvers disagree for {serialized!r}: {first} != {second}"
            )
        rep = representation(instance)
        frozen_rep = _freeze(rep)
        _update_fibre(primary, frozen_rep, first, serialized, instance)
        for name in sorted(candidates):
            feature = candidates[name](instance)
            _update_fibre(
                refined[name],
                (frozen_rep, _freeze(feature)),
                first,
                serialized,
                instance,
            )
        instance_count += 1
    if not primary:
        raise ValueError("declared finite domain is empty")

    maximum_diameter = max(state.maximum - state.minimum for state in primary.values())
    endpoint_key, endpoint_state = min(
        (
            (key, state)
            for key, state in primary.items()
            if state.maximum - state.minimum == maximum_diameter
        ),
        key=lambda item: (-item[1].count, canonical_json_bytes(_jsonable(item[0]))),
    )
    for endpoint_instance, expected_target in (
        (endpoint_state.low_instance, endpoint_state.minimum),
        (endpoint_state.high_instance, endpoint_state.maximum),
    ):
        check = endpoint_checker(endpoint_instance)
        if (
            _freeze(check.get("representation")) != endpoint_key
            or check.get("target") != expected_target
        ):
            raise EndpointCheckerDisagreement(
                "endpoint checker disagrees with the primary fibre or target"
            )

    summary = _summarize_refinement(primary)
    return {
        "instance_count": instance_count,
        "representation_fibre_count": summary["fibre_count"],
        "ambiguous_fibre_count": summary["ambiguous_fibre_count"],
        "maximum_target_diameter": summary["maximum_target_diameter"],
        "selected_endpoint_fibre": {
            "representation": _jsonable(endpoint_key),
            "fibre_multiplicity": endpoint_state.count,
            "low_target": endpoint_state.minimum,
            "high_target": endpoint_state.maximum,
            "low_witness": endpoint_state.low_serialized,
            "high_witness": endpoint_state.high_serialized,
        },
        "candidate_refinements": {
            name: _summarize_refinement(refined[name]) for name in sorted(refined)
        },
    }


def _select_refinement(
    refiner: Callable[[Any], Mapping[str, Any]], name: str
) -> Callable[[Any], Any]:
    def selected(instance: Any) -> Any:
        return refiner(instance)[name]

    return selected


def _audit_graph_panel() -> dict[str, Any]:
    return audit_records(
        instances=graph_masks(),
        representation=graph_representation,
        target_solvers=(graph_chromatic_by_coloring, graph_chromatic_by_independent_cover),
        candidates={
            name: _select_refinement(graph_refinements, name)
            for name in ("clique_number", "component_count", "four_cycle_count")
        },
        serialize_instance=lambda mask: mask,
        endpoint_checker=graph_endpoint_check,
    )


def _audit_cover_panel() -> dict[str, Any]:
    return audit_records(
        instances=cover_families(),
        representation=cover_representation,
        target_solvers=(cover_size_by_subset_search, cover_size_by_mask_dp),
        candidates={
            name: _select_refinement(cover_refinements, name)
            for name in (
                "element_frequency_multiset",
                "pairwise_union_multiset",
                "triple_intersection_multiset",
            )
        },
        serialize_instance=list,
        endpoint_checker=cover_endpoint_check,
    )


def _audit_cnf_panel() -> dict[str, Any]:
    return audit_records(
        instances=cnf_formulas(),
        representation=cnf_representation,
        target_solvers=(cnf_count_by_truth_table, cnf_count_by_clause_recursion),
        candidates={
            name: _select_refinement(cnf_refinements, name)
            for name in (
                "global_clause_sign_type_counts",
                "labeled_signed_pair_profile",
                "unlabeled_signed_pair_profiles",
            )
        },
        serialize_instance=lambda formula: [list(clause) for clause in formula],
        endpoint_checker=cnf_endpoint_check,
    )


DOMAIN_RUNNERS = {
    "graphs": _audit_graph_panel,
    "set_cover": _audit_cover_panel,
    "two_cnf": _audit_cnf_panel,
}


def _run_named_domain(name: str) -> tuple[str, dict[str, Any]]:
    return name, DOMAIN_RUNNERS[name]()


def execute_all_panels(*, workers: int = 1) -> dict[str, Any]:
    if type(workers) is not int or not 1 <= workers <= 16:
        raise ValueError("workers must be an integer from one through sixteen")
    names = tuple(sorted(DOMAIN_RUNNERS))
    if workers == 1:
        panels = dict(_run_named_domain(name) for name in names)
    else:
        with ProcessPoolExecutor(max_workers=min(workers, len(names))) as executor:
            panels = dict(executor.map(_run_named_domain, names))
    return {
        "schema": "ORION.FiberGuardCleanroomOutput.v1",
        "panels": {name: panels[name] for name in names},
        "execution_terminal": "CLEANROOM_EXHAUSTIVE_REPLAY_COMPLETED",
        "independence_terminal": "CANNOT_CHECK",
        "blinding_breach": "BLINDING_BREACH_ISSUE_BODY",
        "comparison_to_frozen_outcomes": "NOT_PERFORMED",
        "scientific_authority_delta": "NONE",
    }


def expected_domain_counts() -> dict[str, int]:
    return {
        "graphs": 1 << len(GRAPH_EDGES),
        "set_cover": len(cover_families()),
        "two_cnf": len(cnf_formulas()),
    }


def validate_non_outcome_fixtures() -> dict[str, Any]:
    triangle = sum(1 << GRAPH_EDGE_INDEX[edge] for edge in ((0, 1), (0, 2), (1, 2)))
    singleton_cover = (1, 2, 4, 8, 16)
    contradictory_formula = ((1, 2), (1, -2), (-1, 2), (-1, -2), (3, 4))
    checks = {
        "graph_dual_solver_fixture": graph_chromatic_by_coloring(triangle)
        == graph_chromatic_by_independent_cover(triangle)
        == graph_endpoint_check(triangle)["target"],
        "set_cover_dual_solver_fixture": cover_size_by_subset_search(singleton_cover)
        == cover_size_by_mask_dp(singleton_cover)
        == cover_endpoint_check(singleton_cover)["target"],
        "two_cnf_dual_solver_fixture": cnf_count_by_truth_table(contradictory_formula)
        == cnf_count_by_clause_recursion(contradictory_formula)
        == cnf_endpoint_check(contradictory_formula)["target"],
    }
    if not all(checks.values()):
        raise TargetSolverDisagreement("a non-outcome fixture checker disagrees")
    return {
        "schema": "ORION.FiberGuardCleanroomNonOutcomeValidation.v1",
        "terminal": "NON_OUTCOME_FIXTURES_VALIDATED",
        "independence_terminal": "CANNOT_CHECK",
        "blinding_breach": "BLINDING_BREACH_ISSUE_BODY",
        "checks": checks,
        "full_panel_execution": "NOT_RUN",
        "comparison_to_frozen_outcomes": "NOT_PERFORMED",
        "lunarc_submission": "NOT_SUBMITTED",
        "scientific_authority_delta": "NONE",
    }


def seal_payload(payload: Mapping[str, Any], *, manifest_sha256: str) -> dict[str, Any]:
    if not HEX_SHA256.fullmatch(manifest_sha256):
        raise ValueError("manifest_sha256 must be a lowercase SHA-256 digest")
    canonical_payload = _jsonable(dict(payload))
    return {
        "schema": "ORION.FiberGuardCleanroomSealedPayload.v1",
        "payload": canonical_payload,
        "binding": {
            "payload_sha256": hashlib.sha256(canonical_json_bytes(canonical_payload)).hexdigest(),
            "manifest_sha256": manifest_sha256,
        },
        "authority": {
            "independence_terminal": "CANNOT_CHECK",
            "comparison_to_frozen_outcomes": "NOT_PERFORMED",
            "scientific_authority_delta": "NONE",
        },
    }


def verify_sealed_payload(sealed: Mapping[str, Any]) -> bool:
    try:
        if sealed.get("schema") != "ORION.FiberGuardCleanroomSealedPayload.v1":
            return False
        binding = sealed["binding"]
        expected = hashlib.sha256(canonical_json_bytes(sealed["payload"])).hexdigest()
        return (
            binding["payload_sha256"] == expected
            and bool(HEX_SHA256.fullmatch(binding["manifest_sha256"]))
            and sealed["authority"]["independence_terminal"] == "CANNOT_CHECK"
        )
    except (KeyError, TypeError, ValueError):
        return False


def _manifest_core(files: list[dict[str, Any]]) -> dict[str, Any]:
    return {"schema": "ORION.FiberGuardCleanroomManifest.v1", "files": files}


def build_manifest(root: Path, paths: Sequence[str]) -> dict[str, Any]:
    root = root.resolve()
    normalized = sorted(set(paths))
    if len(normalized) != len(paths):
        raise ValueError("manifest paths must be unique")
    files = []
    for relative in normalized:
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != relative:
            raise ValueError(f"manifest path is not canonical: {relative}")
        source = root / path
        if source.is_symlink():
            raise ValueError(f"manifest source must not be a symlink: {relative}")
        data = source.read_bytes()
        files.append(
            {
                "path": relative,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    core = _manifest_core(files)
    return {**core, "manifest_sha256": hashlib.sha256(canonical_json_bytes(core)).hexdigest()}


def verify_manifest(
    root: Path,
    manifest: Mapping[str, Any],
    *,
    required_paths: Sequence[str] | None = None,
) -> None:
    if manifest.get("schema") != "ORION.FiberGuardCleanroomManifest.v1":
        raise ManifestMismatch("manifest schema mismatch")
    files = manifest.get("files")
    if type(files) is not list:
        raise ManifestMismatch("manifest file list is missing")
    if any(
        type(record) is not dict or set(record) != {"bytes", "path", "sha256"} for record in files
    ):
        raise ManifestMismatch("manifest record shape is not exact")
    paths = [record["path"] for record in files]
    if paths != sorted(paths):
        raise ManifestMismatch("manifest paths are not sorted")
    if len(paths) != len(set(paths)):
        raise ManifestMismatch("manifest paths are not unique")
    if required_paths is not None:
        exact_required = tuple(sorted(required_paths))
        if len(exact_required) != len(set(exact_required)):
            raise ManifestMismatch("exact required allowlist is not unique")
        if tuple(paths) != exact_required:
            raise ManifestMismatch("manifest does not match the exact required allowlist")
    expected_core = _manifest_core(files)
    expected_digest = hashlib.sha256(canonical_json_bytes(expected_core)).hexdigest()
    if manifest.get("manifest_sha256") != expected_digest:
        raise ManifestMismatch("manifest content digest mismatch")
    root = root.resolve()
    for record in files:
        try:
            relative = record["path"]
            path = Path(relative)
            if path.is_absolute() or ".." in path.parts:
                raise ManifestMismatch(f"noncanonical manifest path: {relative}")
            data = (root / path).read_bytes()
            observed = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            if observed != {"bytes": record["bytes"], "sha256": record["sha256"]}:
                raise ManifestMismatch(f"manifest mismatch for {relative}")
        except (KeyError, OSError, TypeError) as error:
            raise ManifestMismatch(f"cannot verify manifest record: {record!r}") from error


def _git_commit_exists(repository: Path, commit: str) -> bool:
    return (
        subprocess.run(
            ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
            cwd=repository,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


def _git_is_ancestor(repository: Path, commit: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=repository,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


def _git_output(repository: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *arguments],
            cwd=repository,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as error:
        raise ExecutionAuthorizationMismatch(
            f"cannot resolve git identity: {' '.join(arguments)}"
        ) from error


def _git_is_ancestor_of(repository: Path, ancestor: str, descendant: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=repository,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


def _git_status(repository: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=repository,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as error:
        raise ExecutionAuthorizationMismatch("cannot inspect checkout cleanliness") from error


def require_checkout_scope(repository: Path) -> str:
    """Accept a full checkout or one exact, materialized cone-mode sparse scope."""

    sparse = subprocess.run(
        ["git", "config", "--bool", "core.sparseCheckout"],
        cwd=repository,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if sparse.returncode == 1 or sparse.stdout.strip() == "false":
        return "FULL"
    if sparse.returncode != 0 or sparse.stdout.strip() != "true":
        raise ExecutionAuthorizationMismatch("cannot resolve sparse-checkout state")
    cone = subprocess.run(
        ["git", "config", "--bool", "core.sparseCheckoutCone"],
        cwd=repository,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if cone.returncode != 0 or cone.stdout.strip() != "true":
        raise ExecutionAuthorizationMismatch("sparse checkout must use exact cone mode")
    try:
        listed = subprocess.check_output(
            ["git", "sparse-checkout", "list"],
            cwd=repository,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ExecutionAuthorizationMismatch("cannot resolve sparse-checkout paths") from error
    paths = tuple(line.strip() for line in listed.splitlines() if line.strip())
    if paths != SPARSE_CHECKOUT_PATHS:
        raise ExecutionAuthorizationMismatch("sparse-checkout paths are not the exact R8 scope")
    for relative in SPARSE_REQUIRED_FILES:
        path = repository / relative
        if path.is_symlink() or not path.is_file():
            raise ExecutionAuthorizationMismatch(
                f"sparse checkout did not materialize required path: {relative.as_posix()}"
            )
        working_blob = subprocess.check_output(
            ["git", "hash-object", relative.as_posix()],
            cwd=repository,
            text=True,
        ).strip()
        committed_blob = _git_output(repository, "rev-parse", f"HEAD:{relative.as_posix()}")
        if working_blob != committed_blob:
            raise ExecutionAuthorizationMismatch(
                f"sparse checkout materialized path drifted: {relative.as_posix()}"
            )
    return "SPARSE_EXACT_FIVE_PAPER_R8"


def require_packet_identity(packet_path: Path, *, repository: Path) -> dict[str, Any]:
    """Resolve the frozen subject only through the exact validated v2 packet pair.

    The v1 packet was a self-referential placeholder and is permanently invalid.
    The canonical v2 validator binds the subject, packet-publication commit, and
    successor publication record before this function returns a subject identity.
    """

    repository = repository.resolve()
    expected_packet = repository / PACKET_PATH
    validator = repository / PACKET_VALIDATOR_PATH
    try:
        if packet_path.is_symlink() or packet_path.resolve() != expected_packet.resolve():
            raise PacketIdentityMismatch("packet path is not the canonical v2 packet")
        if validator.is_symlink() or not validator.is_file():
            raise PacketIdentityMismatch("canonical packet validator is unavailable")
        validator_bytes = validator.read_bytes()
        if (
            len(validator_bytes) != PACKET_VALIDATOR_BYTES
            or hashlib.sha256(validator_bytes).hexdigest() != PACKET_VALIDATOR_SHA256
            or _git_output(repository, "rev-parse", f"HEAD:{PACKET_VALIDATOR_PATH.as_posix()}")
            != PACKET_VALIDATOR_GIT_BLOB
        ):
            raise PacketIdentityMismatch("canonical packet validator identity drifted")
    except (OSError, ExecutionAuthorizationMismatch) as error:
        raise PacketIdentityMismatch("packet or validator path cannot be resolved") from error

    completed = subprocess.run(
        [
            sys.executable,
            str(validator),
            "--repo-root",
            str(repository),
            "--json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "no diagnostic"
        raise PacketIdentityMismatch(f"v2 packet publication binding failed: {detail}")
    try:
        packet = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise PacketIdentityMismatch("v2 packet validator returned invalid JSON") from error
    if type(packet) is not dict or set(packet) != PACKET_VALIDATION_FIELDS:
        raise PacketIdentityMismatch("validated packet result fields are not exact")
    subject = packet.get("scientific_subject")
    publication = packet.get("packet_publication")
    if (
        packet.get("schema") != "ORION.FivePaperR8.PacketPublicationBinding.v1"
        or packet.get("terminal") != "R8_PACKET_SUBJECT_AND_PUBLICATION_IDENTITIES_BOUND"
        or packet.get("source_ref_status") not in {"EXACT", "NOT_AVAILABLE_LOCALLY"}
        or packet.get("authority") != PACKET_AUTHORITY
        or type(subject) is not dict
        or type(publication) is not dict
        or type(subject.get("commit")) is not str
        or not HEX_SHA1.fullmatch(subject["commit"])
        or type(subject.get("tree")) is not str
        or not HEX_SHA1.fullmatch(subject["tree"])
        or publication.get("commit") == subject["commit"]
    ):
        raise PacketIdentityMismatch("validated v2 packet values are not exact")
    try:
        head = _git_output(repository, "rev-parse", "HEAD")
    except ExecutionAuthorizationMismatch as error:
        raise PacketIdentityMismatch("packet validator checkout cannot be resolved") from error
    if packet.get("validated_at_checkout") != head:
        raise PacketIdentityMismatch("packet validator checkout identity drifted")
    return packet


AUTHORIZATION_FIELDS = {
    "schema",
    "job_id",
    "scientific_subject_commit",
    "scientific_subject_tree",
    "implementation_commit",
    "implementation_tree",
    "source_manifest_sha256",
    "grants_execution_authority",
    "grants_lunarc_submission",
    "authority_terminal",
}


def require_execution_authorization(
    authorization_path: Path,
    *,
    repository: Path,
    scientific_subject_commit: str,
    source_manifest_sha256: str,
) -> dict[str, Any]:
    """Require an external object binding the exact clean implementation checkout."""

    try:
        raw = authorization_path.read_bytes()
        authorization = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        raise ExecutionAuthorizationMismatch(
            "execution authorization object is unavailable or invalid"
        ) from error
    if type(authorization) is not dict or set(authorization) != AUTHORIZATION_FIELDS:
        raise ExecutionAuthorizationMismatch("execution authorization fields are not exact")
    if authorization["schema"] != "ORION.FiberGuardCleanroomExecutionAuthorization.v1":
        raise ExecutionAuthorizationMismatch("execution authorization schema mismatch")
    if authorization["job_id"] != "JOB-C-R8-1":
        raise ExecutionAuthorizationMismatch("execution authorization job mismatch")
    for name in (
        "scientific_subject_commit",
        "implementation_commit",
    ):
        if type(authorization[name]) is not str or not HEX_SHA1.fullmatch(authorization[name]):
            raise ExecutionAuthorizationMismatch(f"authorization {name} is invalid")
    for name in (
        "scientific_subject_tree",
        "implementation_tree",
    ):
        if type(authorization[name]) is not str or not HEX_SHA1.fullmatch(authorization[name]):
            raise ExecutionAuthorizationMismatch(f"authorization {name} is invalid")
    if authorization["scientific_subject_commit"] != scientific_subject_commit:
        raise ExecutionAuthorizationMismatch("authorization scientific subject mismatch")
    if authorization["source_manifest_sha256"] != source_manifest_sha256:
        raise ExecutionAuthorizationMismatch("authorization source manifest mismatch")
    if not HEX_SHA256.fullmatch(source_manifest_sha256):
        raise ExecutionAuthorizationMismatch("authorization source manifest digest is invalid")
    if authorization["grants_execution_authority"] is not True:
        raise ExecutionAuthorizationMismatch("execution authority is not granted")
    if authorization["grants_lunarc_submission"] is not True:
        raise ExecutionAuthorizationMismatch("LUNARC submission authority is not granted")
    if authorization["authority_terminal"] != "ROOT_REVIEW_AUTHORIZED":
        raise ExecutionAuthorizationMismatch("root-review authorization terminal is absent")

    subject_tree = _git_output(repository, "rev-parse", f"{scientific_subject_commit}^{{tree}}")
    if subject_tree != authorization["scientific_subject_tree"]:
        raise ExecutionAuthorizationMismatch("authorization scientific subject tree mismatch")
    head = _git_output(repository, "rev-parse", "HEAD")
    tree = _git_output(repository, "rev-parse", "HEAD^{tree}")
    if head != authorization["implementation_commit"]:
        raise ExecutionAuthorizationMismatch("authorization does not bind exact HEAD")
    if tree != authorization["implementation_tree"]:
        raise ExecutionAuthorizationMismatch("authorization does not bind exact HEAD tree")
    if not _git_is_ancestor_of(repository, scientific_subject_commit, head):
        raise ExecutionAuthorizationMismatch(
            "authorized implementation does not descend from the scientific subject"
        )
    if _git_status(repository):
        raise ExecutionAuthorizationMismatch("execution requires an exact clean checkout")
    require_checkout_scope(repository)

    return {
        **authorization,
        "authorization_bytes": len(raw),
        "authorization_sha256": hashlib.sha256(raw).hexdigest(),
    }


def build_execution_provenance(
    *,
    repository: Path,
    workers: int,
    command: Sequence[str],
    started_at: str,
    ended_at: str,
    wall_time_seconds: float,
    maximum_rss: int,
    exit_code: int,
    stdout: bytes,
    stderr: bytes,
    slurm_job_id: str,
) -> dict[str, Any]:
    """Build the exact run/environment record sealed into an execution receipt."""

    status = _git_status(repository)
    return {
        "schema": "ORION.FiberGuardCleanroomExecutionProvenance.v1",
        "git_commit": _git_output(repository, "rev-parse", "HEAD"),
        "git_tree": _git_output(repository, "rev-parse", "HEAD^{tree}"),
        "git_status": "CLEAN" if not status else f"DIRTY:{status}",
        "checkout_scope": require_checkout_scope(repository),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "processor": platform.processor() or "CANNOT_CHECK",
        "cpu_count": os.cpu_count(),
        "workers": workers,
        "command": list(command),
        "slurm_job_id": slurm_job_id,
        "started_at": started_at,
        "ended_at": ended_at,
        "wall_time_seconds": wall_time_seconds,
        "maximum_rss": maximum_rss,
        "exit_code": exit_code,
        "stdout_bytes": len(stdout),
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_bytes": len(stderr),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
    }
