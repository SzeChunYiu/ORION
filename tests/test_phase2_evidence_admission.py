from __future__ import annotations

import hashlib

from orion.self_orion.evidence_admission import (
    EvidenceArtifactBinding,
    Phase2EvidenceReceipt,
    verify_phase2_evidence_receipt,
    verify_phase2_observation_bundle_artifacts,
)
from orion.self_orion.phase2_campaign import (
    Phase2CampaignCriterion,
    Phase2ExternalObservation,
    Phase2ExternalObservationBundle,
    Phase2ExternalObservationStatus,
)


SUBJECT = "1" * 64
EVALUATOR = "2" * 64
PRODUCER = "3" * 64
VERIFIER = "4" * 64
EPOCH = "epoch-1"


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _receipt(artifact_hash: str, *, path: str = "results/live.json") -> Phase2EvidenceReceipt:
    return Phase2EvidenceReceipt(
        subject_revision_hash=SUBJECT,
        evaluator_artifact_hash=EVALUATOR,
        evaluation_epoch_id=EPOCH,
        artifacts=(
            EvidenceArtifactBinding(
                artifact_id="live-report",
                relative_path=path,
                sha256=artifact_hash,
            ),
        ),
    )


def _observation(artifact_hash: str, **overrides: object) -> Phase2ExternalObservation:
    values: dict[str, object] = {
        "criterion": Phase2CampaignCriterion.LIVE_TRIAL,
        "evidence_artifact_id": "live-report",
        "evidence_artifact_hash": artifact_hash,
        "subject_revision_hash": SUBJECT,
        "evaluator_artifact_hash": EVALUATOR,
        "producer_process_lineage_hash": PRODUCER,
        "verifier_process_lineage_hash": VERIFIER,
        "evaluation_epoch_id": EPOCH,
        "split_id": "fresh",
        "status": Phase2ExternalObservationStatus.COMPLETE,
        "frozen_before_candidate": True,
        "fresh_split": True,
        "note": "host verified",
    }
    values.update(overrides)
    return Phase2ExternalObservation(**values)  # type: ignore[arg-type]


def _bundle(observation: Phase2ExternalObservation) -> Phase2ExternalObservationBundle:
    return Phase2ExternalObservationBundle(
        bundle_id="phase2-external",
        subject_revision_hash=SUBJECT,
        evaluator_artifact_hash=EVALUATOR,
        evaluation_epoch_id=EPOCH,
        observations=(observation,),
    )


def test_clean_host_visible_bytes_are_admitted(tmp_path) -> None:
    result = tmp_path / "results" / "live.json"
    result.parent.mkdir()
    result.write_bytes(b'{"status":"COMPLETE"}\n')
    expected = _digest(result.read_bytes())

    report = verify_phase2_evidence_receipt(
        _receipt(expected),
        tmp_path,
        expected_subject_revision_hash=SUBJECT,
        expected_evaluator_artifact_hash=EVALUATOR,
        expected_evaluation_epoch_id=EPOCH,
    )

    assert report.admitted
    assert report.blockers == ()
    assert report.observed_hashes == (("live-report", expected),)


def test_missing_artifact_is_not_admitted_even_if_summary_claims_it_exists(tmp_path) -> None:
    # Regression for #159/#207: prose or a summary is not artifact custody.
    report = verify_phase2_evidence_receipt(_receipt("a" * 64), tmp_path)

    assert not report.admitted
    assert "artifact_missing:live-report" in report.blockers


def test_tampered_artifact_bytes_fail_closed(tmp_path) -> None:
    result = tmp_path / "results" / "live.json"
    result.parent.mkdir()
    result.write_bytes(b"changed after freeze")

    report = verify_phase2_evidence_receipt(_receipt("a" * 64), tmp_path)

    assert not report.admitted
    assert "artifact_hash_mismatch:live-report" in report.blockers


