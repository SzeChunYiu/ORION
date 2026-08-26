from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

import build_manifest
import fiberguard_cleanroom as fg
import run_replay
import verify_receipt


def _manifest(tmp_path: Path) -> dict[str, object]:
    (tmp_path / "source.py").write_text("value = 1\n")
    return fg.build_manifest(tmp_path, ("source.py",))


def _git(repository: Path, *arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=repository, text=True).strip()


def _committed_repository(root: Path) -> tuple[Path, str, str, str, str]:
    repository = root / "repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    subprocess.run(
        ["git", "config", "user.email", "guard@example.invalid"],
        cwd=repository,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "FiberGuard gate test"],
        cwd=repository,
        check=True,
    )
    source = repository / "source.py"
    source.write_text("subject = 1\n")
    subprocess.run(["git", "add", "source.py"], cwd=repository, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "subject"], cwd=repository, check=True)
    subject = _git(repository, "rev-parse", "HEAD")
    subject_tree = _git(repository, "rev-parse", "HEAD^{tree}")
    source.write_text("subject = 1\nimplementation = 1\n")
    subprocess.run(["git", "add", "source.py"], cwd=repository, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "implementation"],
        cwd=repository,
        check=True,
    )
    implementation = _git(repository, "rev-parse", "HEAD")
    implementation_tree = _git(repository, "rev-parse", "HEAD^{tree}")
    return repository, subject, subject_tree, implementation, implementation_tree


def _packet_validation(
    *, subject: str, subject_tree: str, implementation: str, implementation_tree: str
) -> dict[str, object]:
    return {
        "schema": "ORION.FivePaperR8.PacketPublicationBinding.v1",
        "terminal": "R8_PACKET_SUBJECT_AND_PUBLICATION_IDENTITIES_BOUND",
        "scientific_subject": {
            "commit": subject,
            "tree": subject_tree,
            "source_branch": "codex/five-paper-top-tier-r8-20260826",
            "source_ref": "refs/heads/codex/five-paper-top-tier-r8-20260826",
            "source_ref_observed_commit": subject,
            "exact_checkout_required": True,
            "scope": "synthetic unit-test subject",
        },
        "packet_publication": {
            "commit": implementation,
            "tree": implementation_tree,
            "path": fg.PACKET_PATH.as_posix(),
            "git_blob": "a" * 40,
            "sha256": "b" * 64,
            "bytes": 1,
        },
        "predecessor_packet": {
            "schema": "ORION.FivePaperR8.PacketCommit.v1",
            "publication_commit": subject,
            "publication_tree": subject_tree,
            "path": fg.PACKET_PATH.as_posix(),
            "git_blob": "c" * 40,
            "sha256": "d" * 64,
            "bytes": 1,
            "preserved_path": ("papers/five-paper-top-tier-r8/R8_PACKET_COMMIT_V1_PRESERVED.json"),
            "status": "PRESERVED_AS_HISTORICAL_INVALID_SELF_REFERENCE_ATTEMPT",
        },
        "authority": dict(fg.PACKET_AUTHORITY),
        "validated_at_checkout": implementation,
        "source_ref_status": "EXACT",
    }


