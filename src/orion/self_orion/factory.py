from __future__ import annotations

from orion.providers.development import (
    ArtifactBackedSandboxCandidateRunner,
    DevelopmentArtifactStore,
    LLMDevelopmentChangeProvider,
    SandboxPatchExecutor,
)
from orion.providers.llm.base import LLMProvider
from orion.runtime.runtime import OrionRuntime
from orion.self_orion.change_control import ProtectedDevelopmentEvaluator
from orion.self_orion.self_driving import ShadowSelfDrivingController


def build_llm_shadow_self_driving_controller(
    *,
    research_runtime: OrionRuntime,
    development_llm: LLMProvider,
    artifact_store: DevelopmentArtifactStore,
    sandbox_executor: SandboxPatchExecutor,
    protected_evaluator: ProtectedDevelopmentEvaluator,
    base_revision: str,
) -> ShadowSelfDrivingController:
    """Compose a complete proposal-only LLM development stack around ORION control."""

    development_provider = LLMDevelopmentChangeProvider(development_llm, artifact_store)
    sandbox_runner = ArtifactBackedSandboxCandidateRunner(
        artifact_store=artifact_store,
        executor=sandbox_executor,
    )
    return ShadowSelfDrivingController.from_components(
        runtime=research_runtime,
        development_provider=development_provider,
        sandbox_runner=sandbox_runner,
        protected_evaluator=protected_evaluator,
        base_revision=base_revision,
    )


__all__ = ["build_llm_shadow_self_driving_controller"]
