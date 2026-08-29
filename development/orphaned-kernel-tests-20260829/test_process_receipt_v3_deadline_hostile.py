"""Hostile oracle for Process Receipt V3 absolute-deadline provenance.

The strict lane is an ordered protocol, not a caller-attached timeout label.
Every post-spawn external effect uses::

    typed binding -> DeadlineAdmission(PRE) -> external effect -> typed result
    -> DeadlineCompletion(POST) -> result interpretation / possible retry

PROCESS_START is the sole pre-child exception: DeadlineBinding is its PRE,
event-chain position plus invocation occurrence is its occurrence identity, and
ProcessStartCompletion is its POST.  A successful attempt binds the new child
between those observations; a failed attempt does not invent one.  The uniform
effect-occurrence grammar begins only once a child occurrence exists.

An admission is bound to its exact event-chain position and one globally
ordered MAIN effect occurrence.  A completion closes only that occurrence.
Completion-time crossing retains the completed attempt and any result already
returned by it, latches TIMEOUT, and forbids every later MAIN external effect.

The selector lane commits the registered capture-host backend, timeout encoder,
syscall wrapper, and EINTR visibility.  CPython's PEP-475 internal retries are
one opaque logical SELECT effect and must never also appear as a visible
``RetryObserved(INTERRUPTED)``.  Outer deadlines are accepted only through a
typed same-clock-domain occurrence commitment; a bare monotonic integer has no
portable meaning.

The logical subject deliberately retains its P0 clock-contract and decoder
mechanism commitments, even though this makes it capture-host dependent.  The
host epoch occurrence and selector backend coordinates belong only to the
materialized invocation; later cross-host normalization remains outside P1.

Deferred outside P1: host authenticity of clock readings; suspend, VM, reboot,
and cross-host translation policy; scheduler/syscall hard-real-time overshoot;
capture wiring beyond a closed local registry; hidden-retry audit beyond that
registry; READ hard-duration bounds; OS watchdog/kill latency; and separately
frozen cleanup reserve policy.  Legacy receipts remain valid only in their
byte-identical legacy reducer lane and cannot acquire strict authority by
relinking strict events.  These residuals grant no scientific, promotion, or
solution authority.
"""

from __future__ import annotations

import errno
import inspect
import math
import struct
import time
from dataclasses import replace

import pytest

import orion.kernel.process_receipt as process_receipt
from orion.kernel.process_receipt import (
    BytesObserved,
    Channel,
    ChannelEof,
    ChildIdentityBound,
    DescriptorAcquired,
    EventPhase,
    FailureKind,
    FailureRole,
    FinalizationBegin,
    FinalizationState,
    HandoffState,
    MaterializedInvocation,
    OperationAttempt,
    ProcessCommandSubject,
    ProcessLifecycleEvent,
    ProcessOperation,
    ProcessStage,
    ProcessTarget,
    ProcessWorkEnvelope,
    ProcessWorkVector,
    ReadyBatch,
    ReplayStatus,
    RetryContract,
    RetryKind,
    RetryObserved,
    TimeoutObservation,
    WaitDisposition,
    WaitObservation,
    append_process_event,
    build_process_receipt,
    reduce_process_events,
    verify_process_receipt,
)
from orion.kernel.transition import canonical_digest


HEX_A = "a" * 64
HEX_B = "b" * 64
HEX_C = "c" * 64
MAX_NS = (1 << 63) - 1
START_NS = 100
TIMEOUT_NS = 50
REQUESTED_DEADLINE_NS = START_NS + TIMEOUT_NS
# Subject, invocation, and receipt identities deliberately commit the registered
# P0 wait decoder, including its interpreter/platform coordinates.  Freeze their
# portable payload relation below rather than one host-specific digest literal.
LEGACY_P0_RETRY_CONTRACT_HASH = (
    "3025bad2c6c71776b387cf82d973cb20761b80f524bba27a8e76bbd504da74fb"
)
LEGACY_P0_REDUCER_IDENTITY = (
    "0f6a4b1e9fe0084827f1579645637c70312b2cadc1662b1b68012a443f31c4bb"
)
LEGACY_P0_REPLAY_IDENTITY = (
    "06e63d41a8e468533444f0542dd99fcad987d0824adae2a0ed9d060d4232fac6"
)
LEGACY_FAILED_START_EVENT_HASH = (
    "4af5dcb3719a23cb5f9dce22de6f5184e226909743907ccaecd2e07972782e1f"
)
LEGACY_READY_BATCH_EVENT_HASH = (
    "cce77505e6172b458315f61456b1548c1ebe8b8ad8e74943dd60a932911cf785"
)
LEGACY_BYTES_OBSERVED_EVENT_HASH = (
    "d3fe34f67596ed1e78b465c490ffca87e67ca5d9017cf50bf1f7addd6616ecd1"
)
LEGACY_CHANNEL_EOF_EVENT_HASH = (
    "b2279f2650947674853e630e3493cb82fb7c0367e617eeca7b9ca407da2c06b8"
)
LEGACY_RETRY_OBSERVED_EVENT_HASH = (
    "d41856a31476d8b4a54b8c62591956db9ca05fc9ac9c152ab6912e0f788f0cd1"
)
EXPECTED_UNCHANGED_P0_GREEN_NODE_IDS = (
    "test_d00_legacy_event_and_receipt_serialization_are_byte_identical",
    "test_d00_unbound_legacy_result_event_hashes_remain_byte_identical[ready-batch]",
    "test_d00_unbound_legacy_result_event_hashes_remain_byte_identical[bytes-observed]",
    "test_d00_unbound_legacy_result_event_hashes_remain_byte_identical[channel-eof]",
    "test_d00_unbound_legacy_result_event_hashes_remain_byte_identical[retry-observed]",
)
assert len(EXPECTED_UNCHANGED_P0_GREEN_NODE_IDS) == 5

LEGACY_WORK_COORDINATE_NAMES = (
    "records_admitted",
    "roots_admitted",
    "root_path_components",
    "source_path_components",
    "descriptor_operation_attempts",
    "executable_bytes_observed",
    "git_control_bytes_observed",
    "local_bytes_observed",
    "retained_bytes",
    "git_process_starts",
    "git_protocol_operations",
    "git_stdout_bytes_observed",
    "git_stderr_bytes_observed",
    "git_distinct_objects",
    "git_object_bytes_observed",
    "git_tree_entries_parsed",
    "git_tag_steps",
)

EXPECTED_DEADLINE_SOURCE_NAMES = (
    "REQUESTED_TIMEOUT",
    "OUTER_DEADLINE",
)
EXPECTED_START_ADMISSION_NAMES = (
    "ADMITTED",
    "DENIED_EXPIRED",
)
EXPECTED_DEADLINE_EFFECT_PHASE_NAMES = (
    "PRE_EFFECT",
    "POST_EFFECT",
)
EXPECTED_EINTR_VISIBILITY_NAMES = (
    "INTERNAL_RECOMPUTE",
    "VISIBLE",
)
STRICT_MAIN_EVENTS_PER_EFFECT = 5
STRICT_FINALIZE_EVENTS_PER_ATTEMPT = 2
# Binding, child/start completion, three descriptor acquisitions, two helper
# handoff transitions, timeout latch, finalization begin, and two closed-lane
# transition slots.  PROCESS_START itself is already conservatively charged as
# a five-event MAIN effect even though it uses fewer envelopes.
STRICT_AUXILIARY_EVENT_COUNT = 12


def _required(name: str) -> object:
    value = getattr(process_receipt, name, None)
    assert value is not None, f"Process Receipt V3 deadline contract lacks {name}"
    return value


def _identity(name: str) -> str:
    value = _required(name)
    assert type(value) is str and len(value) == 64
    assert all(character in "0123456789abcdef" for character in value)
    return value


def _clock_contract() -> object:
    contract_type = _required("ProcessClockContract")
    contract = _required("PROCESS_CLOCK_CONTRACT")
    assert type(contract) is contract_type
    return contract


def _clock_domain_occurrence() -> object:
    occurrence_type = _required("ClockDomainOccurrence")
    occurrence = _required("PROCESS_CLOCK_DOMAIN_OCCURRENCE")
    assert type(occurrence) is occurrence_type
    return occurrence


def _select_timeout_contract() -> object:
    contract_type = _required("SelectTimeoutContract")
    contract = _required("PROCESS_SELECT_TIMEOUT_CONTRACT")
    assert type(contract) is contract_type
    assert contract.eintr_visibility is _enum_member(
        "EintrVisibility", "INTERNAL_RECOMPUTE"
    )
    return contract


def _strict_feasibility(subject: ProcessCommandSubject) -> object:
    feasibility_type = _required("StrictDeadlineFeasibility")
    factory = getattr(feasibility_type, "for_subject", None)
    assert callable(factory), (
        "strict mode must preflight worst-case event cardinality before capture"
    )
    return factory(
        subject=subject,
        strict_deadline_contract_identity=_identity(
            "PROCESS_STRICT_DEADLINE_CONTRACT_IDENTITY"
        ),
        maximum_event_count=process_receipt.MAX_PROCESS_EVENT_COUNT,
    )


def _independent_worst_case_event_count(
    *,
    main_effect_count: int,
    finalize_attempt_count: int,
    auxiliary_event_count: int = STRICT_AUXILIARY_EVENT_COUNT,
) -> int:
    return (
        STRICT_MAIN_EVENTS_PER_EFFECT * main_effect_count
        + STRICT_FINALIZE_EVENTS_PER_ATTEMPT * finalize_attempt_count
        + auxiliary_event_count
    )


def _enum_member(enum_name: str, member_name: str) -> object:
    enum_type = _required(enum_name)
    member = getattr(enum_type, member_name, None)
    assert member is not None, f"{enum_name} lacks {member_name}"
    return member


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


def _legacy_work_payload(work: ProcessWorkVector) -> dict[str, int]:
    return {name: getattr(work, name) for name in LEGACY_WORK_COORDINATE_NAMES}


def _legacy_command_subject_payload(
    subject: ProcessCommandSubject,
) -> dict[str, object]:
    return {
        "operation": subject.operation.value,
        "logical_argv": subject.logical_argv,
        "logical_environment": subject.logical_environment,
        "root_subject_hash": subject.root_subject_hash,
        "instrument_subject_hash": subject.instrument_subject_hash,
        "requested_timeout_ns": subject.requested_timeout_ns,
        "status_limit": subject.status_limit,
        "stdout_limit": subject.stdout_limit,
        "stderr_limit": subject.stderr_limit,
        "combined_limit": subject.combined_limit,
        "work_envelope": {
            "main_limit": _legacy_work_payload(subject.work_envelope.main_limit),
            "finalize_limit": _legacy_work_payload(
                subject.work_envelope.finalize_limit
            ),
        },
        "retry_contract": tuple(
            {
                "stage": rule.stage.value,
                "target": rule.target.value,
                "kind": rule.kind.value,
                "max_retries": rule.max_retries,
            }
            for rule in subject.retry_contract.rules
        ),
        "retry_contract_hash": LEGACY_P0_RETRY_CONTRACT_HASH,
        "wait_decoder_identity": subject.wait_decoder_identity,
        "wait_supported_signals": subject.wait_supported_signals,
        "wait_nonblocking_option_mask": subject.wait_nonblocking_option_mask,
    }


def _legacy_invocation_payload(
    invocation: MaterializedInvocation,
) -> dict[str, object]:
    return {
        "command_subject_hash": invocation.command_subject_hash,
        "host_nonce_hex": invocation.host_nonce.hex(),
        "materialized_argv": invocation.materialized_argv,
        "materialized_environment": invocation.materialized_environment,
    }


def _legacy_event_payload(payload: object) -> dict[str, object]:
    if type(payload) is OperationAttempt:
        return {
            "kind": "OPERATION_ATTEMPT",
            "stage": payload.stage.value,
            "target": payload.target.value,
            "outcome": payload.outcome.value,
            "failure_kind": payload.failure_kind.value,
            "mechanism_errno": payload.mechanism_errno,
            "failure_role": payload.failure_role.value,
        }
    if type(payload) is ChildIdentityBound:
        return {
            "kind": "CHILD_IDENTITY_BOUND",
            "child_pid": payload.child_pid,
            "process_group_id": payload.process_group_id,
            "deadline_monotonic_ns": payload.deadline_monotonic_ns,
        }
    if type(payload) is TimeoutObservation:
        return {
            "kind": "TIMEOUT_OBSERVATION",
            "deadline_monotonic_ns": payload.deadline_monotonic_ns,
            "observed_monotonic_ns": payload.observed_monotonic_ns,
            "crossed": payload.crossed,
            "handoff_state": payload.handoff_state.value,
        }
    if type(payload) is ReadyBatch:
        return {
            "kind": "READY_BATCH",
            "channels": tuple(channel.value for channel in payload.channels),
        }
    if type(payload) is BytesObserved:
        return {
            "kind": "BYTES_OBSERVED",
            "channel": payload.channel.value,
            "acquired_bytes_hex": payload.acquired_bytes.hex(),
            "retained_prefix_delta_hex": payload.retained_prefix_delta.hex(),
        }
    if type(payload) is ChannelEof:
        return {
            "kind": "CHANNEL_EOF",
            "channel": payload.channel.value,
        }
    if type(payload) is RetryObserved:
        return {
            "kind": "RETRY_OBSERVED",
            "stage": payload.stage.value,
            "target": payload.target.value,
            "retry_kind": payload.kind.value,
            "ordinal": payload.ordinal,
        }
    raise AssertionError(f"legacy reference lacks {type(payload).__name__}")


