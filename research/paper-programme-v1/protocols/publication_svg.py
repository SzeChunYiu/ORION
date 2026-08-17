#!/usr/bin/env python3
"""Small dependency-free SVG helpers for ORION publication artifacts.

This utility is deliberately generic: paper-specific analysis code should first
produce frozen CSV/JSON summaries from normalized raw records, then render those
summaries. It never invents missing observations or fills CANNOT_CHECK cells.

Exports:
- bar_chart          — single series bar chart (with optional color_key)
- grouped_bar_chart  — paired grouped bars (two bars per label)
- scatter_plot       — labelled scatter
- heatmap            — matrix with optional row/col order and custom format
"""
from __future__ import annotations

import argparse
import csv
import html
import json
from pathlib import Path
from typing import Iterable


WIDTH = 900
HEIGHT = 560
MARGIN_LEFT = 100
MARGIN_RIGHT = 40
MARGIN_TOP = 65
MARGIN_BOTTOM = 100


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _scale(value: float, lo: float, hi: float, out_lo: float, out_hi: float) -> float:
    if hi == lo:
        return (out_lo + out_hi) / 2.0
    return out_lo + (value - lo) * (out_hi - out_lo) / (hi - lo)


def _svg_start(title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{WIDTH/2}" y="32" text-anchor="middle" font-family="sans-serif" font-size="20">{_esc(title)}</text>',
    ]


def _axes(lines: list[str], *, y_min: float, y_max: float, y_label: str, y_ticks: int = 5) -> None:
    x0, y0 = MARGIN_LEFT, HEIGHT - MARGIN_BOTTOM
    x1, y1 = WIDTH - MARGIN_RIGHT, MARGIN_TOP
    lines.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="black"/>')
    lines.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="black"/>')
    for i in range(y_ticks + 1):
        value = y_min + (y_max - y_min) * i / y_ticks
        y = _scale(value, y_min, y_max, y0, y1)
        lines.append(f'<line x1="{x0-5}" y1="{y:.2f}" x2="{x0}" y2="{y:.2f}" stroke="black"/>')
        lines.append(f'<text x="{x0-10}" y="{y+4:.2f}" text-anchor="end" font-family="sans-serif" font-size="12">{value:.3g}</text>')
    lines.append(f'<text x="22" y="{(y0+y1)/2}" transform="rotate(-90 22 {(y0+y1)/2})" text-anchor="middle" font-family="sans-serif" font-size="14">{_esc(y_label)}</text>')


def bar_chart(rows: Iterable[dict[str, object]], *, label_key: str, value_key: str, title: str, y_label: str, color_key: str | None = None) -> str:
    data = [(str(row[label_key]), float(row[value_key])) for row in rows]
    if not data:
        raise ValueError("bar chart requires non-empty data")
    values = [v for _, v in data]
    y_min = min(0.0, min(values))
    y_max = max(values)
    if y_max == y_min:
        y_max = y_min + 1.0
    lines = _svg_start(title)
    _axes(lines, y_min=y_min, y_max=y_max, y_label=y_label)
    x0, x1 = MARGIN_LEFT, WIDTH - MARGIN_RIGHT
    y0, y1 = HEIGHT - MARGIN_BOTTOM, MARGIN_TOP
    slot = (x1 - x0) / len(data)
    bar_w = max(4.0, slot * 0.62)
    zero_y = _scale(0.0, y_min, y_max, y0, y1)
    for i, (label, value) in enumerate(data):
        cx = x0 + slot * (i + 0.5)
        vy = _scale(value, y_min, y_max, y0, y1)
        top, bottom = min(vy, zero_y), max(vy, zero_y)
        color = "#666"
        if color_key:
            color = str(list(rows)[i].get(color_key, "#666"))
        lines.append(f'<rect x="{cx-bar_w/2:.2f}" y="{top:.2f}" width="{bar_w:.2f}" height="{max(1.0,bottom-top):.2f}" fill="{color}"/>')
        lines.append(f'<text x="{cx:.2f}" y="{y0+18}" transform="rotate(35 {cx:.2f} {y0+18})" text-anchor="start" font-family="sans-serif" font-size="11">{_esc(label)}</text>')
    lines.append('</svg>')
    return "\n".join(lines)


