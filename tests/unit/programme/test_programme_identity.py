"""Identity binding, and the cross-layer encoding contract with P5."""

from __future__ import annotations

from orion.programme.identity import (
    canonical_bytes,
    chain_link_digest,
    content_digest,
    is_sha256,
    seal,
    verify_seal,
)
from orion.study.p5.v2_evidence import canonical_bytes as p5_canonical_bytes
from orion.study.p5.v2_evidence import content_digest as p5_content_digest


def test_encoding_matches_p5_on_non_ascii_payloads() -> None:
    """The contract that makes a programme record chainable onto a P5 link.

    A non-ASCII payload is the discriminating case: the two encodings agree on
    pure ASCII and diverge the moment `ensure_ascii` differs.
    """

    payload = {"claim": "réplication à Lund", "note": "σ-algebra", "n": 3}
    assert canonical_bytes(payload) == p5_canonical_bytes(payload)
    assert content_digest(payload) == p5_content_digest(payload)


def test_seal_round_trips_and_detects_tampering() -> None:
    document = seal({"schema_version": "x.v1", "value": 1})
    assert is_sha256(document["content_digest"])
    assert verify_seal(document) == ()

    tampered = dict(document)
    tampered["value"] = 2
    assert "content_digest does not match document content" in verify_seal(tampered)


def test_seal_is_idempotent_in_value() -> None:
    once = seal({"a": 1})
    twice = seal(once)
    assert once == twice


def test_verify_seal_rejects_unexpected_identity() -> None:
    document = seal({"a": 1})
    other = seal({"a": 2})
    errors = verify_seal(document, expected_digest=other["content_digest"])
    assert "document identity mismatch against expected digest" in errors


def test_verify_seal_reports_missing_digest_rather_than_passing() -> None:
    assert verify_seal({"a": 1}) == ("content_digest must be a SHA-256 digest",)


def test_chain_link_digest_binds_to_its_predecessor() -> None:
    payload = {"event": "e-1"}
    first = chain_link_digest("0" * 64, payload)
    second = chain_link_digest("1" * 64, payload)
    assert first != second


def test_is_sha256_rejects_uppercase_and_short_values() -> None:
    assert not is_sha256("A" * 64)
    assert not is_sha256("a" * 63)
    assert not is_sha256(None)
