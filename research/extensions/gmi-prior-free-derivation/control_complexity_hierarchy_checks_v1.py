#!/usr/bin/env python3
"""Finite checks for the rooted control-complexity hierarchy.

The registered witnesses distinguish:
  chi_act  : repeated per-step action-information coloring,
  chi_plan : one-time rooted-plan coloring, and
  N_dyn    : minimum autonomous closed-cover state count.

The checker is dependency-free and exhausts all finite colorings/covers for the
small registered examples. It is evidence for the witnesses, not a proof of the
general hierarchy theorem.
"""

from __future__ import annotations

import itertools
import json


def nonempty_subsets(vertices):
    vertices = tuple(vertices)
    return [
        frozenset(c)
        for r in range(1, len(vertices) + 1)
        for c in itertools.combinations(vertices, r)
    ]


def action_compatible(block, allowed):
    return bool(set.intersection(*(set(allowed[v]) for v in block)))


def rooted_plan_compatible_one_observation(block, allowed, successor):
    """Compatibility for deterministic residual dynamics with one observation.

    Because the observation is uninformative, a common rooted strategy is an
    open-loop action sequence. The current uncertainty set evolves by the
    successor map. A plan exists exactly when every uncertainty set encountered
    on the eventual finite orbit has a common admissible action.
    """
    current = frozenset(block)
    seen = set()
    while current not in seen:
        seen.add(current)
        if not action_compatible(current, allowed):
            return False
        current = frozenset(successor[v] for v in current)
    return True


def minimum_coloring(vertices, compatible):
    vertices = tuple(vertices)
    for k in range(1, len(vertices) + 1):
        for colors in itertools.product(range(k), repeat=len(vertices)):
            if set(colors) != set(range(k)):
                continue
            valid = True
            for color in range(k):
                block = frozenset(
                    vertices[i] for i, assigned in enumerate(colors) if assigned == color
                )
                if not compatible(block):
                    valid = False
                    break
            if valid:
                return k, dict(zip(vertices, colors))
    raise AssertionError("finite instance must be colorable by singleton colors")


def minimum_closed_cover(vertices, allowed, successor):
    """Exhaust minimum closed cover for the one-observation deterministic case."""
    vertices = set(vertices)
    compatible_blocks = [
        block
        for block in nonempty_subsets(vertices)
        if action_compatible(block, allowed)
    ]

    for m in range(1, len(vertices) + 1):
        for family in itertools.combinations(compatible_blocks, m):
            if set().union(*(set(block) for block in family)) != vertices:
                continue

            action_options = [
                sorted(set.intersection(*(set(allowed[v]) for v in block)))
                for block in family
            ]
            for actions in itertools.product(*action_options):
                closed = True
                for block, _action in zip(family, actions):
                    implied = {successor[v] for v in block}
                    if not any(implied <= set(target) for target in family):
                        closed = False
                        break
                if closed:
                    return m, family, actions

    raise AssertionError("singleton residual states always give a closed cover")


def analyze(vertices, allowed, successor):
    chi_act, act_coloring = minimum_coloring(
        vertices, lambda block: action_compatible(block, allowed)
    )
    chi_plan, plan_coloring = minimum_coloring(
        vertices,
        lambda block: rooted_plan_compatible_one_observation(
            block, allowed, successor
        ),
    )
    n_dyn, closed_cover, actions = minimum_closed_cover(
        vertices, allowed, successor
    )
    return {
        "chi_act": chi_act,
        "chi_plan": chi_plan,
        "N_dyn": n_dyn,
        "action_coloring": act_coloring,
        "plan_coloring": plan_coloring,
        "closed_cover": [sorted(block, key=str) for block in closed_cover],
        "closed_cover_actions": list(actions),
    }


def main():
    # Witness A: repeated action information is cheaper than a one-time plan.
    witness_a = analyze(
        vertices=("x", "y", "z"),
        allowed={"x": {0}, "y": {0}, "z": {1}},
        successor={"x": "x", "y": "z", "z": "x"},
    )
    assert witness_a["chi_act"] == 2
    assert witness_a["chi_plan"] == 3
    assert witness_a["N_dyn"] == 3

    # Witness B: two one-time rooted plans exist, but plan execution itself
    # requires a third autonomous phase/state when no external clock or state
    # oracle is supplied.
    witness_b = analyze(
        vertices=(0, 1, 2, 3),
        allowed={0: {0}, 1: {0}, 2: {1}, 3: {0, 1}},
        successor={0: 1, 1: 3, 2: 2, 3: 2},
    )
    assert witness_b["chi_act"] == 2
    assert witness_b["chi_plan"] == 2
    assert witness_b["N_dyn"] == 3

    result = {
        "hierarchy": "chi_act <= chi_plan <= N_dyn",
        "strict_action_to_plan": witness_a,
        "strict_plan_to_dynamic": witness_b,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
