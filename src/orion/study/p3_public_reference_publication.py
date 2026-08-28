from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Mapping, Sequence

SYSTEM_LABELS = {
    "orion": "ORION typed mapping",
    "flat_predicate_canonicalization": "Flat predicate canonicalization",
    "exact_coordinate_conservative": "Exact-coordinate conservative",
}


def _fmt(value: float) -> str:
    return f"{value:.4f}"


def _svg_bar_chart(title: str, labels: Sequence[str], values: Sequence[float], *, max_value: float = 1.0) -> str:
    width, height = 760, 110 + 56 * len(labels)
    x0, plot_w = 270, 420
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="20" y="30" font-family="sans-serif" font-size="18" font-weight="bold">{html.escape(title)}</text>',
        f'<line x1="{x0}" y1="50" x2="{x0}" y2="{height-30}" stroke="black"/>',
    ]
    for i, (label, value) in enumerate(zip(labels, values, strict=True)):
        y = 70 + i * 56
        bar_w = 0 if max_value <= 0 else plot_w * value / max_value
        lines.extend([
            f'<text x="20" y="{y+18}" font-family="sans-serif" font-size="13">{html.escape(label)}</text>',
            f'<rect x="{x0}" y="{y}" width="{bar_w:.2f}" height="24" fill="none" stroke="black" stroke-width="2"/>',
            f'<text x="{x0 + bar_w + 8:.2f}" y="{y+18}" font-family="monospace" font-size="13">{value:.4f}</text>',
        ])
    lines.append('</svg>')
    return "\n".join(lines) + "\n"


def _svg_ci_chart(title: str, rows: Sequence[tuple[str, float, float, float]]) -> str:
    width, height = 820, 120 + 62 * len(rows)
    x0, plot_w = 360, 380
    lo_axis, hi_axis = -0.4, 0.4
    def x(value: float) -> float:
        return x0 + (value - lo_axis) / (hi_axis - lo_axis) * plot_w
    zero = x(0.0)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="20" y="30" font-family="sans-serif" font-size="18" font-weight="bold">{html.escape(title)}</text>',
        f'<line x1="{zero:.2f}" y1="50" x2="{zero:.2f}" y2="{height-30}" stroke="black" stroke-dasharray="4 4"/>',
    ]
    for i, (label, point, low, high) in enumerate(rows):
        y = 78 + i * 62
        lines.extend([
            f'<text x="20" y="{y+5}" font-family="sans-serif" font-size="13">{html.escape(label)}</text>',
            f'<line x1="{x(low):.2f}" y1="{y}" x2="{x(high):.2f}" y2="{y}" stroke="black" stroke-width="2"/>',
            f'<line x1="{x(low):.2f}" y1="{y-6}" x2="{x(low):.2f}" y2="{y+6}" stroke="black"/>',
            f'<line x1="{x(high):.2f}" y1="{y-6}" x2="{x(high):.2f}" y2="{y+6}" stroke="black"/>',
            f'<circle cx="{x(point):.2f}" cy="{y}" r="5" fill="black"/>',
            f'<text x="{x0+plot_w+12}" y="{y+5}" font-family="monospace" font-size="12">{point:+.4f} [{low:+.4f}, {high:+.4f}]</text>',
        ])
    lines.append('</svg>')
    return "\n".join(lines) + "\n"


