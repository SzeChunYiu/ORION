#!/usr/bin/env python3
"""Render the accepted P4 protected campaign from immutable safe aggregates.

The renderer never reads protected per-case gold.  Its only data input is
``figures/data/RESULTS_SUMMARY_V1.json``, which is itself derived from the
accepted Actions safe bundle for campaign run 31968809206.
"""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "figures" / "data" / "RESULTS_SUMMARY_V1.json"
OUT = ROOT / "figures"
TABLES = ROOT / "tables"

WIDTH = 920
HEIGHT = 520
MARGIN_L = 90
MARGIN_R = 35
MARGIN_T = 55
MARGIN_B = 95
PLOT_W = WIDTH - MARGIN_L - MARGIN_R
PLOT_H = HEIGHT - MARGIN_T - MARGIN_B

PANEL_IDS = (
    "ORION",
    "provenanceguard-style-source-routing",
    "attributionbench-multisource-attribution",
    "fire-iterative-retrieve-or-verify",
    "claimbench-sciclaimhunt-scientific-evidence",
    "provenai-citation-fidelity-influence",
    "rewardhackingagents-search-contamination",
)

SHORT = {
    "ORION": "ORION",
    "provenanceguard-style-source-routing": "ProvenanceGuard-style",
    "attributionbench-multisource-attribution": "AttributionBench-style",
    "fire-iterative-retrieve-or-verify": "FIRE-style",
    "claimbench-sciclaimhunt-scientific-evidence": "CLAIM-BENCH-style",
    "provenai-citation-fidelity-influence": "ProvenAI-style",
    "rewardhackingagents-search-contamination": "RewardHacking/STC-style",
    "citation-presence-format": "Citation format",
    "pooled-evidence-nli-support": "Pooled support",
    "claim-level-auditability-provenance": "Auditability/provenance",
    "ablation-no-exact-content-binding": "− exact content",
    "ablation-no-content-provenance-distinction": "− source identity",
    "ablation-no-checker-lineage-independence": "− checker independence",
    "ablation-no-hostile-checker-battery": "− hostile checker battery",
    "ablation-no-behavioral-influence": "− behavioral influence",
    "ablation-no-evaluator-protection-telemetry": "− evaluator protection",
    "ablation-soft-confidence": "soft confidence",
    "ablation-no-search-contamination-block": "− contamination block",
}


def _load() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert data["status"] == "PROTECTED_RESULTS_ACCEPTED"
    assert data["campaign_run_id"] == "31968809206"
    assert data["typed_panel_status"] == "PASS"
    assert data["H1"]["status"] == "PASS"
    assert data["H2"]["status"] == "PASS"
    assert data["independent_reproduction"]["headline_reproduced"] is True
    return data


def _svg_start(title: str, subtitle: str = "") -> list[str]:
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{WIDTH/2:.0f}" y="28" text-anchor="middle" font-family="sans-serif" font-size="18" font-weight="bold">{escape(title)}</text>',
    ]
    if subtitle:
        lines.append(
            f'<text x="{WIDTH/2:.0f}" y="47" text-anchor="middle" font-family="sans-serif" font-size="11">{escape(subtitle)}</text>'
        )
    return lines


def _axes(lines: list[str], *, x_label: str, y_label: str, y_max: float = 1.0) -> None:
    x0, y0 = MARGIN_L, MARGIN_T + PLOT_H
    lines += [
        f'<line x1="{x0}" y1="{MARGIN_T}" x2="{x0}" y2="{y0}" stroke="black"/>',
        f'<line x1="{x0}" y1="{y0}" x2="{MARGIN_L+PLOT_W}" y2="{y0}" stroke="black"/>',
    ]
    for i in range(6):
        value = y_max * i / 5
        y = y0 - PLOT_H * i / 5
        lines.append(f'<line x1="{x0-5}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="black"/>')
        lines.append(f'<text x="{x0-10}" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="10">{value:.2f}</text>')
    lines.append(f'<text x="{MARGIN_L+PLOT_W/2:.1f}" y="{HEIGHT-16}" text-anchor="middle" font-family="sans-serif" font-size="12">{escape(x_label)}</text>')
    lines.append(f'<text transform="translate(22 {MARGIN_T+PLOT_H/2:.1f}) rotate(-90)" text-anchor="middle" font-family="sans-serif" font-size="12">{escape(y_label)}</text>')


