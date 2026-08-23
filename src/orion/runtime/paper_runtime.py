from __future__ import annotations

from orion.engine.guards import MechanicGuard
from orion.engine.navigation import PaperParityNavigator
from orion.engine.paper_parity_solver import PaperParityOrionSolver
from orion.engine.solver import SolverConfig
from orion.providers.experience.base import ExperienceStore
from orion.providers.llm.base import LLMProvider
from orion.providers.reasoner.llm import LLMResearchReasoner
from orion.providers.retrieval.base import RetrievalProvider
from orion.providers.verification.base import VerificationProvider
from orion.runtime.runtime import OrionRuntime as _KernelOrionRuntime
from orion.runtime.runtime import RuntimeResult


class OrionRuntime(_KernelOrionRuntime):
    """Public ORION runtime with paper-described atom/fibre/donor navigation enabled."""

    @classmethod
    def from_providers(
        cls,
        *,
        llm: LLMProvider,
        retrieval: RetrievalProvider,
        verification: VerificationProvider,
        experience_store: ExperienceStore | None = None,
        config: SolverConfig | None = None,
        guards: tuple[MechanicGuard, ...] = (),
        producer_process_lineage_hash: str | None = None,
        evaluator_artifact_hash: str | None = None,
        navigation_profile: str = "orion",
        navigator: PaperParityNavigator | None = None,
    ) -> "OrionRuntime":
        if navigator is None:
            if navigation_profile == "orion":
                navigator = PaperParityNavigator.normal()
            elif navigation_profile == "orion-q":
                navigator = PaperParityNavigator.orion_q()
            else:
                raise ValueError("navigation_profile must be 'orion' or 'orion-q'")
        reasoner = LLMResearchReasoner(llm)
        solver = PaperParityOrionSolver(
            reasoner=reasoner,
            retrieval=retrieval,
            verification=verification,
            config=config,
            guards=guards,
            navigator=navigator,
        )
        return cls(
            solver,
            experience_store=experience_store,
            producer_process_lineage_hash=producer_process_lineage_hash,
            evaluator_artifact_hash=evaluator_artifact_hash,
        )

    @property
    def navigation_plan(self):
        return getattr(self._solver, "last_navigation_plan", None)


__all__ = ["OrionRuntime", "RuntimeResult"]
