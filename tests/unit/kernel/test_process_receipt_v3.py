from __future__ import annotations

import errno
import os
import posix
import signal
from dataclasses import replace

import pytest

import orion.kernel.process_receipt as process_receipt

from orion.kernel.process_receipt import (
    PROCESS_RECEIPT_V2_SCHEMA_VERSION,
    PROCESS_RECEIPT_V3_SCHEMA_VERSION,
    PROCESS_RECEIPT_REDUCER_IDENTITY,
    PROCESS_RECEIPT_REPLAY_IDENTITY,
    PROCESS_WORK_DIMENSIONS,
    MAX_PROCESS_ARGV_ENTRIES,
    MAX_PROCESS_EVENT_COUNT,
    MAX_PROCESS_ID,
    MAX_PROCESS_OUTPUT_LIMIT,
    MAX_PROCESS_TEXT_BYTES,
    PROCESS_HOST_NONCE_BYTES,
    PROCESS_HELPER_STATUS_ACQUISITION_LIMIT,
    PROCESS_HELPER_STATUS_FRAME_LIMIT,
    PROCESS_HELPER_STATUS_RECEIPT_LIMIT,
    BytesObserved,
    Channel,
    ChannelEof,
    ChildIdentityBound,
    CloseAttempt,
    CloseDisposition,
    DeadlineCompletion,
    DescriptorAcquired,
    DeadlineEffectPhase,
    EventPhase,
    ExitObserved,
    ExitState,
    FailureKind,
    FailureRole,
    FinalizationBegin,
    HandoffState,
    HandoffTransition,
    LegacyCutoverDisposition,
    MaterializedInvocation,
    OperationAttempt,
    ProcessCommandSubject,
    ProcessLifecycleEvent,
    ProcessOperation,
    ProcessReceiptV3,
    ProcessStartCompletion,
    ProcessStage,
    ProcessState,
    ProcessTarget,
    ProcessWorkEnvelope,
    ProcessWorkVector,
    ReadyBatch,
    ReapDisposition,
    ReapObservation,
    ReplayStatus,
    RetryContract,
    RetryKind,
    RetryObserved,
    RootIdentityObservation,
    RootObservationDisposition,
    RootObservationPhase,
    SelectorState,
    SignalAttempt,
    StrictDeadlineFeasibility,
    TimeoutObservation,
    WaitDisposition,
    WaitMode,
    WaitObservation,
    WaitStatusKind,
    WaitStatusProvenance,
    append_process_event,
    build_process_receipt,
    cutover_process_receipt_v2,
    reduce_process_events,
    verify_process_receipt,
)


