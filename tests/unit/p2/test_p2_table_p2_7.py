from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(
    "papers/paper-02-open-world-scientific-discovery/scripts/render_table_p2_7.py"
)


def test_table_p2_7_matches_source_probe_json_files() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert "matches source probe JSON files" in completed.stdout
