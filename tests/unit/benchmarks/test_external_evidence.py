import hashlib

from orion.benchmarks.external_evidence import (
    ExternalCriterion,
    ExternalEvidenceManifest,
    ExternalEvidenceRecord,
    ExternalEvidenceStatus,
    assess_external_flagship,
    assess_external_paper,
    empty_external_manifest,
)
from orion.benchmarks.result import BenchmarkStatus


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def _record(criterion: ExternalCriterion, **overrides):
    paper_id = criterion.value[:2]
    values = dict(
        paper_id=paper_id,
        criterion=criterion,
        evidence_artifact_id=f"artifact:{criterion.value.lower()}",
        evidence_artifact_hash=_digest(f"artifact:{criterion.value}"),
        subject_revision_hash=_digest("subject:revision"),
        evaluator_artifact_hash=_digest("evaluator:external"),
        producer_process_lineage_hash=_digest(f"producer:{criterion.value}"),
        verifier_process_lineage_hash=_digest(f"verifier:{criterion.value}"),
        evaluation_epoch_id="epoch:external-v1",
        split_id=f"split:fresh:{criterion.value.lower()}",
        status=ExternalEvidenceStatus.PASS,
        frozen_before_candidate=True,
        fresh_split=True,
        note="independently verified external criterion",
    )
    values.update(overrides)
    return ExternalEvidenceRecord(**values)


def _manifest(records):
    return ExternalEvidenceManifest(
        manifest_id="external:fixture",
        subject_revision_hash=_digest("subject:revision"),
        evaluator_artifact_hash=_digest("evaluator:external"),
        evaluation_epoch_id="epoch:external-v1",
        records=tuple(records),
    )


def test_repository_only_manifest_keeps_all_five_papers_cannot_check():
    reports = assess_external_flagship(empty_external_manifest())
    assert {report.paper_id for report in reports} == {"P1", "P2", "P3", "P4", "P5"}
    assert all(report.status is BenchmarkStatus.CANNOT_CHECK for report in reports)


def test_complete_independent_p4_manifest_can_pass_the_gate_in_a_known_world():
    records = [_record(item) for item in ExternalCriterion if item.value.startswith("P4_")]
    report = assess_external_paper(_manifest(records), "P4")
    assert report.status is BenchmarkStatus.PASS


def test_self_verified_or_subject_mismatched_external_record_cannot_pass():
    records = [_record(item) for item in ExternalCriterion if item.value.startswith("P5_")]
    target = ExternalCriterion.P5_FRESH_TRANSFER
    records = [
        _record(
            target,
            verifier_process_lineage_hash=_digest(f"producer:{target.value}"),
            subject_revision_hash=_digest("other-subject"),
        )
        if item.criterion is target
        else item
        for item in records
    ]
    report = assess_external_paper(_manifest(records), "P5")
    assert report.status is BenchmarkStatus.CANNOT_CHECK
    assert any("self_verified_external_record" in blocker for blocker in report.blockers)
    assert any("subject_revision_mismatch" in blocker for blocker in report.blockers)


def test_verified_fail_is_fail_not_cannot_check():
    records = [_record(item) for item in ExternalCriterion if item.value.startswith("P2_")]
    target = ExternalCriterion.P2_SYSTEM_BEATS_BASELINE
    records = [
        _record(target, status=ExternalEvidenceStatus.FAIL)
        if item.criterion is target
        else item
        for item in records
    ]
    report = assess_external_paper(_manifest(records), "P2")
    assert report.status is BenchmarkStatus.FAIL
    assert report.blockers == (f"criterion_failed:{target.value}",)


def test_external_cannot_check_record_blocks_even_with_all_other_passes():
    records = [_record(item) for item in ExternalCriterion if item.value.startswith("P1_")]
    target = ExternalCriterion.P1_LABELS_HIDDEN
    records = [
        _record(target, status=ExternalEvidenceStatus.CANNOT_CHECK)
        if item.criterion is target
        else item
        for item in records
    ]
    report = assess_external_paper(_manifest(records), "P1")
    assert report.status is BenchmarkStatus.CANNOT_CHECK
    assert f"criterion_cannot_check:{target.value}" in report.blockers
