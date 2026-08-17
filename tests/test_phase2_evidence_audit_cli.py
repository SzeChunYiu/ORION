from __future__ import annotations

import hashlib
import json

from orion.self_orion.evidence_admission import EvidenceArtifactBinding, Phase2EvidenceReceipt
from orion.self_orion.evidence_admission_io import write_phase2_evidence_receipt_v1
from orion.self_orion.evidence_audit_cli import audit_phase2_evidence_receipt_file, main


SUBJECT = "1" * 64
EVALUATOR = "2" * 64
EPOCH = "epoch-audit"


def _write_fixture(tmp_path):
    root = tmp_path / "artifacts"
    result = root / "results" / "live.json"
    result.parent.mkdir(parents=True)
    payload = b'{"result":"bound"}\n'
    result.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    receipt = Phase2EvidenceReceipt(
        subject_revision_hash=SUBJECT,
        evaluator_artifact_hash=EVALUATOR,
        evaluation_epoch_id=EPOCH,
        artifacts=(
            EvidenceArtifactBinding(
                artifact_id="live-report",
                relative_path="results/live.json",
                sha256=digest,
            ),
        ),
    )
    receipt_path = tmp_path / "receipt.json"
    write_phase2_evidence_receipt_v1(receipt, receipt_path)
    return root, result, receipt_path, digest


def test_independent_audit_passes_only_with_exact_host_visible_bytes(tmp_path) -> None:
    root, _, receipt_path, digest = _write_fixture(tmp_path)

    report = audit_phase2_evidence_receipt_file(
        receipt_path,
        root,
        expected_subject_revision_hash=SUBJECT,
        expected_evaluator_artifact_hash=EVALUATOR,
        expected_evaluation_epoch_id=EPOCH,
    )

    assert report.status == "PASS"
    assert report.blockers == ()
    assert report.observed_hashes == (("live-report", digest),)
    assert report.receipt_hash is not None
    assert report.document_hash is not None
    assert report.grants_phase2_closure is False
    assert report.grants_governed_self_orion is False


def test_missing_or_tampered_bytes_are_cannot_check(tmp_path) -> None:
    for mutation in ("missing", "tampered"):
        root, result, receipt_path, _ = _write_fixture(tmp_path / mutation)
        if mutation == "missing":
            result.unlink()
        else:
            result.write_bytes(b"tampered")

        report = audit_phase2_evidence_receipt_file(
            receipt_path,
            root,
            expected_subject_revision_hash=SUBJECT,
            expected_evaluator_artifact_hash=EVALUATOR,
            expected_evaluation_epoch_id=EPOCH,
        )

        assert report.status == "CANNOT_CHECK"
        assert any(
            blocker.startswith("artifact_missing:")
            or blocker.startswith("artifact_hash_mismatch:")
            for blocker in report.blockers
        )
        assert report.grants_phase2_closure is False


def test_host_selected_subject_evaluator_and_epoch_dominate_receipt(tmp_path) -> None:
    root, _, receipt_path, _ = _write_fixture(tmp_path)

    substitutions = (
        {"expected_subject_revision_hash": "9" * 64},
        {"expected_evaluator_artifact_hash": "8" * 64},
        {"expected_evaluation_epoch_id": "other-epoch"},
    )
    defaults = {
        "expected_subject_revision_hash": SUBJECT,
        "expected_evaluator_artifact_hash": EVALUATOR,
        "expected_evaluation_epoch_id": EPOCH,
    }
    for substitution in substitutions:
        report = audit_phase2_evidence_receipt_file(
            receipt_path,
            root,
            **(defaults | substitution),
        )
        assert report.status == "CANNOT_CHECK"
        assert report.blockers


def test_invalid_receipt_is_cannot_check_not_a_crash(tmp_path) -> None:
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text('{"candidate_says_valid":true}')

    report = audit_phase2_evidence_receipt_file(
        receipt_path,
        tmp_path,
        expected_subject_revision_hash=SUBJECT,
        expected_evaluator_artifact_hash=EVALUATOR,
        expected_evaluation_epoch_id=EPOCH,
    )

    assert report.status == "CANNOT_CHECK"
    assert len(report.blockers) == 1
    assert report.blockers[0].startswith("receipt_invalid:")
    assert report.receipt_hash is None


def test_cli_emits_machine_readable_non_authorizing_result(tmp_path, capsys) -> None:
    root, _, receipt_path, _ = _write_fixture(tmp_path)

    exit_code = main(
        [
            "--receipt",
            str(receipt_path),
            "--artifact-root",
            str(root),
            "--subject-revision-hash",
            SUBJECT,
            "--evaluator-artifact-hash",
            EVALUATOR,
            "--evaluation-epoch-id",
            EPOCH,
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["schema"] == "Phase2EvidenceAudit.v1"
    assert payload["status"] == "PASS"
    assert payload["grants_phase2_closure"] is False
    assert payload["grants_governed_self_orion"] is False