def test_fixture_receipt_is_sealed_without_packet_or_panel_outcomes(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    receipt = run_replay.prepare_fixture_receipt(manifest)
    assert fg.verify_sealed_payload(receipt)
    assert receipt["binding"]["manifest_sha256"] == manifest["manifest_sha256"]
    assert receipt["payload"]["full_panel_execution"] == "NOT_RUN"
    assert receipt["payload"]["independence_terminal"] == "CANNOT_CHECK"
    assert receipt["payload"]["blinding_breach"] == "BLINDING_BREACH_ISSUE_BODY"


def test_execute_mode_rejects_legacy_placeholder_packet_before_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = _manifest(tmp_path)
    packet_path = tmp_path / "R8_PACKET_COMMIT.json"
    packet_path.write_text(
        json.dumps(
            {
                "schema": "ORION.FivePaperR8.PacketCommit.v1",
                "packet_commit": "TO_BE_BOUND_AFTER_MATERIALIZATION",
                "base_commit": "0" * 40,
                "branch": "codex/five-paper-top-tier-r8-20260826",
            }
        )
    )
    dispatched = False

    def forbidden_dispatch(*, workers: int) -> dict[str, object]:
        nonlocal dispatched
        dispatched = True
        return {"workers": workers}

    monkeypatch.setattr(run_replay.fg, "execute_all_panels", forbidden_dispatch)
    with pytest.raises(fg.PacketIdentityMismatch, match="canonical v2 packet"):
        run_replay.prepare_execution_receipt(
            manifest=manifest,
            packet_path=packet_path,
            repository=tmp_path,
            workers=16,
        )
    assert not dispatched


def test_exact_v2_subject_and_publication_binding_resolves_at_checkout() -> None:
    cleanroom = Path(__file__).resolve().parents[1]
    repository = cleanroom.parents[3]
    packet = fg.require_packet_identity(repository / fg.PACKET_PATH, repository=repository)
    assert packet["terminal"] == "R8_PACKET_SUBJECT_AND_PUBLICATION_IDENTITIES_BOUND"
    assert packet["source_ref_status"] in {"EXACT", "NOT_AVAILABLE_LOCALLY"}
    assert packet["scientific_subject"]["commit"] == ("0c451e862a0eeddac7c673813c4dc499f134b088")
    assert packet["scientific_subject"]["tree"] == ("dbf96cce53d21d25584479fb740473293fae75e0")
    assert packet["packet_publication"]["commit"] != packet["scientific_subject"]["commit"]
    assert packet["authority"] == fg.PACKET_AUTHORITY


def test_execute_mode_checks_external_authority_before_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository, subject, subject_tree, implementation, implementation_tree = _committed_repository(
        tmp_path
    )
    manifest = fg.build_manifest(repository, ("source.py",))
    packet_path = tmp_path / "R8_PACKET_COMMIT.json"
    packet_path.write_text(
        json.dumps(
            {
                "schema": "ORION.FivePaperR8.PacketCommit.v1",
                "packet_commit": subject,
                "base_commit": subject,
                "branch": "codex/five-paper-top-tier-r8-20260826",
            }
        )
    )
    dispatched = False

    def forbidden_dispatch(*, workers: int) -> dict[str, object]:
        nonlocal dispatched
        dispatched = True
        return {"workers": workers}

    monkeypatch.setattr(run_replay.fg, "execute_all_panels", forbidden_dispatch)
    monkeypatch.setattr(
        run_replay.fg,
        "require_packet_identity",
        lambda packet_path, *, repository: _packet_validation(
            subject=subject,
            subject_tree=subject_tree,
            implementation=implementation,
            implementation_tree=implementation_tree,
        ),
    )
    with pytest.raises(fg.ExecutionAuthorizationMismatch, match="external root-review"):
        run_replay.prepare_execution_receipt(
            manifest=manifest,
            packet_path=packet_path,
            repository=repository,
            workers=2,
        )
    assert not dispatched


def test_receipt_verifier_binds_manifest_and_rejects_tamper(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    receipt = run_replay.prepare_fixture_receipt(manifest)
    verify_receipt.verify_receipt(root=tmp_path, manifest=manifest, receipt=receipt)

    receipt["binding"]["manifest_sha256"] = "f" * 64
    with pytest.raises(verify_receipt.ReceiptMismatch, match="manifest"):
        verify_receipt.verify_receipt(root=tmp_path, manifest=manifest, receipt=receipt)


def test_atomic_json_writer_leaves_no_partial_file(tmp_path: Path) -> None:
    destination = tmp_path / "receipt.json"
    run_replay.write_json_atomic(destination, {"b": 2, "a": 1})
    assert destination.read_text() == '{\n  "a": 1,\n  "b": 2\n}\n'
    assert list(tmp_path.glob("*.tmp")) == []


def test_source_manifest_allowlist_is_cleanroom_local_and_unique() -> None:
    paths = build_manifest.SOURCE_PATHS
    assert len(paths) == len(set(paths))
    assert paths == tuple(sorted(paths))
    assert "conftest.py" in paths
    assert "fiberguard_cleanroom.py" in paths
    assert "tests/test_fiberguard_cleanroom.py" in paths
    assert all(not path.startswith("../") and "/artifact/" not in f"/{path}" for path in paths)


def test_execution_manifest_gate_requires_the_exact_source_allowlist(tmp_path: Path) -> None:
    (tmp_path / "implementation.py").write_text("value = 1\n")
    (tmp_path / "protocol.json").write_text("{}\n")
    incomplete = fg.build_manifest(tmp_path, ("implementation.py",))
    with pytest.raises(fg.ManifestMismatch, match="exact required allowlist"):
        fg.verify_manifest(
            tmp_path,
            incomplete,
            required_paths=("implementation.py", "protocol.json"),
        )


def test_external_authorization_binds_exact_clean_commit_tree_and_subject(
    tmp_path: Path,
) -> None:
    repository, subject, subject_tree, implementation, implementation_tree = _committed_repository(
        tmp_path
    )
    authorization = tmp_path / "authorization.json"
    authorization.write_text(
        json.dumps(
            {
                "schema": "ORION.FiberGuardCleanroomExecutionAuthorization.v1",
                "job_id": "JOB-C-R8-1",
                "scientific_subject_commit": subject,
                "scientific_subject_tree": subject_tree,
                "implementation_commit": implementation,
                "implementation_tree": implementation_tree,
                "source_manifest_sha256": "a" * 64,
                "grants_execution_authority": True,
                "grants_lunarc_submission": True,
                "authority_terminal": "ROOT_REVIEW_AUTHORIZED",
            },
            sort_keys=True,
        )
    )
    bound = fg.require_execution_authorization(
        authorization,
        repository=repository,
        scientific_subject_commit=subject,
        source_manifest_sha256="a" * 64,
    )
    assert bound["implementation_commit"] == implementation
    assert bound["implementation_tree"] == implementation_tree
    assert bound["authorization_sha256"] == hashlib.sha256(authorization.read_bytes()).hexdigest()

    (repository / "dirty.txt").write_text("unbound\n")
    with pytest.raises(fg.ExecutionAuthorizationMismatch, match="clean checkout"):
        fg.require_execution_authorization(
            authorization,
            repository=repository,
            scientific_subject_commit=subject,
            source_manifest_sha256="a" * 64,
        )


def test_checkout_scope_accepts_full_or_exact_r8_sparse_cone(tmp_path: Path) -> None:
    repository = tmp_path / "scope-repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    subprocess.run(
        ["git", "config", "user.email", "scope@example.invalid"], cwd=repository, check=True
    )
    subprocess.run(["git", "config", "user.name", "Scope test"], cwd=repository, check=True)
    for relative in fg.SPARSE_REQUIRED_FILES:
        path = repository / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"bound {relative.as_posix()}\n")
    subprocess.run(["git", "add", "."], cwd=repository, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "scope"], cwd=repository, check=True)
    assert fg.require_checkout_scope(repository) == "FULL"

    subprocess.run(["git", "sparse-checkout", "init", "--cone"], cwd=repository, check=True)
    subprocess.run(
        ["git", "sparse-checkout", "set", *fg.SPARSE_CHECKOUT_PATHS],
        cwd=repository,
        check=True,
    )
    assert fg.require_checkout_scope(repository) == "SPARSE_EXACT_FIVE_PAPER_R8"

    subprocess.run(["git", "sparse-checkout", "set", "papers"], cwd=repository, check=True)
    with pytest.raises(fg.ExecutionAuthorizationMismatch, match="exact R8 scope"):
        fg.require_checkout_scope(repository)


