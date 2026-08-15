from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceRecord:
    """Immutable source material retained with provenance."""

    evidence_id: str
    content: str
    source_uri: str
    domain_ids: tuple[str, ...] = ()
    certificate_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.evidence_id.strip():
            raise ValueError("evidence_id is required")
        if not self.content.strip():
            raise ValueError("evidence content is required")
        if not self.source_uri.strip():
            raise ValueError("source_uri is required")


def evidence_record_fingerprint(record: EvidenceRecord) -> str:
    """Return a canonical content-and-provenance binding for one evidence record."""

    payload = {
        "evidence_id": record.evidence_id,
        "content": record.content,
        "source_uri": record.source_uri,
        "domain_ids": list(record.domain_ids),
        "certificate_ids": list(record.certificate_ids),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def normalized_content(text: str) -> str:
    """Collapse presentation differences that are not content differences."""

    return " ".join(unicodedata.normalize("NFKC", text).split())


def content_fingerprint(record: EvidenceRecord) -> str:
    """Return a digest of an evidence record's content alone.

    Deliberately a sibling of `evidence_record_fingerprint` rather than a
    replacement: that function binds identity and provenance *into* the hash,
    which is correct when the question is "is this the same record", and wrong
    when the question is "have I already read this". Two mirrors of one paper
    carry different `evidence_id` and `source_uri`, so the provenance-bound
    fingerprint reports them as distinct material — and a novelty signal built
    on it can never fall to zero against a live source that re-mints
    identifiers.
    """

    return hashlib.sha256(normalized_content(record.content).encode("utf-8")).hexdigest()
