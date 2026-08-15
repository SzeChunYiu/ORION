from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell, MechanicDimension


class DependencyKind(str, Enum):
    MECHANIC = "MECHANIC"
    PROVIDER = "PROVIDER"
    EVALUATOR = "EVALUATOR"
    DATA = "DATA"
    TOOL = "TOOL"
    SCHEMA = "SCHEMA"
    EVIDENCE = "EVIDENCE"
    RESOURCE = "RESOURCE"
    EXTERNAL_SYSTEM = "EXTERNAL_SYSTEM"


@dataclass(frozen=True)
class DependencyRequirement:
    dependency_id: str
    mechanic_id: str
    kind: DependencyKind
    required: bool
    identity_binding: str
    precondition: str
    failure_propagation: str
    fallback_semantics: str
    integrity_provenance_requirement: str

    def __post_init__(self) -> None:
        required_text = (
            self.dependency_id,
            self.mechanic_id,
            self.identity_binding,
            self.precondition,
            self.failure_propagation,
            self.fallback_semantics,
            self.integrity_provenance_requirement,
        )
        if any(not item.strip() for item in required_text):
            raise ValueError("dependency identity/binding/precondition/failure/fallback/provenance are required")


@dataclass(frozen=True)
class MechanicDependencyPlan:
    mechanic_id: str
    dependencies: tuple[DependencyRequirement, ...]
    step_specific_dependencies_open: bool = True

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip() or not self.dependencies:
            raise ValueError("mechanic dependency plan requires identity and dependencies")
        if any(item.mechanic_id != self.mechanic_id for item in self.dependencies):
            raise ValueError("dependency mechanic mismatch")
        ids = [item.dependency_id for item in self.dependencies]
        if len(set(ids)) != len(ids):
            raise ValueError("dependency ids must be unique")


def _structural_dependency(cell: MechanicCell, dependency_id: str) -> DependencyRequirement:
    return DependencyRequirement(
        dependency_id=dependency_id,
        mechanic_id=cell.mechanic_id,
        kind=DependencyKind.MECHANIC,
        required=True,
        identity_binding="Bind the exact dependency mechanic contract/version and any material implementation identity at run entry.",
        precondition="The dependency exists, its required contract is resolvable, and any required upstream receipt/state is available under compatible scope.",
        failure_propagation="A required dependency failure/block/cannot-check is propagated as a typed prerequisite residual unless an explicit local fallback contract applies.",
        fallback_semantics="No implicit fallback. Any alternative dependency/path must be named, versioned, verified and recorded as a variation.",
        integrity_provenance_requirement="Retain dependency identity, version/content digest, upstream receipt/provenance and supersession lineage where material.",
    )


def _runtime_dependency(cell: MechanicCell) -> DependencyRequirement:
    return DependencyRequirement(
        dependency_id="external:ORION_RUNTIME",
        mechanic_id=cell.mechanic_id,
        kind=DependencyKind.EXTERNAL_SYSTEM,
        required=True,
        identity_binding="Bind the runtime/build/provider deployment manifest by content hash at run entry.",
        precondition="The declared runtime and protected host services are available under the required versions and scope.",
        failure_propagation="Runtime unavailability propagates as a typed blocked or cannot-check residual.",
        fallback_semantics="No implicit fallback; a substitute runtime is a new recorded variation.",
        integrity_provenance_requirement="Retain deployment manifest, build hashes, provider identities and supersession lineage.",
    )


def default_dependency_plan(cell: MechanicCell) -> MechanicDependencyPlan:
    """Bind the structural mechanic dependencies already present in the recursive graph.

    Containment is not a dependency edge. Cells without a known mechanic prerequisite
    receive an external runtime contract rather than a synthetic graph reference.
    Step-specific provider/data/tool dependencies remain open.
    """

    dependencies = (
        tuple(
            _structural_dependency(cell, dependency_id)
            for dependency_id in cell.dependency_ids
        )
        if cell.dependency_ids
        else (_runtime_dependency(cell),)
    )
    return MechanicDependencyPlan(
        mechanic_id=cell.mechanic_id,
        dependencies=dependencies,
        step_specific_dependencies_open=True,
    )


def apply_default_dependency_plan(cell: MechanicCell) -> MechanicCell:
    plan = default_dependency_plan(cell)
    empirical_open = tuple(
        dict.fromkeys(
            cell.empirical_open_coordinates
            + (
                "step-specific provider/evaluator/data/tool/schema/evidence/resource dependencies, version compatibility, fallback validity and failure propagation",
            )
        )
    )
    external_contract_ids = tuple(
        item.dependency_id
        for item in plan.dependencies
        if item.kind is not DependencyKind.MECHANIC
    )
    provisional = tuple(
        dict.fromkeys((*cell.provisional_dimensions, MechanicDimension.DEPENDENCIES))
    )
    return replace(
        cell,
        external_dependency_contract_ids=external_contract_ids,
        empirical_open_coordinates=empirical_open,
        provisional_dimensions=provisional,
    )


def apply_default_dependency_plans(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_dependency_plan(cell) for cell in cells)
