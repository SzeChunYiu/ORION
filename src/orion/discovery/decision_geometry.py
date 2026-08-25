"""Finite reference core for Epistemic Decision Geometry.

This module computes responsibility-relative optimal actions, Bayes regret,
minimax regret, and the exact two-world hedge decomposition.  It is a
reference implementation for research protocols; it grants no scientific,
novelty, or adoption authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Hashable, Mapping, TypeVar

State = TypeVar("State", bound=Hashable)
Action = TypeVar("Action", bound=Hashable)
Observation = TypeVar("Observation", bound=Hashable)


def _ordered(values):
    return tuple(sorted(values, key=lambda value: (type(value).__name__, repr(value))))


def validate_loss_table(
    losses: Mapping[State, Mapping[Action, float]],
) -> tuple[tuple[State, ...], tuple[Action, ...]]:
    if not losses:
        raise ValueError("loss table requires at least one state")
    states = _ordered(losses)
    first_actions: set[Action] | None = None
    for state in states:
        row = losses[state]
        if not row:
            raise ValueError(f"state {state!r} has no actions")
        actions = set(row)
        if first_actions is None:
            first_actions = actions
        elif actions != first_actions:
            raise ValueError("every state must expose the same action set")
        for action, raw_loss in row.items():
            value = float(raw_loss)
            if not isfinite(value):
                raise ValueError(
                    f"loss must be finite: state={state!r}, action={action!r}"
                )
    assert first_actions is not None
    return states, _ordered(first_actions)


def _normalised_probabilities(
    states: tuple[State, ...],
    probabilities: Mapping[State, float] | None,
) -> dict[State, float]:
    if probabilities is None:
        mass = 1.0 / len(states)
        return {state: mass for state in states}
    if set(probabilities) != set(states):
        raise ValueError("probability keys must equal the loss-table state set")
    result = {state: float(probabilities[state]) for state in states}
    if any(not isfinite(value) or value < 0 for value in result.values()):
        raise ValueError("probabilities must be finite and non-negative")
    total = sum(result.values())
    if total <= 0:
        raise ValueError("probabilities must have positive total mass")
    return {state: value / total for state, value in result.items()}


def optimal_actions(
    losses: Mapping[State, Mapping[Action, float]], state: State
) -> tuple[Action, ...]:
    _, actions = validate_loss_table(losses)
    if state not in losses:
        raise KeyError(state)
    best = min(float(losses[state][action]) for action in actions)
    return tuple(
        action for action in actions if float(losses[state][action]) == best
    )


def regret_table(
    losses: Mapping[State, Mapping[Action, float]],
) -> dict[State, dict[Action, float]]:
    states, actions = validate_loss_table(losses)
    result: dict[State, dict[Action, float]] = {}
    for state in states:
        minimum = min(float(losses[state][action]) for action in actions)
        result[state] = {
            action: float(losses[state][action]) - minimum for action in actions
        }
    return result


def common_optimal_actions(
    losses: Mapping[State, Mapping[Action, float]],
    states: tuple[State, ...] | None = None,
) -> tuple[Action, ...]:
    all_states, _ = validate_loss_table(losses)
    selected = all_states if states is None else tuple(states)
    if not selected:
        raise ValueError("common-optimum query requires at least one state")
    if any(state not in losses for state in selected):
        raise KeyError("selected state absent from loss table")
    common = set(optimal_actions(losses, selected[0]))
    for state in selected[1:]:
        common.intersection_update(optimal_actions(losses, state))
    return _ordered(common)


def zero_regret_supported(
    losses: Mapping[State, Mapping[Action, float]],
    states: tuple[State, ...] | None = None,
) -> bool:
    return bool(common_optimal_actions(losses, states))


@dataclass(frozen=True)
class BayesDecision:
    action: Hashable
    expected_loss: float
    expected_regret: float
    tied_actions: tuple[Hashable, ...]


def bayes_decision(
    losses: Mapping[State, Mapping[Action, float]],
    probabilities: Mapping[State, float] | None = None,
) -> BayesDecision:
    states, actions = validate_loss_table(losses)
    probs = _normalised_probabilities(states, probabilities)
    regrets = regret_table(losses)
    expected_loss = {
        action: sum(probs[state] * float(losses[state][action]) for state in states)
        for action in actions
    }
    expected_regret = {
        action: sum(probs[state] * regrets[state][action] for state in states)
        for action in actions
    }
    best = min(expected_loss.values())
    tied = tuple(action for action in actions if expected_loss[action] == best)
    chosen = tied[0]
    return BayesDecision(
        action=chosen,
        expected_loss=best,
        expected_regret=expected_regret[chosen],
        tied_actions=tied,
    )


@dataclass(frozen=True)
class MinimaxDecision:
    action: Hashable
    worst_regret: float
    tied_actions: tuple[Hashable, ...]


def minimax_regret_decision(
    losses: Mapping[State, Mapping[Action, float]],
) -> MinimaxDecision:
    states, actions = validate_loss_table(losses)
    regrets = regret_table(losses)
    worst = {
        action: max(regrets[state][action] for state in states) for action in actions
    }
    optimum = min(worst.values())
    tied = tuple(action for action in actions if worst[action] == optimum)
    return MinimaxDecision(action=tied[0], worst_regret=optimum, tied_actions=tied)


@dataclass(frozen=True)
class TwoWorldHedgeReport:
    left_state: Hashable
    right_state: Hashable
    left_optima: tuple[Hashable, ...]
    right_optima: tuple[Hashable, ...]
    best_action: Hashable
    exact_equal_prior_regret: float
    cross_action_gap: float | None
    half_gap_value: float | None
    hedge_gain: float | None
    hedge_present: bool
    common_optimum_present: bool


def two_world_hedge_report(
    losses: Mapping[State, Mapping[Action, float]],
    left_state: State,
    right_state: State,
) -> TwoWorldHedgeReport:
    states, actions = validate_loss_table(losses)
    if left_state not in states or right_state not in states:
        raise KeyError("both states must appear in the loss table")
    if left_state == right_state:
        raise ValueError("two-world report requires distinct states")
    regrets = regret_table(losses)
    left_optima = optimal_actions(losses, left_state)
    right_optima = optimal_actions(losses, right_state)
    sums = {
        action: regrets[left_state][action] + regrets[right_state][action]
        for action in actions
    }
    best_sum = min(sums.values())
    best_actions = tuple(action for action in actions if sums[action] == best_sum)
    common = bool(set(left_optima) & set(right_optima))

    cross_gap: float | None = None
    half_gap: float | None = None
    hedge_gain: float | None = None
    if len(left_optima) == 1 and len(right_optima) == 1 and left_optima != right_optima:
        left_action = left_optima[0]
        right_action = right_optima[0]
        cross_gap = min(
            regrets[left_state][right_action], regrets[right_state][left_action]
        )
        half_gap = cross_gap / 2.0
        hedge_gain = cross_gap - best_sum
        if hedge_gain < -1e-12:
            raise AssertionError("best action cannot be worse than both cross choices")
        hedge_gain = max(0.0, hedge_gain)

    return TwoWorldHedgeReport(
        left_state=left_state,
        right_state=right_state,
        left_optima=left_optima,
        right_optima=right_optima,
        best_action=best_actions[0],
        exact_equal_prior_regret=best_sum / 2.0,
        cross_action_gap=cross_gap,
        half_gap_value=half_gap,
        hedge_gain=hedge_gain,
        hedge_present=bool(hedge_gain is not None and hedge_gain > 0),
        common_optimum_present=common,
    )


def partition_bayes_regret(
    losses: Mapping[State, Mapping[Action, float]],
    observation: Mapping[State, Observation],
    probabilities: Mapping[State, float] | None = None,
) -> float:
    states, _ = validate_loss_table(losses)
    if set(observation) != set(states):
        raise ValueError("observation map must cover exactly the state set")
    probs = _normalised_probabilities(states, probabilities)
    fibres: dict[Observation, list[State]] = {}
    for state in states:
        fibres.setdefault(observation[state], []).append(state)

    total = 0.0
    for fibre_states in fibres.values():
        fibre_mass = sum(probs[state] for state in fibre_states)
        conditional = {state: probs[state] / fibre_mass for state in fibre_states}
        fibre_losses = {state: losses[state] for state in fibre_states}
        total += fibre_mass * bayes_decision(fibre_losses, conditional).expected_regret
    return total


def refines(
    finer: Mapping[State, Hashable],
    coarser: Mapping[State, Hashable],
) -> bool:
    if set(finer) != set(coarser):
        raise ValueError("partition maps must cover the same states")
    induced: dict[Hashable, Hashable] = {}
    for state in finer:
        fine_value = finer[state]
        coarse_value = coarser[state]
        prior = induced.setdefault(fine_value, coarse_value)
        if prior != coarse_value:
            return False
    return True


__all__ = [
    "BayesDecision",
    "MinimaxDecision",
    "TwoWorldHedgeReport",
    "bayes_decision",
    "common_optimal_actions",
    "minimax_regret_decision",
    "optimal_actions",
    "partition_bayes_regret",
    "refines",
    "regret_table",
    "two_world_hedge_report",
    "validate_loss_table",
    "zero_regret_supported",
]
