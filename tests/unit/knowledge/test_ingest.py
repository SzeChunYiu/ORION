from __future__ import annotations

from pathlib import Path

from orion.kernel.store import LedgerStore
from orion.knowledge.identity import ReadDecision
from orion.knowledge.ingest import content_digest_for, ingest_records
from orion.knowledge.ledger import known_sources, read_receipts
from orion.knowledge.providers.arxiv import parse_atom

SCHEMA = "claim-extraction-v0"
FRAME = "frame:stopping-rules"


def _feed(summary: str = "We propose a new simple network architecture.") -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/1706.03762v7</id>
    <title>Attention Is All You Need</title>
    <summary>{summary}</summary>
    <arxiv:doi>10.1038/s41586-021-03819-3</arxiv:doi>
  </entry>
</feed>"""


def _records(summary: str | None = None):
    _, records, _ = parse_atom(_feed(summary) if summary else _feed())
    return records


def _store(tmp_path: Path) -> LedgerStore:
    return LedgerStore(tmp_path / "state")


def test_the_same_paper_fetched_twice_is_read_once(tmp_path: Path) -> None:
    """The question this whole subsystem exists to answer."""

    records = _records()
    first = ingest_records(_store(tmp_path), records, schema_version=SCHEMA, frame_id=FRAME)
    second = ingest_records(_store(tmp_path), records, schema_version=SCHEMA, frame_id=FRAME)

    assert first.counts() == {ReadDecision.UNSEEN.value: 1}
    assert second.counts() == {ReadDecision.ALREADY_READ.value: 1}
    assert len(second.ingested) == 0


def test_the_skip_survives_a_process_restart(tmp_path: Path) -> None:
    records = _records()
    ingest_records(_store(tmp_path), records, schema_version=SCHEMA, frame_id=FRAME)
    # A fresh store object over the same directory holds nothing in memory.
    again = ingest_records(_store(tmp_path), records, schema_version=SCHEMA, frame_id=FRAME)
    assert again.skipped and not again.ingested


def test_a_revised_abstract_is_read_again_and_says_why(tmp_path: Path) -> None:
    ingest_records(_store(tmp_path), _records(), schema_version=SCHEMA, frame_id=FRAME)
    revised = ingest_records(
        _store(tmp_path),
        _records("A substantially rewritten abstract."),
        schema_version=SCHEMA,
        frame_id=FRAME,
    )
    assert revised.counts() == {ReadDecision.CONTENT_CHANGED.value: 1}


def test_the_same_paper_for_a_new_question_is_read_again(tmp_path: Path) -> None:
    ingest_records(_store(tmp_path), _records(), schema_version=SCHEMA, frame_id=FRAME)
    other = ingest_records(
        _store(tmp_path), _records(), schema_version=SCHEMA, frame_id="frame:novelty"
    )
    assert other.counts() == {ReadDecision.NEW_FRAME.value: 1}


def test_a_new_extraction_schema_forces_a_re_read(tmp_path: Path) -> None:
    ingest_records(_store(tmp_path), _records(), schema_version=SCHEMA, frame_id=FRAME)
    upgraded = ingest_records(
        _store(tmp_path), _records(), schema_version="v1", frame_id=FRAME
    )
    assert upgraded.counts() == {ReadDecision.NEW_SCHEMA.value: 1}


def test_the_arxiv_doi_alias_is_carried_into_the_ledger(tmp_path: Path) -> None:
    """So the same work arriving later by DOI is recognised, not re-read."""

    store = _store(tmp_path)
    ingest_records(store, _records(), schema_version=SCHEMA, frame_id=FRAME)
    works = known_sources(_store(tmp_path))

    assert len(works) == 1
    assert works[0].keys == {"arxiv:1706.03762", "doi:10.1038/s41586-021-03819-3"}


def test_the_digest_ignores_retrieval_context(tmp_path: Path) -> None:
    """Digesting the raw response would make every re-fetch look like a
    revision, because responses carry timestamps and pagination context."""

    assert content_digest_for(_records()[0]) == content_digest_for(_records()[0])


def test_nothing_is_written_for_a_paper_already_read(tmp_path: Path) -> None:
    records = _records()
    ingest_records(_store(tmp_path), records, schema_version=SCHEMA, frame_id=FRAME)
    before = len(read_receipts(_store(tmp_path)))
    ingest_records(_store(tmp_path), records, schema_version=SCHEMA, frame_id=FRAME)
    assert len(read_receipts(_store(tmp_path))) == before
