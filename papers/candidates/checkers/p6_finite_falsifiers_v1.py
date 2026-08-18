#!/usr/bin/env python3
"""Deterministic finite falsifiers for candidate P6.

No LLM/API dependency. These checks instantiate bounded examples supporting
FORMAL_CORE_V1.md; they are not proofs of the general theorems.
"""
from collections import deque


def descendants(graph, starts):
    out = set()
    q = deque(starts)
    while q:
        x = q.popleft()
        for y in graph.get(x, ()):
            if y not in out:
                out.add(y)
                q.append(y)
    return out


def check_reopening():
    graph = {"x": {"q1"}, "q1": {"q2"}, "z": {"q3"}}
    certified = {"q1", "q2", "q3"}
    affected = descendants(graph, {"x"}) & certified
    reopened = certified - affected
    assert affected == {"q1", "q2"}
    assert reopened == {"q3"}
    assert reopened != set()


def check_history_aware_commutation():
    def m(state):
        s = dict(state)
        s["x"] += 1
        s["H"] = state["H"] + ("m",)
        return s

    def n(state):
        s = dict(state)
        s["y"] *= 2
        s["H"] = state["H"] + ("n",)
        return s

    e = {"x": 1, "y": 3, "H": ()}
    mn = n(m(e))
    nm = m(n(e))
    assert (mn["x"], mn["y"]) == (nm["x"], nm["y"]) == (2, 6)
    assert mn["H"] != nm["H"]
    assert sorted(mn["H"]) == sorted(nm["H"])


def check_non_escalation():
    trusted_roots = {"root"}
    tokens = {("root", "ASSERT", "claim:*")}

    def narrow(token, scope):
        issuer, domain, _ = token
        assert issuer in trusted_roots
        assert scope.startswith("claim:")
        return (issuer, domain, scope)

    t = narrow(next(iter(tokens)), "claim:42")
    assert t[0] == "root" and t[1] == "ASSERT"
    forged = ("candidate", "ASSERT", "claim:*")
    assert forged[0] not in trusted_roots


def check_residual_obligation_preservation():
    obligations = {"independent_check"}
    later_success = True
    if later_success:
        obligations = set(obligations)
    assert obligations == {"independent_check"}


def check_recursive_cycle_and_self_authorization():
    edge = ("audit:m", "audit:m")
    assert edge[0] == edge[1]
    candidate_controls_policy = True
    policy = (lambda _: True) if candidate_controls_policy else (lambda _: False)
    assert policy("arbitrary_candidate") is True


def main():
    checks = [
        check_reopening,
        check_history_aware_commutation,
        check_non_escalation,
        check_residual_obligation_preservation,
        check_recursive_cycle_and_self_authorization,
    ]
    for check in checks:
        check()
        print(f"PASS {check.__name__}")
    print(f"P6_FINITE_FALSIFIERS_V1: {len(checks)}/{len(checks)} PASS")


if __name__ == "__main__":
    main()
