"""Reproduce the merged GLM-5.2 attribution result from raw records.

The 21/24 figure is an immutable evidence seed for issue #282. Stale 24/24
prose is ignored. Architecture completion cannot rewrite these errors.
"""

from __future__ import annotations

import json
from pathlib import Path

from orion.study.p5.attribution_receipt import (
    IMMUTABLE_RESIDUAL_ERRORS,
    RESULTS_RELPATH,
    reproduce_attribution_from_records,
    write_reproduction_artifacts,
)


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / RESULTS_RELPATH
RECEIPT = ROOT / "papers/paper-05-self-orion/evidence/glm-5.2-attribution/REPRODUCTION_RECEIPT.json"
TABLE = ROOT / "papers/paper-05-self-orion/evidence/TABLE_P5_3_HIDDEN_CAUSE_ATTRIBUTION.json"


def test_raw_records_reproduce_21_of_24_and_preserve_three_errors() -> None:
    report = reproduce_attribution_from_records(RESULTS)

    assert report["model"] == "glm-5.2"
    assert report["metrics"]["total_cases"] == 24
    assert report["metrics"]["correct_attributions"] == 21
    assert report["metrics"]["incorrect_attributions"] == 3
    assert report["metrics"]["errors"] == 0
    assert report["metrics"]["accuracy"] == 0.875
    assert report["metrics"]["macro_f1"] == 0.875
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


def test_reproduction_receipt_and_table_are_content_addressed() -> None:
    artifacts = write_reproduction_artifacts(ROOT)
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    table = json.loads(TABLE.read_text(encoding="utf-8"))

    assert artifacts["receipt_sha256"] == receipt["receipt_sha256"]
    assert receipt["metrics"]["correct_attributions"] == 21
    assert receipt["metrics"]["total_cases"] == 24
    assert [error["case_id"] for error in receipt["residual_errors"]] == [
        "P5-HC-002",
        "P5-HC-012",
        "P5-HC-018",
    ]
    assert table["summary_metrics"]["correct_attributions"] == 21
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
