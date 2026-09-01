#!/usr/bin/env python3
"""Render the completed P2 offline failure table and stopping-safety figure.

Publication-layer only: reads the immutable compact result summary and does not
recompute or change scientific outcomes. Use ``--check`` in CI to prevent a
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


def _scope(payload: dict) -> tuple[int, str, int]:
    frozen = payload.get("frozen_run")
    if not isinstance(frozen, dict):
        raise ValueError("missing frozen_run")
    n_tasks = frozen.get("n_tasks")
    n_records = frozen.get("n_result_records")
    authority = payload.get("analysis_authority")
    achieved = payload.get("achieved_precision")
    if not isinstance(n_tasks, int) or isinstance(n_tasks, bool) or n_tasks < 1:
        raise ValueError("frozen_run.n_tasks must be a positive integer")
    if not isinstance(n_records, int) or isinstance(n_records, bool) or n_records < 1:
        raise ValueError("frozen_run.n_result_records must be a positive integer")
    if not isinstance(authority, str) or not authority:
        raise ValueError("analysis_authority must be non-empty")
    if not isinstance(achieved, dict) or achieved.get("n_tasks") != n_tasks:
        raise ValueError("achieved_precision must bind frozen_run.n_tasks")
    if achieved.get("achieved_tier") != authority:
        raise ValueError("analysis_authority must match achieved_precision.achieved_tier")
    if achieved.get("primary_promoted") is not False:
        raise ValueError("offline companion cannot self-promote a primary claim")
    return n_tasks, authority, n_records


def render_table(payload: dict) -> str:
    n_tasks, authority, n_records = _scope(payload)
    systems = payload["systems"]
    lines = [
        "# Table ORION-12-3 — offline controlled-index failure taxonomy",
        "",
        f"**Authority:** `{authority}`. These are terminal task classifications from the frozen {n_tasks}-task offline companion after the three deterministic repeats are collapsed within task. They are not external benchmark results; the achieved precision for this family is recorded in `RESULTS_SUMMARY_V1.json` under `achieved_precision`, and no primary is promoted here.",
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

    orion_cc = int(systems["orion_full"]["status_counts"].get("CANNOT_CHECK", 0))
    unavailable_pc = int(
        systems["no_unavailable_route_open_state"]["failure_counts"].get(
            "premature_closure", 0
        )
    )
    dedup_budget = int(
        systems["no_content_identity_dedup"]["failure_counts"].get("budget_exhausted", 0)
    )
    exploratory_transport = int(
        systems["adaptive_multiroute_exploratory"]["failure_counts"].get(
            "transport_failure", 0
        )
    )
    exploratory_cannot_check = int(
        systems["adaptive_multiroute_exploratory"]["status_counts"].get(
            "CANNOT_CHECK", 0
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
            f"- full ORION converts {orion_cc} materially censored cases into `CANNOT_CHECK` rather than a completeness claim;",
            f"- the `no_unavailable_route_open_state` ablation converts those same safety cases into {unavailable_pc} premature-closure failures;",
            f"- the `no_content_identity_dedup` ablation creates {dedup_budget} budget-exhaustion failures after duplicate work consumes the read budget;",
            "- simple/single-pass baselines terminate with premature closure because reachable relevant material remains on unexercised routes;",
            f"- the exploratory adaptive comparator retains {exploratory_cannot_check} censored tasks as `CANNOT_CHECK`; under the current canonical vocabulary, {exploratory_transport} of those remain encoded as terminal `transport_failure` labels rather than being promoted into failures.",
            "",
            f"Source of record: `RESULTS_SUMMARY_V1.json`, itself checked by clean-CI regeneration against the frozen {n_records}-run record digest.",
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


def _ticks(n_tasks: int) -> tuple[int, ...]:
    return tuple(round(n_tasks * fraction / 4) for fraction in range(5))


def render_svg(payload: dict) -> str:
    n_tasks, authority, _ = _scope(payload)
    rows = _figure_rows(payload)
    width, height = 920, 390
    left, top, step, bar_height = 255, 82, 44, 24
    plot_width = 595
    scale = plot_width / n_tasks
    ticks = _ticks(n_tasks)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="28" y="32" font-family="sans-serif" font-size="20" font-weight="700">P2-6 — stopping-safety failures in the frozen offline companion</text>',
        f'<text x="28" y="55" font-family="sans-serif" font-size="13">Terminal premature-closure classifications / {n_tasks} frozen tasks / descriptive only</text>',
        f'<line x1="{left}" y1="{top-12}" x2="{left}" y2="{top+step*(len(rows)-1)+bar_height+8}" stroke="black"/>',
    ]
    for tick in ticks:
        x = round(left + tick * scale)
        out.append(f'<line x1="{x}" y1="{top-12}" x2="{x}" y2="{top+step*(len(rows)-1)+bar_height+8}" stroke="#dddddd"/>')
        out.append(f'<text x="{x}" y="{height-28}" text-anchor="middle" font-family="sans-serif" font-size="12">{tick}</text>')
    for index, (label, _system_id, count) in enumerate(rows):
        y = top + index * step
        escaped = html.escape(label)
        bar_width_px = round(count * scale)
        out.append(f'<text x="{left-12}" y="{y+17}" text-anchor="end" font-family="sans-serif" font-size="13">{escaped}</text>')
        out.append(f'<rect x="{left}" y="{y}" width="{bar_width_px}" height="{bar_height}" fill="#555555"/>')
        out.append(f'<text x="{left+bar_width_px+8}" y="{y+17}" font-family="sans-serif" font-size="13">{count}</text>')
    out.extend(
        [
            f'<text x="{left+250}" y="{height-7}" text-anchor="middle" font-family="sans-serif" font-size="12">count of terminal premature-closure failures</text>',
            '</svg>',
            '',
        ]
    )
    return "\n".join(out)


def render_tikz(payload: dict) -> str:
    n_tasks, authority, _ = _scope(payload)
    rows = _figure_rows(payload)
    ticks = _ticks(n_tasks)
    x_scale = 5.25 / n_tasks
    node_offset = n_tasks / 80
    axis_max = n_tasks * 1.05
    lines = [
        "% GENERATED from evidence/offline_results/RESULTS_SUMMARY_V1.json",
        f"\\begin{{tikzpicture}}[x={x_scale:.5f}cm,y=0.65cm]",
        f"\\draw[->] (0,0) -- ({axis_max:.2f},0) node[right]{{terminal premature-closure failures}};",
    ]
    for tick in ticks:
        lines.append(f"\\draw ({tick},0.08) -- ({tick},-0.08) node[below]{{{tick}}};")
    for index, (label, _system_id, count) in enumerate(rows, start=1):
        y = index
        latex_label = label.replace("=", "$=$")
        lines.append(f"\\node[anchor=east] at (-0.35,{y+0.18}) {{{latex_label}}};")
        if count:
            lines.append(f"\\fill[black!65] (0,{y}) rectangle ({count},{y+0.36});")
        lines.append(f"\\node[anchor=west] at ({count+node_offset:.2f},{y+0.18}) {{{count}}};")
    lines.extend(
        [
            f"\\node[anchor=west,font=\\small] at (0,{len(rows)+1.0}) {{{n_tasks} frozen tasks; descriptive only}};",
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
