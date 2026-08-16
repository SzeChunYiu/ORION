import json
import urllib.parse

import pytest

from orion.core.search import SearchQuery, SearchRouteKind
from orion.providers.retrieval.literature import (
    CrossrefRetrievalProvider,
    EuropePMCRetrievalProvider,
    MultiSourceLiteratureRetrievalProvider,
)


def _query():
    return SearchQuery(
        "query:test",
        "microglia complement synapse elimination",
        "route:test",
        SearchRouteKind.PARENT_DISCIPLINE,
        "neuroimmunology",
    )


def test_europe_pmc_adapter_returns_source_bound_core_metadata_without_provider_as_domain():
    captured = {}

    def transport(url, headers, timeout):
        captured["url"] = url
        return json.dumps(
            {
                "resultList": {
                    "result": [
                        {
                            "source": "MED",
                            "id": "12345",
                            "title": "Complement and microglia",
                            "abstractText": "A source-local abstract.",
                            "authorString": "A Author; B Author",
                            "journalTitle": "Example Journal",
                            "pubYear": "2025",
                            "doi": "10.1000/example",
                        }
                    ]
                }
            }
        ).encode()

    provider = EuropePMCRetrievalProvider(transport=transport)
    items = provider.search(_query(), limit=3)

    assert len(items) == 1
    item = items[0]
    assert item.item_id == "europepmc:MED:12345"
    assert item.source_uri == "https://europepmc.org/article/MED/12345"
    assert "Abstract: A source-local abstract." in item.content
    assert item.domain_ids == ("neuroimmunology",)
    assert "europepmc" in item.item_id
    parsed = urllib.parse.urlparse(captured["url"])
    params = urllib.parse.parse_qs(parsed.query)
    assert params["resultType"] == ["core"]
    assert params["format"] == ["json"]


def test_crossref_adapter_returns_doi_bound_metadata_without_provider_as_domain():
    captured = {}

    def transport(url, headers, timeout):
        captured["url"] = url
        return json.dumps(
            {
                "message": {
                    "items": [
                        {
                            "DOI": "10.1000/MOS2",
                            "title": ["Screening in monolayer MoS2"],
                            "abstract": "Dielectric screening changes quasiparticle and excitonic energies.",
                            "author": [{"given": "Ada", "family": "Example"}],
                            "published": {"date-parts": [[2024, 1, 1]]},
                            "container-title": ["2D Materials"],
                            "URL": "https://doi.org/10.1000/MOS2",
                        }
                    ]
                }
            }
        ).encode()

    provider = CrossrefRetrievalProvider(mailto="research@example.test", transport=transport)
    items = provider.search(_query(), limit=2)

    assert len(items) == 1
    item = items[0]
    assert item.item_id == "crossref:doi:10.1000/mos2"
    assert item.source_uri == "https://doi.org/10.1000/MOS2"
    assert "Ada Example" in item.content
    assert item.domain_ids == ("neuroimmunology",)
    params = urllib.parse.parse_qs(urllib.parse.urlparse(captured["url"]).query)
    assert params["query.bibliographic"] == [_query().text]
    assert params["mailto"] == ["research@example.test"]


def test_literature_provider_without_domain_hint_does_not_invent_provider_domain():
    query = SearchQuery(
        "query:no-domain",
        "screening monolayer MoS2 exciton",
        "route:no-domain",
        SearchRouteKind.FUNCTION_ONLY,
    )
    provider = CrossrefRetrievalProvider(
        transport=lambda url, headers, timeout: json.dumps(
            {
                "message": {
                    "items": [
                        {
                            "DOI": "10.1000/ONE",
                            "title": ["One paper"],
                            "URL": "https://doi.org/10.1000/ONE",
                        }
                    ]
                }
            }
        ).encode()
    )
    assert provider.search(query, limit=1)[0].domain_ids == ()


def test_multi_source_retrieval_is_strict_about_source_failure():
    class Good:
        def search(self, query, *, limit):
            return ()

    class Broken:
        def search(self, query, *, limit):
            raise RuntimeError("source unavailable")

    provider = MultiSourceLiteratureRetrievalProvider((Good(), Broken()))
    with pytest.raises(RuntimeError, match="source unavailable"):
        provider.search(_query(), limit=5)


def test_multi_source_retrieval_deduplicates_identical_source_and_content():
    item = EuropePMCRetrievalProvider(
        transport=lambda url, headers, timeout: json.dumps(
            {
                "resultList": {
                    "result": [
                        {"source": "MED", "id": "1", "title": "Same paper"}
                    ]
                }
            }
        ).encode()
    )
    provider = MultiSourceLiteratureRetrievalProvider((item, item))
    results = provider.search(_query(), limit=5)
    assert len(results) == 1
