from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class Polarity(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATED = "NEGATED"
    UNKNOWN = "UNKNOWN"


class Modality(str, Enum):
    ASSERTED = "ASSERTED"
    POSSIBLE = "POSSIBLE"
    PROBABLE = "PROBABLE"
    NECESSARY = "NECESSARY"
    CONDITIONAL = "CONDITIONAL"
    COUNTERFACTUAL = "COUNTERFACTUAL"
    UNKNOWN = "UNKNOWN"


class MeaningRelation(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    CONTRADICTORY = "CONTRADICTORY"
    CONTEXTUAL_DIFFERENCE = "CONTEXTUAL_DIFFERENCE"
    DISTINCT_REFERENT = "DISTINCT_REFERENT"
    DISTINCT_CONSTRUCT = "DISTINCT_CONSTRUCT"
    DISTINCT_MEASUREMENT = "DISTINCT_MEASUREMENT"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class ScientificMeaningProjection:
    """A source-local linguistic/scientific meaning projection.

    This object is deliberately proposal-level. Extracting a predicate, referent,
    modality or measurement from text does not create scientific authority; it
    makes the interpretation coordinates explicit enough to challenge and map.
    """

    projection_id: str
    source_id: str
    source_span: str
    predicate: str
    argument_roles: tuple[tuple[str, str], ...] = ()
    referent_ids: tuple[str, ...] = ()
    construct_ids: tuple[str, ...] = ()
    measurement_ids: tuple[str, ...] = ()
    temporal_context_ids: tuple[str, ...] = ()
    discourse_relation: str = ""
    attribution_id: str = ""
    polarity: Polarity = Polarity.UNKNOWN
    modality: Modality = Modality.UNKNOWN
    assumption_ids: tuple[str, ...] = ()
    unresolved_ambiguities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        required = (self.projection_id, self.source_id, self.source_span, self.predicate)
        if any(not item.strip() for item in required):
            raise ValueError("meaning projection identity, source, span and predicate are required")
        role_ids = [role for role, _ in self.argument_roles]
        if len(role_ids) != len(set(role_ids)):
            raise ValueError("semantic argument roles must be unique within one projection")

    @property
    def context_ids(self) -> tuple[str, ...]:
        values = [
            f"polarity:{self.polarity.value}",
            f"modality:{self.modality.value}",
        ]
        if self.attribution_id:
            values.append(f"attribution:{self.attribution_id}")
        if self.discourse_relation:
            values.append(f"discourse:{self.discourse_relation}")
        values.extend(f"construct:{item}" for item in self.construct_ids)
        values.extend(f"measurement:{item}" for item in self.measurement_ids)
        values.extend(f"temporal:{item}" for item in self.temporal_context_ids)
        values.extend(f"assumption:{item}" for item in self.assumption_ids)
        return tuple(dict.fromkeys(values))


@dataclass(frozen=True)
class MeaningComparison:
    relation: MeaningRelation
    reasons: tuple[str, ...]

    @property
    def glue_eligible(self) -> bool:
        return self.relation is MeaningRelation.COMPATIBLE


def _same_or_empty(left: tuple[str, ...], right: tuple[str, ...]) -> bool:
    return not left or not right or left == right


def compare_meaning(
    left: ScientificMeaningProjection,
    right: ScientificMeaningProjection,
) -> MeaningComparison:
    """Conservative comparison used before a source-level GLUE hypothesis.

    It prefers contextual separation or UNRESOLVED over false equivalence. A
    contradiction is licensed only when the relevant identity/context
    coordinates align and asserted polarity differs.
    """

    if left.unresolved_ambiguities or right.unresolved_ambiguities:
        return MeaningComparison(
            MeaningRelation.UNRESOLVED,
            ("at least one source interpretation retains unresolved ambiguity",),
        )
    if left.predicate != right.predicate:
        return MeaningComparison(
            MeaningRelation.UNRESOLVED,
            ("predicates are not yet normalized to a shared relation",),
        )
    if left.referent_ids and right.referent_ids and left.referent_ids != right.referent_ids:
        return MeaningComparison(
            MeaningRelation.DISTINCT_REFERENT,
            ("same predicate is applied to different referents",),
        )
    if left.construct_ids and right.construct_ids and left.construct_ids != right.construct_ids:
        return MeaningComparison(
            MeaningRelation.DISTINCT_CONSTRUCT,
            ("apparent term/predicate refers to different scientific constructs",),
        )
    if left.measurement_ids and right.measurement_ids and left.measurement_ids != right.measurement_ids:
        return MeaningComparison(
            MeaningRelation.DISTINCT_MEASUREMENT,
            ("same construct is operationalized by different measurements",),
        )

    contextual_reasons: list[str] = []
    if not _same_or_empty(left.temporal_context_ids, right.temporal_context_ids):
        contextual_reasons.append("temporal/state context differs")
    if left.attribution_id and right.attribution_id and left.attribution_id != right.attribution_id:
        contextual_reasons.append("attribution/speaker differs")
    if (
        left.discourse_relation
        and right.discourse_relation
        and left.discourse_relation != right.discourse_relation
    ):
        contextual_reasons.append("discourse relation differs")
    if left.assumption_ids and right.assumption_ids and left.assumption_ids != right.assumption_ids:
        contextual_reasons.append("assumption context differs")

    if left.modality != right.modality:
        contextual_reasons.append("modal force differs")
    if contextual_reasons:
        return MeaningComparison(
            MeaningRelation.CONTEXTUAL_DIFFERENCE,
            tuple(contextual_reasons),
        )

    if (
        left.polarity is not Polarity.UNKNOWN
        and right.polarity is not Polarity.UNKNOWN
        and left.polarity != right.polarity
    ):
        if left.modality is Modality.ASSERTED and right.modality is Modality.ASSERTED:
            return MeaningComparison(
                MeaningRelation.CONTRADICTORY,
                ("aligned asserted propositions have opposite polarity",),
            )
        return MeaningComparison(
            MeaningRelation.CONTEXTUAL_DIFFERENCE,
            ("polarity differs under non-asserted/unknown modal force",),
        )

    return MeaningComparison(MeaningRelation.COMPATIBLE, ())


def bridge_compatible(
    left: ScientificMeaningProjection,
    right: ScientificMeaningProjection,
    *,
    pivot_referent_id: str,
) -> MeaningComparison:
    """Check whether two A-B/B-C projections really share the same B pivot."""

    if pivot_referent_id not in left.referent_ids or pivot_referent_id not in right.referent_ids:
        return MeaningComparison(
            MeaningRelation.DISTINCT_REFERENT,
            ("literature bridge does not share the declared pivot referent",),
        )
    if left.measurement_ids and right.measurement_ids and left.measurement_ids != right.measurement_ids:
        return MeaningComparison(
            MeaningRelation.DISTINCT_MEASUREMENT,
            ("bridge pivot is observed through incompatible operationalizations",),
        )
    if left.construct_ids and right.construct_ids and left.construct_ids != right.construct_ids:
        return MeaningComparison(
            MeaningRelation.DISTINCT_CONSTRUCT,
            ("bridge pivot labels distinct scientific constructs",),
        )
    return MeaningComparison(MeaningRelation.COMPATIBLE, ())


class ScientificLanguageInterpreter(Protocol):
    """Provider port for text -> typed meaning projection.

    An LLM, semantic parser or hybrid pipeline may implement this port. The
    returned projection remains proposal-level until mapped/verified downstream.
    """

    def project(self, *, source_id: str, text: str) -> tuple[ScientificMeaningProjection, ...]: ...


__all__ = [
    "MeaningComparison",
    "MeaningRelation",
    "Modality",
    "Polarity",
    "ScientificLanguageInterpreter",
    "ScientificMeaningProjection",
    "bridge_compatible",
    "compare_meaning",
]
