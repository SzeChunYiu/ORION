"""Mutation tests for the ORION-01–25 science-gap register V2."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "papers/publication_closure/TOP_TIER_SCIENCE_GAP_REGISTER_V2.md"
CHECKER = ROOT / "papers/publication_closure/audit_top_tier_science_gap_register_v2.py"


def _load():
    spec = importlib.util.spec_from_file_location("gap_register_v2", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = _load()


def test_committed_register_passes() -> None:
    report = checker.audit_path(REGISTER)
    assert report["status"] == "PASS", report["errors"]
    assert report["paper_count"] == 25
    assert report["scientific_authority_delta"] == "NONE"


def test_missing_paper_turns_audit_red() -> None:
    text = REGISTER.read_text(encoding="utf-8")
    mutant = "\n".join(line for line in text.splitlines() if not line.startswith("| ORION-25 |"))
    report = checker.audit_text(mutant)
    assert report["status"] == "FAIL"
    assert any("ORION-01 through ORION-25" in error for error in report["errors"])


def test_unearned_promotion_in_a_row_turns_audit_red() -> None:
    text = REGISTER.read_text(encoding="utf-8")
    mutant = text.replace(
        "Stop: `NEW_SUCCESSOR_QUESTION_REQUIRED__NO_RESCUE`.",
        "Stop: `TOP_TIER_PROMOTION_EARNED`.",
        1,
    )
    report = checker.audit_text(mutant)
    assert report["status"] == "FAIL"
    assert any("unearned top-tier authority" in error for error in report["errors"])


def test_external_authority_softening_turns_audit_red() -> None:
    text = REGISTER.read_text(encoding="utf-8")
    mutant = text.replace(
        "| ORION-18 | `EXTERNAL_AUTHORITY_BLOCKED` | `EXTERNAL_AUTHORITY_REQUIRED` |",
        "| ORION-18 | `READY_TO_FILE` | `UNRUN_OPTIONAL` |",
    )
    report = checker.audit_text(mutant)
    assert report["status"] == "FAIL"
    assert any("external" in error and "softened" in error for error in report["errors"])


def test_short_assessment_sha_turns_audit_red() -> None:
    text = REGISTER.read_text(encoding="utf-8")
    mutant = text.replace(
        "87e2bcb330d243b7062ddba1ca26e426632edeab",
        "87e2bcb",
        1,
    )
    report = checker.audit_text(mutant)
    assert report["status"] == "FAIL"
    assert any("assessment cut drifted" in error for error in report["errors"])
