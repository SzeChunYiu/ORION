from __future__ import annotations

from dataclasses import dataclass

from orion.core.problem import Problem
from orion.core.solution import Solution
from orion.core.state import OrionState
from orion.engine.solver import OrionSolver, SolverConfig
from orion.engine.trace import SolveTrace
from orion.providers.llm.base import LLMProvider
from orion.providers.reasoner.llm import LLMResearchReasoner
from orion.providers.retrieval.base import RetrievalProvider
from orion.providers.verification.base import VerificationProvider


@dataclass(frozen=True)
class RuntimeResult:
    solution: Solution
    final_state: OrionState
    trace: SolveTrace


class OrionRuntime:
    """Composition root for a running ORION instance.

    External providers enter here. The engine and scientific authority semantics remain
    independent of the concrete LLM, retriever or verifier implementation.
    """

    def __init__(self, solver: OrionSolver) -> None:
        self._solver = solver

    @classmethod
    def from_providers(
        cls,
        *,
        llm: LLMProvider,
        retrieval: RetrievalProvider,
        verification: VerificationProvider,
        config: SolverConfig | None = None,
    ) -> "OrionRuntime":
        reasoner = LLMResearchReasoner(llm)
        solver = OrionSolver(
            reasoner=reasoner,
            retrieval=retrieval,
            verification=verification,
            config=config,
        )
        return cls(solver)

    def solve(self, problem: Problem, *, initial_state: OrionState | None = None) -> RuntimeResult:
        solution, final_state, trace = self._solver.solve(problem, initial_state=initial_state)
        return RuntimeResult(solution=solution, final_state=final_state, trace=trace)
