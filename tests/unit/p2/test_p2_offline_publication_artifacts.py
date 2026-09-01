"""Publication-layer drift checks for completed P2 offline artifacts."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RENDER = ROOT / "papers" / "orion-12-open-world-scientific-discovery" / "scripts" / "render_offline_results.py"
REGENERATE = ROOT / "papers" / "orion-12-open-world-scientific-discovery" / "scripts" / "run_offline_companion.py"


def test_offline_failure_table_and_figure_are_generated_from_result_summary() -> None:
    proc = subprocess.run(
        [sys.executable, str(RENDER), "--check"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_publication_regeneration_command_matches_frozen_archive() -> None:
    proc = subprocess.run(
        [sys.executable, str(REGENERATE), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