def generate(analysis: Mapping[str, object], out_dir: Path) -> None:
    pooled = analysis["pooled"]
    assert isinstance(pooled, Mapping)
    systems = pooled["systems"]
    comparisons = pooled["primary_comparisons"]
    ablations = pooled["ablation_deltas"]
    assert isinstance(systems, Mapping) and isinstance(comparisons, Mapping) and isinstance(ablations, Mapping)
    by_family = analysis["by_case_family"]
    assert isinstance(by_family, Mapping)

    out_dir.mkdir(parents=True, exist_ok=True)

    md = [
        "# ORION-13 public-reference confirmatory publication tables V1",
        "",
        "Generated deterministically from `CONFIRMATORY_ANALYSIS.json`. Scope: already-structured public-reference mapping only.",
        "",
        "## Table PR3-T1 — confirmatory composition",
        "",
        "| Case family | n | ORION false merge | Flat false merge | Exact abstention |",
        "|---|---:|---:|---:|---:|",
    ]
    for family, block in sorted(by_family.items()):
        assert isinstance(block, Mapping)
        md.append(
            f"| `{family}` | {int(block['case_count'])} | "
            f"{_fmt(float(block['orion']['false_merge_rate']))} | "
            f"{_fmt(float(block['flat_predicate_canonicalization']['false_merge_rate']))} | "
            f"{_fmt(float(block['exact_coordinate_conservative']['abstention_rate']))} |"
        )

    md += [
        "",
        "## Table PR3-T2 — pooled systems",
        "",
        "| System | Accuracy | False merge | False split | Abstention |",
        "|---|---:|---:|---:|---:|",
    ]
    for system_id in ("orion", "flat_predicate_canonicalization", "exact_coordinate_conservative"):
        block = systems[system_id]
        assert isinstance(block, Mapping)
        md.append(
            f"| {SYSTEM_LABELS[system_id]} | {_fmt(float(block['accuracy']['rate']))} | "
            f"{_fmt(float(block['false_merge']['rate']))} | {_fmt(float(block['false_split']['rate']))} | "
            f"{_fmt(float(block['abstention']['rate']))} |"
        )

    md += [
        "",
        "## Table PR3-T3 — predeclared primary comparisons",
        "",
        "| Comparison | Difference | 95% paired bootstrap CI |",
        "|---|---:|---:|",
    ]
    for key, label in (
        ("false_merge_orion_minus_flat", "ORION − flat false merge"),
        ("false_split_orion_minus_exact", "ORION − exact false split"),
    ):
        block = comparisons[key]
        assert isinstance(block, Mapping)
        md.append(f"| {label} | {float(block['candidate_minus_baseline']):+.4f} | [{float(block['ci95_low']):+.4f}, {float(block['ci95_high']):+.4f}] |")

    md += [
        "",
        "## Table PR3-T4 — covered ablations",
        "",
        "| Ablation | False-merge delta vs full ORION | 95% CI |",
        "|---|---:|---:|",
    ]
    ci_rows: list[tuple[str, float, float, float]] = []
    for ablation_id, block in sorted(ablations.items()):
        assert isinstance(block, Mapping)
        fm = block["false_merge_ablation_minus_full"]
        assert isinstance(fm, Mapping)
        point, low, high = float(fm["candidate_minus_baseline"]), float(fm["ci95_low"]), float(fm["ci95_high"])
        md.append(f"| `{ablation_id}` | {point:+.4f} | [{low:+.4f}, {high:+.4f}] |")
        ci_rows.append((ablation_id.replace('_', ' '), point, low, high))

    md += [
        "",
        "**Authority boundary.** These tables do not establish raw-text extraction, retrieval/provider quality, generated-portrait recoverability, downstream utility, or the original eight-family end-to-end claim.",
        "",
    ]
    (out_dir / "PUBLIC_REFERENCE_CONFIRMATORY_TABLES_V1.md").write_text("\n".join(md), encoding="utf-8")

    system_labels = [SYSTEM_LABELS[x] for x in ("orion", "flat_predicate_canonicalization", "exact_coordinate_conservative")]
    system_fm = [float(systems[x]["false_merge"]["rate"]) for x in ("orion", "flat_predicate_canonicalization", "exact_coordinate_conservative")]
    (out_dir / "PR3-F1_false_merge_by_system.svg").write_text(
        _svg_bar_chart("Confirmatory false-merge rate by system", system_labels, system_fm, max_value=0.25), encoding="utf-8"
    )

    family_labels, family_flat = [], []
    for family, block in sorted(by_family.items()):
        family_labels.append(str(family).replace('_', ' '))
        family_flat.append(float(block["flat_predicate_canonicalization"]["false_merge_rate"]))
    (out_dir / "PR3-F2_flat_false_merge_by_case_family.svg").write_text(
        _svg_bar_chart("Flat-canonicalization false merges by case family", family_labels, family_flat, max_value=0.5), encoding="utf-8"
    )

    (out_dir / "PR3-F3_ablation_false_merge_deltas.svg").write_text(
        _svg_ci_chart("Ablation false-merge deltas versus full ORION", ci_rows), encoding="utf-8"
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate publication artifacts from frozen P3 confirmatory analysis")
    parser.add_argument("--analysis", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    analysis = json.loads(args.analysis.read_text(encoding="utf-8"))
    if not isinstance(analysis, dict):
        raise ValueError("analysis must be a JSON object")
    generate(analysis, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
