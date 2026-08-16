from __future__ import annotations

import errno
import hashlib
import inspect
import os
import shutil
import subprocess
import sys
import time
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

import orion.kernel as kernel
import orion.kernel.evidence as evidence_module
from orion.kernel.evidence import (
    EVIDENCE_MANIFEST_SCHEMA_VERSION,
    EVIDENCE_SNAPSHOT_SCHEMA_VERSION,
    EvidenceStatus,
    EvidenceRoleBinding,
    HostEvidenceRecord,
    HostEvidenceSource,
    HostEvidenceManifest,
    HostEvidenceSnapshot,
    capture_host_evidence_snapshot,
    snapshot_hash,
)


def _binding(
    *,
    binding_id: str = "binding:source",
    evidence_ref: str = "orion:source.bin@" + "a" * 64,
    role_id: str = "role:primary-source",
    obligation_id: str = "obligation:source-content",
) -> EvidenceRoleBinding:
    return EvidenceRoleBinding(
        binding_id=binding_id,
        evidence_ref=evidence_ref,
        role_id=role_id,
        obligation_id=obligation_id,
    )


def _source_from_ref(ref: str) -> HostEvidenceSource:
    scheme, separator, remainder = ref.partition(":")
    assert separator
    relative_path, separator, declaration = remainder.rpartition("@")
    assert separator
    if declaration.startswith("git:"):
        return HostEvidenceSource(
            source_id=ref,
            backend_type="git",
            root_scheme=scheme,
            relative_path=relative_path,
            git_revision=declaration.removeprefix("git:"),
        )
    return HostEvidenceSource(
        source_id=ref,
        backend_type="file",
        root_scheme=scheme,
        relative_path=relative_path,
        expected_content_sha256=declaration,
    )


def _manifest(
    *bindings: EvidenceRoleBinding,
    sources: tuple[HostEvidenceSource, ...] | None = None,
) -> HostEvidenceManifest:
    selected_bindings = bindings or (_binding(),)
    if sources is None:
        sources = tuple(
            {
                binding.evidence_ref: _source_from_ref(binding.evidence_ref)
                for binding in selected_bindings
            }.values()
        )
    return HostEvidenceManifest(
        manifest_id="manifest:test",
        required_obligation_ids=("obligation:source-content",),
        sources=sources,
        bindings=selected_bindings,
    )


