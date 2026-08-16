from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class WorkRelation(str, Enum):
    """Typed relationship between ORION's candidate claim and one external work."""

    PRECURSOR = "PRECURSOR"
    OVERLAPS = "OVERLAPS"
    COMPLEMENTARY = "COMPLEMENTARY"
    STRONGER_ON_AXIS = "STRONGER_ON_AXIS"
    WEAKER_ON_AXIS = "WEAKER_ON_AXIS"
    SUBSUMES_CANDIDATE = "SUBSUMES_CANDIDATE"
    ORTHOGONAL = "ORTHOGONAL"


class AbsorptionDisposition(str, Enum):
    """What ORION should do with a useful mechanism from nearest work."""

    ADOPT = "ADOPT"
    ADAPT = "ADAPT"
    COMPOSE = "COMPOSE"
    DEFER = "DEFER"
    REJECT = "REJECT"


class NoveltyVerdict(str, Enum):
    """Novelty is always a scoped comparison verdict, never an authority upgrade."""

    BLOCKED_NO_NEAREST_WORK = "BLOCKED_NO_NEAREST_WORK"
    BLOCKED_SEARCH_OPEN = "BLOCKED_SEARCH_OPEN"
    BLOCKED_NO_FALSIFIER = "BLOCKED_NO_FALSIFIER"
    SUBSUMED = "SUBSUMED"
    CANDIDATE_DELTA = "CANDIDATE_DELTA"


@dataclass(frozen=True)
class ExternalMechanism:
    work_id: str
    mechanism_id: str
    description: str
    evidence_refs: tuple[str, ...]
    assumptions: tuple[str, ...] = ()
    strengths: tuple[str, ...] = ()
    failure_modes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.work_id.strip() or not self.mechanism_id.strip() or not self.description.strip():
            raise ValueError("nearest-work mechanism requires work, mechanism and description")
        if not self.evidence_refs or any(not ref.strip() for ref in self.evidence_refs):
            raise ValueError("nearest-work mechanisms require evidence references")


@dataclass(frozen=True)
class AbsorptionDecision:
    mechanism_id: str
    disposition: AbsorptionDisposition
    target_mechanic_ids: tuple[str, ...]
    rationale: str
    preserved_constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.mechanism_id.strip() or not self.rationale.strip():
            raise ValueError("absorption decision requires mechanism and rationale")
        if self.disposition in {
            AbsorptionDisposition.ADOPT,
            AbsorptionDisposition.ADAPT,
            AbsorptionDisposition.COMPOSE,
        } and not self.target_mechanic_ids:
            raise ValueError("absorbed mechanisms require at least one ORION target")


@dataclass(frozen=True)
class NearestWorkComparison:
    work_id: str
    relation: WorkRelation
    absorbed_mechanism_ids: tuple[str, ...]
    residual_delta_ids: tuple[str, ...]
    note: str

    def __post_init__(self) -> None:
        if not self.work_id.strip() or not self.note.strip():
            raise ValueError("nearest-work comparison requires work identity and note")


@dataclass(frozen=True)
class NoveltyCase:
    paper_id: str
    target_claim: str
    comparisons: tuple[NearestWorkComparison, ...]
    candidate_delta_ids: tuple[str, ...]
    falsifier_ids: tuple[str, ...]
    unresolved_route_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.paper_id.strip() or not self.target_claim.strip():
            raise ValueError("novelty case requires paper identity and target claim")
        comparison_ids = [comparison.work_id for comparison in self.comparisons]
        if len(set(comparison_ids)) != len(comparison_ids):
            raise ValueError("nearest-work comparisons must be unique by work")
        if len(set(self.candidate_delta_ids)) != len(self.candidate_delta_ids):
            raise ValueError("candidate deltas must be unique")


@dataclass(frozen=True)
class NoveltyAssessment:
    verdict: NoveltyVerdict
    nearest_work_count: int
    absorbed_mechanism_count: int
    candidate_delta_ids: tuple[str, ...]
    reasons: tuple[str, ...]

    @property
    def publication_novelty_authorized(self) -> bool:
        """A research comparison may nominate novelty; it never certifies publication novelty."""

        return False


def validate_absorption(
    mechanisms: tuple[ExternalMechanism, ...],
    decisions: tuple[AbsorptionDecision, ...],
) -> None:
    mechanism_ids = {mechanism.mechanism_id for mechanism in mechanisms}
    if len(mechanism_ids) != len(mechanisms):
        raise ValueError("nearest-work mechanism ids must be unique")
    decision_ids = [decision.mechanism_id for decision in decisions]
    if len(set(decision_ids)) != len(decision_ids):
        raise ValueError("each mechanism may receive at most one absorption decision")
    unknown = tuple(sorted(set(decision_ids) - mechanism_ids))
    if unknown:
        raise ValueError(f"absorption decision references unknown mechanisms: {unknown}")


def assess_novelty_case(case: NoveltyCase) -> NoveltyAssessment:
    """Fail-closed novelty comparison after nearest-work absorption.

    The result is intentionally weaker than a publication claim.  A candidate delta
    is reportable only after at least one nearest work has been compared, the declared
    nearest-work/search routes are closed for the scoped claim, and a falsifier exists.
    If a nearest work already subsumes the claim and no distinct delta survives,
    the case is explicitly SUBSUMED rather than rebranded.
    """

    absorbed = tuple(
        dict.fromkeys(
            mechanism_id
            for comparison in case.comparisons
            for mechanism_id in comparison.absorbed_mechanism_ids
        )
    )
    if not case.comparisons:
        return NoveltyAssessment(
            NoveltyVerdict.BLOCKED_NO_NEAREST_WORK,
            0,
            len(absorbed),
            case.candidate_delta_ids,
            ("no nearest work has been compared",),
        )
    if case.unresolved_route_ids:
        return NoveltyAssessment(
            NoveltyVerdict.BLOCKED_SEARCH_OPEN,
            len(case.comparisons),
            len(absorbed),
            case.candidate_delta_ids,
            tuple(f"nearest-work route remains open: {route}" for route in case.unresolved_route_ids),
        )
    if not case.falsifier_ids:
        return NoveltyAssessment(
            NoveltyVerdict.BLOCKED_NO_FALSIFIER,
            len(case.comparisons),
            len(absorbed),
            case.candidate_delta_ids,
            ("candidate novelty has no registered falsifier",),
        )
    if any(
        comparison.relation is WorkRelation.SUBSUMES_CANDIDATE
        for comparison in case.comparisons
    ) and not case.candidate_delta_ids:
        return NoveltyAssessment(
            NoveltyVerdict.SUBSUMED,
            len(case.comparisons),
            len(absorbed),
            (),
            ("nearest work already subsumes the scoped candidate claim",),
        )
    if not case.candidate_delta_ids:
        return NoveltyAssessment(
            NoveltyVerdict.SUBSUMED,
            len(case.comparisons),
            len(absorbed),
            (),
            ("no decision-relevant delta survives nearest-work comparison",),
        )
    return NoveltyAssessment(
        NoveltyVerdict.CANDIDATE_DELTA,
        len(case.comparisons),
        len(absorbed),
        case.candidate_delta_ids,
        (
            "a scoped difference survives nearest-work comparison",
            "the difference remains a candidate until its falsifier and fresh evaluation are executed",
        ),
    )


__all__ = [
    "AbsorptionDecision",
    "AbsorptionDisposition",
    "ExternalMechanism",
    "NearestWorkComparison",
    "NoveltyAssessment",
    "NoveltyCase",
    "NoveltyVerdict",
    "WorkRelation",
    "assess_novelty_case",
    "validate_absorption",
]
