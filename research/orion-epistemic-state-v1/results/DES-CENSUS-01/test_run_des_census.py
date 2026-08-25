"""Non-authorizing mechanical checks for the frozen DES-CENSUS-01 executor."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("des_census", HERE / "run_des_census.py")
assert SPEC and SPEC.loader
des_census = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(des_census)


def test_cannot_check_is_typed_and_unknown_label_is_retained() -> None:
    cannot = des_census.assign_coordinates(
        "CANNOT_CHECK", "unresolved route obligation"
    )
    unknown = des_census.assign_coordinates(
        "ZEBRA_QUARTZ_TERMINAL", "opaque legacy terminal"
    )
    assert {"C", "R"}.issubset(cannot)
    assert unknown == ()


def test_detector_retains_composites_statuses_dependencies_and_transitions() -> None:
    text = (
        "terminal = FOO_BAR\n"
        "status = CANNOT_CHECK because provider missing\n"
        "depends_on: receipt.json\n"
        "OPEN_STATE -> CLOSED_STATE\n"
    )
    rows = des_census.detect_text_occurrences(
        path="fixture.md", blob_oid="a" * 40, text=text
    )
    values = {row["raw_value"] for row in rows}
    families = {family for row in rows for family in row["families"]}
    assert {"FOO_BAR", "CANNOT_CHECK", "OPEN_STATE", "CLOSED_STATE"} <= values
    assert {
        "terminal",
        "status",
        "composite_label",
        "cannot_check_reason",
        "dependency",
        "transition",
    } <= families


def test_reconciliation_rejects_a_dropped_occurrence() -> None:
    denominators = {
        "tracked_entries": 1,
        "file_rows": 1,
        "occurrences": 2,
        "classified_occurrences": 1,
        "unclassified_occurrences": 1,
    }
    des_census.require_reconciliation(denominators)
    with pytest.raises(ValueError, match="occurrence classification denominator"):
        des_census.require_reconciliation({**denominators, "unclassified_occurrences": 0})


def test_raw_occurrence_encoding_round_trips_without_dropping_adverse_rows() -> None:
    rows = des_census.detect_text_occurrences(
        path="fixture.md",
        blob_oid="b" * 40,
        text="status = CANNOT_CHECK\nterminal = OPAQUE_ZEBRA\n",
    )
    encoded = des_census.encode_occurrence_rows(
        rows,
        [{"path": "fixture.md", "oid": "b" * 40}],
    )
    decoded = des_census.decode_occurrence_rows(encoded)
    assert decoded == rows
    assert any(row["raw_value"] == "CANNOT_CHECK" for row in decoded)
    assert any(row["classification"] == "UNCLASSIFIED" for row in decoded)
