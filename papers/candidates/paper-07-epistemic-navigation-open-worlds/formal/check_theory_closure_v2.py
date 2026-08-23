#!/usr/bin/env python3
"""Deterministic support checker for P7 formal core V2.

Standard-library only. These finite witnesses support theorem boundaries; they
are not empirical claims about real search agents.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Completion:
    observed_history: tuple[str, ...]
    mandatory_satisfied: bool
    hidden_witness: str | None = None


def observationally_equivalent(a: Completion, b: Completion) -> bool:
    return a.observed_history == b.observed_history


def extension_ambiguous(completions: tuple[Completion, ...]) -> bool:
    return any(
        observationally_equivalent(a, b)
        and a.mandatory_satisfied != b.mandatory_satisfied
        for a in completions
        for b in completions
    )


def check_stopping_impossibility() -> int:
    h = ("query:q", "result:empty")
    complete = Completion(h, True, None)
    incomplete = Completion(h, False, "hidden-relevant")
    assert extension_ambiguous((complete, incomplete))
    for decision in ("TASK_STOP", "CONTINUE", "CANNOT_CHECK"):
        if decision == "TASK_STOP":
            assert incomplete.mandatory_satisfied is False
        else:
            assert complete.mandatory_satisfied is True
    return 3


def check_certificate_absence_not_ambiguity() -> int:
    singleton = (Completion(("manifest:closed-world",), True, None),)
    assert not extension_ambiguous(singleton)
    rich = (
        Completion(("query:q", "result:empty"), True, None),
        Completion(("query:q", "result:empty"), False, "unseen"),
    )
    assert extension_ambiguous(rich)
    return 2


STATES = ("s0", "s1")
ACTIONS = ("a0", "a1")
RAW = {"s0": ("shared", "bit0"), "s1": ("shared", "bit1")}


def old_obs(state: str) -> str:
    return RAW[state][0]


def new_obs(state: str) -> tuple[str, str]:
    return RAW[state]


def success(state: str, action: str) -> bool:
    return (state, action) in {("s0", "a0"), ("s1", "a1")}


def old_chart_policies():
    for action in ACTIONS:
        yield {"shared": action}


def check_representation_refinement_strictness() -> int:
    for policy in old_chart_policies():
        wins = [success(s, policy[old_obs(s)]) for s in STATES]
        assert not all(wins)
    refined = {
        ("shared", "bit0"): "a0",
        ("shared", "bit1"): "a1",
    }
    assert all(success(s, refined[new_obs(s)]) for s in STATES)
    assert set(RAW) == set(STATES)
    return 3


def check_harmful_coarsening() -> int:
    refined = {new_obs(s): ("a0" if s == "s0" else "a1") for s in STATES}
    assert all(success(s, refined[new_obs(s)]) for s in STATES)
    for action in ACTIONS:
        assert not all(success(s, action) for s in STATES)
    return 3


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    proposition: str
    value: float


@dataclass(frozen=True)
class Obligation:
    obligation_id: str
    predicate: str
    threshold: float

    def satisfied_by(self, e: Evidence) -> bool:
        if e.proposition != self.predicate:
            return False
        return e.value > self.threshold


def check_evidence_not_closure_transport() -> int:
    e = Evidence("e1", "x", 5.0)
    old = Obligation("o_old", "x", 3.0)
    new = Obligation("o_new", "x", 7.0)
    assert old.satisfied_by(e)
    assert not new.satisfied_by(e)
    return 1


@dataclass(frozen=True)
class Transport:
    maps_support: bool
    preserves_semantics: bool
    maps_obligation: bool
    preserves_satisfaction_meaning: bool
    preserves_evidence_identity: bool
    excludes_new_defeater: bool

    @property
    def complete(self) -> bool:
        return all((
            self.maps_support,
            self.preserves_semantics,
            self.maps_obligation,
            self.preserves_satisfaction_meaning,
            self.preserves_evidence_identity,
            self.excludes_new_defeater,
        ))


def transfer_terminal(t: Transport, *, target_ambiguous_if_missing: bool) -> str:
    if t.complete:
        return "TRANSFER_CLOSURE"
    return "REOPEN" if target_ambiguous_if_missing else "CANNOT_CHECK"


def check_support_transport() -> int:
    count = 0
    for bits in product((False, True), repeat=6):
        t = Transport(*bits)
        good = transfer_terminal(t, target_ambiguous_if_missing=True)
        if t.complete:
            assert good == "TRANSFER_CLOSURE"
        else:
            assert good == "REOPEN"
            assert transfer_terminal(t, target_ambiguous_if_missing=False) == "CANNOT_CHECK"
        count += 1
    return count


def task_terminal(
    *,
    route_exhausted: bool,
    mandatory_open: bool,
    censored_unknown: bool,
    budget_exhausted: bool,
) -> str:
    if mandatory_open or censored_unknown:
        if budget_exhausted:
            return "CANNOT_CHECK"
        return "CONTINUE"
    if route_exhausted:
        return "ROUTE_STOP"
    return "TASK_STOP"


def check_stop_terminals() -> int:
    assert task_terminal(route_exhausted=True, mandatory_open=True, censored_unknown=False, budget_exhausted=False) == "CONTINUE"
    assert task_terminal(route_exhausted=True, mandatory_open=False, censored_unknown=False, budget_exhausted=False) == "ROUTE_STOP"
    assert task_terminal(route_exhausted=False, mandatory_open=False, censored_unknown=False, budget_exhausted=False) == "TASK_STOP"
    assert task_terminal(route_exhausted=True, mandatory_open=True, censored_unknown=True, budget_exhausted=True) == "CANNOT_CHECK"
    return 4


@dataclass(frozen=True)
class RouteStructure:
    chart: str
    objective: str
    nodes: frozenset[str]
    edges: frozenset[tuple[str, str]]
    initial_obligations: frozenset[str]
    normalized_trace: tuple[str, ...]
    terminal_semantics: tuple[str, ...]


def structurally_equivalent(
    source: RouteStructure,
    target: RouteStructure,
    renaming: dict[str, str],
) -> bool:
    return (
        {renaming[node] for node in source.nodes} == set(target.nodes)
        and {(renaming[a], renaming[b]) for a, b in source.edges} == set(target.edges)
        and source.objective == target.objective
        and source.initial_obligations == target.initial_obligations
        and tuple(renaming[node] for node in source.normalized_trace) == target.normalized_trace
        and source.terminal_semantics == target.terminal_semantics
    )


def route_refines(
    coarse: RouteStructure,
    fine: RouteStructure,
    projection: dict[str, str],
) -> bool:
    return (
        {projection[node] for node in fine.nodes} == set(coarse.nodes)
        and {(projection[a], projection[b]) for a, b in fine.edges} == set(coarse.edges)
        and fine.objective == coarse.objective
        and fine.initial_obligations == coarse.initial_obligations
        and tuple(projection[node] for node in fine.normalized_trace) == coarse.normalized_trace
        and fine.terminal_semantics == coarse.terminal_semantics
    )


def check_route_relations() -> int:
    terminals = ("ROUTE_STOP", "TASK_STOP", "CANNOT_CHECK")
    original = RouteStructure(
        "coarse",
        "objective-1",
        frozenset({"a", "b"}),
        frozenset({("a", "b")}),
        frozenset({"o"}),
        ("a", "b"),
        terminals,
    )
    renamed = RouteStructure(
        "renamed",
        "objective-1",
        frozenset({"x", "y"}),
        frozenset({("x", "y")}),
        frozenset({"o"}),
        ("x", "y"),
        terminals,
    )
    assert structurally_equivalent(original, renamed, {"a": "x", "b": "y"})

    refined = RouteStructure(
        "fine",
        "objective-1",
        frozenset({"a0", "a1", "b"}),
        frozenset({("a0", "b"), ("a1", "b")}),
        frozenset({"o"}),
        ("a0", "b"),
        terminals,
    )
    assert route_refines(original, refined, {"a0": "a", "a1": "a", "b": "b"})

    changed_obligation = RouteStructure(
        original.chart,
        original.objective,
        original.nodes,
        original.edges,
        frozenset({"different"}),
        original.normalized_trace,
        terminals,
    )
    assert not structurally_equivalent(original, changed_obligation, {"a": "a", "b": "b"})
    assert not route_refines(original, changed_obligation, {"a": "a", "b": "b"})
    return 4


def recovery_transition(
    *,
    open_obligation: bool,
    dead_end_or_loop: bool,
    alternative_frontier: bool,
    revisit_trigger: bool,
    current_chart_can_resolve: bool,
    candidate_chart_expresses_need: bool,
) -> str:
    if not open_obligation:
        return "TASK_STOP"
    if not current_chart_can_resolve and candidate_chart_expresses_need:
        return "REFRAME"
    if revisit_trigger:
        return "DEFER_REVISIT"
    if dead_end_or_loop and alternative_frontier:
        return "BACKTRACK"
    return "CANNOT_CHECK"


def check_recovery_transitions() -> int:
    common = {
        "open_obligation": True,
        "dead_end_or_loop": False,
        "alternative_frontier": False,
        "revisit_trigger": False,
        "current_chart_can_resolve": True,
        "candidate_chart_expresses_need": False,
    }
    assert recovery_transition(**(common | {"open_obligation": False})) == "TASK_STOP"
    assert recovery_transition(
        **(common | {"current_chart_can_resolve": False, "candidate_chart_expresses_need": True})
    ) == "REFRAME"
    assert recovery_transition(**(common | {"revisit_trigger": True})) == "DEFER_REVISIT"
    assert recovery_transition(
        **(common | {"dead_end_or_loop": True, "alternative_frontier": True})
    ) == "BACKTRACK"
    assert recovery_transition(**(common | {"dead_end_or_loop": True})) == "CANNOT_CHECK"
    return 5


def check_fixed_chart_special_case() -> int:
    states = ("u", "v")
    edges = {("u", "v")}
    identity = {s: s for s in states}
    assert {(identity[a], identity[b]) for a, b in edges} == edges
    return 1


def main() -> int:
    totals = {
        "stopping_impossibility": check_stopping_impossibility(),
        "certificate_boundary": check_certificate_absence_not_ambiguity(),
        "representation_refinement": check_representation_refinement_strictness(),
        "harmful_coarsening": check_harmful_coarsening(),
        "evidence_vs_closure": check_evidence_not_closure_transport(),
        "support_transport": check_support_transport(),
        "stop_terminals": check_stop_terminals(),
        "route_relations": check_route_relations(),
        "recovery_transitions": check_recovery_transitions(),
        "fixed_chart_special_case": check_fixed_chart_special_case(),
    }
    print("P7 THEORY CLOSURE V2: PASS")
    for key, value in totals.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
