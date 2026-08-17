from __future__ import annotations

import json

import pytest

from orion.self_orion.evidence_admission import (
    EvidenceArtifactBinding,
    Phase2EvidenceReceipt,
)
from orion.self_orion.evidence_admission_io import (
    PHASE2_EVIDENCE_RECEIPT_V1_SCHEMA,
    load_phase2_evidence_receipt_v1,
    phase2_evidence_receipt_v1_to_dict,
    write_phase2_evidence_receipt_v1,
)


SUBJECT = "1" * 64
EVALUATOR = "2" * 64
ARTIFACT = "3" * 64


def _receipt() -> Phase2EvidenceReceipt:
    return Phase2EvidenceReceipt(
        subject_revision_hash=SUBJECT,
        evaluator_artifact_hash=EVALUATOR,
        evaluation_epoch_id="epoch-io",
        artifacts=(
            EvidenceArtifactBinding(
                artifact_id="live-report",
                relative_path="results/live.json",
                sha256=ARTIFACT,
            ),
        ),
    )


def test_receipt_v1_round_trip_is_content_addressed(tmp_path) -> None:
    path = tmp_path / "receipt.json"
    write_phase2_evidence_receipt_v1(_receipt(), path)

    loaded = load_phase2_evidence_receipt_v1(path)
    document = json.loads(path.read_text())

    assert document["schema"] == PHASE2_EVIDENCE_RECEIPT_V1_SCHEMA
    assert loaded.receipt == _receipt()
    assert loaded.receipt_hash == document["receipt_hash"]
    assert loaded.document_hash == document["document_hash"]
    assert phase2_evidence_receipt_v1_to_dict(loaded.receipt) == document


def test_document_tampering_without_hash_update_is_rejected(tmp_path) -> None:
    path = tmp_path / "receipt.json"
    write_phase2_evidence_receipt_v1(_receipt(), path)
    document = json.loads(path.read_text())
    document["receipt"]["evaluation_epoch_id"] = "tampered"
    path.write_text(json.dumps(document))

    with pytest.raises(ValueError, match="document hash mismatch"):
        load_phase2_evidence_receipt_v1(path)


def test_stale_receipt_hash_is_rejected_even_if_document_hash_is_recomputed(tmp_path) -> None:
    from orion.self_orion import evidence_admission_io as io

    path = tmp_path / "receipt.json"
    document = phase2_evidence_receipt_v1_to_dict(_receipt())
    document["receipt"]["evaluation_epoch_id"] = "different"
    without_document_hash = {
        key: value for key, value in document.items() if key != "document_hash"
    }
    document["document_hash"] = io._canonical_hash(without_document_hash)
    path.write_text(json.dumps(document))

    with pytest.raises(ValueError, match="payload hash mismatch"):
        load_phase2_evidence_receipt_v1(path)


def test_unknown_document_or_artifact_fields_fail_closed(tmp_path) -> None:
    for location in ("document", "artifact"):
        path = tmp_path / f"{location}.json"
        document = phase2_evidence_receipt_v1_to_dict(_receipt())
        if location == "document":
            document["candidate_says_valid"] = True
        else:
            document["receipt"]["artifacts"][0]["candidate_says_valid"] = True
        path.write_text(json.dumps(document))

        with pytest.raises(ValueError, match="keys mismatch"):
            load_phase2_evidence_receipt_v1(path)


def test_wrong_schema_is_rejected(tmp_path) -> None:
    path = tmp_path / "receipt.json"
    document = phase2_evidence_receipt_v1_to_dict(_receipt())
    document["schema"] = "Phase2EvidenceReceipt.v999"
    path.write_text(json.dumps(document))

    with pytest.raises(ValueError, match="unsupported.*schema"):
        load_phase2_evidence_receipt_v1(path)


def test_malformed_artifact_digest_cannot_survive_deserialization(tmp_path) -> None:
    from orion.self_orion import evidence_admission_io as io

    path = tmp_path / "receipt.json"
    document = phase2_evidence_receipt_v1_to_dict(_receipt())
    document["receipt"]["artifacts"][0]["sha256"] = "not-a-digest"
    document["receipt_hash"] = io._canonical_hash(document["receipt"])
    without_document_hash = {
        key: value for key, value in document.items() if key != "document_hash"
    }
    document["document_hash"] = io._canonical_hash(without_document_hash)
    path.write_text(json.dumps(document))

    with pytest.raises(ValueError, match="SHA-256"):
        load_phase2_evidence_receipt_v1(path)