def _finish(lines: list[str], path: Path) -> None:
    lines.append("</svg>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _system_map(data: dict) -> dict[str, dict]:
    return {item["system_id"]: item for item in data["systems"]}


def figure_p4_2(data: dict) -> None:
    systems = _system_map(data)
    rows = [systems[sid] for sid in PANEL_IDS]
    lines = _svg_start(
        "P4-2 — False scientific-authority promotion",
        "Protected campaign 31968809206; Wilson 95% intervals",
    )
    _axes(lines, x_label="system", y_label="false-promotion rate", y_max=1.0)
    step = PLOT_W / len(rows)
    bar_w = step * 0.56
    y0 = MARGIN_T + PLOT_H
    for i, row in enumerate(rows):
        x = MARGIN_L + step * (i + 0.5)
        value = row["false_promotion"]
        h = PLOT_H * value
        lines.append(f'<rect x="{x-bar_w/2:.1f}" y="{y0-h:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="#777" stroke="black"/>')
        ci = row["false_promotion_ci95"]
        if ci:
            lo, hi = ci
            ylo = y0 - PLOT_H * lo
            yhi = y0 - PLOT_H * hi
            lines.append(f'<line x1="{x:.1f}" y1="{yhi:.1f}" x2="{x:.1f}" y2="{ylo:.1f}" stroke="black" stroke-width="1.5"/>')
            lines.append(f'<line x1="{x-7:.1f}" y1="{yhi:.1f}" x2="{x+7:.1f}" y2="{yhi:.1f}" stroke="black"/>')
            lines.append(f'<line x1="{x-7:.1f}" y1="{ylo:.1f}" x2="{x+7:.1f}" y2="{ylo:.1f}" stroke="black"/>')
        label = SHORT[row["system_id"]]
        lines.append(f'<text transform="translate({x+4:.1f} {y0+13:.1f}) rotate(55)" text-anchor="start" font-family="sans-serif" font-size="9">{escape(label)}</text>')
        lines.append(f'<text x="{x:.1f}" y="{max(MARGIN_T+12, y0-h-7):.1f}" text-anchor="middle" font-family="sans-serif" font-size="10">{value:.3f}</text>')
    _finish(lines, OUT / "p4_2_false_promotion.svg")


def figure_p4_3(data: dict) -> None:
    systems = _system_map(data)
    rows = [systems[sid] for sid in PANEL_IDS]
    lines = _svg_start(
        "P4-3 — Clean authority coverage vs false promotion",
        "Lower false promotion and higher clean coverage are preferred",
    )
    _axes(lines, x_label="false-promotion rate", y_label="clean authority coverage", y_max=1.0)
    x0, y0 = MARGIN_L, MARGIN_T + PLOT_H
    for row in rows:
        x = x0 + PLOT_W * row["false_promotion"]
        y = y0 - PLOT_H * row["coverage"]
        r = 6 if row["system_id"] == "ORION" else 4
        fill = "black" if row["system_id"] == "ORION" else "#777"
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"/>')
        lines.append(f'<text x="{x+7:.1f}" y="{y-7:.1f}" font-family="sans-serif" font-size="9">{escape(SHORT[row["system_id"]])}</text>')
    lines.append(f'<text x="{x0+8}" y="{MARGIN_T+15}" font-family="sans-serif" font-size="10">preferred corner</text>')
    _finish(lines, OUT / "p4_3_coverage_frontier.svg")


def figure_p4_4(data: dict) -> None:
    families = [item for item in data["attack_families"] if item["family"] != "CLEAN_POSITIVE"]
    lines = _svg_start(
        "P4-4 — Hostile-family terminal accuracy",
        f'ORION vs strongest frozen comparator: {SHORT[data["strongest_frozen_comparator"]]}',
    )
    cell_w = PLOT_W / max(1, len(families))
    row_h = 95
    y_top = 105
    labels = ("ORION", "Comparator")
    for row_idx, row_label in enumerate(labels):
        y = y_top + row_idx * row_h
        lines.append(f'<text x="{MARGIN_L-12}" y="{y+30}" text-anchor="end" font-family="sans-serif" font-size="11">{row_label}</text>')
        for i, item in enumerate(families):
            value = item["orion_correct_terminal_rate"] if row_idx == 0 else item["comparator_correct_terminal_rate"]
            shade = int(255 - 190 * value)
            x = MARGIN_L + i * cell_w
            lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_w-2:.1f}" height="60" fill="rgb({shade},{shade},{shade})" stroke="#aaa"/>')
            text_fill = "white" if value > 0.62 else "black"
            lines.append(f'<text x="{x+cell_w/2:.1f}" y="{y+35:.1f}" text-anchor="middle" font-family="sans-serif" font-size="10" fill="{text_fill}">{value:.2f}</text>')
            if row_idx == 1:
                lines.append(f'<text transform="translate({x+cell_w/2+4:.1f} {y+74:.1f}) rotate(55)" text-anchor="start" font-family="sans-serif" font-size="8">{escape(item["family"])}</text>')
    lines.append(f'<text x="{MARGIN_L+PLOT_W/2:.1f}" y="{HEIGHT-20}" text-anchor="middle" font-family="sans-serif" font-size="11">attack family (1.00 = correct terminal on all 30 protected cases)</text>')
    _finish(lines, OUT / "p4_4_detection_by_attack.svg")