def _legacy_failure_occurrence_payload(value: object | None) -> object:
    if value is None:
        return None
    return {
        "event_index": value.event_index,
        "phase": value.phase.value,
        "stage": value.stage.value,
        "target": value.target.value,
        "kind": value.kind.value,
        "mechanism_errno": value.mechanism_errno,
        "role": value.role.value,
        "close_disposition": (
            value.close_disposition.value
            if value.close_disposition is not None
            else None
        ),
        "occurrence_hash": value.occurrence_hash,
    }


def _legacy_derived_payload(state: object) -> dict[str, object]:
    return {
        "acquired_prefix": tuple(value.value for value in state.acquired_prefix),
        "nonblocking_prefix": tuple(value.value for value in state.nonblocking_prefix),
        "registered_prefix": tuple(value.value for value in state.registered_prefix),
        "unregistered_prefix": tuple(
            value.value for value in state.unregistered_prefix
        ),
        "eof_prefix": tuple(value.value for value in state.eof_prefix),
        "status_acquired_hex": state.status_acquired.hex(),
        "stdout_acquired_hex": state.stdout_acquired.hex(),
        "stderr_acquired_hex": state.stderr_acquired.hex(),
        "status_retained_hex": state.status_retained.hex(),
        "stdout_retained_hex": state.stdout_retained.hex(),
        "stderr_retained_hex": state.stderr_retained.hex(),
        "status_bytes_observed": state.status_bytes_observed,
        "stdout_bytes_observed": state.stdout_bytes_observed,
        "stderr_bytes_observed": state.stderr_bytes_observed,
        "process_state": state.process_state.value,
        "child_pid": state.child_pid,
        "process_group_id": state.process_group_id,
        "pre_root_observation": (
            _legacy_event_payload(state.pre_root_observation)
            if state.pre_root_observation is not None
            else None
        ),
        "post_root_observation": (
            _legacy_event_payload(state.post_root_observation)
            if state.post_root_observation is not None
            else None
        ),
        "timeout_observation": (
            _legacy_event_payload(state.timeout_observation)
            if state.timeout_observation is not None
            else None
        ),
        "handoff_state": state.handoff_state.value,
        "exit_state": state.exit_state.value,
        "returncode": state.returncode,
        "termination_signal": state.termination_signal,
        "reap_disposition": state.reap_disposition.value,
        "selector_state": state.selector_state.value,
        "status_state": state.status_state.value,
        "stdout_state": state.stdout_state.value,
        "stderr_state": state.stderr_state.value,
        "status_close_disposition": state.status_close_disposition.value,
        "stdout_close_disposition": state.stdout_close_disposition.value,
        "stderr_close_disposition": state.stderr_close_disposition.value,
        "status_close_attempts": state.status_close_attempts,
        "stdout_close_attempts": state.stdout_close_attempts,
        "stderr_close_attempts": state.stderr_close_attempts,
        "post_disposition": state.post_disposition.value,
        "finalization_state": state.finalization_state.value,
        "main_work": _legacy_work_payload(state.main_work),
        "finalize_work": _legacy_work_payload(state.finalize_work),
        "first_primary": _legacy_failure_occurrence_payload(state.first_primary),
        "finalize_indices": state.finalize_indices,
        "failure_recurrence_signatures": state.failure_recurrence_signatures,
        "failure_occurrences": tuple(
            _legacy_failure_occurrence_payload(value)
            for value in state.failure_occurrences
        ),
        "retry_counts": tuple(
            {
                "stage": value.stage.value,
                "target": value.target.value,
                "kind": value.kind.value,
                "count": value.count,
            }
            for value in state.retry_counts
        ),
        "can_project_success": state.can_project_success,
    }


def _legacy_event_envelope_payload(
    event: ProcessLifecycleEvent,
) -> dict[str, object]:
    return {
        "event_index": event.event_index,
        "previous_event_hash": event.previous_event_hash,
        "phase": event.phase.value,
        "payload": _legacy_event_payload(event.payload),
        "work_delta": _legacy_work_payload(event.work_delta),
        "event_hash": event.event_hash,
    }


def _legacy_receipt_reference_hash(receipt: object) -> str:
    return canonical_digest(
        {
            "schema_version": receipt.schema_version,
            "subject": _legacy_command_subject_payload(receipt.subject),
            "command_subject_hash": receipt.command_subject_hash,
            "invocation": _legacy_invocation_payload(receipt.invocation),
            "invocation_occurrence_id": receipt.invocation.invocation_occurrence_id,
            "retry_contract_hash": LEGACY_P0_RETRY_CONTRACT_HASH,
            "reducer_identity": LEGACY_P0_REDUCER_IDENTITY,
            "replay_identity": LEGACY_P0_REPLAY_IDENTITY,
            "events": [
                _legacy_event_envelope_payload(event) for event in receipt.events
            ],
            "derived_state": _legacy_derived_payload(receipt.derived_state),
            "operational_only": receipt.operational_only,
            "scientific_authority": receipt.scientific_authority,
            "promotion_authority": receipt.promotion_authority,
        },
        domain="orion.host-evidence-process-receipt.v3",
    )


def _subject(*, requested_timeout_ns: int = TIMEOUT_NS) -> ProcessCommandSubject:
    main_limit = _work_limit(40)
    finalize_limit = _work_limit(20)
    kwargs: dict[str, object] = {
        "operation": ProcessOperation.PROTECTED_GIT,
        "logical_argv": ("git", "status", "--porcelain=v2"),
        "logical_environment": (("LC_ALL", "C"), ("PATH", "/usr/bin:/bin")),
        "root_subject_hash": HEX_A,
        "instrument_subject_hash": HEX_B,
        "requested_timeout_ns": requested_timeout_ns,
        "status_limit": 1024,
        "stdout_limit": 32,
        "stderr_limit": 32,
        "combined_limit": 64,
        "work_envelope": ProcessWorkEnvelope(main_limit, finalize_limit),
        "retry_contract": RetryContract.frozen_default(),
    }
    fields = ProcessCommandSubject.__dataclass_fields__
    if "clock_contract_hash" in fields:
        kwargs["clock_contract_hash"] = _clock_contract().clock_contract_hash
    if "deadline_decoder_identity" in fields:
        kwargs["deadline_decoder_identity"] = _identity(
            "PROCESS_DEADLINE_DECODER_IDENTITY"
        )
    return ProcessCommandSubject(**kwargs)


def _legacy_subject() -> ProcessCommandSubject:
    """Freeze the P0 constructor path: no strict deadline coordinates."""

    limit = _work_limit()
    return ProcessCommandSubject(
        operation=ProcessOperation.PROTECTED_GIT,
        logical_argv=("git", "status", "--porcelain=v2"),
        logical_environment=(("LC_ALL", "C"), ("PATH", "/usr/bin:/bin")),
        root_subject_hash=HEX_A,
        instrument_subject_hash=HEX_B,
        requested_timeout_ns=TIMEOUT_NS,
        status_limit=1024,
        stdout_limit=32,
        stderr_limit=32,
        combined_limit=64,
        work_envelope=ProcessWorkEnvelope(limit, limit),
        retry_contract=RetryContract.frozen_default(),
    )


def _invocation(
    subject: ProcessCommandSubject, nonce: bytes = b"d" * 32
) -> MaterializedInvocation:
    _strict_feasibility(subject)
    fields = MaterializedInvocation.__dataclass_fields__
    assert {
        "strict_deadline_contract_identity",
        "clock_domain_occurrence_id",
        "select_timeout_contract_hash",
    } <= set(fields), (
        "materialized invocation must commit its capture-host clock occurrence "
        "and selector timeout contract"
    )
    return MaterializedInvocation(
        command_subject_hash=subject.command_subject_hash,
        host_nonce=nonce,
        materialized_argv=("/usr/bin/python3", "-I", "helper.py", "17"),
        materialized_environment=(("LC_ALL", "C"), ("PATH", "/usr/bin:/bin")),
        strict_deadline_contract_identity=_identity(
            "PROCESS_STRICT_DEADLINE_CONTRACT_IDENTITY"
        ),
        clock_domain_occurrence_id=(
            _clock_domain_occurrence().clock_domain_occurrence_id
        ),
        select_timeout_contract_hash=(
            _select_timeout_contract().select_timeout_contract_hash
        ),
    )


