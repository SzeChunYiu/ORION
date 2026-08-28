from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import errno
import os
from pathlib import Path
import selectors
import time
from typing import Callable

import pytest

from orion.kernel import evidence as evidence_module


_CHANNELS = ("status", "stdout", "stderr")
_SELECTOR_RETRY_COORDINATES = ("eintr", "early_empty")
_STREAM_RETRY_COORDINATES = ("read_eintr", "readiness_race")
_PRE_EXEC_FRAME = (
    b'{"errno":null,"kind":null,"stage":"HELPER_PRE_EXEC",'
    b'"version":"orion.git-helper-status.v1"}\n'
)
_PARTIAL_STDOUT = b"partial-out\xff"
_PARTIAL_STDERR = b"partial-err\x00"
_BOUND = 8


def test_provisional_nonblocking_product_coordinates_are_frozen() -> None:
    assert evidence_module._GIT_IO_CHANNELS == _CHANNELS
    assert (
        evidence_module._GIT_SELECTOR_RETRY_COORDINATES
        == _SELECTOR_RETRY_COORDINATES
    )
    assert (
        evidence_module._GIT_STREAM_RETRY_COORDINATES
        == _STREAM_RETRY_COORDINATES
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


def _helper_source(
    *,
    stdout: bytes = _PARTIAL_STDOUT,
    stderr: bytes = _PARTIAL_STDERR,
    linger: bool,
) -> str:
    suffix = "import time; time.sleep(10)" if linger else "os._exit(0)"
    return (
        "import os, sys\n"
        "status_fd = int(sys.argv[4])\n"
        f"os.write(status_fd, {_PRE_EXEC_FRAME!r})\n"
        "os.close(status_fd)\n"
        f"os.write(1, {stdout!r})\n"
        f"os.write(2, {stderr!r})\n"
        f"{suffix}"
    )


def _run_probe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    stdout: bytes = _PARTIAL_STDOUT,
    stderr: bytes = _PARTIAL_STDERR,
    linger: bool,
    stdout_limit: int = 4_096,
    stderr_limit: int = 4_096,
    combined_limit: int = 8_192,
    opened: evidence_module._OpenedRoot | None = None,
    work_ledger: evidence_module._EvidenceWorkLedger | None = None,
    stdout_secondary_work_dimension: str | None = None,
    helper_source: str | None = None,
    timeout_seconds: float = 2,
) -> evidence_module._GitCommandResult:
    owned_opened = opened is None
    if opened is None:
        opened = _open_test_git_root(tmp_path / "repo")
    monkeypatch.setattr(
        evidence_module,
        "_GIT_EXECUTABLE",
        evidence_module._GIT_FD_HELPER_EXECUTABLE,
    )
    monkeypatch.setattr(
        evidence_module,
        "_GIT_FD_EXEC_HELPER",
        (
            helper_source
            if helper_source is not None
            else _helper_source(stdout=stdout, stderr=stderr, linger=linger)
        ),
    )
    try:
        return evidence_module._run_protected_git(
            opened,
            "rev-parse",
            "--show-object-format=storage",
            stdout_limit=stdout_limit,
            stderr_limit=stderr_limit,
            combined_limit=combined_limit,
            ref="source:nonblocking-output",
            ordinal=4,
            timeout_seconds=timeout_seconds,
            work_ledger=work_ledger,
            stdout_secondary_work_dimension=stdout_secondary_work_dimension,
        )
    finally:
        if owned_opened:
            _close_test_git_root(opened)


def _assert_root_pair(result: evidence_module._GitCommandResult) -> None:
    assert tuple(
        occurrence.phase for occurrence in result.root_observation_occurrences
    ) == (
        evidence_module.EvidenceRootObservationPhase.PRE,
        evidence_module.EvidenceRootObservationPhase.POST,
    )