def test_absolute_and_parent_escape_paths_are_rejected(tmp_path) -> None:
    for path in ("../outside.json", "/tmp/outside.json"):
        report = verify_phase2_evidence_receipt(_receipt("a" * 64, path=path), tmp_path)
        assert not report.admitted
        assert "artifact_path_escape:live-report" in report.blockers


def test_duplicate_artifact_identity_and_path_are_rejected(tmp_path) -> None:
    result = tmp_path / "same.json"
    result.write_bytes(b"same")
    digest = _digest(result.read_bytes())
    binding = EvidenceArtifactBinding("same", "same.json", digest)
    receipt = Phase2EvidenceReceipt(
        subject_revision_hash=SUBJECT,
        evaluator_artifact_hash=EVALUATOR,
        evaluation_epoch_id=EPOCH,
        artifacts=(binding, binding),
    )

    report = verify_phase2_evidence_receipt(receipt, tmp_path)

    assert not report.admitted
    assert "duplicate_artifact_id:same" in report.blockers
    assert "duplicate_artifact_path:same.json" in report.blockers


def test_host_selected_subject_evaluator_and_epoch_dominate_receipt(tmp_path) -> None:
    result = tmp_path / "results" / "live.json"
    result.parent.mkdir()
    result.write_bytes(b"bound")
    receipt = _receipt(_digest(result.read_bytes()))

    report = verify_phase2_evidence_receipt(
        receipt,
        tmp_path,
        expected_subject_revision_hash="9" * 64,
        expected_evaluator_artifact_hash="8" * 64,
        expected_evaluation_epoch_id="later-epoch",
    )

    assert not report.admitted
    assert "subject_revision_mismatch" in report.blockers
    assert "evaluator_artifact_mismatch" in report.blockers
    assert "evaluation_epoch_mismatch" in report.blockers


def test_observation_must_bind_the_same_verified_artifact_bytes(tmp_path) -> None:
    result = tmp_path / "results" / "live.json"
    result.parent.mkdir()
    result.write_bytes(b"real bytes")
    actual = _digest(result.read_bytes())
    bundle = _bundle(_observation("f" * 64))

    report = verify_phase2_observation_bundle_artifacts(
        bundle, _receipt(actual), tmp_path
    )

    assert not report.admitted
    assert "observation_artifact_hash_mismatch:live-report" in report.blockers


def test_observation_artifact_must_be_present_in_receipt(tmp_path) -> None:
    result = tmp_path / "other.json"
    result.write_bytes(b"other")
    digest = _digest(result.read_bytes())
    receipt = Phase2EvidenceReceipt(
        subject_revision_hash=SUBJECT,
        evaluator_artifact_hash=EVALUATOR,
        evaluation_epoch_id=EPOCH,
        artifacts=(EvidenceArtifactBinding("other", "other.json", digest),),
    )
    bundle = _bundle(_observation("a" * 64))

    report = verify_phase2_observation_bundle_artifacts(bundle, receipt, tmp_path)

    assert not report.admitted
    assert "observation_artifact_unbound:live-report" in report.blockers


def test_observation_cannot_switch_subject_evaluator_or_epoch(tmp_path) -> None:
    result = tmp_path / "results" / "live.json"
    result.parent.mkdir()
    result.write_bytes(b"real bytes")
    digest = _digest(result.read_bytes())
    observation = _observation(
        digest,
        subject_revision_hash="7" * 64,
        evaluator_artifact_hash="6" * 64,
        evaluation_epoch_id="wrong-epoch",
    )
    bundle = _bundle(observation)

    report = verify_phase2_observation_bundle_artifacts(
        bundle, _receipt(digest), tmp_path
    )

    assert not report.admitted
    assert "observation_subject_mismatch:LIVE_TRIAL" in report.blockers
    assert "observation_evaluator_mismatch:LIVE_TRIAL" in report.blockers
    assert "observation_epoch_mismatch:LIVE_TRIAL" in report.blockers
