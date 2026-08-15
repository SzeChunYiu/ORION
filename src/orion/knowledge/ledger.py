from __future__ import annotations

from orion.kernel.store import EntryKind, LedgerStore

from .identity import (
    ReadDecision,
    ReadReceipt,
    SourceIdentity,
    canonical_source_id,
    decide_read,
    merge_identities,
)


def record_source(store: LedgerStore, identity: SourceIdentity) -> None:
    """Append a work to the durable record of what ORION knows exists.

    Keys are canonicalized at the write boundary. A ledger that stores whatever
    string it was handed accumulates un-normalized keys that can never match a
    later lookup, so the cache would miss silently and the paper would be read
    again — the exact failure this subsystem exists to prevent.
    """

    store.append(
        EntryKind.SOURCE,
        {
            "source_id": str(canonical_source_id(identity.source_id)),
            "aliases": sorted(
                {str(canonical_source_id(item)) for item in identity.aliases}
            ),
            "title": identity.title,
        },
    )


def record_read(store: LedgerStore, receipt: ReadReceipt) -> None:
    """Append evidence that a specific rendition was actually extracted from."""

    store.append(
        EntryKind.READ,
        {
            "source_id": str(canonical_source_id(receipt.source_id)),
            "content_digest": receipt.content_digest,
            "schema_version": receipt.schema_version,
            "frame_id": receipt.frame_id,
            "contribution_ids": list(receipt.contribution_ids),
        },
    )


def known_sources(store: LedgerStore) -> tuple[SourceIdentity, ...]:
    """Replay every recorded work, collapsing alias-sharing records into one.

    Merging happens on read rather than on write because an alias learned later
    can join two works recorded earlier as separate. Folding at write time would
    freeze the wrong answer; the ledger stays append-only and the merge is a
    projection over it.
    """

    identities = tuple(
        SourceIdentity(
            source_id=str(entry.payload["source_id"]),
            aliases=tuple(str(item) for item in entry.payload.get("aliases", ()) or ()),
            title=str(entry.payload.get("title", "") or ""),
        )
        for entry in store.entries(EntryKind.SOURCE)
        if entry.payload.get("source_id")
    )
    return merge_identities(identities)


def read_receipts(store: LedgerStore) -> tuple[ReadReceipt, ...]:
    receipts: list[ReadReceipt] = []
    for entry in store.entries(EntryKind.READ):
        payload = entry.payload
        try:
            receipts.append(
                ReadReceipt(
                    source_id=str(payload["source_id"]),
                    content_digest=str(payload["content_digest"]),
                    schema_version=str(payload["schema_version"]),
                    frame_id=str(payload["frame_id"]),
                    contribution_ids=tuple(
                        str(item) for item in payload.get("contribution_ids", ()) or ()
                    ),
                )
            )
        except (KeyError, ValueError):
            continue
    return tuple(receipts)


def decide_read_from_ledger(
    store: LedgerStore,
    raw_identifier: str,
    content_digest: str,
    schema_version: str,
    frame_id: str,
) -> ReadDecision:
    """Decide whether to read a source, using everything durably recorded.

    The raw identifier is canonicalized first, and aliases are resolved through
    the merged source set, so a paper previously recorded under its DOI is
    recognised when it arrives again as an arXiv id. Without that step the cache
    would miss on exactly the cross-route re-encounters it exists to catch.
    """

    # Map every known alias to its work's primary key, then push both the query
    # and every receipt through it. Normalizing only the query would still miss
    # a receipt that happens to be stored under a third alias of the same work.
    primary_of: dict[str, str] = {}
    for identity in known_sources(store):
        for key in identity.keys:
            primary_of[key] = identity.source_id

    canonical = str(canonical_source_id(raw_identifier))
    resolved = primary_of.get(canonical, canonical)
    receipts = tuple(
        ReadReceipt(
            source_id=primary_of.get(item.source_id, item.source_id),
            content_digest=item.content_digest,
            schema_version=item.schema_version,
            frame_id=item.frame_id,
            contribution_ids=item.contribution_ids,
        )
        for item in read_receipts(store)
    )
    return decide_read(resolved, content_digest, schema_version, frame_id, receipts)
