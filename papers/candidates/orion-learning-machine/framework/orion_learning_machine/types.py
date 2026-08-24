from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping


class Verdict(str, Enum):
    SUCCESS = "success"
    FAIL = "fail"
    UNKNOWN = "unknown"
    UNAUTHORIZED = "unauthorized"
    CANNOT_CHECK = "cannot_check"


@dataclass(frozen=True)
class Provenance:
    donor: str
    source_id: str
    revision: str | None = None
    step: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MechanicSpec:
    mechanic_id: str
    family: str
    description: str
    cost: float = 1.0
    provenance: tuple[Provenance, ...] = ()
    prerequisites: tuple[str, ...] = ()
    # Donor-specific strengths/conditions that must remain visible even after a
    # canonical family is generalized across sources.
    protected_traits: tuple[str, ...] = ()
    # If supplied, two mechanics may share an ID only when this semantic key
    # agrees.  It is deliberately caller-defined until P6 stabilizes its exact
    # contract identity interface.
    compatibility_key: str | None = None
    executor: Callable[[Any], "ExecutionResult"] | None = field(default=None, compare=False, repr=False)


@dataclass(frozen=True)
class ExecutionResult:
    verdict: Verdict
    state: Any
    mechanic_id: str
    evidence: Mapping[str, Any] = field(default_factory=dict)
    provenance: tuple[Provenance, ...] = ()
    reason: str | None = None


@dataclass(frozen=True)
class Experience:
    mechanic_id: str
    features: Mapping[str, float]
    verdict: Verdict
    source_id: str
    donor: str
    trajectory_id: str
    step: int
    evidence: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CompetenceEstimate:
    mechanic_id: str
    p_success: float
    evidence_mass: float
    status: Verdict
    nearest_distance: float


@dataclass(frozen=True)
class CapabilityRoute:
    """Auditable route-or-abstain output that carries no execution authority."""

    selected_mechanic_id: str | None
    status: Verdict
    assessments: tuple[CompetenceEstimate, ...]
    min_success_probability: float
    reason: str
    authorizes_execution: bool = False


@dataclass(frozen=True)
class PlanStep:
    mechanic_id: str
    predicted_success: float
    cost: float
    rationale: str


@dataclass(frozen=True)
class SolverPlan:
    steps: tuple[PlanStep, ...]
    expected_success: float
    expected_cost: float
    status: Verdict
    provenance: tuple[Provenance, ...] = ()


@dataclass(frozen=True)
class MacroSpec:
    macro_id: str
    sequence: tuple[str, ...]
    support: int
    donors: tuple[str, ...]
    source_trajectories: tuple[str, ...]
    source_ids: tuple[str, ...] = ()
    transfer_support: int = 0

@dataclass(frozen=True)
class TransitionObservation:
    mechanic_id: str
    context: Mapping[str, Any]
    effect: str
    donor: str
    source_id: str
    trace_id: str
    verdict: Verdict = Verdict.SUCCESS


@dataclass(frozen=True)
class EmpiricalMechanicContract:
    mechanic_id: str
    support: int
    effect_counts: Mapping[str, int]
    modal_effect: str | None
    donors: tuple[str, ...]
    source_ids: tuple[str, ...]
    context_values: Mapping[str, tuple[str, ...]]

@dataclass(frozen=True)
class PlanExecution:
    verdict: Verdict
    final_state: Any
    results: tuple[ExecutionResult, ...]
    failed_step: int | None = None
    reason: str | None = None
