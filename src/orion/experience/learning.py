from __future__ import annotations

from dataclasses import dataclass

from .authority import PatternVerificationTrustStore, resolve_pattern_verification
from .model import (
    EpisodeOutcome,
    ExperienceLedger,
    FailurePatternCandidate,
    LessonAuthority,
    PatternAssessment,
    PatternAssessmentVerdict,
    PatternValidationEvidence,
    TaskEpisode,
    failure_pattern_support_reasons,
    structural_failure_signature,
)

_FAILURE_OUTCOMES = {
    EpisodeOutcome.FAILURE,
    EpisodeOutcome.PARTIAL_SUCCESS,
    EpisodeOutcome.BLOCKED,
    EpisodeOutcome.CANNOT_CHECK,
}


def _normalized_failure_signature(episode: TaskEpisode) -> tuple[str, ...]:
    return structural_failure_signature(episode)


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
    independent_run_ids = {item.parent_run_id or item.run_id for item in failures}
    if len(independent_run_ids) != len(failures):
        return None
    mechanic_ids = {item.mechanic_id for item in failures}
    if len(mechanic_ids) != 1:
        return None
    distinct_variations = {item.variation_signature for item in failures}
    if len(distinct_variations) < 2:
        return None
    core = set(_normalized_failure_signature(failures[0]))
    for item in failures[1:]:
        core &= set(_normalized_failure_signature(item))
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
    """Assess without protected trust roots; this path can never promote reuse."""

    return _assess_pattern_reuse(ledger, candidate, evidence, trust_store=None)


@dataclass(frozen=True)
class ProtectedPatternReuseAssessor:
    """Host-owned promotion boundary, constructed outside candidate/solver control."""

    trust_store: PatternVerificationTrustStore

    def assess(
        self,
        ledger: ExperienceLedger,
        candidate: FailurePatternCandidate,
        evidence: PatternValidationEvidence,
    ) -> PatternAssessment:
        return _assess_pattern_reuse(
            ledger,
            candidate,
            evidence,
            trust_store=self.trust_store,
        )


