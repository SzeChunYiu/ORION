from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(
    "papers/orion-12-open-world-scientific-discovery/scripts/"
    "render_offline_mechanisms_publication.py"
)


def test_publication_mechanism_layouts_match_canonical_coordinates() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert "match canonical coordinates" in completed.stdout
