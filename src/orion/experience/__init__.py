"""Immutable problem-solving experience and failure-learning primitives."""

from .learning import assess_pattern_reuse, propose_failure_pattern
from .matching import related_failure_episodes, signature_similarity
from .model import (
    EpisodeOutcome,
    ExperienceLedger,
    FailurePatternCandidate,
    LessonAuthority,
    PatternAssessment,
    PatternAssessmentVerdict,
    PatternValidationEvidence,
    PatternVerificationReceipt,
    TaskEpisode,
    failure_pattern_fingerprint,
)
from .recording import episode_from_receipt

__all__ = [
    "EpisodeOutcome",
    "ExperienceLedger",
    "FailurePatternCandidate",
    "LessonAuthority",
    "PatternAssessment",
    "PatternAssessmentVerdict",
    "PatternValidationEvidence",
    "PatternVerificationReceipt",
    "TaskEpisode",
    "assess_pattern_reuse",
    "episode_from_receipt",
    "failure_pattern_fingerprint",
    "propose_failure_pattern",
    "related_failure_episodes",
    "signature_similarity",
]
