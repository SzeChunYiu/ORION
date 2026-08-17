"""Step 2: typed dependency invalidation and auditable reopening.

The mechanism already exists in miniature. ``orion.core.closure.ClosureCertificate``
carries ``dependency_coordinates`` and an ``invalidate(reason)`` that returns a
*new* frozen certificate via ``dataclasses.replace`` — reopening therefore cannot
rewrite the prior certificate, because it never touches it. This module makes
that property explicit, types the trigger, and records the reopening in an
append-only ledger built the same way as
``orion.study.p5.negative_history_chain`` (genesis digest, per-link predecessor
binding, sealed document hash).

The invariant worth stating plainly: a reopen event only ever *adds*. It marks
prior record digests superseded and names successors; it never edits a
superseded record, and the ledger keeps the superseded digest forever, so any
historical state remains reconstructible after any number of reopenings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from orion.core.closure import ClosureCertificate
from orion.programme.coordinates import coordinate_errors, covers
from orion.programme.identity import (
    DEPENDENCY_EDGE_SCHEMA,
    REOPEN_EVENT_SCHEMA,
    REOPEN_GENESIS_SCHEMA,
    REOPEN_LEDGER_SCHEMA,
    chain_link_digest,
    content_digest,
    is_sha256,
    seal,
    verify_seal,
)
from orion.programme.records import dedup, required_text_errors


class Layer(str, Enum):
    OBJECT = "OBJECT"
    SEARCH_UNIVERSE = "SEARCH_UNIVERSE"
    METHOD = "METHOD"


class InvalidationTrigger(str, Enum):
    """Why a reopening happened. Untyped reopening is indistinguishable from drift."""

    NEW_OBJECT_EVIDENCE = "NEW_OBJECT_EVIDENCE"
    CONTRADICTING_OBJECT_CLAIM = "CONTRADICTING_OBJECT_CLAIM"
    NEW_DOMAIN_DISCOVERED = "NEW_DOMAIN_DISCOVERED"
    NEW_ROUTE_DISCOVERED = "NEW_ROUTE_DISCOVERED"
    NEW_REPRESENTATION_DISCOVERED = "NEW_REPRESENTATION_DISCOVERED"
    BLIND_SPOT_FOUND = "BLIND_SPOT_FOUND"
    METHOD_REVISION = "METHOD_REVISION"
    METHOD_APPLICABILITY_VIOLATED = "METHOD_APPLICABILITY_VIOLATED"
    SOURCE_VERSION_CHANGED = "SOURCE_VERSION_CHANGED"
    EVALUATOR_REVISION = "EVALUATOR_REVISION"
    NEGATIVE_HISTORY_ADDITION = "NEGATIVE_HISTORY_ADDITION"
    EXTERNAL_AUTHORITY_DIRECTIVE = "EXTERNAL_AUTHORITY_DIRECTIVE"


@dataclass(frozen=True)
class DependencyEdge:
    """``dependent`` is only as settled as ``supports``.

    Co-evolution is the point: edges run in every direction between the three
    layers, so an object finding can unsettle a search closure and a method
    revision can unsettle an object claim.
    """

    edge_id: str
    dependent_layer: Layer
    dependent_record_id: str
    supports_layer: Layer
    supports_record_id: str
    watched_coordinates: tuple[str, ...]
    triggers: tuple[InvalidationTrigger, ...]

    def observes(self, coordinate: str) -> bool:
        return any(covers(watched, coordinate) for watched in self.watched_coordinates)


@dataclass(frozen=True)
class ReopenEvent:
    """One typed, auditable reopening.

    ``superseded_record_digests`` and ``successor_record_digests`` must be
    disjoint. Overlap would mean a record is its own successor, which is the
    signature of an in-place edit dressed as a reopening.
    """

    event_id: str
    trigger: InvalidationTrigger
    origin_layer: Layer
    origin_record_id: str
    changed_coordinates: tuple[str, ...]
    reason: str
    epoch: int
    superseded_record_digests: tuple[str, ...] = ()
    successor_record_digests: tuple[str, ...] = ()
    invalidated_certificate_ids: tuple[str, ...] = ()
    prior_state_digest: str | None = None
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)


def dependency_edge_payload(edge: DependencyEdge) -> dict[str, Any]:
    return seal(
        {
            "schema_version": DEPENDENCY_EDGE_SCHEMA,
            "edge_id": edge.edge_id,
            "dependent_layer": edge.dependent_layer.value,
            "dependent_record_id": edge.dependent_record_id,
            "supports_layer": edge.supports_layer.value,
            "supports_record_id": edge.supports_record_id,
            "watched_coordinates": list(edge.watched_coordinates),
            "triggers": [item.value for item in edge.triggers],
        }
    )


def reopen_event_payload(event: ReopenEvent) -> dict[str, Any]:
    return seal(
        {
            "schema_version": REOPEN_EVENT_SCHEMA,
            "event_id": event.event_id,
            "trigger": event.trigger.value,
            "origin_layer": event.origin_layer.value,
            "origin_record_id": event.origin_record_id,
            "changed_coordinates": list(event.changed_coordinates),
            "reason": event.reason,
            "epoch": event.epoch,
            "superseded_record_digests": list(event.superseded_record_digests),
            "successor_record_digests": list(event.successor_record_digests),
            "invalidated_certificate_ids": list(event.invalidated_certificate_ids),
            "prior_state_digest": event.prior_state_digest,
            "metadata": [list(pair) for pair in event.metadata],
        }
    )


def validate_dependency_edge(edge: DependencyEdge) -> tuple[str, ...]:
    errors: list[str] = []
    errors.extend(required_text_errors(edge.edge_id, "edge_id"))
    errors.extend(required_text_errors(edge.dependent_record_id, "dependent_record_id"))
    errors.extend(required_text_errors(edge.supports_record_id, "supports_record_id"))
    errors.extend(coordinate_errors(edge.watched_coordinates, "watched_coordinates"))
    if not edge.triggers:
        errors.append("an edge with no trigger can never fire")
    if (
        edge.dependent_layer is edge.supports_layer
        and edge.dependent_record_id == edge.supports_record_id
    ):
        errors.append("a record cannot depend on itself")
    return dedup(errors)


def validate_reopen_event(event: ReopenEvent) -> tuple[str, ...]:
    errors: list[str] = []
    errors.extend(required_text_errors(event.event_id, "event_id"))
    errors.extend(required_text_errors(event.origin_record_id, "origin_record_id"))
    errors.extend(required_text_errors(event.reason, "reason"))
    errors.extend(coordinate_errors(event.changed_coordinates, "changed_coordinates"))
    if event.epoch < 0:
        errors.append("epoch must be non-negative")

    digests = (*event.superseded_record_digests, *event.successor_record_digests)
    if any(not is_sha256(value) for value in digests):
        errors.append("superseded and successor record digests must be SHA-256")
    overlap = set(event.superseded_record_digests) & set(event.successor_record_digests)
    if overlap:
        errors.append(
            "a reopen event cannot list the same digest as both superseded and"
            f" successor: {sorted(overlap)}"
        )
    if event.superseded_record_digests and not event.successor_record_digests:
        errors.append(
            "a reopen event that supersedes records without naming successors"
            " deletes knowledge instead of reopening it"
        )
    if event.prior_state_digest is not None and not is_sha256(event.prior_state_digest):
        errors.append("prior_state_digest must be SHA-256")
    return dedup(errors)


def affected_edges(
    edges: tuple[DependencyEdge, ...],
    event: ReopenEvent,
) -> tuple[DependencyEdge, ...]:
    """Edges that both watch a changed coordinate and accept this trigger."""

    return tuple(
        edge
        for edge in edges
        if event.trigger in edge.triggers
        and any(edge.observes(coordinate) for coordinate in event.changed_coordinates)
    )


def apply_reopen(
    certificates: tuple[ClosureCertificate, ...],
    event: ReopenEvent,
) -> tuple[ClosureCertificate, ...]:
    """Return a new certificate tuple with affected certificates marked stale.

    The input certificates are never mutated: ``ClosureCertificate.invalidate``
    returns a replacement. That is what makes historical reproducibility a
    structural property here rather than a discipline.
    """

    reason = f"{event.trigger.value}:{event.event_id}"
    updated: list[ClosureCertificate] = []
    for certificate in certificates:
        touched = any(
            covers(watched, coordinate)
            for watched in certificate.dependency_coordinates
            for coordinate in event.changed_coordinates
        )
        named = certificate.certificate_id in event.invalidated_certificate_ids
        if (touched or named) and not certificate.stale:
            updated.append(certificate.invalidate(reason))
        else:
            updated.append(certificate)
    return tuple(updated)


def reopen_genesis(programme_id: str, protocol_digest: str) -> str:
    return content_digest(
        {
            "schema": REOPEN_GENESIS_SCHEMA,
            "programme_id": programme_id,
            "protocol_digest": protocol_digest,
        }
    )


def build_reopen_ledger(
    programme_id: str,
    protocol_digest: str,
    events: tuple[ReopenEvent, ...],
) -> dict[str, Any]:
    """Build the append-only reopening transcript.

    Deterministic, but determinism is not authority: the document is only
    admissible once an external host has frozen its hash and supplies that hash
    back to :func:`verify_reopen_ledger`.
    """

    genesis = reopen_genesis(programme_id, protocol_digest)
    tip = genesis
    links: list[dict[str, Any]] = []
    for sequence, event in enumerate(events):
        payload = {
            "sequence": sequence,
            "event": reopen_event_payload(event),
        }
        link_hash = chain_link_digest(tip, payload)
        links.append({**payload, "previous_chain_hash": tip, "link_hash": link_hash})
        tip = link_hash

    return seal(
        {
            "schema_version": REOPEN_LEDGER_SCHEMA,
            "programme_id": programme_id,
            "protocol_digest": protocol_digest,
            "genesis_hash": genesis,
            "links": links,
            "final_chain_hash": tip,
        }
    )


def verify_reopen_ledger(
    document: dict[str, Any],
    programme_id: str,
    protocol_digest: str,
    events: tuple[ReopenEvent, ...],
    *,
    expected_document_hash: str,
) -> tuple[str, ...]:
    """Return deduplicated errors. An empty tuple means the transcript verifies."""

    errors: list[str] = list(verify_seal(document, expected_digest=expected_document_hash))
    if document.get("schema_version") != REOPEN_LEDGER_SCHEMA:
        errors.append("wrong reopen ledger schema_version")
    if document.get("programme_id") != programme_id:
        errors.append("reopen ledger programme_id mismatch")
    if document.get("protocol_digest") != protocol_digest:
        errors.append("reopen ledger protocol_digest mismatch")

    expected_genesis = reopen_genesis(programme_id, protocol_digest)
    if document.get("genesis_hash") != expected_genesis:
        errors.append("reopen ledger genesis mismatch")

    links = document.get("links")
    if not isinstance(links, list):
        errors.append("reopen ledger links must be a list")
        links = []
    if len(links) != len(events):
        errors.append("reopen ledger link count does not match event count")

    tip = expected_genesis
    for sequence, (event, link) in enumerate(zip(events, links)):
        if not isinstance(link, dict):
            errors.append(f"reopen link {sequence} must be an object")
            continue
        payload = {"sequence": sequence, "event": reopen_event_payload(event)}
        if link.get("previous_chain_hash") != tip:
            errors.append(f"reopen link {sequence} predecessor mismatch")
        if link.get("event") != payload["event"]:
            errors.append(f"reopen link {sequence} event content mismatch")
        expected_link_hash = chain_link_digest(tip, payload)
        if link.get("link_hash") != expected_link_hash:
            errors.append(f"reopen link {sequence} hash mismatch")
        tip = expected_link_hash

    if document.get("final_chain_hash") != tip:
        errors.append("reopen ledger final chain hash mismatch")
    return dedup(errors)


__all__ = [
    "DependencyEdge",
    "InvalidationTrigger",
    "Layer",
    "ReopenEvent",
    "affected_edges",
    "apply_reopen",
    "build_reopen_ledger",
    "dependency_edge_payload",
    "reopen_event_payload",
    "reopen_genesis",
    "validate_dependency_edge",
    "validate_reopen_event",
    "verify_reopen_ledger",
]
