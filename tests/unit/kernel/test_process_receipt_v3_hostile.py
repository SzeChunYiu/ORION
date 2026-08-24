"""Independent hostile witnesses for the frozen Process Receipt V3 core.

These tests deliberately exercise public-construction and lifecycle sequences
that the owned happy-path suite does not cover.  A safe implementation may
either reject an impossible sequence or preserve it as typed operational
failure knowledge, but it must never verify forged accounting or project an
invalid lifecycle as success.
"""

from __future__ import annotations

import errno
from dataclasses import replace

import pytest

import orion.kernel.process_receipt as process_receipt
from orion.kernel.process_receipt import (
    BytesObserved,
    Channel,
    ChannelEof,
    ChildIdentityBound,
    CloseAttempt,
    DescriptorAcquired,
    EventPhase,
    FailureKind,
    FailureRole,
    FinalizationBegin,
    FinalizationState,
    HandoffState,
    HandoffTransition,
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
    ReadyBatch,
    ReplayStatus,
    RetryContract,
    RetryKind,
    RetryObserved,
    RootIdentityObservation,
    RootObservationDisposition,
    RootObservationPhase,
    WaitDisposition,
    WaitObservation,
    append_process_event,
    build_process_receipt,
    reduce_process_events,
    verify_process_receipt,
)


HEX_A = "a" * 64
HEX_B = "b" * 64


def _work_limit(value: int = 100) -> ProcessWorkVector:
    return ProcessWorkVector(
        **{name: value for name in ProcessWorkVector.__dataclass_fields__}
    )


def _subject(
    *,
    stdout_limit: int = 32,
    envelope: ProcessWorkEnvelope | None = None,
    retry_contract: RetryContract | None = None,
) -> ProcessCommandSubject:
    return ProcessCommandSubject(
        operation=ProcessOperation.PROTECTED_GIT,
        logical_argv=("git", "status", "--porcelain=v2"),
        logical_environment=(("LC_ALL", "C"), ("PATH", "/usr/bin:/bin")),
        root_subject_hash=HEX_A,
        instrument_subject_hash=HEX_B,
        requested_timeout_ns=5_000_000_000,
        status_limit=1024,
        stdout_limit=stdout_limit,
        stderr_limit=32,
        combined_limit=64,
        work_envelope=envelope
        or ProcessWorkEnvelope(_work_limit(), _work_limit()),
        retry_contract=retry_contract or RetryContract.frozen_default(),
    )


def _invocation(subject: ProcessCommandSubject, nonce: bytes) -> MaterializedInvocation:
    return MaterializedInvocation(
        command_subject_hash=subject.command_subject_hash,
        host_nonce=nonce,
        materialized_argv=("/usr/bin/python3", "-I", "helper.py", "17"),
        materialized_environment=(("LC_ALL", "C"), ("PATH", "/usr/bin:/bin")),
    )


def _append(
    events: tuple[ProcessLifecycleEvent, ...],
    payload: object,
    *,
    phase: EventPhase = EventPhase.MAIN,
) -> tuple[ProcessLifecycleEvent, ...]:
    return append_process_event(events, payload, phase=phase)


def _root(phase: RootObservationPhase) -> RootIdentityObservation:
    return RootIdentityObservation(
        phase=phase,
        disposition=RootObservationDisposition.MATCHED,
        configured_device=11,
        configured_inode=12,
        descriptor_device=11,
        descriptor_inode=12,
        mechanism_errno=None,
    )


def _rebuild(
    payloads: list[tuple[object, EventPhase]],
) -> tuple[ProcessLifecycleEvent, ...]:
    events: tuple[ProcessLifecycleEvent, ...] = ()
    for payload, phase in payloads:
        events = _append(events, payload, phase=phase)
    return events


