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
    failure_pattern_fingerprint,
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
    if len({item.episode_id for item in failures}) != len(failures):
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

    registered = next(
        (item for item in ledger.failure_patterns if item.pattern_id == candidate.pattern_id),
        None,
    )
    if registered is None:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            ("candidate_not_registered",),
        )
    if registered != candidate:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            ("candidate_content_mismatch",),
        )

    by_id = {item.episode_id: item for item in ledger.episodes}
    missing_support = sorted(set(candidate.supporting_episode_ids) - set(by_id))
    if missing_support:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            tuple(f"unknown_support_episode:{item}" for item in missing_support),
        )
    invalid_support = tuple(
        episode_id
        for episode_id in candidate.supporting_episode_ids
        if by_id[episode_id].mechanic_id != candidate.mechanic_id
        or by_id[episode_id].outcome not in _FAILURE_OUTCOMES
        or not set(candidate.core_failure_signature).issubset(by_id[episode_id].failure_signature)
    )
    if invalid_support:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            tuple(f"invalid_support_episode:{item}" for item in invalid_support),
        )

    referenced = set(evidence.replay_episode_ids) | set(evidence.fresh_transfer_episode_ids)
    missing = sorted(referenced - set(by_id))
    if missing:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            tuple(f"unknown_episode:{item}" for item in missing),
        )
    mechanic_mismatches = tuple(
        episode_id
        for episode_id in (*evidence.replay_episode_ids, *evidence.fresh_transfer_episode_ids)
        if by_id[episode_id].mechanic_id != candidate.mechanic_id
    )
    if mechanic_mismatches:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            tuple(f"mechanic_mismatch:{item}" for item in dict.fromkeys(mechanic_mismatches)),
        )
    if set(evidence.replay_episode_ids) & set(evidence.fresh_transfer_episode_ids):
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            ("replay_and_fresh_transfer_must_be_disjoint",),
        )
    guard_action_id = f"guard:{candidate.pattern_id}"
    guard_missing = tuple(
        episode_id
        for episode_id in (*evidence.replay_episode_ids, *evidence.fresh_transfer_episode_ids)
        if guard_action_id not in by_id[episode_id].action_ids
    )
    if guard_missing:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            tuple(f"guard_not_executed:{item}" for item in dict.fromkeys(guard_missing)),
        )
    support_variations = {
        by_id[episode_id].variation_signature for episode_id in candidate.supporting_episode_ids
    }
    reused_fresh_variations = tuple(
        episode_id
        for episode_id in evidence.fresh_transfer_episode_ids
        if by_id[episode_id].variation_signature in support_variations
    )
    if reused_fresh_variations:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            tuple(f"fresh_transfer_not_fresh:{item}" for item in reused_fresh_variations),
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
    receipt = evidence.verification_receipt
    if receipt is None:
        return PatternAssessment(
            PatternAssessmentVerdict.VERIFIED_LOCAL,
            LessonAuthority.VERIFIED_LOCAL,
            ("fresh transfer succeeded but independent/protected verification is absent",),
        )
    if receipt.pattern_id != candidate.pattern_id:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.VERIFIED_LOCAL,
            ("verification_subject_mismatch",),
        )
    if receipt.pattern_hash != failure_pattern_fingerprint(candidate):
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.VERIFIED_LOCAL,
            ("verification_subject_hash_mismatch",),
        )
    if set(receipt.verified_episode_ids) != referenced:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.VERIFIED_LOCAL,
            ("verification_episode_binding_mismatch",),
        )
    if not receipt.passed:
        return PatternAssessment(
            PatternAssessmentVerdict.CONTRADICTED,
            LessonAuthority.VERIFIED_LOCAL,
            ("protected_verification_failed",),
        )
    if not receipt.independent:
        return PatternAssessment(
            PatternAssessmentVerdict.VERIFIED_LOCAL,
            LessonAuthority.VERIFIED_LOCAL,
            ("verification receipt lacks evaluator/evidence-lineage independence",),
        )
    return PatternAssessment(
        PatternAssessmentVerdict.CONDITIONALLY_REUSABLE,
        LessonAuthority.CONDITIONALLY_REUSABLE,
        ("candidate guard survived replay and fresh independently verified transfer",),
    )
