from __future__ import annotations

from dataclasses import replace
import errno
import os
from pathlib import Path
import select
import signal
import subprocess
import sys

import pytest

from orion.kernel import evidence as evidence_module


_HELPER_STATUS_VERSION = "orion.git-helper-status.v1"
_PORTABLE_HELPER_FRAME_LIMIT = 512
_PORTABLE_HELPER_RECEIPT_LIMIT = 2 * _PORTABLE_HELPER_FRAME_LIMIT
_PORTABLE_HELPER_ACQUISITION_LIMIT = _PORTABLE_HELPER_RECEIPT_LIMIT + 1
_PRE_EXEC_FRAME = (
    b'{"errno":null,"kind":null,"stage":"HELPER_PRE_EXEC",'
    b'"version":"orion.git-helper-status.v1"}\n'
)
_CHDIR_FAILURE_FRAME = (
    b'{"errno":5,"kind":"IO","stage":"HELPER_CHDIR",'
    b'"version":"orion.git-helper-status.v1"}\n'
)
_EXEC_ACCESS_FAILURE_FRAME = (
    f'{{"errno":{errno.EACCES},"kind":"ACCESS_POLICY",'
    '"stage":"HELPER_EXEC",'
    '"version":"orion.git-helper-status.v1"}\n'
).encode("ascii")
_ROOT_ATTESTATION_FAILURE_FRAME = (
    f'{{"errno":{errno.EIO},"kind":"IO",'
    '"stage":"HELPER_ROOT_ATTESTATION",'
    '"version":"orion.git-helper-status.v1"}\n'
).encode("ascii")
_THIRD_FRAME_STATUS = (
    _PRE_EXEC_FRAME + _EXEC_ACCESS_FAILURE_FRAME + _CHDIR_FAILURE_FRAME
)
_OVERSIZED_FRAME_STATUS = _PRE_EXEC_FRAME + (
    b"x" * _PORTABLE_HELPER_FRAME_LIMIT + b"\n"
)
_TOTAL_CAP_SENTINEL_STATUS = _PRE_EXEC_FRAME + (
    b"x" * (_PORTABLE_HELPER_RECEIPT_LIMIT - len(_PRE_EXEC_FRAME))
) + b"!"


def _assert_protocol_uncertainty(
    observation: evidence_module.EvidenceGitHelperStatusObservation,
    receipt: bytes,
) -> None:
    assert observation.protocol_valid is False
    assert observation.handoff_state is evidence_module.EvidenceHelperHandoffState.UNKNOWN
    assert observation.failure_stage is (
        evidence_module.EvidenceProcessFailureStage.HELPER_STATUS_READ
    )
    assert observation.failure_kind is (
        evidence_module.EvidenceProcessFailureKind.PROTOCOL_INVALID
    )
    assert observation.mechanism_errno is None
    assert observation.raw_receipt == receipt
    assert observation.permits_git_outcome_projection is False


