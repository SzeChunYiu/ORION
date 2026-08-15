from __future__ import annotations

from pathlib import Path

from orion.kernel.store import LedgerStore
from orion.knowledge.identity import ReadDecision, ReadReceipt, SourceIdentity
from orion.knowledge.ledger import (
    decide_read_from_ledger,
    known_sources,
    read_receipts,
    record_read,
    record_source,
)

SCHEMA = "claim-extraction-v0"
FRAME = "frame:stopping-rules"
DIGEST = "a" * 64


def _store(tmp_path: Path) -> LedgerStore:
    return LedgerStore(tmp_path / "state")


def test_a_read_survives_a_process_restart(tmp_path: Path) -> None:
    """The whole point: a paper read in one run is not re-read in the next."""

    record_read(
        _store(tmp_path),
        ReadReceipt("arxiv:2301.00001", DIGEST, SCHEMA, FRAME),
    )
    # A brand-new store object over the same directory — nothing carried in memory.
    assert (
        decide_read_from_ledger(
            _store(tmp_path), "arXiv:2301.00001v2", DIGEST, SCHEMA, FRAME
        )
        is ReadDecision.ALREADY_READ
    )


def test_a_paper_recorded_by_doi_is_recognised_when_it_returns_as_an_arxiv_id(
    tmp_path: Path,
) -> None:
    """The cross-route re-encounter this cache exists to catch."""

    store = _store(tmp_path)
    record_source(
        store, SourceIdentity("doi:10.1038/s41586-021-03819-3", aliases=("arxiv:2301.00001",))
    )
    record_read(store, ReadReceipt("doi:10.1038/s41586-021-03819-3", DIGEST, SCHEMA, FRAME))

    assert (
        decide_read_from_ledger(
            _store(tmp_path), "https://arxiv.org/abs/2301.00001", DIGEST, SCHEMA, FRAME
        )
        is ReadDecision.ALREADY_READ
    )


def test_a_receipt_stored_under_a_third_alias_still_matches(tmp_path: Path) -> None:
    """Normalizing only the query would miss this; both sides must be mapped."""

    store = _store(tmp_path)
    record_source(
        store,
        SourceIdentity("doi:10.1038/s41586-021-03819-3", aliases=("arxiv:2301.00001", "openalex:W1")),
    )
    record_read(store, ReadReceipt("arxiv:2301.00001", DIGEST, SCHEMA, FRAME))

    assert (
        decide_read_from_ledger(_store(tmp_path), "doi:10.1038/s41586-021-03819-3", DIGEST, SCHEMA, FRAME)
        is ReadDecision.ALREADY_READ
    )


def test_a_revised_version_is_re_read_across_restart(tmp_path: Path) -> None:
    record_read(
        _store(tmp_path), ReadReceipt("arxiv:2301.00001", DIGEST, SCHEMA, FRAME)
    )
    assert (
        decide_read_from_ledger(
            _store(tmp_path), "arxiv:2301.00001", "b" * 64, SCHEMA, FRAME
        )
        is ReadDecision.CONTENT_CHANGED
    )


def test_a_different_question_still_requires_reading(tmp_path: Path) -> None:
    record_read(
        _store(tmp_path), ReadReceipt("arxiv:2301.00001", DIGEST, SCHEMA, FRAME)
    )
    assert (
        decide_read_from_ledger(
            _store(tmp_path), "arxiv:2301.00001", DIGEST, SCHEMA, "frame:novelty"
        )
        is ReadDecision.NEW_FRAME
    )


def test_an_alias_learned_later_joins_works_recorded_earlier(tmp_path: Path) -> None:
    """Merging is a projection over an append-only log, not a write-time fold."""

    store = _store(tmp_path)
    record_source(store, SourceIdentity("doi:10.1038/s41586-021-03819-3"))
    record_source(store, SourceIdentity("arxiv:2301.00001"))
    assert len(known_sources(store)) == 2

    record_source(
        store, SourceIdentity("doi:10.1038/s41586-021-03819-3", aliases=("arxiv:2301.00001",))
    )
    merged = known_sources(_store(tmp_path))
    assert len(merged) == 1
    assert merged[0].keys == {"doi:10.1038/s41586-021-03819-3", "arxiv:2301.00001"}


def test_an_unread_source_is_still_unseen(tmp_path: Path) -> None:
    assert (
        decide_read_from_ledger(_store(tmp_path), "doi:10.1038/nature12373", DIGEST, SCHEMA, FRAME)
        is ReadDecision.UNSEEN
    )
    assert read_receipts(_store(tmp_path)) == ()


def test_a_messy_identifier_recorded_once_is_found_however_it_returns(
    tmp_path: Path,
) -> None:
    """Normalization happens at the write boundary, not only at lookup.

    Found by a failing test: the ledger previously stored whatever string it was
    handed, so a source recorded under a resolver URL could never match the same
    work arriving as a bare id, and the cache would miss silently — which reads
    as "unseen" and re-reads the paper.
    """

    record_read(
        _store(tmp_path),
        ReadReceipt(
            "https://doi.org/10.1038/S41586-021-03819-3", DIGEST, SCHEMA, FRAME
        ),
    )
    for arrival in (
        "10.1038/s41586-021-03819-3",
        "doi:10.1038/s41586-021-03819-3",
        "  https://doi.org/10.1038/S41586-021-03819-3  ",
    ):
        assert (
            decide_read_from_ledger(_store(tmp_path), arrival, DIGEST, SCHEMA, FRAME)
            is ReadDecision.ALREADY_READ
        ), arrival
