from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell


class InvariantKind(str, Enum):
    AUTHORITY = "AUTHORITY"
    RELATION = "RELATION"
    HISTORY = "HISTORY"
    EVIDENCE = "EVIDENCE"
    SATURATION = "SATURATION"
    REOPEN = "REOPEN"
    EVALUATOR = "EVALUATOR"
    UNCERTAINTY = "UNCERTAINTY"
    EXECUTION = "EXECUTION"
    ROOT_PROGRESS = "ROOT_PROGRESS"
    RESOURCE = "RESOURCE"
    FAILURE_LEARNING = "FAILURE_LEARNING"


@dataclass(frozen=True)
class MechanicInvariant:
    invariant_id: str
    mechanic_id: str
    kind: InvariantKind
    statement: str
    violation_semantics: str
    verification_hook: str

    def __post_init__(self) -> None:
        if any(not item.strip() for item in (self.invariant_id, self.mechanic_id, self.statement, self.violation_semantics, self.verification_hook)):
            raise ValueError("invariant identity/statement/violation/verification hook are required")


@dataclass(frozen=True)
class MechanicInvariantPlan:
    mechanic_id: str
    invariants: tuple[MechanicInvariant, ...]
    step_specific_invariants_open: bool = True

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip() or not self.invariants:
            raise ValueError("invariant plan requires identity/invariants")
        if any(item.mechanic_id != self.mechanic_id for item in self.invariants):
            raise ValueError("invariant mechanic mismatch")


def _inv(cell: MechanicCell, suffix: str, kind: InvariantKind, statement: str, violation: str, hook: str) -> MechanicInvariant:
    return MechanicInvariant(f"invariant:{cell.mechanic_id}:{suffix}", cell.mechanic_id, kind, statement, violation, hook)


def default_invariant_plan(cell: MechanicCell) -> MechanicInvariantPlan:
    return MechanicInvariantPlan(
        mechanic_id=cell.mechanic_id,
        invariants=(
            _inv(cell, "generation-non-authority", InvariantKind.AUTHORITY, "Generated/proposed/model text, telemetry and repeated agreement cannot directly increase scientific authority.", "quarantine attempted authority increase and fail the promotion transition", "authority certificate path audit"),
            _inv(cell, "typed-non-escalation", InvariantKind.RELATION, "A weaker/different relation, representation or measurement cannot silently mint a stronger relation/mechanism claim.", "block the composition/upgrade and open a relation/representation residual", "typed relation/composition audit"),
            _inv(cell, "negative-history-monotone", InvariantKind.HISTORY, "Failed, null, refuted and superseded episodes/results remain addressable after later success.", "reject state mutation that deletes negative-history identity", "history lineage audit"),
            _inv(cell, "missing-evidence-honesty", InvariantKind.EVIDENCE, "Absent mandatory evidence/measurement/verification produces BLOCKED or CANNOT_CHECK rather than an inferred pass.", "fail closed", "verification/prerequisite audit"),
            _inv(cell, "lineage-independence", InvariantKind.EVIDENCE, "Shared evidence ancestry cannot count as independent confirmation or independent-flat credit.", "deduplicate the lineage and reopen independence claim", "evidence provenance graph audit"),
            _inv(cell, "residual-reopening", InvariantKind.REOPEN, "A new material native residual stales the dependent local closure/saturation certificate.", "invalidate dependent closure and reopen the minimal affected fibre", "dependency/reopen audit"),
            _inv(cell, "evaluator-separation", InvariantKind.EVALUATOR, "A candidate/method cannot establish its own improvement by weakening or rewriting its protected evaluator after outcome access.", "block promotion and record authority/governance failure", "candidate/evaluator chronology audit"),
            _inv(cell, "uncertainty-visible", InvariantKind.UNCERTAINTY, "Uncertainty composition/reduction requires visible assumptions; missing assumptions cannot be silently filled.", "retain set/bounds/unknown/cannot-check and open the uncertainty coordinate", "uncertainty-plan audit"),
            _inv(cell, "bounded-closure-honesty", InvariantKind.SATURATION, "Scoped formal/semantic saturation never implies universal completeness or empirical validity.", "reject/qualify the closure claim", "saturation basis and scope audit"),
            _inv(cell, "state-transition-only", InvariantKind.EXECUTION, "Material state changes occur only through declared transitions/events with receipts; hidden mutation is forbidden.", "mark the run unreproducible and open an execution defect", "pre/post state hash + transition lineage"),
            _inv(cell, "root-progress-transport", InvariantKind.ROOT_PROGRESS, "Local metric improvement counts as root progress only with an explicit transport witness under preserved blocking invariants.", "record local-only/false progress and block root-level promotion", "metric/root obligation comparison"),
            _inv(cell, "resource-is-not-closure", InvariantKind.RESOURCE, "Budget exhaustion while material obligations remain open yields CANNOT_CHECK, never bounded closure.", "preserve open obligations and resource-bound terminal", "budget + open-obligation audit"),
            _inv(cell, "failure-no-self-promotion", InvariantKind.FAILURE_LEARNING, "Repeated failure/guard success remains candidate/local evidence until replay, fresh transfer and protected verification bind the exact lesson.", "block reusable/promotion authority and retain candidate status", "experience/guard verification receipt audit"),
        ),
        step_specific_invariants_open=True,
    )


def apply_default_invariant_plan(cell: MechanicCell) -> MechanicCell:
    plan = default_invariant_plan(cell)
    empirical_open = tuple(dict.fromkeys(cell.empirical_open_coordinates + ("step-specific safety/correctness/domain invariants, formal proof obligations and hostile validation",)))
    return replace(cell, invariant_ids=tuple(item.invariant_id for item in plan.invariants), empirical_open_coordinates=empirical_open)


def apply_default_invariant_plans(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_invariant_plan(cell) for cell in cells)
