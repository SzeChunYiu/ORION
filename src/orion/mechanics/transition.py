from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell


class TransitionDeterminism(str, Enum):
    DETERMINISTIC = "DETERMINISTIC"
    SET_VALUED = "SET_VALUED"
    STOCHASTIC = "STOCHASTIC"
    EXTERNAL_NONDETERMINISTIC = "EXTERNAL_NONDETERMINISTIC"


class RetrySafety(str, Enum):
    IDEMPOTENT = "IDEMPOTENT"
    RECEIPT_REPLAY_ONLY = "RECEIPT_REPLAY_ONLY"
    SIDE_EFFECT_GUARD_REQUIRED = "SIDE_EFFECT_GUARD_REQUIRED"
    NOT_RETRY_SAFE = "NOT_RETRY_SAFE"


@dataclass(frozen=True)
class TransitionRule:
    rule_id: str
    mechanic_id: str
    source_phase: str
    target_phase: str
    trigger: str
    preconditions: tuple[str, ...]
    postconditions: tuple[str, ...]
    determinism: TransitionDeterminism
    side_effect_semantics: str
    retry_safety: RetrySafety

    def __post_init__(self) -> None:
        required = (
            self.rule_id,
            self.mechanic_id,
            self.source_phase,
            self.target_phase,
            self.trigger,
            self.side_effect_semantics,
        )
        if any(not item.strip() for item in required):
            raise ValueError("transition identity/phases/trigger/side-effect semantics are required")
        if not self.preconditions or not self.postconditions:
            raise ValueError("transition rule requires preconditions and postconditions")


@dataclass(frozen=True)
class MechanicTransitionPlan:
    mechanic_id: str
    rules: tuple[TransitionRule, ...]
    state_relation: str
    step_specific_dynamics_open: bool = True

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip() or not self.rules or not self.state_relation.strip():
            raise ValueError("mechanic transition plan requires identity/rules/state relation")
        if any(item.mechanic_id != self.mechanic_id for item in self.rules):
            raise ValueError("transition rule mechanic mismatch")
        ids = [item.rule_id for item in self.rules]
        if len(set(ids)) != len(ids):
            raise ValueError("transition rule ids must be unique")


def _rule(
    cell: MechanicCell,
    suffix: str,
    source: str,
    target: str,
    trigger: str,
    pre: tuple[str, ...],
    post: tuple[str, ...],
    determinism: TransitionDeterminism,
    side_effects: str,
    retry: RetrySafety,
) -> TransitionRule:
    return TransitionRule(
        rule_id=f"transition:{cell.mechanic_id}:{suffix}",
        mechanic_id=cell.mechanic_id,
        source_phase=source,
        target_phase=target,
        trigger=trigger,
        preconditions=pre,
        postconditions=post,
        determinism=determinism,
        side_effect_semantics=side_effects,
        retry_safety=retry,
    )


def default_transition_plan(cell: MechanicCell) -> MechanicTransitionPlan:
    """Universal fail-closed lifecycle relation; not step-specific scientific dynamics."""

    terminal_post = ("a MechanicReceipt is emitted", "output/post-state identity is bound", "all side effects retain execution provenance")
    return MechanicTransitionPlan(
        mechanic_id=cell.mechanic_id,
        rules=(
            _rule(
                cell,
                "admit",
                "CREATED",
                "READY",
                "validate declared inputs, dependencies, authority and resource preconditions",
                ("input snapshot is bound", "mechanic/dependency versions are bound"),
                ("mandatory preconditions are either satisfied or a fail-closed terminal transition is selected",),
                TransitionDeterminism.DETERMINISTIC,
                "validation is read-only and must not invoke scientific or external side effects",
                RetrySafety.IDEMPOTENT,
            ),
            _rule(
                cell,
                "execute",
                "READY",
                "RUNNING",
                "begin the declared mechanic action",
                ("READY preconditions hold", "run identity is unique"),
                ("working state changes only through declared transitions/events",),
                TransitionDeterminism.EXTERNAL_NONDETERMINISTIC,
                "external/model/tool actions may have side effects only through declared adapters with receipts",
                RetrySafety.SIDE_EFFECT_GUARD_REQUIRED,
            ),
            _rule(cell, "success", "RUNNING", "SUCCEEDED", "verified local completion condition", ("local completion predicate holds",), terminal_post, TransitionDeterminism.SET_VALUED, "no hidden side effects after terminal receipt", RetrySafety.RECEIPT_REPLAY_ONLY),
            _rule(cell, "partial", "RUNNING", "PARTIAL", "partial/false-progress condition", ("some local result exists", "one or more required obligations remain open or root transport is unlicensed"), terminal_post, TransitionDeterminism.SET_VALUED, "partial output is explicitly typed and cannot masquerade as success", RetrySafety.RECEIPT_REPLAY_ONLY),
            _rule(cell, "failed", "RUNNING", "FAILED", "failure-mode detector fires", ("a registered failure/invariant/expectation violation is observed",), terminal_post, TransitionDeterminism.SET_VALUED, "failed output is quarantined from authority promotion", RetrySafety.RECEIPT_REPLAY_ONLY),
            _rule(cell, "blocked", "CREATED|READY|RUNNING", "BLOCKED", "mandatory prerequisite cannot be satisfied", ("a declared blocking prerequisite/dependency is absent or invalid",), terminal_post, TransitionDeterminism.SET_VALUED, "no downstream state transition may assume the blocked operation executed", RetrySafety.IDEMPOTENT),
            _rule(cell, "cannot-check", "CREATED|READY|RUNNING", "CANNOT_CHECK", "required verification/measurement/resource obligation cannot be completed", ("the required check remains unavailable or resource-bound",), terminal_post, TransitionDeterminism.SET_VALUED, "open uncertainty is preserved rather than coerced into success/failure", RetrySafety.IDEMPOTENT),
        ),
        state_relation="The mechanic defines a guarded relation F_i: (state,input,action) -> P(next_state,output,status); determinism/stochasticity is declared per step rather than assumed globally.",
        step_specific_dynamics_open=True,
    )


def apply_default_transition_plan(cell: MechanicCell) -> MechanicCell:
    plan = default_transition_plan(cell)
    empirical_open = cell.empirical_open_coordinates
    if plan.step_specific_dynamics_open:
        empirical_open = tuple(
            dict.fromkeys(
                empirical_open
                + ("step-specific transition relation, pre/postconditions, nondeterminism/probability model, retry/idempotency and side-effect behavior",)
            )
        )
    return replace(
        cell,
        transition_semantics=(plan.state_relation, *tuple(item.rule_id for item in plan.rules)),
        empirical_open_coordinates=empirical_open,
    )


def apply_default_transition_plans(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_transition_plan(cell) for cell in cells)
