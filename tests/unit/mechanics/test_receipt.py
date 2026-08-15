import pytest

from orion.mechanics import MechanicReceipt, MechanicRunStatus


def test_failed_mechanic_requires_a_failure_signature_or_residual():
    with pytest.raises(ValueError, match="failure signature or residual"):
        MechanicReceipt("r1", "SEARCH.v1", MechanicRunStatus.FAILED)


def test_cannot_check_mechanic_requires_a_failure_signature_or_residual():
    with pytest.raises(ValueError, match="failure signature or residual"):
        MechanicReceipt("r-cannot-check", "VERIFY.v1", MechanicRunStatus.CANNOT_CHECK)


def test_success_receipt_can_be_minimal_but_typed():
    receipt = MechanicReceipt(
        "r2",
        "FRAME.v1",
        MechanicRunStatus.SUCCEEDED,
        cost_units=1.0,
        latency_seconds=0.1,
    )
    assert receipt.status is MechanicRunStatus.SUCCEEDED
