#!/usr/bin/env python3
"""Approximate NMI Article word/display budget for the Paper 2 TeX source.

The counter is deliberately transparent rather than presented as the journal's
submission-system count. It removes comments, math, figure/table environments,
citations, labels, references and TeX control sequences, then counts visible
word-like tokens. Values expanded from custom macros can differ slightly in the
compiled manuscript, so the report retains a conservative over-limit verdict.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "papers/paper-02-open-world-scientific-discovery/manuscript"


def remove_environment(text: str, name: str) -> str:
    pattern = re.compile(
        rf"\\begin\{{{re.escape(name)}\}}.*?\\end\{{{re.escape(name)}\}}",
        re.DOTALL,
    )
    previous = None
    while text != previous:
        previous = text
        text = pattern.sub(" ", text)
    return text


def visible_words(text: str) -> list[str]:
    text = re.sub(r"(?<!\\)%.*", " ", text)
    for environment in (
        "figure",
        "figure*",
        "table",
        "table*",
        "equation",
        "equation*",
        "align",
        "align*",
        "gather",
        "gather*",
        "tikzpicture",
    ):
        text = remove_environment(text, environment)
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.DOTALL)
    text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.DOTALL)
    text = re.sub(r"(?<!\\)\$.*?(?<!\\)\$", " ", text, flags=re.DOTALL)
    text = re.sub(
        r"\\(?:cite\w*|ref|pageref|label|bibliography|bibliographystyle|input)"
        r"\*?(?:\[[^]]*\])?\{[^{}]*\}",
        " ",
        text,
    )
    text = re.sub(r"\\begin\{[^{}]*\}|\\end\{[^{}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^]]*\])?", " ", text)
    text = re.sub(r"\\.", " ", text)
    text = text.replace("{", " ").replace("}", " ").replace("~", " ")
    return re.findall(r"\b[\w]+(?:[-'][\w]+)*\b", text, flags=re.UNICODE)


def between(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


def main() -> None:
    main_text = (MANUSCRIPT / "main.tex").read_text()
    section = MANUSCRIPT / "sections"

    components = {
        "introduction_opening": between(
            main_text,
            r"\section{Introduction}",
            r"\section{Question-conditioned cumulative read state}",
        ),
        "state_and_stopping_setup": between(
            main_text,
            r"\section{Question-conditioned cumulative read state}",
            r"\input{sections/acquisition_authority}",
        ),
        "acquisition_authority_synthesis": (
            section / "acquisition_authority.tex"
        ).read_text(),
        "formal_mechanics": (section / "formalism.tex").read_text(),
        "envelope_theory": (
            section / "acquisition_authority-envelope.tex"
        ).read_text(),
        "empirical_results": (section / "results.tex").read_text(),
        "public_screening_transport": (
            section / "05a-public-screening-transport.tex"
        ).read_text(),
        "post_saturation_validation": (
            section / "p2x_unresolved_route_successor.tex"
        ).read_text(),
        "successor_interface": (
            section / "structure-conditioned-discovery-interface.tex"
        ).read_text(),
        "related_work": between(
            main_text,
            r"\section{Related work}",
            r"\section{Limitations and integrity}",
        ),
        "limitations_and_integrity": between(
            main_text,
            r"\section{Limitations and integrity}",
            r"\input{sections/availability}",
        ),
        "conclusion": between(
            main_text,
            r"\section{Conclusion}",
            r"\bibliographystyle{plain}",
        ),
    }
    counts = {name: len(visible_words(text)) for name, text in components.items()}

    abstract = between(main_text, r"\begin{abstract}", r"\end{abstract}")
    abstract_words = len(visible_words(abstract))
    methods_words = len(visible_words((section / "methods.tex").read_text()))

    display_sources = [main_text, *components.values(), (section / "methods.tex").read_text()]
    figures = sum(len(re.findall(r"\\begin\{figure\*?\}", text)) for text in display_sources)
    tables = sum(len(re.findall(r"\\begin\{table\*?\}", text)) for text in display_sources)

    bibliography_entries = 0
    for name in ("bibliography.bib", "novelty_refresh_2026.bib"):
        bibliography_entries += len(
            re.findall(r"(?m)^\s*@\w+\s*\{", (MANUSCRIPT / name).read_text())
        )

    result = {
        "measurement": "transparent approximate visible-word count",
        "abstract_words": abstract_words,
        "abstract_limit": 150,
        "counted_main_text_words": sum(counts.values()),
        "counted_main_text_limit": 3500,
        "component_words": counts,
        "methods_words_excluded_from_nmi_main_limit": methods_words,
        "main_figures": figures,
        "main_tables": tables,
        "main_displays_combined": figures + tables,
        "main_display_limit": 6,
        "bibliography_entries": bibliography_entries,
        "typical_reference_ceiling": 50,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
