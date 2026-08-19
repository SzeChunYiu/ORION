from __future__ import annotations

import copy

import pytest

from orion.study.p5.revision_level_v3_freeze import (
    derive_candidate_packet,
    derive_protected_commitment,
    validate_candidate_packet,
    validate_protected_suite,
)


def _suite() -> dict:
    return {
        "schema_version": "orion.p5.revision-level-v3.protected-suite.v1",
        "suite_id": "dev:v3:freeze",
        "development_only": True,
        "created_before_outcome_access": True,
        "suite_nonce": "1" * 64,
        "revision_invasiveness": {
            "UNRESOLVED": 0,
            "EVIDENCE_REPAIR": 1,
            "EXECUTION_REPAIR": 1,
            "MEASUREMENT_REPAIR": 2,
            "WITHIN_CLASS_MODEL_REPAIR": 2,
            "MODEL_CLASS_EXPANSION": 4,
            "REPRESENTATION_REGIME_REPAIR": 5,
            "BROAD_SELF_EDIT": 6,
        },
        "cases": [
            {
                "case_id": "V3-FZ-01",
                "symptom_family": "same-residual",
                "visible_symptom": "prediction mismatch",
                "candidate_visible_context": {"domain": "toy"},
                "competing_revision_classes": ["EVIDENCE_REPAIR", "MODEL_CLASS_EXPANSION"],
                "hypotheses": {
                    "EVIDENCE_REPAIR": {"inspect": ["MISSING_SOURCE"]},
                    "MODEL_CLASS_EXPANSION": {"inspect": ["COMPLETE_EVIDENCE_MODEL_MISS"]},
                },
                "allowed_diagnostics": [{"action_id": "inspect", "cost": 1.0}],
                "diagnostic_budget": 1.0,
                "protected_diagnostic_outcomes": {"inspect": "MISSING_SOURCE"},
                "protected_gold_revision_class": "EVIDENCE_REPAIR",
                "preservation_obligations": ["preserve:model"],
                "allowed_change_surface": ["evidence"],
                "protected_surface": ["evaluator"],
                "fresh_transfer_family": "fresh:A",
            },
            {
                "case_id": "V3-FZ-02",
                "symptom_family": "same-residual",
                "visible_symptom": "prediction mismatch",
                "candidate_visible_context": {"domain": "toy"},
                "competing_revision_classes": ["EVIDENCE_REPAIR", "MODEL_CLASS_EXPANSION"],
                "hypotheses": {
                    "EVIDENCE_REPAIR": {"inspect": ["MISSING_SOURCE"]},
                    "MODEL_CLASS_EXPANSION": {"inspect": ["COMPLETE_EVIDENCE_MODEL_MISS"]},
                },
                "allowed_diagnostics": [{"action_id": "inspect", "cost": 1.0}],
                "diagnostic_budget": 1.0,
                "protected_diagnostic_outcomes": {"inspect": "COMPLETE_EVIDENCE_MODEL_MISS"},
                "protected_gold_revision_class": "MODEL_CLASS_EXPANSION",
                "preservation_obligations": ["preserve:evidence"],
                "allowed_change_surface": ["model/class"],
                "protected_surface": ["evaluator"],
                "fresh_transfer_family": "fresh:B",
            },
        ],
    }


def test_candidate_packet_strips_gold_and_protected_outcomes() -> None:
    suite = _suite()
    validate_protected_suite(suite)
    packet = derive_candidate_packet(suite)
    validate_candidate_packet(packet)
    rendered = repr(packet)
    assert "protected_gold_revision_class" not in rendered
    assert "protected_diagnostic_outcomes" not in rendered
    assert "MISSING_SOURCE" in rendered  # hypotheses are public expectations
    assert packet["development_only"] is True


def test_same_symptom_family_may_have_different_protected_gold() -> None:
    suite = _suite()
    validate_protected_suite(suite)
    assert suite["cases"][0]["symptom_family"] == suite["cases"][1]["symptom_family"]
    assert suite["cases"][0]["protected_gold_revision_class"] != suite["cases"][1]["protected_gold_revision_class"]


def test_duplicate_case_identity_is_rejected() -> None:
    suite = _suite()
    suite["cases"][1]["case_id"] = suite["cases"][0]["case_id"]
    with pytest.raises(ValueError, match="duplicate case_id"):
        validate_protected_suite(suite)


def test_duplicate_diagnostic_identity_is_rejected() -> None:
    suite = _suite()
    suite["cases"][0]["allowed_diagnostics"].append({"action_id": "inspect", "cost": 0.5})
    with pytest.raises(ValueError, match="duplicate diagnostic"):
        validate_protected_suite(suite)


def test_gold_must_be_in_competing_revision_classes_or_unresolved() -> None:
    suite = _suite()
    suite["cases"][0]["protected_gold_revision_class"] = "MEASUREMENT_REPAIR"
    with pytest.raises(ValueError, match="gold revision"):
        validate_protected_suite(suite)


def test_protected_and_allowed_surfaces_cannot_overlap() -> None:
    suite = _suite()
    suite["cases"][0]["allowed_change_surface"] = ["evaluator/config"]
    with pytest.raises(ValueError, match="overlap"):
        validate_protected_suite(suite)


def test_protected_commitment_changes_when_gold_changes_but_packet_does_not() -> None:
    left = _suite()
    right = copy.deepcopy(left)
    right["cases"][0]["protected_gold_revision_class"] = "MODEL_CLASS_EXPANSION"
    right["cases"][0]["protected_diagnostic_outcomes"]["inspect"] = "COMPLETE_EVIDENCE_MODEL_MISS"
    assert derive_candidate_packet(left) == derive_candidate_packet(right)
    assert derive_protected_commitment(left) != derive_protected_commitment(right)


def test_zero_nonce_is_rejected() -> None:
    suite = _suite()
    suite["suite_nonce"] = "0" * 64
    with pytest.raises(ValueError, match="nonce"):
        validate_protected_suite(suite)
