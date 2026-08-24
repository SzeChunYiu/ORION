"""Frozen hostile oracle for the protected runner's wait boundary.

The runner only requests terminal blocking waits or WNOHANG polling.  Job-control
request modes (WUNTRACED/WCONTINUED) are deliberately outside the V3 surface:
STOPPED and CONTINUED remain typed all-outcome observations only when the host
returns an unrequested/traced extension.  Capture-time decoding is host-bound;
reduction and replay are pure over the captured typed facts.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
from functools import lru_cache

import pytest

import orion.kernel.process_receipt as process_receipt
from orion.kernel.process_receipt import (
    ChildIdentityBound,
    ExitState,
    FailureKind,
    MaterializedInvocation,
    OperationAttempt,
    ProcessCommandSubject,
    ProcessLifecycleEvent,
    ProcessOperation,
    ProcessStage,
    ProcessState,
    ProcessTarget,
    ProcessWorkEnvelope,
    ProcessWorkVector,
    ReapDisposition,
    ReplayStatus,
    RetryContract,
    WaitDisposition,
    WaitObservation,
    append_process_event,
    build_process_receipt,
    reduce_process_events,
    verify_process_receipt,
)


HEX_A = "a" * 64
HEX_B = "b" * 64
EXPECTED_RAW_WAIT_STATUS_MASK = 0xFFFF
EXPECTED_WAIT_MODE_NAMES = (
    "BLOCKING_TERMINAL",
    "NONBLOCKING_TERMINAL",
)
EXPECTED_WAIT_STATUS_KIND_NAMES = (
    "EXITED",
    "SIGNALLED",
    "STOPPED",
    "CONTINUED",
    "UNKNOWN",
)
EXPECTED_WAIT_STATUS_PROVENANCE_NAMES = (
    "REQUESTED",
    "UNREQUESTED_OR_TRACED_EXTENSION",
)


def _work_limit(value: int = 100) -> ProcessWorkVector:
    return ProcessWorkVector(
        records_admitted=value,
        roots_admitted=value,
        root_path_components=value,
        source_path_components=value,
        descriptor_operation_attempts=value,
        executable_bytes_observed=value,
        git_control_bytes_observed=value,
        local_bytes_observed=value,
        retained_bytes=value,
        git_process_starts=value,
        git_protocol_operations=value,
        git_stdout_bytes_observed=value,
        git_stderr_bytes_observed=value,
        git_distinct_objects=value,
        git_object_bytes_observed=value,
        git_tree_entries_parsed=value,
        git_tag_steps=value,
    )


def _subject() -> ProcessCommandSubject:
    limit = _work_limit()
    return ProcessCommandSubject(
        operation=ProcessOperation.PROTECTED_GIT,
        logical_argv=("git", "status", "--porcelain=v2"),
        logical_environment=(("LC_ALL", "C"), ("PATH", "/usr/bin:/bin")),
        root_subject_hash=HEX_A,
        instrument_subject_hash=HEX_B,
        requested_timeout_ns=5_000_000_000,
        status_limit=1024,
        stdout_limit=32,
        stderr_limit=32,
        combined_limit=64,
        work_envelope=ProcessWorkEnvelope(limit, limit),
        retry_contract=RetryContract.frozen_default(),
    )


def _append(
    events: tuple[ProcessLifecycleEvent, ...], payload: object
) -> tuple[ProcessLifecycleEvent, ...]:
    return append_process_event(events, payload)


def _started_events(pid: int = 501) -> tuple[ProcessLifecycleEvent, ...]:
    events = _append(
        (),
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    return _append(events, ChildIdentityBound(pid, pid, 50_000))


def _invocation(subject: ProcessCommandSubject) -> MaterializedInvocation:
    return MaterializedInvocation(
        command_subject_hash=subject.command_subject_hash,
        host_nonce=b"w" * 32,
        materialized_argv=("/usr/bin/python3", "-I", "helper.py", "17"),
        materialized_environment=(
            ("LC_ALL", "C"),
            ("PATH", "/usr/bin:/bin"),
        ),
    )


def _supported_option_mask() -> int:
    return os.WNOHANG


def _illegal_wait_option_params() -> tuple[object, ...]:
    candidates = (
        ("wuntraced", getattr(os, "WUNTRACED", None)),
        ("wcontinued", getattr(os, "WCONTINUED", None)),
        ("waitid-wexited", getattr(os, "WEXITED", None)),
        ("waitid-wstopped", getattr(os, "WSTOPPED", None)),
        ("waitid-wnowait", getattr(os, "WNOWAIT", None)),
        ("unknown-high-bit", 1 << 30),
    )
    seen: set[int] = set()
    params: list[object] = []
    for name, value in candidates:
        if (
            type(value) is int
            and value not in seen
            and value != _supported_option_mask()
        ):
            seen.add(value)
            params.append(pytest.param(value, id=name))
    return tuple(params)


@lru_cache(maxsize=None)
def _host_status(kind_name: str) -> int:
    if kind_name == "EXITED":
        return 0
    if kind_name == "SIGNALLED":
        status = int(signal.SIGKILL)
        assert os.WIFSIGNALED(status)
        return status
    if kind_name == "STOPPED":
        preferred = (int(signal.SIGSTOP) << 8) | 0x7F
        if os.WIFSTOPPED(preferred) and os.WSTOPSIG(preferred) > 0:
            return preferred
        for status in range(EXPECTED_RAW_WAIT_STATUS_MASK + 1):
            if os.WIFSTOPPED(status) and os.WSTOPSIG(status) > 0:
                return status
        raise AssertionError("host exposes WIFSTOPPED but no stopped wait encoding")
    if kind_name == "CONTINUED":
        if not hasattr(os, "WIFCONTINUED") or not hasattr(os, "WCONTINUED"):
            pytest.skip("host does not expose POSIX continued-status support")
        for status in range(EXPECTED_RAW_WAIT_STATUS_MASK + 1):
            if os.WIFCONTINUED(status):
                return status
        raise AssertionError("host exposes WIFCONTINUED but no continued wait encoding")
    raise AssertionError(f"unknown test status kind: {kind_name}")


@lru_cache(maxsize=None)
def _unsupported_signal_status(kind_name: str) -> int:
    supported = {int(value) for value in signal.valid_signals()}
    for status in range(EXPECTED_RAW_WAIT_STATUS_MASK + 1):
        if (
            kind_name == "SIGNALLED"
            and os.WIFSIGNALED(status)
            and os.WTERMSIG(status) not in supported
        ):
            return status
        if (
            kind_name == "STOPPED"
            and os.WIFSTOPPED(status)
            and os.WSTOPSIG(status) not in supported
        ):
            return status
    raise AssertionError(f"host exposes no unsupported {kind_name} wait word")


def _enum_member(enum_name: str, member_name: str) -> object | None:
    enum_type = getattr(process_receipt, enum_name, None)
    return None if enum_type is None else getattr(enum_type, member_name)


def _wait(
    *,
    raw_status: int,
    options: int,
    mode_name: str,
    kind_name: str,
    provenance_name: str = "REQUESTED",
    pid: int = 501,
    exit_code: int | None = None,
    status_signal: int | None = None,
    decoder_identity: str | None = None,
) -> WaitObservation:
    kwargs: dict[str, object] = {
        "disposition": WaitDisposition.STATUS,
        "requested_child_pid": pid,
        "options": options,
        "returned_pid": pid,
        "raw_wait_status": raw_status,
        "mechanism_errno": None,
    }
    mode = _enum_member("WaitMode", mode_name)
    kind = _enum_member("WaitStatusKind", kind_name)
    provenance = _enum_member("WaitStatusProvenance", provenance_name)
    if mode is not None:
        kwargs["mode"] = mode
    if kind is not None:
        kwargs["status_kind"] = kind
    if provenance is not None:
        kwargs["status_provenance"] = provenance
    if "exit_code" in WaitObservation.__dataclass_fields__:
        if (
            exit_code is None
            and kind_name == "EXITED"
            and type(raw_status) is int
            and 0 <= raw_status <= EXPECTED_RAW_WAIT_STATUS_MASK
        ):
            exit_code = os.waitstatus_to_exitcode(raw_status)
        kwargs["exit_code"] = exit_code
    if "status_signal" in WaitObservation.__dataclass_fields__:
        if status_signal is None and kind_name == "SIGNALLED":
            status_signal = os.WTERMSIG(raw_status)
        elif status_signal is None and kind_name == "STOPPED":
            status_signal = os.WSTOPSIG(raw_status)
        kwargs["status_signal"] = status_signal
    if "decoder_identity" in WaitObservation.__dataclass_fields__:
        kwargs["decoder_identity"] = decoder_identity or getattr(
            process_receipt, "PROCESS_WAIT_DECODER_IDENTITY"
        )
    return WaitObservation(**kwargs)


def _assert_nonterminal_extension_state(state: object) -> None:
    assert state.process_state is ProcessState.STARTED
    assert state.exit_state is ExitState.UNOBSERVED
    assert state.reap_disposition is ReapDisposition.UNOBSERVED
    assert state.returncode is None
    assert state.termination_signal is None
    assert state.first_primary is not None
    assert state.first_primary.stage is ProcessStage.WAIT
    assert state.first_primary.kind is FailureKind.UNKNOWN
    assert state.can_project_success is False


def test_wait_contract_exposes_closed_abstract_domains_and_raw_mask() -> None:
    wait_mode = getattr(process_receipt, "WaitMode", None)
    wait_status_kind = getattr(process_receipt, "WaitStatusKind", None)
    wait_status_provenance = getattr(process_receipt, "WaitStatusProvenance", None)

    assert wait_mode is not None, "WaitMode must be an explicit closed domain"
    assert tuple(wait_mode.__members__) == EXPECTED_WAIT_MODE_NAMES
    assert wait_status_kind is not None, (
        "WaitStatusKind must be an explicit closed domain"
    )
    assert tuple(wait_status_kind.__members__) == EXPECTED_WAIT_STATUS_KIND_NAMES
    assert wait_status_provenance is not None, (
        "WaitStatusProvenance must distinguish requested from traced-extension status"
    )
    assert (
        tuple(wait_status_provenance.__members__)
        == EXPECTED_WAIT_STATUS_PROVENANCE_NAMES
    )
    assert (
        getattr(process_receipt, "PROCESS_WAIT_STATUS_RAW_MASK", None)
        == EXPECTED_RAW_WAIT_STATUS_MASK
    )
    decoder_identity = getattr(process_receipt, "PROCESS_WAIT_DECODER_IDENTITY", None)
    assert isinstance(decoder_identity, str) and len(decoder_identity) == 64
    supported_signals = getattr(process_receipt, "PROCESS_WAIT_SUPPORTED_SIGNALS", None)
    assert type(supported_signals) is tuple
    assert supported_signals == tuple(
        sorted(int(value) for value in signal.valid_signals())
    )
    fields = WaitObservation.__dataclass_fields__
    assert "mode" in fields
    assert "status_kind" in fields
    assert "status_provenance" in fields
    assert "exit_code" in fields
    assert "status_signal" in fields
    assert "decoder_identity" in fields
    subject_fields = ProcessCommandSubject.__dataclass_fields__
    assert "wait_decoder_identity" in subject_fields
    assert "wait_supported_signals" in subject_fields
    subject = _subject()
    assert subject.wait_decoder_identity == decoder_identity
    assert subject.wait_supported_signals == supported_signals


@pytest.mark.parametrize(
    ("mode_name", "options"),
    (
        ("BLOCKING_TERMINAL", 0),
        ("NONBLOCKING_TERMINAL", os.WNOHANG),
    ),
)
def test_wait_mode_binds_exact_requested_host_option_mask(
    mode_name: str, options: int
) -> None:
    wait_mode = getattr(process_receipt, "WaitMode", None)
    assert wait_mode is not None, "portable wait mode is absent"
    observation = _wait(
        raw_status=_host_status("EXITED"),
        options=options,
        mode_name=mode_name,
        kind_name="EXITED",
    )
    assert observation.mode is getattr(wait_mode, mode_name)

    mismatched = os.WNOHANG if options == 0 else 0
    with pytest.raises(ValueError, match="option|mask|mode"):
        _wait(
            raw_status=_host_status("EXITED"),
            options=mismatched,
            mode_name=mode_name,
            kind_name="EXITED",
        )


@pytest.mark.parametrize(
    "options",
    _illegal_wait_option_params(),
)
def test_wait_options_reject_unrequested_job_control_and_unknown_bits(
    options: int,
) -> None:
    with pytest.raises(ValueError, match="option|mask|mode"):
        _wait(
            raw_status=_host_status("EXITED"),
            options=options,
            mode_name="BLOCKING_TERMINAL",
            kind_name="EXITED",
        )


def test_wait_raw_status_high_bits_cannot_alias_normal_exit() -> None:
    """On the current host 0x10000 aliases to EXITED(0) unless masked first."""

    events = _started_events()
    try:
        events = _append(
            events,
            _wait(
                raw_status=EXPECTED_RAW_WAIT_STATUS_MASK + 1,
                options=0,
                mode_name="BLOCKING_TERMINAL",
                kind_name="EXITED",
            ),
        )
        state = reduce_process_events(_subject(), events)
    except ValueError as error:
        assert "raw" in str(error) or "mask" in str(error) or "status" in str(error)
        return
    pytest.fail(
        "high-bit raw status was not rejected before host classification: "
        f"exit_state={state.exit_state.value}, returncode={state.returncode}"
    )


def test_wait_raw_status_c_word_overflow_is_closed_before_os_macro() -> None:
    """0xffffffff currently reaches CPython and escapes as OverflowError."""

    events = _started_events()
    with pytest.raises(ValueError, match="raw|mask|status"):
        events = _append(
            events,
            _wait(
                raw_status=(1 << 32) - 1,
                options=0,
                mode_name="BLOCKING_TERMINAL",
                kind_name="EXITED",
            ),
        )
        reduce_process_events(_subject(), events)


def test_import_does_not_replace_host_waitstatus_decoder() -> None:
    """Importing the receipt algebra must not mutate the process-wide ``os`` API."""

    # pytest's ``pythonpath = ["src"]`` ini option only affects the test
    # process; a bare ``python -c`` child needs PYTHONPATH to import orion at
    # all, otherwise the probe reports ModuleNotFoundError instead of testing
    # the decoder-preservation property.
    src_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(process_receipt.__file__)))
    )
    env = dict(os.environ)
    inherited = env.get("PYTHONPATH")
    env["PYTHONPATH"] = os.pathsep.join(
        [src_root, *inherited.split(os.pathsep)] if inherited else [src_root]
    )
    probe = subprocess.run(
        (
            sys.executable,
            "-c",
            (
                "import os; "
                "before = os.waitstatus_to_exitcode; "
                "import orion.kernel.process_receipt; "
                "after = os.waitstatus_to_exitcode; "
                "raise SystemExit(0 if after is before else 41)"
            ),
        ),
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert probe.returncode == 0, (
        "importing orion.kernel.process_receipt replaced "
        f"os.waitstatus_to_exitcode (probe rc={probe.returncode}, "
        f"stdout={probe.stdout!r}, stderr={probe.stderr!r})"
    )


def test_wait_status_kind_must_match_its_closed_typed_coordinates() -> None:
    assert getattr(process_receipt, "WaitStatusKind", None) is not None
    assert "status_kind" in WaitObservation.__dataclass_fields__
    with pytest.raises(ValueError, match="status|kind|exit|coordinate"):
        _wait(
            raw_status=_host_status("SIGNALLED"),
            options=0,
            mode_name="BLOCKING_TERMINAL",
            kind_name="EXITED",
        )


@pytest.mark.parametrize("raw_kind", ("SIGNALLED", "STOPPED"))
def test_host_decoder_maps_unsupported_signal_words_to_unknown(
    raw_kind: str,
) -> None:
    factory = getattr(WaitObservation, "from_host_status", None)
    assert callable(factory), "capture-time host wait decoder/factory is absent"
    wait_mode = getattr(process_receipt, "WaitMode")
    decoder_identity = getattr(process_receipt, "PROCESS_WAIT_DECODER_IDENTITY")
    observation = factory(
        requested_child_pid=501,
        mode=wait_mode.BLOCKING_TERMINAL,
        returned_pid=501,
        raw_wait_status=_unsupported_signal_status(raw_kind),
        mechanism_errno=None,
        decoder_identity=decoder_identity,
    )

    assert observation.status_kind is process_receipt.WaitStatusKind.UNKNOWN
    assert (
        observation.status_provenance
        is process_receipt.WaitStatusProvenance.UNREQUESTED_OR_TRACED_EXTENSION
    )
    assert observation.status_signal is None
    assert observation.decoder_identity == decoder_identity

    state = reduce_process_events(_subject(), _append(_started_events(), observation))
    assert state.exit_state is ExitState.UNOBSERVED
    assert state.reap_disposition is ReapDisposition.UNKNOWN
    assert state.returncode is None
    assert state.termination_signal is None
    assert state.first_primary is not None
    assert state.first_primary.kind is FailureKind.UNKNOWN


def test_wait_decoder_identity_must_match_the_command_subject() -> None:
    assert "decoder_identity" in WaitObservation.__dataclass_fields__
    assert "wait_decoder_identity" in ProcessCommandSubject.__dataclass_fields__
    observation = _wait(
        raw_status=_host_status("EXITED"),
        options=0,
        mode_name="BLOCKING_TERMINAL",
        kind_name="EXITED",
        decoder_identity="f" * 64,
    )
    with pytest.raises(ValueError, match="decoder|identity|subject"):
        reduce_process_events(_subject(), _append(_started_events(), observation))


def test_stopped_wait_is_nonterminal_and_not_reaped() -> None:
    events = _append(
        _started_events(),
        _wait(
            raw_status=_host_status("STOPPED"),
            options=0,
            mode_name="BLOCKING_TERMINAL",
            kind_name="STOPPED",
            provenance_name="UNREQUESTED_OR_TRACED_EXTENSION",
        ),
    )
    _assert_nonterminal_extension_state(reduce_process_events(_subject(), events))


def test_continued_wait_is_nonterminal_and_not_reaped() -> None:
    events = _append(
        _started_events(),
        _wait(
            raw_status=_host_status("CONTINUED"),
            options=0,
            mode_name="BLOCKING_TERMINAL",
            kind_name="CONTINUED",
            provenance_name="UNREQUESTED_OR_TRACED_EXTENSION",
        ),
    )
    _assert_nonterminal_extension_state(reduce_process_events(_subject(), events))


@pytest.mark.parametrize("kind_name", ("STOPPED", "CONTINUED"))
def test_nonterminal_wait_allows_one_later_terminal_reap(kind_name: str) -> None:
    events = _append(
        _started_events(),
        _wait(
            raw_status=_host_status(kind_name),
            options=0,
            mode_name="BLOCKING_TERMINAL",
            kind_name=kind_name,
            provenance_name="UNREQUESTED_OR_TRACED_EXTENSION",
        ),
    )
    events = _append(
        events,
        _wait(
            raw_status=_host_status("EXITED"),
            options=0,
            mode_name="BLOCKING_TERMINAL",
            kind_name="EXITED",
        ),
    )

    state = reduce_process_events(_subject(), events)
    assert state.exit_state is ExitState.OBSERVED
    assert state.reap_disposition is ReapDisposition.REAPED
    assert state.returncode == 0
    assert state.first_primary is not None
    assert state.first_primary.kind is FailureKind.UNKNOWN
    assert state.can_project_success is False

    repeated = _append(
        events,
        _wait(
            raw_status=_host_status("EXITED"),
            options=0,
            mode_name="BLOCKING_TERMINAL",
            kind_name="EXITED",
        ),
    )
    with pytest.raises(ValueError, match="second reap|reap.*forbidden"):
        reduce_process_events(_subject(), repeated)


@pytest.mark.parametrize("kind_name", ("STOPPED", "CONTINUED"))
def test_nonterminal_status_requires_explicit_unrequested_or_traced_extension(
    kind_name: str,
) -> None:
    assert getattr(process_receipt, "WaitStatusProvenance", None) is not None
    assert "status_provenance" in WaitObservation.__dataclass_fields__
    status = _host_status(kind_name)

    with pytest.raises(ValueError, match="WUNTRACED|traced|provenance|mode"):
        _wait(
            raw_status=status,
            options=0,
            mode_name="BLOCKING_TERMINAL",
            kind_name=kind_name,
            provenance_name="REQUESTED",
        )

    extension = _append(
        _started_events(),
        _wait(
            raw_status=status,
            options=0,
            mode_name="BLOCKING_TERMINAL",
            kind_name=kind_name,
            provenance_name="UNREQUESTED_OR_TRACED_EXTENSION",
        ),
    )
    _assert_nonterminal_extension_state(reduce_process_events(_subject(), extension))


@pytest.mark.parametrize("kind_name", ("STOPPED", "CONTINUED"))
def test_pure_reducer_never_calls_host_wait_decoder(
    monkeypatch: pytest.MonkeyPatch, kind_name: str
) -> None:
    events = _append(
        _started_events(),
        _wait(
            raw_status=_host_status(kind_name),
            options=0,
            mode_name="BLOCKING_TERMINAL",
            kind_name=kind_name,
            provenance_name="UNREQUESTED_OR_TRACED_EXTENSION",
        ),
    )
    events = _append(
        events,
        _wait(
            raw_status=_host_status("EXITED"),
            options=0,
            mode_name="BLOCKING_TERMINAL",
            kind_name="EXITED",
        ),
    )
    subject = _subject()

    def forbidden_host_decode(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("pure replay called a capture-host wait decoder")

    for name in (
        "WIFEXITED",
        "WIFSIGNALED",
        "WIFSTOPPED",
        "WIFCONTINUED",
        "WEXITSTATUS",
        "WTERMSIG",
        "WSTOPSIG",
        "waitstatus_to_exitcode",
    ):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, forbidden_host_decode)

    state = reduce_process_events(subject, events)
    receipt = build_process_receipt(subject, _invocation(subject), events)
    verification = verify_process_receipt(receipt)

    assert state.reap_disposition is ReapDisposition.REAPED
    assert state.returncode == 0
    assert state.first_primary is not None
    assert state.first_primary.kind is FailureKind.UNKNOWN
    assert receipt.derived_state == state
    assert verification.status is ReplayStatus.VERIFIED
    assert verification.replayed_state == state
