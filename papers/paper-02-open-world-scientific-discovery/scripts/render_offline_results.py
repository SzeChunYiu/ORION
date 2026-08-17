#!/usr/bin/env python3
"""Render the completed P2 offline failure table and stopping-safety figure.

Publication-layer only: reads the immutable compact result summary and does not
recompute or change scientific outcomes.  Use ``--check`` in CI to prevent a
hand-edited table/figure from drifting from the archived summary.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
SUMMARY = PAPER / "evidence" / "offline_results" / "RESULTS_SUMMARY_V1.json"
TABLE = PAPER / "evidence" / "offline_results" / "TABLE_P2-3_failure_taxonomy.md"
SVG = PAPER / "manuscript" / "figures" / "P2-6_stopping_failures.svg"
TIKZ = PAPER / "manuscript" / "figures" / "P2-6_stopping_failures.tex"

ORDER = (
    "orion_full",
    "bm25_keyword",
    "dense_retrieval",
    "sparse_dense_hybrid",
    "one_pass_rag",
    "agentic_single_route",
    "protocol_driven_systematic_review",
    "adaptive_multiroute_exploratory",
    "no_route_independence_check",
    "no_question_conditioned_read_ledger",
    "route_stop_can_close_task",
    "no_unavailable_route_open_state",
    "coverage_diagnostic_controls_stopping",
    "no_content_identity_dedup",
)
FAILURE_KEYS = (
    "present_but_missed",
    "retrieved_but_unused",
    "screening_miss",
    "route_starvation",
    "transport_failure",
    "premature_closure",
    "budget_exhausted",
)


def render_table(payload: dict) -> str:
    systems = payload["systems"]
    lines = [
        "# Table P2-3 — offline controlled-index failure taxonomy",
        "",
        "**Authority:** `DESCRIPTIVE_ONLY`. These are terminal task classifications from the frozen 20-task offline companion after the three deterministic repeats are collapsed within task. They are not external benchmark results and carry no inferential interval.",
        "",
        "| System | PASS | CANNOT_CHECK | present-but-missed | retrieved-but-unused | screening miss | route starvation | transport failure | premature closure | budget exhausted |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for system_id in ORDER:
        system = systems[system_id]
        status = system["status_counts"]
        failures = system["failure_counts"]
        counts = [str(int(failures.get(key, 0))) for key in FAILURE_KEYS]
        lines.append(
            "| `{}` | {} | {} | {} |".format(
                system_id,
                int(status.get("PASS", 0)),
                int(status.get("CANNOT_CHECK", 0)),
                " | ".join(counts),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The evaluator has a fixed terminal-failure precedence. A task that is both route-starved and prematurely closed is classified as `premature_closure`, so a zero in a lower-precedence category does **not** prove the mechanism never occurred. The zero columns above mean only that those classes never became the **terminal highest-precedence label** in this collapsed archive.",
            "",
            "The publication-bearing distinctions are:",
            "",
            "- full ORION converts the one materially censored case into `CANNOT_CHECK` rather than a completeness claim;",
            "- the `no_unavailable_route_open_state` ablation converts that same safety case into a premature-closure failure;",
            "- the `no_content_identity_dedup` ablation creates five budget-exhaustion failures after duplicate work consumes the read budget;",
            "- simple/single-pass baselines terminate with premature closure because reachable relevant material remains on unexercised routes;",
            "- the exploratory adaptive comparator exposes three terminal `transport_failure` cases in addition to its premature closures.",
            "",
            "Source of record: `RESULTS_SUMMARY_V1.json`, itself checked by clean-CI regeneration against the frozen 840-run record digest.",
            "",
        ]
    )
    return "\n".join(lines)


def _figure_rows(payload: dict) -> tuple[tuple[str, str, int], ...]:
    systems = payload["systems"]
    selected = (
        ("ORION full", "orion_full"),
        ("Protocol SLR", "protocol_driven_systematic_review"),
        ("No independence", "no_route_independence_check"),
        ("Route stop = task stop", "route_stop_can_close_task"),
        ("Unavailable = closed", "no_unavailable_route_open_state"),
        ("Coverage authority", "coverage_diagnostic_controls_stopping"),
    )
    return tuple(
        (label, system_id, int(systems[system_id]["failure_counts"].get("premature_closure", 0)))
        for label, system_id in selected
    )


def render_svg(payload: dict) -> str:
    rows = _figure_rows(payload)
    width, height = 920, 390
    left, top, step, bar_height, scale = 255, 82, 44, 24, 25
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="28" y="32" font-family="sans-serif" font-size="20" font-weight="700">P2-6 — stopping-safety failures in the frozen offline companion</text>',
        '<text x="28" y="55" font-family="sans-serif" font-size="13">Terminal premature-closure classifications / 20 tasks · DESCRIPTIVE_ONLY</text>',
        f'<line x1="{left}" y1="{top-12}" x2="{left}" y2="{top+step*(len(rows)-1)+bar_height+8}" stroke="black"/>',
    ]
    for tick in (0, 5, 10, 15, 20):
        x = left + tick * scale
        out.append(f'<line x1="{x}" y1="{top-12}" x2="{x}" y2="{top+step*(len(rows)-1)+bar_height+8}" stroke="#dddddd"/>')
        out.append(f'<text x="{x}" y="{height-28}" text-anchor="middle" font-family="sans-serif" font-size="12">{tick}</text>')
    for index, (label, _system_id, count) in enumerate(rows):
        y = top + index * step
        escaped = html.escape(label)
        out.append(f'<text x="{left-12}" y="{y+17}" text-anchor="end" font-family="sans-serif" font-size="13">{escaped}</text>')
        out.append(f'<rect x="{left}" y="{y}" width="{count*scale}" height="{bar_height}" fill="#555555"/>')
        out.append(f'<text x="{left+count*scale+8}" y="{y+17}" font-family="sans-serif" font-size="13">{count}</text>')
    out.extend(
        [
            f'<text x="{left+250}" y="{height-7}" text-anchor="middle" font-family="sans-serif" font-size="12">count of terminal premature-closure failures</text>',
            '</svg>',
            '',
        ]
    )
    return "\n".join(out)


def render_tikz(payload: dict) -> str:
    rows = _figure_rows(payload)
    lines = [
        "% GENERATED from evidence/offline_results/RESULTS_SUMMARY_V1.json",
        "\\begin{tikzpicture}[x=0.25cm,y=0.65cm]",
        "\\draw[->] (0,0) -- (21,0) node[right]{terminal premature-closure failures};",
    ]
    for tick in (0, 5, 10, 15, 20):
        lines.append(f"\\draw ({tick},0.08) -- ({tick},-0.08) node[below]{{{tick}}};")
    for index, (label, _system_id, count) in enumerate(rows, start=1):
        y = index
        latex_label = label.replace("=", "$=$")
        lines.append(f"\\node[anchor=east] at (-0.35,{y+0.18}) {{{latex_label}}};")
        if count:
            lines.append(f"\\fill[black!65] (0,{y}) rectangle ({count},{y+0.36});")
        lines.append(f"\\node[anchor=west] at ({count+0.25},{y+0.18}) {{{count}}};")
    lines.extend(
        [
            f"\\node[anchor=west,font=\\small] at (0,{len(rows)+1.0}) {{20 frozen tasks; descriptive only}};",
            "\\end{tikzpicture}",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    rendered = {TABLE: render_table(payload), SVG: render_svg(payload), TIKZ: render_tikz(payload)}
    if args.check:
        stale = [str(path) for path, text in rendered.items() if not path.is_file() or path.read_text(encoding="utf-8") != text]
        if stale:
            print("stale P2 offline publication artifacts: " + ", ".join(stale), file=sys.stderr)
            return 1
        print("P2 offline failure table/figure match RESULTS_SUMMARY_V1.json")
        return 0
    for path, text in rendered.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
