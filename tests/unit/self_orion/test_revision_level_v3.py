from orion.self_orion.revision_level_v3 import (
    RevisionClass,
    always_unresolved_policy,
    direct_update_policy,
    m_open_only_policy,
    responsibility_gated_policy,
    reveal_diagnostics,
    score_policy,
    stage0_cases,
)


def test_public_view_never_contains_protected_gold() -> None:
    for case in stage0_cases():
        public = case.public_view()
        assert "gold_class" not in public
        assert "minimal_licensed_response" not in public
        assert "forbidden_revision_classes" not in public
        assert case.gold_class.value not in repr(public) or case.gold_class in case.candidate_revision_options


def test_responsibility_gated_policy_solves_white_box_stage0() -> None:
    score = score_policy(stage0_cases(), responsibility_gated_policy)
    assert score.n == 12
    assert score.correct == 12
    assert score.false_broad_revision == 0
    assert score.forbidden_revision == 0
    assert score.unresolved_correct == 1


def test_m_open_only_has_false_broad_revisions() -> None:
    score = score_policy(stage0_cases(), m_open_only_policy)
    assert score.correct < score.n
    assert score.false_broad_revision > 0


def test_simple_direct_update_is_a_real_hard_baseline() -> None:
    score = score_policy(stage0_cases(), direct_update_policy)
    assert 0 < score.correct < score.n
    assert score.false_broad_revision == 0


def test_always_unresolved_is_broken_shut_except_true_unknown() -> None:
    score = score_policy(stage0_cases(), always_unresolved_policy)
    assert score.correct == 1
    assert score.unresolved_correct == 1


def test_feedback_permutation_changes_responsibility_gated_behavior() -> None:
    cases = stage0_cases()
    original = [
        responsibility_gated_policy(case, reveal_diagnostics(case)).revision_class
        for case in cases
    ]
    permutation = {
        RevisionClass.EVIDENCE: RevisionClass.PARAMETER,
        RevisionClass.PARAMETER: RevisionClass.EVIDENCE,
        RevisionClass.NO_SELF_REVISION: RevisionClass.UNRESOLVED,
        RevisionClass.UNRESOLVED: RevisionClass.NO_SELF_REVISION,
    }
    permuted = [
        responsibility_gated_policy(
            case,
            reveal_diagnostics(case, permutation=permutation),
        ).revision_class
        for case in cases
    ]
    assert original != permuted


def test_permutation_degrades_accuracy_instead_of_fake_adaptivity() -> None:
    permutation = {
        RevisionClass.EVIDENCE: RevisionClass.PARAMETER,
        RevisionClass.PARAMETER: RevisionClass.EVIDENCE,
        RevisionClass.NO_SELF_REVISION: RevisionClass.UNRESOLVED,
        RevisionClass.UNRESOLVED: RevisionClass.NO_SELF_REVISION,
    }
    original = score_policy(stage0_cases(), responsibility_gated_policy)
    permuted = score_policy(stage0_cases(), responsibility_gated_policy, permutation=permutation)
    assert original.accuracy == 1.0
    assert permuted.accuracy < original.accuracy
