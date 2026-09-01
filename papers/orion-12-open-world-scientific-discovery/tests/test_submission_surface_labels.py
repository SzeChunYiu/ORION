from __future__ import annotations

import re
import subprocess
from pathlib import Path


PAPER = Path("papers/orion-12-open-world-scientific-discovery")
FORBIDDEN = re.compile(
    rb"tier(?:_b|\\_b|-b| b)(?:_committed|\\_committed|-committed| committed)",
    re.IGNORECASE,
)


def _assert_clean(path: Path, data: bytes) -> None:
    match = FORBIDDEN.search(data)
    assert match is None, f"internal precision-tier label in submission surface {path}: {match.group()!r}"


def test_orion12_submission_surfaces_use_scientific_language() -> None:
    text_surfaces = [
        PAPER / "submission/COVER_LETTER.md",
        PAPER / "submission/SUBMISSION_MANIFEST_V1.json",
        PAPER / "manuscript/main.tex",
        PAPER / "manuscript/ipm_submission.tex",
        PAPER / "manuscript/arxiv_submission.tex",
        *sorted((PAPER / "manuscript/sections").glob("*.tex")),
        *sorted((PAPER / "manuscript/figures").glob("*.tex")),
        *sorted((PAPER / "manuscript/figures").glob("*.svg")),
    ]
    for path in text_surfaces:
        _assert_clean(path, path.read_bytes())

    pdf_surfaces = [
        PAPER / "manuscript/main.pdf",
        PAPER / "manuscript/arxiv_submission.pdf",
        PAPER / "manuscript/ipm_submission.pdf",
        PAPER / "submission/manuscript.pdf",
        PAPER / "submission/publication-final-20260901/arxiv/manuscript.pdf",
        PAPER / "submission/publication-final-20260901/journal/manuscript_anonymous.pdf",
    ]
    for path in pdf_surfaces:
        text = subprocess.check_output(["pdftotext", str(path), "-"])
        metadata = subprocess.check_output(["pdfinfo", str(path)])
        _assert_clean(path, text + metadata)
