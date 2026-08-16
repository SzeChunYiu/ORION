from __future__ import annotations

import json
from pathlib import Path

from orion.benchmarks.external_evidence import (
    ExternalCriterion,
    ExternalEvidenceManifest,
    ExternalEvidenceRecord,
    ExternalEvidenceStatus,
)


def load_external_manifest(path: Path | str) -> ExternalEvidenceManifest:
    """Load and validate one host-produced external-evidence manifest JSON file."""

    source = Path(path)
    raw = json.loads(source.read_text())
    records = tuple(
        ExternalEvidenceRecord(
            paper_id=item["paper_id"],
            criterion=ExternalCriterion(item["criterion"]),
            evidence_artifact_id=item["evidence_artifact_id"],
            evidence_artifact_hash=item["evidence_artifact_hash"],
            subject_revision_hash=item["subject_revision_hash"],
            evaluator_artifact_hash=item["evaluator_artifact_hash"],
            producer_process_lineage_hash=item["producer_process_lineage_hash"],
            verifier_process_lineage_hash=item["verifier_process_lineage_hash"],
            evaluation_epoch_id=item["evaluation_epoch_id"],
            split_id=item["split_id"],
            status=ExternalEvidenceStatus(item["status"]),
            frozen_before_candidate=bool(item["frozen_before_candidate"]),
            fresh_split=bool(item["fresh_split"]),
            note=item["note"],
        )
        for item in raw.get("records", ())
    )
    return ExternalEvidenceManifest(
        manifest_id=raw["manifest_id"],
        subject_revision_hash=raw["subject_revision_hash"],
        evaluator_artifact_hash=raw["evaluator_artifact_hash"],
        evaluation_epoch_id=raw["evaluation_epoch_id"],
        records=records,
    )


def external_manifest_to_dict(manifest: ExternalEvidenceManifest) -> dict[str, object]:
    return {
        "manifest_id": manifest.manifest_id,
        "subject_revision_hash": manifest.subject_revision_hash,
        "evaluator_artifact_hash": manifest.evaluator_artifact_hash,
        "evaluation_epoch_id": manifest.evaluation_epoch_id,
        "records": [
            {
                "paper_id": item.paper_id,
                "criterion": item.criterion.value,
                "evidence_artifact_id": item.evidence_artifact_id,
                "evidence_artifact_hash": item.evidence_artifact_hash,
                "subject_revision_hash": item.subject_revision_hash,
                "evaluator_artifact_hash": item.evaluator_artifact_hash,
                "producer_process_lineage_hash": item.producer_process_lineage_hash,
                "verifier_process_lineage_hash": item.verifier_process_lineage_hash,
                "evaluation_epoch_id": item.evaluation_epoch_id,
                "split_id": item.split_id,
                "status": item.status.value,
                "frozen_before_candidate": item.frozen_before_candidate,
                "fresh_split": item.fresh_split,
                "note": item.note,
            }
            for item in manifest.records
        ],
    }


def write_external_manifest(manifest: ExternalEvidenceManifest, path: Path | str) -> None:
    Path(path).write_text(json.dumps(external_manifest_to_dict(manifest), indent=2, sort_keys=True) + "\n")


__all__ = ["external_manifest_to_dict", "load_external_manifest", "write_external_manifest"]
