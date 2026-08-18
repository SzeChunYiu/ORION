#!/usr/bin/env python3
"""Deterministic countermodels/checks for P7 formal core V1.

The script uses only Python's standard library. It demonstrates bounded
instances of the general proofs; it is not an empirical LLM-agent benchmark.

Important theorem boundary: the stopping impossibility is conditioned on
extension ambiguity. Absence of a syntactic closure-certificate object is not,
by itself, defined to imply ambiguity in every admissible model class.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from itertools import combinations
from typing import FrozenSet, Mapping


@dataclass(frozen=True)
class World:
    graph: Mapping[str, FrozenSet[str]]
    relevant: Mapping[str, bool]


def observable_signature(world: World, observed: FrozenSet[str]) -> tuple[object, ...]:
    """Return exactly the state exposed on observed nodes."""
    return tuple(
        (
            node,
            tuple(sorted(target for target in world.graph.get(node, frozenset()) if target in observed)),
            bool(world.relevant.get(node, False)),
        )
        for node in sorted(observed)
    )


def reachable(
    graph: Mapping[str, FrozenSet[str]],
    start: str,
    goal: str,
) -> bool:
    pending: deque[str] = deque([start])
    seen = {start}
    while pending:
        node = pending.popleft()
        if node == goal:
            return True
        for target in graph.get(node, frozenset()):
            if target not in seen:
                seen.add(target)
                pending.append(target)
    return False


def check_extension_ambiguity() -> int:
    """Construct complete/incomplete completions with identical finite history."""
    observed_nodes = ("start", "seen-a", "seen-b")
    case_count = 0

    # Enumerate every observed undirected-edge subset to pressure the
    # construction across different finite visible histories. This deliberately
    # defines a rich admissible class in which an unseen relevant location may
    # be added without changing the observed signature.
    possible_edges = list(combinations(observed_nodes, 2))
    for mask in range(1 << len(possible_edges)):
        visible_graph: dict[str, set[str]] = {node: set() for node in observed_nodes}
        for index, (left, right) in enumerate(possible_edges):
            if (mask >> index) & 1:
                visible_graph[left].add(right)
                visible_graph[right].add(left)

        complete = World(
            graph={node: frozenset(targets) for node, targets in visible_graph.items()},
            relevant={node: False for node in observed_nodes},
        )
        incomplete_graph = {
            node: frozenset(targets) for node, targets in visible_graph.items()
        }
        incomplete_graph["hidden-relevant"] = frozenset()
        incomplete = World(
            graph=incomplete_graph,
            relevant={
                **{node: False for node in observed_nodes},
                "hidden-relevant": True,
            },
        )

        observed = frozenset(observed_nodes)
        assert observable_signature(complete, observed) == observable_signature(
            incomplete, observed
        )
        assert not any(complete.relevant.values())
        assert any(incomplete.relevant.values())
        case_count += 1

    return case_count


def check_certificate_absence_not_equivalent_to_ambiguity() -> None:
    """A missing certificate object need not imply two admissible completions."""
    closure_certificate_present = False

    # This model class is fixed by an external structural constraint: the sole
    # admissible completion is known here to contain no unseen relevant state.
    # We intentionally do not encode that fact as a `closure certificate` token
    # to demonstrate that certificate absence and extension ambiguity are not
    # definitionally identical.
    admissible_completion_truth_values = (False,)
    extension_ambiguous = len(set(admissible_completion_truth_values)) > 1

    assert closure_certificate_present is False
    assert extension_ambiguous is False


def check_route_stop_not_task_stop() -> None:
    route_state = {
        "executed-route": "ROUTE_STOP",
        "censored-route": "UNAVAILABLE_OPEN_OBLIGATION",
    }
    assert route_state["executed-route"] == "ROUTE_STOP"
    assert route_state["censored-route"] != "SATISFIED"
    task_stop_authorized = all(
        state in {"SATISFIED", "VALIDLY_DISCHARGED"}
        for state in route_state.values()
    )
    assert not task_stop_authorized


def check_overlap_independence_counterexamples() -> None:
    # Structurally independent routes can return the same content.
    route_a = {
        "source": "independent-index-A",
        "critical_failure": "A-index-loss",
        "outputs": frozenset({"paper-X"}),
    }
    route_b = {
        "source": "independent-index-B",
        "critical_failure": "B-index-loss",
        "outputs": frozenset({"paper-X"}),
    }
    assert route_a["critical_failure"] != route_b["critical_failure"]
    assert route_a["outputs"] == route_b["outputs"]

    # Structurally dependent routes can return disjoint content.
    route_c = {
        "source": "shared-censored-index",
        "critical_failure": "shared-index-loss",
        "outputs": frozenset({"paper-Y"}),
    }
    route_d = {
        "source": "shared-censored-index",
        "critical_failure": "shared-index-loss",
        "outputs": frozenset({"paper-Z"}),
    }
    assert route_c["critical_failure"] == route_d["critical_failure"]
    assert route_c["outputs"].isdisjoint(route_d["outputs"])


def check_topology_change_expressivity() -> None:
    initial = {
        "start": frozenset({"dead-end"}),
        "dead-end": frozenset(),
    }
    reframed = {
        "start": frozenset({"dead-end", "new-coordinate"}),
        "dead-end": frozenset(),
        "new-coordinate": frozenset({"goal"}),
        "goal": frozenset(),
    }
    assert not reachable(initial, "start", "goal")
    assert reachable(reframed, "start", "goal")


def check_reframe_preservation() -> None:
    support = frozenset({"claim-source", "measurement-relation", "route-contract"})

    complete_map = {
        "claim-source": "claim-source-prime",
        "measurement-relation": "measurement-relation-prime",
        "route-contract": "route-contract-prime",
    }
    incomplete_map = {
        "claim-source": "claim-source-prime",
        "route-contract": "route-contract-prime",
    }

    preserved = support.issubset(complete_map.keys())
    must_reopen = not support.issubset(incomplete_map.keys())
    assert preserved
    assert must_reopen


def check_evidence_transport_without_closure_transport() -> None:
    """Goal change may preserve evidence identity but reopen the old closure."""
    evidence_identity_before = "evidence:content-hash-123"
    evidence_identity_after = "evidence:content-hash-123"
    old_obligation = "find-any-relevant-effect"
    new_obligation = "find-effect-with-independent-replication"

    assert evidence_identity_before == evidence_identity_after
    assert old_obligation != new_obligation

    old_closure_certificate_scope = frozenset({old_obligation})
    new_obligation_covered = new_obligation in old_closure_certificate_scope
    assert not new_obligation_covered


def check_fail_closed_stop() -> None:
    obligation_states = {
        "known-source": "SATISFIED",
        "censored-provider": "UNKNOWN",
        "measurement-defeater": "VALIDLY_DISCHARGED",
    }
    closure_certificates = {"known-source", "measurement-defeater"}

    mandatory_open = {
        obligation
        for obligation, state in obligation_states.items()
        if state != "SATISFIED" and obligation not in closure_certificates
    }
    assert mandatory_open == {"censored-provider"}
    assert not (len(mandatory_open) == 0)


def check_unnecessary_reframe_negative_control() -> None:
    """A widened navigator should not reframe when the current chart suffices."""
    fixed_chart = {
        "start": frozenset({"goal"}),
        "goal": frozenset(),
    }
    assert reachable(fixed_chart, "start", "goal")
    reframe_required = False
    assert reframe_required is False


def main() -> int:
    ambiguous_pairs = check_extension_ambiguity()
    check_certificate_absence_not_equivalent_to_ambiguity()
    check_route_stop_not_task_stop()
    check_overlap_independence_counterexamples()
    check_topology_change_expressivity()
    check_reframe_preservation()
    check_evidence_transport_without_closure_transport()
    check_fail_closed_stop()
    check_unnecessary_reframe_negative_control()

    print("P7 deterministic countermodels: PASS")
    print(f"  extension-ambiguous complete/incomplete pairs: {ambiguous_pairs}")
    print("  certificate-absence != extension-ambiguity counterexample: confirmed")
    print("  route-stop/task-stop counterexample: confirmed")
    print("  overlap/independence counterexamples: confirmed")
    print("  topology-change strict-expressivity instance: confirmed")
    print("  preservation/reopening fixtures: confirmed")
    print("  evidence-preserved / closure-reopened goal-change fixture: confirmed")
    print("  fail-closed stopping fixture: confirmed")
    print("  unnecessary-reframe negative control: confirmed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())