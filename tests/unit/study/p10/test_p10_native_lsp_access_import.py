from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
EXTRACTOR = (
    REPO_ROOT
    / "research"
    / "extensions"
    / "p9-p10-structural-scaling"
    / "extract_p10_native_lsp_state_v1.py"
)


def test_native_lsp_extractor_imports_in_the_clean_runner_environment() -> None:
    """The sharded workflow must reach argument parsing without ambient paths."""

    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    completed = subprocess.run(
        [sys.executable, str(EXTRACTOR), "--help"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "--mathlib-checkout" in completed.stdout
