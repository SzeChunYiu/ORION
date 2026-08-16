import hashlib

from orion.self_orion.readiness import (
    EvidenceStatus,
    ReadinessCriterion,
    ReadinessEvidenceRecord,
    SelfOrionReadinessStage,
    ShadowSelfDrivingArchitectureEvidence,
    assess_readiness,
    assess_readiness_stage,
    assess_shadow_self_driving_architecture,
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def _architecture(**overrides):
    values = dict(
        structural_open_questions=0,
        graph_defect_count=0,
        mechanical_work_item_count=1,
        component_artifact_ids=("component:driver", "component:research-loop", "component:change-control"),
        protected_boundary_artifact_ids=("boundary:sandbox", "boundary:evaluator"),
        failure_history_artifact_ids=("history:episodes",),
        self_merge_capability_present=False,
    )
    values.update(overrides)
    return ShadowSelfDrivingArchitectureEvidence(**values)


def _record(criterion: ReadinessCriterion, **overrides):
    values = dict(
        criterion=criterion,
        evidence_artifact_id=f"artifact:{criterion.value.lower()}",
        evidence_artifact_hash=_digest(f"artifact:{criterion.value}"),
        subject_revision_hash=_digest("subject:revision"),
        evaluator_artifact_hash=_digest("evaluator:frozen"),
        producer_process_lineage_hash=_digest(f"producer:{criterion.value}"),
        verifier_process_lineage_hash=_digest(f"verifier:{criterion.value}"),
        evaluation_epoch_id="epoch:frozen-v1",
        split_id=f"split:fresh:{criterion.value.lower()}",
        status=EvidenceStatus.PASS,
        frozen_before_candidate=True,
        fresh_split=True,
        reason="protected criterion evidence",
    )
    values.update(overrides)
    return ReadinessEvidenceRecord(**values)


def _complete_empirical():
    return tuple(_record(criterion) for criterion in ReadinessCriterion)


def test_complete_architecture_is_shadow_self_driving_even_without_empirical_evidence():
    architecture = _architecture()
    report = assess_shadow_self_driving_architecture(architecture)
    assert report.ready
    assert assess_readiness_stage(architecture, ()) is SelfOrionReadinessStage.SHADOW_SELF_DRIVING


def test_missing_architecture_boundary_or_self_merge_keeps_system_in_bootstrap():
    assert not assess_shadow_self_driving_architecture(
        _architecture(protected_boundary_artifact_ids=())
    ).ready
    assert assess_readiness_stage(
        _architecture(self_merge_capability_present=True), ()
    ) is SelfOrionReadinessStage.BOOTSTRAP


def test_complete_empirical_records_reach_only_pending_external_attestation():
    stage = assess_readiness_stage(_architecture(), _complete_empirical())
    assert stage is SelfOrionReadinessStage.READY_PENDING_EXTERNAL_ATTESTATION
    assert "GOVERNED_SELF_ORION" not in {item.value for item in SelfOrionReadinessStage}


def test_self_verified_or_posthoc_records_cannot_pass():
    record = _record(
        ReadinessCriterion.DETECTS_SELF_FAILURE,
        verifier_process_lineage_hash=_digest("producer:DETECTS_SELF_FAILURE"),
        frozen_before_candidate=False,
    )
    report = assess_readiness((record,))
    assert not report.passed
    assert any("self_verified" in blocker for blocker in report.blockers)
    assert any("posthoc_evaluator" in blocker for blocker in report.blockers)


def test_cannot_check_is_distinct_from_fail_and_blocks_readiness():
    records = list(_complete_empirical())
    target = ReadinessCriterion.CHALLENGER_PASSES_FRESH_ASSURANCE
    records = [
        _record(target, status=EvidenceStatus.CANNOT_CHECK)
        if item.criterion is target
        else item
        for item in records
    ]
    report = assess_readiness(tuple(records))
    assert not report.passed
    assert any("CANNOT_CHECK" in blocker for blocker in report.blockers)
    assert assess_readiness_stage(_architecture(), tuple(records)) is SelfOrionReadinessStage.SHADOW_SELF_DRIVING


def test_records_must_bind_one_subject_evaluator_and_epoch():
    records = list(_complete_empirical())
    target = ReadinessCriterion.LOCALIZES_RESPONSIBILITY
    records = [
        _record(
            target,
            subject_revision_hash=_digest("other-subject"),
            evaluator_artifact_hash=_digest("other-evaluator"),
            evaluation_epoch_id="epoch:other",
        )
        if item.criterion is target
        else item
        for item in records
    ]
    report = assess_readiness(tuple(records))
    assert not report.passed
    assert "readiness_records_bind_multiple_subject_revisions" in report.blockers
    assert "readiness_records_bind_multiple_evaluator_artifacts" in report.blockers
    assert "readiness_records_bind_multiple_evaluation_epochs" in report.blockers