def _success_events() -> tuple[ProcessLifecycleEvent, ...]:
    events: tuple[ProcessLifecycleEvent, ...] = ()
    events = _append(events, _root(RootObservationPhase.PRE))
    for channel in Channel:
        events = _append(events, DescriptorAcquired(channel))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(events, ChildIdentityBound(501, 501, 50_000))
    events = _append(
        events,
        OperationAttempt.succeeded(
            ProcessStage.SELECTOR_CREATE, ProcessTarget.SELECTOR
        ),
    )
    for target in (
        ProcessTarget.STATUS,
        ProcessTarget.STDOUT,
        ProcessTarget.STDERR,
    ):
        events = _append(
            events,
            OperationAttempt.succeeded(ProcessStage.NONBLOCKING_CONFIGURE, target),
        )
    for target in (
        ProcessTarget.STATUS,
        ProcessTarget.STDOUT,
        ProcessTarget.STDERR,
    ):
        events = _append(
            events,
            OperationAttempt.succeeded(ProcessStage.SELECTOR_REGISTER, target),
        )
    events = _append(events, HandoffTransition(HandoffState.PRE_EXEC))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.SELECT, ProcessTarget.SELECTOR),
    )
    events = _append(events, ReadyBatch((Channel.STATUS, Channel.STDOUT)))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.READ, ProcessTarget.STATUS),
    )
    events = _append(events, ChannelEof(Channel.STATUS))
    events = _append(events, HandoffTransition(HandoffState.CONFIRMED))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.READ, ProcessTarget.STDOUT),
    )
    events = _append(events, BytesObserved(Channel.STDOUT, b"ok", b"ok"))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.SELECT, ProcessTarget.SELECTOR),
    )
    events = _append(events, ReadyBatch((Channel.STDOUT, Channel.STDERR)))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.READ, ProcessTarget.STDOUT),
    )
    events = _append(events, ChannelEof(Channel.STDOUT))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.READ, ProcessTarget.STDERR),
    )
    events = _append(events, ChannelEof(Channel.STDERR))
    events = _append(
        events,
        WaitObservation(
            WaitDisposition.STATUS,
            requested_child_pid=501,
            options=0,
            returned_pid=501,
            raw_wait_status=0,
            mechanism_errno=None,
        ),
    )
    events = _append(events, FinalizationBegin(), phase=EventPhase.FINALIZE)
    for target in (
        ProcessTarget.STATUS,
        ProcessTarget.STDOUT,
        ProcessTarget.STDERR,
    ):
        events = _append(
            events,
            OperationAttempt.succeeded(ProcessStage.SELECTOR_UNREGISTER, target),
            phase=EventPhase.FINALIZE,
        )
    for target in (
        ProcessTarget.STATUS,
        ProcessTarget.STDOUT,
        ProcessTarget.STDERR,
    ):
        events = _append(
            events,
            CloseAttempt.succeeded(target),
            phase=EventPhase.FINALIZE,
        )
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.CLOSE, ProcessTarget.SELECTOR),
        phase=EventPhase.FINALIZE,
    )
    return _append(
        events,
        _root(RootObservationPhase.POST),
        phase=EventPhase.FINALIZE,
    )


def _failed_nonblocking_receipt(
    subject: ProcessCommandSubject, nonce: bytes
):
    events = _append((), DescriptorAcquired(Channel.STATUS))
    events = _append(
        events,
        OperationAttempt.failed(
            ProcessStage.NONBLOCKING_CONFIGURE,
            ProcessTarget.STATUS,
            kind=FailureKind.IO,
            mechanism_errno=errno.EIO,
            role=FailureRole.PRIMARY,
        ),
    )
    return build_process_receipt(subject, _invocation(subject, nonce), events)


def test_replay_rederives_required_work_instead_of_trusting_event_delta() -> None:
    zero = ProcessWorkVector.zero()
    subject = _subject(
        envelope=ProcessWorkEnvelope(zero, zero),
        retry_contract=RetryContract(()),
    )
    payload = OperationAttempt.succeeded(
        ProcessStage.PROCESS_START, ProcessTarget.PROCESS
    )
    unsigned = {
        "event_index": 0,
        "previous_event_hash": None,
        "phase": EventPhase.MAIN.value,
        "payload": process_receipt._event_payload(payload),
        "work_delta": process_receipt._work_payload(zero),
    }
    forged = ProcessLifecycleEvent(
        0,
        None,
        EventPhase.MAIN,
        payload,
        zero,
        process_receipt.canonical_digest(
            unsigned, domain=process_receipt._EVENT_DOMAIN
        ),
    )

    with pytest.raises(ValueError, match="work delta|accounting"):
        build_process_receipt(
            subject,
            _invocation(subject, b"w" * 32),
            (forged,),
        )


