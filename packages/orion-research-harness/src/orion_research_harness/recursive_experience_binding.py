from __future__ import annotations

from typing import Any

from orion.providers.reasoner import recursive_llm as _core_recursive

from . import recursive_runner as _runner
from .mechanics_bridge import compile_workspace_development_fibre


class WorkspaceRecursiveLLMResearchReasoner(
    _core_recursive.RecursiveLLMResearchReasoner
):
    """Recursive reasoner with automatic cross-run DevelopmentFibre retrieval.

    Core ORION remains workspace-agnostic. In the research harness, BrokerLLMProvider
    already binds an immutable ResearchWorkspace. This adapter compiles the affected
    canonical DevelopmentFibres against that workspace's historical TaskEpisodes before
    each residual decomposition, so DIAGNOSE.EXPERIENCE_RETRIEVAL and REOPEN.FIBRE are
    automatic rather than optional CLI side operations.
    """

    def __init__(self, provider) -> None:
        super().__init__(provider)
        broker = getattr(provider, "_broker", None)
        self._workspace = getattr(broker, "workspace", None)

    def decompose_residual(self, residual, problem, state):
        previous = tuple(getattr(self, "_development_fibre_context", ()))
        rows: list[dict[str, Any]] = []
        if self._workspace is not None:
            for mechanic_id in _core_recursive._affected_mechanic_ids(residual):
                try:
                    compiled = compile_workspace_development_fibre(
                        self._workspace, mechanic_id
                    )
                except KeyError:
                    continue
                rows.append(
                    {
                        "source": "WORKSPACE_HISTORY_FIBRE",
                        "mechanic_id": mechanic_id,
                        "fibre": compiled["fibre"],
                        "authority": compiled["authority"],
                    }
                )
        self.set_development_fibre_context((*previous, *rows))
        try:
            return super().decompose_residual(residual, problem, state)
        finally:
            self.set_development_fibre_context(previous)


def install_workspace_recursive_reasoner() -> None:
    """Bind the harness runner to the workspace-aware recursive reasoner."""

    _runner.RecursiveLLMResearchReasoner = WorkspaceRecursiveLLMResearchReasoner
    _runner._workspace_recursive_reasoner_installed = True


install_workspace_recursive_reasoner()


__all__ = [
    "WorkspaceRecursiveLLMResearchReasoner",
    "install_workspace_recursive_reasoner",
]