def _assert_primary_failure(
    result: evidence_module._GitCommandResult,
    *,
    stage: evidence_module.EvidenceProcessFailureStage,
    kind: evidence_module.EvidenceProcessFailureKind,
    error_number: int,
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
    assert receipt.stage is stage
    assert receipt.kind is kind
    assert receipt.mechanism_errno == error_number
    assert receipt.handoff_state is handoff_state
    assert receipt.helper_status_receipt == helper_status_receipt
    assert receipt.stdout_bytes == stdout
    assert receipt.stderr_bytes == stderr
    assert result.helper_handoff_state is handoff_state
    assert result.helper_status_receipt == helper_status_receipt
    _assert_root_pair(result)


class _RecordingSelector:
    def __init__(
        self,
        factory: Callable[[], selectors.BaseSelector],
        events: list[str],
        *,
        fail_close: bool = False,
    ) -> None:
        self._selector = factory()
        self._events = events
        self._fail_close = fail_close

    def register(
        self,
        fileobj: object,
        events: int,
        data: object = None,
    ) -> selectors.SelectorKey:
        assert isinstance(data, str)
        self._events.append(f"register:{data}")
        return self._selector.register(fileobj, events, data)

    def close(self) -> None:
        self._events.append("selector-close")
        self._selector.close()
        if self._fail_close:
            raise OSError(errno.EIO, "simulated secondary selector close failure")

    def __getattr__(self, name: str) -> object:
        return getattr(self._selector, name)


def test_each_channel_is_nonblocking_before_its_registration_and_use(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_factory = evidence_module.selectors.DefaultSelector
    real_set_blocking = evidence_module.os.set_blocking
    events: list[str] = []
    set_fds: list[int] = []

    def factory() -> _RecordingSelector:
        events.append("selector-create")
        return _RecordingSelector(real_factory, events)

    def record_set_blocking(file_descriptor: int, blocking: bool) -> None:
        channel = _CHANNELS[len(set_fds)]
        set_fds.append(file_descriptor)
        events.append(f"nonblocking:{channel}")
        assert blocking is False
        real_set_blocking(file_descriptor, blocking)

    monkeypatch.setattr(evidence_module.selectors, "DefaultSelector", factory)
    monkeypatch.setattr(evidence_module.os, "set_blocking", record_set_blocking)

    result = _run_probe(tmp_path, monkeypatch, linger=False)

    assert events[:7] == [
        "selector-create",
        "nonblocking:status",
        "register:status",
        "nonblocking:stdout",
        "register:stdout",
        "nonblocking:stderr",
        "register:stderr",
    ]
    assert len(set(set_fds)) == 3
    assert result.returncode == 0
    assert result.nonblocking_channels == _CHANNELS
    assert result.registered_channels == _CHANNELS
    assert result.readiness_failure_stage == ""
    assert result.readiness_failure_channel == ""
    assert result.readiness_failure_fd is None


@pytest.mark.parametrize(
    ("failed_channel", "error_number", "expected_kind"),
    tuple(
        pytest.param(channel, error_number, expected_kind)
        for channel in _CHANNELS
        for error_number, expected_kind in (
            (errno.EIO, evidence_module.EvidenceProcessFailureKind.IO),
            (
                errno.EBADF,
                evidence_module.EvidenceProcessFailureKind.DESCRIPTOR_INVALID,
            ),
        )
    ),
)
def test_nonblocking_setup_failure_preserves_exact_prior_occurrences(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failed_channel: str,
    error_number: int,
    expected_kind: evidence_module.EvidenceProcessFailureKind,
) -> None:
    real_factory = evidence_module.selectors.DefaultSelector
    real_set_blocking = evidence_module.os.set_blocking
    events: list[str] = []
    set_fds: dict[str, int] = {}

    def factory() -> _RecordingSelector:
        events.append("selector-create")
        return _RecordingSelector(real_factory, events)

    def fail_selected_setup(file_descriptor: int, blocking: bool) -> None:
        channel = _CHANNELS[len(set_fds)]
        set_fds[channel] = file_descriptor
        events.append(f"nonblocking:{channel}")
        assert blocking is False
        if channel == failed_channel:
            raise OSError(error_number, f"simulated {channel} setup failure")
        real_set_blocking(file_descriptor, blocking)

    monkeypatch.setattr(evidence_module.selectors, "DefaultSelector", factory)
    monkeypatch.setattr(evidence_module.os, "set_blocking", fail_selected_setup)

    result = _run_probe(tmp_path, monkeypatch, linger=False)

    failure_index = _CHANNELS.index(failed_channel)
    successful_prefix = _CHANNELS[:failure_index]
    expected_events = ["selector-create"]
    for channel in successful_prefix:
        expected_events.extend((f"nonblocking:{channel}", f"register:{channel}"))
    expected_events.append(f"nonblocking:{failed_channel}")
    assert events[:-1] == expected_events
    assert events[-1] == "selector-close"
    nonblocking_stage = getattr(
        evidence_module.EvidenceProcessFailureStage,
        "NONBLOCKING_CONFIGURE",
        None,
    )
    assert nonblocking_stage is not None
    _assert_primary_failure(
        result,
        stage=nonblocking_stage,
        kind=expected_kind,
        error_number=error_number,
    )
    assert result.process_failure is not None
    payload = result.process_failure.canonical_payload()
    assert result.process_failure.schema_version != (
        "orion.host-evidence-process-failure.v2"
    )
    assert payload["selector_target"] == failed_channel
    assert payload["registered_channel_prefix"] == list(successful_prefix)
    assert result.nonblocking_channels == successful_prefix
    assert result.registered_channels == successful_prefix
    assert result.stdout == b""
    assert result.stderr == b""
    assert result.readiness_failure_stage == (
        f"{failed_channel.upper()}_SET_NONBLOCKING"
    )
    assert result.readiness_failure_channel == failed_channel
    assert result.readiness_failure_fd == set_fds[failed_channel]


def test_nonblocking_primary_failure_survives_selector_close_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_factory = evidence_module.selectors.DefaultSelector
    real_set_blocking = evidence_module.os.set_blocking
    events: list[str] = []
    setup_count = 0

    def factory() -> _RecordingSelector:
        events.append("selector-create")
        return _RecordingSelector(real_factory, events, fail_close=True)

    def fail_stdout_setup(file_descriptor: int, blocking: bool) -> None:
        nonlocal setup_count
        channel = _CHANNELS[setup_count]
        setup_count += 1
        events.append(f"nonblocking:{channel}")
        if channel == "stdout":
            raise OSError(errno.EIO, "simulated stdout setup failure")
        real_set_blocking(file_descriptor, blocking)

    monkeypatch.setattr(evidence_module.selectors, "DefaultSelector", factory)
    monkeypatch.setattr(evidence_module.os, "set_blocking", fail_stdout_setup)

    result = _run_probe(tmp_path, monkeypatch, linger=False)

    nonblocking_stage = getattr(
        evidence_module.EvidenceProcessFailureStage,
        "NONBLOCKING_CONFIGURE",
        None,
    )
    assert nonblocking_stage is not None
    _assert_primary_failure(
        result,
        stage=nonblocking_stage,
        kind=evidence_module.EvidenceProcessFailureKind.IO,
        error_number=errno.EIO,
    )
    assert result.process_failure is not None
    payload = result.process_failure.canonical_payload()
    assert payload["selector_target"] == "stdout"
    assert payload["registered_channel_prefix"] == ["status"]
    assert result.readiness_failure_stage == "STDOUT_SET_NONBLOCKING"
    assert events[-1] == "selector-close"


def test_selector_registration_failures_bind_target_prefix_and_do_not_collide(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Same-errno register failures are distinct operational occurrences."""

    real_factory = evidence_module.selectors.DefaultSelector
    real_monotonic_ns = evidence_module.time.monotonic_ns
    frozen_now = real_monotonic_ns()
    active_target = ""
    observed_prefixes: list[tuple[str, ...]] = []

    class RegistrationFailingSelector:
        def __init__(self) -> None:
            self._selector = real_factory()
            self._registered: list[str] = []

        def register(
            self,
            fileobj: object,
            events: int,
            data: object = None,
        ) -> selectors.SelectorKey:
            assert isinstance(data, str)
            if data == active_target:
                observed_prefixes.append(tuple(self._registered))
                raise OSError(errno.EIO, "simulated selector registration failure")
            key = self._selector.register(fileobj, events, data)
            self._registered.append(data)
            return key

        def __getattr__(self, name: str) -> object:
            return getattr(self._selector, name)

    monkeypatch.setattr(
        evidence_module.selectors,
        "DefaultSelector",
        RegistrationFailingSelector,
    )
    monkeypatch.setattr(evidence_module.time, "monotonic_ns", lambda: frozen_now)
    opened = _open_test_git_root(tmp_path / "repo")
    receipts: list[evidence_module.EvidenceProcessFailureReceipt] = []
    registration_results: list[evidence_module._GitCommandResult] = []
    try:
        for target in _CHANNELS:
            active_target = target
            result = _run_probe(
                tmp_path,
                monkeypatch,
                stdout=b"",
                stderr=b"",
                linger=True,
                opened=opened,
            )
            _assert_primary_failure(
                result,
                stage=evidence_module.EvidenceProcessFailureStage.SELECTOR_REGISTER,
                kind=evidence_module.EvidenceProcessFailureKind.IO,
                error_number=errno.EIO,
            )
            assert result.process_failure is not None
            registration_results.append(result)
            receipts.append(
                replace(
                    result.process_failure,
                    invocation_subject_hash="f" * 64,
                )
            )
    finally:
        _close_test_git_root(opened)

    expected_prefixes = [(), ("status",), ("status", "stdout")]
    assert observed_prefixes == expected_prefixes
    for target, prefix, result in zip(
        _CHANNELS,
        expected_prefixes,
        registration_results,
        strict=True,
    ):
        assert result.nonblocking_channels == (*prefix, target)
        assert result.registered_channels == prefix
        assert result.readiness_failure_stage == f"{target.upper()}_REGISTER"
        assert result.readiness_failure_channel == target
        assert result.readiness_failure_fd is not None
    common_payloads = []
    violations: list[str] = []
    for target, prefix, receipt in zip(
        _CHANNELS,
        expected_prefixes,
        receipts,
        strict=True,
    ):
        payload = receipt.canonical_payload()
        common_payloads.append(
            {
                key: value
                for key, value in payload.items()
                if key
                not in {
                    "selector_target",
                    "registered_channel_prefix",
                    "signature_hash",
                }
            }
        )
        if payload.get("selector_target") != target:
            violations.append(
                f"{target}: selector_target={payload.get('selector_target')!r}"
            )
        if payload.get("registered_channel_prefix") != list(prefix):
            violations.append(
                f"{target}: registered_channel_prefix="
                f"{payload.get('registered_channel_prefix')!r}"
            )
    if len({receipt.schema_version for receipt in receipts}) != 1:
        violations.append("registration receipts disagree on schema version")
    if receipts[0].schema_version == "orion.host-evidence-process-failure.v2":
        violations.append("registration discriminator would silently mutate V2")
    if len({receipt.receipt_hash for receipt in receipts}) != len(_CHANNELS):
        violations.append("receipt hashes collide across registration targets")
    if len({receipt.signature_hash for receipt in receipts}) != len(_CHANNELS):
        violations.append("recurrence signatures collide across registration targets")
    if len({repr(payload) for payload in common_payloads}) != 1:
        violations.append("supposedly common registration coordinates drifted")
    assert not violations, "; ".join(violations)


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


def test_single_select_eintr_is_immutably_accounted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_factory = evidence_module.selectors.DefaultSelector

    def factory() -> _DelegatingSelector:
        return _DelegatingSelector(
            real_factory,
            [OSError(errno.EINTR, "simulated select interruption")],
        )

    monkeypatch.setattr(evidence_module.selectors, "DefaultSelector", factory)

    result = _run_probe(tmp_path, monkeypatch, linger=False)

    assert result.returncode == 0
    assert result.selector_retry_counts == (1, 0)
    assert result.stream_retry_counts == ((0, 0), (0, 0), (0, 0))
    with pytest.raises(FrozenInstanceError):
        result.selector_retry_counts = (0, 0)  # type: ignore[misc]


def test_repeated_select_eintr_is_bounded_even_when_clock_is_stuck(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    retry_limit = evidence_module._GIT_SELECTOR_EINTR_RETRY_LIMIT
    assert 1 <= retry_limit <= 64
    real_factory = evidence_module.selectors.DefaultSelector
    selected: _DelegatingSelector | None = None

    def factory() -> _DelegatingSelector:
        nonlocal selected
        selected = _DelegatingSelector(
            real_factory,
            [OSError(errno.EINTR, "simulated select interruption")] * retry_limit,
        )
        return selected

    monkeypatch.setattr(evidence_module.selectors, "DefaultSelector", factory)
    monkeypatch.setattr(evidence_module.time, "monotonic_ns", lambda: 123_456_789)

    result = _run_probe(tmp_path, monkeypatch, linger=True)

    assert selected is not None
    assert selected.select_calls == retry_limit
    _assert_primary_failure(
        result,
        stage=evidence_module.EvidenceProcessFailureStage.SELECT,
        kind=evidence_module.EvidenceProcessFailureKind.INTERRUPTED,
        error_number=errno.EINTR,
    )
    assert result.selector_retry_counts == (retry_limit, 0)
    assert result.readiness_failure_stage == "SELECT"
    assert result.readiness_failure_channel == ""


def test_repeated_early_empty_is_accounted_when_clock_is_stuck(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    retry_limit = evidence_module._GIT_SELECTOR_EMPTY_RETRY_LIMIT
    real_factory = evidence_module.selectors.DefaultSelector
    selected: _DelegatingSelector | None = None

    def factory() -> _DelegatingSelector:
        nonlocal selected
        selected = _DelegatingSelector(real_factory, ["EMPTY"] * retry_limit)
        return selected

    monkeypatch.setattr(evidence_module.selectors, "DefaultSelector", factory)
    monkeypatch.setattr(evidence_module.time, "monotonic_ns", lambda: 123_456_789)

    result = _run_probe(tmp_path, monkeypatch, linger=True)

    assert selected is not None
    assert selected.select_calls == retry_limit
    assert result.returncode is None
    assert result.timed_out is False
    assert result.process_failure is not None
    assert result.process_failure.stage is evidence_module.EvidenceProcessFailureStage.SELECT
    assert result.process_failure.kind is (
        evidence_module.EvidenceProcessFailureKind.PROTOCOL_INVALID
    )
    assert result.selector_retry_counts == (0, retry_limit)


class _ScriptedBatchSelector:
    def __init__(self, *, later_ready_stream: str | None = None) -> None:
        self._keys: dict[int, selectors.SelectorKey] = {}
        self.calls = 0
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
        keys = tuple(self._keys.values())
        if self.calls >= 2 and self.later_ready_stream is not None:
            keys = tuple(
                key for key in keys if key.data == self.later_ready_stream
            )
        return [(key, selectors.EVENT_READ) for key in reversed(keys)]

    def close(self) -> None:
        self._keys.clear()


def _record_selector_stream_fds(
    selected: _ScriptedBatchSelector,
) -> dict[int, str]:
    by_fd: dict[int, str] = {}
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
    return by_fd


@pytest.mark.parametrize("target", _CHANNELS)
def test_single_read_eintr_is_immutably_accounted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
) -> None:
    selected = _ScriptedBatchSelector()
    by_fd = _record_selector_stream_fds(selected)
    monkeypatch.setattr(evidence_module.selectors, "DefaultSelector", lambda: selected)
    real_read = evidence_module.os.read
    reads = {channel: 0 for channel in _CHANNELS}

    def scripted_read(file_descriptor: int, size: int) -> bytes:
        stream = by_fd.get(file_descriptor)
        if stream is None:
            return real_read(file_descriptor, size)
        reads[stream] += 1
        if stream == target and reads[stream] == 1:
            raise OSError(errno.EINTR, f"simulated {stream} read interruption")
        successful_index = 2 if stream == target else 1
        if reads[stream] == successful_index:
            return {
                "status": _PRE_EXEC_FRAME,
                "stdout": _PARTIAL_STDOUT,
                "stderr": _PARTIAL_STDERR,
            }[stream]
        return b""

    monkeypatch.setattr(evidence_module.os, "read", scripted_read)

    result = _run_probe(tmp_path, monkeypatch, linger=False)

    expected = [[0, 0] for _ in _CHANNELS]
    expected[_CHANNELS.index(target)][0] = 1
    assert result.returncode == 0
    assert result.stream_retry_counts == tuple(tuple(row) for row in expected)


@pytest.mark.parametrize("target", _CHANNELS)
def test_single_readiness_race_returns_to_selection_and_recovers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
) -> None:
    selected = _ScriptedBatchSelector()
    by_fd = _record_selector_stream_fds(selected)
    monkeypatch.setattr(evidence_module.selectors, "DefaultSelector", lambda: selected)
    real_read = evidence_module.os.read
    reads = {channel: 0 for channel in _CHANNELS}

    def scripted_read(file_descriptor: int, size: int) -> bytes:
        stream = by_fd.get(file_descriptor)
        if stream is None:
            return real_read(file_descriptor, size)
        reads[stream] += 1
        if stream == target and reads[stream] == 1:
            raise BlockingIOError(errno.EAGAIN, f"simulated {stream} readiness race")
        successful_index = 2 if stream == target else 1
        if reads[stream] == successful_index:
            return {
                "status": _PRE_EXEC_FRAME,
                "stdout": _PARTIAL_STDOUT,
                "stderr": _PARTIAL_STDERR,
            }[stream]
        return b""

    monkeypatch.setattr(evidence_module.os, "read", scripted_read)

    result = _run_probe(tmp_path, monkeypatch, linger=False)

    expected = [[0, 0] for _ in _CHANNELS]
    expected[_CHANNELS.index(target)][1] = 1
    assert selected.calls >= 2
    assert result.returncode == 0
    assert result.process_failure is None
    assert result.timed_out is False
    assert result.stream_retry_counts == tuple(tuple(row) for row in expected)


@pytest.mark.parametrize(
    ("target", "expected_stage"),
    (
        ("status", evidence_module.EvidenceProcessFailureStage.HELPER_STATUS_READ),
        ("stdout", evidence_module.EvidenceProcessFailureStage.STDOUT_READ),
        ("stderr", evidence_module.EvidenceProcessFailureStage.STDERR_READ),
    ),
)
def test_repeated_readiness_race_has_finite_exact_non_timeout_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
    expected_stage: evidence_module.EvidenceProcessFailureStage,
) -> None:
    retry_limit = evidence_module._GIT_STREAM_READINESS_RETRY_LIMIT
    assert 1 <= retry_limit <= 64
    selected = _ScriptedBatchSelector(later_ready_stream=target)
    by_fd = _record_selector_stream_fds(selected)
    monkeypatch.setattr(evidence_module.selectors, "DefaultSelector", lambda: selected)
    monkeypatch.setattr(evidence_module.time, "monotonic_ns", lambda: 123_456_789)
    real_read = evidence_module.os.read
    reads = {channel: 0 for channel in _CHANNELS}
    races = 0

    def scripted_read(file_descriptor: int, size: int) -> bytes:
        nonlocal races
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
        races += 1
        if races > retry_limit:
            raise RuntimeError("readiness retry exceeded its frozen bound")
        raise BlockingIOError(errno.EAGAIN, f"simulated {stream} readiness race")

    monkeypatch.setattr(evidence_module.os, "read", scripted_read)

    result = _run_probe(tmp_path, monkeypatch, linger=True)

    expected = [[0, 0] for _ in _CHANNELS]
    expected[_CHANNELS.index(target)][1] = retry_limit
    assert races == retry_limit
    retry_exhausted_kind = getattr(
        evidence_module.EvidenceProcessFailureKind,
        "RETRY_EXHAUSTED",
        None,
    )
    assert retry_exhausted_kind is not None
    _assert_primary_failure(
        result,
        stage=expected_stage,
        kind=retry_exhausted_kind,
        error_number=errno.EAGAIN,
        stdout=_PARTIAL_STDOUT,
        stderr=_PARTIAL_STDERR,
        handoff_state=evidence_module.EvidenceHelperHandoffState.PRE_EXEC,
        helper_status_receipt=_PRE_EXEC_FRAME,
    )
    assert result.process_failure is not None
    assert result.process_failure.kind is not (
        evidence_module.EvidenceProcessFailureKind.PROCESS_LIMIT
    )
    assert result.stream_retry_counts == tuple(tuple(row) for row in expected)
    assert result.readiness_failure_stage == f"{target.upper()}_READ"
    assert result.readiness_failure_channel == target
    assert result.readiness_failure_fd in by_fd


def test_status_acquisition_cap_plus_one_is_immediately_protocol_invalid(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    acquisition_limit = evidence_module._GIT_HELPER_STATUS_ACQUISITION_LIMIT
    assert acquisition_limit == evidence_module._GIT_HELPER_STATUS_RECEIPT_LIMIT + 1
    receipt = b"x" * acquisition_limit
    helper_source = (
        "import os, sys, time\n"
        "status_fd = int(sys.argv[4])\n"
        f"os.write(status_fd, {receipt!r})\n"
        "time.sleep(10)\n"
    )

    result = _run_probe(
        tmp_path,
        monkeypatch,
        stdout=b"",
        stderr=b"",
        linger=True,
        helper_source=helper_source,
        timeout_seconds=0.25,
    )

    assert result.returncode is None
    assert result.timed_out is False
    assert result.helper_handoff_state is (
        evidence_module.EvidenceHelperHandoffState.UNKNOWN
    )
    assert result.helper_status_receipt == receipt
    assert result.process_failure is not None
    assert result.process_failure.stage is (
        evidence_module.EvidenceProcessFailureStage.HELPER_STATUS_READ
    )
    assert result.process_failure.kind is (
        evidence_module.EvidenceProcessFailureKind.PROTOCOL_INVALID
    )
    assert result.process_failure.mechanism_errno is None
    assert result.process_failure.helper_status_receipt == receipt
    assert result.mechanism_limitation is (
        evidence_module.EvidenceMechanismLimitationKind.PROTOCOL
    )


@pytest.mark.parametrize("target", ("stdout", "stderr"))
@pytest.mark.parametrize("size", (0, 1))
def test_zero_logical_output_cap_distinguishes_eof_from_one_byte(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
    size: int,
) -> None:
    payload = b"Z" * size
    result = _run_probe(
        tmp_path,
        monkeypatch,
        stdout=payload if target == "stdout" else b"",
        stderr=payload if target == "stderr" else b"",
        linger=False,
        stdout_limit=0 if target == "stdout" else 1,
        stderr_limit=0 if target == "stderr" else 1,
        combined_limit=1,
    )

    retained = result.stdout if target == "stdout" else result.stderr
    acquired_not_output = (
        result.stdout_acquired_not_output
        if target == "stdout"
        else result.stderr_acquired_not_output
    )
    assert retained == b""
    assert acquired_not_output == payload
    assert result.output_limited is (size == 1)
    assert result.returncode == (None if size == 1 else 0)
    assert result.stdout_limited is (target == "stdout" and size == 1)
    assert result.stderr_limited is (target == "stderr" and size == 1)
    assert result.combined_limited is False


@pytest.mark.parametrize("target", ("stdout", "stderr"))
@pytest.mark.parametrize("size", (_BOUND - 1, _BOUND, _BOUND + 1))
def test_each_output_stream_distinguishes_b_minus_one_b_and_b_plus_one(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
    size: int,
) -> None:
    payload = b"A" * min(size, _BOUND) + (b"Z" if size > _BOUND else b"")
    stdout = payload if target == "stdout" else b""
    stderr = payload if target == "stderr" else b""

    result = _run_probe(
        tmp_path,
        monkeypatch,
        stdout=stdout,
        stderr=stderr,
        linger=False,
        stdout_limit=_BOUND,
        stderr_limit=_BOUND,
        combined_limit=2 * _BOUND,
    )

    retained = result.stdout if target == "stdout" else result.stderr
    sentinel = (
        result.stdout_acquired_not_output
        if target == "stdout"
        else result.stderr_acquired_not_output
    )
    assert retained == payload[:_BOUND]
    assert sentinel == (b"Z" if size == _BOUND + 1 else b"")
    assert result.output_limited is (size == _BOUND + 1)
    assert result.returncode == (None if size == _BOUND + 1 else 0)
    assert result.combined_limited is False
    assert result.stdout_limited is (
        target == "stdout" and size == _BOUND + 1
    )
    assert result.stderr_limited is (
        target == "stderr" and size == _BOUND + 1
    )
    _assert_root_pair(result)


@pytest.mark.parametrize("size", (_BOUND - 1, _BOUND, _BOUND + 1))
def test_combined_output_distinguishes_b_minus_one_b_and_b_plus_one(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    size: int,
) -> None:
    payload = b"A" * min(size, _BOUND) + (b"Z" if size > _BOUND else b"")

    result = _run_probe(
        tmp_path,
        monkeypatch,
        stdout=payload,
        stderr=b"",
        linger=False,
        stdout_limit=2 * _BOUND,
        stderr_limit=2 * _BOUND,
        combined_limit=_BOUND,
    )

    assert result.stdout == payload[:_BOUND]
    assert result.stdout_acquired_not_output == (
        b"Z" if size == _BOUND + 1 else b""
    )
    assert result.combined_limited is (size == _BOUND + 1)
    assert result.stdout_limited is False
    assert result.stderr_limited is False
    assert result.returncode == (None if size == _BOUND + 1 else 0)


@pytest.mark.parametrize("total_size", (_BOUND - 1, _BOUND, _BOUND + 1))
def test_split_streams_share_one_exact_combined_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    total_size: int,
) -> None:
    stdout = b"O" * 3
    stderr_size = total_size - len(stdout)
    stderr = b"E" * min(stderr_size, _BOUND - len(stdout))
    if total_size > _BOUND:
        stderr += b"Z"

    result = _run_probe(
        tmp_path,
        monkeypatch,
        stdout=stdout,
        stderr=stderr,
        linger=False,
        stdout_limit=2 * _BOUND,
        stderr_limit=2 * _BOUND,
        combined_limit=_BOUND,
    )

    combined = result.stdout + result.stderr
    assert combined == (stdout + stderr)[:_BOUND]
    assert result.stdout_acquired_not_output == b""
    assert result.stderr_acquired_not_output == (
        b"Z" if total_size == _BOUND + 1 else b""
    )
    assert result.combined_limited is (total_size == _BOUND + 1)
    assert result.stdout_limited is False
    assert result.stderr_limited is False
    assert result.returncode == (None if total_size == _BOUND + 1 else 0)


@pytest.mark.parametrize("actual_size", (4, 5, 6))
def test_verified_object_maps_every_observation_beyond_logical_d_to_too_large(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    actual_size: int,
) -> None:
    logical_limit = 4
    logical_payload = b"x" * logical_limit
    actual_payload = b"x" * actual_size
    ref = "source:object-boundary"
    monkeypatch.setattr(
        evidence_module,
        "_GIT_EXECUTABLE",
        evidence_module._GIT_FD_HELPER_EXECUTABLE,
    )
    monkeypatch.setattr(
        evidence_module,
        "_GIT_FD_EXEC_HELPER",
        (
            "import os, sys\n"
            "status_fd = int(sys.argv[4])\n"
            f"os.write(status_fd, {_PRE_EXEC_FRAME!r})\n"
            "os.close(status_fd)\n"
            f"os.write(1, b'4\\n' if sys.argv[-2] == '-s' else {actual_payload!r})\n"
            "os._exit(0)"
        ),
    )
    opened = _open_test_git_root(tmp_path / "repo")
    ledger = evidence_module._EvidenceWorkLedger(
        evidence_module.DEFAULT_HOST_EVIDENCE_WORK_CONTRACT,
        started_monotonic_ns=time.monotonic_ns(),
    )
    instrument = evidence_module._observe_protected_git_instrument(
        ledger,
        ref=ref,
        ordinal=0,
    )
    assert instrument.usable
    opened = replace(opened, protected_git_instrument=instrument)
    work_state = evidence_module._CaptureWorkState(
        max_local_bytes=0,
        max_git_commands=0,
        max_git_stdout_bytes=0,
        max_git_stderr_bytes=0,
        max_elapsed_ns=0,
        max_path_components=0,
        max_tree_entries=0,
        max_git_object_bytes=0,
        max_git_objects=0,
        enforce_limits=False,
    )
    oid = evidence_module._git_object_oid("sha1", "blob", logical_payload)
    object_key = (
        opened.git_source_device,
        opened.git_source_inode,
        "sha1",
        "blob",
        oid,
    )
    try:
        result = evidence_module._read_verified_git_object(
            opened,
            object_format="sha1",
            object_type="blob",
            oid=oid,
            limit=logical_limit,
            work_state=work_state,
            work_ledger=ledger,
            ref=ref,
            ordinal=0,
        )
    finally:
        _close_test_git_root(opened)

    (
        status,
        payload,
        note,
        limitation,
        process_failure,
        mechanism_errno,
        instrument_failure,
    ) = result
    usage = ledger.used.as_dict()
    observed_size = min(actual_size, logical_limit + 1)
    assert limitation is None
    assert process_failure is None
    assert mechanism_errno is None
    assert instrument_failure is None
    assert usage["git_object_bytes_observed"] == observed_size
    assert usage["git_stdout_bytes_observed"] == len(b"4\n") + observed_size
    if actual_size == logical_limit:
        assert status is evidence_module.EvidenceStatus.RESOLVED
        assert payload == logical_payload
        assert note == ""
        assert usage["git_distinct_objects"] == 1
        assert object_key in ledger.seen_git_oids
        assert object_key in ledger.verified_git_object_cache
    else:
        assert status is evidence_module.EvidenceStatus.TOO_LARGE
        assert payload == b""
        assert note == "Git object exceeds capture limit"
        assert usage["git_distinct_objects"] == 0
        assert object_key not in ledger.seen_git_oids
        assert object_key not in ledger.verified_git_object_cache


def _work_vector(**overrides: int) -> evidence_module.EvidenceWorkVector:
    values = {name: 0 for name in evidence_module.EVIDENCE_WORK_DIMENSIONS}
    values.update(overrides)
    return evidence_module.EvidenceWorkVector(
        tuple(values[name] for name in evidence_module.EVIDENCE_WORK_DIMENSIONS)
    )


def _work_contract(
    *,
    stdout_observed: int,
    secondary_observed: int,
) -> evidence_module.HostEvidenceWorkContract:
    return evidence_module.HostEvidenceWorkContract(
        limits=_work_vector(
            descriptor_operation_attempts=100,
            executable_bytes_observed=(
                2 * evidence_module.MAX_EVIDENCE_EXECUTABLE_BYTES
            ),
            git_process_starts=1,
            git_protocol_operations=1,
            git_stdout_bytes_observed=stdout_observed,
            git_stderr_bytes_observed=100,
            git_object_bytes_observed=secondary_observed,
        ),
        wall_time_budget_ns=5_000_000_000,
        per_record_retained_limit=100,
        git_call_timeout_ns=2_000_000_000,
        max_read_chunk_bytes=1_048_576,
    )


def test_secondary_stdout_work_dimension_has_an_exact_byte_allowlist(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No output byte may be charged to an unrelated work coordinate."""

    opened = evidence_module._OpenedRoot(
        scheme="repo",
        configured_path=tmp_path / "unopened",
        file_descriptor=None,
        source_device=None,
        source_inode=None,
    )
    monkeypatch.setattr(evidence_module, "_GIT_EXECUTABLE", None)
    allowed = "git_object_bytes_observed"
    invalid_dimensions = tuple(
        name for name in evidence_module.EVIDENCE_WORK_DIMENSIONS if name != allowed
    )
    assert "records_admitted" in invalid_dimensions
    assert "git_process_starts" in invalid_dimensions
    assert "git_stdout_bytes_observed" in invalid_dimensions
    assert "git_stderr_bytes_observed" in invalid_dimensions

    for dimension in invalid_dimensions:
        with pytest.raises(ValueError, match="secondary Git stdout work dimension"):
            evidence_module._run_protected_git(
                opened,
                "cat-file",
                "blob",
                "a" * 40,
                stdout_secondary_work_dimension=dimension,
            )

    result = evidence_module._run_protected_git(
        opened,
        "cat-file",
        "blob",
        "a" * 40,
        stdout_secondary_work_dimension=allowed,
    )
    assert result.mechanism_limitation is (
        evidence_module.EvidenceMechanismLimitationKind.PROCESS_START
    )


def _bind_test_git_instrument(
    opened: evidence_module._OpenedRoot,
    ledger: evidence_module._EvidenceWorkLedger,
) -> evidence_module._OpenedRoot:
    instrument = evidence_module._observe_protected_git_instrument(
        ledger,
        ref="source:nonblocking-output",
        ordinal=4,
    )
    assert instrument.usable
    return replace(opened, protected_git_instrument=instrument)


def _open_ledger_probe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    stdout_observed: int,
    secondary_observed: int,
) -> tuple[evidence_module._OpenedRoot, evidence_module._EvidenceWorkLedger]:
    monkeypatch.setattr(
        evidence_module,
        "_TRUSTED_EXECUTABLE_OWNER_UIDS",
        frozenset({0, os.geteuid()}),
    )
    monkeypatch.setattr(
        evidence_module,
        "_GIT_EXECUTABLE",
        evidence_module._GIT_FD_HELPER_EXECUTABLE,
    )
    monkeypatch.setattr(
        evidence_module,
        "_GIT_FD_EXEC_HELPER",
        _helper_source(stdout=(b"A" * _BOUND) + b"Z", stderr=b"", linger=False),
    )
    opened = _open_test_git_root(tmp_path / "repo")
    ledger = evidence_module._EvidenceWorkLedger(
        _work_contract(
            stdout_observed=stdout_observed,
            secondary_observed=secondary_observed,
        ),
        started_monotonic_ns=time.monotonic_ns(),
    )
    return _bind_test_git_instrument(opened, ledger), ledger


def test_output_sentinel_is_charged_to_every_coupled_work_coordinate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened, ledger = _open_ledger_probe(
        tmp_path,
        monkeypatch,
        stdout_observed=_BOUND + 1,
        secondary_observed=_BOUND + 1,
    )
    try:
        result = _run_probe(
            tmp_path,
            monkeypatch,
            stdout=(b"A" * _BOUND) + b"Z",
            stderr=b"",
            linger=False,
            stdout_limit=_BOUND,
            stderr_limit=_BOUND,
            combined_limit=2 * _BOUND,
            opened=opened,
            work_ledger=ledger,
            stdout_secondary_work_dimension="git_object_bytes_observed",
        )
    finally:
        _close_test_git_root(opened)

    usage = ledger.used.as_dict()
    assert result.stdout == b"A" * _BOUND
    assert result.stdout_acquired_not_output == b"Z"
    assert usage["git_stdout_bytes_observed"] == _BOUND + 1
    assert usage["git_object_bytes_observed"] == _BOUND + 1
    assert result.stdout_limited is True


@pytest.mark.parametrize("actual_size", (_BOUND, _BOUND + 1))
@pytest.mark.parametrize(
    ("stdout_observed", "secondary_observed", "expected_dimensions"),
    (
        (
            _BOUND,
            _BOUND + 1,
            ("git_stdout_bytes_observed",),
        ),
        (
            _BOUND + 1,
            _BOUND,
            ("git_object_bytes_observed",),
        ),
        (
            _BOUND,
            _BOUND,
            (
                "git_stdout_bytes_observed",
                "git_object_bytes_observed",
            ),
        ),
    ),
)
def test_zero_coupled_sentinel_room_censors_without_an_os_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    actual_size: int,
    stdout_observed: int,
    secondary_observed: int,
    expected_dimensions: tuple[str, ...],
) -> None:
    opened, ledger = _open_ledger_probe(
        tmp_path,
        monkeypatch,
        stdout_observed=stdout_observed,
        secondary_observed=secondary_observed,
    )
    real_factory = evidence_module.selectors.DefaultSelector
    real_read = evidence_module.os.read
    by_fd: dict[int, str] = {}
    observed_output_bytes = 0

    class RecordingSelector(_RecordingSelector):
        def register(
            self,
            fileobj: object,
            events: int,
            data: object = None,
        ) -> selectors.SelectorKey:
            key = super().register(fileobj, events, data)
            assert isinstance(data, str)
            by_fd[key.fd] = data
            return key

    monkeypatch.setattr(
        evidence_module.selectors,
        "DefaultSelector",
        lambda: RecordingSelector(real_factory, []),
    )

    def count_read(file_descriptor: int, size: int) -> bytes:
        nonlocal observed_output_bytes
        chunk = real_read(file_descriptor, size)
        if by_fd.get(file_descriptor) == "stdout":
            observed_output_bytes += len(chunk)
        return chunk

    monkeypatch.setattr(evidence_module.os, "read", count_read)
    try:
        result = _run_probe(
            tmp_path,
            monkeypatch,
            stdout=(b"A" * _BOUND) + (b"Z" if actual_size > _BOUND else b""),
            stderr=b"",
            linger=False,
            stdout_limit=_BOUND,
            stderr_limit=_BOUND,
            combined_limit=2 * _BOUND,
            opened=opened,
            work_ledger=ledger,
            stdout_secondary_work_dimension="git_object_bytes_observed",
        )
    finally:
        _close_test_git_root(opened)

    usage = ledger.used.as_dict()
    assert observed_output_bytes == _BOUND
    assert result.stdout == b"A" * _BOUND
    assert result.stdout_acquired_not_output == b""
    assert result.work_exhaustion is not None
    assert result.work_exhaustion.dimensions == expected_dimensions
    assert usage["git_stdout_bytes_observed"] == _BOUND
    assert usage["git_object_bytes_observed"] == _BOUND
