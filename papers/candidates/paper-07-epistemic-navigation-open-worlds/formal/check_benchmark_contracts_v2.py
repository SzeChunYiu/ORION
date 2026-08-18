"""Focused theorem/benchmark contract checks for candidate ORION Paper 7 V2.

This addendum complements the existing V1 bounded checker and does not establish
novelty or live-agent efficacy.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, FrozenSet, Iterable, Mapping, MutableMapping, Optional, Sequence, Set, Tuple

Edge = Tuple[str, str]


class ObligationStatus(str, Enum):
    OPEN = "OPEN"
    SATISFIED = "SATISFIED"
    VALID_CLOSURE = "VALID_CLOSURE"
    CENSORED = "CENSORED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class Topology:
    nodes: FrozenSet[str]
    edges: FrozenSet[Edge]
    start: str
    goals: FrozenSet[str]

    def successors(self, node: str) -> FrozenSet[str]:
        return frozenset(target for source, target in self.edges if source == node)


@dataclass(frozen=True)
class ObservationHistory:
    visited: FrozenSet[str]
    revealed_edges: FrozenSet[Edge]
    observations: Tuple[Tuple[str, str], ...] = ()
    closure_certificate: Optional[str] = None


@dataclass(frozen=True)
class World:
    topology: Topology
    relevant: FrozenSet[str]


def reachable(topology: Topology, target: str) -> bool:
    seen = {topology.start}
    frontier = [topology.start]
    while frontier:
        current = frontier.pop()
        if current == target:
            return True
        for nxt in topology.successors(current):
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    return False


def observationally_equivalent(left: World, right: World, history: ObservationHistory) -> bool:
    """Compare only facts exposed by the finite history."""
    if history.visited - left.topology.nodes or history.visited - right.topology.nodes:
        return False
    left_edges = frozenset(edge for edge in left.topology.edges if edge[0] in history.visited)
    right_edges = frozenset(edge for edge in right.topology.edges if edge[0] in history.visited)
    left_relevant = left.relevant.intersection(history.visited)
    right_relevant = right.relevant.intersection(history.visited)
    return left_edges == right_edges == history.revealed_edges and left_relevant == right_relevant


def unseen_relevant_extension(base: World, history: ObservationHistory) -> World:
    """Construct the indistinguishable incomplete-world witness for P7.T1.

    The hidden node is attached behind an unvisited boundary node, so observations
    available in the supplied history do not change.
    """
    boundary_candidates = sorted(base.topology.nodes - history.visited)
    if not boundary_candidates:
        raise ValueError("history has no unvisited boundary from which to form an extension")
    boundary = boundary_candidates[0]
    hidden = "__hidden_relevant__"
    nodes = frozenset(set(base.topology.nodes) | {hidden})
    edges = frozenset(set(base.topology.edges) | {(boundary, hidden)})
    topology = Topology(nodes, edges, base.topology.start, base.topology.goals)
    return World(topology, frozenset(set(base.relevant) | {hidden}))


def task_completion_identifiable(world: World, history: ObservationHistory) -> bool:
    """Completion is identifiable only with an accepted closure certificate."""
    return history.closure_certificate is not None


@dataclass(frozen=True)
class Reframe:
    source_name: str
    target_name: str
    node_map: Mapping[str, str]
    preserved_edges: FrozenSet[Edge]


def topology_change_witness() -> Tuple[Topology, Topology, Reframe]:
    fixed = Topology(
        nodes=frozenset({"start", "dead_end", "latent_goal"}),
        edges=frozenset({("start", "dead_end")}),
        start="start",
        goals=frozenset({"latent_goal"}),
    )
    reframed = Topology(
        nodes=frozenset({"start'", "factorized", "latent_goal'"}),
        edges=frozenset({("start'", "factorized"), ("factorized", "latent_goal'")}),
        start="start'",
        goals=frozenset({"latent_goal'"}),
    )
    reframe = Reframe(
        "surface-variable topology",
        "factorized-variable topology",
        {"start": "start'", "latent_goal": "latent_goal'"},
        frozenset(),
    )
    return fixed, reframed, reframe


def certificate_transfers(
    support_nodes: Iterable[str],
    support_edges: Iterable[Edge],
    node_map: Mapping[str, str],
    preserved_edges: Iterable[Edge],
    predicates_preserved: bool,
) -> bool:
    support_nodes = set(support_nodes)
    support_edges = set(support_edges)
    mapped_nodes = set(node_map)
    if not support_nodes.issubset(mapped_nodes):
        return False
    translated_edges = {(node_map[a], node_map[b]) for a, b in support_edges}
    return predicates_preserved and translated_edges.issubset(set(preserved_edges))


@dataclass(frozen=True)
class Route:
    name: str
    backend: str
    derivation: str
    coverage_assumption: str
    outputs: FrozenSet[str]


def structurally_independent(left: Route, right: Route) -> bool:
    return (
        left.backend != right.backend
        and left.derivation != right.derivation
        and left.coverage_assumption != right.coverage_assumption
    )


def route_overlap(left: Route, right: Route) -> FrozenSet[str]:
    return left.outputs.intersection(right.outputs)


def task_stop_authorized(obligations: Mapping[str, ObligationStatus]) -> bool:
    return bool(obligations) and all(
        status in {ObligationStatus.SATISFIED, ObligationStatus.VALID_CLOSURE}
        for status in obligations.values()
    )


def route_stop_authorized(no_more_action_under_policy: bool) -> bool:
    return no_more_action_under_policy


def evaluate_benchmark_case(case: Mapping[str, object]) -> str:
    """Evaluate the frozen gold terminal from the benchmark contract.

    This is a reference-policy oracle for manifest integrity, not a learned-agent
    baseline.  It encodes the paper's non-compensatory terminal semantics:
    required topology change dominates local progress; unresolved/censored
    coverage blocks global completion; deceptive nominal diversity can stop a
    route without closing the task.
    """
    if bool(case.get("topology_change_required")):
        return "REFRAME"
    family = str(case.get("family", ""))
    censored = case.get("censored_regions", [])
    if family in {"unknown_coverage", "censored_route"} or bool(censored):
        return "CANNOT_CHECK"
    if family == "deceptive_route_diversity":
        return "ROUTE_STOP"
    return "TASK_STOP"


def validate_benchmark_case(case: Mapping[str, object]) -> Tuple[bool, str]:
    required = {
        "id",
        "family",
        "domain",
        "topology_change_required",
        "mandatory_obligations",
        "censored_regions",
        "negative_control",
        "expected_terminal",
        "gold",
    }
    missing = required - set(case)
    if missing:
        return False, f"missing fields: {sorted(missing)}"
    if case["expected_terminal"] not in {"TASK_STOP", "ROUTE_STOP", "REFRAME", "DEFER", "CANNOT_CHECK"}:
        return False, "invalid expected terminal"
    obligations = case["mandatory_obligations"]
    if not isinstance(obligations, list) or not obligations or not all(isinstance(item, str) and item for item in obligations):
        return False, "mandatory_obligations must be a non-empty string list"
    if not isinstance(case["censored_regions"], list):
        return False, "censored_regions must be a list"
    if not isinstance(case["gold"], Mapping):
        return False, "gold must be an object"
    if bool(case["negative_control"]) and bool(case["topology_change_required"]):
        return False, "negative controls cannot require topology change"
    predicted = evaluate_benchmark_case(case)
    if predicted != case["expected_terminal"]:
        return False, f"terminal mismatch: evaluator={predicted}, expected={case['expected_terminal']}"
    return True, "ok"


def run_checks() -> dict:
    results: MutableMapping[str, object] = {}

    base_topology = Topology(
        nodes=frozenset({"s", "observed", "boundary"}),
        edges=frozenset({("s", "observed"), ("s", "boundary")}),
        start="s",
        goals=frozenset(),
    )
    complete = World(base_topology, frozenset({"observed"}))
    history = ObservationHistory(
        visited=frozenset({"s"}),
        revealed_edges=frozenset({("s", "observed"), ("s", "boundary")}),
    )
    incomplete = unseen_relevant_extension(complete, history)
    results["P7.T1.indistinguishable_extension"] = observationally_equivalent(complete, incomplete, history)
    results["P7.T1.no_uncertified_global_stop"] = not task_completion_identifiable(complete, history)

    fixed, reframed, _ = topology_change_witness()
    fixed_goal = next(iter(fixed.goals))
    reframed_goal = next(iter(reframed.goals))
    results["P7.T2.strict_witness"] = not reachable(fixed, fixed_goal) and reachable(reframed, reframed_goal)

    results["P7.T3.preservation_positive"] = certificate_transfers(
        {"a", "b"}, {("a", "b")}, {"a": "a'", "b": "b'"}, {("a'", "b'")}, True
    )
    results["P7.T3.preservation_hostile"] = not certificate_transfers(
        {"a", "b"}, {("a", "b")}, {"a": "a'", "b": "b'"}, set(), True
    )

    independent_same_output_a = Route("a", "db-a", "seed-a", "ontology-a", frozenset({"paper-x"}))
    independent_same_output_b = Route("b", "db-b", "seed-b", "ontology-b", frozenset({"paper-x"}))
    dependent_disjoint_a = Route("c", "same-db", "same-seed", "same-scope", frozenset({"paper-y"}))
    dependent_disjoint_b = Route("d", "same-db", "same-seed", "same-scope", frozenset({"paper-z"}))
    results["P7.T4.same_output_can_be_independent"] = structurally_independent(independent_same_output_a, independent_same_output_b) and bool(route_overlap(independent_same_output_a, independent_same_output_b))
    results["P7.T4.disjoint_output_can_be_dependent"] = (not structurally_independent(dependent_disjoint_a, dependent_disjoint_b)) and not route_overlap(dependent_disjoint_a, dependent_disjoint_b)

    results["P7.T5.fail_closed_positive"] = task_stop_authorized(
        {"coverage": ObligationStatus.SATISFIED, "censored_route": ObligationStatus.VALID_CLOSURE}
    )
    results["P7.T5.fail_closed_censored"] = not task_stop_authorized(
       {"coverage": ObligationStatus.SATISFIED, "censored_route": ObligationStatus.CENSORED}
    )
    results["P7.T5.route_stop_not_task_stop"] = route_stop_authorized(True) and not task_stop_authorized(
        {"route_a": ObligationStatus.SATISFIED, "route_b": ObligationStatus.OPEN}
    )

    results["all_passed"] = all(bool(value) for value in results.values())
    return dict(results)


if __name__ == "__main__":
    import json

    print(json.dumps(run_checks(), indent=2, sort_keys=True))
