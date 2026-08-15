from orion.experience import (
    EpisodeOutcome,
    ExperienceLedger,
    LessonAuthority,
    PatternAssessmentVerdict,
    PatternValidationEvidence,
    TaskEpisode,
    assess_pattern_reuse,
    propose_failure_pattern,
    related_failure_episodes,
)


def _episode(episode_id, variation, outcome, *, failure=("missed_parent_domain", "false_flatness")):
    return TaskEpisode(
        episode_id=episode_id,
        task_id=f"task:{episode_id}",
        mechanic_id="SEARCH.v1",
        problem_signature=("open-world-search", "parent-discipline"),
        variation_signature=(variation,),
        pre_state_hash=f"pre:{episode_id}",
        action_ids=("search",),
        observation_ids=(f"obs:{episode_id}",),
        outcome=outcome,
        failure_signature=failure if outcome is not EpisodeOutcome.SUCCESS else (),
        residual_ids=(f"residual:{episode_id}",) if outcome is not EpisodeOutcome.SUCCESS else (),
        evidence_ids=(f"evidence:{episode_id}",),
        post_state_hash=f"post:{episode_id}",
        timestamp="2026-08-15T20:00:00+02:00",
    )


def test_failure_variations_form_candidate_knowledge_but_not_authority():
    first = _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE)
    second = _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE)
    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:parent-domain-miss",
        candidate_guard="run a parent-discipline challenge before task saturation",
        falsifier="fresh tasks no longer benefit from the guard",
    )
    assert candidate is not None
    assert candidate.authority is LessonAuthority.CANDIDATE
    assert len(candidate.variation_signatures) == 2
    assert related_failure_episodes(first, (first, second)) == (second,)

    assessment = assess_pattern_reuse(
        ExperienceLedger(episodes=(first, second), failure_patterns=(candidate,)),
        candidate,
        PatternValidationEvidence(),
    )
    assert assessment.verdict is PatternAssessmentVerdict.CANDIDATE_ONLY
    assert not assessment.reusable


def test_replay_and_fresh_transfer_are_separate_promotion_gates():
    first = _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE)
    second = _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE)
    replay = _episode("replay", "replay", EpisodeOutcome.SUCCESS)
    fresh = _episode("fresh", "unseen-domain", EpisodeOutcome.SUCCESS)
    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:parent-domain-miss",
        candidate_guard="run a parent-discipline challenge before task saturation",
        falsifier="fresh tasks no longer benefit from the guard",
    )
    assert candidate is not None
    ledger = ExperienceLedger(episodes=(first, second, replay, fresh), failure_patterns=(candidate,))

    local = assess_pattern_reuse(ledger, candidate, PatternValidationEvidence(replay_episode_ids=("replay",)))
    assert local.verdict is PatternAssessmentVerdict.VERIFIED_LOCAL
    assert not local.reusable

    transferred = assess_pattern_reuse(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh",),
            independent_verification=True,
        ),
    )
    assert transferred.verdict is PatternAssessmentVerdict.CONDITIONALLY_REUSABLE
    assert transferred.reusable


def test_failed_fresh_transfer_contradicts_reuse_candidate():
    first = _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE)
    second = _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE)
    replay = _episode("replay", "replay", EpisodeOutcome.SUCCESS)
    fresh_failure = _episode("fresh-failure", "unseen-domain", EpisodeOutcome.FAILURE)
    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:parent-domain-miss",
        candidate_guard="run a parent-discipline challenge before task saturation",
        falsifier="fresh tasks no longer benefit from the guard",
    )
    assert candidate is not None
    ledger = ExperienceLedger(episodes=(first, second, replay, fresh_failure), failure_patterns=(candidate,))
    assessment = assess_pattern_reuse(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh-failure",),
            independent_verification=True,
        ),
    )
    assert assessment.verdict is PatternAssessmentVerdict.CONTRADICTED
    assert not assessment.reusable
