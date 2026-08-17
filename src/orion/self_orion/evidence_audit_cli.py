from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from orion.self_orion.evidence_admission import verify_phase2_evidence_receipt
from orion.self_orion.evidence_admission_io import load_phase2_evidence_receipt_v1


@dataclass(frozen=True)
class Phase2EvidenceAuditDocument:
    status: str
    receipt_hash: str | None
    document_hash: str | None
    subject_revision_hash: str
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    blockers: tuple[str, ...]
    observed_hashes: tuple[tuple[str, str], ...]

    @property
    def grants_phase2_closure(self) -> bool:
        return False

    @property
    def grants_governed_self_orion(self) -> bool:
        return False

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "Phase2EvidenceAudit.v1",
            "status": self.status,
            "receipt_hash": self.receipt_hash,
            "document_hash": self.document_hash,
            "subject_revision_hash": self.subject_revision_hash,
            "evaluator_artifact_hash": self.evaluator_artifact_hash,
            "evaluation_epoch_id": self.evaluation_epoch_id,
            "blockers": list(self.blockers),
            "observed_hashes": [
                {"artifact_id": artifact_id, "sha256": digest}
                for artifact_id, digest in self.observed_hashes
            ],
            "grants_phase2_closure": False,
            "grants_governed_self_orion": False,
        }


def audit_phase2_evidence_receipt_file(
    receipt_path: str | Path,
    artifact_root: str | Path,
    *,
    expected_subject_revision_hash: str,
    expected_evaluator_artifact_hash: str,
    expected_evaluation_epoch_id: str,
) -> Phase2EvidenceAuditDocument:
    try:
        loaded = load_phase2_evidence_receipt_v1(receipt_path)
    except ValueError as exc:
        return Phase2EvidenceAuditDocument(
            status="CANNOT_CHECK",
            receipt_hash=None,
            document_hash=None,
            subject_revision_hash=expected_subject_revision_hash,
            evaluator_artifact_hash=expected_evaluator_artifact_hash,
            evaluation_epoch_id=expected_evaluation_epoch_id,
            blockers=(f"receipt_invalid:{exc}",),
            observed_hashes=(),
        )

    report = verify_phase2_evidence_receipt(
        loaded.receipt,
        artifact_root,
        expected_subject_revision_hash=expected_subject_revision_hash,
        expected_evaluator_artifact_hash=expected_evaluator_artifact_hash,
        expected_evaluation_epoch_id=expected_evaluation_epoch_id,
    )
    return Phase2EvidenceAuditDocument(
        status="PASS" if report.admitted else "CANNOT_CHECK",
        receipt_hash=loaded.receipt_hash,
        document_hash=loaded.document_hash,
        subject_revision_hash=expected_subject_revision_hash,
        evaluator_artifact_hash=expected_evaluator_artifact_hash,
        evaluation_epoch_id=expected_evaluation_epoch_id,
        blockers=report.blockers,
        observed_hashes=report.observed_hashes,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Independently re-check Phase-2 evidence receipt bytes without granting phase authority"
    )
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--subject-revision-hash", required=True)
    parser.add_argument("--evaluator-artifact-hash", required=True)
    parser.add_argument("--evaluation-epoch-id", required=True)
    args = parser.parse_args(argv)

    document = audit_phase2_evidence_receipt_file(
        args.receipt,
        args.artifact_root,
        expected_subject_revision_hash=args.subject_revision_hash,
        expected_evaluator_artifact_hash=args.evaluator_artifact_hash,
        expected_evaluation_epoch_id=args.evaluation_epoch_id,
    )
    print(json.dumps(document.to_dict(), sort_keys=True, separators=(",", ":")))
    return 0 if document.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "Phase2EvidenceAuditDocument",
    "audit_phase2_evidence_receipt_file",
    "main",
]
