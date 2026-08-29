from __future__ import annotations

import errno
import os
import stat
import subprocess
from dataclasses import asdict, replace
from pathlib import Path

import pytest

import orion.kernel.evidence as evidence_module


def _work_vector(**overrides: int) -> evidence_module.EvidenceWorkVector:
    values = {name: 0 for name in evidence_module.EVIDENCE_WORK_DIMENSIONS}
    values.update(overrides)
    return evidence_module.EvidenceWorkVector(
        tuple(values[name] for name in evidence_module.EVIDENCE_WORK_DIMENSIONS)
    )


def _work_contract(
    *,
    descriptor_operation_attempts: int,
    wall_time_budget_ns: int = 5_000_000_000,
) -> evidence_module.HostEvidenceWorkContract:
    default = evidence_module.DEFAULT_HOST_EVIDENCE_WORK_CONTRACT
    limits = default.limits.as_dict()
    limits["descriptor_operation_attempts"] = descriptor_operation_attempts
    return evidence_module.HostEvidenceWorkContract(
        limits=_work_vector(**limits),
        wall_time_budget_ns=wall_time_budget_ns,
        per_record_retained_limit=default.per_record_retained_limit,
        git_call_timeout_ns=min(
            default.git_call_timeout_ns,
            wall_time_budget_ns,
        ),
        max_read_chunk_bytes=default.max_read_chunk_bytes,
    )


def _deadline_exhaustion(ref: str) -> evidence_module.EvidenceWorkExhaustion:
    zero = evidence_module.EvidenceWorkVector.zero()
    return evidence_module.EvidenceWorkExhaustion(
        kind=evidence_module.EvidenceWorkExhaustionKind.DEADLINE,
        stage="test.post-command-root-observation",
        ref=ref,
        ordinal=0,
        dimensions=("wall_time",),
        requested=zero,
        remaining_before=zero,
        usage_before=zero,
        operation_index=0,
    )


def _open_git_root(root: Path) -> evidence_module._OpenedRoot:
    root.mkdir()
    (root / ".git").mkdir()
    opened = evidence_module._open_root_without_symlinks("repo", root)
    assert opened.file_descriptor is not None
    assert opened.git_directory_fd is not None
    return opened


def _close_opened_root(opened: evidence_module._OpenedRoot) -> None:
    if opened.git_directory_fd is not None:
        os.close(opened.git_directory_fd)
    if opened.file_descriptor is not None:
        os.close(opened.file_descriptor)


@pytest.mark.parametrize(
    ("component", "expected_kind"),
    (("HEAD", "directory"), ("objects", "file"), ("refs", "file")),
)
def test_bare_component_constructor_rejects_wrong_expected_kind_for_coordinate(
    component: str,
    expected_kind: str,
) -> None:
    observed_mode = (
        stat.S_IFDIR | 0o755
        if expected_kind == "directory"
        else stat.S_IFREG | 0o644
    )

    with pytest.raises(ValueError, match="expected kind"):
        evidence_module._BareRepositoryComponentObservation(
            component,
            expected_kind,
            "EXPECTED_KIND",
            observed_mode=observed_mode,
        )


@pytest.mark.parametrize(
    ("disposition", "observed_mode"),
    (
        ("EXPECTED_KIND", stat.S_IFDIR | 0o755),
        ("WRONG_KIND", stat.S_IFREG | 0o644),
    ),
)
def test_bare_component_constructor_checks_mode_against_disposition(
    disposition: str,
    observed_mode: int,
) -> None:
    with pytest.raises(ValueError, match="observed kind"):
        evidence_module._BareRepositoryComponentObservation(
            "HEAD",
            "file",
            disposition,
            observed_mode=observed_mode,
        )


def test_bare_false_constructor_rejects_unknown_prefix_before_negative() -> None:
    unknown_head = evidence_module._BareRepositoryComponentObservation(
        "HEAD",
        "file",
        "MECHANISM_CENSORED",
        mechanism_errno=errno.EIO,
    )
    absent_objects = evidence_module._BareRepositoryComponentObservation(
        "objects",
        "directory",
        "ABSENT",
    )

    with pytest.raises(ValueError, match="prefix"):
        evidence_module._BareRepositoryObservation(
            False,
            evidence_module.EvidenceStatus.RESOLVED,
            (unknown_head, absent_objects),
        )


def test_bare_mechanism_constructor_requires_matching_component_errno() -> None:
    censored_head = evidence_module._BareRepositoryComponentObservation(
        "HEAD",
        "file",
        "MECHANISM_CENSORED",
        mechanism_errno=errno.EIO,
    )

    with pytest.raises(ValueError, match="errno"):
        evidence_module._BareRepositoryObservation(
            None,
            evidence_module.EvidenceStatus.CANNOT_CHECK_MECHANISM,
            (censored_head,),
            mechanism_limitation=(
                evidence_module.EvidenceMechanismLimitationKind.FILESYSTEM_IO
            ),
            mechanism_errno=errno.EBADF,
        )


def test_bare_component_constructor_treats_enoent_as_absence_not_censorship() -> None:
    with pytest.raises(ValueError, match="errno|absen"):
        evidence_module._BareRepositoryComponentObservation(
            "HEAD",
            "file",
            "MECHANISM_CENSORED",
            mechanism_errno=errno.ENOENT,
        )


