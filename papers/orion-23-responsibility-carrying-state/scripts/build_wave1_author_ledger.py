#!/usr/bin/env python3
"""Build the private author-context atomic inventory before blind review."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-23-responsibility-carrying-state"
SOURCE = PAPER / "journal_package/wave1_current/source/main.tex"
OUTPUT = PAPER / "wave1_closeout/private_evidence/AUTHOR_ATOMIC_CLAIM_LEDGER.csv"


def clean(text: str) -> str:
    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\cite\w*\{[^}]*\}", "[cited source]", text)
    text = re.sub(r"\\(?:textbf|emph|paragraph|section|subsection)\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\(?:ref|eqref)\{[^}]*\}", "referenced display", text)
    text = re.sub(r"\$([^$]*)\$", r"\1", text)
    text = text.replace("\\%", "%").replace("~", " ").replace("&", " and ")
    text = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?", " ", text)
    text = text.replace("{", "").replace("}", "").replace("\\", " ")
    return re.sub(r"\s+", " ", text).strip(" .")


def classify(section: str, proposition: str):
    low = proposition.lower()
    if section == "Reproducibility and availability":
        return "availability", "VERIFIED", "current anonymous source/review archives and independent verifier", "Anonymous-review scope only; public deposition remains a human filing action."
    if "[cited source]" in proposition or section == "Related work and claim boundary":
        return "literature", "VERIFIED", "current bibliography plus live identity audit dated 2026-08-28", "No component-priority claim; one unverified candidate donor was excluded."
    if section in {"Evaluation design", "Results"} or any(token in low for token in ("1,797", "17,970", "24/24", "48/48", "60/60", "0.970", "0.238", "0.396", "48.44", "44.44", "3,840", "2,304")):
        return "empirical_or_finite_result", "VERIFIED", "anonymous row-level review data and standard-library independent verifier", "One learned dataset or complete registered finite panel; no population or deployment authority."
    if section == "Responsibility-relative support":
        return "definition_or_proposition", "VERIFIED", "definition, direct proof, and finite collision witnesses", "Exact only on a declared world set and responsibility."
    if section == "Limitations":
        return "boundary", "BOUNDED_INFERENCE", "current evidence hierarchy and retained adverse measurement", "Anti-generalization statement must remain at least this strong."
    return "interpretation", "BOUNDED_INFERENCE", "current manuscript evidence hierarchy", "Must remain within one learned dataset and three finite panels."


def main() -> None:
    rows = []
    section = "Abstract"
    buffer = []
    start = 1
    in_table = False

    def add(text: str, location: str) -> None:
        for proposition in re.split(r"(?<=[.!?])\s+(?=[A-Z])|;\s+(?=[A-Za-z])", clean(text)):
            if len(proposition) < 15:
                continue
            kind, status, warrant, scope = classify(section, proposition)
            rows.append({
                "atomic_id": f"AC-{len(rows)+1:03d}",
                "location": location,
                "exact_atomic_proposition": proposition,
                "claim_class": kind,
                "importance": "headline" if any(x in proposition.lower() for x in ("responsibility-relative", "current provenance", "high confidence", "does not establish")) else "supporting",
                "scope_and_qualifiers": scope,
                "warrant_pointer": warrant,
                "independent_check": "PENDING_BLIND_COVERAGE",
                "status": status,
                "release_action": "retain at current scope; narrow or remove if blind review does not find entailment",
            })

    lines = SOURCE.read_text().splitlines()
    for number, line in enumerate(lines, 1):
        heading = re.search(r"\\section\{([^}]*)\}", line)
        if heading:
            if buffer: add(" ".join(buffer), f"{section}; source lines {start}-{number-1}")
            buffer = []
            section = heading.group(1)
            start = number + 1
            continue
        if "\\begin{table" in line or "\\begin{tabular" in line:
            if buffer: add(" ".join(buffer), f"{section}; source lines {start}-{number-1}")
            buffer = []
            in_table = True
            continue
        if "\\end{table" in line or "\\end{tabular" in line:
            in_table = False
            start = number + 1
            continue
        if in_table or line.lstrip().startswith(("\\document", "\\usepackage", "\\title", "\\author", "\\def", "\\new", "\\begin", "\\end", "\\bibliograph")):
            continue
        if not line.strip():
            if buffer: add(" ".join(buffer), f"{section}; source lines {start}-{number-1}")
            buffer = []
            start = number + 1
        else:
            buffer.append(line)
    if buffer: add(" ".join(buffer), f"{section}; source lines {start}-{len(lines)}")

    table_propositions = [
        "The learned-data study contains 1,797 source items and 3,594 responsibility episodes per policy arm.",
        "Responsibility-relative and always-raw policies have combined accuracy 0.944 and exact-digit accuracy 0.970.",
        "Responsibility-relative routing reads 33 state values per episode versus 64 for always raw.",
        "Confidence-only exact-digit accuracy is 0.396 with unsupported reuse rate 0.777.",
        "Provenance-only and unqualified exact-digit accuracy is 0.238 with unsupported reuse rate 1.000.",
        "In the 12-case old/new formula panel, responsibility-relative and always-raw policies are correct on 24 of 24 episodes.",
        "Confidence-only and provenance-only policies are correct on 12 of 24 formula episodes and make 12 stale reuses.",
        "In the 48-case provenance comparison, each provenance-tiered arm is correct on 36 cases and makes 12 unsupported reuses.",
        "Responsibility-relative, composed, and always-raw policies are correct on all 48 provenance-comparison cases.",
        "In the 60-case transport panel, unconditional transport makes 40 unsound transports and is verifier-correct on 40 cases.",
        "Signature equality and always reissuing make 20 needless reissues each.",
        "The local drift-bound rule is verifier-correct on all 60 cases with zero unsound transport and zero needless reissue.",
    ]
    section = "Results"
    for proposition in table_propositions: add(proposition, "Tables 1-4")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    print(f"wrote {len(rows)} atomic rows to {OUTPUT}")


if __name__ == "__main__":
    main()
