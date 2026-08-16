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


def test_all_five_canonical_manuscripts_are_structurally_complete():
    for paper_id, paper in PAPERS.items():
        manuscript = paper / "manuscript"
        files, tex = _collect_tex(manuscript)
        assert files, paper_id
        assert "\\begin{abstract}" in tex and "\\end{abstract}" in tex, paper_id
        assert "\\textbf{Keywords:" in tex, paper_id
        assert "\\bibliography{bibliography}" in tex, paper_id
        assert "CANNOT\\_CHECK" in tex, f"{paper_id} must preserve the external evidence boundary"

        protocol = json.loads((paper / "protocol" / "PROTOCOL_V1.json").read_text(encoding="utf-8"))
        assert protocol["protocol_id"] in tex, f"{paper_id} manuscript must name its prospective protocol"
        assert protocol["protocol_status"] == "DESIGN_FROZEN"
        assert protocol["outcome_accessed"] is False


def test_all_manuscript_citations_resolve_to_local_bibliography_keys():
    for paper_id, paper in PAPERS.items():
        manuscript = paper / "manuscript"
        _, tex = _collect_tex(manuscript)
        citations = _citation_keys(tex)
        bibliography = manuscript / "bibliography.bib"
        assert bibliography.exists(), paper_id
        bib_text = bibliography.read_text(encoding="utf-8")
        bib_keys = set(BIB_KEY_RE.findall(bib_text))
        missing = sorted(citations - bib_keys)
        assert not missing, f"{paper_id} missing bibliography entries: {missing}"


def test_no_duplicate_bibliography_keys_within_a_paper():
    for paper_id, paper in PAPERS.items():
        bib_text = (paper / "manuscript" / "bibliography.bib").read_text(encoding="utf-8")
        keys = BIB_KEY_RE.findall(bib_text)
        duplicates = sorted({key for key in keys if keys.count(key) > 1})
        assert not duplicates, f"{paper_id} duplicate bibliography keys: {duplicates}"
