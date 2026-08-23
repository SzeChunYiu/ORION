"""Focused assumption-regression checks for ORION candidate Paper 6 V2.

This addendum complements, rather than replaces, the exhaustive V1 checker.
It freezes counterexamples for theorem assumptions that finite graph enumeration
alone cannot establish: path realizability, footprint fidelity, history-aware
commutation, non-escalation, recursion, and protected authority roots.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Dict, FrozenSet, Iterable, Mapping, MutableMapping, Sequence, Set, Tuple

StatusMap = Dict[str, str]
Edge = Tuple[str, str]
State = Dict[str, int]

CERTIFIED = "certified"
OPEN = "open"
CANNOT_CHECK = "cannot_check"


def descendants(edges: Iterable[Edge], seeds: Iterable[str]) -> Set[str]:
    adjacency: Dict[str, Set[str]] = {}
    for source, target in edges:
        adjacency.setdefault(source, set()).add(target)
    seen: Set[str] = set()
    frontier = list(seeds)
    while frontier:
        current = frontier.pop()
        for nxt in adjacency.get(current, set()):
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    return seen


def selective_reopen(
    statuses: Mapping[str, str],
    edges: Iterable[Edge],
    changed: Iterable[str],
    unavailable_support: Iterable[str] = (),
) -> StatusMap:
    """Reopen certified descendants and preserve unrelated statuses."""
    reopened = dict(statuses)
    affected = descendants(edges, changed)
    unavailable = set(unavailable_support)
    for claim in affected:
        if reopened.get(claim) == CERTIFIED:
            reopened[claim] = CANNOT_CHECK if claim in unavailable else OPEN
    return reopened


def reopening_is_sound(
    after: Mapping[str, str], potentially_invalidated: Iterable[str]
) -> bool:
    """Finite witness check for Theorem P6.T1's conclusion."""
    return all(after.get(claim) != CERTIFIED for claim in potentially_invalidated)


def minimality_witness(
    edges: Iterable[Edge], changed: Iterable[str], retained_certified: str
) -> bool:
    """Return True when a retained descendant admits a path-realizable countermodel.

    This function captures the added assumption in P6 V2: every descendant path
    may be semantically necessary in at least one admissible witness semantics.
    Under that robust interpretation, leaving any descendant certified is unsafe.
    """
    return retained_certified in descendants(edges, changed)


@dataclass(frozen=True)
class Mechanic:
    name: str
    read: FrozenSet[str]
    write: FrozenSet[str]
    transition: Callable[[Mapping[str, int]], Mapping[str, int]]

    def apply(self, state: Mapping[str, int]) -> State:
        proposal = dict(self.transition({key: state[key] for key in self.read}))
        if not set(proposal).issubset(self.write):
            raise ValueError(f"{self.name} wrote outside declared footprint")
        result = dict(state)
        result.update(proposal)
        return result


def strongly_separated(left: Mechanic, right: Mechanic) -> bool:
    return not (
        left.write.intersection(right.read.union(right.write))
        or right.write.intersection(left.read.union(left.write))
    )


def commute_on_scientific_projection(
    left: Mechanic, right: Mechanic, state: Mapping[str, int]
) -> bool:
    """Check current-state equality; ordered audit histories are handled separately."""
    if not strongly_separated(left, right):
        return False
    return right.apply(left.apply(state)) == left.apply(right.apply(state))


def independent_ordered_histories(left: Mechanic, right: Mechanic) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    """Return distinct histories that are equivalent under one independent swap."""
    return ((left.name, right.name), (right.name, left.name))


def trace_equivalent_by_independent_swap(
    first: Tuple[str, ...], second: Tuple[str, ...], independent: FrozenSet[FrozenSet[str]]
) -> bool:
    if first == second:
        return True
    if len(first) != 2 or len(second) != 2 or first != tuple(reversed(second)):
        return False
    return frozenset(first) in independent


def exhaustive_commutation_check(
    left: Mechanic, right: Mechanic, coordinates: Sequence[str]
) -> bool:
    for values in product((0, 1), repeat=len(coordinates)):
        state = dict(zip(coordinates, values))
        if not commute_on_scientific_projection(left, right, state):
            return False
    return True


@dataclass(frozen=True)
class AuthorityToken:
    issuer: str
    domain: str
    scope: FrozenSet[str]
    root: str


def is_narrowing(candidate: AuthorityToken, parent: AuthorityToken) -> bool:
    return (
        candidate.root == parent.root
        and candidate.domain == parent.domain
        and candidate.scope.issubset(parent.scope)
    )


def step_is_non_escalating(
    before: FrozenSet[AuthorityToken],
    after: FrozenSet[AuthorityToken],
    trusted_roots: FrozenSet[str],
) -> bool:
    for token in after:
        if token in before:
            continue
        if token.root in trusted_roots and token.issuer in trusted_roots:
            continue
        if any(is_narrowing(token, parent) for parent in before):
            continue
        return False
    return True


def trace_is_non_escalating(
    trace: Sequence[FrozenSet[AuthorityToken]], trusted_roots: FrozenSet[str]
) -> bool:
    return all(
        step_is_non_escalating(before, after, trusted_roots)
        for before, after in zip(trace, trace[1:])
    )


def rank_decreases(call_edges: Iterable[Edge], rank: Mapping[str, int]) -> bool:
    return all(rank[child] < rank[parent] for parent, child in call_edges)


