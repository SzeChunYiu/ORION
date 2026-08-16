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


class ReferentResolution(str, Enum):
    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class ReferentBinding:
    mention: str
    resolution: ReferentResolution
    referent_id: str = ""
    context_id: str = ""

    def __post_init__(self) -> None:
        if not self.mention.strip():
            raise ValueError("referent binding requires a mention")
        if self.resolution is ReferentResolution.RESOLVED and not self.referent_id.strip():
            raise ValueError("resolved referent binding requires a referent id")


class MappingRelation(str, Enum):
    EQUIVALENT = "EQUIVALENT"
    REFINES = "REFINES"
    COMPLEMENTS = "COMPLEMENTS"
    CONTEXTUAL = "CONTEXTUAL"
    INCOMPATIBLE = "INCOMPATIBLE"


@dataclass(frozen=True)
class RepresentationMapping:
    mapping_id: str
    source_representation_id: str
    target_representation_id: str
    relation: MappingRelation
    evidence_ids: tuple[str, ...]
    recoverable: bool = True

    def __post_init__(self) -> None:
        required = (
            self.mapping_id,
            self.source_representation_id,
            self.target_representation_id,
        )
        if any(not item.strip() for item in required):
            raise ValueError("representation mapping identity and endpoints are required")
        if not self.evidence_ids:
            raise ValueError("representation mapping requires evidence provenance")
        if self.target_representation_id.startswith("orion:") and not self.recoverable:
            raise ValueError(
                "an ORION-native representation must remain recoverable to its source"
            )


@dataclass(frozen=True)
class KnowledgeContribution:
    contribution_id: str
    text: str
    assimilation: AssimilationOutcome
    evidence_ids: tuple[str, ...]
    discovered_domain_ids: tuple[str, ...] = ()
    representation_ids: tuple[str, ...] = ()
    contradicts_claim_ids: tuple[str, ...] = ()
    related_claim_ids: tuple[str, ...] = ()
    context_ids: tuple[str, ...] = ()
    referent_bindings: tuple[ReferentBinding, ...] = ()
    representation_mappings: tuple[RepresentationMapping, ...] = ()
    assumption_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.contribution_id.strip() or not self.text.strip():
            raise ValueError("contribution identity and text are required")
        if not self.evidence_ids:
            raise ValueError("contribution must retain evidence provenance")
        mapping_ids = [item.mapping_id for item in self.representation_mappings]
        if len(mapping_ids) != len(set(mapping_ids)):
            raise ValueError("representation mapping ids must be unique per contribution")
