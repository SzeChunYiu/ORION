from __future__ import annotations

import errno
import os
from pathlib import Path
import selectors
import sys
from typing import Callable

import pytest

from orion.kernel import evidence as evidence_module


# Frozen product state for this atom:
# Q = (phase, registered streams, status bytes, stdout bytes, stderr bytes,
#      consecutive empty selects, first primary failure).
# Only the first primary selector/read failure is projected. Cleanup is currently
# best-effort and cannot replace it. No state in this product grants Git outcome
# projection or scientific authority.
_SELECTOR_PRODUCT_STATE_CONTRACT = (
    "phase",
    "registered_status_stdout_stderr",
    "bounded_status_bytes",
    "bounded_stdout_bytes",
    "bounded_stderr_bytes",
    "consecutive_empty_selects",
    "first_primary_failure",
)

_PRE_EXEC_FRAME = (
    b'{"errno":null,"kind":null,"stage":"HELPER_PRE_EXEC",'
    b'"version":"orion.git-helper-status.v1"}\n'
)
_PARTIAL_STDOUT = b"partial-out\xff"
_PARTIAL_STDERR = b"partial-err\x00"


def test_selector_product_state_contract_is_frozen() -> None:
    assert _SELECTOR_PRODUCT_STATE_CONTRACT == (
        "phase",
        "registered_status_stdout_stderr",
        "bounded_status_bytes",
        "bounded_stdout_bytes",
        "bounded_stderr_bytes",
        "consecutive_empty_selects",
        "first_primary_failure",
    )


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


def _helper_source(*, linger: bool) -> str:
    suffix = "import time; time.sleep(10)" if linger else "os._exit(0)"
    return (
        "import os, sys\n"
        "status_fd = int(sys.argv[4])\n"
        f"os.write(status_fd, {_PRE_EXEC_FRAME!r})\n"
        "os.close(status_fd)\n"
        f"os.write(1, {_PARTIAL_STDOUT!r})\n"
        f"os.write(2, {_PARTIAL_STDERR!r})\n"
        f"{suffix}"
    )


def _run_probe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    linger: bool,
) -> evidence_module._GitCommandResult:
    opened = _open_test_git_root(tmp_path / "repo")
    monkeypatch.setattr(
        evidence_module,
        "_GIT_EXECUTABLE",
        os.path.realpath(sys.executable),
    )
    monkeypatch.setattr(
        evidence_module,
        "_GIT_FD_EXEC_HELPER",
        _helper_source(linger=linger),
    )
    try:
        return evidence_module._run_protected_git(
            opened,
            "rev-parse",
            "--show-object-format=storage",
            ref="source:selector-lifecycle",
            ordinal=3,
            timeout_seconds=2,
        )
    finally:
        _close_test_git_root(opened)


def _assert_primary_failure(
    result: evidence_module._GitCommandResult,
    *,
    stage: evidence_module.EvidenceProcessFailureStage,
    kind: evidence_module.EvidenceProcessFailureKind,
    error_number: int | None,
    stdout: bytes = b"",
    stderr: bytes = b"",
    handoff_state: evidence_module.EvidenceHelperHandoffState = (
        evidence_module.EvidenceHelperHandoffState.UNKNOWN
    ),
    helper_status_receipt: bytes = b"",
) -> None:
    assert result.returncode is None
    assert result.timed_out is False
    assert result.mechanism_limitation is (
        evidence_module.EvidenceMechanismLimitationKind.PROCESS_IO
    )
    assert result.process_failure is not None
    receipt = result.process_failure
    assert receipt.operation is evidence_module.EvidenceGitOperation.OBJECT_FORMAT
    assert receipt.stage is stage
    assert receipt.kind is kind
    assert receipt.ref == "source:selector-lifecycle"
    assert receipt.capture_ordinal == 3
    assert receipt.process_start_index == 1
    assert receipt.invocation_subject_hash == result.invocation_subject_hash
    assert receipt.mechanism_errno == error_number
    assert receipt.handoff_state is handoff_state
    assert receipt.helper_status_receipt == helper_status_receipt
    assert receipt.stdout_bytes == stdout
    assert receipt.stderr_bytes == stderr
    assert result.helper_handoff_state is handoff_state
    assert result.helper_status_receipt == helper_status_receipt
    phases = tuple(item.phase for item in result.root_observation_occurrences)
    assert phases == (
        evidence_module.EvidenceRootObservationPhase.PRE,
        evidence_module.EvidenceRootObservationPhase.POST,
    )


