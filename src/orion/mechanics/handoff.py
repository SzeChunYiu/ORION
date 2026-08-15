from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import HandoffField, MechanicCell


class FieldPresence(str, Enum):
    REQUIRED = "REQUIRED"
    OPTIONAL_EXPLICIT = "OPTIONAL_EXPLICIT"


class AuthorityTransport(str, Enum):
    NONE = "NONE"
    EXPLICIT_CERTIFICATE_ONLY = "EXPLICIT_CERTIFICATE_ONLY"


@dataclass(frozen=True)
class HandoffRequirement:
    field_id: str
    description: str
    schema_ref: str
    presence: FieldPresence
    unit_semantics: str
    uncertainty_semantics: str
    provenance_required: bool
    authority_transport: AuthorityTransport

    def __post_init__(self) -> None:
        required = (
            self.field_id,
            self.description,
            self.schema_ref,
            self.unit_semantics,
            self.uncertainty_semantics,
        )
        if any(not item.strip() for item in required):
            raise ValueError("handoff field identity/schema/unit/uncertainty semantics are required")


@dataclass(frozen=True)
class MechanicHandoffPlan:
    mechanic_id: str
    schema_id: str
    schema_version: str
    fields: tuple[HandoffRequirement, ...]
    missing_required_semantics: str
    compatibility_policy: str
    step_specific_payload_open: bool = True

    def __post_init__(self) -> None:
        if any(not item.strip() for item in (self.mechanic_id, self.schema_id, self.schema_version, self.missing_required_semantics, self.compatibility_policy)):
            raise ValueError("handoff plan identity/version/missing/compatibility semantics are required")
        if not self.fields:
            raise ValueError("handoff plan requires fields")
        ids = [item.field_id for item in self.fields]
        if len(set(ids)) != len(ids):
            raise ValueError("handoff requirement ids must be unique")


def _field(
    field_id: str,
    description: str,
    schema_ref: str,
    *,
    required: bool,
    unit_semantics: str = "not-applicable",
    uncertainty_semantics: str = "not-applicable",
    provenance_required: bool = False,
    authority_transport: AuthorityTransport = AuthorityTransport.NONE,
) -> HandoffRequirement:
    return HandoffRequirement(
        field_id=field_id,
        description=description,
        schema_ref=schema_ref,
        presence=FieldPresence.REQUIRED if required else FieldPresence.OPTIONAL_EXPLICIT,
        unit_semantics=unit_semantics,
        uncertainty_semantics=uncertainty_semantics,
        provenance_required=provenance_required,
        authority_transport=authority_transport,
    )


def default_handoff_plan(cell: MechanicCell) -> MechanicHandoffPlan:
    """Universal mechanic-receipt envelope.

    The envelope makes control/provenance fields explicit. It does not define the
    mechanic-specific scientific payload, which remains a child research obligation.
    """

    return MechanicHandoffPlan(
        mechanic_id=cell.mechanic_id,
        schema_id="orion.MechanicReceiptEnvelope",
        schema_version="v0",
        fields=(
            _field("status", "Fail-closed execution status.", "MechanicRunStatus", required=True),
            _field("output_artifact_ids", "Stable identifiers of produced artifacts.", "tuple[str]", required=True, provenance_required=True),
            _field("handoff_values", "Mechanic-specific typed payload keyed by declared field id.", "tuple[(field_id,value)]", required=True, provenance_required=True),
            _field("metric_observations", "Typed metric observations including unit/evidence/uncertainty.", "tuple[MetricObservation]", required=True, unit_semantics="declared per metric", uncertainty_semantics="declared per observation", provenance_required=True),
            _field("residual_ids", "Material/unresolved residuals for downstream diagnosis/reopen.", "tuple[str]", required=True, provenance_required=True),
            _field("evidence_ids", "Evidence identifiers touched by the mechanic; identity alone grants no authority.", "tuple[str]", required=True, provenance_required=True, authority_transport=AuthorityTransport.EXPLICIT_CERTIFICATE_ONLY),
            _field("provenance_ids", "Execution/source/proposal lineage identifiers.", "tuple[str]", required=True, provenance_required=True),
            _field("cost_units", "Normalized resource cost under the active cost model.", "float", required=True, unit_semantics="cost_unit", uncertainty_semantics="valid only under active provider accounting coverage"),
            _field("latency_seconds", "Wall-clock completion latency.", "float", required=True, unit_semantics="s", uncertainty_semantics="clock resolution/scheduling limitations"),
        ),
        missing_required_semantics="A missing required field makes the handoff invalid/blocked; downstream mechanics may not infer the value from prose or defaults.",
        compatibility_policy="Schemas are versioned. Presence semantics are explicit; backward/forward compatibility must be assessed before a producer or consumer version is changed.",
        step_specific_payload_open=True,
    )


def apply_default_handoff_plan(cell: MechanicCell) -> MechanicCell:
    plan = default_handoff_plan(cell)
    fields = tuple(
        HandoffField(
            field_id=item.field_id,
            description=item.description,
            schema_ref=f"{plan.schema_id}/{plan.schema_version}#{item.schema_ref}",
            required=item.presence is FieldPresence.REQUIRED,
        )
        for item in plan.fields
    )
    empirical_open = cell.empirical_open_coordinates
    if plan.step_specific_payload_open:
        empirical_open = tuple(
            dict.fromkeys(
                empirical_open
                + ("step-specific handoff payload fields, schemas, units, uncertainty, compatibility and authority transport",)
            )
        )
    return replace(cell, handoff_fields=fields, empirical_open_coordinates=empirical_open)


def apply_default_handoff_plans(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_handoff_plan(cell) for cell in cells)
