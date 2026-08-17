"""Objective-revision state is append-only: old objectives are never overwritten."""
from __future__ import annotations

from dataclasses import replace

import pytest

from orion.goal_evolution.revision import (
    AuthorityProvenance,
    ObjectiveRevisionArchive,
    ObjectiveRevisionRecord,
    ObjectiveRevisionStatus,
    ObjectiveVersion,
    RevisionStatusEvent,
    append_status_event,
    append_version,
    current_status,
    empty_archive,
    register_revision,
)

_SHA_A = "a" * 64
_SHA_B = "b" * 64
_SHA_C = "c" * 64


def _host() -> AuthorityProvenance:
    return AuthorityProvenance(
        actor_id="host:goal-evolution",
        role="HOST",
        artifact_hash=_SHA_A,
    )


def _version(version_id: str = "obj:v1", definition: str = "maximize valid evidence coverage") -> ObjectiveVersion:
    return ObjectiveVersion(
        version_id=version_id,
        definition=definition,
        code_hash=_SHA_A if version_id.endswith("v1") else _SHA_B,
        constraints=("retain_false_merge_safety", "retain_integrity_check"),
        proxy_assumptions=("count_is_a_proxy_for_coverage",),
    )


def _record(
    *,
    revision_id: str = "rev:1",
    old_version_id: str = "obj:v1",
    new_version_id: str = "obj:v2",
) -> ObjectiveRevisionRecord:
    return ObjectiveRevisionRecord(
        revision_id=revision_id,
        old_version_id=old_version_id,
        new_version_id=new_version_id,
        mapping=(("coverage_count", "validated_coverage"),),
        scientific_intent_ref="intent:hidden:coverage-integrity",
        failure_observations=("proxy saturates without validity",),
        competing_responsibility_hypotheses=("OBJECTIVE", "IMPLEMENTATION"),
        frozen_discriminator_hash=_SHA_C,
        predicted_tradeoffs=("lower raw count, higher validity",),
        unchanged_protected_constraints=("retain_false_merge_safety", "retain_integrity_check"),
        authority_provenance=_host(),
    )


def test_archive_never_overwrites_an_old_objective_version() -> None:
    archive = append_version(empty_archive(), _version())
    first = archive.versions[0]
    with pytest.raises(ValueError, match="overwrite"):
        append_version(archive, replace(_version(), definition="rewritten in place", code_hash=_SHA_B))
    later = append_version(archive, _version("obj:v2", "maximize validated coverage"))
    assert later.versions[0] == first
    assert later.versions[0].definition == "maximize valid evidence coverage"
    assert [item.version_id for item in later.versions] == ["obj:v1", "obj:v2"]


def test_status_transitions_are_append_only_and_preserve_old_new_mapping() -> None:
    archive = append_version(empty_archive(), _version())
    archive = append_version(archive, _version("obj:v2", "maximize validated coverage"))
    archive = register_revision(archive, _record())
    assert current_status(archive, "rev:1") is ObjectiveRevisionStatus.PROPOSED
    archive = append_status_event(
        archive,
        RevisionStatusEvent(
            event_id="status:rev:1:admitted",
            revision_id="rev:1",
            status=ObjectiveRevisionStatus.ADMITTED_FOR_TEST,
            authority_provenance=_host(),
            reason="frozen for prospective test before protected outcomes",
        ),
    )
    archive = append_status_event(
        archive,
        RevisionStatusEvent(
            event_id="status:rev:1:rejected",
            revision_id="rev:1",
            status=ObjectiveRevisionStatus.REJECTED,
            authority_provenance=_host(),
            reason="protected compare unavailable or hostile",
        ),
    )
    assert current_status(archive, "rev:1") is ObjectiveRevisionStatus.REJECTED
    assert archive.records[0].mapping == (("coverage_count", "validated_coverage"),)
    assert archive.records[0].old_version_id == "obj:v1"
    assert archive.records[0].new_version_id == "obj:v2"
    assert len(archive.status_events) == 3
    with pytest.raises(ValueError, match="overwrite"):
        register_revision(archive, replace(_record(), frozen_discriminator_hash="d" * 64))


def test_candidate_cannot_author_revision_authority_provenance() -> None:
    with pytest.raises(ValueError, match="authority"):
        AuthorityProvenance(actor_id="candidate:1", role="CANDIDATE", artifact_hash=_SHA_A)
    record = _record()
    assert record.authority_provenance.role == "HOST"
    assert record.authority_provenance.authorizes_candidate_mutation is False


def test_retired_status_keeps_the_retired_objective_version() -> None:
    archive = append_version(empty_archive(), _version())
    archive = append_version(archive, _version("obj:v2", "maximize validated coverage"))
    archive = register_revision(archive, _record())
    archive = append_status_event(
        archive,
        RevisionStatusEvent(
            event_id="status:rev:1:retired-old",
            revision_id="rev:1",
            status=ObjectiveRevisionStatus.RETIRED,
            authority_provenance=_host(),
            reason="old operational objective retired after successor admission",
            subject_version_id="obj:v1",
        ),
    )
    assert archive.version("obj:v1").definition == "maximize valid evidence coverage"
    assert current_status(archive, "rev:1") is ObjectiveRevisionStatus.RETIRED
