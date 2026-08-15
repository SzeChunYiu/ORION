from __future__ import annotations

from typing import Protocol

from orion.core.search import RetrievedItem, SearchQuery


class RetrievalProvider(Protocol):
    def search(self, query: SearchQuery, *, limit: int) -> tuple[RetrievedItem, ...]:
        ...
