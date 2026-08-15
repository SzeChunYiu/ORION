from dataclasses import replace

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from orion.core import EvidenceRecord, evidence_record_fingerprint
from orion.experience import (
    EpisodeOutcome,
    ExperienceLedger,
    FailurePatternCandidate,
    LessonAuthority,
    PatternAssessmentVerdict,
    PatternValidationEvidence,
    PatternVerificationReceipt,
    PatternVerificationTrustStore,
    PatternVerifierRegistration,
    PatternVerifierSigningIdentity,
    ProtectedPatternReuseAssessor,
    TaskEpisode,
    assess_pattern_reuse,
    evidence_binding_lineage_hash,
    failure_pattern_fingerprint,
    mint_pattern_verification_receipt,
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
    task_id="task:parent-domain",
    run_id=None,
    evaluation_epoch_id="evaluation:source",
    split_id="split:source",
):
    return TaskEpisode(
        episode_id=episode_id,
        task_id=task_id,
        run_id=run_id or f"run:{episode_id}",
        parent_run_id=None,
        evaluation_epoch_id=evaluation_epoch_id,
        split_id=split_id,
        mechanic_id=mechanic_id,
        problem_signature=("open-world-search", "parent-discipline"),
        variation_signature=(variation,),
        pre_state_hash=f"pre:{episode_id}",
        action_ids=action_ids,
        observation_ids=(f"obs:{episode_id}",),
        outcome=outcome,
        failure_signature=failure if outcome is not EpisodeOutcome.SUCCESS else (),
        residual_ids=(f"residual:{episode_id}",)
        if outcome is not EpisodeOutcome.SUCCESS
        else (),
        evidence_ids=(f"evidence:{episode_id}",),
        evidence_bindings=((f"evidence:{episode_id}", "d" * 64),),
        post_state_hash=f"post:{episode_id}",
        timestamp="2026-08-15T20:00:00+02:00",
        producer_process_lineage_hash="a" * 64,
        evaluator_artifact_hash="b" * 64,
    )


def _protected_receipt(
    candidate,
    episodes,
    *,
    passed=True,
    process_lineage_hash="1" * 64,
    evaluator_artifact_hash="2" * 64,
    evidence_lineage_hash="3" * 64,
):
    signing = PatternVerifierSigningIdentity(
        verifier_id="protected:test-verifier",
        key_id="key:test-v1",
        signing_key=b"t" * 32,
        process_lineage_hash=process_lineage_hash,
        evaluator_artifact_hash=evaluator_artifact_hash,
        evidence_lineage_hash=evidence_lineage_hash,
    )
    context = PatternVerificationTrustStore(
        registrations=(
            PatternVerifierRegistration(
                verifier_id=signing.verifier_id,
                key_id=signing.key_id,
                verification_key=(
                    Ed25519PrivateKey.from_private_bytes(signing.signing_key)
                    .public_key()
                    .public_bytes_raw()
                ),
                process_lineage_hash=signing.process_lineage_hash,
                evaluator_artifact_hash=signing.evaluator_artifact_hash,
                evidence_lineage_hash=signing.evidence_lineage_hash,
            ),
        )
    )
    receipt = mint_pattern_verification_receipt(
        signing,
        candidate,
        episodes,
        passed=passed,
        reason="protected known-answer fixture",
        issued_at="2026-08-15T22:00:00+02:00",
    )
    return receipt, ProtectedPatternReuseAssessor(context)


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
    replay = _episode(
        "replay",
        "vocabulary-a",
        EpisodeOutcome.SUCCESS,
        action_ids=("search", guard_action),
    )
    fresh = _episode(
        "fresh",
        "unseen-domain",
        EpisodeOutcome.SUCCESS,
        action_ids=("search", guard_action),
        task_id="task:fresh-domain",
        evaluation_epoch_id="evaluation:fresh",
        split_id="split:fresh",
    )
    ledger = ExperienceLedger(
        episodes=(first, second, replay, fresh), failure_patterns=(candidate,)
    )

    local = assess_pattern_reuse(
        ledger, candidate, PatternValidationEvidence(replay_episode_ids=("replay",))
    )
    assert local.verdict is PatternAssessmentVerdict.VERIFIED_LOCAL
    assert not local.reusable

    receipt, authority = _protected_receipt(candidate, (first, second, replay, fresh))
    unprotected = assess_pattern_reuse(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh",),
            verification_receipt=receipt,
        ),
    )
    assert unprotected.verdict is PatternAssessmentVerdict.VERIFIED_LOCAL
    assert unprotected.reasons == ("protected promotion authority was not invoked",)
    transferred = authority.assess(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh",),
            verification_receipt=receipt,
        ),
    )
    assert transferred.verdict is PatternAssessmentVerdict.VERIFIED_LOCAL
    assert transferred.reasons == ("external_lineage_separation_attestation_required",)
    assert not transferred.reusable


