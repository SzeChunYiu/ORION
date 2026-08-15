from __future__ import annotations

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
