"""Load the frozen transfer literature matrix. No live arXiv queries."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

DISPOSITIONS = ("ADOPT", "ADAPT", "COMPOSE", "DEFER", "REJECT")

REQUIRED_SEARCH_TERMS = (
    "cross-domain agent memory transfer",
    "skill transfer language agents",
    "case-based reasoning transfer",
    "analogical transfer",
    "program synthesis component reuse",
    "algorithm selection meta-learning",
    "negative transfer",
    "transferability estimation",
    "software design pattern transfer",
    "assumption-aware transfer",
)


@dataclass(frozen=True)
class LiteratureRow:
    identifier: str
    title: str
    mechanism: str
    disposition: str
    local_source: str
    effect: str


@dataclass(frozen=True)
class LiteratureMatrix:
    source: str
    arxiv_api_queried: bool
    search_terms_covered: tuple[str, ...]
    consecutive_flat_rounds: int
    stop_rule: str
    rows: tuple[LiteratureRow, ...]

    @property
    def dispositions_used(self) -> tuple[str, ...]:
        return tuple(sorted({row.disposition for row in self.rows}))


def load_literature_matrix(path: Path) -> LiteratureMatrix:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("literature matrix must be an object")
    rows = tuple(
        LiteratureRow(
            identifier=str(item["identifier"]),
            title=str(item["title"]),
            mechanism=str(item["mechanism"]),
            disposition=str(item["disposition"]),
            local_source=str(item["local_source"]),
            effect=str(item["effect"]),
        )
        for item in raw["rows"]
    )
    return LiteratureMatrix(
        source=str(raw["source"]),
        arxiv_api_queried=bool(raw["arxiv_api_queried"]),
        search_terms_covered=tuple(raw["search_terms_covered"]),
        consecutive_flat_rounds=int(raw["consecutive_flat_rounds"]),
        stop_rule=str(raw["stop_rule"]),
        rows=rows,
    )