@pytest.mark.parametrize(
    ("limitation", "error_number"),
    (
        (
            evidence_module.EvidenceMechanismLimitationKind.ACCESS_POLICY,
            errno.EIO,
        ),
        (
            evidence_module.EvidenceMechanismLimitationKind.DESCRIPTOR_LIMIT,
            errno.EACCES,
        ),
    ),
)
def test_root_observation_constructor_rejects_incompatible_errno_class(
    limitation: evidence_module.EvidenceMechanismLimitationKind,
    error_number: int,
) -> None:
    with pytest.raises(ValueError, match="errno"):
        evidence_module._RootDescriptorObservation(
            None,
            evidence_module.EvidenceStatus.CANNOT_CHECK_MECHANISM,
            mechanism_limitation=limitation,
            mechanism_errno=error_number,
        )


@pytest.mark.parametrize(
    ("limitation", "error_number"),
    (
        (
            evidence_module.EvidenceMechanismLimitationKind.FILESYSTEM_IO,
            errno.EACCES,
        ),
        (
            evidence_module.EvidenceMechanismLimitationKind.FILESYSTEM_IO,
            errno.EMFILE,
        ),
        (
            evidence_module.EvidenceMechanismLimitationKind.PROCESS_TIMEOUT,
            errno.EIO,
        ),
    ),
)
def test_root_observation_constructor_closes_limitation_errno_matrix(
    limitation: evidence_module.EvidenceMechanismLimitationKind,
    error_number: int,
) -> None:
    with pytest.raises(ValueError, match="limitation|errno"):
        evidence_module._RootDescriptorObservation(
            None,
            evidence_module.EvidenceStatus.CANNOT_CHECK_MECHANISM,
            mechanism_limitation=limitation,
            mechanism_errno=error_number,
        )


@pytest.mark.parametrize(
    "identity_overrides",
    (
        {"configured_device": 1},
        {"configured_inode": 2},
        {"descriptor_device": 3, "descriptor_inode": 4},
        {
            "configured_device": 1,
            "configured_inode": 2,
            "descriptor_device": 3,
            "descriptor_inode": 4,
        },
    ),
)
def test_censored_root_observation_rejects_impossible_identity_shapes(
    identity_overrides: dict[str, int],
) -> None:
    with pytest.raises(ValueError, match="identit"):
        evidence_module._RootDescriptorObservation(
            None,
            evidence_module.EvidenceStatus.CANNOT_CHECK_MECHANISM,
            mechanism_limitation=(
                evidence_module.EvidenceMechanismLimitationKind.FILESYSTEM_IO
            ),
            mechanism_errno=errno.EIO,
            **identity_overrides,
        )


def test_censored_root_observation_retains_completed_configured_identity() -> None:
    observation = evidence_module._RootDescriptorObservation(
        None,
        evidence_module.EvidenceStatus.CANNOT_CHECK_MECHANISM,
        configured_device=1,
        configured_inode=2,
        mechanism_limitation=(
            evidence_module.EvidenceMechanismLimitationKind.FILESYSTEM_IO
        ),
        mechanism_errno=errno.EBADF,
    )

    assert (observation.configured_device, observation.configured_inode) == (1, 2)
    assert observation.descriptor_device is None
    assert observation.descriptor_inode is None


@pytest.mark.parametrize(
    ("limitation", "error_number"),
    (
        (
            evidence_module.EvidenceMechanismLimitationKind.FILESYSTEM_IO,
            errno.EACCES,
        ),
        (
            evidence_module.EvidenceMechanismLimitationKind.FILESYSTEM_IO,
            errno.EMFILE,
        ),
        (
            evidence_module.EvidenceMechanismLimitationKind.PROCESS_TIMEOUT,
            errno.EIO,
        ),
    ),
)
def test_bare_observation_constructor_closes_limitation_errno_matrix(
    limitation: evidence_module.EvidenceMechanismLimitationKind,
    error_number: int,
) -> None:
    censored_head = evidence_module._BareRepositoryComponentObservation(
        "HEAD",
        "file",
        "MECHANISM_CENSORED",
        mechanism_errno=error_number,
    )

    with pytest.raises(ValueError, match="limitation|errno"):
        evidence_module._BareRepositoryObservation(
            None,
            evidence_module.EvidenceStatus.CANNOT_CHECK_MECHANISM,
            (censored_head,),
            mechanism_limitation=limitation,
            mechanism_errno=error_number,
        )


