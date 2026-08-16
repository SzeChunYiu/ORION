from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from orion.core.search import SearchRouteKind


class IgnoranceKind(str, Enum):
    """Minimal action-relevant classes for source-local known unknowns."""

    FULL_UNKNOWN = "FULL_UNKNOWN"
    EXPLICIT_QUESTION = "EXPLICIT_QUESTION"
    INCOMPLETE_EVIDENCE = "INCOMPLETE_EVIDENCE"
    INDEFINITE_RELATIONSHIP = "INDEFINITE_RELATIONSHIP"
    ALTERNATIVE_OR_CONTROVERSY = "ALTERNATIVE_OR_CONTROVERSY"
    ANOMALOUS_OBSERVATION = "ANOMALOUS_OBSERVATION"
    RESEARCH_BARRIER = "RESEARCH_BARRIER"
    FUTURE_RESEARCH = "FUTURE_RESEARCH"


class IgnoranceAction(str, Enum):
    SEARCH_EVIDENCE = "SEARCH_EVIDENCE"
    OPEN_SUBQUESTION = "OPEN_SUBQUESTION"
    DESIGN_DISCRIMINATOR = "DESIGN_DISCRIMINATOR"
    REPLICATE_OR_EXPERIMENT = "REPLICATE_OR_EXPERIMENT"
    REPAIR_RESEARCH_BARRIER = "REPAIR_RESEARCH_BARRIER"
    RETAIN_FUTURE_WORK_CANDIDATE = "RETAIN_FUTURE_WORK_CANDIDATE"


@dataclass(frozen=True)
class IgnoranceProjection:
    """A source-local statement of missing/incomplete scientific knowledge.

    The projection records what *this source* says is unknown and the knowledge
    goal it implies. It is never proof that the gap is globally real, current or
    exhaustive. Promotion to an ORION residual requires independent evidence and
    the ordinary authority/diagnosis machinery.
    """

    projection_id: str
    source_id: str
    source_span: str
    kind: IgnoranceKind
    knowledge_goal: str
    subject_ids: tuple[str, ...] = ()
    context_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    source_taxonomy_label: str = ""
    uncertainty_note: str = ""

    def __post_init__(self) -> None:
        required = (
            self.projection_id,
            self.source_id,
            self.source_span,
            self.knowledge_goal,
        )
        if any(not item.strip() for item in required):
            raise ValueError("ignorance projection identity/source/span/knowledge goal are required")
        if self.evidence_ids and any(not item.strip() for item in self.evidence_ids):
            raise ValueError("ignorance evidence ids must be non-empty")

    @property
    def asserts_global_gap(self) -> bool:
        return False


@dataclass(frozen=True)
class IgnoranceActionPlan:
    projection_id: str
    action: IgnoranceAction
    route_kind: SearchRouteKind | None
    rationale: str
    requires_independent_confirmation: bool = True
    creates_scientific_authority: bool = False


_ACTIONS: dict[IgnoranceKind, tuple[IgnoranceAction, SearchRouteKind | None, str]] = {
    IgnoranceKind.FULL_UNKNOWN: (
        IgnoranceAction.SEARCH_EVIDENCE,
        SearchRouteKind.FUNCTION_ONLY,
        "A source reports a substantial unknown; search independently before treating it as a current gap.",
    ),
    IgnoranceKind.EXPLICIT_QUESTION: (
        IgnoranceAction.OPEN_SUBQUESTION,
        SearchRouteKind.PARENT_DISCIPLINE,
        "Preserve the explicit inquiry as a candidate child question and seek mature parent-domain treatments.",
    ),
    IgnoranceKind.INCOMPLETE_EVIDENCE: (
        IgnoranceAction.SEARCH_EVIDENCE,
        SearchRouteKind.CITATION_NEIGHBORHOOD,
        "The stated deficiency is evidential; acquire independent and newer evidence rather than rewriting the framework.",
    ),
    IgnoranceKind.INDEFINITE_RELATIONSHIP: (
        IgnoranceAction.DESIGN_DISCRIMINATOR,
        SearchRouteKind.LITERATURE_BRIDGE,
        "An underspecified relationship calls for competing relation hypotheses and a separating observation.",
    ),
    IgnoranceKind.ALTERNATIVE_OR_CONTROVERSY: (
        IgnoranceAction.DESIGN_DISCRIMINATOR,
        SearchRouteKind.ADVERSARIAL_OMISSION,
        "Contested alternatives require explicit competing hypotheses and evidence that could discriminate them.",
    ),
    IgnoranceKind.ANOMALOUS_OBSERVATION: (
        IgnoranceAction.REPLICATE_OR_EXPERIMENT,
        None,
        "An anomalous/curious result should be replicated or experimentally discriminated before theory change.",
    ),
    IgnoranceKind.RESEARCH_BARRIER: (
        IgnoranceAction.REPAIR_RESEARCH_BARRIER,
        SearchRouteKind.IMPLEMENTATION_ANALOG,
        "A stated methodological/instrumental barrier should trigger tool, measurement or method repair research.",
    ),
    IgnoranceKind.FUTURE_RESEARCH: (
        IgnoranceAction.RETAIN_FUTURE_WORK_CANDIDATE,
        SearchRouteKind.FRESHNESS,
        "Future-work language is a source proposal; retain and check freshness/relevance without manufacturing a global gap.",
    ),
}


def plan_for_ignorance(projection: IgnoranceProjection) -> IgnoranceActionPlan:
    action, route, rationale = _ACTIONS[projection.kind]
    return IgnoranceActionPlan(
        projection_id=projection.projection_id,
        action=action,
        route_kind=route,
        rationale=rationale,
    )


def deduplicate_ignorance(
    projections: tuple[IgnoranceProjection, ...],
) -> tuple[IgnoranceProjection, ...]:
    """Deduplicate exact source-local claims without merging distinct contexts.

    Same subject/kind/goal from different sources is retained because independent
    source projections are evidence about recurrence, not duplicate storage.
    """

    seen: set[tuple[str, str, IgnoranceKind, str, tuple[str, ...]]] = set()
    retained: list[IgnoranceProjection] = []
    for item in projections:
        key = (
            item.source_id,
            item.source_span,
            item.kind,
            item.knowledge_goal,
            item.context_ids,
        )
        if key in seen:
            continue
        seen.add(key)
        retained.append(item)
    return tuple(retained)


class ScientificIgnoranceInterpreter(Protocol):
    """Provider port for text -> proposal-level ignorance projections."""

    def project_ignorance(
        self,
        *,
        source_id: str,
        text: str,
    ) -> tuple[IgnoranceProjection, ...]: ...


__all__ = [
    "IgnoranceAction",
    "IgnoranceActionPlan",
    "IgnoranceKind",
    "IgnoranceProjection",
    "ScientificIgnoranceInterpreter",
    "deduplicate_ignorance",
    "plan_for_ignorance",
]
