from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(
    "papers/orion-12-open-world-scientific-discovery/scripts/render_route_stop_oracle.py"
)


def test_route_stop_publication_table_matches_frozen_projection() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert "matches the frozen O1 projection" in completed.stdout
