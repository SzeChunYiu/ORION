from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from orion.core.problem import Problem
from orion.core.solution import SolutionStatus
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
        if any(not item.strip() for item in (self.packet_id, self.evaluation_epoch_id, self.provider_manifest_hash, self.evaluator_artifact_hash, self.baseline_id)):
            raise ValueError("trial packet identity/provider/evaluator/baseline fields are required")
        if self.resource_budget_units <= 0 or self.max_orion_to_baseline_resource_ratio <= 0:
            raise ValueError("trial resources must be positive")
        ids = [item.task_id for item in self.tasks]
        if not ids or len(set(ids)) != len(ids):
            raise ValueError("trial tasks must be non-empty and uniquely identified")
        kinds = {item.kind for item in self.tasks}
        if ResearchTrialKind.WIDE_LITERATURE not in kinds or ResearchTrialKind.DEEP_TARGET not in kinds:
            raise ValueError("Shadow live trial requires at least one wide-literature and one deep-target task")
        for digest in (self.provider_manifest_hash, self.evaluator_artifact_hash):
            if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
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
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


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
    def run(self, task: FrozenTrialTask, *, evaluation_epoch_id: str) -> BaselineTaskResult: ...


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


def _orion_resources(result: RuntimeResult) -> float:
    return sum(event.receipt.cost_units or 0.0 for event in result.trace.events)


class ShadowLiveTrialRunner:
    """Execute a frozen matched-resource trial without granting promotion authority."""

    def __init__(self, *, orion: OrionRuntime, baseline: BaselineResearchRunner) -> None:
        self._orion = orion
        self._baseline = baseline

    def run(self, packet: FrozenLiveTrialPacket) -> ShadowLiveTrialReport:
        comparisons: list[TrialTaskComparison] = []
        for task in packet.tasks:
            baseline = self._baseline.run(task, evaluation_epoch_id=packet.evaluation_epoch_id)
            orion = self._orion.solve(
                task.problem,
                variation_signature=task.variation_signature,
                evaluation_epoch_id=packet.evaluation_epoch_id,
                split_id=task.split_id,
            )
            orion_resources = _orion_resources(orion)
            resource_limit = min(
                packet.resource_budget_units,
                baseline.resource_units * packet.max_orion_to_baseline_resource_ratio
                if baseline.resource_units > 0
                else packet.resource_budget_units,
            )
            required_recovered = set(task.required_evidence_ids).issubset(orion.solution.evidence_ids)
            comparisons.append(
                TrialTaskComparison(
                    task_id=task.task_id,
                    kind=task.kind,
                    orion_status=orion.solution.status,
                    orion_evidence_count=len(orion.solution.evidence_ids),
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
            wide_task_count=sum(item.kind is ResearchTrialKind.WIDE_LITERATURE for item in comparisons),
            deep_task_count=sum(item.kind is ResearchTrialKind.DEEP_TARGET for item in comparisons),
            boundary=(
                "This report is Shadow evidence only. It compares the frozen ORION runtime with a matched baseline and preserves episode identities. "
                "It cannot promote ORION, modify its evaluator, or establish general autonomous-research capability."
            ),
        )


__all__ = [
    "BaselineResearchRunner",
    "BaselineTaskResult",
    "FrozenLiveTrialPacket",
    "FrozenTrialTask",
    "ResearchTrialKind",
    "ShadowLiveTrialReport",
    "ShadowLiveTrialRunner",
    "TrialTaskComparison",
]