HEX_A = "a" * 64
HEX_B = "b" * 64
PRE_EXEC_FRAME = (
    b'{"errno":null,"kind":null,"stage":"HELPER_PRE_EXEC",'
    b'"version":"orion.git-helper-status.v1"}\n'
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


def _subject(
    *,
    retry_contract: RetryContract | None = None,
    envelope: ProcessWorkEnvelope | None = None,
    status_limit: int = 1024,
    stdout_limit: int = 32,
    stderr_limit: int = 32,
    combined_limit: int = 64,
) -> ProcessCommandSubject:
    return ProcessCommandSubject(
        operation=ProcessOperation.PROTECTED_GIT,
        logical_argv=("git", "status", "--porcelain=v2"),
        logical_environment=(("LC_ALL", "C"), ("PATH", "/usr/bin:/bin")),
        root_subject_hash=HEX_A,
        instrument_subject_hash=HEX_B,
        requested_timeout_ns=5_000_000_000,
        status_limit=status_limit,
        stdout_limit=stdout_limit,
        stderr_limit=stderr_limit,
        combined_limit=combined_limit,
        work_envelope=envelope
        or ProcessWorkEnvelope(main_limit=_work_limit(), finalize_limit=_work_limit()),
        retry_contract=retry_contract or RetryContract.frozen_default(),
    )


def _invocation(subject: ProcessCommandSubject, nonce: bytes) -> MaterializedInvocation:
    return MaterializedInvocation(
        command_subject_hash=subject.command_subject_hash,
        host_nonce=nonce,
        materialized_argv=("/usr/bin/python3", "-I", "helper.py", "17"),
        materialized_environment=(
            ("LC_ALL", "C"),
            ("PATH", "/usr/bin:/bin"),
        ),
    )


def _strict_subject_and_invocation() -> tuple[
    ProcessCommandSubject, MaterializedInvocation
]:
    subject = replace(
        _subject(),
        clock_contract_hash=process_receipt.PROCESS_CLOCK_CONTRACT.clock_contract_hash,
        deadline_decoder_identity=(process_receipt.PROCESS_DEADLINE_DECODER_IDENTITY),
        command_subject_hash="",
    )
    invocation = replace(
        _invocation(subject, b"s" * PROCESS_HOST_NONCE_BYTES),
        strict_deadline_contract_identity=(
            process_receipt.PROCESS_STRICT_DEADLINE_CONTRACT_IDENTITY
        ),
        clock_domain_occurrence_id=(
            process_receipt.PROCESS_CLOCK_DOMAIN_OCCURRENCE.clock_domain_occurrence_id
        ),
        select_timeout_contract_hash=(
            process_receipt.PROCESS_SELECT_TIMEOUT_CONTRACT.select_timeout_contract_hash
        ),
        invocation_occurrence_id="",
    )
    return subject, invocation


def _append(
    events: tuple[ProcessLifecycleEvent, ...],
    payload: object,
    *,
    phase: EventPhase = EventPhase.MAIN,
    work_delta: ProcessWorkVector | None = None,
) -> tuple[ProcessLifecycleEvent, ...]:
    return append_process_event(
        events,
        payload,
        phase=phase,
        work_delta=work_delta,
    )


def _root_observation(phase: RootObservationPhase) -> RootIdentityObservation:
    return RootIdentityObservation(
        phase=phase,
        disposition=RootObservationDisposition.MATCHED,
        configured_device=11,
        configured_inode=12,
        descriptor_device=11,
        descriptor_inode=12,
        mechanism_errno=None,
    )


def _failed_receipt(
    subject: ProcessCommandSubject,
    nonce: bytes,
    *,
    stage: ProcessStage,
) -> ProcessReceiptV3:
    events: tuple[ProcessLifecycleEvent, ...] = ()
    events = _append(events, DescriptorAcquired(Channel.STATUS))
    if stage is ProcessStage.SELECTOR_REGISTER:
        events = _append(
            events,
            OperationAttempt.succeeded(
                ProcessStage.SELECTOR_CREATE, ProcessTarget.SELECTOR
            ),
        )
        events = _append(
            events,
            OperationAttempt.succeeded(
                ProcessStage.NONBLOCKING_CONFIGURE, ProcessTarget.STATUS
            ),
        )
    events = _append(
        events,
        OperationAttempt.failed(
            stage,
            ProcessTarget.STATUS,
            kind=FailureKind.BAD_DESCRIPTOR,
            mechanism_errno=errno.EBADF,
            role=FailureRole.PRIMARY,
        ),
    )
    return build_process_receipt(subject, _invocation(subject, nonce), events)


def _success_events() -> tuple[ProcessLifecycleEvent, ...]:
    events: tuple[ProcessLifecycleEvent, ...] = ()
    events = _append(events, _root_observation(RootObservationPhase.PRE))
    for channel in Channel:
        events = _append(events, DescriptorAcquired(channel))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(
        events,
        ChildIdentityBound(
            child_pid=501,
            process_group_id=501,
            deadline_monotonic_ns=50_000,
        ),
    )
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
    events = _append(events, ReadyBatch((Channel.STATUS, Channel.STDOUT)))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.READ, ProcessTarget.STATUS),
    )
    events = _append(
        events,
        BytesObserved(Channel.STATUS, PRE_EXEC_FRAME, PRE_EXEC_FRAME),
    )
    events = _append(events, HandoffTransition(HandoffState.PRE_EXEC))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.READ, ProcessTarget.STDOUT),
    )
    events = _append(events, BytesObserved(Channel.STDOUT, b"ok", b"ok"))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.SELECT, ProcessTarget.SELECTOR),
    )
    events = _append(
        events,
        ReadyBatch((Channel.STATUS, Channel.STDOUT, Channel.STDERR)),
    )
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
    events = _append(events, ChannelEof(Channel.STDOUT))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.READ, ProcessTarget.STDERR),
    )
    events = _append(events, ChannelEof(Channel.STDERR))
    events = _append(
        events,
        WaitObservation(
            disposition=WaitDisposition.STATUS,
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
    events = _append(
        events,
        _root_observation(RootObservationPhase.POST),
        phase=EventPhase.FINALIZE,
    )
    return events


def _success_events_with_wait_status(
    raw_wait_status: int,
) -> tuple[ProcessLifecycleEvent, ...]:
    rebuilt: tuple[ProcessLifecycleEvent, ...] = ()
    for event in _success_events():
        payload = event.payload
        if isinstance(payload, WaitObservation):
            payload = replace(payload, raw_wait_status=raw_wait_status)
        rebuilt = _append(rebuilt, payload, phase=event.phase)
    return rebuilt


def test_v3_uses_one_all_outcome_schema_and_false_authority_literals() -> None:
    subject = _subject()
    receipt = build_process_receipt(subject, _invocation(subject, b"n" * 32), ())

    assert receipt.schema_version == PROCESS_RECEIPT_V3_SCHEMA_VERSION
    assert receipt.operational_only is True
    assert receipt.scientific_authority is False
    assert receipt.promotion_authority is False
    assert verify_process_receipt(receipt).status is ReplayStatus.VERIFIED

    forged = replace(receipt, scientific_authority=True)
    assert verify_process_receipt(forged).status is ReplayStatus.AUTHORITY_VIOLATION


@pytest.mark.parametrize(
    ("raw_wait_status", "expected_returncode", "expected_signal", "expected_kind"),
    (
        (73 << 8, 73, None, "EXIT_NONZERO"),
        (int(signal.SIGKILL), -int(signal.SIGKILL), int(signal.SIGKILL), "SIGNALLED"),
    ),
)
def test_canonical_abnormal_exit_derives_failed_process_knowledge(
    raw_wait_status: int,
    expected_returncode: int,
    expected_signal: int | None,
    expected_kind: str,
) -> None:
    state = reduce_process_events(
        _subject(), _success_events_with_wait_status(raw_wait_status)
    )

    assert state.handoff_state is HandoffState.CONFIRMED
    assert state.returncode == expected_returncode
    assert state.termination_signal == expected_signal
    assert state.can_project_success is False
    assert state.first_primary is not None
    assert state.first_primary.stage is ProcessStage.WAIT
    assert state.first_primary.target is ProcessTarget.PROCESS
    assert state.first_primary.kind.value == expected_kind
    assert state.first_primary.role is FailureRole.PRIMARY
    assert len(state.failure_occurrences) == 1
    assert len(state.failure_recurrence_signatures) == 1


def test_portable_caps_reject_host_nonce_text_count_integer_and_limit_b_plus_one() -> (
    None
):
    subject = _subject()
    assert len(b"n" * PROCESS_HOST_NONCE_BYTES) == PROCESS_HOST_NONCE_BYTES
    for size in (PROCESS_HOST_NONCE_BYTES - 1, PROCESS_HOST_NONCE_BYTES + 1):
        with pytest.raises(ValueError, match="exactly"):
            _invocation(subject, b"n" * size)

    with pytest.raises(ValueError, match="entry cap"):
        MaterializedInvocation(
            command_subject_hash=subject.command_subject_hash,
            host_nonce=b"n" * PROCESS_HOST_NONCE_BYTES,
            materialized_argv=("x",) * (MAX_PROCESS_ARGV_ENTRIES + 1),
            materialized_environment=(),
        )
    with pytest.raises(ValueError, match="UTF-8 cap"):
        MaterializedInvocation(
            command_subject_hash=subject.command_subject_hash,
            host_nonce=b"n" * PROCESS_HOST_NONCE_BYTES,
            materialized_argv=("x" * (MAX_PROCESS_TEXT_BYTES + 1),),
            materialized_environment=(),
        )
    with pytest.raises(ValueError, match="portable maximum"):
        ChildIdentityBound(MAX_PROCESS_ID + 1, 1, 1)
    with pytest.raises(ValueError, match="portable maximum"):
        replace(subject, status_limit=MAX_PROCESS_OUTPUT_LIMIT + 1)


def test_event_sequence_cap_rejects_b_plus_one_even_for_zero_cost_payloads() -> None:
    events: tuple[ProcessLifecycleEvent, ...] = ()
    for _ in range(MAX_PROCESS_EVENT_COUNT):
        events = _append(events, HandoffTransition(HandoffState.UNKNOWN))
    assert len(events) == MAX_PROCESS_EVENT_COUNT
    with pytest.raises(ValueError, match="event count cap"):
        _append(events, HandoffTransition(HandoffState.UNKNOWN))


def test_stage_target_table_distinguishes_nonblocking_from_registration() -> None:
    subject = _subject()
    nonblocking = _failed_receipt(
        subject, b"a" * 32, stage=ProcessStage.NONBLOCKING_CONFIGURE
    )
    registration = _failed_receipt(
        subject, b"b" * 32, stage=ProcessStage.SELECTOR_REGISTER
    )

    assert (
        nonblocking.derived_state.failure_recurrence_signatures
        != registration.derived_state.failure_recurrence_signatures
    )
    with pytest.raises(ValueError, match="stage-target"):
        OperationAttempt.succeeded(ProcessStage.READ, ProcessTarget.SELECTOR)


def test_stage_specific_errno_kinds_cannot_collapse_readiness_or_spawn_limit() -> None:
    with pytest.raises(ValueError, match="stage-specific"):
        OperationAttempt.failed(
            ProcessStage.PROCESS_START,
            ProcessTarget.PROCESS,
            kind=FailureKind.WOULD_BLOCK,
            mechanism_errno=errno.EAGAIN,
            role=FailureRole.PRIMARY,
        )
    spawn_limit = OperationAttempt.failed(
        ProcessStage.PROCESS_START,
        ProcessTarget.PROCESS,
        kind=FailureKind.PROCESS_LIMIT,
        mechanism_errno=errno.EAGAIN,
        role=FailureRole.PRIMARY,
    )
    assert spawn_limit.failure_kind is FailureKind.PROCESS_LIMIT

    with pytest.raises(ValueError, match="stage-specific"):
        OperationAttempt.failed(
            ProcessStage.READ,
            ProcessTarget.STDOUT,
            kind=FailureKind.WOULD_BLOCK,
            mechanism_errno=errno.EAGAIN,
            role=FailureRole.PRIMARY,
        )
    race = OperationAttempt.retryable(
        ProcessStage.READ,
        ProcessTarget.STDOUT,
        kind=FailureKind.READINESS_RACE,
        mechanism_errno=errno.EAGAIN,
    )
    exhausted = OperationAttempt.failed(
        ProcessStage.READ,
        ProcessTarget.STDOUT,
        kind=FailureKind.RETRY_EXHAUSTED,
        mechanism_errno=errno.EAGAIN,
        role=FailureRole.PRIMARY,
    )
    assert race.failure_kind is FailureKind.READINESS_RACE
    assert exhausted.failure_kind is FailureKind.RETRY_EXHAUSTED


def test_receipt_binds_exact_reducer_and_replay_identity() -> None:
    subject = _subject()
    receipt = build_process_receipt(subject, _invocation(subject, b"r" * 32), ())
    assert receipt.reducer_identity == PROCESS_RECEIPT_REDUCER_IDENTITY
    assert receipt.replay_identity == PROCESS_RECEIPT_REPLAY_IDENTITY

    forged = replace(receipt, reducer_identity=HEX_A)
    assert (
        verify_process_receipt(forged).status is ReplayStatus.REDUCER_IDENTITY_MISMATCH
    )


def test_host_nonce_changes_occurrence_and_receipt_but_not_recurrence() -> None:
    subject = _subject()
    first = _failed_receipt(
        subject, b"a" * 32, stage=ProcessStage.NONBLOCKING_CONFIGURE
    )
    second = _failed_receipt(
        subject, b"b" * 32, stage=ProcessStage.NONBLOCKING_CONFIGURE
    )

    assert first.command_subject_hash == second.command_subject_hash
    assert (
        first.invocation.invocation_occurrence_id
        != second.invocation.invocation_occurrence_id
    )
    assert first.receipt_hash != second.receipt_hash
    assert (
        first.derived_state.failure_recurrence_signatures
        == second.derived_state.failure_recurrence_signatures
    )


def test_event_drop_reorder_and_duplicate_are_rejected() -> None:
    subject = _subject()
    receipt = _failed_receipt(subject, b"c" * 32, stage=ProcessStage.SELECTOR_REGISTER)

    dropped = replace(receipt, events=receipt.events[:-1])
    reordered = replace(receipt, events=(receipt.events[1], receipt.events[0]))
    duplicated = replace(receipt, events=receipt.events + (receipt.events[-1],))

    assert verify_process_receipt(dropped).status is ReplayStatus.DERIVATION_MISMATCH
    assert verify_process_receipt(reordered).status is ReplayStatus.EVENT_CHAIN_INVALID
    assert verify_process_receipt(duplicated).status is ReplayStatus.EVENT_CHAIN_INVALID


def test_full_relink_is_rejected_against_original_receipt_identity() -> None:
    subject = _subject()
    original = _failed_receipt(
        subject, b"d" * 32, stage=ProcessStage.NONBLOCKING_CONFIGURE
    )
    events: tuple[ProcessLifecycleEvent, ...] = ()
    events = _append(events, DescriptorAcquired(Channel.STATUS))
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
    relinked = build_process_receipt(subject, original.invocation, events)

    verification = verify_process_receipt(
        relinked, expected_receipt_hash=original.receipt_hash
    )
    assert verification.status is ReplayStatus.EXPECTED_RECEIPT_MISMATCH


def test_retry_contract_mutation_changes_subject_and_expected_replay() -> None:
    frozen = RetryContract.frozen_default()
    mutated = RetryContract(
        frozen.rules[:-1] + (replace(frozen.rules[-1], max_retries=3),)
    )
    original_subject = _subject(retry_contract=frozen)
    mutated_subject = _subject(retry_contract=mutated)
    assert original_subject.command_subject_hash != mutated_subject.command_subject_hash

    receipt = build_process_receipt(
        mutated_subject, _invocation(mutated_subject, b"e" * 32), ()
    )
    verification = verify_process_receipt(
        receipt, expected_retry_contract_hash=frozen.retry_contract_hash
    )
    assert verification.status is ReplayStatus.RETRY_CONTRACT_MISMATCH


def test_retry_events_are_bounded_by_the_committed_contract() -> None:
    subject = _subject()
    events: tuple[ProcessLifecycleEvent, ...] = ()
    events = _append(
        events,
        OperationAttempt.succeeded(
            ProcessStage.SELECTOR_CREATE, ProcessTarget.SELECTOR
        ),
    )
    for ordinal in range(1, 9):
        events = _append(
            events,
            OperationAttempt.retryable(
                ProcessStage.SELECT,
                ProcessTarget.SELECTOR,
                kind=FailureKind.EMPTY_READY,
                mechanism_errno=None,
            ),
        )
        events = _append(
            events,
            RetryObserved(
                ProcessStage.SELECT,
                ProcessTarget.SELECTOR,
                RetryKind.EMPTY_READY,
                ordinal,
            ),
        )
    receipt = build_process_receipt(subject, _invocation(subject, b"f" * 32), events)
    assert receipt.derived_state.retry_counts[0].count == 8

    over_limit = _append(
        events,
        OperationAttempt.retryable(
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            kind=FailureKind.EMPTY_READY,
            mechanism_errno=None,
        ),
    )
    over_limit = _append(
        over_limit,
        RetryObserved(
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            RetryKind.EMPTY_READY,
            9,
        ),
    )
    with pytest.raises(ValueError, match="retry contract"):
        build_process_receipt(subject, _invocation(subject, b"f" * 32), over_limit)


def test_retry_event_cannot_float_without_preceding_retryable_attempt() -> None:
    subject = _subject()
    events = _append(
        (),
        RetryObserved(
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            RetryKind.EMPTY_READY,
            1,
        ),
    )
    with pytest.raises(ValueError, match="preceding retryable"):
        reduce_process_events(subject, events)


def test_ready_read_and_bytes_require_exact_causal_predecessors() -> None:
    subject = _subject()
    with pytest.raises(ValueError, match="successful select"):
        reduce_process_events(
            subject,
            _append((), ReadyBatch((Channel.STDOUT,))),
        )
    with pytest.raises(ValueError, match="successful read"):
        reduce_process_events(
            subject,
            _append((), BytesObserved(Channel.STDOUT, b"x", b"x")),
        )


def test_exit_and_reap_cannot_be_fabricated_without_charged_wait_and_child() -> None:
    events = _append(
        (),
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(
        events,
        ChildIdentityBound(801, 801, deadline_monotonic_ns=50_000),
    )
    with pytest.raises(ValueError, match="closed process-event payload"):
        _append(events, ExitObserved(0))
    with pytest.raises(ValueError, match="closed process-event payload"):
        _append((), ReapObservation(ReapDisposition.UNKNOWN))


def test_cleanup_failure_cannot_mask_the_one_primary_failure() -> None:
    subject = _subject()
    events: tuple[ProcessLifecycleEvent, ...] = ()
    events = _append(events, DescriptorAcquired(Channel.STATUS))
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
    events = _append(events, FinalizationBegin(), phase=EventPhase.FINALIZE)
    events = _append(
        events,
        CloseAttempt.failed(
            ProcessTarget.STATUS, errno.EINTR, role=FailureRole.CLEANUP
        ),
        phase=EventPhase.FINALIZE,
    )
    receipt = build_process_receipt(subject, _invocation(subject, b"g" * 32), events)

    assert receipt.derived_state.first_primary is not None
    assert (
        receipt.derived_state.first_primary.stage is ProcessStage.NONBLOCKING_CONFIGURE
    )
    assert receipt.derived_state.first_primary.event_index == 1
    assert len(receipt.derived_state.failure_recurrence_signatures) == 2


def test_first_finalize_failure_is_primary_by_chronology_not_producer_label() -> None:
    subject = _subject()
    prefix: tuple[ProcessLifecycleEvent, ...] = ()
    prefix = _append(prefix, DescriptorAcquired(Channel.STATUS))
    prefix = _append(prefix, FinalizationBegin(), phase=EventPhase.FINALIZE)
    mislabeled = _append(
        prefix,
        CloseAttempt.failed(
            ProcessTarget.STATUS,
            errno.EIO,
            role=FailureRole.CLEANUP,
        ),
        phase=EventPhase.FINALIZE,
    )
    with pytest.raises(ValueError, match="chronology"):
        reduce_process_events(subject, mislabeled)

    correctly_labeled = _append(
        prefix,
        CloseAttempt.failed(
            ProcessTarget.STATUS,
            errno.EIO,
            role=FailureRole.PRIMARY,
        ),
        phase=EventPhase.FINALIZE,
    )
    state = reduce_process_events(subject, correctly_labeled)
    assert state.first_primary is not None
    assert state.first_primary.stage is ProcessStage.CLOSE


def test_recurrence_ignores_chronological_role_but_occurrence_identity_does_not() -> (
    None
):
    subject = _subject()
    first: tuple[ProcessLifecycleEvent, ...] = ()
    first = _append(first, DescriptorAcquired(Channel.STATUS))
    first = _append(first, FinalizationBegin(), phase=EventPhase.FINALIZE)
    first = _append(
        first,
        CloseAttempt.failed(ProcessTarget.STATUS, errno.EIO, role=FailureRole.PRIMARY),
        phase=EventPhase.FINALIZE,
    )
    first_state = reduce_process_events(subject, first)

    second: tuple[ProcessLifecycleEvent, ...] = ()
    second = _append(second, DescriptorAcquired(Channel.STATUS))
    second = _append(
        second,
        OperationAttempt.failed(
            ProcessStage.NONBLOCKING_CONFIGURE,
            ProcessTarget.STATUS,
            kind=FailureKind.IO,
            mechanism_errno=errno.EIO,
            role=FailureRole.PRIMARY,
        ),
    )
    second = _append(second, FinalizationBegin(), phase=EventPhase.FINALIZE)
    second = _append(
        second,
        CloseAttempt.failed(ProcessTarget.STATUS, errno.EIO, role=FailureRole.CLEANUP),
        phase=EventPhase.FINALIZE,
    )
    second_state = reduce_process_events(subject, second)

    assert (
        first_state.failure_recurrence_signatures[0]
        == second_state.failure_recurrence_signatures[1]
    )
    assert (
        first_state.failure_occurrences[0].occurrence_hash
        != second_state.failure_occurrences[1].occurrence_hash
    )


def test_second_primary_failure_is_rejected() -> None:
    subject = _subject()
    events: tuple[ProcessLifecycleEvent, ...] = ()
    events = _append(events, DescriptorAcquired(Channel.STATUS))
    for stage in (
        ProcessStage.NONBLOCKING_CONFIGURE,
        ProcessStage.NONBLOCKING_CONFIGURE,
    ):
        events = _append(
            events,
            OperationAttempt.failed(
                stage,
                ProcessTarget.STATUS,
                kind=FailureKind.IO,
                mechanism_errno=errno.EIO,
                role=FailureRole.PRIMARY,
            ),
        )
    with pytest.raises(ValueError, match="chronology"):
        build_process_receipt(subject, _invocation(subject, b"h" * 32), events)


def test_main_exhaustion_allows_only_the_reserved_finalize_envelope() -> None:
    one_descriptor = replace(_work_limit(0), descriptor_operation_attempts=1)
    finalize = replace(
        _work_limit(0),
        descriptor_operation_attempts=2,
    )
    subject = _subject(
        envelope=ProcessWorkEnvelope(
            main_limit=one_descriptor,
            finalize_limit=finalize,
        )
    )
    events: tuple[ProcessLifecycleEvent, ...] = ()
    events = _append(events, DescriptorAcquired(Channel.STATUS))
    events = _append(
        events,
        OperationAttempt.succeeded(
            ProcessStage.NONBLOCKING_CONFIGURE, ProcessTarget.STATUS
        ),
    )
    exhausted_main = _append(
        events,
        OperationAttempt.succeeded(
            ProcessStage.SELECTOR_REGISTER, ProcessTarget.STATUS
        ),
    )
    with pytest.raises(ValueError, match="main work envelope"):
        build_process_receipt(subject, _invocation(subject, b"i" * 32), exhausted_main)

    events = _append(events, FinalizationBegin(), phase=EventPhase.FINALIZE)
    events = _append(
        events,
        CloseAttempt.succeeded(ProcessTarget.STATUS),
        phase=EventPhase.FINALIZE,
    )
    events = _append(
        events,
        _root_observation(RootObservationPhase.POST),
        phase=EventPhase.FINALIZE,
    )
    receipt = build_process_receipt(subject, _invocation(subject, b"i" * 32), events)
    assert receipt.derived_state.finalize_indices == (2, 3, 4)


def test_work_lanes_use_exact_17_coordinate_evidence_vector() -> None:
    assert tuple(ProcessWorkVector.__dataclass_fields__) == PROCESS_WORK_DIMENSIONS
    assert len(PROCESS_WORK_DIMENSIONS) == 17


def test_finalization_begin_is_zero_and_os_attempts_charge_descriptor_work() -> None:
    begin = ProcessLifecycleEvent.create(
        event_index=0,
        previous_event_hash=None,
        phase=EventPhase.FINALIZE,
        payload=FinalizationBegin(),
    )
    assert begin.work_delta == ProcessWorkVector.zero()

    with pytest.raises(ValueError, match="finalization.*descriptor_operation_attempts"):
        ProcessLifecycleEvent.create(
            event_index=1,
            previous_event_hash=begin.event_hash,
            phase=EventPhase.FINALIZE,
            payload=SignalAttempt.succeeded(
                target=ProcessTarget.PROCESS,
                numeric_signal=int(signal.SIGKILL),
                child_pid=1,
                process_group_id=1,
            ),
            work_delta=ProcessWorkVector.zero(),
        )


def test_finalize_envelope_cannot_launder_new_main_work() -> None:
    subject = _subject()
    events = _append((), FinalizationBegin(), phase=EventPhase.FINALIZE)
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
        phase=EventPhase.FINALIZE,
    )
    with pytest.raises(ValueError, match="not permitted during FINALIZE"):
        reduce_process_events(subject, events)


def test_reaped_with_unobserved_exit_is_rejected() -> None:
    with pytest.raises(ValueError, match="closed process-event payload"):
        _append((), ReapObservation(ReapDisposition.REAPED))


def test_successful_signal_does_not_imply_exit_observation() -> None:
    subject = _subject()
    events = _append(
        (),
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(events, ChildIdentityBound(601, 601, 50_000))
    events = _append(
        events,
        SignalAttempt.succeeded(
            target=ProcessTarget.PROCESS_GROUP,
            numeric_signal=int(signal.SIGKILL),
            child_pid=601,
            process_group_id=601,
        ),
    )
    state = reduce_process_events(subject, events)
    assert state.exit_state is ExitState.UNOBSERVED


def test_signal_attempt_cannot_precede_process_start() -> None:
    subject = _subject()
    events = _append(
        (),
        SignalAttempt.succeeded(
            target=ProcessTarget.PROCESS_GROUP,
            numeric_signal=int(signal.SIGKILL),
            child_pid=601,
            process_group_id=601,
        ),
    )
    with pytest.raises(ValueError, match="exact child"):
        reduce_process_events(subject, events)


def test_wait_binds_exact_child_and_derives_exit_signal_and_reap() -> None:
    subject = _subject()
    events = _append(
        (),
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(events, ChildIdentityBound(1101, 1101, 50_000))
    events = _append(
        events,
        WaitObservation(
            disposition=WaitDisposition.STATUS,
            requested_child_pid=1101,
            options=0,
            returned_pid=1101,
            raw_wait_status=int(signal.SIGKILL),
            mechanism_errno=None,
        ),
    )
    state = reduce_process_events(subject, events)
    assert state.exit_state is ExitState.OBSERVED
    assert state.returncode == -signal.SIGKILL
    assert state.termination_signal == signal.SIGKILL
    assert state.reap_disposition is ReapDisposition.REAPED

    wrong = _append(
        events[:-1],
        WaitObservation(
            disposition=WaitDisposition.WRONG_PID,
            requested_child_pid=1101,
            options=0,
            returned_pid=1102,
            raw_wait_status=0,
            mechanism_errno=None,
        ),
    )
    wrong_state = reduce_process_events(subject, wrong)
    assert wrong_state.reap_disposition is ReapDisposition.UNKNOWN
    assert wrong_state.first_primary is not None
    assert wrong_state.first_primary.stage is ProcessStage.WAIT


def test_unregistered_wait_decoder_cannot_verify_a_raw_typed_forgery() -> None:
    numeric_signal = int(signal.SIGKILL)
    try:
        subject = replace(
            _subject(),
            wait_decoder_identity="f" * 64,
            wait_supported_signals=(numeric_signal,),
            command_subject_hash="",
        )
    except ValueError:
        return

    events = _append(
        (),
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(events, ChildIdentityBound(1101, 1101, 50_000))
    events = _append(
        events,
        WaitObservation(
            disposition=WaitDisposition.STATUS,
            requested_child_pid=1101,
            options=0,
            returned_pid=1101,
            raw_wait_status=0,
            mechanism_errno=None,
            mode=WaitMode.BLOCKING_TERMINAL,
            status_kind=WaitStatusKind.SIGNALLED,
            status_provenance=WaitStatusProvenance.REQUESTED,
            exit_code=None,
            status_signal=numeric_signal,
            decoder_identity="f" * 64,
        ),
    )
    try:
        receipt = build_process_receipt(
            subject,
            _invocation(subject, b"f" * 32),
            events,
        )
    except ValueError:
        return
    assert verify_process_receipt(receipt).status is not ReplayStatus.VERIFIED


def test_import_does_not_replace_the_host_waitstatus_decoder() -> None:
    assert os.waitstatus_to_exitcode is posix.waitstatus_to_exitcode


def test_timeout_binds_deadline_crossing_and_handoff_without_implying_exit() -> None:
    subject = _subject()
    events = _append(
        (),
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(events, ChildIdentityBound(1201, 1201, 50_000))
    events = _append(
        events,
        TimeoutObservation(
            deadline_monotonic_ns=50_000,
            observed_monotonic_ns=50_001,
            crossed=True,
            handoff_state=HandoffState.NOT_REACHED,
        ),
    )
    state = reduce_process_events(subject, events)
    assert state.timeout_observation == events[-1].payload
    assert state.first_primary is not None
    assert state.first_primary.stage is ProcessStage.TIMEOUT
    assert state.exit_state is ExitState.UNOBSERVED
    assert state.reap_disposition is ReapDisposition.UNOBSERVED


def test_failed_signal_is_failure_knowledge_without_implying_exit() -> None:
    subject = _subject()
    events = _append(
        (),
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(events, ChildIdentityBound(1301, 1301, 50_000))
    events = _append(
        events,
        SignalAttempt.failed(
            target=ProcessTarget.PROCESS_GROUP,
            numeric_signal=int(signal.SIGKILL),
            child_pid=1301,
            process_group_id=1301,
            mechanism_errno=errno.EPERM,
        ),
    )
    state = reduce_process_events(subject, events)
    assert state.first_primary is not None
    assert state.first_primary.stage is ProcessStage.TERMINATE
    assert state.exit_state is ExitState.UNOBSERVED


@pytest.mark.parametrize(
    ("mechanism_errno", "disposition"),
    (
        (errno.EINTR, CloseDisposition.OPEN_RETRYABLE),
        (errno.EINPROGRESS, CloseDisposition.DEALLOCATED_ASYNC_UNKNOWN),
        (errno.EIO, CloseDisposition.DEALLOCATED_ERROR),
        (errno.EBADF, CloseDisposition.INVALID_BEFORE_ATTEMPT),
    ),
)
def test_posix_close_failure_preserves_exact_final_state_and_recurrence(
    mechanism_errno: int, disposition: CloseDisposition
) -> None:
    subject = _subject()
    events: tuple[ProcessLifecycleEvent, ...] = ()
    events = _append(events, DescriptorAcquired(Channel.STATUS))
    events = _append(events, FinalizationBegin(), phase=EventPhase.FINALIZE)
    events = _append(
        events,
        CloseAttempt.failed(
            ProcessTarget.STATUS,
            mechanism_errno,
            role=FailureRole.PRIMARY,
        ),
        phase=EventPhase.FINALIZE,
    )
    state = reduce_process_events(subject, events)

    assert state.status_close_disposition is disposition
    assert state.can_project_success is False
    assert len(state.failure_recurrence_signatures) == 1


def test_posix_close_dispositions_have_distinct_recurrence_and_no_blind_retry() -> None:
    subject = _subject()
    signatures: set[str] = set()
    for mechanism_errno in (errno.EINTR, errno.EINPROGRESS, errno.EIO, errno.EBADF):
        events: tuple[ProcessLifecycleEvent, ...] = ()
        events = _append(events, DescriptorAcquired(Channel.STATUS))
        events = _append(events, FinalizationBegin(), phase=EventPhase.FINALIZE)
        events = _append(
            events,
            CloseAttempt.failed(
                ProcessTarget.STATUS,
                mechanism_errno,
                role=FailureRole.PRIMARY,
            ),
            phase=EventPhase.FINALIZE,
        )
        signatures.add(
            reduce_process_events(subject, events).failure_recurrence_signatures[0]
        )
    assert len(signatures) == 4

    retry = _append(
        (),
        RetryObserved(
            ProcessStage.CLOSE,
            ProcessTarget.STATUS,
            RetryKind.INTERRUPTED,
            1,
        ),
    )
    with pytest.raises(ValueError, match="preceding retryable"):
        reduce_process_events(subject, retry)


def test_eintr_close_permits_one_distinct_charged_followup_attempt() -> None:
    subject = _subject()
    events: tuple[ProcessLifecycleEvent, ...] = ()
    events = _append(events, DescriptorAcquired(Channel.STATUS))
    events = _append(events, FinalizationBegin(), phase=EventPhase.FINALIZE)
    events = _append(
        events,
        CloseAttempt.failed(
            ProcessTarget.STATUS,
            errno.EINTR,
            role=FailureRole.PRIMARY,
            attempt_ordinal=1,
        ),
        phase=EventPhase.FINALIZE,
    )
    events = _append(
        events,
        CloseAttempt.succeeded(ProcessTarget.STATUS, attempt_ordinal=2),
        phase=EventPhase.FINALIZE,
    )
    state = reduce_process_events(subject, events)
    assert state.status_close_disposition is CloseDisposition.CONFIRMED
    assert state.status_close_attempts == 2
    assert state.finalize_work.descriptor_operation_attempts == 2


@pytest.mark.parametrize("mechanism_errno", (errno.EINPROGRESS, errno.EIO, errno.EBADF))
def test_deallocated_or_invalid_close_cannot_be_retried(mechanism_errno: int) -> None:
    subject = _subject()
    events: tuple[ProcessLifecycleEvent, ...] = ()
    events = _append(events, DescriptorAcquired(Channel.STATUS))
    events = _append(events, FinalizationBegin(), phase=EventPhase.FINALIZE)
    events = _append(
        events,
        CloseAttempt.failed(
            ProcessTarget.STATUS,
            mechanism_errno,
            role=FailureRole.PRIMARY,
            attempt_ordinal=1,
        ),
        phase=EventPhase.FINALIZE,
    )
    events = _append(
        events,
        CloseAttempt.succeeded(ProcessTarget.STATUS, attempt_ordinal=2),
        phase=EventPhase.FINALIZE,
    )
    with pytest.raises(ValueError, match="only EINTR"):
        reduce_process_events(subject, events)


def test_ready_batch_is_canonical_and_duplicate_free() -> None:
    assert ReadyBatch((Channel.STATUS, Channel.STDOUT, Channel.STDERR)).channels == (
        Channel.STATUS,
        Channel.STDOUT,
        Channel.STDERR,
    )
    with pytest.raises(ValueError, match="canonical channel order"):
        ReadyBatch((Channel.STDERR, Channel.STATUS))
    with pytest.raises(ValueError, match="duplicate"):
        ReadyBatch((Channel.STATUS, Channel.STATUS))
    with pytest.raises(ValueError, match="nonempty"):
        ReadyBatch(())


def test_bytes_observed_separates_acquired_sentinel_from_retained_prefix() -> None:
    subject = _subject(stdout_limit=2, combined_limit=64)
    events: tuple[ProcessLifecycleEvent, ...] = ()
    events = _append(events, DescriptorAcquired(Channel.STATUS))
    events = _append(events, DescriptorAcquired(Channel.STDOUT))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(events, ChildIdentityBound(701, 701, 50_000))
    events = _append(
        events,
        OperationAttempt.succeeded(
            ProcessStage.SELECTOR_CREATE, ProcessTarget.SELECTOR
        ),
    )
    for target in (ProcessTarget.STATUS, ProcessTarget.STDOUT):
        events = _append(
            events,
            OperationAttempt.succeeded(ProcessStage.NONBLOCKING_CONFIGURE, target),
        )
    for target in (ProcessTarget.STATUS, ProcessTarget.STDOUT):
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
        OperationAttempt.succeeded(ProcessStage.READ, ProcessTarget.STDOUT),
    )
    events = _append(events, BytesObserved(Channel.STDOUT, b"abc", b"ab"))
    state = reduce_process_events(subject, events)

    assert state.stdout_bytes_observed == 3
    assert state.stdout_acquired == b"abc"
    assert state.stdout_retained == b"ab"
    assert state.main_work.git_stdout_bytes_observed == 3
    assert state.main_work.retained_bytes == 2
    with pytest.raises(ValueError, match="prefix"):
        BytesObserved(Channel.STDOUT, b"abc", b"ac")


def test_success_projection_requires_confirmed_close_reap_and_post() -> None:
    subject = _subject()
    receipt = build_process_receipt(
        subject,
        _invocation(subject, b"k" * 32),
        _success_events(),
    )
    state = receipt.derived_state

    assert state.acquired_prefix == tuple(Channel)
    assert state.nonblocking_prefix == tuple(Channel)
    assert state.registered_prefix == tuple(Channel)
    assert state.process_state is ProcessState.STARTED
    assert (state.child_pid, state.process_group_id) == (501, 501)
    assert state.pre_root_observation == _root_observation(RootObservationPhase.PRE)
    assert state.post_root_observation == _root_observation(RootObservationPhase.POST)
    assert state.selector_state is SelectorState.CLOSED_CONFIRMED
    assert state.unregistered_prefix == tuple(Channel)
    assert state.can_project_success is True
    assert state.stdout_bytes_observed == 2
    assert state.stdout_retained == b"ok"


def test_confirmed_handoff_requires_exact_canonical_status_receipt() -> None:
    subject = _subject()
    payloads: list[tuple[object, EventPhase]] = []
    for event in _success_events():
        payload = event.payload
        if isinstance(payload, BytesObserved) and payload.channel is Channel.STATUS:
            invalid = PRE_EXEC_FRAME.replace(b'"errno":null', b'"errno":0')
            payload = BytesObserved(Channel.STATUS, invalid, invalid)
        payloads.append((payload, event.phase))

    events: tuple[ProcessLifecycleEvent, ...] = ()
    for payload, phase in payloads:
        events = _append(events, payload, phase=phase)
    state = reduce_process_events(subject, events)

    assert state.handoff_state is not HandoffState.CONFIRMED
    assert state.first_primary is not None
    assert state.first_primary.kind is FailureKind.PROTOCOL
    assert state.can_project_success is False


def test_canonical_helper_exec_failure_is_exact_operational_knowledge() -> None:
    subject = _subject(
        envelope=ProcessWorkEnvelope(
            main_limit=_work_limit(1000),
            finalize_limit=_work_limit(1000),
        )
    )
    exec_failure = (
        PRE_EXEC_FRAME
        + f'{{"errno":{errno.EACCES},"kind":"ACCESS_POLICY",'
        '"stage":"HELPER_EXEC",'
        '"version":"orion.git-helper-status.v1"}\n'.encode("ascii")
    )
    events: tuple[ProcessLifecycleEvent, ...] = ()
    events = _append(events, DescriptorAcquired(Channel.STATUS))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(events, ChildIdentityBound(44, 44, 50_000))
    events = _append(
        events,
        OperationAttempt.succeeded(
            ProcessStage.SELECTOR_CREATE, ProcessTarget.SELECTOR
        ),
    )
    events = _append(
        events,
        OperationAttempt.succeeded(
            ProcessStage.NONBLOCKING_CONFIGURE, ProcessTarget.STATUS
        ),
    )
    events = _append(
        events,
        OperationAttempt.succeeded(
            ProcessStage.SELECTOR_REGISTER, ProcessTarget.STATUS
        ),
    )
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.SELECT, ProcessTarget.SELECTOR),
    )
    events = _append(events, ReadyBatch((Channel.STATUS,)))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.READ, ProcessTarget.STATUS),
    )
    events = _append(
        events,
        BytesObserved(Channel.STATUS, exec_failure, exec_failure),
    )
    events = _append(events, HandoffTransition(HandoffState.FAILED))
    state = reduce_process_events(subject, events)

    assert state.handoff_state is HandoffState.FAILED
    assert state.first_primary is not None
    assert state.first_primary.kind is FailureKind.PERMISSION
    assert state.first_primary.mechanism_errno == errno.EACCES
    assert state.can_project_success is False


def test_helper_status_caps_are_frozen_at_frame_two_frame_and_sentinel() -> None:
    assert PROCESS_HELPER_STATUS_FRAME_LIMIT == 512
    assert PROCESS_HELPER_STATUS_RECEIPT_LIMIT == 1024
    assert PROCESS_HELPER_STATUS_ACQUISITION_LIMIT == 1025
    with pytest.raises(ValueError, match="frozen helper-status receipt cap"):
        replace(_subject(), status_limit=1023, command_subject_hash="")


def test_cleanup_phase_is_derived_and_cannot_borrow_main_work() -> None:
    subject = _subject()
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

    events: tuple[ProcessLifecycleEvent, ...] = ()
    for payload, phase in payloads:
        events = _append(events, payload, phase=phase)
    state = reduce_process_events(subject, events)

    assert state.finalize_work.descriptor_operation_attempts > 0
    assert state.first_primary is not None
    assert state.can_project_success is False


def test_root_observation_identity_cannot_contradict_disposition() -> None:
    with pytest.raises(ValueError, match="contradicts"):
        RootIdentityObservation(
            phase=RootObservationPhase.PRE,
            disposition=RootObservationDisposition.MATCHED,
            configured_device=1,
            configured_inode=2,
            descriptor_device=1,
            descriptor_inode=3,
            mechanism_errno=None,
        )


def test_helper_status_cap_allows_only_one_unretained_1025th_sentinel() -> None:
    subject = _subject(
        status_limit=1024,
        envelope=ProcessWorkEnvelope(
            main_limit=_work_limit(5000), finalize_limit=_work_limit(5000)
        ),
    )
    events: tuple[ProcessLifecycleEvent, ...] = ()
    events = _append(events, DescriptorAcquired(Channel.STATUS))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(events, ChildIdentityBound(901, 901, 50_000))
    events = _append(
        events,
        OperationAttempt.succeeded(
            ProcessStage.SELECTOR_CREATE, ProcessTarget.SELECTOR
        ),
    )
    events = _append(
        events,
        OperationAttempt.succeeded(
            ProcessStage.NONBLOCKING_CONFIGURE, ProcessTarget.STATUS
        ),
    )
    events = _append(
        events,
        OperationAttempt.succeeded(
            ProcessStage.SELECTOR_REGISTER, ProcessTarget.STATUS
        ),
    )
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.SELECT, ProcessTarget.SELECTOR),
    )
    events = _append(events, ReadyBatch((Channel.STATUS,)))
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.READ, ProcessTarget.STATUS),
    )
    events = _append(events, BytesObserved(Channel.STATUS, b"s" * 1025, b"s" * 1024))
    state = reduce_process_events(subject, events)
    assert state.status_bytes_observed == 1025
    assert len(state.status_retained) == 1024

    too_much = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.SELECT, ProcessTarget.SELECTOR),
    )
    too_much = _append(too_much, ReadyBatch((Channel.STATUS,)))
    too_much = _append(
        too_much,
        OperationAttempt.succeeded(ProcessStage.READ, ProcessTarget.STATUS),
    )
    too_much = _append(
        too_much,
        BytesObserved(Channel.STATUS, b"x", b""),
    )
    with pytest.raises(ValueError, match="acquired sentinel cap"):
        reduce_process_events(subject, too_much)


