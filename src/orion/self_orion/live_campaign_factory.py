from __future__ import annotations

from dataclasses import dataclass

from orion.engine.guards import MechanicGuard
from orion.engine.solver import SolverConfig
from orion.providers.experience.base import ExperienceStore
from orion.providers.experience.memory import InMemoryExperienceStore
from orion.providers.live_phase2 import LivePhase2ProviderStack
from orion.self_orion.baseline import SimpleLLMRetrievalBaseline
from orion.self_orion.live_accounted import AccountedShadowLiveTrialRunner


@dataclass(frozen=True)
class LivePhase2TrialHarness:
    stack: LivePhase2ProviderStack
    baseline: SimpleLLMRetrievalBaseline
    runner: AccountedShadowLiveTrialRunner

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
    """Compose real-provider ORION + simple baseline with identical call-cost units.

    The live harness always records failure episodes and measures ORION at the
    same provider-call boundary used by the baseline. Callers may supply a
    durable protected experience store; otherwise an in-memory store prevents a
    failed/partial campaign from becoming unrecordable through omitted config.
    """

    bound_evaluator = evaluator_artifact_hash or stack.evaluator_artifact_hash
    if bound_evaluator != stack.evaluator_artifact_hash:
        raise ValueError(
            "runtime evaluator artifact must match the protected verification stack"
        )
    retained_experience = (
        experience_store
        if experience_store is not None
        else InMemoryExperienceStore()
    )
    baseline = SimpleLLMRetrievalBaseline(
        llm=stack.llm,
        retrieval=stack.retrieval,
        max_results=baseline_max_results,
        retrieval_call_cost_units=baseline_retrieval_call_cost_units,
        llm_call_cost_units=baseline_llm_call_cost_units,
    )
    runner = AccountedShadowLiveTrialRunner.from_providers(
        llm=stack.llm,
        retrieval=stack.retrieval,
        verification=stack.verification,
        baseline=baseline,
        experience_store=retained_experience,
        config=config,
        guards=guards,
        producer_process_lineage_hash=producer_process_lineage_hash,
        evaluator_artifact_hash=bound_evaluator,
        retrieval_call_cost_units=baseline_retrieval_call_cost_units,
        llm_call_cost_units=baseline_llm_call_cost_units,
    )
    return LivePhase2TrialHarness(stack, baseline, runner)


__all__ = ["LivePhase2TrialHarness", "build_live_phase2_trial_harness"]
