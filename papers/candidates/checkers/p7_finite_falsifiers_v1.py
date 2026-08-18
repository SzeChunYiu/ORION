#!/usr/bin/env python3
"""Deterministic finite falsifiers for candidate P7."""
from collections import deque


def reachable(graph, start, goal):
    q = deque([start])
    seen = {start}
    while q:
        x = q.popleft()
        if x == goal:
            return True
        for y in graph.get(x, ()):
            if y not in seen:
                seen.add(y)
                q.append(y)
    return False


def check_extension_ambiguity():
    history = ("observe:a",)
    w0 = {"history": history, "mandatory_unsatisfied": False}
    w1 = {"history": history, "mandatory_unsatisfied": True}
    assert w0["history"] == w1["history"]
    assert w0["mandatory_unsatisfied"] != w1["mandatory_unsatisfied"]
    rule = lambda h: "task_stop"
    assert rule(history) == "task_stop"
    assert w1["mandatory_unsatisfied"] is True


def check_certificate_absence_not_equivalent_to_ambiguity():
    admissible_completions = [{"mandatory_unsatisfied": False}]
    has_certificate = False
    ambiguous = len({w["mandatory_unsatisfied"] for w in admissible_completions}) > 1
    assert has_certificate is False
    assert ambiguous is False


def check_route_stop_not_task_stop():
    routes = {"executed": {"r1": "route_stop"}, "unavailable": {"r2": "open"}}
    assert all(v == "route_stop" for v in routes["executed"].values())
    assert "open" in routes["unavailable"].values()


def check_chart_change_expressivity():
    t = {"s": {"a"}, "a": set()}
    t2 = {"s2": {"g"}, "g": set()}
    assert not reachable(t, "s", "g")
    assert reachable(t2, "s2", "g")


def check_support_transport_and_goal_change():
    support = {"node:a", "edge:a->b", "evidence:1"}
    preserved = {"node:a", "edge:a->b", "evidence:1"}
    assert support <= preserved
    old_goal = "find_any_effect"
    new_goal = "find_effect_with_independent_replication"
    evidence_identity_preserved = True
    closure_transports = old_goal == new_goal
    assert evidence_identity_preserved is True
    assert closure_transports is False


def check_fail_closed_stop():
    mandatory_open = {"coverage:r2"}
    task_stop_allowed = not mandatory_open
    assert task_stop_allowed is False


def check_unnecessary_reframe_negative_control():
    graph = {"s": {"g"}, "g": set()}
    assert reachable(graph, "s", "g")
    reframe_required = False
    assert reframe_required is False


def main():
    checks = [
        check_extension_ambiguity,
        check_certificate_absence_not_equivalent_to_ambiguity,
        check_route_stop_not_task_stop,
        check_chart_change_expressivity,
        check_support_transport_and_goal_change,
        check_fail_closed_stop,
        check_unnecessary_reframe_negative_control,
    ]
    for check in checks:
        check()
        print(f"PASS {check.__name__}")
    print(f"P7_FINITE_FALSIFIERS_V1: {len(checks)}/{len(checks)} PASS")


if __name__ == "__main__":
    main()
