from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AssimilationOutcome(str, Enum):
    ALREADY_KNOWN = "ALREADY_KNOWN"
    EQUIVALENT_VIEW = "EQUIVALENT_VIEW"
    COMPLEMENTARY_FACET = "COMPLEMENTARY_FACET"
    REFINES_EXISTING_FACET = "REFINES_EXISTING_FACET"
    NEW_CONTEXT_COORDINATE = "NEW_CONTEXT_COORDINATE"
    NEW_REPRESENTATION = "NEW_REPRESENTATION"
    NEW_MECHANISM = "NEW_MECHANISM"
    CONTRADICTS_EXISTING = "CONTRADICTS_EXISTING"
    EXPOSES_ASSUMPTION = "EXPOSES_ASSUMPTION"
    EXPOSES_SEARCH_UNIVERSE_GAP = "EXPOSES_SEARCH_UNIVERSE_GAP"
    EXPOSES_METHOD_FAILURE = "EXPOSES_METHOD_FAILURE"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class KnowledgeContribution:
    contribution_id: str
    text: str
    assimilation: AssimilationOutcome
    evidence_ids: tuple[str, ...]
    discovered_domain_ids: tuple[str, ...] = ()
    representation_ids: tuple[str, ...] = ()
    contradicts_claim_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.contribution_id.strip() or not self.text.strip():
            raise ValueError("contribution identity and text are required")
        if not self.evidence_ids:
            raise ValueError("contribution must retain evidence provenance")
