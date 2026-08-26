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


def test_harness_import_does_not_eagerly_execute_incomplete_p2_runner() -> None:
    completed = _fresh_import("import orion_research_harness")

    assert completed.returncode == 0, completed.stderr


def test_direct_p2_runner_import_uses_canonical_read_decision_boundary() -> None:
    completed = _fresh_import(
        """
from typing import get_type_hints
from orion.knowledge.identity import ReadDecision
from orion.study.p2.runner import BudgetedSession
assert get_type_hints(BudgetedSession._classify_read)["return"] is ReadDecision
"""
    )

    # The 2026-08-24 ReadClassification failure remains recorded in the frozen
    # containment receipt.  After the separately validated P2 vocabulary
    # migration, requiring that historical import failure here would regress a
    # repaired production boundary rather than preserve the adverse evidence.
    assert completed.returncode == 0, completed.stderr
