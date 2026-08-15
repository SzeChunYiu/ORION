from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell


class ResourceKind(str, Enum):
    WALL_TIME = "WALL_TIME"
    MODEL_TOKENS = "MODEL_TOKENS"
    COMPUTE = "COMPUTE"
    MEMORY = "MEMORY"
    TOOL_CALLS = "TOOL_CALLS"
    DATA_ACCESS = "DATA_ACCESS"
    MONETARY_COST = "MONETARY_COST"
    HUMAN_ATTENTION = "HUMAN_ATTENTION"


@dataclass(frozen=True)
class ResourceCoordinate:
    coordinate_id: str
    mechanic_id: str
    kind: ResourceKind
    unit: str
    accounting_semantics: str
    margin_semantics: str
    exhaustion_semantics: str

    def __post_init__(self) -> None:
        required = (
            self.coordinate_id,
            self.mechanic_id,
            self.unit,
            self.accounting_semantics,
            self.margin_semantics,
            self.exhaustion_semantics,
        )
        if any(not value.strip() for value in required):
            raise ValueError("resource coordinate fields cannot be empty")


@dataclass(frozen=True)
class MechanicResourcePlan:
    mechanic_id: str
    coordinates: tuple[ResourceCoordinate, ...]
    budget_rule: str
    margin_rule: str
    metareasoning_partition_rule: str
    exhaustion_rule: str

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip() or not self.coordinates:
            raise ValueError("resource plan requires identity and resource coordinates")
        if len({item.kind for item in self.coordinates}) != len(self.coordinates):
            raise ValueError("resource kinds must be unique within a mechanic plan")
        for value in (
            self.budget_rule,
            self.margin_rule,
            self.metareasoning_partition_rule,
            self.exhaustion_rule,
        ):
            if not value.strip():
                raise ValueError("resource plan rules cannot be empty")


def default_resource_plan(cell: MechanicCell) -> MechanicResourcePlan:
    def coordinate(
        kind: ResourceKind,
        unit: str,
        accounting: str,
        margin: str,
        exhaustion: str,
    ) -> ResourceCoordinate:
        return ResourceCoordinate(
            coordinate_id=f"resource:{cell.mechanic_id}:{kind.value.lower()}",
            mechanic_id=cell.mechanic_id,
            kind=kind,
            unit=unit,
            accounting_semantics=accounting,
            margin_semantics=margin,
            exhaustion_semantics=exhaustion,
        )

    return MechanicResourcePlan(
        mechanic_id=cell.mechanic_id,
        coordinates=(
            coordinate(
                ResourceKind.WALL_TIME,
                "seconds",
                "Measure elapsed time per attempt/route/action and preserve timeout/cancellation identity.",
                "Reserve explicit schedule slack for uncertainty and recovery rather than budgeting to the nominal limit.",
                "Timeout with material obligations open is resource-bound CANNOT_CHECK, not scientific refutation or saturation.",
            ),
            coordinate(
                ResourceKind.MODEL_TOKENS,
                "tokens",
                "Charge prompt, completion and context-compilation tokens to the producing mechanic/run/provider.",
                "Reserve capacity for mandatory epistemic context, verification and failure reporting before discretionary generation.",
                "If mandatory context cannot fit, fail closed rather than silently truncate it.",
            ),
            coordinate(
                ResourceKind.COMPUTE,
                "compute_units",
                "Account CPU/GPU/accelerator or solver work using the best available provider-specific normalized receipt.",
                "Maintain headroom for verification, recovery and discriminator execution when those are required for a valid terminal.",
                "Compute exhaustion preserves the unresolved state and returns CANNOT_CHECK_RESOURCE_BOUND.",
            ),
            coordinate(
                ResourceKind.MEMORY,
                "bytes",
                "Measure working-state/context/cache memory separately from durable canonical storage.",
                "Keep headroom for mandatory state, receipts and recovery metadata before caches or optional views.",
                "Evict only explicitly recomputable/cache state; mandatory epistemic state must not be silently dropped.",
            ),
            coordinate(
                ResourceKind.TOOL_CALLS,
                "calls",
                "Charge external retrieval, model, verifier and execution calls by provider/action identity.",
                "Reserve calls for independent challenge/verification when the task contract requires them.",
                "Call-budget exhaustion with open material obligations yields CANNOT_CHECK_RESOURCE_BOUND.",
            ),
            coordinate(
                ResourceKind.DATA_ACCESS,
                "items",
                "Account source records/pages/files/rows inspected or transferred, preserving source and query lineage.",
                "Do not consume the entire data budget on one route when the frozen search basis requires heterogeneous coverage.",
                "Data-access limits are reported as coverage censoring and cannot be interpreted as absence of relevant evidence.",
            ),
            coordinate(
                ResourceKind.MONETARY_COST,
                "currency_units",
                "Record externally billed model/tool/compute/data cost at the run/action level when observable.",
                "Keep a declared contingency for required verification/recovery instead of spending the full budget on proposals.",
                "Cost exhaustion blocks further paid actions without upgrading epistemic status.",
            ),
            coordinate(
                ResourceKind.HUMAN_ATTENTION,
                "minutes",
                "Record requested/consumed human review, labeling, approval or intervention time as a scarce external resource.",
                "Reserve human attention for decisions whose authority/ambiguity cannot be safely delegated or mechanically resolved.",
                "Unavailable required human review yields BLOCKED/CANNOT_CHECK rather than an inferred approval.",
            ),
        ),
        budget_rule=(
            "Every execution binds a declared finite resource envelope before high-cost work. "
            "Costs are charged to the mechanic/action that caused them; hidden provider/tool consumption cannot count as free progress."
        ),
        margin_rule=(
            "Budgets carry explicit uncertainty/risk margin. Nominal capacity is not treated as fully spendable when verification, recovery, "
            "mandatory context or protected evaluation still require resources."
        ),
        metareasoning_partition_rule=(
            "Meta-level planning/search-control/diagnosis consumes the same finite resource pool as object-level execution. "
            "Reserve a non-zero object-level execution/verification allocation; when calibrated value-of-computation is unavailable, use a "
            "declared deterministic quota rather than allowing metareasoning to expand without bound."
        ),
        exhaustion_rule=(
            "Open material obligations at any hard resource limit produce CANNOT_CHECK_RESOURCE_BOUND (or BLOCKED when an external mandatory "
            "resource is unavailable). Resource exhaustion never mints bounded saturation, success, or scientific authority."
        ),
    )


def apply_default_resource_plan(cell: MechanicCell) -> MechanicCell:
    plan = default_resource_plan(cell)
    empirical_open = tuple(
        dict.fromkeys(
            cell.empirical_open_coordinates
            + (
                "step-specific resource limits/margins, provider cost model, metareasoning allocation, load sensitivity and value-of-computation calibration",
            )
        )
    )
    return replace(
        cell,
        resource_coordinates=tuple(
            (
                f"{item.coordinate_id}:{item.kind.value}:unit={item.unit}:"
                f"accounting={item.accounting_semantics}:margin={item.margin_semantics}:"
                f"exhaustion={item.exhaustion_semantics}"
            )
            for item in plan.coordinates
        ),
        empirical_open_coordinates=empirical_open,
    )


def apply_default_resource_plans(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_resource_plan(cell) for cell in cells)