def contains_cycle(edges: Iterable[Edge]) -> bool:
    adjacency: Dict[str, Set[str]] = {}
    nodes: Set[str] = set()
    for source, target in edges:
        adjacency.setdefault(source, set()).add(target)
        nodes.update((source, target))

    white, grey, black = 0, 1, 2
    colour = {node: white for node in nodes}

    def visit(node: str) -> bool:
        colour[node] = grey
        for nxt in adjacency.get(node, set()):
            if colour[nxt] == grey:
                return True
            if colour[nxt] == white and visit(nxt):
                return True
        colour[node] = black
        return False

    return any(colour[node] == white and visit(node) for node in nodes)


def self_authorization_countermodel(candidate_controls_policy: bool, candidate_controls_evidence: bool) -> bool:
    """Witness the constant-accept policy when both authority inputs are writable."""
    return candidate_controls_policy and candidate_controls_evidence


def evaluate_countermodel_case(case: Mapping[str, object]) -> str:
    """Evaluate a frozen hostile configuration against the reference rules."""
    kind = str(case.get("kind", ""))
    detected = False
    if kind == "stale_certification":
        detected = bool(case.get("path_realizable")) and bool(case.get("retained_descendant"))
    elif kind == "undeclared_write":
        detected = not set(case.get("proposed_write", [])).issubset(set(case.get("declared_write", [])))
    elif kind == "nonseparated_composition":
        detected = bool(set(case.get("left_write", [])).intersection(set(case.get("right_read", []))))
    elif kind == "authority_escalation":
        detected = (
            case.get("candidate_root") != case.get("trusted_root")
            and not bool(case.get("scope_narrowing"))
        )
    elif kind == "recursive_cycle":
        edges = {(str(left), str(right)) for left, right in case.get("call_edges", [])}
        detected = contains_cycle(edges)
    elif kind == "self_authorization":
        detected = self_authorization_countermodel(
            bool(case.get("candidate_controls_policy")),
            bool(case.get("candidate_controls_evidence")),
        )
    else:
        raise ValueError(f"unknown countermodel kind: {kind}")
    return "DETECTED" if detected else "NOT_DETECTED"


def validate_countermodel_case(case: Mapping[str, object]) -> Tuple[bool, str]:
    required = {"id", "kind", "expected_verdict"}
    missing = required - set(case)
    if missing:
        return False, f"missing fields: {sorted(missing)}"
    if case["expected_verdict"] not in {"DETECTED", "NOT_DETECTED"}:
        return False, "invalid expected_verdict"
    try:
        actual = evaluate_countermodel_case(case)
    except (TypeError, ValueError) as exc:
        return False, str(exc)
    if actual != case["expected_verdict"]:
        return False, f"verdict mismatch: evaluator={actual}, expected={case['expected_verdict']}"
    return True, "ok"


def run_checks() -> dict:
    results: MutableMapping[str, object] = {}

    edges = {("x", "q1"), ("q1", "q2"), ("z", "q3")}
    statuses = {"q1": CERTIFIED, "q2": CERTIFIED, "q3": CERTIFIED}
    reopened = selective_reopen(statuses, edges, {"x"})
    results["P6.T1.downstream_reopening"] = reopening_is_sound(reopened, {"q1", "q2"}) and reopened["q3"] == CERTIFIED
    results["P6.T2.path_realizable_minimality"] = minimality_witness(edges, {"x"}, "q2")

    left = Mechanic(
        "left",
        frozenset({"a"}),
        frozenset({"b"}),
        lambda local: {"b": 1 - local["a"]},
    )
    right = Mechanic(
        "right",
        frozenset({"c"}),
        frozenset({"d"}),
        lambda local: {"d": local["c"]},
    )
    results["P6.T3.scientific_projection_commutation"] = exhaustive_commutation_check(
        left, right, ("a", "b", "c", "d")
    )
    history_lr, history_rl = independent_ordered_histories(left, right)
    results["P6.T3.ordered_histories_distinct"] = history_lr != history_rl
    results["P6.T3.histories_trace_equivalent"] = trace_equivalent_by_independent_swap(
        history_lr, history_rl, frozenset({frozenset({left.name, right.name})})
    )

    root = AuthorityToken("host", "assert", frozenset({"claim", "metadata"}), "host")
    narrowed = AuthorityToken("agent", "assert", frozenset({"claim"}), "host")
    forged = AuthorityToken("agent", "self_modify", frozenset({"registry"}), "agent")
    results["P6.T4.sequential_non_escalation_positive"] = trace_is_non_escalating(
        (frozenset({root}), frozenset({root, narrowed}), frozenset({narrowed})),
        frozenset({"host"}),
    )
    results["P6.T4.sequential_non_escalation_hostile"] = not trace_is_non_escalating(
        (frozenset({root}), frozenset({root, forged})), frozenset({"host"})
    )

    acyclic_calls = {("root", "child"), ("child", "leaf")}
    cyclic_calls = {("root", "root")}
    results["P6.T5.rank_descent_termination"] = rank_decreases(acyclic_calls, {"root": 2, "child": 1, "leaf": 0}) and not contains_cycle(acyclic_calls)
    results["P6.T5.missing_descent_countermodel"] = contains_cycle(cyclic_calls)
    results["P6.T6.self_authorization_countermodel"] = self_authorization_countermodel(True, True)

    results["all_passed"] = all(bool(value) for value in results.values())
    return dict(results)


if __name__ == "__main__":
    import json

    print(json.dumps(run_checks(), indent=2, sort_keys=True))
