from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from orion.core.search import RetrievedItem, SearchQuery

from .base import RetrievalProvider


HTTPGetTransport = Callable[[str, dict[str, str], float], bytes]


def _default_get(url: str, headers: dict[str, str], timeout: float) -> bytes:
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - adapters freeze HTTPS origins
            return response.read()
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"literature API HTTP {error.code}: {body[:1000]}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"literature API transport failed: {error.reason}") from error


def _clean(value: object) -> str:
    return " ".join(str(value or "").split())


def _scientific_domain_ids(query: SearchQuery) -> tuple[str, ...]:
    """Return only scientific/search-domain identity, never provider provenance.

    Europe PMC/Crossref identity remains exact in item_id/source_uri. Mixing the
    provider label into domain_ids causes W to treat a retrieval backend as a
    newly discovered scientific domain and can trigger redundant search loops.
    """

    return (query.domain_hint,) if query.domain_hint else ()


@dataclass(frozen=True)
class EuropePMCRetrievalProvider(RetrievalProvider):
    """Public Europe PMC REST search adapter for life-sciences literature."""

    timeout_seconds: float = 30.0
    transport: HTTPGetTransport = _default_get
    endpoint: str = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    def __post_init__(self) -> None:
        if self.endpoint != "https://www.ebi.ac.uk/europepmc/webservices/rest/search":
            raise ValueError("Europe PMC endpoint is frozen to the official HTTPS REST search endpoint")
        if self.timeout_seconds <= 0:
            raise ValueError("Europe PMC timeout must be positive")

    def search(self, query: SearchQuery, *, limit: int) -> tuple[RetrievedItem, ...]:
        if limit < 1:
            return ()
        params = urllib.parse.urlencode(
            {
                "query": query.text,
                "resultType": "core",
                "pageSize": min(limit, 1000),
                "format": "json",
            }
        )
        body = self.transport(
            f"{self.endpoint}?{params}",
            {"Accept": "application/json", "User-Agent": "orion-research-os/0.1"},
            self.timeout_seconds,
        )
        raw = json.loads(body)
        results = raw.get("resultList", {}).get("result", []) if isinstance(raw, dict) else []
        if not isinstance(results, list):
            raise RuntimeError("Europe PMC response resultList.result must be an array")
        items: list[RetrievedItem] = []
        for record in results[:limit]:
            if not isinstance(record, dict):
                continue
            source = _clean(record.get("source")) or "UNKNOWN"
            external_id = _clean(record.get("id") or record.get("pmid") or record.get("pmcid"))
            title = _clean(record.get("title"))
            abstract = _clean(record.get("abstractText"))
            if not external_id or not title:
                continue
            doi = _clean(record.get("doi"))
            author = _clean(record.get("authorString"))
            journal = _clean(record.get("journalTitle"))
            year = _clean(record.get("pubYear"))
            lines = [f"Title: {title}"]
            if author:
                lines.append(f"Authors: {author}")
            if journal or year:
                lines.append(f"Publication: {'; '.join(item for item in (journal, year) if item)}")
            if doi:
                lines.append(f"DOI: {doi}")
            if abstract:
                lines.append(f"Abstract: {abstract}")
            items.append(
                RetrievedItem(
                    item_id=f"europepmc:{source}:{external_id}",
                    content="\n".join(lines),
                    source_uri=f"https://europepmc.org/article/{source}/{external_id}",
                    domain_ids=_scientific_domain_ids(query),
                )
            )
        return tuple(items)


