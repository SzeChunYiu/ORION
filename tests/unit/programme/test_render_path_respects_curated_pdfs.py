"""A paper whose committed PDF is asserted by a test must not be rendered blindly.

ORION-05's committed PDF is a curated, de-identified artifact: its title and
author deliberately differ from ``manuscript/main.tex``, and
``test_orion05_wave1_manuscript_surface.py`` pins three properties of it --
byte-identity with the package copy, absence of the project name, and presence
of specific claim carriers. Rendering that paper from source violates all three,
because the source is not what produced the PDF.

That divergence looks exactly like a stale artifact from the outside, and was
treated as one: ORION-05 was added to the submission-set render workflow, the
PDF was rebuilt, and main went red. The revert is #1918.

This test makes the precondition mechanical. A paper may appear in a render
workflow only if either no test asserts on its committed PDF, or it is recorded
below as having been checked against those assertions.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
TESTS = REPO_ROOT / "tests"
PAPERS = REPO_ROOT / "papers"

# Papers with a PDF-asserting test that have been read and confirmed compatible
# with being rendered from source. Adding a name here is a claim that someone
# opened the test and checked what it pins -- not a way to silence this.
RENDER_COMPATIBLE = {
    # The unified publication test names ORION-01--03 while inspecting their
    # current package archives, not a hand-curated working PDF. Their working
    # PDFs are already rebuilt and byte-compared by the clipping workflow.
    "orion-01-certificate-realization",
    "orion-02-fiberguard-finite-fibre",
    "orion-03-typed-merge-falsification",
    "orion-11-recursive-epistemic-reconstruction",
    "orion-12-open-world-scientific-discovery",
    # The publication regression module names ORION-14 while checking that its
    # clean-CI render provenance remains attached to the batch that produced
    # it.  The committed PDF is that canonical render, not a curated divergent
    # artifact, and the clipping workflow already rebuilds and byte-checks it.
    "orion-14-verified-scientific-discovery",
    # The render-reconciliation regression test intentionally exercises this
    # working PDF's checksum binding; the clean-CI PDF is its canonical render.
    "orion-23-responsibility-carrying-state",
}

# Papers whose committed PDF is curated and must never be rendered from source.
CURATED_PDF = {
    "orion-05-tare-expressivity",
}


def _paper_dirs() -> list[str]:
    return sorted(p.name for p in PAPERS.glob("orion-*") if p.is_dir())


def _papers_asserted_by_tests() -> set[str]:
    """Papers named by a test file that also reads a committed PDF."""
    asserted: set[str] = set()
    names = _paper_dirs()
    for test_file in TESTS.rglob("*.py"):
        try:
            text = test_file.read_text(errors="replace")
        except OSError:
            continue
        if "main.pdf" not in text and "manuscript.pdf" not in text:
            continue
        for name in names:
            if name in text:
                asserted.add(name)
    return asserted


def _papers_in_render_workflows() -> set[str]:
    rendered: set[str] = set()
    names = _paper_dirs()
    for wf in WORKFLOWS.glob("*.yml"):
        try:
            text = wf.read_text(errors="replace")
        except OSError:
            continue
        if "latexmk" not in text:
            continue
        # A workflow may exclude a paper from its render path explicitly. The
        # marker is read here so the workflow and CURATED_PDF cannot silently
        # disagree: excluding a paper there is what keeps it out of this set.
        excluded = set(re.findall(r"#\s*CURATED_EXCLUDE:\s*(\S+)", text))
        for name in names:
            if name in excluded:
                continue
            if name in text:
                rendered.add(name)
                continue
            # workflows address papers by glob, e.g. papers/orion-07-*
            stem = re.match(r"(orion-\d+)-", name)
            if stem and f"papers/{stem.group(1)}-*" in text:
                rendered.add(name)
                continue
            # ...or by a wildcard covering every paper, e.g. papers/orion-??-*.
            # Missing these is how a curated PDF ended up inside a render path
            # without this guard noticing.
            if re.search(r"papers/orion-[?*]+-?\*", text):
                rendered.add(name)
    return rendered


def test_curated_pdfs_are_never_in_a_render_path() -> None:
    """The specific regression: a curated PDF must not be rebuilt from source."""
    rendered = _papers_in_render_workflows()
    violations = sorted(CURATED_PDF & rendered)
    assert not violations, (
        f"these papers have a curated committed PDF but appear in a render "
        f"workflow: {violations}. Their source did not produce that PDF, so "
        f"rendering replaces a deliberate artifact with a different document. "
        f"See #1918."
    )


def test_pdf_asserting_papers_in_render_paths_were_checked() -> None:
    """Any paper both rendered and PDF-asserted must be explicitly accounted for."""
    rendered = _papers_in_render_workflows()
    asserted = _papers_asserted_by_tests()
    unaccounted = sorted((rendered & asserted) - RENDER_COMPATIBLE - CURATED_PDF)
    assert not unaccounted, (
        f"these papers are in a render workflow and have a test asserting on "
        f"their committed PDF, but are recorded in neither RENDER_COMPATIBLE "
        f"nor CURATED_PDF: {unaccounted}. Read the asserting test and decide "
        f"which it is before rendering; a curated PDF and a stale one are "
        f"indistinguishable from the outside."
    )


def test_the_detector_actually_finds_known_cases() -> None:
    """Control: if these lookups return nothing, the guards above pass vacuously."""
    assert _paper_dirs(), "no paper directories found; the scan is broken"
    asserted = _papers_asserted_by_tests()
    assert "orion-05-tare-expressivity" in asserted, (
        "ORION-05 has a test asserting on its committed PDF and must be "
        "detected; if this fails the detector is broken, not the tree"
    )
    rendered = _papers_in_render_workflows()
    assert rendered, "no papers detected in any render workflow; the scan is broken"
