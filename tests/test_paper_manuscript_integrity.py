from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPERS = {
    "P1": ROOT / "papers" / "paper-01-recursive-epistemic-reconstruction",
    "P2": ROOT / "papers" / "paper-02-open-world-scientific-discovery",
    "P3": ROOT / "papers" / "paper-03-global-knowledge-portrait",
    "P4": ROOT / "papers" / "paper-04-verified-scientific-discovery",
    "P5": ROOT / "papers" / "paper-05-self-orion",
}

INPUT_RE = re.compile(r"\\input\{([^}]+)\}")
CITE_RE = re.compile(r"\\cite(?:t|p)?\{([^}]+)\}")
BIB_KEY_RE = re.compile(r"@\w+\{\s*([^,\s]+)\s*,", re.MULTILINE)
BIBLIOGRAPHY_DECLARATION_RE = re.compile(r"\\bibliography\{([^}]+)\}")


def _collect_tex(manuscript: Path) -> tuple[list[Path], str]:
    pending = [manuscript / "main.tex"]
    seen: set[Path] = set()
    chunks: list[str] = []
    while pending:
        path = pending.pop()
        assert path.exists(), f"missing manuscript input: {path}"
        path = path.resolve()
        if path in seen:
            continue
        seen.add(path)
        text = path.read_text(encoding="utf-8")
        chunks.append(text)
        for raw in INPUT_RE.findall(text):
            child = manuscript / raw
            if child.suffix != ".tex":
                child = child.with_suffix(".tex")
            pending.append(child)
    return sorted(seen), "\n".join(chunks)


def _citation_keys(tex: str) -> set[str]:
    keys: set[str] = set()
    for group in CITE_RE.findall(tex):
        keys.update(part.strip() for part in group.split(",") if part.strip())
    return keys


def _bibliography_names(tex: str, paper_id: str) -> list[str]:
    """The .bib basenames a manuscript loads, from its own `\\bibliography{...}`.

    A manuscript may split its bibliography across several files. Hard-coding
    `\\bibliography{bibliography}` made every key defined in a second file look
    like a missing entry, which reads as a broken manuscript and invites deleting
    real citations to satisfy the checker. Reading the declaration keeps the
    check on what LaTeX will actually resolve.
    """

    match = BIBLIOGRAPHY_DECLARATION_RE.search(tex)
    assert match, f"{paper_id} manuscript declares no \\bibliography{{...}}"
    return [part.strip() for part in match.group(1).split(",") if part.strip()]


def _bibliography_keys(manuscript: Path, tex: str, paper_id: str) -> list[str]:
    """Every key defined across the loaded .bib files, duplicates preserved."""

    keys: list[str] = []
    for name in _bibliography_names(tex, paper_id):
        path = manuscript / f"{name}.bib"
        assert path.exists(), f"{paper_id} loads a bibliography that does not exist: {path.name}"
        keys.extend(BIB_KEY_RE.findall(path.read_text(encoding="utf-8")))
    return keys


def _unbound_values(value: object) -> list[str]:
    if isinstance(value, dict):
        result: list[str] = []
        for item in value.values():
            result.extend(_unbound_values(item))
        return result
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(_unbound_values(item))
        return result
    return [str(value)] if value == "UNBOUND" else []


#: The three-valued boundary, in the two forms a manuscript may state it.
#:
#: This used to be one check: the literal token ``CANNOT\\_CHECK`` had to appear
#: in the TeX. The token is internal vocabulary, and a manuscript that spells the
#: idea out in prose instead is stating the boundary *better*, not dropping it --
#: so requiring the token would push papers to keep a machine identifier in their
#: body to satisfy a test. What has to survive is the distinction itself: an
#: outcome that could not be determined is reported separately from one
#: determined to be false, and the two are never merged.
#:
#: So either form is accepted, and the prose form is not a loophole: it must name
#: the third value, name the negative it is being kept apart from, and say they
#: are kept apart -- all three in one sentence. A paper that quietly drops the
#: boundary satisfies neither branch.
THIRD_VALUE_TERMS = ("undetermined", "indeterminate", "could not be determined")
NEGATIVE_RESULT_TERMS = (
    "is false",
    "to be false",
    "a negative",
    "negative result",
    "evidence of absence",
    "refuted",
)
SEPARATION_TERMS = (
    "separately",
    "never merged",
    "never silently resolved",
    "distinct from",
    "not the same as",
    "rather than",
)


def _states_the_three_valued_boundary(tex: str) -> bool:
    """True when one sentence names the third value, the negative, and their separation."""

    flat = " ".join(tex.split()).lower()
    for sentence in re.split(r"(?<=[.;])\s+", flat):
        if not any(term in sentence for term in THIRD_VALUE_TERMS):
            continue
        if not any(term in sentence for term in NEGATIVE_RESULT_TERMS):
            continue
        if any(term in sentence for term in SEPARATION_TERMS):
            return True
    return False


def test_all_five_canonical_manuscripts_are_structurally_complete():
    for paper_id, paper in PAPERS.items():
        manuscript = paper / "manuscript"
        files, tex = _collect_tex(manuscript)
        assert files, paper_id
        assert "\\begin{abstract}" in tex and "\\end{abstract}" in tex, paper_id
        assert "\\textbf{Keywords:" in tex, paper_id
        assert _bibliography_names(tex, paper_id), paper_id
        assert "CANNOT\\_CHECK" in tex or _states_the_three_valued_boundary(tex), (
            f"{paper_id} must preserve the external evidence boundary: either the "
            "machine token, or one sentence naming the third value, the negative it "
            "is kept apart from, and that they are kept apart"
        )

        protocol = json.loads((paper / "protocol" / "PROTOCOL_V1.json").read_text(encoding="utf-8"))
        assert protocol["protocol_id"] in tex, f"{paper_id} manuscript must name its prospective protocol"
        assert protocol["protocol_status"] in {"DESIGN_FROZEN", "EXECUTION_FROZEN"}
        assert protocol["outcome_accessed"] is False
        if protocol["protocol_status"] == "EXECUTION_FROZEN":
            assert not _unbound_values(protocol["execution_bindings"]), (
                f"{paper_id} may be EXECUTION_FROZEN only with concrete bindings"
            )


def test_all_manuscript_citations_resolve_to_local_bibliography_keys():
    for paper_id, paper in PAPERS.items():
        manuscript = paper / "manuscript"
        _, tex = _collect_tex(manuscript)
        citations = _citation_keys(tex)
        bib_keys = set(_bibliography_keys(manuscript, tex, paper_id))
        missing = sorted(citations - bib_keys)
        assert not missing, f"{paper_id} missing bibliography entries: {missing}"


def test_no_duplicate_bibliography_keys_within_a_paper():
    for paper_id, paper in PAPERS.items():
        manuscript = paper / "manuscript"
        _, tex = _collect_tex(manuscript)
        # Across every loaded file, not within each one: the same key defined in
        # two bib files is exactly the collision this test exists to catch, and
        # checking them separately would miss it.
        keys = _bibliography_keys(manuscript, tex, paper_id)
        duplicates = sorted({key for key in keys if keys.count(key) > 1})
        assert not duplicates, f"{paper_id} duplicate bibliography keys: {duplicates}"
