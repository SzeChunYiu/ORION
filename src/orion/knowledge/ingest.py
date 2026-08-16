from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from orion.core.evidence import EvidenceRecord, content_fingerprint
from orion.kernel.store import LedgerStore

from .identity import ReadDecision, ReadReceipt, SourceIdentity
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


def record_content(record: ArxivRecord) -> str:
    """The text whose digest decides whether this rendition was already read.

    Title and abstract, not the raw response: the response carries retrieval
    timestamps and pagination context that differ on every fetch, so digesting
    it would make every re-fetch look like a revision and defeat the cache
    entirely.
    """

    return f"{record.title}\n\n{record.summary}"


def content_digest_for(record: ArxivRecord) -> str:
    return content_fingerprint(
        EvidenceRecord(
            evidence_id=record.source_id,
            content=record_content(record) or record.source_id,
            source_uri=record.source_id,
        )
    )


def ingest_records(
    store: LedgerStore,
    records: Sequence[ArxivRecord],
    *,
    schema_version: str,
    frame_id: str,
) -> IngestReport:
    """Offer retrieved records to the durable ledger, reading each at most once.

    This is the edge that makes retrieval cumulative rather than repetitive. A
    paper already read at this content, under this extraction schema, for this
    question is skipped; anything else is recorded with the reason it still
    needed reading, so a re-read is always attributable to a revision, a schema
    change or a new question rather than to forgetting.
    """

    outcomes: list[IngestOutcome] = []
    for record in records:
        digest = content_digest_for(record)
        decision = decide_read_from_ledger(
            store, record.source_id, digest, schema_version, frame_id
        )
        if decision is not ReadDecision.ALREADY_READ:
            record_source(
                store,
                SourceIdentity(
                    source_id=record.source_id,
                    aliases=record.aliases,
                    title=record.title,
                ),
            )
            record_read(
                store,
                ReadReceipt(
                    source_id=record.source_id,
                    content_digest=digest,
                    schema_version=schema_version,
                    frame_id=frame_id,
                ),
            )
        outcomes.append(IngestOutcome(record.source_id, decision, digest))
    return IngestReport(tuple(outcomes))
