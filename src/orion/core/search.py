from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchQuery:
    query_id: str
    text: str
    route_id: str
    domain_hint: str | None = None

    def __post_init__(self) -> None:
        if not self.query_id.strip() or not self.text.strip() or not self.route_id.strip():
            raise ValueError("query_id, text and route_id are required")


@dataclass(frozen=True)
class RetrievedItem:
    item_id: str
    content: str
    source_uri: str
    domain_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.item_id.strip() or not self.content.strip() or not self.source_uri.strip():
            raise ValueError("retrieved item identity, content and source are required")
