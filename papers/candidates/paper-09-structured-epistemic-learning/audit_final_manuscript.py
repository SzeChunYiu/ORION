from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
MANUSCRIPT = HERE / "manuscript" / "main.tex"
BIB = HERE / "manuscript" / "references.bib"

REQUIRED_CITATION_KEYS = {
    "ying2021graphormer",
    "hu2020hgt",
    "rampasek2022gps",
    "gebhart2021knowledge",
    "bodnar2022sheaf",
    "velickovic2022clrs",
    "bounsi2024transnar",
    "ellis2020dreamcoder",
    "grand2023lilo",
    "hao2024coconut",
    "goyal2021nps",
    "posner2026mwm",
    "lo2026serialization",
    "liem2026temporal",
    "anonymous2026chokepoints",
    "li2025questbench",
}

FORBIDDEN_FINAL_MARKERS = {
    r"\pending",
    "PENDING_OFFICIAL_RECEIPT",
    "PENDING\\_OFFICIAL\\_RECEIPT",
    "currently pending",
    "still-running",
}

FORBIDDEN_OVERCLAIM_PHRASES = {
    "we introduce relational inductive bias",
    "we discover that serialization loses structure",
    "we are the first to separate representation from reasoning failure",
    "we solve compositional generalization",
    "we introduce a new sheaf",
    "we introduce a new graph neural architecture",
    "we introduce a new neuro-symbolic architecture",
}

REQUIRED_BOUNDARY_PHRASES = {
    "not a new theorem",
    "not a new graph",
    "whole held-out domain",
    "same-information",
    "no neural architecture",
}


def _fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    if not MANUSCRIPT.is_file() or not BIB.is_file():
        _fail("missing final manuscript or bibliography")
    text = MANUSCRIPT.read_text(encoding="utf-8")
    lower = text.lower()
    bib = BIB.read_text(encoding="utf-8")

    for marker in sorted(FORBIDDEN_FINAL_MARKERS):
        if marker in text:
            _fail(f"final manuscript still contains pending marker: {marker!r}")

    for phrase in sorted(FORBIDDEN_OVERCLAIM_PHRASES):
        if phrase in lower:
            _fail(f"final manuscript contains prohibited overclaim phrase: {phrase!r}")

    for phrase in sorted(REQUIRED_BOUNDARY_PHRASES):
        if phrase.lower() not in lower:
            _fail(f"final manuscript lacks required bounded-scope phrase: {phrase!r}")

    missing_bib = sorted(key for key in REQUIRED_CITATION_KEYS if f"{{{key}," not in bib)
    if missing_bib:
        _fail(f"bibliography lacks required donor keys: {missing_bib!r}")

    missing_cites = sorted(
        key
        for key in REQUIRED_CITATION_KEYS
        if key not in text
    )
    if missing_cites:
        _fail(f"manuscript body does not cite required donor keys: {missing_cites!r}")

    required_inputs = {
        r"\input{generated_result_macros.tex}",
        r"\input{generated_headline_tables.tex}",
    }
    missing_inputs = sorted(item for item in required_inputs if item not in text)
    if missing_inputs:
        _fail(f"final manuscript does not consume generated evidence artifacts: {missing_inputs!r}")

    if "Anonymous Authors" not in text:
        _fail("double-blind manuscript no longer uses Anonymous Authors")

    print("P9 final manuscript claim/citation/evidence audit: PASS")


if __name__ == "__main__":
    main()
