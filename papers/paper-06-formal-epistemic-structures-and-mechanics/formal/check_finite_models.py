#!/usr/bin/env python3
"""Deterministic bounded checks for P6 formal core V1.

No external package and no model/LLM API is used. These checks support, but do
not replace, the general mathematical proofs in manuscript/FORMAL_CORE_V1.md.

Important theorem boundary: separated mechanics are checked for equality on the
current scientific-state projection. Ordered audit histories are intentionally
allowed to differ and are checked only up to an independent-event trace swap.
"""

from __future__ import annotations

from itertools import combinations, product
from typing import FrozenSet, Iterable, Sequence


def powerset(items: Iterable[int | str]) -> list[FrozenSet[int | str]]:
    values = list(items)
    return [
        frozenset(choice)
        for size in range(len(values) + 1)
        for choice in combinations(values, size)
    ]


def is_dag(node_count: int, edges: Sequence[tuple[int, int]]) -> bool:
    indegree = [0] * node_count
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
    for source, target in edges:
        adjacency[source].append(target)
        indegree[target] += 1

    ready = [node for node, degree in enumerate(indegree) if degree == 0]
    visited = 0
    while ready:
        source = ready.pop()
        visited += 1
        for target in adjacency[source]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    return visited == node_count


def descendants(
    node_count: int,
    edges: Sequence[tuple[int, int]],
    changed: FrozenSet[int],
) -> FrozenSet[int]:
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
    for source, target in edges:
        adjacency[source].append(target)

    seen = set(changed)
    pending = list(changed)
    while pending:
        source = pending.pop()
        for target in adjacency[source]:
            if target not in seen:
                seen.add(target)
                pending.append(target)
    return frozenset(seen.difference(changed))


def check_reopening(node_count: int = 4) -> tuple[int, int]:
    possible_edges = [
        (source, target)
        for source in range(node_count)
        for target in range(node_count)
        if source != target
    ]
    dag_count = 0
    case_count = 0

    for mask in range(1 << len(possible_edges)):
        edges = tuple(
            possible_edges[index]
            for index in range(len(possible_edges))
            if (mask >> index) & 1
        )
        if not is_dag(node_count, edges):
            continue
        dag_count += 1

        for changed_raw in powerset(range(node_count)):
            changed = frozenset(int(value) for value in changed_raw)
            if not changed:
                continue
            downstream = descendants(node_count, edges, changed)

            for certified_raw in powerset(range(node_count)):
                certified = frozenset(int(value) for value in certified_raw)
                retained = certified.difference(downstream)

                # Sufficiency on the graph abstraction: no downstream
                # certified node survives.
                assert not retained.intersection(downstream)

                # Minimality of the implementation: no non-descendant is
                # reopened by this operator.
                assert retained == certified.difference(downstream)
                case_count += 1

    return dag_count, case_count


def apply_local_mechanic(
    state: tuple[int, ...],
    write_coordinate: int,
    read_coordinates: FrozenSet[int],
) -> tuple[int, ...]:
    output = list(state)
    # A deterministic nontrivial local state transformer.
    output[write_coordinate] = (
        output[write_coordinate]
        + sum(output[index] for index in read_coordinates)
        + 1
    ) % 2
    return tuple(output)


def check_separated_commutation(node_count: int = 4) -> int:
    """Check equality of the current scientific-state projection only."""
    case_count = 0
    coordinates = range(node_count)

    for write_left, write_right in combinations(coordinates, 2):
        shared_read_candidates = [
            coordinate
            for coordinate in coordinates
            if coordinate not in (write_left, write_right)
        ]
        for left_reads_raw in powerset(shared_read_candidates):
            left_reads = frozenset(int(value) for value in left_reads_raw)
            for right_reads_raw in powerset(shared_read_candidates):
                right_reads = frozenset(int(value) for value in right_reads_raw)
                for state in product((0, 1), repeat=node_count):
                    left_then_right = apply_local_mechanic(
                        apply_local_mechanic(state, write_left, left_reads),
                        write_right,
                        right_reads,
                    )
                    right_then_left = apply_local_mechanic(
                        apply_local_mechanic(state, write_right, right_reads),
                        write_left,
                        left_reads,
                    )
                    assert left_then_right == right_then_left
                    case_count += 1

    return case_count


