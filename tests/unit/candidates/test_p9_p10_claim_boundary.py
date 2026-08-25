from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "papers" / "candidates" / "checkers" / "check_p9_p10_claim_boundary.py"


@pytest.fixture
def checker():
    spec = importlib.util.spec_from_file_location("p9_p10_boundary", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_existing_p1_p8_manuscripts_are_clean(checker) -> None:
    assert checker.violations(list(checker.DEFAULT_PATHS)) == []


def test_future_bounded_bridge_is_not_an_overclaim(checker, tmp_path: Path) -> None:
    manuscript = tmp_path / "bounded.md"
    manuscript.write_text(
        "P9 structural learning and P10 method invention remain CANNOT_CHECK; "
        "future work will evaluate them prospectively.\n",
        encoding="utf-8",
    )
    assert checker.violations([manuscript]) == []


def test_explicit_not_evidence_boundary_is_not_an_overclaim(checker, tmp_path: Path) -> None:
    manuscript = tmp_path / "bounded.md"
    manuscript.write_text(
        "This is a representation result, not evidence that the representation "
        "is sufficient for neural structural learning.\n",
        encoding="utf-8",
    )
    assert checker.violations([manuscript]) == []


def test_empirical_p9_result_is_rejected(checker, tmp_path: Path) -> None:
    manuscript = tmp_path / "overclaim.md"
    manuscript.write_text(
        "Our P9 structural-learning model achieved superior benchmark performance.\n",
        encoding="utf-8",
    )
    findings = checker.violations([manuscript])
    assert len(findings) == 1
    assert findings[0].startswith("P9_P10_OVERCLAIM:")


def test_p10_invention_result_is_rejected(checker, tmp_path: Path) -> None:
    manuscript = tmp_path / "invention.md"
    manuscript.write_text(
        "Our P10 system discovered and generated an invented method.\n",
        encoding="utf-8",
    )
    assert checker.violations([manuscript])
