import hashlib
import json

from orion.benchmarks.cli import main
from orion.benchmarks.external_evidence import (
    ExternalCriterion,
    ExternalEvidenceManifest,
    ExternalEvidenceRecord,
    ExternalEvidenceStatus,
)
from orion.benchmarks.external_io import load_external_manifest, write_external_manifest


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def test_repository_only_cli_reports_all_external_papers_cannot_check(capsys):
    assert main(["external-status"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["local_all_pass"]
    assert not payload["publication_ready"]
    assert {item["paper_id"] for item in payload["external"]} == {"P1", "P2", "P3", "P4", "P5"}
    assert {item["status"] for item in payload["external"]} == {"CANNOT_CHECK"}


def test_manifest_json_roundtrip_and_cli_passes_complete_p4_known_world(tmp_path, capsys):
    subject = _digest("subject")
    evaluator = _digest("evaluator")
    epoch = "epoch:external"
    records = tuple(
        ExternalEvidenceRecord(
            paper_id="P4",
            criterion=criterion,
            evidence_artifact_id=f"artifact:{criterion.value}",
            evidence_artifact_hash=_digest(f"artifact:{criterion.value}"),
            subject_revision_hash=subject,
            evaluator_artifact_hash=evaluator,
            producer_process_lineage_hash=_digest(f"producer:{criterion.value}"),
            verifier_process_lineage_hash=_digest(f"verifier:{criterion.value}"),
            evaluation_epoch_id=epoch,
            split_id=f"split:fresh:{criterion.value}",
            status=ExternalEvidenceStatus.PASS,
            frozen_before_candidate=True,
            fresh_split=True,
            note="fixture external evidence",
        )
        for criterion in ExternalCriterion
        if criterion.value.startswith("P4_")
    )
    manifest = ExternalEvidenceManifest(
        manifest_id="manifest:p4",
        subject_revision_hash=subject,
        evaluator_artifact_hash=evaluator,
        evaluation_epoch_id=epoch,
        records=records,
    )
    path = tmp_path / "manifest.json"
    write_external_manifest(manifest, path)
    loaded = load_external_manifest(path)
    assert loaded == manifest

    assert main(["external-status", "--manifest", str(path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    p4 = next(item for item in payload["external"] if item["paper_id"] == "P4")
    assert p4["status"] == "PASS"
    assert not payload["publication_ready"]  # P1/P2/P3/P5 are still absent.