def test_reap_unknown_or_close_unknown_blocks_projection() -> None:
    subject = _subject()
    events = _success_events()
    reap_index = next(
        index
        for index, event in enumerate(events)
        if isinstance(event.payload, WaitObservation)
    )
    rebuilt: tuple[ProcessLifecycleEvent, ...] = ()
    for index, event in enumerate(events):
        payload = (
            WaitObservation(
                disposition=WaitDisposition.NO_CHILD,
                requested_child_pid=501,
                options=0,
                returned_pid=None,
                raw_wait_status=None,
                mechanism_errno=errno.ECHILD,
            )
            if index == reap_index
            else event.payload
        )
        rebuilt = _append(rebuilt, payload, phase=event.phase)
    assert reduce_process_events(subject, rebuilt).can_project_success is False

    close_index = next(
        index
        for index, event in enumerate(events)
        if isinstance(event.payload, CloseAttempt)
        and event.payload.target is ProcessTarget.STATUS
    )
    rebuilt = ()
    for index, event in enumerate(events):
        payload = (
            CloseAttempt.failed(
                ProcessTarget.STATUS,
                errno.EINPROGRESS,
                role=FailureRole.PRIMARY,
            )
            if index == close_index
            else event.payload
        )
        rebuilt = _append(rebuilt, payload, phase=event.phase)
    assert reduce_process_events(subject, rebuilt).can_project_success is False


