#!/usr/bin/env python3
"""Deterministic hostile checks for P8 formal core V1.

This is a small executable model of the paper's structural claims.  It uses no
external package, model, judge, or LLM API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Iterable, Mapping


@dataclass(frozen=True)
class Judgment:
    issuer: str
    domain: str
    scope: FrozenSet[str]
    valid: bool = True


@dataclass(frozen=True)
class Action:
    domain: str
    scope: FrozenSet[str]


def conversion_reachable(
    source: str,
    target: str,
    conversions: FrozenSet[tuple[str, str]],
) -> bool:
    pending = [source]
    seen = {source}
    while pending:
        current = pending.pop()
        if current == target:
            return True
        for left, right in conversions:
            if left == current and right not in seen:
                seen.add(right)
                pending.append(right)
    return False


def authorize(
    judgment: Judgment,
    action: Action,
    *,
    trusted_issuers: FrozenSet[str],
    conversions: FrozenSet[tuple[str, str]],
    hard_obligations: Mapping[str, str],
    active_defeaters: FrozenSet[str] = frozenset(),
) -> bool:
    if not judgment.valid or judgment.issuer not in trusted_issuers:
        return False
    if not action.scope.issubset(judgment.scope):
        return False
    if not conversion_reachable(judgment.domain, action.domain, conversions):
        return False
    if any(status != "SAT" for status in hard_obligations.values()):
        return False
    if active_defeaters:
        return False
    return True


def descendants(
    graph: Mapping[str, FrozenSet[str]],
    roots: Iterable[str],
) -> FrozenSet[str]:
    seen = set(roots)
    pending = list(roots)
    while pending:
        current = pending.pop()
        for child in graph.get(current, frozenset()):
            if child not in seen:
                seen.add(child)
                pending.append(child)
    return frozenset(seen)


def check_no_laundering() -> int:
    domains = (
        "reframe",
        "route_stop",
        "task_stop",
        "map_merge",
        "assert",
        "self_modify",
    )
    trusted = frozenset({"protected-host"})
    obligations = {"hard-1": "SAT"}
    case_count = 0

    for source in domains:
        judgment = Judgment(
            issuer="protected-host",
            domain=source,
            scope=frozenset({"object-1"}),
        )
        for target in domains:
            action = Action(domain=target, scope=frozenset({"object-1"}))
            result = authorize(
                judgment,
                action,
                trusted_issuers=trusted,
                conversions=frozenset(),
                hard_obligations=obligations,
            )
            assert result is (source == target)
            case_count += 1

    # A registered route-stop -> task-stop conversion is possible only when it
    # is explicit; the fixture represents the existence of a sound coverage
    # coercion, not proof that any real coercion is sound.
    route_judgment = Judgment(
        issuer="protected-host",
        domain="route_stop",
        scope=frozenset({"object-1"}),
    )
    task_action = Action(domain="task_stop", scope=frozenset({"object-1"}))
    assert authorize(
        route_judgment,
        task_action,
        trusted_issuers=trusted,
        conversions=frozenset({("route_stop", "task_stop")}),
        hard_obligations={"coverage-certificate": "SAT"},
    )
    assert not authorize(
        route_judgment,
        task_action,
        trusted_issuers=trusted,
        conversions=frozenset({("route_stop", "task_stop")}),
        hard_obligations={"coverage-certificate": "UNKNOWN"},
    )

    return case_count


def check_scope_monotonicity() -> None:
    judgment = Judgment(
        issuer="protected-host",
        domain="assert",
        scope=frozenset({"claim-a", "claim-b"}),
    )
    trusted = frozenset({"protected-host"})
    obligations = {"independent-check": "SAT"}

    assert authorize(
        judgment,
        Action("assert", frozenset({"claim-a"})),
        trusted_issuers=trusted,
        conversions=frozenset(),
        hard_obligations=obligations,
    )
    assert not authorize(
        judgment,
        Action("assert", frozenset({"claim-a", "claim-b", "claim-c"})),
        trusted_issuers=trusted,
        conversions=frozenset(),
        hard_obligations=obligations,
    )


def check_noncompensatory_counterexamples() -> int:
    case_count = 0
    threshold = 100
    positive_weight = 3
    for finite_penalty in range(0, 101):
        count = (threshold + finite_penalty + positive_weight - 1) // positive_weight
        score = count * positive_weight - finite_penalty
        assert score >= threshold
        blocker_active = True
        assert blocker_active
        case_count += 1
    return case_count


def check_revocation() -> None:
    graph = {
        "evidence-A": frozenset({"obligation-A"}),
        "obligation-A": frozenset({"authorization-A"}),
        "evidence-B": frozenset({"authorization-B"}),
        "authorization-A": frozenset(),
        "authorization-B": frozenset(),
    }
    revoked = descendants(graph, {"evidence-A"})
    assert revoked == frozenset({"evidence-A", "obligation-A", "authorization-A"})
    assert "authorization-B" not in revoked


def check_self_authorization_countermodel() -> None:
    candidates = {
        "valid-change": True,
        "harmful-change": False,
        "unverified-change": False,
    }
    candidate_controlled_policy = lambda _candidate: True
    authorized = {
        candidate: candidate_controlled_policy(candidate)
        for candidate in candidates
    }
    assert all(authorized.values())
    assert any(authorized[name] and not external_truth for name, external_truth in candidates.items())


def check_domain_embedding_fixtures() -> None:
    # Toy fixtures verify that the common terminal vocabulary can encode each
    # gate.  Exact equivalence to the real P1-P5 implementations remains an
    # explicit paper obligation.
    fixtures = {
        "P1-reframe": {"responsibility": "SAT", "coordinate-permission": "SAT"},
        "P2-task-stop": {"coverage": "SAT", "censored-routes": "SAT"},
        "P3-merge": {"referent": "SAT", "measurement": "SAT"},
        "P4-assert": {"content-bound-evidence": "SAT", "protected-check": "SAT"},
        "P5-self-modify": {"replay": "SAT", "fresh-transfer": "SAT", "protected-check": "SAT"},
    }
    assert all(all(value == "SAT" for value in obligations.values()) for obligations in fixtures.values())

    blocked = dict(fixtures)
    blocked["P5-self-modify"] = {
        "replay": "SAT",
        "fresh-transfer": "UNKNOWN",
        "protected-check": "SAT",
    }
    assert not all(value == "SAT" for value in blocked["P5-self-modify"].values())


def main() -> int:
    laundering_cases = check_no_laundering()
    check_scope_monotonicity()
    additive_cases = check_noncompensatory_counterexamples()
    check_revocation()
    check_self_authorization_countermodel()
    check_domain_embedding_fixtures()

    print("P8 authority-calculus checks: PASS")
    print(f"  cross-domain no-coercion cases: {laundering_cases}")
    print("  scope narrowing/widening fixtures: confirmed")
    print(f"  finite-penalty additive counterexamples: {additive_cases}")
    print("  dependency revocation fixture: confirmed")
    print("  self-authorization countermodel: confirmed")
    print("  P1-P5 toy embedding fixtures: confirmed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