def test_execution_provenance_binds_command_resources_and_stream_hashes(
    tmp_path: Path,
) -> None:
    repository, _, _, implementation, implementation_tree = _committed_repository(tmp_path)
    provenance = fg.build_execution_provenance(
        repository=repository,
        workers=3,
        command=("python", "run_replay.py", "--mode", "execute"),
        started_at="2026-08-26T12:00:00.000000Z",
        ended_at="2026-08-26T12:00:02.500000Z",
        wall_time_seconds=2.5,
        maximum_rss=12345,
        exit_code=0,
        stdout=b"panel progress\n",
        stderr=b"",
        slurm_job_id="12345",
    )
    assert provenance["git_commit"] == implementation
    assert provenance["git_tree"] == implementation_tree
    assert provenance["git_status"] == "CLEAN"
    assert provenance["checkout_scope"] == "FULL"
    assert provenance["workers"] == 3
    assert provenance["wall_time_seconds"] == 2.5
    assert provenance["maximum_rss"] == 12345
    assert provenance["maximum_rss_scope"] == (
        "RUSAGE_SELF_EXECUTOR_ONLY__EXCLUDES_CHILD_PROCESS_PEAKS"
    )
    assert provenance["maximum_rss_unit"] in {
        "KiB",
        "bytes",
        "CANNOT_CHECK_PLATFORM_NATIVE",
    }
    assert provenance["exit_code"] == 0
    assert provenance["stdout_sha256"] == hashlib.sha256(b"panel progress\n").hexdigest()
    assert provenance["stderr_sha256"] == hashlib.sha256(b"").hexdigest()


