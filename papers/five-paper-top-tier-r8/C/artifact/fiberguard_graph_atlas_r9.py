#!/usr/bin/env python3
"""Exact seven-vertex Graph Atlas extension for FiberGuard R9.

The experiment uses the complete NetworkX Graph Atlas slice on seven vertices
(one representative of every unlabeled simple graph on seven vertices), checks
chromatic number with two independent exact solvers, and audits refinements of
(sorted degree sequence, triangle count).
"""
from __future__ import annotations

import collections
import functools
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Callable, Sequence

import networkx as nx

SCHEMA = "ORION.FiberGuard.GraphAtlasR9.Results.v1"
ATLAS_OFFSET_N7 = 209


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def graph_adjacency_masks(graph: nx.Graph) -> tuple[int, ...]:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    adjacency = [0] * graph.number_of_nodes()
    for left, right in graph.edges():
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left
    return tuple(adjacency)


def chromatic_backtracking(graph: nx.Graph) -> int:
    adjacency = graph_adjacency_masks(graph)
    n = len(adjacency)
    order = sorted(range(n), key=lambda vertex: adjacency[vertex].bit_count(), reverse=True)
    lower = max((len(clique) for clique in nx.find_cliques(graph)), default=1)
    colours = [-1] * n

    def feasible(colour_count: int, depth: int) -> bool:
        if depth == n:
            return True
        vertex = order[depth]
        forbidden = {
            colours[other]
            for other in range(n)
            if colours[other] >= 0 and ((adjacency[vertex] >> other) & 1)
        }
        for colour in range(colour_count):
            if colour in forbidden:
                continue
            colours[vertex] = colour
            if feasible(colour_count, depth + 1):
                return True
            colours[vertex] = -1
        return False

    for colour_count in range(lower, n + 1):
        if feasible(colour_count, 0):
            return colour_count
    raise AssertionError("unreachable")


def chromatic_partition_enumeration(graph: nx.Graph) -> int:
    adjacency = graph_adjacency_masks(graph)
    n = len(adjacency)
    best = n
    blocks: list[int] = []

    def independent(block: int, vertex: int) -> bool:
        return (adjacency[vertex] & block) == 0

    def search(vertex: int) -> None:
        nonlocal best
        if len(blocks) >= best:
            return
        if vertex == n:
            best = min(best, len(blocks))
            return
        for index, block in enumerate(tuple(blocks)):
            if independent(block, vertex):
                blocks[index] = block | (1 << vertex)
                search(vertex + 1)
                blocks[index] = block
        blocks.append(1 << vertex)
        search(vertex + 1)
        blocks.pop()

    search(0)
    return best


def triangle_count(graph: nx.Graph) -> int:
    return sum(nx.triangles(graph).values()) // 3


def base_feature(graph: nx.Graph) -> tuple[tuple[int, ...], int]:
    return tuple(sorted(degree for _, degree in graph.degree())), triangle_count(graph)


def connected_component_count(graph: nx.Graph) -> int:
    return nx.number_connected_components(graph)


def induced_c4_count(graph: nx.Graph) -> int:
    count = 0
    for nodes in itertools.combinations(graph.nodes(), 4):
        subgraph = graph.subgraph(nodes)
        if (
            subgraph.number_of_edges() == 4
            and nx.is_connected(subgraph)
            and all(degree == 2 for _, degree in subgraph.degree())
        ):
            count += 1
    return count


def clique_number(graph: nx.Graph) -> int:
    return max((len(clique) for clique in nx.find_cliques(graph)), default=0)


def one_wl_trace(graph: nx.Graph) -> tuple[tuple[int, ...], ...]:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    nodes = tuple(graph.nodes())
    colours = {node: 0 for node in nodes}
    trace: list[tuple[int, ...]] = []
    for _ in range(len(nodes)):
        signatures = {
            node: (colours[node], tuple(sorted(colours[other] for other in graph.neighbors(node))))
            for node in nodes
        }
        palette = {signature: index for index, signature in enumerate(sorted(set(signatures.values())))}
        refined = {node: palette[signatures[node]] for node in nodes}
        trace.append(tuple(sorted(collections.Counter(refined.values()).values())))
        unchanged_partition = all(
            (refined[left] == refined[right]) == (colours[left] == colours[right])
            for left in nodes
            for right in nodes
        )
        colours = refined
        if unchanged_partition:
            break
    return tuple(trace)


