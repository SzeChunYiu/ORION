from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CLOSURE = ROOT / "research" / "assimilation" / "STRUCTURAL_ASSIMILATION_CLOSURE_V1.json"


def _payload() -> dict:
    return json.loads(CLOSURE.read_text())


def test_structural_process_closure_is_negative_and_non_authorizing() -> None:
    payload = _payload()
    assert payload["issue_454"]["candidate_terminal"] == "USEFUL_PROCESS_NOT_NOVEL"
    assert payload["scientific_method_novelty_granted"] is False
    assert payload["grants_issue_closure_authority"] is False
    assert payload["grants_merge_authority"] is False
    assert len(payload["issue_454"]["no_material_change_rounds"]) >= 2


def test_rlc_harvest_closure_covers_every_day_and_two_final_rounds() -> None:
    harvest = _payload()["issue_457"]
    assert harvest["candidate_terminal"] == "RLC_2026_STRUCTURAL_HARVEST_SATURATED"
    assert set(harvest["coverage"].values()) == {"TRIAGED"}
    assert len(harvest["no_material_change_rounds"]) >= 2


def test_unread_rlc_route_is_explicitly_non_load_bearing() -> None:
    routes = _payload()["issue_457"]["final_source_dispositions"]
    hidden = next(item for item in routes if item["route"] == "Hidden Tuning Is Misleading the RL Community")
    assert hidden["source_state"] == "DEFER/CANNOT_CHECK"
    assert "non-load-bearing" in hidden["consequence"]
