from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum

from orion.mechanics.model import MetricObservation


class EpisodeOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILURE = "FAILURE"
    BLOCKED = "BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


class LessonAuthority(str, Enum):
    CANDIDATE = "CANDIDATE"
    VERIFIED_LOCAL = "VERIFIED_LOCAL"
    CONDITIONALLY_REUSABLE = "CONDITIONALLY_REUSABLE"


@dataclass(frozen=True)
class TaskEpisode:
    """Immutable observation of what ORION actually attempted and observed."""

    episode_id: str
    task_id: str
    run_id: str
    parent_run_id: str | None
    evaluation_epoch_id: str
    split_id: str
    mechanic_id: str
    problem_signature: tuple[str, ...]
    variation_signature: tuple[str, ...]
    pre_state_hash: str
    action_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    outcome: EpisodeOutcome
    failure_signature: tuple[str, ...]
    residual_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    evidence_bindings: tuple[tuple[str, str], ...]
    post_state_hash: str
    timestamp: str
    producer_process_lineage_hash: str | None = None
    evaluator_artifact_hash: str | None = None
    source_receipt_id: str | None = None
    output_artifact_ids: tuple[str, ...] = ()
    handoff_values: tuple[tuple[str, str], ...] = ()
    metric_observations: tuple[MetricObservation, ...] = ()
    provenance_ids: tuple[str, ...] = ()
    cost_units: float | None = None
    latency_seconds: float | None = None

    def __post_init__(self) -> None:
        required = (
            self.episode_id,
            self.task_id,
            self.run_id,
            self.evaluation_epoch_id,
            self.split_id,
            self.mechanic_id,
            self.pre_state_hash,
            self.post_state_hash,
            self.timestamp,
        )
        if any(not value.strip() for value in required):
            raise ValueError(
                "episode identities, state hashes and timestamp are required"
            )
        if self.parent_run_id == self.run_id:
            raise ValueError("an episode cannot be its own parent run")
        if not self.problem_signature:
            raise ValueError("episode problem signature is required")
        if not self.action_ids:
            raise ValueError("episode action trace is required")
        if self.cost_units is not None and self.cost_units < 0:
            raise ValueError("episode cost cannot be negative")
        if self.latency_seconds is not None and self.latency_seconds < 0:
            raise ValueError("episode latency cannot be negative")
        for digest in (
            self.producer_process_lineage_hash,
            self.evaluator_artifact_hash,
        ):
            if digest is not None and (
                len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
            ):
                raise ValueError("episode lineage bindings must be SHA-256 hashes")
        binding_ids = [evidence_id for evidence_id, _ in self.evidence_bindings]
        if len(set(binding_ids)) != len(binding_ids):
            raise ValueError("episode evidence bindings must have unique ids")
        if set(binding_ids) != set(self.evidence_ids):
            raise ValueError("episode must content-bind every evidence id")
        for _, digest in self.evidence_bindings:
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError("episode evidence bindings require SHA-256 hashes")
        if self.outcome in {
            EpisodeOutcome.FAILURE,
            EpisodeOutcome.PARTIAL_SUCCESS,
            EpisodeOutcome.BLOCKED,
            EpisodeOutcome.CANNOT_CHECK,
        } and not (self.failure_signature or self.residual_ids):
            raise ValueError(
                "non-success episode requires a failure signature or residual"
            )