def test_v2_has_a_hard_cannot_migrate_cutover() -> None:
    cutover = cutover_process_receipt_v2(HEX_A)

    assert cutover.source_schema_version == PROCESS_RECEIPT_V2_SCHEMA_VERSION
    assert cutover.target_schema_version == PROCESS_RECEIPT_V3_SCHEMA_VERSION
    assert cutover.disposition is LegacyCutoverDisposition.CANNOT_MIGRATE
    assert not isinstance(cutover, ProcessReceiptV3)


def test_strict_deadline_data_contracts_rederive_their_closed_coordinates() -> None:
    completion = DeadlineCompletion.from_observation(
        effect_occurrence_id=HEX_A,
        deadline_binding_hash=HEX_B,
        child_occurrence_id=HEX_A,
        clock_domain_occurrence_id=HEX_B,
        completion_event_index=0,
        completion_previous_event_hash=None,
        deadline_monotonic_ns=10,
        observed_monotonic_ns=10,
    )
    assert completion.phase is DeadlineEffectPhase.POST_EFFECT
    assert completion.crossed is True
    assert completion.remaining_ns == 0
    with pytest.raises(ValueError, match="hash|completion"):
        replace(completion, deadline_completion_hash=HEX_A)

    start_completion = ProcessStartCompletion.from_observation(
        invocation_occurrence_id=HEX_A,
        deadline_binding_hash=HEX_B,
        child_occurrence_id=None,
        clock_domain_occurrence_id=HEX_A,
        completion_event_index=0,
        completion_previous_event_hash=None,
        deadline_monotonic_ns=11,
        observed_monotonic_ns=10,
    )
    assert start_completion.crossed is False
    assert start_completion.remaining_ns == 1
    with pytest.raises(ValueError, match="hash|completion"):
        replace(start_completion, process_start_completion_hash=HEX_B)

    with pytest.raises(ValueError, match="auxiliary|frozen|feasib"):
        StrictDeadlineFeasibility(
            main_effect_count=100,
            finalize_attempt_count=0,
            auxiliary_event_count=0,
            worst_case_main_event_count=500,
            worst_case_finalize_event_count=0,
            worst_case_total_event_count=500,
            maximum_event_count=512,
        )


