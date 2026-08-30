#!/usr/bin/env python3
"""Finite DAG regression for ORION23.RESPONSIBILITY_CLOSURE_MINIMALITY.v1."""


def reachable(n, edges, starts):
    adjacency = {i: [] for i in range(n)}
    for u, v in edges:
        adjacency[u].append(v)
    seen = set(starts)
    stack = list(starts)
    while stack:
        u = stack.pop()
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def main():
    systems = 0
    invalidation_sets_checked = 0
    for n in range(1, 6):
        possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
        for edge_mask in range(1 << len(possible_edges)):
            edges = {
                edge for i, edge in enumerate(possible_edges) if (edge_mask >> i) & 1
            }
            for change_mask in range(1, 1 << n):
                changed = {i for i in range(n) if (change_mask >> i) & 1}
                closure = reachable(n, edges, changed)

                # Independent ancestor definition.
                by_ancestor = {
                    r
                    for r in range(n)
                    if any(r in reachable(n, edges, {c}) for c in changed)
                }
                assert closure == by_ancestor

                # Under the worst-case load-bearing model, a sound invalidation
                # set is exactly a superset of the mandatory closure.  Verify
                # that closure is the unique inclusion/cardinality minimum.
                safe_sets = []
                for mask in range(1 << n):
                    invalidated = {i for i in range(n) if (mask >> i) & 1}
                    safe = closure <= invalidated
                    if safe:
                        safe_sets.append(invalidated)
                    invalidation_sets_checked += 1
                minimum_size = min(map(len, safe_sets))
                minima = [s for s in safe_sets if len(s) == minimum_size]
                assert minima == [closure]
                systems += 1

    print(
        "ORION23_RESPONSIBILITY_CLOSURE_MINIMALITY_V1_PASS "
        f"dag_change_systems={systems} invalidation_sets={invalidation_sets_checked}"
    )


if __name__ == "__main__":
    main()