def grouped_bar_chart(rows: list[dict[str, object]], *, label_key: str, bar_keys: list[tuple[str, str, str]], title: str, y_label: str) -> str:
    """Grouped bar chart with two bars per label.

    bar_keys is a list of (key, color, legend_label) tuples.
    e.g., [("coverage", "#2196F3", "Coverage"), ("false_promotion", "#FF9800", "False promotion")]
    """
    if not rows:
        raise ValueError("grouped bar chart requires non-empty data")
    all_values = [float(row[k]) for row in rows for k, _, _ in bar_keys]
    y_min = min(0.0, min(all_values))
    y_max = max(all_values)
    if y_max == y_min:
        y_max = y_min + 1.0
    lines = _svg_start(title)
    _axes(lines, y_min=y_min, y_max=y_max, y_label=y_label)
    x0, x1 = MARGIN_LEFT, WIDTH - MARGIN_RIGHT
    y0, y1 = HEIGHT - MARGIN_BOTTOM, MARGIN_TOP
    n_groups = len(rows)
    n_bars = len(bar_keys)
    slot = (x1 - x0) / n_groups
    group_w = slot * 0.8
    bar_w = group_w / n_bars
    zero_y = _scale(0.0, y_min, y_max, y0, y1)
    for i, row in enumerate(rows):
        gx = x0 + slot * (i + 0.5) - group_w / 2
        for j, (key, color, _) in enumerate(bar_keys):
            value = float(row[key])
            cx = gx + j * bar_w + bar_w / 2
            vy = _scale(value, y_min, y_max, y0, y1)
            top, bottom = min(vy, zero_y), max(vy, zero_y)
            lines.append(f'<rect x="{cx-bar_w/2:.2f}" y="{top:.2f}" width="{bar_w:.2f}" height="{max(1.0,bottom-top):.2f}" fill="{color}"/>')
    # Labels and legend
    for i, row in enumerate(rows):
        cx = x0 + slot * (i + 0.5)
        lines.append(f'<text x="{cx:.2f}" y="{y0+18}" transform="rotate(35 {cx:.2f} {y0+18})" text-anchor="start" font-family="sans-serif" font-size="11">{_esc(str(row[label_key]))}</text>')
    # Legend
    leg_x = x1 - 20
    leg_y = y1 - 10
    for j, (_, color, legend_label) in enumerate(bar_keys):
        ly = leg_y + j * 20
        lines.append(f'<rect x="{leg_x-15}" y="{ly-7}" width="12" height="12" fill="{color}"/>')
        lines.append(f'<text x="{leg_x}" y="{ly+3}" font-family="sans-serif" font-size="11">{_esc(legend_label)}</text>')
    lines.append('</svg>')
    return "\n".join(lines)


