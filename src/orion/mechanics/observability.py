from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell, MechanicDimension


class ObservationClass(str, Enum):
    RUNTIME_TELEMETRY = "RUNTIME_TELEMETRY"
    RESOURCE_MEASURE = "RESOURCE_MEASURE"
    INTERFACE_SIGNAL = "INTERFACE_SIGNAL"
    FAILURE_SIGNAL = "FAILURE_SIGNAL"
    VERIFICATION_SIGNAL = "VERIFICATION_SIGNAL"
    PERFORMANCE_MEASURE = "PERFORMANCE_MEASURE"
    SCIENTIFIC_MEASUREMENT = "SCIENTIFIC_MEASUREMENT"


@dataclass(frozen=True)
class ObservationSpec:
    observation_id: str
    mechanic_id: str
    observation_class: ObservationClass
    quantity_or_measurand: str
    instrument_or_source: str
    unit: str
    collection_trigger: str
    uncertainty_semantics: str
    decision_use: str
    provenance_required: bool = True
    may_create_scientific_authority: bool = False

    def __post_init__(self) -> None:
        required = (
            self.observation_id,
            self.mechanic_id,
            self.quantity_or_measurand,
            self.instrument_or_source,
            self.unit,
            self.collection_trigger,
            self.uncertainty_semantics,
            self.decision_use,
        )
        if any(not item.strip() for item in required):
            raise ValueError(
                "observation identity, measurand/source/unit/trigger/uncertainty/use are required"
            )
        if (
            self.observation_class is not ObservationClass.SCIENTIFIC_MEASUREMENT
            and self.may_create_scientific_authority
        ):
            raise ValueError(
                "runtime/interface/performance telemetry cannot directly create scientific authority"
            )


@dataclass(frozen=True)
class MechanicObservationPlan:
    mechanic_id: str
    observations: tuple[ObservationSpec, ...]
    step_specific_measurement_open: bool = True

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip() or not self.observations:
            raise ValueError(
                "mechanic observation plan requires identity and observations"
            )
        if any(item.mechanic_id != self.mechanic_id for item in self.observations):
            raise ValueError("observation mechanic mismatch")
        ids = [item.observation_id for item in self.observations]
        if len(set(ids)) != len(ids):
            raise ValueError("observation ids must be unique")


def _observation(
    cell: MechanicCell,
    suffix: str,
    observation_class: ObservationClass,
    quantity: str,
    source: str,
    unit: str,
    trigger: str,
    uncertainty: str,
    use: str,
) -> ObservationSpec:
    return ObservationSpec(
        observation_id=f"observe:{cell.mechanic_id}:{suffix}",
        mechanic_id=cell.mechanic_id,
        observation_class=observation_class,
        quantity_or_measurand=quantity,
        instrument_or_source=source,
        unit=unit,
        collection_trigger=trigger,
        uncertainty_semantics=uncertainty,
        decision_use=use,
        may_create_scientific_authority=False,
    )


def default_observation_plan(cell: MechanicCell) -> MechanicObservationPlan:
    """Universal runtime observability baseline.

    These observations make execution inspectable. They are not substitutes for the
    mechanic-specific scientific/performance measurands that still require research.
    """

    return MechanicObservationPlan(
        mechanic_id=cell.mechanic_id,
        observations=(
            _observation(
                cell,
                "run-status",
                ObservationClass.RUNTIME_TELEMETRY,
                "declared mechanic execution outcome",
                "MechanicReceipt.status",
                "categorical",
                "at mechanic completion or fail-closed exit",
                "exact software enum; does not quantify scientific truth",
                "route success/partial/failure/blocked/cannot-check behavior and experience recording",
            ),
            _observation(
                cell,
                "latency",
                ObservationClass.RESOURCE_MEASURE,
                "wall-clock execution latency",
                "runtime monotonic clock",
                "s",
                "at mechanic completion",
                "clock resolution and scheduling delay are measurement limitations",
                "resource/performance accounting and regression detection",
            ),
            _observation(
                cell,
                "cost",
                ObservationClass.RESOURCE_MEASURE,
                "declared normalized resource cost",
                "provider/runtime accounting",
                "cost_unit",
                "at mechanic completion",
                "valid only under the active cost model and provider accounting coverage",
                "matched-resource comparison and budget control",
            ),
            _observation(
                cell,
                "residuals",
                ObservationClass.FAILURE_SIGNAL,
                "typed unresolved residual identifiers emitted by the mechanic",
                "MechanicReceipt.residual_ids",
                "count+categorical",
                "on emission and completion",
                "absence of a residual is not proof that no unknown residual exists",
                "recurse, reopen, diagnose and prevent false closure",
            ),
            _observation(
                cell,
                "evidence-lineage",
                ObservationClass.VERIFICATION_SIGNAL,
                "evidence/provenance identifiers touched by the mechanic",
                "MechanicReceipt evidence/provenance fields",
                "identifier_set",
                "on evidence/provenance mutation or completion",
                "identifier presence does not imply evidence sufficiency or independence",
                "trace verification inputs and detect lineage gaps",
            ),
            _observation(
                cell,
                "handoff-presence",
                ObservationClass.INTERFACE_SIGNAL,
                "declared downstream handoff fields actually emitted",
                "MechanicReceipt.handoff_values",
                "field_set",
                "at mechanic completion",
                "schema presence is distinct from semantic correctness or calibration",
                "detect missing interface fields before downstream execution",
            ),
        ),
        step_specific_measurement_open=True,
    )


def apply_default_observation_plan(cell: MechanicCell) -> MechanicCell:
    plan = default_observation_plan(cell)
    empirical_open = cell.empirical_open_coordinates
    if plan.step_specific_measurement_open:
        empirical_open = tuple(
            dict.fromkeys(
                empirical_open
                + (
                    "step-specific performance/scientific measurands, measurement validity, calibration, uncertainty and decision thresholds",
                )
            )
        )
    return replace(
        cell,
        observable_ids=tuple(item.observation_id for item in plan.observations),
        provisional_dimensions=tuple(
            dict.fromkeys(
                (*cell.provisional_dimensions, MechanicDimension.OBSERVABILITY)
            )
        ),
        empirical_open_coordinates=empirical_open,
    )


def apply_default_observation_plans(
    cells: tuple[MechanicCell, ...],
) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_observation_plan(cell) for cell in cells)
