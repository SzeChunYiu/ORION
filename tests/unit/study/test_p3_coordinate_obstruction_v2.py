from __future__ import annotations

import pytest

from orion.study.p3_coordinate_obstruction_v2 import (
    FAMILIES,
    GOLD_STATUS,
    PROTOCOL_ID,
    ProtocolFreezeError,
    emit_freeze,
    fixtures,
    load_frozen_fixtures,
    load_frozen_protocol,
    validate_fixture,
)


def test_protocol_freeze_has_eight_families_and_cannot_check_gold() -> None:
    hashes = emit_freeze()
    assert hashes["gold_status"] == GOLD_STATUS
    protocol = load_frozen_protocol()
    assert protocol["protocol_id"] == PROTOCOL_ID
    assert protocol["protocol_status"] == "DESIGN_FROZEN"
    assert protocol["outcome_accessed"] is False
    assert protocol["gold_status"] == GOLD_STATUS
    assert protocol["v1_confirmatory_immutable"] is True
    assert protocol["required_families"] == list(FAMILIES)
    assert "generic schema induction" in protocol["novelty_nonclaims"]
    records = load_frozen_fixtures()
    present = {item["family"] for item in records}
    assert present == set(FAMILIES)
    assert all(item["gold_status"] == GOLD_STATUS for item in records)
    assert all(item["expected_integration"] is None for item in records)
    assert all(item["llm_gold_forbidden"] is True for item in records)
    assert any(item["arity"] == "triple" for item in records)


def test_llm_gold_cannot_be_attached_to_v2_fixture() -> None:
    record = dict(fixtures()[0])
    record["gold_authority"] = {"kind": "LLM_PROPOSAL", "evidence": ["none"]}
    record["gold_status"] = GOLD_STATUS
    with pytest.raises(ProtocolFreezeError, match="forbidden gold authority"):
        validate_fixture(record)


def test_v2_fixture_cannot_invent_expected_integration() -> None:
    record = dict(fixtures()[0])
    record["expected_integration"] = "OBSTRUCTION"
    with pytest.raises(ProtocolFreezeError, match="expected_integration"):
        validate_fixture(record)
