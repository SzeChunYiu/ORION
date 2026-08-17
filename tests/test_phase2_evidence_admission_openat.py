from __future__ import annotations

import hashlib
import os

import pytest

import orion.self_orion.evidence_admission as admission
from orion.self_orion.evidence_admission import (
    EvidenceArtifactBinding,
    Phase2EvidenceReceipt,
    verify_phase2_evidence_receipt,
)


SUBJECT = "1" * 64
EVALUATOR = "2" * 64


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _receipt(path: str, digest: str) -> Phase2EvidenceReceipt:
    return Phase2EvidenceReceipt(
        subject_revision_hash=SUBJECT,
        evaluator_artifact_hash=EVALUATOR,
        evaluation_epoch_id="epoch-openat",
        artifacts=(EvidenceArtifactBinding("artifact", path, digest),),
    )


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlinks unavailable")
def test_final_symlink_is_never_followed(tmp_path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside-final"
    outside.write_bytes(b"secret outside root")
    (tmp_path / "linked.json").symlink_to(outside)

    report = verify_phase2_evidence_receipt(
        _receipt("linked.json", _digest(outside.read_bytes())), tmp_path
    )

    assert not report.admitted
    assert "artifact_path_unsafe:artifact" in report.blockers
    assert report.observed_hashes == ()


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlinks unavailable")
def test_parent_directory_symlink_is_never_followed(tmp_path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside-parent"
    outside.mkdir()
    (outside / "result.json").write_bytes(b"outside result")
    (tmp_path / "results").symlink_to(outside, target_is_directory=True)

    report = verify_phase2_evidence_receipt(
        _receipt("results/result.json", _digest(b"outside result")), tmp_path
    )

    assert not report.admitted
    assert "artifact_path_unsafe:artifact" in report.blockers
    assert report.observed_hashes == ()


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlinks unavailable")
def test_artifact_root_itself_may_not_be_a_symlink(tmp_path) -> None:
    real_root = tmp_path / "real"
    real_root.mkdir()
    (real_root / "result.json").write_bytes(b"real")
    linked_root = tmp_path / "linked-root"
    linked_root.symlink_to(real_root, target_is_directory=True)

    report = verify_phase2_evidence_receipt(
        _receipt("result.json", _digest(b"real")), linked_root
    )

    assert not report.admitted
    assert "artifact_root_unsafe" in report.blockers
    assert report.observed_hashes == ()


def test_platform_without_descriptor_relative_nofollow_fails_closed(
    tmp_path, monkeypatch
) -> None:
    (tmp_path / "result.json").write_bytes(b"real")
    monkeypatch.setattr(admission, "_secure_descriptor_traversal_available", lambda: False)

    report = verify_phase2_evidence_receipt(
        _receipt("result.json", _digest(b"real")), tmp_path
    )

    assert not report.admitted
    assert report.blockers == ("secure_descriptor_traversal_unavailable",)
    assert report.observed_hashes == ()
