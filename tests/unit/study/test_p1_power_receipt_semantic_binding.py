from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.study.p1_p5_successor_readiness import assess_protocol


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = ROOT / "research/claim_expansion/p1/gpt_r7/R7A_MAXT_POWER_AMENDMENT_V2.json"


def _protocol() -> dict[str, object]:
    return json.loads(PROTOCOL.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("field", "tampered_value"),
    (
        ("simulation_seed", 1),
        ("simulation_draws", 10000),
        ("registered_simulated_minimum_independent_units", 32),
        ("registered_simulated_projected_joint_power", 0.999999),
        ("registered_simulated_critical_value", 1.0),
    ),
)
def test_p1_protocol_cannot_override_bound_max_t_receipt(
    field: str, tampered_value: object
) -> None:
    protocol = _protocol()
    protocol["power"][field] = tampered_value
    report = assess_protocol(protocol, root=ROOT)
    assert f"p1_registered_power_receipt_mismatch:{field}" in report.blockers
    assert report.status == "LOCAL_PREOUTCOME_CHECK_FAILED"
    assert report.execution_authorized is False


def test_untampered_p1_protocol_still_passes_local_preoutcome_checks() -> None:
    report = assess_protocol(_protocol(), root=ROOT)
    assert report.status == "READY_FOR_EXTERNAL_BINDING", report.blockers
    assert report.execution_authorized is False
    assert report.execution_terminal == "P1_R7A_CANNOT_CHECK_EXTERNAL_BINDINGS"