def test_unequal_caller_selected_lineages_cannot_spoof_independent_promotion():
    first = _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE)
    second = _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE)
    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:caller-lineage-spoof",
        candidate_guard="challenge the parent-domain basis",
        falsifier="guard has no transfer benefit",
    )
    assert candidate is not None
    guard_action = f"guard:{candidate.pattern_id}"
    replay = _episode(
        "replay",
        "vocabulary-a",
        EpisodeOutcome.SUCCESS,
        action_ids=(guard_action,),
    )
    fresh = _episode(
        "fresh",
        "unseen-domain",
        EpisodeOutcome.SUCCESS,
        action_ids=(guard_action,),
        task_id="task:fresh-domain",
        evaluation_epoch_id="evaluation:fresh",
        split_id="split:fresh",
    )
    episodes = (first, second, replay, fresh)
    receipt, authority = _protected_receipt(
        candidate,
        episodes,
        process_lineage_hash="4" * 64,
        evaluator_artifact_hash="5" * 64,
        evidence_lineage_hash="6" * 64,
    )

    assessment = authority.assess(
        ExperienceLedger(episodes=episodes, failure_patterns=(candidate,)),
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh",),
            verification_receipt=receipt,
        ),
    )

    assert assessment.verdict is PatternAssessmentVerdict.VERIFIED_LOCAL
    assert assessment.reasons == ("external_lineage_separation_attestation_required",)
    assert not assessment.reusable


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
    replay = _episode(
        "replay",
        "vocabulary-a",
        EpisodeOutcome.SUCCESS,
        action_ids=("search", guard_action),
    )
    fresh_failure = _episode(
        "fresh-failure",
        "unseen-domain",
        EpisodeOutcome.FAILURE,
        action_ids=("search", guard_action),
        task_id="task:fresh-domain",
        evaluation_epoch_id="evaluation:fresh",
        split_id="split:fresh",
    )
    ledger = ExperienceLedger(
        episodes=(first, second, replay, fresh_failure), failure_patterns=(candidate,)
    )
    assessment = assess_pattern_reuse(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh-failure",),
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
    ledger = ExperienceLedger(
        episodes=(first, second, unrelated), failure_patterns=(candidate,)
    )

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
    success = _episode("success", "vocabulary-a", EpisodeOutcome.SUCCESS)
    ledger = ExperienceLedger(
        episodes=(first, second, success), failure_patterns=(candidate,)
    )

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
    replay = _episode(
        "replay", "vocabulary-a", EpisodeOutcome.SUCCESS, action_ids=(guard_action,)
    )
    fresh = _episode(
        "fresh",
        "unseen-domain",
        EpisodeOutcome.SUCCESS,
        action_ids=(guard_action,),
        task_id="task:fresh-domain",
        evaluation_epoch_id="evaluation:fresh",
        split_id="split:fresh",
    )
    ledger = ExperienceLedger(
        episodes=(first, second, replay, fresh), failure_patterns=(candidate,)
    )
    altered = replace(
        candidate, candidate_guard="different guard with the same pattern id"
    )
    receipt, authority = _protected_receipt(altered, (first, second, replay, fresh))

    assessment = authority.assess(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh",),
            verification_receipt=receipt,
        ),
    )

    assert assessment.verdict is PatternAssessmentVerdict.CANNOT_CHECK
    assert assessment.reasons == ("verification_subject_hash_mismatch",)


