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


def research_task_for_question(cell: MechanicCell, question: MechanicQuestion) -> MechanicResearchTask:
    if question.mechanic_id != cell.mechanic_id:
        raise ValueError("mechanic question/cell mismatch")
    route_kind = _ROUTE_BY_DIMENSION.get(question.dimension, SearchRouteKind.FUNCTION_ONLY)
    slug = question.dimension.value.lower()
    query = SearchQuery(
        query_id=f"mechanic:{cell.mechanic_id}:{slug}",
        text=f"{cell.purpose} {question.question}",
        route_id=f"mechanic-audit:{cell.mechanic_id}:{route_kind.value.lower()}",
        route_kind=route_kind,
    )
    return MechanicResearchTask(
        mechanic_id=cell.mechanic_id,
        question_id=question.question_id,
        dimension=question.dimension,
        query=query,
    )


def plan_mechanic_research(cell: MechanicCell, *, limit: int = 8) -> tuple[MechanicResearchTask, ...]:
    """Select V0 audit questions and turn them into provider-neutral search queries."""

    questions = plan_next_questions(generate_mechanic_questions(cell), limit=limit)
    return tuple(research_task_for_question(cell, question) for question in questions)