@pytest.mark.parametrize("failure", (errno.EIO, errno.EBADF, "deadline"))
def test_post_success_root_unknown_is_typed_and_hash_bound(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: int | str,
) -> None:
    opened = _open_git_root(tmp_path / "repo")
    fake_git = tmp_path / "fake-git"
    fake_git.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fake_git.chmod(0o755)
    monkeypatch.setattr(evidence_module, "_GIT_EXECUTABLE", str(fake_git))

    ref = f"source:post-root-{failure}"
    if failure == "deadline":
        post_observation = evidence_module._RootDescriptorObservation(
            None,
            evidence_module.EvidenceStatus.CANNOT_CHECK_RESOURCE,
            work_exhaustion=_deadline_exhaustion(ref),
            note="post-command root observation crossed the deadline",
        )
    else:
        post_observation = evidence_module._RootDescriptorObservation(
            None,
            evidence_module.EvidenceStatus.CANNOT_CHECK_MECHANISM,
            mechanism_limitation=(
                evidence_module.EvidenceMechanismLimitationKind.FILESYSTEM_IO
            ),
            mechanism_errno=failure,
            note="post-command root identity is unavailable",
        )

    real_probe = evidence_module._root_descriptor_matches
    probes: list[evidence_module._RootDescriptorObservation] = []

    def sequenced_probe(
        selected_root: evidence_module._OpenedRoot,
        **options: object,
    ) -> evidence_module._RootDescriptorObservation:
        if not probes:
            observation = real_probe(selected_root, **options)
            probes.append(observation)
            return observation
        probes.append(post_observation)
        return post_observation

    monkeypatch.setattr(
        evidence_module,
        "_root_descriptor_matches",
        sequenced_probe,
    )
    try:
        result = evidence_module._run_protected_git(
            opened,
            "probe",
            ref=ref,
            ordinal=0,
        )
    finally:
        _close_opened_root(opened)

    assert len(probes) == 2
    assert result.returncode == 0
    assert result.root_stable is None
    assert result.root_observation is post_observation
    assert result.root_observation_hash == post_observation.observation_hash
    if failure == "deadline":
        assert result.root_observation.status is (
            evidence_module.EvidenceStatus.CANNOT_CHECK_RESOURCE
        )
    else:
        assert result.root_observation.status is (
            evidence_module.EvidenceStatus.CANNOT_CHECK_MECHANISM
        )
        assert result.root_observation.mechanism_errno == failure


def test_git_resolution_binds_root_observation_occurrence_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened = _open_git_root(tmp_path / "repo")
    ledger = evidence_module._EvidenceWorkLedger(
        _work_contract(descriptor_operation_attempts=100),
        started_monotonic_ns=evidence_module.time.monotonic_ns(),
    )

    def resolve_with_identity(configured_identity: tuple[int, int] | None) -> object:
        identity_fields = (
            {}
            if configured_identity is None
            else {
                "configured_device": configured_identity[0],
                "configured_inode": configured_identity[1],
            }
        )
        observation = evidence_module._RootDescriptorObservation(
            None,
            evidence_module.EvidenceStatus.CANNOT_CHECK_MECHANISM,
            mechanism_limitation=(
                evidence_module.EvidenceMechanismLimitationKind.FILESYSTEM_IO
            ),
            mechanism_errno=errno.EIO,
            note="root identity observation was censored",
            **identity_fields,
        )

        def censored_git(*args: object, **kwargs: object) -> object:
            del args, kwargs
            return evidence_module._GitCommandResult(
                0,
                b"sha1\n",
                b"",
                None,
                mechanism_limitation=observation.mechanism_limitation,
                mechanism_errno=observation.mechanism_errno,
                root_observation=observation,
            )

        monkeypatch.setattr(evidence_module, "_run_protected_git", censored_git)
        resolution = evidence_module._resolve_git_revision(
            opened,
            "a" * 40,
            evidence_module._CaptureWorkState(
                1_000,
                1_000,
                1_000,
                1_000,
                1_000_000_000,
                1_000,
                1_000,
                1_000,
                1_000,
            ),
            work_ledger=ledger,
            ref="source:root-occurrence-binding",
            ordinal=0,
        )
        return observation, resolution

    try:
        first_observation, first_resolution = resolve_with_identity(None)
        second_observation, second_resolution = resolve_with_identity((1, 2))
    finally:
        _close_opened_root(opened)

    def scalar_values(value: object) -> list[object]:
        if isinstance(value, dict):
            return [
                scalar
                for item in value.values()
                for scalar in scalar_values(item)
            ]
        if isinstance(value, (list, tuple)):
            return [scalar for item in value for scalar in scalar_values(item)]
        return [value]

    assert first_observation.observation_hash != second_observation.observation_hash
    assert first_observation.observation_hash in scalar_values(asdict(first_resolution))
    assert second_observation.observation_hash in scalar_values(asdict(second_resolution))
    assert first_resolution != second_resolution


def test_pre_root_occurrence_binds_capture_and_command_subject() -> None:
    observation = evidence_module._RootDescriptorObservation(
        True,
        evidence_module.EvidenceStatus.RESOLVED,
        configured_device=1,
        configured_inode=2,
        descriptor_device=1,
        descriptor_inode=2,
    )
    receipt_type = evidence_module.EvidenceRootObservationOccurrenceReceipt
    receipt_fields = set(receipt_type.__dataclass_fields__)
    capture_field = next(
        (
            name
            for name in ("capture_occurrence_id", "capture_id")
            if name in receipt_fields
        ),
        None,
    )
    subject_field = next(
        (
            name
            for name in ("command_subject_hash", "invocation_subject_hash")
            if name in receipt_fields
        ),
        None,
    )
    assert capture_field is not None
    assert subject_field is not None
    coordinates: dict[str, object] = {
        capture_field: "c" * 64,
        subject_field: "a" * 64,
    }

    receipt = receipt_type(
        phase=evidence_module.EvidenceRootObservationPhase.PRE,
        operation=evidence_module.EvidenceGitOperation.OBJECT_FORMAT,
        ref="source:root-occurrence",
        capture_ordinal=0,
        event_sequence=1,
        previous_occurrence_hash=None,
        process_start_index=None,
        observation=observation,
        **coordinates,
    )

    receipt_scalars = asdict(receipt).values()
    assert "c" * 64 in receipt_scalars
    assert "a" * 64 in receipt_scalars