def _forge_frozen_dataclass(value: object, **changes: object) -> object:
    forged = object.__new__(type(value))
    for name in value.__dataclass_fields__:
        object.__setattr__(
            forged,
            name,
            changes.get(name, getattr(value, name)),
        )
    return forged


def _unchecked_rehashed_event(payload: object) -> ProcessLifecycleEvent:
    work_delta = ProcessWorkVector.zero()
    unsigned = {
        "event_index": 0,
        "previous_event_hash": None,
        "phase": EventPhase.MAIN.value,
        "payload": process_receipt._event_payload(payload),
        "work_delta": process_receipt._work_payload(work_delta),
    }
    event = object.__new__(ProcessLifecycleEvent)
    object.__setattr__(event, "event_index", 0)
    object.__setattr__(event, "previous_event_hash", None)
    object.__setattr__(event, "phase", EventPhase.MAIN)
    object.__setattr__(event, "payload", payload)
    object.__setattr__(event, "work_delta", work_delta)
    object.__setattr__(
        event,
        "event_hash",
        process_receipt.canonical_digest(
            unsigned,
            domain=process_receipt._EVENT_DOMAIN,
        ),
    )
    return event


@pytest.mark.parametrize(
    "forgery",
    ("requested", "effective", "source", "commitment"),
)
def test_deadline_binding_is_self_validated_at_event_and_replay_boundaries(
    forgery: str,
) -> None:
    subject, invocation = _strict_subject_and_invocation()
    outer = process_receipt.OuterDeadlineCommitment(
        deadline_monotonic_ns=130,
        clock_domain_occurrence_id=(
            process_receipt.PROCESS_CLOCK_DOMAIN_OCCURRENCE.clock_domain_occurrence_id
        ),
        consumer_invocation_occurrence_id=invocation.invocation_occurrence_id,
        producer_invocation_occurrence_id=HEX_A,
        parent_deadline_binding_hash=HEX_B,
    )
    binding = process_receipt.DeadlineBinding.from_start_observation(
        invocation_occurrence_id=invocation.invocation_occurrence_id,
        started_monotonic_ns=100,
        requested_timeout_ns=subject.requested_timeout_ns,
        outer_deadline=outer,
        clock_domain_occurrence=process_receipt.PROCESS_CLOCK_DOMAIN_OCCURRENCE,
        clock_contract=process_receipt.PROCESS_CLOCK_CONTRACT,
        deadline_decoder_identity=process_receipt.PROCESS_DEADLINE_DECODER_IDENTITY,
    )
    changes: dict[str, object] = {}
    if forgery == "requested":
        changes["requested_deadline_monotonic_ns"] = (
            binding.requested_deadline_monotonic_ns - 1
        )
    elif forgery == "effective":
        changes["effective_deadline_monotonic_ns"] = (
            binding.requested_deadline_monotonic_ns
        )
    elif forgery == "source":
        changes["winning_source"] = process_receipt.DeadlineSource.REQUESTED_TIMEOUT
    else:
        changes["outer_deadline_commitment_hash"] = "c" * 64
    forged = _forge_frozen_dataclass(binding, **changes)

    with pytest.raises(ValueError, match="deadline|binding|commitment|payload"):
        ProcessLifecycleEvent.create(
            event_index=0,
            previous_event_hash=None,
            phase=EventPhase.MAIN,
            payload=forged,
        )

    unchecked_event = _unchecked_rehashed_event(forged)
    with pytest.raises(ValueError, match="deadline|binding|commitment|payload"):
        reduce_process_events(
            subject,
            (unchecked_event,),
            invocation_occurrence_id=invocation.invocation_occurrence_id,
        )


