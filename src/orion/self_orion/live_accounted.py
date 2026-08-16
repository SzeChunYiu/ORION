from __future__ import annotations

from dataclasses import replace

from orion.core.search import RetrievedItem, SearchQuery
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
    RetrievedItemSnapshot,
    SearchObservation,
    ShadowLiveTrialReport,
    ShadowLiveTrialRunner,
)


class AttemptRecordingRetrievalProvider:
    """Record every live retrieval attempt, including provider exceptions."""

    def __init__(self, delegate: RetrievalProvider) -> None:
        self._delegate = delegate
        self._observations: list[SearchObservation] = []

    def mark(self) -> int:
        return len(self._observations)

    def observations_since(self, mark: int) -> tuple[SearchObservation, ...]:
        if mark < 0 or mark > len(self._observations):
            raise ValueError("invalid retrieval observation mark")
        return tuple(self._observations[mark:])

    @staticmethod
    def _observation(
        query: SearchQuery,
        *,
        limit: int,
        items: tuple[RetrievedItem, ...],
    ) -> SearchObservation:
        return SearchObservation(
            query_id=query.query_id,
            query_text=query.text,
            route_id=query.route_id,
            route_kind=query.route_kind.value,
            domain_hint=query.domain_hint,
            limit=limit,
            items=tuple(
                RetrievedItemSnapshot(
                    item_id=item.item_id,
                    content=item.content,
                    source_uri=item.source_uri,
                    domain_ids=item.domain_ids,
                )
                for item in items
            ),
        )

    def search(self, query: SearchQuery, *, limit: int) -> tuple[RetrievedItem, ...]:
        try:
            items = tuple(self._delegate.search(query, limit=limit))
        except Exception:
            # The paired mechanic receipt preserves the exception class. This
            # observation preserves the exact attempted query/route/limit even
            # when no provider result exists.
            self._observations.append(
                self._observation(query, limit=limit, items=())
            )
            raise
        self._observations.append(
            self._observation(query, limit=limit, items=items)
        )
        return items


class AccountedShadowLiveTrialRunner(ShadowLiveTrialRunner):
    """Live trial runner with task-bound provider-call accounting and raw attempts."""

    def __init__(
        self,
        *,
        orion,
        baseline: BaselineResearchRunner,
        retrieval_recorder: AttemptRecordingRetrievalProvider,
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
        self._last_run_mark = 0

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
        attempt_recorder = AttemptRecordingRetrievalProvider(retrieval)
        # The base factory adds its own success recorder around our provider.
        # ORION therefore calls the attempt recorder, while this runner reads
        # the inner stream that also contains failed attempts.
        base = ShadowLiveTrialRunner.from_providers(
            llm=accounting_llm,
            retrieval=attempt_recorder,
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
            retrieval_recorder=attempt_recorder,
            accounting_llm=accounting_llm,
            retrieval_call_cost_units=retrieval_call_cost_units,
            llm_call_cost_units=llm_call_cost_units,
        )

    @property
    def llm_call_observations(self):
        return self._accounting_llm.observations_since(self._last_run_mark)

    def llm_calls_for_task(self, task_id: str) -> int:
        return self._accounting_llm.attempted_calls_for_problem_since(
            task_id, self._last_run_mark
        )

    def run(self, packet: FrozenLiveTrialPacket) -> ShadowLiveTrialReport:
        self._last_run_mark = self._accounting_llm.mark()
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


__all__ = ["AccountedShadowLiveTrialRunner", "AttemptRecordingRetrievalProvider"]