def test_root_observation_occurrence_separates_recurrence_from_event_identity() -> None:
    observation = evidence_module._RootDescriptorObservation(
        True,
        evidence_module.EvidenceStatus.RESOLVED,
        configured_device=1,
        configured_inode=2,
        descriptor_device=1,
        descriptor_inode=2,
        note="root identities match",
    )
    receipt_type = evidence_module.EvidenceRootObservationOccurrenceReceipt
    phase_type = evidence_module.EvidenceRootObservationPhase
    receipt_fields = set(receipt_type.__dataclass_fields__)
    capture_field = next(
        name
        for name in ("capture_occurrence_id", "capture_id")
        if name in receipt_fields
    )
    subject_field = next(
        name
        for name in ("command_subject_hash", "invocation_subject_hash")
        if name in receipt_fields
    )
    common = {
        "phase": phase_type.PRE,
        "operation": evidence_module.EvidenceGitOperation.OBJECT_FORMAT,
        "ref": "source:root-occurrence",
        "capture_ordinal": 0,
        "event_sequence": 1,
        "previous_occurrence_hash": None,
        "process_start_index": None,
        capture_field: "c" * 64,
        subject_field: "a" * 64,
        "observation": observation,
    }
    baseline = receipt_type(**common)
    changed_ref = receipt_type(**{**common, "ref": "source:other-root-occurrence"})
    changed_ordinal = receipt_type(**{**common, "capture_ordinal": 1})
    changed_capture = receipt_type(**{**common, capture_field: "d" * 64})
    changed_sequence = receipt_type(
        **{
            **common,
            "event_sequence": 3,
            "previous_occurrence_hash": "c" * 64,
        }
    )
    changed_predecessor = receipt_type(
        **{
            **common,
            "event_sequence": 3,
            "previous_occurrence_hash": "d" * 64,
        }
    )
    post_fields = {
        **common,
        "phase": phase_type.POST,
        "event_sequence": 2,
        "previous_occurrence_hash": baseline.occurrence_hash,
        "process_start_index": 1,
        "invocation_subject_hash": "e" * 64,
    }
    post = receipt_type(**post_fields)
    changed_subject = receipt_type(**{**post_fields, subject_field: "b" * 64})
    occurrences = (
        baseline,
        changed_ref,
        changed_ordinal,
        changed_capture,
        changed_subject,
        changed_sequence,
        changed_predecessor,
        post,
    )

    assert {receipt.observation_hash for receipt in occurrences} == {
        observation.observation_hash
    }
    assert len({receipt.occurrence_hash for receipt in occurrences}) == len(
        occurrences
    )

    changed_observation = replace(
        observation,
        configured_inode=3,
        descriptor_inode=3,
    )
    changed_payload = receipt_type(**{**common, "observation": changed_observation})
    assert changed_payload.observation_hash != baseline.observation_hash
    assert changed_payload.occurrence_hash != baseline.occurrence_hash


@pytest.mark.parametrize(
    ("phase", "event_sequence", "predecessor", "process_index", "invocation_hash"),
    (
        (
            evidence_module.EvidenceRootObservationPhase.PRE,
            1,
            None,
            None,
            "b" * 64,
        ),
        (
            evidence_module.EvidenceRootObservationPhase.POST,
            2,
            "c" * 64,
            1,
            "",
        ),
    ),
)
def test_root_occurrence_phase_requires_exact_invocation_coordinate(
    phase: evidence_module.EvidenceRootObservationPhase,
    event_sequence: int,
    predecessor: str | None,
    process_index: int | None,
    invocation_hash: str,
) -> None:
    observation = evidence_module._RootDescriptorObservation(
        True,
        evidence_module.EvidenceStatus.RESOLVED,
        configured_device=1,
        configured_inode=2,
        descriptor_device=1,
        descriptor_inode=2,
    )

    with pytest.raises(ValueError, match="phase|pre|post|invocation"):
        evidence_module.EvidenceRootObservationOccurrenceReceipt(
            phase=phase,
            operation=evidence_module.EvidenceGitOperation.OBJECT_FORMAT,
            ref="source:root-occurrence-phase-grammar",
            capture_ordinal=0,
            event_sequence=event_sequence,
            previous_occurrence_hash=predecessor,
            capture_occurrence_id="a" * 64,
            command_subject_hash="d" * 64,
            process_start_index=process_index,
            invocation_subject_hash=invocation_hash,
            observation=observation,
        )


