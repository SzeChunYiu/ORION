from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_p6_p8_peer_review_ready_package() -> None:
    root = Path(__file__).resolve().parents[3]
    script = root / "papers" / "candidates" / "submission" / "check_peer_review_ready.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert "peer-review-ready structural gate: PASS" in result.stdout
