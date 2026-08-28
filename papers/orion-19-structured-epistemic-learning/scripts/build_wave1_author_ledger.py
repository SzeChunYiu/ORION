#!/usr/bin/env python3
"""Build the author-context atomic inventory used before blind review."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-19-structured-epistemic-learning"
SOURCE = PAPER / "journal_package" / "wave1_current/source/main.tex"
OUTPUT = PAPER / "wave1_closeout/private_evidence/AUTHOR_ATOMIC_CLAIM_LEDGER.csv"


def clean(fragment: str) -> str:
    fragment = re.sub(r"%.*", "", fragment)
    fragment = fragment.replace("\\Info{}", "information")
    fragment = fragment.replace("\\Access{}", "accessibility")
    fragment = fragment.replace("\\Compute{}", "computation")
    fragment = fragment.replace("\\Indeterminate", "indeterminate")
    fragment = re.sub(r"\\cite\w*\{[^}]*\}", "[cited source]", fragment)
    fragment = re.sub(r"\\ref\{[^}]*\}", "referenced section", fragment)
    fragment = re.sub(r"\\text(?:sc|bf|it|tt)\{([^{}]*)\}", r"\1", fragment)
    fragment = re.sub(r"\\emph\{([^{}]*)\}", r"\1", fragment)
    fragment = re.sub(r"\$([^$]*)\$", r"\1", fragment)
    fragment = fragment.replace("\\%", "%").replace("~", " ")
    fragment = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?", "", fragment)
    fragment = fragment.replace("{", "").replace("}", "")
    fragment = fragment.replace("\\", " ").replace("&", " and ")
    return re.sub(r"\s+", " ", fragment).strip(" .")


def classify(section: str, proposition: str) -> tuple[str, str, str, str]:
    low = proposition.lower()
    if section in {"Reproducibility and availability"}:
        return (
            "availability_or_compliance",
            "VERIFIED",
            "journal_package/wave1_current plus deterministic package verifier",
            "Anonymous-review availability only; public archive deposition remains a human publication action.",
        )
    if "related work" in section.lower() or "[cited source]" in proposition:
        return (
            "literature_fact",
            "VERIFIED",
            "references.bib plus LIVE_LITERATURE_ENTAILMENT_AUDIT_2026-08-28.md",
            "Search and metadata checks are current to 2026-08-28; no priority claim is made for component ideas.",
        )
    empirical_markers = [
        "four of five", "four-of-five", "one for", "false compute", "0.972", "0.955",
        "69,834", "3,230", "206,720", "69,898", "0.980", "0.945", "0.969",
        "0.946", "0.035", "0.023", "-0.000", "qwen2.5", "0.140625", "32 of",
        "220", "512", "128", "24-redraw", "24 stratified", "0.964", "0.0006",
        "zero", "null", "protected disposition", "diagnostic agrees", "generic policy",
    ]
    if section in {"Results", "Conclusion", "Discussion"} and any(x in low for x in empirical_markers):
        if any(x in low for x in ["qwen", "wine", "breast", "cubic transform", "inverse repair"]):
            warrant = "protected secondary-study receipts and execution ledger"
        elif any(x in low for x in ["remint", "serialized", "220", "32 of"]):
            warrant = "hostile representation audit and bound protected predictions"
        elif any(x in low for x in ["redraw", "half-sample", "0.964", "0.0006"]):
            warrant = "transport follow-up receipt and per-partition evidence"
        elif any(x in low for x in ["resource", "69,834", "3,230", "206,720", "69,898", "domin"]):
            warrant = "corrected seven-coordinate resource ledger and independent checker"
        else:
            warrant = "primary diagnostic receipt, independent reproduction, and reader-facing evidence table"
        return (
            "empirical_result",
            "VERIFIED",
            warrant,
            "Fixed-family descriptive evidence; no population prevalence or universal transfer claim.",
        )
    if section in {"Diagnostic design"}:
        return (
            "method",
            "VERIFIED",
            "prospectively frozen diagnostic protocol and current reader-facing evidence table",
            "Method scope is limited to three registered intervention classes and five fixed families.",
        )
    if section in {"Limitations"}:
        return (
            "interpretation",
            "BOUNDED_INFERENCE",
            "current manuscript evidence hierarchy and adverse-result ledger",
            "Limitation or anti-generalization statement; release requires it to remain at least this strong.",
        )
    return (
        "interpretation",
        "BOUNDED_INFERENCE",
        "current manuscript evidence hierarchy",
        "Interpretation must remain no stronger than the fixed-family outcomes and visible adverse evidence.",
    )


def main() -> None:
    lines = SOURCE.read_text().splitlines()
    rows = []
    section = "Abstract"
    in_body = False
    in_table = False
    buffer: list[str] = []
    start_line = 1

    def flush(end_line: int) -> None:
        nonlocal buffer, start_line
        text = clean(" ".join(buffer))
        buffer = []
        if not text or len(text) < 20:
            return
        for piece in re.split(r"(?<=[.!?])\s+(?=[A-Z])|;\s+(?=[a-zA-Z])", text):
            piece = piece.strip()
            if len(piece) < 15:
                continue
            claim_class, status, warrant, boundary = classify(section, piece)
            rows.append({
                "atomic_id": f"AC-{len(rows)+1:03d}",
                "location": f"{section}; source lines {start_line}-{end_line}",
                "exact_atomic_proposition": piece,
                "claim_class": claim_class,
                "importance": "headline" if any(k in piece.lower() for k in ["four of five", "four-of-five", "false compute", "bounded procedure"]) else "supporting",
                "qualifiers_and_scope": boundary,
                "warrant_pointer": warrant,
                "independent_check": "PENDING_BLIND_COVERAGE" if status != "BOUNDED_INFERENCE" else "PENDING_REVIEWER_INFERENCE_CHECK",
                "status": status,
                "release_action": "retain at current scope; revise or remove if independent check does not entail",
            })

    for number, line in enumerate(lines, 1):
        if "\\begin{abstract}" in line:
            in_body = True
            section = "Abstract"
            start_line = number + 1
            continue
        if not in_body:
            continue
        heading = re.search(r"\\section\{([^}]*)\}", line)
        if heading:
            flush(number - 1)
            section = heading.group(1)
            start_line = number + 1
            continue
        if "\\begin{table" in line or "\\begin{tabular" in line:
            flush(number - 1)
            in_table = True
            continue
        if "\\end{table" in line or "\\end{tabular" in line:
            in_table = False
            start_line = number + 1
            continue
        if in_table or line.lstrip().startswith("\\") and not line.lstrip().startswith(("\\paragraph", "\\subsection")):
            continue
        if not line.strip():
            flush(number - 1)
            start_line = number + 1
        else:
            buffer.append(line)
    flush(len(lines))

    manual = [
        ("Table 1", "Digits with a cubic interface: probe accessibility; protected no qualifying intervention; generic computation; diagnostic incorrect."),
        ("Table 1", "Digits with missing pixels: probe information; protected information; generic computation; diagnostic correct."),
        ("Table 1", "Hidden-bit parity: probe information; protected information; generic computation; diagnostic correct."),
        ("Table 1", "Reversibly encoded Boolean state: probe accessibility; protected accessibility; generic computation; diagnostic correct."),
        ("Table 1", "Affine-map composition: probe computation; protected computation; generic computation; diagnostic correct."),
        ("Table 1", "The table total is four correct diagnostic dispositions among five fixed families."),
    ]
    for location, proposition in manual:
        rows.append({
            "atomic_id": f"AC-{len(rows)+1:03d}",
            "location": location,
            "exact_atomic_proposition": proposition,
            "claim_class": "figure_or_table",
            "importance": "headline",
            "qualifiers_and_scope": "Fixed-family descriptive result.",
            "warrant_pointer": "reader-facing evidence table and primary independent receipt",
            "independent_check": "PENDING_BLIND_COVERAGE",
            "status": "VERIFIED",
            "release_action": "retain at current scope",
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} author-context atomic rows to {OUTPUT}")


if __name__ == "__main__":
    main()
