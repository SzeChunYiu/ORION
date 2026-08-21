from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from orion.core.contributions import KnowledgeContribution
from orion.core.problem import Problem
from orion.core.problem_tree import ResidualDecomposition
from orion.core.residuals import Residual, Responsibility
from orion.core.search import RetrievedItem, SearchQuery
from orion.core.state import OrionState


@dataclass(frozen=True)
class Diagnosis:
    responsibilities: tuple[Responsibility, ...]
    rationale: str


@dataclass(frozen=True)
class ReframeProposal:
    add_domain_ids: tuple[str, ...] = ()
    add_representation_ids: tuple[str, ...] = ()
    note: str = ""


class ResearchReasoner(Protocol):
    """Semantic/cognitive functions ORION may delegate to an LLM or other reasoner.

    Decomposition is proposal-only.  A reasoner may propose child problems and
    discriminators, but the recursive controller validates/bounds them and the
    ordinary ORION verification/authority path remains authoritative.
    """

    def plan_search(self, problem: Problem, state: OrionState) -> tuple[SearchQuery, ...]:
        ...

    def interpret(self, item: RetrievedItem, problem: Problem, state: OrionState) -> KnowledgeContribution:
        ...

    def reconstruct(self, problem: Problem, state: OrionState) -> str:
        ...

    def diagnose(self, residual: Residual, problem: Problem, state: OrionState) -> Diagnosis:
        ...

    def decompose_residual(
        self,
        residual: Residual,
        problem: Problem,
        state: OrionState,
    ) -> ResidualDecomposition:
        ...

    def propose_reframe(
        self,
        residual: Residual,
        diagnosis: Diagnosis,
        problem: Problem,
        state: OrionState,
    ) -> ReframeProposal:
        ...

    def compose_answer(self, problem: Problem, state: OrionState) -> str:
        ...
