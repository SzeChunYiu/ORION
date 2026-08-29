"""Hostile regressions for the ORION 01-25 top-tier science-closure gate."""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[3]
DOC = ROOT / "papers/reviewer_gate/orion_top_tier_closure_v1"
CHECKER = ROOT / "scripts/check_orion_top_tier_closure_v1.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("orion_top_tier_checker", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = _load()


def _copy(tmp_path: Path) -> Path:
    target = tmp_path / "gate"
    shutil.copytree(DOC, target)
    return target


def _replace(root: Path, name: str, old: str, new: str) -> None:
    path = root / name
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_canonical_gate_is_green() -> None:
    assert MODULE.validate(DOC) == []


def test_missing_paper_is_red(tmp_path: Path) -> None:
    root = _copy(tmp_path)
    _replace(root, "ORION_24_25.md", "## ORION-25", "## REMOVED-25")
    assert any("paper coverage mismatch" in e for e in MODULE.validate(root))


def test_hard_retraction_cannot_promote(tmp_path: Path) -> None:
    root = _copy(tmp_path)
    _replace(root, "ORION_01_03.md", "- `BASELINE_PROMOTION_ALLOWED`: false", "- `BASELINE_PROMOTION_ALLOWED`: true")
    assert any("hard retraction cannot promote" in e for e in MODULE.validate(root))


def test_open_pr_cannot_gain_credit(tmp_path: Path) -> None:
    root = _copy(tmp_path)
    _replace(root, "README.md", "`counts_as_evidence=false`", "`counts_as_evidence=true`")
    assert any("open PR lacks zero-credit marker" in e for e in MODULE.validate(root))


def test_external_replication_cannot_be_precredited(tmp_path: Path) -> None:
    root = _copy(tmp_path)
    _replace(root, "ORION_06_08.md", "- `EXTERNAL_STATUS`: required_not_yet_credited", "- `EXTERNAL_STATUS`: credited")
    assert any("external evidence must remain uncredited" in e for e in MODULE.validate(root))


def test_three_primary_endpoints_are_required(tmp_path: Path) -> None:
    root = _copy(tmp_path)
    path = root / "ORION_09_10.md"
    text = path.read_text(encoding="utf-8")
    line = next(line for line in text.splitlines() if line.startswith("- `PRIMARY_ENDPOINTS`:"))
    shortened = line.rsplit(" || ", 1)[0]
    path.write_text(text.replace(line, shortened, 1), encoding="utf-8")
    assert any("needs at least three primary endpoints" in e for e in MODULE.validate(root))


def test_stale_baseline_is_red(tmp_path: Path) -> None:
    root = _copy(tmp_path)
    _replace(root, "README.md", MODULE.BASELINE, "0" * 40)
    assert any("baseline commit mismatch" in e for e in MODULE.validate(root))


def test_manuscript_cannot_unlock_before_evidence(tmp_path: Path) -> None:
    root = _copy(tmp_path)
    _replace(root, "ORION_21_23.md", "- `MANUSCRIPT_UNLOCK`: Only after", "- `MANUSCRIPT_UNLOCK`: Immediately after")
    assert any("manuscript unlock must begin Only after" in e for e in MODULE.validate(root))
