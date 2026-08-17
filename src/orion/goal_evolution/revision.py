"""Append-only objective versions and revision status. Old objectives are never overwritten."""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum


_HEX = frozenset("0123456789abcdef")
_HOST_ROLES = frozenset({"HOST", "DISCRIMINATOR"})


def _text(value: str, field: str) -> None:
    if not value.strip():
        raise ValueError(f"{field} is required")


def _sha(value: str, field: str) -> None:
    if len(value) != 64 or any(character not in _HEX for character in value):
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")


class ObjectiveRevisionStatus(str, Enum):
    PROPOSED = "PROPOSED"
    REJECTED = "REJECTED"
    ADMITTED_FOR_TEST = "ADMITTED_FOR_TEST"
    RETIRED = "RETIRED"


class ResponsibilityClass(str, Enum):
    OBJECTIVE = "OBJECTIVE"
    MEASUREMENT_SPECIFICATION = "MEASUREMENT_SPECIFICATION"
    IMPLEMENTATION = "IMPLEMENTATION"
    METHOD = "METHOD"
    ENVIRONMENT = "ENVIRONMENT"
    EVALUATOR = "EVALUATOR"
    UNRESOLVED = "UNRESOLVED"


PROPOSAL_LEGAL_RESPONSIBILITIES = frozenset(
    {ResponsibilityClass.OBJECTIVE, ResponsibilityClass.MEASUREMENT_SPECIFICATION}
)


@dataclass(frozen=True)
class AuthorityProvenance:
    actor_id: str
    role: str
    artifact_hash: str

    def __post_init__(self) -> None:
        _text(self.actor_id, "actor_id")
        _text(self.role, "role")
        _sha(self.artifact_hash, "artifact_hash")
        if self.role not in _HOST_ROLES:
            raise ValueError("authority provenance cannot be candidate-authored")

    @property
    def authorizes_candidate_mutation(self) -> bool:
        return False


@dataclass(frozen=True)
class ObjectiveVersion:
    version_id: str
    definition: str
    code_hash: str
    constraints: tuple[str, ...]
    proxy_assumptions: tuple[str, ...]

    def __post_init__(self) -> None:
        _text(self.version_id, "version_id")
        _text(self.definition, "definition")
        _sha(self.code_hash, "code_hash")
        if not self.constraints:
            raise ValueError("objective version requires protected constraints")


@dataclass(frozen=True)
class ObjectiveRevisionRecord:
    revision_id: str
    old_version_id: str
    new_version_id: str
    mapping: tuple[tuple[str, str], ...]
    scientific_intent_ref: str
    failure_observations: tuple[str, ...]
    competing_responsibility_hypotheses: tuple[str, ...]
    frozen_discriminator_hash: str
    predicted_tradeoffs: tuple[str, ...]
    unchanged_protected_constraints: tuple[str, ...]
    authority_provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.revision_id, "revision_id")
        _text(self.old_version_id, "old_version_id")
        _text(self.new_version_id, "new_version_id")
        _text(self.scientific_intent_ref, "scientific_intent_ref")
        _sha(self.frozen_discriminator_hash, "frozen_discriminator_hash")
        if self.old_version_id == self.new_version_id:
            raise ValueError("revision must map an old objective onto a distinct new objective")
        if not self.mapping:
            raise ValueError("old/new objective mapping is required")
        if not self.unchanged_protected_constraints:
            raise ValueError("protected constraints must remain explicit")
        if self.authority_provenance.authorizes_candidate_mutation:
            raise ValueError("authority provenance cannot authorize candidate mutation")


@dataclass(frozen=True)
class RevisionStatusEvent:
    event_id: str
    revision_id: str
    status: ObjectiveRevisionStatus
    authority_provenance: AuthorityProvenance
    reason: str
    subject_version_id: str = ""

    def __post_init__(self) -> None:
        _text(self.event_id, "event_id")
        _text(self.revision_id, "revision_id")
        _text(self.reason, "reason")
        if self.authority_provenance.authorizes_candidate_mutation:
            raise ValueError("authority provenance cannot authorize candidate mutation")


@dataclass(frozen=True)
class ObjectiveRevisionArchive:
    versions: tuple[ObjectiveVersion, ...]
    records: tuple[ObjectiveRevisionRecord, ...]
    status_events: tuple[RevisionStatusEvent, ...]
    current_operational_version_id: str = ""

    def version(self, version_id: str) -> ObjectiveVersion:
        for item in self.versions:
            if item.version_id == version_id:
                return item
        raise KeyError(version_id)


def empty_archive() -> ObjectiveRevisionArchive:
    return ObjectiveRevisionArchive((), (), (), "")


def append_version(
    archive: ObjectiveRevisionArchive, version: ObjectiveVersion
) -> ObjectiveRevisionArchive:
    if any(item.version_id == version.version_id for item in archive.versions):
        raise ValueError("overwrite: objective versions are append-only")
    current = archive.current_operational_version_id or version.version_id
    return ObjectiveRevisionArchive(
        archive.versions + (version,),
        archive.records,
        archive.status_events,
        current,
    )


def register_revision(
    archive: ObjectiveRevisionArchive, record: ObjectiveRevisionRecord
) -> ObjectiveRevisionArchive:
    if any(item.revision_id == record.revision_id for item in archive.records):
        raise ValueError("overwrite: revision records are append-only")
    archive.version(record.old_version_id)
    archive.version(record.new_version_id)
    proposed = RevisionStatusEvent(
        event_id=f"status:{record.revision_id}:proposed",
        revision_id=record.revision_id,
        status=ObjectiveRevisionStatus.PROPOSED,
        authority_provenance=record.authority_provenance,
        reason="objective revision proposed under host authority",
    )
    return ObjectiveRevisionArchive(
        archive.versions,
        archive.records + (record,),
        archive.status_events + (proposed,),
        archive.current_operational_version_id,
    )


def append_status_event(
    archive: ObjectiveRevisionArchive, event: RevisionStatusEvent
) -> ObjectiveRevisionArchive:
    if any(item.event_id == event.event_id for item in archive.status_events):
        raise ValueError("overwrite: revision status events are append-only")
    if all(item.revision_id != event.revision_id for item in archive.records):
        raise ValueError("status event references an unknown revision")
    return ObjectiveRevisionArchive(
        archive.versions,
        archive.records,
        archive.status_events + (event,),
        archive.current_operational_version_id,
    )


def current_status(archive: ObjectiveRevisionArchive, revision_id: str) -> ObjectiveRevisionStatus:
    events = tuple(item for item in archive.status_events if item.revision_id == revision_id)
    if not events:
        raise KeyError(revision_id)
    return events[-1].status


def with_current_operational_version(
    archive: ObjectiveRevisionArchive, version_id: str
) -> ObjectiveRevisionArchive:
    archive.version(version_id)
    return replace(archive, current_operational_version_id=version_id)