@dataclass(frozen=True)
class CrossrefRetrievalProvider(RetrievalProvider):
    """Public Crossref REST metadata adapter for cross-domain scholarly works."""

    timeout_seconds: float = 30.0
    mailto: str = ""
    transport: HTTPGetTransport = _default_get
    endpoint: str = "https://api.crossref.org/works"

    def __post_init__(self) -> None:
        if self.endpoint != "https://api.crossref.org/works":
            raise ValueError("Crossref endpoint is frozen to the official HTTPS works endpoint")
        if self.timeout_seconds <= 0:
            raise ValueError("Crossref timeout must be positive")

    def search(self, query: SearchQuery, *, limit: int) -> tuple[RetrievedItem, ...]:
        if limit < 1:
            return ()
        parameters: dict[str, object] = {
            "query.bibliographic": query.text,
            "rows": min(limit, 1000),
            "select": "DOI,title,abstract,author,published,container-title,URL,subject,type",
        }
        if self.mailto:
            parameters["mailto"] = self.mailto
        params = urllib.parse.urlencode(parameters)
        body = self.transport(
            f"{self.endpoint}?{params}",
            {"Accept": "application/json", "User-Agent": "orion-research-os/0.1"},
            self.timeout_seconds,
        )
        raw = json.loads(body)
        message = raw.get("message", {}) if isinstance(raw, dict) else {}
        records = message.get("items", []) if isinstance(message, dict) else []
        if not isinstance(records, list):
            raise RuntimeError("Crossref response message.items must be an array")
        items: list[RetrievedItem] = []
        for record in records[:limit]:
            if not isinstance(record, dict):
                continue
            doi = _clean(record.get("DOI"))
            title_values = record.get("title")
            title = _clean(title_values[0]) if isinstance(title_values, list) and title_values else ""
            source_uri = _clean(record.get("URL")) or (f"https://doi.org/{doi}" if doi else "")
            if not title or not source_uri:
                continue
            abstract = _clean(record.get("abstract"))
            container_values = record.get("container-title")
            container = _clean(container_values[0]) if isinstance(container_values, list) and container_values else ""
            authors = record.get("author")
            author_names: list[str] = []
            if isinstance(authors, list):
                for author in authors:
                    if not isinstance(author, dict):
                        continue
                    name = _clean(" ".join(filter(None, (_clean(author.get("given")), _clean(author.get("family"))))))
                    if name:
                        author_names.append(name)
            date_parts = record.get("published", {}).get("date-parts", []) if isinstance(record.get("published"), dict) else []
            year = ""
            if isinstance(date_parts, list) and date_parts and isinstance(date_parts[0], list) and date_parts[0]:
                year = _clean(date_parts[0][0])
            lines = [f"Title: {title}"]
            if author_names:
                lines.append("Authors: " + "; ".join(author_names[:20]))
            if container or year:
                lines.append(f"Publication: {'; '.join(item for item in (container, year) if item)}")
            if doi:
                lines.append(f"DOI: {doi}")
            if abstract:
                lines.append(f"Abstract: {abstract}")
            item_id = f"crossref:doi:{doi.lower()}" if doi else "crossref:url:" + urllib.parse.quote(source_uri, safe="")
            items.append(
                RetrievedItem(
                    item_id=item_id,
                    content="\n".join(lines),
                    source_uri=source_uri,
                    domain_ids=_scientific_domain_ids(query),
                )
            )
        return tuple(items)


class MultiSourceLiteratureRetrievalProvider(RetrievalProvider):
    """Strict multi-source retrieval for Phase-2 coverage.

    Every configured source must respond successfully. This intentionally treats
    a source outage as a coverage failure instead of silently presenting a
    partial search as complete.
    """

    def __init__(self, providers: Sequence[RetrievalProvider]) -> None:
        self._providers = tuple(providers)
        if not self._providers:
            raise ValueError("multi-source literature retrieval requires at least one provider")

    def search(self, query: SearchQuery, *, limit: int) -> tuple[RetrievedItem, ...]:
        if limit < 1:
            return ()
        per_source = max(1, limit)
        combined: list[RetrievedItem] = []
        for provider in self._providers:
            combined.extend(provider.search(query, limit=per_source))
        deduplicated: list[RetrievedItem] = []
        seen: set[tuple[str, str]] = set()
        for item in combined:
            key = (item.source_uri, item.content)
            if key in seen:
                continue
            seen.add(key)
            deduplicated.append(item)
            if len(deduplicated) >= limit:
                break
        return tuple(deduplicated)


__all__ = [
    "CrossrefRetrievalProvider",
    "EuropePMCRetrievalProvider",
    "HTTPGetTransport",
    "MultiSourceLiteratureRetrievalProvider",
]
