from __future__ import annotations

from dataclasses import dataclass, replace

from orion.core.problem import Problem
from orion.core.search import RetrievedItem, SearchQuery
from orion.core.state import OrionState
from orion.engine.contracts import OperatorResult
from orion.engine.cycle import CycleOperator, Transition
from orion.providers.reasoner.base import ResearchReasoner
from orion.providers.retrieval.base import RetrievalProvider


@dataclass(frozen=True)
class SearchBatch:
    queries: tuple[SearchQuery, ...]
    items: tuple[RetrievedItem, ...]


class SearchOperator:
    operator_id = "SEARCH.v1"

    def __init__(
        self,
        reasoner: ResearchReasoner,
        retrieval: RetrievalProvider,
        *,
        limit_per_query: int = 8,
    ) -> None:
        self._reasoner = reasoner
        self._retrieval = retrieval
        self._limit = limit_per_query

    def run(self, problem: Problem, state: OrionState) -> OperatorResult[SearchBatch]:
        queries = self._reasoner.plan_search(problem, state)
        items: list[RetrievedItem] = []
        searched_domains: list[str] = []
        route_ids: list[str] = []

        for query in queries:
            items.extend(self._retrieval.search(query, limit=self._limit))
            route_ids.append(query.route_id)
            if query.domain_hint:
                searched_domains.append(query.domain_hint)

        universe = state.search_universe.mark_searched(tuple(searched_domains), tuple(route_ids))
        next_state = replace(state, search_universe=universe)
        transition = Transition(
            operator=CycleOperator.SEARCH,
            input_epoch=state.epoch,
            output_epoch=state.epoch,
            evidence_ids=tuple(item.item_id for item in items),
            changed_coordinates=("W.SEARCHED",) if queries else (),
        )
        return OperatorResult(next_state, SearchBatch(queries, tuple(items)), transition)
