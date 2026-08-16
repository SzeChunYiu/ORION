from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from orion.core.evidence import EvidenceRecord, content_fingerprint
from orion.kernel.store import LedgerStore

from .identity import ReadDecision, ReadReceipt, SourceIdentity, canonical_source_id
from .ledger import decide_read_from_ledger, record_read, record_source
from .providers.arxiv import ArxivRecord


@dataclass(frozen=True)
class IngestOutcome:
    """What happened to one retrieved record."""

    source_id: str
    decision: ReadDecision
    content_digest: str

    @property
    def read(self) -> bool:
        return self.decision is not ReadDecision.ALREADY_READ


@dataclass(frozen=True)
class IngestReport:
    """The result of offering a batch of retrieved records to the ledger."""

    outcomes: tuple[IngestOutcome, ...] = field(default_factory=tuple)

    @property
    def ingested(self) -> tuple[IngestOutcome, ...]:
        return tuple(item for item in self.outcomes if item.read)

    @property
    def skipped(self) -> tuple[IngestOutcome, ...]:
        return tuple(item for item in self.outcomes if not item.read)

    def counts(self) -> dict[str, int]:
        tally: dict[str, int] = {}
        for item in self.outcomes:
            tally[item.decision.value] = tally.get(item.decision.value, 0) + 1
        return tally


def content_digest(
    *,
    source_id: str,
    content: str,
) -> str:
    """Content-address one retrieval rendition independently of fetch metadata."""

    return content_fingerprint(
        EvidenceRecord(
            evidence_id=source_id,
            content=content or source_id,
            source_uri=source_id,
        )
    )


def ingest_document(
    store: LedgerStore,
    *,
    source_id: str,
    content: str,
    title: str = "",
    aliases: tuple[str, ...] = (),
    schema_version: str,
    frame_id: str,
) -> IngestOutcome:
    """Put one generic retrieved document through the durable read/source edge.

    The knowledge research loop uses this function rather than maintaining a
    second copy of the read-ledger rules. A document is never promoted to a
    scientific claim here: this records only that a specific content rendition
    was retrieved/read for a specific frame under a specific extraction schema.
    """

    digest = content_digest(source_id=source_id, content=content)
    decision = decide_read_from_ledger(
        store,
        source_id,
        digest,
        schema_version,
        frame_id,
    )
    if decision is not ReadDecision.ALREADY_READ:
        canonical = canonical_source_id(source_id)
        record_source(
            store,
            SourceIdentity(
                source_id=str(canonical) if canonical.is_resolvable else source_id,
                aliases=aliases,
                title=title,
            ),
        )
        record_read(
            store,
            ReadReceipt(
                source_id=source_id,
                content_digest=digest,
                schema_version=schema_version,
                frame_id=frame_id,
            ),
        )
    return IngestOutcome(source_id, decision, digest)


def record_content(record: ArxivRecord) -> str:
    """The text whose digest decides whether this rendition was already read.

    Title and abstract, not the raw response: the response carries retrieval
    timestamps and pagination context that differ on every fetch, so digesting
    it would make every re-fetch look like a revision and defeat the cache
    entirely.
    """

    return f"{record.title}\n\n{record.summary}"


def content_digest_for(record: ArxivRecord) -> str:
    return content_digest(source_id=record.source_id, content=record_content(record))


def ingest_records(
    store: LedgerStore,
    records: Sequence[ArxivRecord],
    *,
    schema_version: str,
    frame_id: str,
) -> IngestReport:
    """Offer arXiv records to the same generic durable ingestion edge."""

    outcomes = tuple(
        ingest_document(
            store,
            source_id=record.source_id,
            content=record_content(record),
            title=record.title,
            aliases=record.aliases,
            schema_version=schema_version,
            frame_id=frame_id,
        )
        for record in records
    )
    return IngestReport(outcomes)