def _legacy_invocation(subject: ProcessCommandSubject) -> MaterializedInvocation:
    return MaterializedInvocation(
        command_subject_hash=subject.command_subject_hash,
        host_nonce=b"d" * 32,
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


def _binding(
    invocation: MaterializedInvocation,
    *,
    started_ns: int = START_NS,
    requested_timeout_ns: int = TIMEOUT_NS,
    outer_deadline: object | None = None,
    clock_domain_occurrence: object | None = None,
    clock_contract: object | None = None,
    deadline_decoder_identity: str | None = None,
) -> object:
    binding_type = _required("DeadlineBinding")
    factory = getattr(binding_type, "from_start_observation", None)
    assert callable(factory), (
        "DeadlineBinding requires pure checked from_start_observation construction"
    )
    return factory(
        invocation_occurrence_id=invocation.invocation_occurrence_id,
        started_monotonic_ns=started_ns,
        requested_timeout_ns=requested_timeout_ns,
        outer_deadline=outer_deadline,
        clock_domain_occurrence=(clock_domain_occurrence or _clock_domain_occurrence()),
        clock_contract=(clock_contract or _clock_contract()),
        deadline_decoder_identity=(
            deadline_decoder_identity or _identity("PROCESS_DEADLINE_DECODER_IDENTITY")
        ),
    )


def _overflow_refusal(
    invocation: MaterializedInvocation,
    *,
    started_ns: int = MAX_NS - TIMEOUT_NS + 1,
    requested_timeout_ns: int = TIMEOUT_NS,
) -> object:
    refusal_type = _required("DeadlineRefusal")
    factory = getattr(refusal_type, "from_checked_add_overflow", None)
    assert callable(factory), (
        "DeadlineRefusal requires checked, typed overflow construction"
    )
    return factory(
        invocation_occurrence_id=invocation.invocation_occurrence_id,
        started_monotonic_ns=started_ns,
        requested_timeout_ns=requested_timeout_ns,
        outer_deadline=None,
        clock_domain_occurrence=_clock_domain_occurrence(),
        clock_contract=_clock_contract(),
        deadline_decoder_identity=_identity("PROCESS_DEADLINE_DECODER_IDENTITY"),
    )


def _child(
    binding: object, invocation: MaterializedInvocation, pid: int = 501
) -> ChildIdentityBound:
    required = {
        "invocation_occurrence_id",
        "deadline_binding_hash",
        "child_occurrence_id",
    }
    fields = ChildIdentityBound.__dataclass_fields__
    assert required <= set(fields), (
        "ChildIdentityBound must derive an exact child occurrence from invocation "
        "and deadline binding"
    )
    return ChildIdentityBound(
        child_pid=pid,
        process_group_id=pid,
        deadline_monotonic_ns=binding.effective_deadline_monotonic_ns,
        invocation_occurrence_id=invocation.invocation_occurrence_id,
        deadline_binding_hash=binding.deadline_binding_hash,
    )


def _outer_deadline(
    consumer_invocation: MaterializedInvocation,
    deadline_ns: int,
    *,
    clock_domain_occurrence: object | None = None,
    producer_invocation_occurrence_id: str = HEX_A,
    parent_deadline_binding_hash: str = HEX_B,
) -> object:
    commitment_type = _required("OuterDeadlineCommitment")
    return commitment_type(
        deadline_monotonic_ns=deadline_ns,
        clock_domain_occurrence_id=(
            clock_domain_occurrence or _clock_domain_occurrence()
        ).clock_domain_occurrence_id,
        consumer_invocation_occurrence_id=(
            consumer_invocation.invocation_occurrence_id
        ),
        producer_invocation_occurrence_id=producer_invocation_occurrence_id,
        parent_deadline_binding_hash=parent_deadline_binding_hash,
    )


def _timeout_observation(
    binding: object,
    child: ChildIdentityBound,
    observed_ns: int,
) -> TimeoutObservation:
    """A non-effect crossing observation, used only before FINALIZE."""

    required = {
        "deadline_binding_hash",
        "child_occurrence_id",
        "clock_domain_occurrence_id",
        "remaining_ns",
    }
    assert required <= set(TimeoutObservation.__dataclass_fields__)
    effective = binding.effective_deadline_monotonic_ns
    return TimeoutObservation(
        deadline_monotonic_ns=effective,
        observed_monotonic_ns=observed_ns,
        crossed=observed_ns >= effective,
        handoff_state=HandoffState.NOT_REACHED,
        deadline_binding_hash=binding.deadline_binding_hash,
        child_occurrence_id=child.child_occurrence_id,
        clock_domain_occurrence_id=binding.clock_domain_occurrence_id,
        remaining_ns=max(0, effective - observed_ns),
    )


def _next_effect_ordinal(events: tuple[ProcessLifecycleEvent, ...]) -> int:
    admission_type = _required("DeadlineAdmission")
    return 1 + sum(type(event.payload) is admission_type for event in events)


def _timeout_float64_bits(remaining_ns: int) -> str:
    encoder = getattr(_select_timeout_contract(), "encode_timeout_float64_bits", None)
    assert callable(encoder), (
        "registered selector contract must deterministically encode remaining_ns"
    )
    bits = encoder(remaining_ns)
    assert type(bits) is str and len(bits) == 16
    return bits


def _selector_timeout_ns() -> int:
    return max(TIMEOUT_NS, 8 * _select_timeout_contract().backend_quantum_ns)


def _admission(
    events: tuple[ProcessLifecycleEvent, ...],
    invocation: MaterializedInvocation,
    binding: object,
    child: ChildIdentityBound,
    stage: ProcessStage,
    target: ProcessTarget,
    observed_ns: int,
    *,
    attempt_ordinal: int | None = None,
    timeout_argument_float64_bits: str | None = None,
) -> object:
    admission_type = _required("DeadlineAdmission")
    factory = getattr(admission_type, "from_observation", None)
    assert callable(factory)
    ordinal = (
        _next_effect_ordinal(events) if attempt_ordinal is None else attempt_ordinal
    )
    remaining_ns = max(0, binding.effective_deadline_monotonic_ns - observed_ns)
    select_bits = timeout_argument_float64_bits
    if stage is ProcessStage.SELECT and select_bits is None:
        select_bits = _timeout_float64_bits(remaining_ns)
    return factory(
        invocation_occurrence_id=invocation.invocation_occurrence_id,
        deadline_binding_hash=binding.deadline_binding_hash,
        child_occurrence_id=child.child_occurrence_id,
        clock_domain_occurrence_id=binding.clock_domain_occurrence_id,
        stage=stage,
        target=target,
        attempt_ordinal=ordinal,
        admission_event_index=len(events),
        admission_previous_event_hash=(events[-1].event_hash if events else None),
        deadline_monotonic_ns=binding.effective_deadline_monotonic_ns,
        observed_monotonic_ns=observed_ns,
        select_timeout_contract=(
            _select_timeout_contract() if stage is ProcessStage.SELECT else None
        ),
        timeout_argument_float64_bits=select_bits,
    )


def _completion(
    events: tuple[ProcessLifecycleEvent, ...],
    binding: object,
    child: ChildIdentityBound,
    admission: object,
    observed_ns: int,
) -> object:
    completion_type = _required("DeadlineCompletion")
    factory = getattr(completion_type, "from_observation", None)
    assert callable(factory)
    return factory(
        effect_occurrence_id=admission.effect_occurrence_id,
        deadline_binding_hash=binding.deadline_binding_hash,
        child_occurrence_id=child.child_occurrence_id,
        clock_domain_occurrence_id=binding.clock_domain_occurrence_id,
        completion_event_index=len(events),
        completion_previous_event_hash=(events[-1].event_hash if events else None),
        deadline_monotonic_ns=binding.effective_deadline_monotonic_ns,
        observed_monotonic_ns=observed_ns,
    )


def _effect_attempt(
    stage: ProcessStage,
    target: ProcessTarget,
    admission: object,
    *,
    retryable_kind: FailureKind | None = None,
    failed_kind: FailureKind | None = None,
    mechanism_errno: int | None = None,
) -> OperationAttempt:
    assert {"effect_occurrence_id", "attempt_ordinal"} <= set(
        OperationAttempt.__dataclass_fields__
    )
    kwargs = {
        "effect_occurrence_id": admission.effect_occurrence_id,
        "attempt_ordinal": admission.attempt_ordinal,
    }
    assert not (retryable_kind is not None and failed_kind is not None)
    if retryable_kind is None and failed_kind is None:
        return OperationAttempt.succeeded(stage, target, **kwargs)
    if failed_kind is not None:
        return OperationAttempt.failed(
            stage,
            target,
            kind=failed_kind,
            mechanism_errno=mechanism_errno,
            role=FailureRole.PRIMARY,
            **kwargs,
        )
    assert retryable_kind is not None
    return OperationAttempt.retryable(
        stage,
        target,
        kind=retryable_kind,
        mechanism_errno=mechanism_errno,
        **kwargs,
    )


def _retry_with_deadline(
    stage: ProcessStage,
    target: ProcessTarget,
    kind: RetryKind,
    ordinal: int,
    effect_occurrence_id: str,
) -> RetryObserved:
    assert "effect_occurrence_id" in RetryObserved.__dataclass_fields__
    return RetryObserved(
        stage,
        target,
        kind,
        ordinal,
        effect_occurrence_id=effect_occurrence_id,
    )


def _ready_batch(admission: object, channels: tuple[Channel, ...]) -> ReadyBatch:
    assert "effect_occurrence_id" in ReadyBatch.__dataclass_fields__
    return ReadyBatch(channels, effect_occurrence_id=admission.effect_occurrence_id)


def _empty_ready(admission: object) -> object:
    result_type = _required("EmptyReadyObserved")
    return result_type(effect_occurrence_id=admission.effect_occurrence_id)


def _bytes_observed(
    admission: object,
    channel: Channel,
    acquired: bytes,
    retained: bytes,
) -> BytesObserved:
    assert "effect_occurrence_id" in BytesObserved.__dataclass_fields__
    return BytesObserved(
        channel,
        acquired,
        retained,
        effect_occurrence_id=admission.effect_occurrence_id,
    )


def _channel_eof(admission: object, channel: Channel) -> ChannelEof:
    assert "effect_occurrence_id" in ChannelEof.__dataclass_fields__
    return ChannelEof(channel, effect_occurrence_id=admission.effect_occurrence_id)


def _append_effect(
    events: tuple[ProcessLifecycleEvent, ...],
    invocation: MaterializedInvocation,
    binding: object,
    child: ChildIdentityBound,
    stage: ProcessStage,
    target: ProcessTarget,
    *,
    admission_ns: int,
    completion_ns: int,
    retryable_kind: FailureKind | None = None,
    failed_kind: FailureKind | None = None,
    mechanism_errno: int | None = None,
    result: str | tuple[Channel, ...] | tuple[Channel, bytes, bytes] | None = None,
    attempt_ordinal: int | None = None,
    timeout_argument_float64_bits: str | None = None,
) -> tuple[tuple[ProcessLifecycleEvent, ...], object, object]:
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        stage,
        target,
        admission_ns,
        attempt_ordinal=attempt_ordinal,
        timeout_argument_float64_bits=timeout_argument_float64_bits,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(
            stage,
            target,
            admission,
            retryable_kind=retryable_kind,
            failed_kind=failed_kind,
            mechanism_errno=mechanism_errno,
        ),
    )
    if result is not None:
        if result == "EMPTY_READY":
            events = _append(events, _empty_ready(admission))
        elif len(result) == 1:
            events = _append(events, _ready_batch(admission, result))
        else:
            channel, acquired, retained = result
            events = _append(
                events,
                _bytes_observed(admission, channel, acquired, retained),
            )
    completion = _completion(events, binding, child, admission, completion_ns)
    events = _append(events, completion)
    return events, admission, completion


def _start_completion(
    events: tuple[ProcessLifecycleEvent, ...],
    invocation: MaterializedInvocation,
    binding: object,
    child: ChildIdentityBound | None,
    observed_ns: int,
) -> object:
    completion_type = _required("ProcessStartCompletion")
    factory = getattr(completion_type, "from_observation", None)
    assert callable(factory), (
        "spawn must have a post-return deadline observation after child binding"
    )
    return factory(
        invocation_occurrence_id=invocation.invocation_occurrence_id,
        deadline_binding_hash=binding.deadline_binding_hash,
        child_occurrence_id=(child.child_occurrence_id if child is not None else None),
        clock_domain_occurrence_id=binding.clock_domain_occurrence_id,
        completion_event_index=len(events),
        completion_previous_event_hash=(events[-1].event_hash if events else None),
        deadline_monotonic_ns=binding.effective_deadline_monotonic_ns,
        observed_monotonic_ns=observed_ns,
    )


def _started(
    subject: ProcessCommandSubject,
    invocation: MaterializedInvocation,
    *,
    outer_deadline: object | None = None,
    completion_ns: int = START_NS,
) -> tuple[object, ChildIdentityBound, tuple[ProcessLifecycleEvent, ...]]:
    binding = _binding(
        invocation,
        requested_timeout_ns=subject.requested_timeout_ns,
        outer_deadline=outer_deadline,
    )
    events = _append((), binding)
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    child = _child(binding, invocation)
    events = _append(events, child)
    events = _append(
        events,
        _start_completion(events, invocation, binding, child, completion_ns),
    )
    # Exercise the occurrence parameter on every strict reduction path.
    reduce_process_events(
        subject,
        events,
        invocation_occurrence_id=invocation.invocation_occurrence_id,
    )
    return binding, child, events


def _forge(value: object, **changes: object) -> object:
    """Bypass frozen-dataclass construction so replay must revalidate payloads."""

    forged = object.__new__(type(value))
    for name in value.__dataclass_fields__:
        object.__setattr__(forged, name, changes.get(name, getattr(value, name)))
    return forged


def _rematerialize_start_completion(value: object, **changes: object) -> object:
    """Build an internally valid completion with selected contextual coordinates."""

    factory = getattr(type(value), "from_observation", None)
    assert callable(factory)
    coordinates = {
        "invocation_occurrence_id": value.invocation_occurrence_id,
        "deadline_binding_hash": value.deadline_binding_hash,
        "child_occurrence_id": value.child_occurrence_id,
        "clock_domain_occurrence_id": value.clock_domain_occurrence_id,
        "completion_event_index": value.completion_event_index,
        "completion_previous_event_hash": value.completion_previous_event_hash,
        "deadline_monotonic_ns": value.deadline_monotonic_ns,
        "observed_monotonic_ns": value.observed_monotonic_ns,
    }
    coordinates.update(changes)
    return factory(**coordinates)


def _reduce_strict(
    subject: ProcessCommandSubject,
    invocation: MaterializedInvocation,
    events: tuple[ProcessLifecycleEvent, ...],
) -> object:
    return reduce_process_events(
        subject,
        events,
        invocation_occurrence_id=invocation.invocation_occurrence_id,
    )


def _status_registered_prefix(
    subject: ProcessCommandSubject,
    invocation: MaterializedInvocation,
) -> tuple[object, ChildIdentityBound, tuple[ProcessLifecycleEvent, ...]]:
    binding, child, events = _started(subject, invocation)
    events = _append(events, DescriptorAcquired(Channel.STATUS))
    events, _admission_value, _completion_value = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.NONBLOCKING_CONFIGURE,
        ProcessTarget.STATUS,
        admission_ns=START_NS + 1,
        completion_ns=START_NS + 1,
    )
    events, _admission_value, _completion_value = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 2,
        completion_ns=START_NS + 2,
    )
    events, _admission_value, _completion_value = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_REGISTER,
        ProcessTarget.STATUS,
        admission_ns=START_NS + 3,
        completion_ns=START_NS + 3,
    )
    _reduce_strict(subject, invocation, events)
    return binding, child, events


def _status_ready_prefix(
    subject: ProcessCommandSubject,
    invocation: MaterializedInvocation,
) -> tuple[object, ChildIdentityBound, tuple[ProcessLifecycleEvent, ...]]:
    binding, child, events = _status_registered_prefix(subject, invocation)
    events, _admission_value, _completion_value = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 4,
        completion_ns=START_NS + 5,
        result=(Channel.STATUS,),
    )
    _reduce_strict(subject, invocation, events)
    return binding, child, events


def test_d00_deadline_contract_is_closed_registered_and_receipted() -> None:
    source = _required("DeadlineSource")
    start_admission = _required("StartAdmissionState")
    phase = _required("DeadlineEffectPhase")
    visibility = _required("EintrVisibility")
    binding = _required("DeadlineBinding")
    refusal_reason = _required("DeadlineRefusalReason")
    refusal = _required("DeadlineRefusal")
    deadline_admission = _required("DeadlineAdmission")
    deadline_completion = _required("DeadlineCompletion")
    start_completion = _required("ProcessStartCompletion")
    select_argument = _required("SelectCallArgument")

    assert tuple(source.__members__) == EXPECTED_DEADLINE_SOURCE_NAMES
    assert tuple(start_admission.__members__) == EXPECTED_START_ADMISSION_NAMES
    assert tuple(phase.__members__) == EXPECTED_DEADLINE_EFFECT_PHASE_NAMES
    assert tuple(visibility.__members__) == EXPECTED_EINTR_VISIBILITY_NAMES
    assert tuple(refusal_reason.__members__) == ("ARITHMETIC_OVERFLOW",)
    assert hasattr(binding, "from_start_observation")
    assert hasattr(refusal, "from_checked_add_overflow")
    assert hasattr(deadline_admission, "from_observation")
    assert hasattr(deadline_completion, "from_observation")

    for name in (
        "PROCESS_CLOCK_DOMAIN_IDENTITY",
        "PROCESS_DEADLINE_DECODER_IDENTITY",
        "PROCESS_STRICT_DEADLINE_CONTRACT_IDENTITY",
        "PROCESS_RECEIPT_LEGACY_REDUCER_IDENTITY",
        "PROCESS_RECEIPT_STRICT_DEADLINE_REDUCER_IDENTITY",
    ):
        _identity(name)

    assert {
        "clock_contract_hash",
        "deadline_decoder_identity",
    } <= set(ProcessCommandSubject.__dataclass_fields__)
    assert {
        "invocation_occurrence_id",
        "started_monotonic_ns",
        "requested_timeout_ns",
        "requested_deadline_monotonic_ns",
        "outer_deadline_monotonic_ns",
        "outer_deadline_commitment_hash",
        "effective_deadline_monotonic_ns",
        "winning_source",
        "start_admission_state",
        "clock_domain_identity",
        "clock_domain_occurrence_id",
        "clock_contract_hash",
        "deadline_decoder_identity",
        "deadline_binding_hash",
    } <= set(binding.__dataclass_fields__)
    assert {
        "phase",
        "invocation_occurrence_id",
        "deadline_binding_hash",
        "child_occurrence_id",
        "clock_domain_occurrence_id",
        "stage",
        "target",
        "attempt_ordinal",
        "admission_event_index",
        "admission_previous_event_hash",
        "deadline_monotonic_ns",
        "observed_monotonic_ns",
        "remaining_ns",
        "crossed",
        "select_call_argument",
        "effect_occurrence_id",
        "deadline_admission_hash",
    } <= set(deadline_admission.__dataclass_fields__)
    assert {
        "phase",
        "effect_occurrence_id",
        "deadline_binding_hash",
        "child_occurrence_id",
        "clock_domain_occurrence_id",
        "completion_event_index",
        "completion_previous_event_hash",
        "deadline_monotonic_ns",
        "observed_monotonic_ns",
        "remaining_ns",
        "crossed",
        "deadline_completion_hash",
    } <= set(deadline_completion.__dataclass_fields__)
    assert {
        "invocation_occurrence_id",
        "deadline_binding_hash",
        "child_occurrence_id",
        "clock_domain_occurrence_id",
        "completion_event_index",
        "completion_previous_event_hash",
        "deadline_monotonic_ns",
        "observed_monotonic_ns",
        "remaining_ns",
        "crossed",
        "process_start_completion_hash",
    } <= set(start_completion.__dataclass_fields__)
    assert {
        "effect_occurrence_id",
        "remaining_ns",
        "timeout_argument_float64_bits",
        "semantic_requested_wait_ns",
        "select_timeout_contract_hash",
        "select_call_argument_hash",
    } <= set(select_argument.__dataclass_fields__)
    for result_type in (
        ReadyBatch,
        BytesObserved,
        ChannelEof,
        _required("EmptyReadyObserved"),
        RetryObserved,
    ):
        assert "effect_occurrence_id" in result_type.__dataclass_fields__
    assert "deadline_censored_effect_occurrences" in (
        process_receipt.ProcessDerivedState.__dataclass_fields__
    )


