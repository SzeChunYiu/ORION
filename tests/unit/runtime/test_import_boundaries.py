from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PYTHONPATH = os.pathsep.join(
    (
        str(ROOT / "packages" / "orion-research-harness" / "src"),
        str(ROOT / "src"),
    )
)


def _fresh_import(code: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = PYTHONPATH
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_kernel_then_public_runtime_imports_preserve_export_identities() -> None:
    completed = _fresh_import(
        """
from orion.runtime.runtime import OrionRuntime as DirectKernel
from orion.runtime.runtime import RuntimeResult as DirectResult
from orion.runtime import KernelOrionRuntime, OrionRuntime, RuntimeResult
from orion.runtime.paper_runtime import OrionRuntime as PaperRuntime
assert KernelOrionRuntime is DirectKernel
assert OrionRuntime is PaperRuntime
assert RuntimeResult is DirectResult
"""
    )

    assert completed.returncode == 0, completed.stderr


def test_navigation_first_constructs_default_completion_program() -> None:
    completed = _fresh_import(
        """
from orion.engine.navigation import PaperParityNavigator
navigator = PaperParityNavigator.normal()
assert navigator.donor_registry.registry_id == "orion:donors:normal:v2"
assert navigator._cells
"""
    )

    assert completed.returncode == 0, completed.stderr


def test_public_runtime_then_top_level_orion_imports_in_fresh_interpreter() -> None:
    completed = _fresh_import(
        """
from orion.runtime import OrionRuntime
from orion.runtime.paper_runtime import OrionRuntime as PaperRuntime
assert OrionRuntime is PaperRuntime
import orion
"""
    )

    assert completed.returncode == 0, completed.stderr


def test_harness_import_no_longer_reenters_partial_navigation() -> None:
    completed = _fresh_import("import orion_research_harness")

    assert "partially initialized module 'orion.engine.navigation'" not in completed.stderr
    if completed.returncode != 0:
        assert "ReadClassification" in completed.stderr
