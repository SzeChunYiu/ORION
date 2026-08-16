from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.core.contributions import (
    AssimilationOutcome,
    KnowledgeContribution,
    MappingRelation,
    ReferentBinding,
    ReferentResolution,
    RepresentationMapping,
)
from orion.core.problem import Problem
from orion.core.residuals import Residual, ResidualKind, Responsibility
from orion.core.search import RetrievedItem


class CompatibilityVerdict(str, Enum):
    UNMAPPED = "UNMAPPED"
    COMPATIBLE = "COMPATIBLE"
    PARTIAL = "PARTIAL"
    INCOMPATIBLE = "INCOMPATIBLE"


@dataclass(frozen=True)
class SourceProjection:
    projection_id: str
    contribution_id: str
    frame_id: str
    source_uri: str
    evidence_ids: tuple[str, ...]
    assimilation: AssimilationOutcome
    context_ids: tuple[str, ...] = ()
    related_claim_ids: tuple[str, ...] = ()
    referent_bindings: tuple[ReferentBinding, ...] = ()
    representation_mapping_ids: tuple[str, ...] = ()
    assumption_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        required = (
            self.projection_id,
            self.contribution_id,
            self.frame_id,
            self.source_uri,
        )
        if any(not item.strip() for item in required):
            raise ValueError("source projection identity, frame and source are required")
        if not self.evidence_ids:
            raise ValueError("source projection requires evidence provenance")


@dataclass(frozen=True)
class AssimilationEffect:
    integrate_claim: bool
    widen_search_universe: bool
    required_residual_kind: ResidualKind | None = None


_EFFECTS: dict[AssimilationOutcome, AssimilationEffect] = {
    AssimilationOutcome.ALREADY_KNOWN: AssimilationEffect(False, False),
    AssimilationOutcome.EQUIVALENT_VIEW: AssimilationEffect(False, False),
    AssimilationOutcome.COMPLEMENTARY_FACET: AssimilationEffect(True, True),
    AssimilationOutcome.REFINES_EXISTING_FACET: AssimilationEffect(True, True),
    AssimilationOutcome.NEW_CONTEXT_COORDINATE: AssimilationEffect(True, True),
    AssimilationOutcome.NEW_REPRESENTATION: AssimilationEffect(True, True),
    AssimilationOutcome.NEW_MECHANISM: AssimilationEffect(True, True),
    AssimilationOutcome.CONTRADICTS_EXISTING: AssimilationEffect(
        True,
        False,
        ResidualKind.CONTRADICTION,
    ),
    AssimilationOutcome.EXPOSES_ASSUMPTION: AssimilationEffect(
        True,
        False,
        ResidualKind.CONTEXT_GAP,
    ),
    AssimilationOutcome.EXPOSES_SEARCH_UNIVERSE_GAP: AssimilationEffect(
        True,
        True,
        ResidualKind.SEARCH_COVERAGE_FAILURE,
    ),
    AssimilationOutcome.EXPOSES_METHOD_FAILURE: AssimilationEffect(
        True,
        True,
        ResidualKind.METHOD_GAP,
    ),
    AssimilationOutcome.UNRESOLVED: AssimilationEffect(
        False,
        False,
        ResidualKind.CONTEXT_GAP,
    ),
}


def assimilation_effect(outcome: AssimilationOutcome) -> AssimilationEffect:
    return _EFFECTS[outcome]


def build_source_projection(
    contribution: KnowledgeContribution,
    item: RetrievedItem,
    problem: Problem,
) -> SourceProjection:
    """Bind one semantic interpretation back to its source and research frame."""

    if item.item_id not in contribution.evidence_ids:
        raise ValueError("contribution is not bound to the retrieved item it interprets")
    contexts = tuple(
        dict.fromkeys(
            (
                f"problem:{problem.problem_id}",
                *contribution.context_ids,
                *(f"domain:{item_id}" for item_id in item.domain_ids),
            )
        )
    )
    return SourceProjection(
        projection_id=f"projection:{contribution.contribution_id}",
        contribution_id=contribution.contribution_id,
        frame_id=f"problem:{problem.problem_id}",
        source_uri=item.source_uri,
        evidence_ids=contribution.evidence_ids,
        assimilation=contribution.assimilation,
        context_ids=contexts,
        related_claim_ids=contribution.related_claim_ids,
        referent_bindings=contribution.referent_bindings,
        representation_mapping_ids=tuple(
            item.mapping_id for item in contribution.representation_mappings
        ),
        assumption_ids=contribution.assumption_ids,
    )


