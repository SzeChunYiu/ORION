from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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
    post_state_hash: str
    timestamp: str
    cost_units: float = 0.0

    def __post_init__(self) -> None:
        required = (self.episode_id, self.task_id, self.mechanic_id, self.pre_state_hash, self.post_state_hash, self.timestamp)
        if any(not value.strip() for value in required):
            raise ValueError("episode identities, state hashes and timestamp are required")
        if not self.problem_signature:
            raise ValueError("episode problem signature is required")
        if not self.action_ids:
            raise ValueError("episode action trace is required")
        if self.cost_units < 0:
            raise ValueError("episode cost cannot be negative")
        if self.outcome in {EpisodeOutcome.FAILURE, EpisodeOutcome.PARTIAL_SUCCESS, EpisodeOutcome.BLOCKED} and not (self.failure_signature or self.residual_ids):
            raise ValueError("non-success episode requires a failure signature or residual")


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
        if not self.pattern_id.strip() or not self.mechanic_id.strip() or not self.candidate_guard.strip() or not self.falsifier.strip():
            raise ValueError("failure pattern identity, mechanic, guard and falsifier are required")
        if not self.core_failure_signature or len(self.supporting_episode_ids) < 2:
            raise ValueError("failure pattern requires a shared signature and at least two episodes")


@dataclass(frozen=True)
class PatternValidationEvidence:
    replay_episode_ids: tuple[str, ...] = ()
    fresh_transfer_episode_ids: tuple[str, ...] = ()
    independent_verification: bool = False


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
