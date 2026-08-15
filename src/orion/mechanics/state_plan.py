from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell


class StateRole(str, Enum):
    EXECUTION_IDENTITY = "EXECUTION_IDENTITY"
    INPUT_SNAPSHOT = "INPUT_SNAPSHOT"
    VERSION_BINDING = "VERSION_BINDING"
    WORKING = "WORKING"
    CONTROL_PHASE = "CONTROL_PHASE"
    OUTPUT_SNAPSHOT = "OUTPUT_SNAPSHOT"


class StateMutability(str, Enum):
    IMMUTABLE_PER_RUN = "IMMUTABLE_PER_RUN"
    TRANSITION_CONTROLLED = "TRANSITION_CONTROLLED"
    FINALIZED_ON_EXIT = "FINALIZED_ON_EXIT"


class StatePersistence(str, Enum):
    DURABLE = "DURABLE"
    RECONSTRUCTIBLE = "RECONSTRUCTIBLE"
    EPHEMERAL_WITH_RECEIPT = "EPHEMERAL_WITH_RECEIPT"


@dataclass(frozen=True)
class StateVariableSpec:
    state_id: str
    mechanic_id: str
    role: StateRole
    description: str
    schema_ref: str
    mutability: StateMutability
    persistence: StatePersistence
    replay_semantics: str

    def __post_init__(self) -> None:
        if any(not item.strip() for item in (self.state_id, self.mechanic_id, self.description, self.schema_ref, self.replay_semantics)):
            raise ValueError("state variable identity/description/schema/replay semantics are required")


@dataclass(frozen=True)
class MechanicStatePlan:
    mechanic_id: str
    variables: tuple[StateVariableSpec, ...]
    mutation_rule: str
    step_specific_state_open: bool = True

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip() or not self.variables or not self.mutation_rule.strip():
            raise ValueError("mechanic state plan requires identity, variables and mutation rule")
        if any(item.mechanic_id != self.mechanic_id for item in self.variables):
            raise ValueError("state variable mechanic mismatch")
        ids = [item.state_id for item in self.variables]
        if len(set(ids)) != len(ids):
            raise ValueError("state variable ids must be unique")


def _state(
    cell: MechanicCell,
    suffix: str,
    role: StateRole,
    description: str,
    schema_ref: str,
    mutability: StateMutability,
    persistence: StatePersistence,
    replay: str,
) -> StateVariableSpec:
    return StateVariableSpec(
        state_id=f"state:{cell.mechanic_id}:{suffix}",
        mechanic_id=cell.mechanic_id,
        role=role,
        description=description,
        schema_ref=schema_ref,
        mutability=mutability,
        persistence=persistence,
        replay_semantics=replay,
    )


def default_state_plan(cell: MechanicCell) -> MechanicStatePlan:
    """Universal execution-state envelope, not the step-specific scientific state model."""

    return MechanicStatePlan(
        mechanic_id=cell.mechanic_id,
        variables=(
            _state(
                cell,
                "run-id",
                StateRole.EXECUTION_IDENTITY,
                "Stable identity of this mechanic execution attempt.",
                "str",
                StateMutability.IMMUTABLE_PER_RUN,
                StatePersistence.DURABLE,
                "Identical replay may reuse evidence/history but a new physical attempt receives a distinct run identity.",
            ),
            _state(
                cell,
                "input-snapshot",
                StateRole.INPUT_SNAPSHOT,
                "Digest/identity of the exact input and parent state observed at entry.",
                "content_digest",
                StateMutability.IMMUTABLE_PER_RUN,
                StatePersistence.DURABLE,
                "Replay/comparison is invalid if the bound input snapshot differs unless the variation is explicitly modeled.",
            ),
            _state(
                cell,
                "mechanic-version",
                StateRole.VERSION_BINDING,
                "Exact mechanic contract/implementation identity used by the run.",
                "version+content_digest",
                StateMutability.IMMUTABLE_PER_RUN,
                StatePersistence.DURABLE,
                "Comparisons across versions are treated as method variations rather than silent repeats.",
            ),
            _state(
                cell,
                "dependency-bindings",
                StateRole.VERSION_BINDING,
                "Exact evaluator/provider/tool/data/dependency identities material to execution.",
                "tuple[dependency_identity]",
                StateMutability.IMMUTABLE_PER_RUN,
                StatePersistence.DURABLE,
                "A dependency change invalidates strict replay identity and may trigger a re-opened comparison.",
            ),
            _state(
                cell,
                "phase",
                StateRole.CONTROL_PHASE,
                "Current lifecycle phase of the mechanic attempt.",
                "enum",
                StateMutability.TRANSITION_CONTROLLED,
                StatePersistence.RECONSTRUCTIBLE,
                "Phase must be reconstructible from ordered transition/event receipts.",
            ),
            _state(
                cell,
                "working-digest",
                StateRole.WORKING,
                "Digest of mechanic-local working state required for diagnosis/checkpointing.",
                "content_digest",
                StateMutability.TRANSITION_CONTROLLED,
                StatePersistence.EPHEMERAL_WITH_RECEIPT,
                "A durable transition receipt records enough identity to compare/reconstruct the relevant working-state evolution.",
            ),
            _state(
                cell,
                "output-snapshot",
                StateRole.OUTPUT_SNAPSHOT,
                "Digest/identity of the finalized state/output handed downstream.",
                "content_digest",
                StateMutability.FINALIZED_ON_EXIT,
                StatePersistence.DURABLE,
                "The finalized output snapshot plus transition lineage defines the downstream comparison point.",
            ),
        ),
        mutation_rule="State mutation occurs only through declared mechanic transitions/events; hidden mutation outside the transition/receipt lineage is an engineering and reproducibility defect.",
        step_specific_state_open=True,
    )


def apply_default_state_plan(cell: MechanicCell) -> MechanicCell:
    plan = default_state_plan(cell)
    empirical_open = cell.empirical_open_coordinates
    if plan.step_specific_state_open:
        empirical_open = tuple(
            dict.fromkeys(
                empirical_open
                + ("step-specific scientific/algorithmic state variables, transition graph, latent-state identifiability and replay fidelity",)
            )
        )
    return replace(
        cell,
        state_ids=tuple(item.state_id for item in plan.variables),
        empirical_open_coordinates=empirical_open,
    )


def apply_default_state_plans(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_state_plan(cell) for cell in cells)