def figure_p4_5(data: dict) -> None:
    systems = _system_map(data)
    rows = [systems[sid] for sid in PANEL_IDS if systems[sid]["attribution_accuracy"] is not None]
    lines = _svg_start("P4-5 — Source attribution vs semantic support", "Coordinates remain separate even when both are high")
    _axes(lines, x_label="source-attribution accuracy", y_label="support/contradiction F1", y_max=1.0)
    x0, y0 = MARGIN_L, MARGIN_T + PLOT_H
    for idx, row in enumerate(rows):
        x = x0 + PLOT_W * row["attribution_accuracy"]
        y = y0 - PLOT_H * row["semantic_support_accuracy"]
        # jitter labels only, not data coordinates
        dx = 8 + (idx % 3) * 5
        dy = -8 - (idx % 2) * 11
        fill = "black" if row["system_id"] == "ORION" else "#777"
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{fill}"/>')
        lines.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" font-family="sans-serif" font-size="8">{escape(SHORT[row["system_id"]])}</text>')
    _finish(lines, OUT / "p4_5_attribution_vs_support.svg")


def figure_p4_6(data: dict) -> None:
    systems = _system_map(data)
    rows = [systems[sid] for sid in PANEL_IDS]
    max_cost = max(row["resource_cost"] for row in rows) * 1.1
    lines = _svg_start("P4-6 — Resource cost vs false promotion", "Frozen resource units; lower false promotion is preferred")
    _axes(lines, x_label="resource units", y_label="false-promotion rate", y_max=1.0)
    x0, y0 = MARGIN_L, MARGIN_T + PLOT_H
    for idx, row in enumerate(rows):
        x = x0 + PLOT_W * row["resource_cost"] / max_cost
        y = y0 - PLOT_H * row["false_promotion"]
        fill = "black" if row["system_id"] == "ORION" else "#777"
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{fill}"/>')
        lines.append(f'<text x="{x+7:.1f}" y="{y-7-(idx%2)*10:.1f}" font-family="sans-serif" font-size="8">{escape(SHORT[row["system_id"]])}</text>')
    for i in range(6):
        value = max_cost * i / 5
        x = x0 + PLOT_W * i / 5
        lines.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y0+5}" stroke="black"/>')
        lines.append(f'<text x="{x:.1f}" y="{y0+18}" text-anchor="middle" font-family="sans-serif" font-size="9">{value:.1f}</text>')
    _finish(lines, OUT / "p4_6_cost_false_promotion.svg")


def _tex_escape(text: str) -> str:
    return (
        text.replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("%", "\\%")
        .replace("&", "\\&")
        .replace("#", "\\#")
    )


