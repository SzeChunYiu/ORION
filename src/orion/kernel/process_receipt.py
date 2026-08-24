"""Immutable, replayable process-lifecycle receipts.

This module is deliberately independent of :mod:`orion.kernel.evidence`.  It
defines the closed V3 receipt algebra used to bind a logical command, a
host-specific invocation occurrence, a hash-chained lifecycle, and its
deterministic reduction.  Import mints one opaque runtime clock-occurrence
nonce; beyond that one-time entropy boundary it performs no process, selector,
clock-read, or filesystem operation and confers no execution or evaluation
authority.
"""

from __future__ import annotations

import errno
import json
import math
import os
import selectors
import signal
import struct
import sys
import time
from dataclasses import dataclass, field, fields, is_dataclass, replace
from enum import Enum
from typing import TypeAlias

from orion.kernel.transition import canonical_digest


PROCESS_RECEIPT_V3_SCHEMA_VERSION = "orion.host-evidence-process-receipt.v3"
PROCESS_RECEIPT_V2_SCHEMA_VERSION = "orion.host-evidence-process-receipt.v2"
PROCESS_HOST_NONCE_BYTES = 32
MAX_PROCESS_ARGV_ENTRIES = 256
MAX_PROCESS_ENVIRONMENT_ENTRIES = 256
MAX_PROCESS_TEXT_BYTES = 4096
MAX_PROCESS_EVENT_COUNT = 512
MAX_PROCESS_ID = (1 << 31) - 1
MAX_PROCESS_SIGNAL = 255
MAX_PROCESS_MONOTONIC_NS = (1 << 63) - 1
MAX_PROCESS_OUTPUT_LIMIT = 16 * 1024 * 1024
MAX_PROCESS_EVENT_BYTES = 1024 * 1024
MAX_PROCESS_WORK_COORDINATE = (1 << 63) - 1
STRICT_MAIN_EVENTS_PER_EFFECT = 5
STRICT_FINALIZE_EVENTS_PER_ATTEMPT = 2
STRICT_AUXILIARY_EVENT_COUNT = 12
PROCESS_HELPER_STATUS_PROTOCOL_VERSION = "orion.git-helper-status.v1"
PROCESS_HELPER_STATUS_FRAME_LIMIT = 512
PROCESS_HELPER_STATUS_RECEIPT_LIMIT = 2 * PROCESS_HELPER_STATUS_FRAME_LIMIT
PROCESS_HELPER_STATUS_ACQUISITION_LIMIT = PROCESS_HELPER_STATUS_RECEIPT_LIMIT + 1
PROCESS_HELPER_PRE_EXEC_FRAME = (
    b'{"errno":null,"kind":null,"stage":"HELPER_PRE_EXEC",'
    b'"version":"orion.git-helper-status.v1"}\n'
)
PROCESS_WAIT_STATUS_RAW_MASK = 0xFFFF
PROCESS_WAIT_SUPPORTED_SIGNALS = tuple(
    sorted(int(value) for value in signal.valid_signals())
)
PROCESS_WAIT_NONBLOCKING_OPTION_MASK = int(os.WNOHANG)
PROCESS_WAIT_DECODER_IDENTITY = canonical_digest(
    {
        "algorithm": "python-os-wait-status-capture.v1",
        "raw_wait_status_mask": PROCESS_WAIT_STATUS_RAW_MASK,
        "supported_signals": PROCESS_WAIT_SUPPORTED_SIGNALS,
        "nonblocking_option_mask": PROCESS_WAIT_NONBLOCKING_OPTION_MASK,
        "os_name": os.name,
        "platform": sys.platform,
        "python_implementation": sys.implementation.name,
        "python_version": tuple(sys.version_info[:3]),
    },
    domain="orion.host-evidence-process-wait-decoder.v1",
)
_PROCESS_WAIT_DECODER_REGISTRY = frozenset(
    {
        (
            PROCESS_WAIT_DECODER_IDENTITY,
            PROCESS_WAIT_SUPPORTED_SIGNALS,
            PROCESS_WAIT_NONBLOCKING_OPTION_MASK,
        )
    }
)
_COMMAND_SUBJECT_DOMAIN = "orion.host-evidence-process-command-subject.v3"
_INVOCATION_OCCURRENCE_DOMAIN = "orion.host-evidence-process-occurrence.v3"
_RETRY_CONTRACT_DOMAIN = "orion.host-evidence-process-retry-contract.v1"
_CLOCK_CONTRACT_DOMAIN = "orion.host-evidence-process-clock-contract.v1"
_CLOCK_DOMAIN_OCCURRENCE_DOMAIN = (
    "orion.host-evidence-process-clock-domain-occurrence.v1"
)
_DEADLINE_BINDING_DOMAIN = "orion.host-evidence-process-deadline-binding.v1"
_OUTER_DEADLINE_COMMITMENT_DOMAIN = (
    "orion.host-evidence-process-outer-deadline-commitment.v1"
)
_DEADLINE_REFUSAL_DOMAIN = "orion.host-evidence-process-deadline-refusal.v1"
_DEADLINE_ADMISSION_DOMAIN = "orion.host-evidence-process-deadline-admission.v1"
_DEADLINE_COMPLETION_DOMAIN = "orion.host-evidence-process-deadline-completion.v1"
_PROCESS_START_COMPLETION_DOMAIN = "orion.host-evidence-process-start-completion.v1"
_EFFECT_OCCURRENCE_DOMAIN = "orion.host-evidence-process-effect-occurrence.v1"
_SELECT_TIMEOUT_CONTRACT_DOMAIN = (
    "orion.host-evidence-process-select-timeout-contract.v1"
)
_SELECT_CALL_ARGUMENT_DOMAIN = "orion.host-evidence-process-select-call-argument.v1"
_EVENT_DOMAIN = "orion.host-evidence-process-lifecycle-event.v3"
_RECURRENCE_DOMAIN = "orion.host-evidence-process-failure-recurrence.v3"
PROCESS_RECEIPT_REDUCER_IDENTITY = canonical_digest(
    (
        PROCESS_RECEIPT_V3_SCHEMA_VERSION,
        "closed-event-algebra.v1",
        "componentwise-work-reduction.v1",
        "first-primary-nonmasking.v1",
        "posix-close-2024.v1",
        "rederived-work-accounting.v2",
        "git-helper-status-v1.v1",
        "causal-finalize-lane.v1",
        "invocation-bound-failure-occurrence.v1",
        "prefix-causal-recurrence.v3",
        "outcome-independent-predecessors.v1",
        "committed-retry-exhaustion.v1",
        "finalize-wait-retry.v1",
        "typed-terminal-handoff-predecessors.v1",
        "typed-failed-process-exit.v1",
        "capture-bound-wait-status.v1",
        "pure-wait-status-reduction.v1",
    ),
    domain="orion.host-evidence-process-reducer-identity.v1",
)
PROCESS_RECEIPT_REPLAY_IDENTITY = canonical_digest(
    (
        PROCESS_RECEIPT_V3_SCHEMA_VERSION,
        PROCESS_RECEIPT_REDUCER_IDENTITY,
        "hash-chain-replay.v1",
        "exact-derived-state.v1",
        "capture-decoder-free-replay.v1",
    ),
    domain="orion.host-evidence-process-replay-identity.v1",
)
PROCESS_RECEIPT_LEGACY_REDUCER_IDENTITY = PROCESS_RECEIPT_REDUCER_IDENTITY
PROCESS_RECEIPT_LEGACY_REPLAY_IDENTITY = PROCESS_RECEIPT_REPLAY_IDENTITY


PROCESS_CLOCK_DOMAIN_IDENTITY = canonical_digest(
    (
        "python-time-monotonic-ns.v1",
        "opaque-host-epoch.v1",
        "exact-uint63-nanoseconds.v1",
    ),
    domain="orion.host-evidence-process-clock-domain-identity.v1",
)
PROCESS_DEADLINE_DECODER_IDENTITY = canonical_digest(
    (
        PROCESS_CLOCK_DOMAIN_IDENTITY,
        "checked-start-plus-timeout.v1",
        "minimum-with-requested-tie.v1",
        "remaining-max-zero.v1",
        "equality-inclusive-crossing.v1",
    ),
    domain="orion.host-evidence-process-deadline-decoder-identity.v1",
)


class ProcessOperation(Enum):
    PROTECTED_GIT = "PROTECTED_GIT"


class Channel(Enum):
    STATUS = "status"
    STDOUT = "stdout"
    STDERR = "stderr"


class ProcessStage(Enum):
    PROCESS_START = "PROCESS_START"
    SELECTOR_CREATE = "SELECTOR_CREATE"
    NONBLOCKING_CONFIGURE = "NONBLOCKING_CONFIGURE"
    SELECTOR_REGISTER = "SELECTOR_REGISTER"
    SELECT = "SELECT"
    READ = "READ"
    SELECTOR_UNREGISTER = "SELECTOR_UNREGISTER"
    WAIT = "WAIT"
    TIMEOUT = "TIMEOUT"
    TERMINATE = "TERMINATE"
    CLOSE = "CLOSE"
    POST = "POST"


class ProcessTarget(Enum):
    PROCESS = "process"
    PROCESS_GROUP = "process_group"
    SELECTOR = "selector"
    STATUS = "status"
    STDOUT = "stdout"
    STDERR = "stderr"
    ROOT = "root"


class EventPhase(Enum):
    MAIN = "MAIN"
    FINALIZE = "FINALIZE"


class DeadlineSource(Enum):
    REQUESTED_TIMEOUT = "REQUESTED_TIMEOUT"
    OUTER_DEADLINE = "OUTER_DEADLINE"


class StartAdmissionState(Enum):
    ADMITTED = "ADMITTED"
    DENIED_EXPIRED = "DENIED_EXPIRED"


class DeadlineEffectPhase(Enum):
    PRE_EFFECT = "PRE_EFFECT"
    POST_EFFECT = "POST_EFFECT"


class EintrVisibility(Enum):
    INTERNAL_RECOMPUTE = "INTERNAL_RECOMPUTE"
    VISIBLE = "VISIBLE"


class DeadlineRefusalReason(Enum):
    ARITHMETIC_OVERFLOW = "ARITHMETIC_OVERFLOW"


class OperationOutcome(Enum):
    SUCCEEDED = "SUCCEEDED"
    RETRYABLE = "RETRYABLE"
    FAILED = "FAILED"


class FailureKind(Enum):
    NONE = "NONE"
    INTERRUPTED = "INTERRUPTED"
    WOULD_BLOCK = "WOULD_BLOCK"
    READINESS_RACE = "READINESS_RACE"
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"
    PROCESS_LIMIT = "PROCESS_LIMIT"
    EMPTY_READY = "EMPTY_READY"
    BAD_DESCRIPTOR = "BAD_DESCRIPTOR"
    IO = "IO"
    TIMEOUT = "TIMEOUT"
    RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"
    PROTOCOL = "PROTOCOL"
    PERMISSION = "PERMISSION"
    NOT_FOUND = "NOT_FOUND"
    EXIT_NONZERO = "EXIT_NONZERO"
    SIGNALLED = "SIGNALLED"
    UNKNOWN = "UNKNOWN"


class FailureRole(Enum):
    NONE = "NONE"
    PRIMARY = "PRIMARY"
    CLEANUP = "CLEANUP"


class RetryKind(Enum):
    INTERRUPTED = "INTERRUPTED"
    EMPTY_READY = "EMPTY_READY"
    WOULD_BLOCK = "WOULD_BLOCK"


class HandoffState(Enum):
    NOT_REACHED = "NOT_REACHED"
    PRE_EXEC = "PRE_EXEC"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class ExitState(Enum):
    UNOBSERVED = "UNOBSERVED"
    OBSERVED = "OBSERVED"


class ProcessState(Enum):
    NOT_STARTED = "NOT_STARTED"
    STARTED = "STARTED"


class ReapDisposition(Enum):
    UNOBSERVED = "UNOBSERVED"
    REAPED = "REAPED"
    UNKNOWN = "UNKNOWN"


class SelectorState(Enum):
    UNCREATED = "UNCREATED"
    CREATED = "CREATED"
    CLOSED_CONFIRMED = "CLOSED_CONFIRMED"
    CLOSE_UNKNOWN = "CLOSE_UNKNOWN"


class ChannelState(Enum):
    UNACQUIRED = "UNACQUIRED"
    ACQUIRED = "ACQUIRED"
    NONBLOCKING = "NONBLOCKING"
    REGISTERED = "REGISTERED"
    EOF = "EOF"
    UNREGISTERED = "UNREGISTERED"
    CLOSED_CONFIRMED = "CLOSED_CONFIRMED"
    CLOSE_OPEN_RETRYABLE = "CLOSE_OPEN_RETRYABLE"
    CLOSE_DEALLOCATED_ASYNC_UNKNOWN = "CLOSE_DEALLOCATED_ASYNC_UNKNOWN"
    CLOSE_DEALLOCATED_ERROR = "CLOSE_DEALLOCATED_ERROR"
    CLOSE_INVALID_BEFORE_ATTEMPT = "CLOSE_INVALID_BEFORE_ATTEMPT"


class CloseDisposition(Enum):
    NOT_ATTEMPTED = "NOT_ATTEMPTED"
    CONFIRMED = "CONFIRMED"
    # POSIX.1-2024: EINTR leaves the descriptor open and permits a later close.
    OPEN_RETRYABLE = "OPEN_RETRYABLE"
    # POSIX.1-2024: EINPROGRESS deallocates the descriptor while completion is
    # asynchronous and not yet established.
    DEALLOCATED_ASYNC_UNKNOWN = "DEALLOCATED_ASYNC_UNKNOWN"
    # POSIX.1-2024: errors other than EBADF/EINTR/EINPROGRESS deallocate the fd.
    DEALLOCATED_ERROR = "DEALLOCATED_ERROR"
    # EBADF establishes that the argument was not a valid open descriptor.
    INVALID_BEFORE_ATTEMPT = "INVALID_BEFORE_ATTEMPT"


class PostDisposition(Enum):
    UNOBSERVED = "UNOBSERVED"
    MATCHED = "MATCHED"
    CHANGED = "CHANGED"
    UNKNOWN = "UNKNOWN"


class RootObservationPhase(Enum):
    PRE = "PRE"
    POST = "POST"


class RootObservationDisposition(Enum):
    MATCHED = "MATCHED"
    CHANGED = "CHANGED"
    UNKNOWN = "UNKNOWN"


class WaitDisposition(Enum):
    STATUS = "STATUS"
    NO_STATUS = "NO_STATUS"
    INTERRUPTED = "INTERRUPTED"
    NO_CHILD = "NO_CHILD"
    WRONG_PID = "WRONG_PID"
    ERROR = "ERROR"


class WaitMode(Enum):
    BLOCKING_TERMINAL = "BLOCKING_TERMINAL"
    NONBLOCKING_TERMINAL = "NONBLOCKING_TERMINAL"


class WaitStatusKind(Enum):
    EXITED = "EXITED"
    SIGNALLED = "SIGNALLED"
    STOPPED = "STOPPED"
    CONTINUED = "CONTINUED"
    UNKNOWN = "UNKNOWN"


class WaitStatusProvenance(Enum):
    REQUESTED = "REQUESTED"
    UNREQUESTED_OR_TRACED_EXTENSION = "UNREQUESTED_OR_TRACED_EXTENSION"


