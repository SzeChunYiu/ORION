from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "research/paper-programme-v1/audit_resolution_ledger.py"
LEDGER = ROOT / "research/paper-programme-v1/P1_P15_RECURSIVE_RESOLUTION_LEDGER_2026-08-23.json"


def _module():
    spec = importlib.util.spec_from_file_location("audit_resolution_ledger", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_git_audit_derives_repository_root_from_its_own_location() -> None:
    module = _module()
    assert module.REPO == ROOT
    assert module.REPO.is_dir()


def test_relative_ledger_path_resolves_from_repository_root() -> None:
    module = _module()
    relative = LEDGER.relative_to(ROOT)
    assert module._ledger_path(relative) == LEDGER
    assert module._ledger_path(LEDGER) == LEDGER