def test_deadline_payload_subclass_cannot_downgrade_to_legacy_identity() -> None:
    subject, invocation = _strict_subject_and_invocation()
    refusal = process_receipt.DeadlineRefusal.from_checked_add_overflow(
        invocation_occurrence_id=invocation.invocation_occurrence_id,
        started_monotonic_ns=(
            process_receipt.MAX_PROCESS_MONOTONIC_NS - subject.requested_timeout_ns + 1
        ),
        requested_timeout_ns=subject.requested_timeout_ns,
        outer_deadline=None,
        clock_domain_occurrence=process_receipt.PROCESS_CLOCK_DOMAIN_OCCURRENCE,
        clock_contract=process_receipt.PROCESS_CLOCK_CONTRACT,
        deadline_decoder_identity=process_receipt.PROCESS_DEADLINE_DECODER_IDENTITY,
    )

    class RefusalSubclass(process_receipt.DeadlineRefusal):
        pass

    subclass_payload = RefusalSubclass(
        **{name: getattr(refusal, name) for name in refusal.__dataclass_fields__}
    )
    events = _append((), refusal)
    object.__setattr__(events[0], "payload", subclass_payload)

    with pytest.raises(ValueError, match="exact|payload|closed"):
        build_process_receipt(subject, invocation, events)


