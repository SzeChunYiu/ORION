"""Object-knowledge layer: what the programme claims about its research object.

Extends ``orion.core.claims.ClaimRecord`` and ``orion.core.evidence.EvidenceRecord``
rather than replacing them. A ``ClaimRecord`` carries claim text, evidence ids,
authority, contradictions; what it does not carry is the version of the source
the evidence came from, nor the coordinates the claim depends on. Those two
absences are the two Phase-4 failure modes — silent source substitution, and a
claim that survives the invalidation of its own basis — so this record adds
exactly them and reuses the rest.

Plural views are represented, not resolved. Two records may share a
``view_group_id`` while contradicting one another; neither is deleted, and
neither may be ``VERIFIED`` without a resolution certificate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from orion.programme.coordinates import coordinate_errors
from orion.programme.identity import OBJECT_KNOWLEDGE_SCHEMA, is_sha256, seal
from orion.programme.records import (
    ObjectAuthority,
    ProvenanceBinding,
    dedup,
    required_ids_errors,
    required_text_errors,
)


@dataclass(frozen=True)
class ObjectKnowledgeRecord:
    """One versioned claim about one referent, bound to its provenance and dependencies."""

    object_id: str
    referent_id: str
    claim_id: str
    claim_text: str
    record_version: int
    evidence_ids: tuple[str, ...]
    provenance: tuple[ProvenanceBinding, ...]
    depends_on_coordinates: tuple[str, ...]
    authority: ObjectAuthority = ObjectAuthority.OPEN
    view_group_id: str | None = None
    contradicts_object_ids: tuple[str, ...] = ()
    resolution_certificate_id: str | None = None
    measurement_ids: tuple[str, ...] = ()
    method_record_ids: tuple[str, ...] = ()
    search_universe_record_id: str | None = None
    open_residual_ids: tuple[str, ...] = ()
    uncertainty_note: str = ""
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.record_version < 1:
            raise ValueError("object record_version starts at 1")


def object_knowledge_payload(record: ObjectKnowledgeRecord) -> dict[str, Any]:
    """Serialize one record to the sealed wire form."""

    return seal(
        {
            "schema_version": OBJECT_KNOWLEDGE_SCHEMA,
            "object_id": record.object_id,
            "referent_id": record.referent_id,
            "claim_id": record.claim_id,
            "claim_text": record.claim_text,
            "record_version": record.record_version,
            "authority": record.authority.value,
            "evidence_ids": list(record.evidence_ids),
            "provenance": [
                {
                    "source_id": binding.source_id,
                    "source_uri": binding.source_uri,
                    "source_family": binding.source_family,
                    "source_version": binding.source_version,
                    "content_sha256": binding.content_sha256,
                    "retrieved_at_epoch": binding.retrieved_at_epoch,
                }
                for binding in record.provenance
            ],
            "depends_on_coordinates": list(record.depends_on_coordinates),
            "view_group_id": record.view_group_id,
            "contradicts_object_ids": list(record.contradicts_object_ids),
            "resolution_certificate_id": record.resolution_certificate_id,
            "measurement_ids": list(record.measurement_ids),
            "method_record_ids": list(record.method_record_ids),
            "search_universe_record_id": record.search_universe_record_id,
            "open_residual_ids": list(record.open_residual_ids),
            "uncertainty_note": record.uncertainty_note,
            "metadata": [list(pair) for pair in record.metadata],
        }
    )


def validate_object_knowledge_record(record: ObjectKnowledgeRecord) -> tuple[str, ...]:
    """Return deduplicated blockers. An empty tuple means the record is admissible.

    Admissible is not the same as true: this validator checks that the record is
    *bindable and invalidatable*, never that its claim holds.
    """

    errors: list[str] = []
    errors.extend(required_text_errors(record.object_id, "object_id"))
    errors.extend(required_text_errors(record.referent_id, "referent_id"))
    errors.extend(required_text_errors(record.claim_id, "claim_id"))
    errors.extend(required_text_errors(record.claim_text, "claim_text"))
    errors.extend(coordinate_errors(record.depends_on_coordinates, "depends_on_coordinates"))

    if record.authority is ObjectAuthority.OPEN:
        # An open claim is allowed to carry no evidence: that is what open means.
        pass
    else:
        errors.extend(required_ids_errors(record.evidence_ids, "evidence_ids"))
        if not record.provenance:
            errors.append("a claim above OPEN requires at least one provenance binding")

    bound_hashes = {binding.content_sha256 for binding in record.provenance}
    if any(not is_sha256(value) for value in bound_hashes):
        errors.append("every provenance binding must carry a SHA-256 content hash")

    if record.authority is ObjectAuthority.VERIFIED:
        if record.contradicts_object_ids and not record.resolution_certificate_id:
            errors.append(
                "a VERIFIED claim that contradicts another claim requires a"
                " resolution certificate; plural views are not resolved by fiat"
            )
        if record.open_residual_ids:
            errors.append("a VERIFIED claim cannot carry open residuals")
        if record.search_universe_record_id is None:
            errors.append(
                "a VERIFIED claim must name the search-universe record it was"
                " verified under, or its closure cannot be reopened"
            )

    if record.contradicts_object_ids and record.view_group_id is None:
        errors.append("contradicting records must share an explicit view_group_id")

    if record.object_id in record.contradicts_object_ids:
        errors.append("a record cannot contradict itself")

    return dedup(errors)


def validate_object_knowledge_layer(
    records: tuple[ObjectKnowledgeRecord, ...],
) -> tuple[str, ...]:
    """Cross-record checks: identity uniqueness and symmetric contradiction."""

    errors: list[str] = []
    for record in records:
        errors.extend(f"{record.object_id}: {error}" for error in
                      validate_object_knowledge_record(record))

    seen: set[tuple[str, int]] = set()
    for record in records:
        key = (record.object_id, record.record_version)
        if key in seen:
            errors.append(f"duplicate object record identity {key}")
        seen.add(key)

    by_id = {record.object_id: record for record in records}
    for record in records:
        for other_id in record.contradicts_object_ids:
            other = by_id.get(other_id)
            if other is None:
                errors.append(
                    f"{record.object_id}: contradicts unknown record {other_id!r}"
                )
                continue
            if record.object_id not in other.contradicts_object_ids:
                errors.append(
                    f"{record.object_id}: contradiction with {other_id} is not mutual;"
                    " a one-sided contradiction hides the losing view"
                )

    return dedup(errors)


__all__ = [
    "ObjectKnowledgeRecord",
    "object_knowledge_payload",
    "validate_object_knowledge_layer",
    "validate_object_knowledge_record",
]