def test_d00_clock_contract_is_self_validating_and_exactly_host_bound() -> None:
    contract_type = _required("ProcessClockContract")
    assert {
        "name",
        "reader",
        "implementation",
        "monotonic",
        "adjustable",
        "resolution_float64_bits",
        "clock_contract_hash",
    } <= set(contract_type.__dataclass_fields__)
    contract = _clock_contract()
    info = time.get_clock_info("monotonic")
    assert contract.name == "monotonic"
    assert contract.reader == "time.monotonic_ns"
    assert contract.implementation == info.implementation
    assert type(contract.implementation) is str and contract.implementation.strip()
    assert contract.monotonic is info.monotonic is True
    assert contract.adjustable is info.adjustable is False
    assert contract.resolution_float64_bits == struct.pack(">d", info.resolution).hex()
    resolution = struct.unpack(">d", bytes.fromhex(contract.resolution_float64_bits))[0]
    assert math.isfinite(resolution) and resolution > 0.0
    assert type(contract.clock_contract_hash) is str
    assert len(contract.clock_contract_hash) == 64

    with pytest.raises(ValueError, match="hash|contract"):
        replace(contract, clock_contract_hash="f" * 64)
    with pytest.raises(ValueError, match="bool|monotonic|exact"):
        replace(contract, monotonic=1, clock_contract_hash="")
    for invalid_bits in ("0000000000000000", "7ff8000000000000"):
        with pytest.raises(ValueError, match="resolution|finite|positive|float64"):
            replace(
                contract,
                resolution_float64_bits=invalid_bits,
                clock_contract_hash="",
            )


def test_d00_clock_domain_occurrence_is_derived_not_caller_declared() -> None:
    occurrence_type = _required("ClockDomainOccurrence")
    assert {
        "clock_contract_hash",
        "host_clock_epoch_nonce",
        "clock_domain_occurrence_id",
    } <= set(occurrence_type.__dataclass_fields__)
    occurrence = _clock_domain_occurrence()
    assert occurrence.clock_contract_hash == _clock_contract().clock_contract_hash
    assert type(occurrence.host_clock_epoch_nonce) is bytes
    assert len(occurrence.host_clock_epoch_nonce) == 32
    _identity("PROCESS_CLOCK_DOMAIN_IDENTITY")
    assert type(occurrence.clock_domain_occurrence_id) is str
    assert len(occurrence.clock_domain_occurrence_id) == 64

    with pytest.raises(ValueError, match="occurrence|hash|derived|domain"):
        replace(occurrence, clock_domain_occurrence_id=HEX_C)


def test_d00_selector_timeout_contract_is_closed_registered_and_conservative() -> None:
    contract_type = _required("SelectTimeoutContract")
    assert {
        "timeout_encoder_identity",
        "selector_backend_identity",
        "syscall_wrapper_identity",
        "eintr_visibility",
        "backend_quantum_ns",
        "select_timeout_contract_hash",
    } <= set(contract_type.__dataclass_fields__)
    contract = _select_timeout_contract()
    for name in (
        "timeout_encoder_identity",
        "selector_backend_identity",
        "syscall_wrapper_identity",
        "select_timeout_contract_hash",
    ):
        value = getattr(contract, name)
        assert type(value) is str and len(value) == 64
    assert type(contract.backend_quantum_ns) is int
    assert contract.backend_quantum_ns > 0

    with pytest.raises(ValueError, match="registered|selector|backend|wrapper|encoder"):
        replace(
            contract,
            selector_backend_identity=HEX_C,
            select_timeout_contract_hash="",
        )
    with pytest.raises(ValueError, match="registered|EINTR|visibility|wrapper"):
        replace(
            contract,
            eintr_visibility=_enum_member("EintrVisibility", "VISIBLE"),
            select_timeout_contract_hash="",
        )


def test_d00_strict_event_cardinality_is_prospectively_feasible() -> None:
    subject = _subject()
    assert process_receipt.STRICT_MAIN_EVENTS_PER_EFFECT == (
        STRICT_MAIN_EVENTS_PER_EFFECT
    )
    assert process_receipt.STRICT_FINALIZE_EVENTS_PER_ATTEMPT == (
        STRICT_FINALIZE_EVENTS_PER_ATTEMPT
    )
    assert process_receipt.STRICT_AUXILIARY_EVENT_COUNT == (
        STRICT_AUXILIARY_EVENT_COUNT
    )
    feasibility = _strict_feasibility(subject)
    assert {
        "main_effect_count",
        "finalize_attempt_count",
        "auxiliary_event_count",
        "worst_case_main_event_count",
        "worst_case_finalize_event_count",
        "worst_case_total_event_count",
        "maximum_event_count",
    } <= set(type(feasibility).__dataclass_fields__)
    assert feasibility.main_effect_count == (
        subject.work_envelope.main_limit.descriptor_operation_attempts
    )
    assert feasibility.finalize_attempt_count == (
        subject.work_envelope.finalize_limit.descriptor_operation_attempts
    )
    expected = _independent_worst_case_event_count(
        main_effect_count=feasibility.main_effect_count,
        finalize_attempt_count=feasibility.finalize_attempt_count,
        auxiliary_event_count=feasibility.auxiliary_event_count,
    )
    assert feasibility.worst_case_total_event_count == expected
    assert feasibility.worst_case_total_event_count <= feasibility.maximum_event_count
    assert feasibility.maximum_event_count == process_receipt.MAX_PROCESS_EVENT_COUNT


def test_d00_infeasible_strict_subject_is_rejected_before_capture() -> None:
    value = process_receipt.MAX_PROCESS_EVENT_COUNT
    limit = _work_limit(value)
    oversized = replace(
        _legacy_subject(),
        work_envelope=ProcessWorkEnvelope(limit, limit),
        command_subject_hash="",
    )
    with pytest.raises(ValueError, match="event|cap|feasib|cardinality"):
        _strict_feasibility(oversized)


def test_d00_strict_event_feasibility_has_exact_cap_and_cap_plus_one_edges() -> None:
    checker = _required("_checked_strict_event_cardinality")
    assert callable(checker)
    at_cap = checker(
        main_effect_count=100,
        finalize_attempt_count=0,
        auxiliary_event_count=12,
        maximum_event_count=process_receipt.MAX_PROCESS_EVENT_COUNT,
    )
    assert (
        _independent_worst_case_event_count(
            main_effect_count=100,
            finalize_attempt_count=0,
            auxiliary_event_count=12,
        )
        == process_receipt.MAX_PROCESS_EVENT_COUNT
    )
    assert at_cap == process_receipt.MAX_PROCESS_EVENT_COUNT

    with pytest.raises(ValueError, match="event|cap|feasib|cardinality"):
        checker(
            main_effect_count=100,
            finalize_attempt_count=0,
            auxiliary_event_count=13,
            maximum_event_count=process_receipt.MAX_PROCESS_EVENT_COUNT,
        )


def test_d00_legacy_empty_receipt_is_byte_identical_and_verified() -> None:
    subject = _legacy_subject()
    invocation = _legacy_invocation(subject)
    receipt = build_process_receipt(subject, invocation, ())
    verification = verify_process_receipt(receipt)
    subject_payload = _legacy_command_subject_payload(subject)
    invocation_payload = _legacy_invocation_payload(invocation)

    assert process_receipt._command_subject_payload(subject) == subject_payload
    assert subject.command_subject_hash == canonical_digest(
        subject_payload,
        domain="orion.host-evidence-process-command-subject.v3",
    )
    assert process_receipt._invocation_payload(invocation) == invocation_payload
    assert invocation.invocation_occurrence_id == canonical_digest(
        invocation_payload,
        domain="orion.host-evidence-process-occurrence.v3",
    )
    assert subject.retry_contract.retry_contract_hash == (LEGACY_P0_RETRY_CONTRACT_HASH)
    assert receipt.retry_contract_hash == LEGACY_P0_RETRY_CONTRACT_HASH
    assert receipt.reducer_identity == LEGACY_P0_REDUCER_IDENTITY
    assert receipt.replay_identity == LEGACY_P0_REPLAY_IDENTITY
    derived_payload = _legacy_derived_payload(receipt.derived_state)
    assert process_receipt._derived_payload(receipt.derived_state) == derived_payload
    assert receipt.receipt_hash == _legacy_receipt_reference_hash(receipt)

    changed_wait_payload = dict(subject_payload)
    changed_wait_payload["wait_decoder_identity"] = HEX_C
    assert (
        canonical_digest(
            changed_wait_payload,
            domain="orion.host-evidence-process-command-subject.v3",
        )
        != subject.command_subject_hash
    )
    assert (
        _identity("PROCESS_RECEIPT_LEGACY_REDUCER_IDENTITY")
        == LEGACY_P0_REDUCER_IDENTITY
    )
    assert verification.status is ReplayStatus.VERIFIED


def test_d00_legacy_event_and_receipt_serialization_are_byte_identical() -> None:
    subject = _legacy_subject()
    invocation = _legacy_invocation(subject)
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
    receipt = build_process_receipt(subject, invocation, events)
    verification = verify_process_receipt(receipt)

    assert process_receipt._event_payload(events[0].payload) == (
        _legacy_event_payload(events[0].payload)
    )
    assert events[0].event_hash == LEGACY_FAILED_START_EVENT_HASH
    assert process_receipt._derived_payload(receipt.derived_state) == (
        _legacy_derived_payload(receipt.derived_state)
    )
    assert subject.retry_contract.retry_contract_hash == (LEGACY_P0_RETRY_CONTRACT_HASH)
    assert receipt.retry_contract_hash == LEGACY_P0_RETRY_CONTRACT_HASH
    assert receipt.reducer_identity == LEGACY_P0_REDUCER_IDENTITY
    assert receipt.replay_identity == LEGACY_P0_REPLAY_IDENTITY
    assert receipt.receipt_hash == _legacy_receipt_reference_hash(receipt)

    legacy_child = ChildIdentityBound(501, 501, REQUESTED_DEADLINE_NS)
    legacy_timeout = TimeoutObservation(
        deadline_monotonic_ns=REQUESTED_DEADLINE_NS,
        observed_monotonic_ns=REQUESTED_DEADLINE_NS,
        crossed=True,
        handoff_state=HandoffState.NOT_REACHED,
    )
    for legacy_payload in (legacy_child, legacy_timeout):
        assert process_receipt._event_payload(legacy_payload) == (
            _legacy_event_payload(legacy_payload)
        )
    assert verification.status is ReplayStatus.VERIFIED


@pytest.mark.parametrize(
    ("payload", "expected_event_hash"),
    (
        (
            ReadyBatch((Channel.STATUS, Channel.STDOUT)),
            LEGACY_READY_BATCH_EVENT_HASH,
        ),
        (
            BytesObserved(Channel.STDOUT, b"ok", b"ok"),
            LEGACY_BYTES_OBSERVED_EVENT_HASH,
        ),
        (ChannelEof(Channel.STDOUT), LEGACY_CHANNEL_EOF_EVENT_HASH),
        (
            RetryObserved(
                ProcessStage.READ,
                ProcessTarget.STDOUT,
                RetryKind.INTERRUPTED,
                1,
            ),
            LEGACY_RETRY_OBSERVED_EVENT_HASH,
        ),
    ),
    ids=("ready-batch", "bytes-observed", "channel-eof", "retry-observed"),
)
def test_d00_unbound_legacy_result_event_hashes_remain_byte_identical(
    payload: object,
    expected_event_hash: str,
) -> None:
    assert getattr(payload, "effect_occurrence_id", None) is None
    assert process_receipt._event_payload(payload) == _legacy_event_payload(payload)
    event = _append((), payload)[0]
    assert event.event_hash == expected_event_hash


