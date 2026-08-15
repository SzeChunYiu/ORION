from __future__ import annotations

from dataclasses import dataclass

from orion.core.search import SearchQuery, SearchRouteKind

from .model import MechanicCell, MechanicDimension
from .questioning import MechanicQuestion, generate_mechanic_questions, plan_next_questions


@dataclass(frozen=True)
class MechanicResearchTask:
    """Mechanical bridge from an open mechanic question to a search task."""

    mechanic_id: str
    question_id: str
    dimension: MechanicDimension
    query: SearchQuery


_ROUTE_BY_DIMENSION: dict[MechanicDimension, SearchRouteKind] = {
    MechanicDimension.PARENT_DISCIPLINE: SearchRouteKind.PARENT_DISCIPLINE,
    MechanicDimension.SEARCH_COVERAGE: SearchRouteKind.ADVERSARIAL_OMISSION,
    MechanicDimension.SATURATION: SearchRouteKind.LITERATURE_BRIDGE,
    MechanicDimension.ENGINEERING: SearchRouteKind.CROSS_DOMAIN,
    MechanicDimension.VERIFICATION: SearchRouteKind.CROSS_DOMAIN,
}


def _query_for(cell: MechanicCell, question: MechanicQuestion) -> SearchQuery:
    route_kind = _ROUTE_BY_DIMENSION.get(question.dimension, SearchRouteKind.FUNCTION_ONLY)
    slug = question.dimension.value.lower()
    return SearchQuery(
        query_id=f"mechanic:{cell.mechanic_id}:{slug}",
        text=f"{cell.purpose} {question.question}",
        route_id=f"mechanic-audit:{cell.mechanic_id}:{route_kind.value.lower()}",
        route_kind=route_kind,
    )


def plan_mechanic_research(cell: MechanicCell, *, limit: int = 8) -> tuple[MechanicResearchTask, ...]:
    """Select V0 audit questions and turn them into provider-neutral search queries.

    No language model is needed to remember the question families or choose the first
    route family. Search execution and interpretation may still use external providers.
    """

    questions = plan_next_questions(generate_mechanic_questions(cell), limit=limit)
    return tuple(
        MechanicResearchTask(
            mechanic_id=cell.mechanic_id,
            question_id=question.question_id,
            dimension=question.dimension,
            query=_query_for(cell, question),
        )
        for question in questions
    )
