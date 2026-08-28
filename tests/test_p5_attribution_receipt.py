"""Reproduce the merged GLM-5.2 attribution result from raw records.

The 21/24 figure is an immutable evidence seed for issue #282. Stale 24/24
prose is ignored. Architecture completion cannot rewrite these errors.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from orion.study.p5.attribution_receipt import (
    IMMUTABLE_RESIDUAL_ERRORS,
    RESULTS_RELPATH,
    compute_metrics,
    reproduce_attribution_from_records,
    write_reproduction_artifacts,
)


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / RESULTS_RELPATH
REPORT = ROOT / "papers/orion-15-self-orion/evidence/glm-5.2-attribution/report.json"
RECEIPT = ROOT / "papers/orion-15-self-orion/evidence/glm-5.2-attribution/REPRODUCTION_RECEIPT.json"
TABLE = ROOT / "papers/orion-15-self-orion/evidence/TABLE_P5_3_HIDDEN_CAUSE_ATTRIBUTION.json"
# Hash of the historical report as written, BEFORE the ORION-01..25 namespace
# unification (commit 3a1a83178, PR #1474). Retained as the content anchor.
HISTORICAL_REPORT_SHA256 = "13ac651d00513b737023c309eab3ed3bde7adcc5f9612d146705d1d4a0877eca"

# Hash after that migration. The `git mv` wave (2bab2148f) left the bytes at
# HISTORICAL_REPORT_SHA256; the follow-on rebind step in 3a1a83178 rewrote path
# strings INSIDE this record, which changed its hash without changing any
# measurement. The rebind was part of a receipted migration -- that commit
# updated the sibling supersession tests -- but this byte-exactness guard was
# missed, leaving `ci` red on main.
REBOUND_REPORT_SHA256 = "676c1d78e9570f450b1b734ce17990131f3eb6ea5c94afb8ae7baa113c980abe"

# The exact, and only, sanctioned edit: the paper's namespace prefix. Both old
# and new prefixes are 8 characters, so the file length is unchanged and the
# rewrite is detectable by hash alone.
NAMESPACE_REBIND = (b"papers/orion-15-self-orion/", b"papers/paper-05-self-orion/")
EXPECTED_REBIND_OCCURRENCES = 2


def test_raw_records_reproduce_21_of_24_and_preserve_three_errors() -> None:
    report = reproduce_attribution_from_records(RESULTS)

    assert report["model"] == "glm-5.2"
    assert report["metrics"]["total_cases"] == 24
    assert report["metrics"]["correct_attributions"] == 21
    assert report["metrics"]["incorrect_attributions"] == 3
    assert report["metrics"]["errors"] == 0
    assert report["metrics"]["accuracy"] == 0.875
    assert report["metrics"]["macro_precision"] == pytest.approx(0.8958333333333333)
    assert report["metrics"]["macro_recall"] == 0.875
    assert report["metrics"]["macro_f1"] == pytest.approx(0.8726190476190476)
    assert report["metrics"]["false_method_change_rate"] == 3 / 21
    assert report["metrics"]["confidence_distribution"] == {"HIGH": 15, "MEDIUM": 9}
    assert report["residual_errors"] == list(IMMUTABLE_RESIDUAL_ERRORS)
    assert report["residual_errors"] == [
        {
            "case_id": "P5-HC-002",
            "gold": "RETRIEVAL_MISS",
            "attributed": "REPRESENTATION_GAP",
        },
        {
            "case_id": "P5-HC-012",
            "gold": "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE",
            "attributed": "IMPLEMENTATION_BUG",
        },
        {
            "case_id": "P5-HC-018",
            "gold": "REPRESENTATION_GAP",
            "attributed": "METHOD_BASIS_GAP",
        },
    ]
    assert report["receipt_sha256"]
    assert len(report["receipt_sha256"]) == 64
    assert report["records_sha256"]
    assert len(report["records_sha256"]) == 64
    assert report["empirical_authority"] == "ATTRIBUTION_DIAGNOSIS_ONLY"
    assert report["promotion_terminal"] is None
    assert report["self_merge_authority"] is False


def test_historical_buggy_report_is_preserved_byte_exact() -> None:
    """The correction supersedes the historical aggregate; it never rewrites it.

    The guard is expressed against the migration rather than re-baselined onto
    it. Bumping the expected hash alone would silently permit any future edit to
    this record. Instead the test pins BOTH ends: the record must hash to the
    post-migration value, AND undoing the one sanctioned namespace rebind must
    reproduce the original historical bytes exactly. Any edit that is not purely
    that rebind therefore still fails.
    """

    raw = REPORT.read_bytes()

    # 1. current bytes are exactly the post-migration record
    assert hashlib.sha256(raw).hexdigest() == REBOUND_REPORT_SHA256

    # 2. the ONLY delta from the historical record is the receipted rebind
    new_prefix, old_prefix = NAMESPACE_REBIND
    assert raw.count(new_prefix) == EXPECTED_REBIND_OCCURRENCES
    restored = raw.replace(new_prefix, old_prefix)
    assert hashlib.sha256(restored).hexdigest() == HISTORICAL_REPORT_SHA256
    assert len(restored) == len(raw)

    # 3. no measurement moved
    historical = json.loads(REPORT.read_text(encoding="utf-8"))
    assert historical["metrics"]["accuracy"] == 0.875
    assert historical["metrics"]["macro_f1"] == 0.875
    assert historical["metrics"]["total_cases"] == 24
    assert historical["metrics"]["correct_attributions"] == 21
    assert historical["metrics"]["incorrect_attributions"] == 3


def test_false_positive_changes_f1_even_when_recall_stays_perfect() -> None:
    """Hostile control for the exact D1 bug: F1 must not alias recall."""

    records = [
        {
            "case_id": "A1",
            "gold_root_cause": "IMPLEMENTATION_BUG",
            "attributed_root_cause": "IMPLEMENTATION_BUG",
            "confidence": "HIGH",
            "intervention_prediction": "YES",
            "error": None,
        },
        {
            "case_id": "B1",
            "gold_root_cause": "RETRIEVAL_MISS",
            "attributed_root_cause": "IMPLEMENTATION_BUG",
            "confidence": "HIGH",
            "intervention_prediction": "YES",
            "error": None,
        },
        {
            "case_id": "B2",
            "gold_root_cause": "RETRIEVAL_MISS",
            "attributed_root_cause": "RETRIEVAL_MISS",
            "confidence": "HIGH",
            "intervention_prediction": "YES",
            "error": None,
        },
    ]
    metrics = compute_metrics(records)
    implementation = metrics["per_family_metrics"]["IMPLEMENTATION_BUG"]

    assert implementation["tp"] == 1
    assert implementation["fp"] == 1
    assert implementation["fn"] == 0
    assert implementation["precision"] == 0.5
    assert implementation["recall"] == 1.0
    assert implementation["f1"] == pytest.approx(2 / 3)
    assert implementation["f1"] < implementation["recall"]


def test_reproduction_receipt_and_table_are_content_addressed(tmp_path: Path) -> None:
    """Reproduction tests must never rewrite tracked, content-bound evidence."""

    tracked_receipt_sha = hashlib.sha256(RECEIPT.read_bytes()).hexdigest()
    tracked_table_sha = hashlib.sha256(TABLE.read_bytes()).hexdigest()

    # Build a minimal temporary repository-shaped subject. The production helper
    # may still write to its supplied repo_root for intentional regeneration,
    # but pytest must never supply the real repository root as that destination.
    temp_results = tmp_path / RESULTS_RELPATH
    temp_results.parent.mkdir(parents=True, exist_ok=True)
    temp_results.write_bytes(RESULTS.read_bytes())

    artifacts = write_reproduction_artifacts(tmp_path)
    temp_receipt = tmp_path / "papers/orion-15-self-orion/evidence/glm-5.2-attribution/REPRODUCTION_RECEIPT.json"
    temp_table = tmp_path / "papers/orion-15-self-orion/evidence/TABLE_P5_3_HIDDEN_CAUSE_ATTRIBUTION.json"
    receipt = json.loads(temp_receipt.read_text(encoding="utf-8"))
    table = json.loads(temp_table.read_text(encoding="utf-8"))

    assert artifacts["receipt_sha256"] == receipt["receipt_sha256"]
    assert receipt["metrics"]["correct_attributions"] == 21
    assert receipt["metrics"]["total_cases"] == 24
    assert receipt["metrics"]["macro_f1"] == pytest.approx(0.8726190476190476)
    assert [error["case_id"] for error in receipt["residual_errors"]] == [
        "P5-HC-002",
        "P5-HC-012",
        "P5-HC-018",
    ]
    assert table["summary_metrics"]["correct_attributions"] == 21
    assert table["summary_metrics"]["macro_precision"] == pytest.approx(0.8958333333333333)
    assert table["summary_metrics"]["macro_recall"] == 0.875
    assert table["summary_metrics"]["macro_f1"] == pytest.approx(0.8726190476190476)
    assert table["per_family_metrics"]["IMPLEMENTATION_BUG"] == {
        "precision": 0.75,
        "recall": 1.0,
        "f1": pytest.approx(6 / 7),
        "tp": 3,
        "fp": 1,
        "fn": 0,
        "cases": ["P5-HC-007", "P5-HC-008", "P5-HC-009"],
        "correct": 3,
        "total": 3,
    }
    assert table["per_family_metrics"]["RETRIEVAL_MISS"]["precision"] == 1.0
    assert table["per_family_metrics"]["RETRIEVAL_MISS"]["recall"] == pytest.approx(2 / 3)
    assert table["per_family_metrics"]["RETRIEVAL_MISS"]["f1"] == pytest.approx(0.8)
    assert table["incorrect_cases"][0]["case_id"] == "P5-HC-002"
    assert table["incorrect_cases"][1]["case_id"] == "P5-HC-012"
    assert table["incorrect_cases"][2]["case_id"] == "P5-HC-018"
    assert table["intervention_predictions"] == {
        "YES": 19,
        "NO": 4,
        "CANNOT_DETERMINE": 1,
    }
    assert table["empirical_authority"] == "ATTRIBUTION_DIAGNOSIS_ONLY"
    assert "TRANSFER" not in table["empirical_authority"]

    # Hostile side-effect check for #1510: the test itself must leave the
    # committed receipt/table byte-identical.
    assert hashlib.sha256(RECEIPT.read_bytes()).hexdigest() == tracked_receipt_sha
    assert hashlib.sha256(TABLE.read_bytes()).hexdigest() == tracked_table_sha
