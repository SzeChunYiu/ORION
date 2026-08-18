from __future__ import annotations

import pytest

from orion.transfer.v2.uncertainty_containment import (
    ContainmentStatus,
    ValidityState,
    assess_containment,
    build_validity_envelope,
)


def envelope(*, parent_digest: str | None = None):
    return build_validity_envelope(
        envelope_id="env:v1" if parent_digest is None else "env:v2",
        claim_id="claim:contain",
        subject_id="model:demo",
        context_states={
            "context:supported": ValidityState.SUPPORTED,
            "context:invalid": ValidityState.INVALID,
            "context:unknown": ValidityState.UNRESOLVED,
        },
        evidence_ids=("evidence:validity",),
        parent_envelope_digest=parent_digest,
    )


def test_supported_context_is_in_scope_but_not_truth_certificate() -> None:
    report = assess_containment(envelope(), context_id="context:supported")

    assert report.status is ContainmentStatus.IN_SCOPE
    assert report.establishes_model_correctness is False
    assert report.grants_scientific_authority is False
    assert report.rewrites_model is False


def test_invalid_context_is_blocked() -> None:
    report = assess_containment(envelope(), context_id="context:invalid")

    assert report.status is ContainmentStatus.BLOCKED


def test_unresolved_and_unregistered_contexts_fail_closed() -> None:
    unresolved = assess_containment(envelope(), context_id="context:unknown")
    missing = assess_containment(envelope(), context_id="context:not-registered")

    assert unresolved.status is ContainmentStatus.UNRESOLVED
    assert missing.status is ContainmentStatus.UNRESOLVED
    assert "CONTEXT_NOT_REGISTERED" in missing.reasons


def test_successor_envelope_links_parent_without_mutating_parent() -> None:
    first = envelope()
    successor = build_validity_envelope(
        envelope_id="env:v2",
        claim_id="claim:contain",
        subject_id="model:demo",
        context_states={"context:supported": ValidityState.INVALID},
        evidence_ids=("evidence:new",),
        parent_envelope_digest=first.digest,
    )

    assert successor.parent_envelope_digest == first.digest
    assert dict(first.context_states)["context:supported"] is ValidityState.SUPPORTED
    assert dict(successor.context_states)["context:supported"] is ValidityState.INVALID
    assert successor.digest != first.digest


def test_duplicate_context_entries_are_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate context"):
        build_validity_envelope(
            envelope_id="bad",
            claim_id="claim:contain",
            subject_id="model:demo",
            context_state_pairs=(
                ("context:x", ValidityState.SUPPORTED),
                ("context:x", ValidityState.INVALID),
            ),
        )