def test_successful_command_retains_ordered_pre_post_root_occurrences(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened = _open_git_root(tmp_path / "repo")
    fake_git = tmp_path / "fake-git"
    fake_git.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fake_git.chmod(0o755)
    monkeypatch.setattr(evidence_module, "_GIT_EXECUTABLE", str(fake_git))
    monkeypatch.setattr(
        evidence_module,
        "_TRUSTED_EXECUTABLE_OWNER_UIDS",
        frozenset({0, os.geteuid()}),
    )
    ledger = evidence_module._EvidenceWorkLedger(
        _work_contract(descriptor_operation_attempts=100),
        started_monotonic_ns=evidence_module.time.monotonic_ns(),
    )
    instrument = evidence_module._observe_protected_git_instrument(
        work_ledger=ledger,
        ref="source:root-occurrence-pre-post",
        ordinal=0,
    )
    assert instrument.usable
    opened = replace(opened, protected_git_instrument=instrument)

    try:
        result = evidence_module._run_protected_git(
            opened,
            "probe",
            work_ledger=ledger,
            ref="source:root-occurrence-pre-post",
            ordinal=0,
        )
    finally:
        _close_opened_root(opened)

    assert result.returncode == 0
    occurrences = tuple(ledger.root_observation_occurrences)
    assert result.root_observation_occurrences == occurrences
    assert tuple(item.phase for item in occurrences) == (
        evidence_module.EvidenceRootObservationPhase.PRE,
        evidence_module.EvidenceRootObservationPhase.POST,
    )
    assert occurrences[0].process_start_index is None
    assert occurrences[0].invocation_subject_hash == ""
    assert occurrences[1].process_start_index == result.process_start_index
    assert occurrences[1].invocation_subject_hash == result.invocation_subject_hash
    assert occurrences[1].previous_occurrence_hash == occurrences[0].occurrence_hash
    assert occurrences[1].command_subject_hash == occurrences[0].command_subject_hash


def test_popen_return_then_parent_status_close_failure_still_records_post(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened = _open_git_root(tmp_path / "repo")
    fake_git = tmp_path / "fake-git"
    fake_git.write_text("#!/bin/sh\nsleep 1\n", encoding="utf-8")
    fake_git.chmod(0o755)
    monkeypatch.setattr(evidence_module, "_GIT_EXECUTABLE", str(fake_git))

    real_pipe = evidence_module.os.pipe
    real_close = evidence_module.os.close
    real_popen = evidence_module.subprocess.Popen
    status_write_fd: int | None = None
    popen_returned = False
    injected = False

    def recording_pipe() -> tuple[int, int]:
        nonlocal status_write_fd
        read_fd, write_fd = real_pipe()
        if status_write_fd is None:
            status_write_fd = write_fd
        return read_fd, write_fd

    def fail_first_parent_status_close(file_descriptor: int) -> None:
        nonlocal injected
        if popen_returned and file_descriptor == status_write_fd and not injected:
            injected = True
            raise OSError(errno.EIO, "simulated parent status-FD close failure")
        real_close(file_descriptor)

    def recording_popen(*args: object, **kwargs: object) -> subprocess.Popen[bytes]:
        nonlocal popen_returned
        process = real_popen(*args, **kwargs)
        popen_returned = True
        return process

    monkeypatch.setattr(evidence_module.os, "pipe", recording_pipe)
    monkeypatch.setattr(evidence_module.os, "close", fail_first_parent_status_close)
    monkeypatch.setattr(evidence_module.subprocess, "Popen", recording_popen)
    try:
        result = evidence_module._run_protected_git(
            opened,
            "probe",
            ref="source:root-occurrence-post-popen-close",
            ordinal=0,
        )
    finally:
        _close_opened_root(opened)

    assert popen_returned and injected
    assert result.returncode is None
    assert tuple(item.phase for item in result.root_observation_occurrences) == (
        evidence_module.EvidenceRootObservationPhase.PRE,
        evidence_module.EvidenceRootObservationPhase.POST,
    )
    post = result.root_observation_occurrences[-1]
    assert post.process_start_index is not None
    assert post.invocation_subject_hash
    assert post.previous_occurrence_hash == (
        result.root_observation_occurrences[-2].occurrence_hash
    )


def test_record_and_snapshot_bind_ordered_root_observation_occurrences(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(
        ["git", "-C", str(repo), "init", "-q"],
        check=True,
        capture_output=True,
    )
    (repo / "payload.bin").write_bytes(b"orion-root-occurrence")
    subprocess.run(
        ["git", "-C", str(repo), "add", "payload.bin"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=ORION Hostile Test",
            "-c",
            "user.email=orion-hostile@example.invalid",
            "commit",
            "-q",
            "-m",
            "root occurrence fixture",
        ],
        check=True,
        capture_output=True,
    )
    commit_oid = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    source_id = "source:root-occurrence-public-binding"
    obligation_id = "obligation:root-occurrence-public-binding"
    source = evidence_module.HostEvidenceSource(
        source_id=source_id,
        backend_type="git",
        root_scheme="repo",
        relative_path="payload.bin",
        git_revision=commit_oid,
    )
    binding = evidence_module.EvidenceRoleBinding(
        binding_id="binding:root-occurrence-public-binding",
        evidence_ref=source_id,
        role_id="role:root-occurrence-public-binding",
        obligation_id=obligation_id,
    )
    manifest = evidence_module.HostEvidenceManifest(
        manifest_id="manifest:root-occurrence-public-binding",
        required_obligation_ids=(obligation_id,),
        sources=(source,),
        bindings=(binding,),
    )

    snapshot = evidence_module.capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )
    record = snapshot.records[0]
    repeated_snapshot = evidence_module.capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
    )

    def capture_occurrence_id(value: object) -> str:
        for name in ("capture_occurrence_id", "capture_id"):
            candidate = getattr(value, name, None)
            if candidate is not None:
                assert isinstance(candidate, str)
                assert candidate
                return candidate
        raise AssertionError("public evidence value lacks a capture occurrence ID")

    snapshot_capture_id = capture_occurrence_id(snapshot)
    assert capture_occurrence_id(record) == snapshot_capture_id
    assert capture_occurrence_id(repeated_snapshot) != snapshot_capture_id
    record_occurrences = record.root_observation_occurrences
    snapshot_occurrences = snapshot.root_observation_occurrences
    assert len(record_occurrences) >= 2
    assert snapshot_occurrences == record_occurrences
    assert {
        capture_occurrence_id(item) for item in snapshot_occurrences
    } == {snapshot_capture_id}
    assert {
        item.occurrence_hash
        for item in repeated_snapshot.root_observation_occurrences
    }.isdisjoint({item.occurrence_hash for item in snapshot_occurrences})

    forced_capture_id = "f" * 64
    forced_first = evidence_module.capture_host_evidence_snapshot(
        (source_id,),
        roots={"repo": repo},
        manifest=manifest,
        captured_at_authority_revision="a" * 64,
        captured_at_support_revision="b" * 64,
        capture_occurrence_id=forced_capture_id,
    )
    try:
        forced_second = evidence_module.capture_host_evidence_snapshot(
            (source_id,),
            roots={"repo": repo},
            manifest=manifest,
            captured_at_authority_revision="a" * 64,
            captured_at_support_revision="b" * 64,
            capture_occurrence_id=forced_capture_id,
        )
    except ValueError:
        pass
    else:
        assert forced_first.capture_occurrence_id != forced_capture_id
        assert forced_second.capture_occurrence_id != forced_capture_id
        assert (
            forced_first.capture_occurrence_id
            != forced_second.capture_occurrence_id
        )
        assert {
            item.occurrence_hash
            for item in forced_first.root_observation_occurrences
        }.isdisjoint(
            {
                item.occurrence_hash
                for item in forced_second.root_observation_occurrences
            }
        )
        assert forced_first.records[0].record_hash != forced_second.records[0].record_hash
        assert forced_first.snapshot_id != forced_second.snapshot_id
        assert (
            forced_first.records[0].record_signature_hash
            == forced_second.records[0].record_signature_hash
        )
        assert (
            forced_first.snapshot_signature_hash
            == forced_second.snapshot_signature_hash
        )
    occurrence_hashes = tuple(item.occurrence_hash for item in record_occurrences)
    assert tuple(item.event_sequence for item in snapshot_occurrences) == tuple(
        range(1, len(snapshot_occurrences) + 1)
    )
    assert snapshot_occurrences[0].previous_occurrence_hash is None
    assert tuple(
        item.previous_occurrence_hash for item in snapshot_occurrences[1:]
    ) == occurrence_hashes[:-1]

    def ordered_scalars(value: object) -> list[object]:
        if isinstance(value, dict):
            return [
                scalar
                for item in value.values()
                for scalar in ordered_scalars(item)
            ]
        if isinstance(value, (list, tuple)):
            return [scalar for item in value for scalar in ordered_scalars(item)]
        return [value]

    def contains_ordered_hashes(payload: object) -> bool:
        scalars = ordered_scalars(payload)
        cursor = 0
        for scalar in scalars:
            if cursor < len(occurrence_hashes) and scalar == occurrence_hashes[cursor]:
                cursor += 1
        return cursor == len(occurrence_hashes)

    assert contains_ordered_hashes(evidence_module._host_record_payload(record))
    assert contains_ordered_hashes(evidence_module._host_snapshot_payload(snapshot))

    try:
        reversed_record = replace(
            record,
            root_observation_occurrences=tuple(reversed(record_occurrences)),
        )
    except ValueError:
        pass
    else:
        assert reversed_record.record_hash != record.record_hash


@pytest.mark.parametrize("terminal_path", ("timeout", "output-limit"))
def test_post_process_terminal_path_observes_and_binds_root_before_return(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    terminal_path: str,
) -> None:
    opened = _open_git_root(tmp_path / "repo")
    fake_git = tmp_path / "fake-git"
    fake_git.write_text(
        "#!/bin/sh\nsleep 1\n"
        if terminal_path == "timeout"
        else "#!/bin/sh\nprintf 12345\n",
        encoding="utf-8",
    )
    fake_git.chmod(0o755)
    monkeypatch.setattr(evidence_module, "_GIT_EXECUTABLE", str(fake_git))

    real_probe = evidence_module._root_descriptor_matches
    probes: list[evidence_module._RootDescriptorObservation] = []

    def observing_probe(
        selected_root: evidence_module._OpenedRoot,
        **options: object,
    ) -> evidence_module._RootDescriptorObservation:
        result = real_probe(selected_root, **options)
        probes.append(result)
        return result

    monkeypatch.setattr(
        evidence_module,
        "_root_descriptor_matches",
        observing_probe,
    )
    options: dict[str, int | float] = (
        {"timeout_seconds": 0.01}
        if terminal_path == "timeout"
        else {"stdout_limit": 4, "stderr_limit": 4, "combined_limit": 8}
    )
    try:
        result = evidence_module._run_protected_git(
            opened,
            "probe",
            ref=f"source:post-root-{terminal_path}",
            ordinal=0,
            **options,
        )
    finally:
        _close_opened_root(opened)

    assert result.timed_out is (terminal_path == "timeout")
    assert result.output_limited is (terminal_path == "output-limit")
    assert len(probes) == 2
    assert result.root_observation is probes[-1]
    assert result.root_stable is probes[-1].matches
    assert result.root_observation_hash == probes[-1].observation_hash


@pytest.mark.parametrize("terminal_path", ("helper-failure", "selector-error"))
def test_post_spawn_failure_observes_and_binds_root_before_return(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    terminal_path: str,
) -> None:
    opened = _open_git_root(tmp_path / "repo")
    fake_git = tmp_path / "fake-git"
    fake_git.write_text("#!/bin/sh\nsleep 1\n", encoding="utf-8")
    fake_git.chmod(0o755)
    monkeypatch.setattr(evidence_module, "_GIT_EXECUTABLE", str(fake_git))
    if terminal_path == "helper-failure":
        monkeypatch.setattr(
            evidence_module,
            "_GIT_FD_EXEC_HELPER",
            (
                "import os, sys\n"
                "status_fd = int(sys.argv[4])\n"
                "os.write(status_fd, b'1')\n"
                "os._exit(126)"
            ),
        )
    else:

        def fail_selector() -> object:
            raise OSError(errno.EIO, "simulated selector construction failure")

        monkeypatch.setattr(
            evidence_module.selectors,
            "DefaultSelector",
            fail_selector,
        )

    real_probe = evidence_module._root_descriptor_matches
    probes: list[evidence_module._RootDescriptorObservation] = []

    def observing_probe(
        selected_root: evidence_module._OpenedRoot,
        **options: object,
    ) -> evidence_module._RootDescriptorObservation:
        result = real_probe(selected_root, **options)
        probes.append(result)
        return result

    monkeypatch.setattr(
        evidence_module,
        "_root_descriptor_matches",
        observing_probe,
    )
    try:
        result = evidence_module._run_protected_git(
            opened,
            "probe",
            ref=f"source:post-root-{terminal_path}",
            ordinal=0,
        )
    finally:
        _close_opened_root(opened)

    assert result.returncode is None
    assert len(probes) == 2
    assert result.root_observation is probes[-1]
    assert result.root_stable is probes[-1].matches
    assert result.root_observation_hash == probes[-1].observation_hash


def test_post_spawn_completion_deadline_binds_resource_root_observation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened = _open_git_root(tmp_path / "repo")
    fake_git = tmp_path / "fake-git"
    fake_git.write_text("#!/bin/sh\nsleep 1\n", encoding="utf-8")
    fake_git.chmod(0o755)
    monkeypatch.setattr(evidence_module, "_GIT_EXECUTABLE", str(fake_git))
    monkeypatch.setattr(
        evidence_module,
        "_TRUSTED_EXECUTABLE_OWNER_UIDS",
        frozenset({0, os.geteuid()}),
    )
    ledger = evidence_module._EvidenceWorkLedger(
        _work_contract(descriptor_operation_attempts=100),
        started_monotonic_ns=evidence_module.time.monotonic_ns(),
    )
    instrument = evidence_module._observe_protected_git_instrument(
        work_ledger=ledger,
        ref="source:post-root-process-start-deadline",
        ordinal=0,
    )
    assert instrument.usable
    opened = replace(opened, protected_git_instrument=instrument)

    real_complete = ledger.charge_completed_observation

    def complete_at_process_start(
        stage: str,
        delta: evidence_module.EvidenceWorkVector,
        *,
        ref: str,
        ordinal: int,
        now_monotonic_ns: int,
    ) -> evidence_module.EvidenceWorkExhaustion | None:
        if stage == "git.process.started":
            now_monotonic_ns = ledger.deadline_monotonic_ns
        return real_complete(
            stage,
            delta,
            ref=ref,
            ordinal=ordinal,
            now_monotonic_ns=now_monotonic_ns,
        )

    monkeypatch.setattr(ledger, "charge_completed_observation", complete_at_process_start)
    real_probe = evidence_module._root_descriptor_matches
    probes: list[evidence_module._RootDescriptorObservation] = []

    def observing_probe(
        selected_root: evidence_module._OpenedRoot,
        **options: object,
    ) -> evidence_module._RootDescriptorObservation:
        result = real_probe(selected_root, **options)
        probes.append(result)
        return result

    monkeypatch.setattr(
        evidence_module,
        "_root_descriptor_matches",
        observing_probe,
    )
    try:
        result = evidence_module._run_protected_git(
            opened,
            "probe",
            work_ledger=ledger,
            ref="source:post-root-process-start-deadline",
            ordinal=0,
        )
    finally:
        _close_opened_root(opened)

    assert len(probes) == 2
    assert result.root_stable is None
    assert result.root_observation is probes[-1]
    assert result.root_observation.status is (
        evidence_module.EvidenceStatus.CANNOT_CHECK_RESOURCE
    )
    assert result.root_observation_hash == probes[-1].observation_hash
    assert result.work_exhaustion is ledger.exhaustion


@pytest.mark.parametrize(
    "result_overrides",
    (
        {
            "mechanism_limitation": (
                evidence_module.EvidenceMechanismLimitationKind.PROCESS_IO
            )
        },
        {"mechanism_errno": errno.EBADF},
    ),
)
def test_git_command_result_rejects_root_censorship_projection_mismatch(
    result_overrides: dict[str, object],
) -> None:
    observation = evidence_module._RootDescriptorObservation(
        None,
        evidence_module.EvidenceStatus.CANNOT_CHECK_MECHANISM,
        mechanism_limitation=(
            evidence_module.EvidenceMechanismLimitationKind.FILESYSTEM_IO
        ),
        mechanism_errno=errno.EIO,
    )
    constructor_options: dict[str, object] = {
        "mechanism_limitation": observation.mechanism_limitation,
        "mechanism_errno": observation.mechanism_errno,
        "root_observation": observation,
    }
    constructor_options.update(result_overrides)

    with pytest.raises(ValueError, match="root|projection"):
        evidence_module._GitCommandResult(
            None,
            b"",
            b"",
            None,
            **constructor_options,
        )


def _observe_layout_effects(
    monkeypatch: pytest.MonkeyPatch,
    *,
    cross_deadline_after: int | None = None,
) -> tuple[list[str], list[int]]:
    effects: list[str] = []
    clock = [0]
    real_dup = evidence_module.os.dup
    real_stat = evidence_module.os.stat
    real_open = evidence_module.os.open
    real_fstat = evidence_module.os.fstat

    def completed(name: str, value: int | os.stat_result) -> int | os.stat_result:
        effects.append(name)
        if cross_deadline_after == len(effects):
            clock[0] = 6
        return value

    def observed_dup(fd: int) -> int:
        return int(completed("dup", real_dup(fd)))

    def observed_stat(*args: object, **kwargs: object) -> os.stat_result:
        return completed("stat", real_stat(*args, **kwargs))  # type: ignore[return-value]

    def observed_open(*args: object, **kwargs: object) -> int:
        return int(completed("open", real_open(*args, **kwargs)))

    def observed_fstat(fd: int) -> os.stat_result:
        return completed("fstat", real_fstat(fd))  # type: ignore[return-value]

    monkeypatch.setattr(evidence_module.os, "dup", observed_dup)
    monkeypatch.setattr(evidence_module.os, "stat", observed_stat)
    monkeypatch.setattr(evidence_module.os, "open", observed_open)
    monkeypatch.setattr(evidence_module.os, "fstat", observed_fstat)
    monkeypatch.setattr(evidence_module.time, "monotonic_ns", lambda: clock[0])
    return effects, clock


@pytest.mark.parametrize("descriptor_limit", range(6))
def test_git_layout_descriptor_vector_admits_exact_effect_prefix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    descriptor_limit: int,
) -> None:
    git_dir = tmp_path / "git-dir"
    git_dir.mkdir()
    (git_dir / "config").write_bytes(b"[core]\n\trepositoryformatversion = 0\n")
    git_fd = os.open(git_dir, os.O_RDONLY | os.O_DIRECTORY)
    ledger = evidence_module._EvidenceWorkLedger(
        _work_contract(descriptor_operation_attempts=descriptor_limit),
        started_monotonic_ns=0,
    )
    effects, _ = _observe_layout_effects(monkeypatch)
    try:
        observation = evidence_module._read_git_control_file(
            git_fd,
            "config",
            work_ledger=ledger,
            ref="source:layout-vector",
            ordinal=0,
        )
    finally:
        os.close(git_fd)

    expected_effects = ["dup", "stat", "open", "fstat", "fstat"][
        :descriptor_limit
    ]
    assert effects == expected_effects
    assert (
        ledger.used.as_dict()["descriptor_operation_attempts"]
        == len(expected_effects)
    )
    if descriptor_limit < 5:
        assert observation.disposition is (
            evidence_module._ArtifactObservationDisposition.RESOURCE_EXHAUSTED
        )
        assert ledger.exhaustion is not None
        assert ledger.exhaustion.dimensions == ("descriptor_operation_attempts",)
    else:
        assert observation.disposition is (
            evidence_module._ArtifactObservationDisposition.BOUND
        )
        assert ledger.exhaustion is None