class FinalizationState(Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"


class ReplayStatus(Enum):
    VERIFIED = "VERIFIED"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    AUTHORITY_VIOLATION = "AUTHORITY_VIOLATION"
    COMMAND_SUBJECT_MISMATCH = "COMMAND_SUBJECT_MISMATCH"
    REDUCER_IDENTITY_MISMATCH = "REDUCER_IDENTITY_MISMATCH"
    REPLAY_IDENTITY_MISMATCH = "REPLAY_IDENTITY_MISMATCH"
    INVOCATION_MISMATCH = "INVOCATION_MISMATCH"
    RETRY_CONTRACT_MISMATCH = "RETRY_CONTRACT_MISMATCH"
    EVENT_CHAIN_INVALID = "EVENT_CHAIN_INVALID"
    LIFECYCLE_INVALID = "LIFECYCLE_INVALID"
    DERIVATION_MISMATCH = "DERIVATION_MISMATCH"
    RECEIPT_HASH_MISMATCH = "RECEIPT_HASH_MISMATCH"
    EXPECTED_RECEIPT_MISMATCH = "EXPECTED_RECEIPT_MISMATCH"


class LegacyCutoverDisposition(Enum):
    CANNOT_MIGRATE = "CANNOT_MIGRATE"


class LegacyCutoverLimitation(Enum):
    V3_LIFECYCLE_INFORMATION_ABSENT = "V3_LIFECYCLE_INFORMATION_ABSENT"


_CHANNELS = tuple(Channel)
_CHANNEL_TARGET = {
    Channel.STATUS: ProcessTarget.STATUS,
    Channel.STDOUT: ProcessTarget.STDOUT,
    Channel.STDERR: ProcessTarget.STDERR,
}
_TARGET_CHANNEL = {target: channel for channel, target in _CHANNEL_TARGET.items()}
_STAGE_ORDER = {stage: index for index, stage in enumerate(ProcessStage)}
_TARGET_ORDER = {target: index for index, target in enumerate(ProcessTarget)}
_RETRY_ORDER = {kind: index for index, kind in enumerate(RetryKind)}

PROCESS_STAGE_TARGET_TABLE = frozenset(
    {
        (ProcessStage.PROCESS_START, ProcessTarget.PROCESS),
        (ProcessStage.SELECTOR_CREATE, ProcessTarget.SELECTOR),
        *((ProcessStage.NONBLOCKING_CONFIGURE, target) for target in _TARGET_CHANNEL),
        *((ProcessStage.SELECTOR_REGISTER, target) for target in _TARGET_CHANNEL),
        (ProcessStage.SELECT, ProcessTarget.SELECTOR),
        *((ProcessStage.READ, target) for target in _TARGET_CHANNEL),
        *((ProcessStage.SELECTOR_UNREGISTER, target) for target in _TARGET_CHANNEL),
        (ProcessStage.WAIT, ProcessTarget.PROCESS),
        (ProcessStage.TIMEOUT, ProcessTarget.PROCESS),
        (ProcessStage.TERMINATE, ProcessTarget.PROCESS),
        (ProcessStage.TERMINATE, ProcessTarget.PROCESS_GROUP),
        (ProcessStage.CLOSE, ProcessTarget.SELECTOR),
        *((ProcessStage.CLOSE, target) for target in _TARGET_CHANNEL),
        (ProcessStage.POST, ProcessTarget.ROOT),
    }
)


def _require_exact_enum(value: object, enum_type: type[Enum], name: str) -> None:
    if type(value) is not enum_type:
        raise ValueError(f"{name} must be an exact {enum_type.__name__}")


def _require_nonnegative_int(value: object, name: str) -> None:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a nonnegative exact integer")


def _require_positive_int(value: object, name: str) -> None:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{name} must be a positive exact integer")


def _require_bounded_int(value: object, name: str, maximum: int) -> None:
    _require_nonnegative_int(value, name)
    if value > maximum:
        raise ValueError(f"{name} exceeds its portable maximum")


def _require_exact_tuple(value: object, name: str) -> None:
    if type(value) is not tuple:
        raise ValueError(f"{name} must be an exact immutable tuple")


def _require_registered_wait_decoder(
    decoder_identity: str,
    supported_signals: tuple[int, ...],
    nonblocking_option_mask: int,
) -> None:
    coordinates = (
        decoder_identity,
        supported_signals,
        nonblocking_option_mask,
    )
    if coordinates not in _PROCESS_WAIT_DECODER_REGISTRY:
        raise ValueError("wait decoder contract is not registered for V3")


def _require_exact_bytes(value: object, name: str) -> None:
    if type(value) is not bytes:
        raise ValueError(f"{name} must be exact immutable bytes")


def _require_hash(value: object, name: str) -> None:
    if (
        type(value) is not str
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{name} must be a lowercase SHA-256 hexadecimal digest")


def _validate_stage_target(stage: ProcessStage, target: ProcessTarget) -> None:
    _require_exact_enum(stage, ProcessStage, "stage")
    _require_exact_enum(target, ProcessTarget, "target")
    if (stage, target) not in PROCESS_STAGE_TARGET_TABLE:
        raise ValueError("invalid process stage-target pair")


def _validate_string_tuple(value: tuple[str, ...], name: str) -> None:
    _require_exact_tuple(value, name)
    if not value:
        raise ValueError(f"{name} must not be empty")
    if len(value) > MAX_PROCESS_ARGV_ENTRIES:
        raise ValueError(f"{name} exceeds the entry cap")
    for item in value:
        if type(item) is not str or not item:
            raise ValueError(f"{name} must contain nonempty exact strings")
        if len(item.encode("utf-8")) > MAX_PROCESS_TEXT_BYTES:
            raise ValueError(f"{name} item exceeds the UTF-8 cap")


def _validate_environment(value: tuple[tuple[str, str], ...], name: str) -> None:
    _require_exact_tuple(value, name)
    if len(value) > MAX_PROCESS_ENVIRONMENT_ENTRIES:
        raise ValueError(f"{name} exceeds the entry cap")
    previous: str | None = None
    for entry in value:
        if (
            type(entry) is not tuple
            or len(entry) != 2
            or type(entry[0]) is not str
            or type(entry[1]) is not str
            or not entry[0]
        ):
            raise ValueError(f"{name} must contain exact string pairs")
        if previous is not None and entry[0] <= previous:
            raise ValueError(f"{name} keys must be unique and canonically ordered")
        if any(len(item.encode("utf-8")) > MAX_PROCESS_TEXT_BYTES for item in entry):
            raise ValueError(f"{name} item exceeds the UTF-8 cap")
        previous = entry[0]


def _require_nonempty_exact_string(value: object, name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{name} must be a nonempty exact string")


def _require_exact_bool(value: object, name: str) -> None:
    if type(value) is not bool:
        raise ValueError(f"{name} must be an exact bool")


def _exact_graph_equal(left: object, right: object) -> bool:
    """Compare every retained coordinate, including ``compare=False`` fields."""

    if type(left) is not type(right):
        return False
    if is_dataclass(left) and not isinstance(left, type):
        return all(
            _exact_graph_equal(getattr(left, item.name), getattr(right, item.name))
            for item in fields(left)
        )
    if type(left) is tuple:
        assert type(right) is tuple
        return len(left) == len(right) and all(
            _exact_graph_equal(left_item, right_item)
            for left_item, right_item in zip(left, right, strict=True)
        )
    return bool(left == right)


def _require_stable_constructor_replay(
    value: object,
    expected_type: type[object],
    name: str,
) -> None:
    """Require an exact value to survive a fresh constructor replay unchanged."""

    if type(value) is not expected_type:
        raise ValueError(f"{name} must have exact type {expected_type.__name__}")
    try:
        reconstructed = replace(value)
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError(f"{name} failed constructor replay validation") from exc
    if not _exact_graph_equal(value, reconstructed):
        raise ValueError(f"{name} changes under constructor replay validation")


def _require_finite_positive_float64_bits(value: object, name: str) -> None:
    if (
        type(value) is not str
        or len(value) != 16
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{name} must encode exactly one float64 value")
    decoded = struct.unpack(">d", bytes.fromhex(value))[0]
    if not math.isfinite(decoded) or decoded <= 0.0:
        raise ValueError(f"{name} must encode a finite positive float64 value")


@dataclass(frozen=True)
class ProcessClockContract:
    name: str
    reader: str
    implementation: str
    monotonic: bool
    adjustable: bool
    resolution_float64_bits: str
    clock_contract_hash: str = ""

    def __post_init__(self) -> None:
        _require_nonempty_exact_string(self.name, "clock name")
        _require_nonempty_exact_string(self.reader, "clock reader")
        _require_nonempty_exact_string(self.implementation, "clock implementation")
        _require_exact_bool(self.monotonic, "monotonic")
        _require_exact_bool(self.adjustable, "adjustable")
        _require_finite_positive_float64_bits(
            self.resolution_float64_bits,
            "clock resolution_float64_bits",
        )
        expected = canonical_digest(
            {
                "name": self.name,
                "reader": self.reader,
                "implementation": self.implementation,
                "monotonic": self.monotonic,
                "adjustable": self.adjustable,
                "resolution_float64_bits": self.resolution_float64_bits,
            },
            domain=_CLOCK_CONTRACT_DOMAIN,
        )
        if self.clock_contract_hash not in {"", expected}:
            raise ValueError("clock_contract_hash does not match clock contract")
        object.__setattr__(self, "clock_contract_hash", expected)


@dataclass(frozen=True)
class ClockDomainOccurrence:
    clock_contract_hash: str
    host_clock_epoch_nonce: bytes
    clock_domain_occurrence_id: str = ""

    def __post_init__(self) -> None:
        _require_hash(self.clock_contract_hash, "clock_contract_hash")
        _require_exact_bytes(self.host_clock_epoch_nonce, "host_clock_epoch_nonce")
        if len(self.host_clock_epoch_nonce) != PROCESS_HOST_NONCE_BYTES:
            raise ValueError("host_clock_epoch_nonce must be exactly 32 bytes")
        expected = canonical_digest(
            {
                "clock_domain_identity": PROCESS_CLOCK_DOMAIN_IDENTITY,
                "clock_contract_hash": self.clock_contract_hash,
                "host_clock_epoch_nonce_hex": self.host_clock_epoch_nonce.hex(),
            },
            domain=_CLOCK_DOMAIN_OCCURRENCE_DOMAIN,
        )
        if self.clock_domain_occurrence_id not in {"", expected}:
            raise ValueError(
                "clock_domain_occurrence_id is not derived from the clock domain"
            )
        object.__setattr__(self, "clock_domain_occurrence_id", expected)


_SELECT_TIMEOUT_ENCODER_IDENTITY = canonical_digest(
    (
        "floor-to-registered-backend-quantum.v1",
        "finite-nonnegative-binary64.v1",
        "never-exceed-pre-effect-remaining.v1",
    ),
    domain="orion.host-evidence-process-select-timeout-encoder.v1",
)
_SELECTOR_BACKEND_IDENTITY = canonical_digest(
    (
        selectors.DefaultSelector.__module__,
        selectors.DefaultSelector.__qualname__,
        os.name,
        sys.platform,
        sys.implementation.name,
        tuple(sys.version_info[:3]),
    ),
    domain="orion.host-evidence-process-selector-backend.v1",
)
_SELECTOR_SYSCALL_WRAPPER_IDENTITY = canonical_digest(
    (
        selectors.DefaultSelector.select.__module__,
        selectors.DefaultSelector.select.__qualname__,
        "pep-475-internal-timeout-recomputation.v1",
        sys.implementation.name,
        tuple(sys.version_info[:3]),
    ),
    domain="orion.host-evidence-process-selector-syscall-wrapper.v1",
)


def _registered_selector_backend_quantum_ns() -> int:
    name = selectors.DefaultSelector.__name__
    if name in {"EpollSelector", "PollSelector", "DevpollSelector"}:
        return 1_000_000
    if name == "SelectSelector":
        return 1_000
    return 1


_SELECTOR_BACKEND_QUANTUM_NS = _registered_selector_backend_quantum_ns()


@dataclass(frozen=True)
class SelectTimeoutContract:
    timeout_encoder_identity: str
    selector_backend_identity: str
    syscall_wrapper_identity: str
    eintr_visibility: EintrVisibility
    backend_quantum_ns: int
    select_timeout_contract_hash: str = ""

    def __post_init__(self) -> None:
        for value, name in (
            (self.timeout_encoder_identity, "timeout_encoder_identity"),
            (self.selector_backend_identity, "selector_backend_identity"),
            (self.syscall_wrapper_identity, "syscall_wrapper_identity"),
        ):
            _require_hash(value, name)
        _require_exact_enum(self.eintr_visibility, EintrVisibility, "eintr_visibility")
        _require_positive_int(self.backend_quantum_ns, "backend_quantum_ns")
        expected_coordinates = (
            _SELECT_TIMEOUT_ENCODER_IDENTITY,
            _SELECTOR_BACKEND_IDENTITY,
            _SELECTOR_SYSCALL_WRAPPER_IDENTITY,
            EintrVisibility.INTERNAL_RECOMPUTE,
            _SELECTOR_BACKEND_QUANTUM_NS,
        )
        actual_coordinates = (
            self.timeout_encoder_identity,
            self.selector_backend_identity,
            self.syscall_wrapper_identity,
            self.eintr_visibility,
            self.backend_quantum_ns,
        )
        if actual_coordinates != expected_coordinates:
            raise ValueError(
                "selector backend, wrapper, encoder, or EINTR visibility is not "
                "registered"
            )
        expected = canonical_digest(
            {
                "timeout_encoder_identity": self.timeout_encoder_identity,
                "selector_backend_identity": self.selector_backend_identity,
                "syscall_wrapper_identity": self.syscall_wrapper_identity,
                "eintr_visibility": self.eintr_visibility.value,
                "backend_quantum_ns": self.backend_quantum_ns,
            },
            domain=_SELECT_TIMEOUT_CONTRACT_DOMAIN,
        )
        if self.select_timeout_contract_hash not in {"", expected}:
            raise ValueError(
                "select_timeout_contract_hash does not match registered contract"
            )
        object.__setattr__(self, "select_timeout_contract_hash", expected)


_CLOCK_INFO = time.get_clock_info("monotonic")
PROCESS_CLOCK_CONTRACT = ProcessClockContract(
    name="monotonic",
    reader="time.monotonic_ns",
    implementation=_CLOCK_INFO.implementation,
    monotonic=_CLOCK_INFO.monotonic,
    adjustable=_CLOCK_INFO.adjustable,
    resolution_float64_bits=struct.pack(">d", _CLOCK_INFO.resolution).hex(),
)
# Freshness is intentionally conservative: two runtimes never become the same
# opaque monotonic epoch merely because their public clock/platform coordinates
# agree.  Later persistence work must distinguish self-validating historical
# replay from membership in this current-capture registry; P1 does not translate
# or compare clock coordinates across runtimes, boots, or hosts.
_REGISTERED_CLOCK_EPOCH_NONCE = os.urandom(PROCESS_HOST_NONCE_BYTES)
PROCESS_CLOCK_DOMAIN_OCCURRENCE = ClockDomainOccurrence(
    clock_contract_hash=PROCESS_CLOCK_CONTRACT.clock_contract_hash,
    host_clock_epoch_nonce=_REGISTERED_CLOCK_EPOCH_NONCE,
)
PROCESS_SELECT_TIMEOUT_CONTRACT = SelectTimeoutContract(
    timeout_encoder_identity=_SELECT_TIMEOUT_ENCODER_IDENTITY,
    selector_backend_identity=_SELECTOR_BACKEND_IDENTITY,
    syscall_wrapper_identity=_SELECTOR_SYSCALL_WRAPPER_IDENTITY,
    eintr_visibility=EintrVisibility.INTERNAL_RECOMPUTE,
    backend_quantum_ns=_SELECTOR_BACKEND_QUANTUM_NS,
)

_PROCESS_CLOCK_CONTRACT_REGISTRY = frozenset(
    {PROCESS_CLOCK_CONTRACT.clock_contract_hash}
)
_PROCESS_CLOCK_DOMAIN_OCCURRENCE_REGISTRY = frozenset(
    {
        (
            PROCESS_CLOCK_DOMAIN_OCCURRENCE.clock_domain_occurrence_id,
            PROCESS_CLOCK_DOMAIN_OCCURRENCE.clock_contract_hash,
        )
    }
)
_PROCESS_DEADLINE_DECODER_REGISTRY = frozenset({PROCESS_DEADLINE_DECODER_IDENTITY})
_PROCESS_SELECT_TIMEOUT_CONTRACT_REGISTRY = frozenset(
    {PROCESS_SELECT_TIMEOUT_CONTRACT.select_timeout_contract_hash}
)

PROCESS_STRICT_DEADLINE_CONTRACT_IDENTITY = canonical_digest(
    (
        PROCESS_CLOCK_DOMAIN_IDENTITY,
        PROCESS_DEADLINE_DECODER_IDENTITY,
        PROCESS_SELECT_TIMEOUT_CONTRACT.select_timeout_contract_hash,
        STRICT_MAIN_EVENTS_PER_EFFECT,
        STRICT_FINALIZE_EVENTS_PER_ATTEMPT,
        STRICT_AUXILIARY_EVENT_COUNT,
        MAX_PROCESS_EVENT_COUNT,
    ),
    domain="orion.host-evidence-process-strict-deadline-contract.v1",
)
PROCESS_RECEIPT_STRICT_DEADLINE_REDUCER_IDENTITY = canonical_digest(
    (
        PROCESS_RECEIPT_V3_SCHEMA_VERSION,
        PROCESS_STRICT_DEADLINE_CONTRACT_IDENTITY,
        "strict-deadline-effect-transactions.v1",
        "legacy-lane-separate.v1",
    ),
    domain="orion.host-evidence-process-reducer-identity.v1",
)
PROCESS_RECEIPT_STRICT_DEADLINE_REPLAY_IDENTITY = canonical_digest(
    (
        PROCESS_RECEIPT_V3_SCHEMA_VERSION,
        PROCESS_RECEIPT_STRICT_DEADLINE_REDUCER_IDENTITY,
        "hash-chain-replay.v1",
        "exact-derived-state.v1",
        "capture-clock-free-replay.v1",
    ),
    domain="orion.host-evidence-process-replay-identity.v1",
)


def _require_registered_clock_contract(value: ProcessClockContract) -> None:
    if type(value) is not ProcessClockContract:
        raise ValueError("clock contract must be an exact ProcessClockContract")
    if value.clock_contract_hash not in _PROCESS_CLOCK_CONTRACT_REGISTRY:
        raise ValueError("clock contract is not registered for strict deadlines")


def _require_registered_clock_domain_occurrence(
    value: ClockDomainOccurrence,
) -> None:
    if type(value) is not ClockDomainOccurrence:
        raise ValueError(
            "clock domain occurrence must be an exact ClockDomainOccurrence"
        )
    coordinates = (value.clock_domain_occurrence_id, value.clock_contract_hash)
    if coordinates not in _PROCESS_CLOCK_DOMAIN_OCCURRENCE_REGISTRY:
        raise ValueError("clock domain occurrence is not registered")


def _require_registered_deadline_decoder(value: str) -> None:
    _require_hash(value, "deadline_decoder_identity")
    if value not in _PROCESS_DEADLINE_DECODER_REGISTRY:
        raise ValueError("deadline decoder identity is not registered")


def _require_registered_select_timeout_contract_hash(value: str) -> None:
    _require_hash(value, "select_timeout_contract_hash")
    if value not in _PROCESS_SELECT_TIMEOUT_CONTRACT_REGISTRY:
        raise ValueError("selector timeout contract is not registered")


def _checked_strict_event_cardinality(
    *,
    main_effect_count: int,
    finalize_attempt_count: int,
    auxiliary_event_count: int,
    maximum_event_count: int,
) -> int:
    for value, name in (
        (main_effect_count, "main_effect_count"),
        (finalize_attempt_count, "finalize_attempt_count"),
        (auxiliary_event_count, "auxiliary_event_count"),
        (maximum_event_count, "maximum_event_count"),
    ):
        _require_nonnegative_int(value, name)
    if maximum_event_count == 0:
        raise ValueError("strict event feasibility maximum must be positive")
    main_events = STRICT_MAIN_EVENTS_PER_EFFECT * main_effect_count
    finalize_events = STRICT_FINALIZE_EVENTS_PER_ATTEMPT * finalize_attempt_count
    total = main_events + finalize_events + auxiliary_event_count
    if total > maximum_event_count:
        raise ValueError("strict event cardinality is infeasible for the event cap")
    return total


PROCESS_WORK_DIMENSIONS = (
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


@dataclass(frozen=True)
class ProcessWorkVector:
    records_admitted: int = 0
    roots_admitted: int = 0
    root_path_components: int = 0
    source_path_components: int = 0
    descriptor_operation_attempts: int = 0
    executable_bytes_observed: int = 0
    git_control_bytes_observed: int = 0
    local_bytes_observed: int = 0
    retained_bytes: int = 0
    git_process_starts: int = 0
    git_protocol_operations: int = 0
    git_stdout_bytes_observed: int = 0
    git_stderr_bytes_observed: int = 0
    git_distinct_objects: int = 0
    git_object_bytes_observed: int = 0
    git_tree_entries_parsed: int = 0
    git_tag_steps: int = 0

    def __post_init__(self) -> None:
        if tuple(self.__dataclass_fields__) != PROCESS_WORK_DIMENSIONS:
            raise RuntimeError("process work coordinate order diverged")
        for name in self.__dataclass_fields__:
            _require_bounded_int(getattr(self, name), name, MAX_PROCESS_WORK_COORDINATE)

    @classmethod
    def zero(cls) -> ProcessWorkVector:
        return cls()

    def __add__(self, other: ProcessWorkVector) -> ProcessWorkVector:
        if type(other) is not ProcessWorkVector:
            return NotImplemented
        return ProcessWorkVector(
            **{
                name: getattr(self, name) + getattr(other, name)
                for name in self.__dataclass_fields__
            }
        )

    def exceeds(self, limit: ProcessWorkVector) -> bool:
        if type(limit) is not ProcessWorkVector:
            raise ValueError("work limit must be an exact ProcessWorkVector")
        return any(
            getattr(self, name) > getattr(limit, name)
            for name in self.__dataclass_fields__
        )


@dataclass(frozen=True)
class ProcessWorkEnvelope:
    main_limit: ProcessWorkVector
    finalize_limit: ProcessWorkVector

    def __post_init__(self) -> None:
        if type(self.main_limit) is not ProcessWorkVector:
            raise ValueError("main_limit must be an exact ProcessWorkVector")
        if type(self.finalize_limit) is not ProcessWorkVector:
            raise ValueError("finalize_limit must be an exact ProcessWorkVector")


@dataclass(frozen=True)
class RetryRule:
    stage: ProcessStage
    target: ProcessTarget
    kind: RetryKind
    max_retries: int

    def __post_init__(self) -> None:
        _validate_stage_target(self.stage, self.target)
        _require_exact_enum(self.kind, RetryKind, "kind")
        _require_positive_int(self.max_retries, "max_retries")
        if self.max_retries > MAX_PROCESS_EVENT_COUNT:
            raise ValueError("max_retries exceeds its portable maximum")


def _retry_rule_key(rule: RetryRule) -> tuple[int, int, int]:
    return (
        _STAGE_ORDER[rule.stage],
        _TARGET_ORDER[rule.target],
        _RETRY_ORDER[rule.kind],
    )


@dataclass(frozen=True)
class RetryContract:
    rules: tuple[RetryRule, ...]
    retry_contract_hash: str = ""

    def __post_init__(self) -> None:
        _require_exact_tuple(self.rules, "rules")
        previous: tuple[int, int, int] | None = None
        for rule in self.rules:
            if type(rule) is not RetryRule:
                raise ValueError("rules must contain exact RetryRule values")
            key = _retry_rule_key(rule)
            if previous is not None and key <= previous:
                raise ValueError("retry rules must be unique and canonically ordered")
            previous = key
        expected = canonical_digest(
            [_retry_rule_payload(rule) for rule in self.rules],
            domain=_RETRY_CONTRACT_DOMAIN,
        )
        if self.retry_contract_hash not in {"", expected}:
            raise ValueError("retry_contract_hash does not match retry rules")
        object.__setattr__(self, "retry_contract_hash", expected)

    @classmethod
    def frozen_default(cls) -> RetryContract:
        rules: list[RetryRule] = [
            RetryRule(
                ProcessStage.SELECT,
                ProcessTarget.SELECTOR,
                RetryKind.INTERRUPTED,
                8,
            ),
            RetryRule(
                ProcessStage.SELECT,
                ProcessTarget.SELECTOR,
                RetryKind.EMPTY_READY,
                8,
            ),
        ]
        for target in (
            ProcessTarget.STATUS,
            ProcessTarget.STDOUT,
            ProcessTarget.STDERR,
        ):
            rules.extend(
                (
                    RetryRule(
                        ProcessStage.READ,
                        target,
                        RetryKind.INTERRUPTED,
                        8,
                    ),
                    RetryRule(
                        ProcessStage.READ,
                        target,
                        RetryKind.WOULD_BLOCK,
                        8,
                    ),
                )
            )
        rules.append(
            RetryRule(
                ProcessStage.WAIT,
                ProcessTarget.PROCESS,
                RetryKind.INTERRUPTED,
                8,
            )
        )
        return cls(tuple(rules))

    def maximum_for(
        self, stage: ProcessStage, target: ProcessTarget, kind: RetryKind
    ) -> int | None:
        for rule in self.rules:
            if (rule.stage, rule.target, rule.kind) == (stage, target, kind):
                return rule.max_retries
        return None


@dataclass(frozen=True)
class ProcessCommandSubject:
    operation: ProcessOperation
    logical_argv: tuple[str, ...]
    logical_environment: tuple[tuple[str, str], ...]
    root_subject_hash: str
    instrument_subject_hash: str
    requested_timeout_ns: int
    status_limit: int
    stdout_limit: int
    stderr_limit: int
    combined_limit: int
    work_envelope: ProcessWorkEnvelope
    retry_contract: RetryContract
    wait_decoder_identity: str = PROCESS_WAIT_DECODER_IDENTITY
    wait_supported_signals: tuple[int, ...] = PROCESS_WAIT_SUPPORTED_SIGNALS
    wait_nonblocking_option_mask: int = PROCESS_WAIT_NONBLOCKING_OPTION_MASK
    command_subject_hash: str = ""
    clock_contract_hash: str | None = None
    deadline_decoder_identity: str | None = None

    def __post_init__(self) -> None:
        _require_exact_enum(self.operation, ProcessOperation, "operation")
        _validate_string_tuple(self.logical_argv, "logical_argv")
        _validate_environment(self.logical_environment, "logical_environment")
        _require_hash(self.root_subject_hash, "root_subject_hash")
        _require_hash(self.instrument_subject_hash, "instrument_subject_hash")
        _require_bounded_int(
            self.requested_timeout_ns,
            "requested_timeout_ns",
            MAX_PROCESS_MONOTONIC_NS,
        )
        if self.requested_timeout_ns == 0:
            raise ValueError("requested_timeout_ns must be positive")
        for name in ("status_limit", "stdout_limit", "stderr_limit", "combined_limit"):
            _require_bounded_int(getattr(self, name), name, MAX_PROCESS_OUTPUT_LIMIT)
        if self.status_limit != PROCESS_HELPER_STATUS_RECEIPT_LIMIT:
            raise ValueError(
                "status_limit must equal the frozen helper-status receipt cap"
            )
        if self.combined_limit < max(self.stdout_limit, self.stderr_limit):
            raise ValueError("combined_limit cannot be below an individual limit")
        if type(self.work_envelope) is not ProcessWorkEnvelope:
            raise ValueError("work_envelope must be an exact ProcessWorkEnvelope")
        if type(self.retry_contract) is not RetryContract:
            raise ValueError("retry_contract must be an exact RetryContract")
        _require_hash(self.wait_decoder_identity, "wait_decoder_identity")
        _require_exact_tuple(self.wait_supported_signals, "wait_supported_signals")
        if not self.wait_supported_signals:
            raise ValueError("wait_supported_signals cannot be empty")
        for numeric_signal in self.wait_supported_signals:
            _require_bounded_int(
                numeric_signal,
                "wait_supported_signals member",
                MAX_PROCESS_SIGNAL,
            )
            if numeric_signal == 0:
                raise ValueError("wait_supported_signals members must be positive")
        if self.wait_supported_signals != tuple(
            sorted(set(self.wait_supported_signals))
        ):
            raise ValueError("wait_supported_signals must be sorted and unique")
        _require_positive_int(
            self.wait_nonblocking_option_mask,
            "wait_nonblocking_option_mask",
        )
        _require_registered_wait_decoder(
            self.wait_decoder_identity,
            self.wait_supported_signals,
            self.wait_nonblocking_option_mask,
        )
        strict_coordinates = (
            self.clock_contract_hash,
            self.deadline_decoder_identity,
        )
        if any(value is not None for value in strict_coordinates):
            if any(value is None for value in strict_coordinates):
                raise ValueError(
                    "strict subject clock and decoder coordinates must be complete"
                )
            assert self.clock_contract_hash is not None
            assert self.deadline_decoder_identity is not None
            _require_hash(self.clock_contract_hash, "clock_contract_hash")
            if self.clock_contract_hash not in _PROCESS_CLOCK_CONTRACT_REGISTRY:
                raise ValueError("subject clock contract is not registered")
            _require_registered_deadline_decoder(self.deadline_decoder_identity)
        expected = canonical_digest(
            _command_subject_payload(self), domain=_COMMAND_SUBJECT_DOMAIN
        )
        if self.command_subject_hash not in {"", expected}:
            raise ValueError("command_subject_hash does not match command subject")
        object.__setattr__(self, "command_subject_hash", expected)


@dataclass(frozen=True)
class MaterializedInvocation:
    command_subject_hash: str
    host_nonce: bytes
    materialized_argv: tuple[str, ...]
    materialized_environment: tuple[tuple[str, str], ...]
    invocation_occurrence_id: str = ""
    strict_deadline_contract_identity: str | None = None
    clock_domain_occurrence_id: str | None = None
    select_timeout_contract_hash: str | None = None

    def __post_init__(self) -> None:
        _require_hash(self.command_subject_hash, "command_subject_hash")
        _require_exact_bytes(self.host_nonce, "host_nonce")
        if len(self.host_nonce) != PROCESS_HOST_NONCE_BYTES:
            raise ValueError("host_nonce must be exactly 32 bytes")
        _validate_string_tuple(self.materialized_argv, "materialized_argv")
        _validate_environment(self.materialized_environment, "materialized_environment")
        strict_coordinates = (
            self.strict_deadline_contract_identity,
            self.clock_domain_occurrence_id,
            self.select_timeout_contract_hash,
        )
        if any(value is not None for value in strict_coordinates):
            if any(value is None for value in strict_coordinates):
                raise ValueError(
                    "strict deadline invocation contract coordinates must be complete"
                )
            assert self.strict_deadline_contract_identity is not None
            assert self.clock_domain_occurrence_id is not None
            assert self.select_timeout_contract_hash is not None
            _require_hash(
                self.strict_deadline_contract_identity,
                "strict_deadline_contract_identity",
            )
            if (
                self.strict_deadline_contract_identity
                != PROCESS_STRICT_DEADLINE_CONTRACT_IDENTITY
            ):
                raise ValueError("strict deadline contract identity is not registered")
            _require_hash(
                self.clock_domain_occurrence_id,
                "clock_domain_occurrence_id",
            )
            if self.clock_domain_occurrence_id != (
                PROCESS_CLOCK_DOMAIN_OCCURRENCE.clock_domain_occurrence_id
            ):
                raise ValueError("clock domain occurrence is not registered")
            _require_registered_select_timeout_contract_hash(
                self.select_timeout_contract_hash
            )
        expected = canonical_digest(
            _invocation_payload(self), domain=_INVOCATION_OCCURRENCE_DOMAIN
        )
        if self.invocation_occurrence_id not in {"", expected}:
            raise ValueError(
                "invocation_occurrence_id does not match materialized invocation"
            )
        object.__setattr__(self, "invocation_occurrence_id", expected)


def _validate_process_work_vector(value: object, name: str) -> None:
    _require_stable_constructor_replay(value, ProcessWorkVector, name)


def _validate_process_work_envelope(value: object, name: str) -> None:
    if type(value) is not ProcessWorkEnvelope:
        raise ValueError(f"{name} must be an exact ProcessWorkEnvelope")
    _validate_process_work_vector(value.main_limit, f"{name}.main_limit")
    _validate_process_work_vector(value.finalize_limit, f"{name}.finalize_limit")
    _require_stable_constructor_replay(value, ProcessWorkEnvelope, name)


def _validate_retry_rule(value: object, name: str) -> None:
    _require_stable_constructor_replay(value, RetryRule, name)


def _validate_retry_contract(value: object, name: str) -> None:
    if type(value) is not RetryContract:
        raise ValueError(f"{name} must be an exact RetryContract")
    _require_exact_tuple(value.rules, f"{name}.rules")
    for index, rule in enumerate(value.rules):
        _validate_retry_rule(rule, f"{name}.rules[{index}]")
    _require_stable_constructor_replay(value, RetryContract, name)


def _validate_process_command_subject(value: object) -> None:
    if type(value) is not ProcessCommandSubject:
        raise ValueError("subject must be an exact ProcessCommandSubject")
    _validate_process_work_envelope(value.work_envelope, "subject.work_envelope")
    _validate_retry_contract(value.retry_contract, "subject.retry_contract")
    _require_stable_constructor_replay(value, ProcessCommandSubject, "subject")


def _validate_materialized_invocation(value: object) -> None:
    _require_stable_constructor_replay(
        value,
        MaterializedInvocation,
        "materialized invocation",
    )


@dataclass(frozen=True)
class StrictDeadlineFeasibility:
    main_effect_count: int
    finalize_attempt_count: int
    auxiliary_event_count: int
    worst_case_main_event_count: int
    worst_case_finalize_event_count: int
    worst_case_total_event_count: int
    maximum_event_count: int

    def __post_init__(self) -> None:
        for value, name in (
            (self.main_effect_count, "main_effect_count"),
            (self.finalize_attempt_count, "finalize_attempt_count"),
            (self.auxiliary_event_count, "auxiliary_event_count"),
            (self.worst_case_main_event_count, "worst_case_main_event_count"),
            (
                self.worst_case_finalize_event_count,
                "worst_case_finalize_event_count",
            ),
            (self.worst_case_total_event_count, "worst_case_total_event_count"),
            (self.maximum_event_count, "maximum_event_count"),
        ):
            _require_nonnegative_int(value, name)
        if self.auxiliary_event_count != STRICT_AUXILIARY_EVENT_COUNT:
            raise ValueError(
                "strict event feasibility must include the frozen auxiliary count"
            )
        if self.maximum_event_count != MAX_PROCESS_EVENT_COUNT:
            raise ValueError("strict event feasibility must use the frozen event cap")
        expected_main = STRICT_MAIN_EVENTS_PER_EFFECT * self.main_effect_count
        expected_finalize = (
            STRICT_FINALIZE_EVENTS_PER_ATTEMPT * self.finalize_attempt_count
        )
        expected_total = _checked_strict_event_cardinality(
            main_effect_count=self.main_effect_count,
            finalize_attempt_count=self.finalize_attempt_count,
            auxiliary_event_count=self.auxiliary_event_count,
            maximum_event_count=self.maximum_event_count,
        )
        if (
            self.worst_case_main_event_count != expected_main
            or self.worst_case_finalize_event_count != expected_finalize
            or self.worst_case_total_event_count != expected_total
        ):
            raise ValueError("strict event feasibility coordinates are inconsistent")

    @classmethod
    def for_subject(
        cls,
        *,
        subject: ProcessCommandSubject,
        strict_deadline_contract_identity: str,
        maximum_event_count: int,
    ) -> StrictDeadlineFeasibility:
        if type(subject) is not ProcessCommandSubject:
            raise ValueError("strict event feasibility requires an exact subject")
        _require_hash(
            strict_deadline_contract_identity,
            "strict_deadline_contract_identity",
        )
        if (
            strict_deadline_contract_identity
            != PROCESS_STRICT_DEADLINE_CONTRACT_IDENTITY
        ):
            raise ValueError("strict deadline contract identity is not registered")
        if maximum_event_count != MAX_PROCESS_EVENT_COUNT:
            raise ValueError("strict event feasibility must use the frozen event cap")
        main_effect_count = (
            subject.work_envelope.main_limit.descriptor_operation_attempts
        )
        finalize_attempt_count = (
            subject.work_envelope.finalize_limit.descriptor_operation_attempts
        )
        total = _checked_strict_event_cardinality(
            main_effect_count=main_effect_count,
            finalize_attempt_count=finalize_attempt_count,
            auxiliary_event_count=STRICT_AUXILIARY_EVENT_COUNT,
            maximum_event_count=maximum_event_count,
        )
        return cls(
            main_effect_count=main_effect_count,
            finalize_attempt_count=finalize_attempt_count,
            auxiliary_event_count=STRICT_AUXILIARY_EVENT_COUNT,
            worst_case_main_event_count=(
                STRICT_MAIN_EVENTS_PER_EFFECT * main_effect_count
            ),
            worst_case_finalize_event_count=(
                STRICT_FINALIZE_EVENTS_PER_ATTEMPT * finalize_attempt_count
            ),
            worst_case_total_event_count=total,
            maximum_event_count=maximum_event_count,
        )


@dataclass(frozen=True)
class OuterDeadlineCommitment:
    deadline_monotonic_ns: int
    clock_domain_occurrence_id: str
    consumer_invocation_occurrence_id: str
    producer_invocation_occurrence_id: str
    parent_deadline_binding_hash: str
    outer_deadline_commitment_hash: str = ""

    def __post_init__(self) -> None:
        _require_bounded_int(
            self.deadline_monotonic_ns,
            "deadline_monotonic_ns",
            MAX_PROCESS_MONOTONIC_NS,
        )
        for value, name in (
            (self.clock_domain_occurrence_id, "clock_domain_occurrence_id"),
            (
                self.consumer_invocation_occurrence_id,
                "consumer_invocation_occurrence_id",
            ),
            (
                self.producer_invocation_occurrence_id,
                "producer_invocation_occurrence_id",
            ),
            (self.parent_deadline_binding_hash, "parent_deadline_binding_hash"),
        ):
            _require_hash(value, name)
        expected = canonical_digest(
            {
                "deadline_monotonic_ns": self.deadline_monotonic_ns,
                "clock_domain_occurrence_id": self.clock_domain_occurrence_id,
                "consumer_invocation_occurrence_id": (
                    self.consumer_invocation_occurrence_id
                ),
                "producer_invocation_occurrence_id": (
                    self.producer_invocation_occurrence_id
                ),
                "parent_deadline_binding_hash": self.parent_deadline_binding_hash,
            },
            domain=_OUTER_DEADLINE_COMMITMENT_DOMAIN,
        )
        if self.outer_deadline_commitment_hash not in {"", expected}:
            raise ValueError(
                "outer_deadline_commitment_hash does not match typed commitment"
            )
        object.__setattr__(self, "outer_deadline_commitment_hash", expected)


@dataclass(frozen=True)
class DeadlineBinding:
    invocation_occurrence_id: str
    started_monotonic_ns: int
    requested_timeout_ns: int
    requested_deadline_monotonic_ns: int
    outer_deadline_monotonic_ns: int | None
    outer_deadline_commitment_hash: str | None
    outer_deadline_producer_invocation_occurrence_id: str | None
    outer_deadline_parent_binding_hash: str | None
    effective_deadline_monotonic_ns: int
    winning_source: DeadlineSource
    start_admission_state: StartAdmissionState
    clock_domain_identity: str
    clock_domain_occurrence_id: str
    clock_contract_hash: str
    deadline_decoder_identity: str
    deadline_binding_hash: str = ""

    def __post_init__(self) -> None:
        _require_hash(self.invocation_occurrence_id, "invocation_occurrence_id")
        for value, name in (
            (self.started_monotonic_ns, "started_monotonic_ns"),
            (self.requested_timeout_ns, "requested_timeout_ns"),
            (
                self.requested_deadline_monotonic_ns,
                "requested_deadline_monotonic_ns",
            ),
            (
                self.effective_deadline_monotonic_ns,
                "effective_deadline_monotonic_ns",
            ),
        ):
            _require_bounded_int(value, name, MAX_PROCESS_MONOTONIC_NS)
        if self.requested_timeout_ns == 0:
            raise ValueError("requested timeout must be positive")
        if self.started_monotonic_ns > (
            MAX_PROCESS_MONOTONIC_NS - self.requested_timeout_ns
        ):
            raise ValueError("requested deadline checked arithmetic overflow")
        expected_requested = self.started_monotonic_ns + self.requested_timeout_ns
        if self.requested_deadline_monotonic_ns != expected_requested:
            raise ValueError("requested deadline arithmetic is inconsistent")
        outer_coordinates = (
            self.outer_deadline_monotonic_ns,
            self.outer_deadline_commitment_hash,
            self.outer_deadline_producer_invocation_occurrence_id,
            self.outer_deadline_parent_binding_hash,
        )
        if any(value is not None for value in outer_coordinates):
            if any(value is None for value in outer_coordinates):
                raise ValueError("outer deadline commitment coordinates are incomplete")
            assert self.outer_deadline_monotonic_ns is not None
            assert self.outer_deadline_commitment_hash is not None
            assert self.outer_deadline_producer_invocation_occurrence_id is not None
            assert self.outer_deadline_parent_binding_hash is not None
            reconstructed_outer = OuterDeadlineCommitment(
                deadline_monotonic_ns=self.outer_deadline_monotonic_ns,
                clock_domain_occurrence_id=self.clock_domain_occurrence_id,
                consumer_invocation_occurrence_id=self.invocation_occurrence_id,
                producer_invocation_occurrence_id=(
                    self.outer_deadline_producer_invocation_occurrence_id
                ),
                parent_deadline_binding_hash=(self.outer_deadline_parent_binding_hash),
            )
            if (
                reconstructed_outer.outer_deadline_commitment_hash
                != self.outer_deadline_commitment_hash
            ):
                raise ValueError(
                    "outer deadline commitment hash does not match retained provenance"
                )
            if self.outer_deadline_monotonic_ns < expected_requested:
                expected_effective = self.outer_deadline_monotonic_ns
                expected_source = DeadlineSource.OUTER_DEADLINE
            else:
                expected_effective = expected_requested
                expected_source = DeadlineSource.REQUESTED_TIMEOUT
        else:
            expected_effective = expected_requested
            expected_source = DeadlineSource.REQUESTED_TIMEOUT
        _require_exact_enum(self.winning_source, DeadlineSource, "winning_source")
        if (
            self.effective_deadline_monotonic_ns != expected_effective
            or self.winning_source is not expected_source
        ):
            raise ValueError("effective deadline minimum or source is inconsistent")
        _require_exact_enum(
            self.start_admission_state,
            StartAdmissionState,
            "start_admission_state",
        )
        expected_admission = (
            StartAdmissionState.DENIED_EXPIRED
            if expected_effective <= self.started_monotonic_ns
            else StartAdmissionState.ADMITTED
        )
        if self.start_admission_state is not expected_admission:
            raise ValueError("start admission contradicts the effective deadline")
        _require_hash(self.clock_domain_identity, "clock_domain_identity")
        if self.clock_domain_identity != PROCESS_CLOCK_DOMAIN_IDENTITY:
            raise ValueError("clock domain identity is not registered")
        _require_hash(
            self.clock_domain_occurrence_id,
            "clock_domain_occurrence_id",
        )
        if self.clock_domain_occurrence_id != (
            PROCESS_CLOCK_DOMAIN_OCCURRENCE.clock_domain_occurrence_id
        ):
            raise ValueError("clock domain occurrence is not registered")
        _require_hash(self.clock_contract_hash, "clock_contract_hash")
        if self.clock_contract_hash not in _PROCESS_CLOCK_CONTRACT_REGISTRY:
            raise ValueError("clock contract is not registered")
        _require_registered_deadline_decoder(self.deadline_decoder_identity)
        expected = canonical_digest(
            {
                "invocation_occurrence_id": self.invocation_occurrence_id,
                "started_monotonic_ns": self.started_monotonic_ns,
                "requested_timeout_ns": self.requested_timeout_ns,
                "requested_deadline_monotonic_ns": (
                    self.requested_deadline_monotonic_ns
                ),
                "outer_deadline_monotonic_ns": self.outer_deadline_monotonic_ns,
                "outer_deadline_commitment_hash": (self.outer_deadline_commitment_hash),
                "outer_deadline_producer_invocation_occurrence_id": (
                    self.outer_deadline_producer_invocation_occurrence_id
                ),
                "outer_deadline_parent_binding_hash": (
                    self.outer_deadline_parent_binding_hash
                ),
                "effective_deadline_monotonic_ns": (
                    self.effective_deadline_monotonic_ns
                ),
                "winning_source": self.winning_source.value,
                "start_admission_state": self.start_admission_state.value,
                "clock_domain_identity": self.clock_domain_identity,
                "clock_domain_occurrence_id": self.clock_domain_occurrence_id,
                "clock_contract_hash": self.clock_contract_hash,
                "deadline_decoder_identity": self.deadline_decoder_identity,
            },
            domain=_DEADLINE_BINDING_DOMAIN,
        )
        if self.deadline_binding_hash not in {"", expected}:
            raise ValueError("deadline_binding_hash does not match deadline binding")
        object.__setattr__(self, "deadline_binding_hash", expected)

    @classmethod
    def from_start_observation(
        cls,
        *,
        invocation_occurrence_id: str,
        started_monotonic_ns: int,
        requested_timeout_ns: int,
        outer_deadline: object | None,
        clock_domain_occurrence: ClockDomainOccurrence,
        clock_contract: ProcessClockContract,
        deadline_decoder_identity: str,
    ) -> DeadlineBinding:
        _require_registered_clock_contract(clock_contract)
        _require_registered_clock_domain_occurrence(clock_domain_occurrence)
        if (
            clock_domain_occurrence.clock_contract_hash
            != clock_contract.clock_contract_hash
        ):
            raise ValueError("clock occurrence and contract identities disagree")
        _require_registered_deadline_decoder(deadline_decoder_identity)
        _require_hash(invocation_occurrence_id, "invocation_occurrence_id")
        _require_bounded_int(
            started_monotonic_ns,
            "started_monotonic_ns",
            MAX_PROCESS_MONOTONIC_NS,
        )
        _require_bounded_int(
            requested_timeout_ns,
            "requested_timeout_ns",
            MAX_PROCESS_MONOTONIC_NS,
        )
        if requested_timeout_ns == 0:
            raise ValueError("requested timeout must be positive")
        if started_monotonic_ns > MAX_PROCESS_MONOTONIC_NS - requested_timeout_ns:
            raise ValueError("requested deadline checked arithmetic overflow")
        requested_deadline = started_monotonic_ns + requested_timeout_ns

        outer_deadline_monotonic_ns: int | None = None
        outer_deadline_commitment_hash: str | None = None
        outer_deadline_producer_invocation_occurrence_id: str | None = None
        outer_deadline_parent_binding_hash: str | None = None
        effective_deadline = requested_deadline
        winning_source = DeadlineSource.REQUESTED_TIMEOUT
        if outer_deadline is not None:
            if type(outer_deadline) is not OuterDeadlineCommitment:
                raise ValueError("outer deadline must be an exact typed commitment")
            if (
                outer_deadline.clock_domain_occurrence_id
                != clock_domain_occurrence.clock_domain_occurrence_id
            ):
                raise ValueError(
                    "outer deadline clock-domain occurrence does not match consumer"
                )
            if (
                outer_deadline.consumer_invocation_occurrence_id
                != invocation_occurrence_id
            ):
                raise ValueError(
                    "outer deadline commitment is bound to another consumer invocation"
                )
            outer_deadline_monotonic_ns = outer_deadline.deadline_monotonic_ns
            outer_deadline_commitment_hash = (
                outer_deadline.outer_deadline_commitment_hash
            )
            outer_deadline_producer_invocation_occurrence_id = (
                outer_deadline.producer_invocation_occurrence_id
            )
            outer_deadline_parent_binding_hash = (
                outer_deadline.parent_deadline_binding_hash
            )
            if outer_deadline_monotonic_ns < requested_deadline:
                effective_deadline = outer_deadline_monotonic_ns
                winning_source = DeadlineSource.OUTER_DEADLINE

        start_admission_state = (
            StartAdmissionState.DENIED_EXPIRED
            if effective_deadline <= started_monotonic_ns
            else StartAdmissionState.ADMITTED
        )
        return cls(
            invocation_occurrence_id=invocation_occurrence_id,
            started_monotonic_ns=started_monotonic_ns,
            requested_timeout_ns=requested_timeout_ns,
            requested_deadline_monotonic_ns=requested_deadline,
            outer_deadline_monotonic_ns=outer_deadline_monotonic_ns,
            outer_deadline_commitment_hash=outer_deadline_commitment_hash,
            outer_deadline_producer_invocation_occurrence_id=(
                outer_deadline_producer_invocation_occurrence_id
            ),
            outer_deadline_parent_binding_hash=outer_deadline_parent_binding_hash,
            effective_deadline_monotonic_ns=effective_deadline,
            winning_source=winning_source,
            start_admission_state=start_admission_state,
            clock_domain_identity=PROCESS_CLOCK_DOMAIN_IDENTITY,
            clock_domain_occurrence_id=(
                clock_domain_occurrence.clock_domain_occurrence_id
            ),
            clock_contract_hash=clock_contract.clock_contract_hash,
            deadline_decoder_identity=deadline_decoder_identity,
        )


@dataclass(frozen=True)
class DeadlineRefusal:
    reason: DeadlineRefusalReason
    invocation_occurrence_id: str
    started_monotonic_ns: int
    requested_timeout_ns: int
    clock_domain_occurrence_id: str
    clock_contract_hash: str
    deadline_decoder_identity: str
    deadline_refusal_hash: str = ""

    def __post_init__(self) -> None:
        _require_exact_enum(self.reason, DeadlineRefusalReason, "reason")
        _require_hash(self.invocation_occurrence_id, "invocation_occurrence_id")
        _require_bounded_int(
            self.started_monotonic_ns,
            "started_monotonic_ns",
            MAX_PROCESS_MONOTONIC_NS,
        )
        _require_bounded_int(
            self.requested_timeout_ns,
            "requested_timeout_ns",
            MAX_PROCESS_MONOTONIC_NS,
        )
        if self.requested_timeout_ns == 0 or self.started_monotonic_ns <= (
            MAX_PROCESS_MONOTONIC_NS - self.requested_timeout_ns
        ):
            raise ValueError(
                "deadline overflow refusal requires unrepresentable operands"
            )
        if self.clock_domain_occurrence_id != (
            PROCESS_CLOCK_DOMAIN_OCCURRENCE.clock_domain_occurrence_id
        ):
            raise ValueError("clock domain occurrence is not registered")
        if self.clock_contract_hash not in _PROCESS_CLOCK_CONTRACT_REGISTRY:
            raise ValueError("clock contract is not registered")
        _require_registered_deadline_decoder(self.deadline_decoder_identity)
        expected = canonical_digest(
            {
                "reason": self.reason.value,
                "invocation_occurrence_id": self.invocation_occurrence_id,
                "started_monotonic_ns": self.started_monotonic_ns,
                "requested_timeout_ns": self.requested_timeout_ns,
                "clock_domain_occurrence_id": self.clock_domain_occurrence_id,
                "clock_contract_hash": self.clock_contract_hash,
                "deadline_decoder_identity": self.deadline_decoder_identity,
            },
            domain=_DEADLINE_REFUSAL_DOMAIN,
        )
        if self.deadline_refusal_hash not in {"", expected}:
            raise ValueError("deadline_refusal_hash does not match refusal")
        object.__setattr__(self, "deadline_refusal_hash", expected)

    @classmethod
    def from_checked_add_overflow(
        cls,
        *,
        invocation_occurrence_id: str,
        started_monotonic_ns: int,
        requested_timeout_ns: int,
        outer_deadline: object | None,
        clock_domain_occurrence: ClockDomainOccurrence,
        clock_contract: ProcessClockContract,
        deadline_decoder_identity: str,
    ) -> DeadlineRefusal:
        if outer_deadline is not None:
            raise ValueError("overflow refusal does not accept an outer deadline")
        _require_registered_clock_contract(clock_contract)
        _require_registered_clock_domain_occurrence(clock_domain_occurrence)
        if (
            clock_domain_occurrence.clock_contract_hash
            != clock_contract.clock_contract_hash
        ):
            raise ValueError("clock occurrence and contract identities disagree")
        _require_registered_deadline_decoder(deadline_decoder_identity)
        return cls(
            reason=DeadlineRefusalReason.ARITHMETIC_OVERFLOW,
            invocation_occurrence_id=invocation_occurrence_id,
            started_monotonic_ns=started_monotonic_ns,
            requested_timeout_ns=requested_timeout_ns,
            clock_domain_occurrence_id=(
                clock_domain_occurrence.clock_domain_occurrence_id
            ),
            clock_contract_hash=clock_contract.clock_contract_hash,
            deadline_decoder_identity=deadline_decoder_identity,
        )


@dataclass(frozen=True)
class SelectCallArgument:
    effect_occurrence_id: str
    remaining_ns: int
    timeout_argument_float64_bits: str
    semantic_requested_wait_ns: int
    select_timeout_contract_hash: str
    select_call_argument_hash: str = ""

    def __post_init__(self) -> None:
        _require_hash(self.effect_occurrence_id, "effect_occurrence_id")
        _require_bounded_int(
            self.remaining_ns,
            "remaining_ns",
            MAX_PROCESS_MONOTONIC_NS,
        )
        if (
            type(self.timeout_argument_float64_bits) is not str
            or len(self.timeout_argument_float64_bits) != 16
            or any(
                character not in "0123456789abcdef"
                for character in self.timeout_argument_float64_bits
            )
        ):
            raise ValueError("select timeout must encode exactly one float64")
        timeout = struct.unpack(
            ">d", bytes.fromhex(self.timeout_argument_float64_bits)
        )[0]
        if not math.isfinite(timeout) or timeout < 0.0:
            raise ValueError("select timeout float64 must be finite and nonnegative")
        _require_bounded_int(
            self.semantic_requested_wait_ns,
            "semantic_requested_wait_ns",
            MAX_PROCESS_MONOTONIC_NS,
        )
        if self.semantic_requested_wait_ns > self.remaining_ns:
            raise ValueError("semantic select wait must be conservative")
        _require_registered_select_timeout_contract_hash(
            self.select_timeout_contract_hash
        )
        expected = canonical_digest(
            {
                "effect_occurrence_id": self.effect_occurrence_id,
                "remaining_ns": self.remaining_ns,
                "timeout_argument_float64_bits": (self.timeout_argument_float64_bits),
                "semantic_requested_wait_ns": self.semantic_requested_wait_ns,
                "select_timeout_contract_hash": (self.select_timeout_contract_hash),
            },
            domain=_SELECT_CALL_ARGUMENT_DOMAIN,
        )
        if self.select_call_argument_hash not in {"", expected}:
            raise ValueError("select_call_argument_hash does not match argument")
        object.__setattr__(self, "select_call_argument_hash", expected)


@dataclass(frozen=True)
class DeadlineAdmission:
    phase: DeadlineEffectPhase
    invocation_occurrence_id: str
    deadline_binding_hash: str
    child_occurrence_id: str
    clock_domain_occurrence_id: str
    stage: ProcessStage
    target: ProcessTarget
    attempt_ordinal: int
    admission_event_index: int
    admission_previous_event_hash: str | None
    deadline_monotonic_ns: int
    observed_monotonic_ns: int
    remaining_ns: int
    crossed: bool
    select_call_argument: SelectCallArgument | None
    effect_occurrence_id: str
    deadline_admission_hash: str = ""

    def __post_init__(self) -> None:
        _require_exact_enum(self.phase, DeadlineEffectPhase, "phase")
        if self.phase is not DeadlineEffectPhase.PRE_EFFECT:
            raise ValueError("deadline admission must use PRE_EFFECT")
        for value, name in (
            (self.invocation_occurrence_id, "invocation_occurrence_id"),
            (self.deadline_binding_hash, "deadline_binding_hash"),
            (self.child_occurrence_id, "child_occurrence_id"),
            (self.clock_domain_occurrence_id, "clock_domain_occurrence_id"),
            (self.effect_occurrence_id, "effect_occurrence_id"),
        ):
            _require_hash(value, name)
        _validate_stage_target(self.stage, self.target)
        _require_positive_int(self.attempt_ordinal, "attempt_ordinal")
        _require_bounded_int(
            self.admission_event_index,
            "admission_event_index",
            MAX_PROCESS_EVENT_COUNT - 1,
        )
        if self.admission_previous_event_hash is not None:
            _require_hash(
                self.admission_previous_event_hash,
                "admission_previous_event_hash",
            )
        expected_effect_occurrence_id = canonical_digest(
            {
                "invocation_occurrence_id": self.invocation_occurrence_id,
                "deadline_binding_hash": self.deadline_binding_hash,
                "child_occurrence_id": self.child_occurrence_id,
                "clock_domain_occurrence_id": self.clock_domain_occurrence_id,
                "stage": self.stage.value,
                "target": self.target.value,
                "attempt_ordinal": self.attempt_ordinal,
                "admission_event_index": self.admission_event_index,
                "admission_previous_event_hash": self.admission_previous_event_hash,
            },
            domain=_EFFECT_OCCURRENCE_DOMAIN,
        )
        if self.effect_occurrence_id != expected_effect_occurrence_id:
            raise ValueError(
                "effect_occurrence_id is not derived from admission coordinates"
            )
        for value, name in (
            (self.deadline_monotonic_ns, "deadline_monotonic_ns"),
            (self.observed_monotonic_ns, "observed_monotonic_ns"),
            (self.remaining_ns, "remaining_ns"),
        ):
            _require_bounded_int(value, name, MAX_PROCESS_MONOTONIC_NS)
        _require_exact_bool(self.crossed, "crossed")
        expected_crossed = self.observed_monotonic_ns >= self.deadline_monotonic_ns
        expected_remaining = max(
            0, self.deadline_monotonic_ns - self.observed_monotonic_ns
        )
        if self.crossed is not expected_crossed or self.remaining_ns != (
            expected_remaining
        ):
            raise ValueError("deadline admission crossing or remaining is inconsistent")
        if self.stage is ProcessStage.SELECT:
            if type(self.select_call_argument) is not SelectCallArgument:
                raise ValueError("SELECT admission requires a select call argument")
            if (
                self.select_call_argument.effect_occurrence_id
                != self.effect_occurrence_id
            ):
                raise ValueError("select argument belongs to another effect occurrence")
        elif self.select_call_argument is not None:
            raise ValueError("non-SELECT admission cannot carry a select argument")
        expected = canonical_digest(
            {
                "phase": self.phase.value,
                "invocation_occurrence_id": self.invocation_occurrence_id,
                "deadline_binding_hash": self.deadline_binding_hash,
                "child_occurrence_id": self.child_occurrence_id,
                "clock_domain_occurrence_id": self.clock_domain_occurrence_id,
                "stage": self.stage.value,
                "target": self.target.value,
                "attempt_ordinal": self.attempt_ordinal,
                "admission_event_index": self.admission_event_index,
                "admission_previous_event_hash": self.admission_previous_event_hash,
                "deadline_monotonic_ns": self.deadline_monotonic_ns,
                "observed_monotonic_ns": self.observed_monotonic_ns,
                "remaining_ns": self.remaining_ns,
                "crossed": self.crossed,
                "select_call_argument_hash": (
                    self.select_call_argument.select_call_argument_hash
                    if self.select_call_argument is not None
                    else None
                ),
                "effect_occurrence_id": self.effect_occurrence_id,
            },
            domain=_DEADLINE_ADMISSION_DOMAIN,
        )
        if self.deadline_admission_hash not in {"", expected}:
            raise ValueError("deadline_admission_hash does not match admission")
        object.__setattr__(self, "deadline_admission_hash", expected)

    @classmethod
    def from_observation(cls, **coordinates: object) -> DeadlineAdmission:
        raise ValueError(
            "deadline admission construction requires the strict effect transaction"
        )


@dataclass(frozen=True)
class DeadlineCompletion:
    phase: DeadlineEffectPhase
    effect_occurrence_id: str
    deadline_binding_hash: str
    child_occurrence_id: str
    clock_domain_occurrence_id: str
    completion_event_index: int
    completion_previous_event_hash: str | None
    deadline_monotonic_ns: int
    observed_monotonic_ns: int
    remaining_ns: int
    crossed: bool
    deadline_completion_hash: str = ""

    def __post_init__(self) -> None:
        _require_exact_enum(self.phase, DeadlineEffectPhase, "phase")
        if self.phase is not DeadlineEffectPhase.POST_EFFECT:
            raise ValueError("deadline completion must use POST_EFFECT")
        for value, name in (
            (self.effect_occurrence_id, "effect_occurrence_id"),
            (self.deadline_binding_hash, "deadline_binding_hash"),
            (self.child_occurrence_id, "child_occurrence_id"),
            (self.clock_domain_occurrence_id, "clock_domain_occurrence_id"),
        ):
            _require_hash(value, name)
        _require_bounded_int(
            self.completion_event_index,
            "completion_event_index",
            MAX_PROCESS_EVENT_COUNT - 1,
        )
        if self.completion_previous_event_hash is not None:
            _require_hash(
                self.completion_previous_event_hash,
                "completion_previous_event_hash",
            )
        for value, name in (
            (self.deadline_monotonic_ns, "deadline_monotonic_ns"),
            (self.observed_monotonic_ns, "observed_monotonic_ns"),
            (self.remaining_ns, "remaining_ns"),
        ):
            _require_bounded_int(value, name, MAX_PROCESS_MONOTONIC_NS)
        _require_exact_bool(self.crossed, "crossed")
        expected_crossed = self.observed_monotonic_ns >= self.deadline_monotonic_ns
        expected_remaining = max(
            0, self.deadline_monotonic_ns - self.observed_monotonic_ns
        )
        if self.crossed is not expected_crossed or self.remaining_ns != (
            expected_remaining
        ):
            raise ValueError(
                "deadline completion crossing or remaining is inconsistent"
            )
        expected = canonical_digest(
            {
                "phase": self.phase.value,
                "effect_occurrence_id": self.effect_occurrence_id,
                "deadline_binding_hash": self.deadline_binding_hash,
                "child_occurrence_id": self.child_occurrence_id,
                "clock_domain_occurrence_id": self.clock_domain_occurrence_id,
                "completion_event_index": self.completion_event_index,
                "completion_previous_event_hash": (self.completion_previous_event_hash),
                "deadline_monotonic_ns": self.deadline_monotonic_ns,
                "observed_monotonic_ns": self.observed_monotonic_ns,
                "remaining_ns": self.remaining_ns,
                "crossed": self.crossed,
            },
            domain=_DEADLINE_COMPLETION_DOMAIN,
        )
        if self.deadline_completion_hash not in {"", expected}:
            raise ValueError("deadline_completion_hash does not match completion")
        object.__setattr__(self, "deadline_completion_hash", expected)

    @classmethod
    def from_observation(
        cls,
        *,
        effect_occurrence_id: str,
        deadline_binding_hash: str,
        child_occurrence_id: str,
        clock_domain_occurrence_id: str,
        completion_event_index: int,
        completion_previous_event_hash: str | None,
        deadline_monotonic_ns: int,
        observed_monotonic_ns: int,
    ) -> DeadlineCompletion:
        return cls(
            phase=DeadlineEffectPhase.POST_EFFECT,
            effect_occurrence_id=effect_occurrence_id,
            deadline_binding_hash=deadline_binding_hash,
            child_occurrence_id=child_occurrence_id,
            clock_domain_occurrence_id=clock_domain_occurrence_id,
            completion_event_index=completion_event_index,
            completion_previous_event_hash=completion_previous_event_hash,
            deadline_monotonic_ns=deadline_monotonic_ns,
            observed_monotonic_ns=observed_monotonic_ns,
            remaining_ns=max(0, deadline_monotonic_ns - observed_monotonic_ns),
            crossed=observed_monotonic_ns >= deadline_monotonic_ns,
        )


@dataclass(frozen=True)
class ProcessStartCompletion:
    invocation_occurrence_id: str
    deadline_binding_hash: str
    child_occurrence_id: str | None
    clock_domain_occurrence_id: str
    completion_event_index: int
    completion_previous_event_hash: str | None
    deadline_monotonic_ns: int
    observed_monotonic_ns: int
    remaining_ns: int
    crossed: bool
    process_start_completion_hash: str = ""

    def __post_init__(self) -> None:
        for value, name in (
            (self.invocation_occurrence_id, "invocation_occurrence_id"),
            (self.deadline_binding_hash, "deadline_binding_hash"),
            (self.clock_domain_occurrence_id, "clock_domain_occurrence_id"),
        ):
            _require_hash(value, name)
        if self.child_occurrence_id is not None:
            _require_hash(self.child_occurrence_id, "child_occurrence_id")
        _require_bounded_int(
            self.completion_event_index,
            "completion_event_index",
            MAX_PROCESS_EVENT_COUNT - 1,
        )
        if self.completion_previous_event_hash is not None:
            _require_hash(
                self.completion_previous_event_hash,
                "completion_previous_event_hash",
            )
        for value, name in (
            (self.deadline_monotonic_ns, "deadline_monotonic_ns"),
            (self.observed_monotonic_ns, "observed_monotonic_ns"),
            (self.remaining_ns, "remaining_ns"),
        ):
            _require_bounded_int(value, name, MAX_PROCESS_MONOTONIC_NS)
        _require_exact_bool(self.crossed, "crossed")
        expected_crossed = self.observed_monotonic_ns >= self.deadline_monotonic_ns
        expected_remaining = max(
            0, self.deadline_monotonic_ns - self.observed_monotonic_ns
        )
        if self.crossed is not expected_crossed or self.remaining_ns != (
            expected_remaining
        ):
            raise ValueError(
                "process start completion crossing or remaining is inconsistent"
            )
        expected = canonical_digest(
            {
                "invocation_occurrence_id": self.invocation_occurrence_id,
                "deadline_binding_hash": self.deadline_binding_hash,
                "child_occurrence_id": self.child_occurrence_id,
                "clock_domain_occurrence_id": self.clock_domain_occurrence_id,
                "completion_event_index": self.completion_event_index,
                "completion_previous_event_hash": (self.completion_previous_event_hash),
                "deadline_monotonic_ns": self.deadline_monotonic_ns,
                "observed_monotonic_ns": self.observed_monotonic_ns,
                "remaining_ns": self.remaining_ns,
                "crossed": self.crossed,
            },
            domain=_PROCESS_START_COMPLETION_DOMAIN,
        )
        if self.process_start_completion_hash not in {"", expected}:
            raise ValueError("process_start_completion_hash does not match completion")
        object.__setattr__(self, "process_start_completion_hash", expected)

    @classmethod
    def from_observation(
        cls,
        *,
        invocation_occurrence_id: str,
        deadline_binding_hash: str,
        child_occurrence_id: str | None,
        clock_domain_occurrence_id: str,
        completion_event_index: int,
        completion_previous_event_hash: str | None,
        deadline_monotonic_ns: int,
        observed_monotonic_ns: int,
    ) -> ProcessStartCompletion:
        return cls(
            invocation_occurrence_id=invocation_occurrence_id,
            deadline_binding_hash=deadline_binding_hash,
            child_occurrence_id=child_occurrence_id,
            clock_domain_occurrence_id=clock_domain_occurrence_id,
            completion_event_index=completion_event_index,
            completion_previous_event_hash=completion_previous_event_hash,
            deadline_monotonic_ns=deadline_monotonic_ns,
            observed_monotonic_ns=observed_monotonic_ns,
            remaining_ns=max(0, deadline_monotonic_ns - observed_monotonic_ns),
            crossed=observed_monotonic_ns >= deadline_monotonic_ns,
        )


@dataclass(frozen=True)
class EmptyReadyObserved:
    effect_occurrence_id: str

    def __post_init__(self) -> None:
        _require_hash(self.effect_occurrence_id, "effect_occurrence_id")


@dataclass(frozen=True)
class DescriptorAcquired:
    channel: Channel

    def __post_init__(self) -> None:
        _require_exact_enum(self.channel, Channel, "channel")


@dataclass(frozen=True)
class ChildIdentityBound:
    child_pid: int
    process_group_id: int
    deadline_monotonic_ns: int

    def __post_init__(self) -> None:
        for value, name in (
            (self.child_pid, "child_pid"),
            (self.process_group_id, "process_group_id"),
        ):
            _require_bounded_int(value, name, MAX_PROCESS_ID)
            if value == 0:
                raise ValueError(f"{name} must be positive")
        _require_bounded_int(
            self.deadline_monotonic_ns,
            "deadline_monotonic_ns",
            MAX_PROCESS_MONOTONIC_NS,
        )
        if self.deadline_monotonic_ns == 0:
            raise ValueError("deadline_monotonic_ns must be positive")


@dataclass(frozen=True)
class RootIdentityObservation:
    phase: RootObservationPhase
    disposition: RootObservationDisposition
    configured_device: int | None
    configured_inode: int | None
    descriptor_device: int | None
    descriptor_inode: int | None
    mechanism_errno: int | None

    def __post_init__(self) -> None:
        _require_exact_enum(self.phase, RootObservationPhase, "phase")
        _require_exact_enum(self.disposition, RootObservationDisposition, "disposition")
        values = (
            self.configured_device,
            self.configured_inode,
            self.descriptor_device,
            self.descriptor_inode,
        )
        for value in values:
            if value is not None:
                _require_bounded_int(value, "root identity coordinate", (1 << 64) - 1)
        if self.mechanism_errno is not None:
            _require_positive_int(self.mechanism_errno, "mechanism_errno")
        if self.disposition in {
            RootObservationDisposition.MATCHED,
            RootObservationDisposition.CHANGED,
        }:
            if (
                any(value is None for value in values)
                or self.mechanism_errno is not None
            ):
                raise ValueError("resolved root observation requires exact identities")
            configured = (self.configured_device, self.configured_inode)
            descriptor = (self.descriptor_device, self.descriptor_inode)
            if (self.disposition is RootObservationDisposition.MATCHED) != (
                configured == descriptor
            ):
                raise ValueError("root disposition contradicts exact identities")
        elif self.mechanism_errno is None:
            raise ValueError("unknown root observation requires mechanism_errno")


@dataclass(frozen=True)
class ReadyBatch:
    channels: tuple[Channel, ...]
    effect_occurrence_id: str | None = None

    def __post_init__(self) -> None:
        _require_exact_tuple(self.channels, "channels")
        if not self.channels:
            raise ValueError("ready batch must be nonempty")
        for channel in self.channels:
            _require_exact_enum(channel, Channel, "channels item")
        if len(set(self.channels)) != len(self.channels):
            raise ValueError("ready batch cannot contain a duplicate channel")
        ranks = [_CHANNELS.index(channel) for channel in self.channels]
        if ranks != sorted(ranks):
            raise ValueError("ready batch must use canonical channel order")
        if self.effect_occurrence_id is not None:
            _require_hash(self.effect_occurrence_id, "effect_occurrence_id")


@dataclass(frozen=True)
class BytesObserved:
    channel: Channel
    acquired_bytes: bytes
    retained_prefix_delta: bytes
    effect_occurrence_id: str | None = None

    def __post_init__(self) -> None:
        _require_exact_enum(self.channel, Channel, "channel")
        _require_exact_bytes(self.acquired_bytes, "acquired_bytes")
        _require_exact_bytes(self.retained_prefix_delta, "retained_prefix_delta")
        if not self.acquired_bytes:
            raise ValueError("acquired_bytes must not be empty")
        if len(self.acquired_bytes) > MAX_PROCESS_EVENT_BYTES:
            raise ValueError("acquired_bytes exceeds the per-event byte cap")
        if not self.acquired_bytes.startswith(self.retained_prefix_delta):
            raise ValueError("retained_prefix_delta must be a prefix of acquired_bytes")
        if self.effect_occurrence_id is not None:
            _require_hash(self.effect_occurrence_id, "effect_occurrence_id")


@dataclass(frozen=True)
class ChannelEof:
    channel: Channel
    effect_occurrence_id: str | None = None

    def __post_init__(self) -> None:
        _require_exact_enum(self.channel, Channel, "channel")
        if self.effect_occurrence_id is not None:
            _require_hash(self.effect_occurrence_id, "effect_occurrence_id")


@dataclass(frozen=True)
class HandoffTransition:
    state: HandoffState

    def __post_init__(self) -> None:
        _require_exact_enum(self.state, HandoffState, "state")
        if self.state is HandoffState.NOT_REACHED:
            raise ValueError("NOT_REACHED is an initial state, not a transition")


@dataclass(frozen=True)
class _HelperStatusObservation:
    state: HandoffState
    protocol_valid: bool
    failure_kind: FailureKind | None
    mechanism_errno: int | None
    helper_stage: str


_HELPER_FAILURE_STAGES = frozenset(
    {
        "HELPER_BOOTSTRAP",
        "HELPER_ROOT_ATTESTATION",
        "HELPER_CHDIR",
        "HELPER_GIT_OPEN",
        "HELPER_GIT_ATTESTATION",
        "HELPER_EXEC",
    }
)


def _helper_wire_kind(mechanism_errno: int) -> str:
    if mechanism_errno in {errno.EMFILE, errno.ENFILE}:
        return "DESCRIPTOR_LIMIT"
    return {
        errno.EAGAIN: "PROCESS_LIMIT",
        errno.ENOENT: "UNAVAILABLE",
        errno.EACCES: "ACCESS_POLICY",
        errno.EPERM: "ACCESS_POLICY",
        errno.E2BIG: "ARGUMENT_LIMIT",
        errno.ENOEXEC: "EXEC_FORMAT",
        errno.ENOMEM: "MEMORY_LIMIT",
        errno.ETXTBSY: "TEXT_BUSY",
        errno.EBADF: "DESCRIPTOR_INVALID",
        errno.EINTR: "INTERRUPTED",
    }.get(mechanism_errno, "IO")


def _helper_failure_kind(mechanism_errno: int) -> FailureKind:
    if mechanism_errno in {
        errno.EMFILE,
        errno.ENFILE,
        errno.E2BIG,
        errno.ENOMEM,
    }:
        return FailureKind.RESOURCE_EXHAUSTED
    if mechanism_errno == errno.EAGAIN:
        return FailureKind.PROCESS_LIMIT
    return _failure_kind_from_errno(mechanism_errno)


def _parse_helper_status_receipt(
    receipt: bytes, *, eof: bool
) -> _HelperStatusObservation:
    """Parse the frozen bounded helper protocol without granting authority."""

    def protocol_unknown() -> _HelperStatusObservation:
        return _HelperStatusObservation(
            HandoffState.UNKNOWN,
            False,
            FailureKind.PROTOCOL,
            None,
            "HELPER_STATUS_READ",
        )

    if (
        type(receipt) is not bytes
        or type(eof) is not bool
        or not receipt
        or len(receipt) > PROCESS_HELPER_STATUS_RECEIPT_LIMIT
        or not receipt.endswith(b"\n")
        or receipt.count(b"\n") not in {1, 2}
    ):
        return protocol_unknown()
    frames = receipt.splitlines(keepends=True)
    if any(
        len(frame) > PROCESS_HELPER_STATUS_FRAME_LIMIT or not frame.endswith(b"\n")
        for frame in frames
    ):
        return protocol_unknown()

    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        parsed: dict[str, object] = {}
        for key, value in pairs:
            if key in parsed:
                raise ValueError("duplicate helper-status field")
            parsed[key] = value
        return parsed

    payloads: list[dict[str, object]] = []
    for frame in frames:
        try:
            payload = json.loads(
                frame[:-1].decode("utf-8", errors="strict"),
                object_pairs_hook=unique_object,
                parse_float=lambda token: (_ for _ in ()).throw(
                    ValueError(f"helper-status float is forbidden: {token}")
                ),
                parse_constant=lambda token: (_ for _ in ()).throw(
                    ValueError(f"helper-status constant is forbidden: {token}")
                ),
            )
            canonical = (
                json.dumps(
                    payload,
                    allow_nan=False,
                    ensure_ascii=True,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode("ascii")
                + b"\n"
            )
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
            UnicodeEncodeError,
            RecursionError,
        ):
            return protocol_unknown()
        if (
            type(payload) is not dict
            or set(payload) != {"errno", "kind", "stage", "version"}
            or canonical != frame
            or payload["version"] != PROCESS_HELPER_STATUS_PROTOCOL_VERSION
        ):
            return protocol_unknown()
        payloads.append(payload)

    first = payloads[0]
    first_is_pre_exec = (
        first["stage"] == "HELPER_PRE_EXEC"
        and first["kind"] is None
        and first["errno"] is None
    )
    if len(payloads) == 2 and not first_is_pre_exec:
        return protocol_unknown()
    if len(payloads) == 1 and first_is_pre_exec:
        return _HelperStatusObservation(
            HandoffState.CONFIRMED if eof else HandoffState.PRE_EXEC,
            True,
            None,
            None,
            "HELPER_PRE_EXEC",
        )

    terminal = payloads[-1]
    stage = terminal["stage"]
    kind = terminal["kind"]
    mechanism_errno = terminal["errno"]
    if (
        type(stage) is not str
        or stage not in _HELPER_FAILURE_STAGES
        or (len(payloads) == 1 and stage == "HELPER_EXEC")
        or (len(payloads) == 2 and stage != "HELPER_EXEC")
        or type(mechanism_errno) is not int
        or mechanism_errno <= 0
        or kind != _helper_wire_kind(mechanism_errno)
    ):
        return protocol_unknown()
    return _HelperStatusObservation(
        HandoffState.FAILED,
        True,
        _helper_failure_kind(mechanism_errno),
        mechanism_errno,
        stage,
    )


@dataclass(frozen=True)
class ExitObserved:
    returncode: int

    def __post_init__(self) -> None:
        if type(self.returncode) is not int:
            raise ValueError("returncode must be an exact integer")


@dataclass(frozen=True)
class ReapObservation:
    disposition: ReapDisposition

    def __post_init__(self) -> None:
        _require_exact_enum(self.disposition, ReapDisposition, "disposition")
        if self.disposition is ReapDisposition.UNOBSERVED:
            raise ValueError("UNOBSERVED is an initial state, not an observation")


def _capture_wait_mode_for_options(options: int) -> WaitMode:
    _require_nonnegative_int(options, "options")
    if options == 0:
        return WaitMode.BLOCKING_TERMINAL
    if options == PROCESS_WAIT_NONBLOCKING_OPTION_MASK:
        return WaitMode.NONBLOCKING_TERMINAL
    raise ValueError("wait option mask is outside the terminal wait modes")


def _capture_wait_options_for_mode(mode: WaitMode) -> int:
    _require_exact_enum(mode, WaitMode, "mode")
    if mode is WaitMode.BLOCKING_TERMINAL:
        return 0
    return PROCESS_WAIT_NONBLOCKING_OPTION_MASK


def _decode_capture_host_wait_status(
    raw_wait_status: int,
) -> tuple[WaitStatusKind, WaitStatusProvenance, int | None, int | None]:
    """Decode one word while the registered capture host is available."""

    _require_bounded_int(
        raw_wait_status,
        "raw_wait_status",
        PROCESS_WAIT_STATUS_RAW_MASK,
    )
    predicates = (
        (WaitStatusKind.EXITED, bool(os.WIFEXITED(raw_wait_status))),
        (WaitStatusKind.SIGNALLED, bool(os.WIFSIGNALED(raw_wait_status))),
        (WaitStatusKind.STOPPED, bool(os.WIFSTOPPED(raw_wait_status))),
        (
            WaitStatusKind.CONTINUED,
            bool(os.WIFCONTINUED(raw_wait_status))
            if hasattr(os, "WIFCONTINUED")
            else False,
        ),
    )
    matched = tuple(kind for kind, applies in predicates if applies)
    extension = WaitStatusProvenance.UNREQUESTED_OR_TRACED_EXTENSION
    if len(matched) != 1:
        return WaitStatusKind.UNKNOWN, extension, None, None

    kind = matched[0]
    if kind is WaitStatusKind.EXITED:
        return (
            kind,
            WaitStatusProvenance.REQUESTED,
            int(os.WEXITSTATUS(raw_wait_status)),
            None,
        )
    if kind is WaitStatusKind.SIGNALLED:
        numeric_signal = int(os.WTERMSIG(raw_wait_status))
        if numeric_signal not in PROCESS_WAIT_SUPPORTED_SIGNALS:
            return WaitStatusKind.UNKNOWN, extension, None, None
        return kind, WaitStatusProvenance.REQUESTED, None, numeric_signal
    if kind is WaitStatusKind.STOPPED:
        numeric_signal = int(os.WSTOPSIG(raw_wait_status))
        if numeric_signal not in PROCESS_WAIT_SUPPORTED_SIGNALS:
            return WaitStatusKind.UNKNOWN, extension, None, None
        return kind, extension, None, numeric_signal
    return WaitStatusKind.CONTINUED, extension, None, None


_WAIT_TABLE_UNKNOWN = 0
_WAIT_TABLE_EXITED = 1
_WAIT_TABLE_SIGNALLED = 2
_WAIT_TABLE_STOPPED = 3
_WAIT_TABLE_CONTINUED = 4


def _capture_wait_decoder_table() -> bytes:
    """Freeze the bounded host decoder so replay never calls ambient OS macros."""

    table = bytearray()
    code_for_kind = {
        WaitStatusKind.UNKNOWN: _WAIT_TABLE_UNKNOWN,
        WaitStatusKind.EXITED: _WAIT_TABLE_EXITED,
        WaitStatusKind.SIGNALLED: _WAIT_TABLE_SIGNALLED,
        WaitStatusKind.STOPPED: _WAIT_TABLE_STOPPED,
        WaitStatusKind.CONTINUED: _WAIT_TABLE_CONTINUED,
    }
    for raw_wait_status in range(PROCESS_WAIT_STATUS_RAW_MASK + 1):
        kind, _provenance, exit_code, status_signal = _decode_capture_host_wait_status(
            raw_wait_status
        )
        coordinate = (
            exit_code
            if exit_code is not None
            else status_signal
            if status_signal is not None
            else 0
        )
        table.extend((code_for_kind[kind], coordinate))
    return bytes(table)


_PROCESS_WAIT_DECODER_TABLE = _capture_wait_decoder_table()


def _decode_host_wait_status(
    raw_wait_status: int,
) -> tuple[WaitStatusKind, WaitStatusProvenance, int | None, int | None]:
    """Replay the import-frozen capture decoder without ambient host calls."""

    _require_bounded_int(
        raw_wait_status,
        "raw_wait_status",
        PROCESS_WAIT_STATUS_RAW_MASK,
    )
    offset = 2 * raw_wait_status
    code = _PROCESS_WAIT_DECODER_TABLE[offset]
    coordinate = _PROCESS_WAIT_DECODER_TABLE[offset + 1]
    extension = WaitStatusProvenance.UNREQUESTED_OR_TRACED_EXTENSION
    if code == _WAIT_TABLE_EXITED:
        return WaitStatusKind.EXITED, WaitStatusProvenance.REQUESTED, coordinate, None
    if code == _WAIT_TABLE_SIGNALLED:
        return (
            WaitStatusKind.SIGNALLED,
            WaitStatusProvenance.REQUESTED,
            None,
            coordinate,
        )
    if code == _WAIT_TABLE_STOPPED:
        return WaitStatusKind.STOPPED, extension, None, coordinate
    if code == _WAIT_TABLE_CONTINUED:
        return WaitStatusKind.CONTINUED, extension, None, None
    return WaitStatusKind.UNKNOWN, extension, None, None


@dataclass(frozen=True)
class WaitObservation:
    disposition: WaitDisposition
    requested_child_pid: int
    options: int
    returned_pid: int | None
    raw_wait_status: int | None
    mechanism_errno: int | None
    mode: WaitMode | None = None
    status_kind: WaitStatusKind | None = None
    status_provenance: WaitStatusProvenance | None = None
    exit_code: int | None = None
    status_signal: int | None = None
    decoder_identity: str | None = None
    _coordinates_inferred: bool = field(default=False, repr=False, compare=False)

    @classmethod
    def from_host_status(
        cls,
        *,
        requested_child_pid: int,
        mode: WaitMode,
        returned_pid: int,
        raw_wait_status: int,
        mechanism_errno: int | None,
        decoder_identity: str,
    ) -> WaitObservation:
        """Capture and type one host status; replay never invokes this decoder."""

        _require_exact_enum(mode, WaitMode, "mode")
        _require_hash(decoder_identity, "decoder_identity")
        if decoder_identity != PROCESS_WAIT_DECODER_IDENTITY:
            raise ValueError("decoder_identity does not name this capture-host decoder")
        if mechanism_errno is not None:
            raise ValueError("host status cannot carry a mechanism errno")
        status_kind, provenance, exit_code, status_signal = _decode_host_wait_status(
            raw_wait_status
        )
        return cls(
            disposition=WaitDisposition.STATUS,
            requested_child_pid=requested_child_pid,
            options=_capture_wait_options_for_mode(mode),
            returned_pid=returned_pid,
            raw_wait_status=raw_wait_status,
            mechanism_errno=None,
            mode=mode,
            status_kind=status_kind,
            status_provenance=provenance,
            exit_code=exit_code,
            status_signal=status_signal,
            decoder_identity=decoder_identity,
        )

    def __post_init__(self) -> None:
        _require_exact_enum(self.disposition, WaitDisposition, "disposition")
        _require_bounded_int(
            self.requested_child_pid, "requested_child_pid", MAX_PROCESS_ID
        )
        if self.requested_child_pid == 0:
            raise ValueError("requested_child_pid must be positive")
        if type(self._coordinates_inferred) is not bool:
            raise ValueError("_coordinates_inferred must be an exact boolean")
        legacy_coordinates_missing = all(
            value is None
            for value in (
                self.mode,
                self.status_kind,
                self.status_provenance,
                self.exit_code,
                self.status_signal,
                self.decoder_identity,
            )
        )
        if self._coordinates_inferred or legacy_coordinates_missing:
            object.__setattr__(
                self,
                "mode",
                _capture_wait_mode_for_options(self.options),
            )
            object.__setattr__(
                self,
                "decoder_identity",
                PROCESS_WAIT_DECODER_IDENTITY,
            )
            if self.disposition is WaitDisposition.STATUS:
                if self.raw_wait_status is None:
                    raise ValueError("STATUS wait requires a raw status")
                kind, provenance, exit_code, status_signal = _decode_host_wait_status(
                    self.raw_wait_status
                )
                object.__setattr__(self, "status_kind", kind)
                object.__setattr__(self, "status_provenance", provenance)
                object.__setattr__(self, "exit_code", exit_code)
                object.__setattr__(self, "status_signal", status_signal)
            else:
                object.__setattr__(self, "status_kind", None)
                object.__setattr__(self, "status_provenance", None)
                object.__setattr__(self, "exit_code", None)
                object.__setattr__(self, "status_signal", None)
            object.__setattr__(self, "_coordinates_inferred", True)

        assert self.mode is not None
        expected_options = _capture_wait_options_for_mode(self.mode)
        if self.options != expected_options:
            raise ValueError("wait option mask contradicts the requested wait mode")
        assert self.decoder_identity is not None
        _require_hash(self.decoder_identity, "decoder_identity")
        for value, name in (
            (self.returned_pid, "returned_pid"),
            (self.raw_wait_status, "raw_wait_status"),
        ):
            if value is not None:
                _require_bounded_int(
                    value,
                    name,
                    (
                        MAX_PROCESS_ID
                        if name == "returned_pid"
                        else PROCESS_WAIT_STATUS_RAW_MASK
                    ),
                )
        if self.mechanism_errno is not None:
            _require_positive_int(self.mechanism_errno, "mechanism_errno")
        if self.disposition is WaitDisposition.STATUS:
            if (
                self.returned_pid is None
                or self.returned_pid <= 0
                or self.raw_wait_status is None
                or self.mechanism_errno is not None
            ):
                raise ValueError("STATUS wait requires returned PID and raw status")
            _require_exact_enum(self.status_kind, WaitStatusKind, "status_kind")
            _require_exact_enum(
                self.status_provenance,
                WaitStatusProvenance,
                "status_provenance",
            )
            if self.status_kind is WaitStatusKind.EXITED:
                if (
                    type(self.exit_code) is not int
                    or not 0 <= self.exit_code <= 255
                    or self.status_signal is not None
                    or self.status_provenance is not WaitStatusProvenance.REQUESTED
                ):
                    raise ValueError("EXITED status has invalid typed coordinates")
            elif self.status_kind is WaitStatusKind.SIGNALLED:
                if (
                    self.exit_code is not None
                    or type(self.status_signal) is not int
                    or self.status_signal not in PROCESS_WAIT_SUPPORTED_SIGNALS
                    or self.status_provenance is not WaitStatusProvenance.REQUESTED
                ):
                    raise ValueError("SIGNALLED status has invalid typed coordinates")
            elif self.status_kind is WaitStatusKind.STOPPED:
                if (
                    self.exit_code is not None
                    or type(self.status_signal) is not int
                    or self.status_signal not in PROCESS_WAIT_SUPPORTED_SIGNALS
                    or self.status_provenance
                    is not WaitStatusProvenance.UNREQUESTED_OR_TRACED_EXTENSION
                ):
                    raise ValueError(
                        "STOPPED status requires traced extension provenance"
                    )
            elif self.status_kind in {
                WaitStatusKind.CONTINUED,
                WaitStatusKind.UNKNOWN,
            }:
                if (
                    self.exit_code is not None
                    or self.status_signal is not None
                    or self.status_provenance
                    is not WaitStatusProvenance.UNREQUESTED_OR_TRACED_EXTENSION
                ):
                    raise ValueError(
                        "nonterminal or unknown status requires extension provenance"
                    )

            if self.decoder_identity == PROCESS_WAIT_DECODER_IDENTITY:
                expected_coordinates = _decode_host_wait_status(self.raw_wait_status)
                actual_coordinates = (
                    self.status_kind,
                    self.status_provenance,
                    self.exit_code,
                    self.status_signal,
                )
                if actual_coordinates != expected_coordinates:
                    raise ValueError(
                        "wait status kind and coordinates contradict raw host status"
                    )
        elif self.disposition is WaitDisposition.WRONG_PID:
            if (
                self.returned_pid is None
                or self.returned_pid in {0, self.requested_child_pid}
                or self.raw_wait_status is None
                or self.mechanism_errno is not None
            ):
                raise ValueError("WRONG_PID wait must preserve the alien status")
        elif self.disposition is WaitDisposition.NO_STATUS:
            if (
                self.returned_pid != 0
                or self.raw_wait_status is not None
                or self.mechanism_errno is not None
                or self.mode is not WaitMode.NONBLOCKING_TERMINAL
            ):
                raise ValueError("NO_STATUS requires WNOHANG and returned PID zero")
        else:
            expected_errno = {
                WaitDisposition.INTERRUPTED: errno.EINTR,
                WaitDisposition.NO_CHILD: errno.ECHILD,
            }.get(self.disposition)
            if self.returned_pid is not None or self.raw_wait_status is not None:
                raise ValueError("failed wait cannot carry PID or raw status")
            if expected_errno is not None and self.mechanism_errno != expected_errno:
                raise ValueError("wait disposition contradicts errno")
            if self.mechanism_errno is None:
                raise ValueError("failed wait requires errno")
        if self.disposition is not WaitDisposition.STATUS and any(
            value is not None
            for value in (
                self.status_kind,
                self.status_provenance,
                self.exit_code,
                self.status_signal,
            )
        ):
            raise ValueError("non-status wait cannot carry typed status coordinates")


@dataclass(frozen=True)
class SignalAttempt:
    target: ProcessTarget
    numeric_signal: int
    child_pid: int
    process_group_id: int
    outcome: OperationOutcome
    mechanism_errno: int | None

    def __post_init__(self) -> None:
        if self.target not in {ProcessTarget.PROCESS, ProcessTarget.PROCESS_GROUP}:
            raise ValueError("signal target must be child or process group")
        _require_bounded_int(self.numeric_signal, "numeric_signal", MAX_PROCESS_SIGNAL)
        if self.numeric_signal == 0:
            raise ValueError("numeric_signal must be positive")
        for value, name in (
            (self.child_pid, "child_pid"),
            (self.process_group_id, "process_group_id"),
        ):
            _require_bounded_int(value, name, MAX_PROCESS_ID)
            if value == 0:
                raise ValueError(f"{name} must be positive")
        _require_exact_enum(self.outcome, OperationOutcome, "outcome")
        if self.outcome is OperationOutcome.SUCCEEDED:
            if self.mechanism_errno is not None:
                raise ValueError("successful signal cannot carry errno")
        else:
            if self.mechanism_errno is None:
                raise ValueError("failed signal requires errno")
            _require_positive_int(self.mechanism_errno, "mechanism_errno")

    @classmethod
    def succeeded(
        cls,
        *,
        target: ProcessTarget,
        numeric_signal: int,
        child_pid: int,
        process_group_id: int,
    ) -> SignalAttempt:
        return cls(
            target,
            numeric_signal,
            child_pid,
            process_group_id,
            OperationOutcome.SUCCEEDED,
            None,
        )

    @classmethod
    def failed(
        cls,
        *,
        target: ProcessTarget,
        numeric_signal: int,
        child_pid: int,
        process_group_id: int,
        mechanism_errno: int,
    ) -> SignalAttempt:
        return cls(
            target,
            numeric_signal,
            child_pid,
            process_group_id,
            OperationOutcome.FAILED,
            mechanism_errno,
        )


@dataclass(frozen=True)
class TimeoutObservation:
    deadline_monotonic_ns: int
    observed_monotonic_ns: int
    crossed: bool
    handoff_state: HandoffState

    def __post_init__(self) -> None:
        _require_bounded_int(
            self.deadline_monotonic_ns,
            "deadline_monotonic_ns",
            MAX_PROCESS_MONOTONIC_NS,
        )
        if self.deadline_monotonic_ns == 0:
            raise ValueError("deadline_monotonic_ns must be positive")
        _require_bounded_int(
            self.observed_monotonic_ns,
            "observed_monotonic_ns",
            MAX_PROCESS_MONOTONIC_NS,
        )
        if type(self.crossed) is not bool:
            raise ValueError("crossed must be an exact bool")
        _require_exact_enum(self.handoff_state, HandoffState, "handoff_state")
        if self.crossed != (self.observed_monotonic_ns >= self.deadline_monotonic_ns):
            raise ValueError("timeout crossing contradicts monotonic observations")


@dataclass(frozen=True)
class RetryObserved:
    stage: ProcessStage
    target: ProcessTarget
    kind: RetryKind
    ordinal: int
    effect_occurrence_id: str | None = None

    def __post_init__(self) -> None:
        _validate_stage_target(self.stage, self.target)
        _require_exact_enum(self.kind, RetryKind, "kind")
        _require_positive_int(self.ordinal, "ordinal")
        if self.effect_occurrence_id is not None:
            _require_hash(self.effect_occurrence_id, "effect_occurrence_id")


@dataclass(frozen=True)
class OperationAttempt:
    stage: ProcessStage
    target: ProcessTarget
    outcome: OperationOutcome
    failure_kind: FailureKind = FailureKind.NONE
    mechanism_errno: int | None = None
    failure_role: FailureRole = FailureRole.NONE
    effect_occurrence_id: str | None = None
    attempt_ordinal: int | None = None

    def __post_init__(self) -> None:
        _validate_stage_target(self.stage, self.target)
        _require_exact_enum(self.outcome, OperationOutcome, "outcome")
        _require_exact_enum(self.failure_kind, FailureKind, "failure_kind")
        _require_exact_enum(self.failure_role, FailureRole, "failure_role")
        strict_effect_coordinates = (
            self.effect_occurrence_id,
            self.attempt_ordinal,
        )
        if any(value is not None for value in strict_effect_coordinates):
            if any(value is None for value in strict_effect_coordinates):
                raise ValueError("strict effect attempt coordinates must be complete")
            assert self.effect_occurrence_id is not None
            assert self.attempt_ordinal is not None
            _require_hash(self.effect_occurrence_id, "effect_occurrence_id")
            _require_positive_int(self.attempt_ordinal, "attempt_ordinal")
        if self.stage is ProcessStage.POST:
            raise ValueError("POST must use the typed PostAttempt payload")
        if self.stage is ProcessStage.WAIT:
            raise ValueError("WAIT must use the typed WaitObservation payload")
        if self.stage is ProcessStage.TERMINATE:
            raise ValueError("TERMINATE must use the typed SignalAttempt payload")
        if self.stage is ProcessStage.CLOSE and self.target in _TARGET_CHANNEL:
            raise ValueError("descriptor CLOSE must use the typed CloseAttempt payload")
        if self.mechanism_errno is not None:
            _require_positive_int(self.mechanism_errno, "mechanism_errno")
        if self.outcome is OperationOutcome.SUCCEEDED:
            if (
                self.failure_kind is not FailureKind.NONE
                or self.mechanism_errno is not None
                or self.failure_role is not FailureRole.NONE
            ):
                raise ValueError("successful operation cannot carry failure fields")
        elif self.outcome is OperationOutcome.RETRYABLE:
            if (
                self.failure_kind is FailureKind.NONE
                or self.failure_role is not FailureRole.NONE
            ):
                raise ValueError(
                    "retryable operation requires a typed kind and no failure role"
                )
        elif (
            self.failure_kind is FailureKind.NONE
            or self.failure_role is FailureRole.NONE
        ):
            raise ValueError("failed operation requires typed failure kind and role")
        if self.outcome is not OperationOutcome.SUCCEEDED:
            expected_kind = _stage_specific_failure_kind(
                self.stage, self.outcome, self.mechanism_errno, self.failure_kind
            )
            if self.failure_kind is not expected_kind:
                raise ValueError("failure kind violates stage-specific errno semantics")

    @classmethod
    def succeeded(
        cls,
        stage: ProcessStage,
        target: ProcessTarget,
        *,
        effect_occurrence_id: str | None = None,
        attempt_ordinal: int | None = None,
    ) -> OperationAttempt:
        return cls(
            stage,
            target,
            OperationOutcome.SUCCEEDED,
            effect_occurrence_id=effect_occurrence_id,
            attempt_ordinal=attempt_ordinal,
        )

    @classmethod
    def failed(
        cls,
        stage: ProcessStage,
        target: ProcessTarget,
        *,
        kind: FailureKind,
        mechanism_errno: int | None,
        role: FailureRole,
        effect_occurrence_id: str | None = None,
        attempt_ordinal: int | None = None,
    ) -> OperationAttempt:
        return cls(
            stage,
            target,
            OperationOutcome.FAILED,
            kind,
            mechanism_errno,
            role,
            effect_occurrence_id,
            attempt_ordinal,
        )

    @classmethod
    def retryable(
        cls,
        stage: ProcessStage,
        target: ProcessTarget,
        *,
        kind: FailureKind,
        mechanism_errno: int | None,
        effect_occurrence_id: str | None = None,
        attempt_ordinal: int | None = None,
    ) -> OperationAttempt:
        return cls(
            stage,
            target,
            OperationOutcome.RETRYABLE,
            kind,
            mechanism_errno,
            FailureRole.NONE,
            effect_occurrence_id,
            attempt_ordinal,
        )


def _stage_specific_failure_kind(
    stage: ProcessStage,
    outcome: OperationOutcome,
    mechanism_errno: int | None,
    declared: FailureKind,
) -> FailureKind:
    if mechanism_errno is None:
        if (
            outcome is OperationOutcome.RETRYABLE
            and stage is ProcessStage.SELECT
            and declared is FailureKind.EMPTY_READY
        ):
            return FailureKind.EMPTY_READY
        return declared
    if mechanism_errno in {errno.EAGAIN, errno.EWOULDBLOCK}:
        if stage is ProcessStage.PROCESS_START:
            return FailureKind.PROCESS_LIMIT
        if stage is ProcessStage.READ:
            return (
                FailureKind.READINESS_RACE
                if outcome is OperationOutcome.RETRYABLE
                else FailureKind.RETRY_EXHAUSTED
            )
        return FailureKind.WOULD_BLOCK
    if mechanism_errno == errno.EINTR:
        return (
            FailureKind.INTERRUPTED
            if outcome is OperationOutcome.RETRYABLE
            else FailureKind.RETRY_EXHAUSTED
        )
    return _failure_kind_from_errno(mechanism_errno)


def _failure_kind_from_errno(mechanism_errno: int) -> FailureKind:
    if mechanism_errno == errno.EINTR:
        return FailureKind.INTERRUPTED
    if mechanism_errno in {errno.EAGAIN, errno.EWOULDBLOCK}:
        return FailureKind.WOULD_BLOCK
    if mechanism_errno == errno.EBADF:
        return FailureKind.BAD_DESCRIPTOR
    if mechanism_errno in {errno.EACCES, errno.EPERM}:
        return FailureKind.PERMISSION
    if mechanism_errno == errno.ENOENT:
        return FailureKind.NOT_FOUND
    return FailureKind.IO


def _close_disposition_from_errno(mechanism_errno: int) -> CloseDisposition:
    if mechanism_errno == errno.EINTR:
        return CloseDisposition.OPEN_RETRYABLE
    if mechanism_errno == errno.EINPROGRESS:
        return CloseDisposition.DEALLOCATED_ASYNC_UNKNOWN
    if mechanism_errno == errno.EBADF:
        return CloseDisposition.INVALID_BEFORE_ATTEMPT
    return CloseDisposition.DEALLOCATED_ERROR


@dataclass(frozen=True)
class CloseAttempt:
    target: ProcessTarget
    outcome: OperationOutcome
    disposition: CloseDisposition
    attempt_ordinal: int
    failure_kind: FailureKind = FailureKind.NONE
    mechanism_errno: int | None = None
    failure_role: FailureRole = FailureRole.NONE

    def __post_init__(self) -> None:
        _validate_stage_target(ProcessStage.CLOSE, self.target)
        if self.target not in _TARGET_CHANNEL:
            raise ValueError("CloseAttempt is only for descriptor channel targets")
        _require_exact_enum(self.outcome, OperationOutcome, "outcome")
        _require_exact_enum(self.disposition, CloseDisposition, "disposition")
        _require_positive_int(self.attempt_ordinal, "attempt_ordinal")
        _require_exact_enum(self.failure_kind, FailureKind, "failure_kind")
        _require_exact_enum(self.failure_role, FailureRole, "failure_role")
        if self.mechanism_errno is not None:
            _require_positive_int(self.mechanism_errno, "mechanism_errno")
        if self.outcome is OperationOutcome.SUCCEEDED:
            if (
                self.disposition is not CloseDisposition.CONFIRMED
                or self.failure_kind is not FailureKind.NONE
                or self.mechanism_errno is not None
                or self.failure_role is not FailureRole.NONE
            ):
                raise ValueError(
                    "successful close must be confirmed without failure fields"
                )
        else:
            if self.mechanism_errno is None:
                raise ValueError("failed close requires mechanism_errno")
            if self.failure_role is FailureRole.NONE:
                raise ValueError("failed close requires a failure role")
            if self.failure_kind is not _failure_kind_from_errno(self.mechanism_errno):
                raise ValueError("failed close has inconsistent failure kind")
            if self.disposition is not _close_disposition_from_errno(
                self.mechanism_errno
            ):
                raise ValueError("failed close has inconsistent POSIX disposition")

    @classmethod
    def succeeded(
        cls, target: ProcessTarget, *, attempt_ordinal: int = 1
    ) -> CloseAttempt:
        return cls(
            target,
            OperationOutcome.SUCCEEDED,
            CloseDisposition.CONFIRMED,
            attempt_ordinal,
        )

    @classmethod
    def failed(
        cls,
        target: ProcessTarget,
        mechanism_errno: int,
        *,
        role: FailureRole,
        attempt_ordinal: int = 1,
    ) -> CloseAttempt:
        _require_positive_int(mechanism_errno, "mechanism_errno")
        return cls(
            target,
            OperationOutcome.FAILED,
            _close_disposition_from_errno(mechanism_errno),
            attempt_ordinal,
            _failure_kind_from_errno(mechanism_errno),
            mechanism_errno,
            role,
        )


@dataclass(frozen=True)
class PostAttempt:
    disposition: PostDisposition

    def __post_init__(self) -> None:
        _require_exact_enum(self.disposition, PostDisposition, "disposition")
        if self.disposition is PostDisposition.UNOBSERVED:
            raise ValueError("UNOBSERVED is an initial state, not a POST attempt")
        _validate_stage_target(ProcessStage.POST, ProcessTarget.ROOT)


@dataclass(frozen=True)
class FinalizationBegin:
    pass


ProcessEventPayload: TypeAlias = (
    DeadlineBinding
    | DeadlineRefusal
    | DeadlineAdmission
    | DeadlineCompletion
    | ProcessStartCompletion
    | DescriptorAcquired
    | ChildIdentityBound
    | RootIdentityObservation
    | ReadyBatch
    | EmptyReadyObserved
    | BytesObserved
    | ChannelEof
    | HandoffTransition
    | WaitObservation
    | SignalAttempt
    | TimeoutObservation
    | RetryObserved
    | OperationAttempt
    | CloseAttempt
    | FinalizationBegin
)


_PAYLOAD_TYPES = (
    DeadlineBinding,
    DeadlineRefusal,
    DeadlineAdmission,
    DeadlineCompletion,
    ProcessStartCompletion,
    DescriptorAcquired,
    ChildIdentityBound,
    RootIdentityObservation,
    ReadyBatch,
    EmptyReadyObserved,
    BytesObserved,
    ChannelEof,
    HandoffTransition,
    WaitObservation,
    SignalAttempt,
    TimeoutObservation,
    RetryObserved,
    OperationAttempt,
    CloseAttempt,
    FinalizationBegin,
)


def _validate_closed_event_payload(payload: object) -> None:
    if type(payload) not in _PAYLOAD_TYPES:
        raise ValueError("payload must be an exact closed process-event payload")
    if type(payload) is DeadlineAdmission and payload.select_call_argument is not None:
        _require_stable_constructor_replay(
            payload.select_call_argument,
            SelectCallArgument,
            "deadline admission select call argument",
        )
    _require_stable_constructor_replay(
        payload,
        type(payload),
        "process-event payload",
    )


def _work_vector(**values: int) -> ProcessWorkVector:
    return ProcessWorkVector(**values)


def _required_work_delta(
    payload: ProcessEventPayload, phase: EventPhase
) -> ProcessWorkVector:
    if isinstance(payload, BytesObserved):
        acquired_coordinate = {
            Channel.STATUS: "git_control_bytes_observed",
            Channel.STDOUT: "git_stdout_bytes_observed",
            Channel.STDERR: "git_stderr_bytes_observed",
        }[payload.channel]
        return _work_vector(
            **{
                acquired_coordinate: len(payload.acquired_bytes),
                "retained_bytes": len(payload.retained_prefix_delta),
            }
        )
    if isinstance(payload, RetryObserved):
        return ProcessWorkVector.zero()
    if isinstance(payload, CloseAttempt):
        return _work_vector(descriptor_operation_attempts=1)
    if isinstance(payload, RootIdentityObservation):
        return _work_vector(descriptor_operation_attempts=1)
    if isinstance(payload, (WaitObservation, SignalAttempt)):
        return _work_vector(descriptor_operation_attempts=1)
    if isinstance(payload, OperationAttempt):
        values: dict[str, int] = {}
        if payload.stage is ProcessStage.PROCESS_START:
            values["git_protocol_operations"] = 1
            if payload.outcome is OperationOutcome.SUCCEEDED:
                values["git_process_starts"] = 1
        values["descriptor_operation_attempts"] = 1
        return _work_vector(**values)
    return ProcessWorkVector.zero()


class ProcessEventChainError(ValueError):
    """The lifecycle envelope is not an intact ordered hash chain."""


@dataclass(frozen=True)
class ProcessLifecycleEvent:
    event_index: int
    previous_event_hash: str | None
    phase: EventPhase
    payload: ProcessEventPayload
    work_delta: ProcessWorkVector
    event_hash: str

    def __post_init__(self) -> None:
        _require_nonnegative_int(self.event_index, "event_index")
        if self.event_index >= MAX_PROCESS_EVENT_COUNT:
            raise ValueError("event_index exceeds the portable event count cap")
        if self.previous_event_hash is not None:
            _require_hash(self.previous_event_hash, "previous_event_hash")
        _require_exact_enum(self.phase, EventPhase, "phase")
        _validate_closed_event_payload(self.payload)
        _validate_process_work_vector(self.work_delta, "work_delta")
        _require_hash(self.event_hash, "event_hash")

    @classmethod
    def create(
        cls,
        *,
        event_index: int,
        previous_event_hash: str | None,
        phase: EventPhase,
        payload: ProcessEventPayload,
        work_delta: ProcessWorkVector | None = None,
    ) -> ProcessLifecycleEvent:
        _validate_closed_event_payload(payload)
        _require_exact_enum(phase, EventPhase, "phase")
        required = _required_work_delta(payload, phase)
        selected = required if work_delta is None else work_delta
        _validate_process_work_vector(selected, "work_delta")
        if selected != required:
            if (
                phase is EventPhase.FINALIZE
                and isinstance(
                    payload,
                    (
                        OperationAttempt,
                        CloseAttempt,
                        RootIdentityObservation,
                        WaitObservation,
                        SignalAttempt,
                    ),
                )
                and selected.descriptor_operation_attempts
                != required.descriptor_operation_attempts
            ):
                raise ValueError(
                    "finalization OS event must charge descriptor_operation_attempts"
                )
            raise ValueError(
                "event work delta does not match the frozen accounting contract"
            )
        unsigned = {
            "event_index": event_index,
            "previous_event_hash": previous_event_hash,
            "phase": phase.value,
            "payload": _event_payload(payload),
            "work_delta": _work_payload(selected),
        }
        event_hash = canonical_digest(unsigned, domain=_EVENT_DOMAIN)
        return cls(
            event_index,
            previous_event_hash,
            phase,
            payload,
            selected,
            event_hash,
        )


def _validate_process_lifecycle_event(event: object) -> None:
    if type(event) is not ProcessLifecycleEvent:
        raise ValueError("event must be an exact ProcessLifecycleEvent")
    _validate_closed_event_payload(event.payload)
    _validate_process_work_vector(event.work_delta, "event work_delta")
    _require_stable_constructor_replay(
        event,
        ProcessLifecycleEvent,
        "process lifecycle event",
    )


def append_process_event(
    events: tuple[ProcessLifecycleEvent, ...],
    payload: ProcessEventPayload,
    *,
    phase: EventPhase = EventPhase.MAIN,
    work_delta: ProcessWorkVector | None = None,
) -> tuple[ProcessLifecycleEvent, ...]:
    _require_exact_tuple(events, "events")
    if len(events) >= MAX_PROCESS_EVENT_COUNT:
        raise ValueError("process event count cap is exhausted")
    for event in events:
        if type(event) is not ProcessLifecycleEvent:
            raise ValueError("events must contain exact ProcessLifecycleEvent values")
    event = ProcessLifecycleEvent.create(
        event_index=len(events),
        previous_event_hash=events[-1].event_hash if events else None,
        phase=phase,
        payload=payload,
        work_delta=work_delta,
    )
    return events + (event,)


@dataclass(frozen=True)
class FailureOccurrence:
    event_index: int
    phase: EventPhase
    stage: ProcessStage
    target: ProcessTarget
    kind: FailureKind
    mechanism_errno: int | None
    role: FailureRole
    close_disposition: CloseDisposition | None
    # Occurrence identity binds the invocation nonce, while derived-state
    # equality represents the same mechanical reduction with or without that
    # optional occurrence binding.  The hash remains serialized and directly
    # comparable, but does not make otherwise identical reductions unequal.
    occurrence_hash: str = field(compare=False)


@dataclass(frozen=True)
class RetryCount:
    stage: ProcessStage
    target: ProcessTarget
    kind: RetryKind
    count: int


@dataclass(frozen=True)
class ProcessDerivedState:
    acquired_prefix: tuple[Channel, ...]
    nonblocking_prefix: tuple[Channel, ...]
    registered_prefix: tuple[Channel, ...]
    unregistered_prefix: tuple[Channel, ...]
    eof_prefix: tuple[Channel, ...]
    status_acquired: bytes
    stdout_acquired: bytes
    stderr_acquired: bytes
    status_retained: bytes
    stdout_retained: bytes
    stderr_retained: bytes
    status_bytes_observed: int
    stdout_bytes_observed: int
    stderr_bytes_observed: int
    process_state: ProcessState
    child_pid: int | None
    process_group_id: int | None
    pre_root_observation: RootIdentityObservation | None
    post_root_observation: RootIdentityObservation | None
    timeout_observation: TimeoutObservation | None
    handoff_state: HandoffState
    exit_state: ExitState
    returncode: int | None
    termination_signal: int | None
    reap_disposition: ReapDisposition
    selector_state: SelectorState
    status_state: ChannelState
    stdout_state: ChannelState
    stderr_state: ChannelState
    status_close_disposition: CloseDisposition
    stdout_close_disposition: CloseDisposition
    stderr_close_disposition: CloseDisposition
    status_close_attempts: int
    stdout_close_attempts: int
    stderr_close_attempts: int
    post_disposition: PostDisposition
    finalization_state: FinalizationState
    main_work: ProcessWorkVector
    finalize_work: ProcessWorkVector
    first_primary: FailureOccurrence | None
    finalize_indices: tuple[int, ...]
    failure_recurrence_signatures: tuple[str, ...]
    failure_occurrences: tuple[FailureOccurrence, ...]
    retry_counts: tuple[RetryCount, ...]
    can_project_success: bool
    deadline_binding: DeadlineBinding | None = None
    deadline_refusal: DeadlineRefusal | None = None
    deadline_censored_effect_occurrences: tuple[str, ...] = ()


def _record_failure(
    *,
    command_subject_hash: str,
    invocation_occurrence_id: str | None,
    event: ProcessLifecycleEvent,
    stage: ProcessStage,
    target: ProcessTarget,
    kind: FailureKind,
    mechanism_errno: int | None,
    role: FailureRole,
    close_disposition: CloseDisposition | None,
    acquired_prefix: tuple[Channel, ...],
    nonblocking_prefix: tuple[Channel, ...],
    registered_prefix: tuple[Channel, ...],
    process_state: ProcessState,
    handoff_state: HandoffState,
    selector_state: SelectorState,
    causal_discriminator: tuple[str, ...],
) -> tuple[FailureOccurrence, str]:
    signature = canonical_digest(
        {
            "command_subject_hash": command_subject_hash,
            "stage": stage.value,
            "target": target.value,
            "kind": kind.value,
            "mechanism_errno": mechanism_errno,
            "close_disposition": (
                close_disposition.value if close_disposition is not None else None
            ),
            "acquired_prefix": tuple(value.value for value in acquired_prefix),
            "nonblocking_prefix": tuple(value.value for value in nonblocking_prefix),
            "registered_prefix": tuple(value.value for value in registered_prefix),
            "process_state": process_state.value,
            "handoff_state": handoff_state.value,
            "selector_state": selector_state.value,
            "causal_discriminator": causal_discriminator,
        },
        domain=_RECURRENCE_DOMAIN,
    )
    occurrence_scope = invocation_occurrence_id or canonical_digest(
        ("UNBOUND_INVOCATION", command_subject_hash),
        domain="orion.host-evidence-process-unbound-occurrence.v1",
    )
    occurrence_hash = canonical_digest(
        {
            "recurrence_signature": signature,
            "invocation_occurrence_id": occurrence_scope,
            "event_hash": event.event_hash,
            "event_index": event.event_index,
            "phase": event.phase.value,
            "role": role.value,
        },
        domain="orion.host-evidence-process-failure-occurrence.v1",
    )
    occurrence = FailureOccurrence(
        event.event_index,
        event.phase,
        stage,
        target,
        kind,
        mechanism_errno,
        role,
        close_disposition,
        occurrence_hash,
    )
    return occurrence, signature


def _validate_event_link(
    event: ProcessLifecycleEvent, index: int, previous_hash: str | None
) -> None:
    _validate_process_lifecycle_event(event)
    if event.event_index != index or event.previous_event_hash != previous_hash:
        raise ProcessEventChainError("event index or previous hash breaks the chain")
    expected = canonical_digest(
        {
            "event_index": event.event_index,
            "previous_event_hash": event.previous_event_hash,
            "phase": event.phase.value,
            "payload": _event_payload(event.payload),
            "work_delta": _work_payload(event.work_delta),
        },
        domain=_EVENT_DOMAIN,
    )
    if event.event_hash != expected:
        raise ProcessEventChainError("event hash does not match event contents")


def _channel_state_after_close(disposition: CloseDisposition) -> ChannelState:
    return {
        CloseDisposition.CONFIRMED: ChannelState.CLOSED_CONFIRMED,
        CloseDisposition.OPEN_RETRYABLE: ChannelState.CLOSE_OPEN_RETRYABLE,
        CloseDisposition.DEALLOCATED_ASYNC_UNKNOWN: (
            ChannelState.CLOSE_DEALLOCATED_ASYNC_UNKNOWN
        ),
        CloseDisposition.DEALLOCATED_ERROR: ChannelState.CLOSE_DEALLOCATED_ERROR,
        CloseDisposition.INVALID_BEFORE_ATTEMPT: (
            ChannelState.CLOSE_INVALID_BEFORE_ATTEMPT
        ),
    }[disposition]


def _validate_output_bounds(
    subject: ProcessCommandSubject,
    acquired: dict[Channel, bytes],
    retained: dict[Channel, bytes],
) -> None:
    channel_limits = {
        Channel.STATUS: subject.status_limit,
        Channel.STDOUT: subject.stdout_limit,
        Channel.STDERR: subject.stderr_limit,
    }
    for channel in Channel:
        acquired_length = len(acquired[channel])
        retained_length = len(retained[channel])
        limit = channel_limits[channel]
        if retained_length > limit:
            raise ValueError("retained output exceeds committed retained cap")
        if acquired_length > limit + 1:
            raise ValueError("output exceeds acquired sentinel cap")
        if not acquired[channel].startswith(retained[channel]):
            raise ValueError("retained output is not a global acquired prefix")
        if acquired_length - retained_length > 1:
            raise ValueError("more than one unretained sentinel was acquired")

    output_acquired = len(acquired[Channel.STDOUT]) + len(acquired[Channel.STDERR])
    output_retained = len(retained[Channel.STDOUT]) + len(retained[Channel.STDERR])
    if output_retained > subject.combined_limit:
        raise ValueError("retained output exceeds combined retained cap")
    if output_acquired > subject.combined_limit + 1:
        raise ValueError("combined output exceeds acquired sentinel cap")

    for channel in Channel:
        acquired_length = len(acquired[channel])
        retained_length = len(retained[channel])
        if acquired_length == retained_length:
            continue
        channel_boundary = acquired_length == channel_limits[channel] + 1
        combined_boundary = (
            channel in {Channel.STDOUT, Channel.STDERR}
            and output_acquired == subject.combined_limit + 1
            and output_retained == subject.combined_limit
        )
        if not channel_boundary and not combined_boundary:
            raise ValueError("unretained sentinel precedes every committed boundary")


def _requires_finalize_lane(payload: ProcessEventPayload) -> bool:
    if isinstance(payload, FinalizationBegin):
        return True
    if isinstance(payload, CloseAttempt | SignalAttempt):
        return True
    if isinstance(payload, RootIdentityObservation):
        return payload.phase is RootObservationPhase.POST
    return isinstance(payload, OperationAttempt) and payload.stage in {
        ProcessStage.SELECTOR_UNREGISTER,
        ProcessStage.CLOSE,
    }


def _payload_stage_target(
    payload: ProcessEventPayload,
) -> tuple[ProcessStage, ProcessTarget]:
    if isinstance(payload, OperationAttempt):
        return payload.stage, payload.target
    if isinstance(payload, CloseAttempt):
        return ProcessStage.CLOSE, payload.target
    if isinstance(payload, SignalAttempt):
        return ProcessStage.TERMINATE, payload.target
    if isinstance(payload, RootIdentityObservation):
        return ProcessStage.POST, ProcessTarget.ROOT
    return ProcessStage.POST, ProcessTarget.ROOT


def reduce_process_events(
    subject: ProcessCommandSubject,
    events: tuple[ProcessLifecycleEvent, ...],
    *,
    invocation_occurrence_id: str | None = None,
) -> ProcessDerivedState:
    _validate_process_command_subject(subject)
    _require_registered_wait_decoder(
        subject.wait_decoder_identity,
        subject.wait_supported_signals,
        subject.wait_nonblocking_option_mask,
    )
    if invocation_occurrence_id is not None:
        _require_hash(invocation_occurrence_id, "invocation_occurrence_id")
    _require_exact_tuple(events, "events")
    if len(events) > MAX_PROCESS_EVENT_COUNT:
        raise ValueError("process event count cap is exceeded")

    acquired: list[Channel] = []
    nonblocking: list[Channel] = []
    registered: list[Channel] = []
    unregistered: list[Channel] = []
    eof_seen: set[Channel] = set()
    retained = {channel: b"" for channel in Channel}
    acquired_output = {channel: b"" for channel in Channel}
    observed = {channel: 0 for channel in Channel}
    channel_states = {channel: ChannelState.UNACQUIRED for channel in Channel}
    close_dispositions = {
        channel: CloseDisposition.NOT_ATTEMPTED for channel in Channel
    }
    close_attempts = {channel: 0 for channel in Channel}
    selector_state = SelectorState.UNCREATED
    process_state = ProcessState.NOT_STARTED
    child_pid: int | None = None
    process_group_id: int | None = None
    pre_root_observation: RootIdentityObservation | None = None
    post_root_observation: RootIdentityObservation | None = None
    timeout_observation: TimeoutObservation | None = None
    deadline_binding: DeadlineBinding | None = None
    deadline_refusal: DeadlineRefusal | None = None
    handoff_state = HandoffState.NOT_REACHED
    exit_state = ExitState.UNOBSERVED
    returncode: int | None = None
    termination_signal: int | None = None
    reap_disposition = ReapDisposition.UNOBSERVED
    wait_observed = False
    post_disposition = PostDisposition.UNOBSERVED
    finalization_state = FinalizationState.NOT_STARTED
    main_work = ProcessWorkVector.zero()
    finalize_work = ProcessWorkVector.zero()
    finalize_indices: list[int] = []
    retry_counts: dict[tuple[ProcessStage, ProcessTarget, RetryKind], int] = {}
    successful_select_pending = False
    ready_pending: set[Channel] = set()
    successful_read_pending: Channel | None = None
    retry_pending: tuple[ProcessStage, ProcessTarget, RetryKind] | None = None
    first_primary: FailureOccurrence | None = None
    recurrence_signatures: list[str] = []
    failure_occurrences: list[FailureOccurrence] = []
    previous_hash: str | None = None

    def record_derived_failure(
        event: ProcessLifecycleEvent,
        *,
        stage: ProcessStage,
        target: ProcessTarget,
        kind: FailureKind,
        mechanism_errno: int | None,
        close_disposition: CloseDisposition | None = None,
        supplied_role: FailureRole | None = None,
        causal_discriminator: tuple[str, ...] = (),
    ) -> None:
        nonlocal first_primary
        role = FailureRole.PRIMARY if not failure_occurrences else FailureRole.CLEANUP
        if supplied_role is not None and supplied_role is not role:
            raise ValueError("supplied failure role contradicts reducer chronology")
        occurrence, signature = _record_failure(
            command_subject_hash=subject.command_subject_hash,
            invocation_occurrence_id=invocation_occurrence_id,
            event=event,
            stage=stage,
            target=target,
            kind=kind,
            mechanism_errno=mechanism_errno,
            role=role,
            close_disposition=close_disposition,
            acquired_prefix=tuple(acquired),
            nonblocking_prefix=tuple(nonblocking),
            registered_prefix=tuple(registered),
            process_state=process_state,
            handoff_state=handoff_state,
            selector_state=selector_state,
            causal_discriminator=causal_discriminator,
        )
        recurrence_signatures.append(signature)
        failure_occurrences.append(occurrence)
        if first_primary is None:
            first_primary = occurrence

    for index, event in enumerate(events):
        if type(event) is not ProcessLifecycleEvent:
            raise ProcessEventChainError(
                "events must contain exact ProcessLifecycleEvent values"
            )
        _validate_event_link(event, index, previous_hash)
        previous_hash = event.event_hash

        if retry_pending is not None and not isinstance(event.payload, RetryObserved):
            raise ValueError("retryable attempt requires immediate RetryObserved")
        if successful_select_pending and not isinstance(event.payload, ReadyBatch):
            raise ValueError("successful select requires immediate ReadyBatch")
        if successful_read_pending is not None and not isinstance(
            event.payload, (BytesObserved, ChannelEof)
        ):
            raise ValueError("successful read requires immediate bytes or EOF")

        if index > 0 and (
            deadline_refusal is not None
            or (
                deadline_binding is not None
                and deadline_binding.start_admission_state
                is StartAdmissionState.DENIED_EXPIRED
            )
        ):
            raise ValueError(
                "deadline refusal or expired start admission forbids continuation"
            )

        if post_disposition is not PostDisposition.UNOBSERVED:
            raise ValueError("POST must be the final lifecycle event")
        payload = event.payload
        if type(payload) in {DeadlineBinding, DeadlineRefusal}:
            if index != 0 or event.phase is not EventPhase.MAIN:
                raise ValueError(
                    "deadline binding or refusal must be the initial event"
                )
            if invocation_occurrence_id is None:
                raise ValueError("strict deadline prefix requires an invocation")
            if payload.invocation_occurrence_id != invocation_occurrence_id:
                raise ValueError(
                    "deadline prefix is bound to another invocation occurrence"
                )
            if payload.requested_timeout_ns != subject.requested_timeout_ns:
                raise ValueError(
                    "deadline requested timeout does not match command subject"
                )
            if (
                subject.clock_contract_hash is None
                or subject.deadline_decoder_identity is None
            ):
                raise ValueError("strict deadline prefix requires a strict subject")
            if payload.clock_contract_hash != subject.clock_contract_hash:
                raise ValueError(
                    "deadline clock contract does not match command subject"
                )
            if payload.deadline_decoder_identity != subject.deadline_decoder_identity:
                raise ValueError(
                    "deadline decoder identity does not match command subject"
                )
        mandatory_finalize = _requires_finalize_lane(payload)
        effective_phase = EventPhase.FINALIZE if mandatory_finalize else event.phase
        if mandatory_finalize and event.phase is not EventPhase.FINALIZE:
            stage, target = _payload_stage_target(payload)
            record_derived_failure(
                event,
                stage=stage,
                target=target,
                kind=FailureKind.PROTOCOL,
                mechanism_errno=None,
                causal_discriminator=("cleanup_labelled_main",),
            )
        if isinstance(payload, FinalizationBegin):
            if event.phase is not EventPhase.FINALIZE:
                raise ValueError("FINALIZATION_BEGIN must be a FINALIZE event")
            if finalization_state is not FinalizationState.NOT_STARTED:
                raise ValueError("FINALIZATION_BEGIN may occur only once")
            if event.work_delta != ProcessWorkVector.zero():
                raise ValueError("FINALIZATION_BEGIN must charge zero work")
            finalization_state = FinalizationState.IN_PROGRESS
        elif event.phase is EventPhase.FINALIZE:
            if finalization_state is FinalizationState.NOT_STARTED:
                raise ValueError("FINALIZE event precedes FINALIZATION_BEGIN")
        elif finalization_state is not FinalizationState.NOT_STARTED:
            raise ValueError("MAIN event cannot follow FINALIZATION_BEGIN")

        if event.phase is EventPhase.FINALIZE:
            if isinstance(payload, OperationAttempt) and payload.stage in {
                ProcessStage.PROCESS_START,
                ProcessStage.SELECTOR_CREATE,
                ProcessStage.NONBLOCKING_CONFIGURE,
                ProcessStage.SELECTOR_REGISTER,
                ProcessStage.SELECT,
                ProcessStage.READ,
            }:
                raise ValueError(
                    f"{payload.stage.value} is not permitted during FINALIZE"
                )
            if isinstance(
                payload,
                (
                    DescriptorAcquired,
                    ReadyBatch,
                    BytesObserved,
                    HandoffTransition,
                    ChildIdentityBound,
                ),
            ):
                raise ValueError(
                    f"{type(payload).__name__} is not permitted during FINALIZE"
                )
            if isinstance(payload, RetryObserved) and (
                payload.stage is not ProcessStage.WAIT
                or payload.target is not ProcessTarget.PROCESS
                or payload.kind is not RetryKind.INTERRUPTED
                or retry_pending
                != (ProcessStage.WAIT, ProcessTarget.PROCESS, RetryKind.INTERRUPTED)
            ):
                raise ValueError(
                    "only an immediate WAIT/EINTR RetryObserved is permitted "
                    "during FINALIZE"
                )

        required_work = _required_work_delta(payload, effective_phase)
        if effective_phase is EventPhase.MAIN:
            main_work = main_work + required_work
            if main_work.exceeds(subject.work_envelope.main_limit):
                raise ValueError("main work envelope accounting is exhausted")
        else:
            finalize_indices.append(index)
            finalize_work = finalize_work + required_work
            if finalize_work.exceeds(subject.work_envelope.finalize_limit):
                raise ValueError("finalize work envelope accounting is exhausted")

        if type(payload) is DeadlineBinding:
            deadline_binding = payload
            if payload.start_admission_state is StartAdmissionState.DENIED_EXPIRED:
                record_derived_failure(
                    event,
                    stage=ProcessStage.PROCESS_START,
                    target=ProcessTarget.PROCESS,
                    kind=FailureKind.TIMEOUT,
                    mechanism_errno=None,
                    causal_discriminator=(
                        "expired_deadline_binding",
                        payload.winning_source.value,
                    ),
                )
        elif type(payload) is DeadlineRefusal:
            deadline_refusal = payload
            record_derived_failure(
                event,
                stage=ProcessStage.PROCESS_START,
                target=ProcessTarget.PROCESS,
                kind=FailureKind.RESOURCE_EXHAUSTED,
                mechanism_errno=None,
                causal_discriminator=(
                    "deadline_refusal",
                    payload.reason.value,
                ),
            )
        elif isinstance(payload, DescriptorAcquired):
            if event.phase is not EventPhase.MAIN:
                raise ValueError("descriptor acquisition cannot occur during FINALIZE")
            expected = (
                _CHANNELS[len(acquired)] if len(acquired) < len(_CHANNELS) else None
            )
            if payload.channel is not expected:
                raise ValueError("descriptor acquisition must extend canonical prefix")
            acquired.append(payload.channel)
            channel_states[payload.channel] = ChannelState.ACQUIRED
        elif isinstance(payload, ChildIdentityBound):
            if (
                event.phase is not EventPhase.MAIN
                or process_state is not ProcessState.STARTED
                or child_pid is not None
            ):
                raise ValueError(
                    "child/process-group identity requires one started occurrence"
                )
            child_pid = payload.child_pid
            process_group_id = payload.process_group_id
        elif isinstance(payload, RootIdentityObservation):
            if payload.phase is RootObservationPhase.PRE:
                if (
                    event.phase is not EventPhase.MAIN
                    or process_state is not ProcessState.NOT_STARTED
                    or pre_root_observation is not None
                ):
                    raise ValueError(
                        "PRE root observation has invalid lifecycle position"
                    )
                pre_root_observation = payload
            else:
                if finalization_state is not FinalizationState.IN_PROGRESS:
                    raise ValueError("POST requires an active finalization traversal")
                if any(
                    channel in acquired
                    and close_dispositions[channel] is CloseDisposition.NOT_ATTEMPTED
                    for channel in Channel
                ):
                    raise ValueError("POST must follow descriptor cleanup traversal")
                if selector_state is SelectorState.CREATED:
                    raise ValueError("POST must follow selector cleanup traversal")
                if process_state is ProcessState.STARTED and (
                    not wait_observed or reap_disposition is ReapDisposition.UNOBSERVED
                ):
                    raise ValueError(
                        "POST must follow an exact child wait/reap or typed unknown reap"
                    )
                post_root_observation = payload
                post_disposition = PostDisposition[payload.disposition.name]
                finalization_state = FinalizationState.COMPLETE
        elif isinstance(payload, ReadyBatch):
            if not successful_select_pending:
                raise ValueError("ReadyBatch requires a successful select")
            for channel in payload.channels:
                if channel_states[channel] is not ChannelState.REGISTERED:
                    raise ValueError("ready channel must currently be registered")
                if channel in ready_pending:
                    raise ValueError("ready channel is already pending consumption")
            ready_pending.update(payload.channels)
            successful_select_pending = False
        elif isinstance(payload, BytesObserved):
            if successful_read_pending is not payload.channel:
                raise ValueError("bytes require a successful read of that channel")
            if channel_states[payload.channel] is not ChannelState.REGISTERED:
                raise ValueError("bytes require a registered channel")
            observed[payload.channel] += len(payload.acquired_bytes)
            acquired_output[payload.channel] += payload.acquired_bytes
            retained[payload.channel] += payload.retained_prefix_delta
            _validate_output_bounds(subject, acquired_output, retained)
            if len(payload.acquired_bytes) > len(payload.retained_prefix_delta):
                record_derived_failure(
                    event,
                    stage=ProcessStage.READ,
                    target=_CHANNEL_TARGET[payload.channel],
                    kind=FailureKind.RESOURCE_EXHAUSTED,
                    mechanism_errno=None,
                    causal_discriminator=(
                        "unretained_limit_sentinel",
                        payload.channel.value,
                    ),
                )
            ready_pending.remove(payload.channel)
            successful_read_pending = None
        elif isinstance(payload, ChannelEof):
            if successful_read_pending is not payload.channel:
                raise ValueError("EOF requires a successful read of that channel")
            if channel_states[payload.channel] is not ChannelState.REGISTERED:
                raise ValueError("EOF requires a registered channel")
            if payload.channel in eof_seen:
                raise ValueError("channel EOF cannot be observed twice")
            eof_seen.add(payload.channel)
            channel_states[payload.channel] = ChannelState.EOF
            ready_pending.remove(payload.channel)
            successful_read_pending = None
        elif isinstance(payload, HandoffTransition):
            observation = _parse_helper_status_receipt(
                acquired_output[Channel.STATUS],
                eof=Channel.STATUS in eof_seen,
            )
            started_helper = (
                process_state is ProcessState.STARTED and child_pid is not None
            )
            if (
                payload.state
                in {
                    HandoffState.FAILED,
                    HandoffState.UNKNOWN,
                }
                and not started_helper
                and event.work_delta == _required_work_delta(payload, event.phase)
            ):
                raise ValueError(
                    "terminal handoff requires a started helper predecessor"
                )
            predecessor_ok = {
                HandoffState.PRE_EXEC: (
                    started_helper and handoff_state is HandoffState.NOT_REACHED
                ),
                HandoffState.CONFIRMED: (
                    started_helper and handoff_state is HandoffState.PRE_EXEC
                ),
                HandoffState.FAILED: (
                    started_helper
                    and handoff_state
                    in {HandoffState.NOT_REACHED, HandoffState.PRE_EXEC}
                ),
                # Preserve invalid/unbound observations as failure knowledge;
                # UNKNOWN never licenses a later transition or projection.
                HandoffState.UNKNOWN: (
                    started_helper
                    and handoff_state
                    in {HandoffState.NOT_REACHED, HandoffState.PRE_EXEC}
                ),
            }[payload.state]
            if observation.state is payload.state and predecessor_ok:
                handoff_state = payload.state
                if payload.state in {HandoffState.FAILED, HandoffState.UNKNOWN}:
                    record_derived_failure(
                        event,
                        stage=(
                            ProcessStage.PROCESS_START
                            if observation.protocol_valid
                            else ProcessStage.READ
                        ),
                        target=(
                            ProcessTarget.PROCESS
                            if observation.protocol_valid
                            else ProcessTarget.STATUS
                        ),
                        kind=observation.failure_kind or FailureKind.PROTOCOL,
                        mechanism_errno=observation.mechanism_errno,
                        causal_discriminator=(observation.helper_stage,),
                    )
            else:
                record_derived_failure(
                    event,
                    stage=ProcessStage.READ,
                    target=ProcessTarget.STATUS,
                    kind=FailureKind.PROTOCOL,
                    mechanism_errno=None,
                    causal_discriminator=(
                        "helper_status_transition_mismatch",
                        observation.helper_stage,
                        payload.state.value,
                    ),
                )
                handoff_state = HandoffState.UNKNOWN
        elif isinstance(payload, WaitObservation):
            wait_observed = True
            if child_pid is None or payload.requested_child_pid != child_pid:
                raise ValueError("wait must target the exact child occurrence")
            if payload.decoder_identity != subject.wait_decoder_identity:
                raise ValueError("wait decoder identity contradicts command subject")
            subject_options = (
                0
                if payload.mode is WaitMode.BLOCKING_TERMINAL
                else subject.wait_nonblocking_option_mask
            )
            if payload.options != subject_options:
                raise ValueError("wait option mask contradicts command subject mode")
            if (
                payload.status_signal is not None
                and payload.status_signal not in subject.wait_supported_signals
            ):
                raise ValueError("wait status signal is outside the subject domain")
            if reap_disposition is ReapDisposition.REAPED:
                raise ValueError("second reap observation is forbidden")
            if payload.disposition is WaitDisposition.STATUS:
                if payload.returned_pid != child_pid:
                    raise ValueError("wait returned a status for the wrong exact child")
                assert payload.status_kind is not None
                if payload.status_kind is WaitStatusKind.EXITED:
                    assert payload.exit_code is not None
                    returncode = payload.exit_code
                    termination_signal = None
                    exit_state = ExitState.OBSERVED
                    reap_disposition = ReapDisposition.REAPED
                    if returncode != 0:
                        record_derived_failure(
                            event,
                            stage=ProcessStage.WAIT,
                            target=ProcessTarget.PROCESS,
                            kind=FailureKind.EXIT_NONZERO,
                            mechanism_errno=None,
                            causal_discriminator=("exit_code", str(returncode)),
                        )
                elif payload.status_kind is WaitStatusKind.SIGNALLED:
                    assert payload.status_signal is not None
                    termination_signal = payload.status_signal
                    returncode = -payload.status_signal
                    exit_state = ExitState.OBSERVED
                    reap_disposition = ReapDisposition.REAPED
                    record_derived_failure(
                        event,
                        stage=ProcessStage.WAIT,
                        target=ProcessTarget.PROCESS,
                        kind=FailureKind.SIGNALLED,
                        mechanism_errno=None,
                        causal_discriminator=(
                            "signal",
                            str(payload.status_signal),
                        ),
                    )
                elif payload.status_kind in {
                    WaitStatusKind.STOPPED,
                    WaitStatusKind.CONTINUED,
                }:
                    record_derived_failure(
                        event,
                        stage=ProcessStage.WAIT,
                        target=ProcessTarget.PROCESS,
                        kind=FailureKind.UNKNOWN,
                        mechanism_errno=None,
                        causal_discriminator=(
                            "nonterminal_status",
                            payload.status_kind.value,
                        ),
                    )
                else:
                    reap_disposition = ReapDisposition.UNKNOWN
                    record_derived_failure(
                        event,
                        stage=ProcessStage.WAIT,
                        target=ProcessTarget.PROCESS,
                        kind=FailureKind.UNKNOWN,
                        mechanism_errno=None,
                        causal_discriminator=("unknown_wait_status",),
                    )
            elif payload.disposition is WaitDisposition.WRONG_PID:
                reap_disposition = ReapDisposition.UNKNOWN
                record_derived_failure(
                    event,
                    stage=ProcessStage.WAIT,
                    target=ProcessTarget.PROCESS,
                    kind=FailureKind.PROTOCOL,
                    mechanism_errno=None,
                )
            elif payload.disposition in {
                WaitDisposition.NO_CHILD,
                WaitDisposition.ERROR,
            }:
                reap_disposition = ReapDisposition.UNKNOWN
                assert payload.mechanism_errno is not None
                record_derived_failure(
                    event,
                    stage=ProcessStage.WAIT,
                    target=ProcessTarget.PROCESS,
                    kind=_failure_kind_from_errno(payload.mechanism_errno),
                    mechanism_errno=payload.mechanism_errno,
                )
            elif payload.disposition is WaitDisposition.INTERRUPTED:
                retry_pending = (
                    ProcessStage.WAIT,
                    ProcessTarget.PROCESS,
                    RetryKind.INTERRUPTED,
                )
        elif isinstance(payload, SignalAttempt):
            if (
                child_pid is None
                or process_group_id is None
                or payload.child_pid != child_pid
                or payload.process_group_id != process_group_id
            ):
                raise ValueError(
                    "signal must bind the exact child/process-group occurrence"
                )
            if payload.outcome is OperationOutcome.FAILED:
                assert payload.mechanism_errno is not None
                record_derived_failure(
                    event,
                    stage=ProcessStage.TERMINATE,
                    target=payload.target,
                    kind=_failure_kind_from_errno(payload.mechanism_errno),
                    mechanism_errno=payload.mechanism_errno,
                )
        elif isinstance(payload, TimeoutObservation):
            if child_pid is None:
                raise ValueError("timeout requires a bound child occurrence")
            bound_deadline = next(
                value.payload.deadline_monotonic_ns
                for value in events[: index + 1]
                if isinstance(value.payload, ChildIdentityBound)
            )
            if payload.deadline_monotonic_ns != bound_deadline:
                raise ValueError("timeout deadline differs from occurrence commitment")
            if payload.handoff_state is not handoff_state:
                raise ValueError("timeout handoff state differs from reducer state")
            if timeout_observation is not None:
                raise ValueError("timeout may be observed only once")
            timeout_observation = payload
            if payload.crossed:
                record_derived_failure(
                    event,
                    stage=ProcessStage.TIMEOUT,
                    target=ProcessTarget.PROCESS,
                    kind=FailureKind.TIMEOUT,
                    mechanism_errno=None,
                )
        elif isinstance(payload, RetryObserved):
            key = (payload.stage, payload.target, payload.kind)
            if retry_pending != key:
                raise ValueError(
                    "retry event requires matching preceding retryable attempt"
                )
            maximum = subject.retry_contract.maximum_for(*key)
            expected_ordinal = retry_counts.get(key, 0) + 1
            if maximum is None or payload.ordinal != expected_ordinal:
                raise ValueError("retry event is outside the committed retry contract")
            if payload.ordinal > maximum:
                raise ValueError("retry contract maximum is exceeded")
            retry_counts[key] = payload.ordinal
            if payload.stage is ProcessStage.READ:
                ready_pending.discard(_TARGET_CHANNEL[payload.target])
            retry_pending = None
        elif isinstance(payload, OperationAttempt):
            if payload.stage is ProcessStage.TIMEOUT:
                raise ValueError(
                    "TIMEOUT must use the typed TimeoutObservation payload "
                    "bound to a child"
                )
            # An OS failure is still evidence that this exact operation was
            # attempted.  Therefore the operation's enabling predicate must
            # hold before *every* outcome, not only before state-advancing
            # successes.  Otherwise a producer could manufacture failure
            # knowledge for an operation that was not yet executable.
            if (
                payload.stage is ProcessStage.PROCESS_START
                and process_state is not ProcessState.NOT_STARTED
            ):
                raise ValueError("process may be started only once")
            if (
                payload.stage is ProcessStage.SELECTOR_CREATE
                and selector_state is not SelectorState.UNCREATED
            ):
                raise ValueError("selector may be created only once")
            if payload.stage is ProcessStage.NONBLOCKING_CONFIGURE:
                channel = _TARGET_CHANNEL[payload.target]
                if channel_states[channel] is not ChannelState.ACQUIRED:
                    raise ValueError(
                        "nonblocking configuration requires acquired channel"
                    )
                expected = (
                    _CHANNELS[len(nonblocking)]
                    if len(nonblocking) < len(_CHANNELS)
                    else None
                )
                if channel is not expected:
                    raise ValueError(
                        "nonblocking configuration requires its canonical "
                        "acquired predecessor"
                    )
            if payload.stage is ProcessStage.SELECTOR_REGISTER:
                channel = _TARGET_CHANNEL[payload.target]
                if selector_state is not SelectorState.CREATED:
                    raise ValueError("registration requires a created selector")
                if channel_states[channel] is not ChannelState.NONBLOCKING:
                    raise ValueError("registration requires a nonblocking channel")
                expected = (
                    _CHANNELS[len(registered)]
                    if len(registered) < len(_CHANNELS)
                    else None
                )
                if channel is not expected:
                    raise ValueError(
                        "registration requires its canonical channel predecessor"
                    )
            if payload.stage in {ProcessStage.WAIT, ProcessStage.TERMINATE} and (
                process_state is not ProcessState.STARTED or child_pid is None
            ):
                raise ValueError("wait or terminate attempt requires a started process")
            if payload.stage is ProcessStage.SELECT:
                if selector_state is not SelectorState.CREATED:
                    raise ValueError("select requires a created selector")
                if ready_pending:
                    raise ValueError("select cannot replace unconsumed ready channels")
            if payload.stage is ProcessStage.READ:
                channel = _TARGET_CHANNEL[payload.target]
                if channel not in ready_pending:
                    raise ValueError("read requires a pending ready channel")
            if payload.stage is ProcessStage.SELECTOR_UNREGISTER:
                channel = _TARGET_CHANNEL[payload.target]
                if channel_states[channel] not in {
                    ChannelState.REGISTERED,
                    ChannelState.EOF,
                }:
                    raise ValueError("unregister requires a registered channel")
                expected = (
                    _CHANNELS[len(unregistered)]
                    if len(unregistered) < len(_CHANNELS)
                    else None
                )
                if channel is not expected:
                    raise ValueError(
                        "unregister requires its canonical channel predecessor"
                    )
            if (
                payload.stage is ProcessStage.CLOSE
                and payload.target is ProcessTarget.SELECTOR
            ):
                if selector_state is not SelectorState.CREATED:
                    raise ValueError("selector close requires created selector")
                if any(
                    state in {ChannelState.REGISTERED, ChannelState.EOF}
                    for state in channel_states.values()
                ):
                    raise ValueError("selector close requires unregister traversal")
            if payload.outcome is OperationOutcome.RETRYABLE:
                retry_kind = {
                    FailureKind.EMPTY_READY: RetryKind.EMPTY_READY,
                    FailureKind.INTERRUPTED: RetryKind.INTERRUPTED,
                    FailureKind.READINESS_RACE: RetryKind.WOULD_BLOCK,
                    FailureKind.WOULD_BLOCK: RetryKind.WOULD_BLOCK,
                }.get(payload.failure_kind)
                if retry_kind is None:
                    raise ValueError(
                        "retryable failure kind has no retry contract event"
                    )
                retry_pending = (payload.stage, payload.target, retry_kind)
                continue
            if payload.outcome is OperationOutcome.FAILED:
                if payload.failure_kind is FailureKind.RETRY_EXHAUSTED:
                    if payload.mechanism_errno == errno.EINTR:
                        exhausted_kind = RetryKind.INTERRUPTED
                    elif payload.mechanism_errno in {
                        errno.EAGAIN,
                        errno.EWOULDBLOCK,
                    }:
                        exhausted_kind = RetryKind.WOULD_BLOCK
                    elif (
                        payload.mechanism_errno is None
                        and payload.stage is ProcessStage.SELECT
                    ):
                        exhausted_kind = RetryKind.EMPTY_READY
                    else:
                        raise ValueError(
                            "retry exhaustion lacks a typed retry mechanism"
                        )
                    exhausted_key = (
                        payload.stage,
                        payload.target,
                        exhausted_kind,
                    )
                    maximum = subject.retry_contract.maximum_for(*exhausted_key)
                    if maximum is None or retry_counts.get(exhausted_key, 0) != maximum:
                        raise ValueError(
                            "retry exhaustion requires the committed retry count"
                        )
                record_derived_failure(
                    event=event,
                    stage=payload.stage,
                    target=payload.target,
                    kind=payload.failure_kind,
                    mechanism_errno=payload.mechanism_errno,
                    supplied_role=payload.failure_role,
                )
                if (
                    payload.stage is ProcessStage.CLOSE
                    and payload.target is ProcessTarget.SELECTOR
                ):
                    selector_state = SelectorState.CLOSE_UNKNOWN
                continue

            if payload.stage is ProcessStage.PROCESS_START:
                if process_state is not ProcessState.NOT_STARTED:
                    raise ValueError("process may be started only once")
                process_state = ProcessState.STARTED
            elif payload.stage is ProcessStage.SELECT:
                successful_select_pending = True
            elif payload.stage is ProcessStage.READ:
                successful_read_pending = _TARGET_CHANNEL[payload.target]
            elif payload.stage is ProcessStage.SELECTOR_CREATE:
                if selector_state is not SelectorState.UNCREATED:
                    raise ValueError("selector may be created only once")
                selector_state = SelectorState.CREATED
            elif payload.stage is ProcessStage.NONBLOCKING_CONFIGURE:
                channel = _TARGET_CHANNEL[payload.target]
                if channel_states[channel] is not ChannelState.ACQUIRED:
                    raise ValueError(
                        "nonblocking configuration requires acquired channel"
                    )
                expected = (
                    _CHANNELS[len(nonblocking)]
                    if len(nonblocking) < len(_CHANNELS)
                    else None
                )
                if channel is not expected:
                    raise ValueError(
                        "nonblocking configuration must extend canonical prefix"
                    )
                nonblocking.append(channel)
                channel_states[channel] = ChannelState.NONBLOCKING
            elif payload.stage is ProcessStage.SELECTOR_REGISTER:
                channel = _TARGET_CHANNEL[payload.target]
                if selector_state is not SelectorState.CREATED:
                    raise ValueError("registration requires a created selector")
                if channel_states[channel] is not ChannelState.NONBLOCKING:
                    raise ValueError("registration requires a nonblocking channel")
                expected = (
                    _CHANNELS[len(registered)]
                    if len(registered) < len(_CHANNELS)
                    else None
                )
                if channel is not expected:
                    raise ValueError("registration must extend canonical prefix")
                registered.append(channel)
                channel_states[channel] = ChannelState.REGISTERED
            elif payload.stage is ProcessStage.SELECTOR_UNREGISTER:
                channel = _TARGET_CHANNEL[payload.target]
                if channel_states[channel] not in {
                    ChannelState.REGISTERED,
                    ChannelState.EOF,
                }:
                    raise ValueError("unregister requires a registered channel")
                expected = (
                    _CHANNELS[len(unregistered)]
                    if len(unregistered) < len(_CHANNELS)
                    else None
                )
                if channel is not expected:
                    raise ValueError("unregister must extend canonical prefix")
                unregistered.append(channel)
                channel_states[channel] = ChannelState.UNREGISTERED
            elif payload.stage is ProcessStage.CLOSE:
                if payload.target is ProcessTarget.SELECTOR:
                    if selector_state is not SelectorState.CREATED:
                        raise ValueError("selector close requires created selector")
                    if any(
                        state in {ChannelState.REGISTERED, ChannelState.EOF}
                        for state in channel_states.values()
                    ):
                        raise ValueError("selector close requires unregister traversal")
                    selector_state = SelectorState.CLOSED_CONFIRMED
        elif isinstance(payload, CloseAttempt):
            channel = _TARGET_CHANNEL[payload.target]
            if channel_states[channel] is ChannelState.UNACQUIRED:
                raise ValueError("close attempt requires acquired descriptor")
            if (
                payload.outcome is OperationOutcome.SUCCEEDED
                and channel in registered
                and channel not in unregistered
            ):
                record_derived_failure(
                    event,
                    stage=ProcessStage.SELECTOR_UNREGISTER,
                    target=payload.target,
                    kind=FailureKind.PROTOCOL,
                    mechanism_errno=None,
                    causal_discriminator=(
                        "registered_channel_closed_without_unregister",
                    ),
                )
            if payload.attempt_ordinal != close_attempts[channel] + 1:
                raise ValueError("close attempt ordinal must be consecutive")
            if close_attempts[channel] and (
                close_dispositions[channel] is not CloseDisposition.OPEN_RETRYABLE
            ):
                raise ValueError("only EINTR open close state permits another attempt")
            close_dispositions[channel] = payload.disposition
            close_attempts[channel] = payload.attempt_ordinal
            channel_states[channel] = _channel_state_after_close(payload.disposition)
            if payload.outcome is OperationOutcome.FAILED:
                record_derived_failure(
                    event=event,
                    stage=ProcessStage.CLOSE,
                    target=payload.target,
                    kind=payload.failure_kind,
                    mechanism_errno=payload.mechanism_errno,
                    close_disposition=payload.disposition,
                    supplied_role=payload.failure_role,
                )

    if retry_pending is not None:
        raise ValueError("retryable attempt lacks RetryObserved")
    if successful_select_pending:
        raise ValueError("successful select lacks ReadyBatch")
    if successful_read_pending is not None:
        raise ValueError("successful read lacks bytes or EOF")
    eof_prefix = tuple(channel for channel in _CHANNELS if channel in eof_seen)
    can_project = (
        tuple(acquired) == _CHANNELS
        and tuple(nonblocking) == _CHANNELS
        and tuple(registered) == _CHANNELS
        and tuple(unregistered) == _CHANNELS
        and eof_seen == set(_CHANNELS)
        and process_state is ProcessState.STARTED
        and child_pid is not None
        and process_group_id is not None
        and pre_root_observation is not None
        and pre_root_observation.disposition is RootObservationDisposition.MATCHED
        and post_root_observation is not None
        and post_root_observation.disposition is RootObservationDisposition.MATCHED
        and handoff_state is HandoffState.CONFIRMED
        and acquired_output[Channel.STATUS] == PROCESS_HELPER_PRE_EXEC_FRAME
        and retained[Channel.STATUS] == PROCESS_HELPER_PRE_EXEC_FRAME
        and all(
            len(acquired_output[channel]) == len(retained[channel])
            for channel in Channel
        )
        and exit_state is ExitState.OBSERVED
        and returncode == 0
        and reap_disposition is ReapDisposition.REAPED
        and selector_state is SelectorState.CLOSED_CONFIRMED
        and all(
            disposition is CloseDisposition.CONFIRMED
            for disposition in close_dispositions.values()
        )
        and post_disposition is PostDisposition.MATCHED
        and finalization_state is FinalizationState.COMPLETE
        and first_primary is None
        and not recurrence_signatures
    )
    return ProcessDerivedState(
        acquired_prefix=tuple(acquired),
        nonblocking_prefix=tuple(nonblocking),
        registered_prefix=tuple(registered),
        unregistered_prefix=tuple(unregistered),
        eof_prefix=eof_prefix,
        status_acquired=acquired_output[Channel.STATUS],
        stdout_acquired=acquired_output[Channel.STDOUT],
        stderr_acquired=acquired_output[Channel.STDERR],
        status_retained=retained[Channel.STATUS],
        stdout_retained=retained[Channel.STDOUT],
        stderr_retained=retained[Channel.STDERR],
        status_bytes_observed=observed[Channel.STATUS],
        stdout_bytes_observed=observed[Channel.STDOUT],
        stderr_bytes_observed=observed[Channel.STDERR],
        process_state=process_state,
        child_pid=child_pid,
        process_group_id=process_group_id,
        pre_root_observation=pre_root_observation,
        post_root_observation=post_root_observation,
        timeout_observation=timeout_observation,
        handoff_state=handoff_state,
        exit_state=exit_state,
        returncode=returncode,
        termination_signal=termination_signal,
        reap_disposition=reap_disposition,
        selector_state=selector_state,
        status_state=channel_states[Channel.STATUS],
        stdout_state=channel_states[Channel.STDOUT],
        stderr_state=channel_states[Channel.STDERR],
        status_close_disposition=close_dispositions[Channel.STATUS],
        stdout_close_disposition=close_dispositions[Channel.STDOUT],
        stderr_close_disposition=close_dispositions[Channel.STDERR],
        status_close_attempts=close_attempts[Channel.STATUS],
        stdout_close_attempts=close_attempts[Channel.STDOUT],
        stderr_close_attempts=close_attempts[Channel.STDERR],
        post_disposition=post_disposition,
        finalization_state=finalization_state,
        main_work=main_work,
        finalize_work=finalize_work,
        first_primary=first_primary,
        finalize_indices=tuple(finalize_indices),
        failure_recurrence_signatures=tuple(recurrence_signatures),
        failure_occurrences=tuple(failure_occurrences),
        retry_counts=tuple(
            RetryCount(stage, target, kind, count)
            for (stage, target, kind), count in sorted(
                retry_counts.items(),
                key=lambda item: (
                    _STAGE_ORDER[item[0][0]],
                    _TARGET_ORDER[item[0][1]],
                    _RETRY_ORDER[item[0][2]],
                ),
            )
        ),
        can_project_success=can_project,
        deadline_binding=deadline_binding,
        deadline_refusal=deadline_refusal,
    )


@dataclass(frozen=True)
class ProcessReceiptV3:
    schema_version: str
    subject: ProcessCommandSubject
    command_subject_hash: str
    invocation: MaterializedInvocation
    retry_contract_hash: str
    reducer_identity: str
    replay_identity: str
    events: tuple[ProcessLifecycleEvent, ...]
    derived_state: ProcessDerivedState
    operational_only: bool
    scientific_authority: bool
    promotion_authority: bool
    receipt_hash: str

    def __post_init__(self) -> None:
        if type(self.schema_version) is not str:
            raise ValueError("schema_version must be an exact string")
        if type(self.subject) is not ProcessCommandSubject:
            raise ValueError("subject must be an exact ProcessCommandSubject")
        _require_hash(self.command_subject_hash, "command_subject_hash")
        if type(self.invocation) is not MaterializedInvocation:
            raise ValueError("invocation must be an exact MaterializedInvocation")
        _require_hash(self.retry_contract_hash, "retry_contract_hash")
        _require_hash(self.reducer_identity, "reducer_identity")
        _require_hash(self.replay_identity, "replay_identity")
        _require_exact_tuple(self.events, "events")
        if type(self.derived_state) is not ProcessDerivedState:
            raise ValueError("derived_state must be an exact ProcessDerivedState")
        if type(self.operational_only) is not bool:
            raise ValueError("operational_only must be an exact bool")
        if type(self.scientific_authority) is not bool:
            raise ValueError("scientific_authority must be an exact bool")
        if type(self.promotion_authority) is not bool:
            raise ValueError("promotion_authority must be an exact bool")
        _require_hash(self.receipt_hash, "receipt_hash")


def _validate_process_receipt_graph(receipt: object) -> None:
    if type(receipt) is not ProcessReceiptV3:
        raise ValueError("receipt must be an exact ProcessReceiptV3")
    _require_stable_constructor_replay(receipt, ProcessReceiptV3, "receipt")
    _validate_process_command_subject(receipt.subject)
    _validate_materialized_invocation(receipt.invocation)
    _require_exact_tuple(receipt.events, "receipt.events")
    for event in receipt.events:
        _validate_process_lifecycle_event(event)


@dataclass(frozen=True)
class ProcessReplayVerification:
    status: ReplayStatus
    replayed_state: ProcessDerivedState | None
    computed_receipt_hash: str | None

    @property
    def valid(self) -> bool:
        return self.status is ReplayStatus.VERIFIED


@dataclass(frozen=True)
class ProcessReceiptV2Cutover:
    source_schema_version: str
    target_schema_version: str
    source_receipt_hash: str
    disposition: LegacyCutoverDisposition
    limitation: LegacyCutoverLimitation


def cutover_process_receipt_v2(source_receipt_hash: str) -> ProcessReceiptV2Cutover:
    _require_hash(source_receipt_hash, "source_receipt_hash")
    return ProcessReceiptV2Cutover(
        PROCESS_RECEIPT_V2_SCHEMA_VERSION,
        PROCESS_RECEIPT_V3_SCHEMA_VERSION,
        source_receipt_hash,
        LegacyCutoverDisposition.CANNOT_MIGRATE,
        LegacyCutoverLimitation.V3_LIFECYCLE_INFORMATION_ABSENT,
    )


def _receipt_hash_for(
    *,
    schema_version: str,
    subject: ProcessCommandSubject,
    command_subject_hash: str,
    invocation: MaterializedInvocation,
    retry_contract_hash: str,
    reducer_identity: str,
    replay_identity: str,
    events: tuple[ProcessLifecycleEvent, ...],
    derived_state: ProcessDerivedState,
    operational_only: bool,
    scientific_authority: bool,
    promotion_authority: bool,
) -> str:
    return canonical_digest(
        {
            "schema_version": schema_version,
            "subject": _command_subject_payload(subject),
            "command_subject_hash": command_subject_hash,
            "invocation": _invocation_payload(invocation),
            "invocation_occurrence_id": invocation.invocation_occurrence_id,
            "retry_contract_hash": retry_contract_hash,
            "reducer_identity": reducer_identity,
            "replay_identity": replay_identity,
            "events": [_event_envelope_payload(event) for event in events],
            "derived_state": _derived_payload(derived_state),
            "operational_only": operational_only,
            "scientific_authority": scientific_authority,
            "promotion_authority": promotion_authority,
        },
        domain=PROCESS_RECEIPT_V3_SCHEMA_VERSION,
    )


def _uses_strict_terminal_deadline_prefix(
    events: tuple[ProcessLifecycleEvent, ...],
) -> bool:
    if len(events) != 1 or type(events[0]) is not ProcessLifecycleEvent:
        return False
    payload = events[0].payload
    if type(payload) is DeadlineRefusal:
        return True
    return (
        type(payload) is DeadlineBinding
        and payload.start_admission_state is StartAdmissionState.DENIED_EXPIRED
    )


def _receipt_identity_pair(
    events: tuple[ProcessLifecycleEvent, ...],
) -> tuple[str, str]:
    if _uses_strict_terminal_deadline_prefix(events):
        return (
            PROCESS_RECEIPT_STRICT_DEADLINE_REDUCER_IDENTITY,
            PROCESS_RECEIPT_STRICT_DEADLINE_REPLAY_IDENTITY,
        )
    return (
        PROCESS_RECEIPT_LEGACY_REDUCER_IDENTITY,
        PROCESS_RECEIPT_LEGACY_REPLAY_IDENTITY,
    )


def _strict_terminal_prefix_matches_invocation(
    invocation: MaterializedInvocation,
    events: tuple[ProcessLifecycleEvent, ...],
) -> bool:
    if not _uses_strict_terminal_deadline_prefix(events):
        return True
    payload = events[0].payload
    assert isinstance(payload, (DeadlineBinding, DeadlineRefusal))
    return (
        invocation.strict_deadline_contract_identity
        == PROCESS_STRICT_DEADLINE_CONTRACT_IDENTITY
        and invocation.clock_domain_occurrence_id == payload.clock_domain_occurrence_id
        and invocation.select_timeout_contract_hash
        == PROCESS_SELECT_TIMEOUT_CONTRACT.select_timeout_contract_hash
        and invocation.invocation_occurrence_id == payload.invocation_occurrence_id
    )


def build_process_receipt(
    subject: ProcessCommandSubject,
    invocation: MaterializedInvocation,
    events: tuple[ProcessLifecycleEvent, ...],
) -> ProcessReceiptV3:
    _validate_process_command_subject(subject)
    _validate_materialized_invocation(invocation)
    if invocation.command_subject_hash != subject.command_subject_hash:
        raise ValueError("materialized invocation is bound to another command subject")
    state = reduce_process_events(
        subject,
        events,
        invocation_occurrence_id=invocation.invocation_occurrence_id,
    )
    if not _strict_terminal_prefix_matches_invocation(invocation, events):
        raise ValueError(
            "strict deadline prefix does not match materialized invocation"
        )
    reducer_identity, replay_identity = _receipt_identity_pair(events)
    receipt_hash = _receipt_hash_for(
        schema_version=PROCESS_RECEIPT_V3_SCHEMA_VERSION,
        subject=subject,
        command_subject_hash=subject.command_subject_hash,
        invocation=invocation,
        retry_contract_hash=subject.retry_contract.retry_contract_hash,
        reducer_identity=reducer_identity,
        replay_identity=replay_identity,
        events=events,
        derived_state=state,
        operational_only=True,
        scientific_authority=False,
        promotion_authority=False,
    )
    return ProcessReceiptV3(
        PROCESS_RECEIPT_V3_SCHEMA_VERSION,
        subject,
        subject.command_subject_hash,
        invocation,
        subject.retry_contract.retry_contract_hash,
        reducer_identity,
        replay_identity,
        events,
        state,
        True,
        False,
        False,
        receipt_hash,
    )


def verify_process_receipt(
    receipt: ProcessReceiptV3,
    *,
    expected_receipt_hash: str | None = None,
    expected_retry_contract_hash: str | None = None,
) -> ProcessReplayVerification:
    if type(receipt) is not ProcessReceiptV3:
        return ProcessReplayVerification(ReplayStatus.SCHEMA_MISMATCH, None, None)
    try:
        _validate_process_receipt_graph(receipt)
    except ValueError:
        return ProcessReplayVerification(ReplayStatus.SCHEMA_MISMATCH, None, None)
    if receipt.schema_version != PROCESS_RECEIPT_V3_SCHEMA_VERSION:
        return ProcessReplayVerification(ReplayStatus.SCHEMA_MISMATCH, None, None)
    if (
        receipt.operational_only is not True
        or receipt.scientific_authority is not False
        or receipt.promotion_authority is not False
    ):
        return ProcessReplayVerification(ReplayStatus.AUTHORITY_VIOLATION, None, None)
    if receipt.command_subject_hash != receipt.subject.command_subject_hash:
        return ProcessReplayVerification(
            ReplayStatus.COMMAND_SUBJECT_MISMATCH, None, None
        )
    expected_reducer_identity, expected_replay_identity = _receipt_identity_pair(
        receipt.events
    )
    if receipt.reducer_identity != expected_reducer_identity:
        return ProcessReplayVerification(
            ReplayStatus.REDUCER_IDENTITY_MISMATCH, None, None
        )
    if receipt.replay_identity != expected_replay_identity:
        return ProcessReplayVerification(
            ReplayStatus.REPLAY_IDENTITY_MISMATCH, None, None
        )
    if not _strict_terminal_prefix_matches_invocation(
        receipt.invocation, receipt.events
    ):
        return ProcessReplayVerification(ReplayStatus.INVOCATION_MISMATCH, None, None)
    if (
        receipt.invocation.command_subject_hash != receipt.command_subject_hash
        or receipt.invocation.invocation_occurrence_id
        != canonical_digest(
            _invocation_payload(receipt.invocation),
            domain=_INVOCATION_OCCURRENCE_DOMAIN,
        )
    ):
        return ProcessReplayVerification(ReplayStatus.INVOCATION_MISMATCH, None, None)
    if (
        receipt.retry_contract_hash
        != receipt.subject.retry_contract.retry_contract_hash
    ):
        return ProcessReplayVerification(
            ReplayStatus.RETRY_CONTRACT_MISMATCH, None, None
        )
    if (
        expected_retry_contract_hash is not None
        and receipt.retry_contract_hash != expected_retry_contract_hash
    ):
        return ProcessReplayVerification(
            ReplayStatus.RETRY_CONTRACT_MISMATCH, None, None
        )
    if any(
        event.work_delta != _required_work_delta(event.payload, event.phase)
        for event in receipt.events
    ):
        return ProcessReplayVerification(ReplayStatus.LIFECYCLE_INVALID, None, None)
    try:
        replayed = reduce_process_events(
            receipt.subject,
            receipt.events,
            invocation_occurrence_id=receipt.invocation.invocation_occurrence_id,
        )
    except ProcessEventChainError:
        return ProcessReplayVerification(ReplayStatus.EVENT_CHAIN_INVALID, None, None)
    except ValueError:
        return ProcessReplayVerification(ReplayStatus.LIFECYCLE_INVALID, None, None)
    if not _exact_graph_equal(replayed, receipt.derived_state):
        return ProcessReplayVerification(
            ReplayStatus.DERIVATION_MISMATCH, replayed, None
        )
    computed = _receipt_hash_for(
        schema_version=receipt.schema_version,
        subject=receipt.subject,
        command_subject_hash=receipt.command_subject_hash,
        invocation=receipt.invocation,
        retry_contract_hash=receipt.retry_contract_hash,
        reducer_identity=receipt.reducer_identity,
        replay_identity=receipt.replay_identity,
        events=receipt.events,
        derived_state=replayed,
        operational_only=receipt.operational_only,
        scientific_authority=receipt.scientific_authority,
        promotion_authority=receipt.promotion_authority,
    )
    if computed != receipt.receipt_hash:
        return ProcessReplayVerification(
            ReplayStatus.RECEIPT_HASH_MISMATCH, replayed, computed
        )
    if expected_receipt_hash is not None and computed != expected_receipt_hash:
        return ProcessReplayVerification(
            ReplayStatus.EXPECTED_RECEIPT_MISMATCH, replayed, computed
        )
    return ProcessReplayVerification(ReplayStatus.VERIFIED, replayed, computed)


def _retry_rule_payload(rule: RetryRule) -> dict[str, object]:
    return {
        "stage": rule.stage.value,
        "target": rule.target.value,
        "kind": rule.kind.value,
        "max_retries": rule.max_retries,
    }


def _work_payload(work: ProcessWorkVector) -> dict[str, int]:
    return {
        name: getattr(work, name) for name in ProcessWorkVector.__dataclass_fields__
    }


def _envelope_payload(envelope: ProcessWorkEnvelope) -> dict[str, object]:
    return {
        "main_limit": _work_payload(envelope.main_limit),
        "finalize_limit": _work_payload(envelope.finalize_limit),
    }


def _command_subject_payload(subject: ProcessCommandSubject) -> dict[str, object]:
    payload: dict[str, object] = {
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
        "work_envelope": _envelope_payload(subject.work_envelope),
        "retry_contract": tuple(
            _retry_rule_payload(rule) for rule in subject.retry_contract.rules
        ),
        "retry_contract_hash": subject.retry_contract.retry_contract_hash,
        "wait_decoder_identity": subject.wait_decoder_identity,
        "wait_supported_signals": subject.wait_supported_signals,
        "wait_nonblocking_option_mask": subject.wait_nonblocking_option_mask,
    }
    if subject.clock_contract_hash is not None:
        payload["clock_contract_hash"] = subject.clock_contract_hash
        payload["deadline_decoder_identity"] = subject.deadline_decoder_identity
    return payload


def _invocation_payload(invocation: MaterializedInvocation) -> dict[str, object]:
    payload: dict[str, object] = {
        "command_subject_hash": invocation.command_subject_hash,
        "host_nonce_hex": invocation.host_nonce.hex(),
        "materialized_argv": invocation.materialized_argv,
        "materialized_environment": invocation.materialized_environment,
    }
    if invocation.strict_deadline_contract_identity is not None:
        payload["strict_deadline_contract_identity"] = (
            invocation.strict_deadline_contract_identity
        )
        payload["clock_domain_occurrence_id"] = invocation.clock_domain_occurrence_id
        payload["select_timeout_contract_hash"] = (
            invocation.select_timeout_contract_hash
        )
    return payload


def _event_payload(payload: ProcessEventPayload) -> dict[str, object]:
    if isinstance(payload, DeadlineBinding):
        return {
            "kind": "DEADLINE_BINDING",
            "invocation_occurrence_id": payload.invocation_occurrence_id,
            "started_monotonic_ns": payload.started_monotonic_ns,
            "requested_timeout_ns": payload.requested_timeout_ns,
            "requested_deadline_monotonic_ns": (
                payload.requested_deadline_monotonic_ns
            ),
            "outer_deadline_monotonic_ns": payload.outer_deadline_monotonic_ns,
            "outer_deadline_commitment_hash": (payload.outer_deadline_commitment_hash),
            "outer_deadline_producer_invocation_occurrence_id": (
                payload.outer_deadline_producer_invocation_occurrence_id
            ),
            "outer_deadline_parent_binding_hash": (
                payload.outer_deadline_parent_binding_hash
            ),
            "effective_deadline_monotonic_ns": (
                payload.effective_deadline_monotonic_ns
            ),
            "winning_source": payload.winning_source.value,
            "start_admission_state": payload.start_admission_state.value,
            "clock_domain_identity": payload.clock_domain_identity,
            "clock_domain_occurrence_id": payload.clock_domain_occurrence_id,
            "clock_contract_hash": payload.clock_contract_hash,
            "deadline_decoder_identity": payload.deadline_decoder_identity,
            "deadline_binding_hash": payload.deadline_binding_hash,
        }
    if isinstance(payload, DeadlineRefusal):
        return {
            "kind": "DEADLINE_REFUSAL",
            "reason": payload.reason.value,
            "invocation_occurrence_id": payload.invocation_occurrence_id,
            "started_monotonic_ns": payload.started_monotonic_ns,
            "requested_timeout_ns": payload.requested_timeout_ns,
            "clock_domain_occurrence_id": payload.clock_domain_occurrence_id,
            "clock_contract_hash": payload.clock_contract_hash,
            "deadline_decoder_identity": payload.deadline_decoder_identity,
            "deadline_refusal_hash": payload.deadline_refusal_hash,
        }
    if isinstance(payload, DeadlineAdmission):
        select_argument = payload.select_call_argument
        return {
            "kind": "DEADLINE_ADMISSION",
            "phase": payload.phase.value,
            "invocation_occurrence_id": payload.invocation_occurrence_id,
            "deadline_binding_hash": payload.deadline_binding_hash,
            "child_occurrence_id": payload.child_occurrence_id,
            "clock_domain_occurrence_id": payload.clock_domain_occurrence_id,
            "stage": payload.stage.value,
            "target": payload.target.value,
            "attempt_ordinal": payload.attempt_ordinal,
            "admission_event_index": payload.admission_event_index,
            "admission_previous_event_hash": payload.admission_previous_event_hash,
            "deadline_monotonic_ns": payload.deadline_monotonic_ns,
            "observed_monotonic_ns": payload.observed_monotonic_ns,
            "remaining_ns": payload.remaining_ns,
            "crossed": payload.crossed,
            "select_call_argument": (
                {
                    "effect_occurrence_id": select_argument.effect_occurrence_id,
                    "remaining_ns": select_argument.remaining_ns,
                    "timeout_argument_float64_bits": (
                        select_argument.timeout_argument_float64_bits
                    ),
                    "semantic_requested_wait_ns": (
                        select_argument.semantic_requested_wait_ns
                    ),
                    "select_timeout_contract_hash": (
                        select_argument.select_timeout_contract_hash
                    ),
                    "select_call_argument_hash": (
                        select_argument.select_call_argument_hash
                    ),
                }
                if select_argument is not None
                else None
            ),
            "effect_occurrence_id": payload.effect_occurrence_id,
            "deadline_admission_hash": payload.deadline_admission_hash,
        }
    if isinstance(payload, DeadlineCompletion):
        return {
            "kind": "DEADLINE_COMPLETION",
            "phase": payload.phase.value,
            "effect_occurrence_id": payload.effect_occurrence_id,
            "deadline_binding_hash": payload.deadline_binding_hash,
            "child_occurrence_id": payload.child_occurrence_id,
            "clock_domain_occurrence_id": payload.clock_domain_occurrence_id,
            "completion_event_index": payload.completion_event_index,
            "completion_previous_event_hash": (payload.completion_previous_event_hash),
            "deadline_monotonic_ns": payload.deadline_monotonic_ns,
            "observed_monotonic_ns": payload.observed_monotonic_ns,
            "remaining_ns": payload.remaining_ns,
            "crossed": payload.crossed,
            "deadline_completion_hash": payload.deadline_completion_hash,
        }
    if isinstance(payload, ProcessStartCompletion):
        return {
            "kind": "PROCESS_START_COMPLETION",
            "invocation_occurrence_id": payload.invocation_occurrence_id,
            "deadline_binding_hash": payload.deadline_binding_hash,
            "child_occurrence_id": payload.child_occurrence_id,
            "clock_domain_occurrence_id": payload.clock_domain_occurrence_id,
            "completion_event_index": payload.completion_event_index,
            "completion_previous_event_hash": (payload.completion_previous_event_hash),
            "deadline_monotonic_ns": payload.deadline_monotonic_ns,
            "observed_monotonic_ns": payload.observed_monotonic_ns,
            "remaining_ns": payload.remaining_ns,
            "crossed": payload.crossed,
            "process_start_completion_hash": (payload.process_start_completion_hash),
        }
    if isinstance(payload, DescriptorAcquired):
        return {"kind": "DESCRIPTOR_ACQUIRED", "channel": payload.channel.value}
    if isinstance(payload, ChildIdentityBound):
        return {
            "kind": "CHILD_IDENTITY_BOUND",
            "child_pid": payload.child_pid,
            "process_group_id": payload.process_group_id,
            "deadline_monotonic_ns": payload.deadline_monotonic_ns,
        }
    if isinstance(payload, RootIdentityObservation):
        return {
            "kind": "ROOT_IDENTITY_OBSERVATION",
            "stage": (
                ProcessStage.POST.value
                if payload.phase is RootObservationPhase.POST
                else "PRE"
            ),
            "phase": payload.phase.value,
            "disposition": payload.disposition.value,
            "configured_device": payload.configured_device,
            "configured_inode": payload.configured_inode,
            "descriptor_device": payload.descriptor_device,
            "descriptor_inode": payload.descriptor_inode,
            "mechanism_errno": payload.mechanism_errno,
        }
    if isinstance(payload, ReadyBatch):
        value: dict[str, object] = {
            "kind": "READY_BATCH",
            "channels": tuple(channel.value for channel in payload.channels),
        }
        if payload.effect_occurrence_id is not None:
            value["effect_occurrence_id"] = payload.effect_occurrence_id
        return value
    if isinstance(payload, EmptyReadyObserved):
        return {
            "kind": "EMPTY_READY_OBSERVED",
            "effect_occurrence_id": payload.effect_occurrence_id,
        }
    if isinstance(payload, BytesObserved):
        value = {
            "kind": "BYTES_OBSERVED",
            "channel": payload.channel.value,
            "acquired_bytes_hex": payload.acquired_bytes.hex(),
            "retained_prefix_delta_hex": payload.retained_prefix_delta.hex(),
        }
        if payload.effect_occurrence_id is not None:
            value["effect_occurrence_id"] = payload.effect_occurrence_id
        return value
    if isinstance(payload, ChannelEof):
        value = {"kind": "CHANNEL_EOF", "channel": payload.channel.value}
        if payload.effect_occurrence_id is not None:
            value["effect_occurrence_id"] = payload.effect_occurrence_id
        return value
    if isinstance(payload, HandoffTransition):
        return {"kind": "HANDOFF_TRANSITION", "state": payload.state.value}
    if isinstance(payload, ExitObserved):
        return {"kind": "EXIT_OBSERVED", "returncode": payload.returncode}
    if isinstance(payload, ReapObservation):
        return {
            "kind": "REAP_OBSERVATION",
            "disposition": payload.disposition.value,
        }
    if isinstance(payload, WaitObservation):
        return {
            "kind": "WAIT_OBSERVATION",
            "stage": ProcessStage.WAIT.value,
            "target": ProcessTarget.PROCESS.value,
            "disposition": payload.disposition.value,
            "requested_child_pid": payload.requested_child_pid,
            "options": payload.options,
            "returned_pid": payload.returned_pid,
            "raw_wait_status": payload.raw_wait_status,
            "mechanism_errno": payload.mechanism_errno,
            "mode": payload.mode.value if payload.mode is not None else None,
            "status_kind": (
                payload.status_kind.value if payload.status_kind is not None else None
            ),
            "status_provenance": (
                payload.status_provenance.value
                if payload.status_provenance is not None
                else None
            ),
            "exit_code": payload.exit_code,
            "status_signal": payload.status_signal,
            "decoder_identity": payload.decoder_identity,
        }
    if isinstance(payload, SignalAttempt):
        return {
            "kind": "SIGNAL_ATTEMPT",
            "stage": ProcessStage.TERMINATE.value,
            "target": payload.target.value,
            "numeric_signal": payload.numeric_signal,
            "child_pid": payload.child_pid,
            "process_group_id": payload.process_group_id,
            "outcome": payload.outcome.value,
            "mechanism_errno": payload.mechanism_errno,
        }
    if isinstance(payload, TimeoutObservation):
        return {
            "kind": "TIMEOUT_OBSERVATION",
            "deadline_monotonic_ns": payload.deadline_monotonic_ns,
            "observed_monotonic_ns": payload.observed_monotonic_ns,
            "crossed": payload.crossed,
            "handoff_state": payload.handoff_state.value,
        }
    if isinstance(payload, RetryObserved):
        value = {
            "kind": "RETRY_OBSERVED",
            "stage": payload.stage.value,
            "target": payload.target.value,
            "retry_kind": payload.kind.value,
            "ordinal": payload.ordinal,
        }
        if payload.effect_occurrence_id is not None:
            value["effect_occurrence_id"] = payload.effect_occurrence_id
        return value
    if isinstance(payload, OperationAttempt):
        value = {
            "kind": "OPERATION_ATTEMPT",
            "stage": payload.stage.value,
            "target": payload.target.value,
            "outcome": payload.outcome.value,
            "failure_kind": payload.failure_kind.value,
            "mechanism_errno": payload.mechanism_errno,
            "failure_role": payload.failure_role.value,
        }
        if payload.effect_occurrence_id is not None:
            value["effect_occurrence_id"] = payload.effect_occurrence_id
            value["attempt_ordinal"] = payload.attempt_ordinal
        return value
    if isinstance(payload, CloseAttempt):
        return {
            "kind": "CLOSE_ATTEMPT",
            "stage": ProcessStage.CLOSE.value,
            "target": payload.target.value,
            "outcome": payload.outcome.value,
            "disposition": payload.disposition.value,
            "attempt_ordinal": payload.attempt_ordinal,
            "failure_kind": payload.failure_kind.value,
            "mechanism_errno": payload.mechanism_errno,
            "failure_role": payload.failure_role.value,
        }
    if isinstance(payload, PostAttempt):
        return {
            "kind": "POST_ATTEMPT",
            "stage": ProcessStage.POST.value,
            "target": ProcessTarget.ROOT.value,
            "disposition": payload.disposition.value,
        }
    if isinstance(payload, FinalizationBegin):
        return {"kind": "FINALIZATION_BEGIN"}
    raise ValueError("unknown process event payload")


def _event_envelope_payload(event: ProcessLifecycleEvent) -> dict[str, object]:
    return {
        "event_index": event.event_index,
        "previous_event_hash": event.previous_event_hash,
        "phase": event.phase.value,
        "payload": _event_payload(event.payload),
        "work_delta": _work_payload(event.work_delta),
        "event_hash": event.event_hash,
    }


def _failure_occurrence_payload(
    occurrence: FailureOccurrence | None,
) -> dict[str, object] | None:
    if occurrence is None:
        return None
    return {
        "event_index": occurrence.event_index,
        "phase": occurrence.phase.value,
        "stage": occurrence.stage.value,
        "target": occurrence.target.value,
        "kind": occurrence.kind.value,
        "mechanism_errno": occurrence.mechanism_errno,
        "role": occurrence.role.value,
        "close_disposition": (
            occurrence.close_disposition.value
            if occurrence.close_disposition is not None
            else None
        ),
        "occurrence_hash": occurrence.occurrence_hash,
    }


def _derived_payload(state: ProcessDerivedState) -> dict[str, object]:
    payload: dict[str, object] = {
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
            _event_payload(state.pre_root_observation)
            if state.pre_root_observation is not None
            else None
        ),
        "post_root_observation": (
            _event_payload(state.post_root_observation)
            if state.post_root_observation is not None
            else None
        ),
        "timeout_observation": (
            _event_payload(state.timeout_observation)
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
        "main_work": _work_payload(state.main_work),
        "finalize_work": _work_payload(state.finalize_work),
        "first_primary": _failure_occurrence_payload(state.first_primary),
        "finalize_indices": state.finalize_indices,
        "failure_recurrence_signatures": state.failure_recurrence_signatures,
        "failure_occurrences": tuple(
            _failure_occurrence_payload(value) for value in state.failure_occurrences
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
    if state.deadline_censored_effect_occurrences:
        payload["deadline_censored_effect_occurrences"] = (
            state.deadline_censored_effect_occurrences
        )
    if state.deadline_binding is not None:
        payload["deadline_binding"] = _event_payload(state.deadline_binding)
    if state.deadline_refusal is not None:
        payload["deadline_refusal"] = _event_payload(state.deadline_refusal)
    return payload


__all__ = [
    "MAX_PROCESS_ARGV_ENTRIES",
    "MAX_PROCESS_EVENT_COUNT",
    "MAX_PROCESS_ID",
    "MAX_PROCESS_MONOTONIC_NS",
    "MAX_PROCESS_OUTPUT_LIMIT",
    "MAX_PROCESS_TEXT_BYTES",
    "PROCESS_HELPER_PRE_EXEC_FRAME",
    "PROCESS_HELPER_STATUS_ACQUISITION_LIMIT",
    "PROCESS_HELPER_STATUS_FRAME_LIMIT",
    "PROCESS_HELPER_STATUS_PROTOCOL_VERSION",
    "PROCESS_HELPER_STATUS_RECEIPT_LIMIT",
    "PROCESS_HOST_NONCE_BYTES",
    "PROCESS_RECEIPT_V2_SCHEMA_VERSION",
    "PROCESS_RECEIPT_V3_SCHEMA_VERSION",
    "PROCESS_RECEIPT_REDUCER_IDENTITY",
    "PROCESS_RECEIPT_REPLAY_IDENTITY",
    "PROCESS_RECEIPT_LEGACY_REDUCER_IDENTITY",
    "PROCESS_RECEIPT_LEGACY_REPLAY_IDENTITY",
    "PROCESS_RECEIPT_STRICT_DEADLINE_REDUCER_IDENTITY",
    "PROCESS_RECEIPT_STRICT_DEADLINE_REPLAY_IDENTITY",
    "PROCESS_CLOCK_CONTRACT",
    "PROCESS_CLOCK_DOMAIN_IDENTITY",
    "PROCESS_CLOCK_DOMAIN_OCCURRENCE",
    "PROCESS_DEADLINE_DECODER_IDENTITY",
    "PROCESS_SELECT_TIMEOUT_CONTRACT",
    "PROCESS_STRICT_DEADLINE_CONTRACT_IDENTITY",
    "PROCESS_WAIT_DECODER_IDENTITY",
    "PROCESS_WAIT_NONBLOCKING_OPTION_MASK",
    "PROCESS_WAIT_STATUS_RAW_MASK",
    "PROCESS_WAIT_SUPPORTED_SIGNALS",
    "PROCESS_WORK_DIMENSIONS",
    "PROCESS_STAGE_TARGET_TABLE",
    "STRICT_AUXILIARY_EVENT_COUNT",
    "STRICT_FINALIZE_EVENTS_PER_ATTEMPT",
    "STRICT_MAIN_EVENTS_PER_EFFECT",
    "BytesObserved",
    "Channel",
    "ChannelEof",
    "ChannelState",
    "ChildIdentityBound",
    "CloseAttempt",
    "CloseDisposition",
    "ClockDomainOccurrence",
    "DeadlineAdmission",
    "DeadlineBinding",
    "DeadlineCompletion",
    "DeadlineEffectPhase",
    "DeadlineRefusal",
    "DeadlineRefusalReason",
    "DeadlineSource",
    "DescriptorAcquired",
    "EintrVisibility",
    "EmptyReadyObserved",
    "EventPhase",
    "ExitObserved",
    "ExitState",
    "FailureKind",
    "FailureOccurrence",
    "FailureRole",
    "FinalizationBegin",
    "FinalizationState",
    "HandoffState",
    "HandoffTransition",
    "LegacyCutoverDisposition",
    "LegacyCutoverLimitation",
    "MaterializedInvocation",
    "OperationAttempt",
    "OperationOutcome",
    "OuterDeadlineCommitment",
    "PostAttempt",
    "PostDisposition",
    "ProcessClockContract",
    "ProcessCommandSubject",
    "ProcessDerivedState",
    "ProcessEventChainError",
    "ProcessLifecycleEvent",
    "ProcessOperation",
    "ProcessReceiptV2Cutover",
    "ProcessReceiptV3",
    "ProcessStartCompletion",
    "ProcessReplayVerification",
    "ProcessStage",
    "ProcessState",
    "ProcessTarget",
    "ProcessWorkEnvelope",
    "ProcessWorkVector",
    "ReadyBatch",
    "ReapDisposition",
    "ReapObservation",
    "ReplayStatus",
    "RetryContract",
    "RetryCount",
    "RetryKind",
    "RetryObserved",
    "RetryRule",
    "RootIdentityObservation",
    "RootObservationDisposition",
    "RootObservationPhase",
    "SelectorState",
    "SelectCallArgument",
    "SelectTimeoutContract",
    "SignalAttempt",
    "TimeoutObservation",
    "StartAdmissionState",
    "StrictDeadlineFeasibility",
    "WaitDisposition",
    "WaitMode",
    "WaitObservation",
    "WaitStatusKind",
    "WaitStatusProvenance",
    "append_process_event",
    "build_process_receipt",
    "cutover_process_receipt_v2",
    "reduce_process_events",
    "verify_process_receipt",
]
