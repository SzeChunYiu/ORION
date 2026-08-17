from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .cases import PublicView


@dataclass(frozen=True)
class ResourceUse:
    """Matched-budget accounting. A system that wins by spending more has not won."""

    wallclock_seconds: float = 0.0
    model_tokens: int = 0
    tool_calls: int = 0
    search_queries: int = 0


@dataclass(frozen=True)
class SystemTrace:
    """One system's answer on one case, in gold-comparable coordinates.

    `abstained` is distinct from a wrong answer: a system that declines is not
    credited with a correct non-reframe on a control.
    """

    case_id: str
    system_id: str
    seed: int
    reframed: bool
    responsibility_family: str = ""
    target_coordinates: tuple[str, ...] = ()
    reopened: tuple[str, ...] = ()
    root_solved: bool = False
    abstained: bool = False
    invariant_violations: tuple[str, ...] = ()
    authority_violations: tuple[str, ...] = ()
    max_recursion_depth: int = 0
    resources: ResourceUse = field(default_factory=ResourceUse)
    notes: str = ""


class SystemUnderTest(Protocol):
    """Every compared system, ORION and baselines alike, is exactly this.

    It receives a `PublicView` — never the case, never the gold. The signature
    is the access-control boundary the protocol's `hidden_labels` policy
    requires, enforced by types rather than by discipline.
    """

    system_id: str

    def run(self, view: PublicView, *, seed: int) -> SystemTrace: ...


__all__ = ["ResourceUse", "SystemTrace", "SystemUnderTest"]
