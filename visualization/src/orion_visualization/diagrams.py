"""Deterministic framework/dependency diagrams without graph libraries."""

from __future__ import annotations

import textwrap
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from .styles import apply_atlas_style, new_figure

from matplotlib.patches import FancyArrowPatch, Patch


_GROUP_COLORS = (
    "#56B4E9",
    "#E69F00",
    "#009E73",
    "#CC79A7",
    "#F0E442",
    "#8DA0CB",
    "#A6761D",
    "#B8B8B8",
)


def _validate_graph(
    nodes: Sequence[Any], edges: Sequence[tuple[Any, Any]]
) -> tuple[list[str], list[tuple[str, str]]]:
    node_names = [str(node) for node in nodes]
    if not node_names:
        raise ValueError("nodes must not be empty")
    if len(node_names) != len(set(node_names)):
        raise ValueError("node names must be unique after string conversion")
    known = set(node_names)
    checked_edges: list[tuple[str, str]] = []
    for raw_edge in edges:
        if len(raw_edge) != 2:
            raise ValueError("each edge must contain exactly source and target")
        source, target = map(str, raw_edge)
        if source not in known or target not in known:
            raise ValueError(f"edge ({source!r}, {target!r}) references an unknown node")
        if source == target:
            raise ValueError("self-loop dependencies are not supported")
        checked_edges.append((source, target))
    return node_names, list(dict.fromkeys(checked_edges))


def _layered_positions(
    nodes: Sequence[str], edges: Sequence[tuple[str, str]]
) -> dict[str, tuple[float, float]]:
    """Kahn-style longest-path layers with an explicit cycle fallback."""

    outgoing: dict[str, list[str]] = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}
    for source, target in edges:
        outgoing[source].append(target)
        indegree[target] += 1
    layer = {node: 0 for node in nodes}
    ready = sorted(node for node in nodes if indegree[node] == 0)
    processed: set[str] = set()
    while ready:
        source = ready.pop(0)
        processed.add(source)
        for target in sorted(outgoing[source]):
            layer[target] = max(layer[target], layer[source] + 1)
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
                ready.sort()

    # A cycle is a meaningful framework anomaly, not a reason to omit nodes.
    # Place the unresolved component in a final layer; callers can still see
    # the backward/cyclic arrows and inspect the source graph.
    unresolved = sorted(set(nodes) - processed)
    if unresolved:
        fallback = max((layer[node] for node in processed), default=-1) + 1
        for node in unresolved:
            layer[node] = fallback

    by_layer: dict[int, list[str]] = defaultdict(list)
    for node in nodes:
        by_layer[layer[node]].append(node)
    positions: dict[str, tuple[float, float]] = {}
    for layer_index in sorted(by_layer):
        members = sorted(by_layer[layer_index])
        centre = (len(members) - 1) / 2.0
        for member_index, node in enumerate(members):
            positions[node] = (float(layer_index), float(centre - member_index))
    return positions


def _provided_positions(
    nodes: Sequence[str], positions: Mapping[Any, Sequence[float]]
) -> dict[str, tuple[float, float]]:
    normalised = {str(node): coordinates for node, coordinates in positions.items()}
    if set(normalised) != set(nodes):
        raise ValueError("positions must provide exactly one coordinate for every node")
    result: dict[str, tuple[float, float]] = {}
    for node, coordinates in normalised.items():
        if len(coordinates) != 2:
            raise ValueError("each position must contain x and y")
        x, y = float(coordinates[0]), float(coordinates[1])
        if not np.isfinite(x) or not np.isfinite(y):
            raise ValueError("positions must contain only finite coordinates")
        result[node] = (x, y)
    return result