def test_default_selector_creation_oserror_is_exact_primary_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_selector_creation() -> selectors.BaseSelector:
        raise OSError(errno.EIO, "simulated selector creation failure")

    monkeypatch.setattr(
        evidence_module.selectors,
        "DefaultSelector",
        fail_selector_creation,
    )

    result = _run_probe(tmp_path, monkeypatch, linger=True)

    _assert_primary_failure(
        result,
        stage=evidence_module.EvidenceProcessFailureStage.SELECTOR_CREATE,
        kind=evidence_module.EvidenceProcessFailureKind.IO,
        error_number=errno.EIO,
    )


@pytest.mark.parametrize(
    ("failed_registration", "target"),
    ((1, "status"), (2, "stdout"), (3, "stderr")),
)
def test_each_selector_registration_oserror_is_exact_primary_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failed_registration: int,
    target: str,
) -> None:
    real_factory = evidence_module.selectors.DefaultSelector

    class RegisterFailureSelector:
        def __init__(self) -> None:
            self._selector = real_factory()
            self._count = 0

        def register(
            self,
            fileobj: object,
            events: int,
            data: object = None,
        ) -> selectors.SelectorKey:
            self._count += 1
            assert data == ("status", "stdout", "stderr")[self._count - 1]
            if self._count == failed_registration:
                raise OSError(errno.EIO, f"simulated {target} register failure")
            return self._selector.register(fileobj, events, data)

        def __getattr__(self, name: str) -> object:
            return getattr(self._selector, name)

    monkeypatch.setattr(
        evidence_module.selectors,
        "DefaultSelector",
        RegisterFailureSelector,
    )

    result = _run_probe(tmp_path, monkeypatch, linger=True)

    _assert_primary_failure(
        result,
        stage=evidence_module.EvidenceProcessFailureStage.SELECTOR_REGISTER,
        kind=evidence_module.EvidenceProcessFailureKind.IO,
        error_number=errno.EIO,
    )


class _DelegatingSelector:
    def __init__(
        self,
        factory: Callable[[], selectors.BaseSelector],
        select_effects: list[object],
    ) -> None:
        self._selector = factory()
        self._select_effects = select_effects
        self.select_calls = 0

    def register(
        self,
        fileobj: object,
        events: int,
        data: object = None,
    ) -> selectors.SelectorKey:
        return self._selector.register(fileobj, events, data)

    def select(self, timeout: float | None = None) -> list[tuple[selectors.SelectorKey, int]]:
        self.select_calls += 1
        if self._select_effects:
            effect = self._select_effects.pop(0)
            if isinstance(effect, BaseException):
                raise effect
            if effect == "EMPTY":
                return []
        return self._selector.select(timeout)

    def __getattr__(self, name: str) -> object:
        return getattr(self._selector, name)


def test_selector_select_eintr_retries_and_preserves_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_factory = evidence_module.selectors.DefaultSelector
    selected: _DelegatingSelector | None = None

    def factory() -> _DelegatingSelector:
        nonlocal selected
        selected = _DelegatingSelector(
            real_factory,
            [OSError(errno.EINTR, "simulated interrupted select")],
        )
        return selected

    monkeypatch.setattr(evidence_module.selectors, "DefaultSelector", factory)

    result = _run_probe(tmp_path, monkeypatch, linger=False)

    assert selected is not None
    assert selected.select_calls >= 2
    assert result.returncode == 0
    assert result.process_failure is None
    assert result.timed_out is False
    assert result.stdout == _PARTIAL_STDOUT
    assert result.stderr == _PARTIAL_STDERR
    assert result.helper_handoff_state is (
        evidence_module.EvidenceHelperHandoffState.CONFIRMED
    )


@pytest.mark.parametrize(
    ("error_number", "kind"),
    (
        (errno.EIO, evidence_module.EvidenceProcessFailureKind.IO),
        (
            errno.EBADF,
            evidence_module.EvidenceProcessFailureKind.DESCRIPTOR_INVALID,
        ),
    ),
)
def test_selector_select_terminal_oserror_is_exact_primary_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error_number: int,
    kind: evidence_module.EvidenceProcessFailureKind,
) -> None:
    real_factory = evidence_module.selectors.DefaultSelector

    def factory() -> _DelegatingSelector:
        return _DelegatingSelector(
            real_factory,
            [OSError(error_number, "simulated terminal select failure")],
        )

    monkeypatch.setattr(evidence_module.selectors, "DefaultSelector", factory)

    result = _run_probe(tmp_path, monkeypatch, linger=True)

    _assert_primary_failure(
        result,
        stage=evidence_module.EvidenceProcessFailureStage.SELECT,
        kind=kind,
        error_number=error_number,
    )


