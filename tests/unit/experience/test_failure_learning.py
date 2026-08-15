from orion.experience import (
    EpisodeOutcome,
    ExperienceLedger,
    LessonAuthority,
    PatternAssessmentVerdict,
    PatternValidationEvidence,
    PatternVerificationReceipt,
    TaskEpisode,
    assess_pattern_reuse,
    failure_pattern_fingerprint,
    propose_failure_pattern,
    related_failure_episodes,
)


def _episode(
    episode_id,
    variation,
    outcome,
    *,
    failure=("missed_parent_domain", "false_flatness"),
    mechanic_id="SEARCH.v1",
    action_ids=("search",),
):
    return TaskEpisode(
        episode_id=episode_id,
        task_id=f"task:{episode_id}",
        mechanic_id=mechanic_id,
        problem_signature=("open-world-search", "parent-discipline"),
        variation_signature=(variation,),
        pre_state_hash=f"pre:{episode_id}",
        action_ids=action_ids,
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
    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:parent-domain-miss",
        candidate_guard="run a parent-discipline challenge before task saturation",
        falsifier="fresh tasks no longer benefit from the guard",
    )
    assert candidate is not None
    guard_action = f"guard:{candidate.pattern_id}"
    replay = _episode("replay", "replay", EpisodeOutcome.SUCCESS, action_ids=("search", guard_action))
    fresh = _episode("fresh", "unseen-domain", EpisodeOutcome.SUCCESS, action_ids=("search", guard_action))
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
            verification_receipt=PatternVerificationReceipt(
                receipt_id="verify:pattern:parent-domain-miss",
                pattern_id=candidate.pattern_id,
                pattern_hash=failure_pattern_fingerprint(candidate),
                verified_episode_ids=("replay", "fresh"),
                verifier_id="protected:test-verifier",
                certificate_ids=("certificate:pattern:parent-domain-miss",),
                passed=True,
                independent=True,
            ),
        ),
    )
    assert transferred.verdict is PatternAssessmentVerdict.CONDITIONALLY_REUSABLE
    assert transferred.reusable


def test_failed_fresh_transfer_contradicts_reuse_candidate():
    first = _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE)
    second = _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE)
    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:parent-domain-miss",
        candidate_guard="run a parent-discipline challenge before task saturation",
        falsifier="fresh tasks no longer benefit from the guard",
    )
    assert candidate is not None
    guard_action = f"guard:{candidate.pattern_id}"
    replay = _episode("replay", "replay", EpisodeOutcome.SUCCESS, action_ids=("search", guard_action))
    fresh_failure = _episode(
        "fresh-failure",
        "unseen-domain",
        EpisodeOutcome.FAILURE,
        action_ids=("search", guard_action),
    )
    ledger = ExperienceLedger(episodes=(first, second, replay, fresh_failure), failure_patterns=(candidate,))
    assessment = assess_pattern_reuse(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh-failure",),
            verification_receipt=PatternVerificationReceipt(
                receipt_id="verify:failed-transfer",
                pattern_id=candidate.pattern_id,
                pattern_hash=failure_pattern_fingerprint(candidate),
                verified_episode_ids=("replay", "fresh-failure"),
                verifier_id="protected:test-verifier",
                certificate_ids=("certificate:failed-transfer",),
                passed=False,
                independent=True,
            ),
        ),
    )
    assert assessment.verdict is PatternAssessmentVerdict.CONTRADICTED
    assert not assessment.reusable


def test_unrelated_successes_cannot_promote_a_failure_pattern():
    first = _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE)
    second = _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE)
    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:parent-domain-miss",
        candidate_guard="run a parent-discipline challenge before task saturation",
        falsifier="fresh tasks no longer benefit from the guard",
    )
    assert candidate is not None
    unrelated = _episode(
        "unrelated",
        "unseen-domain",
        EpisodeOutcome.SUCCESS,
        mechanic_id="ABSORB.v1",
        action_ids=("absorb",),
    )
    ledger = ExperienceLedger(episodes=(first, second, unrelated), failure_patterns=(candidate,))

    assessment = assess_pattern_reuse(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("unrelated",),
            fresh_transfer_episode_ids=("unrelated",),
        ),
    )

    assert assessment.verdict is PatternAssessmentVerdict.CANNOT_CHECK
    assert any("mechanic_mismatch" in reason for reason in assessment.reasons)


def test_success_without_candidate_guard_execution_cannot_validate_reuse():
    first = _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE)
    second = _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE)
    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:parent-domain-miss",
        candidate_guard="run a parent-discipline challenge before task saturation",
        falsifier="fresh tasks no longer benefit from the guard",
    )
    assert candidate is not None
    success = _episode("success", "unseen-domain", EpisodeOutcome.SUCCESS)
    ledger = ExperienceLedger(episodes=(first, second, success), failure_patterns=(candidate,))

    assessment = assess_pattern_reuse(
        ledger,
        candidate,
        PatternValidationEvidence(replay_episode_ids=("success",)),
    )

    assert assessment.verdict is PatternAssessmentVerdict.CANNOT_CHECK
    assert assessment.reasons == ("guard_not_executed:success",)


def test_candidate_must_be_registered_in_ledger_before_assessment():
    first = _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE)
    second = _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE)
    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:parent-domain-miss",
        candidate_guard="run a parent-discipline challenge before task saturation",
        falsifier="fresh tasks no longer benefit from the guard",
    )
    assert candidate is not None

    assessment = assess_pattern_reuse(
        ExperienceLedger(episodes=(first, second)),
        candidate,
        PatternValidationEvidence(),
    )

    assert assessment.verdict is PatternAssessmentVerdict.CANNOT_CHECK
    assert assessment.reasons == ("candidate_not_registered",)


def test_duplicate_episode_identity_cannot_form_cross_variation_pattern():
    first = _episode("same", "vocabulary-a", EpisodeOutcome.FAILURE)
    duplicate_identity = _episode("same", "vocabulary-b", EpisodeOutcome.FAILURE)

    candidate = propose_failure_pattern(
        (first, duplicate_identity),
        pattern_id="pattern:invalid-duplicate",
        candidate_guard="do something",
        falsifier="fresh failure",
    )

    assert candidate is None


def test_verification_receipt_must_bind_exact_candidate_content():
    first = _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE)
    second = _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE)
    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:parent-domain-miss",
        candidate_guard="run a parent-discipline challenge before task saturation",
        falsifier="fresh tasks no longer benefit from the guard",
    )
    assert candidate is not None
    guard_action = f"guard:{candidate.pattern_id}"
    replay = _episode("replay", "replay", EpisodeOutcome.SUCCESS, action_ids=(guard_action,))
    fresh = _episode("fresh", "unseen-domain", EpisodeOutcome.SUCCESS, action_ids=(guard_action,))
    ledger = ExperienceLedger(episodes=(first, second, replay, fresh), failure_patterns=(candidate,))

    assessment = assess_pattern_reuse(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh",),
            verification_receipt=PatternVerificationReceipt(
                receipt_id="verify:wrong-content",
                pattern_id=candidate.pattern_id,
                pattern_hash="0" * 64,
                verified_episode_ids=("replay", "fresh"),
                verifier_id="protected:test-verifier",
                certificate_ids=("certificate:wrong-content",),
                passed=True,
                independent=True,
            ),
        ),
    )

    assert assessment.verdict is PatternAssessmentVerdict.CANNOT_CHECK
    assert assessment.reasons == ("verification_subject_hash_mismatch",)