def test_d00_strict_invocation_rejects_an_empty_trace_as_a_downgrade() -> None:
    subject = _subject()
    invocation = _invocation(subject)

    with pytest.raises(
        ValueError,
        match=r"(?i)(?=.*strict)(?=.*(?:binding|trace|dialect))",
    ):
        build_process_receipt(subject, invocation, ())


def test_d00_strict_invocation_rejects_a_legacy_only_trace_as_a_downgrade() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    legacy_only_events = _append(
        (),
        OperationAttempt.failed(
            ProcessStage.PROCESS_START,
            ProcessTarget.PROCESS,
            kind=FailureKind.NOT_FOUND,
            mechanism_errno=errno.ENOENT,
            role=FailureRole.PRIMARY,
        ),
    )

    with pytest.raises(
        ValueError,
        match=r"(?i)(?=.*strict)(?=.*(?:legacy|dialect|binding|trace))",
    ):
        build_process_receipt(subject, invocation, legacy_only_events)


def test_d00_strict_subject_rejects_a_legacy_invocation() -> None:
    subject = _subject()
    strict_invocation = _invocation(subject)
    _binding_value, _child_value, strict_events = _started(
        subject,
        strict_invocation,
    )
    legacy_invocation = _legacy_invocation(subject)

    with pytest.raises(
        ValueError,
        match=r"(?i)(?=.*strict)(?=.*(?:legacy|dialect|contract))",
    ):
        build_process_receipt(subject, legacy_invocation, strict_events)


def test_d00_legacy_lane_rejects_an_effect_bound_payload() -> None:
    subject = _legacy_subject()
    invocation = _legacy_invocation(subject)
    legacy_failed_start = OperationAttempt.failed(
        ProcessStage.PROCESS_START,
        ProcessTarget.PROCESS,
        kind=FailureKind.NOT_FOUND,
        mechanism_errno=errno.ENOENT,
        role=FailureRole.PRIMARY,
    )
    effect_bound_payload = _forge(
        legacy_failed_start,
        effect_occurrence_id=HEX_C,
        attempt_ordinal=1,
    )
    events = _append((), effect_bound_payload)

    with pytest.raises(
        ValueError,
        match=r"(?i)(?=.*legacy)(?=.*(?:effect|bound|dialect))",
    ):
        reduce_process_events(
            subject,
            events,
            invocation_occurrence_id=invocation.invocation_occurrence_id,
        )


def test_d00_strict_trace_rejects_an_unbound_legacy_result() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_registered_prefix(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        START_NS + 4,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(ProcessStage.SELECT, ProcessTarget.SELECTOR, admission),
    )
    unbound_result = ReadyBatch((Channel.STATUS,))
    events = _append(events, unbound_result)
    events = _append(
        events,
        _completion(events, binding, child, admission, START_NS + 5),
    )

    with pytest.raises(
        ValueError,
        match=r"(?i)(?=.*strict)(?=.*(?:unbound|effect|dialect))",
    ):
        _reduce_strict(subject, invocation, events)


def test_d00_verifier_rejects_strict_events_under_legacy_reducer_identity() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    _binding_value, _child_value, events = _started(subject, invocation)
    strict_receipt = build_process_receipt(subject, invocation, events)
    relabelled = _forge(
        strict_receipt,
        reducer_identity=_identity("PROCESS_RECEIPT_LEGACY_REDUCER_IDENTITY"),
    )

    verification = verify_process_receipt(relabelled)
    assert verification.status is ReplayStatus.REDUCER_IDENTITY_MISMATCH
    assert verification.valid is False


def test_d00_verifier_rejects_legacy_events_under_strict_reducer_identity() -> None:
    subject = _legacy_subject()
    invocation = _legacy_invocation(subject)
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
    legacy_receipt = build_process_receipt(subject, invocation, events)
    relabelled = _forge(
        legacy_receipt,
        reducer_identity=_identity("PROCESS_RECEIPT_STRICT_DEADLINE_REDUCER_IDENTITY"),
    )

    verification = verify_process_receipt(relabelled)
    assert verification.status is ReplayStatus.REDUCER_IDENTITY_MISMATCH
    assert verification.valid is False


def test_d00_strict_events_cannot_be_relinked_into_the_legacy_lane() -> None:
    strict_subject = _subject()
    strict_invocation = _invocation(strict_subject)
    strict_binding = _binding(strict_invocation)
    legacy_subject = _legacy_subject()
    legacy_invocation = _legacy_invocation(legacy_subject)
    relinked = _append((), strict_binding)

    with pytest.raises(
        ValueError,
        match=r"(?i)(?=.*strict)(?=.*legacy)",
    ):
        reduce_process_events(
            legacy_subject,
            relinked,
            invocation_occurrence_id=legacy_invocation.invocation_occurrence_id,
        )


def test_d00_stripping_the_strict_discriminator_fails_closed() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    changes = {
        "strict_deadline_contract_identity": None,
        "invocation_occurrence_id": "",
    }
    with pytest.raises(ValueError, match="strict|contract|coordinates|complete"):
        replace(invocation, **changes)


def test_d00_checked_add_overflow_is_a_replayable_pre_spawn_refusal() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    refusal = _overflow_refusal(invocation)
    assert refusal.reason is _enum_member(
        "DeadlineRefusalReason", "ARITHMETIC_OVERFLOW"
    )
    events = _append((), refusal)
    state = _reduce_strict(subject, invocation, events)
    receipt = build_process_receipt(subject, invocation, events)
    verification = verify_process_receipt(receipt)

    assert state.process_state is process_receipt.ProcessState.NOT_STARTED
    assert state.child_pid is None and state.process_group_id is None
    assert state.main_work.git_process_starts == 0
    assert state.deadline_refusal == refusal
    assert state.first_primary is not None
    assert state.first_primary.stage is ProcessStage.PROCESS_START
    assert state.first_primary.kind is FailureKind.RESOURCE_EXHAUSTED
    assert state.can_project_success is False
    assert receipt.reducer_identity == _identity(
        "PROCESS_RECEIPT_STRICT_DEADLINE_REDUCER_IDENTITY"
    )
    assert verification.status is ReplayStatus.VERIFIED
    assert verification.replayed_state == state


def test_d00_deadline_binding_factory_rejects_first_overflowing_value() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    with pytest.raises(ValueError, match="overflow|representable|checked|deadline"):
        _binding(
            invocation,
            started_ns=MAX_NS - TIMEOUT_NS + 1,
            requested_timeout_ns=TIMEOUT_NS,
        )


def test_d00_exact_maximum_deadline_boundary_is_admitted() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding = _binding(
        invocation,
        started_ns=MAX_NS - TIMEOUT_NS,
        requested_timeout_ns=TIMEOUT_NS,
    )
    assert binding.requested_deadline_monotonic_ns == MAX_NS
    assert binding.effective_deadline_monotonic_ns == MAX_NS
    assert binding.start_admission_state is _enum_member(
        "StartAdmissionState", "ADMITTED"
    )


def test_d00_deadline_refusal_factory_rejects_representable_operands() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    with pytest.raises(ValueError, match="overflow|representable|refusal|deadline"):
        _overflow_refusal(
            invocation,
            started_ns=START_NS,
            requested_timeout_ns=TIMEOUT_NS,
        )


def test_d00_raw_outer_deadline_integer_is_not_a_binding_api() -> None:
    binding_type = _required("DeadlineBinding")
    signature = inspect.signature(binding_type.from_start_observation)
    assert "outer_deadline" in signature.parameters
    assert "outer_deadline_monotonic_ns" not in signature.parameters

    subject = _subject()
    invocation = _invocation(subject)
    with pytest.raises(ValueError, match="outer|typed|commitment|deadline"):
        _binding(invocation, outer_deadline=START_NS + 30)


@pytest.mark.parametrize("outer_deadline_ns", (START_NS - 1, START_NS))
def test_d01_expired_typed_outer_deadline_forbids_spawn(
    outer_deadline_ns: int,
) -> None:
    subject = _subject()
    invocation = _invocation(subject)
    outer = _outer_deadline(invocation, outer_deadline_ns)
    binding = _binding(invocation, outer_deadline=outer)

    assert binding.effective_deadline_monotonic_ns == outer_deadline_ns
    assert binding.winning_source is _enum_member("DeadlineSource", "OUTER_DEADLINE")
    assert binding.start_admission_state is _enum_member(
        "StartAdmissionState", "DENIED_EXPIRED"
    )
    events = _append((), binding)
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    with pytest.raises(ValueError, match="deadline|expired|start|admission"):
        _reduce_strict(subject, invocation, events)


@pytest.mark.parametrize("outer_deadline_ns", (START_NS - 1, START_NS))
def test_d01_expired_binding_alone_records_not_started_failure_knowledge(
    outer_deadline_ns: int,
) -> None:
    subject = _subject()
    invocation = _invocation(subject)
    outer = _outer_deadline(invocation, outer_deadline_ns)
    binding = _binding(invocation, outer_deadline=outer)
    state = _reduce_strict(subject, invocation, _append((), binding))

    assert state.deadline_binding == binding
    assert state.process_state is process_receipt.ProcessState.NOT_STARTED
    assert state.child_pid is None and state.process_group_id is None
    assert state.main_work.git_process_starts == 0
    assert state.first_primary is not None
    assert state.first_primary.stage is ProcessStage.PROCESS_START
    assert state.first_primary.kind is FailureKind.TIMEOUT
    assert state.can_project_success is False


def test_d01_outer_equal_requested_deadline_tie_chooses_requested() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding = _binding(
        invocation,
        outer_deadline=_outer_deadline(invocation, REQUESTED_DEADLINE_NS),
    )
    assert binding.requested_deadline_monotonic_ns == REQUESTED_DEADLINE_NS
    assert binding.effective_deadline_monotonic_ns == REQUESTED_DEADLINE_NS
    assert binding.winning_source is _enum_member("DeadlineSource", "REQUESTED_TIMEOUT")
    assert binding.start_admission_state is _enum_member(
        "StartAdmissionState", "ADMITTED"
    )


def test_d01_binding_timeout_must_match_the_command_subject() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    internally_valid = _binding(invocation, requested_timeout_ns=TIMEOUT_NS - 1)
    with pytest.raises(ValueError, match="subject|requested|timeout|binding"):
        _reduce_strict(subject, invocation, _append((), internally_valid))


def test_d01_same_clock_algorithm_but_foreign_occurrence_is_rejected() -> None:
    occurrence_type = _required("ClockDomainOccurrence")
    foreign = occurrence_type(
        clock_contract_hash=_clock_contract().clock_contract_hash,
        host_clock_epoch_nonce=b"x" * 32,
    )
    subject = _subject()
    invocation = _invocation(subject)
    outer = _outer_deadline(
        invocation,
        START_NS + 30,
        clock_domain_occurrence=foreign,
    )
    with pytest.raises(ValueError, match="clock|domain|occurrence|invocation"):
        _binding(
            invocation,
            outer_deadline=outer,
            clock_domain_occurrence=foreign,
        )


def test_d01_outer_commitment_cannot_move_to_another_consumer_invocation() -> None:
    subject = _subject()
    first = _invocation(subject, nonce=b"1" * 32)
    second = _invocation(subject, nonce=b"2" * 32)
    outer = _outer_deadline(first, START_NS + 30)
    with pytest.raises(ValueError, match="outer|consumer|invocation|commitment"):
        _binding(second, outer_deadline=outer)


def test_d01_outer_coordinate_and_commitment_hash_must_agree() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding = _binding(
        invocation,
        outer_deadline=_outer_deadline(invocation, START_NS + 30),
    )
    with pytest.raises(ValueError, match="outer|commitment|deadline|hash"):
        replace(
            binding,
            outer_deadline_monotonic_ns=START_NS + 31,
            deadline_binding_hash="",
        )


@pytest.mark.parametrize("delta", (-1, 1), ids=("shorter", "longer"))
def test_d02_d03_requested_deadline_cannot_be_forged(delta: int) -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding = _binding(invocation)
    with pytest.raises(ValueError, match="requested|timeout|deadline|arithmetic"):
        replace(
            binding,
            requested_deadline_monotonic_ns=(REQUESTED_DEADLINE_NS + delta),
            deadline_binding_hash="",
        )


