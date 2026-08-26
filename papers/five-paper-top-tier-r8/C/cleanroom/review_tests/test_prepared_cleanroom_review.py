from __future__ import annotations

import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest


CLEANROOM = Path(__file__).resolve().parents[1]
REPOSITORY = CLEANROOM.parents[3]
sys.path.insert(0, str(CLEANROOM))

import build_manifest  # noqa: E402
import fiberguard_cleanroom as fg  # noqa: E402
import run_replay  # noqa: E402
import verify_receipt  # noqa: E402


def test_review_is_bound_to_the_prepared_commit_and_tree() -> None:
    prepared = "e0527cba658eceb3af3b84e11bb384d468974e6b"
    tree = subprocess.check_output(
        ["git", "-C", str(REPOSITORY), "rev-parse", f"{prepared}^{{tree}}"],
        text=True,
    ).strip()
    assert tree == "ba5d33cccdda0ef5874a4d267a9746b74d00a5eb"
    assert (
        subprocess.run(
            ["git", "-C", str(REPOSITORY), "merge-base", "--is-ancestor", prepared, "HEAD"],
            check=False,
        ).returncode
        == 0
    )


def test_frozen_manifests_and_non_outcome_receipt_verify() -> None:
    source = json.loads((CLEANROOM / "SOURCE_MANIFEST.json").read_text())
    evidence = json.loads((CLEANROOM / "EVIDENCE_MANIFEST.json").read_text())
    receipt = json.loads((CLEANROOM / "NON_OUTCOME_VALIDATION.json").read_text())
    assert source == fg.build_manifest(CLEANROOM, build_manifest.SOURCE_PATHS)
    fg.verify_manifest(CLEANROOM, source)
    fg.verify_manifest(CLEANROOM, evidence)
    verify_receipt.verify_receipt(root=CLEANROOM, manifest=source, receipt=receipt)


def test_blinding_breach_and_cannot_check_are_preserved() -> None:
    breach = json.loads((CLEANROOM / "BLINDING_BREACH.json").read_text())
    protocol = json.loads((CLEANROOM / "SOURCE_PROTOCOL.json").read_text())
    blocker = json.loads((CLEANROOM / "SUBMISSION_BLOCKER.json").read_text())
    non_outcome = json.loads((CLEANROOM / "NON_OUTCOME_VALIDATION.json").read_text())
    assert breach["breach"] == "BLINDING_BREACH_ISSUE_BODY"
    assert breach["terminal"] == "CANNOT_CHECK"
    assert breach["authority_effect"]["later_truly_blinded_external_worker_required"] is True
    assert protocol["authority"]["independence_terminal"] == "CANNOT_CHECK"
    assert blocker["independence_terminal"] == "CANNOT_CHECK"
    assert blocker["lunarc_submission"] == "NOT_SUBMITTED"
    assert blocker["terminal"] == "BLOCKED_NO_LUNARC_EXECUTION_AUTHORITY__CANNOT_CHECK"
    assert non_outcome["payload"]["full_panel_execution"] == "NOT_RUN"
    assert non_outcome["payload"]["comparison_to_frozen_outcomes"] == "NOT_PERFORMED"


def test_incomplete_v2_packet_cannot_bypass_the_canonical_binding_gate(tmp_path: Path) -> None:
    packet = tmp_path / "R8_PACKET_COMMIT.json"
    packet.write_text(
        json.dumps(
            {
                "schema": "ORION.FivePaperR8.PacketIdentity.v2",
                "contract": "NON_SELF_REFERENTIAL_SUBJECT_PLUS_EXTERNAL_PUBLICATION_BINDING",
                "scientific_subject": {},
                "packet_publication_binding": {},
                "predecessor_packet": {},
                "reader_contract": {},
                "authority": {
                    "grants_execution_authority": False,
                    "grants_lunarc_submission": False,
                },
            }
        )
    )
    with pytest.raises(fg.PacketIdentityMismatch, match="canonical v2 packet"):
        fg.require_packet_identity(packet, repository=REPOSITORY)


