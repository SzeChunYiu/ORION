import hashlib
import json

import pytest

from orion.self_orion.phase2_paper_snapshot import (
    REQUIRED_PHASE2_PAPER_PROGRAMME_PREFIXES,
    PaperProgrammeEntry,
    Phase2PaperProgrammeSnapshot,
    load_paper_programme_snapshot,
    write_paper_programme_snapshot,
)
from orion.self_orion.phase2_terminal_io import (
    load_final_ci_evidence,
    load_frozen_failure_index,
    write_final_ci_evidence,
    write_frozen_failure_index,
)
from orion.self_orion.phase2_terminal_receipts import (
    CIEvidenceConclusion,
    FinalCIEvidence,
    FrozenFailureIndex,
    FrozenFailureRecord,
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def _paper_entries():
    return tuple(
        sorted(
            (
                PaperProgrammeEntry(prefix + "fixture.txt", _digest(prefix))
                for prefix in REQUIRED_PHASE2_PAPER_PROGRAMME_PREFIXES
            ),
            key=lambda item: item.path,
        )
    )


def test_frozen_failure_index_roundtrips_and_rejects_tamper(tmp_path):
    index = FrozenFailureIndex(
        index_id="phase2:important-failures",
        subject_revision_hash=_digest("subject"),
        evaluation_epoch_id="epoch:frozen",
        failures=(
            FrozenFailureRecord(
                failure_id="failure:1",
                failure_class="retrieved-but-unused",
                source_failure_artifact_hash=_digest("failure:1"),
            ),
        ),
    )
    path = tmp_path / "failures.json"
    write_frozen_failure_index(index, path)
    assert load_frozen_failure_index(path) == index

    raw = json.loads(path.read_text())
    raw["failures"][0]["failure_class"] = "post-hoc-relabel"
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="artifact hash mismatch"):
        load_frozen_failure_index(path)


def test_final_ci_evidence_roundtrips_with_independent_lineage(tmp_path):
    evidence = FinalCIEvidence(
        ci_run_id="31950000000",
        head_commit_oid="abc123",
        workflow_identity=".github/workflows/ci.yml",
        test_command="pytest -q",
        job_count=1,
        conclusion=CIEvidenceConclusion.SUCCESS,
        producer_process_lineage_hash=_digest("ci-producer"),
        verifier_process_lineage_hash=_digest("ci-verifier"),
    )
    path = tmp_path / "ci.json"
    write_final_ci_evidence(evidence, path)
    loaded = load_final_ci_evidence(path)
    assert loaded == evidence
    assert loaded.independently_verified


def test_paper_programme_snapshot_requires_every_frozen_prefix(tmp_path):
    entries = _paper_entries()
    snapshot = Phase2PaperProgrammeSnapshot(
        snapshot_id="phase2:paper-programme",
        integration_commit_oid="abc123",
        entries=entries,
    )
    path = tmp_path / "papers.json"
    write_paper_programme_snapshot(snapshot, path)
    assert load_paper_programme_snapshot(path) == snapshot

    with pytest.raises(ValueError, match="missing required prefix"):
        Phase2PaperProgrammeSnapshot(
            snapshot_id="phase2:incomplete",
            integration_commit_oid="abc123",
            entries=entries[:-1],
        )


def test_paper_programme_snapshot_rejects_posthoc_content_rewrite(tmp_path):
    snapshot = Phase2PaperProgrammeSnapshot(
        snapshot_id="phase2:paper-programme",
        integration_commit_oid="abc123",
        entries=_paper_entries(),
    )
    path = tmp_path / "papers.json"
    write_paper_programme_snapshot(snapshot, path)
    raw = json.loads(path.read_text())
    raw["entries"][0]["content_sha256"] = _digest("replacement")
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="artifact hash mismatch"):
        load_paper_programme_snapshot(path)