def test_early_empty_select_before_deadline_retries_instead_of_timeout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_factory = evidence_module.selectors.DefaultSelector
    selected: _DelegatingSelector | None = None

    def factory() -> _DelegatingSelector:
        nonlocal selected
        selected = _DelegatingSelector(real_factory, ["EMPTY"])
        return selected

    monkeypatch.setattr(evidence_module.selectors, "DefaultSelector", factory)

    result = _run_probe(tmp_path, monkeypatch, linger=False)

    assert selected is not None
    assert selected.select_calls >= 2
    assert result.returncode == 0
    assert result.timed_out is False
    assert result.process_failure is None


def test_repeated_early_empty_selects_have_finite_non_timeout_bound(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    retry_limit = evidence_module._GIT_SELECTOR_EMPTY_RETRY_LIMIT
    assert 1 <= retry_limit <= 64
    real_factory = evidence_module.selectors.DefaultSelector
    selected: _DelegatingSelector | None = None

    def factory() -> _DelegatingSelector:
        nonlocal selected
        selected = _DelegatingSelector(
            real_factory,
            ["EMPTY"] * retry_limit,
        )
        return selected

    monkeypatch.setattr(evidence_module.selectors, "DefaultSelector", factory)

    result = _run_probe(tmp_path, monkeypatch, linger=True)

    assert selected is not None
    assert selected.select_calls == retry_limit
    _assert_primary_failure(
        result,
        stage=evidence_module.EvidenceProcessFailureStage.SELECT,
        kind=evidence_module.EvidenceProcessFailureKind.PROTOCOL_INVALID,
        error_number=None,
    )


class _ScriptedBatchSelector:
    def __init__(
        self,
        *,
        terminal_select_errno: int | None = None,
        later_ready_stream: str | None = None,
    ) -> None:
        self._keys: dict[int, selectors.SelectorKey] = {}
        self.calls = 0
        self.terminal_select_errno = terminal_select_errno
        self.later_ready_stream = later_ready_stream

    def register(
        self,
        fileobj: object,
        events: int,
        data: object = None,
    ) -> selectors.SelectorKey:
        fd = fileobj if isinstance(fileobj, int) else fileobj.fileno()  # type: ignore[attr-defined]
        key = selectors.SelectorKey(fileobj, fd, events, data)
        self._keys[fd] = key
        return key

    def unregister(self, fileobj: object) -> selectors.SelectorKey:
        fd = fileobj if isinstance(fileobj, int) else fileobj.fileno()  # type: ignore[attr-defined]
        return self._keys.pop(fd)

    def get_map(self) -> dict[int, selectors.SelectorKey]:
        return self._keys

    def select(self, timeout: float | None = None) -> list[tuple[selectors.SelectorKey, int]]:
        del timeout
        self.calls += 1
        if self.calls == 2 and self.terminal_select_errno is not None:
            raise OSError(self.terminal_select_errno, "scripted second select failure")
        keys = tuple(self._keys.values())
        if self.calls >= 2 and self.later_ready_stream is not None:
            keys = tuple(
                key for key in keys if key.data == self.later_ready_stream
            )
        return [
            (key, selectors.EVENT_READ)
            for key in reversed(keys)
        ]

    def close(self) -> None:
        self._keys.clear()


@pytest.mark.parametrize(
    ("target", "expected_stage", "error_number", "expected_kind"),
    (
        pytest.param(
            target,
            stage,
            error_number,
            kind,
            id=f"{target}-{kind.value.lower()}",
        )
        for target, stage in (
            (
                "status",
                evidence_module.EvidenceProcessFailureStage.HELPER_STATUS_READ,
            ),
            ("stdout", evidence_module.EvidenceProcessFailureStage.STDOUT_READ),
            ("stderr", evidence_module.EvidenceProcessFailureStage.STDERR_READ),
        )
        for error_number, kind in (
            (errno.EIO, evidence_module.EvidenceProcessFailureKind.IO),
            (
                errno.EBADF,
                evidence_module.EvidenceProcessFailureKind.DESCRIPTOR_INVALID,
            ),
        )
    ),
)
def test_each_stream_terminal_read_error_retains_observed_state_and_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
    expected_stage: evidence_module.EvidenceProcessFailureStage,
    error_number: int,
    expected_kind: evidence_module.EvidenceProcessFailureKind,
) -> None:
    selected = _ScriptedBatchSelector(later_ready_stream=target)
    monkeypatch.setattr(
        evidence_module.selectors,
        "DefaultSelector",
        lambda: selected,
    )
    real_read = evidence_module.os.read
    by_fd: dict[int, str] = {}
    reads: dict[str, int] = {"status": 0, "stdout": 0, "stderr": 0}

    original_register = selected.register

    def recording_register(
        fileobj: object,
        events: int,
        data: object = None,
    ) -> selectors.SelectorKey:
        key = original_register(fileobj, events, data)
        assert isinstance(data, str)
        by_fd[key.fd] = data
        return key

    selected.register = recording_register  # type: ignore[method-assign]

    def scripted_read(file_descriptor: int, size: int) -> bytes:
        stream = by_fd.get(file_descriptor)
        if stream is None:
            return real_read(file_descriptor, size)
        reads[stream] += 1
        if reads[stream] == 2 and stream == target:
            raise OSError(
                error_number,
                f"simulated {stream} read failure",
            )
        if reads[stream] == 1:
            return {
                "status": _PRE_EXEC_FRAME,
                "stdout": _PARTIAL_STDOUT,
                "stderr": _PARTIAL_STDERR,
            }[stream]
        return b""

    monkeypatch.setattr(evidence_module.os, "read", scripted_read)

    result = _run_probe(tmp_path, monkeypatch, linger=True)

    _assert_primary_failure(
        result,
        stage=expected_stage,
        kind=expected_kind,
        error_number=error_number,
        stdout=_PARTIAL_STDOUT,
        stderr=_PARTIAL_STDERR,
        handoff_state=evidence_module.EvidenceHelperHandoffState.PRE_EXEC,
        helper_status_receipt=_PRE_EXEC_FRAME,
    )