def test_caller_minted_receipt_cannot_promote_pattern():
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
    replay = _episode(
        "replay", "vocabulary-a", EpisodeOutcome.SUCCESS, action_ids=(guard_action,)
    )
    fresh = _episode(
        "fresh",
        "unseen-domain",
        EpisodeOutcome.SUCCESS,
        action_ids=(guard_action,),
        task_id="task:fresh-domain",
        evaluation_epoch_id="evaluation:fresh",
        split_id="split:fresh",
    )
    ledger = ExperienceLedger(
        episodes=(first, second, replay, fresh), failure_patterns=(candidate,)
    )
    forged = PatternVerificationReceipt(
        receipt_id="forged",
        pattern_id=candidate.pattern_id,
        pattern_hash=failure_pattern_fingerprint(candidate),
        episode_bindings=tuple(
            (item.episode_id, "0" * 64) for item in (first, second, replay, fresh)
        ),
        verifier_id="caller",
        key_id="caller-key",
        process_lineage_hash="0" * 64,
        evaluator_artifact_hash="0" * 64,
        evidence_lineage_hash="0" * 64,
        passed=True,
        reason="caller says so",
        issued_at="2026-08-15T22:00:00+02:00",
        signature="0" * 128,
    )

    assessment = ProtectedPatternReuseAssessor(PatternVerificationTrustStore()).assess(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh",),
            verification_receipt=forged,
        ),
    )

    assert assessment.verdict is PatternAssessmentVerdict.CANNOT_CHECK
    assert assessment.reasons == ("untrusted_pattern_verifier:caller:caller-key",)


def test_episode_content_substitution_invalidates_protected_receipt():
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
    replay = _episode(
        "replay", "vocabulary-a", EpisodeOutcome.SUCCESS, action_ids=(guard_action,)
    )
    fresh = _episode(
        "fresh",
        "unseen-domain",
        EpisodeOutcome.SUCCESS,
        action_ids=(guard_action,),
        task_id="task:fresh-domain",
        evaluation_epoch_id="evaluation:fresh",
        split_id="split:fresh",
    )
    receipt, authority = _protected_receipt(candidate, (first, second, replay, fresh))
    substituted_fresh = replace(
        fresh,
        evidence_bindings=((fresh.evidence_ids[0], "e" * 64),),
    )
    ledger = ExperienceLedger(
        episodes=(first, second, replay, substituted_fresh),
        failure_patterns=(candidate,),
    )

    assessment = authority.assess(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh",),
            verification_receipt=receipt,
        ),
    )

    assert assessment.verdict is PatternAssessmentVerdict.CANNOT_CHECK
    assert assessment.reasons == ("verification_episode_content_mismatch:fresh",)


