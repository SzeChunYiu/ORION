from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from orion.core.problem import Problem
from orion.core.search import RetrievedItem, SearchQuery
from orion.core.solution import SolutionStatus
from orion.engine.guards import MechanicGuard
from orion.engine.solver import SolverConfig
from orion.providers.experience.base import ExperienceStore
from orion.providers.llm.base import LLMProvider
from orion.providers.retrieval.base import RetrievalProvider
from orion.providers.verification.base import VerificationProvider
from orion.runtime.runtime import OrionRuntime, RuntimeResult


class ResearchTrialKind(str, Enum):
    WIDE_LITERATURE = "WIDE_LITERATURE"
    DEEP_TARGET = "DEEP_TARGET"
    SELF_DEVELOPMENT = "SELF_DEVELOPMENT"


@dataclass(frozen=True)
class FrozenTrialTask:
    task_id: str
    kind: ResearchTrialKind
    problem: Problem
    variation_signature: tuple[str, ...]
    split_id: str
    required_evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.task_id.strip() or not self.split_id.strip():
            raise ValueError("trial task identity and split are required")
        if self.problem.problem_id != self.task_id:
            raise ValueError("trial task id must equal problem id")


@dataclass(frozen=True)
class FrozenLiveTrialPacket:
    packet_id: str
    evaluation_epoch_id: str
    tasks: tuple[FrozenTrialTask, ...]
    provider_manifest_hash: str
    evaluator_artifact_hash: str
    baseline_id: str
    resource_budget_units: float
    max_orion_to_baseline_resource_ratio: float = 1.0

    def __post_init__(self) -> None:
        if any(
            not item.strip()
            for item in (
                self.packet_id,
                self.evaluation_epoch_id,
                self.provider_manifest_hash,
                self.evaluator_artifact_hash,
                self.baseline_id,
            )
        ):
            raise ValueError(
                "trial packet identity/provider/evaluator/baseline fields are required"
            )
        if (
            self.resource_budget_units <= 0
            or self.max_orion_to_baseline_resource_ratio <= 0
        ):
            raise ValueError("trial resources must be positive")
        ids = [item.task_id for item in self.tasks]
        if not ids or len(set(ids)) != len(ids):
            raise ValueError("trial tasks must be non-empty and uniquely identified")
        kinds = {item.kind for item in self.tasks}
        if (
            ResearchTrialKind.WIDE_LITERATURE not in kinds
            or ResearchTrialKind.DEEP_TARGET not in kinds
        ):
            raise ValueError(
                "Shadow live trial requires at least one wide-literature and one deep-target task"
            )
        for digest in (self.provider_manifest_hash, self.evaluator_artifact_hash):
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError("provider/evaluator bindings must be SHA-256 hashes")

    @property
    def fingerprint(self) -> str:
        payload = {
            "packet_id": self.packet_id,
            "evaluation_epoch_id": self.evaluation_epoch_id,
            "tasks": [
                {
                    "task_id": item.task_id,
                    "kind": item.kind.value,
                    "problem": {
                        "question": item.problem.question,
                        "scope": item.problem.scope,
                        "initial_domain_ids": list(item.problem.initial_domain_ids),
                        "success_criteria": list(item.problem.success_criteria),
                    },
                    "variation_signature": list(item.variation_signature),
                    "split_id": item.split_id,
                    "required_evidence_ids": list(item.required_evidence_ids),
                }
                for item in self.tasks
            ],
            "provider_manifest_hash": self.provider_manifest_hash,
            "evaluator_artifact_hash": self.evaluator_artifact_hash,
            "baseline_id": self.baseline_id,
            "resource_budget_units": self.resource_budget_units,
            "max_orion_to_baseline_resource_ratio": self.max_orion_to_baseline_resource_ratio,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


@dataclass(frozen=True)
class BaselineTaskResult:
    task_id: str
    solved: bool
    evidence_ids: tuple[str, ...]
    residual_ids: tuple[str, ...]
    resource_units: float
    artifact_hash: str

    def __post_init__(self) -> None:
        if not self.task_id.strip() or not self.artifact_hash.strip():
            raise ValueError("baseline result identity/artifact are required")
        if self.resource_units < 0:
            raise ValueError("baseline resources cannot be negative")


class BaselineResearchRunner(Protocol):
    def run(
        self, task: FrozenTrialTask, *, evaluation_epoch_id: str
    ) -> BaselineTaskResult: ...


@dataclass(frozen=True)
class RetrievedItemSnapshot:
    item_id: str
    content: str
    source_uri: str
    domain_ids: tuple[str, ...]


@dataclass(frozen=True)
class SearchObservation:
    query_id: str
    query_text: str
    route_id: str
    route_kind: str
    domain_hint: str | None
    limit: int
    items: tuple[RetrievedItemSnapshot, ...]


class RecordingRetrievalProvider:
    """Transparent retrieval wrapper that preserves the raw Phase-2 search trace."""

    def __init__(self, delegate: RetrievalProvider) -> None:
        self._delegate = delegate
        self._observations: list[SearchObservation] = []

    def mark(self) -> int:
        return len(self._observations)

    def observations_since(self, mark: int) -> tuple[SearchObservation, ...]:
        if mark < 0 or mark > len(self._observations):
            raise ValueError("invalid retrieval observation mark")
        return tuple(self._observations[mark:])

    def search(self, query: SearchQuery, *, limit: int) -> tuple[RetrievedItem, ...]:
        items = tuple(self._delegate.search(query, limit=limit))
        self._observations.append(
            SearchObservation(
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
        )
        return items


@dataclass(frozen=True)
class MechanicTraceSnapshot:
    operator: str
    summary: str
    receipt_id: str
    mechanic_id: str
    status: str
    action_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    residual_ids: tuple[str, ...]
    failure_signature: tuple[str, ...]
    handoff_values: tuple[tuple[str, str], ...]
    provenance_ids: tuple[str, ...]


@dataclass(frozen=True)
class TrialTaskComparison:
    task_id: str
    kind: ResearchTrialKind
    orion_status: SolutionStatus
    orion_evidence_count: int
    orion_residual_count: int
    orion_resource_units: float
    baseline_solved: bool
    baseline_evidence_count: int
    baseline_residual_count: int
    baseline_resource_units: float
    resource_matched: bool
    required_evidence_recovered: bool
    root_episode_id: str | None
    mechanic_episode_ids: tuple[str, ...]
    search_observations: tuple[SearchObservation, ...] = ()
    mechanic_trace: tuple[MechanicTraceSnapshot, ...] = ()
    solution_evidence_ids: tuple[str, ...] = ()
    absorbed_evidence_ids: tuple[str, ...] = ()
    retrieved_but_unused_ids: tuple[str, ...] = ()
    retrieved_but_unabsorbed_ids: tuple[str, ...] = ()

    @property
    def raw_query_count(self) -> int:
        return len(self.search_observations)

    @property
    def raw_retrieved_item_count(self) -> int:
        return sum(len(item.items) for item in self.search_observations)


@dataclass(frozen=True)
class ShadowLiveTrialReport:
    packet_id: str
    packet_fingerprint: str
    comparisons: tuple[TrialTaskComparison, ...]
    all_resource_matched: bool
    all_failures_recordable: bool
    wide_task_count: int
    deep_task_count: int
    boundary: str

    @property
    def grants_self_promotion(self) -> bool:
        return False

    @property
    def raw_search_trace_retained(self) -> bool:
        """Whether every task retained at least one raw provider search occasion."""

        return bool(self.comparisons) and all(
            item.search_observations for item in self.comparisons
        )

    @property
    def evidence_artifact_hash(self) -> str:
        """Content-address the raw search + answer-use trial artifact."""

        payload = {
            "packet_id": self.packet_id,
            "packet_fingerprint": self.packet_fingerprint,
            "comparisons": [
                {
                    "task_id": comparison.task_id,
                    "kind": comparison.kind.value,
                    "orion_status": comparison.orion_status.value,
                    "solution_evidence_ids": list(comparison.solution_evidence_ids),
                    "absorbed_evidence_ids": list(comparison.absorbed_evidence_ids),
                    "retrieved_but_unused_ids": list(
                        comparison.retrieved_but_unused_ids
                    ),
                    "retrieved_but_unabsorbed_ids": list(
                        comparison.retrieved_but_unabsorbed_ids
                    ),
                    "search_observations": [
                        {
                            "query_id": observation.query_id,
                            "query_text": observation.query_text,
                            "route_id": observation.route_id,
                            "route_kind": observation.route_kind,
                            "domain_hint": observation.domain_hint,
                            "limit": observation.limit,
                            "items": [
                                {
                                    "item_id": retrieved.item_id,
                                    "content": retrieved.content,
                                    "source_uri": retrieved.source_uri,
                                    "domain_ids": list(retrieved.domain_ids),
                                }
                                for retrieved in observation.items
                            ],
                        }
                        for observation in comparison.search_observations
                    ],
                    "mechanic_trace": [
                        {
                            "operator": event.operator,
                            "summary": event.summary,
                            "receipt_id": event.receipt_id,
                            "mechanic_id": event.mechanic_id,
                            "status": event.status,
                            "action_ids": list(event.action_ids),
                            "evidence_ids": list(event.evidence_ids),
                            "residual_ids": list(event.residual_ids),
                            "failure_signature": list(event.failure_signature),
                            "handoff_values": [list(value) for value in event.handoff_values],
                            "provenance_ids": list(event.provenance_ids),
                        }
                        for event in comparison.mechanic_trace
                    ],
                }
                for comparison in self.comparisons
            ],
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


def _orion_resources(result: RuntimeResult) -> float:
    return sum(event.receipt.cost_units or 0.0 for event in result.trace.events)


def _trace_snapshot(result: RuntimeResult) -> tuple[MechanicTraceSnapshot, ...]:
    snapshots: list[MechanicTraceSnapshot] = []
    for event in result.trace.events:
        receipt = event.receipt
        operator = getattr(event.operator, "value", str(event.operator)) if hasattr(event, "operator") else ""
        status_value = getattr(getattr(receipt, "status", ""), "value", getattr(receipt, "status", ""))
        snapshots.append(
            MechanicTraceSnapshot(
                operator=operator,
                summary=str(getattr(event, "summary", "")),
                receipt_id=str(getattr(receipt, "receipt_id", "")),
                mechanic_id=str(getattr(receipt, "mechanic_id", "")),
                status=str(status_value),
                action_ids=tuple(getattr(receipt, "action_ids", ())),
                evidence_ids=tuple(getattr(receipt, "evidence_ids", ())),
                residual_ids=tuple(getattr(receipt, "residual_ids", ())),
                failure_signature=tuple(getattr(receipt, "failure_signature", ())),
                handoff_values=tuple(getattr(receipt, "handoff_values", ())),
                provenance_ids=tuple(getattr(receipt, "provenance_ids", ())),
            )
        )
    return tuple(snapshots)


def _absorbed_evidence_ids(result: RuntimeResult) -> tuple[str, ...]:
    final_state = getattr(result, "final_state", None)
    knowledge = getattr(final_state, "knowledge", None)
    evidence_ids = getattr(knowledge, "evidence_ids", None)
    if evidence_ids is None:
        return tuple(result.solution.evidence_ids)
    return tuple(evidence_ids)


class ShadowLiveTrialRunner:
    """Execute a frozen matched-resource trial without granting promotion authority."""

    def __init__(
        self,
        *,
        orion: OrionRuntime,
        baseline: BaselineResearchRunner,
        retrieval_recorder: RecordingRetrievalProvider | None = None,
    ) -> None:
        self._orion = orion
        self._baseline = baseline
        self._retrieval_recorder = retrieval_recorder

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
    ) -> ShadowLiveTrialRunner:
        """Build the trial runtime with mandatory raw retrieval instrumentation."""

        recorder = RecordingRetrievalProvider(retrieval)
        runtime = OrionRuntime.from_providers(
            llm=llm,
            retrieval=recorder,
            verification=verification,
            experience_store=experience_store,
            config=config,
            guards=guards,
            producer_process_lineage_hash=producer_process_lineage_hash,
            evaluator_artifact_hash=evaluator_artifact_hash,
        )
        return cls(
            orion=runtime,
            baseline=baseline,
            retrieval_recorder=recorder,
        )

    def run(self, packet: FrozenLiveTrialPacket) -> ShadowLiveTrialReport:
        comparisons: list[TrialTaskComparison] = []
        for task in packet.tasks:
            observation_mark = (
                self._retrieval_recorder.mark()
                if self._retrieval_recorder is not None
                else None
            )
            baseline = self._baseline.run(
                task, evaluation_epoch_id=packet.evaluation_epoch_id
            )
            orion = self._orion.solve(
                task.problem,
                variation_signature=task.variation_signature,
                evaluation_epoch_id=packet.evaluation_epoch_id,
                split_id=task.split_id,
            )
            search_observations = (
                self._retrieval_recorder.observations_since(observation_mark)
                if self._retrieval_recorder is not None
                and observation_mark is not None
                else ()
            )
            orion_resources = _orion_resources(orion)
            resource_limit = min(
                packet.resource_budget_units,
                baseline.resource_units * packet.max_orion_to_baseline_resource_ratio
                if baseline.resource_units > 0
                else packet.resource_budget_units,
            )
            solution_ids = tuple(orion.solution.evidence_ids)
            absorbed_ids = _absorbed_evidence_ids(orion)
            retrieved_ids = tuple(
                dict.fromkeys(
                    item.item_id
                    for observation in search_observations
                    for item in observation.items
                )
            )
            required_recovered = set(task.required_evidence_ids).issubset(solution_ids)
            comparisons.append(
                TrialTaskComparison(
                    task_id=task.task_id,
                    kind=task.kind,
                    orion_status=orion.solution.status,
                    orion_evidence_count=len(solution_ids),
                    orion_residual_count=len(orion.solution.residual_ids),
                    orion_resource_units=orion_resources,
                    baseline_solved=baseline.solved,
                    baseline_evidence_count=len(baseline.evidence_ids),
                    baseline_residual_count=len(baseline.residual_ids),
                    baseline_resource_units=baseline.resource_units,
                    resource_matched=orion_resources <= resource_limit,
                    required_evidence_recovered=required_recovered,
                    root_episode_id=orion.experience_episode_id,
                    mechanic_episode_ids=orion.mechanic_experience_episode_ids,
                    search_observations=search_observations,
                    mechanic_trace=_trace_snapshot(orion),
                    solution_evidence_ids=solution_ids,
                    absorbed_evidence_ids=absorbed_ids,
                    retrieved_but_unused_ids=tuple(
                        item for item in retrieved_ids if item not in set(solution_ids)
                    ),
                    retrieved_but_unabsorbed_ids=tuple(
                        item for item in retrieved_ids if item not in set(absorbed_ids)
                    ),
                )
            )
        return ShadowLiveTrialReport(
            packet_id=packet.packet_id,
            packet_fingerprint=packet.fingerprint,
            comparisons=tuple(comparisons),
            all_resource_matched=all(item.resource_matched for item in comparisons),
            all_failures_recordable=all(
                item.orion_status is SolutionStatus.SOLVED_VERIFIED
                or item.root_episode_id is not None
                for item in comparisons
            ),
            wide_task_count=sum(
                item.kind is ResearchTrialKind.WIDE_LITERATURE
                for item in comparisons
            ),
            deep_task_count=sum(
                item.kind is ResearchTrialKind.DEEP_TARGET for item in comparisons
            ),
            boundary=(
                "This report is Shadow evidence only. It compares the frozen ORION runtime with a matched baseline, preserves raw retrieval/search and mechanic-use traces when built through from_providers, and preserves episode identities. "
                "It cannot promote ORION, modify its evaluator, or establish general autonomous-research capability."
            ),
        )


__all__ = [
    "BaselineResearchRunner",
    "BaselineTaskResult",
    "FrozenLiveTrialPacket",
    "FrozenTrialTask",
    "MechanicTraceSnapshot",
    "RecordingRetrievalProvider",
    "ResearchTrialKind",
    "RetrievedItemSnapshot",
    "SearchObservation",
    "ShadowLiveTrialReport",
    "ShadowLiveTrialRunner",
    "TrialTaskComparison",
]
