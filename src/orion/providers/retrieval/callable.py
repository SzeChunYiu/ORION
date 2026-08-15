from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from orion.core.search import RetrievedItem, SearchQuery


@dataclass(frozen=True)
class CallableRetrievalProvider:
    search_fn: Callable[[SearchQuery, int], tuple[RetrievedItem, ...]]

    def search(self, query: SearchQuery, *, limit: int) -> tuple[RetrievedItem, ...]:
        result = self.search_fn(query, limit)
        if not isinstance(result, tuple) or not all(isinstance(item, RetrievedItem) for item in result):
            raise TypeError("retrieval callable must return tuple[RetrievedItem, ...]")
        return result[:limit]