@pytest.mark.parametrize("cross_deadline_after", range(1, 6))
def test_git_layout_deadline_charges_effect_and_forbids_suffix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    cross_deadline_after: int,
) -> None:
    git_dir = tmp_path / "git-dir"
    git_dir.mkdir()
    (git_dir / "config").write_bytes(b"[core]\n\trepositoryformatversion = 0\n")
    git_fd = os.open(git_dir, os.O_RDONLY | os.O_DIRECTORY)
    ledger = evidence_module._EvidenceWorkLedger(
        _work_contract(
            descriptor_operation_attempts=100,
            wall_time_budget_ns=5,
        ),
        started_monotonic_ns=0,
    )
    effects, _ = _observe_layout_effects(
        monkeypatch,
        cross_deadline_after=cross_deadline_after,
    )
    try:
        observation = evidence_module._read_git_control_file(
            git_fd,
            "config",
            work_ledger=ledger,
            ref="source:layout-deadline",
            ordinal=0,
        )
    finally:
        os.close(git_fd)

    expected_effects = ["dup", "stat", "open", "fstat", "fstat"][
        :cross_deadline_after
    ]
    assert effects == expected_effects
    assert observation.disposition is (
        evidence_module._ArtifactObservationDisposition.RESOURCE_EXHAUSTED
    )
    assert ledger.exhaustion is not None
    assert ledger.exhaustion.kind is (
        evidence_module.EvidenceWorkExhaustionKind.DEADLINE
    )
    assert (
        ledger.used.as_dict()["descriptor_operation_attempts"]
        == cross_deadline_after
    )


def test_bare_observation_hash_is_bound_into_root_configuration(
    tmp_path: Path,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    opened = evidence_module._open_root_without_symlinks("repo", root)
    assert opened.bare_repository_observation is not None
    baseline_hash = evidence_module._root_configuration_hash((opened,))
    mutated_observation = replace(
        opened.bare_repository_observation,
        note=opened.bare_repository_observation.note + " mutated",
    )
    mutated_hash = evidence_module._root_configuration_hash(
        (replace(opened, bare_repository_observation=mutated_observation),)
    )
    try:
        assert mutated_observation.observation_hash != (
            opened.bare_repository_observation.observation_hash
        )
        assert mutated_hash != baseline_hash
    finally:
        _close_opened_root(opened)
