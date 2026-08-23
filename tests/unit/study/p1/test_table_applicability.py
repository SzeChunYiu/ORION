from __future__ import annotations

import json
from hashlib import sha256
from collections import Counter
from pathlib import Path

import pytest

from orion.study.p1 import tables
from orion.study.p1.metrics import BinaryRate

ROOT = Path(__file__).resolve().parents[4]
P1_T2 = (
    ROOT
    / "papers/paper-01-recursive-epistemic-reconstruction/results/"
    "P1-T2_baseline_ablation_results.json"
)
P1_CORRECTION = P1_T2.with_name("P1-T2_STATUS_ONTOLOGY_CORRECTION_V1.json")
P1_RAW = P1_T2.parent / "raw" / "test_scored.jsonl"


def _nested_statuses(value):
    if isinstance(value, dict):
        status = value.get("status")
        if isinstance(status, str):
            yield status, value
        for child in value.values():
            yield from _nested_statuses(child)
    elif isinstance(value, list):
        for child in value:
            yield from _nested_statuses(child)


def test_zero_denominator_requires_explicit_applicability_context() -> None:
    missing = BinaryRate()

    applicable = tables._rate_block(
        missing,
        label="root_success",
        scope=tables.SCOPE_ALL,
    )
    assert applicable["status"] == tables.STATUS_CANNOT_CHECK

    inapplicable = tables._rate_block(
        missing,
        label="control_abstention",
        scope=tables.SCOPE_HIDDEN_SHIFT,
    )
    assert inapplicable["status"] == tables.STATUS_NOT_APPLICABLE
    assert "outside its frozen applicability domain" in inapplicable["reason"]


def test_positive_denominator_does_not_override_metric_applicability() -> None:
    observed = BinaryRate(successes=1, n=2)
    block = tables._rate_block(
        observed,
        label="control_abstention",
        scope=tables.SCOPE_HIDDEN_SHIFT,
    )
    assert block["status"] == tables.STATUS_NOT_APPLICABLE
    assert block["interval"] is None
    assert block["n"] == 2
    assert block["value"] == 0.5
    assert "outside its frozen applicability domain" in block["reason"]


def test_unknown_scope_or_metric_fails_closed() -> None:
    with pytest.raises(ValueError, match="unregistered P1 reporting scope"):
        tables._metric_applicable("UNKNOWN_SCOPE", "root_success")
    with pytest.raises(ValueError, match="unregistered P1 binary-rate metric"):
        tables._metric_applicable(tables.SCOPE_ALL, "invented_metric")


def test_committed_complete_table_has_no_false_cannot_check_cells() -> None:
    table = json.loads(P1_T2.read_text(encoding="utf-8"))
    statuses = list(_nested_statuses(table))
    counts = Counter(status for status, _ in statuses)

    assert table["provenance"]["integrity"]["coherent"] is True
    assert table["provenance"]["record_count"] == 2880
    assert counts[tables.STATUS_CANNOT_CHECK] == 0
    assert counts[tables.STATUS_NOT_APPLICABLE] == 288
    compared = [row for row in table["rows"] if row["difference_vs_comparator"]]
    verdicts = Counter(
        row["difference_vs_comparator"]["assessment"]["verdict"] for row in compared
    )
    assert verdicts == {
        tables.STATUS_DESCRIPTIVE_ONLY: 90,
        "NOT_SUPPORTED": 6,
        "EQUIVALENT": 3,
    }
    descriptive = [
        row["difference_vs_comparator"]
        for row in compared
        if row["system_role"] != "SUBJECT"
    ]
    assert len(descriptive) == 90
    assert all(
        block["assessment"]["verdict"] == tables.STATUS_DESCRIPTIVE_ONLY
        for block in descriptive
    )
    assert all(
        block["n"] == 0 and block.get("reason")
        for status, block in statuses
        if status == tables.STATUS_NOT_APPLICABLE
    )


def test_frozen_inapplicable_cell_decomposition_is_exact() -> None:
    table = json.loads(P1_T2.read_text(encoding="utf-8"))
    counts = Counter()
    for row in table["rows"]:
        for metric, block in row["mechanistic"].items():
            if isinstance(block, dict) and block.get("status") == tables.STATUS_NOT_APPLICABLE:
                counts[metric] += 1

    assert counts == {
        "control_abstention": 60,
        "control_correct_restraint": 60,
        "unnecessary_reframe": 60,
        "hidden_shift_success": 36,
        "reframe_target_accuracy": 36,
        "stale_closure_survival": 36,
    }


def test_descriptive_contrasts_do_not_claim_inferential_verdicts() -> None:
    table = json.loads(P1_T2.read_text(encoding="utf-8"))
    compared = [row for row in table["rows"] if row["difference_vs_comparator"]]

    descriptive = [
        row["difference_vs_comparator"]["assessment"]
        for row in compared
        if row["system_role"] != "SUBJECT"
    ]
    inferential = [
        row["difference_vs_comparator"]["assessment"]
        for row in compared
        if row["system_role"] == "SUBJECT"
    ]

    assert len(descriptive) == 90
    assert all(item["verdict"] == tables.STATUS_DESCRIPTIVE_ONLY for item in descriptive)
    assert all(item["rationale"].startswith("NO_REGISTERED_HYPOTHESIS") for item in descriptive)
    assert all(item["hypothesis_id"].startswith("descriptive:") for item in descriptive)
    assert all(item["hypothesis_id"].startswith("P1.") for item in inferential)
    assert all(item["verdict"] != tables.STATUS_DESCRIPTIVE_ONLY for item in inferential)


def test_status_correction_receipt_binds_bytes_and_forbids_promotion() -> None:
    receipt = json.loads(P1_CORRECTION.read_text(encoding="utf-8"))

    assert sha256(P1_T2.read_bytes()).hexdigest() == receipt["after"]["sha256"]
    assert sha256(P1_RAW.read_bytes()).hexdigest() == receipt["raw_archive"]["sha256"]
    assert receipt["before"]["sha256"] == (
        "28945162ede36e85f8f662dbef59d51d0623b5317c696db068c5303aed768b4a"
    )
    assert receipt["scientific_invariants"] == {
        "raw_records_changed": False,
        "numerators_changed": False,
        "denominators_changed": False,
        "confidence_intervals_changed": False,
        "paired_effects_changed": False,
        "registered_p1_hypothesis_verdicts_changed": False,
        "historical_p1_h1_terminal": "NOT_SUPPORTED",
        "scientific_promotion_authorized": False,
    }
