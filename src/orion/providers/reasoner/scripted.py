from __future__ import annotations

from dataclasses import dataclass, field

from orion.core.contributions import KnowledgeContribution
from orion.core.problem import Problem
from orion.core.residuals import Residual, ResidualKind, Responsibility
from orion.core.search import RetrievedItem, SearchQuery
from orion.core.state import OrionState
from orion.providers.reasoner.base import Diagnosis, ReframeProposal


@dataclass
class ScriptedReasoner:
    """Deterministic reasoner for tests; exercises the same contract as an LLM."""

    search_plans: list[tuple[SearchQuery, ...]]
    contributions_by_item_id: dict[str, KnowledgeContribution]
    diagnoses_by_kind: dict[ResidualKind, Diagnosis]
    reframes_by_kind: dict[ResidualKind, ReframeProposal]
    reconstruction_summaries: list[str] = field(default_factory=list)
    answer_text: str = ""
    _search_index: int = 0
    _reconstruct_index: int = 0

    def plan_search(self, problem: Problem, state: OrionState) -> tuple[SearchQuery, ...]:
        if not self.search_plans:
            return ()
        index = min(self._search_index, len(self.search_plans) - 1)
        self._search_index += 1
        return self.search_plans[index]

    def interpret(self, item: RetrievedItem, problem: Problem, state: OrionState) -> KnowledgeContribution:
        return self.contributions_by_item_id[item.item_id]

    def reconstruct(self, problem: Problem, state: OrionState) -> str:
        if not self.reconstruction_summaries:
            return " | ".join(claim.text for claim in state.knowledge.claims)
        index = min(self._reconstruct_index, len(self.reconstruction_summaries) - 1)
        self._reconstruct_index += 1
        return self.reconstruction_summaries[index]

    def diagnose(self, residual: Residual, problem: Problem, state: OrionState) -> Diagnosis:
        return self.diagnoses_by_kind.get(
            residual.kind,
            Diagnosis((Responsibility.EVIDENCE,), "default scripted diagnosis"),
        )

    def propose_reframe(
        self,
        residual: Residual,
        diagnosis: Diagnosis,
        problem: Problem,
        state: OrionState,
    ) -> ReframeProposal:
        return self.reframes_by_kind.get(residual.kind, ReframeProposal())

    def compose_answer(self, problem: Problem, state: OrionState) -> str:
        return self.answer_text or " | ".join(
            claim.text for claim in state.knowledge.claims if claim.authority.value == "VERIFIED"
        )
