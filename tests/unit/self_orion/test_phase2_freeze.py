import json
import subprocess

import pytest

from orion.benchmarks.cli import main
from orion.providers.live_phase2 import (
    build_phase2_live_provider_stack,
    load_live_phase2_provider_manifest,
    write_live_phase2_provider_manifest,
)
from orion.self_orion.phase2_io import load_phase2_binding
from orion.self_orion.phase2_preflight import (
    Phase2PreflightStatus,
    assess_phase2_preflight,
)


def _git(root, *args):
    return subprocess.run(
        ("git", "-C", str(root), *args),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def _repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init")
    _git(root, "config", "user.name", "ORION Test")
    _git(root, "config", "user.email", "orion@example.test")
    _git(root, "remote", "add", "origin", "https://github.com/SzeChunYiu/ORION.git")
    (root / "orion.txt").write_text("exact subject\n")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "subject")
    return root


def _provider_manifest(tmp_path):
    stack = build_phase2_live_provider_stack(
        reasoner_api_key="reasoner-secret",
        reasoner_model="gpt-reasoner-test",
        protected_verifier_endpoint="https://verifier.example.test/v1/verify",
        protected_verifier_token="verifier-secret",
        evaluator_artifact_hash="e" * 64,
        evaluation_epoch_id="epoch:frozen",
    )
    path = tmp_path / "provider.json"
    write_live_phase2_provider_manifest(stack, path)
    return stack, path


def test_phase2_freeze_cli_binds_clean_subject_provider_evaluator_and_packet(tmp_path, capsys):
    root = _repo(tmp_path)
    stack, provider_path = _provider_manifest(tmp_path)
    subject_path = tmp_path / "subject.json"
    binding_path = tmp_path / "binding.json"

    assert main(
        [
            "phase2-freeze",
            "--repo",
            str(root),
            "--provider-manifest",
            str(provider_path),
            "--subject-output",
            str(subject_path),
            "--binding-output",
            str(binding_path),
            "--resource-budget-units",
            "100",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "READY_TO_EXECUTE_SHADOW_TRIAL"
    assert payload["provider_manifest_hash"] == stack.provider_manifest_hash
    assert payload["evaluator_artifact_hash"] == "e" * 64
    assert payload["evaluation_epoch_id"] == "epoch:frozen"
    assert len(payload["subject_revision_hash"]) == 64
    assert len(payload["source_tree_sha256"]) == 64
    assert len(payload["live_trial_packet_fingerprint"]) == 64
    assert not payload["grants_phase2_closure"]

    subject = json.loads(subject_path.read_text())
    binding = load_phase2_binding(binding_path)
    assert subject["subject_revision_hash"] == payload["subject_revision_hash"]
    assert binding.subject_revision_hash == payload["subject_revision_hash"]
    assert binding.provider_manifest_hash == stack.provider_manifest_hash
    assert assess_phase2_preflight(binding).status is Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL


def test_provider_manifest_loader_rejects_tampering(tmp_path):
    _, provider_path = _provider_manifest(tmp_path)
    manifest = load_live_phase2_provider_manifest(provider_path)
    assert len(manifest.hash) == 64
    raw = json.loads(provider_path.read_text())
    raw["reasoner_provider"]["model"] = "posthoc-model"
    provider_path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="hash mismatch"):
        load_live_phase2_provider_manifest(provider_path)


def test_phase2_freeze_rejects_dirty_subject(tmp_path):
    root = _repo(tmp_path)
    _, provider_path = _provider_manifest(tmp_path)
    (root / "orion.txt").write_text("dirty subject\n")
    with pytest.raises(RuntimeError, match="dirty or untracked"):
        main(
            [
                "phase2-freeze",
                "--repo",
                str(root),
                "--provider-manifest",
                str(provider_path),
                "--subject-output",
                str(tmp_path / "subject.json"),
                "--binding-output",
                str(tmp_path / "binding.json"),
                "--resource-budget-units",
                "100",
            ]
        )