def _execute_bound_helper_source(
    root: Path,
    git_executable: Path,
    *arguments: str,
) -> tuple[int, bytes]:
    root_fd = os.open(root, os.O_RDONLY)
    status_read_fd, status_write_fd = os.pipe()
    try:
        root_info = os.fstat(root_fd)
        git_info = os.stat(git_executable, follow_symlinks=False)
        process = subprocess.Popen(  # noqa: S603 - executes the bound test helper
            [
                evidence_module._GIT_FD_HELPER_EXECUTABLE,
                "-I",
                "-S",
                "-c",
                evidence_module._GIT_FD_EXEC_HELPER,
                str(root_fd),
                str(root_info.st_dev),
                str(root_info.st_ino),
                str(status_write_fd),
                str(git_executable),
                str(git_info.st_dev),
                str(git_info.st_ino),
                str(git_info.st_size),
                str(git_info.st_mtime_ns),
                str(git_info.st_ctime_ns),
                *arguments,
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
            pass_fds=(root_fd, status_write_fd),
            env=os.environ.copy(),
        )
        os.close(status_write_fd)
        status_write_fd = -1
        status = bytearray()
        while True:
            ready, _, _ = select.select([status_read_fd], [], [], 5)
            if not ready:
                process.kill()
                process.wait(timeout=5)
                raise AssertionError("bound helper status channel did not terminate")
            chunk = os.read(status_read_fd, select.PIPE_BUF)
            if not chunk:
                break
            status.extend(chunk)
        process.communicate(timeout=5)
        assert process.returncode is not None
        return process.returncode, bytes(status)
    finally:
        os.close(root_fd)
        os.close(status_read_fd)
        if status_write_fd >= 0:
            os.close(status_write_fd)


def _open_test_git_root(root: Path) -> evidence_module._OpenedRoot:
    root.mkdir()
    (root / ".git").mkdir()
    opened = evidence_module._open_root_without_symlinks("repo", root)
    assert opened.file_descriptor is not None
    assert opened.git_directory_fd is not None
    return opened


def _close_test_git_root(opened: evidence_module._OpenedRoot) -> None:
    assert opened.file_descriptor is not None
    assert opened.git_directory_fd is not None
    os.close(opened.git_directory_fd)
    os.close(opened.file_descriptor)


@pytest.mark.parametrize(
    (
        "arguments",
        "expected_operation",
        "returncode",
        "expected_kind",
        "expected_exit_code",
        "expected_signal",
    ),
    (
        (
            ("cat-file", "-t", "a" * 40),
            evidence_module.EvidenceGitOperation.OBJECT_TYPE,
            73,
            evidence_module.EvidenceProcessFailureKind.EXIT_NONZERO,
            73,
            None,
        ),
        (
            ("rev-parse", "--show-object-format=storage"),
            evidence_module.EvidenceGitOperation.OBJECT_FORMAT,
            -signal.SIGKILL,
            evidence_module.EvidenceProcessFailureKind.SIGNALLED,
            None,
            signal.SIGKILL,
        ),
    ),
)
def test_synthetic_git_termination_projects_an_exact_v2_occurrence(
    arguments: tuple[str, ...],
    expected_operation: evidence_module.EvidenceGitOperation,
    returncode: int,
    expected_kind: evidence_module.EvidenceProcessFailureKind,
    expected_exit_code: int | None,
    expected_signal: int | None,
) -> None:
    """Synthetic command results must supply, rather than invent, occurrence data."""

    stdout = b"partial\x00stdout\xff"
    stderr = b"\xffdiagnostic\x00tail"
    invocation_subject_hash = "a" * 64
    result = evidence_module._GitCommandResult(
        returncode,
        stdout,
        stderr,
        True,
        record_io_started=True,
        process_start_index=11,
        invocation_subject_hash=invocation_subject_hash,
        helper_handoff_state=evidence_module.EvidenceHelperHandoffState.UNKNOWN,
        helper_status_receipt=b"",
    )

    receipt = evidence_module._git_process_failure_receipt(
        result,
        arguments=arguments,
        ref="source:synthetic-termination",
        capture_ordinal=4,
    )

    assert receipt.operation is expected_operation
    assert receipt.stage is evidence_module.EvidenceProcessFailureStage.TERMINATION
    assert receipt.kind is expected_kind
    assert receipt.handoff_state is evidence_module.EvidenceHelperHandoffState.UNKNOWN
    assert receipt.ref == "source:synthetic-termination"
    assert receipt.capture_ordinal == 4
    assert receipt.process_start_index == 11
    assert receipt.invocation_subject_hash == invocation_subject_hash
    assert receipt.exit_code == expected_exit_code
    assert receipt.signal == expected_signal
    assert receipt.stdout_bytes == stdout
    assert receipt.stderr_bytes == stderr
    assert receipt.stdout_byte_length == len(stdout)
    assert receipt.stderr_byte_length == len(stderr)
    assert receipt.canonical_payload()["stdout_hex"] == stdout.hex()
    assert receipt.canonical_payload()["stderr_hex"] == stderr.hex()


def test_recurrence_signature_does_not_replace_occurrence_identity() -> None:
    first = evidence_module.EvidenceProcessFailureReceipt(
        operation=evidence_module.EvidenceGitOperation.OBJECT_CONTENT,
        stage=evidence_module.EvidenceProcessFailureStage.TERMINATION,
        kind=evidence_module.EvidenceProcessFailureKind.EXIT_NONZERO,
        handoff_state=evidence_module.EvidenceHelperHandoffState.UNKNOWN,
        ref="source:first-occurrence",
        capture_ordinal=2,
        process_start_index=5,
        invocation_subject_hash="b" * 64,
        exit_code=73,
        stdout_bytes=b"same\x00partial\xff",
        stderr_bytes=b"same\xffdiagnostic\x00",
    )
    later = replace(
        first,
        ref="source:later-occurrence",
        capture_ordinal=9,
        process_start_index=14,
    )

    assert later.signature_hash == first.signature_hash
    assert later.receipt_hash != first.receipt_hash
    assert later.stdout_bytes == first.stdout_bytes
    assert later.stderr_bytes == first.stderr_bytes


def test_versioned_helper_failure_frame_preserves_exact_operational_cause() -> None:
    assert _CHDIR_FAILURE_FRAME != b"1"
    assert len(_CHDIR_FAILURE_FRAME) <= select.PIPE_BUF

    observation = evidence_module._parse_git_helper_status_receipt(
        _CHDIR_FAILURE_FRAME,
        eof=True,
    )

    assert observation.protocol_version == _HELPER_STATUS_VERSION
    assert observation.protocol_valid is True
    assert observation.handoff_state is evidence_module.EvidenceHelperHandoffState.FAILED
    assert observation.failure_stage is evidence_module.EvidenceProcessFailureStage.HELPER_CHDIR
    assert observation.failure_kind is evidence_module.EvidenceProcessFailureKind.IO
    assert observation.mechanism_errno == errno.EIO
    assert observation.raw_receipt == _CHDIR_FAILURE_FRAME
    assert observation.permits_git_outcome_projection is False


@pytest.mark.parametrize(
    ("eof", "expected_state", "permits_projection"),
    (
        (False, evidence_module.EvidenceHelperHandoffState.PRE_EXEC, False),
        (True, evidence_module.EvidenceHelperHandoffState.CONFIRMED, True),
    ),
)
def test_pre_exec_frame_requires_eof_before_git_outcome_projection(
    eof: bool,
    expected_state: evidence_module.EvidenceHelperHandoffState,
    permits_projection: bool,
) -> None:
    assert len(_PRE_EXEC_FRAME) <= select.PIPE_BUF

    observation = evidence_module._parse_git_helper_status_receipt(
        _PRE_EXEC_FRAME,
        eof=eof,
    )

    assert observation.protocol_version == _HELPER_STATUS_VERSION
    assert observation.protocol_valid is True
    assert observation.handoff_state is expected_state
    assert observation.failure_stage is None
    assert observation.failure_kind is None
    assert observation.mechanism_errno is None
    assert observation.raw_receipt == _PRE_EXEC_FRAME
    assert observation.permits_git_outcome_projection is permits_projection


@pytest.mark.parametrize(
    "receipt",
    (
        b"",
        b"1",
        _PRE_EXEC_FRAME[:-2],
        _PRE_EXEC_FRAME.replace(b".v1", b".v2"),
    ),
    ids=("eof-before-pre-exec", "legacy-one-byte", "truncated", "unknown-version"),
)
def test_invalid_helper_status_is_protocol_uncertainty(
    receipt: bytes,
) -> None:
    observation = evidence_module._parse_git_helper_status_receipt(
        receipt,
        eof=True,
    )

    assert observation.protocol_valid is False
    assert observation.handoff_state is evidence_module.EvidenceHelperHandoffState.UNKNOWN
    assert observation.failure_stage is (
        evidence_module.EvidenceProcessFailureStage.HELPER_STATUS_READ
    )
    assert observation.failure_kind is (
        evidence_module.EvidenceProcessFailureKind.PROTOCOL_INVALID
    )
    assert observation.mechanism_errno is None
    assert observation.raw_receipt == receipt
    assert observation.permits_git_outcome_projection is False


def test_pre_exec_then_exec_failure_is_one_valid_ordered_status_receipt() -> None:
    receipt = _PRE_EXEC_FRAME + _EXEC_ACCESS_FAILURE_FRAME

    observation = evidence_module._parse_git_helper_status_receipt(
        receipt,
        eof=True,
    )

    assert observation.protocol_valid is True
    assert observation.handoff_state is evidence_module.EvidenceHelperHandoffState.FAILED
    assert observation.failure_stage is evidence_module.EvidenceProcessFailureStage.HELPER_EXEC
    assert observation.failure_kind is (
        evidence_module.EvidenceProcessFailureKind.ACCESS_POLICY
    )
    assert observation.mechanism_errno == errno.EACCES
    assert observation.raw_receipt == receipt
    assert observation.permits_git_outcome_projection is False


def test_bound_helper_source_is_valid_isolated_python() -> None:
    compiled = compile(
        evidence_module._GIT_FD_EXEC_HELPER,
        "<orion-protected-git-helper>",
        "exec",
        dont_inherit=True,
    )

    assert compiled.co_names


def test_single_exec_failure_without_pre_exec_is_protocol_uncertainty() -> None:
    observation = evidence_module._parse_git_helper_status_receipt(
        _EXEC_ACCESS_FAILURE_FRAME,
        eof=True,
    )

    _assert_protocol_uncertainty(observation, _EXEC_ACCESS_FAILURE_FRAME)


@pytest.mark.parametrize(
    "receipt",
    (
        _PRE_EXEC_FRAME + _PRE_EXEC_FRAME,
        _CHDIR_FAILURE_FRAME + _PRE_EXEC_FRAME,
        _PRE_EXEC_FRAME + _CHDIR_FAILURE_FRAME,
    ),
    ids=("duplicate-pre-exec", "failure-then-pre-exec", "pre-exec-then-non-exec"),
)
def test_out_of_order_helper_frame_sequences_are_protocol_uncertainty(
    receipt: bytes,
) -> None:
    observation = evidence_module._parse_git_helper_status_receipt(
        receipt,
        eof=True,
    )

    _assert_protocol_uncertainty(observation, receipt)


@pytest.mark.parametrize(
    "receipt",
    (
        _CHDIR_FAILURE_FRAME.replace(b'"errno":5', b'"errno":5.0'),
        _CHDIR_FAILURE_FRAME.replace(b'"errno":5', b'"errno":NaN'),
        _CHDIR_FAILURE_FRAME.replace(b'"errno":5', b'"errno":true'),
        _CHDIR_FAILURE_FRAME.replace(b'"errno":5', b'"errno":"5"'),
        _CHDIR_FAILURE_FRAME.replace(
            b'"errno":5',
            b'"errno":5,"errno":5',
        ),
    ),
    ids=("float", "nan", "bool", "string-int", "duplicate-field"),
)
def test_helper_frame_rejects_non_exact_integer_and_duplicate_fields(
    receipt: bytes,
) -> None:
    observation = evidence_module._parse_git_helper_status_receipt(
        receipt,
        eof=True,
    )

    _assert_protocol_uncertainty(observation, receipt)


def test_helper_frame_and_receipt_caps_are_exact_boundaries() -> None:
    frame_limit = evidence_module._GIT_HELPER_STATUS_FRAME_LIMIT
    receipt_limit = evidence_module._GIT_HELPER_STATUS_RECEIPT_LIMIT
    acquisition_limit = evidence_module._GIT_HELPER_STATUS_ACQUISITION_LIMIT

    assert frame_limit == _PORTABLE_HELPER_FRAME_LIMIT
    assert frame_limit <= select.PIPE_BUF
    assert receipt_limit == 2 * frame_limit
    assert acquisition_limit == receipt_limit + 1
    assert len(_PRE_EXEC_FRAME) <= frame_limit
    assert len(_EXEC_ACCESS_FAILURE_FRAME) <= frame_limit

    overlong_frame = b"x" * frame_limit + b"\n"
    frame_observation = evidence_module._parse_git_helper_status_receipt(
        overlong_frame,
        eof=True,
    )
    _assert_protocol_uncertainty(frame_observation, overlong_frame)

    exact_cap = b"x" * (receipt_limit - 1) + b"\n"
    cap_observation = evidence_module._parse_git_helper_status_receipt(
        exact_cap,
        eof=True,
    )
    _assert_protocol_uncertainty(cap_observation, exact_cap)

    sentinel_observation = evidence_module._parse_git_helper_status_receipt(
        exact_cap + b"x",
        eof=True,
    )
    _assert_protocol_uncertainty(sentinel_observation, exact_cap + b"x")

    with pytest.raises(ValueError, match="acquisition cap"):
        evidence_module._parse_git_helper_status_receipt(
            exact_cap + b"xx",
            eof=True,
        )


def test_eof_before_pre_exec_is_exact_protocol_uncertainty() -> None:
    observation = evidence_module._parse_git_helper_status_receipt(
        b"",
        eof=True,
    )

    _assert_protocol_uncertainty(observation, b"")


def test_bound_helper_source_emits_pre_exec_frame_before_successful_exec(
    tmp_path: Path,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    executable = Path(os.path.realpath(sys.executable))

    returncode, status = _execute_bound_helper_source(
        root,
        executable,
        "-c",
        "pass",
    )

    assert returncode == 0
    assert status == _PRE_EXEC_FRAME


def test_bound_helper_source_emits_exact_exec_failure_after_pre_exec(
    tmp_path: Path,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    non_executable = tmp_path / "not-executable"
    non_executable.write_bytes(b"not an executable image")
    non_executable.chmod(0o644)

    returncode, status = _execute_bound_helper_source(root, non_executable)

    assert returncode == 126
    assert status == _PRE_EXEC_FRAME + _EXEC_ACCESS_FAILURE_FRAME


def test_bound_helper_source_emits_exact_root_attestation_failure_stage(
    tmp_path: Path,
) -> None:
    not_a_directory = tmp_path / "not-a-directory"
    not_a_directory.write_bytes(b"root descriptor has the wrong kind")
    executable = Path(os.path.realpath(sys.executable))

    returncode, status = _execute_bound_helper_source(
        not_a_directory,
        executable,
        "-c",
        "pass",
    )

    assert returncode == 126
    assert status == _ROOT_ATTESTATION_FAILURE_FRAME


def test_parent_observes_pre_exec_status_before_waiting_for_child(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened = _open_test_git_root(tmp_path / "repo")
    monkeypatch.setattr(
        evidence_module,
        "_GIT_EXECUTABLE",
        os.path.realpath(sys.executable),
    )
    monkeypatch.setattr(
        evidence_module,
        "_GIT_FD_EXEC_HELPER",
        (
            "import os, sys\n"
            "status_fd = int(sys.argv[4])\n"
            f"os.write(status_fd, {_PRE_EXEC_FRAME!r})\n"
            "os.close(status_fd)\n"
            "os.write(1, b'sha1\\n')\n"
            "os._exit(0)"
        ),
    )
    real_pipe = evidence_module.os.pipe
    real_read = evidence_module.os.read
    real_popen = evidence_module.subprocess.Popen
    status_read_fd: int | None = None
    status_read_observed = False

    def recording_pipe() -> tuple[int, int]:
        nonlocal status_read_fd
        descriptors = real_pipe()
        if status_read_fd is None:
            status_read_fd = descriptors[0]
        return descriptors

    def recording_read(file_descriptor: int, size: int) -> bytes:
        nonlocal status_read_observed
        if file_descriptor == status_read_fd:
            status_read_observed = True
        return real_read(file_descriptor, size)

    class WaitOrderProcess:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self._process = real_popen(*args, **kwargs)

        def __getattr__(self, name: str) -> object:
            return getattr(self._process, name)

        def wait(self, *args: object, **kwargs: object) -> int:
            assert status_read_observed, (
                "parent waited before observing the helper-status channel"
            )
            return self._process.wait(*args, **kwargs)

    monkeypatch.setattr(evidence_module.os, "pipe", recording_pipe)
    monkeypatch.setattr(evidence_module.os, "read", recording_read)
    monkeypatch.setattr(evidence_module.subprocess, "Popen", WaitOrderProcess)
    try:
        result = evidence_module._run_protected_git(
            opened,
            "rev-parse",
            "--show-object-format=storage",
            ref="source:concurrent-helper-status",
            ordinal=0,
        )
    finally:
        _close_test_git_root(opened)

    assert result.returncode == 0
    assert result.helper_handoff_state is (
        evidence_module.EvidenceHelperHandoffState.CONFIRMED
    )
    assert result.helper_status_receipt == _PRE_EXEC_FRAME


@pytest.mark.parametrize(
    "status_receipt",
    (
        b"",
        b"1",
        b'{"malformed":true}\n',
        _THIRD_FRAME_STATUS,
        _OVERSIZED_FRAME_STATUS,
        _TOTAL_CAP_SENTINEL_STATUS,
    ),
    ids=(
        "empty",
        "legacy-one-byte",
        "malformed-frame",
        "third-frame",
        "oversized-frame",
        "total-cap-plus-sentinel",
    ),
)
def test_zero_exit_with_unconfirmed_helper_status_cannot_project_git_outcome(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    status_receipt: bytes,
) -> None:
    opened = _open_test_git_root(tmp_path / "repo")
    monkeypatch.setattr(
        evidence_module,
        "_GIT_EXECUTABLE",
        os.path.realpath(sys.executable),
    )
    status_write = (
        "" if not status_receipt else f"os.write(status_fd, {status_receipt!r})\n"
    )
    monkeypatch.setattr(
        evidence_module,
        "_GIT_FD_EXEC_HELPER",
        (
            "import os, sys\n"
            "status_fd = int(sys.argv[4])\n"
            f"{status_write}"
            "os.close(status_fd)\n"
            "os.write(1, b'sha1\\n')\n"
            "os._exit(0)"
        ),
    )
    try:
        result = evidence_module._run_protected_git(
            opened,
            "rev-parse",
            "--show-object-format=storage",
            ref="source:unconfirmed-helper-status",
            ordinal=0,
        )
    finally:
        _close_test_git_root(opened)

    assert result.returncode is None
    assert result.mechanism_limitation is (
        evidence_module.EvidenceMechanismLimitationKind.PROTOCOL
    )
    assert result.helper_handoff_state is (
        evidence_module.EvidenceHelperHandoffState.UNKNOWN
    )
    assert result.helper_status_receipt == status_receipt
    assert result.process_failure is not None
    receipt = result.process_failure
    assert receipt.operation is evidence_module.EvidenceGitOperation.OBJECT_FORMAT
    assert receipt.stage is (
        evidence_module.EvidenceProcessFailureStage.HELPER_STATUS_READ
    )
    assert receipt.kind is (
        evidence_module.EvidenceProcessFailureKind.PROTOCOL_INVALID
    )
    assert receipt.handoff_state is evidence_module.EvidenceHelperHandoffState.UNKNOWN
    assert receipt.ref == "source:unconfirmed-helper-status"
    assert receipt.capture_ordinal == 0
    assert receipt.process_start_index == 1
    assert receipt.invocation_subject_hash == result.invocation_subject_hash
    assert receipt.mechanism_errno is None
    assert receipt.helper_status_receipt == status_receipt
    assert receipt.stdout_bytes == b"sha1\n"
    assert receipt.stderr_bytes == b""
