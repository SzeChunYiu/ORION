from __future__ import annotations

import hashlib
import json
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
        if self.outcome in {
            EpisodeOutcome.FAILURE,
            EpisodeOutcome.PARTIAL_SUCCESS,
            EpisodeOutcome.BLOCKED,
            EpisodeOutcome.CANNOT_CHECK,
        } and not (self.failure_signature or self.residual_ids):
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
        if len(set(self.supporting_episode_ids)) != len(self.supporting_episode_ids):
            raise ValueError("failure pattern supporting episode ids must be unique")
        if len(set(self.variation_signatures)) != len(self.variation_signatures):
            raise ValueError("failure pattern variation signatures must be unique")


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
    verified_episode_ids: tuple[str, ...]
    verifier_id: str
    certificate_ids: tuple[str, ...]
    passed: bool
    independent: bool
    reason: str = ""

    def __post_init__(self) -> None:
        required = (self.receipt_id, self.pattern_id, self.pattern_hash, self.verifier_id)
        if any(not value.strip() for value in required):
            raise ValueError("pattern verification receipt identity fields are required")
        if len(self.pattern_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.pattern_hash
        ):
            raise ValueError("pattern verification receipt requires a SHA-256 subject hash")
        if not self.verified_episode_ids:
            raise ValueError("pattern verification receipt requires episode bindings")
        if len(set(self.verified_episode_ids)) != len(self.verified_episode_ids):
            raise ValueError("verified episode ids must be unique")
        if self.passed and not self.certificate_ids:
            raise ValueError("passed pattern verification requires certificate ids")


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
