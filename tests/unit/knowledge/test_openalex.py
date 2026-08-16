from __future__ import annotations

import json

import pytest

from orion.knowledge.providers.arxiv import TransportResponse
from orion.knowledge.providers.openalex import (
    BASIC_PAGING_CEILING,
    OpenAlexClient,
    OpenAlexStatus,
    basic_paging_exceeded,
    build_works_url,
    parse_works,
    reconstruct_abstract,
)
from orion.knowledge.rate import RateGate

_WORK = {
    "id": "https://openalex.org/W2741809807",
    "display_name": "Attention Is All You Need",
    "publication_year": 2017,
    "ids": {
        "openalex": "https://openalex.org/W2741809807",
        "doi": "https://doi.org/10.1038/s41586-021-03819-3",
    },
    "abstract_inverted_index": {"We": [0], "propose": [1], "attention": [2]},
    "referenced_works": ["https://openalex.org/W123"],
}


def _body(**meta) -> str:
    return json.dumps({"results": [_WORK], "meta": {"count": 1, **meta}})


def _client(response: TransportResponse, key: str = "k", gate=None) -> OpenAlexClient:
    return OpenAlexClient(transport=lambda url: response, api_key=key, gate=gate)


# --- the inverted index --------------------------------------------------


def test_an_inverted_index_is_reconstructed_in_order() -> None:
    assert reconstruct_abstract({"b": [1], "a": [0], "c": [2]}) == "a b c"


def test_a_token_appearing_twice_is_placed_at_both_positions() -> None:
    assert reconstruct_abstract({"the": [0, 2], "cat": [1]}) == "the cat the"


def test_a_missing_index_is_empty_not_an_error() -> None:
    assert reconstruct_abstract(None) == ""
    assert reconstruct_abstract({}) == ""


def test_a_present_abstract_is_not_read_as_absent() -> None:
    """OpenAlex ships abstracts as an inverted index. Treating that as empty
    would report a present abstract as missing — a false negative for a
    coverage-driven system."""

    _, records, _ = parse_works(_body())
    assert records[0].abstract == "We propose attention"


# --- keyless refusal -----------------------------------------------------


def test_a_keyless_request_is_refused_before_it_is_attempted() -> None:
    """Since Feb 2026 OpenAlex requires a key and ignores mailto. The keyless
    budget is shared across the whole IP, so attempting one spends an allowance
    every other caller on this address depends on."""

    def _should_not_be_called(url: str) -> TransportResponse:
        raise AssertionError("no request may be issued without a key")

    page = OpenAlexClient(transport=_should_not_be_called).fetch_works(search="x")
    assert page.status is OpenAlexStatus.KEY_REQUIRED
    assert "mailto" in page.note


# --- the two paging models ----------------------------------------------


def test_basic_paging_past_the_ceiling_is_refused_with_the_alternative() -> None:
    page = _client(TransportResponse(200, _body())).fetch_works(
        search="x", per_page=100, page=(BASIC_PAGING_CEILING // 100) + 1
    )
    assert page.status is OpenAlexStatus.REFUSED_BASIC_PAGING_CEILING
    assert "cursor" in page.note


def test_the_ceiling_is_on_the_product_not_the_page_number() -> None:
    assert not basic_paging_exceeded(page=100, per_page=100)
    assert basic_paging_exceeded(page=101, per_page=100)
    assert not basic_paging_exceeded(page=1000, per_page=10)


def test_cursor_paging_carries_the_next_cursor() -> None:
    page = _client(TransportResponse(200, _body(next_cursor="IlsxNjA="))).fetch_works(
        search="x", cursor="*"
    )
    assert page.ok
    assert page.next_cursor == "IlsxNjA="


def test_page_and_cursor_are_mutually_exclusive() -> None:
    with pytest.raises(ValueError):
        build_works_url(search="x", page=2, cursor="*")


def test_per_page_above_the_documented_maximum_is_refused() -> None:
    with pytest.raises(ValueError):
        build_works_url(search="x", per_page=101)


# --- records and failures ------------------------------------------------


def test_a_doi_in_the_ids_block_becomes_an_alias() -> None:
    _, records, _ = parse_works(_body())
    assert records[0].source_id == "openalex:W2741809807"
    assert records[0].aliases == ("doi:10.1038/s41586-021-03819-3",)


def test_cost_is_surfaced_so_budget_can_be_tracked() -> None:
    page = _client(TransportResponse(200, _body(cost_usd=0.0001))).fetch_works(search="x")
    assert page.cost_usd == 0.0001
    assert page.total == 1


def test_a_rate_limit_updates_the_gate() -> None:
    gate = RateGate(clock=lambda: 0.0)
    page = _client(
        TransportResponse(429, "", {"Retry-After": "5339"}), gate=gate
    ).fetch_works(search="x")
    assert page.status is OpenAlexStatus.RATE_LIMITED
    assert gate.wait_seconds("openalex") == 5339.0


def test_a_service_error_body_is_not_parsed_as_results() -> None:
    body = json.dumps({"error": "Rate limit exceeded", "message": "Insufficient budget."})
    status, records, meta = parse_works(body)
    assert status is OpenAlexStatus.SERVICE_ERROR
    assert records == ()
    assert "Insufficient" in meta["note"]


def test_malformed_json_is_typed_not_crashed() -> None:
    status, records, _ = parse_works("{not json")
    assert status is OpenAlexStatus.MALFORMED_RESPONSE
    assert records == ()


def test_a_transport_failure_is_data() -> None:
    def _boom(url: str) -> TransportResponse:
        raise TimeoutError("read timed out")

    page = OpenAlexClient(transport=_boom, api_key="k").fetch_works(search="x")
    assert page.status is OpenAlexStatus.TRANSPORT_ERROR
