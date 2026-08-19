from __future__ import annotations

import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SUMMARY = HERE / "evidence" / "OFFICIAL_EVIDENCE_SUMMARY_V1.json"
OUT_JSON = HERE / "evidence" / "HEADLINE_TABLES_V1.json"
OUT_MD = HERE / "evidence" / "HEADLINE_TABLES_V1.md"
OUT_TEX = HERE / "manuscript" / "generated_headline_tables.tex"
LATEX_ROW_BREAK = "\\\\"


def _load_summary() -> dict[str, Any]:
    if not SUMMARY.is_file():
        raise SystemExit(
            "missing fail-closed evidence summary; run build_evidence_summary.py first"
        )
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if data.get("schema") != "P9.OfficialEvidenceSummary.v1":
        raise SystemExit(f"unexpected evidence summary schema: {data.get('schema')!r}")
    return data


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def _latex_escape(text: str) -> str:
    return (
        text.replace("\\", r"\textbackslash{}")
        .replace("_", r"\_")
        .replace("%", r"\%")
        .replace("&", r"\&")
        .replace("#", r"\#")
    )


def build_tables(summary: dict[str, Any]) -> dict[str, Any]:
    m1 = summary["m1"]
    d1 = summary["d1"]
    a2a4 = summary["a2_a4"]
    a5 = summary["a5"]

    m1_rows = []
    for view in ("SURFACE", "TOPOLOGY", "TYPED", "CURRENT", "SEMANTIC"):
        row = m1["views"][view]
        m1_rows.append(
            {
                "view": view,
                "accuracy": row["accuracy"],
                "ceiling": row["exact_view_deterministic_accuracy_ceiling"],
                "gap_to_ceiling": row["exact_view_deterministic_accuracy_ceiling"]
                - row["accuracy"],
                "ceiling_violation": row["ceiling_violation"],
            }
        )

    d1_rows = []
    for arm in (
        "TRANSCRIPT_BAG",
        "UNTYPED_PAIR",
        "TYPED_RELATIONAL",
        "TYPED_SERIALIZED_BAG",
    ):
        row = d1["results"][arm]
        d1_rows.append(
            {
                "arm": arm,
                "selected_model": row["selected_model"],
                "test_accuracy": row["test_accuracy"],
                "macro_f1": row["macro_f1"],
                "double_corruption_accuracy": row["double_corruption_accuracy"],
                "unresolved_accuracy": row["unresolved_accuracy"],
            }
        )

    explicit_rows = [
        {
            "atom": "A2 relation semantics",
            "weaker_view": "TOPOLOGY",
            "weaker_accuracy": a2a4["relation"]["TOPOLOGY"]["full_task_accuracy"],
            "sufficient_view": "TYPED",
            "sufficient_accuracy": a2a4["relation"]["TYPED"]["full_task_accuracy"],
            "interpretation": "typed relation semantics are load-bearing; explicit selection suffices",
        },
        {
            "atom": "A4 failure history",
            "weaker_view": "CURRENT",
            "weaker_accuracy": a2a4["history"]["CURRENT"]["full_task_accuracy"],
            "sufficient_view": "SEMANTIC",
            "sufficient_accuracy": a2a4["history"]["SEMANTIC"]["full_task_accuracy"],
            "interpretation": "admitted scoped failure history is load-bearing; explicit filtering suffices",
        },
        {
            "atom": "A5 affine transport",
            "weaker_view": "TYPED",
            "weaker_accuracy": a5["typed_accuracy"],
            "sufficient_view": "CURRENT",
            "sufficient_accuracy": a5["current_accuracy"],
            "interpretation": "visible local maps plus exact composition close the D0 computation",
        },
    ]

    return {
        "schema": "P9.HeadlineTables.v1",
        "m1_terminal": m1["terminal"],
        "d1_terminal": d1["terminal"],
        "m1_view_ceiling_table": m1_rows,
        "m1_decisive_computation": {
            "current_gluing": m1["views"]["CURRENT"]["gluing"],
            "semantic_gluing": m1["views"]["SEMANTIC"]["gluing"],
            "semantic_mechanic_ranking_accuracy": m1["views"]["SEMANTIC"][
                "mechanic_ranking_test_accuracy"
            ],
        },
        "d1_transfer_table": d1_rows,
        "d1_contrasts": {
            "typed_minus_transcript": d1["typed_minus_transcript"],
            "typed_minus_same_information_serialized": d1[
                "typed_minus_same_information_serialized"
            ],
        },
        "explicit_inference_table": explicit_rows,
        "source_summary": str(SUMMARY.relative_to(HERE)),
        "authority": "DERIVED_PUBLICATION_TABLES_ONLY_NO_SCIENTIFIC_AUTHORITY",
    }