def _manifest_for_ref(ref: str) -> HostEvidenceManifest:
    return _manifest(_binding(evidence_ref=ref))


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(  # noqa: S603 - fixed Git executable and test argv
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _git_literal_object(root: Path, object_type: str, payload: bytes) -> str:
    return subprocess.run(  # noqa: S603 - fixed Git executable and test argv
        [
            "git",
            "-C",
            str(root),
            "hash-object",
            "-w",
            "--stdin",
            "--literally",
            "-t",
            object_type,
        ],
        input=payload,
        check=True,
        capture_output=True,
    ).stdout.decode("ascii").strip()


def test_host_manifest_is_versioned_deeply_immutable_and_hash_bound() -> None:
    manifest = _manifest()

    assert manifest.schema_version == EVIDENCE_MANIFEST_SCHEMA_VERSION
    assert len(manifest.manifest_hash) == 64
    with pytest.raises(FrozenInstanceError):
        manifest.manifest_id = "changed"  # type: ignore[misc]
    with pytest.raises(ValueError, match="tuple"):
        HostEvidenceManifest(
            manifest_id="manifest:mutable",
            required_obligation_ids=[  # type: ignore[arg-type]
                "obligation:source-content"
            ],
            sources=(_source_from_ref(_binding().evidence_ref),),
            bindings=(_binding(),),
        )


def test_host_manifest_rejects_duplicate_and_conflicting_bindings() -> None:
    binding = _binding()
    with pytest.raises(ValueError, match="duplicate"):
        _manifest(binding, binding)
    with pytest.raises(ValueError, match="conflicting"):
        _manifest(
            binding,
            _binding(
                binding_id="binding:conflict",
                role_id="role:untrusted-substitute",
            ),
        )
    with pytest.raises(ValueError, match="unknown obligation"):
        HostEvidenceManifest(
            manifest_id="manifest:unknown",
            required_obligation_ids=("obligation:source-content",),
            sources=(_source_from_ref(_binding().evidence_ref),),
            bindings=(_binding(obligation_id="obligation:not-registered"),),
        )


def test_host_manifest_canonicalizes_obligation_and_binding_order() -> None:
    first = _binding(
        binding_id="binding:a",
        evidence_ref="orion:a.bin@" + "a" * 64,
        obligation_id="obligation:a",
    )
    second = _binding(
        binding_id="binding:b",
        evidence_ref="orion:b.bin@" + "b" * 64,
        obligation_id="obligation:b",
    )

    forward = HostEvidenceManifest(
        manifest_id="manifest:ordered",
        required_obligation_ids=("obligation:a", "obligation:b"),
        sources=(_source_from_ref(first.evidence_ref), _source_from_ref(second.evidence_ref)),
        bindings=(first, second),
    )
    reversed_input = HostEvidenceManifest(
        manifest_id="manifest:ordered",
        required_obligation_ids=("obligation:b", "obligation:a"),
        sources=(_source_from_ref(second.evidence_ref), _source_from_ref(first.evidence_ref)),
        bindings=(second, first),
    )

    assert reversed_input.required_obligation_ids == forward.required_obligation_ids
    assert reversed_input.bindings == forward.bindings
    assert reversed_input.manifest_hash == forward.manifest_hash


def test_one_snapshot_uses_one_open_evidence_occasion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "source.bin"
    original = b"original evidence occasion"
    replacement = b"replacement evidence occasion"
    path.write_bytes(original)
    digest = hashlib.sha256(original).hexdigest()
    ref = f"orion:source.bin@{digest}"
    real_read = evidence_module._read_open_descriptor
    reads = 0

    def read_then_rewrite(fd: int, limit: int) -> tuple[bytes, bool]:
        nonlocal reads
        reads += 1
        payload = real_read(fd, limit)
        path.write_bytes(replacement)
        return payload

    monkeypatch.setattr(evidence_module, "_read_open_descriptor", read_then_rewrite)
    snapshot = capture_host_evidence_snapshot(
        (ref,),
        roots={"orion": tmp_path},
        manifest=_manifest_for_ref(ref),
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )
    original_snapshot_hash = snapshot_hash(snapshot)
    (record,) = snapshot.records

    assert reads == 1
    assert snapshot.schema_version == EVIDENCE_SNAPSHOT_SCHEMA_VERSION
    assert record.status is EvidenceStatus.CHANGED_DURING_CAPTURE
    assert not record.resolved
    assert snapshot.cannot_check
    assert record.content_bytes == original
    assert record.content_hash == digest
    assert record.byte_length == len(original)
    assert record.utf8_text == original.decode("utf-8")
    assert snapshot.snapshot_id == original_snapshot_hash
    assert snapshot_hash(snapshot) == original_snapshot_hash


def test_snapshot_canonicalizes_record_and_obligation_order(tmp_path: Path) -> None:
    first_bytes = b"first"
    second_bytes = b"second"
    (tmp_path / "a.bin").write_bytes(first_bytes)
    (tmp_path / "b.bin").write_bytes(second_bytes)
    first_ref = f"orion:a.bin@{hashlib.sha256(first_bytes).hexdigest()}"
    second_ref = f"orion:b.bin@{hashlib.sha256(second_bytes).hexdigest()}"
    manifest = HostEvidenceManifest(
        manifest_id="manifest:two",
        required_obligation_ids=("obligation:a", "obligation:b"),
        sources=(_source_from_ref(first_ref), _source_from_ref(second_ref)),
        bindings=(
            _binding(
                binding_id="binding:a",
                evidence_ref=first_ref,
                obligation_id="obligation:a",
            ),
            _binding(
                binding_id="binding:b",
                evidence_ref=second_ref,
                obligation_id="obligation:b",
            ),
        ),
    )
    snapshot = capture_host_evidence_snapshot(
        (second_ref, first_ref),
        roots={"orion": tmp_path},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    normalized = replace(
        snapshot,
        records=tuple(reversed(snapshot.records)),
        required_obligation_ids=tuple(reversed(snapshot.required_obligation_ids)),
    )

    assert normalized.records == snapshot.records
    assert normalized.required_obligation_ids == snapshot.required_obligation_ids
    assert normalized.snapshot_id == snapshot.snapshot_id


def test_resolved_file_record_requires_available_matching_bytes(tmp_path: Path) -> None:
    payload = b"content-bound"
    (tmp_path / "source.bin").write_bytes(payload)
    ref = f"orion:source.bin@{hashlib.sha256(payload).hexdigest()}"
    snapshot = capture_host_evidence_snapshot(
        (ref,),
        roots={"orion": tmp_path},
        manifest=_manifest_for_ref(ref),
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )
    (record,) = snapshot.records
    assert record.status is EvidenceStatus.RESOLVED

    with pytest.raises(ValueError, match="match captured content"):
        replace(record, declared_digest="0" * 64)
    with pytest.raises(ValueError, match="available content"):
        replace(record, content_bytes=b"", content_available=False)
    with pytest.raises(ValueError, match="lowercase SHA-256"):
        replace(record, root_configuration_hash="not-a-root-hash")
    with pytest.raises(ValueError, match="role binding"):
        replace(record, role_bindings=())
    with pytest.raises(ValueError, match="backend"):
        replace(record, backend_type="unknown")
    with pytest.raises(ValueError, match="file evidence cannot carry Git"):
        replace(record, source_object_format="sha1")


def test_resolved_git_record_rejects_filesystem_only_metadata(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    (repo / "source.bin").write_bytes(b"git-only metadata")
    _git(repo, "add", "source.bin")
    _git(repo, "commit", "-qm", "git-only metadata")
    oid = _git(repo, "rev-parse", "HEAD")
    source = HostEvidenceSource(
        source_id="source:git-only-metadata",
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision=oid,
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:git-only-metadata",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source.source_id),),
    )
    record = capture_host_evidence_snapshot(
        (source.source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]

    assert record.status is EvidenceStatus.RESOLVED
    with pytest.raises(ValueError, match="Git evidence cannot carry filesystem"):
        replace(record, source_device=1)


def test_structured_source_preserves_delimiters_and_whitespace_in_path(
    tmp_path: Path,
) -> None:
    payload = b"canonical ref"
    relative_path = " source@name.bin"
    (tmp_path / relative_path).write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    source_id = "source:path-with-delimiters"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="file",
        root_scheme="orion",
        relative_path=relative_path,
        expected_content_sha256=digest,
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:structured-source",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    snapshot = capture_host_evidence_snapshot(
        (source_id,),
        roots={"orion": tmp_path},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.RESOLVED
    assert snapshot.records[0].relative_path == relative_path
    assert snapshot.records[0].content_bytes == payload


def test_git_ref_is_resolved_once_then_all_blobs_use_the_frozen_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    (repo / "a.bin").write_bytes(b"first-a")
    (repo / "b.bin").write_bytes(b"first-b")
    _git(repo, "add", "a.bin", "b.bin")
    _git(repo, "commit", "-qm", "first")
    first_oid = _git(repo, "rev-parse", "HEAD")
    _git(repo, "branch", "moving", first_oid)
    (repo / "a.bin").write_bytes(b"second-a")
    (repo / "b.bin").write_bytes(b"second-b")
    _git(repo, "commit", "-qam", "second")
    second_oid = _git(repo, "rev-parse", "HEAD")

    first_ref = "repo:a.bin@git:refs/heads/moving"
    second_ref = "repo:b.bin@git:refs/heads/moving"
    manifest = HostEvidenceManifest(
        manifest_id="manifest:git-freeze",
        required_obligation_ids=("obligation:a", "obligation:b"),
        sources=(_source_from_ref(first_ref), _source_from_ref(second_ref)),
        bindings=(
            _binding(
                binding_id="binding:a",
                evidence_ref=first_ref,
                obligation_id="obligation:a",
            ),
            _binding(
                binding_id="binding:b",
                evidence_ref=second_ref,
                obligation_id="obligation:b",
            ),
        ),
    )
    real_resolve = evidence_module._resolve_git_revision
    resolutions = 0

    def resolve_then_move(*args: object, **kwargs: object) -> object:
        nonlocal resolutions
        resolutions += 1
        resolved = real_resolve(*args, **kwargs)
        _git(repo, "branch", "-f", "moving", second_oid)
        return resolved

    monkeypatch.setattr(
        evidence_module, "_resolve_git_revision", resolve_then_move
    )

    snapshot = capture_host_evidence_snapshot(
        (second_ref, first_ref),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert resolutions == 1
    assert [record.status for record in snapshot.records] == [
        EvidenceStatus.RESOLVED,
        EvidenceStatus.RESOLVED,
    ]
    assert [record.content_bytes for record in snapshot.records] == [
        b"first-a",
        b"first-b",
    ]
    assert {record.resolved_source_revision for record in snapshot.records} == {
        first_oid
    }
    assert all(record.source_object_format == "sha1" for record in snapshot.records)
    assert all(len(record.source_blob_oid) == 40 for record in snapshot.records)
    with pytest.raises(ValueError, match="storage OID"):
        replace(snapshot.records[0], content_bytes=b"forged Git payload")


def test_git_command_work_budget_is_shared_across_snapshot_records(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    (repo / "a.bin").write_bytes(b"a")
    (repo / "b.bin").write_bytes(b"b")
    _git(repo, "add", "a.bin", "b.bin")
    _git(repo, "commit", "-qm", "bounded commands")
    _git(repo, "branch", "frozen")
    sources = tuple(
        HostEvidenceSource(
            source_id=f"source:{name}",
            backend_type="git",
            root_scheme="repo",
            relative_path=name,
            git_revision="refs/heads/frozen",
        )
        for name in ("a.bin", "b.bin")
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:bounded-git-commands",
        required_obligation_ids=("obligation:a", "obligation:b"),
        sources=sources,
        bindings=tuple(
            _binding(
                binding_id=f"binding:{index}",
                evidence_ref=source.source_id,
                obligation_id=f"obligation:{source.relative_path[0]}",
            )
            for index, source in enumerate(sources)
        ),
    )
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_CAPTURE_GIT_COMMANDS", 10)

    snapshot = capture_host_evidence_snapshot(
        tuple(source.source_id for source in sources),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert [record.status for record in snapshot.records] == [
        EvidenceStatus.RESOLVED,
        EvidenceStatus.WORK_BUDGET_EXHAUSTED,
    ]
    assert snapshot.records[0].content_bytes == b"a"
    assert not snapshot.records[1].content_available
    assert snapshot.cannot_check


def test_verified_git_object_cache_reuses_one_checked_blob(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    for name in ("a.bin", "b.bin"):
        (repo / name).write_bytes(b"shared blob")
    _git(repo, "add", "a.bin", "b.bin")
    _git(repo, "commit", "-qm", "shared blob")
    commit_oid = _git(repo, "rev-parse", "HEAD")
    blob_oid = _git(repo, "rev-parse", "HEAD:a.bin")
    sources = tuple(
        HostEvidenceSource(
            source_id=f"source:{name}",
            backend_type="git",
            root_scheme="repo",
            relative_path=name,
            git_revision=commit_oid,
        )
        for name in ("a.bin", "b.bin")
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:shared-blob-cache",
        required_obligation_ids=("obligation:a", "obligation:b"),
        sources=sources,
        bindings=tuple(
            _binding(
                binding_id=f"binding:{index}",
                evidence_ref=source.source_id,
                obligation_id=f"obligation:{source.relative_path[0]}",
            )
            for index, source in enumerate(sources)
        ),
    )
    real_run = evidence_module._run_protected_git
    calls: list[tuple[str, ...]] = []

    def observing_run(
        opened_root: object,
        *arguments: str,
        **kwargs: object,
    ) -> object:
        calls.append(arguments)
        return real_run(opened_root, *arguments, **kwargs)

    monkeypatch.setattr(evidence_module, "_run_protected_git", observing_run)
    snapshot = capture_host_evidence_snapshot(
        tuple(source.source_id for source in sources),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert [record.status for record in snapshot.records] == [
        EvidenceStatus.RESOLVED,
        EvidenceStatus.RESOLVED,
    ]
    assert [record.content_bytes for record in snapshot.records] == [
        b"shared blob",
        b"shared blob",
    ]
    assert calls.count(("cat-file", "-s", blob_oid)) == 1
    assert calls.count(("cat-file", "blob", blob_oid)) == 1
    assert dict(snapshot.capture_work_usage)["distinct_git_objects"] == 3


@pytest.mark.parametrize(
    ("stream", "limit_name", "usage_name"),
    (
        (
            "stdout",
            "MAX_EVIDENCE_CAPTURE_GIT_STDOUT_BYTES",
            "git_stdout_bytes",
        ),
        (
            "stderr",
            "MAX_EVIDENCE_CAPTURE_GIT_STDERR_BYTES",
            "git_stderr_bytes",
        ),
    ),
)
def test_git_output_work_budget_is_global_across_the_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stream: str,
    limit_name: str,
    usage_name: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    fake_git = tmp_path / "fake-git"
    diagnostic = "printf 'xxxx' >&2\n" if stream == "stderr" else ""
    fake_git.write_text(
        "#!/bin/sh\n"
        "case \"$*\" in\n"
        "  *--show-object-format=storage*)\n"
        f"    {diagnostic}"
        "    printf 'sha1\\n'\n"
        "    exit 0\n"
        "    ;;\n"
        "esac\n"
        "exit 1\n",
        encoding="utf-8",
    )
    fake_git.chmod(0o755)
    source_id = f"source:bounded-{stream}"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="a" * 40,
    )
    manifest = HostEvidenceManifest(
        manifest_id=f"manifest:bounded-{stream}",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )
    monkeypatch.setattr(evidence_module, "_GIT_EXECUTABLE", str(fake_git))
    monkeypatch.setattr(evidence_module, limit_name, 3, raising=False)

    snapshot = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.WORK_BUDGET_EXHAUSTED
    # One additional byte is consumed to distinguish exact-cap EOF from overflow.
    assert dict(snapshot.capture_work_usage)[usage_name] == 4
    assert usage_name in snapshot.capture_work_exhausted_dimensions


def test_absolute_capture_deadline_exhaustion_is_receipted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    fake_git = tmp_path / "fake-git"
    fake_git.write_text("#!/bin/sh\nsleep 60\n", encoding="utf-8")
    fake_git.chmod(0o755)
    source_id = "source:deadline"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="a" * 40,
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:deadline",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )
    monkeypatch.setattr(evidence_module, "_GIT_EXECUTABLE", str(fake_git))
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_CAPTURE_ELAPSED_NS", 5_000_000)

    started = time.monotonic()
    snapshot = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.WORK_BUDGET_EXHAUSTED
    assert "elapsed_ns" in snapshot.capture_work_exhausted_dimensions
    assert time.monotonic() - started < 2


@pytest.mark.parametrize("delayed_phase", ("root_setup", "local_read"))
def test_capture_deadline_is_checked_around_root_and_local_io(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    delayed_phase: str,
) -> None:
    payload = b"deadline-local"
    (tmp_path / "source.bin").write_bytes(payload)
    ref = f"orion:source.bin@{hashlib.sha256(payload).hexdigest()}"
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_CAPTURE_ELAPSED_NS", 5_000_000)
    if delayed_phase == "root_setup":
        real_open_roots = evidence_module._open_roots

        def delayed_open_roots(roots: object) -> object:
            time.sleep(0.02)
            return real_open_roots(roots)

        monkeypatch.setattr(evidence_module, "_open_roots", delayed_open_roots)
    else:
        real_read = evidence_module._read_open_descriptor

        def delayed_read(fd: int, limit: int) -> tuple[bytes, bool]:
            time.sleep(0.02)
            return real_read(fd, limit)

        monkeypatch.setattr(evidence_module, "_read_open_descriptor", delayed_read)

    snapshot = capture_host_evidence_snapshot(
        (ref,),
        roots={"orion": tmp_path},
        manifest=_manifest_for_ref(ref),
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.WORK_BUDGET_EXHAUSTED
    assert "elapsed_ns" in snapshot.capture_work_exhausted_dimensions
    assert not snapshot.records[0].content_available


def test_root_setup_deadline_is_receipted_for_an_empty_capture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = HostEvidenceManifest(
        manifest_id="manifest:empty-deadline",
        required_obligation_ids=(),
        sources=(),
        bindings=(),
    )
    real_open_roots = evidence_module._open_roots

    def delayed_open_roots(roots: object) -> object:
        time.sleep(0.02)
        return real_open_roots(roots)

    monkeypatch.setattr(evidence_module, "_open_roots", delayed_open_roots)
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_CAPTURE_ELAPSED_NS", 5_000_000)

    snapshot = capture_host_evidence_snapshot(
        (),
        roots={"orion": tmp_path},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records == ()
    assert "elapsed_ns" in snapshot.capture_work_exhausted_dimensions


def test_local_io_error_after_deadline_is_censored(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = b"deadline-error"
    (tmp_path / "source.bin").write_bytes(payload)
    ref = f"orion:source.bin@{hashlib.sha256(payload).hexdigest()}"

    def delayed_error(fd: int, limit: int) -> tuple[bytes, bool]:
        del fd, limit
        time.sleep(0.02)
        raise OSError(errno.EIO, "delayed read failure")

    monkeypatch.setattr(evidence_module, "_read_open_descriptor", delayed_error)
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_CAPTURE_ELAPSED_NS", 5_000_000)
    snapshot = capture_host_evidence_snapshot(
        (ref,),
        roots={"orion": tmp_path},
        manifest=_manifest_for_ref(ref),
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.WORK_BUDGET_EXHAUSTED
    assert "elapsed_ns" in snapshot.capture_work_exhausted_dimensions
    assert not snapshot.records[0].content_available


def test_git_path_and_tree_entry_work_budgets_are_shared_and_typed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    (repo / "a.bin").write_bytes(b"a")
    (repo / "z.bin").write_bytes(b"z")
    _git(repo, "add", "a.bin", "z.bin")
    _git(repo, "commit", "-qm", "bounded tree work")
    oid = _git(repo, "rev-parse", "HEAD")

    def capture(path: str) -> HostEvidenceSnapshot:
        source = HostEvidenceSource(
            source_id=f"source:{path}",
            backend_type="git",
            root_scheme="repo",
            relative_path=path,
            git_revision=oid,
        )
        manifest = HostEvidenceManifest(
            manifest_id=f"manifest:{path}",
            required_obligation_ids=("obligation:source-content",),
            sources=(source,),
            bindings=(_binding(evidence_ref=source.source_id),),
        )
        return capture_host_evidence_snapshot(
            (source.source_id,),
            roots={"repo": repo},
            manifest=manifest,
            captured_at_authority_revision="a" * 64,
            captured_at_support_revision="b" * 64,
        )

    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_CAPTURE_PATH_COMPONENTS", 0)
    assert capture("z.bin").records[0].status is EvidenceStatus.WORK_BUDGET_EXHAUSTED

    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_CAPTURE_PATH_COMPONENTS", 1)
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_CAPTURE_TREE_ENTRIES", 1)
    assert capture("z.bin").records[0].status is EvidenceStatus.WORK_BUDGET_EXHAUSTED

    monkeypatch.setattr(
        evidence_module, "MAX_EVIDENCE_CAPTURE_TREE_ENTRIES", 100_000
    )
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_CAPTURE_GIT_OBJECT_BYTES", 0)
    assert capture("z.bin").records[0].status is EvidenceStatus.WORK_BUDGET_EXHAUSTED


def test_git_capture_reads_the_opened_root_when_path_is_swapped_and_restored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registered = tmp_path / "registered"
    substitute = tmp_path / "substitute"
    displaced = tmp_path / "displaced"
    for repo, payload in ((registered, b"BENIGN"), (substitute, b"MALICIOUS")):
        repo.mkdir()
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "orion@example.invalid")
        _git(repo, "config", "user.name", "ORION test")
        (repo / "source.bin").write_bytes(payload)
        _git(repo, "add", "source.bin")
        _git(repo, "commit", "-qm", payload.decode("ascii"))
        _git(repo, "branch", "frozen")
    source = HostEvidenceSource(
        source_id="source:descriptor-bound-git-root",
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="refs/heads/frozen",
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:descriptor-bound-git-root",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source.source_id),),
    )
    real_match = evidence_module._root_descriptor_matches
    swapped = False

    def swap_after_precheck(opened_root: object) -> bool:
        nonlocal swapped
        if not swapped:
            matched = real_match(opened_root)
            registered.rename(displaced)
            substitute.rename(registered)
            swapped = True
            return matched
        registered.rename(substitute)
        displaced.rename(registered)
        swapped = False
        return real_match(opened_root)

    monkeypatch.setattr(
        evidence_module, "_root_descriptor_matches", swap_after_precheck
    )

    try:
        snapshot = capture_host_evidence_snapshot(
            (source.source_id,),
            roots={"repo": registered},
            manifest=manifest,
            captured_at_authority_revision="a" * 64,
            captured_at_support_revision="b" * 64,
        )
    finally:
        if swapped:
            registered.rename(substitute)
            displaced.rename(registered)

    assert snapshot.records[0].status is EvidenceStatus.RESOLVED
    assert snapshot.records[0].content_bytes == b"BENIGN"
    assert (registered / "source.bin").read_bytes() == b"BENIGN"


def test_registered_root_symlink_is_not_followed(tmp_path: Path) -> None:
    real_root = tmp_path / "real"
    real_root.mkdir()
    payload = b"must not follow configured root alias"
    (real_root / "source.bin").write_bytes(payload)
    linked_root = tmp_path / "linked"
    linked_root.symlink_to(real_root, target_is_directory=True)
    ref = f"orion:source.bin@{hashlib.sha256(payload).hexdigest()}"

    snapshot = capture_host_evidence_snapshot(
        (ref,),
        roots={"orion": linked_root},
        manifest=_manifest_for_ref(ref),
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.SYMLINK_DISALLOWED
    assert not snapshot.records[0].content_available
    assert snapshot.cannot_check


def test_git_registered_root_symlink_is_not_reclassified_as_a_race(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    (repo / "source.bin").write_bytes(b"git root")
    _git(repo, "add", "source.bin")
    _git(repo, "commit", "-qm", "git root")
    _git(repo, "branch", "frozen")
    linked_repo = tmp_path / "linked-repo"
    linked_repo.symlink_to(repo, target_is_directory=True)
    source_id = "source:linked-git-root"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="refs/heads/frozen",
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:linked-git-root",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    record = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": linked_repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]

    assert record.status is EvidenceStatus.SYMLINK_DISALLOWED


@pytest.mark.parametrize("git_entry_kind", ("gitfile", "symlink", "fifo"))
def test_protected_git_refuses_non_directory_administrative_entries(
    tmp_path: Path,
    git_entry_kind: str,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    git_entry = root / ".git"
    if git_entry_kind == "gitfile":
        git_entry.write_text("gitdir: ../elsewhere\n", encoding="utf-8")
    elif git_entry_kind == "symlink":
        target = tmp_path / "elsewhere"
        target.mkdir()
        git_entry.symlink_to(target, target_is_directory=True)
    else:
        os.mkfifo(git_entry)
    source_id = f"source:unsafe-{git_entry_kind}"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="a" * 40,
    )
    manifest = HostEvidenceManifest(
        manifest_id=f"manifest:unsafe-{git_entry_kind}",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    record = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": root},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]

    assert record.status is EvidenceStatus.UNSUPPORTED_GIT_LAYOUT
    assert not record.content_available


def test_missing_no_follow_capability_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = b"capability gated"
    (tmp_path / "source.bin").write_bytes(payload)
    ref = f"orion:source.bin@{hashlib.sha256(payload).hexdigest()}"
    monkeypatch.setattr(evidence_module.os, "O_NOFOLLOW", 0)
    monkeypatch.setattr(evidence_module.os, "O_NOFOLLOW_ANY", 0, raising=False)

    snapshot = capture_host_evidence_snapshot(
        (ref,),
        roots={"orion": tmp_path},
        manifest=_manifest_for_ref(ref),
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.CAPABILITY_UNAVAILABLE
    assert not snapshot.records[0].content_available
    assert snapshot.cannot_check


def test_fifo_is_rejected_before_open_or_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fifo = tmp_path / "pipe"
    fifo_digest = "0" * 64
    evidence_module.os.mkfifo(fifo)
    ref = f"orion:pipe@{fifo_digest}"
    real_open = evidence_module.os.open
    final_opens = 0

    def observing_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
        nonlocal final_opens
        if path == "pipe":
            final_opens += 1
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(evidence_module.os, "open", observing_open)
    snapshot = capture_host_evidence_snapshot(
        (ref,),
        roots={"orion": tmp_path},
        manifest=_manifest_for_ref(ref),
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.NON_REGULAR_FILE
    assert final_opens == 0
    assert not snapshot.records[0].content_available


@pytest.mark.parametrize("relative_path", ("linked/source.bin", "source-link.bin"))
def test_parent_and_final_symlinks_are_rejected(
    tmp_path: Path, relative_path: str
) -> None:
    real_dir = tmp_path / "real"
    real_dir.mkdir()
    payload = b"symlink target"
    target = real_dir / "source.bin"
    target.write_bytes(payload)
    (tmp_path / "linked").symlink_to(real_dir, target_is_directory=True)
    (tmp_path / "source-link.bin").symlink_to(target)
    ref = f"orion:{relative_path}@{hashlib.sha256(payload).hexdigest()}"

    snapshot = capture_host_evidence_snapshot(
        (ref,),
        roots={"orion": tmp_path},
        manifest=_manifest_for_ref(ref),
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.SYMLINK_DISALLOWED
    assert not snapshot.records[0].content_available


def test_final_component_symlink_swap_between_stat_and_open_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = b"registered bytes"
    substitute = b"substitute bytes"
    source_path = tmp_path / "source.bin"
    substitute_path = tmp_path / "substitute.bin"
    displaced_path = tmp_path / "displaced.bin"
    source_path.write_bytes(original)
    substitute_path.write_bytes(substitute)
    ref = f"orion:source.bin@{hashlib.sha256(original).hexdigest()}"
    real_stat = evidence_module.os.stat
    swapped = False

    def swap_after_nofollow_stat(
        path: object,
        *args: object,
        **kwargs: object,
    ) -> os.stat_result:
        nonlocal swapped
        result = real_stat(path, *args, **kwargs)
        if (
            not swapped
            and path == "source.bin"
            and kwargs.get("dir_fd") is not None
            and kwargs.get("follow_symlinks") is False
        ):
            source_path.rename(displaced_path)
            source_path.symlink_to(substitute_path)
            swapped = True
        return result

    monkeypatch.setattr(evidence_module.os, "stat", swap_after_nofollow_stat)
    try:
        record = capture_host_evidence_snapshot(
            (ref,),
            roots={"orion": tmp_path},
            manifest=_manifest_for_ref(ref),
            captured_at_authority_revision="a" * 64,
            captured_at_support_revision="b" * 64,
        ).records[0]
    finally:
        if swapped:
            source_path.unlink()
            displaced_path.rename(source_path)

    assert record.status in {
        EvidenceStatus.SYMLINK_DISALLOWED,
        EvidenceStatus.CHANGED_DURING_CAPTURE,
    }
    assert not record.content_available


def test_invalid_utf8_octets_remain_distinct_exact_bytes(tmp_path: Path) -> None:
    first_bytes = b"\xff"
    second_bytes = b"\xfe"
    (tmp_path / "first.bin").write_bytes(first_bytes)
    (tmp_path / "second.bin").write_bytes(second_bytes)
    first_ref = f"orion:first.bin@{hashlib.sha256(first_bytes).hexdigest()}"
    second_ref = f"orion:second.bin@{hashlib.sha256(second_bytes).hexdigest()}"
    manifest = HostEvidenceManifest(
        manifest_id="manifest:binary",
        required_obligation_ids=("obligation:first", "obligation:second"),
        sources=(_source_from_ref(first_ref), _source_from_ref(second_ref)),
        bindings=(
            _binding(
                binding_id="binding:first",
                evidence_ref=first_ref,
                obligation_id="obligation:first",
            ),
            _binding(
                binding_id="binding:second",
                evidence_ref=second_ref,
                obligation_id="obligation:second",
            ),
        ),
    )

    snapshot = capture_host_evidence_snapshot(
        (first_ref, second_ref),
        roots={"orion": tmp_path},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert [record.content_bytes for record in snapshot.records] == [
        first_bytes,
        second_bytes,
    ]
    assert all(record.utf8_text is None for record in snapshot.records)
    assert snapshot.records[0].content_hash != snapshot.records[1].content_hash


def test_empty_file_is_available_resolved_binary_evidence(tmp_path: Path) -> None:
    empty = b""
    (tmp_path / "empty.bin").write_bytes(empty)
    ref = f"orion:empty.bin@{hashlib.sha256(empty).hexdigest()}"

    snapshot = capture_host_evidence_snapshot(
        (ref,),
        roots={"orion": tmp_path},
        manifest=_manifest_for_ref(ref),
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )
    (record,) = snapshot.records

    assert record.status is EvidenceStatus.RESOLVED
    assert record.content_available
    assert record.content_bytes == b""
    assert record.byte_length == 0
    assert record.utf8_text == ""


@pytest.mark.parametrize(
    "invalid_digest",
    ("a" * 8, "A" * 64, "g" * 64, "a" * 65),
)
def test_file_source_registration_requires_full_lowercase_sha256(
    invalid_digest: str,
) -> None:
    with pytest.raises(ValueError, match="lowercase SHA-256"):
        HostEvidenceSource(
            source_id="source:invalid-digest",
            backend_type="file",
            root_scheme="orion",
            relative_path="source.bin",
            expected_content_sha256=invalid_digest,
        )


def test_unmapped_request_and_host_required_missing_source_are_preserved(
    tmp_path: Path,
) -> None:
    missing_id = "source:host-required-missing"
    unmapped_id = "source:candidate-unmapped"
    missing_source = HostEvidenceSource(
        source_id=missing_id,
        backend_type="file",
        root_scheme="orion",
        relative_path="missing.bin",
        expected_content_sha256="a" * 64,
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:missing",
        required_obligation_ids=("obligation:source-content",),
        sources=(missing_source,),
        bindings=(_binding(evidence_ref=missing_id),),
    )

    snapshot = capture_host_evidence_snapshot(
        (unmapped_id,),
        roots={"orion": tmp_path},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert {record.ref: record.status for record in snapshot.records} == {
        unmapped_id: EvidenceStatus.ROLE_UNMAPPED,
        missing_id: EvidenceStatus.MISSING_ARTIFACT,
    }
    assert snapshot.unresolved_obligation_ids == ("obligation:source-content",)
    assert snapshot.cannot_check


def test_snapshot_identity_binds_root_manifest_authority_and_support(
    tmp_path: Path,
) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    payload = b"same bytes"
    (first_root / "source.bin").write_bytes(payload)
    (second_root / "source.bin").write_bytes(payload)
    ref = f"orion:source.bin@{hashlib.sha256(payload).hexdigest()}"
    source = _source_from_ref(ref)
    first_manifest = _manifest_for_ref(ref)
    changed_manifest = HostEvidenceManifest(
        manifest_id=first_manifest.manifest_id,
        required_obligation_ids=first_manifest.required_obligation_ids,
        sources=(source,),
        bindings=(_binding(evidence_ref=ref, role_id="role:changed"),),
    )

    def capture(
        root: Path,
        manifest: HostEvidenceManifest,
        authority: str = "a" * 64,
        support: str = "b" * 64,
    ) -> object:
        return capture_host_evidence_snapshot(
            (ref,),
            roots={"orion": root},
            manifest=manifest,
            captured_at_authority_revision=authority,
            captured_at_support_revision=support,
        )

    snapshots = (
        capture(first_root, first_manifest),
        capture(second_root, first_manifest),
        capture(first_root, changed_manifest),
        capture(first_root, first_manifest, authority="c" * 64),
        capture(first_root, first_manifest, support="d" * 64),
    )

    assert len({snapshot.snapshot_id for snapshot in snapshots}) == len(snapshots)


def test_root_configuration_binds_git_helper_executable_and_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = b"helper-bound bytes"
    (tmp_path / "source.bin").write_bytes(payload)
    ref = f"orion:source.bin@{hashlib.sha256(payload).hexdigest()}"

    def capture() -> HostEvidenceSnapshot:
        return capture_host_evidence_snapshot(
            (ref,),
            roots={"orion": tmp_path},
            manifest=_manifest_for_ref(ref),
            captured_at_authority_revision="a" * 64,
            captured_at_support_revision="b" * 64,
        )

    baseline = capture()
    monkeypatch.setattr(
        evidence_module,
        "_GIT_FD_HELPER_EXECUTABLE",
        evidence_module._GIT_FD_HELPER_EXECUTABLE + "-changed",
    )
    executable_changed = capture()
    monkeypatch.setattr(
        evidence_module,
        "_GIT_FD_EXEC_HELPER",
        evidence_module._GIT_FD_EXEC_HELPER + "\n# changed",
    )
    source_changed = capture()

    assert len(
        {
            baseline.root_configuration_hash,
            executable_changed.root_configuration_hash,
            source_changed.root_configuration_hash,
        }
    ) == 3


def test_root_configuration_binds_git_helper_executable_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = b"helper-artifact-bound bytes"
    (tmp_path / "source.bin").write_bytes(payload)
    ref = f"orion:source.bin@{hashlib.sha256(payload).hexdigest()}"
    helper = tmp_path / "helper"
    helper.write_bytes(b"#!/bin/sh\nexit 0\n")
    helper.chmod(0o755)
    monkeypatch.setattr(evidence_module, "_GIT_FD_HELPER_EXECUTABLE", str(helper))

    def capture() -> HostEvidenceSnapshot:
        return capture_host_evidence_snapshot(
            (ref,),
            roots={"orion": tmp_path},
            manifest=_manifest_for_ref(ref),
            captured_at_authority_revision="a" * 64,
            captured_at_support_revision="b" * 64,
        )

    baseline = capture()
    original_stat = helper.stat()
    helper.write_bytes(b"#!/bin/sh\nexit 1\n")
    os.utime(
        helper,
        ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns),
    )
    changed = capture()

    assert baseline.root_configuration_hash != changed.root_configuration_hash


def test_duplicate_requested_source_ids_are_rejected_before_capture(
    tmp_path: Path,
) -> None:
    payload = b"duplicate"
    (tmp_path / "source.bin").write_bytes(payload)
    ref = f"orion:source.bin@{hashlib.sha256(payload).hexdigest()}"

    with pytest.raises(ValueError, match="unique"):
        capture_host_evidence_snapshot(
            (ref, ref),
            roots={"orion": tmp_path},
            manifest=_manifest_for_ref(ref),
            captured_at_authority_revision="a" * 64,
            captured_at_support_revision="b" * 64,
        )


def test_record_constructor_enforces_the_capture_byte_cap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = b"x"
    (tmp_path / "source.bin").write_bytes(original)
    ref = f"orion:source.bin@{hashlib.sha256(original).hexdigest()}"
    record = capture_host_evidence_snapshot(
        (ref,),
        roots={"orion": tmp_path},
        manifest=_manifest_for_ref(ref),
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]
    oversized = b"xy"
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_RECORD_BYTES", 1)

    with pytest.raises(ValueError, match="record byte cap"):
        replace(
            record,
            declared_digest=hashlib.sha256(oversized).hexdigest(),
            content_bytes=oversized,
            source_size=len(oversized),
        )


def test_snapshot_constructor_enforces_total_byte_cap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "a.bin").write_bytes(b"a")
    (tmp_path / "b.bin").write_bytes(b"b")
    first_ref = f"orion:a.bin@{hashlib.sha256(b'a').hexdigest()}"
    second_ref = f"orion:b.bin@{hashlib.sha256(b'b').hexdigest()}"
    manifest = HostEvidenceManifest(
        manifest_id="manifest:snapshot-cap",
        required_obligation_ids=("obligation:a", "obligation:b"),
        sources=(_source_from_ref(first_ref), _source_from_ref(second_ref)),
        bindings=(
            _binding(
                binding_id="binding:a",
                evidence_ref=first_ref,
                obligation_id="obligation:a",
            ),
            _binding(
                binding_id="binding:b",
                evidence_ref=second_ref,
                obligation_id="obligation:b",
            ),
        ),
    )
    snapshot = capture_host_evidence_snapshot(
        (first_ref, second_ref),
        roots={"orion": tmp_path},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_SNAPSHOT_BYTES", 1)

    with pytest.raises(ValueError, match="snapshot byte cap"):
        replace(snapshot)


def test_capture_marks_record_and_snapshot_overflow_without_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "a.bin").write_bytes(b"aaa")
    (tmp_path / "b.bin").write_bytes(b"bbb")
    first_ref = f"orion:a.bin@{hashlib.sha256(b'aaa').hexdigest()}"
    second_ref = f"orion:b.bin@{hashlib.sha256(b'bbb').hexdigest()}"
    manifest = HostEvidenceManifest(
        manifest_id="manifest:capture-caps",
        required_obligation_ids=("obligation:a", "obligation:b"),
        sources=(_source_from_ref(first_ref), _source_from_ref(second_ref)),
        bindings=(
            _binding(
                binding_id="binding:a",
                evidence_ref=first_ref,
                obligation_id="obligation:a",
            ),
            _binding(
                binding_id="binding:b",
                evidence_ref=second_ref,
                obligation_id="obligation:b",
            ),
        ),
    )
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_RECORD_BYTES", 3)
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_SNAPSHOT_BYTES", 5)

    snapshot = capture_host_evidence_snapshot(
        (first_ref, second_ref),
        roots={"orion": tmp_path},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.RESOLVED
    assert snapshot.records[0].content_bytes == b"aaa"
    assert snapshot.records[1].status is EvidenceStatus.TOO_LARGE
    assert not snapshot.records[1].content_available
    assert snapshot.records[1].content_bytes == b""


def test_snapshot_overflow_does_not_erase_later_failure_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "a.bin").write_bytes(b"aaa")
    (tmp_path / "b.bin").write_bytes(b"bbb")
    first_ref = f"orion:a.bin@{hashlib.sha256(b'aaa').hexdigest()}"
    second_ref = f"orion:b.bin@{hashlib.sha256(b'bbb').hexdigest()}"
    missing_ref = "orion:z-missing.bin@" + "c" * 64
    sources = tuple(
        _source_from_ref(ref) for ref in (first_ref, second_ref, missing_ref)
    )
    bindings = tuple(
        _binding(
            binding_id=f"binding:{index}",
            evidence_ref=source.source_id,
            obligation_id=f"obligation:{index}",
        )
        for index, source in enumerate(sources)
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:overflow-preserves-failure",
        required_obligation_ids=tuple(
            f"obligation:{index}" for index in range(len(sources))
        ),
        sources=sources,
        bindings=bindings,
    )
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_SNAPSHOT_BYTES", 5)

    snapshot = capture_host_evidence_snapshot(
        tuple(source.source_id for source in sources),
        roots={"orion": tmp_path},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert [record.status for record in snapshot.records] == [
        EvidenceStatus.RESOLVED,
        EvidenceStatus.TOO_LARGE,
        EvidenceStatus.MISSING_ARTIFACT,
    ]


def test_local_capture_work_budget_bounds_reads_and_preserves_later_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "a.bin").write_bytes(b"a")
    (tmp_path / "b.bin").write_bytes(b"b")
    refs = (
        f"orion:a.bin@{hashlib.sha256(b'a').hexdigest()}",
        f"orion:b.bin@{hashlib.sha256(b'b').hexdigest()}",
        "orion:z-missing.bin@" + "c" * 64,
    )
    sources = tuple(_source_from_ref(ref) for ref in refs)
    bindings = tuple(
        _binding(
            binding_id=f"binding:{index}",
            evidence_ref=source.source_id,
            obligation_id=f"obligation:{index}",
        )
        for index, source in enumerate(sources)
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:bounded-local-work",
        required_obligation_ids=tuple(
            f"obligation:{index}" for index in range(len(sources))
        ),
        sources=sources,
        bindings=bindings,
    )
    descriptor_reads = 0
    real_read = evidence_module._read_open_descriptor

    def count_read(fd: int, limit: int) -> tuple[bytes, bool]:
        nonlocal descriptor_reads
        descriptor_reads += 1
        return real_read(fd, limit)

    monkeypatch.setattr(evidence_module, "_read_open_descriptor", count_read)
    monkeypatch.setattr(
        evidence_module, "MAX_EVIDENCE_CAPTURE_LOCAL_BYTES", 1
    )

    snapshot = capture_host_evidence_snapshot(
        refs,
        roots={"orion": tmp_path},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert descriptor_reads == 1
    assert [record.status for record in snapshot.records] == [
        EvidenceStatus.RESOLVED,
        EvidenceStatus.WORK_BUDGET_EXHAUSTED,
        EvidenceStatus.MISSING_ARTIFACT,
    ]
    assert dict(snapshot.capture_work_usage)["local_bytes_read"] == 1
    assert snapshot.capture_work_exhausted_dimensions == ("local_bytes",)
    assert snapshot.cannot_check


def test_requested_source_count_is_bounded_before_root_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = "source:first-unmapped"
    second = "source:second-unmapped"
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_SOURCE_COUNT", 1)
    root_opens = 0
    real_open_roots = evidence_module._open_roots

    def observing_open_roots(*args: object, **kwargs: object) -> object:
        nonlocal root_opens
        root_opens += 1
        return real_open_roots(*args, **kwargs)

    monkeypatch.setattr(evidence_module, "_open_roots", observing_open_roots)

    with pytest.raises(ValueError, match="source count cap"):
        capture_host_evidence_snapshot(
            (first, second),
            roots={"orion": tmp_path},
            manifest=HostEvidenceManifest(
                manifest_id="manifest:empty",
                required_obligation_ids=(),
                sources=(),
                bindings=(),
            ),
            captured_at_authority_revision="a" * 64,
            captured_at_support_revision="b" * 64,
        )
    assert root_opens == 0


def test_git_shorthand_revision_is_rejected_as_ambiguous(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    (repo / "source.bin").write_bytes(b"git source")
    _git(repo, "add", "source.bin")
    _git(repo, "commit", "-qm", "source")
    source_id = "source:ambiguous-git-name"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="HEAD",
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:ambiguous-git-name",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    snapshot = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.MALFORMED_REF
    assert snapshot.cannot_check


def test_git_missing_revision_and_path_are_retained_typed_records(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    (repo / "present.bin").write_bytes(b"present")
    _git(repo, "add", "present.bin")
    _git(repo, "commit", "-qm", "present")
    _git(repo, "branch", "frozen")
    missing_path_id = "source:missing-git-path"
    missing_revision_id = "source:missing-git-revision"
    sources = (
        HostEvidenceSource(
            source_id=missing_path_id,
            backend_type="git",
            root_scheme="repo",
            relative_path="absent.bin",
            git_revision="refs/heads/frozen",
        ),
        HostEvidenceSource(
            source_id=missing_revision_id,
            backend_type="git",
            root_scheme="repo",
            relative_path="present.bin",
            git_revision="refs/heads/absent",
        ),
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:missing-git",
        required_obligation_ids=("obligation:path", "obligation:revision"),
        sources=sources,
        bindings=(
            _binding(
                binding_id="binding:path",
                evidence_ref=missing_path_id,
                obligation_id="obligation:path",
            ),
            _binding(
                binding_id="binding:revision",
                evidence_ref=missing_revision_id,
                obligation_id="obligation:revision",
            ),
        ),
    )

    snapshot = capture_host_evidence_snapshot(
        (missing_revision_id, missing_path_id),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert {record.ref: record.status for record in snapshot.records} == {
        missing_path_id: EvidenceStatus.PATH_NOT_IN_COMMIT,
        missing_revision_id: EvidenceStatus.COMMIT_NOT_FOUND,
    }
    assert snapshot.cannot_check


def test_git_symlink_tree_entry_is_not_regular_file_evidence(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    (repo / "target.bin").write_bytes(b"target")
    (repo / "linked.bin").symlink_to("target.bin")
    _git(repo, "add", "target.bin", "linked.bin")
    _git(repo, "commit", "-qm", "symlink")
    _git(repo, "branch", "frozen")
    source_id = "source:git-symlink"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="linked.bin",
        git_revision="refs/heads/frozen",
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:git-symlink",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    snapshot = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )
    (record,) = snapshot.records

    assert record.status is EvidenceStatus.NON_REGULAR_FILE
    assert record.source_tree_entry_mode == "120000"
    assert not record.content_available


def test_git_replacement_objects_are_disabled(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    original = b"original object"
    replacement = b"replacement object"
    (repo / "source.bin").write_bytes(original)
    _git(repo, "add", "source.bin")
    _git(repo, "commit", "-qm", "original")
    _git(repo, "branch", "frozen")
    original_oid = _git(repo, "rev-parse", "HEAD:source.bin")
    (repo / "replacement.bin").write_bytes(replacement)
    replacement_oid = _git(repo, "hash-object", "-w", "replacement.bin")
    _git(repo, "replace", original_oid, replacement_oid)
    source_id = "source:no-git-replacement"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="refs/heads/frozen",
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:no-git-replacement",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    snapshot = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )
    (record,) = snapshot.records

    assert record.status is EvidenceStatus.RESOLVED
    assert record.source_blob_oid == original_oid
    assert record.content_bytes == original
    assert record.content_hash == hashlib.sha256(original).hexdigest()


def test_protected_git_refuses_repository_object_alternates(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    _git(outside, "init", "-q")
    _git(outside, "config", "user.email", "orion@example.invalid")
    _git(outside, "config", "user.name", "ORION test")
    (outside / "source.bin").write_bytes(b"outside object")
    _git(outside, "add", "source.bin")
    _git(outside, "commit", "-qm", "outside object")
    outside_commit = _git(outside, "rev-parse", "HEAD")

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    alternates = repo / ".git" / "objects" / "info" / "alternates"
    alternates.parent.mkdir(parents=True, exist_ok=True)
    alternates.write_text(str(outside / ".git" / "objects") + "\n", encoding="utf-8")
    frozen_ref = repo / ".git" / "refs" / "heads" / "frozen"
    frozen_ref.parent.mkdir(parents=True, exist_ok=True)
    frozen_ref.write_text(outside_commit + "\n", encoding="ascii")
    source_id = "source:alternate-object"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="refs/heads/frozen",
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:alternate-object",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    record = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]

    assert record.status is EvidenceStatus.UNSUPPORTED_GIT_LAYOUT
    assert not record.content_available


def test_protected_git_refuses_commondir_indirection(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    (repo / "source.bin").write_bytes(b"common directory")
    _git(repo, "add", "source.bin")
    _git(repo, "commit", "-qm", "common directory")
    commit_oid = _git(repo, "rev-parse", "HEAD")
    (repo / ".git" / "commondir").write_text(".\n", encoding="ascii")
    source_id = "source:commondir"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision=commit_oid,
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:commondir",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    record = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]

    assert record.status is EvidenceStatus.UNSUPPORTED_GIT_LAYOUT
    assert not record.content_available


@pytest.mark.parametrize(
    "include_section",
    ("[include]", '[includeIf "gitdir:**/repo/**"]'),
)
def test_protected_git_refuses_local_config_includes(
    tmp_path: Path,
    include_section: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    (repo / "source.bin").write_bytes(b"included config")
    _git(repo, "add", "source.bin")
    _git(repo, "commit", "-qm", "included config")
    commit_oid = _git(repo, "rev-parse", "HEAD")
    included = tmp_path / "included.cfg"
    included.write_text("[core]\n\tbare = false\n", encoding="utf-8")
    with (repo / ".git" / "config").open("a", encoding="utf-8") as stream:
        stream.write(f"\n{include_section}\n\tpath = {included}\n")
    source_id = "source:config-include"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision=commit_oid,
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:config-include",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    record = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]

    assert record.status is EvidenceStatus.UNSUPPORTED_GIT_LAYOUT
    assert not record.content_available


def test_protected_git_explicitly_refuses_bare_repository_roots(tmp_path: Path) -> None:
    bare = tmp_path / "repo.git"
    _git(tmp_path, "init", "--bare", "-q", str(bare))
    source_id = "source:bare-repository"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="a" * 40,
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:bare-repository",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    record = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": bare},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]

    assert record.status is EvidenceStatus.UNSUPPORTED_GIT_LAYOUT
    assert not record.content_available


def test_protected_git_subprocess_output_is_byte_bounded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / ".git").mkdir()
    fake_git = tmp_path / "fake-git"
    fake_git.write_text(
        "#!/bin/sh\n"
        "head -c 131072 /dev/zero\n"
        "head -c 131072 /dev/zero >&2\n",
        encoding="utf-8",
    )
    fake_git.chmod(0o755)
    opened_root = evidence_module._open_root_without_symlinks("repo", root)
    assert opened_root.file_descriptor is not None
    monkeypatch.setattr(evidence_module, "_GIT_EXECUTABLE", str(fake_git))

    try:
        result = evidence_module._run_protected_git(
            opened_root,
            "probe",
            stdout_limit=32,
            stderr_limit=32,
            combined_limit=64,
        )
    finally:
        assert opened_root.file_descriptor is not None
        os.close(opened_root.file_descriptor)

    assert result.output_limited
    assert result.returncode is None
    assert len(result.stdout) <= 32
    assert len(result.stderr) <= 32
    assert result.note == "Git output exceeded the protected byte limit"


def test_protected_git_subprocess_drains_stdout_and_stderr_concurrently(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / ".git").mkdir()
    fake_git = tmp_path / "fake-git"
    fake_git.write_text(
        "#!/bin/sh\n"
        "head -c 131072 /dev/zero\n"
        "head -c 131072 /dev/zero >&2\n",
        encoding="utf-8",
    )
    fake_git.chmod(0o755)
    opened_root = evidence_module._open_root_without_symlinks("repo", root)
    assert opened_root.file_descriptor is not None
    monkeypatch.setattr(evidence_module, "_GIT_EXECUTABLE", str(fake_git))

    try:
        result = evidence_module._run_protected_git(
            opened_root,
            "probe",
            stdout_limit=140_000,
            stderr_limit=140_000,
            combined_limit=280_000,
        )
    finally:
        assert opened_root.file_descriptor is not None
        os.close(opened_root.file_descriptor)

    assert not result.output_limited
    assert result.returncode == 0
    assert len(result.stdout) == 131_072
    assert len(result.stderr) == 131_072


def test_protected_git_subprocess_timeout_is_typed_and_reaped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / ".git").mkdir()
    fake_git = tmp_path / "fake-git"
    fake_git.write_text("#!/bin/sh\nsleep 60\n", encoding="utf-8")
    fake_git.chmod(0o755)
    opened_root = evidence_module._open_root_without_symlinks("repo", root)
    assert opened_root.file_descriptor is not None
    monkeypatch.setattr(evidence_module, "_GIT_EXECUTABLE", str(fake_git))

    started = time.monotonic()
    try:
        result = evidence_module._run_protected_git(
            opened_root,
            "probe",
            timeout_seconds=0.05,
        )
    finally:
        assert opened_root.file_descriptor is not None
        os.close(opened_root.file_descriptor)

    assert result.timed_out
    assert result.returncode is None
    assert time.monotonic() - started < 2
    assert result.note == "Git command exceeded the protected wall-clock deadline"


@pytest.mark.parametrize("result_flag", ("timed_out", "stdout_limited"))
def test_git_resolution_does_not_misclassify_process_limits_as_missing_repository(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    result_flag: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    source_id = f"source:process-{result_flag}"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="a" * 40,
    )
    manifest = HostEvidenceManifest(
        manifest_id=f"manifest:process-{result_flag}",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )
    flags = {result_flag: True}

    def limited_git(*args: object, **kwargs: object) -> object:
        return evidence_module._GitCommandResult(
            None,
            b"",
            b"",
            True,
            "protected process limit",
            **flags,
        )

    monkeypatch.setattr(evidence_module, "_run_protected_git", limited_git)
    record = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]

    assert record.status is EvidenceStatus.UNREADABLE_ARTIFACT
    assert not record.content_available


def test_protected_git_executable_selection_ignores_ambient_path(
    tmp_path: Path,
) -> None:
    fake_git = tmp_path / "git"
    fake_git.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fake_git.chmod(0o755)
    environment = os.environ.copy()
    environment["PATH"] = str(tmp_path) + os.pathsep + environment.get("PATH", "")
    source_root = str(Path(evidence_module.__file__).parents[2])
    environment["PYTHONPATH"] = source_root + os.pathsep + environment.get(
        "PYTHONPATH", ""
    )

    completed = subprocess.run(  # noqa: S603 - current trusted Python interpreter
        [
            sys.executable,
            "-c",
            "import orion.kernel.evidence as e; print(e._GIT_EXECUTABLE or '')",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.stdout.strip() != str(fake_git)


def test_git_object_bytes_are_independently_checked_against_their_oid(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    original = b"object A"
    replacement = b"object B"
    (repo / "source.bin").write_bytes(original)
    _git(repo, "add", "source.bin")
    _git(repo, "commit", "-qm", "original")
    _git(repo, "branch", "frozen")
    original_oid = _git(repo, "rev-parse", "HEAD:source.bin")
    (repo / "replacement.bin").write_bytes(replacement)
    replacement_oid = _git(repo, "hash-object", "-w", "replacement.bin")
    object_root = repo / ".git" / "objects"
    original_object = object_root / original_oid[:2] / original_oid[2:]
    replacement_object = object_root / replacement_oid[:2] / replacement_oid[2:]
    original_object.chmod(0o644)
    shutil.copyfile(replacement_object, original_object)
    source_id = "source:corrupt-git-object"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="refs/heads/frozen",
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:corrupt-git-object",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    snapshot = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )
    (record,) = snapshot.records

    assert record.status is EvidenceStatus.GIT_OBJECT_MISMATCH
    assert record.content_bytes == replacement
    assert record.source_blob_oid == original_oid
    assert snapshot.cannot_check


def test_non_ascii_git_commit_header_is_retained_as_typed_mismatch(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    malformed = subprocess.run(  # noqa: S603 - fixed Git executable and test argv
        [
            "git",
            "-C",
            str(repo),
            "hash-object",
            "-w",
            "--stdin",
            "--literally",
            "-t",
            "commit",
        ],
        input=b"tree \xff\n\nmalformed commit",
        check=True,
        capture_output=True,
    ).stdout.decode("ascii").strip()
    source = HostEvidenceSource(
        source_id="source:malformed-commit",
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision=malformed,
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:malformed-commit",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source.source_id),),
    )

    snapshot = capture_host_evidence_snapshot(
        (source.source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.GIT_OBJECT_MISMATCH
    assert not snapshot.records[0].content_available
    assert snapshot.cannot_check


def test_git_commit_requires_the_tree_header_first(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    (repo / "source.bin").write_bytes(b"tree payload")
    _git(repo, "add", "source.bin")
    _git(repo, "commit", "-qm", "valid tree")
    tree_oid = _git(repo, "rev-parse", "HEAD^{tree}")
    malformed_commit = _git_literal_object(
        repo,
        "commit",
        f"author misplaced\ntree {tree_oid}\n\nmalformed".encode("ascii"),
    )
    source = HostEvidenceSource(
        source_id="source:tree-not-first",
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision=malformed_commit,
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:tree-not-first",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source.source_id),),
    )

    snapshot = capture_host_evidence_snapshot(
        (source.source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.GIT_OBJECT_MISMATCH
    assert snapshot.cannot_check


def test_git_tag_requires_ordered_object_type_and_tag_headers(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    (repo / "source.bin").write_bytes(b"tag target")
    _git(repo, "add", "source.bin")
    _git(repo, "commit", "-qm", "tag target")
    commit_oid = _git(repo, "rev-parse", "HEAD")
    malformed_tag = _git_literal_object(
        repo,
        "tag",
        (
            f"type commit\nobject {commit_oid}\ntag malformed-order"
            "\n\nmalformed"
        ).encode("ascii"),
    )
    source = HostEvidenceSource(
        source_id="source:malformed-tag-order",
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision=malformed_tag,
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:malformed-tag-order",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source.source_id),),
    )

    snapshot = capture_host_evidence_snapshot(
        (source.source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.GIT_OBJECT_MISMATCH
    assert snapshot.cannot_check


def test_git_tag_declared_target_type_must_match_target_object(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    (repo / "source.bin").write_bytes(b"tag target type")
    _git(repo, "add", "source.bin")
    _git(repo, "commit", "-qm", "tag target type")
    commit_oid = _git(repo, "rev-parse", "HEAD")
    inner_tag = _git_literal_object(
        repo,
        "tag",
        (
            f"object {commit_oid}\ntype commit\ntag inner\n\ninner"
        ).encode("ascii"),
    )
    outer_tag = _git_literal_object(
        repo,
        "tag",
        (
            f"object {inner_tag}\ntype commit\ntag false-edge\n\nouter"
        ).encode("ascii"),
    )
    source = HostEvidenceSource(
        source_id="source:tag-type-edge",
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision=outer_tag,
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:tag-type-edge",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source.source_id),),
    )

    record = capture_host_evidence_snapshot(
        (source.source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]

    assert record.status is EvidenceStatus.GIT_OBJECT_MISMATCH
    assert not record.content_available


def test_malformed_unrelated_tree_entry_blocks_target_resolution(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    payload = b"target bytes"
    (repo / "source.bin").write_bytes(payload)
    blob_oid = _git(repo, "hash-object", "-w", "source.bin")
    raw_oid = bytes.fromhex(blob_oid)
    malformed_tree = _git_literal_object(
        repo,
        "tree",
        b"100644 \x00"
        + raw_oid
        + b"100644 source.bin\x00"
        + raw_oid,
    )
    commit_oid = _git_literal_object(
        repo,
        "commit",
        f"tree {malformed_tree}\n\nmalformed tree".encode("ascii"),
    )
    source = HostEvidenceSource(
        source_id="source:malformed-unrelated-tree-entry",
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision=commit_oid,
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:malformed-unrelated-tree-entry",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source.source_id),),
    )

    snapshot = capture_host_evidence_snapshot(
        (source.source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.GIT_OBJECT_MISMATCH
    assert snapshot.cannot_check


@pytest.mark.parametrize(
    "malformed_step", ("format", "reference", "type", "size")
)
def test_non_ascii_git_control_output_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    malformed_step: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    source = HostEvidenceSource(
        source_id=f"source:malformed-{malformed_step}",
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision=(
            "refs/heads/frozen" if malformed_step == "reference" else "a" * 40
        ),
    )
    manifest = HostEvidenceManifest(
        manifest_id=f"manifest:malformed-{malformed_step}",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source.source_id),),
    )

    def malformed_git(
        opened_root: object, *arguments: str, **options: object
    ) -> evidence_module._GitCommandResult:
        del opened_root, options
        if arguments == ("rev-parse", "--show-object-format=storage"):
            stdout = b"\xff\n" if malformed_step == "format" else b"sha1\n"
        elif arguments[:1] == ("check-ref-format",):
            stdout = b""
        elif arguments[:2] == ("show-ref", "--verify"):
            stdout = b"\xff\n"
        elif arguments[:2] == ("cat-file", "-t"):
            stdout = b"\xff\n" if malformed_step == "type" else b"commit\n"
        elif arguments[:2] == ("cat-file", "-s"):
            stdout = b"\xff\n" if malformed_step == "size" else b"0\n"
        else:
            raise AssertionError(f"unexpected protected Git call: {arguments!r}")
        return evidence_module._GitCommandResult(0, stdout, b"", True)

    monkeypatch.setattr(evidence_module, "_run_protected_git", malformed_git)

    snapshot = capture_host_evidence_snapshot(
        (source.source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.UNREADABLE_ARTIFACT
    assert snapshot.cannot_check


def test_git_diagnostic_expansion_is_bounded_before_record_construction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    source = HostEvidenceSource(
        source_id="source:bounded-diagnostic",
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="a" * 40,
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:bounded-diagnostic",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source.source_id),),
    )

    def invalid_stderr(
        opened_root: object, *arguments: str, **options: object
    ) -> evidence_module._GitCommandResult:
        del opened_root, arguments, options
        return evidence_module._GitCommandResult(
            1,
            b"",
            b"\xff" * evidence_module.MAX_EVIDENCE_TEXT_BYTES,
            True,
        )

    monkeypatch.setattr(evidence_module, "_run_protected_git", invalid_stderr)

    snapshot = capture_host_evidence_snapshot(
        (source.source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    assert snapshot.records[0].status is EvidenceStatus.NOT_A_REPOSITORY
    assert len(snapshot.records[0].note.encode("utf-8")) <= 4_096
    assert snapshot.cannot_check


def test_annotated_tag_object_is_verified_before_peeling_to_commit(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    (repo / "source.bin").write_bytes(b"tagged")
    _git(repo, "add", "source.bin")
    _git(repo, "commit", "-qm", "tagged")
    _git(repo, "tag", "-am", "first tag", "frozen")
    first_tag_oid = _git(repo, "rev-parse", "refs/tags/frozen")
    _git(repo, "tag", "-am", "second tag", "replacement-tag")
    second_tag_oid = _git(repo, "rev-parse", "refs/tags/replacement-tag")
    object_root = repo / ".git" / "objects"
    first_object = object_root / first_tag_oid[:2] / first_tag_oid[2:]
    second_object = object_root / second_tag_oid[:2] / second_tag_oid[2:]
    first_object.chmod(0o644)
    shutil.copyfile(second_object, first_object)
    source_id = "source:corrupt-tag"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="refs/tags/frozen",
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:corrupt-tag",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    snapshot = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )
    (record,) = snapshot.records

    assert record.source_reference_oid == first_tag_oid
    assert record.status is EvidenceStatus.GIT_OBJECT_MISMATCH
    assert snapshot.cannot_check


def test_annotated_tag_and_peeled_commit_identities_remain_separate(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    payload = b"tagged evidence"
    (repo / "source.bin").write_bytes(payload)
    _git(repo, "add", "source.bin")
    _git(repo, "commit", "-qm", "tagged")
    commit_oid = _git(repo, "rev-parse", "HEAD")
    _git(repo, "tag", "-am", "evidence tag", "frozen")
    tag_oid = _git(repo, "rev-parse", "refs/tags/frozen")
    source_id = "source:annotated-tag"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="refs/tags/frozen",
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:annotated-tag",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    record = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]

    assert record.status is EvidenceStatus.RESOLVED
    assert record.source_reference_oid == tag_oid
    assert record.resolved_source_revision == commit_oid
    assert tag_oid != commit_oid
    assert record.content_bytes == payload


def test_sha256_git_storage_oids_are_typed_separately_from_content_digest(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    try:
        _git(repo, "init", "-q", "--object-format=sha256")
    except subprocess.CalledProcessError:
        pytest.skip("installed Git does not support SHA-256 repositories")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    payload = b"sha256 repository evidence"
    (repo / "source.bin").write_bytes(payload)
    _git(repo, "add", "source.bin")
    _git(repo, "commit", "-qm", "sha256")
    _git(repo, "branch", "frozen")
    source_id = "source:sha256-git"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="source.bin",
        git_revision="refs/heads/frozen",
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:sha256-git",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    record = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]

    assert record.status is EvidenceStatus.RESOLVED
    assert record.source_object_format == "sha256"
    assert len(record.source_reference_oid) == 64
    assert len(record.resolved_source_revision) == 64
    assert len(record.source_blob_oid) == 64
    assert record.content_hash == hashlib.sha256(payload).hexdigest()


def test_git_path_is_traversed_as_exact_tree_component_bytes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "orion@example.invalid")
    _git(repo, "config", "user.name", "ORION test")
    relative_path = "dir/[literal]*@name\t.bin"
    (repo / "dir").mkdir()
    payload = b"literal Git path"
    (repo / relative_path).write_bytes(payload)
    _git(repo, "add", "--", relative_path)
    _git(repo, "commit", "-qm", "literal path")
    _git(repo, "branch", "frozen")
    source_id = "source:literal-git-path"
    source = HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path=relative_path,
        git_revision="refs/heads/frozen",
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:literal-git-path",
        required_obligation_ids=("obligation:source-content",),
        sources=(source,),
        bindings=(_binding(evidence_ref=source_id),),
    )

    record = capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]

    assert record.status is EvidenceStatus.RESOLVED
    assert record.relative_path == relative_path
    assert record.content_bytes == payload


def test_capture_surface_has_no_appraisal_authorization_or_apply_seam() -> None:
    forbidden = {
        "appraisal",
        "authorize",
        "authorization",
        "apply",
        "evaluator",
        "policy",
        "signing_key",
        "trust_store",
    }

    assert forbidden.isdisjoint(
        inspect.signature(capture_host_evidence_snapshot).parameters
    )
    assert forbidden.isdisjoint(inspect.signature(HostEvidenceManifest).parameters)
    assert forbidden.isdisjoint(inspect.signature(HostEvidenceSource).parameters)


def test_snapshot_is_deterministic_under_requested_input_order_and_later_mutation(
    tmp_path: Path,
) -> None:
    first_bytes = b"first"
    second_bytes = b"second"
    first_path = tmp_path / "a.bin"
    second_path = tmp_path / "b.bin"
    first_path.write_bytes(first_bytes)
    second_path.write_bytes(second_bytes)
    first_ref = f"orion:a.bin@{hashlib.sha256(first_bytes).hexdigest()}"
    second_ref = f"orion:b.bin@{hashlib.sha256(second_bytes).hexdigest()}"
    manifest = HostEvidenceManifest(
        manifest_id="manifest:deterministic",
        required_obligation_ids=("obligation:a", "obligation:b"),
        sources=(_source_from_ref(second_ref), _source_from_ref(first_ref)),
        bindings=(
            _binding(
                binding_id="binding:b",
                evidence_ref=second_ref,
                obligation_id="obligation:b",
            ),
            _binding(
                binding_id="binding:a",
                evidence_ref=first_ref,
                obligation_id="obligation:a",
            ),
        ),
    )
    roots = {"orion": tmp_path}

    forward = capture_host_evidence_snapshot(
        (first_ref, second_ref),
        roots=roots,
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )
    reverse = capture_host_evidence_snapshot(
        (second_ref, first_ref),
        roots=roots,
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )
    original_hash = forward.snapshot_id
    roots["orion"] = tmp_path / "different"
    first_path.write_bytes(b"changed later")

    assert reverse.records == forward.records
    assert reverse.snapshot_id == original_hash
    assert snapshot_hash(forward) == original_hash


def test_host_source_text_fields_are_explicitly_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_TEXT_BYTES", 4)

    with pytest.raises(ValueError, match="text byte cap"):
        HostEvidenceSource(
            source_id="source:too-long",
            backend_type="file",
            root_scheme="root",
            relative_path="x",
            expected_content_sha256="a" * 64,
        )


def test_git_revision_manifest_obligation_and_record_text_are_bounded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = b"bounded metadata"
    (tmp_path / "p").write_bytes(payload)
    source = HostEvidenceSource(
        source_id="s",
        backend_type="file",
        root_scheme="r",
        relative_path="p",
        expected_content_sha256=hashlib.sha256(payload).hexdigest(),
        media_type="bytes",
    )
    binding = EvidenceRoleBinding(
        binding_id="b",
        evidence_ref="s",
        role_id="role",
        obligation_id="o",
    )
    manifest = HostEvidenceManifest(
        manifest_id="m",
        required_obligation_ids=("o",),
        sources=(source,),
        bindings=(binding,),
    )
    record = capture_host_evidence_snapshot(
        (source.source_id,),
        roots={"r": tmp_path},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_TEXT_BYTES", 64)
    over_limit = "x" * 65

    with pytest.raises(ValueError, match="git_revision.*text byte cap"):
        HostEvidenceSource(
            source_id="s",
            backend_type="git",
            root_scheme="r",
            relative_path="p",
            git_revision=over_limit,
            media_type="bytes",
        )
    with pytest.raises(ValueError, match="manifest_id.*text byte cap"):
        replace(manifest, manifest_id=over_limit)
    with pytest.raises(ValueError, match="required obligation id.*text byte cap"):
        replace(manifest, required_obligation_ids=(over_limit,))

    for field_name in (
        "declared_digest",
        "resolved_source_revision",
        "source_object_format",
        "source_reference_oid",
        "source_blob_oid",
        "source_tree_entry_mode",
        "note",
    ):
        with pytest.raises(ValueError, match=field_name):
            replace(record, **{field_name: over_limit})


def test_direct_collection_and_snapshot_union_counts_are_bounded_before_io(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "p").write_bytes(b"")
    source = HostEvidenceSource(
        source_id="host-required",
        backend_type="file",
        root_scheme="r",
        relative_path="p",
        expected_content_sha256=hashlib.sha256(b"").hexdigest(),
    )
    binding = _binding(
        binding_id="b",
        evidence_ref=source.source_id,
        obligation_id="o",
    )
    manifest = HostEvidenceManifest(
        manifest_id="m",
        required_obligation_ids=("o",),
        sources=(source,),
        bindings=(binding,),
    )
    baseline_snapshot = capture_host_evidence_snapshot(
        (source.source_id,),
        roots={"r": tmp_path},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_OBLIGATION_COUNT", 0)
    with pytest.raises(ValueError, match="obligation count cap"):
        replace(manifest)
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_OBLIGATION_COUNT", 1)
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_SNAPSHOT_RECORDS", 0)
    with pytest.raises(ValueError, match="snapshot record count cap"):
        replace(baseline_snapshot)

    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_SNAPSHOT_RECORDS", 1)
    root_opens = 0

    def observe_root_open(*args: object, **kwargs: object) -> tuple[object, ...]:
        nonlocal root_opens
        root_opens += 1
        return ()

    monkeypatch.setattr(evidence_module, "_open_roots", observe_root_open)
    with pytest.raises(ValueError, match="snapshot record count cap"):
        capture_host_evidence_snapshot(
            ("candidate-unmapped",),
            roots={"r": tmp_path},
            manifest=manifest,
            captured_at_authority_revision="a" * 64,
            captured_at_support_revision="b" * 64,
        )
    assert root_opens == 0


def test_snapshot_work_receipt_rejects_unknown_coordinates(tmp_path: Path) -> None:
    payload = b"work coordinates"
    (tmp_path / "source.bin").write_bytes(payload)
    ref = f"orion:source.bin@{hashlib.sha256(payload).hexdigest()}"
    snapshot = capture_host_evidence_snapshot(
        (ref,),
        roots={"orion": tmp_path},
        manifest=_manifest_for_ref(ref),
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    with pytest.raises(ValueError, match="usage coordinate"):
        replace(snapshot, capture_work_usage=(("unregistered", 0),))
    with pytest.raises(ValueError, match="exhausted coordinate"):
        replace(
            snapshot,
            capture_work_exhausted_dimensions=("unregistered",),
        )


def test_registered_root_count_and_text_are_bounded_before_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root_opens = 0

    def observe_root_open(*args: object, **kwargs: object) -> object:
        nonlocal root_opens
        root_opens += 1
        raise AssertionError("over-limit roots must fail before opening")

    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_ROOT_COUNT", 1)
    monkeypatch.setattr(
        evidence_module, "_open_root_without_symlinks", observe_root_open
    )
    with pytest.raises(ValueError, match="root count cap"):
        evidence_module._open_roots(
            {"first": tmp_path / "first", "second": tmp_path / "second"}
        )
    assert root_opens == 0

    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_ROOT_COUNT", 2)
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_TEXT_BYTES", 4)
    with pytest.raises(ValueError, match="root scheme.*text byte cap"):
        evidence_module._open_roots({"scheme": tmp_path})
    assert root_opens == 0

    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_ROOT_PATH_BYTES", 4)
    with pytest.raises(ValueError, match="root path byte cap"):
        evidence_module._open_roots({"root": tmp_path})
    assert root_opens == 0


def test_manifest_source_and_binding_counts_are_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_SOURCE_COUNT", 0)
    monkeypatch.setattr(evidence_module, "MAX_EVIDENCE_BINDING_COUNT", 0)

    with pytest.raises(ValueError, match="count cap"):
        _manifest()


def test_evidence_hash_layers_are_domain_separated_and_acyclic(
    tmp_path: Path,
) -> None:
    payload = b"hash layers"
    (tmp_path / "source.bin").write_bytes(payload)
    ref = f"orion:source.bin@{hashlib.sha256(payload).hexdigest()}"
    manifest = _manifest_for_ref(ref)
    snapshot = capture_host_evidence_snapshot(
        (ref,),
        roots={"orion": tmp_path},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )
    source = manifest.sources[0]
    record = snapshot.records[0]
    hashes = {
        record.content_hash,
        source.source_hash,
        manifest.manifest_hash,
        record.record_hash,
        snapshot.snapshot_id,
    }

    assert len(hashes) == 5
    assert "record_hash" not in evidence_module._host_record_payload(record)
    assert "snapshot_id" not in evidence_module._host_snapshot_payload(snapshot)
    assert snapshot_hash(snapshot) == snapshot.snapshot_id


def test_record_canonicalizes_role_binding_order(tmp_path: Path) -> None:
    payload = b"multi-role"
    (tmp_path / "source.bin").write_bytes(payload)
    ref = f"orion:source.bin@{hashlib.sha256(payload).hexdigest()}"
    first = _binding(
        binding_id="binding:a",
        evidence_ref=ref,
        role_id="role:a",
        obligation_id="obligation:a",
    )
    second = _binding(
        binding_id="binding:b",
        evidence_ref=ref,
        role_id="role:b",
        obligation_id="obligation:b",
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:multi-role",
        required_obligation_ids=("obligation:a", "obligation:b"),
        sources=(_source_from_ref(ref),),
        bindings=(first, second),
    )
    record = capture_host_evidence_snapshot(
        (ref,),
        roots={"orion": tmp_path},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    ).records[0]

    normalized = replace(record, role_bindings=tuple(reversed(record.role_bindings)))

    assert normalized.role_bindings == record.role_bindings
    assert normalized.record_hash == record.record_hash


def test_evidence_identity_golden_vectors_are_frozen() -> None:
    payload = b"golden evidence bytes\x00\xff"
    digest = hashlib.sha256(payload).hexdigest()
    source = HostEvidenceSource(
        source_id="source:golden",
        backend_type="file",
        root_scheme="orion",
        relative_path="golden.bin",
        expected_content_sha256=digest,
    )
    binding = EvidenceRoleBinding(
        binding_id="binding:golden",
        evidence_ref=source.source_id,
        role_id="role:primary",
        obligation_id="obligation:content",
    )
    manifest = HostEvidenceManifest(
        manifest_id="manifest:golden",
        required_obligation_ids=("obligation:content",),
        sources=(source,),
        bindings=(binding,),
    )
    record = HostEvidenceRecord(
        capture_ordinal=0,
        ref=source.source_id,
        status=EvidenceStatus.RESOLVED,
        backend_type="file",
        scheme="orion",
        relative_path="golden.bin",
        declared_digest=digest,
        resolved_source_revision="",
        source_object_format="",
        source_reference_oid="",
        source_blob_oid="",
        source_tree_entry_mode="",
        root_configuration_hash="c" * 64,
        role_bindings=(binding,),
        content_bytes=payload,
        content_available=True,
        source_device=1,
        source_inode=2,
        source_size=len(payload),
        source_mtime_ns=3,
        source_ctime_ns=4,
    )
    snapshot = HostEvidenceSnapshot(
        root_configuration_hash="c" * 64,
        manifest_hash=manifest.manifest_hash,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
        required_obligation_ids=manifest.required_obligation_ids,
        records=(record,),
    )

    assert source.source_hash == (
        "db9537209d53b23ba2d006e17476311eb055341d2e83d38719d8ede7c6219481"
    )
    assert manifest.manifest_hash == (
        "c96ce82e51663e04a93b16a758b308ec1ad6329262a5a9ce912bae1849f25da9"
    )
    assert record.content_hash == (
        "66e0874a55554cd3d53a1424f15833a26a23e8b7195bd1051ef51824c43bf510"
    )
    assert record.record_hash == (
        "1d6e3946dbe41c008e7894b2a07289dd0c2dbb75bbe1656c9f4cf1331d89942d"
    )
    assert snapshot.snapshot_id == (
        "3bd08c796656a448a6dcd412b64f7cc192e7dc7217d8d02217c2d99da3d30af4"
    )


def test_protected_evidence_api_is_exported_by_the_kernel_package() -> None:
    expected = {
        "EvidenceRoleBinding",
        "HostEvidenceSource",
        "HostEvidenceManifest",
        "HostEvidenceRecord",
        "HostEvidenceSnapshot",
        "capture_host_evidence_snapshot",
        "snapshot_hash",
    }

    assert expected.issubset(kernel.__all__)
    assert all(hasattr(kernel, name) for name in expected)
