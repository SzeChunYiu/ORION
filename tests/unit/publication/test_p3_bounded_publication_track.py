from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_p3_bounded_publication_track_guard() -> None:
    root = Path(__file__).resolve().parents[3]
    checker = (
        root
        / "papers"
        / "orion-13-global-knowledge-portrait"
        / "scripts"
        / "check_bounded_publication_track.py"
    )
    completed = subprocess.run(
        [sys.executable, str(checker)],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "P3_BOUNDED_PUBLICATION_TRACK: PASS" in completed.stdout
