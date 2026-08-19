from __future__ import annotations

from orion.study.p10.a0_runtime import (
    Responsibility,
    build_case,
    candidate_packet,
    derive_responsibility,
    model_payload,
    run_a0,
)


def test_v1_1_same_surface_group_has_all_responsibilities_and_same_candidate_kind_order():
    cases = [
        build_case(
            responsibility,
            seed=f"structure-{index}",
            surface_seed="shared-surface",
        )
        for index, responsibility in enumerate(Responsibility)
    ]
    assert len({case.surface_atom for case in cases}) == 1
    assert len({derive_responsibility(case) for case in cases}) == len(Responsibility)
    orders = {
        tuple(candidate.kind for candidate in candidate_packet(case, order_seed="shared-order"))
        for case in cases
    }
    assert len(orders) == 1


def test_v1_1_model_payload_removes_evaluator_world_identity():
    case = build_case(Responsibility.LOCAL_ACTION, seed="identity", surface_seed="shared")
    payload = model_payload(case)
    assert "world_id" not in payload
    assert case.world_id not in repr(payload)


def test_v1_1_full_run_measures_surface_contract_and_donor_sufficiency():
    result = run_a0(seed="v1.1-smoke", cases_per_family=16)
    assert result["protocol"] == "P10.A0ResponsibilityControlProtocol.v1.1"
    assert result["surface_group_count"] == 16
    assert result["same_surface_hostile_contract_green"] is True
    assert result["arms"]["DONOR_COMPOSED_CONTROL"]["accuracy"] == 1.0
    assert result["arms"]["ORION_RESPONSIBILITY_CONTROL"]["accuracy"] == 1.0
    assert result["terminal"] == "P10_EXISTING_STRUCTURED_CONTROL_SUFFICIENT"
    assert result["grants_live_llm_escalation"] is False
