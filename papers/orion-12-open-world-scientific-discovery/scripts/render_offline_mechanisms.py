#!/usr/bin/env python3
"""Render or verify P2-3/P2-4/P2-5 from the frozen offline mechanism snapshot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PAPER = Path(__file__).resolve().parents[1]
SOURCE = PAPER / "evidence" / "offline_results" / "OFFLINE_MECHANISMS_V1.json"
FIGURES = PAPER / "manuscript" / "figures"
ROUTES = ("LEXICAL", "SEMANTIC", "CITATION", "REFORMULATION", "RESTRICTED")
PRECISION_TIERS = (
    ("TIER_A_full", 1068),
    ("TIER_B_committed", 385),
    ("TIER_C_reduced", 171),
    ("TIER_D_minimum_inferential", 97),
)


def _number(value: float) -> str:
    text = f"{float(value):.6f}".rstrip("0").rstrip(".")
    return text or "0"


def _expected_authority(n_tasks: int) -> str:
    for name, required in PRECISION_TIERS:
        if n_tasks >= required:
            return name
    return "DESCRIPTIVE_ONLY"


def _scope(data: dict[str, Any], *, detail: str) -> str:
    return f"{data['n_tasks']} frozen tasks; {detail}; descriptive mechanism summary"


def _validate(data: dict[str, Any]) -> None:
    if data.get("schema_version") != "orion.p2.offline-mechanisms.v1":
        raise ValueError("unexpected offline mechanism schema")
    n_tasks = data.get("n_tasks")
    if not isinstance(n_tasks, int) or isinstance(n_tasks, bool) or n_tasks < 1:
        raise ValueError("offline mechanism snapshot requires a positive integer n_tasks")
    expected = _expected_authority(n_tasks)
    if data.get("analysis_authority") != expected:
        raise ValueError(
            "offline mechanism authority does not match frozen precision tiers: "
            f"n={n_tasks} requires {expected}"
        )
    if len(str(data.get("source_record_digest_sha256", ""))) != 64:
        raise ValueError("source record digest missing")
    if len(str(data.get("source_raw_artifact_hash_list_digest_sha256", ""))) != 64:
        raise ValueError("source artifact digest missing")


def _trajectory(data: dict[str, Any], system: str) -> list[dict[str, float]]:
    points = data["trajectory_systems"][system]
    if [point["queries"] for point in points] != list(range(13)):
        raise ValueError(f"{system}: trajectory must cover frozen query counts 0..12")
    return points


def render_p2_3_tex(data: dict[str, Any]) -> str:
    orion = _trajectory(data, "orion_full")
    baseline = _trajectory(data, "protocol_driven_systematic_review")
    coords_o = " ".join(
        f"({int(point['queries'])},{_number(point['mean_complete_gold_recall'])})"
        for point in orion
    )
    coords_b = " ".join(
        f"({int(point['queries'])},{_number(point['mean_complete_gold_recall'])})"
        for point in baseline
    )
    scope = _scope(data, detail="repeats collapsed")
    scope_tex = scope.replace("_", r"\_")
    return "\n".join(
        [
            "% GENERATED from evidence/offline_results/OFFLINE_MECHANISMS_V1.json",
            r"\begin{tikzpicture}[x=0.48cm,y=5.0cm]",
            r"\draw[->] (0,0) -- (12.7,0) node[right]{search queries};",
            r"\draw[->] (0,0) -- (0,1.08) node[above]{complete-gold recall};",
            r"\foreach \x in {0,2,4,6,8,10,12} \draw (\x,0.012) -- (\x,-0.012) node[below]{\x};",
            r"\foreach \y/\lab in {0/0,0.25/.25,0.5/.50,0.75/.75,1/1.0} \draw (0.10,\y) -- (-0.10,\y) node[left]{\lab};",
            rf"\draw[thick] plot coordinates {{{coords_o}}};",
            rf"\draw[thick,dashed] plot coordinates {{{coords_b}}};",
            r"\node[anchor=west] at (8.3,0.94) {ORION full};",
            r"\node[anchor=west] at (8.3,0.69) {Protocol SLR};",
            rf"\node[anchor=west,font=\small] at (0,1.16) {{{scope_tex}}};",
            r"\end{tikzpicture}",
        ]
    ) + "\n"


def render_p2_3_svg(data: dict[str, Any]) -> str:
    orion = _trajectory(data, "orion_full")
    baseline = _trajectory(data, "protocol_driven_systematic_review")
    width, height = 720, 430
    left, bottom = 70, 360
    plot_width, plot_height = 600, 300

    def points(values: list[dict[str, float]]) -> str:
        return " ".join(
            f"{left + float(point['queries']) / 12 * plot_width:.2f},"
            f"{bottom - float(point['mean_complete_gold_recall']) * plot_height:.2f}"
            for point in values
        )

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{left + plot_width + 10}" y2="{bottom}" stroke="#111" stroke-width="2"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{bottom - plot_height - 10}" stroke="#111" stroke-width="2"/>',
        '<text x="650" y="393" font-family="sans-serif" font-size="14">search queries</text>',
        '<text x="16" y="34" font-family="sans-serif" font-size="14">recall</text>',
    ]
    for query_count in range(0, 13, 2):
        x = left + query_count / 12 * plot_width
        lines.append(
            f'<line x1="{x:.2f}" y1="{bottom - 5}" x2="{x:.2f}" y2="{bottom + 5}" stroke="#111"/>'
        )
        lines.append(
            f'<text x="{x:.2f}" y="{bottom + 24}" text-anchor="middle" font-family="sans-serif" font-size="12">{query_count}</text>'
        )
    for value, label in ((0, "0"), (0.25, ".25"), (0.5, ".50"), (0.75, ".75"), (1, "1.0")):
        y = bottom - value * plot_height
        lines.append(
            f'<line x1="{left - 5}" y1="{y:.2f}" x2="{left + 5}" y2="{y:.2f}" stroke="#111"/>'
        )
        lines.append(
            f'<text x="{left - 12}" y="{y + 4:.2f}" text-anchor="end" font-family="sans-serif" font-size="12">{label}</text>'
        )
    lines.extend(
        [
            f'<polyline points="{points(orion)}" fill="none" stroke="#111" stroke-width="3"/>',
            f'<polyline points="{points(baseline)}" fill="none" stroke="#777" stroke-width="3" stroke-dasharray="8 6"/>',
            '<text x="500" y="72" font-family="sans-serif" font-size="13">ORION full</text>',
            '<text x="500" y="166" font-family="sans-serif" font-size="13">Protocol SLR</text>',
            f'<text x="70" y="22" font-family="sans-serif" font-size="12">{_scope(data, detail="deterministic repeats collapsed")}</text>',
            '</svg>',
        ]
    )
    return "\n".join(lines) + "\n"


def render_p2_4_tex(data: dict[str, Any]) -> str:
    source = data["orion_route_first_relevant_contribution"]
    labels = {
        "LEXICAL": "Lexical",
        "SEMANTIC": "Semantic",
        "CITATION": "Citation",
        "REFORMULATION": "Reformulation",
        "RESTRICTED": "Restricted",
    }
    verdict_labels = {
        "REFERENCE": "reference",
        "INDEPENDENT": "independent",
        "SHARED_BACKEND": "shared backend",
    }
    lines = [
        "% GENERATED from evidence/offline_results/OFFLINE_MECHANISMS_V1.json",
        r"\begin{tikzpicture}[x=1.35cm,y=1.15cm]",
        r"\draw[->] (0,0) -- (5.6,0);",
        r"\draw[->] (0,0) -- (0,3.45) node[above]{mean first relevant contribution};",
        r"\foreach \y in {0,1,2,3} \draw (0.06,\y) -- (-0.06,\y) node[left]{\y};",
    ]
    for index, route in enumerate(ROUTES):
        x = index + 0.4
        value = float(source[route]["mean_first_relevant_contribution"])
        verdict = source[route]["independence_vs_lexical"]
        fill = "black!70" if verdict in {"REFERENCE", "INDEPENDENT"} else "black!30"
        lines.extend(
            [
                rf"\fill[{fill}] ({x:.1f},0) rectangle ({x + 0.6:.1f},{_number(value)});",
                rf"\node[rotate=35,anchor=east] at ({x + 0.3:.1f},-0.15) {{{labels[route]}}};",
                rf"\node[anchor=south,font=\scriptsize] at ({x + 0.3:.1f},{_number(value)}) {{{_number(value)}}};",
                rf"\node[rotate=90,anchor=west,font=\scriptsize] at ({x + 0.3:.1f},0.10) {{{verdict_labels[verdict]}}};",
            ]
        )
    scope = _scope(data, detail="contribution counted by content identity")
    scope_tex = scope.replace("_", r"\_")
    lines.extend(
        [
            rf"\node[anchor=west,font=\small] at (0,3.70) {{{scope_tex}}};",
            r"\end{tikzpicture}",
        ]
    )
    return "\n".join(lines) + "\n"


def render_p2_4_svg(data: dict[str, Any]) -> str:
    source = data["orion_route_first_relevant_contribution"]
    labels = {
        "LEXICAL": "Lexical",
        "SEMANTIC": "Semantic",
        "CITATION": "Citation",
        "REFORMULATION": "Reformulation",
        "RESTRICTED": "Restricted",
    }
    verdict_labels = {
        "REFERENCE": "reference",
        "INDEPENDENT": "independent",
        "SHARED_BACKEND": "shared backend",
    }
    width, height = 760, 450
    left, bottom, plot_height = 70, 350, 270
    bar_width, gap = 80, 38
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<line x1="{left}" y1="{bottom}" x2="720" y2="{bottom}" stroke="#111" stroke-width="2"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="55" stroke="#111" stroke-width="2"/>',
        '<text x="16" y="30" font-family="sans-serif" font-size="13">mean contribution</text>',
        f'<text x="70" y="20" font-family="sans-serif" font-size="12">{_scope(data, detail="content-identity first relevant contribution")}</text>',
    ]
    for y_value in (0, 1, 2, 3):
        y = bottom - y_value / 3 * plot_height
        lines.append(
            f'<line x1="{left - 5}" y1="{y:.2f}" x2="{left + 5}" y2="{y:.2f}" stroke="#111"/>'
        )
        lines.append(
            f'<text x="{left - 12}" y="{y + 4:.2f}" text-anchor="end" font-family="sans-serif" font-size="12">{y_value}</text>'
        )
    for index, route in enumerate(ROUTES):
        value = float(source[route]["mean_first_relevant_contribution"])
        verdict = source[route]["independence_vs_lexical"]
        x = left + 45 + index * (bar_width + gap)
        bar_height = value / 3 * plot_height
        y = bottom - bar_height
        fill = "#333" if verdict in {"REFERENCE", "INDEPENDENT"} else "#aaa"
        lines.extend(
            [
                f'<rect x="{x}" y="{y:.2f}" width="{bar_width}" height="{bar_height:.2f}" fill="{fill}"/>',
                f'<text x="{x + bar_width / 2:.2f}" y="{y - 8:.2f}" text-anchor="middle" font-family="sans-serif" font-size="12">{_number(value)}</text>',
                f'<text x="{x + bar_width / 2:.2f}" y="{bottom + 22}" text-anchor="middle" font-family="sans-serif" font-size="12">{labels[route]}</text>',
                f'<text x="{x + bar_width / 2:.2f}" y="{bottom + 40}" text-anchor="middle" font-family="sans-serif" font-size="10">{verdict_labels[verdict]}</text>',
            ]
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def _verdict_label(verdict: str) -> str:
    if verdict == "SHARED_BACKEND":
        return "shared backend"
    if verdict == "INDEPENDENT":
        return "independent"
    if verdict == "SAME_ROUTE":
        return "same route"
    raise ValueError(f"unexpected route verdict: {verdict}")


def render_p2_5_tex(data: dict[str, Any]) -> str:
    matrix = data["orion_content_overlap_matrix"]
    labels = {
        "LEXICAL": "Lex",
        "SEMANTIC": "Sem",
        "CITATION": "Cit",
        "REFORMULATION": "Ref",
        "RESTRICTED": "Res",
    }
    lines = [
        "% GENERATED from evidence/offline_results/OFFLINE_MECHANISMS_V1.json",
        r"\begin{tikzpicture}[x=1.25cm,y=1.0cm]",
    ]
    for column, route in enumerate(ROUTES):
        lines.append(
            rf"\node[rotate=45,anchor=west] at ({column + 1},5.4) {{{labels[route]}}};"
        )
    for row, left_route in enumerate(ROUTES):
        y = 4 - row
        lines.append(
            rf"\node[anchor=east] at (0.65,{y + 0.35:.2f}) {{{labels[left_route]}}};"
        )
        for column, right_route in enumerate(ROUTES):
            x = column + 0.7
            cell = matrix[left_route][right_route]
            value = float(cell["mean_content_jaccard"])
            verdict = cell["independence_verdict"]
            fill = "black!70" if value >= 0.5 else ("black!25" if value > 0 else "white")
            text_color = "white" if value >= 0.5 else "black"
            lines.extend(
                [
                    rf"\filldraw[fill={fill},draw=black!35] ({x:.2f},{y:.2f}) rectangle ({x + 0.8:.2f},{y + 0.7:.2f});",
                    rf"\node[text={text_color},font=\scriptsize] at ({x + 0.4:.2f},{y + 0.42:.2f}) {{{_number(value)}}};",
                ]
            )
            if left_route != right_route:
                short = "shared" if verdict == "SHARED_BACKEND" else "ind."
                lines.append(
                    rf"\node[text={text_color},font=\tiny] at ({x + 0.4:.2f},{y + 0.16:.2f}) {{{short}}};"
                )
    compact_scope = (
        f"{data['n_tasks']} frozen tasks; content identity; repeats collapsed; "
        f"authority {data['analysis_authority']}"
    )
    compact_scope_tex = compact_scope.replace("_", r"\_")
    lines.extend(
        [
            r"\node[anchor=west,font=\small] at (0.7,-0.55) {cell = mean task-level content Jaccard; ind. = structurally independent};",
            rf"\node[anchor=west,font=\scriptsize,text width=6.8cm,align=left] at (0.7,-0.95) {{{compact_scope_tex}}};",
            r"\end{tikzpicture}",
        ]
    )
    return "\n".join(lines) + "\n"


def render_p2_5_svg(data: dict[str, Any]) -> str:
    matrix = data["orion_content_overlap_matrix"]
    labels = {
        "LEXICAL": "Lexical",
        "SEMANTIC": "Semantic",
        "CITATION": "Citation",
        "REFORMULATION": "Reform.",
        "RESTRICTED": "Restricted",
    }
    width, height = 690, 590
    cell_size, left, top = 88, 150, 80
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="150" y="24" font-family="sans-serif" font-size="12">Mean task-level content Jaccard; structural independence shown in each off-diagonal cell</text>',
    ]
    for column, route in enumerate(ROUTES):
        x = left + column * cell_size + cell_size / 2
        lines.append(
            f'<text x="{x:.2f}" y="64" text-anchor="middle" font-family="sans-serif" font-size="11">{labels[route]}</text>'
        )
    for row, left_route in enumerate(ROUTES):
        y = top + row * cell_size + cell_size / 2
        lines.append(
            f'<text x="{left - 12}" y="{y + 4:.2f}" text-anchor="end" font-family="sans-serif" font-size="11">{labels[left_route]}</text>'
        )
        for column, right_route in enumerate(ROUTES):
            x0 = left + column * cell_size
            y0 = top + row * cell_size
            cell = matrix[left_route][right_route]
            value = float(cell["mean_content_jaccard"])
            verdict = cell["independence_verdict"]
            fill = "#555" if value >= 0.5 else ("#bbb" if value > 0 else "#fff")
            text_color = "#fff" if value >= 0.5 else "#111"
            lines.extend(
                [
                    f'<rect x="{x0}" y="{y0}" width="{cell_size}" height="{cell_size}" fill="{fill}" stroke="#aaa"/>',
                    f'<text x="{x0 + cell_size / 2:.2f}" y="{y0 + 38:.2f}" text-anchor="middle" fill="{text_color}" font-family="sans-serif" font-size="12">{_number(value)}</text>',
                ]
            )
            if left_route != right_route:
                label = _verdict_label(verdict)
                lines.append(
                    f'<text x="{x0 + cell_size / 2:.2f}" y="{y0 + 57:.2f}" text-anchor="middle" fill="{text_color}" font-family="sans-serif" font-size="9">{label}</text>'
                )
    lines.extend(
        [
            '<text x="150" y="552" font-family="sans-serif" font-size="11">Diagonal is self-overlap. Lexical/Reformulation share a backend and are not independent.</text>',
            f'<text x="150" y="570" font-family="sans-serif" font-size="11">{_scope(data, detail="content identity; deterministic repeats collapsed")}</text>',
            '</svg>',
        ]
    )
    return "\n".join(lines) + "\n"


def render_all(data: dict[str, Any]) -> dict[Path, str]:
    _validate(data)
    return {
        FIGURES / "P2-3_cumulative_discovery.tex": render_p2_3_tex(data),
        FIGURES / "P2-3_cumulative_discovery.svg": render_p2_3_svg(data),
        FIGURES / "P2-4_route_contribution.tex": render_p2_4_tex(data),
        FIGURES / "P2-4_route_contribution.svg": render_p2_4_svg(data),
        FIGURES / "P2-5_route_overlap.tex": render_p2_5_tex(data),
        FIGURES / "P2-5_route_overlap.svg": render_p2_5_svg(data),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write generated figure files")
    parser.add_argument("--check", action="store_true", help="verify committed figure files")
    args = parser.parse_args(argv)
    if not args.write and not args.check:
        args.check = True

    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    outputs = render_all(data)
    if args.write:
        FIGURES.mkdir(parents=True, exist_ok=True)
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(PAPER)}")
    if args.check:
        drifted: list[str] = []
        for path, content in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                drifted.append(str(path.relative_to(PAPER)))
        if drifted:
            print("offline mechanism figures drifted: " + ", ".join(drifted), file=sys.stderr)
            return 1
        print("offline mechanism figures match the frozen mechanism projection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
