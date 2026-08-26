#!/usr/bin/env python3
"""Exact multi-domain representation-collision benchmark for Paper C R8.

The benchmark is deliberately finite and exhaustive on each declared domain.
It groups instances by a frozen representation, solves the exact target twice,
and reports the largest target diameter inside any representation fibre.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import functools
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "ORION.FiberGuardR8.Results.v1"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass
class FibreRecord:
    minimum: int
    maximum: int
    minimum_witness: Any
    maximum_witness: Any
    multiplicity: int = 0

    @property
    def diameter(self) -> int:
        return self.maximum - self.minimum


def update_fibre(table: dict[Any, FibreRecord], feature: Any, target: int, witness: Any) -> None:
    row = table.get(feature)
    if row is None:
        table[feature] = FibreRecord(target, target, witness, witness, 1)
        return
    row.multiplicity += 1
    if target < row.minimum:
        row.minimum = target
        row.minimum_witness = witness
    if target > row.maximum:
        row.maximum = target
        row.maximum_witness = witness


def best_fibre(table: dict[Any, FibreRecord]) -> tuple[Any, FibreRecord]:
    return max(table.items(), key=lambda item: (item[1].diameter, item[1].multiplicity, repr(item[0])))


def refinement_summary(records, base_feature, candidate_features, baseline_name):
    rows = {}
    for name, feature_fn in candidate_features.items():
        refined = {}
        for instance, target in records:
            update_fibre(refined, (base_feature(instance), feature_fn(instance)), target, None)
        maximum = max(row.diameter for row in refined.values())
        ambiguous = sum(1 for row in refined.values() if row.diameter > 0)
        rows[name] = {
            "maximum_fibre_diameter": maximum,
            "refined_fibre_count": len(refined),
            "ambiguous_fibre_count": ambiguous,
        }
    selected = min(rows, key=lambda name: (rows[name]["maximum_fibre_diameter"], rows[name]["ambiguous_fibre_count"], name))
    return {
        "candidate_results": rows,
        "collision_guided_selection": selected,
        "collision_guided_result": rows[selected],
        "matched_baseline_selection": baseline_name,
        "matched_baseline_result": rows[baseline_name],
        "strict_improvement_over_baseline": (
            rows[selected]["maximum_fibre_diameter"], rows[selected]["ambiguous_fibre_count"]
        ) < (
            rows[baseline_name]["maximum_fibre_diameter"], rows[baseline_name]["ambiguous_fibre_count"]
        ),
    }


# ---------------------------------------------------------------------------
# Domain 1: graph colouring
# ---------------------------------------------------------------------------

def graph_adjacency(n: int, mask: int) -> tuple[int, ...]:
    adj = [0] * n
    bit = 0
    for i in range(n):
        for j in range(i + 1, n):
            if (mask >> bit) & 1:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            bit += 1
    return tuple(adj)


def graph_triangle_count_a(adj: Sequence[int]) -> int:
    total = 0
    n = len(adj)
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1:
                total += ((adj[i] & adj[j]) >> (j + 1)).bit_count()
    return total


def graph_triangle_count_b(adj: Sequence[int]) -> int:
    n = len(adj)
    return sum(
        1
        for i in range(n)
        for j in range(i + 1, n)
        for k in range(j + 1, n)
        if ((adj[i] >> j) & 1) and ((adj[i] >> k) & 1) and ((adj[j] >> k) & 1)
    )


def graph_feature(adj: Sequence[int]) -> tuple[tuple[int, ...], int]:
    return tuple(sorted(x.bit_count() for x in adj)), graph_triangle_count_a(adj)


def chromatic_backtracking(adj: Sequence[int]) -> int:
    n = len(adj)
    order = sorted(range(n), key=lambda v: adj[v].bit_count(), reverse=True)
    for colour_count in range(1, n + 1):
        colours = [-1] * n

        def search(depth: int) -> bool:
            if depth == n:
                return True
            v = order[depth]
            forbidden = {
                colours[u]
                for u in range(n)
                if colours[u] >= 0 and ((adj[v] >> u) & 1)
            }
            for colour in range(colour_count):
                if colour not in forbidden:
                    colours[v] = colour
                    if search(depth + 1):
                        return True
                    colours[v] = -1
            return False

        if search(0):
            return colour_count
    raise AssertionError("unreachable")


def chromatic_partition_enumeration(adj: Sequence[int]) -> int:
    n = len(adj)
    best = n
    blocks: list[int] = []

    def independent(block: int, v: int) -> bool:
        return (adj[v] & block) == 0

    def search(v: int) -> None:
        nonlocal best
        if len(blocks) >= best:
            return
        if v == n:
            best = min(best, len(blocks))
            return
        for i, block in enumerate(tuple(blocks)):
            if independent(block, v):
                blocks[i] = block | (1 << v)
                search(v + 1)
                blocks[i] = block
        blocks.append(1 << v)
        search(v + 1)
        blocks.pop()

    search(0)
    return best


def graph_extra_features(adj: Sequence[int]) -> dict[str, Any]:
    n = len(adj)
    seen = 0
    components = 0
    for start in range(n):
        if (seen >> start) & 1:
            continue
        components += 1
        stack = [start]
        seen |= 1 << start
        while stack:
            vertex = stack.pop()
            remaining = adj[vertex] & ~seen
            while remaining:
                bit = remaining & -remaining
                neighbour = bit.bit_length() - 1
                seen |= bit
                stack.append(neighbour)
                remaining -= bit
    four_cycles = 0
    for i in range(n):
        for j in range(i + 1, n):
            common = (adj[i] & adj[j]).bit_count()
            four_cycles += common * (common - 1) // 2
    four_cycles //= 2
    clique_number = 0
    for subset in range(1 << n):
        if subset.bit_count() <= clique_number:
            continue
        if all(not ((subset >> v) & 1) or (((subset & ~(1 << v)) & ~adj[v]) == 0) for v in range(n)):
            clique_number = subset.bit_count()
    return {
        "connected_component_count": components,
        "four_cycle_count": four_cycles,
        "clique_number": clique_number,
    }


def run_graph_domain() -> dict[str, Any]:
    n = 6
    edge_slots = n * (n - 1) // 2
    fibres: dict[Any, FibreRecord] = {}
    records = []
    target_checks = 0
    for mask in range(1 << edge_slots):
        adj = graph_adjacency(n, mask)
        assert graph_triangle_count_a(adj) == graph_triangle_count_b(adj)
        target_a = chromatic_backtracking(adj)
        target_b = chromatic_partition_enumeration(adj)
        assert target_a == target_b
        target_checks += 1
        records.append((adj, target_a))
        update_fibre(fibres, graph_feature(adj), target_a, {"edge_mask": mask})
    feature, row = best_fibre(fibres)
    graph_candidates = {
        name: (lambda instance, name=name: graph_extra_features(instance)[name])
        for name in graph_extra_features(records[0][0])
    }
    refinement = refinement_summary(records, graph_feature, graph_candidates, "connected_component_count")
    return {
        "domain": "GRAPH_COLOURING_N6",
        "instance_space": "all labeled simple graphs on six vertices",
        "instance_count": 1 << edge_slots,
        "representation": {
            "name": "sorted_degree_sequence_plus_triangle_count",
            "feature": [list(feature[0]), feature[1]],
        },
        "target": "chromatic_number",
        "fibre_count": len(fibres),
        "maximum_fibre_diameter": row.diameter,
        "endpoint_values": [row.minimum, row.maximum],
        "fibre_multiplicity": row.multiplicity,
        "endpoint_witnesses": [row.minimum_witness, row.maximum_witness],
        "independent_target_checks": target_checks,
        "refinement_experiment": refinement,
        "status": "FINITE_EXACT",
    }


# ---------------------------------------------------------------------------
# Domain 2: minimum set cover
# ---------------------------------------------------------------------------

def set_cover_feature(family: Sequence[int]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    sizes = tuple(sorted(s.bit_count() for s in family))
    intersections = tuple(
        sorted((family[i] & family[j]).bit_count() for i in range(len(family)) for j in range(i + 1, len(family)))
    )
    return sizes, intersections


def minimum_cover_subset_enumeration(family: Sequence[int], universe: int) -> int:
    for count in range(1, len(family) + 1):
        for indices in itertools.combinations(range(len(family)), count):
            covered = 0
            for i in indices:
                covered |= family[i]
            if covered == universe:
                return count
    raise AssertionError("family does not cover universe")


def minimum_cover_mask_dp(family: Sequence[int], universe: int) -> int:
    infinity = len(family) + 1
    dp = [infinity] * (universe + 1)
    dp[0] = 0
    for subset in family:
        nxt = dp[:]
        for covered, cost in enumerate(dp):
            if cost < infinity:
                merged = covered | subset
                nxt[merged] = min(nxt[merged], cost + 1)
        dp = nxt
    assert dp[universe] < infinity
    return dp[universe]


def set_cover_extra_features(family: Sequence[int], universe_size: int = 5) -> dict[str, Any]:
    pairwise_unions = tuple(
        sorted((family[i] | family[j]).bit_count() for i in range(len(family)) for j in range(i + 1, len(family)))
    )
    element_frequencies = tuple(
        sorted(sum((subset >> element) & 1 for subset in family) for element in range(universe_size))
    )
    triple_intersections = tuple(
        sorted(
            (family[i] & family[j] & family[k]).bit_count()
            for i in range(len(family))
            for j in range(i + 1, len(family))
            for k in range(j + 1, len(family))
        )
    )
    return {
        "pairwise_union_multiset": pairwise_unions,
        "element_frequency_multiset": element_frequencies,
        "triple_intersection_multiset": triple_intersections,
    }


def run_set_cover_domain() -> dict[str, Any]:
    universe_size = 5
    universe = (1 << universe_size) - 1
    set_count = 5
    candidates = tuple(range(1, universe + 1))
    fibres: dict[Any, FibreRecord] = {}
    records = []
    instance_count = 0
    for family in itertools.combinations(candidates, set_count):
        if not family or functools.reduce(int.__or__, family, 0) != universe:
            continue
        target_a = minimum_cover_subset_enumeration(family, universe)
        target_b = minimum_cover_mask_dp(family, universe)
        assert target_a == target_b
        instance_count += 1
        records.append((family, target_a))
        update_fibre(
            fibres,
            set_cover_feature(family),
            target_a,
            {"sets": list(family)},
        )
    feature, row = best_fibre(fibres)
    set_cover_candidates = {
        name: (lambda instance, name=name: set_cover_extra_features(instance, universe_size)[name])
        for name in set_cover_extra_features(records[0][0], universe_size)
    }
    refinement = refinement_summary(
        records, set_cover_feature, set_cover_candidates, "element_frequency_multiset"
    )
    return {
        "domain": "SET_COVER_U5_M5",
        "instance_space": "all five-set subfamilies of nonempty subsets of a five-element universe that cover the universe",
        "instance_count": instance_count,
        "representation": {
            "name": "sorted_set_sizes_plus_pairwise_intersection_multiset",
            "feature": [list(feature[0]), list(feature[1])],
        },
        "target": "minimum_cover_size",
        "fibre_count": len(fibres),
        "maximum_fibre_diameter": row.diameter,
        "endpoint_values": [row.minimum, row.maximum],
        "fibre_multiplicity": row.multiplicity,
        "endpoint_witnesses": [row.minimum_witness, row.maximum_witness],
        "independent_target_checks": instance_count,
        "refinement_experiment": refinement,
        "status": "FINITE_EXACT",
    }


# ---------------------------------------------------------------------------
# Domain 3: satisfying-assignment count for 2-CNF
# ---------------------------------------------------------------------------

def all_binary_clauses(variable_count: int) -> tuple[tuple[int, int], ...]:
    literals = tuple(range(1, variable_count + 1)) + tuple(range(-1, -variable_count - 1, -1))
    clauses = []
    for a_index in range(len(literals)):
        for b_index in range(a_index + 1, len(literals)):
            a, b = literals[a_index], literals[b_index]
            if abs(a) != abs(b):
                clauses.append((a, b))
    return tuple(clauses)


def literal_value(literal: int, assignment: int) -> bool:
    bit = bool((assignment >> (abs(literal) - 1)) & 1)
    return bit if literal > 0 else not bit


def satisfying_count_assignment_loop(formula: Sequence[tuple[int, int]], variable_count: int) -> int:
    return sum(
        1
        for assignment in range(1 << variable_count)
        if all(literal_value(a, assignment) or literal_value(b, assignment) for a, b in formula)
    )


def satisfying_count_bitset(formula: Sequence[tuple[int, int]], variable_count: int) -> int:
    all_assignments = (1 << (1 << variable_count)) - 1
    surviving = all_assignments
    for a, b in formula:
        clause_mask = 0
        for assignment in range(1 << variable_count):
            if literal_value(a, assignment) or literal_value(b, assignment):
                clause_mask |= 1 << assignment
        surviving &= clause_mask
    return surviving.bit_count()


def sat_feature(formula: Sequence[tuple[int, int]], variable_count: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    positive = [0] * variable_count
    negative = [0] * variable_count
    cooccurrence = [[0] * variable_count for _ in range(variable_count)]
    for a, b in formula:
        for literal in (a, b):
            if literal > 0:
                positive[literal - 1] += 1
            else:
                negative[-literal - 1] += 1
        i, j = sorted((abs(a) - 1, abs(b) - 1))
        cooccurrence[i][j] += 1
    return (
        tuple(positive + negative),
        tuple(cooccurrence[i][j] for i in range(variable_count) for j in range(i + 1, variable_count)),
    )


def sat_extra_features(formula: Sequence[tuple[int, int]], variable_count: int = 4) -> dict[str, Any]:
    global_sign_types = [0, 0, 0, 0]
    per_pair: dict[tuple[int, int], list[int]] = {}
    for a, b in formula:
        if abs(a) > abs(b):
            a, b = b, a
        sign_type = (0 if a > 0 else 2) + (0 if b > 0 else 1)
        global_sign_types[sign_type] += 1
        pair = (abs(a) - 1, abs(b) - 1)
        per_pair.setdefault(pair, [0, 0, 0, 0])[sign_type] += 1
    labeled_profile = tuple(
        tuple(per_pair.get((i, j), [0, 0, 0, 0]))
        for i in range(variable_count)
        for j in range(i + 1, variable_count)
    )
    profile_multiset = tuple(sorted(labeled_profile))
    return {
        "global_clause_sign_type_counts": tuple(global_sign_types),
        "variable_pair_signed_profile_multiset": profile_multiset,
        "labeled_variable_pair_signed_profile": labeled_profile,
    }


def run_sat_domain() -> dict[str, Any]:
    variable_count = 4
    clause_count = 5
    clauses = all_binary_clauses(variable_count)
    fibres: dict[Any, FibreRecord] = {}
    records = []
    instance_count = 0
    for indices in itertools.combinations(range(len(clauses)), clause_count):
        formula = tuple(clauses[i] for i in indices)
        target_a = satisfying_count_assignment_loop(formula, variable_count)
        target_b = satisfying_count_bitset(formula, variable_count)
        assert target_a == target_b
        instance_count += 1
        records.append((formula, target_a))
        update_fibre(fibres, sat_feature(formula, variable_count), target_a, {"clauses": [list(c) for c in formula]})
    feature, row = best_fibre(fibres)
    sat_candidates = {
        name: (lambda instance, name=name: sat_extra_features(instance, variable_count)[name])
        for name in sat_extra_features(records[0][0], variable_count)
    }
    refinement = refinement_summary(
        records,
        lambda instance: sat_feature(instance, variable_count),
        sat_candidates,
        "global_clause_sign_type_counts",
    )
    return {
        "domain": "TWO_CNF_N4_M5",
        "instance_space": "all five-clause subsets of the 24 non-tautological binary clauses on four labeled variables",
        "instance_count": instance_count,
        "representation": {
            "name": "signed_variable_occurrence_counts_plus_labeled_variable_pair_cooccurrence",
            "feature": [list(feature[0]), list(feature[1])],
        },
        "target": "number_of_satisfying_assignments",
        "fibre_count": len(fibres),
        "maximum_fibre_diameter": row.diameter,
        "endpoint_values": [row.minimum, row.maximum],
        "fibre_multiplicity": row.multiplicity,
        "endpoint_witnesses": [row.minimum_witness, row.maximum_witness],
        "independent_target_checks": instance_count,
        "refinement_experiment": refinement,
        "status": "FINITE_EXACT",
    }


def main() -> None:
    domains = [run_graph_domain(), run_set_cover_domain(), run_sat_domain()]
    result = {
        "schema": SCHEMA,
        "authority": {
            "finite_exact_on_declared_domains": True,
            "general_real_world_prevalence": False,
            "independent_external_replay": False,
            "grants_scientific_authority": False,
        },
        "domains": domains,
        "all_domains_have_nonzero_diameter": all(d["maximum_fibre_diameter"] > 0 for d in domains),
    }
    result["content_sha256"] = digest(result)
    output = Path(__file__).with_name("FIBERGUARD_R8_RESULTS.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