def test_recurrence_retains_registered_prefix_as_causal_discriminator() -> None:
    subject = _subject()
    no_prefix = _append(
        (),
        OperationAttempt.succeeded(
            ProcessStage.SELECTOR_CREATE, ProcessTarget.SELECTOR
        ),
    )
    no_prefix = _append(
        no_prefix,
        OperationAttempt.failed(
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            kind=FailureKind.IO,
            mechanism_errno=errno.EIO,
            role=FailureRole.PRIMARY,
        ),
    )

    registered = _append((), DescriptorAcquired(Channel.STATUS))
    registered = _append(
        registered,
        OperationAttempt.succeeded(
            ProcessStage.SELECTOR_CREATE, ProcessTarget.SELECTOR
        ),
    )
    registered = _append(
        registered,
        OperationAttempt.succeeded(
            ProcessStage.NONBLOCKING_CONFIGURE, ProcessTarget.STATUS
        ),
    )
    registered = _append(
        registered,
        OperationAttempt.succeeded(
            ProcessStage.SELECTOR_REGISTER, ProcessTarget.STATUS
        ),
    )
    registered = _append(
        registered,
        OperationAttempt.failed(
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            kind=FailureKind.IO,
            mechanism_errno=errno.EIO,
            role=FailureRole.PRIMARY,
        ),
    )

    first = reduce_process_events(subject, no_prefix)
    second = reduce_process_events(subject, registered)
    assert first.registered_prefix != second.registered_prefix
    assert (
        first.failure_recurrence_signatures
        != second.failure_recurrence_signatures
    )


def test_cleanup_phase_labels_cannot_launder_finalize_reserve() -> None:
    payloads: list[tuple[object, EventPhase]] = []
    for event in _success_events():
        if isinstance(event.payload, FinalizationBegin):
            continue
        if (
            isinstance(event.payload, RootIdentityObservation)
            and event.payload.phase is RootObservationPhase.POST
        ):
            payloads.append((FinalizationBegin(), EventPhase.FINALIZE))
            payloads.append((event.payload, EventPhase.FINALIZE))
        elif event.phase is EventPhase.FINALIZE:
            payloads.append((event.payload, EventPhase.MAIN))
        else:
            payloads.append((event.payload, event.phase))

    state = reduce_process_events(_subject(), _rebuild(payloads))
    assert state.can_project_success is False


def test_success_projection_requires_unregister_cleanup_events() -> None:
    payloads = [
        (event.payload, event.phase)
        for event in _success_events()
        if not (
            isinstance(event.payload, OperationAttempt)
            and event.payload.stage is ProcessStage.SELECTOR_UNREGISTER
        )
    ]
    state = reduce_process_events(_subject(), _rebuild(payloads))
    assert state.can_project_success is False


def test_output_cap_plus_one_sentinel_blocks_success_projection() -> None:
    payloads: list[tuple[object, EventPhase]] = []
    for event in _success_events():
        payload = event.payload
        if isinstance(payload, BytesObserved) and payload.channel is Channel.STDOUT:
            payload = BytesObserved(Channel.STDOUT, b"ok!", b"ok")
        payloads.append((payload, event.phase))

    state = reduce_process_events(_subject(stdout_limit=2), _rebuild(payloads))
    assert state.stdout_acquired == b"ok!"
    assert state.stdout_retained == b"ok"
    assert state.can_project_success is False


