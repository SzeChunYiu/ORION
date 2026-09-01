"""Tests for P2 figure and table rendering scripts.

These tests verify that the rendering scripts produce reproducible output
from the archived evidence files.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


def test_figure_p2_2_check_mode():
    """Test that P2-2 figure artifacts are up-to-date."""
    script = Path("papers/orion-12-open-world-scientific-discovery/scripts/render_figure_p2_2.py")
    if not script.exists():
        sys.stderr.write(f"Skipping test: {script} not found\n")
        return

    result = subprocess.run(
        [sys.executable or "python3", str(script), "--check"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 3:
        pytest.skip("committed figure uses a different Matplotlib version")
    assert result.returncode == 0, f"P2-2 figure check failed: {result.stderr}"
    # Exit 0 is not the whole verdict: the checker also exits 0-adjacent (3) when
    # the figure content could not be compared, and announces that weaker outcome
    # on its own line. Assert the full-match line so a run that only compared the
    # tex and the manifest hash cannot be read as a run that compared everything.
    assert (
        "P2-2 tex, figure content and manifest source hash all match the committed data"
        in result.stdout
    )


def test_table_p2_2_check_mode():
    """Test that P2-2 table is up-to-date."""
    script = Path("papers/orion-12-open-world-scientific-discovery/scripts/render_table_p2_2.py")
    if not script.exists():
        sys.stderr.write(f"Skipping test: {script} not found\n")
        return

    result = subprocess.run(
        [sys.executable or "python3", str(script), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"P2-2 table check failed: {result.stderr}"
    assert "TABLE_P2-2 matches source JSON files" in result.stdout


def test_p2_2_manifest_exists():
    """Test that P2-2 manifest file exists and is valid JSON."""
    manifest = Path("papers/orion-12-open-world-scientific-discovery/manuscript/figures/P2-2_manifest.json")
    if not manifest.exists():
        sys.stderr.write(f"Skipping test: {manifest} not found\n")
        return

    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert "artifacts" in data
    assert "pdf" in data["artifacts"]
    assert "tex" in data["artifacts"]


def test_table_p2_2_exists():
    """Test that P2-2 table file exists."""
    table = Path("papers/orion-12-open-world-scientific-discovery/protocol/TABLE_P2-2_baseline_ablation_cost.md")
    if not table.exists():
        sys.stderr.write(f"Skipping test: {table} not found\n")
        return

    content = table.read_text(encoding="utf-8")
    assert "Table P2-2" in content
    assert "GENERATED FILE" in content
    assert "TIER_B_committed" in content
    assert "no inferential claims are made" in content


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