def task_episode_fingerprint(episode: TaskEpisode) -> str:
    payload = {
        "episode_id": episode.episode_id,
        "task_id": episode.task_id,
        "run_id": episode.run_id,
        "parent_run_id": episode.parent_run_id,
        "evaluation_epoch_id": episode.evaluation_epoch_id,
        "split_id": episode.split_id,
        "mechanic_id": episode.mechanic_id,
        "problem_signature": list(episode.problem_signature),
        "variation_signature": list(episode.variation_signature),
        "pre_state_hash": episode.pre_state_hash,
        "action_ids": list(episode.action_ids),
        "observation_ids": list(episode.observation_ids),
        "outcome": episode.outcome.value,
        "failure_signature": list(episode.failure_signature),
        "residual_ids": list(episode.residual_ids),
        "evidence_ids": list(episode.evidence_ids),
        "evidence_bindings": [list(item) for item in episode.evidence_bindings],
        "post_state_hash": episode.post_state_hash,
        "timestamp": episode.timestamp,
        "producer_process_lineage_hash": episode.producer_process_lineage_hash,
        "evaluator_artifact_hash": episode.evaluator_artifact_hash,
        "source_receipt_id": episode.source_receipt_id,
        "output_artifact_ids": list(episode.output_artifact_ids),
        "handoff_values": [list(item) for item in episode.handoff_values],
        "metric_observations": [
            {
                "metric_id": item.metric_id,
                "value": item.value,
                "unit": item.unit,
                "evidence_ids": list(item.evidence_ids),
                "uncertainty": item.uncertainty,
            }
            for item in episode.metric_observations
        ],
        "provenance_ids": list(episode.provenance_ids),
        "cost_units": episode.cost_units,
        "latency_seconds": episode.latency_seconds,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class FailurePatternCandidate:
    pattern_id: str
    mechanic_id: str
    core_failure_signature: tuple[str, ...]
    variation_signatures: tuple[tuple[str, ...], ...]
    supporting_episode_ids: tuple[str, ...]
    candidate_guard: str
    falsifier: str
    authority: LessonAuthority = LessonAuthority.CANDIDATE

    def __post_init__(self) -> None:
        if (
            not self.pattern_id.strip()
            or not self.mechanic_id.strip()
            or not self.candidate_guard.strip()
            or not self.falsifier.strip()
        ):
            raise ValueError(
                "failure pattern identity, mechanic, guard and falsifier are required"
            )
        if not self.core_failure_signature or len(self.supporting_episode_ids) < 2:
            raise ValueError(
                "failure pattern requires a shared signature and at least two episodes"
            )
        if len(set(self.supporting_episode_ids)) != len(self.supporting_episode_ids):
            raise ValueError("failure pattern supporting episode ids must be unique")
        if len(set(self.variation_signatures)) != len(self.variation_signatures):
            raise ValueError("failure pattern variation signatures must be unique")
        if self.authority is not LessonAuthority.CANDIDATE:
            raise ValueError(
                "failure pattern candidates cannot self-assert promoted authority"
            )


def structural_failure_signature(episode: TaskEpisode) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                *episode.failure_signature,
                *(f"residual:{item}" for item in episode.residual_ids),
            }
        )
    )


def failure_pattern_support_reasons(
    candidate: FailurePatternCandidate,
    episodes: tuple[TaskEpisode, ...],
) -> tuple[str, ...]:
    """Revalidate candidate recurrence from immutable support episode content."""

    by_id = {episode.episode_id: episode for episode in episodes}
    reasons: list[str] = []
    support: list[TaskEpisode] = []
    for episode_id in candidate.supporting_episode_ids:
        episode = by_id.get(episode_id)
        if episode is None:
            reasons.append(f"unknown_support_episode:{episode_id}")
            continue
        support.append(episode)
        if episode.mechanic_id != candidate.mechanic_id:
            reasons.append(f"invalid_support_mechanic:{episode_id}")
        if episode.outcome not in {
            EpisodeOutcome.FAILURE,
            EpisodeOutcome.PARTIAL_SUCCESS,
            EpisodeOutcome.BLOCKED,
            EpisodeOutcome.CANNOT_CHECK,
        }:
            reasons.append(f"invalid_support_outcome:{episode_id}")
        if not set(candidate.core_failure_signature).issubset(
            structural_failure_signature(episode)
        ):
            reasons.append(f"invalid_support_signature:{episode_id}")
    root_run_ids = [episode.parent_run_id or episode.run_id for episode in support]
    if len(set(root_run_ids)) != len(root_run_ids):
        reasons.append("support_runs_not_independent")
    observed_variations = tuple(
        sorted({episode.variation_signature for episode in support})
    )
    if len(observed_variations) < 2:
        reasons.append("support_variations_not_distinct")
    if observed_variations != tuple(sorted(candidate.variation_signatures)):
        reasons.append("support_variation_manifest_mismatch")
    return tuple(reasons)


