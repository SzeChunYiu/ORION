from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SearchRouteKind(str, Enum):
    """Independent route families used to challenge the current search basis."""

    CURRENT_VOCABULARY = "CURRENT_VOCABULARY"
    LEXICAL_VARIANT = "LEXICAL_VARIANT"
    FUNCTION_ONLY = "FUNCTION_ONLY"
    PARENT_DISCIPLINE = "PARENT_DISCIPLINE"
    CROSS_DOMAIN = "CROSS_DOMAIN"
    LITERATURE_BRIDGE = "LITERATURE_BRIDGE"
    CITATION_NEIGHBORHOOD = "CITATION_NEIGHBORHOOD"
    ADVERSARIAL_OMISSION = "ADVERSARIAL_OMISSION"
    FRESHNESS = "FRESHNESS"


@dataclass(frozen=True)
class SearchQuery:
    query_id: str
    text: str
    route_id: str
    route_kind: SearchRouteKind
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