FOUR_PAIRS = tuple(itertools.combinations(range(4), 2))
FOUR_PAIR_INDEX = {pair: index for index, pair in enumerate(FOUR_PAIRS)}
FOUR_PERMUTATIONS = tuple(itertools.permutations(range(4)))


@functools.lru_cache(maxsize=None)
def canonical_four_vertex_code(mask: int) -> int:
    best = 1 << len(FOUR_PAIRS)
    for permutation in FOUR_PERMUTATIONS:
        permuted = 0
        for output_bit, (left, right) in enumerate(FOUR_PAIRS):
            source_pair = tuple(sorted((permutation[left], permutation[right])))
            if (mask >> FOUR_PAIR_INDEX[source_pair]) & 1:
                permuted |= 1 << output_bit
        best = min(best, permuted)
    return best


def induced_graphlet4_profile(graph: nx.Graph) -> tuple[tuple[int, int], ...]:
    counts: collections.Counter[int] = collections.Counter()
    nodes = tuple(graph.nodes())
    for subset in itertools.combinations(nodes, 4):
        mask = 0
        for bit, (left, right) in enumerate(FOUR_PAIRS):
            if graph.has_edge(subset[left], subset[right]):
                mask |= 1 << bit
        counts[canonical_four_vertex_code(mask)] += 1
    assert sum(counts.values()) == 35
    return tuple(sorted(counts.items()))


def graph_witness(atlas_index: int, graph: nx.Graph) -> dict[str, Any]:
    relabeled = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    graph6 = nx.to_graph6_bytes(relabeled, header=False).decode("ascii").strip()
    return {
        "atlas_index": atlas_index,
        "graph6": graph6,
        "edges": [list(edge) for edge in sorted(tuple(sorted(edge)) for edge in relabeled.edges())],
    }


def refinement_summary(
    records: Sequence[tuple[int, nx.Graph, int]],
    feature_fn: Callable[[nx.Graph], Any],
) -> dict[str, Any]:
    fibres: dict[Any, set[int]] = {}
    for _, graph, target in records:
        fibres.setdefault((base_feature(graph), feature_fn(graph)), set()).add(target)
    ambiguous = [values for values in fibres.values() if len(values) > 1]
    return {
        "refined_fibre_count": len(fibres),
        "ambiguous_fibre_count": len(ambiguous),
        "maximum_fibre_diameter": max((max(values) - min(values) for values in ambiguous), default=0),
    }


