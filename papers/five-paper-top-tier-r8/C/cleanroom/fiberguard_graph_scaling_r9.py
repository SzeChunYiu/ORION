#!/usr/bin/env python3
"""Independent finite controls for FiberGuard Graph Scaling Theorem R9.

This implementation does not import the original FiberGuard generator or its
chromatic-number solvers. It checks finite members of the all-size construction.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

SCHEMA = "ORION.FiberGuard.GraphScalingControls.R9.v1"


def haggkvist_hell_graph(n: int, r: int) -> tuple[tuple[int, ...], int]:
    tails = list(itertools.combinations(range(n), r))
    vertices = [(head, tail) for tail in tails for head in range(n) if head not in tail]
    tail_sets = [set(tail) for _, tail in vertices]
    adjacency = [0] * len(vertices)
    for i, (head_i, _) in enumerate(vertices):
        tail_i = tail_sets[i]
        for j in range(i + 1, len(vertices)):
            head_j, _ = vertices[j]
            tail_j = tail_sets[j]
            if head_i in tail_j and head_j in tail_i and tail_i.isdisjoint(tail_j):
                adjacency[i] |= 1 << j
                adjacency[j] |= 1 << i
    return tuple(adjacency), len(vertices)


def two_copies(adjacency: tuple[int, ...]) -> tuple[int, ...]:
    n = len(adjacency)
    output = [0] * (2 * n)
    for i, row in enumerate(adjacency):
        output[i] = row
        output[n + i] = row << n
    return tuple(output)


def circulant_bipartite_mate(part_size: int, degree: int) -> tuple[int, ...]:
    adjacency = [0] * (2 * part_size)
    for left in range(part_size):
        for shift in range(degree):
            right = part_size + ((left + shift) % part_size)
            adjacency[left] |= 1 << right
            adjacency[right] |= 1 << left
    return tuple(adjacency)


def triangle_count(adjacency: tuple[int, ...]) -> int:
    total = 0
    for i, row in enumerate(adjacency):
        higher = row & ~((1 << (i + 1)) - 1)
        while higher:
            bit = higher & -higher
            j = bit.bit_length() - 1
            higher -= bit
            total += (row & adjacency[j] & ~((1 << (j + 1)) - 1)).bit_count()
    return total


def frozen_feature(adjacency: tuple[int, ...]) -> tuple[tuple[int, ...], int]:
    return tuple(sorted(row.bit_count() for row in adjacency)), triangle_count(adjacency)


def greedy_upper_bound(adjacency: tuple[int, ...]) -> int:
    order = sorted(range(len(adjacency)), key=lambda v: adjacency[v].bit_count(), reverse=True)
    colors = [-1] * len(adjacency)
    used_count = 0
    for vertex in order:
        forbidden = {
            colors[neighbor]
            for neighbor in range(len(adjacency))
            if colors[neighbor] >= 0 and ((adjacency[vertex] >> neighbor) & 1)
        }
        color = 0
        while color in forbidden:
            color += 1
        colors[vertex] = color
        used_count = max(used_count, color + 1)
    return used_count


def exact_chromatic_number(adjacency: tuple[int, ...]) -> int:
    """Exact DSATUR branch and bound, used only on the finite control panel."""
    n = len(adjacency)
    best = greedy_upper_bound(adjacency)
    colors = [-1] * n
    saturation_masks = [0] * n
    degrees = [row.bit_count() for row in adjacency]

    def search(colored: int, used: int) -> None:
        nonlocal best
        if used >= best:
            return
        if colored == n:
            best = used
            return
        uncolored = [v for v in range(n) if colors[v] < 0]
        vertex = max(uncolored, key=lambda v: (saturation_masks[v].bit_count(), degrees[v]))
        forbidden = saturation_masks[vertex]
        for color in range(min(used + 1, best - 1)):
            if (forbidden >> color) & 1:
                continue
            colors[vertex] = color
            changed: list[int] = []
            neighbors = adjacency[vertex]
            while neighbors:
                bit = neighbors & -neighbors
                neighbor = bit.bit_length() - 1
                neighbors -= bit
                if colors[neighbor] < 0 and not ((saturation_masks[neighbor] >> color) & 1):
                    saturation_masks[neighbor] |= 1 << color
                    changed.append(neighbor)
            search(colored + 1, max(used, color + 1))
            for neighbor in changed:
                saturation_masks[neighbor] &= ~(1 << color)
            colors[vertex] = -1

    search(0, 0)
    return best


def run() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for n, r in ((4, 2), (5, 2), (6, 2)):
        hh, vertex_count = haggkvist_hell_graph(n, r)
        expected_vertices = (n - r) * math.comb(n, r)
        degree = r * math.comb(n - r - 1, r - 1)
        assert vertex_count == expected_vertices
        assert all(row.bit_count() == degree for row in hh)
        high = two_copies(hh)
        bipartite = circulant_bipartite_mate(vertex_count, degree)
        assert triangle_count(hh) == 0
        assert triangle_count(high) == 0
        assert triangle_count(bipartite) == 0
        assert frozen_feature(high) == frozen_feature(bipartite)
        chi_hh = exact_chromatic_number(hh)
        rows.append(
            {
                "n": n,
                "r": r,
                "hh_vertices": vertex_count,
                "paired_vertices": 2 * vertex_count,
                "degree": degree,
                "feature_equal": True,
                "triangle_count": 0,
                "hh_chromatic_number_exact": chi_hh,
                "bipartite_chromatic_number": 2,
                "collision_diameter_exact": chi_hh - 2,
            }
        )
    result: dict[str, object] = {
        "schema": SCHEMA,
        "authority": {
            "finite_controls_exact": True,
            "all_size_authority_from_computation": False,
            "all_size_authority_from_displayed_proof_and_donor_theorem": True,
            "external_prevalence": False,
        },
        "rows": rows,
    }
    payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    result["content_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="FIBERGUARD_GRAPH_SCALING_R9_RESULTS.json")
    args = parser.parse_args()
    result = run()
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