def test_d04_spawn_cannot_omit_the_prospective_deadline_binding() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    events = _append(
        (),
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    with pytest.raises(ValueError, match="deadline|binding|start|admission"):
        _reduce_strict(subject, invocation, events)


def test_d04_generic_timeout_event_cannot_replace_a_deadline_binding() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    events = _append(
        (),
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(events, ChildIdentityBound(501, 501, REQUESTED_DEADLINE_NS))
    events = _append(
        events,
        TimeoutObservation(
            deadline_monotonic_ns=REQUESTED_DEADLINE_NS,
            observed_monotonic_ns=REQUESTED_DEADLINE_NS,
            crossed=True,
            handoff_state=HandoffState.NOT_REACHED,
        ),
    )
    with pytest.raises(ValueError, match="deadline|binding|occurrence|timeout|strict"):
        _reduce_strict(subject, invocation, events)


def test_d04_spawn_requires_post_return_completion_after_child_binding() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding = _binding(invocation)
    events = _append((), binding)
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    events = _append(events, _child(binding, invocation))
    with pytest.raises(ValueError, match="start|spawn|completion|pending"):
        _reduce_strict(subject, invocation, events)


def test_d04_failed_spawn_also_requires_post_return_completion() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding = _binding(invocation)
    events = _append((), binding)
    events = _append(
        events,
        OperationAttempt.failed(
            ProcessStage.PROCESS_START,
            ProcessTarget.PROCESS,
            kind=FailureKind.IO,
            mechanism_errno=errno.EIO,
            role=FailureRole.PRIMARY,
        ),
    )

    with pytest.raises(ValueError, match="start|spawn|completion|pending|post"):
        _reduce_strict(subject, invocation, events)


def test_d04_failed_spawn_completion_at_deadline_latches_without_a_child() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding = _binding(invocation)
    events = _append((), binding)
    events = _append(
        events,
        OperationAttempt.failed(
            ProcessStage.PROCESS_START,
            ProcessTarget.PROCESS,
            kind=FailureKind.IO,
            mechanism_errno=errno.EIO,
            role=FailureRole.PRIMARY,
        ),
    )
    completion = _start_completion(
        events,
        invocation,
        binding,
        None,
        REQUESTED_DEADLINE_NS,
    )
    events = _append(events, completion)
    state = _reduce_strict(subject, invocation, events)

    assert state.process_state is process_receipt.ProcessState.NOT_STARTED
    assert state.child_pid is None and state.process_group_id is None
    assert state.main_work.git_process_starts == 0
    assert state.first_primary is not None
    assert state.first_primary.kind is FailureKind.IO
    assert any(
        occurrence.kind is FailureKind.TIMEOUT
        for occurrence in state.failure_occurrences
    )
    assert state.can_project_success is False


def test_d04_start_completion_observation_cannot_regress_before_start() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding = _binding(invocation)
    events = _append((), binding)
    events = _append(
        events,
        OperationAttempt.failed(
            ProcessStage.PROCESS_START,
            ProcessTarget.PROCESS,
            kind=FailureKind.IO,
            mechanism_errno=errno.EIO,
            role=FailureRole.PRIMARY,
        ),
    )
    regressed = _start_completion(
        events,
        invocation,
        binding,
        None,
        START_NS - 1,
    )
    candidate = _append(events, regressed)

    with pytest.raises(
        ValueError, match="start|completion|monotonic|regress|chronology"
    ):
        _reduce_strict(subject, invocation, candidate)


@pytest.mark.parametrize(
    "coordinate",
    ("completion_event_index", "completion_previous_event_hash"),
)
def test_d04_start_completion_chain_coordinates_are_rederived(
    coordinate: str,
) -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    prefix = events[:-1]
    original = events[-1].payload
    changes = {
        "completion_event_index": len(prefix) - 1,
        "completion_previous_event_hash": prefix[-2].event_hash,
    }
    moved = _rematerialize_start_completion(
        original,
        **{coordinate: changes[coordinate]},
    )
    candidate = _append(prefix, moved)

    with pytest.raises(ValueError, match="start|completion|event|index|previous|chain"):
        _reduce_strict(subject, invocation, candidate)


@pytest.mark.parametrize(
    "coordinate",
    (
        "invocation_occurrence_id",
        "deadline_binding_hash",
        "clock_domain_occurrence_id",
    ),
)
def test_d04_start_completion_provenance_is_rederived(coordinate: str) -> None:
    subject = _subject()
    invocation = _invocation(subject)
    _binding_value, _child_value, events = _started(subject, invocation)
    prefix = events[:-1]
    original = events[-1].payload
    moved = _rematerialize_start_completion(original, **{coordinate: HEX_C})
    candidate = _append(prefix, moved)

    with pytest.raises(
        ValueError,
        match="start|completion|invocation|binding|clock|occurrence|provenance",
    ):
        _reduce_strict(subject, invocation, candidate)


def test_d04_successful_spawn_completion_cannot_omit_the_child() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding = _binding(invocation)
    events = _append((), binding)
    events = _append(
        events,
        OperationAttempt.succeeded(
            ProcessStage.PROCESS_START,
            ProcessTarget.PROCESS,
        ),
    )
    completion = _start_completion(events, invocation, binding, None, START_NS)
    candidate = _append(events, completion)
    with pytest.raises(ValueError, match="start|success|child|completion"):
        _reduce_strict(subject, invocation, candidate)


def test_d04_failed_spawn_cannot_forge_a_child_before_completion() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding = _binding(invocation)
    events = _append((), binding)
    events = _append(
        events,
        OperationAttempt.failed(
            ProcessStage.PROCESS_START,
            ProcessTarget.PROCESS,
            kind=FailureKind.IO,
            mechanism_errno=errno.EIO,
            role=FailureRole.PRIMARY,
        ),
    )
    child = _child(binding, invocation)
    events = _append(events, child)
    completion = _start_completion(events, invocation, binding, child, START_NS)
    candidate = _append(events, completion)
    with pytest.raises(ValueError, match="start|failed|child|completion"):
        _reduce_strict(subject, invocation, candidate)


def test_d04_spawn_completion_at_deadline_retains_child_and_latches_timeout() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(
        subject,
        invocation,
        completion_ns=REQUESTED_DEADLINE_NS,
    )
    state = _reduce_strict(subject, invocation, events)

    assert state.child_pid == child.child_pid
    assert state.process_group_id == child.process_group_id
    assert state.main_work.git_process_starts == 1
    assert state.first_primary is not None
    assert state.first_primary.kind is FailureKind.TIMEOUT
    assert state.can_project_success is False

    late_admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        REQUESTED_DEADLINE_NS - 1,
    )
    with pytest.raises(ValueError, match="timeout|deadline|latched|main"):
        _reduce_strict(subject, invocation, _append(events, late_admission))


def test_d04_late_spawn_still_allows_independent_finalize_wait_reserve() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    _binding_value, child, events = _started(
        subject,
        invocation,
        completion_ns=REQUESTED_DEADLINE_NS,
    )
    events = _append(events, FinalizationBegin(), phase=EventPhase.FINALIZE)
    events = _append(
        events,
        WaitObservation(
            WaitDisposition.INTERRUPTED,
            requested_child_pid=child.child_pid,
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
    state = _reduce_strict(subject, invocation, events)
    assert state.finalization_state is FinalizationState.IN_PROGRESS
    assert state.retry_counts[0].count == 1


def test_d05_selector_create_requires_an_admission_event() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    ghost_admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        START_NS + 1,
    )
    events = _append(
        events,
        _effect_attempt(
            ProcessStage.SELECTOR_CREATE,
            ProcessTarget.SELECTOR,
            ghost_admission,
        ),
    )
    completion = _completion(
        events,
        binding,
        child,
        ghost_admission,
        START_NS + 2,
    )
    events = _append(events, completion)
    with pytest.raises(ValueError, match="deadline|admission|effect|predecessor"):
        _reduce_strict(subject, invocation, events)


def test_d05_read_requires_an_admission_event() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_ready_prefix(subject, invocation)
    ghost_admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.READ,
        ProcessTarget.STATUS,
        START_NS + 6,
    )
    events = _append(
        events,
        _effect_attempt(
            ProcessStage.READ,
            ProcessTarget.STATUS,
            ghost_admission,
        ),
    )
    events = _append(
        events,
        _bytes_observed(ghost_admission, Channel.STATUS, b"x", b"x"),
    )
    completion = _completion(
        events,
        binding,
        child,
        ghost_admission,
        START_NS + 7,
    )
    events = _append(events, completion)
    with pytest.raises(ValueError, match="deadline|admission|effect|predecessor"):
        _reduce_strict(subject, invocation, events)


def test_d05_admission_must_be_the_immediate_attempt_predecessor() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        START_NS + 1,
    )
    events = _append(events, admission)
    events = _append(events, DescriptorAcquired(Channel.STATUS))
    events = _append(
        events,
        _effect_attempt(
            ProcessStage.SELECTOR_CREATE,
            ProcessTarget.SELECTOR,
            admission,
        ),
    )
    events = _append(
        events,
        _completion(events, binding, child, admission, START_NS + 2),
    )
    with pytest.raises(ValueError, match="immediate|admission|predecessor|effect"):
        _reduce_strict(subject, invocation, events)


@pytest.mark.parametrize("outcome", ("ready", "empty", "failed"))
def test_d05_select_outcome_cannot_omit_completion(outcome: str) -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_registered_prefix(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        START_NS + 4,
    )
    events = _append(events, admission)
    if outcome in {"ready", "empty"}:
        attempt = _effect_attempt(
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            admission,
        )
    else:
        attempt = _effect_attempt(
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            admission,
            failed_kind=FailureKind.IO,
            mechanism_errno=errno.EIO,
        )
    events = _append(events, attempt)
    if outcome == "ready":
        events = _append(events, _ready_batch(admission, (Channel.STATUS,)))
    if outcome == "empty":
        events = _append(events, _empty_ready(admission))
    with pytest.raises(ValueError, match="completion|pending|post|effect"):
        _reduce_strict(subject, invocation, events)


@pytest.mark.parametrize("outcome", ("succeeded", "retryable", "failed"))
def test_d05_read_outcome_cannot_omit_completion(outcome: str) -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_ready_prefix(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.READ,
        ProcessTarget.STATUS,
        START_NS + 6,
    )
    events = _append(events, admission)
    if outcome == "succeeded":
        attempt = _effect_attempt(
            ProcessStage.READ,
            ProcessTarget.STATUS,
            admission,
        )
        events = _append(events, attempt)
        events = _append(
            events,
            _bytes_observed(admission, Channel.STATUS, b"x", b"x"),
        )
    elif outcome == "retryable":
        attempt = _effect_attempt(
            ProcessStage.READ,
            ProcessTarget.STATUS,
            admission,
            retryable_kind=FailureKind.READINESS_RACE,
            mechanism_errno=errno.EAGAIN,
        )
        events = _append(events, attempt)
    else:
        attempt = _effect_attempt(
            ProcessStage.READ,
            ProcessTarget.STATUS,
            admission,
            failed_kind=FailureKind.IO,
            mechanism_errno=errno.EIO,
        )
        events = _append(events, attempt)
    with pytest.raises(ValueError, match="completion|pending|post|effect"):
        _reduce_strict(subject, invocation, events)


def test_d05_successful_select_requires_one_intrinsic_result_before_post() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    events, _create, _create_completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 1,
        completion_ns=START_NS + 1,
    )
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        START_NS + 2,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(ProcessStage.SELECT, ProcessTarget.SELECTOR, admission),
    )
    completion = _completion(events, binding, child, admission, START_NS + 3)
    with pytest.raises(ValueError, match="select|result|ready|empty|completion"):
        _reduce_strict(subject, invocation, _append(events, completion))


def test_d05_successful_read_requires_one_intrinsic_result_before_post() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_ready_prefix(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.READ,
        ProcessTarget.STATUS,
        START_NS + 6,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(ProcessStage.READ, ProcessTarget.STATUS, admission),
    )
    completion = _completion(events, binding, child, admission, START_NS + 7)
    with pytest.raises(ValueError, match="read|result|bytes|EOF|completion"):
        _reduce_strict(subject, invocation, _append(events, completion))


def test_d05_select_cannot_return_ready_and_empty_for_one_effect() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_registered_prefix(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        START_NS + 4,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(ProcessStage.SELECT, ProcessTarget.SELECTOR, admission),
    )
    events = _append(events, _ready_batch(admission, (Channel.STATUS,)))
    events = _append(events, _empty_ready(admission))
    completion = _completion(events, binding, child, admission, START_NS + 5)
    with pytest.raises(ValueError, match="exactly one|result|ready|empty"):
        _reduce_strict(subject, invocation, _append(events, completion))


def test_d05_read_cannot_return_bytes_and_eof_for_one_effect() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_ready_prefix(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.READ,
        ProcessTarget.STATUS,
        START_NS + 6,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(ProcessStage.READ, ProcessTarget.STATUS, admission),
    )
    events = _append(
        events,
        _bytes_observed(admission, Channel.STATUS, b"x", b"x"),
    )
    events = _append(events, _channel_eof(admission, Channel.STATUS))
    completion = _completion(events, binding, child, admission, START_NS + 7)
    with pytest.raises(ValueError, match="exactly one|result|bytes|EOF"):
        _reduce_strict(subject, invocation, _append(events, completion))


def test_d05_unrelated_event_cannot_split_attempt_and_completion() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        START_NS + 1,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(
            ProcessStage.SELECTOR_CREATE,
            ProcessTarget.SELECTOR,
            admission,
        ),
    )
    events = _append(events, DescriptorAcquired(Channel.STATUS))
    completion = _completion(events, binding, child, admission, START_NS + 2)
    events = _append(events, completion)
    with pytest.raises(ValueError, match="completion|result|contiguous|effect"):
        _reduce_strict(subject, invocation, events)


def test_d05_one_admission_cannot_authorize_two_equal_timestamp_effects() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    events, admission, _completion_value = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 1,
        completion_ns=START_NS + 1,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(
            ProcessStage.SELECTOR_CREATE,
            ProcessTarget.SELECTOR,
            admission,
        ),
    )
    events = _append(
        events,
        _completion(events, binding, child, admission, START_NS + 1),
    )
    with pytest.raises(ValueError, match="occurrence|event|reuse|admission|ordinal"):
        _reduce_strict(subject, invocation, events)


def test_d05_stage_target_cannot_change_under_an_effect_id() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        START_NS + 1,
    )
    events = _append(events, admission)
    forged = _forge(
        _effect_attempt(
            ProcessStage.SELECTOR_CREATE,
            ProcessTarget.SELECTOR,
            admission,
        ),
        stage=ProcessStage.SELECT,
    )
    events = _append(events, forged)
    events = _append(
        events,
        _completion(events, binding, child, admission, START_NS + 2),
    )
    with pytest.raises(
        ValueError,
        match=r"(?i)(?=.*stage)(?=.*(?:effect|admission))",
    ):
        _reduce_strict(subject, invocation, events)


