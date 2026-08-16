from orion.knowledge.subject_identity import (
    EvaluationTarget,
    ExecutionSubjectObservation,
    FrozenSubjectSpec,
    PlatformSubjectObservation,
    SubjectVerdict,
    verify_execution_subject,
)


SOURCE = "source-sha"
BASE = "base-sha"
MERGE = "merge-sha"
MERGE_TREE = "merge-tree"


def _spec(target: EvaluationTarget = EvaluationTarget.INTEGRATION_RESULT):
    return FrozenSubjectSpec(SOURCE, BASE, target)


def _platform(**overrides):
    values = dict(source_sha=SOURCE, base_sha=BASE, integration_sha=MERGE, integration_tree_sha=MERGE_TREE, externally_observed=True)
    values.update(overrides)
    return PlatformSubjectObservation(**values)


def _execution(**overrides):
    values = dict(executed_sha=MERGE, executed_tree_sha=MERGE_TREE, externally_observed=True)
    values.update(overrides)
    return ExecutionSubjectObservation(**values)


def test_integration_exact_revision_and_tree_is_valid():
    report = verify_execution_subject(_spec(), _platform(), _execution())
    assert report.verdict is SubjectVerdict.VALID_REVISION_AND_TREE
    assert report.valid and report.revision_identified and report.tree_identified


def test_source_head_cannot_masquerade_as_integration_result():
    report = verify_execution_subject(_spec(), _platform(), _execution(executed_sha=SOURCE, executed_tree_sha="source-tree"))
    assert report.verdict is SubjectVerdict.INVALID
    assert not report.valid


def test_explicit_head_only_evaluation_is_revision_scoped():
    report = verify_execution_subject(
        _spec(EvaluationTarget.SOURCE_HEAD),
        _platform(integration_sha=None, integration_tree_sha=None),
        _execution(executed_sha=SOURCE, executed_tree_sha=None),
    )
    assert report.verdict is SubjectVerdict.VALID_REVISION
    assert report.revision_identified and not report.tree_identified


def test_matching_tree_without_revision_is_partial_not_revision_identity():
    report = verify_execution_subject(_spec(), _platform(), _execution(executed_sha=None, executed_tree_sha=MERGE_TREE))
    assert report.verdict is SubjectVerdict.PARTIALLY_IDENTIFIED_TREE_ONLY
    assert not report.valid and not report.revision_identified and report.tree_identified


def test_tree_mismatch_invalid_even_when_revision_label_matches():
    report = verify_execution_subject(_spec(), _platform(), _execution(executed_sha=MERGE, executed_tree_sha="different-tree"))
    assert report.verdict is SubjectVerdict.INVALID
    assert report.revision_identified and not report.tree_identified


def test_candidate_self_report_cannot_become_execution_authority():
    report = verify_execution_subject(_spec(), _platform(), _execution(externally_observed=False))
    assert report.verdict is SubjectVerdict.CANNOT_CHECK
    assert not report.valid


def test_missing_integration_identity_is_cannot_check():
    report = verify_execution_subject(_spec(), _platform(integration_sha=None, integration_tree_sha=None), _execution())
    assert report.verdict is SubjectVerdict.CANNOT_CHECK


def test_same_tree_different_revision_never_upgrades_revision_identity():
    report = verify_execution_subject(_spec(), _platform(), _execution(executed_sha="different-history", executed_tree_sha=MERGE_TREE))
    assert report.verdict is SubjectVerdict.PARTIALLY_IDENTIFIED_TREE_ONLY
    assert not report.revision_identified and report.tree_identified
