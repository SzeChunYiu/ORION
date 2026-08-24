"""Fail-closed structural donor assimilation for issue #454.

Companion to ``scientific_structure_assimilation`` -- the frozen first-wave A-G
receipts schema that ``research/structural-assimilation-v1`` seals against.  This
variant keeps the same fail-closed purpose with a stricter draft shape:
free-form per-coordinate records, a four-level source-access enum, and finding
kinds shared with the mechanism-assimilation authority ladder.

A paper can change ORION's scientific framing before any individual algorithm is
copied.  This module records that framing without turning it into ORION novelty or
scientific authority.  The receipt is deliberately stricter than a citation or a
paper-level ADOPT label: it separates ontology, explanation, failure, revision,
inquiry, preservation, and authority commitments, records coordinate-level
structural dispositions, and requires an observable programme consequence (or an
explicit no-change reason).

The receipt is a research-discipline object.  It never validates the donor's
scientific claims and never authorizes an ORION mutation, result, or publication
claim.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from orion.knowledge.mechanism_assimilation import (
    AssimilationAuthority,
    authority_rank,
)
from orion.novelty.hashing import sha256_canonical

SCHEMA_ID = "orion.scientific-structure-assimilation-receipt.v1"


class StructuralDisposition(str, Enum):
    ADOPT_STRUCTURE = "ADOPT_STRUCTURE"
    ADAPT_STRUCTURE = "ADAPT_STRUCTURE"
    COMPOSE_STRUCTURES = "COMPOSE_STRUCTURES"
    CONFLICT = "CONFLICT"
    ORTHOGONAL = "ORTHOGONAL"
    DEFER_CANNOT_CHECK = "DEFER/CANNOT_CHECK"


class StructuralSourceAccess(str, Enum):
    FULL_TEXT_PRIMARY = "FULL_TEXT_PRIMARY"
    PRIMARY_RECORD_ONLY = "PRIMARY_RECORD_ONLY"
    SECONDARY_ONLY = "SECONDARY_ONLY"
    UNREACHABLE = "UNREACHABLE"


class StructuralScope(str, Enum):
    DOMAIN_SPECIFIC = "DOMAIN_SPECIFIC"
    MULTI_DOMAIN = "MULTI_DOMAIN"
    GENERAL_FRAMEWORK = "GENERAL_FRAMEWORK"


class StructuralFindingKind(str, Enum):
    SOURCE_INSUFFICIENT = "SOURCE_INSUFFICIENT"
    ALGORITHM_ONLY_ABSORPTION = "ALGORITHM_ONLY_ABSORPTION"
    PHILOSOPHY_LAUNDERING = "PHILOSOPHY_LAUNDERING"
    CONFLICT_WITHOUT_DISCRIMINATOR = "CONFLICT_WITHOUT_DISCRIMINATOR"
    AUTHORITY_ESCALATION = "AUTHORITY_ESCALATION"
    PRESERVATION_ERASURE = "PRESERVATION_ERASURE"
    SCOPE_LAUNDERING = "SCOPE_LAUNDERING"
    CITATION_ONLY_RECEIPT = "CITATION_ONLY_RECEIPT"


class StructuralAssimilationVerdict(str, Enum):
    ADMITTED = "ADMITTED"
    BLOCKED = "BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class StructuralSource:
    source_id: str
    title: str
    version: str
    source_uri: str
    access: StructuralSourceAccess
    source_scope: StructuralScope

    def __post_init__(self) -> None:
        for value, name in (
            (self.source_id, "source_id"),
            (self.title, "title"),
            (self.version, "version"),
            (self.source_uri, "source_uri"),
        ):
            if not value.strip():
                raise ValueError(f"{name} must be non-empty")
        object.__setattr__(self, "access", StructuralSourceAccess(self.access))
        object.__setattr__(self, "source_scope", StructuralScope(self.source_scope))


@dataclass(frozen=True)
class StructuralCoordinate:
    coordinate_id: str
    donor_commitment: str
    disposition: StructuralDisposition
    rationale: str

    def __post_init__(self) -> None:
        if not self.coordinate_id.strip() or not self.donor_commitment.strip() or not self.rationale.strip():
            raise ValueError("structural coordinate requires id, donor commitment, and rationale")
        object.__setattr__(self, "disposition", StructuralDisposition(self.disposition))


@dataclass(frozen=True)
class ScientificStructureAssimilationDraft:
    receipt_id: str
    source: StructuralSource
    scientific_ontology: tuple[str, ...]
    explanation_commitments: tuple[str, ...]
    failure_semantics: tuple[str, ...]
    revision_semantics: tuple[str, ...]
    inquiry_semantics: tuple[str, ...]
    evidence_authority_semantics: tuple[str, ...]
    preservation_obligations: tuple[str, ...]
    coordinates: tuple[StructuralCoordinate, ...]
    adopted_donor_claims: tuple[str, ...]
    retained_orion_residuals: tuple[str, ...]
    downstream_consequences: tuple[str, ...]
    conflicts: tuple[str, ...] = ()
    conflict_discriminators: tuple[str, ...] = ()
    no_change_reason: str = ""
    donor_authority: AssimilationAuthority = AssimilationAuthority.DESCRIPTIVE
    claimed_orion_authority: AssimilationAuthority = AssimilationAuthority.DESCRIPTIVE
    claimed_orion_scope: StructuralScope = StructuralScope.DOMAIN_SPECIFIC

    def __post_init__(self) -> None:
        if not self.receipt_id.strip():
            raise ValueError("receipt_id must be non-empty")
        object.__setattr__(self, "donor_authority", AssimilationAuthority(self.donor_authority))
        object.__setattr__(self, "claimed_orion_authority", AssimilationAuthority(self.claimed_orion_authority))
        object.__setattr__(self, "claimed_orion_scope", StructuralScope(self.claimed_orion_scope))


@dataclass(frozen=True)
class StructuralFinding:
    kind: StructuralFindingKind
    detail: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", StructuralFindingKind(self.kind))
        if not self.detail.strip():
            raise ValueError("finding detail must be non-empty")


@dataclass(frozen=True)
class ScientificStructureAssimilationReceipt:
    schema_id: str
    receipt_id: str
    source: StructuralSource
    coordinates: tuple[StructuralCoordinate, ...]
    adopted_donor_claims: tuple[str, ...]
    retained_orion_residuals: tuple[str, ...]
    downstream_consequences: tuple[str, ...]
    findings: tuple[StructuralFinding, ...]
    verdict: StructuralAssimilationVerdict
    verdict_reasons: tuple[str, ...]
    content_hash: str = field(default="")

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    @property
    def grants_novelty_authority(self) -> bool:
        return False

    @property
    def self_authorizing(self) -> bool:
        return False


def _norm(value: str) -> str:
    return " ".join(value.casefold().split())


def assess_structural_assimilation(
    draft: ScientificStructureAssimilationDraft,
) -> tuple[StructuralFinding, ...]:
    findings: list[StructuralFinding] = []

    core_groups = (
        draft.scientific_ontology,
        draft.explanation_commitments,
        draft.failure_semantics,
        draft.revision_semantics,
        draft.inquiry_semantics,
        draft.evidence_authority_semantics,
    )
    if any(not group for group in core_groups) or not draft.coordinates:
        findings.append(
            StructuralFinding(
                StructuralFindingKind.ALGORITHM_ONLY_ABSORPTION,
                "receipt omits at least one structural commitment family or has no coordinate-level dispositions",
            )
        )

    adopted = {_norm(value) for value in draft.adopted_donor_claims}
    residuals = {_norm(value) for value in draft.retained_orion_residuals}
    overlap = sorted(adopted & residuals)
    if overlap:
        findings.append(
            StructuralFinding(
                StructuralFindingKind.PHILOSOPHY_LAUNDERING,
                "donor-owned structural claims are simultaneously retained as ORION residuals: " + "; ".join(overlap),
            )
        )

    if draft.conflicts and not draft.conflict_discriminators:
        findings.append(
            StructuralFinding(
                StructuralFindingKind.CONFLICT_WITHOUT_DISCRIMINATOR,
                "incompatible structural assumptions were recorded without a discriminator/countermodel",
            )
        )

    if authority_rank(draft.claimed_orion_authority) > authority_rank(draft.donor_authority):
        findings.append(
            StructuralFinding(
                StructuralFindingKind.AUTHORITY_ESCALATION,
                f"donor authority {draft.donor_authority.value} was escalated to {draft.claimed_orion_authority.value}",
            )
        )

    if draft.revision_semantics and not draft.preservation_obligations:
        findings.append(
            StructuralFinding(
                StructuralFindingKind.PRESERVATION_ERASURE,
                "revision semantics are recorded without stating what survives/reopens across revision",
            )
        )

    if (
        draft.source.source_scope is StructuralScope.DOMAIN_SPECIFIC
        and draft.claimed_orion_scope is StructuralScope.GENERAL_FRAMEWORK
    ):
        findings.append(
            StructuralFinding(
                StructuralFindingKind.SCOPE_LAUNDERING,
                "domain-specific donor evidence was promoted directly to a general-framework ORION claim",
            )
        )

    if not draft.downstream_consequences and not draft.no_change_reason.strip():
        findings.append(
            StructuralFinding(
                StructuralFindingKind.CITATION_ONLY_RECEIPT,
                "receipt records no protocol/baseline/claim/ownership consequence and no explicit NO_CHANGE reason",
            )
        )

    return tuple(findings)


def seal_structural_assimilation(
    draft: ScientificStructureAssimilationDraft,
) -> ScientificStructureAssimilationReceipt:
    """Seal a non-authorizing structural receipt.

    Internal hostile findings are definite defects and therefore BLOCK.  A clean
    receipt based on less than a readable primary full text remains CANNOT_CHECK;
    a title, abstract, programme listing, or secondary summary cannot establish a
    paper's full scientific commitments.
    """

    findings = assess_structural_assimilation(draft)
    reasons: list[str] = []
    if findings:
        verdict = StructuralAssimilationVerdict.BLOCKED
        reasons.extend(f"{finding.kind.value}: {finding.detail}" for finding in findings)
    elif draft.source.access is not StructuralSourceAccess.FULL_TEXT_PRIMARY:
        verdict = StructuralAssimilationVerdict.CANNOT_CHECK
        reasons.append(
            "full primary text was not available; structure may be routed as DEFER but cannot be admitted"
        )
    else:
        verdict = StructuralAssimilationVerdict.ADMITTED
        reasons.append("primary full text read and all structural hostile checks passed")

    receipt = ScientificStructureAssimilationReceipt(
        schema_id=SCHEMA_ID,
        receipt_id=draft.receipt_id,
        source=draft.source,
        coordinates=draft.coordinates,
        adopted_donor_claims=draft.adopted_donor_claims,
        retained_orion_residuals=draft.retained_orion_residuals,
        downstream_consequences=draft.downstream_consequences,
        findings=findings,
        verdict=verdict,
        verdict_reasons=tuple(reasons),
    )
    return ScientificStructureAssimilationReceipt(
        **{**receipt.__dict__, "content_hash": sha256_canonical(receipt)}
    )
