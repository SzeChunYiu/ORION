from __future__ import annotations

from dataclasses import dataclass

from orion.engine.guards import MechanicGuard
from orion.engine.solver import SolverConfig
from orion.providers.experience.base import ExperienceStore
from orion.providers.live_phase2 import LivePhase2ProviderStack
from orion.self_orion.baseline import SimpleLLMRetrievalBaseline
from orion.self_orion.live_trial import ShadowLiveTrialRunner


@dataclass(frozen=True)
class LivePhase2TrialHarness:
    stack: LivePhase2ProviderStack
    baseline: SimpleLLMRetrievalBaseline
    runner: ShadowLiveTrialRunner

    @property
    def provider_manifest_hash(self) -> str:
        return self.stack.provider_manifest_hash

    @property
    def evaluator_artifact_hash(self) -> str:
        return self.stack.evaluator_artifact_hash

    @property
    def evaluation_epoch_id(self) -> str:
        return self.stack.evaluation_epoch_id


def build_live_phase2_trial_harness(
    stack: LivePhase2ProviderStack,
    *,
    experience_store: ExperienceStore | None = None,
    config: SolverConfig | None = None,
    guards: tuple[MechanicGuard, ...] = (),
    producer_process_lineage_hash: str | None = None,
    evaluator_artifact_hash: str | None = None,
    baseline_max_results: int = 12,
    baseline_retrieval_call_cost_units: float = 1.0,
    baseline_llm_call_cost_units: float = 1.0,
) -> LivePhase2TrialHarness:
    """Compose the real-provider ORION + matched simple baseline campaign pair."""

    bound_evaluator = evaluator_artifact_hash or stack.evaluator_artifact_hash
    if bound_evaluator != stack.evaluator_artifact_hash:
        raise ValueError("runtime evaluator artifact must match the protected verification stack")
    baseline = SimpleLLMRetrievalBaseline(
        llm=stack.llm,
        retrieval=stack.retrieval,
        max_results=baseline_max_results,
        retrieval_call_cost_units=baseline_retrieval_call_cost_units,
        llm_call_cost_units=baseline_llm_call_cost_units,
    )
    runner = ShadowLiveTrialRunner.from_providers(
        llm=stack.llm,
        retrieval=stack.retrieval,
        verification=stack.verification,
        baseline=baseline,
        experience_store=experience_store,
        config=config,
        guards=guards,
        producer_process_lineage_hash=producer_process_lineage_hash,
        evaluator_artifact_hash=bound_evaluator,
    )
    return LivePhase2TrialHarness(stack, baseline, runner)


__all__ = ["LivePhase2TrialHarness", "build_live_phase2_trial_harness"]
