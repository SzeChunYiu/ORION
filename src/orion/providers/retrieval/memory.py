from __future__ import annotations

from dataclasses import dataclass, field

from orion.core.search import RetrievedItem, SearchQuery


@dataclass
class InMemoryRetrievalProvider:
    """Deterministic provider used for known-world and integration tests."""

    results_by_query: dict[str, tuple[RetrievedItem, ...]]
    seen_queries: list[SearchQuery] = field(default_factory=list)

    def search(self, query: SearchQuery, *, limit: int) -> tuple[RetrievedItem, ...]:
        self.seen_queries.append(query)
        return self.results_by_query.get(query.text, ())[:limit]
