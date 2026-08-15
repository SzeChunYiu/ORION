from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MechanicDimension(str, Enum):
    """Audit dimensions that every atomic mechanic must answer or explicitly waive."""

    INPUTS = "INPUTS"
    OUTPUTS = "OUTPUTS"
    HANDOFF = "HANDOFF"
    STATE = "STATE"
    OBSERVABILITY = "OBSERVABILITY"
    ACTIONS = "ACTIONS"
    TRANSITION_MODEL = "TRANSITION_MODEL"
    MATHEMATICS = "MATHEMATICS"
    INVARIANTS = "INVARIANTS"
    OBJECTIVE = "OBJECTIVE"
    METRICS = "METRICS"
    OPTIMIZATION = "OPTIMIZATION"
    UNCERTAINTY = "UNCERTAINTY"
    RESOURCES = "RESOURCES"
    FAILURE = "FAILURE"
    DIAGNOSIS = "DIAGNOSIS"
    STORAGE = "STORAGE"
    PROVENANCE = "PROVENANCE"
    VERIFICATION = "VERIFICATION"
    AUTHORITY_SECURITY = "AUTHORITY_SECURITY"
    ENGINEERING = "ENGINEERING"
    DEPENDENCIES = "DEPENDENCIES"
    REOPEN = "REOPEN"
    SEARCH_COVERAGE = "SEARCH_COVERAGE"
    PARENT_DISCIPLINE = "PARENT_DISCIPLINE"
    SATURATION = "SATURATION"
    EMPIRICAL_OPEN = "EMPIRICAL_OPEN"


class MetricKind(str, Enum):
    QUALITY = "QUALITY"
    COVERAGE = "COVERAGE"
    COST = "COST"
    LATENCY = "LATENCY"
    RELIABILITY = "RELIABILITY"
    UNCERTAINTY = "UNCERTAINTY"
    RESOURCE = "RESOURCE"
    SAFETY = "SAFETY"
    DIAGNOSTIC = "DIAGNOSTIC"


class MetricDirection(str, Enum):
    MAXIMIZE = "MAXIMIZE"
    MINIMIZE = "MINIMIZE"
    TARGET = "TARGET"
    NON_COMPENSATORY_GATE = "NON_COMPENSATORY_GATE"
    OBSERVE_ONLY = "OBSERVE_ONLY"


@dataclass(frozen=True)
class MetricSpec:
    metric_id: str
    description: str
    kind: MetricKind
    direction: MetricDirection
    unit: str
    required_for_handoff: bool = False
    threshold_semantics: str = ""
    uncertainty_semantics: str = ""

    def __post_init__(self) -> None:
        if not self.metric_id.strip() or not self.description.strip() or not self.unit.strip():
            raise ValueError("metric identity, description and unit are required")
        if self.direction in {MetricDirection.TARGET, MetricDirection.NON_COMPENSATORY_GATE} and not self.threshold_semantics.strip():
            raise ValueError("target/gate metrics require threshold semantics")


@dataclass(frozen=True)
class MetricObservation:
    metric_id: str
    value: float | int | str
    unit: str
    evidence_ids: tuple[str, ...] = ()
    uncertainty: float | None = None

    def __post_init__(self) -> None:
        if not self.metric_id.strip() or not self.unit.strip():
            raise ValueError("metric observation identity and unit are required")
        if self.uncertainty is not None and self.uncertainty < 0:
            raise ValueError("metric uncertainty cannot be negative")


@dataclass(frozen=True)
class HandoffField:
    field_id: str
    description: str
    schema_ref: str
    required: bool = True

    def __post_init__(self) -> None:
        if not self.field_id.strip() or not self.description.strip() or not self.schema_ref.strip():
            raise ValueError("handoff field identity, description and schema are required")


@dataclass(frozen=True)
class DimensionWaiver:
    dimension: MechanicDimension
    reason: str

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("dimension waiver requires a reason")


@dataclass(frozen=True)
class MechanicCell:
    """A recursively auditable atomic problem-solving mechanic.

    A cell may be incomplete. Incompleteness is intentional input to the mechanical
    question generator; missing dimensions are never silently treated as satisfied.
    """

    mechanic_id: str
    purpose: str
    scope: str
    input_ids: tuple[str, ...] = ()
    output_ids: tuple[str, ...] = ()
    handoff_fields: tuple[HandoffField, ...] = ()
    state_ids: tuple[str, ...] = ()
    observable_ids: tuple[str, ...] = ()
    action_ids: tuple[str, ...] = ()
    transition_semantics: tuple[str, ...] = ()
    mathematical_semantics: tuple[str, ...] = ()
    invariant_ids: tuple[str, ...] = ()
    constraint_ids: tuple[str, ...] = ()
    objective_ids: tuple[str, ...] = ()
    metrics: tuple[MetricSpec, ...] = ()
    optimization_rules: tuple[str, ...] = ()
    uncertainty_semantics: tuple[str, ...] = ()
    resource_coordinates: tuple[str, ...] = ()
    failure_signatures: tuple[str, ...] = ()
    falsifiers: tuple[str, ...] = ()
    diagnosis_rules: tuple[str, ...] = ()
    storage_contracts: tuple[str, ...] = ()
    provenance_contracts: tuple[str, ...] = ()
    verification_contracts: tuple[str, ...] = ()
    authority_boundaries: tuple[str, ...] = ()
    engineering_contracts: tuple[str, ...] = ()
    dependency_ids: tuple[str, ...] = ()
    child_mechanic_ids: tuple[str, ...] = ()
    reopen_triggers: tuple[str, ...] = ()
    search_coverage_obligations: tuple[str, ...] = ()
    parent_domain_hypotheses: tuple[str, ...] = ()
    saturation_criteria: tuple[str, ...] = ()
    empirical_open_coordinates: tuple[str, ...] = ()
    waivers: tuple[DimensionWaiver, ...] = ()

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip() or not self.purpose.strip() or not self.scope.strip():
            raise ValueError("mechanic identity, purpose and scope are required")
        metric_ids = [item.metric_id for item in self.metrics]
        if len(set(metric_ids)) != len(metric_ids):
            raise ValueError("mechanic metric ids must be unique")
        handoff_ids = [item.field_id for item in self.handoff_fields]
        if len(set(handoff_ids)) != len(handoff_ids):
            raise ValueError("mechanic handoff field ids must be unique")
        waived = [item.dimension for item in self.waivers]
        if len(set(waived)) != len(waived):
            raise ValueError("a mechanic dimension can be waived at most once")
        if self.mechanic_id in self.child_mechanic_ids:
            raise ValueError("a mechanic cannot be its own child")

    @property
    def waived_dimensions(self) -> frozenset[MechanicDimension]:
        return frozenset(item.dimension for item in self.waivers)