def _unchecked_rehashed_trace(
    events: tuple[ProcessLifecycleEvent, ...],
    *,
    replacement_type: type[object],
    replacement: object,
) -> tuple[ProcessLifecycleEvent, ...]:
    rebuilt: list[ProcessLifecycleEvent] = []
    previous_event_hash: str | None = None
    for event_index, source in enumerate(events):
        payload = (
            replacement if type(source.payload) is replacement_type else source.payload
        )
        unsigned = {
            "event_index": event_index,
            "previous_event_hash": previous_event_hash,
            "phase": source.phase.value,
            "payload": process_receipt._event_payload(payload),
            "work_delta": process_receipt._work_payload(source.work_delta),
        }
        event_hash = process_receipt.canonical_digest(
            unsigned,
            domain=process_receipt._EVENT_DOMAIN,
        )
        forged_event = object.__new__(ProcessLifecycleEvent)
        object.__setattr__(forged_event, "event_index", event_index)
        object.__setattr__(
            forged_event,
            "previous_event_hash",
            previous_event_hash,
        )
        object.__setattr__(forged_event, "phase", source.phase)
        object.__setattr__(forged_event, "payload", payload)
        object.__setattr__(forged_event, "work_delta", source.work_delta)
        object.__setattr__(forged_event, "event_hash", event_hash)
        rebuilt.append(forged_event)
        previous_event_hash = event_hash
    return tuple(rebuilt)


