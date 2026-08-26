#!/usr/bin/env python3
"""Figure P2-1: the discovery pipeline, rendered from one specification.

The figure separates retrieval, screening, route stopping and task closure, and
shows which edges are *not* present: no route outcome reaches task closure, and
the coverage diagnostic reaches it only as advice. That absence is the paper's
claim, so the figure is generated from a specification a test can read rather
than drawn by hand in two places.

Two renderers share that specification: SVG for review inside the repository and
TikZ for the manuscript. A hand-drawn manuscript figure would drift from the SVG
the moment either was edited, and a figure that disagrees with the state machine
it illustrates is worse than no figure.

Layout is explicit rather than automatic. Edges may route through waypoints so
that no connector crosses a box, and edge labels carry an opaque backing so they
stay readable where lines pass beneath them --- a reviewer reads the printed
figure, not the source.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Node:
    node_id: str
    label: str
    column: float
    row: float
    kind: str = "stage"  # stage | state | advisory | obligation | waypoint

    @property
    def is_drawn(self) -> bool:
        return self.kind != "waypoint"


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    label: str = ""
    style: str = "solid"  # solid | dashed (dashed = advisory, never authority)
    via: tuple[str, ...] = ()
    label_at: float = 0.5


@dataclass(frozen=True)
class FigureSpec:
    title: str
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]
    forbidden_edges: tuple[Edge, ...] = field(default=())

    def node(self, node_id: str) -> Node:
        for item in self.nodes:
            if item.node_id == node_id:
                return item
        raise KeyError(node_id)

    def path(self, edge: Edge) -> tuple[Node, ...]:
        return tuple(
            self.node(item) for item in (edge.source, *edge.via, edge.target)
        )

    def __post_init__(self) -> None:
        ids = [item.node_id for item in self.nodes]
        if len(ids) != len(set(ids)):
            raise ValueError("figure node ids must be unique")
        known = set(ids)
        for edge in (*self.edges, *self.forbidden_edges):
            for endpoint in (edge.source, edge.target, *edge.via):
                if endpoint not in known:
                    raise ValueError(f"edge references unknown node: {endpoint}")
        drawn = {(edge.source, edge.target) for edge in self.edges}
        for edge in self.forbidden_edges:
            if (edge.source, edge.target) in drawn:
                raise ValueError(
                    "an edge cannot be both drawn and marked forbidden: "
                    f"{edge.source} -> {edge.target}"
                )


PIPELINE = FigureSpec(
    title="P2-1  Discovery pipeline: retrieval, screening, route stop, task closure",
    nodes=(
        Node("question", "Research question\nand extraction frame", 0, 0),
        Node("routes", "Route ensemble\nkind / backend /\nquery derivation", 0, 1),
        Node("retrieval", "Retrieval\nraw provider records", 0, 2),
        Node("identity", "Content identity\nand alias closure", 0, 3),
        Node("readstate", "Question-conditioned\nread state", 0, 4),
        Node("screening", "Screening\neligibility decision", 0, 5),
        Node("routestop", "Route stop\ncontinue / reformulate /\nswitch / suspend / stop", 1.3, 5, kind="state"),
        Node("coverage", "Coverage diagnostic\ncapture-recapture", 2.6, 5, kind="advisory"),
        Node("obligations", "Open obligations\nunavailable or\ncensored routes", 1.3, 6.9, kind="obligation"),
        Node("closure", "Task closure\nfail-closed", 0, 8.3),
        Node("reopen_corner", "", 2.1, 1, kind="waypoint"),
        Node("advisory_corner", "", 2.6, 8.3, kind="waypoint"),
    ),
    edges=(
        Edge("question", "routes"),
        Edge("routes", "retrieval"),
        Edge("retrieval", "identity"),
        Edge("identity", "readstate", "dedup by content digest"),
        Edge("readstate", "screening", "read or legitimate reread"),
        Edge("screening", "routestop", "marginal novelty"),
        Edge("routestop", "coverage", "route captures"),
        Edge("routestop", "obligations", "suspend:\ntransport failure"),
        Edge("obligations", "closure", "must be empty", label_at=0.45),
        Edge("coverage", "closure", "advisory only", style="dashed", via=("advisory_corner",), label_at=0.35),
        Edge("routestop", "routes", "reopen trigger", via=("reopen_corner",), label_at=0.5),
    ),
    forbidden_edges=(
        Edge("routestop", "closure", "route stop cannot\ncertify task closure", label_at=0.55),
    ),
)

_KIND_FILL = {
    "stage": "#ffffff",
    "state": "#eceff4",
    "advisory": "#faf5e6",
    "obligation": "#f9ecec",
}

_COL_W = 230.0
_ROW_H = 96.0
_BOX_W = 168.0
_BOX_H = 62.0
_MARGIN = 30.0
_TITLE_H = 34.0


def _centre(node: Node) -> tuple[float, float]:
    return (
        _MARGIN + node.column * _COL_W + _BOX_W / 2,
        _TITLE_H + _MARGIN + node.row * _ROW_H + _BOX_H / 2,
    )


def _point_on_boundary(node: Node, towards: tuple[float, float]) -> tuple[float, float]:
    """Where a connector should leave a box, so arrowheads touch the edge.

    Lines drawn centre-to-centre disappear under the boxes at both ends and put
    the arrowhead inside the target, which is what made the first draft of this
    figure unreadable.
    """

    cx, cy = _centre(node)
    if not node.is_drawn:
        return cx, cy
    dx, dy = towards[0] - cx, towards[1] - cy
    if dx == 0 and dy == 0:
        return cx, cy
    half_w, half_h = _BOX_W / 2 + 3, _BOX_H / 2 + 3
    scale_x = half_w / abs(dx) if dx else float("inf")
    scale_y = half_h / abs(dy) if dy else float("inf")
    scale = min(scale_x, scale_y)
    return cx + dx * scale, cy + dy * scale


def _polyline(spec: FigureSpec, edge: Edge) -> list[tuple[float, float]]:
    nodes = spec.path(edge)
    points: list[tuple[float, float]] = []
    for index, node in enumerate(nodes):
        neighbour = nodes[index + 1] if index + 1 < len(nodes) else nodes[index - 1]
        points.append(_point_on_boundary(node, _centre(neighbour)))
    return points


def _label_anchor(points: list[tuple[float, float]], at: float) -> tuple[float, float]:
    spans = [
        (
            ((points[i + 1][0] - points[i][0]) ** 2 + (points[i + 1][1] - points[i][1]) ** 2)
            ** 0.5,
            i,
        )
        for i in range(len(points) - 1)
    ]
    total = sum(length for length, _ in spans) or 1.0
    walked = 0.0
    for length, index in spans:
        if walked + length >= total * at:
            remain = (total * at - walked) / (length or 1.0)
            x1, y1 = points[index]
            x2, y2 = points[index + 1]
            return x1 + (x2 - x1) * remain, y1 + (y2 - y1) * remain
        walked += length
    return points[-1]


def render_svg(spec: FigureSpec) -> str:
    drawn = [item for item in spec.nodes if item.is_drawn]
    width = _MARGIN * 2 + max(item.column for item in spec.nodes) * _COL_W + _BOX_W
    height = _TITLE_H + _MARGIN * 2 + max(item.row for item in drawn) * _ROW_H + _BOX_H
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'width="{width:.0f}" height="{height:.0f}" '
        'font-family="Helvetica,Arial,sans-serif">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#333"/></marker>'
        '<marker id="blocked" viewBox="0 0 10 10" refX="5" refY="5" '
        'markerWidth="8" markerHeight="8" orient="auto">'
        '<path d="M 1 1 L 9 9 M 9 1 L 1 9" stroke="#b03030" stroke-width="2" fill="none"/>'
        "</marker></defs>",
        f'<text x="{_MARGIN}" y="22" font-size="14" font-weight="bold">'
        f"{_esc(spec.title)}</text>",
    ]

    for edge in spec.edges:
        out.extend(_edge_svg(spec, edge, blocked=False))
    for edge in spec.forbidden_edges:
        out.extend(_edge_svg(spec, edge, blocked=True))

    for node in drawn:
        cx, cy = _centre(node)
        x, y = cx - _BOX_W / 2, cy - _BOX_H / 2
        fill = _KIND_FILL.get(node.kind, "#ffffff")
        out.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{_BOX_W}" height="{_BOX_H}" rx="5" '
            f'fill="{fill}" stroke="#333" stroke-width="1.1"/>'
        )
        lines = node.label.split("\n")
        first = cy - (len(lines) - 1) * 6.5 + 3.5
        for index, line in enumerate(lines):
            out.append(
                f'<text x="{cx:.1f}" y="{first + index * 13:.1f}" font-size="10.5" '
                f'text-anchor="middle">{_esc(line)}</text>'
            )
    out.append("</svg>")
    return "\n".join(out)


def _edge_svg(spec: FigureSpec, edge: Edge, *, blocked: bool) -> list[str]:
    points = _polyline(spec, edge)
    colour = "#b03030" if blocked else "#333"
    marker = "blocked" if blocked else "arrow"
    dash = ' stroke-dasharray="6 4"' if edge.style == "dashed" or blocked else ""
    path = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    parts = [
        f'<polyline points="{path}" fill="none" stroke="{colour}" stroke-width="1.2"'
        f'{dash} marker-end="url(#{marker})"/>'
    ]
    if edge.label:
        lx, ly = _label_anchor(points, edge.label_at)
        rows = edge.label.split("\n")
        half = max(len(item) for item in rows) * 2.6 + 4
        height = 12 * len(rows) + 2
        parts.append(
            f'<rect x="{lx - half:.1f}" y="{ly - height / 2:.1f}" width="{half * 2:.1f}" '
            f'height="{height}" fill="#ffffff" opacity="0.94"/>'
        )
        first = ly - (len(rows) - 1) * 6 + 3
        for index, row in enumerate(rows):
            parts.append(
                f'<text x="{lx:.1f}" y="{first + index * 12:.1f}" font-size="9" '
                f'text-anchor="middle" fill="{colour}">{_esc(row)}</text>'
            )
    return parts


def render_tikz(spec: FigureSpec) -> str:
    lines = [
        "% Generated by manuscript/figures/pipeline_figure.py in "
        "paper-02-open-world-scientific-discovery.",
        "% Do not edit by hand: regenerate so the figure cannot drift from the state machine.",
        # Scaled to the text column: a TikZ picture wider than \linewidth is an
        # overfull box in every journal template, and the figure would run into
        # the margin of the printed artifact a reviewer reads.
        "\\resizebox{\\linewidth}{!}{%",
        "\\begin{tikzpicture}[",
        "  x=2.6cm, y=-1.05cm, font=\\scriptsize, >=Latex,",
        "  stage/.style={draw, rounded corners=2pt, align=center, inner sep=3pt,"
        " text width=3.0cm, minimum height=0.95cm},",
        "  state/.style={stage, fill=black!6},",
        "  advisory/.style={stage, fill=yellow!10},",
        "  obligation/.style={stage, fill=red!7},",
        "  waypoint/.style={coordinate},",
        "  elabel/.style={fill=white, align=center, inner sep=1.5pt, font=\\tiny},",
        "  flow/.style={->},",
        "  advisoryflow/.style={->, dashed},",
        "  blocked/.style={red!60!black, dashed, thick},",
        "  cross/.style={red!60!black, font=\\scriptsize}]",
    ]
    for node in spec.nodes:
        label = "" if not node.is_drawn else node.label.replace("\n", "\\\\")
        lines.append(
            f"  \\node[{node.kind}] ({node.node_id}) at ({node.column * 1.6:g}, "
            f"{node.row * 1.35:g}) {{{label}}};"
        )
    for edge in (*spec.edges, *spec.forbidden_edges):
        blocked = edge in spec.forbidden_edges
        style = "blocked" if blocked else ("advisoryflow" if edge.style == "dashed" else "flow")
        hops = " -- ".join(f"({item})" for item in (edge.source, *edge.via, edge.target))
        if edge.label:
            first, rest = hops.split(" -- ", 1)
            label = _tex(edge.label).replace("\n", "\\\\")
            position = f"pos={edge.label_at:g}" if edge.label_at != 0.5 else "midway"
            marker = " node[cross, pos=0.75] {$\\times$}" if blocked else ""
            hops = f"{first} -- node[elabel, {position}] {{{label}}}{marker} {rest}"
        lines.append(f"  \\draw[{style}] {hops};")
    lines.append("\\end{tikzpicture}%")
    lines.append("}")
    return "\n".join(lines)


def _tex(value: str) -> str:
    return value.replace("_", "\\_").replace("&", "\\&").replace("%", "\\%")


def _esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="directory receiving P2-1_pipeline.svg and P2-1_pipeline.tex",
    )
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "P2-1_pipeline.svg").write_text(render_svg(PIPELINE), encoding="utf-8")
    (args.out_dir / "P2-1_pipeline.tex").write_text(render_tikz(PIPELINE) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'P2-1_pipeline.svg'}")
    print(f"wrote {args.out_dir / 'P2-1_pipeline.tex'}")


if __name__ == "__main__":
    main()