def test_helper_status_bytes_cannot_be_relabelled_confirmed_handoff() -> None:
    payloads: list[tuple[object, EventPhase]] = []
    first_batch = True
    for event in _success_events():
        payload = event.payload
        if (
            isinstance(payload, HandoffTransition)
            and payload.state is HandoffState.PRE_EXEC
        ):
            continue
        if isinstance(payload, ReadyBatch) and first_batch:
            payload = ReadyBatch((Channel.STATUS,))
            first_batch = False
        if isinstance(payload, ChannelEof) and payload.channel is Channel.STATUS:
            payloads.extend(
                (
                    (BytesObserved(Channel.STATUS, b"EXECFAIL", b"EXECFAIL"), event.phase),
                    (
                        OperationAttempt.succeeded(
                            ProcessStage.SELECT, ProcessTarget.SELECTOR
                        ),
                        EventPhase.MAIN,
                    ),
                    (ReadyBatch((Channel.STATUS, Channel.STDOUT)), EventPhase.MAIN),
                    (
                        OperationAttempt.succeeded(
                            ProcessStage.READ, ProcessTarget.STATUS
                        ),
                        EventPhase.MAIN,
                    ),
                    (ChannelEof(Channel.STATUS), EventPhase.MAIN),
                    (HandoffTransition(HandoffState.PRE_EXEC), EventPhase.MAIN),
                )
            )
        else:
            payloads.append((payload, event.phase))

    state = reduce_process_events(_subject(), _rebuild(payloads))
    assert state.status_retained == b"EXECFAIL"
    assert state.can_project_success is False
    assert state.first_primary is not None


def test_failure_occurrence_identity_binds_invocation_nonce() -> None:
    subject = _subject()
    first = _failed_nonblocking_receipt(subject, b"a" * 32)
    second = _failed_nonblocking_receipt(subject, b"b" * 32)

    assert (
        first.derived_state.failure_recurrence_signatures
        == second.derived_state.failure_recurrence_signatures
    )
    assert (
        first.derived_state.failure_occurrences[0].occurrence_hash
        != second.derived_state.failure_occurrences[0].occurrence_hash
    )


def test_nonzero_exit_becomes_operational_failure_knowledge() -> None:
    payloads: list[tuple[object, EventPhase]] = []
    for event in _success_events():
        payload = event.payload
        if isinstance(payload, WaitObservation):
            payload = replace(payload, raw_wait_status=1 << 8)
        payloads.append((payload, event.phase))

    state = reduce_process_events(_subject(), _rebuild(payloads))
    assert state.returncode == 1
    assert state.can_project_success is False
    assert state.first_primary is not None
    assert state.failure_occurrences


def test_generic_timeout_operation_cannot_bypass_typed_observation() -> None:
    events = _append(
        (),
        OperationAttempt.failed(
            ProcessStage.TIMEOUT,
            ProcessTarget.PROCESS,
            kind=FailureKind.TIMEOUT,
            mechanism_errno=None,
            role=FailureRole.PRIMARY,
        ),
    )
    with pytest.raises(ValueError, match="typed|TimeoutObservation|bound child"):
        reduce_process_events(_subject(), events)


def test_failed_registration_requires_its_resource_predecessors() -> None:
    events = _append(
        (),
        OperationAttempt.failed(
            ProcessStage.SELECTOR_REGISTER,
            ProcessTarget.STATUS,
            kind=FailureKind.BAD_DESCRIPTOR,
            mechanism_errno=errno.EBADF,
            role=FailureRole.PRIMARY,
        ),
    )
    with pytest.raises(ValueError, match="selector|nonblocking|acquired|predecessor"):
        reduce_process_events(_subject(), events)


def test_retry_exhausted_requires_committed_retry_count() -> None:
    events: tuple[ProcessLifecycleEvent, ...] = ()
    for channel in Channel:
        events = _append(events, DescriptorAcquired(channel))
    events = _append(
        events,
        OperationAttempt.succeeded(
            ProcessStage.SELECTOR_CREATE, ProcessTarget.SELECTOR
        ),
    )
    for target in (
        ProcessTarget.STATUS,
        ProcessTarget.STDOUT,
        ProcessTarget.STDERR,
    ):
        events = _append(
            events,
            OperationAttempt.succeeded(ProcessStage.NONBLOCKING_CONFIGURE, target),
        )
    for target in (
        ProcessTarget.STATUS,
        ProcessTarget.STDOUT,
        ProcessTarget.STDERR,
    ):
        events = _append(
            events,
            OperationAttempt.succeeded(ProcessStage.SELECTOR_REGISTER, target),
        )
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.SELECT, ProcessTarget.SELECTOR),
    )
    events = _append(events, ReadyBatch((Channel.STDOUT,)))
    events = _append(
        events,
        OperationAttempt.failed(
            ProcessStage.READ,
            ProcessTarget.STDOUT,
            kind=FailureKind.RETRY_EXHAUSTED,
            mechanism_errno=errno.EAGAIN,
            role=FailureRole.PRIMARY,
        ),
    )

    with pytest.raises(ValueError, match="retry.*exhaust"):
        reduce_process_events(_subject(), events)