def compatibility_of(
    mappings: tuple[RepresentationMapping, ...],
) -> CompatibilityVerdict:
    if not mappings:
        return CompatibilityVerdict.UNMAPPED
    relations = {item.relation for item in mappings}
    if MappingRelation.INCOMPATIBLE in relations:
        return CompatibilityVerdict.INCOMPATIBLE
    if relations <= {MappingRelation.EQUIVALENT, MappingRelation.REFINES}:
        return CompatibilityVerdict.COMPATIBLE
    return CompatibilityVerdict.PARTIAL


def representation_ids_for(
    contribution: KnowledgeContribution,
) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            (
                *contribution.representation_ids,
                *(
                    item.source_representation_id
                    for item in contribution.representation_mappings
                ),
                *(
                    item.target_representation_id
                    for item in contribution.representation_mappings
                ),
            )
        )
    )


def _residual(
    contribution: KnowledgeContribution,
    kind: ResidualKind,
    description: str,
    responsibilities: tuple[Responsibility, ...],
    suffix: str,
) -> Residual:
    return Residual(
        residual_id=(
            f"residual:assimilation:{contribution.contribution_id}:"
            f"{kind.value.lower()}:{suffix}"
        ),
        kind=kind,
        description=description,
        candidate_responsibilities=responsibilities,
        metadata=(
            ("contribution_id", contribution.contribution_id),
            ("assimilation", contribution.assimilation.value),
        ),
    )


def residuals_for_contribution(
    contribution: KnowledgeContribution,
) -> tuple[Residual, ...]:
    """Materialize deterministic residuals implied by typed assimilation evidence."""

    residuals: list[Residual] = []
    effect = assimilation_effect(contribution.assimilation)
    if effect.required_residual_kind is not None:
        responsibility = {
            ResidualKind.CONTRADICTION: (Responsibility.REPRESENTATION,),
            ResidualKind.CONTEXT_GAP: (Responsibility.QUESTION, Responsibility.EVIDENCE),
            ResidualKind.SEARCH_COVERAGE_FAILURE: (Responsibility.SEARCH,),
            ResidualKind.METHOD_GAP: (Responsibility.METHOD,),
        }[effect.required_residual_kind]
        residuals.append(
            _residual(
                contribution,
                effect.required_residual_kind,
                f"Assimilation outcome {contribution.assimilation.value} remains material.",
                responsibility,
                "outcome",
            )
        )

    unresolved_referents = tuple(
        item
        for item in contribution.referent_bindings
        if item.resolution is not ReferentResolution.RESOLVED
    )
    if unresolved_referents:
        labels = ", ".join(item.mention for item in unresolved_referents)
        residuals.append(
            _residual(
                contribution,
                ResidualKind.CONTEXT_GAP,
                f"Referent resolution remains open for: {labels}",
                (Responsibility.REPRESENTATION, Responsibility.EVIDENCE),
                "referent",
            )
        )

    compatibility = compatibility_of(contribution.representation_mappings)
    if compatibility is CompatibilityVerdict.INCOMPATIBLE:
        residuals.append(
            _residual(
                contribution,
                ResidualKind.REPRESENTATION_FAILURE,
                "At least one source-to-target representation mapping is incompatible.",
                (Responsibility.REPRESENTATION,),
                "mapping",
            )
        )
    elif (
        contribution.assimilation is AssimilationOutcome.NEW_REPRESENTATION
        and compatibility is CompatibilityVerdict.UNMAPPED
        and not contribution.representation_ids
    ):
        residuals.append(
            _residual(
                contribution,
                ResidualKind.REPRESENTATION_FAILURE,
                "A new representation was asserted without a representation identity or mapping.",
                (Responsibility.REPRESENTATION,),
                "unmapped",
            )
        )

    unique: dict[str, Residual] = {item.residual_id: item for item in residuals}
    return tuple(unique.values())


__all__ = [
    "AssimilationEffect",
    "CompatibilityVerdict",
    "SourceProjection",
    "assimilation_effect",
    "build_source_projection",
    "compatibility_of",
    "representation_ids_for",
    "residuals_for_contribution",
]
