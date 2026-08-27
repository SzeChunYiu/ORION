from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANUSCRIPT_DIR = HERE / "manuscript"
MANUSCRIPT = MANUSCRIPT_DIR / "main.tex"
BIB = MANUSCRIPT_DIR / "references.bib"

#: ``main.tex`` carries the preamble and a list of ``\input`` lines; the prose
#: lives in ``manuscript/sections/NN-name.tex`` and the evidence tables in the
#: generated artifacts. Auditing ``main.tex`` alone would therefore audit the
#: preamble and find none of the claims, citations or forbidden phrases it is
#: supposed to police -- and report PASS for having read nothing. The audit
#: assembles the same document LaTeX does before checking it.
_INPUT = re.compile(r"\\input\{([^}]+)\}")


def assemble(entry: Path, _seen: frozenset[Path] = frozenset()) -> str:
    r"""``entry`` with every ``\input`` file it pulls in, resolved recursively.

    A cycle or a missing file yields the unresolved ``\input`` line rather than
    an exception: the audit's job is to fail on manuscript content, and the
    LaTeX build is what fails on a broken include.
    """

    text = entry.read_text(encoding="utf-8")
    seen = _seen | {entry.resolve()}

    def expand(match: re.Match[str]) -> str:
        target = MANUSCRIPT_DIR / match.group(1)
        if target.suffix != ".tex":
            target = target.with_suffix(".tex")
        if not target.is_file() or target.resolve() in seen:
            return match.group(0)
        return match.group(0) + "\n" + assemble(target, seen)

    return _INPUT.sub(expand, text)


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
    "kassenaar2026when",
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

# Each tuple is a semantic alternative set: at least one phrase must be present.
REQUIRED_BOUNDARY_ALTERNATIVES = (
    ("not a new theorem", "is not a new theorem", "the collision-derived ceiling below is not a new theorem"),
    ("not a new graph", "do not introduce a new graph", "does not introduce a new graph"),
    ("whole held-out domain",),
    ("same-information",),
    ("no neural architecture", "do not introduce a new neural architecture"),
)


def _fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    if not MANUSCRIPT.is_file() or not BIB.is_file():
        _fail("missing final manuscript or bibliography")
    text = assemble(MANUSCRIPT)
    lower = text.lower()
    bib = BIB.read_text(encoding="utf-8")

    for marker in sorted(FORBIDDEN_FINAL_MARKERS):
        if marker in text:
            _fail(f"final manuscript still contains pending marker: {marker!r}")

    for phrase in sorted(FORBIDDEN_OVERCLAIM_PHRASES):
        if phrase in lower:
            _fail(f"final manuscript contains prohibited overclaim phrase: {phrase!r}")

    for alternatives in REQUIRED_BOUNDARY_ALTERNATIVES:
        if not any(phrase.lower() in lower for phrase in alternatives):
            _fail(f"final manuscript lacks required bounded-scope meaning: one of {alternatives!r}")

    missing_bib = sorted(key for key in REQUIRED_CITATION_KEYS if f"{{{key}," not in bib)
    if missing_bib:
        _fail(f"bibliography lacks required donor keys: {missing_bib!r}")

    missing_cites = sorted(key for key in REQUIRED_CITATION_KEYS if key not in text)
    if missing_cites:
        _fail(f"manuscript body does not cite required donor keys: {missing_cites!r}")

    required_inputs = {r"\input{generated_result_macros.tex}", r"\input{generated_headline_tables.tex}"}
    missing_inputs = sorted(item for item in required_inputs if item not in text)
    if missing_inputs:
        _fail(f"final manuscript does not consume generated evidence artifacts: {missing_inputs!r}")

    if "Anonymous Authors" not in text:
        _fail("double-blind manuscript no longer uses Anonymous Authors")

    print("P9 final manuscript claim/citation/evidence audit: PASS")


if __name__ == "__main__":
    main()