def test_post_cannot_complete_before_exact_child_wait_and_reap() -> None:
    events = _append(
        (),
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(events, ChildIdentityBound(77, 77, 50_000))
    events = _append(events, FinalizationBegin(), phase=EventPhase.FINALIZE)
    events = _append(
        events,
        _root(RootObservationPhase.POST),
        phase=EventPhase.FINALIZE,
    )

    with pytest.raises(ValueError, match="wait|reap|exit"):
        reduce_process_events(_subject(), events)


def test_finalize_wait_eintr_can_encode_its_bounded_retry() -> None:
    events = _append(
        (),
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(events, ChildIdentityBound(99, 99, 50_000))
    events = _append(events, FinalizationBegin(), phase=EventPhase.FINALIZE)
    events = _append(
        events,
        WaitObservation(
            WaitDisposition.INTERRUPTED,
            requested_child_pid=99,
            options=0,
            returned_pid=None,
            raw_wait_status=None,
            mechanism_errno=errno.EINTR,
        ),
        phase=EventPhase.FINALIZE,
    )
    events = _append(
        events,
        RetryObserved(
            ProcessStage.WAIT,
            ProcessTarget.PROCESS,
            RetryKind.INTERRUPTED,
            1,
        ),
        phase=EventPhase.FINALIZE,
    )

    state = reduce_process_events(_subject(), events)
    assert state.finalization_state is FinalizationState.IN_PROGRESS
    assert state.retry_counts[0].count == 1


def test_failed_spawn_does_not_claim_a_process_start_debit() -> None:
    events = _append(
        (),
        OperationAttempt.failed(
            ProcessStage.PROCESS_START,
            ProcessTarget.PROCESS,
            kind=FailureKind.NOT_FOUND,
            mechanism_errno=errno.ENOENT,
            role=FailureRole.PRIMARY,
        ),
    )
    state = reduce_process_events(_subject(), events)
    assert state.process_state is ProcessState.NOT_STARTED
    assert state.main_work.git_protocol_operations == 1
    assert state.main_work.git_process_starts == 0


@pytest.mark.parametrize("handoff", (HandoffState.FAILED, HandoffState.UNKNOWN))
def test_terminal_handoff_requires_a_started_helper_and_failure_knowledge(
    handoff: HandoffState,
) -> None:
    events = _append((), HandoffTransition(handoff))
    with pytest.raises(ValueError, match="started|PRE_EXEC|predecessor"):
        reduce_process_events(_subject(), events)


def test_forged_work_receipt_is_not_replay_verified_even_with_matching_hash() -> None:
    """The same accounting attack must fail at the public replay boundary."""

    zero = ProcessWorkVector.zero()
    subject = _subject(
        envelope=ProcessWorkEnvelope(zero, zero),
        retry_contract=RetryContract(()),
    )
    payload = HandoffTransition(HandoffState.UNKNOWN)
    invented = replace(zero, records_admitted=1)
    subject = replace(
        subject,
        work_envelope=ProcessWorkEnvelope(invented, zero),
        command_subject_hash="",
    )
    unsigned = {
        "event_index": 0,
        "previous_event_hash": None,
        "phase": EventPhase.MAIN.value,
        "payload": process_receipt._event_payload(payload),
        "work_delta": process_receipt._work_payload(invented),
    }
    forged = ProcessLifecycleEvent(
        0,
        None,
        EventPhase.MAIN,
        payload,
        invented,
        process_receipt.canonical_digest(
            unsigned, domain=process_receipt._EVENT_DOMAIN
        ),
    )
    receipt = build_process_receipt(
        subject,
        _invocation(subject, b"o" * 32),
        (forged,),
    )

    assert verify_process_receipt(receipt).status is not ReplayStatus.VERIFIED
