from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(
    "papers/orion-12-open-world-scientific-discovery/scripts/render_offline_mechanisms.py"
)


def test_offline_mechanism_figures_match_frozen_snapshot() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert "match the frozen mechanism projection" in completed.stdout
