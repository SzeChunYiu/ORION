"""P1 figure generation must be deterministic and the --check mode must detect staleness.

Tests validate:
1. --check passes on the pristine tree (no-alarm case first)
2. --check fails when a PDF is mutated (validate the checker works)
3. All five required figures exist with non-zero size
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest


# Skip all tests if matplotlib is not available
matplotlib = pytest.importorskip("matplotlib")


ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "papers" / "paper-01-recursive-epistemic-reconstruction"
SCRIPT = PAPER / "scripts" / "make_figures.py"
FIGURES_DIR = PAPER / "results" / "figures"
MANIFEST = FIGURES_DIR / "manifest.json"

# The five required figures from issue #98 L124–128
REQUIRED_FIGURES = {
    "P1-2": "P1-2_main_outcome.pdf",
    "P1-3": "P1-3_selectivity_frontier.pdf",
    "P1-4": "P1-4_reopening.pdf",
    "P1-5": "P1-5_efficiency.pdf",
    "P1-6": "P1-6_recursion_stability.pdf",
}


def test_all_five_required_figures_exist_and_are_non_empty():
    """All five figures from issue #98 L124–128 must exist with content."""
    for name, filename in REQUIRED_FIGURES.items():
        path = FIGURES_DIR / filename
        assert path.exists(), f"Missing required figure: {name} ({path})"
        assert path.stat().st_size > 0, f"Figure is empty: {name} ({path})"
        # Verify it's a valid PDF by checking the PDF header
        header = path.read_bytes()[:4]
        assert header == b"%PDF", f"File is not a valid PDF: {name} ({path})"


def test_figure_check_passes_on_pristine_tree():
    """The --check mode must pass on the pristine tree (no-alarm case)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"--check failed on pristine tree: {result.stderr}"
    assert "FIGURE_CHECK: OK" in result.stderr or "FIGURE_CHECK: OK" in result.stdout


def test_figure_check_fails_on_mutated_pdf():
    """The --check mode must detect when a PDF is mutated (validate the checker)."""
    # Pick P1-2 to mutate
    pdf_path = FIGURES_DIR / REQUIRED_FIGURES["P1-2"]
    original = pdf_path.read_bytes()

    try:
        # Mutate the PDF by appending a byte
        pdf_path.write_bytes(original + b"X")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "figure hash mismatch: P1-2" in result.stderr

    finally:
        # Restore original
        pdf_path.write_bytes(original)


def test_manifest_exists_and_contains_sha256_hashes():
    """The manifest must exist with SHA256 hashes for all figures."""
    # Regenerate figures first to ensure manifest is current
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Figure generation failed: {result.stderr}"
    assert MANIFEST.exists(), f"Manifest not found: {MANIFEST}"

    import json

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # Check required keys
    assert "generated_by" in manifest
    assert "cannot_check_records_excluded" in manifest
    assert manifest["cannot_check_records_excluded"] == 0
    assert "generator_sha256" in manifest
    assert "archive_sha256" in manifest
    assert "exclusion_reason" in manifest
    assert "figures" in manifest

    # All five figures must be in the manifest
    for name, filename in REQUIRED_FIGURES.items():
        assert name in manifest["figures"], f"Missing {name} in manifest"
        entry = manifest["figures"][name]
        assert "path" in entry
        assert "sha256" in entry
        assert "size_bytes" in entry
        assert entry["size_bytes"] > 0

        # Verify the SHA256 matches the actual file
        pdf_path = FIGURES_DIR / filename
        actual_sha256 = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
        assert actual_sha256 == entry["sha256"], f"SHA256 mismatch for {name}"


def test_manifest_records_complete_live_provider_recovery():
    """The manifest must record that all former provider failures were recovered."""
    import json

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["cannot_check_records_excluded"] == 0
    assert "all cells recovered" in manifest["exclusion_reason"].lower()


def test_figure_generation_produces_valid_pdfs():
    """Running the script should produce all five figures successfully."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Figure generation failed: {result.stderr}"
    assert "Generated" in result.stdout or "Generated" in result.stderr


def _regenerate() -> dict[str, str]:
    result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, f"Figure generation failed: {result.stderr}"
    return {
        key: hashlib.sha256((FIGURES_DIR / name).read_bytes()).hexdigest()
        for key, name in REQUIRED_FIGURES.items()
    }


def test_regenerating_the_figures_twice_produces_identical_bytes():
    """The figures must be a function of their records and nothing else.

    Matplotlib stamps a wall-clock ``CreationDate`` into every PDF it writes, so
    each run of this very test used to rewrite all five figures and their
    manifest with fresh hashes. ``manifest.json`` recorded when the pipeline was
    last run, not what the figures contain, and no reader could distinguish a
    real change from a re-run because every re-run changed the hash.
    """

    first = _regenerate()
    second = _regenerate()

    assert first == second


def test_the_committed_manifest_is_the_hash_of_the_regenerated_figures():
    """A binding is only a binding if regenerating reproduces it."""

    import json

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    regenerated = _regenerate()

    for key, digest in regenerated.items():
        assert manifest["figures"][key]["sha256"] == digest, key


def test_no_figure_carries_a_wall_clock_creation_date():
    """The specific field that made the manifest track the clock."""

    for name in REQUIRED_FIGURES.values():
        assert b"/CreationDate" not in (FIGURES_DIR / name).read_bytes(), name
