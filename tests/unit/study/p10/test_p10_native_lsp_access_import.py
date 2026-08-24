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


def test_native_lsp_extractor_binds_the_frozen_manifest_after_paper_refactor() -> None:
    """The runner must resolve the byte-identical manifest at its live path."""

    probe = f"""
import importlib.util
import sys
from pathlib import Path

extractor = Path({str(EXTRACTOR)!r})
sys.path.insert(0, str(extractor.parent))
spec = importlib.util.spec_from_file_location("p10_native_lsp_probe", extractor)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
print(module.MANIFEST.relative_to(Path({str(REPO_ROOT)!r})))
print(module.sha_file(module.MANIFEST))
"""
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    completed = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.splitlines() == [
        "papers/paper-xx-content-bound-math-evaluation/benchmark/"
        "MATHLIB_CORPUS_V2_MANIFEST.json",
        "373e621b918f7a686e4a1eab4f16f4f808b0d735911ca6f5dfc54dd0ac767564",
    ]
