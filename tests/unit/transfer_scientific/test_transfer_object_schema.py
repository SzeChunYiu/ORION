"""Frozen scientific transfer-object schema: pairs and representations before outcomes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.transfer.scientific.objects import (
    FORBIDDEN_OUTCOME_FIELDS,
    SCHEMA_VERSION,
    ScientificTransferObject,
    load_schema,
    schema_digest,
    transfer_object_from_payload,
)
from orion.transfer.v2.canonical import content_digest

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = (
    ROOT
    / "research"
    / "cross-domain-mechanic-transfer-v1"
    / "schemas"
    / "TRANSFER_OBJECT_SCHEMA_V1.json"
)

REQUIRED_FIELDS = (
    "schema_version",
    "object_id",
    "problem_signature",
    "io_contract",
    "obligations",
    "assumptions",
    "preconditions",
    "transformation_steps",
    "failure_modes",
    "verification_hooks",
    "falsifiers",
    "authority_boundaries",
    "cost_requirements",
    "evidence_level",
    "source_evidence_identities",
    "target_compatibility_tests",
    "forbidden_transfers",
    "content_hash",
)


def _valid_payload() -> dict[str, object]:
    unsigned = {
        "schema_version": SCHEMA_VERSION,
        "object_id": "cell:active-discriminator:debugging",
        "problem_signature": {
            "signature_id": "sig:debug-isolate",
            "family_id": "debugging",
            "surface_domain": "software-failure-diagnosis",
            "hidden_state": "latent-responsible-component",
            "observability": "partial-probeable",
            "actions": ["probe", "abstain"],
            "ground_truth_class": "protected",
            "dependence": 0.6,
            "authority_risk": 0.8,
            "nonstationarity": 0.2,
            "reversibility": 0.9,
        },
        "io_contract": {
            "inputs": ["failure-report", "component-graph"],
            "outputs": ["responsibility-hypothesis"],
            "observables": ["probe-outcome"],
        },
        "obligations": ["distinguish-responsibility-before-repair"],
        "assumptions": ["probes_are_reversible", "components_are_separable"],
        "preconditions": ["probe_tool_available"],
        "transformation_steps": ["select-discriminator", "probe", "update-hypothesis"],
        "failure_modes": ["non-diagnosable-overlap"],
        "verification_hooks": ["held-out-component-isolation"],
        "falsifiers": ["discriminator-separates-toy-components"],
        "authority_boundaries": {
            "may_grant": ["inspection-license"],
            "may_not_grant": ["publication-authority", "target-label-access"],
        },
        "cost_requirements": {
            "context_budget": 4,
            "tools_required": ["probe"],
        },
        "evidence_level": "LOCAL_ENGINEERING_ONLY",
        "source_evidence_identities": ["artifact:debug-toy-v1"],
        "target_compatibility_tests": ["assumption:probes_are_reversible"],
        "forbidden_transfers": ["copy-source-patch-into-target"],
    }
    payload = dict(unsigned)
    payload["content_hash"] = content_digest(unsigned)
    return payload


def test_schema_file_declares_frozen_required_fields() -> None:
    schema = load_schema(SCHEMA_PATH)
    assert schema["$id"] == "ORION.scientific-transfer-object.v1"
    assert schema["additionalProperties"] is False
    for field in REQUIRED_FIELDS:
        assert field in schema["required"]
        assert field in schema["properties"]


def test_schema_digest_is_content_addressed_and_stable() -> None:
    digest = schema_digest(SCHEMA_PATH)
    assert digest.startswith("sha256:")
    assert digest == content_digest(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))


def test_valid_object_roundtrips_and_binds_content_hash() -> None:
    obj = transfer_object_from_payload(_valid_payload())
    assert isinstance(obj, ScientificTransferObject)
    assert obj.schema_version == SCHEMA_VERSION
    obj.verify()
    rebuilt = transfer_object_from_payload(obj.to_payload())
    assert rebuilt.to_payload() == obj.to_payload()


def test_hidden_target_labels_are_rejected() -> None:
    payload = _valid_payload()
    payload["target_label"] = "B"
    with pytest.raises(ValueError, match="forbidden outcome"):
        transfer_object_from_payload(payload)


def test_content_hash_mismatch_is_rejected() -> None:
    payload = _valid_payload()
    payload["content_hash"] = "sha256:" + ("0" * 64)
    with pytest.raises(ValueError, match="digest mismatch"):
        transfer_object_from_payload(payload)


def test_empty_assumptions_or_authority_boundaries_are_rejected() -> None:
    payload = _valid_payload()
    payload["assumptions"] = []
    del payload["content_hash"]
    payload["content_hash"] = content_digest(
        {key: value for key, value in payload.items() if key != "content_hash"}
    )
    with pytest.raises(ValueError, match="assumption"):
        transfer_object_from_payload(payload)


def test_forbidden_outcome_field_names_are_explicit() -> None:
    assert "heldout_answer" in FORBIDDEN_OUTCOME_FIELDS
    assert "target_label" in FORBIDDEN_OUTCOME_FIELDS
    assert "score" in FORBIDDEN_OUTCOME_FIELDS
