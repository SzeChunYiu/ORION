from __future__ import annotations

from dataclasses import dataclass

from orion.core.search import SearchRouteKind
from orion.kernel.store import LedgerStore
from orion.knowledge.research_loop import ResearchPacket, RouteBinding, run_research_round
from orion.knowledge.space import KnowledgeSpace, TraversalResult
from orion.mechanics.model import MechanicCell
from orion.mechanics.questioning import MechanicQuestion


@dataclass(frozen=True)
class ShadowKnowledgeInvestigation:
    """Evidence/retrieval diagnostics available to a Shadow development step."""

    packet: ResearchPacket
    traversal: TraversalResult
    boundary: str = (
        "Retrieved documents and structured-space traversal are diagnostic evidence inputs only. "
        "They do not turn source projections into verified claims, satisfy empirical closure, "
        "or grant ORION authority to promote its own changes."
    )

    @property
    def candidate_ids(self) -> tuple[str, ...]:
        return tuple(item.source_id for item in self.packet.candidates)

    @property
    def supporting_claim_ids(self) -> tuple[str, ...]:
        return tuple(item.claim_id for item in self.traversal.supporting)

    @property
    def contested_claim_pairs(self) -> tuple[tuple[str, str], ...]:
        return tuple(
            (left.claim_id, right.claim_id) for left, right in self.traversal.contested
        )


class ShadowKnowledgeRuntime:
    """Production knowledge path for proposal-only Shadow Self-ORION research."""

    def __init__(
        self,
        *,
        store: LedgerStore,
        bindings: tuple[RouteBinding, ...],
        declared_routes: tuple[SearchRouteKind, ...] = (),
        space: KnowledgeSpace | None = None,
        schema_version: str = "shadow-knowledge-v1",
    ) -> None:
        self._store = store
        self._bindings = bindings
        self._declared_routes = declared_routes
        self._space = space if space is not None else KnowledgeSpace()
        self._schema_version = schema_version

    def investigate(
        self,
        *,
        cell: MechanicCell,
        question: MechanicQuestion,
    ) -> ShadowKnowledgeInvestigation:
        packet = run_research_round(
            self._store,
            cell,
            question,
            self._bindings,
            declared_routes=self._declared_routes,
            schema_version=self._schema_version,
        )
        traversal = self._space.traverse(question.question)
        return ShadowKnowledgeInvestigation(packet=packet, traversal=traversal)


__all__ = ["ShadowKnowledgeInvestigation", "ShadowKnowledgeRuntime"]