def test_receipt_verifier_rejects_semantically_overstated_payload(
    tmp_path: Path,
) -> None:
    manifest = _manifest(tmp_path)
    receipt = fg.seal_payload(
        {
            "independence_terminal": "FORBIDDEN_PASS",
            "comparison_to_frozen_outcomes": "FORBIDDEN_PERFORMED",
            "scientific_authority_delta": "FORBIDDEN_GAIN",
        },
        manifest_sha256=str(manifest["manifest_sha256"]),
    )
    with pytest.raises(verify_receipt.ReceiptMismatch, match="payload schema"):
        verify_receipt.verify_receipt(
            root=tmp_path,
            manifest=manifest,
            receipt=receipt,
        )


def test_execution_receipt_rejects_incomplete_identity_and_provenance(
    tmp_path: Path,
) -> None:
    manifest = _manifest(tmp_path)
    receipt = fg.seal_payload(
        {
            "schema": "ORION.FiberGuardCleanroomOutput.v1",
            "panels": {"graphs": {}, "set_cover": {}, "two_cnf": {}},
            "execution_terminal": "CLEANROOM_EXHAUSTIVE_REPLAY_COMPLETED",
            "independence_terminal": "CANNOT_CHECK",
            "blinding_breach": "BLINDING_BREACH_ISSUE_BODY",
            "comparison_to_frozen_outcomes": "NOT_PERFORMED",
            "scientific_authority_delta": "NONE",
            "packet_identity": {},
            "execution_authorization": {"authority_terminal": "ROOT_REVIEW_AUTHORIZED"},
            "execution_provenance": {"git_status": "CLEAN", "exit_code": 0},
        },
        manifest_sha256=str(manifest["manifest_sha256"]),
    )
    with pytest.raises(verify_receipt.ReceiptMismatch, match="provenance schema"):
        verify_receipt.verify_receipt(
            root=tmp_path,
            manifest=manifest,
            receipt=receipt,
        )


