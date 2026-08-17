from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from orion.self_orion.evidence_admission import (
    EvidenceArtifactBinding,
    Phase2EvidenceReceipt,
)


PHASE2_EVIDENCE_RECEIPT_V1_SCHEMA = "Phase2EvidenceReceipt.v1"


def _canonical_hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _object(value: object, name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _exact_keys(value: dict[str, object], expected: set[str], name: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"{name} keys mismatch: missing={missing} extra={extra}")


def phase2_evidence_receipt_payload(receipt: Phase2EvidenceReceipt) -> dict[str, object]:
    return {
        "subject_revision_hash": receipt.subject_revision_hash,
        "evaluator_artifact_hash": receipt.evaluator_artifact_hash,
        "evaluation_epoch_id": receipt.evaluation_epoch_id,
        "artifacts": [
            {
                "artifact_id": item.artifact_id,
                "relative_path": item.relative_path,
                "sha256": item.sha256,
            }
            for item in receipt.artifacts
        ],
    }


def phase2_evidence_receipt_v1_to_dict(
    receipt: Phase2EvidenceReceipt,
) -> dict[str, object]:
    payload = phase2_evidence_receipt_payload(receipt)
    document: dict[str, object] = {
        "schema": PHASE2_EVIDENCE_RECEIPT_V1_SCHEMA,
        "receipt_hash": _canonical_hash(payload),
        "receipt": payload,
    }
    document["document_hash"] = _canonical_hash(document)
    return document


def write_phase2_evidence_receipt_v1(
    receipt: Phase2EvidenceReceipt,
    path: str | Path,
) -> None:
    Path(path).write_text(
        json.dumps(phase2_evidence_receipt_v1_to_dict(receipt), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


@dataclass(frozen=True)
class LoadedPhase2EvidenceReceiptV1:
    receipt: Phase2EvidenceReceipt
    receipt_hash: str
    document_hash: str


def load_phase2_evidence_receipt_v1(
    path: str | Path,
) -> LoadedPhase2EvidenceReceiptV1:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"unable to load Phase-2 evidence receipt: {exc}") from exc

    document = _object(raw, "Phase-2 evidence receipt document")
    _exact_keys(
        document,
        {"schema", "receipt", "receipt_hash", "document_hash"},
        "Phase-2 evidence receipt document",
    )
    if document.get("schema") != PHASE2_EVIDENCE_RECEIPT_V1_SCHEMA:
        raise ValueError("unsupported Phase-2 evidence receipt schema")

    claimed_document_hash = _string(document.get("document_hash"), "document_hash")
    without_document_hash = {
        key: value for key, value in document.items() if key != "document_hash"
    }
    if _canonical_hash(without_document_hash) != claimed_document_hash:
        raise ValueError("Phase-2 evidence receipt document hash mismatch")

    receipt_payload = _object(document.get("receipt"), "receipt")
    _exact_keys(
        receipt_payload,
        {
            "subject_revision_hash",
            "evaluator_artifact_hash",
            "evaluation_epoch_id",
            "artifacts",
        },
        "receipt",
    )
    claimed_receipt_hash = _string(document.get("receipt_hash"), "receipt_hash")
    if _canonical_hash(receipt_payload) != claimed_receipt_hash:
        raise ValueError("Phase-2 evidence receipt payload hash mismatch")

    artifacts_raw = receipt_payload.get("artifacts")
    if not isinstance(artifacts_raw, list):
        raise ValueError("receipt.artifacts must be an array")

    artifacts: list[EvidenceArtifactBinding] = []
    for index, raw_artifact in enumerate(artifacts_raw):
        artifact = _object(raw_artifact, f"receipt.artifacts[{index}]")
        _exact_keys(
            artifact,
            {"artifact_id", "relative_path", "sha256"},
            f"receipt.artifacts[{index}]",
        )
        artifacts.append(
            EvidenceArtifactBinding(
                artifact_id=_string(
                    artifact.get("artifact_id"), f"receipt.artifacts[{index}].artifact_id"
                ),
                relative_path=_string(
                    artifact.get("relative_path"),
                    f"receipt.artifacts[{index}].relative_path",
                ),
                sha256=_string(
                    artifact.get("sha256"), f"receipt.artifacts[{index}].sha256"
                ),
            )
        )

    receipt = Phase2EvidenceReceipt(
        subject_revision_hash=_string(
            receipt_payload.get("subject_revision_hash"), "receipt.subject_revision_hash"
        ),
        evaluator_artifact_hash=_string(
            receipt_payload.get("evaluator_artifact_hash"),
            "receipt.evaluator_artifact_hash",
        ),
        evaluation_epoch_id=_string(
            receipt_payload.get("evaluation_epoch_id"), "receipt.evaluation_epoch_id"
        ),
        artifacts=tuple(artifacts),
    )

    rebuilt = phase2_evidence_receipt_v1_to_dict(receipt)
    if rebuilt["receipt_hash"] != claimed_receipt_hash:
        raise ValueError("Phase-2 evidence receipt semantic hash mismatch")
    if rebuilt["document_hash"] != claimed_document_hash:
        raise ValueError("Phase-2 evidence receipt semantic document mismatch")

    return LoadedPhase2EvidenceReceiptV1(
        receipt=receipt,
        receipt_hash=claimed_receipt_hash,
        document_hash=claimed_document_hash,
    )


__all__ = [
    "LoadedPhase2EvidenceReceiptV1",
    "PHASE2_EVIDENCE_RECEIPT_V1_SCHEMA",
    "load_phase2_evidence_receipt_v1",
    "phase2_evidence_receipt_payload",
    "phase2_evidence_receipt_v1_to_dict",
    "write_phase2_evidence_receipt_v1",
]
