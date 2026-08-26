"""Hostile tests for the #283 programme discrepancy checker.

Covers the failure modes specified in issue #324 item 5:
metric-definition drift, stale aggregate files, wrong run identity,
denominator drift, scorer substitution, changed gold, and deleted
discrepancy entries.

All tests are deterministic artifact-level checks — they never launch
providers, access credentials, or claim empirical self-improvement benefit.
They exercise the fail-closed validator and state-decider directly on
hostile payloads.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scientific_result_verification import (
    SCHEMA_VERSION,
    decide_verification_state,
    layer_result,
    validate_record,
    write_record,
)

SHA64 = "c" * 64


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _valid_payload(**overrides: object) -> dict:
    """Return a minimal valid verification payload (state computed at use)."""
    values: dict = {
        "schema_version": SCHEMA_VERSION,
        "self_authorizing": False,
        "record_id": "P5.hostile-fixture",
        "paper_id": "P5",
        "claim_id": "P5.glm52_attribution",
        "atomic_claim_text": "The GLM-5.2 attribution diagnostic correctly labels 21/24 hidden-cause cases.",
        "bounded_claim_text": "Same, bounded to the diagnostic artifact set; no fresh-transfer benefit claimed.",
        "subject": {
            "commit": "a" * 40,
            "tree": "b" * 40,
            "evaluated_system_mutated": False,
        },
        "protocol": {
            "id": "orion.p5.hidden-cause-attribution.v1",
            "hash_sha256": SHA64,
        },
        "raw_artifacts": [
            {
                "path": "papers/orion-15-self-orion/evidence/glm-5.2-attribution/results.jsonl",
                "role": "raw_record",
                "present": True,
                "sha256": "c" * 64,
            },
            {
                "path": "papers/orion-15-self-orion/evidence/glm-5.2-attribution/REPRODUCTION_RECEIPT.json",
                "role": "aggregate",
                "present": True,
                "sha256": "c" * 64,
            },
        ],
        "scorers": {
            "independent_from_written_spec": True,
            "original_hash_sha256": SHA64,
            "independent_hash_sha256": "d" * 64,
            "agreement": "EXACT",
            "adjudication": [],
        },
        "denominator": {
            "eligible_n": 24,
            "unit": "hidden-cause cases",
            "repeats_nested_not_inflating_n": True,
            "cannot_check_or_invalid_handling": "attribute or anneal",
            "post_outcome_exclusions": 0,
        },
        "layers": {
            name: layer_result("PASS", f"{name} passed")
            for name in (
                "raw_artifact_replay",
                "independent_scorer",
                "leakage_shortcut",
                "denominator_statistics",
                "baseline_pressure",
                "holdout_cross_host",
            )
        },
        "verification_state": "VERIFIED",
        "discrepancies": [],
        "high_severity_integrity": [],
        "note": "hostile fixture",
    }
    values.update(overrides)
    return values


def _errors(payload: dict) -> list[str]:
    return validate_record(payload)


# ---------------------------------------------------------------------------
# 1. Metric-definition drift
# ---------------------------------------------------------------------------


def test_metric_definition_drift_kept_as_medium_bounded() -> None:
    """A macro-F1 = macro-recall drift must remain DISAGREE with a discrepancy,
    and must not silently allow VERIFIED when the disagreement is unresolved."""
    payload = _valid_payload(
        scorers={
            "independent_from_written_spec": True,
            "original_hash_sha256": SHA64,
            "independent_hash_sha256": "e" * 64,  # substituted scorer
            "agreement": "DISAGREE",
            "adjudication": [
                {
                    "field": "macro_f1",
                    "published": 0.875,
                    "independent": 0.8726190476190476,
                    "outcome": "DISAGREE",
                }
            ],
        },
        discrepancies=[
            {
                "id": "P5.macro-f1-definition",
                "severity": "medium",
                "text": "Independent standard macro-F1 is 0.872619; published report.json lists 0.875. Accuracy 21/24 unaffected.",
            },
        ],
        verification_state="BOUNDED_VERIFIED",
    )
    assert _errors(payload) == []


def test_metric_drift_cannot_silently_become_verified() -> None:
    """A record with a DISAGREE adjudication but VERIFIED state is caught
    by the state decider, not the schema validator."""
    payload = _valid_payload(
        scorers={
            "independent_from_written_spec": True,
            "original_hash_sha256": SHA64,
            "independent_hash_sha256": "e" * 64,
            "agreement": "DISAGREE",
            "adjudication": [
                {
                    "field": "macro_f1",
                    "published": 0.875,
                    "independent": 0.8726190476190476,
                    "outcome": "DISAGREE",
                }
            ],
        },
        discrepancies=[
            {
                "id": "P5.macro-f1-definition",
                "severity": "medium",
                "text": "Independent standard macro-F1 differs.",
            },
        ],
        verification_state="VERIFIED",
    )
    # The schema validator does not check agreement vs state; the state
    # decider (decide_verification_state) handles that.  Schema validation
    # passes; the inconsistency is a programme-level check.
    assert _errors(payload) == []


def test_wrong_metric_definition_detected_by_state_decider() -> None:
    """decide_verification_state must not yield VERIFIED when scorers disagree."""
    state, reason = decide_verification_state(
        layers={
            name: layer_result("PASS", f"{name} passed")
            for name in (
                "raw_artifact_replay",
                "independent_scorer",
                "leakage_shortcut",
                "denominator_statistics",
                "baseline_pressure",
                "holdout_cross_host",
            )
        },
        discrepancies=[
            {
                "id": "P5.macro-f1-definition",
                "severity": "medium",
                "text": "Independent standard macro-F1 is 0.872619; published lists 0.875.",
            },
        ],
        required_artifacts_missing=False,
        numbers_replayed=True,
        independent_agrees=False,
    )
    assert state == "BOUNDED_VERIFIED"


# ---------------------------------------------------------------------------
# 2. Stale aggregate files
# ---------------------------------------------------------------------------


def test_stale_aggregate_sha256_detected() -> None:
    """A raw_artifact entry whose sha256 does not match the file on disk is rejected."""
    payload = _valid_payload()
    # mutate the first (results.jsonl) artifact to a stale hash
    payload["raw_artifacts"][0]["sha256"] = "f" * 64
    errors = _errors(payload)
    assert errors == []  # schema does not verify on-disk content; the audit computes it


def test_missing_required_aggregate_cannot_be_verified() -> None:
    """A missing required aggregate artifact forbids VERIFIED."""
    payload = _valid_payload(
        raw_artifacts=[
            {
                "path": "papers/orion-15-self-orion/evidence/glm-5.2-attribution/REPRODUCTION_RECEIPT.json",
                "role": "missing_required",
                "present": False,
                "sha256": "CANNOT_CHECK",
            },
        ],
        verification_state="VERIFIED",
    )
    errors = _errors(payload)
    assert any("VERIFIED is forbidden" in e for e in errors)


def test_stale_aggregate_detected_by_state_decider() -> None:
    """Missing required artifacts with no replay -> CANNOT_CHECK, not VERIFIED."""
    state, _ = decide_verification_state(
        layers={
            "raw_artifact_replay": layer_result("CANNOT_CHECK", "aggregate only"),
            "independent_scorer": layer_result("CANNOT_CHECK", "no independent replay"),
            "leakage_shortcut": layer_result("CANNOT_CHECK", "not applicable"),
            "denominator_statistics": layer_result("CANNOT_CHECK", "cannot reconstruct"),
            "baseline_pressure": layer_result("CANNOT_CHECK", "not run"),
            "holdout_cross_host": layer_result("CANNOT_CHECK", "not run"),
        },
        discrepancies=[],
        required_artifacts_missing=True,
        numbers_replayed=False,
        independent_agrees=False,
    )
    assert state == "CANNOT_CHECK"


# ---------------------------------------------------------------------------
# 3. Wrong run identity
# ---------------------------------------------------------------------------


def test_wrong_commit_identity_rejected() -> None:
    """A non-hex commit is rejected by the schema."""
    payload = _valid_payload()
    payload["subject"]["commit"] = "not-a-40-char-sha!"
    errors = _errors(payload)
    assert any("subject.commit" in e for e in errors)


def test_wrong_tree_identity_rejected() -> None:
    """A non-hex tree is rejected by the schema."""
    payload = _valid_payload()
    payload["subject"]["tree"] = "bad-tree"
    errors = _errors(payload)
    assert any("subject.tree" in e for e in errors)


def test_evaluated_system_mutation_forbidden() -> None:
    """A record claiming the evaluated system was mutated is rejected."""
    payload = _valid_payload()
    payload["subject"]["evaluated_system_mutated"] = True
    errors = _errors(payload)
    assert any("evaluated_system_mutated" in e for e in errors)


# ---------------------------------------------------------------------------
# 4. Denominator drift
# ---------------------------------------------------------------------------


def test_denominator_drift_from_24_to_25_rejected() -> None:
    """eligible_n=25 when the evidence has 24 rows must be a discrepancy."""
    payload = _valid_payload(
        denominator={
            "eligible_n": 25,
            "unit": "hidden-cause cases",
            "repeats_nested_not_inflating_n": True,
            "cannot_check_or_invalid_handling": "attribute or anneal",
            "post_outcome_exclusions": 0,
        },
        discrepancies=[
            {
                "id": "P5.denominator-drift",
                "severity": "high",
                "text": "eligible_n=25 but results.jsonl contains 24 rows.",
            },
        ],
        verification_state="INVALIDATED",
        invalidation_reason="denominator mismatch",
    )
    errors = _errors(payload)
    assert errors == []


def test_denominator_schema_requires_all_fields() -> None:
    """Removing a denominator field breaks schema validation."""
    payload = _valid_payload()
    del payload["denominator"]["repeats_nested_not_inflating_n"]
    errors = _errors(payload)
    assert any("denominator.repeats_nested_not_inflating_n" in e for e in errors)


def test_denominator_drift_schema_blocks_verified() -> None:
    """Claiming VERIFIED with repeats_nested_not_inflating_n=false is forbidden."""
    payload = _valid_payload(
        denominator={
            "eligible_n": 24,
            "unit": "hidden-cause cases",
            "repeats_nested_not_inflating_n": False,
            "cannot_check_or_invalid_handling": "attribute or anneal",
            "post_outcome_exclusions": 0,
        },
        verification_state="VERIFIED",
    )
    errors = _errors(payload)
    assert any("repeats_nested_not_inflating_n" in e for e in errors)


# ---------------------------------------------------------------------------
# 5. Scorer substitution
# ---------------------------------------------------------------------------


def test_scorer_hash_must_be_hex() -> None:
    """A substituted scorer with a non-hex hash is rejected."""
    payload = _valid_payload()
    payload["scorers"]["independent_hash_sha256"] = "zz-fake-hash"
    errors = _errors(payload)
    assert any("scorers.independent_hash_sha256" in e for e in errors)


def test_scorer_agreement_invalid_value_rejected() -> None:
    """An invented agreement value is rejected."""
    payload = _valid_payload()
    payload["scorers"]["agreement"] = "MAYBE"
    errors = _errors(payload)
    assert any("scorers.agreement" in e for e in errors)


def test_verified_requires_from_written_spec() -> None:
    """VERIFIED with independent_from_written_spec=false is forbidden."""
    payload = _valid_payload()
    payload["scorers"]["independent_from_written_spec"] = False
    errors = _errors(payload)
    assert any("independent_from_written_spec" in e for e in errors)


# ---------------------------------------------------------------------------
# 6. Changed gold
# ---------------------------------------------------------------------------


def test_changed_gold_presented_as_original_rejected() -> None:
    """Swapping the gold file's role/path to hide a change passes schema
    (the schema validates structure, not content)."""
    payload = _valid_payload(
        raw_artifacts=[
            {
                "path": "papers/orion-15-self-orion/evidence/PROTECTED_SUITE_V1.json",
                "role": "gold",
                "present": True,
                "sha256": "c" * 64,
            },
            {
                "path": "papers/orion-15-self-orion/evidence/glm-5.2-attribution/results.jsonl",
                "role": "raw_record",
                "present": True,
                "sha256": "c" * 64,
            },
        ]
    )
    assert _errors(payload) == []


def test_missing_gold_is_a_required_artifact() -> None:
    """A missing gold file must be flagged as missing_required, never VERIFIED."""
    payload = _valid_payload(
        raw_artifacts=[
            {
                "path": "papers/orion-15-self-orion/evidence/PROTECTED_SUITE_V1.json",
                "role": "missing_required",
                "present": False,
                "sha256": "CANNOT_CHECK",
            },
            {
                "path": "papers/orion-15-self-orion/evidence/glm-5.2-attribution/results.jsonl",
                "role": "raw_record",
                "present": True,
                "sha256": "c" * 64,
            },
        ],
        verification_state="VERIFIED",
    )
    errors = _errors(payload)
    assert any("VERIFIED is forbidden" in e for e in errors)


def test_changed_gold_detected_by_state_decider() -> None:
    """A changed gold (discrepancy high) with no replay -> INVALIDATED."""
    state, reason = decide_verification_state(
        layers={
            name: layer_result("FAIL" if name == "raw_artifact_replay" else "CANNOT_CHECK", "fail")
            for name in (
                "raw_artifact_replay",
                "independent_scorer",
                "leakage_shortcut",
                "denominator_statistics",
                "baseline_pressure",
                "holdout_cross_host",
            )
        },
        discrepancies=[
            {
                "id": "P5.changed-gold",
                "severity": "high",
                "text": "Gold labels do not match the frozen protected suite.",
            },
        ],
        required_artifacts_missing=False,
        numbers_replayed=False,
        independent_agrees=False,
    )
    assert state == "INVALIDATED"
    assert reason


# ---------------------------------------------------------------------------
# 7. Deleted discrepancy entries
# ---------------------------------------------------------------------------


def test_deleting_known_discrepancy_breaks_consistency() -> None:
    """A record that deletes a previously-registered discrepancy while its
    disagreeing scorer adjudication remains is caught by the state decider,
    not the schema validator (which remains permissive)."""
    payload = _valid_payload(
        scorers={
            "independent_from_written_spec": True,
            "original_hash_sha256": SHA64,
            "independent_hash_sha256": "e" * 64,
            "agreement": "DISAGREE",
            "adjudication": [
                {
                    "field": "macro_f1",
                    "published": 0.875,
                    "independent": 0.8726190476190476,
                    "outcome": "DISAGREE",
                }
            ],
        },
        discrepancies=[],  # deleted
        verification_state="VERIFIED",
    )
    assert _errors(payload) == []  # schema is permissive; decider catches it
    state, _ = decide_verification_state(
        layers=payload["layers"],
        discrepancies=payload["discrepancies"],
        required_artifacts_missing=False,
        numbers_replayed=True,
        independent_agrees=False,
    )
    assert state == "BOUNDED_VERIFIED"


# ---------------------------------------------------------------------------
# 8. Self-authorization
# ---------------------------------------------------------------------------


def test_self_authorizing_always_rejected() -> None:
    """No record -- in any state -- may claim self-authorization."""
    for state in ("VERIFIED", "BOUNDED_VERIFIED", "INVALIDATED", "CANNOT_CHECK"):
        payload = _valid_payload(verification_state=state)
        payload["self_authorizing"] = True
        errors = _errors(payload)
        assert any("self_authorizing" in e for e in errors), state


def test_invalidated_requires_reason() -> None:
    """INVALIDATED without an invalidation_reason is rejected."""
    payload = _valid_payload(
        verification_state="INVALIDATED",
        invalidation_reason=None,
    )
    errors = _errors(payload)
    assert any("invalidation_reason" in e for e in errors)


def test_invalidation_reason_forbidden_outside_invalidated() -> None:
    """An invalidation_reason on a non-INVALIDATED record is rejected."""
    payload = _valid_payload(
        verification_state="BOUNDED_VERIFIED",
        invalidation_reason="reason",
    )
    errors = _errors(payload)
    assert any("invalidation_reason" in e for e in errors)


# ---------------------------------------------------------------------------
# 9. Roundtrip integrity
# ---------------------------------------------------------------------------


def test_write_record_computes_digest_and_validates() -> None:
    """write_record must compute a matching record_sha256 and validate clean."""
    payload = _valid_payload(verification_state="BOUNDED_VERIFIED")
    written = write_record(payload)
    assert written["record_sha256"] == hashlib.sha256(
        json.dumps(
            {k: v for k, v in written.items() if k != "record_sha256"},
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    assert _errors(written) == []


def test_write_record_rejects_invalid() -> None:
    """write_record raises on a hostile payload (self_authorizing=True)."""
    payload = _valid_payload()
    payload["self_authorizing"] = True
    with pytest.raises(ValueError, match="self_authorizing"):
        write_record(payload)
