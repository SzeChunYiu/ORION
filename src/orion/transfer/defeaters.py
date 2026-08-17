from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class AuthorityReadiness(str, Enum):
    READY_FOR_EXTERNAL_CHECK = "READY_FOR_EXTERNAL_CHECK"
    BLOCKED = "BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class Defeater:
    defeater_id: str
    severity: float
    unresolved: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.severity <= 1.0:
            raise ValueError("severity must be in [0,1]")


@dataclass(frozen=True)
class EvidenceAction:
    action_id: str
    addresses: frozenset[str]
    success_probability: float
    cost: float
    protected: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.success_probability <= 1.0:
            raise ValueError("success_probability must be in [0,1]")
        if self.cost <= 0:
            raise ValueError("cost must be positive")


class DefeaterPlanner:
    """Plans evidence acquisition; it never grants authority itself."""

    def __init__(self, *, critical_threshold: float = 0.7) -> None:
        if not 0.0 <= critical_threshold <= 1.0:
            raise ValueError("critical_threshold must be in [0,1]")
        self.critical_threshold = critical_threshold

    def _unresolved(self, defeaters: Iterable[Defeater]) -> tuple[Defeater, ...]:
        return tuple(d for d in defeaters if d.unresolved)

    def choose_action(
        self,
        defeaters: Iterable[Defeater],
        actions: Iterable[EvidenceAction],
    ) -> EvidenceAction | None:
        unresolved = {d.defeater_id: d for d in self._unresolved(defeaters)}
        scored: list[tuple[float, str, EvidenceAction]] = []
        for action in actions:
            if not action.protected:
                continue
            benefit = sum(
                unresolved[d].severity * action.success_probability
                for d in action.addresses
                if d in unresolved
            )
            if benefit > 0:
                scored.append((benefit / action.cost, action.action_id, action))
        if not scored:
            return None
        return max(scored, key=lambda item: (item[0], item[1]))[2]

    def readiness(
        self,
        defeaters: Iterable[Defeater],
        actions: Iterable[EvidenceAction],
    ) -> AuthorityReadiness:
        unresolved = self._unresolved(defeaters)
        if not unresolved:
            return AuthorityReadiness.READY_FOR_EXTERNAL_CHECK
        critical = tuple(d for d in unresolved if d.severity >= self.critical_threshold)
        if not critical:
            return AuthorityReadiness.BLOCKED
        action = self.choose_action(critical, actions)
        if action is None:
            return AuthorityReadiness.CANNOT_CHECK
        return AuthorityReadiness.BLOCKED