@pytest.mark.parametrize("target", ("status", "stdout", "stderr"))
def test_each_stream_single_read_eintr_retries_and_preserves_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
) -> None:
    selected = _ScriptedBatchSelector()
    monkeypatch.setattr(
        evidence_module.selectors,
        "DefaultSelector",
        lambda: selected,
    )
    real_read = evidence_module.os.read
    by_fd: dict[int, str] = {}
    reads: dict[str, int] = {"status": 0, "stdout": 0, "stderr": 0}
    original_register = selected.register

    def recording_register(
        fileobj: object,
        events: int,
        data: object = None,
    ) -> selectors.SelectorKey:
        key = original_register(fileobj, events, data)
        assert isinstance(data, str)
        by_fd[key.fd] = data
        return key

    selected.register = recording_register  # type: ignore[method-assign]

    def scripted_read(file_descriptor: int, size: int) -> bytes:
        stream = by_fd.get(file_descriptor)
        if stream is None:
            return real_read(file_descriptor, size)
        reads[stream] += 1
        if reads[stream] == 1 and stream == target:
            raise OSError(errno.EINTR, f"simulated {stream} read interruption")
        successful_read = reads[stream] == (2 if stream == target else 1)
        if successful_read:
            return {
                "status": _PRE_EXEC_FRAME,
                "stdout": _PARTIAL_STDOUT,
                "stderr": _PARTIAL_STDERR,
            }[stream]
        return b""

    monkeypatch.setattr(evidence_module.os, "read", scripted_read)

    result = _run_probe(tmp_path, monkeypatch, linger=False)

    assert reads[target] >= 2
    assert result.returncode == 0
    assert result.process_failure is None
    assert result.timed_out is False
    assert result.stdout == _PARTIAL_STDOUT
    assert result.stderr == _PARTIAL_STDERR
    assert result.helper_handoff_state is (
        evidence_module.EvidenceHelperHandoffState.CONFIRMED
    )
    assert result.helper_status_receipt == _PRE_EXEC_FRAME