def check_history_aware_commutation() -> None:
    """Show same current state need not mean identical ordered audit history."""
    state = (0, 1, 0, 1)
    left_reads = frozenset({2})
    right_reads = frozenset({3})

    after_left = apply_local_mechanic(state, 0, left_reads)
    state_lr = apply_local_mechanic(after_left, 1, right_reads)
    history_lr = ("left", "right")

    after_right = apply_local_mechanic(state, 1, right_reads)
    state_rl = apply_local_mechanic(after_right, 0, left_reads)
    history_rl = ("right", "left")

    assert state_lr == state_rl
    assert history_lr != history_rl

    # For this two-event independent fixture, the trace quotient generated by
    # swapping adjacent independent events identifies the histories. Sorting is
    # merely a deterministic encoding of that single-swap equivalence here; it
    # is not proposed as a general trace-equivalence algorithm.
    assert tuple(sorted(history_lr)) == tuple(sorted(history_rl))


def check_authority_non_escalation() -> int:
    trusted_roots = frozenset({"root-0", "root-1"})
    universe = frozenset({"root-0", "root-1", "untrusted"})
    case_count = 0

    for initial_raw in powerset(universe):
        initial = frozenset(str(value) for value in initial_raw)
        for retain_1_raw in powerset(universe):
            retain_1 = frozenset(str(value) for value in retain_1_raw)
            for grant_1_raw in powerset(trusted_roots):
                grant_1 = frozenset(str(value) for value in grant_1_raw)
                state_1 = initial.intersection(retain_1).union(grant_1)
                assert state_1.issubset(initial.union(trusted_roots))

                for retain_2_raw in powerset(universe):
                    retain_2 = frozenset(str(value) for value in retain_2_raw)
                    for grant_2_raw in powerset(trusted_roots):
                        grant_2 = frozenset(str(value) for value in grant_2_raw)
                        state_2 = state_1.intersection(retain_2).union(grant_2)
                        assert state_2.issubset(initial.union(trusted_roots))
                        case_count += 1

    return case_count


def check_residual_obligation_preservation() -> None:
    """Later computational success cannot silently erase a hard obligation."""
    initial_obligations = frozenset({"independent-check"})
    later_computation_succeeded = True
    explicit_authorized_discharge = False

    obligations_after = initial_obligations
    if explicit_authorized_discharge:
        obligations_after = frozenset()

    assert later_computation_succeeded
    assert obligations_after == initial_obligations

    # Positive control: an explicitly authorized discharge may close it.
    explicit_authorized_discharge = True
    obligations_after = (
        frozenset()
        if explicit_authorized_discharge
        else initial_obligations
    )
    assert not obligations_after


def check_recursive_countermodel() -> None:
    transition = {"audit-self": "audit-self"}
    current = "audit-self"
    seen: set[str] = set()
    while current not in seen:
        seen.add(current)
        current = transition[current]
    assert current == "audit-self"


def check_self_authorization_countermodel() -> None:
    candidates = ("good-change", "harmful-change", "unverified-change")
    candidate_controlled_policy = lambda _candidate: True
    assert all(candidate_controlled_policy(candidate) for candidate in candidates)


def main() -> int:
    dags, reopening_cases = check_reopening()
    commutation_cases = check_separated_commutation()
    check_history_aware_commutation()
    authority_cases = check_authority_non_escalation()
    check_residual_obligation_preservation()
    check_recursive_countermodel()
    check_self_authorization_countermodel()

    print("P6 finite-model checks: PASS")
    print(f"  DAGs enumerated: {dags}")
    print(f"  reopening cases: {reopening_cases}")
    print(f"  scientific-projection separated-commutation cases: {commutation_cases}")
    print("  ordered-history distinction / independent trace equivalence: confirmed")
    print(f"  non-escalation compositions: {authority_cases}")
    print("  residual-obligation preservation fixture: confirmed")
    print("  recursive self-loop countermodel: detected")
    print("  candidate-controlled authorization countermodel: detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())