def test_legacy_packet_cannot_bypass_the_canonical_v2_path(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "review@example.invalid"], cwd=tmp_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Prepared packet reviewer"], cwd=tmp_path, check=True
    )
    source = tmp_path / "source.py"
    source.write_text("value = 1\n")
    subprocess.run(["git", "add", "source.py"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "subject"], cwd=tmp_path, check=True)
    subject = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp_path, text=True).strip()
    source.write_text("value = 2  # dirty and unbound\n")
    packet = tmp_path / "R8_PACKET_COMMIT.json"
    packet.write_text(
        json.dumps(
            {
                "schema": "ORION.FivePaperR8.PacketCommit.v1",
                "packet_commit": subject,
                "base_commit": "f" * 40,
                "branch": "codex/five-paper-top-tier-r8-20260826",
            }
        )
    )
    with pytest.raises(fg.PacketIdentityMismatch, match="canonical v2 packet"):
        fg.require_packet_identity(packet, repository=tmp_path)
    assert subprocess.check_output(["git", "status", "--porcelain"], cwd=tmp_path, text=True)


def test_execution_manifest_gate_rejects_an_incomplete_allowlist(tmp_path: Path) -> None:
    (tmp_path / "one.py").write_text("value = 1\n")
    incomplete = fg.build_manifest(tmp_path, ("one.py",))
    fg.verify_manifest(tmp_path, incomplete)
    with pytest.raises(fg.ManifestMismatch, match="exact required allowlist"):
        fg.verify_manifest(
            tmp_path,
            incomplete,
            required_paths=build_manifest.SOURCE_PATHS,
        )
    assert "required_paths=build_manifest.SOURCE_PATHS" in inspect.getsource(run_replay.main)


def test_receipt_verifier_rejects_semantically_overstated_payload(tmp_path: Path) -> None:
    (tmp_path / "one.py").write_text("value = 1\n")
    manifest = fg.build_manifest(tmp_path, ("one.py",))
    synthetic = fg.seal_payload(
        {
            "independence_terminal": "FORBIDDEN_PASS",
            "comparison_to_frozen_outcomes": "FORBIDDEN_PERFORMED",
            "scientific_authority_delta": "FORBIDDEN_GAIN",
        },
        manifest_sha256=manifest["manifest_sha256"],
    )
    with pytest.raises(verify_receipt.ReceiptMismatch, match="payload schema"):
        verify_receipt.verify_receipt(
            root=tmp_path,
            manifest=manifest,
            receipt=synthetic,
        )


def test_third_checkers_are_algorithmically_distinct_but_same_source_custody() -> None:
    checkers = (
        fg.graph_endpoint_check,
        fg.cover_endpoint_check,
        fg.cnf_endpoint_check,
    )
    assert all(
        inspect.getsourcefile(checker) == str(CLEANROOM / "fiberguard_cleanroom.py")
        for checker in checkers
    )
    assert "graph_chromatic_by_coloring" not in inspect.getsource(fg.graph_endpoint_check)
    assert "cover_size_by_subset_search" not in inspect.getsource(fg.cover_endpoint_check)
    assert "cnf_count_by_truth_table" not in inspect.getsource(fg.cnf_endpoint_check)


def test_slurm_envelope_keeps_external_run_and_authorization_gates() -> None:
    script = (CLEANROOM / "slurm" / "job_c_r8_1.slurm").read_text()
    assert "#SBATCH --cpus-per-task=16" in script
    assert "#SBATCH --mem=32G" in script
    assert "#SBATCH --time=02:00:00" in script
    assert "--workers 16" in script
    for required_provenance in (
        "git rev-parse HEAD",
        "git status --porcelain",
        "--authorization-file",
        "ORION_REPOSITORY",
        "FIBERGUARD_EXECUTION_AUTHORIZATION",
    ):
        assert required_provenance in script
    assert len(fg.DOMAIN_RUNNERS) == 3


def test_non_outcome_receipt_contains_no_execution_provenance() -> None:
    receipt = json.loads((CLEANROOM / "NON_OUTCOME_VALIDATION.json").read_text())
    payload = receipt["payload"]
    for missing in (
        "git_commit",
        "git_tree",
        "git_status",
        "python_version",
        "slurm_job_id",
        "wall_time_seconds",
        "maximum_rss",
        "stdout_sha256",
        "stderr_sha256",
    ):
        assert missing not in payload