@pytest.mark.parametrize(
    ("target", "expected_stage"),
    (
        (
            "status",
            evidence_module.EvidenceProcessFailureStage.HELPER_STATUS_READ,
        ),
        ("stdout", evidence_module.EvidenceProcessFailureStage.STDOUT_READ),
        ("stderr", evidence_module.EvidenceProcessFailureStage.STDERR_READ),
    ),
)
def test_each_stream_repeated_read_eintr_has_finite_typed_bound(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
    expected_stage: evidence_module.EvidenceProcessFailureStage,
) -> None:
    retry_limit = evidence_module._GIT_STREAM_READ_EINTR_RETRY_LIMIT
    assert 1 <= retry_limit <= 64
    selected = _ScriptedBatchSelector(later_ready_stream=target)
    monkeypatch.setattr(
        evidence_module.selectors,
        "DefaultSelector",
        lambda: selected,
    )
    real_read = evidence_module.os.read
    by_fd: dict[int, str] = {}
    reads: dict[str, int] = {"status": 0, "stdout": 0, "stderr": 0}
    interruptions = 0
    original_register = selected.register

    def recording_register(
        fileobj: object,
        events: int,
        data: object = None,
    ) -> selectors.SelectorKey:
        key = original_register(fileobj, events, data)
        assert isinstance(data, str)
        by_fd[key.fd] = data
        return key

    selected.register = recording_register  # type: ignore[method-assign]

    def scripted_read(file_descriptor: int, size: int) -> bytes:
        nonlocal interruptions
        stream = by_fd.get(file_descriptor)
        if stream is None:
            return real_read(file_descriptor, size)
        reads[stream] += 1
        if reads[stream] == 1:
            return {
                "status": _PRE_EXEC_FRAME,
                "stdout": _PARTIAL_STDOUT,
                "stderr": _PARTIAL_STDERR,
            }[stream]
        assert stream == target
        interruptions += 1
        if interruptions > retry_limit:
            raise RuntimeError("read EINTR retry exceeded its frozen bound")
        raise OSError(errno.EINTR, f"simulated {stream} read interruption")

    monkeypatch.setattr(evidence_module.os, "read", scripted_read)

    result = _run_probe(tmp_path, monkeypatch, linger=True)

    assert interruptions == retry_limit
    _assert_primary_failure(
        result,
        stage=expected_stage,
        kind=evidence_module.EvidenceProcessFailureKind.INTERRUPTED,
        error_number=errno.EINTR,
        stdout=_PARTIAL_STDOUT,
        stderr=_PARTIAL_STDERR,
        handoff_state=evidence_module.EvidenceHelperHandoffState.PRE_EXEC,
        helper_status_receipt=_PRE_EXEC_FRAME,
    )


def test_ready_batch_is_processed_status_then_stdout_then_stderr(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selected = _ScriptedBatchSelector(terminal_select_errno=errno.EIO)
    monkeypatch.setattr(
        evidence_module.selectors,
        "DefaultSelector",
        lambda: selected,
    )
    real_read = evidence_module.os.read
    by_fd: dict[int, str] = {}
    read_order: list[str] = []
    original_register = selected.register

    def recording_register(
        fileobj: object,
        events: int,
        data: object = None,
    ) -> selectors.SelectorKey:
        key = original_register(fileobj, events, data)
        assert isinstance(data, str)
        by_fd[key.fd] = data
        return key

    selected.register = recording_register  # type: ignore[method-assign]

    def recording_read(file_descriptor: int, size: int) -> bytes:
        stream = by_fd.get(file_descriptor)
        if stream is None:
            return real_read(file_descriptor, size)
        read_order.append(stream)
        return {
            "status": _PRE_EXEC_FRAME,
            "stdout": _PARTIAL_STDOUT,
            "stderr": _PARTIAL_STDERR,
        }[stream]

    monkeypatch.setattr(evidence_module.os, "read", recording_read)

    result = _run_probe(tmp_path, monkeypatch, linger=True)

    assert read_order[:3] == ["status", "stdout", "stderr"]
    _assert_primary_failure(
        result,
        stage=evidence_module.EvidenceProcessFailureStage.SELECT,
        kind=evidence_module.EvidenceProcessFailureKind.IO,
        error_number=errno.EIO,
        stdout=_PARTIAL_STDOUT,
        stderr=_PARTIAL_STDERR,
        handoff_state=evidence_module.EvidenceHelperHandoffState.PRE_EXEC,
        helper_status_receipt=_PRE_EXEC_FRAME,
    )


@pytest.mark.xfail(
    strict=True,
    reason="cleanup/reap atom must move POST after the complete cleanup traversal",
)
def test_post_root_occurrence_follows_selector_cleanup_traversal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    selected = _ScriptedBatchSelector(terminal_select_errno=errno.EIO)
    selected.calls = 1
    real_close = selected.close

    def recording_close() -> None:
        events.append("selector-close")
        real_close()

    selected.close = recording_close  # type: ignore[method-assign]
    monkeypatch.setattr(
        evidence_module.selectors,
        "DefaultSelector",
        lambda: selected,
    )
    real_probe = evidence_module._root_descriptor_matches
    root_calls = 0

    def recording_root_probe(
        opened_root: evidence_module._OpenedRoot,
        **kwargs: object,
    ) -> evidence_module._RootDescriptorObservation:
        nonlocal root_calls
        root_calls += 1
        observation = real_probe(opened_root, **kwargs)
        events.append("pre-root" if root_calls == 1 else "post-root")
        return observation

    monkeypatch.setattr(
        evidence_module,
        "_root_descriptor_matches",
        recording_root_probe,
    )

    result = _run_probe(tmp_path, monkeypatch, linger=True)

    assert result.process_failure is not None
    assert events.index("selector-close") < events.index("post-root")