def render_markdown(tables: dict[str, Any]) -> str:
    lines = [
        "# P9 headline tables V1",
        "",
        "Derived only from `OFFICIAL_EVIDENCE_SUMMARY_V1.json`.",
        "",
        "## M1 — view accuracy versus exact empirical ceiling",
        "",
        "| View | Accuracy | Ceiling | Gap | Violation |",
        "|---|---:|---:|---:|---|",
    ]
    for row in tables["m1_view_ceiling_table"]:
        lines.append(
            f"| {row['view']} | {_fmt(row['accuracy'])} | {_fmt(row['ceiling'])} | "
            f"{_fmt(row['gap_to_ceiling'])} | {row['ceiling_violation']} |"
        )
    lines.extend(
        [
            "",
            "## D1 — protected whole-domain transfer",
            "",
            "| Arm | Selected model | Accuracy | Macro-F1 | Double corruption | UNRESOLVED |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in tables["d1_transfer_table"]:
        lines.append(
            f"| {row['arm']} | `{row['selected_model']}` | {_fmt(row['test_accuracy'])} | "
            f"{_fmt(row['macro_f1'])} | {_fmt(row['double_corruption_accuracy'])} | "
            f"{_fmt(row['unresolved_accuracy'])} |"
        )
    lines.extend(
        [
            "",
            f"Typed relational minus transcript: **{_fmt(tables['d1_contrasts']['typed_minus_transcript'])}**.",
            f"Typed relational minus same-information serialization: **{_fmt(tables['d1_contrasts']['typed_minus_same_information_serialized'])}**.",
            "",
            "## Explicit-inference closure",
            "",
            "| Atom | Weaker view | Weaker accuracy | Sufficient view | Sufficient accuracy | Interpretation |",
            "|---|---|---:|---|---:|---|",
        ]
    )
    for row in tables["explicit_inference_table"]:
        lines.append(
            f"| {row['atom']} | {row['weaker_view']} | {_fmt(row['weaker_accuracy'])} | "
            f"{row['sufficient_view']} | {_fmt(row['sufficient_accuracy'])} | {row['interpretation']} |"
        )
    return "\n".join(lines) + "\n"


def render_latex(tables: dict[str, Any]) -> str:
    lines = [
        "% Generated by build_headline_tables.py; do not edit by hand.",
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{M1 protected accuracy versus the exact empirical deterministic ceiling induced by each frozen view.}",
        r"\label{tab:m1-ceilings}",
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        f"View & Accuracy & Ceiling & Gap {LATEX_ROW_BREAK}",
        r"\midrule",
    ]
    for row in tables["m1_view_ceiling_table"]:
        lines.append(
            f"{_latex_escape(row['view'])} & {_fmt(row['accuracy'])} & {_fmt(row['ceiling'])} & "
            f"{_fmt(row['gap_to_ceiling'])} {LATEX_ROW_BREAK}"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])

    lines.extend(
        [
            r"\begin{table*}[t]",
            r"\centering",
            r"\caption{D1 protected whole-domain transfer to transactional workflows. The typed serialized bag exposes the same typed semantic fields as the relational arm but removes the explicit relational comparison.}",
            r"\label{tab:d1-transfer}",
            r"\begin{tabular}{llrrrr}",
            r"\toprule",
            f"Arm & Selected model & Accuracy & Macro-F1 & Double corruption & UNRESOLVED {LATEX_ROW_BREAK}",
            r"\midrule",
        ]
    )
    for row in tables["d1_transfer_table"]:
        lines.append(
            f"{_latex_escape(row['arm'])} & {_latex_escape(row['selected_model'])} & "
            f"{_fmt(row['test_accuracy'])} & {_fmt(row['macro_f1'])} & "
            f"{_fmt(row['double_corruption_accuracy'])} & {_fmt(row['unresolved_accuracy'])} "
            f"{LATEX_ROW_BREAK}"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""])
    return "\n".join(lines) + "\n"


def main() -> None:
    summary = _load_summary()
    tables = build_tables(summary)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(tables, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(tables), encoding="utf-8")
    OUT_TEX.write_text(render_latex(tables), encoding="utf-8")
    print(OUT_JSON.relative_to(HERE))
    print(OUT_MD.relative_to(HERE))
    print(OUT_TEX.relative_to(HERE))


if __name__ == "__main__":
    main()
