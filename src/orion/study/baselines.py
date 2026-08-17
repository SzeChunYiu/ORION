"""Resource-matched baseline integrations for ORION Paper 3.

Each baseline accepts source documents (list of dicts with text + metadata)
and returns structured integration results matching the annotation schema.

Resource-matching invariant: all baselines use the same frozen model family,
same context budget per case, and same retrieval allowance.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Sequence


# ── data types ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SourceDocument:
    """A frozen source document or span."""
    document_id: str
    document_version: str
    text: str
    discipline: str = ""
    span_start: int = 0
    span_end: int = 0
    text_hash: str = ""


@dataclass(frozen=True)
class IntegrationResult:
    """Structured integration result matching the annotation schema.

    This is the common output schema every baseline and ablation must produce.
    """
    system_id: str
    case_id: str
    mapping_relation: str = "UNRESOLVED"
    referent_relation: str = "UNRESOLVED"
    construct_relation: str = "UNRESOLVED"
    measurement_relation: str = "UNRESOLVED"
    context_relation: str = "UNRESOLVED"
    polarity_relation: str = "UNRESOLVED"
    modality_relation: str = "UNRESOLVED"
    attribution_relation: str = "UNRESOLVED"
    discourse_relation: str = "UNRESOLVED"
    contradiction_verdict: str = "UNRESOLVED"
    integration_verdict: str = "UNRESOLVED"
    preservation_conditions: tuple[str, ...] = ()
    recoverability_target: tuple[str, ...] = ()
    notes: str = ""


# ── abstract baseline ─────────────────────────────────────────────────────────

class Baseline(ABC):
    """Abstract base for all P3 baselines and ablations."""

    @abstractmethod
    def integrate(self, sources: Sequence[SourceDocument]) -> IntegrationResult:
        """Integrate a set of source documents into a single portrait entry."""

    @abstractmethod
    def system_id(self) -> str:
        """Unique identifier for this baseline (alphanumeric, no spaces)."""


# ── VanillaLongContext ────────────────────────────────────────────────────────

class VanillaLongContext(Baseline):
    """Baseline 1: concatenate all source documents into a single long context.

    No retrieval, no structure, no mapping types. The model sees the full text
    and produces a single integration verdict.
    """
    _id: str = "VanillaLongContext"

    def system_id(self) -> str:
        return self._id

    def integrate(self, sources: Sequence[SourceDocument]) -> IntegrationResult:
        # Placeholder — actual implementation calls the frozen model with
        # concatenated source texts and parses the structured output.
        return IntegrationResult(
            system_id=self._id,
            case_id="",
            notes="CONCATENATE_ALL_SOURCES",
        )


# ── ScientificRAG ─────────────────────────────────────────────────────────────

class ScientificRAG(Baseline):
    """Baseline 2: retrieve the most relevant passages per source document.

    Uses a frozen embedding model + vector store to retrieve K passages per
    source, then integrates from the retrieved subset.
    """
    _id: str = "ScientificRAG"

    def system_id(self) -> str:
        return self._id

    def integrate(self, sources: Sequence[SourceDocument]) -> IntegrationResult:
        return IntegrationResult(
            system_id=self._id,
            case_id="",
            notes="RETRIEVE_TOP_K",
        )


# ── CrossDomainRAG ────────────────────────────────────────────────────────────

class CrossDomainRAG(Baseline):
    """Baseline 3: cross-domain retrieval augmentation.

    Same as ScientificRAG but with domain-adapted embeddings and a cross-domain
    re-ranker stage.
    """
    _id: str = "CrossDomainRAG"

    def system_id(self) -> str:
        return self._id

    def integrate(self, sources: Sequence[SourceDocument]) -> IntegrationResult:
        return IntegrationResult(
            system_id=self._id,
            case_id="",
            notes="CROSS_DOMAIN_RETRIEVAL",
        )


# ── FlatUniversalSchema ───────────────────────────────────────────────────────

class FlatUniversalSchema(Baseline):
    """Baseline 4: map all information into a single flat universal schema.

    Ignores source boundaries and discipline-specific ontologies. Produces one
    merged representation without tracking provenance.
    """
    _id: str = "FlatUniversalSchema"

    def system_id(self) -> str:
        return self._id

    def integrate(self, sources: Sequence[SourceDocument]) -> IntegrationResult:
        return IntegrationResult(
            system_id=self._id,
            case_id="",
            notes="FLAT_UNIVERSAL_MERGE",
        )


# ── SCOPE_SCION_Like ──────────────────────────────────────────────────────────

class SCOPE_SCION_Like(Baseline):
    """Baseline 5: projection-based integration inspired by SCOPE/SCION.

    Maintains source-local projections with typed inter-source mappings.
    Similar to the ORION framework but without the full coordinate system.
    """
    _id: str = "SCOPE_SCION_Like"

    def system_id(self) -> str:
        return self._id

    def integrate(self, sources: Sequence[SourceDocument]) -> IntegrationResult:
        return IntegrationResult(
            system_id=self._id,
            case_id="",
            notes="PROJECTION_BASED",
        )


# ── ProvenanceSchema ──────────────────────────────────────────────────────────

class ProvenanceSchema(Baseline):
    """Baseline 6: provenance-first integration.

    Every integration decision is traced back to the exact source sentence.
    Sacrifices integration flexibility for strict lineage tracking.
    """
    _id: str = "ProvenanceSchema"

    def system_id(self) -> str:
        return self._id

    def integrate(self, sources: Sequence[SourceDocument]) -> IntegrationResult:
        return IntegrationResult(
            system_id=self._id,
            case_id="",
            notes="PROVENANCE_TRACKED",
        )


# ── all baselines ─────────────────────────────────────────────────────────────

ALL_BASELINES: list[Baseline] = [
    VanillaLongContext(),
    ScientificRAG(),
    CrossDomainRAG(),
    FlatUniversalSchema(),
    SCOPE_SCION_Like(),
    ProvenanceSchema(),
]

BASELINE_IDS: list[str] = [b.system_id() for b in ALL_BASELINES]