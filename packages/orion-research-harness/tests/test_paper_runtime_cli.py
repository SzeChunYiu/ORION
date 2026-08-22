from __future__ import annotations

import json

from orion.self_orion.saturation_vector import DevelopmentSaturationAxis
from orion_research_harness.paper_cli import main


def _route(route_id: str, family: str, assumption: str) -> dict[str, object]:
    return {
        "route_id": route_id,
        "route_family": family,
        "obligation_ids": ["o"],
        "critical_assumption_ids": [assumption],
        "coverage_scope_ids": ["scope:o"],
    }


def test_navigation_plan_cli_fail_closes_open_task(capsys):
    payload = {
        "active_chart": {
            "chart_id": "chart",
            "location_ids": ["s"],
            "edges": [],
            "obligation_ids": ["o"],
        },
        "current_location_id": "s",
        "frontier_ids": [],
        "routes": [_route("r", "PARENT", "assumption:a")],
        "obligations": [{"obligation_id": "o", "mandatory": True, "status": "OPEN"}],
        "remaining_budget": 0,
    }
    assert main(["navigation-plan", "--json", json.dumps(payload)]) == 4
    result = json.loads(capsys.readouterr().out)
    assert result["decision"]["action"] == "CANNOT_CHECK"
    assert result["decision"]["grants_global_task_stop_authority"] is False
    assert result["grants_scientific_authority"] is False


def test_research_saturation_cli_uses_structural_route_independence(capsys):
    axes = [item.value for item in DevelopmentSaturationAxis]
    payload = {
        "rounds": [
            {
                "round_id": "1",
                "route_contracts": [_route("r1", "PARENT", "assumption:a")],
                "observed_axes": axes,
                "axis_item_ids": {},
            },
            {
                "round_id": "2",
                "route_contracts": [_route("r2", "OMISSION", "assumption:b")],
                "observed_axes": axes,
                "axis_item_ids": {},
            },
        ]
    }
    assert main(["research-saturation", "--json", json.dumps(payload)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["report"]["bounded_saturated"] is True
    assert result["report"]["cannot_check_resource_bound"] is False
    assert result["report"]["grants_absolute_completeness"] is False
    assert result["grants_global_task_stop_authority"] is False
