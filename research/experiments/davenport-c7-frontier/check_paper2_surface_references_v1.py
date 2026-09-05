#!/usr/bin/env python3
"""Fail closed on stale or mistyped references in Paper 2 public surfaces."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FRONTIER = ROOT / "research/experiments/davenport-c7-frontier"
SURFACES = (
    FRONTIER / "PAPER2_TOP_SPECIALIST_THEOREM_SPINE_V1.md",
    FRONTIER / "PAPER2_MANUSCRIPT_DRAFT_V1.md",
    FRONTIER / "PAPER2_NEAREST_WORK_AUDIT_V1.md",
    FRONTIER / "A2_RADIAL_STAIRCASE_HOSTILE_AUDIT_V1.md",
)
REFERENCE_RE = re.compile(r"`([^`\n]+\.(?:md|py|json|cpp|yml))`")
FORBIDDEN_REFERENCES = {
    "A2_EXACT_RADIAL_EXCESS_V1.md",
    "check_a2_exact_radial_excess_v1.py",
    "check_a2_maximal_overlap_standard_familIES_v1.py",
}
FORBIDDEN_SNIPPETS = {
    "support-four length-`(3p-1)/2` atom",
    "length-`(3p-1)/2` support-four maximal atom",
}


def resolve_reference(reference: str) -> Path:
    if reference.startswith(".github/") or "/" in reference:
        return ROOT / reference
    return FRONTIER / reference


def main() -> None:
    for surface in SURFACES:
        assert surface.is_file(), surface

    references: list[tuple[str, str]] = []
    missing: list[tuple[str, str]] = []
    forbidden_hits: list[tuple[str, str]] = []
    snippet_hits: list[tuple[str, str]] = []

    for surface in SURFACES:
        text = surface.read_text(encoding="utf-8")
        for snippet in FORBIDDEN_SNIPPETS:
            if snippet in text:
                snippet_hits.append((surface.name, snippet))
        for reference in REFERENCE_RE.findall(text):
            references.append((surface.name, reference))
            if Path(reference).name in FORBIDDEN_REFERENCES:
                forbidden_hits.append((surface.name, reference))
            if not resolve_reference(reference).is_file():
                missing.append((surface.name, reference))

    assert not snippet_hits, snippet_hits
    assert not forbidden_hits, forbidden_hits
    assert not missing, missing
    assert any(reference == "PAPER2_MANUSCRIPT_DRAFT_V1.md" for _, reference in references)
    assert any(reference == "run_paper2_reproduction_v1.py" for _, reference in references)
    assert any(reference == ".github/workflows/shadow-davenport-paper2-a2-breakthrough.yml" for _, reference in references)

    spine = SURFACES[0].read_text(encoding="utf-8")
    assert "boxed{|U_a|=3p-2}" in spine
    assert "The first-corridor companion length is `(3p-1)/2=3H+1`, not the maximal-atom length." in spine

    print(json.dumps({
        "status": "PAPER2_SURFACE_REFERENCES_GREEN",
        "surfaces_checked": len(SURFACES),
        "backticked_file_references_checked": len(references),
        "missing_references": len(missing),
        "forbidden_reference_hits": len(forbidden_hits),
        "forbidden_length_snippet_hits": len(snippet_hits),
        "authority": "publication-surface consistency audit only",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
