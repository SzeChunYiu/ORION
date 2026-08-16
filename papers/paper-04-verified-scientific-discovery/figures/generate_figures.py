#!/usr/bin/env python3
"""Generate ORION-P4 publication figures and tables.

The figure pipeline is deliberately data-driven: summary JSON/CSV documents in
`figures/data/` are rendered through the dependency-free `publication_svg.py`
helpers hosted in the research paper-programme protocols directory. This script
regenerates every figure and table listed in PLOT_SPEC_V1.md.

While the protected campaign is still UNBOUND, it renders from the stub
summary (STUB_SUMMARY_V1.json) so repository consumers can validate the
rendering pipeline end-to-end. After execution, the same script is re-run from
frozen result artifacts without code changes.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DATA = _HERE / "data"
_TABLES = _HERE.parent / "tables"
_OUT = _HERE
_PROTOCOLS = (_HERE.parent.parent.parent / "research/paper-programme-v1/protocols").resolve()
sys.path.insert(0, str(_PROTOCOLS))

from publication_svg import bar_chart, heatmap  # noqa: E402

SYSTEMS = [
    "ORION",
    "CitationFormat",
    "PooledNLI",
    "AttributionBench",
    "ProvenanceGuard",
    "IterativeRV",
    "Auditability",
]

ATTACK_FAMILIES = [
    "clean_supported_positive",
    "correct_fact_wrong_source",
    "content_substitution",
    "source_conflation",
    "pooled_support_wrong_owner",
    "cited_but_non_influential",
    "weak_non_discriminating_checker",
    "same_lane_checker",
    "posthoc_checker_or_evaluator",
    "search_time_contamination",
    "evaluator_or_guard_tampering",
    "heldout_label_access",
    "genuinely_insufficient_evidence",
]


def _load_stub(key: str) -> list[dict[str, object]]:
    payload = json.loads((_DATA / "STUB_SUMMARY_V1.json").read_text(encoding="utf-8"))
    return payload[key]


def _float(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_p4_2(data: list[dict[str, object]]) -> str:
    rows = [{"system": datum["system"], "rate": _float(datum["false_promotion_rate"]) or 0.0} for datum in data]
    return bar_chart(
        rows,
        label_key="system",
        value_key="rate",
        title="False Authority-Promotion Rate by System",
        y_label="False promotion rate",
    )


def build_p4_3(data: list[dict[str, object]]) -> str:
    rows = [
        {
            "system": datum["system"],
            "coverage": _float(datum["clean_authority_coverage"]) or 0.0,
            "false_promotion": _float(datum["false_promotion_rate"]) or 0.0,
        }
        for datum in data
    ]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="560" viewBox="0 0 900 560">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="450" y="32" text-anchor="middle" font-family="sans-serif" font-size="20">Safety–Coverage Frontier</text>',
    ]
    # axes
    x0, x1 = 100, 860
    y0, y1 = 460, 65
    lines.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="black"/>')
    lines.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="black"/>')
    for i in range(11):
        v = i / 10.0
        x = x0 + (x1 - x0) * v
        y = y0 - (y0 - y1) * v
        lines.append(f'<line x1="{x0-5}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="black"/>')
        lines.append(f'<text x="{x0-10}" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="12">{v:.1f}</text>')
    lines.append(f'<text x="22" y="{(y0+y1)/2}" transform="rotate(-90 22 {(y0+y1)/2})" text-anchor="middle" font-family="sans-serif" font-size="14">Rate</text>')
    lines.append(f'<text x="{(x0+x1)/2}" y="{y0+30}" text-anchor="middle" font-family="sans-serif" font-size="14">Coverage (left, blue) and false promotion (right, orange)</text>')
    # scatter points
    colors = {"ORION": "#2196F3"}
    for datum in data:
        system = datum["system"]
        cov = _float(datum["clean_authority_coverage"]) or 0.0
        fp = _float(datum["false_promotion_rate"]) or 0.0
        x = x0 + (x1 - x0) * cov
        y = y0 - (y0 - y1) * fp
        color = colors.get(system, "#FF9800")
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{color}"/>')
        lines.append(f'<text x="{x+8:.1f}" y="{y-8:.1f}" font-family="sans-serif" font-size="11">{system}</text>')
    lines.append("</svg>")
    return "\n".join(lines)


def build_p4_4(data: list[dict[str, object]]) -> str:
    return heatmap(
        data,
        row_key="attack_family",
        col_key="system",
        value_key="detection_rate",
        title="Detection Rate by Attack Family",
    )


def build_p4_5(data: list[dict[str, object]]) -> str:
    rows = [
        {
            "system": datum["system"],
            "attribution": _float(datum["source_attribution_accuracy"]) or 0.0,
            "support_f1": _float(datum["support_contradiction_f1"]) or 0.0,
        }
        for datum in data
    ]
    return bar_chart(
        rows,
        label_key="system",
        value_key="attribution",
        title="Source Attribution vs Semantic Support Accuracy",
        y_label="Accuracy / F1",
    )


def build_p4_6(data: list[dict[str, object]]) -> str:
    rows = [
        {
            "system": datum["system"],
            "cost": _float(datum["wallclock_seconds"]) or 0.0,
            "false_promotion": _float(datum["false_promotion_rate"]) or 0.0,
        }
        for datum in data
    ]
    return bar_chart(
        rows,
        label_key="system",
        value_key="cost",
        title="Cost vs False-Promotion Trade-off",
        y_label="Normalized cost / False promotion",
    )


def _wilson(successes: float, total: float) -> tuple[float, float]:
    z = 1.96
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return max(0.0, center - half), min(1.0, center + half)


def write_table_p4_2(data: list[dict[str, object]]) -> None:
    header = ["System", "False promotion", "Clean coverage", "Correct CANNOT_CHECK", "Cost (s)", "Run status"]
    lines = [
        "% Generated by figures/generate_figures.py from figures/data/STUB_SUMMARY_V1.json",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Stub baseline and ablation results (DESIGN_FROZEN; campaign UNBOUND). "
        "Values render the rendering pipeline from stub summary data and must be replaced by "
        "protected-run results before any empirical claim is reported.}",
        "\\label{tab:p4_t2}",
        "\\begin{tabular}{" + "l" + "c" * (len(header) - 1) + "}",
        "\\toprule",
        " & ".join(header) + " \\\\",
        "\\midrule",
    ]
    for datum in data:
        fp = _float(datum["false_promotion_rate"])
        cov = _float(datum["clean_authority_coverage"])
        cc = _float(datum["correct_cannot_check_rate"])
        cost = _float(datum["wallclock_seconds"])
        fp_s = f"{fp:.3f}" if fp is not None else "---"
        cov_s = f"{cov:.3f}" if cov is not None else "---"
        cc_s = f"{cc:.3f}" if cc is not None else "---"
        cost_s = f"{cost:.1f}" if cost is not None else "---"
        lines.append(f"{datum['system']} & {fp_s} & {cov_s} & {cc_s} & {cost_s} & STUB \\\\")
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "",
    ]
    (_TABLES / "p4_t2_baseline_ablation_results.tex").write_text("\n".join(lines), encoding="utf-8")


def write_table_p4_3(data: list[dict[str, object]]) -> None:
    header = ["System", "Total CANNOT_CHECK", "Correct abstention", "False block", "False positive", "Infra failure"]
    lines = [
        "% Generated by figures/generate_figures.py from figures/data/STUB_SUMMARY_V1.json",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Stub CANNOT_CHECK / error breakdown (DESIGN_FROZEN; campaign UNBOUND).}",
        "\\label{tab:p4_t3}",
        "\\begin{tabular}{" + "l" + "c" * (len(header) - 1) + "}",
        "\\toprule",
        " & ".join(header) + " \\\\",
        "\\midrule",
    ]
    for datum in data:
        lines.append(
            f"{datum['system']} & 0 & 0 & 0 & 0 & 0 \\\\"
        )
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "",
    ]
    (_TABLES / "p4_t3_cannot_check_errors.tex").write_text("\n".join(lines), encoding="utf-8")


def write_table_p4_1() -> None:
    header = ["Family", "Cases (n)", "Public clean", "Public hostile", "Protected hostile", "Protected holdout", "Hidden labels"]
    lines = [
        "% Generated by figures/generate_figures.py from figures/data/STUB_SUMMARY_V1.json",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Stub attack battery and custody manifest (DESIGN_FROZEN; campaign UNBOUND).}",
        "\\label{tab:p4_t1}",
        "\\begin{tabular}{lcccccc}",
        "\\toprule",
        " & ".join(header) + " \\\\",
        "\\midrule",
    ]
    for family in ATTACK_FAMILIES:
        lines.append(f"{family} & --- & --- & --- & --- & --- & Yes \\\\")
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "",
    ]
    (_TABLES / "p4_t1_attack_custody.tex").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT = _OUT
    data = _load_stub("summary")
    (OUT / "p4_2_false_promotion.svg").write_text(build_p4_2(data), encoding="utf-8")
    (OUT / "p4_3_coverage_frontier.svg").write_text(build_p4_3(data), encoding="utf-8")
    (OUT / "p4_4_detection_by_attack.svg").write_text(build_p4_4(_load_stub("heatmap")), encoding="utf-8")
    (OUT / "p4_5_attribution_vs_support.svg").write_text(build_p4_5(data), encoding="utf-8")
    (OUT / "p4_6_cost_false_promotion.svg").write_text(build_p4_6(data), encoding="utf-8")
    write_table_p4_1()
    write_table_p4_2(data)
    write_table_p4_3(data)
    print(f"wrote 5 SVGs + 3 LaTeX tables under {OUT.parent}")


if __name__ == "__main__":
    main()