def scatter_plot(rows: Iterable[dict[str, object]], *, x_key: str, y_key: str, label_key: str, title: str, x_label: str, y_label: str) -> str:
    data = [(float(row[x_key]), float(row[y_key]), str(row[label_key])) for row in rows]
    if not data:
        raise ValueError("scatter plot requires non-empty data")
    xs, ys = [x for x, _, _ in data], [y for _, y, _ in data]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    if x_min == x_max:
        x_max = x_min + 1.0
    if y_min == y_max:
        y_max = y_min + 1.0
    lines = _svg_start(title)
    _axes(lines, y_min=y_min, y_max=y_max, y_label=y_label)
    x0, x1 = MARGIN_LEFT, WIDTH - MARGIN_RIGHT
    y0, y1 = HEIGHT - MARGIN_BOTTOM, MARGIN_TOP
    lines.append(f'<text x="{(x0+x1)/2}" y="{HEIGHT-20}" text-anchor="middle" font-family="sans-serif" font-size="14">{_esc(x_label)}</text>')
    for x, y, label in data:
        sx = _scale(x, x_min, x_max, x0, x1)
        sy = _scale(y, y_min, y_max, y0, y1)
        lines.append(f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="5" fill="#555"/>')
        lines.append(f'<text x="{sx+7:.2f}" y="{sy-7:.2f}" font-family="sans-serif" font-size="11">{_esc(label)}</text>')
    lines.append('</svg>')
    return "\n".join(lines)


def heatmap(rows: list[dict[str, object]], *, row_key: str, col_key: str, value_key: str, title: str,
            row_order: list[str] | None = None, col_order: list[str] | None = None, fmt: str = ".3g") -> str:
    if not rows:
        raise ValueError("heatmap requires non-empty data")
    row_names = row_order or sorted({str(r[row_key]) for r in rows})
    col_names = col_order or sorted({str(r[col_key]) for r in rows})
    values = [float(r[value_key]) for r in rows]
    v_min, v_max = min(values), max(values)
    table = {(str(r[row_key]), str(r[col_key])): float(r[value_key]) for r in rows}
    lines = _svg_start(title)
    x0, y0 = MARGIN_LEFT + 80, MARGIN_TOP + 30
    cell_w = (WIDTH - x0 - MARGIN_RIGHT) / max(1, len(col_names))
    cell_h = (HEIGHT - y0 - MARGIN_BOTTOM) / max(1, len(row_names))
    for c, name in enumerate(col_names):
        x = x0 + (c + 0.5) * cell_w
        lines.append(f'<text x="{x:.2f}" y="{y0-10}" transform="rotate(-30 {x:.2f} {y0-10})" text-anchor="start" font-family="sans-serif" font-size="11">{_esc(name)}</text>')
    for r, name in enumerate(row_names):
        y = y0 + (r + 0.5) * cell_h
        lines.append(f'<text x="{x0-10}" y="{y+4:.2f}" text-anchor="end" font-family="sans-serif" font-size="11">{_esc(name)}</text>')
        for c, col in enumerate(col_names):
            value = table.get((name, col))
            x = x0 + c * cell_w
            cy = y0 + r * cell_h
            if value is None:
                fill = "#eee"
                text = "NA"
            else:
                fraction = 0.5 if v_max == v_min else (value-v_min)/(v_max-v_min)
                shade = int(245 - 170 * fraction)
                fill = f'rgb({shade},{shade},{shade})'
                text = f'{value:{fmt}}'
            lines.append(f'<rect x="{x:.2f}" y="{cy:.2f}" width="{cell_w:.2f}" height="{cell_h:.2f}" fill="{fill}" stroke="white"/>')
            lines.append(f'<text x="{x+cell_w/2:.2f}" y="{cy+cell_h/2+4:.2f}" text-anchor="middle" font-family="sans-serif" font-size="10">{text}</text>')
    lines.append('</svg>')
    return "\n".join(lines)


def _load_rows(path: Path) -> list[dict[str, object]]:
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("JSON input must be a list of row objects")
        return payload
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="kind", required=True)
    for name in ("bar", "scatter", "heatmap"):
        p = sub.add_parser(name)
        p.add_argument("input", type=Path)
        p.add_argument("output", type=Path)
        p.add_argument("--title", required=True)
    bar = sub.choices["bar"]
    bar.add_argument("--label", required=True)
    bar.add_argument("--value", required=True)
    bar.add_argument("--y-label", required=True)
    scatter = sub.choices["scatter"]
    scatter.add_argument("--x", required=True)
    scatter.add_argument("--y", required=True)
    scatter.add_argument("--label", required=True)
    scatter.add_argument("--x-label", required=True)
    scatter.add_argument("--y-label", required=True)
    hm = sub.choices["heatmap"]
    hm.add_argument("--row", required=True)
    hm.add_argument("--column", required=True)
    hm.add_argument("--value", required=True)
    args = parser.parse_args()
    rows = _load_rows(args.input)
    if args.kind == "bar":
        svg = bar_chart(rows, label_key=args.label, value_key=args.value, title=args.title, y_label=args.y_label)
    elif args.kind == "scatter":
        svg = scatter_plot(rows, x_key=args.x, y_key=args.y, label_key=args.label, title=args.title, x_label=args.x_label, y_label=args.y_label)
    else:
        svg = heatmap(rows, row_key=args.row, col_key=args.column, value_key=args.value, title=args.title)
    args.output.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
