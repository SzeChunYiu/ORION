"""Revisioned protected authority/support projections.

These are immutable, logical-time projections.  They contain no wall-clock
reads, no global mutable registry and no candidate-controlled promotion path.
Every relying-party decision later binds the exact authority and support
revision it observed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .support import (
    DependencyStatusEvent,
    SupportEvaluation,
    SupportSet,
    evaluate_support,
)
from .transition import canonical_digest


_HEX = frozenset("0123456789abcdef")


def _text(value: str, field: str) -> None:
    if not value.strip():
        raise ValueError(f"{field} is required")


def _sha(value: str, field: str) -> None:
    if len(value) != 64 or any(character not in _HEX for character in value):
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")


class AuthorityObjectKind(str, Enum):
    EVALUATOR = "EVALUATOR"
    POLICY = "POLICY"
    KEY = "KEY"
    TRUST_ROOT = "TRUST_ROOT"


class AuthorityObjectStatus(str, Enum):
    LIVE = "LIVE"
    STALE = "STALE"
    REVOKED = "REVOKED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class AuthorityRegistration:
    registration_id: str
    kind: AuthorityObjectKind
    artifact_hash: str
    epoch_id: str
    metadata_hash: str
    public_key_hex: str = ""

    def __post_init__(self) -> None:
        _text(self.registration_id, "registration_id")
        _sha(self.artifact_hash, "artifact_hash")
        _text(self.epoch_id, "epoch_id")
        _sha(self.metadata_hash, "metadata_hash")
        if self.public_key_hex:
            if len(self.public_key_hex) != 64 or any(
                character not in _HEX for character in self.public_key_hex
            ):
                raise ValueError("public_key_hex must be exactly 32 lowercase-hex bytes")
        if self.kind in {AuthorityObjectKind.EVALUATOR, AuthorityObjectKind.KEY} and not self.public_key_hex:
            raise ValueError("evaluator/key registrations require a public key")
        if self.kind in {AuthorityObjectKind.POLICY, AuthorityObjectKind.TRUST_ROOT} and self.public_key_hex:
            raise ValueError("policy/trust-root registration does not carry a verifier public key")

    @property
    def commitment(self) -> str:
        return canonical_digest(
            {
                "registration_id": self.registration_id,
                "kind": self.kind.value,
                "artifact_hash": self.artifact_hash,
                "epoch_id": self.epoch_id,
                "metadata_hash": self.metadata_hash,
                "public_key_hex": self.public_key_hex,
            },
            domain="orion.authority-registration.v1",
        )


@dataclass(frozen=True)
class AuthorityStatusEvent:
    event_id: str
    registration_id: str
    status: AuthorityObjectStatus
    observed_at: int
    reason: str

    def __post_init__(self) -> None:
        _text(self.event_id, "event_id")
        _text(self.registration_id, "registration_id")
        if self.observed_at < 0:
            raise ValueError("observed_at must be nonnegative")
        _text(self.reason, "reason")


def append_authority_status(
    history: tuple[AuthorityStatusEvent, ...],
    event: AuthorityStatusEvent,
) -> tuple[AuthorityStatusEvent, ...]:
    if any(item.event_id == event.event_id for item in history):
        raise ValueError("authority status event ids must be unique")
    prior = tuple(item for item in history if item.registration_id == event.registration_id)
    if prior and event.observed_at < prior[-1].observed_at:
        raise ValueError("cannot append an authority status older than its current tail")
    return (*history, event)


@dataclass(frozen=True)
class AuthorityState:
    registrations: tuple[AuthorityRegistration, ...]
    status_history: tuple[AuthorityStatusEvent, ...]
    status_time: int

    def __post_init__(self) -> None:
        if self.status_time < 0:
            raise ValueError("status_time must be nonnegative")
        registration_ids = tuple(item.registration_id for item in self.registrations)
        if len(registration_ids) != len(set(registration_ids)):
            raise ValueError("authority registration ids must be unique")
        event_ids = tuple(item.event_id for item in self.status_history)
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("authority status event ids must be unique")
        unknown = {
            item.registration_id for item in self.status_history
        } - set(registration_ids)
        if unknown:
            raise ValueError("authority status history references unknown registrations")

    @property
    def revision(self) -> str:
        return canonical_digest(
            {
                "registrations": [
                    {
                        "registration_id": item.registration_id,
                        "kind": item.kind.value,
                        "artifact_hash": item.artifact_hash,
                        "epoch_id": item.epoch_id,
                        "metadata_hash": item.metadata_hash,
                        "public_key_hex": item.public_key_hex,
                    }
                    for item in sorted(self.registrations, key=lambda item: item.registration_id)
                ],
                "status_history": [
                    {
                        "event_id": item.event_id,
                        "registration_id": item.registration_id,
                        "status": item.status.value,
                        "observed_at": item.observed_at,
                        "reason": item.reason,
                    }
                    for item in self.status_history
                ],
                "status_time": self.status_time,
            },
            domain="orion.authority-state.v1",
        )

    def registration(self, registration_id: str) -> AuthorityRegistration | None:
        return next(
            (item for item in self.registrations if item.registration_id == registration_id),
            None,
        )

    def current_status(self, registration_id: str) -> AuthorityObjectStatus:
        relevant = [
            item
            for item in self.status_history
            if item.registration_id == registration_id and item.observed_at <= self.status_time
        ]
        if not relevant:
            return AuthorityObjectStatus.UNKNOWN
        return max(relevant, key=lambda item: item.observed_at).status

    def live_registration(
        self,
        registration_id: str,
        *,
        kind: AuthorityObjectKind | None = None,
    ) -> AuthorityRegistration | None:
        registration = self.registration(registration_id)
        if registration is None:
            return None
        if kind is not None and registration.kind is not kind:
            return None
        if self.current_status(registration_id) is not AuthorityObjectStatus.LIVE:
            return None
        return registration


@dataclass(frozen=True)
class SupportState:
    support_sets: tuple[SupportSet, ...]
    dependency_history: tuple[DependencyStatusEvent, ...]
    status_time: int

    def __post_init__(self) -> None:
        if self.status_time < 0:
            raise ValueError("status_time must be nonnegative")

    @property
    def revision(self) -> str:
        return canonical_digest(
            {
                "support_sets": [
                    {
                        "support_set_id": item.support_set_id,
                        "dependency_ids": list(item.dependency_ids),
                    }
                    for item in sorted(self.support_sets, key=lambda item: item.support_set_id)
                ],
                "dependency_history": [
                    {
                        "event_id": item.event_id,
                        "dependency_id": item.dependency_id,
                        "status": item.status.value,
                        "observed_at": item.observed_at,
                        "reason": item.reason,
                    }
                    for item in self.dependency_history
                ],
                "status_time": self.status_time,
            },
            domain="orion.support-state.v1",
        )

    @property
    def evaluation(self) -> SupportEvaluation:
        return evaluate_support(
            self.support_sets,
            self.dependency_history,
            status_time=self.status_time,
        )


__all__ = [
    "AuthorityObjectKind",
    "AuthorityObjectStatus",
    "AuthorityRegistration",
    "AuthorityState",
    "AuthorityStatusEvent",
    "SupportState",
    "append_authority_status",
]