def test_verifier_lineage_mismatch_invalidates_an_authentic_receipt():
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
    replay = _episode(
        "replay", "vocabulary-a", EpisodeOutcome.SUCCESS, action_ids=(guard_action,)
    )
    fresh = _episode(
        "fresh",
        "unseen-domain",
        EpisodeOutcome.SUCCESS,
        action_ids=(guard_action,),
        task_id="task:fresh-domain",
        evaluation_epoch_id="evaluation:fresh",
        split_id="split:fresh",
    )
    episodes = (first, second, replay, fresh)
    ledger = ExperienceLedger(episodes=episodes, failure_patterns=(candidate,))
    receipt, authority = _protected_receipt(candidate, episodes)
    registration = authority.trust_store.registrations[0]

    for field_name, reason in (
        ("process_lineage_hash", "verification_process_lineage_mismatch"),
        ("evaluator_artifact_hash", "verification_evaluator_lineage_mismatch"),
        ("evidence_lineage_hash", "verification_evidence_lineage_mismatch"),
    ):
        mismatched = ProtectedPatternReuseAssessor(
            PatternVerificationTrustStore(
                registrations=(replace(registration, **{field_name: "4" * 64}),)
            )
        )
        assessment = mismatched.assess(
            ledger,
            candidate,
            PatternValidationEvidence(
                replay_episode_ids=("replay",),
                fresh_transfer_episode_ids=("fresh",),
                verification_receipt=receipt,
            ),
        )

        assert assessment.verdict is PatternAssessmentVerdict.CANNOT_CHECK
        assert assessment.reasons == (reason,)


def test_same_run_aliases_cannot_form_a_failure_pattern():
    first = _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE, run_id="run:same")
    second = _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE, run_id="run:same")

    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:same-run-alias",
        candidate_guard="do something",
        falsifier="fresh failure",
    )

    assert candidate is None


def test_cannot_check_residuals_form_candidate_failure_knowledge():
    first = _episode(
        "e1",
        "verifier-a",
        EpisodeOutcome.CANNOT_CHECK,
        failure=(),
    )
    second = _episode(
        "e2",
        "verifier-b",
        EpisodeOutcome.CANNOT_CHECK,
        failure=(),
    )
    first = replace(first, residual_ids=("missing-verifier",))
    second = replace(second, residual_ids=("missing-verifier",))

    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:missing-verifier",
        candidate_guard="route to a protected verifier",
        falsifier="verification is available",
    )

    assert candidate is not None
    assert candidate.core_failure_signature == ("residual:missing-verifier",)
    assert related_failure_episodes(first, (first, second)) == (second,)


def test_atomic_failures_from_one_parent_run_are_not_independent_recurrence():
    first = replace(
        _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE, run_id="run:atom-1"),
        parent_run_id="run:root",
    )
    second = replace(
        _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE, run_id="run:atom-2"),
        parent_run_id="run:root",
    )

    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:same-parent-run",
        candidate_guard="do something",
        falsifier="fresh failure",
    )

    assert candidate is None


def test_manually_registered_same_parent_support_cannot_bypass_assessment_or_minting():
    first = replace(
        _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE),
        parent_run_id="run:shared-root",
    )
    second = replace(
        _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE),
        parent_run_id="run:shared-root",
    )
    candidate = FailurePatternCandidate(
        pattern_id="pattern:manual-bypass",
        mechanic_id="SEARCH.v1",
        core_failure_signature=("missed_parent_domain",),
        variation_signatures=(first.variation_signature, second.variation_signature),
        supporting_episode_ids=(first.episode_id, second.episode_id),
        candidate_guard="challenge the parent-domain basis",
        falsifier="guard has no transfer benefit",
    )
    ledger = ExperienceLedger(episodes=(first, second), failure_patterns=(candidate,))

    assessment = assess_pattern_reuse(ledger, candidate, PatternValidationEvidence())

    assert assessment.verdict is PatternAssessmentVerdict.CANNOT_CHECK
    assert "support_runs_not_independent" in assessment.reasons
    signing = PatternVerifierSigningIdentity(
        "protected:test",
        "key:v1",
        b"s" * 32,
        "1" * 64,
        "2" * 64,
        "3" * 64,
    )
    with pytest.raises(ValueError, match="support_runs_not_independent"):
        mint_pattern_verification_receipt(
            signing,
            candidate,
            (first, second),
            passed=True,
            reason="must not mint",
            issued_at="2026-08-15T22:00:00+02:00",
        )


