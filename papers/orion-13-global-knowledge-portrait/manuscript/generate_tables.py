#!/usr/bin/env python3
"""Generate the two manuscript tables from the frozen confirmatory analysis."""

from __future__ import annotations

import json
from pathlib import Path


MANUSCRIPT = Path(__file__).resolve().parent
PAPER = MANUSCRIPT.parent
ANALYSIS = (
    PAPER
    / "evidence"
    / "public-reference-v1.1-confirmatory"
    / "CONFIRMATORY_ANALYSIS.json"
)
OUT = MANUSCRIPT / "tables"


def fmt(value: float) -> str:
    return f"{value:.4f}"


def main() -> int:
    data = json.loads(ANALYSIS.read_text(encoding="utf-8"))
    if data["case_count"] != 32:
        raise SystemExit("confirmatory case count drift")
    families = data["by_case_family"]
    expected = {
        "different_name_same_referent": 13,
        "polarity_modality_attribution_context": 13,
        "valid_invalid_representation_mapping": 6,
    }
    observed = {key: int(families[key]["case_count"]) for key in expected}
    if observed != expected:
        raise SystemExit(f"confirmatory family composition drift: {observed}")

    OUT.mkdir(parents=True, exist_ok=True)
    family_tex = r"""\begin{table}[t]
\centering
\small
\begin{tabular}{lr}
\toprule
\textbf{Confirmatory case family} & \textbf{Cases} \\
\midrule
Different name / same referent & 13 \\
Polarity, modality, attribution, or context & 13 \\
Valid / invalid representation mapping & 6 \\
\midrule
\textbf{Total} & \textbf{32} \\
\bottomrule
\end{tabular}
\caption{Composition of the case-identifier-disjoint confirmatory public-reference holdout.}
\label{tab:confirmatory-families}
\end{table}
"""
    (OUT / "confirmatory_case_families.tex").write_text(family_tex, encoding="utf-8")

    systems = data["pooled"]["systems"]
    names = [
        ("orion", "Coordinate-governed mapping"),
        ("flat_predicate_canonicalization", "Flat predicate canonicalization"),
        ("exact_coordinate_conservative", "Exact-coordinate conservative"),
    ]
    rows: list[str] = []
    for key, label in names:
        record = systems[key]
        rows.append(
            f"{label} & {fmt(record['accuracy']['rate'])} & "
            f"{fmt(record['false_merge']['rate'])} & "
            f"{fmt(record['false_split']['rate'])} & "
            f"{fmt(record['abstention']['rate'])} \\\\" 
        )
    primary = data["pooled"]["primary_comparisons"]
    fm = primary["false_merge_orion_minus_flat"]
    fs = primary["false_split_orion_minus_exact"]
    result_tex = "\n".join(
        [
            r"\begin{table}[t]",
            r"\centering",
            r"\small",
            r"\begin{tabular}{lrrrr}",
            r"\toprule",
            r"\textbf{Rule} & \textbf{Accuracy} & \textbf{False merge} & \textbf{False split} & \textbf{Abstention} \\",
            r"\midrule",
            *rows,
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Confirmatory outcomes on 32 frozen mapping cases. Rates use one decision per case. The paired false-merge difference for coordinate-governed minus flat mapping was "
            + f"{fmt(fm['candidate_minus_baseline'])} "
            + f"(95\\% bootstrap interval [{fmt(fm['ci95_low'])}, {fmt(fm['ci95_high'])}]). "
            + r"The paired false-split difference relative to the exact-coordinate control was "
            + f"{fmt(fs['candidate_minus_baseline'])} "
            + f"([{fmt(fs['ci95_low'])}, {fmt(fs['ci95_high'])}]).}}",
            r"\label{tab:confirmatory-primary}",
            r"\end{table}",
            "",
        ]
    )
    (OUT / "confirmatory_primary_results.tex").write_text(result_tex, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
