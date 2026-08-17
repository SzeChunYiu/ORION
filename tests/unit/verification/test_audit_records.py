from __future__ import annotations

from pathlib import Path

from audit import run_all
from scientific_result_verification import validate_record

ROOT = Path(__file__).resolve().parents[3]


def test_audit_emits_receipts_for_flagship_surfaces():
    records = run_all(ROOT)
    ids = {row["record_id"] for row in records}
    assert "P4.H1.false-authority-promotion" in ids
    assert "P4.H2.clean-authority-coverage" in ids
    assert "P3.C5.confirmatory-mapping" in ids
    assert "P2.controlled-complete-gold" in ids
    assert "P5.glm-5.2-attribution-21-24" in ids
    assert "P1.H1.root-success-not-supported" in ids
    for row in records:
        errors = validate_record(row)
        assert errors == [], (row["record_id"], errors)
        assert row["self_authorizing"] is False
        assert row["subject"]["evaluated_system_mutated"] is False
        assert row["verification_state"] != "VERIFIED" or not row["high_severity_integrity"]
        p1_h1 = row["record_id"] == "P1.H1.root-success-not-supported"
        if p1_h1:
            assert "NOT_SUPPORTED" in row["atomic_claim_text"]
            assert row["verification_state"] in {"BOUNDED_VERIFIED", "CANNOT_CHECK"}
