from __future__ import annotations

import hashlib
import json
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
