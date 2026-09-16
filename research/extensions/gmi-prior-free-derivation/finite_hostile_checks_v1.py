#!/usr/bin/env python3
"""Finite hostile witnesses for the prior-free GMI formal core.

The script is intentionally dependency-free. It checks finite countermodels that
motivated corrections from FORMAL_CORE_V1 to FORMAL_CORE_V2. These checks do not
prove the general theorems; they prevent the registered counterexamples from
being lost or accidentally contradicted by later prose.
"""

from __future__ import annotations

import itertools
import json


def min_valid_colors(vertices, conflict_hyperedges):
    """Return the minimum coloring with no monochromatic conflict hyperedge."""
    verts = list(vertices)
    edges = [set(edge) for edge in conflict_hyperedges]
    for k in range(1, len(verts) + 1):
        for colors in itertools.product(range(k), repeat=len(verts)):
            assignment = dict(zip(verts, colors))
            if all(len({assignment[v] for v in edge}) > 1 for edge in edges):
                return k, assignment
    raise AssertionError("finite hypergraph should always be colorable")


def main():
    # RED 1: pointwise dominance can be invisible to a scalar expectation when
    # the strict improvement lies entirely on a zero-mass environment.
    envs = ["e0", "e1"]
    mu = {"e0": 1.0, "e1": 0.0}
    risk_n = {"e0": 0.0, "e1": 0.0}
    risk_m = {"e0": 0.0, "e1": 1.0}
    pointwise_dominance = (
        all(risk_n[e] <= risk_m[e] for e in envs)
        and any(risk_n[e] < risk_m[e] for e in envs)
    )
    bayes_n = sum(mu[e] * risk_n[e] for e in envs)
    bayes_m = sum(mu[e] * risk_m[e] for e in envs)
    assert pointwise_dominance
    assert bayes_n == bayes_m == 0.0

    # RED 2: distinct exact stochastic action laws do not imply a message
    # alphabet as large as the number of histories. A binary message can encode
    # arbitrarily many Bernoulli parameters through its probability law.
    ps = [0.0, 0.25, 0.5, 0.75, 1.0]
    action_dists = [{"a1": p, "a0": 1.0 - p} for p in ps]
    distinct_action_dists = len(
        {tuple(sorted(dist.items())) for dist in action_dists}
    )
    assert distinct_action_dists == 5
    assert 2 < distinct_action_dists

    # RED 3: pairwise controller-state mergeability is not transitive.
    gamma = {
        "h1": {"a", "b"},
        "h2": {"b", "c"},
        "h3": {"a", "c"},
    }
    pair_intersections = {
        f"{i},{j}": sorted(gamma[i] & gamma[j])
        for i, j in itertools.combinations(gamma, 2)
    }
    triple = set.intersection(*(gamma[h] for h in gamma))
    assert all(pair_intersections.values())
    assert not triple

    # The unique minimal conflict in this witness is the triple itself, so two
    # controller-state colors suffice although no single state can contain all
    # three histories.
    control_k, control_coloring = min_valid_colors(
        gamma.keys(), [set(gamma.keys())]
    )
    assert control_k == 2

    # RED 4: best-reachable frontier differs from reachable points on the global
    # frontier when all globally optimal morphologies are unreachable.
    cost = {"a": 2, "b": 1, "c": 0}
    global_frontier = {
        x for x in cost if not any(cost[y] < cost[x] for y in cost)
    }
    reachable = {"a", "b"}
    reachable_global = global_frontier & reachable
    best_reachable = {
        x
        for x in reachable
        if not any(cost[y] < cost[x] for y in reachable)
    }
    assert global_frontier == {"c"}
    assert reachable_global == set()
    assert best_reachable == {"b"}

    # GREEN witness for the corrected zero-error graph theorem: a three-clique
    # requires three transcript colors.
    vertices = ["u1", "u2", "u3"]
    pair_conflicts = [set(edge) for edge in itertools.combinations(vertices, 2)]
    clique_k, clique_coloring = min_valid_colors(vertices, pair_conflicts)
    assert clique_k == 3

    result = {
        "control_nontransitivity": {
            "minimum_valid_state_colors": control_k,
            "one_coloring": control_coloring,
            "pair_intersections": pair_intersections,
            "pairwise_mergeable": True,
            "triple_intersection": sorted(triple),
            "triple_jointly_controllable": False,
        },
        "development_frontier": {
            "best_reachable_frontier": sorted(best_reachable),
            "global_frontier": sorted(global_frontier),
            "reachable_global_frontier": sorted(reachable_global),
            "reachable_set": sorted(reachable),
        },
        "null_prior_scalarization": {
            "bayes_risk_M": bayes_m,
            "bayes_risk_N": bayes_n,
            "pointwise_dominance": pointwise_dominance,
        },
        "stochastic_cut_counterexample": {
            "distinct_exact_action_distributions": distinct_action_dists,
            "message_alphabet_size": 2,
            "num_histories": len(ps),
        },
        "zero_error_clique": {
            "chromatic_number": clique_k,
            "clique_size": 3,
            "one_coloring": clique_coloring,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
