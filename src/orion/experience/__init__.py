"""Immutable problem-solving experience and failure-learning primitives."""

from .authority import (
    PatternVerificationResolution,
    PatternVerificationTrustStore,
    PatternVerifierRegistration,
    PatternVerifierSigningIdentity,
    evidence_binding_lineage_hash,
    mint_pattern_verification_receipt,
    resolve_pattern_verification,
)
from .learning import (
    ProtectedPatternReuseAssessor,
    assess_pattern_reuse,
    propose_failure_pattern,
)
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
    task_episode_fingerprint,
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
    "PatternVerificationResolution",
    "PatternVerificationTrustStore",
    "PatternVerifierRegistration",
    "PatternVerifierSigningIdentity",
    "ProtectedPatternReuseAssessor",
    "TaskEpisode",
    "assess_pattern_reuse",
    "episode_from_receipt",
    "evidence_binding_lineage_hash",
    "failure_pattern_fingerprint",
    "mint_pattern_verification_receipt",
    "propose_failure_pattern",
    "related_failure_episodes",
    "resolve_pattern_verification",
    "signature_similarity",
    "task_episode_fingerprint",
]
