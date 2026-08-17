from __future__ import annotations

import pytest

from orion.knowledge.providers.arxiv import (
    SAFE_START_LIMIT,
    ArxivClient,
    FetchStatus,
    TransportResponse,
    build_query_url,
    parse_atom,
)
from orion.knowledge.rate import RateGate

_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/1706.03762v7</id>
    <title>Attention Is All You Need</title>
    <summary>We propose a new simple network architecture.</summary>
    <published>2017-06-12T17:57:34Z</published>
    <updated>2023-08-02T00:41:18Z</updated>
    <author><name>Ashish Vaswani</name></author>
    <author><name>Noam Shazeer</name></author>
    <arxiv:doi>10.1038/s41586-021-03819-3</arxiv:doi>
    <arxiv:primary_category term="cs.CL"/>
  </entry>
</feed>"""

_LEGACY_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/hep-th/9901001v2</id>
    <title>A Legacy Identifier Example</title>
    <summary>A legacy arXiv archive identifier must retain its category prefix.</summary>
    <published>1999-01-01T00:00:00Z</published>
    <updated>2000-01-01T00:00:00Z</updated>
    <author><name>Legacy Author</name></author>
    <arxiv:primary_category term="hep-th"/>
  </entry>
</feed>"""

_IN_BAND_ERROR = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/api/errors#incorrect_id_format</id>
    <title>Error</title>
    <summary>The server encountered an internal error.</summary>
  </entry>
</feed>"""

_BILLION_LAUGHS = """<?xml version="1.0"?>
<!DOCTYPE lolz [<!ENTITY lol "lol"><!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;">]>
<feed xmlns="http://www.w3.org/2005/Atom"><title>&lol2;</title></feed>"""


def _client(response: TransportResponse, gate: RateGate | None = None) -> ArxivClient:
    return ArxivClient(transport=lambda url: response, gate=gate)


def test_a_versioned_id_becomes_one_work_with_the_version_kept() -> None:
    status, records, _ = parse_atom(_FEED)
    assert status is FetchStatus.OK
    record = records[0]
    assert record.source_id == "arxiv:1706.03762"
    assert record.identity.version == "7"
    assert record.versioned_id == "1706.03762v7"
    assert record.authors == ("Ashish Vaswani", "Noam Shazeer")
    assert record.primary_category == "cs.CL"


def test_a_legacy_versioned_id_keeps_its_archive_prefix() -> None:
    """A legacy ID is ``archive/NNNNNNNvN``; dropping the archive makes a
    retrieved paper impossible to match against a correct external evaluator."""

    status, records, _ = parse_atom(_LEGACY_FEED)
    assert status is FetchStatus.OK
    assert len(records) == 1
    record = records[0]
    assert record.source_id == "arxiv:hep-th/9901001"
    assert record.identity.version == "2"
    assert record.versioned_id == "hep-th/9901001v2"
    assert record.primary_category == "hep-th"


def test_a_doi_arxiv_reports_for_an_entry_is_a_genuine_alias() -> None:
    """The one case where a nearby identifier really does identify the work:
    arXiv states it in a field describing the entry, not in prose."""

    _, records, _ = parse_atom(_FEED)
    assert records[0].aliases == ("doi:10.1038/s41586-021-03819-3",)


def test_an_in_band_service_error_is_not_reported_as_an_empty_result() -> None:
    """arXiv returns faults inside a 200-shaped Atom document. Parsing that as
    zero records turns a service failure into 'nothing matched' — a false
    negative that reads downstream as evidence of absence."""

    status, records, note = parse_atom(_IN_BAND_ERROR)
    assert status is FetchStatus.SERVICE_ERROR
    assert records == ()
    assert note


def test_entity_expansion_in_remote_xml_is_refused() -> None:
    """Untrusted remote input: stdlib ElementTree expands entities."""

    status, records, note = parse_atom(_BILLION_LAUGHS)
    assert status is FetchStatus.MALFORMED_RESPONSE
    assert records == ()
    assert "Entities" in note or "unparseable" in note


def test_deep_paging_is_refused_rather_than_walked_into() -> None:
    """arXiv fails past a few thousand `start` with HTTP 500, not the
    documented 400. Refusing with guidance beats retrying into a wall."""

    result = _client(TransportResponse(200, _FEED)).fetch(
        search_query="cat:cs.IR", start=SAFE_START_LIMIT + 1
    )
    assert result.status is FetchStatus.REFUSED_UNSAFE_PAGING
    assert "OAI-PMH" in result.note


def test_a_rate_limit_is_authoritative_and_updates_the_gate() -> None:
    """Observed 2026-08-16: arXiv returned 429 to an isolated request that
    honoured the published spacing, so the published budget is a floor."""

    clock = lambda: 0.0  # noqa: E731
    gate = RateGate(clock=clock)
    result = _client(
        TransportResponse(429, "", {"Retry-After": "120"}), gate
    ).fetch(search_query="cat:cs.IR")

    assert result.status is FetchStatus.RATE_LIMITED
    assert result.retry_after_seconds == 120.0
    assert gate.wait_seconds("arxiv") == 120.0


def test_a_rate_limit_without_a_header_still_refuses() -> None:
    result = _client(TransportResponse(429, "")).fetch(search_query="cat:cs.IR")
    assert result.status is FetchStatus.RATE_LIMITED
    assert result.retry_after_seconds is None


def test_a_transport_failure_is_data_not_a_crash() -> None:
    def _boom(url: str) -> TransportResponse:
        raise TimeoutError("read timed out")

    result = ArxivClient(transport=_boom).fetch(search_query="cat:cs.IR")
    assert result.status is FetchStatus.TRANSPORT_ERROR
    assert "TimeoutError" in result.note


def test_server_errors_are_distinguished_from_empty_results() -> None:
    result = _client(TransportResponse(500, "")).fetch(search_query="cat:cs.IR")
    assert result.status is FetchStatus.SERVICE_ERROR


def test_a_query_needs_something_to_query_for() -> None:
    with pytest.raises(ValueError):
        build_query_url()


def test_max_results_beyond_the_documented_slice_is_refused() -> None:
    with pytest.raises(ValueError):
        build_query_url(search_query="cat:cs.IR", max_results=2001)


def test_the_url_carries_the_declared_parameters() -> None:
    url = build_query_url(id_list=("1706.03762",), start=10, max_results=5)
    assert "id_list=1706.03762" in url
    assert "start=10" in url and "max_results=5" in url