def _receipt_with_graph(
    source: ProcessReceiptV3,
    *,
    subject: ProcessCommandSubject | None = None,
    invocation: MaterializedInvocation | None = None,
    events: tuple[ProcessLifecycleEvent, ...] | None = None,
    derived_state: object | None = None,
) -> ProcessReceiptV3:
    selected_subject = source.subject if subject is None else subject
    selected_invocation = source.invocation if invocation is None else invocation
    selected_events = source.events if events is None else events
    selected_state = source.derived_state if derived_state is None else derived_state
    receipt_hash = process_receipt._receipt_hash_for(
        schema_version=source.schema_version,
        subject=selected_subject,
        command_subject_hash=selected_subject.command_subject_hash,
        invocation=selected_invocation,
        retry_contract_hash=selected_subject.retry_contract.retry_contract_hash,
        reducer_identity=source.reducer_identity,
        replay_identity=source.replay_identity,
        events=selected_events,
        derived_state=selected_state,
        operational_only=source.operational_only,
        scientific_authority=source.scientific_authority,
        promotion_authority=source.promotion_authority,
    )
    return _forge_frozen_dataclass(
        source,
        subject=selected_subject,
        command_subject_hash=selected_subject.command_subject_hash,
        invocation=selected_invocation,
        retry_contract_hash=selected_subject.retry_contract.retry_contract_hash,
        events=selected_events,
        derived_state=selected_state,
        receipt_hash=receipt_hash,
    )


@pytest.mark.parametrize(
    ("payload_type", "changes"),
    (
        (WaitObservation, {"raw_wait_status": int(signal.SIGKILL)}),
        (ChildIdentityBound, {"deadline_monotonic_ns": 0}),
    ),
)
@pytest.mark.parametrize("boundary", ("create", "reduce", "build", "verify"))
def test_constructor_bypassed_p0_payload_cannot_gain_verified_success(
    payload_type: type[object],
    changes: dict[str, object],
    boundary: str,
) -> None:
    subject = _subject()
    invocation = _invocation(subject, b"v" * PROCESS_HOST_NONCE_BYTES)
    valid_events = _success_events()
    original = next(
        event.payload for event in valid_events if type(event.payload) is payload_type
    )
    forged = _forge_frozen_dataclass(original, **changes)

    if boundary == "create":
        with pytest.raises(ValueError, match="payload|constructor|valid"):
            ProcessLifecycleEvent.create(
                event_index=0,
                previous_event_hash=None,
                phase=EventPhase.MAIN,
                payload=forged,
            )
        return

    forged_events = _unchecked_rehashed_trace(
        valid_events,
        replacement_type=payload_type,
        replacement=forged,
    )
    if boundary == "reduce":
        with pytest.raises(ValueError, match="payload|constructor|valid"):
            reduce_process_events(
                subject,
                forged_events,
                invocation_occurrence_id=invocation.invocation_occurrence_id,
            )
        return
    if boundary == "build":
        with pytest.raises(ValueError, match="payload|constructor|valid"):
            build_process_receipt(subject, invocation, forged_events)
        return

    valid_receipt = build_process_receipt(subject, invocation, valid_events)
    forged_receipt = _receipt_with_graph(valid_receipt, events=forged_events)
    verification = verify_process_receipt(forged_receipt)
    assert verification.status is not ReplayStatus.VERIFIED
    assert not verification.valid


def _rehash_subject(
    subject: ProcessCommandSubject,
    **changes: object,
) -> ProcessCommandSubject:
    forged = _forge_frozen_dataclass(
        subject,
        **changes,
        command_subject_hash="",
    )
    object.__setattr__(
        forged,
        "command_subject_hash",
        process_receipt.canonical_digest(
            process_receipt._command_subject_payload(forged),
            domain=process_receipt._COMMAND_SUBJECT_DOMAIN,
        ),
    )
    return forged


def _rehash_invocation(
    invocation: MaterializedInvocation,
    **changes: object,
) -> MaterializedInvocation:
    forged = _forge_frozen_dataclass(
        invocation,
        **changes,
        invocation_occurrence_id="",
    )
    object.__setattr__(
        forged,
        "invocation_occurrence_id",
        process_receipt.canonical_digest(
            process_receipt._invocation_payload(forged),
            domain=process_receipt._INVOCATION_OCCURRENCE_DOMAIN,
        ),
    )
    return forged


def _constructor_bypassed_subject_and_invocation(
    forgery: str,
) -> tuple[ProcessCommandSubject, MaterializedInvocation]:
    subject = _subject()
    invocation = _invocation(subject, b"g" * PROCESS_HOST_NONCE_BYTES)
    if forgery == "subject-timeout":
        subject = _rehash_subject(subject, requested_timeout_ns=0)
        invocation = _rehash_invocation(
            invocation,
            command_subject_hash=subject.command_subject_hash,
        )
    elif forgery == "nested-retry-rule":
        contract = subject.retry_contract
        bad_rule = _forge_frozen_dataclass(contract.rules[0], max_retries=0)
        bad_contract = _forge_frozen_dataclass(
            contract,
            rules=(bad_rule,) + contract.rules[1:],
            retry_contract_hash="",
        )
        object.__setattr__(
            bad_contract,
            "retry_contract_hash",
            process_receipt.canonical_digest(
                [
                    process_receipt._retry_rule_payload(rule)
                    for rule in bad_contract.rules
                ],
                domain=process_receipt._RETRY_CONTRACT_DOMAIN,
            ),
        )
        subject = _rehash_subject(subject, retry_contract=bad_contract)
        invocation = _rehash_invocation(
            invocation,
            command_subject_hash=subject.command_subject_hash,
        )
    else:
        invocation = _rehash_invocation(invocation, host_nonce=b"n" * 31)
    return subject, invocation


@pytest.mark.parametrize(
    "forgery",
    ("subject-timeout", "nested-retry-rule", "invocation-nonce"),
)
@pytest.mark.parametrize("boundary", ("build", "verify"))
def test_constructor_bypassed_receipt_graph_fails_closed_at_public_boundaries(
    forgery: str,
    boundary: str,
) -> None:
    valid_subject = _subject()
    valid_invocation = _invocation(
        valid_subject,
        b"g" * PROCESS_HOST_NONCE_BYTES,
    )
    valid_receipt = build_process_receipt(
        valid_subject,
        valid_invocation,
        _success_events(),
    )
    subject, invocation = _constructor_bypassed_subject_and_invocation(forgery)

    if boundary == "build":
        with pytest.raises(ValueError, match="subject|invocation|constructor|valid"):
            build_process_receipt(subject, invocation, valid_receipt.events)
        return

    forged_receipt = _receipt_with_graph(
        valid_receipt,
        subject=subject,
        invocation=invocation,
    )
    verification = verify_process_receipt(forged_receipt)
    assert verification.status is not ReplayStatus.VERIFIED
    assert not verification.valid


def test_replay_compares_serialized_failure_occurrence_identity() -> None:
    receipt = _failed_receipt(
        _subject(),
        b"o" * PROCESS_HOST_NONCE_BYTES,
        stage=ProcessStage.SELECTOR_REGISTER,
    )
    occurrence = receipt.derived_state.failure_occurrences[0]
    forged_occurrence = _forge_frozen_dataclass(
        occurrence,
        occurrence_hash="f" * 64,
    )
    forged_state = _forge_frozen_dataclass(
        receipt.derived_state,
        first_primary=forged_occurrence,
        failure_occurrences=(forged_occurrence,),
    )
    forged_receipt = _receipt_with_graph(
        receipt,
        derived_state=forged_state,
    )

    verification = verify_process_receipt(forged_receipt)
    assert verification.status is ReplayStatus.DERIVATION_MISMATCH
    assert not verification.valid
