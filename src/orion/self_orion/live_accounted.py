from __future__ import annotations

from dataclasses import replace

from orion.engine.guards import MechanicGuard
from orion.engine.solver import SolverConfig
from orion.providers.experience.base import ExperienceStore
from orion.providers.llm.accounting import AccountingLLMProvider
from orion.providers.llm.base import LLMProvider
from orion.providers.retrieval.base import RetrievalProvider
from orion.providers.verification.base import VerificationProvider
from orion.self_orion.live_trial import (
    BaselineResearchRunner,
    FrozenLiveTrialPacket,
    ShadowLiveTrialReport,
    ShadowLiveTrialRunner,
)


class AccountedShadowLiveTrialRunner(ShadowLiveTrialRunner):
    """Live trial runner with task-bound LLM/retrieval provider-call accounting."""

    def __init__(
        self,
        *,
        orion,
        baseline: BaselineResearchRunner,
        retrieval_recorder,
        accounting_llm: AccountingLLMProvider,
        retrieval_call_cost_units: float = 1.0,
        llm_call_cost_units: float = 1.0,
    ) -> None:
        super().__init__(
            orion=orion,
            baseline=baseline,
            retrieval_recorder=retrieval_recorder,
        )
        if retrieval_call_cost_units < 0 or llm_call_cost_units < 0:
            raise ValueError("live provider-call resource costs cannot be negative")
        self._accounting_llm = accounting_llm
        self._retrieval_call_cost_units = retrieval_call_cost_units
        self._llm_call_cost_units = llm_call_cost_units

    @classmethod
    def from_providers(
        cls,
        *,
        llm: LLMProvider,
        retrieval: RetrievalProvider,
        verification: VerificationProvider,
        baseline: BaselineResearchRunner,
        experience_store: ExperienceStore | None = None,
        config: SolverConfig | None = None,
        guards: tuple[MechanicGuard, ...] = (),
        producer_process_lineage_hash: str | None = None,
        evaluator_artifact_hash: str | None = None,
        retrieval_call_cost_units: float = 1.0,
        llm_call_cost_units: float = 1.0,
    ) -> AccountedShadowLiveTrialRunner:
        accounting_llm = AccountingLLMProvider(llm)
        base = ShadowLiveTrialRunner.from_providers(
            llm=accounting_llm,
            retrieval=retrieval,
            verification=verification,
            baseline=baseline,
            experience_store=experience_store,
            config=config,
            guards=guards,
            producer_process_lineage_hash=producer_process_lineage_hash,
            evaluator_artifact_hash=evaluator_artifact_hash,
        )
        return cls(
            orion=base._orion,
            baseline=baseline,
            retrieval_recorder=base._retrieval_recorder,
            accounting_llm=accounting_llm,
            retrieval_call_cost_units=retrieval_call_cost_units,
            llm_call_cost_units=llm_call_cost_units,
        )

    @property
    def llm_call_observations(self):
        return self._accounting_llm.observations()

    def llm_calls_for_task(self, task_id: str) -> int:
        return self._accounting_llm.attempted_calls_for_problem(task_id)

    def run(self, packet: FrozenLiveTrialPacket) -> ShadowLiveTrialReport:
        raw = super().run(packet)
        comparisons = []
        for item in raw.comparisons:
            retrieval_calls = item.raw_query_count
            llm_calls = self.llm_calls_for_task(item.task_id)
            orion_units = (
                retrieval_calls * self._retrieval_call_cost_units
                + llm_calls * self._llm_call_cost_units
            )
            resource_matched = (
                orion_units <= packet.resource_budget_units
                and item.baseline_resource_units <= packet.resource_budget_units
                and orion_units
                <= item.baseline_resource_units
                * packet.max_orion_to_baseline_resource_ratio
            )
            comparisons.append(
                replace(
                    item,
                    orion_resource_units=orion_units,
                    resource_matched=resource_matched,
                )
            )
        return replace(
            raw,
            comparisons=tuple(comparisons),
            all_resource_matched=all(item.resource_matched for item in comparisons),
        )


__all__ = ["AccountedShadowLiveTrialRunner"]