def test_d05_target_only_cannot_change_under_a_read_effect_id() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_ready_prefix(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.READ,
        ProcessTarget.STATUS,
        START_NS + 6,
    )
    events = _append(events, admission)
    forged = _forge(
        _effect_attempt(ProcessStage.READ, ProcessTarget.STATUS, admission),
        target=ProcessTarget.STDOUT,
    )
    events = _append(events, forged)
    events = _append(
        events,
        _bytes_observed(admission, Channel.STATUS, b"x", b"x"),
    )
    events = _append(
        events,
        _completion(events, binding, child, admission, START_NS + 7),
    )
    with pytest.raises(
        ValueError,
        match=r"(?i)(?=.*target)(?=.*(?:effect|admission|occurrence))",
    ):
        _reduce_strict(subject, invocation, events)


def test_d05_completion_cannot_move_from_one_effect_to_the_next() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    events, first, _first_completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 1,
        completion_ns=START_NS + 1,
    )
    second = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        START_NS + 2,
    )
    events = _append(events, second)
    events = _append(
        events,
        _effect_attempt(ProcessStage.SELECT, ProcessTarget.SELECTOR, second),
    )
    events = _append(events, _empty_ready(second))
    valid_second_completion = _completion(
        events,
        binding,
        child,
        second,
        START_NS + 3,
    )
    moved = replace(
        valid_second_completion,
        effect_occurrence_id=first.effect_occurrence_id,
        deadline_completion_hash="",
    )
    events = _append(events, moved)
    with pytest.raises(ValueError, match="completion|effect|occurrence|event"):
        _reduce_strict(subject, invocation, events)


def test_d05_result_payload_cannot_move_between_effects() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_registered_prefix(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        START_NS + 4,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(ProcessStage.SELECT, ProcessTarget.SELECTOR, admission),
    )
    moved = _forge(
        _ready_batch(admission, (Channel.STATUS,)),
        effect_occurrence_id=HEX_C,
    )
    events = _append(events, moved)
    completion = _completion(events, binding, child, admission, START_NS + 5)
    with pytest.raises(ValueError, match="result|ready|effect|occurrence"):
        _reduce_strict(subject, invocation, _append(events, completion))


@pytest.mark.parametrize("result_kind", ("bytes", "eof"))
def test_d05_read_result_cannot_move_between_effects(result_kind: str) -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_ready_prefix(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.READ,
        ProcessTarget.STATUS,
        START_NS + 6,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(ProcessStage.READ, ProcessTarget.STATUS, admission),
    )
    result = (
        _bytes_observed(admission, Channel.STATUS, b"x", b"x")
        if result_kind == "bytes"
        else _channel_eof(admission, Channel.STATUS)
    )
    moved = _forge(result, effect_occurrence_id=HEX_C)
    events = _append(events, moved)
    completion = _completion(events, binding, child, admission, START_NS + 7)
    with pytest.raises(ValueError, match="result|bytes|EOF|effect|occurrence"):
        _reduce_strict(subject, invocation, _append(events, completion))


def test_d05_later_global_ordinal_cannot_survive_removed_earlier_effect() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        START_NS + 1,
        attempt_ordinal=2,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(
            ProcessStage.SELECTOR_CREATE,
            ProcessTarget.SELECTOR,
            admission,
        ),
    )
    completion = _completion(events, binding, child, admission, START_NS + 1)
    with pytest.raises(ValueError, match="ordinal|global|consecutive|effect"):
        _reduce_strict(subject, invocation, _append(events, completion))


def test_d05_distinct_effects_may_have_equal_monotonic_timestamps() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    events, first, _first_completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 1,
        completion_ns=START_NS + 1,
    )
    events, second, _second_completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 1,
        completion_ns=START_NS + 1,
        result="EMPTY_READY",
    )
    events = _append(
        events,
        _retry_with_deadline(
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            RetryKind.EMPTY_READY,
            1,
            second.effect_occurrence_id,
        ),
    )
    state = _reduce_strict(subject, invocation, events)
    assert first.effect_occurrence_id != second.effect_occurrence_id
    assert state.retry_counts[0].count == 1


def test_d05_retry_decision_does_not_authorize_the_next_effect() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    events, _create, _create_completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 1,
        completion_ns=START_NS + 1,
    )
    events, select_admission, _select_completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 2,
        completion_ns=START_NS + 3,
        result="EMPTY_READY",
    )
    events = _append(
        events,
        _retry_with_deadline(
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            RetryKind.EMPTY_READY,
            1,
            select_admission.effect_occurrence_id,
        ),
    )
    events = _append(
        events,
        OperationAttempt.succeeded(
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            effect_occurrence_id=select_admission.effect_occurrence_id,
            attempt_ordinal=select_admission.attempt_ordinal,
        ),
    )
    events = _append(events, _empty_ready(select_admission))
    events = _append(
        events,
        _completion(events, binding, child, select_admission, START_NS + 4),
    )
    with pytest.raises(ValueError, match="fresh|admission|effect|retry"):
        _reduce_strict(subject, invocation, events)


def test_d05_internal_cpython_selector_empty_retry_uses_a_fresh_effect() -> None:
    timeout_ns = _selector_timeout_ns()
    quantum_ns = _select_timeout_contract().backend_quantum_ns
    subject = _subject(requested_timeout_ns=timeout_ns)
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    events, _create, _create_completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 1,
        completion_ns=START_NS + 1,
    )
    events, first_select, _first_completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 2 * quantum_ns,
        completion_ns=START_NS + 3 * quantum_ns,
        result="EMPTY_READY",
    )
    events = _append(
        events,
        _retry_with_deadline(
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            RetryKind.EMPTY_READY,
            1,
            first_select.effect_occurrence_id,
        ),
    )
    events, second_select, _second_completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 4 * quantum_ns,
        completion_ns=START_NS + 5 * quantum_ns,
        result="EMPTY_READY",
    )
    events = _append(
        events,
        _retry_with_deadline(
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            RetryKind.EMPTY_READY,
            2,
            second_select.effect_occurrence_id,
        ),
    )
    state = _reduce_strict(subject, invocation, events)
    assert first_select.effect_occurrence_id != second_select.effect_occurrence_id
    assert first_select.remaining_ns == timeout_ns - 2 * quantum_ns
    assert second_select.remaining_ns == timeout_ns - 4 * quantum_ns
    assert state.retry_counts[0].count == 2


def test_d05_internal_retry_wrapper_rejects_visible_select_eintr() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    events, _create, _create_completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 1,
        completion_ns=START_NS + 1,
    )
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        START_NS + 2,
    )
    attempt = _effect_attempt(
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        admission,
        retryable_kind=FailureKind.INTERRUPTED,
        mechanism_errno=errno.EINTR,
    )
    candidate = _append(events, admission)
    candidate = _append(candidate, attempt)
    completion = _completion(
        candidate,
        binding,
        child,
        admission,
        START_NS + 3,
    )
    candidate = _append(candidate, completion)
    candidate = _append(
        candidate,
        _retry_with_deadline(
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            RetryKind.INTERRUPTED,
            1,
            admission.effect_occurrence_id,
        ),
    )
    with pytest.raises(
        ValueError,
        match="internal|EINTR|visible|wrapper|selector|contract",
    ):
        _reduce_strict(subject, invocation, candidate)


def test_d05_retry_observation_must_bind_the_completed_effect() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    events, _create, _create_completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 1,
        completion_ns=START_NS + 1,
    )
    events, admission, _completion_value = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 2,
        completion_ns=START_NS + 3,
        result="EMPTY_READY",
    )
    retry = _retry_with_deadline(
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        RetryKind.EMPTY_READY,
        1,
        admission.effect_occurrence_id,
    )
    forged = _forge(retry, effect_occurrence_id=HEX_C)
    with pytest.raises(ValueError, match="retry|effect|occurrence"):
        _reduce_strict(subject, invocation, _append(events, forged))


def test_d06_child_and_matching_start_completion_forgery_are_rederived() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding = _binding(invocation)
    events = _append((), binding)
    events = _append(
        events,
        OperationAttempt.succeeded(ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
    )
    real_child = _child(binding, invocation)
    forged_child = _forge(real_child, child_occurrence_id=HEX_C)
    forged_events = _append(events, forged_child)
    forged_events = _append(
        forged_events,
        _start_completion(
            forged_events,
            invocation,
            binding,
            forged_child,
            START_NS,
        ),
    )

    with pytest.raises(ValueError, match="child|occurrence|derived|binding"):
        _reduce_strict(subject, invocation, forged_events)


def test_d06_timeout_cannot_move_between_child_occurrences() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    timeout = _timeout_observation(
        binding,
        child,
        binding.effective_deadline_monotonic_ns,
    )
    moved = _forge(timeout, child_occurrence_id=HEX_C)
    with pytest.raises(ValueError, match="child|occurrence|timeout|binding"):
        _reduce_strict(subject, invocation, _append(events, moved))


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("remaining_ns", 2),
        ("crossed", True),
    ),
)
def test_d07_admission_crossing_and_remaining_are_exact(
    field: str,
    value: object,
) -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        REQUESTED_DEADLINE_NS - 1,
    )
    with pytest.raises(ValueError, match="remaining|cross|deadline|observation"):
        replace(admission, **{field: value, "deadline_admission_hash": ""})


def test_d07_deadline_equality_is_not_an_admission() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    with pytest.raises(ValueError, match="cross|deadline|admission|expired"):
        _admission(
            events,
            invocation,
            binding,
            child,
            ProcessStage.SELECTOR_CREATE,
            ProcessTarget.SELECTOR,
            REQUESTED_DEADLINE_NS,
        )


def test_d07_completion_equality_is_crossed_and_exact() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        REQUESTED_DEADLINE_NS - 1,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(
            ProcessStage.SELECTOR_CREATE,
            ProcessTarget.SELECTOR,
            admission,
        ),
    )
    completion = _completion(
        events,
        binding,
        child,
        admission,
        REQUESTED_DEADLINE_NS,
    )
    assert admission.crossed is False and admission.remaining_ns == 1
    assert completion.crossed is True and completion.remaining_ns == 0
    with pytest.raises(ValueError, match="remaining|cross|deadline|completion"):
        replace(
            completion,
            crossed=False,
            deadline_completion_hash="",
        )


def test_d08_select_argument_is_exactly_encoded_from_pre_remaining() -> None:
    timeout_ns = _selector_timeout_ns()
    quantum_ns = _select_timeout_contract().backend_quantum_ns
    elapsed_ns = 2 * quantum_ns
    subject = _subject(requested_timeout_ns=timeout_ns)
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        START_NS + elapsed_ns,
    )
    argument = admission.select_call_argument
    assert argument is not None
    assert argument.effect_occurrence_id == admission.effect_occurrence_id
    assert argument.remaining_ns == timeout_ns - elapsed_ns
    assert argument.timeout_argument_float64_bits == _timeout_float64_bits(
        timeout_ns - elapsed_ns
    )
    assert 0 <= argument.semantic_requested_wait_ns <= argument.remaining_ns
    assert (
        argument.select_timeout_contract_hash
        == _select_timeout_contract().select_timeout_contract_hash
    )


@pytest.mark.parametrize(
    "bad_kind",
    ("absent", "nan", "infinity", "negative", "one_ulp", "original_timeout"),
)
def test_d08_select_argument_forgery_fails_closed(bad_kind: str) -> None:
    timeout_ns = _selector_timeout_ns()
    quantum_ns = _select_timeout_contract().backend_quantum_ns
    elapsed_ns = 2 * quantum_ns
    subject = _subject(requested_timeout_ns=timeout_ns)
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    remaining = timeout_ns - elapsed_ns
    valid_bits = _timeout_float64_bits(remaining)
    valid_float = struct.unpack(">d", bytes.fromhex(valid_bits))[0]
    bad_bits = {
        "nan": struct.pack(">d", math.nan).hex(),
        "infinity": struct.pack(">d", math.inf).hex(),
        "negative": struct.pack(">d", -valid_float).hex(),
        "one_ulp": struct.pack(">d", math.nextafter(valid_float, math.inf)).hex(),
        "original_timeout": _timeout_float64_bits(timeout_ns),
    }.get(bad_kind)

    if bad_kind == "absent":
        admission = _admission(
            events,
            invocation,
            binding,
            child,
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            START_NS + elapsed_ns,
        )
        with pytest.raises(ValueError, match="select|argument|timeout|required"):
            replace(
                admission,
                select_call_argument=None,
                deadline_admission_hash="",
            )
    else:
        assert bad_bits is not None
        with pytest.raises(
            ValueError,
            match="select|timeout|encoder|float64|remaining|finite|negative",
        ):
            _admission(
                events,
                invocation,
                binding,
                child,
                ProcessStage.SELECT,
                ProcessTarget.SELECTOR,
                START_NS + elapsed_ns,
                timeout_argument_float64_bits=bad_bits,
            )


def test_d08_selector_semantic_wait_cannot_exceed_remaining() -> None:
    timeout_ns = _selector_timeout_ns()
    quantum_ns = _select_timeout_contract().backend_quantum_ns
    subject = _subject(requested_timeout_ns=timeout_ns)
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        binding.effective_deadline_monotonic_ns - quantum_ns,
    )
    argument = admission.select_call_argument
    assert argument is not None
    with pytest.raises(ValueError, match="semantic|wait|remaining|conservative"):
        replace(
            argument,
            semantic_requested_wait_ns=argument.remaining_ns + 1,
            select_call_argument_hash="",
        )


