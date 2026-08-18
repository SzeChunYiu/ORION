"""The P1 donor readiness report measures a gap rather than closing it.

Its value is entirely in refusing to seal receipts it cannot support. A report
that emitted 36 green receipts from a matrix carrying none of the ORION-side
fields would be the exact artifact #318's hostile checks exist to detect, produced
by #318's own tooling.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "research" / "assimilation" / "p1_donor_readiness.py"
REPORT_PATH = ROOT / "research" / "assimilation" / "P1_DONOR_READINESS_V1.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("p1_donor_readiness", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_report_matches_a_live_re_derivation() -> None:
    module = _load_module()
    committed = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert committed["schema_version"] == module.SCHEMA_VERSION
    assert module.validate(committed) == []


def test_no_receipt_is_sealable_from_the_matrix_alone() -> None:
    """The matrix has no ORION side, so nothing can be sealed from it.

    If this ever passes with a non-zero count, either the matrix gained the
    ORION-side fields or something started inventing them. The second is the
    failure worth catching.
    """

    committed = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert committed["summary"]["receipt_sealable_now"] == 0
    assert all(row["receipt_sealable"] is False for row in committed["mechanisms"])
    for row in committed["mechanisms"]:
        assert row["receipt_blockers"], row["mechanism"]


def test_every_receipt_field_the_matrix_lacks_is_named() -> None:
    module = _load_module()
    committed = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    for row in committed["mechanisms"]:
        assert set(module.RECEIPT_FIELDS_NOT_IN_MATRIX) <= set(row["receipt_blockers"])


def test_unread_bodies_are_counted_against_the_adopt_dispositions() -> None:
    """The number this report exists to surface.

    An ADOPT strikes a mechanism from ORION's novelty. Doing that on a body nobody
    read is the case `MechanismAssimilationReceipt.v1` refuses to admit, so the
    count belongs in the summary rather than being recoverable only by inspection.
    """

    committed = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    summary = committed["summary"]
    assert summary["adopt_on_unread_bodies"] <= summary["adopt"]
    assert summary["abstract_only"] + summary["full_text_read"] == summary["donor_mechanisms"]
    unread_adopts = [
        row
        for row in committed["mechanisms"]
        if row["disposition"] == "ADOPT" and row["access"] == "ABSTRACT_ONLY"
    ]
    assert len(unread_adopts) == summary["adopt_on_unread_bodies"]


def test_no_donor_would_trip_the_ungrounded_source_check() -> None:
    """Every P1 donor is a primary source, so the gap is access, not provenance."""

    committed = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert {row["source_kind"] for row in committed["mechanisms"]} == {"PRIMARY_PAPER"}


def test_the_report_grants_nothing() -> None:
    committed = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert committed["grants_authority"] == "NONE"
    assert committed["closes_gate"] is None
    assert committed["issue"] == 318