def test_authorized_execution_receipt_binds_identity_and_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository, subject, subject_tree, implementation, implementation_tree = _committed_repository(
        tmp_path
    )
    manifest = fg.build_manifest(repository, ("source.py",))
    packet = tmp_path / "packet.json"
    packet.write_text("{}\n")
    packet_validation = _packet_validation(
        subject=subject,
        subject_tree=subject_tree,
        implementation=implementation,
        implementation_tree=implementation_tree,
    )
    monkeypatch.setattr(
        run_replay.fg,
        "require_packet_identity",
        lambda packet_path, *, repository: packet_validation,
    )
    authorization = tmp_path / "authorization.json"
    authorization.write_text(
        json.dumps(
            {
                "schema": "ORION.FiberGuardCleanroomExecutionAuthorization.v1",
                "job_id": "JOB-C-R8-1",
                "scientific_subject_commit": subject,
                "scientific_subject_tree": subject_tree,
                "implementation_commit": implementation,
                "implementation_tree": implementation_tree,
                "source_manifest_sha256": manifest["manifest_sha256"],
                "grants_execution_authority": True,
                "grants_lunarc_submission": True,
                "authority_terminal": "ROOT_REVIEW_AUTHORIZED",
            },
            sort_keys=True,
        )
    )
    monkeypatch.setattr(
        run_replay.fg,
        "execute_all_panels",
        lambda *, workers: {
            "schema": "ORION.FiberGuardCleanroomOutput.v1",
            "panels": {"graphs": {}, "set_cover": {}, "two_cnf": {}},
            "execution_terminal": "CLEANROOM_EXHAUSTIVE_REPLAY_COMPLETED",
            "independence_terminal": "CANNOT_CHECK",
            "blinding_breach": "BLINDING_BREACH_ISSUE_BODY",
            "comparison_to_frozen_outcomes": "NOT_PERFORMED",
            "scientific_authority_delta": "NONE",
        },
    )
    receipt = run_replay.prepare_execution_receipt(
        manifest=manifest,
        packet_path=packet,
        authorization_path=authorization,
        repository=repository,
        workers=2,
        command=("python", "run_replay.py", "--mode", "execute"),
        slurm_job_id="synthetic-control",
    )
    with pytest.raises(verify_receipt.ReceiptMismatch, match="external authorization object"):
        verify_receipt.verify_receipt(
            root=repository,
            manifest=manifest,
            receipt=receipt,
        )
    verify_receipt.verify_receipt(
        root=repository,
        manifest=manifest,
        receipt=receipt,
        authorization_path=authorization,
    )
    assert receipt["payload"]["execution_provenance"]["git_status"] == "CLEAN"
    assert receipt["payload"]["execution_authorization"]["implementation_commit"] == implementation

    mutated_payload = json.loads(json.dumps(receipt["payload"]))
    mutated_payload["packet_identity"]["predecessor_packet"] = {}
    mutated_receipt = fg.seal_payload(
        mutated_payload,
        manifest_sha256=str(manifest["manifest_sha256"]),
    )
    with pytest.raises(verify_receipt.ReceiptMismatch, match="packet identity values"):
        verify_receipt.verify_receipt(
            root=repository,
            manifest=manifest,
            receipt=mutated_receipt,
            authorization_path=authorization,
        )

    swapped_payload = json.loads(json.dumps(receipt["payload"]))
    swapped_subject = swapped_payload["packet_identity"]["scientific_subject"]
    swapped_publication = swapped_payload["packet_identity"]["packet_publication"]
    swapped_subject["commit"] = swapped_publication["commit"]
    swapped_subject["source_ref_observed_commit"] = swapped_publication["commit"]
    swapped_receipt = fg.seal_payload(
        swapped_payload,
        manifest_sha256=str(manifest["manifest_sha256"]),
    )
    with pytest.raises(verify_receipt.ReceiptMismatch, match="packet identity values"):
        verify_receipt.verify_receipt(
            root=repository,
            manifest=manifest,
            receipt=swapped_receipt,
            authorization_path=authorization,
        )


def test_slurm_envelope_and_packet_gate_are_static() -> None:
    script = (Path(__file__).resolve().parents[1] / "slurm" / "job_c_r8_1.slurm").read_text()
    assert "#SBATCH --cpus-per-task=16" in script
    assert "#SBATCH --mem=32G" in script
    assert "#SBATCH --time=02:00:00" in script
    assert "--mode execute" in script
    assert "R8_PACKET_COMMIT.json" in script
    assert "ORION_REPOSITORY" in script
    assert "FIBERGUARD_EXECUTION_AUTHORIZATION" in script
    assert "--authorization-file" in script
    assert 'OUTPUT="${RUN_ROOT}/results/JOB-C-R8-1-${SLURM_JOB_ID}.json"' in script
    assert 'OUTPUT="${CLEANROOM}' not in script
    assert "--workers 16" in script


@pytest.mark.parametrize(
    "sample",
    (0, 1, 7, 1_234, 23_456, 2**15 - 1),
)
def test_graph_sample_has_three_way_target_agreement(sample: int) -> None:
    first = fg.graph_chromatic_by_coloring(sample)
    second = fg.graph_chromatic_by_independent_cover(sample)
    third = fg.graph_endpoint_check(sample)["target"]
    assert first == second == third


def test_cover_and_cnf_samples_have_three_way_target_agreement() -> None:
    cover_samples = fg.cover_families()[::25_000]
    for family in cover_samples:
        assert (
            fg.cover_size_by_subset_search(family)
            == fg.cover_size_by_mask_dp(family)
            == fg.cover_endpoint_check(family)["target"]
        )

    cnf_samples = fg.cnf_formulas()[::7_000]
    for formula in cnf_samples:
        assert (
            fg.cnf_count_by_truth_table(formula)
            == fg.cnf_count_by_clause_recursion(formula)
            == fg.cnf_endpoint_check(formula)["target"]
        )