def main() -> None:
    atlas = nx.graph_atlas_g()
    seven_vertex_graphs = [
        (index, nx.convert_node_labels_to_integers(graph.copy(), ordering="sorted"))
        for index, graph in enumerate(atlas)
        if graph.number_of_nodes() == 7
    ]
    assert len(atlas) == 1253
    assert len(seven_vertex_graphs) == 1044
    assert seven_vertex_graphs[0][0] == ATLAS_OFFSET_N7
    assert seven_vertex_graphs[-1][0] == 1252

    records: list[tuple[int, nx.Graph, int]] = []
    for atlas_index, graph in seven_vertex_graphs:
        target_a = chromatic_backtracking(graph)
        target_b = chromatic_partition_enumeration(graph)
        assert target_a == target_b
        records.append((atlas_index, graph, target_a))

    base_fibres: dict[Any, list[tuple[int, nx.Graph, int]]] = {}
    for row in records:
        base_fibres.setdefault(base_feature(row[1]), []).append(row)
    ambiguous_base = {
        feature: rows
        for feature, rows in base_fibres.items()
        if len({target for _, _, target in rows}) > 1
    }
    best_feature, best_rows = max(
        ambiguous_base.items(),
        key=lambda item: (
            max(target for _, _, target in item[1]) - min(target for _, _, target in item[1]),
            len(item[1]),
            repr(item[0]),
        ),
    )
    minimum_row = min(best_rows, key=lambda row: (row[2], row[0]))
    maximum_row = max(best_rows, key=lambda row: (row[2], -row[0]))

    feature_families: dict[str, Callable[[nx.Graph], Any]] = {
        "connected_component_count": connected_component_count,
        "induced_c4_count": induced_c4_count,
        "clique_number": clique_number,
        "one_wl_trace": one_wl_trace,
        "induced_graphlet4_profile": induced_graphlet4_profile,
        "c4_clique_wl_bundle": lambda graph: (
            induced_c4_count(graph),
            clique_number(graph),
            one_wl_trace(graph),
        ),
        "wl_graphlet4_bundle": lambda graph: (
            one_wl_trace(graph),
            induced_graphlet4_profile(graph),
        ),
    }
    refinements = {name: refinement_summary(records, function) for name, function in feature_families.items()}

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "authority": {
            "finite_exact_on_complete_unlabeled_n7_atlas": True,
            "independent_target_solver_agreement": True,
            "external_replay": False,
            "production_prevalence": False,
            "grants_journal_authority": False,
        },
        "environment_contract": {
            "networkx_version": nx.__version__,
            "atlas_total_graph_count": len(atlas),
            "seven_vertex_atlas_range": [ATLAS_OFFSET_N7, 1252],
            "seven_vertex_unlabeled_graph_count": len(records),
        },
        "target": "chromatic_number",
        "base_representation": "sorted_degree_sequence_plus_triangle_count",
        "base_result": {
            "fibre_count": len(base_fibres),
            "ambiguous_fibre_count": len(ambiguous_base),
            "maximum_fibre_diameter": max(
                max(target for _, _, target in rows) - min(target for _, _, target in rows)
                for rows in ambiguous_base.values()
            ),
            "maximum_diameter_fibre_feature": [list(best_feature[0]), best_feature[1]],
            "maximum_diameter_fibre_multiplicity": len(best_rows),
            "endpoint_values": [minimum_row[2], maximum_row[2]],
            "endpoint_witnesses": [
                graph_witness(minimum_row[0], minimum_row[1]),
                graph_witness(maximum_row[0], maximum_row[1]),
            ],
        },
        "target_distribution": dict(sorted(collections.Counter(target for _, _, target in records).items())),
        "refinement_results": refinements,
        "registered_discriminators": {
            "n6_c4_repair_does_not_transfer_to_n7": (
                refinements["induced_c4_count"]["ambiguous_fibre_count"] > 0
            ),
            "graphlet4_repairs_target_on_complete_n7_atlas": (
                refinements["induced_graphlet4_profile"]["maximum_fibre_diameter"] == 0
            ),
            "c4_clique_wl_repairs_target_on_complete_n7_atlas": (
                refinements["c4_clique_wl_bundle"]["maximum_fibre_diameter"] == 0
            ),
            "wl_plus_graphlet4_identifies_every_atlas_graph": (
                refinements["wl_graphlet4_bundle"]["refined_fibre_count"] == len(records)
            ),
        },
        "controls": {
            "graphlet4_profile_total_induced_subgraphs": 35,
            "two_exact_chromatic_solvers_per_graph": len(records),
            "complete_graph_has_chromatic_number_7": next(
                target for _, graph, target in records if graph.number_of_edges() == 21
            ) == 7,
            "empty_graph_has_chromatic_number_1": next(
                target for _, graph, target in records if graph.number_of_edges() == 0
            ) == 1,
        },
        "terminal": "C_GRAPH_ATLAS_N7_EXACT_REFINEMENT_EXTENSION_PASS",
    }
    result["content_sha256"] = digest(result)
    output = Path(__file__).with_name("FIBERGUARD_GRAPH_ATLAS_R9_RESULTS.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