def table_p4_1(data: dict) -> None:
    lines = [
        "% Generated from accepted campaign 31968809206; do not hand edit.",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Protected attack battery and terminal accuracy. The final hidden campaign contains 420 mechanical-gold cases; the 39 tracked repository cases are public calibration only.}",
        "\\label{tab:p4_t1}",
        "\\small",
        "\\begin{tabular}{lrrr}",
        "\\toprule",
        "Family & $n$ & ORION terminal acc. & comparator terminal acc. \\\\",
        "\\midrule",
    ]
    for item in data["attack_families"]:
        lines.append(
            f"{_tex_escape(item['family'])} & {item['n']} & {item['orion_correct_terminal_rate']:.3f} & {item['comparator_correct_terminal_rate']:.3f} \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    (TABLES / "p4_t1_attack_custody.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def table_p4_2(data: dict) -> None:
    systems = _system_map(data)
    ordered = list(PANEL_IDS) + [
        "citation-presence-format",
        "pooled-evidence-nli-support",
        "claim-level-auditability-provenance",
        "ablation-no-exact-content-binding",
        "ablation-no-content-provenance-distinction",
        "ablation-no-checker-lineage-independence",
        "ablation-no-hostile-checker-battery",
        "ablation-no-behavioral-influence",
        "ablation-no-evaluator-protection-telemetry",
        "ablation-soft-confidence",
        "ablation-no-search-contamination-block",
    ]
    lines = [
        "% Generated from accepted campaign 31968809206; do not hand edit.",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Baseline and ablation results on the frozen 420-case protected campaign. FP is false scientific-authority promotion; coverage is promotion on 60 clean positives.}",
        "\\label{tab:p4_t2}",
        "\\scriptsize",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "System & FP rate & clean cov. & resource & latency (s) \\\\",
        "\\midrule",
    ]
    for sid in ordered:
        row = systems[sid]
        lines.append(
            f"{_tex_escape(SHORT[sid])} & {row['false_promotion']:.3f} & {row['coverage']:.3f} & {row['resource_cost']:.1f} & {row['latency_seconds']:.4f} \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    (TABLES / "p4_t2_baseline_ablation_results.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def table_p4_3(data: dict) -> None:
    h1, h2, h3 = data["H1"], data["H2"], data["H3"]
    tel = data["telemetry"]
    lines = [
        "% Generated from accepted campaign 31968809206; do not hand edit.",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Headline inference, abstention result, false-negative cost, and custody checks. H3 is reported as not supported rather than promoted by a tie.}",
        "\\label{tab:p4_t3}",
        "\\small",
        "\\begin{tabular}{p{0.38\\linewidth}p{0.53\\linewidth}}",
        "\\toprule",
        "Item & Result \\\\",
        "\\midrule",
        f"H1 false-promotion difference & {h1['orion_minus_baseline_false_promotion']:.3f}, 95\\% CI [{h1['ci95_low']:.3f}, {h1['ci95_high']:.3f}], PASS \\\\",
        f"H2 clean-coverage difference & {h2['orion_minus_baseline_clean_coverage']:.3f}, 95\\% CI [{h2['ci95_low']:.3f}, {h2['ci95_high']:.3f}], PASS \\\\",
        f"H3 correct CANNOT\\_CHECK difference & {h3['orion_minus_baseline_correct_cannot_check']:.3f}, 95\\% CI [{h3['ci95_low']:.3f}, {h3['ci95_high']:.3f}], NOT SUPPORTED \\\\",
        "ORION clean false negatives & 0/60 (0.000); no coverage loss \\\\",
        f"Actual protected identifier accesses & candidate {tel['candidate_protected_identifier_hits']}; comparators {tel['comparator_protected_identifier_hits']} \\\\",
        f"Actual external IP connects during scored execution & candidate {tel['candidate_external_ip_connects']}; comparators {tel['comparator_external_ip_connects']} \\\\",
        f"Independent reproduction & {'PASS' if data['independent_reproduction']['headline_reproduced'] else 'FAIL'} \\\\",
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
    ]
    (TABLES / "p4_t3_cannot_check_errors.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    data = _load()
    OUT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    figure_p4_2(data)
    figure_p4_3(data)
    figure_p4_4(data)
    figure_p4_5(data)
    figure_p4_6(data)
    table_p4_1(data)
    table_p4_2(data)
    table_p4_3(data)
    print("rendered accepted P4 protected results from", DATA)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
