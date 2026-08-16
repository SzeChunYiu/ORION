from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from orion.kernel.apply import grade_and_apply
from orion.kernel.driver import replay_cells
from orion.kernel.gate import grade_answer
from orion.kernel.round import run_round


@pytest.mark.parametrize(
    ("target", "forbidden"),
    (
        (grade_answer, {"assurance_service", "registry", "signing_key", "evaluate"}),
        (grade_and_apply, {"assurance_service", "registry", "signing_key", "evaluate"}),
        (run_round, {"assurance_service", "registry", "signing_key", "evaluate"}),
        (replay_cells, {"assurance_service", "registry", "signing_key", "evaluate"}),
    ),
)
def test_candidate_facing_interfaces_accept_no_authority_material(
    target: object, forbidden: set[str]
) -> None:
    """Untrusted callers can submit proposals, never roots, keys or evaluators."""

    assert forbidden.isdisjoint(inspect.signature(target).parameters)


def test_candidate_facing_modules_do_not_import_protected_host_runtime() -> None:
    """Keep appraisal/authorization code on the host side of the trust boundary."""

    kernel_root = Path(__file__).parents[3] / "src" / "orion" / "kernel"
    candidate_modules = ("gate.py", "apply.py", "round.py", "driver.py")
    forbidden_modules = {
        "orion.kernel.assurance",
        "orion.kernel.authorization",
        "orion.kernel.authority_state",
        "orion.kernel.host",
    }

    for module_name in candidate_modules:
        tree = ast.parse((kernel_root / module_name).read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        assert forbidden_modules.isdisjoint(imported), module_name
