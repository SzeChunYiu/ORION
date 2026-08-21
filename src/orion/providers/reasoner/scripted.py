from __future__ import annotations

from dataclasses import dataclass, field

from orion.core.contributions import KnowledgeContribution
from orion.core.problem import Problem
from orion.core.problem_tree import (
    ProblemDecomposition,
    RecursiveProblemStopReason,
    ResidualDecomposition,
)
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
    decompositions_by_kind: dict[ResidualKind, ResidualDecomposition] = field(
        default_factory=dict
    )
    problem_decompositions_by_id: dict[str, ProblemDecomposition] = field(
        default_factory=dict
    )
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

    def decompose_problem(
        self,
        problem: Problem,
        state: OrionState,
    ) -> ProblemDecomposition:
        decomposition = self.problem_decompositions_by_id.get(problem.problem_id)
        if decomposition is None:
            decomposition = ProblemDecomposition(
                parent_problem_id=problem.problem_id,
                stop_reason=RecursiveProblemStopReason.NO_DECISION_SEPARATING_DECOMPOSITION,
                rationale="no scripted broader-problem decomposition",
            )
        decomposition.verify(problem)
        return decomposition

    def decompose_residual(
        self,
        residual: Residual,
        problem: Problem,
        state: OrionState,
    ) -> ResidualDecomposition:
        decomposition = self.decompositions_by_kind.get(residual.kind)
        if decomposition is None:
            decomposition = ResidualDecomposition(
                parent_residual_id=residual.residual_id,
                stop_reason=RecursiveProblemStopReason.IRREDUCIBLE_AT_CURRENT_RESOLUTION,
                rationale="no scripted finer decomposition",
            )
        decomposition.verify(residual)
        return decomposition

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