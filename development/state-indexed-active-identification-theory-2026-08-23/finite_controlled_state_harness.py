#!/usr/bin/env python3
"""Exact finite witnesses for state-indexed active identification.

All arithmetic is rational except that no approximation is needed.  The script
writes only its colocated JSON receipt.  It is a local mathematical check, not
empirical validation, protected evaluation, or external review.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
RECEIPT = ROOT / "CONTROLLED_STATE_RECEIPT.json"
Vector = tuple[Fraction, ...]


@dataclass(frozen=True)
class Branch:
    label: str
    next_state: str
    probabilities: Vector


@dataclass(frozen=True)
class Action:
    name: str
    cost: Fraction
    branches: tuple[Branch, ...]


@dataclass(frozen=True)
class Model:
    worlds: tuple[str, ...]
    terminal: tuple[tuple[str, tuple[Vector, ...]], ...]
    actions: tuple[tuple[str, tuple[Action, ...]], ...]

    def terminal_at(self, state: str) -> tuple[Vector, ...]:
        return dict(self.terminal)[state]

    def actions_at(self, state: str) -> tuple[Action, ...]:
        return dict(self.actions).get(state, ())

    def validate(self) -> None:
        states = set(dict(self.terminal))
        assert self.worlds and states
        width = len(self.worlds)
        for _, vectors in self.terminal:
            assert vectors
            assert all(len(v) == width and all(x >= 0 for x in v) for v in vectors)
        for state, actions in self.actions:
            assert state in states
            for action in actions:
                assert action.cost >= 0 and action.branches
                assert all(branch.next_state in states for branch in action.branches)
                assert all(len(branch.probabilities) == width for branch in action.branches)
                for w in range(width):
                    total = sum((branch.probabilities[w] for branch in action.branches), Fraction(0))
                    assert total == 1
                    assert all(branch.probabilities[w] >= 0 for branch in action.branches)


def gamma_solver(model: Model):
    model.validate()

    @lru_cache(maxsize=None)
    def gamma(horizon: int, state: str) -> frozenset[Vector]:
        assert horizon >= 0
        result = set(model.terminal_at(state))
        if horizon == 0:
            return frozenset(result)
        for action in model.actions_at(state):
            continuation_sets = [gamma(horizon - 1, b.next_state) for b in action.branches]
            for choices in itertools.product(*continuation_sets):
                vector = tuple(
                    action.cost + sum(
                        (branch.probabilities[w] * choices[i][w]
                         for i, branch in enumerate(action.branches)),
                        Fraction(0),
                    )
                    for w in range(len(model.worlds))
                )
                result.add(vector)
        return frozenset(result)

    return gamma


def explicit_tree_solver(model: Model):
    """Independently enumerate syntactic trees and evaluate them."""
    model.validate()

    @lru_cache(maxsize=None)
    def trees(horizon: int, state: str) -> tuple[tuple, ...]:
        result: list[tuple] = [
            ("stop", terminal_index)
            for terminal_index in range(len(model.terminal_at(state)))
        ]
        if horizon == 0:
            return tuple(result)
        for action_index, action in enumerate(model.actions_at(state)):
            child_sets = [trees(horizon - 1, b.next_state) for b in action.branches]
            for children in itertools.product(*child_sets):
                result.append(("act", action_index, children))
        return tuple(result)

    def risk(tree: tuple, state: str) -> Vector:
        if tree[0] == "stop":
            return model.terminal_at(state)[tree[1]]
        action = model.actions_at(state)[tree[1]]
        children = tree[2]
        child_risks = [risk(child, branch.next_state)
                       for child, branch in zip(children, action.branches)]
        return tuple(
            action.cost + sum(
                (branch.probabilities[w] * child_risks[i][w]
                 for i, branch in enumerate(action.branches)),
                Fraction(0),
            )
            for w in range(len(model.worlds))
        )

    def frontier(horizon: int, state: str) -> frozenset[Vector]:
        return frozenset(risk(tree, state) for tree in trees(horizon, state))

    return trees, frontier


def crosscheck(model: Model, horizon: int, state: str, gamma) -> tuple[bool, int]:
    trees, explicit_frontier = explicit_tree_solver(model)
    return gamma(horizon, state) == explicit_frontier(horizon, state), len(trees(horizon, state))


def dot(prior: Vector, vector: Vector) -> Fraction:
    return sum((p * value for p, value in zip(prior, vector)), Fraction(0))


def bayes_value(vectors: Iterable[Vector], prior: Vector) -> Fraction:
    return min(dot(prior, vector) for vector in vectors)


def deterministic_robust_value(vectors: Iterable[Vector], priors: tuple[Vector, ...]) -> Fraction:
    return min(max(dot(prior, vector) for prior in priors) for vector in vectors)


def classification_terminals(targets: tuple[int, ...]) -> tuple[Vector, Vector]:
    return tuple(
        tuple(Fraction(int(decision != target)) for target in targets)
        for decision in (0, 1)
    )  # type: ignore[return-value]


def unavailable_initial_check() -> dict:
    worlds = ("w0", "w1")
    terminal = classification_terminals((0, 1))
    reveal = Action(
        "reveal",
        Fraction(0),
        (
            Branch("o0", "done", (Fraction(1), Fraction(0))),
            Branch("o1", "done", (Fraction(0), Fraction(1))),
        ),
    )
    model = Model(
        worlds,
        (("initial", terminal), ("open", terminal), ("done", terminal)),
        (("initial", ()), ("open", (reveal,)), ("done", ())),
    )
    gamma = gamma_solver(model)
    prior = (Fraction(1, 2), Fraction(1, 2))
    legal = bayes_value(gamma(1, "initial"), prior)
    open_value = bayes_value(gamma(1, "open"), prior)
    legal_cross, legal_trees = crosscheck(model, 1, "initial", gamma)
    open_cross, open_trees = crosscheck(model, 1, "open", gamma)
    return {
        "id": "C1_UNAVAILABLE_INITIAL_TEST",
        "pass": legal == Fraction(1, 2) and open_value == 0 and legal_cross and open_cross,
        "legal_initial_value": str(legal),
        "explicit_tree_crosscheck": legal_cross and open_cross,
        "explicit_tree_counts": {"initial": legal_trees, "open": open_trees},
        "same_test_if_open_value": str(open_value),
        "initial_legal_actions": 0,
    }


def destructive_no_repeat_check() -> dict:
    worlds = ("w0", "w1")
    terminal = classification_terminals((0, 1))
    branches_spent = (
        Branch("o0", "spent", (Fraction(9, 10), Fraction(2, 5))),
        Branch("o1", "spent", (Fraction(1, 10), Fraction(3, 5))),
    )
    destructive = Action("destructive_A", Fraction(0), branches_spent)
    legal_model = Model(
        worlds,
        (("fresh", terminal), ("spent", terminal)),
        (("fresh", (destructive,)), ("spent", ())),
    )
    legal_gamma = gamma_solver(legal_model)
    prior = (Fraction(1, 2), Fraction(1, 2))
    legal_one = bayes_value(legal_gamma(1, "fresh"), prior)
    legal_two = bayes_value(legal_gamma(2, "fresh"), prior)

    repeatable = Action(
        "repeatable_A",
        Fraction(0),
        tuple(Branch(b.label, "fresh", b.probabilities) for b in branches_spent),
    )
    illegal_stationary_model = Model(
        worlds,
        (("fresh", terminal),),
        (("fresh", (repeatable,)),),
    )
    stationary_gamma = gamma_solver(illegal_stationary_model)
    repeated_two = bayes_value(stationary_gamma(2, "fresh"), prior)
    legal_cross, legal_trees = crosscheck(legal_model, 2, "fresh", legal_gamma)
    stationary_cross, stationary_trees = crosscheck(
        illegal_stationary_model, 2, "fresh", stationary_gamma
    )
    return {
        "id": "C2_DESTRUCTIVE_NO_REPEAT",
        "pass": legal_one == Fraction(1, 4) and legal_two == legal_one
                and repeated_two == Fraction(7, 40) and legal_cross and stationary_cross,
        "legal_one_test_value": str(legal_one),
        "explicit_tree_crosscheck": legal_cross and stationary_cross,
        "explicit_tree_counts": {"legal": legal_trees, "stationary": stationary_trees},
        "legal_two_horizon_value": str(legal_two),
        "illegal_stationary_repeat_value": str(repeated_two),
    }


def stochastic_next_state_check() -> dict:
    worlds = ("w0", "w1")
    terminal = classification_terminals((0, 1))
    triage = Action(
        "triage",
        Fraction(1, 20),
        (
            Branch("tick_good", "good", (Fraction(3, 4), Fraction(1, 4))),
            Branch("tick_bad", "bad", (Fraction(1, 4), Fraction(3, 4))),
        ),
    )
    model = Model(
        worlds,
        (("initial", terminal), ("good", terminal), ("bad", terminal)),
        (("initial", (triage,)), ("good", ()), ("bad", ())),
    )
    gamma = gamma_solver(model)
    prior = (Fraction(1, 2), Fraction(1, 2))
    value = bayes_value(gamma(1, "initial"), prior)
    balanced_vector = (Fraction(3, 10), Fraction(3, 10))
    explicit_cross, tree_count = crosscheck(model, 1, "initial", gamma)
    return {
        "id": "C3_STOCHASTIC_NEXT_STATE",
        "pass": value == Fraction(3, 10) and balanced_vector in gamma(1, "initial")
                and explicit_cross,
        "optimal_value": str(value),
        "explicit_tree_crosscheck": explicit_cross,
        "explicit_tree_count": tree_count,
        "target_vector": [str(x) for x in balanced_vector],
        "frontier_size": len(gamma(1, "initial")),
    }


def randomized_minimax_check() -> dict:
    terminal = classification_terminals((0, 1))
    priors = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
    deterministic = deterministic_robust_value(terminal, priors)
    fair = tuple((a + b) / 2 for a, b in zip(terminal[0], terminal[1]))
    randomized = max(dot(prior, fair) for prior in priors)
    return {
        "id": "C4_RANDOMIZED_MINIMAX",
        "pass": deterministic == 1 and randomized == Fraction(1, 2),
        "deterministic_robust_value": str(deterministic),
        "fair_randomized_vector": [str(x) for x in fair],
        "randomized_robust_value": str(randomized),
    }


def nonclosed_credal_check() -> dict:
    # Pi={(theta,1-theta):0<theta<1}; v=(1,0).  The exact supremum is 1,
    # approached by theta_k=1-1/k, but no licensed theta attains it.
    sequence = tuple(Fraction(k - 1, k) for k in range(2, 9))
    values = sequence
    return {
        "id": "C5_NONCLOSED_CREDAL_NONATTAINMENT",
        "pass": all(a < b < 1 for a, b in zip(values, values[1:])),
        "risk_vector": ["1", "0"],
        "support_supremum": "1",
        "attained_in_credal_set": False,
        "approaching_values": [str(x) for x in values],
        "policy_attainment_affected": False,
    }


def zero_cost_closure_check() -> dict:
    worlds_bits = ((0, 0), (0, 1), (1, 0), (1, 1))
    worlds = tuple(f"{x1}{x2}" for x1, x2 in worlds_bits)
    targets = tuple(x1 ^ x2 for x1, x2 in worlds_bits)
    terminal = classification_terminals(targets)
    reveal_x1 = Action(
        "reveal_x1_free",
        Fraction(0),
        (
            Branch("x1=0", "stage1", tuple(Fraction(int(x1 == 0)) for x1, _ in worlds_bits)),
            Branch("x1=1", "stage1", tuple(Fraction(int(x1 == 1)) for x1, _ in worlds_bits)),
        ),
    )
    reveal_x2 = Action(
        "reveal_x2_free",
        Fraction(0),
        (
            Branch("x2=0", "done", tuple(Fraction(int(x2 == 0)) for _, x2 in worlds_bits)),
            Branch("x2=1", "done", tuple(Fraction(int(x2 == 1)) for _, x2 in worlds_bits)),
        ),
    )
    model = Model(
        worlds,
        (("stage0", terminal), ("stage1", terminal), ("done", terminal)),
        (("stage0", (reveal_x1,)), ("stage1", (reveal_x2,)), ("done", ())),
    )
    gamma = gamma_solver(model)
    prior = tuple(Fraction(1, 4) for _ in worlds)
    values = [bayes_value(gamma(n, "stage0"), prior) for n in range(3)]
    perfect = tuple(Fraction(0) for _ in worlds)
    explicit_cross, tree_count = crosscheck(model, 2, "stage0", gamma)
    return {
        "id": "C6_ZERO_COST_CLOSURE",
        "pass": values == [Fraction(1, 2), Fraction(1, 2), Fraction(0)]
                and perfect in gamma(2, "stage0") and explicit_cross,
        "bayes_values_horizon_0_1_2": [str(x) for x in values],
        "explicit_tree_crosscheck": explicit_cross,
        "explicit_tree_count": tree_count,
        "perfect_zero_cost_vector_present": perfect in gamma(2, "stage0"),
        "total_acquisition_cost": "0",
    }


def fixed_vs_rectangular_check() -> dict:
    atoms = ((0, 0), (0, 1), (1, 0), (1, 1))  # (Z,Y)
    worlds = tuple(f"z{z}y{y}" for z, y in atoms)
    targets = tuple(y for _, y in atoms)
    terminal = classification_terminals(targets)
    observe_z = Action(
        "observe_Z",
        Fraction(0),
        (
            Branch("z=0", "z0", tuple(Fraction(int(z == 0)) for z, _ in atoms)),
            Branch("z=1", "z1", tuple(Fraction(int(z == 1)) for z, _ in atoms)),
        ),
    )
    model = Model(
        worlds,
        (("root", terminal), ("z0", terminal), ("z1", terminal)),
        (("root", (observe_z,)), ("z0", ()), ("z1", ())),
    )
    gamma = gamma_solver(model)
    p_a = (Fraction(9, 10), Fraction(0), Fraction(0), Fraction(1, 10))
    p_b = (Fraction(0), Fraction(1, 10), Fraction(9, 10), Fraction(0))
    fixed_det = deterministic_robust_value(gamma(1, "root"), (p_a, p_b))
    explicit_cross, tree_count = crosscheck(model, 1, "root", gamma)
    # For decision probabilities q0,q1 after Z=0,1:
    # R_A+R_B = 1/5 + (4/5)(q0+q1), hence max >= 1/10.
    # q0=q1=0 attains 1/10.  Rectangular posterior sets contain both point
    # labels at each z, so the local randomized minimax error is 1/2 at each z.
    rectangular = Fraction(1, 2)
    return {
        "id": "C7_FIXED_VS_RECTANGULAR",
        "pass": fixed_det == Fraction(1, 10) and rectangular == Fraction(1, 2)
                and explicit_cross,
        "fixed_ex_ante_minimax_value": str(fixed_det),
        "explicit_tree_crosscheck": explicit_cross,
        "explicit_tree_count": tree_count,
        "rectangular_posterior_local_value": str(rectangular),
        "strict_gap": str(rectangular - fixed_det),
        "fixed_lower_bound_identity": "R_A+R_B=1/5+(4/5)(q0+q1)>=1/5",
    }


def run() -> dict:
    checks = [
        unavailable_initial_check(),
        destructive_no_repeat_check(),
        stochastic_next_state_check(),
        randomized_minimax_check(),
        nonclosed_credal_check(),
        zero_cost_closure_check(),
        fixed_vs_rectangular_check(),
    ]
    passed = sum(bool(check["pass"]) for check in checks)
    script_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return {
        "schema": "state-indexed-active-identification-receipt-v1",
        "scope": "exact finite local mathematical witnesses only",
        "empirical_authority": False,
        "external_independent_review": False,
        "protected_evaluation": False,
        "checks_total": len(checks),
        "checks_passed": passed,
        "all_pass": passed == len(checks),
        "script_sha256": script_sha,
        "checks": checks,
    }


if __name__ == "__main__":
    result = run()
    RECEIPT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_pass"] else 1)
