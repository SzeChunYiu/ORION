from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SATURATION = ROOT / "research" / "revival" / "p1" / "P1_NEAREST_WORK_SATURATION_ROUNDS_D_E_V1.json"


def test_two_consecutive_no_material_change_rounds_are_explicit_and_bounded() -> None:
    payload = json.loads(SATURATION.read_text())
    assert payload["two_consecutive_no_material_change_rounds"] is True
    rounds = payload["rounds"]
    assert [item["round_id"] for item in rounds] == ["D", "E"]
    assert all(item["material_design_change"] is False for item in rounds)
    assert all(item["material_novelty_change"] is False for item in rounds)
    assert all(item["candidates"] for item in rounds)
    assert payload["bounded_literature_terminal"] == "P1_NEAREST_WORK_BOUNDED_AT_2026_08_17"
    assert "science-specific causal-evidence admission policy" in payload["surviving_candidate_residual"]
    assert "not the P1_BOUNDED_SATURATION terminal" in payload["claim_boundary"]


def test_saturation_receipt_retains_reopen_triggers() -> None:
    payload = json.loads(SATURATION.read_text())
    triggers = payload["reopen_triggers"]
    assert len(triggers) >= 4
    assert any("before submission" in item for item in triggers)
    assert any("#287" in item for item in triggers)
    assert any("R3 result" in item for item in triggers)
