"""Independent public-reference scorer for ORION-P3 Phase A.

This module implements the written mapping decision specification frozen in
``P3.coordinate-obstruction.v2`` / the V1 annotation handbook order. It may
import projection *schemas* and parsers. It must not import ``compare_meaning``
or ``evaluate_case``; those are the incumbent evaluator under audit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

from orion.knowledge.semantics import (
    MeaningRelation,
    Modality,
    Polarity,
    ScientificMeaningProjection,
)
from orion.study.p3_public_reference import projection_from_dict, validate_case

GLUE = "GLUE"
OBSTRUCTION = "OBSTRUCTION"
UNRESOLVED = "UNRESOLVED"

NONMERGE_TO_OBSTRUCTION = {
    MeaningRelation.CONTRADICTORY,
    MeaningRelation.CONTEXTUAL_DIFFERENCE,
    MeaningRelation.DISTINCT_REFERENT,
    MeaningRelation.DISTINCT_CONSTRUCT,
    MeaningRelation.DISTINCT_MEASUREMENT,
}


class IndependentEvaluator(Protocol):
    """Second scorer from the written decision specification."""

    def score(self, case: Mapping[str, object]) -> IndependentScore: ...


@dataclass(frozen=True)
class IndependentScore:
    case_id: str
    meaning_relation: str
    integration_verdict: str
    reasons: tuple[str, ...]


def integration_verdict_for(relation: MeaningRelation) -> str:
    if relation is MeaningRelation.COMPATIBLE:
        return GLUE
    if relation is MeaningRelation.UNRESOLVED:
        return UNRESOLVED
    if relation in NONMERGE_TO_OBSTRUCTION:
        return OBSTRUCTION
    return UNRESOLVED


def _both_nonempty_and_unequal(left: tuple[str, ...], right: tuple[str, ...]) -> bool:
    return bool(left) and bool(right) and left != right


def _temporal_differs(left: tuple[str, ...], right: tuple[str, ...]) -> bool:
    """Written spec: a missing temporal coordinate does not license a difference."""
    if not left or not right:
        return False
    return left != right


def score_projections(
    left: ScientificMeaningProjection,
    right: ScientificMeaningProjection,
) -> tuple[MeaningRelation, tuple[str, ...]]:
    """Walk the frozen coordinate order: identity, operationalization, context, polarity."""

    if left.unresolved_ambiguities or right.unresolved_ambiguities:
        return MeaningRelation.UNRESOLVED, (
            "at least one source interpretation retains unresolved ambiguity",
        )
    if left.predicate != right.predicate:
        return MeaningRelation.UNRESOLVED, (
            "predicates are not yet normalized to a shared relation",
        )
    if _both_nonempty_and_unequal(left.referent_ids, right.referent_ids):
        return MeaningRelation.DISTINCT_REFERENT, (
            "same predicate is applied to different referents",
        )
    if _both_nonempty_and_unequal(left.construct_ids, right.construct_ids):
        return MeaningRelation.DISTINCT_CONSTRUCT, (
            "apparent term/predicate refers to different scientific constructs",
        )
    if _both_nonempty_and_unequal(left.measurement_ids, right.measurement_ids):
        return MeaningRelation.DISTINCT_MEASUREMENT, (
            "same construct is operationalized by different measurements",
        )

    reasons: list[str] = []
    if _temporal_differs(left.temporal_context_ids, right.temporal_context_ids):
        reasons.append("temporal/state context differs")
    if left.attribution_id and right.attribution_id and left.attribution_id != right.attribution_id:
        reasons.append("attribution/speaker differs")
    if (
        left.discourse_relation
        and right.discourse_relation
        and left.discourse_relation != right.discourse_relation
    ):
        reasons.append("discourse relation differs")
    if _both_nonempty_and_unequal(left.assumption_ids, right.assumption_ids):
        reasons.append("assumption context differs")
    if left.modality != right.modality:
        reasons.append("modal force differs")
    if reasons:
        return MeaningRelation.CONTEXTUAL_DIFFERENCE, tuple(reasons)

    polarities_known = (
        left.polarity is not Polarity.UNKNOWN and right.polarity is not Polarity.UNKNOWN
    )
    if polarities_known and left.polarity != right.polarity:
        if left.modality is Modality.ASSERTED and right.modality is Modality.ASSERTED:
            return MeaningRelation.CONTRADICTORY, (
                "aligned asserted propositions have opposite polarity",
            )
        return MeaningRelation.CONTEXTUAL_DIFFERENCE, (
            "polarity differs under non-asserted/unknown modal force",
        )
    return MeaningRelation.COMPATIBLE, ()


class HandbookOrderEvaluator:
    """Independent evaluator bound to the annotation-handbook coordinate order."""

    def score(self, case: Mapping[str, object]) -> IndependentScore:
        validated = validate_case(dict(case))
        left = projection_from_dict(validated["left_projection"])
        right = projection_from_dict(validated["right_projection"])
        relation, reasons = score_projections(left, right)
        return IndependentScore(
            case_id=str(validated["case_id"]),
            meaning_relation=relation.value,
            integration_verdict=integration_verdict_for(relation),
            reasons=reasons,
        )


DEFAULT_INDEPENDENT_EVALUATOR: IndependentEvaluator = HandbookOrderEvaluator()