def _assess_pattern_reuse(
    ledger: ExperienceLedger,
    candidate: FailurePatternCandidate,
    evidence: PatternValidationEvidence,
    *,
    trust_store: PatternVerificationTrustStore | None,
) -> PatternAssessment:
    """Keep recurrence as candidate knowledge until replay and fresh transfer succeed."""

    registered = next(
        (
            item
            for item in ledger.failure_patterns
            if item.pattern_id == candidate.pattern_id
        ),
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
    support_reasons = failure_pattern_support_reasons(candidate, ledger.episodes)
    if support_reasons:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            support_reasons,
        )

    referenced = set(evidence.replay_episode_ids) | set(
        evidence.fresh_transfer_episode_ids
    )
    missing = sorted(referenced - set(by_id))
    if missing:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            tuple(f"unknown_episode:{item}" for item in missing),
        )
    mechanic_mismatches = tuple(
        episode_id
        for episode_id in (
            *evidence.replay_episode_ids,
            *evidence.fresh_transfer_episode_ids,
        )
        if by_id[episode_id].mechanic_id != candidate.mechanic_id
    )
    if mechanic_mismatches:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            tuple(
                f"mechanic_mismatch:{item}"
                for item in dict.fromkeys(mechanic_mismatches)
            ),
        )
    if set(evidence.replay_episode_ids) & set(evidence.fresh_transfer_episode_ids):
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            ("replay_and_fresh_transfer_must_be_disjoint",),
        )
    support_episodes = tuple(by_id[item] for item in candidate.supporting_episode_ids)
    support_run_ids = {item.parent_run_id or item.run_id for item in support_episodes}
    replay_aliases = tuple(
        episode_id
        for episode_id in evidence.replay_episode_ids
        if (by_id[episode_id].parent_run_id or by_id[episode_id].run_id)
        in support_run_ids
    )
    if replay_aliases:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            tuple(f"replay_reuses_support_run:{item}" for item in replay_aliases),
        )
    support_replay_keys = {
        (item.task_id, item.problem_signature, item.variation_signature)
        for item in support_episodes
    }
    replay_mismatches = tuple(
        episode_id
        for episode_id in evidence.replay_episode_ids
        if (
            by_id[episode_id].task_id,
            by_id[episode_id].problem_signature,
            by_id[episode_id].variation_signature,
        )
        not in support_replay_keys
    )
    if replay_mismatches:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            tuple(
                f"replay_not_bound_to_support_case:{item}" for item in replay_mismatches
            ),
        )
    guard_action_id = f"guard:{candidate.pattern_id}"
    guard_missing = tuple(
        episode_id
        for episode_id in (
            *evidence.replay_episode_ids,
            *evidence.fresh_transfer_episode_ids,
        )
        if guard_action_id not in by_id[episode_id].action_ids
    )
    if guard_missing:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            tuple(
                f"guard_not_executed:{item}" for item in dict.fromkeys(guard_missing)
            ),
        )
    support_variations = {
        by_id[episode_id].variation_signature
        for episode_id in candidate.supporting_episode_ids
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
            tuple(
                f"fresh_transfer_not_fresh:{item}" for item in reused_fresh_variations
            ),
        )
    prior_episodes = support_episodes + tuple(
        by_id[item] for item in evidence.replay_episode_ids
    )
    prior_run_ids = {item.parent_run_id or item.run_id for item in prior_episodes}
    prior_task_ids = {item.task_id for item in prior_episodes}
    prior_split_ids = {item.split_id for item in prior_episodes}
    prior_evaluation_ids = {item.evaluation_epoch_id for item in prior_episodes}
    prior_variations = {item.variation_signature for item in prior_episodes}
    fresh_identity_failures: list[str] = []
    for episode_id in evidence.fresh_transfer_episode_ids:
        episode = by_id[episode_id]
        if (episode.parent_run_id or episode.run_id) in prior_run_ids:
            fresh_identity_failures.append(
                f"fresh_transfer_run_not_distinct:{episode_id}"
            )
        if episode.task_id in prior_task_ids:
            fresh_identity_failures.append(
                f"fresh_transfer_task_not_distinct:{episode_id}"
            )
        if episode.split_id in prior_split_ids:
            fresh_identity_failures.append(
                f"fresh_transfer_split_not_distinct:{episode_id}"
            )
        if episode.evaluation_epoch_id in prior_evaluation_ids:
            fresh_identity_failures.append(
                f"fresh_transfer_evaluation_not_distinct:{episode_id}"
            )
        if episode.variation_signature in prior_variations:
            fresh_identity_failures.append(
                f"fresh_transfer_variation_not_distinct:{episode_id}"
            )
        prior_run_ids.add(episode.parent_run_id or episode.run_id)
        prior_task_ids.add(episode.task_id)
        prior_split_ids.add(episode.split_id)
        prior_evaluation_ids.add(episode.evaluation_epoch_id)
        prior_variations.add(episode.variation_signature)
    if fresh_identity_failures:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.CANDIDATE,
            tuple(fresh_identity_failures),
        )
    if not evidence.replay_episode_ids:
        return PatternAssessment(
            PatternAssessmentVerdict.CANDIDATE_ONLY,
            LessonAuthority.CANDIDATE,
            (
                "repeated failures are observed but the candidate guard has not survived replay",
            ),
        )
    replay_failures = tuple(
        item
        for item in evidence.replay_episode_ids
        if by_id[item].outcome is not EpisodeOutcome.SUCCESS
    )
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
    transfer_failures = tuple(
        item
        for item in evidence.fresh_transfer_episode_ids
        if by_id[item].outcome is not EpisodeOutcome.SUCCESS
    )
    if transfer_failures:
        return PatternAssessment(
            PatternAssessmentVerdict.CONTRADICTED,
            LessonAuthority.VERIFIED_LOCAL,
            tuple(
                f"fresh_transfer_not_successful:{item}" for item in transfer_failures
            ),
        )
    receipt = evidence.verification_receipt
    if receipt is None:
        return PatternAssessment(
            PatternAssessmentVerdict.VERIFIED_LOCAL,
            LessonAuthority.VERIFIED_LOCAL,
            (
                "fresh transfer succeeded but independent/protected verification is absent",
            ),
        )
    if trust_store is None:
        return PatternAssessment(
            PatternAssessmentVerdict.VERIFIED_LOCAL,
            LessonAuthority.VERIFIED_LOCAL,
            ("protected promotion authority was not invoked",),
        )
    verification_episodes = tuple(
        by_id[item]
        for item in dict.fromkeys(
            candidate.supporting_episode_ids
            + evidence.replay_episode_ids
            + evidence.fresh_transfer_episode_ids
        )
    )
    resolution = resolve_pattern_verification(
        trust_store,
        receipt,
        candidate,
        verification_episodes,
    )
    if not resolution.valid:
        return PatternAssessment(
            PatternAssessmentVerdict.CANNOT_CHECK,
            LessonAuthority.VERIFIED_LOCAL,
            resolution.reasons,
        )
    if not receipt.passed:
        return PatternAssessment(
            PatternAssessmentVerdict.CONTRADICTED,
            LessonAuthority.VERIFIED_LOCAL,
            ("protected_verification_failed",),
        )
    if not (
        resolution.process_independent
        and resolution.evaluator_independent
        and resolution.evidence_lineage_independent
    ):
        return PatternAssessment(
            PatternAssessmentVerdict.VERIFIED_LOCAL,
            LessonAuthority.VERIFIED_LOCAL,
            resolution.reasons,
        )
    # V0 can authenticate who signed this exact assessment, but every lineage
    # label above is still supplied when the in-process identity/episodes are
    # constructed.  Unequal hashes therefore prove inequality, not independent
    # organizational or process custody.  Keep the future authority level in the
    # schema, but fail closed until an externally rooted separation attestor can
    # bind those lineages to independently controlled executions.
    return PatternAssessment(
        PatternAssessmentVerdict.VERIFIED_LOCAL,
        LessonAuthority.VERIFIED_LOCAL,
        ("external_lineage_separation_attestation_required",),
    )
