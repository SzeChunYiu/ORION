"""Plot and table generators for ORION Paper 3.

Produces the 7 figures (P3-1 through P3-7) and 3 tables (P3-T1 through P3-T3)
specified in the frozen protocol, using the shared SVG utilities.

All figures are generated as SVG files via the dependency-free publication_svg
module. Tables are generated as LaTeX fragments.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

# publication_svg sits at research/paper-programme-v1/protocols/publication_svg.py
_SVG_MODULE = Path(__file__).resolve().parents[3] / "research" / "paper-programme-v1" / "protocols"

# ── figure definitions ────────────────────────────────────────────────────────

FIGURE_SPECS: dict[str, dict[str, object]] = {
    "P3-1": {
        "title": "P3-1: False Merge Rate by Baseline (Wilson 95% CI)",
        "kind": "bar",
        "label_key": "system_id",
        "value_key": "false_merge_rate",
        "y_label": "False Merge Rate",
    },
    "P3-2": {
        "title": "P3-2: Valid Integration Rate by Baseline (Wilson 95% CI)",
        "kind": "bar",
        "label_key": "system_id",
        "value_key": "valid_integration_rate",
        "y_label": "Valid Integration Rate",
    },
    "P3-3": {
        "title": "P3-3: False Merge Rate by Ablation (Wilson 95% CI)",
        "kind": "bar",
        "label_key": "system_id",
        "value_key": "false_merge_rate",
        "y_label": "False Merge Rate",
    },
    "P3-4": {
        "title": "P3-4: Valid Integration Rate by Ablation (Wilson 95% CI)",
        "kind": "bar",
        "label_key": "system_id",
        "value_key": "valid_integration_rate",
        "y_label": "Valid Integration Rate",
    },
    "P3-5": {
        "title": "P3-5: Mapping F1 Macro by System",
        "kind": "bar",
        "label_key": "system_id",
        "value_key": "mapping_f1_macro",
        "y_label": "Mapping F1 (Macro)",
    },
    "P3-6": {
        "title": "P3-6: Discipline-Stratified False Merge Rate",
        "kind": "heatmap",
        "row_key": "system_id",
        "col_key": "discipline",
        "value_key": "false_merge_rate",
    },
    "P3-7": {
        "title": "P3-7: False Merge Rate vs. Valid Integration Rate (Scatter)",
        "kind": "scatter",
        "x_key": "false_merge_rate",
        "y_key": "valid_integration_rate",
        "label_key": "system_id",
        "x_label": "False Merge Rate",
        "y_label": "Valid Integration Rate",
    },
}

TABLE_SPECS: dict[str, dict[str, object]] = {
    "P3-T1": {
        "title": "P3-T1: Primary Hypothesis Tests (H1: Superiority & Non-Inferiority)",
        "columns": ["system_id", "false_merge_rate", "valid_integration_rate",
                     "superiority_passed", "non_inferiority_passed", "both_passed"],
    },
    "P3-T2": {
        "title": "P3-T2: Ablation Breakdown (Delta from Full ORION)",
        "columns": ["ablation_id", "delta_false_merge_rate", "delta_valid_integration_rate",
                     "delta_mapping_f1_macro", "cohens_h", "effect_size_category"],
    },
    "P3-T3": {
        "title": "P3-T3: Discipline-Stratified Results (Full ORION)",
        "columns": ["discipline", "n_cases", "false_merge_rate", "valid_integration_rate",
                     "mapping_f1_macro", "source_recoverability_rate"],
    },
}


def generate_figure(
    fig_id: str,
    data_rows: Sequence[dict[str, object]],
    output_dir: str | Path,
) -> Path:
    """Generate a single figure SVG from result data.

    Args:
        fig_id: Figure ID (P3-1 through P3-7).
        data_rows: List of dicts with the required keys for this figure.
        output_dir: Directory to write the SVG file.

    Returns:
        Path to the generated SVG file.
    """
    spec = FIGURE_SPECS.get(fig_id)
    if spec is None:
        raise ValueError(f"Unknown figure: {fig_id}")

    # Dynamic import to avoid hard dependency
    import importlib.util
    svg_path = _SVG_MODULE / "publication_svg.py"
    if not svg_path.exists():
        raise FileNotFoundError(f"SVG module not found at {svg_path}")
    spec_mod = importlib.util.spec_from_file_location("publication_svg", str(svg_path))
    svg = importlib.util.module_from_spec(spec_mod)
    spec_mod.loader.exec_module(svg)

    output = Path(output_dir) / f"{fig_id}.svg"
    output.parent.mkdir(parents=True, exist_ok=True)

    kind = spec["kind"]
    if kind == "bar":
        content = svg.bar_chart(
            data_rows,
            label_key=str(spec["label_key"]),
            value_key=str(spec["value_key"]),
            title=str(spec["title"]),
            y_label=str(spec["y_label"]),
        )
    elif kind == "scatter":
        content = svg.scatter_plot(
            data_rows,
            x_key=str(spec["x_key"]),
            y_key=str(spec["y_key"]),
            label_key=str(spec["label_key"]),
            title=str(spec["title"]),
            x_label=str(spec["x_label"]),
            y_label=str(spec["y_label"]),
        )
    elif kind == "heatmap":
        content = svg.heatmap(
            data_rows,
            row_key=str(spec["row_key"]),
            col_key=str(spec["col_key"]),
            value_key=str(spec["value_key"]),
            title=str(spec["title"]),
        )
    else:
        raise ValueError(f"Unknown plot kind: {kind}")

    output.write_text(content, encoding="utf-8")
    return output


def generate_all_figures(
    results: Sequence[dict[str, object]],
    output_dir: str | Path,
) -> dict[str, Path]:
    """Generate all 7 figures from result data.

    Returns a dict mapping figure_id -> Path.
    """
    paths: dict[str, Path] = {}
    for fig_id in FIGURE_SPECS:
        paths[fig_id] = generate_figure(fig_id, results, output_dir)
    return paths


def generate_table_latex(
    table_id: str,
    data_rows: Sequence[dict[str, object]],
    output_dir: str | Path,
) -> Path:
    """Generate a LaTeX table fragment from result data.

    Args:
        table_id: Table ID (P3-T1 through P3-T3).
        data_rows: List of dicts with the required keys.
        output_dir: Directory to write the .tex file.

    Returns:
        Path to the generated .tex file.
    """
    spec = TABLE_SPECS.get(table_id)
    if spec is None:
        raise ValueError(f"Unknown table: {table_id}")

    columns = spec["columns"]
    output = Path(output_dir) / f"{table_id}.tex"
    output.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "% Automatically generated by ORION P3 evaluation framework",
        r"\begin{table}[t]",
        r"\centering",
        r"\begin{tabular}{" + "l" + "r" * (len(columns) - 1) + "}",
        r"\toprule",
        " & ".join(r"\textbf{" + c.replace("_", "\\_") + "}" for c in columns) + r" \\",
        r"\midrule",
    ]

    for row in data_rows:
        cells = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                cells.append(f"{val:.4f}")
            elif isinstance(val, bool):
                cells.append(r"\checkmark" if val else r"\xmark")
            elif val is None:
                cells.append("---")
            else:
                cells.append(str(val))
        lines.append(" & ".join(cells) + r" \\")

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\caption{" + str(spec["title"]) + "}",
        r"\label{tab:" + table_id.replace("-", ":") + "}",
        r"\end{table}",
    ])

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def generate_all_tables(
    results: Sequence[dict[str, object]],
    output_dir: str | Path,
) -> dict[str, Path]:
    """Generate all 3 tables from result data.

    Returns a dict mapping table_id -> Path.
    """
    paths: dict[str, Path] = {}
    for table_id in TABLE_SPECS:
        paths[table_id] = generate_table_latex(table_id, results, output_dir)
    return paths