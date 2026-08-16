from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .local import DEFAULT_SUFFIXES, index_local_corpus, read_text_head
from .providers.arxiv import ArxivClient, FetchStatus, TransportResponse
from .rate import RateGate
from .research_loop import RetrievedDoc


class ProviderBudgetNotReady(RuntimeError):
    """Raised when a provider route would violate its bound request budget."""


class ProviderSearchUnavailable(RuntimeError):
    """Raised when a provider returned a typed non-OK retrieval outcome."""


def _query_terms(query: str) -> set[str]:
    return {
        token.strip(".,:;()[]{}\"'").lower()
        for token in query.split()
        if len(token.strip(".,:;()[]{}\"'")) > 3
    }


@dataclass(frozen=True)
class LocalCorpusSearcher:
    """Use ORION's content-addressed local corpus index as a real search route."""

    root: Path
    suffixes: tuple[str, ...] = DEFAULT_SUFFIXES
    max_results: int = 25

    def __post_init__(self) -> None:
        if self.max_results < 1:
            raise ValueError("local search max_results must be positive")

    def search(self, query: str) -> tuple[RetrievedDoc, ...]:
        terms = _query_terms(query)
        files, _ = index_local_corpus(self.root, self.suffixes)
        ranked: list[tuple[int, str, RetrievedDoc]] = []
        for item in files:
            content = read_text_head(item.path)
            haystack = content.lower()
            overlap = sum(term in haystack for term in terms)
            if terms and overlap == 0:
                continue
            ranked.append(
                (
                    overlap,
                    item.identity.source_id,
                    RetrievedDoc(
                        source_id=item.identity.source_id,
                        content=content,
                        title=item.identity.title,
                    ),
                )
            )
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return tuple(item[2] for item in ranked[: self.max_results])


@dataclass
class ArxivRouteSearcher:
    """Rate-gated arXiv backend for a knowledge research route.

    The gate is checked before transport. ``ArxivClient`` then records the
    request and any server Retry-After value on the same gate, so the next route
    cannot borrow unused capacity from another provider or silently burst.
    """

    client: ArxivClient
    gate: RateGate
    max_results: int = 25

    def __post_init__(self) -> None:
        if self.max_results < 1:
            raise ValueError("arXiv search max_results must be positive")

    def search(self, query: str) -> tuple[RetrievedDoc, ...]:
        wait = self.gate.wait_seconds("arxiv")
        if wait > 0:
            raise ProviderBudgetNotReady(
                f"arxiv route requires {wait:.6f}s more provider spacing"
            )
        result = self.client.fetch(
            search_query=f"all:{query}",
            max_results=self.max_results,
        )
        if result.status is not FetchStatus.OK:
            raise ProviderSearchUnavailable(
                f"arxiv search unavailable: {result.status.value}: {result.note}"
            )
        return tuple(
            RetrievedDoc(
                source_id=record.source_id,
                content=f"{record.title}\n\n{record.summary}",
                title=record.title,
                aliases=record.aliases,
            )
            for record in result.records
        )


def build_arxiv_searcher(
    *,
    transport: Callable[[str], TransportResponse],
    clock: Callable[[], float] = time.monotonic,
    max_results: int = 25,
) -> ArxivRouteSearcher:
    """Construct the provider with the repository's verified rate budget active."""

    gate = RateGate(clock=clock)
    client = ArxivClient(transport=transport, gate=gate)
    return ArxivRouteSearcher(client=client, gate=gate, max_results=max_results)


__all__ = [
    "ArxivRouteSearcher",
    "LocalCorpusSearcher",
    "ProviderBudgetNotReady",
    "ProviderSearchUnavailable",
    "build_arxiv_searcher",
]
