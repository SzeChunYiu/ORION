from __future__ import annotations

from .model import (
    EpisodeOutcome,
    ExperienceLedger,
    FailurePatternCandidate,
    LessonAuthority,
    PatternAssessment,
    PatternAssessmentVerdict,
    PatternValidationEvidence,
    TaskEpisode,
)


_FAILURE_OUTCOMES = {EpisodeOutcome.FAILURE, EpisodeOutcome.PARTIAL_SUCCESS, EpisodeOutcome.BLOCKED}


def propose_failure_pattern(
    episodes: tuple[TaskEpisode, ...],
    *,
    pattern_id: str,
    candidate_guard: str,
    falsifier: str,
) -> FailurePatternCandidate | None:
    """Abstract repeated failure variations into a proposal-only candidate pattern."""

    failures = tuple(item for item in episodes if item.outcome in _FAILURE_OUTCOMES)
    if len(failures) < 2:
        return None
    mechanic_ids = {item.mechanic_id for item in failures}
    if len(mechanic_ids) != 1:
        return None
    distinct_variations = {item.variation_signature for item in failures}
    if len(distinct_variations) < 2:
        return None
    core = set(failures[0].failure_signature)
    for item in failures[1:]:
        core &= set(item.failure_signature)
    if not core:
        return None
    return FailurePatternCandidate(
        pattern_id=pattern_id,
        mechanic_id=failures[0].mechanic_id,
        core_failure_signature=tuple(sorted(core)),
        variation_signatures=tuple(sorted(distinct_variations)),
        supporting_episode_ids=tuple(sorted(item.episode_id for item in failures)),
        candidate_guard=candidate_guard,
        falsifier=falsifier,
        authority=LessonAuthority.CANDIDATE,
    )


def assess_pattern_reuse(
    ledger: ExperienceLedger,
    candidate: FailurePatternCandidate,
    evidence: PatternValidationEvidence,
) -> PatternAssessment:
    """Keep recurrence as candidate knowledge until replay and fresh transfer succeed."""

    by_id = {item.episode_id: item for item in ledger.episodes}
    referenced = set(evidence.replay_episode_ids) | set(evidence.fresh_transfer_episode_ids)
    missing = sorted(referenced - set(by_id))
    if missing:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            tuple(f"unknown_episode:{item}" for item in missing),
        )
    if not evidence.replay_episode_ids:
        return PatternAssessment(
            PatternAssessmentVerdict.CANDIDATE_ONLY,
            LessonAuthority.CANDIDATE,
            ("repeated failures are observed but the candidate guard has not survived replay",),
        )
    replay_failures = tuple(item for item in evidence.replay_episode_ids if by_id[item].outcome is not EpisodeOutcome.SUCCESS)
    if replay_failures:
        return PatternAssessment(
            PatternAssessmentVerdict.CONTRADICTED,
            LessonAuthority.CANDIDATE,
            tuple(f"replay_not_successful:{item}" for item in replay_failures),
        )
    if not evidence.fresh_transfer_episode_ids:
        return PatternAssessment(
            PatternAssessmentVerdict.VERIFIED_LOCAL,
            LessonAuthority.VERIFIED_LOCAL,
            ("candidate guard survived replay but has no fresh transfer evidence",),
        )
    transfer_failures = tuple(item for item in evidence.fresh_transfer_episode_ids if by_id[item].outcome is not EpisodeOutcome.SUCCESS)
    if transfer_failures:
        return PatternAssessment(
            PatternAssessmentVerdict.CONTRADICTED,
            LessonAuthority.VERIFIED_LOCAL,
            tuple(f"fresh_transfer_not_successful:{item}" for item in transfer_failures),
        )
    if not evidence.independent_verification:
        return PatternAssessment(
            PatternAssessmentVerdict.VERIFIED_LOCAL,
            LessonAuthority.VERIFIED_LOCAL,
            ("fresh transfer succeeded but independent/protected verification is absent",),
        )
    return PatternAssessment(
        PatternAssessmentVerdict.CONDITIONALLY_REUSABLE,
        LessonAuthority.CONDITIONALLY_REUSABLE,
        ("candidate guard survived replay and fresh independently verified transfer",),
    )
