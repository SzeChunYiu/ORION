from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MATRIX = ROOT / "research" / "paper-programme-v1" / "P1_P15_ACTIVE_BLOCKER_MATRIX_2026-08-22.json"


def test_matrix_covers_every_paper_once_and_forbids_string_scan_authority():
    payload = json.loads(MATRIX.read_text(encoding="utf-8"))
    rows = payload["papers"]
    assert [row["paper_id"] for row in rows] == [f"P{index}" for index in range(1, 16)]
    assert len({row["paper_id"] for row in rows}) == 15
    assert payload["raw_string_count_is_authoritative"] is False
    assert "zero unresolved ACTIVE claim-authority blockers" in payload["acceptance_criterion"]


def test_every_paper_has_an_explicit_next_campaign_or_audit():
    payload = json.loads(MATRIX.read_text(encoding="utf-8"))
    for row in payload["papers"]:
        assert row["state"]
        assert isinstance(row["historical_adverse"], list)
        assert isinstance(row["active_blockers"], list)
        assert row["repair_or_campaign"], row["paper_id"]


def test_known_scanner_traps_are_encoded():
    payload = json.loads(MATRIX.read_text(encoding="utf-8"))
    by_paper = {row["paper_id"]: row for row in payload["papers"]}
    assert "not_adverse" in by_paper["P2"]
    assert any("LABEL_RECOVERED_BY_CUE" in item for item in by_paper["P4"]["active_blockers"])
    assert "PROJECTION_CONTAMINATION" in by_paper["P13"]["state"]
    assert "DEFECTIVE_GATE" in by_paper["P14"]["state"]