def test_failure_pattern_candidate_cannot_self_assert_promoted_authority():
    with pytest.raises(ValueError, match="cannot self-assert"):
        FailurePatternCandidate(
            "pattern:self-promoted",
            "SEARCH.v1",
            ("failure",),
            (("a",), ("b",)),
            ("e1", "e2"),
            "guard",
            "falsifier",
            authority=LessonAuthority.CONDITIONALLY_REUSABLE,
        )


def test_protected_verifier_sharing_candidate_lineage_cannot_promote():
    first = _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE)
    second = _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE)
    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:shared-lineage",
        candidate_guard="challenge the parent-domain basis",
        falsifier="guard has no transfer benefit",
    )
    assert candidate is not None
    guard_action = f"guard:{candidate.pattern_id}"
    replay = _episode(
        "replay", "vocabulary-a", EpisodeOutcome.SUCCESS, action_ids=(guard_action,)
    )
    fresh = _episode(
        "fresh",
        "fresh-domain",
        EpisodeOutcome.SUCCESS,
        action_ids=(guard_action,),
        task_id="task:fresh",
        split_id="split:fresh",
        evaluation_epoch_id="evaluation:fresh",
    )
    episodes = tuple(
        replace(episode, producer_process_lineage_hash="1" * 64)
        for episode in (first, second, replay, fresh)
    )
    ledger = ExperienceLedger(episodes=episodes, failure_patterns=(candidate,))
    receipt, authority = _protected_receipt(candidate, episodes)

    assessment = authority.assess(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh",),
            verification_receipt=receipt,
        ),
    )

    assert assessment.verdict is PatternAssessmentVerdict.VERIFIED_LOCAL
    assert assessment.reasons == ("verification_process_not_independent",)


def test_protected_verifier_sharing_candidate_evidence_lineage_cannot_promote():
    first = _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE)
    second = _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE)
    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:shared-evidence-lineage",
        candidate_guard="challenge the evidence basis",
        falsifier="guard has no transfer benefit",
    )
    assert candidate is not None
    guard_action = f"guard:{candidate.pattern_id}"
    replay = _episode(
        "replay", "vocabulary-a", EpisodeOutcome.SUCCESS, action_ids=(guard_action,)
    )
    fresh = _episode(
        "fresh",
        "fresh-domain",
        EpisodeOutcome.SUCCESS,
        action_ids=(guard_action,),
        task_id="task:fresh",
        split_id="split:fresh",
        evaluation_epoch_id="evaluation:fresh",
    )
    episodes = (first, second, replay, fresh)
    receipt, authority = _protected_receipt(
        candidate,
        episodes,
        evidence_lineage_hash=evidence_binding_lineage_hash(episodes),
    )
    ledger = ExperienceLedger(episodes=episodes, failure_patterns=(candidate,))

    assessment = authority.assess(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh",),
            verification_receipt=receipt,
        ),
    )

    assert assessment.verdict is PatternAssessmentVerdict.VERIFIED_LOCAL
    assert assessment.reasons == ("verification_evidence_lineage_not_independent",)


