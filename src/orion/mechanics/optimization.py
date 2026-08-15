from __future__ import annotations

from dataclasses import dataclass, replace

from .model import MechanicCell


@dataclass(frozen=True)
class MechanicOptimizationPolicy:
    policy_id: str
    mechanic_id: str
    candidate_semantics: str
    hard_filter: tuple[str, ...]
    vector_coordinates: tuple[str, ...]
    selection_rule: str
    probability_policy: str
    exploration_policy: str
    stopping_boundary: str

    def __post_init__(self) -> None:
        required = (
            self.policy_id,
            self.mechanic_id,
            self.candidate_semantics,
            self.selection_rule,
            self.probability_policy,
            self.exploration_policy,
            self.stopping_boundary,
        )
        if any(not value.strip() for value in required) or not self.hard_filter or not self.vector_coordinates:
            raise ValueError("optimization policy requires identity/candidates/gates/vector/selection/probability/exploration/stopping")


def default_optimization_policy(cell: MechanicCell) -> MechanicOptimizationPolicy:
    return MechanicOptimizationPolicy(
        policy_id=f"optimization:{cell.mechanic_id}:shadow-v0",
        mechanic_id=cell.mechanic_id,
        candidate_semantics="Enumerate only actions/alternatives licensed by the mechanic action contract and current dependency/resource/authority state.",
        hard_filter=(
            "reject candidates violating authority/safety/evaluator/interface invariants",
            "reject candidates requiring unavailable mandatory evidence or dependencies unless they explicitly return BLOCKED/CANNOT_CHECK",
            "reject candidates whose local progress cannot be related to a registered root-relevant coordinate when root progress is claimed",
            "reject retries that can duplicate external side effects without an idempotency/receipt guard",
        ),
        vector_coordinates=(
            "root-relevant obligation progress",
            "alternative-separation/information value",
            "new relevant coverage",
            "residual/uncertainty reduction",
            "reliability/harm risk",
            "resource cost",
            "latency",
            "verification debt",
        ),
        selection_rule=(
            "After hard filtering, retain non-dominated/Pareto candidates over the declared vector. "
            "Use a registered deterministic tie-breaker (mandatory trigger -> worst-case/root separation -> lower verification debt -> lower cost) when no calibrated tradeoff model exists."
        ),
        probability_policy=(
            "Expected utility/value-of-information may be used only when probabilities and utility tradeoffs are justified/calibrated. "
            "Missing priors are never fabricated merely to make a scalar optimizer computable."
        ),
        exploration_policy=(
            "Reserve bounded capacity for challenge/diversifying/novel alternatives when the active policy could be trapped by representation or search fixation; extra exploration must remain costed and falsifiable."
        ),
        stopping_boundary=(
            "Local action optimization cannot authorize task/mechanic saturation. Stopping remains governed by the separate bounded-saturation contract and may return CANNOT_CHECK."
        ),
    )


def apply_default_optimization_policy(cell: MechanicCell) -> MechanicCell:
    policy = default_optimization_policy(cell)
    empirical_open = tuple(
        dict.fromkeys(
            cell.empirical_open_coordinates
            + (
                "step-specific candidate generator, calibrated utility/separation model, exploration budget, optimization regret and baseline comparison",
            )
        )
    )
    return replace(
        cell,
        optimization_semantics=(
            policy.candidate_semantics,
            *policy.hard_filter,
            f"vector={','.join(policy.vector_coordinates)}",
            policy.selection_rule,
            policy.probability_policy,
            policy.exploration_policy,
            policy.stopping_boundary,
        ),
        empirical_open_coordinates=empirical_open,
    )


def apply_default_optimization_policies(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_optimization_policy(cell) for cell in cells)
