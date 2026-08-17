"""Content and lineage binding for Phase-4 programme records.

Encoding contract
-----------------
``canonical_bytes`` here must produce the same bytes as
``orion.study.p5.v2_evidence.canonical_bytes`` — including ``ensure_ascii=False``.
This is a correctness requirement, not a style preference: a programme record
whose digest is computed under a different JSON encoding can never chain onto a
P5 negative-history link, and the divergence would only surface on the first
record carrying a non-ASCII character.

The relationship is expressed as a *test*
(``tests/unit/programme/test_programme_identity.py``)
rather than an import, because ``orion.programme`` sits above ``orion.study.p5``
in the layering ``development/README.md`` mandates, and an upward import would
invert it. A pinning test also fails loudly if either side drifts, which a shared
import would not.

Known repo defect (not fixed here, additive-files rule): three ``canonical_bytes``
definitions exist (``study/p2/corpus.py``, ``study/p5/v2_evidence.py``,
``kernel/store.py``) and they do **not** agree — the kernel copy leaves
``ensure_ascii`` at its default ``True``. Anything hashed with the kernel copy
cannot chain onto a P5 record.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from hashlib import sha256
from typing import Any

PROGRAMME_SCHEMA_NAMESPACE = "orion.programme"

PROTOCOL_SCHEMA = f"{PROGRAMME_SCHEMA_NAMESPACE}.protocol.v1"
OBJECT_KNOWLEDGE_SCHEMA = f"{PROGRAMME_SCHEMA_NAMESPACE}.object-knowledge.v1"
SEARCH_UNIVERSE_KNOWLEDGE_SCHEMA = f"{PROGRAMME_SCHEMA_NAMESPACE}.search-universe-knowledge.v1"
METHOD_KNOWLEDGE_SCHEMA = f"{PROGRAMME_SCHEMA_NAMESPACE}.method-knowledge.v1"
DEPENDENCY_EDGE_SCHEMA = f"{PROGRAMME_SCHEMA_NAMESPACE}.dependency-edge.v1"
REOPEN_EVENT_SCHEMA = f"{PROGRAMME_SCHEMA_NAMESPACE}.reopen-event.v1"
REOPEN_LEDGER_SCHEMA = f"{PROGRAMME_SCHEMA_NAMESPACE}.reopen-ledger.v1"
REOPEN_GENESIS_SCHEMA = f"{PROGRAMME_SCHEMA_NAMESPACE}.reopen-genesis.v1"
HOSTILE_CHECK_REPORT_SCHEMA = f"{PROGRAMME_SCHEMA_NAMESPACE}.hostile-check-report.v1"

_HEX = frozenset("0123456789abcdef")

_DIGEST_FIELD = "content_digest"


def canonical_bytes(payload: Any) -> bytes:
    """Encode a payload as canonical JSON. Byte-compatible with P5 (see module docstring)."""

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def content_digest(payload: Any) -> str:
    """Return the SHA-256 of a payload's canonical encoding."""

    return sha256(canonical_bytes(payload)).hexdigest()


def is_sha256(value: object) -> bool:
    """True only for a lower-case 64-character hexadecimal digest."""

    return (
        isinstance(value, str)
        and len(value) == 64
        and value == value.lower()
        and all(character in _HEX for character in value)
    )


def seal(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return a copy of ``payload`` carrying its own content digest.

    The digest is computed over the payload *without* the digest field, so a
    sealed document can be re-verified by removing one key. Sealing an already
    sealed payload is idempotent in value, not in provenance: the caller is
    responsible for not re-sealing a document it has mutated in place.
    """

    unsealed = {key: value for key, value in payload.items() if key != _DIGEST_FIELD}
    sealed = dict(unsealed)
    sealed[_DIGEST_FIELD] = content_digest(unsealed)
    return sealed


def verify_seal(
    document: Mapping[str, Any],
    *,
    expected_digest: str | None = None,
) -> tuple[str, ...]:
    """Return deduplicated errors for a sealed document. Empty tuple means intact."""

    errors: list[str] = []
    if not isinstance(document, Mapping):
        return ("sealed document must be a mapping",)

    claimed = document.get(_DIGEST_FIELD)
    if not is_sha256(claimed):
        errors.append("content_digest must be a SHA-256 digest")
    else:
        unsealed = {key: value for key, value in document.items() if key != _DIGEST_FIELD}
        if claimed != content_digest(unsealed):
            errors.append("content_digest does not match document content")

    if expected_digest is not None:
        if not is_sha256(expected_digest):
            errors.append("expected digest must be a SHA-256 digest")
        elif claimed != expected_digest:
            errors.append("document identity mismatch against expected digest")

    return tuple(dict.fromkeys(errors))


def chain_link_digest(previous_digest: str, payload: Mapping[str, Any]) -> str:
    """Bind one payload to its predecessor, giving an append-only lineage."""

    return content_digest({"previous": previous_digest, "payload": dict(payload)})


__all__ = [
    "DEPENDENCY_EDGE_SCHEMA",
    "HOSTILE_CHECK_REPORT_SCHEMA",
    "METHOD_KNOWLEDGE_SCHEMA",
    "OBJECT_KNOWLEDGE_SCHEMA",
    "PROGRAMME_SCHEMA_NAMESPACE",
    "PROTOCOL_SCHEMA",
    "REOPEN_EVENT_SCHEMA",
    "REOPEN_GENESIS_SCHEMA",
    "REOPEN_LEDGER_SCHEMA",
    "SEARCH_UNIVERSE_KNOWLEDGE_SCHEMA",
    "canonical_bytes",
    "chain_link_digest",
    "content_digest",
    "is_sha256",
    "seal",
    "verify_seal",
]
