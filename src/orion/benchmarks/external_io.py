from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orion.benchmarks.external_evidence import (
    ExternalCriterion,
    ExternalEvidenceManifest,
    ExternalEvidenceRecord,
    ExternalEvidenceStatus,
)


MANIFEST_SCHEMA = "ExternalEvidenceManifest.v1"


def _require_mapping(value: object, *, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{where} must be a JSON object")
    return value


def _require_bool(value: object, *, field: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{field} must be a JSON boolean")
    return value


def load_external_manifest(path: Path | str) -> ExternalEvidenceManifest:
    """Load and validate one host-produced ExternalEvidenceManifest.v1 JSON file."""

    source = Path(path)
    raw = _require_mapping(json.loads(source.read_text(encoding="utf-8")), where="manifest")
    if raw.get("schema") != MANIFEST_SCHEMA:
        raise ValueError(f"manifest schema must be {MANIFEST_SCHEMA}")
    raw_records = raw.get("records", ())
    if not isinstance(raw_records, list):
        raise ValueError("manifest records must be a JSON array")

    records: list[ExternalEvidenceRecord] = []
    for index, raw_record in enumerate(raw_records):
        item = _require_mapping(raw_record, where=f"records[{index}]")
        records.append(
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
                frozen_before_candidate=_require_bool(
                    item["frozen_before_candidate"], field=f"records[{index}].frozen_before_candidate"
                ),
                fresh_split=_require_bool(item["fresh_split"], field=f"records[{index}].fresh_split"),
                note=item["note"],
            )
        )

    return ExternalEvidenceManifest(
        manifest_id=raw["manifest_id"],
        subject_revision_hash=raw["subject_revision_hash"],
        evaluator_artifact_hash=raw["evaluator_artifact_hash"],
        evaluation_epoch_id=raw["evaluation_epoch_id"],
        records=tuple(records),
    )


def external_manifest_to_dict(manifest: ExternalEvidenceManifest) -> dict[str, object]:
    return {
        "schema": MANIFEST_SCHEMA,
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
    Path(path).write_text(
        json.dumps(external_manifest_to_dict(manifest), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


__all__ = [
    "MANIFEST_SCHEMA",
    "external_manifest_to_dict",
    "load_external_manifest",
    "write_external_manifest",
]
