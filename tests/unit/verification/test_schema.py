from __future__ import annotations

import pytest

from scientific_result_verification import (
    SCHEMA_VERSION,
    dump_record,
    layer_result,
    validate_record,
    write_record,
)


def _layers(**overrides):
    base = {
        "raw_artifact_replay": layer_result("PASS", "replayed"),
        "independent_scorer": layer_result("PASS", "agreed"),
        "leakage_shortcut": layer_result("PASS", "no leak"),
        "denominator_statistics": layer_result("PASS", "n ok"),
        "baseline_pressure": layer_result("PASS", "baseline named"),
        "holdout_cross_host": layer_result("PASS", "holdout run"),
    }
    base.update(overrides)
    return base


def _valid(**overrides):
    payload = {
        "schema_version": SCHEMA_VERSION,
        "record_id": "fixture.claim",
        "self_authorizing": False,
        "paper_id": "P4",
        "claim_id": "P4.H1",
        "atomic_claim_text": "ORION false promotions 0/360.",
        "bounded_claim_text": "Bounded to the frozen V2 battery.",
        "subject": {
            "commit": "a" * 40,
            "tree": "b" * 40,
            "note": "fixture",
            "evaluated_system_mutated": False,
        },
        "protocol": {"id": "P4.protected-authority.v2", "hash_sha256": "c" * 64, "path": "x"},
        "raw_artifacts": [
            {"path": "metrics.json", "role": "aggregate", "present": True, "sha256": "d" * 64}
        ],
        "scorers": {
            "original_hash_sha256": "e" * 64,
            "independent_hash_sha256": "f" * 64,
            "independent_from_written_spec": True,
            "agreement": "EXACT",
            "adjudication": [],
        },
        "denominator": {
            "eligible_n": 360,
            "unit": "case",
            "repeats_nested_not_inflating_n": True,
            "cannot_check_or_invalid_handling": "none",
            "post_outcome_exclusions": 0,
        },
        "layers": _layers(),
        "verification_state": "VERIFIED",
        "invalidation_reason": None,
        "discrepancies": [],
        "high_severity_integrity": [],
    }
    payload.update(overrides)
    return payload


def test_valid_verified_roundtrip(tmp_path):
    record = write_record(_valid())
    assert record["record_sha256"]
    assert validate_record(record) == []
    path = tmp_path / "r.json"
    dump_record(path, {k: v for k, v in record.items() if k != "record_sha256"})
    assert path.is_file()


def test_self_authorizing_true_rejected():
    payload = _valid(self_authorizing=True)
    assert any("self_authorizing" in err for err in validate_record(payload))


def test_verified_forbidden_when_required_artifact_missing():
    payload = _valid()
    payload["raw_artifacts"] = [
        {"path": "missing.jsonl", "role": "missing_required", "present": False, "sha256": "CANNOT_CHECK"}
    ]
    errors = validate_record(payload)
    assert any("VERIFIED is forbidden" in err for err in errors)


def test_verified_forbidden_when_holdout_cannot_check():
    payload = _valid(layers=_layers(holdout_cross_host=layer_result("CANNOT_CHECK", "not run")))
    errors = validate_record(payload)
    assert any("holdout_cross_host" in err for err in errors)


def test_invalidated_requires_reason():
    payload = _valid(verification_state="INVALIDATED", invalidation_reason=None)
    assert any("invalidation_reason" in err for err in validate_record(payload))


def test_write_record_rejects_invalid():
    with pytest.raises(ValueError, match="self_authorizing"):
        write_record(_valid(self_authorizing=True))
