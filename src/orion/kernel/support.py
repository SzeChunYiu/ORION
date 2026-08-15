from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum


class DependencyStatus(str, Enum):
    """Freshness state of one exact, versioned dependency."""

    LIVE = "LIVE"
    STALE = "STALE"
    REVOKED = "REVOKED"
    UNKNOWN = "UNKNOWN"


class SupportVerdict(str, Enum):
    """Verdict licensed by a disjunction of conjunctive support sets."""

    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


class SupportReasonCode(str, Enum):
    """Machine-readable reason why a support set is not live."""

    DEPENDENCY_STALE = "DEPENDENCY_STALE"
    DEPENDENCY_REVOKED = "DEPENDENCY_REVOKED"
    DEPENDENCY_UNKNOWN = "DEPENDENCY_UNKNOWN"
    NO_SUPPORT_SETS = "NO_SUPPORT_SETS"


def _require_identifier(value: str, field_name: str) -> None:
    if not value or value.isspace():
        raise ValueError(f"{field_name} must be nonblank")


@dataclass(frozen=True)
class DependencyStatusEvent:
    """One immutable observation in a dependency's append-only history."""

    event_id: str
    dependency_id: str
    status: DependencyStatus
    observed_at: int
    reason: str

    def __post_init__(self) -> None:
        _require_identifier(self.event_id, "event_id")
        _require_identifier(self.dependency_id, "dependency_id")
        if self.observed_at < 0:
            raise ValueError("observed_at must be nonnegative")
        _require_identifier(self.reason, "reason")


@dataclass(frozen=True)
class SupportSet:
    """One conjunctive warrant; multiple instances are DNF alternatives."""

    support_set_id: str
    dependency_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_identifier(self.support_set_id, "support_set_id")
        if not self.dependency_ids:
            raise ValueError("dependency_ids must not be empty")
        for dependency_id in self.dependency_ids:
            _require_identifier(dependency_id, "dependency_id")
        if len(set(self.dependency_ids)) != len(self.dependency_ids):
            raise ValueError("dependency_ids must be unique within a support set")


@dataclass(frozen=True)
class SupportReason:
    code: SupportReasonCode
    support_set_id: str | None
    dependency_id: str | None
    status: DependencyStatus | None
    message: str


@dataclass(frozen=True)
class SupportEvaluation:
    verdict: SupportVerdict
    status_time: int
    live_support_set_ids: tuple[str, ...]
    invalid_support_set_ids: tuple[str, ...]
    reasons: tuple[SupportReason, ...]


def append_dependency_status(
    history: Sequence[DependencyStatusEvent], event: DependencyStatusEvent
) -> tuple[DependencyStatusEvent, ...]:
    """Return history with one event appended; prior observations are retained."""

    if any(item.event_id == event.event_id for item in history):
        raise ValueError(f"event_id {event.event_id!r} already exists")
    same_dependency = tuple(
        item for item in history if item.dependency_id == event.dependency_id
    )
    if same_dependency and event.observed_at < same_dependency[-1].observed_at:
        raise ValueError("cannot append a dependency status older than its current tail")
    return (*history, event)


def _statuses_at(
    events: Sequence[DependencyStatusEvent], status_time: int
) -> dict[str, DependencyStatus]:
    statuses: dict[str, DependencyStatus] = {}
    timestamps: dict[str, int] = {}
    for event in events:
        if event.observed_at > status_time:
            continue
        previous = timestamps.get(event.dependency_id)
        if previous is None or event.observed_at >= previous:
            statuses[event.dependency_id] = event.status
            timestamps[event.dependency_id] = event.observed_at
    return statuses


def _reason(
    support_set_id: str, dependency_id: str, status: DependencyStatus
) -> SupportReason:
    codes = {
        DependencyStatus.STALE: SupportReasonCode.DEPENDENCY_STALE,
        DependencyStatus.REVOKED: SupportReasonCode.DEPENDENCY_REVOKED,
        DependencyStatus.UNKNOWN: SupportReasonCode.DEPENDENCY_UNKNOWN,
    }
    return SupportReason(
        code=codes[status],
        support_set_id=support_set_id,
        dependency_id=dependency_id,
        status=status,
        message=(
            f"support set {support_set_id!r} depends on {dependency_id!r}, "
            f"which is {status.value} at status time"
        ),
    )


def evaluate_support(
    support_sets: Sequence[SupportSet],
    dependency_history: Sequence[DependencyStatusEvent],
    *,
    status_time: int,
) -> SupportEvaluation:
    """Evaluate a frozen DNF support graph at an explicit logical time.

    Dependencies inside a support set are conjunctive. Support sets are
    alternatives. A revoked dependency demonstrably breaks its conjunction;
    stale, unknown and not-yet-observed dependencies leave it indeterminate.
    The function deliberately has no wall-clock access.
    """

    if status_time < 0:
        raise ValueError("status_time must be nonnegative")
    support_ids = tuple(item.support_set_id for item in support_sets)
    if len(set(support_ids)) != len(support_ids):
        raise ValueError("support_set_id values must be unique")
    event_ids = tuple(item.event_id for item in dependency_history)
    if len(set(event_ids)) != len(event_ids):
        raise ValueError("event_id values must be unique")
    if not support_sets:
        reason = SupportReason(
            code=SupportReasonCode.NO_SUPPORT_SETS,
            support_set_id=None,
            dependency_id=None,
            status=None,
            message="no support sets were supplied",
        )
        return SupportEvaluation(
            verdict=SupportVerdict.CANNOT_CHECK,
            status_time=status_time,
            live_support_set_ids=(),
            invalid_support_set_ids=(),
            reasons=(reason,),
        )

    statuses = _statuses_at(dependency_history, status_time)
    live: list[str] = []
    invalid: list[str] = []
    broken: set[str] = set()
    reasons: list[SupportReason] = []
    for support_set in support_sets:
        dependency_statuses = tuple(
            statuses.get(dependency_id, DependencyStatus.UNKNOWN)
            for dependency_id in support_set.dependency_ids
        )
        if all(status is DependencyStatus.LIVE for status in dependency_statuses):
            live.append(support_set.support_set_id)
            continue

        invalid.append(support_set.support_set_id)
        if DependencyStatus.REVOKED in dependency_statuses:
            broken.add(support_set.support_set_id)
        reasons.extend(
            _reason(support_set.support_set_id, dependency_id, status)
            for dependency_id, status in zip(
                support_set.dependency_ids, dependency_statuses, strict=True
            )
            if status is not DependencyStatus.LIVE
        )

    if live:
        verdict = SupportVerdict.PASS
    elif len(broken) == len(support_sets):
        verdict = SupportVerdict.FAIL
    else:
        verdict = SupportVerdict.CANNOT_CHECK
    return SupportEvaluation(
        verdict=verdict,
        status_time=status_time,
        live_support_set_ids=tuple(live),
        invalid_support_set_ids=tuple(invalid),
        reasons=tuple(reasons),
    )
