from __future__ import annotations

import json
from types import SimpleNamespace

from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.residuals import Residual, ResidualKind, Responsibility
from orion.core.search_universe import SearchUniverseState
from orion.core.state import KnowledgeState, OrionState
from orion.providers.llm.base import LLMResponse
from orion_research_harness import recursive_experience_binding as binding


class _Provider:
    def __init__(self) -> None:
        self._broker = SimpleNamespace(workspace=object())
        self.requests = []

    def complete(self, request):
        self.requests.append(request)
        return LLMResponse(
            content=json.dumps(
                {
                    "atoms": [],
                    "stop_reason": "IRREDUCIBLE_AT_CURRENT_RESOLUTION",
                    "rationale": "bounded history-binding test",
                }
            ),
            model_id="history-binding-test",
        )


def test_workspace_history_fibres_are_injected_before_residual_decomposition(monkeypatch) -> None:
    compiled = []

    def fake_compile(_workspace, mechanic_id):
        compiled.append(mechanic_id)
        return {
            "authority": "DERIVED_WORKING_VIEW_ONLY__NO_PROMOTION_AUTHORITY",
            "fibre": {
                "mechanic_id": mechanic_id,
                "related_episode_ids": ["episode:historical"],
                "failure_episode_ids": ["episode:historical"],
            },
        }

    monkeypatch.setattr(binding, "compile_workspace_development_fibre", fake_compile)
    provider = _Provider()
    reasoner = binding.WorkspaceRecursiveLLMResearchReasoner(provider)
    residual = Residual(
        residual_id="residual:method-history",
        kind=ResidualKind.METHOD_GAP,
        description="A repeated method-language failure remains after donor closure.",
        candidate_responsibilities=(Responsibility.METHOD,),
    )
    state = OrionState(
        knowledge=KnowledgeState(residuals=(residual,)),
        search_universe=SearchUniverseState(),
        method=MethodState(method_version="test"),
    )
    reasoner.decompose_residual(
        residual,
        Problem("problem:history", "Resolve the repeated method failure"),
        state,
    )

    assert compiled
    assert "DIAGNOSE.EXPERIENCE_RETRIEVAL.v0" in compiled
    assert "REOPEN.FIBRE.v0" in compiled
    assert "REFRAME.METHOD.v0" in compiled
    assert len(provider.requests) == 1
    payload = json.loads(provider.requests[0].user)
    history_rows = [
        row
        for row in payload["development_fibre_context"]
        if row.get("source") == "WORKSPACE_HISTORY_FIBRE"
    ]
    assert history_rows
    assert any(
        "episode:historical" in row["fibre"].get("failure_episode_ids", [])
        for row in history_rows
    )
