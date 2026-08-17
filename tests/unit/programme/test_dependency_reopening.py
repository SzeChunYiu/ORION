"""Typed invalidation, and the property that reopening never rewrites the past."""

from __future__ import annotations

from dataclasses import replace

from orion.core.closure import ClosureCertificate
from orion.programme.dependency import (
    DependencyEdge,
    InvalidationTrigger,
    Layer,
    ReopenEvent,
    affected_edges,
    apply_reopen,
    build_reopen_ledger,
    reopen_event_payload,
    validate_dependency_edge,
    validate_reopen_event,
    verify_reopen_ledger,
)
from orion.programme.identity import content_digest

PROTOCOL_DIGEST = content_digest({"protocol": "fixture"})


def _edge() -> DependencyEdge:
    return DependencyEdge(
        edge_id="edge-1",
        dependent_layer=Layer.OBJECT,
        dependent_record_id="obj-1",
        supports_layer=Layer.SEARCH_UNIVERSE,
        supports_record_id="uni-1",
        watched_coordinates=("W.ROUTE_KIND",),
        triggers=(InvalidationTrigger.NEW_ROUTE_DISCOVERED,),
    )


def _event(**overrides: object) -> ReopenEvent:
    base = {
        "event_id": "reopen-1",
        "trigger": InvalidationTrigger.NEW_ROUTE_DISCOVERED,
        "origin_layer": Layer.SEARCH_UNIVERSE,
        "origin_record_id": "uni-1",
        "changed_coordinates": ("W.ROUTE_KIND.registry",),
        "reason": "a registry route was found that W did not model",
        "epoch": 1,
        "superseded_record_digests": (content_digest({"record": "old"}),),
        "successor_record_digests": (content_digest({"record": "new"}),),
    }
    base.update(overrides)
    return ReopenEvent(**base)  # type: ignore[arg-type]


def test_well_formed_edge_and_event_validate() -> None:
    assert validate_dependency_edge(_edge()) == ()
    assert validate_reopen_event(_event()) == ()


def test_edge_fires_only_for_a_watched_coordinate_and_accepted_trigger() -> None:
    edges = (_edge(),)
    assert affected_edges(edges, _event()) == edges
    assert affected_edges(edges, _event(changed_coordinates=("K.CLAIM.obj-9",))) == ()
    assert affected_edges(
        edges, _event(trigger=InvalidationTrigger.METHOD_REVISION)
    ) == ()


def test_object_evidence_can_reopen_a_search_universe_closure() -> None:
    """Co-evolution runs in both directions, not only universe -> object."""

    edge = replace(
        _edge(),
        dependent_layer=Layer.SEARCH_UNIVERSE,
        dependent_record_id="uni-1",
        supports_layer=Layer.OBJECT,
        supports_record_id="obj-1",
        watched_coordinates=("K.CLAIM",),
        triggers=(InvalidationTrigger.NEW_OBJECT_EVIDENCE,),
    )
    event = _event(
        trigger=InvalidationTrigger.NEW_OBJECT_EVIDENCE,
        origin_layer=Layer.OBJECT,
        origin_record_id="obj-1",
        changed_coordinates=("K.CLAIM.obj-1",),
    )
    assert affected_edges((edge,), event) == (edge,)


def test_supersession_without_a_successor_is_deletion() -> None:
    errors = validate_reopen_event(_event(successor_record_digests=()))
    assert any("deletes knowledge" in error for error in errors)


def test_a_record_cannot_be_its_own_successor() -> None:
    same = content_digest({"record": "same"})
    errors = validate_reopen_event(
        _event(superseded_record_digests=(same,), successor_record_digests=(same,))
    )
    assert any("both superseded and" in error for error in errors)


def test_apply_reopen_leaves_prior_certificates_byte_identical() -> None:
    """Historical reproducibility is structural: invalidation returns a replacement."""

    certificate = ClosureCertificate(
        certificate_id="cert-1",
        scope="search-universe closure",
        dependency_coordinates=("W.ROUTE_KIND",),
    )
    before = content_digest(
        {
            "certificate_id": certificate.certificate_id,
            "scope": certificate.scope,
            "dependency_coordinates": list(certificate.dependency_coordinates),
            "stale": certificate.stale,
            "stale_reason": certificate.stale_reason,
        }
    )

    updated = apply_reopen((certificate,), _event())

    assert updated[0] is not certificate
    assert updated[0].stale is True
    assert certificate.stale is False
    after = content_digest(
        {
            "certificate_id": certificate.certificate_id,
            "scope": certificate.scope,
            "dependency_coordinates": list(certificate.dependency_coordinates),
            "stale": certificate.stale,
            "stale_reason": certificate.stale_reason,
        }
    )
    assert after == before


def test_apply_reopen_leaves_unrelated_certificates_untouched() -> None:
    unrelated = ClosureCertificate(
        certificate_id="cert-2",
        scope="method closure",
        dependency_coordinates=("M.METHOD.m-a",),
    )
    assert apply_reopen((unrelated,), _event()) == (unrelated,)


def test_reopen_ledger_verifies_against_its_frozen_hash() -> None:
    events = (_event(), _event(event_id="reopen-2", epoch=2))
    document = build_reopen_ledger("prog-1", PROTOCOL_DIGEST, events)
    errors = verify_reopen_ledger(
        document,
        "prog-1",
        PROTOCOL_DIGEST,
        events,
        expected_document_hash=document["content_digest"],
    )
    assert errors == ()


def test_reopen_ledger_detects_a_reordered_event() -> None:
    events = (_event(), _event(event_id="reopen-2", epoch=2))
    document = build_reopen_ledger("prog-1", PROTOCOL_DIGEST, events)
    errors = verify_reopen_ledger(
        document,
        "prog-1",
        PROTOCOL_DIGEST,
        tuple(reversed(events)),
        expected_document_hash=document["content_digest"],
    )
    assert errors != ()


def test_reopen_ledger_detects_an_edited_event_body() -> None:
    events = (_event(),)
    document = build_reopen_ledger("prog-1", PROTOCOL_DIGEST, events)
    document["links"][0]["event"] = reopen_event_payload(_event(reason="a softer reason"))
    errors = verify_reopen_ledger(
        document,
        "prog-1",
        PROTOCOL_DIGEST,
        events,
        expected_document_hash=document["content_digest"],
    )
    assert errors != ()


def test_reopen_ledger_rejects_a_dropped_event() -> None:
    events = (_event(), _event(event_id="reopen-2", epoch=2))
    document = build_reopen_ledger("prog-1", PROTOCOL_DIGEST, events)
    errors = verify_reopen_ledger(
        document,
        "prog-1",
        PROTOCOL_DIGEST,
        events[:1],
        expected_document_hash=document["content_digest"],
    )
    assert any("link count" in error for error in errors)
