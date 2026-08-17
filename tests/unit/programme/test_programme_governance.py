"""Step-3 governance freeze is complete as a document and grants nothing."""

from __future__ import annotations

from orion.programme.activation import PREPARATORY_STATUS, UNBOUND_DIGEST
from orion.programme.governance import (
    GOVERNANCE_SCHEMA,
    governance_payload,
    repository_governance_freeze,
    validate_governance_payload,
)
from orion.programme.identity import verify_seal


def test_repository_governance_is_inert_and_complete() -> None:
    freeze = repository_governance_freeze()
    assert freeze.programme_status == PREPARATORY_STATUS
    assert freeze.grants_self_sustaining_authority is False
    assert freeze.grants_phase4_closure is False
    assert freeze.freeze_in_force is False
    assert freeze.host_authority_id == ""
    assert freeze.evaluator_artifact_hash == UNBOUND_DIGEST
    assert freeze.held_out_split_hash == UNBOUND_DIGEST
    assert freeze.objectives
    assert freeze.research_question_queue_policy
    assert freeze.exploration_exploitation_policy
    assert freeze.budget_ceilings
    assert freeze.stop_rules
    assert freeze.protected_benchmark_families
    assert freeze.held_out_refresh_policy
    assert freeze.evaluator_custody_policy
    assert freeze.evaluator_versioning_policy
    assert freeze.search_web_contamination_policy
    assert freeze.halt_revert_conditions


def test_governance_payload_is_sealed_and_valid() -> None:
    payload = governance_payload(repository_governance_freeze())
    assert verify_seal(payload) == ()
    assert payload["schema_version"] == GOVERNANCE_SCHEMA
    assert payload["authority_granted"] is False
    assert validate_governance_payload(payload) == ()


def test_governance_payload_rejects_a_self_grant() -> None:
    payload = governance_payload(repository_governance_freeze())
    payload["grants_self_sustaining_authority"] = True
    errors = validate_governance_payload(payload)
    assert "governance document must not grant self-sustaining authority" in errors


def test_governance_payload_rejects_a_bound_evaluator_identity() -> None:
    payload = governance_payload(repository_governance_freeze())
    payload["evaluator_artifact_hash"] = "a" * 64
    errors = validate_governance_payload(payload)
    assert any("evaluator_artifact_hash" in item for item in errors)


def test_governance_payload_rejects_freeze_in_force() -> None:
    payload = governance_payload(repository_governance_freeze())
    payload["freeze_in_force"] = True
    errors = validate_governance_payload(payload)
    assert "governance freeze is not in force while activation is withheld" in errors