def failure_pattern_fingerprint(candidate: FailurePatternCandidate) -> str:
    payload = {
        "pattern_id": candidate.pattern_id,
        "mechanic_id": candidate.mechanic_id,
        "core_failure_signature": list(candidate.core_failure_signature),
        "variation_signatures": [list(item) for item in candidate.variation_signatures],
        "supporting_episode_ids": list(candidate.supporting_episode_ids),
        "candidate_guard": candidate.candidate_guard,
        "falsifier": candidate.falsifier,
        "authority": candidate.authority.value,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class PatternVerificationReceipt:
    """Protected, subject-bound verification of replay and fresh-transfer episodes.

    The assessment layer consumes this receipt but never mints it. Concrete runtime
    integrations must obtain it from a verifier outside the candidate/solver path.
    """

    receipt_id: str
    pattern_id: str
    pattern_hash: str
    episode_bindings: tuple[tuple[str, str], ...]
    verifier_id: str
    key_id: str
    process_lineage_hash: str
    evaluator_artifact_hash: str
    evidence_lineage_hash: str
    passed: bool
    reason: str
    issued_at: str
    signature: str

    def __post_init__(self) -> None:
        required = (
            self.receipt_id,
            self.pattern_id,
            self.pattern_hash,
            self.verifier_id,
            self.key_id,
            self.process_lineage_hash,
            self.evaluator_artifact_hash,
            self.evidence_lineage_hash,
            self.reason,
            self.issued_at,
            self.signature,
        )
        if any(not value.strip() for value in required):
            raise ValueError(
                "pattern verification receipt identity fields are required"
            )
        if len(self.pattern_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.pattern_hash
        ):
            raise ValueError(
                "pattern verification receipt requires a SHA-256 subject hash"
            )
        for digest in (
            self.process_lineage_hash,
            self.evaluator_artifact_hash,
            self.evidence_lineage_hash,
        ):
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError(
                    "pattern verification lineage bindings require SHA-256 hashes"
                )
        if not self.episode_bindings:
            raise ValueError("pattern verification receipt requires episode bindings")
        episode_ids = [episode_id for episode_id, _ in self.episode_bindings]
        if len(set(episode_ids)) != len(episode_ids):
            raise ValueError("verified episode ids must be unique")
        for _, digest in self.episode_bindings:
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError(
                    "pattern verification episode bindings require SHA-256 hashes"
                )
        if len(self.signature) != 128 or any(
            character not in "0123456789abcdef" for character in self.signature
        ):
            raise ValueError(
                "pattern verification receipt requires an Ed25519 signature"
            )


@dataclass(frozen=True)
class PatternValidationEvidence:
    replay_episode_ids: tuple[str, ...] = ()
    fresh_transfer_episode_ids: tuple[str, ...] = ()
    verification_receipt: PatternVerificationReceipt | None = None


class PatternAssessmentVerdict(str, Enum):
    CANDIDATE_ONLY = "CANDIDATE_ONLY"
    VERIFIED_LOCAL = "VERIFIED_LOCAL"
    CONDITIONALLY_REUSABLE = "CONDITIONALLY_REUSABLE"
    CONTRADICTED = "CONTRADICTED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class PatternAssessment:
    verdict: PatternAssessmentVerdict
    target_authority: LessonAuthority
    reasons: tuple[str, ...]

    @property
    def reusable(self) -> bool:
        return self.verdict is PatternAssessmentVerdict.CONDITIONALLY_REUSABLE


@dataclass(frozen=True)
class ExperienceLedger:
    episodes: tuple[TaskEpisode, ...] = ()
    failure_patterns: tuple[FailurePatternCandidate, ...] = ()

    def __post_init__(self) -> None:
        episode_ids = [item.episode_id for item in self.episodes]
        if len(set(episode_ids)) != len(episode_ids):
            raise ValueError("experience ledger episode ids must be unique")
        pattern_ids = [item.pattern_id for item in self.failure_patterns]
        if len(set(pattern_ids)) != len(pattern_ids):
            raise ValueError("experience ledger pattern ids must be unique")
