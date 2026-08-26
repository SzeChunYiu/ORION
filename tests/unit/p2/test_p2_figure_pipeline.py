"""Figure P2-1 must agree with the state machine it illustrates.

The figure asserts a negative — no route outcome and no coverage diagnostic
reaches task closure — so the tests check the absence as strictly as the
presence, and check that the two renderings and the two committed artifacts
cannot drift apart.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
FIGURES = (
    ROOT / "papers" / "orion-12-open-world-scientific-discovery" / "manuscript" / "figures"
)
MODULE_PATH = FIGURES / "pipeline_figure.py"


def _module():
    spec = importlib.util.spec_from_file_location("p2_pipeline_figure", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Register before executing: @dataclass resolves annotations through
    # sys.modules[cls.__module__], which is absent for a spec-loaded module and
    # fails at class-creation time rather than anywhere near the cause.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_committed_artifacts_match_a_fresh_render():
    module = _module()
    svg = (FIGURES / "P2-1_pipeline.svg").read_text(encoding="utf-8")
    tikz = (FIGURES / "P2-1_pipeline.tex").read_text(encoding="utf-8")
    assert svg == module.render_svg(module.PIPELINE)
    assert tikz == module.render_tikz(module.PIPELINE) + "\n"


def test_both_renderings_carry_every_node_and_edge():
    module = _module()
    svg = module.render_svg(module.PIPELINE)
    tikz = module.render_tikz(module.PIPELINE)
    for node in module.PIPELINE.nodes:
        for line in node.label.split("\n"):
            assert line in svg, f"SVG missing node text: {line}"
            assert line in tikz, f"TikZ missing node text: {line}"
    for edge in module.PIPELINE.edges:
        assert f"({edge.source}) --" in tikz
        assert f"({edge.target});" in tikz or f"({edge.target})" in tikz
    # every drawn edge produces one connector, plus the forbidden edge
    assert svg.count("<polyline ") == len(module.PIPELINE.edges) + len(
        module.PIPELINE.forbidden_edges
    )
    # waypoints route connectors; they must never be drawn as boxes
    waypoints = [item for item in module.PIPELINE.nodes if not item.is_drawn]
    assert waypoints, "the layout relies on waypoint routing"
    assert svg.count("<rect ") == 1 + len(
        [item for item in module.PIPELINE.nodes if item.is_drawn]
    ) + len([edge for edge in (*module.PIPELINE.edges, *module.PIPELINE.forbidden_edges) if edge.label])
    for waypoint in waypoints:
        line = next(row for row in tikz.splitlines() if f"({waypoint.node_id})" in row and "\\node" in row)
        assert line.startswith("  \\node[waypoint]") and line.endswith("{};"), (
            f"a waypoint must render as an empty coordinate, got: {line}"
        )


def test_the_four_pipeline_stages_are_separated():
    module = _module()
    ids = {node.node_id for node in module.PIPELINE.nodes}
    assert {"retrieval", "screening", "routestop", "closure"} <= ids


def test_route_stop_does_not_reach_task_closure():
    module = _module()
    drawn = {(edge.source, edge.target) for edge in module.PIPELINE.edges}
    assert ("routestop", "closure") not in drawn, (
        "a drawn route-stop -> closure edge would contradict fail-closed stopping"
    )
    assert ("routestop", "closure") in {
        (edge.source, edge.target) for edge in module.PIPELINE.forbidden_edges
    }
    svg = module.render_svg(module.PIPELINE)
    assert "url(#blocked)" in svg, "the forbidden edge must render with the blocked marker"


def test_coverage_reaches_closure_only_as_an_advisory_edge():
    module = _module()
    coverage_edges = [
        edge
        for edge in module.PIPELINE.edges
        if edge.source == "coverage" and edge.target == "closure"
    ]
    assert len(coverage_edges) == 1
    assert coverage_edges[0].style == "dashed"
    assert "advisory" in coverage_edges[0].label


def test_unavailable_routes_become_an_obligation_that_gates_closure():
    module = _module()
    drawn = {(edge.source, edge.target) for edge in module.PIPELINE.edges}
    assert ("routestop", "obligations") in drawn
    assert ("obligations", "closure") in drawn


def test_specification_rejects_malformed_figures():
    module = _module()
    node_a = module.Node("a", "A", 0, 0)
    node_b = module.Node("b", "B", 1, 0)

    # no-alarm case: a well-formed spec must construct without complaint
    module.FigureSpec("ok", (node_a, node_b), (module.Edge("a", "b"),))

    with pytest.raises(ValueError):
        module.FigureSpec("dupe", (node_a, node_a), ())
    with pytest.raises(ValueError):
        module.FigureSpec("dangling", (node_a,), (module.Edge("a", "missing"),))
    with pytest.raises(ValueError):
        module.FigureSpec(
            "contradiction",
            (node_a, node_b),
            (module.Edge("a", "b"),),
            forbidden_edges=(module.Edge("a", "b"),),
        )
