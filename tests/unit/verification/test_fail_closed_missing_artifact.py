from __future__ import annotations

from scientific_result_verification import (
    decide_verification_state,
    layer_result,
    missing_artifact_record,
    validate_record,
)


def _core_layers(replay="PASS", scorer="PASS", denom="PASS", holdout="CANNOT_CHECK"):
    return {
        "raw_artifact_replay": layer_result(replay, "x"),
        "independent_scorer": layer_result(scorer, "x"),
        "leakage_shortcut": layer_result("CANNOT_CHECK", "x"),
        "denominator_statistics": layer_result(denom, "x"),
        "baseline_pressure": layer_result("CANNOT_CHECK", "x"),
        "holdout_cross_host": layer_result(holdout, "x"),
    }


def test_missing_required_artifact_cannot_be_verified():
    layers = _core_layers()
    state, _reason = decide_verification_state(
        layers=layers,
        discrepancies=[],
        required_artifacts_missing=True,
        numbers_replayed=False,
        independent_agrees=False,
    )
    assert state == "CANNOT_CHECK"


def test_missing_artifact_plus_failed_layer_invalidates():
    layers = _core_layers(replay="FAIL")
    state, reason = decide_verification_state(
        layers=layers,
        discrepancies=[],
        required_artifacts_missing=True,
        numbers_replayed=False,
        independent_agrees=False,
    )
    assert state == "INVALIDATED"
    assert reason


def test_schema_rejects_verified_with_missing_required_row():
    payload = {
        "schema_version": "orion.scientific-result-verification.v1",
        "record_id": "x",
        "self_authorizing": False,
        "paper_id": "P4",
        "claim_id": "P4.H1",
        "atomic_claim_text": "x",
        "bounded_claim_text": "x",
        "subject": {
            "commit": "a" * 40,
            "tree": None,
            "evaluated_system_mutated": False,
        },
        "protocol": {"id": "p", "hash_sha256": "c" * 64},
        "raw_artifacts": [missing_artifact_record(path="gone.jsonl")],
        "scorers": {
            "original_hash_sha256": "CANNOT_CHECK",
            "independent_hash_sha256": "d" * 64,
            "independent_from_written_spec": True,
            "agreement": "CANNOT_CHECK",
            "adjudication": [],
        },
        "denominator": {
            "eligible_n": 1,
            "unit": "case",
            "repeats_nested_not_inflating_n": True,
            "cannot_check_or_invalid_handling": "x",
            "post_outcome_exclusions": 0,
        },
        "layers": _core_layers(),
        "verification_state": "VERIFIED",
        "invalidation_reason": None,
        "discrepancies": [],
        "high_severity_integrity": [],
    }
    errors = validate_record(payload)
    assert errors