def test_d08_eintr_retry_cannot_reset_the_original_timeout() -> None:
    timeout_ns = _selector_timeout_ns()
    quantum_ns = _select_timeout_contract().backend_quantum_ns
    subject = _subject(requested_timeout_ns=timeout_ns)
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    original_timeout_bits = _timeout_float64_bits(timeout_ns)
    with pytest.raises(ValueError, match="select|timeout|encoder|remaining"):
        _admission(
            events,
            invocation,
            binding,
            child,
            ProcessStage.SELECT,
            ProcessTarget.SELECTOR,
            START_NS + 2 * quantum_ns,
            timeout_argument_float64_bits=original_timeout_bits,
        )


def test_d09_retryable_read_crossing_is_charged_but_cannot_retry() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_ready_prefix(subject, invocation)
    events, admission, completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.READ,
        ProcessTarget.STATUS,
        admission_ns=REQUESTED_DEADLINE_NS - 1,
        completion_ns=REQUESTED_DEADLINE_NS,
        retryable_kind=FailureKind.READINESS_RACE,
        mechanism_errno=errno.EAGAIN,
    )
    state = _reduce_strict(subject, invocation, events)
    assert completion.crossed is True
    assert state.first_primary is not None
    assert state.first_primary.kind is FailureKind.TIMEOUT
    assert state.main_work.descriptor_operation_attempts > 0

    retry = _retry_with_deadline(
        ProcessStage.READ,
        ProcessTarget.STATUS,
        RetryKind.WOULD_BLOCK,
        1,
        admission.effect_occurrence_id,
    )
    candidate = _append(events, retry)
    with pytest.raises(ValueError, match="deadline|cross|retry|latched"):
        _reduce_strict(subject, invocation, candidate)


def test_d09_failed_read_crossing_makes_timeout_govern_continuation() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_ready_prefix(subject, invocation)
    events, _admission_value, completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.READ,
        ProcessTarget.STATUS,
        admission_ns=REQUESTED_DEADLINE_NS - 1,
        completion_ns=REQUESTED_DEADLINE_NS,
        failed_kind=FailureKind.IO,
        mechanism_errno=errno.EIO,
    )
    state = _reduce_strict(subject, invocation, events)
    assert completion.crossed is True
    assert state.first_primary is not None
    assert state.first_primary.kind is FailureKind.IO
    assert any(
        occurrence.kind is FailureKind.TIMEOUT
        for occurrence in state.failure_occurrences
    )
    assert state.can_project_success is False

    later = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        REQUESTED_DEADLINE_NS - 1,
    )
    with pytest.raises(ValueError, match="timeout|deadline|latched|main"):
        _reduce_strict(subject, invocation, _append(events, later))


def test_d10_completion_before_its_admission_is_rejected() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        START_NS + 20,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(
            ProcessStage.SELECTOR_CREATE,
            ProcessTarget.SELECTOR,
            admission,
        ),
    )
    with pytest.raises(ValueError, match="clock|regress|monotonic|completion"):
        _completion(events, binding, child, admission, START_NS + 19)


def test_d10_clock_regression_is_rejected_across_effect_checks() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    events, _first, _first_completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        admission_ns=START_NS + 20,
        completion_ns=START_NS + 20,
    )
    regressed = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        START_NS + 19,
    )
    with pytest.raises(ValueError, match="clock|regress|monotonic|observation"):
        _reduce_strict(subject, invocation, _append(events, regressed))


def test_d10_clock_domain_occurrence_cannot_change_inside_one_binding() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        START_NS + 1,
    )
    forged = _forge(admission, clock_domain_occurrence_id=HEX_C)
    with pytest.raises(ValueError, match="clock|domain|occurrence|binding"):
        _reduce_strict(subject, invocation, _append(events, forged))


def test_d11_reducer_build_and_verify_never_call_the_host_clock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    subject = _subject()
    invocation = _invocation(subject)
    _binding_value, _child_value, events = _started(subject, invocation)

    def forbidden_clock(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("pure deadline replay called a host clock")

    monkeypatch.setattr(time, "monotonic_ns", forbidden_clock)
    monkeypatch.setattr(time, "get_clock_info", forbidden_clock)
    state = _reduce_strict(subject, invocation, events)
    receipt = build_process_receipt(subject, invocation, events)
    verification = verify_process_receipt(receipt)

    assert receipt.derived_state == state
    assert verification.status is ReplayStatus.VERIFIED
    assert verification.replayed_state == state


@pytest.mark.parametrize(
    ("outer_deadline_ns", "source_name", "crossed_ns"),
    (
        (None, "REQUESTED_TIMEOUT", REQUESTED_DEADLINE_NS),
        (START_NS + 30, "OUTER_DEADLINE", START_NS + 30),
    ),
    ids=("requested_timeout", "outer_deadline"),
)
def test_d12_timeout_cause_is_derived_from_the_winning_minimum(
    outer_deadline_ns: int | None,
    source_name: str,
    crossed_ns: int,
) -> None:
    subject = _subject()
    invocation = _invocation(subject)
    outer = (
        None
        if outer_deadline_ns is None
        else _outer_deadline(invocation, outer_deadline_ns)
    )
    binding, child, events = _started(
        subject,
        invocation,
        outer_deadline=outer,
    )
    state = _reduce_strict(
        subject,
        invocation,
        _append(events, _timeout_observation(binding, child, crossed_ns)),
    )
    source = _enum_member("DeadlineSource", source_name)
    assert state.deadline_binding.winning_source is source
    assert state.timeout_observation is not None
    assert state.first_primary is not None
    assert state.first_primary.kind is FailureKind.TIMEOUT
    assert source_name in state.first_primary.causal_discriminator


@pytest.mark.parametrize("forgery", ("effective", "source", "commitment"))
def test_d12_outer_minimum_proof_cannot_be_forged(forgery: str) -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding = _binding(
        invocation,
        outer_deadline=_outer_deadline(invocation, START_NS + 30),
    )
    changes: dict[str, object] = {"deadline_binding_hash": ""}
    if forgery == "effective":
        changes["effective_deadline_monotonic_ns"] = REQUESTED_DEADLINE_NS
    elif forgery == "source":
        changes["winning_source"] = _enum_member(
            "DeadlineSource",
            "REQUESTED_TIMEOUT",
        )
    else:
        changes["outer_deadline_commitment_hash"] = HEX_C
    with pytest.raises(
        ValueError,
        match="outer|minimum|source|effective|deadline|commitment",
    ):
        replace(binding, **changes)


@pytest.mark.parametrize(
    "identity_name",
    (
        "clock_domain_occurrence",
        "clock_contract",
        "deadline_decoder_identity",
    ),
)
def test_d13_unregistered_clock_or_decoder_identity_fails_closed(
    identity_name: str,
) -> None:
    subject = _subject()
    invocation = _invocation(subject)
    if identity_name == "clock_contract":
        registered = _clock_contract()
        value = replace(
            registered,
            implementation=f"{registered.implementation}:unregistered",
            clock_contract_hash="",
        )
    elif identity_name == "clock_domain_occurrence":
        occurrence_type = _required("ClockDomainOccurrence")
        value = occurrence_type(
            clock_contract_hash=_clock_contract().clock_contract_hash,
            host_clock_epoch_nonce=b"f" * 32,
        )
    else:
        value = "f" * 64
    with pytest.raises(
        ValueError, match="clock|decoder|registered|identity|occurrence"
    ):
        _binding(invocation, **{identity_name: value})


@pytest.mark.parametrize(
    "subject_field",
    ("clock_contract_hash", "deadline_decoder_identity"),
)
def test_d13_strict_identity_forgery_through_the_subject_fails_closed(
    subject_field: str,
) -> None:
    subject = _subject()
    assert subject_field in ProcessCommandSubject.__dataclass_fields__
    with pytest.raises(ValueError, match="subject|clock|decoder|registered|identity"):
        replace(
            subject,
            **{subject_field: HEX_C, "command_subject_hash": ""},
        )


@pytest.mark.parametrize(
    "invocation_field",
    (
        "strict_deadline_contract_identity",
        "clock_domain_occurrence_id",
        "select_timeout_contract_hash",
    ),
)
def test_d13_strict_identity_forgery_through_invocation_fails_closed(
    invocation_field: str,
) -> None:
    subject = _subject()
    invocation = _invocation(subject)
    with pytest.raises(
        ValueError,
        match="strict|clock|selector|registered|contract|occurrence",
    ):
        replace(
            invocation,
            **{invocation_field: HEX_C, "invocation_occurrence_id": ""},
        )


def test_d14_select_post_crossing_charges_attempt_and_latches_timeout() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_registered_prefix(subject, invocation)
    before = _reduce_strict(subject, invocation, events)
    events, admission, completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        admission_ns=REQUESTED_DEADLINE_NS - 1,
        completion_ns=REQUESTED_DEADLINE_NS,
        result=(Channel.STATUS,),
    )
    state = _reduce_strict(subject, invocation, events)
    assert completion.crossed is True
    assert (
        state.main_work.descriptor_operation_attempts
        == before.main_work.descriptor_operation_attempts + 1
    )
    assert state.first_primary is not None
    assert state.first_primary.kind is FailureKind.TIMEOUT
    assert state.can_project_success is False
    assert admission.effect_occurrence_id in (
        state.deadline_censored_effect_occurrences
    )

    later = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.READ,
        ProcessTarget.STATUS,
        REQUESTED_DEADLINE_NS - 1,
    )
    with pytest.raises(ValueError, match="timeout|latched|deadline|main"):
        _reduce_strict(subject, invocation, _append(events, later))


def test_d14_read_bytes_returned_at_crossing_remain_charged() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_ready_prefix(subject, invocation)
    before = _reduce_strict(subject, invocation, events)
    events, admission, completion = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.READ,
        ProcessTarget.STATUS,
        admission_ns=REQUESTED_DEADLINE_NS - 1,
        completion_ns=REQUESTED_DEADLINE_NS,
        result=(Channel.STATUS, b"x", b"x"),
    )
    state = _reduce_strict(subject, invocation, events)

    assert completion.crossed is True
    assert state.status_acquired == before.status_acquired + b"x"
    assert state.status_retained == before.status_retained + b"x"
    assert state.main_work.git_control_bytes_observed == (
        before.main_work.git_control_bytes_observed + 1
    )
    assert state.main_work.retained_bytes == before.main_work.retained_bytes + 1
    assert state.first_primary is not None
    assert state.first_primary.kind is FailureKind.TIMEOUT
    assert admission.effect_occurrence_id in (
        state.deadline_censored_effect_occurrences
    )


def test_d14_read_eof_at_crossing_does_not_authorize_canonical_eof() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_ready_prefix(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.READ,
        ProcessTarget.STATUS,
        REQUESTED_DEADLINE_NS - 1,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(ProcessStage.READ, ProcessTarget.STATUS, admission),
    )
    events = _append(events, _channel_eof(admission, Channel.STATUS))
    completion = _completion(
        events,
        binding,
        child,
        admission,
        REQUESTED_DEADLINE_NS,
    )
    events = _append(events, completion)
    state = _reduce_strict(subject, invocation, events)

    assert completion.crossed is True
    assert Channel.STATUS not in state.eof_prefix
    assert state.first_primary is not None
    assert state.first_primary.kind is FailureKind.TIMEOUT
    assert admission.effect_occurrence_id in (
        state.deadline_censored_effect_occurrences
    )


def test_d14_result_cannot_be_added_after_crossed_completion() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_ready_prefix(subject, invocation)
    admission = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.READ,
        ProcessTarget.STATUS,
        REQUESTED_DEADLINE_NS - 1,
    )
    events = _append(events, admission)
    events = _append(
        events,
        _effect_attempt(
            ProcessStage.READ,
            ProcessTarget.STATUS,
            admission,
            retryable_kind=FailureKind.READINESS_RACE,
            mechanism_errno=errno.EAGAIN,
        ),
    )
    completion = _completion(
        events,
        binding,
        child,
        admission,
        REQUESTED_DEADLINE_NS,
    )
    events = _append(events, completion)
    late_bytes = _bytes_observed(admission, Channel.STATUS, b"x", b"x")
    with pytest.raises(ValueError, match="completion|result|timeout|effect"):
        _reduce_strict(subject, invocation, _append(events, late_bytes))


def test_d14_timeout_latch_is_irreversible_even_with_later_false_admission() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _started(subject, invocation)
    events = _append(
        events,
        _timeout_observation(binding, child, REQUESTED_DEADLINE_NS),
    )
    false_later = _admission(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECTOR_CREATE,
        ProcessTarget.SELECTOR,
        REQUESTED_DEADLINE_NS - 1,
    )
    with pytest.raises(ValueError, match="timeout|latched|irreversible|deadline"):
        _reduce_strict(subject, invocation, _append(events, false_later))


def test_d14_finalize_wait_reserve_survives_effect_completion_crossing() -> None:
    subject = _subject()
    invocation = _invocation(subject)
    binding, child, events = _status_registered_prefix(subject, invocation)
    events, _admission_value, _completion_value = _append_effect(
        events,
        invocation,
        binding,
        child,
        ProcessStage.SELECT,
        ProcessTarget.SELECTOR,
        admission_ns=REQUESTED_DEADLINE_NS - 1,
        completion_ns=REQUESTED_DEADLINE_NS,
        result="EMPTY_READY",
    )
    events = _append(events, FinalizationBegin(), phase=EventPhase.FINALIZE)
    events = _append(
        events,
        WaitObservation(
            WaitDisposition.INTERRUPTED,
            requested_child_pid=child.child_pid,
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
    state = _reduce_strict(subject, invocation, events)
    assert state.finalization_state is FinalizationState.IN_PROGRESS
    assert state.first_primary is not None
    assert state.first_primary.kind is FailureKind.TIMEOUT