def test_same_id_evidence_content_substitution_invalidates_receipt():
    original = EvidenceRecord("e:fixed", "original content", "known://source")
    substituted = EvidenceRecord("e:fixed", "substituted content", "known://source")
    first = _episode("e1", "vocabulary-a", EpisodeOutcome.FAILURE)
    second = _episode("e2", "vocabulary-b", EpisodeOutcome.FAILURE)
    candidate = propose_failure_pattern(
        (first, second),
        pattern_id="pattern:evidence-binding",
        candidate_guard="challenge the evidence artifact",
        falsifier="guard has no transfer benefit",
    )
    assert candidate is not None
    guard_action = f"guard:{candidate.pattern_id}"
    replay = _episode(
        "replay", "vocabulary-a", EpisodeOutcome.SUCCESS, action_ids=(guard_action,)
    )
    fresh = replace(
        _episode(
            "fresh",
            "fresh-domain",
            EpisodeOutcome.SUCCESS,
            action_ids=(guard_action,),
            task_id="task:fresh",
            split_id="split:fresh",
            evaluation_epoch_id="evaluation:fresh",
        ),
        evidence_ids=(original.evidence_id,),
        evidence_bindings=(
            (original.evidence_id, evidence_record_fingerprint(original)),
        ),
    )
    receipt, authority = _protected_receipt(candidate, (first, second, replay, fresh))
    replaced_fresh = replace(
        fresh,
        evidence_bindings=(
            (substituted.evidence_id, evidence_record_fingerprint(substituted)),
        ),
    )
    ledger = ExperienceLedger(
        episodes=(first, second, replay, replaced_fresh),
        failure_patterns=(candidate,),
    )

    assessment = authority.assess(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh",),
            verification_receipt=receipt,
        ),
    )

    assert assessment.verdict is PatternAssessmentVerdict.CANNOT_CHECK
    assert assessment.reasons == ("verification_episode_content_mismatch:fresh",)


def test_fresh_transfer_cannot_reuse_support_split_or_evaluation_epoch():
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
    replay = _episode(
        "replay", "vocabulary-a", EpisodeOutcome.SUCCESS, action_ids=(guard_action,)
    )

    for field_name, reason in (
        ("split_id", "fresh_transfer_split_not_distinct:fresh"),
        ("evaluation_epoch_id", "fresh_transfer_evaluation_not_distinct:fresh"),
    ):
        fresh = _episode(
            "fresh",
            "unseen-domain",
            EpisodeOutcome.SUCCESS,
            action_ids=(guard_action,),
            task_id="task:fresh-domain",
            evaluation_epoch_id="evaluation:fresh",
            split_id="split:fresh",
        )
        fresh = replace(fresh, **{field_name: getattr(first, field_name)})
        ledger = ExperienceLedger(
            episodes=(first, second, replay, fresh),
            failure_patterns=(candidate,),
        )
        assessment = assess_pattern_reuse(
            ledger,
            candidate,
            PatternValidationEvidence(
                replay_episode_ids=("replay",),
                fresh_transfer_episode_ids=("fresh",),
            ),
        )

        assert assessment.verdict is PatternAssessmentVerdict.CANNOT_CHECK
        assert reason in assessment.reasons


def test_multiple_fresh_transfers_must_be_mutually_independent():
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
    replay = _episode(
        "replay", "vocabulary-a", EpisodeOutcome.SUCCESS, action_ids=(guard_action,)
    )
    fresh_a = _episode(
        "fresh-a",
        "unseen-domain-a",
        EpisodeOutcome.SUCCESS,
        action_ids=(guard_action,),
        task_id="task:fresh-a",
        evaluation_epoch_id="evaluation:fresh-shared",
        split_id="split:fresh-shared",
    )
    fresh_b = _episode(
        "fresh-b",
        "unseen-domain-b",
        EpisodeOutcome.SUCCESS,
        action_ids=(guard_action,),
        task_id="task:fresh-b",
        evaluation_epoch_id="evaluation:fresh-shared",
        split_id="split:fresh-shared",
    )
    ledger = ExperienceLedger(
        episodes=(first, second, replay, fresh_a, fresh_b),
        failure_patterns=(candidate,),
    )

    assessment = assess_pattern_reuse(
        ledger,
        candidate,
        PatternValidationEvidence(
            replay_episode_ids=("replay",),
            fresh_transfer_episode_ids=("fresh-a", "fresh-b"),
        ),
    )

    assert assessment.verdict is PatternAssessmentVerdict.CANNOT_CHECK
    assert "fresh_transfer_split_not_distinct:fresh-b" in assessment.reasons
    assert "fresh_transfer_evaluation_not_distinct:fresh-b" in assessment.reasons