def plot_dependency_diagram(
    nodes: Sequence[Any],
    edges: Sequence[tuple[Any, Any]],
    *,
    groups: Mapping[Any, Any] | None = None,
    positions: Mapping[Any, Sequence[float]] | None = None,
    title: str = "Framework dependencies",
):
    """Render a dependency graph using a deterministic dependency-layer layout.

    Edges point from prerequisite/source to dependent/target.  Cyclic nodes are
    retained in a final layer rather than silently discarded.
    """

    apply_atlas_style()
    node_names, checked_edges = _validate_graph(nodes, edges)
    coordinates = (
        _layered_positions(node_names, checked_edges)
        if positions is None
        else _provided_positions(node_names, positions)
    )
    group_by_node = {node: "component" for node in node_names}
    if groups is not None:
        supplied = {str(node): str(group) for node, group in groups.items()}
        unknown = set(supplied) - set(node_names)
        if unknown:
            raise ValueError(f"groups references unknown nodes: {sorted(unknown)}")
        group_by_node.update(supplied)
    group_names = list(dict.fromkeys(group_by_node[node] for node in node_names))
    color_by_group = {
        group: _GROUP_COLORS[index % len(_GROUP_COLORS)] for index, group in enumerate(group_names)
    }

    x_values = [coordinates[node][0] for node in node_names]
    y_values = [coordinates[node][1] for node in node_names]
    x_span = max(x_values) - min(x_values)
    y_span = max(y_values) - min(y_values)
    fig, ax = new_figure(figsize=(max(7.0, 2.25 * (x_span + 1.0)), max(4.2, 1.15 * (y_span + 2.0))))

    for source, target in checked_edges:
        source_x, source_y = coordinates[source]
        target_x, target_y = coordinates[target]
        delta_x = target_x - source_x
        delta_y = target_y - source_y
        distance = float(np.hypot(delta_x, delta_y))
        unit_x, unit_y = delta_x / distance, delta_y / distance
        # Node labels have variable-width bounding boxes.  Data-coordinate
        # margins keep every arrowhead outside the target box instead of
        # relying on one point-based shrink value that hides heads on wide
        # labels.
        margin = 0.38 if abs(delta_x) >= abs(delta_y) else 0.23
        start = (source_x + unit_x * margin, source_y + unit_y * margin)
        end = (target_x - unit_x * margin, target_y - unit_y * margin)
        arrow = FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=18,
            linewidth=1.35,
            color="#4B5563",
            connectionstyle="arc3,rad=0.06" if source_x == target_x else "arc3,rad=0.0",
            shrinkA=0,
            shrinkB=0,
            zorder=1,
        )
        ax.add_patch(arrow)

    for node in node_names:
        x, y = coordinates[node]
        group = group_by_node[node]
        ax.text(
            x,
            y,
            textwrap.fill(node, width=19),
            ha="center",
            va="center",
            fontsize=9,
            bbox={
                "boxstyle": "round,pad=0.48",
                "facecolor": color_by_group[group],
                "edgecolor": "#1F2937",
                "linewidth": 1.0,
            },
            zorder=2,
        )

    margin_x = max(0.6, 0.12 * max(x_span, 1.0))
    margin_y = max(0.8, 0.12 * max(y_span, 1.0))
    ax.set_xlim(min(x_values) - margin_x, max(x_values) + margin_x)
    ax.set_ylim(min(y_values) - margin_y, max(y_values) + margin_y)
    ax.set_title(title)
    ax.axis("off")
    if groups is not None:
        handles = [
            Patch(facecolor=color_by_group[group], edgecolor="#1F2937", label=group)
            for group in group_names
        ]
        ax.legend(handles=handles, title="Component class", frameon=False, loc="upper left")
    return fig, ax, coordinates


def plot_framework_diagram(
    components: Mapping[Any, Sequence[Any]],
    dependencies: Sequence[tuple[Any, Any]],
    *,
    title: str = "ORION framework map",
):
    """Convenience wrapper for grouped framework components."""

    nodes: list[str] = []
    groups: dict[str, str] = {}
    for group, members in components.items():
        for member in members:
            node = str(member)
            nodes.append(node)
            groups[node] = str(group)
    return plot_dependency_diagram(nodes, dependencies, groups=groups, title=title)
