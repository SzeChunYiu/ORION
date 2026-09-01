from __future__ import annotations

import json
from pathlib import Path

import pytest

from nq_engine_a.factorization import FactorizationStatus, find_disjoint_zero_sums
from nq_engine_a.group import GroupSpec

ROOT = Path(__file__).resolve().parents[1]


def load_witness(name: str) -> list[list[int]]:
    payload = json.loads((ROOT / "fixtures" / name).read_text())
    assert "EXPECTED_OUTCOME_EXPOSURE" in payload["exposure_markers"]
    return payload["witness"]


@pytest.mark.permitted_lower_control
def test_expected_outcome_exposed_d2_lower_witness_has_no_two_disjoint_zero_sums() -> None:
    result = find_disjoint_zero_sums(GroupSpec(5, 3), load_witness("d2_lower_witness.json"), 2)
    assert result.status is FactorizationStatus.NEGATIVE
    assert result.exhaustive


@pytest.mark.permitted_lower_control
def test_expected_outcome_exposed_d3_lower_witness_has_two_but_not_three_factors() -> None:
    spec = GroupSpec(5, 3)
    witness = load_witness("d3_lower_witness.json")
    two = find_disjoint_zero_sums(spec, witness, 2)
    three = find_disjoint_zero_sums(spec, witness, 3, max_states=300_000)
    assert two.status is FactorizationStatus.POSITIVE
    assert two.certificate is not None
    assert three.status is FactorizationStatus.NEGATIVE
    assert three.exhaustive
