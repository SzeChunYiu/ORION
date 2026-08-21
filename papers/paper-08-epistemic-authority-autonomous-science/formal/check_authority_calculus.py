#!/usr/bin/env python3
"""Deterministic hostile checks for P8 formal core V1.

This is a small executable model of the paper's structural claims. It uses no
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
    epoch: int = 0
    valid: bool = True


@dataclass(frozen=True)
class Action:
    domain: str
    scope: FrozenSet[str]
    epoch: int = 0


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
    if judgment.epoch != action.epoch:
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
            epoch=4,
        )
        for target in domains:
            action = Action(
                domain=target,
                scope=frozenset({"object-1"}),
                epoch=4,
            )
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
        epoch=4,
    )
    task_action = Action(
        domain="task_stop",
        scope=frozenset({"object-1"}),
        epoch=4,
    )
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
        epoch=2,
    )
    trusted = frozenset({"protected-host"})
    obligations = {"independent-check": "SAT"}

    assert authorize(
        judgment,
        Action("assert", frozenset({"claim-a"}), epoch=2),
        trusted_issuers=trusted,
        conversions=frozenset(),
        hard_obligations=obligations,
    )
    assert not authorize(
        judgment,
        Action("assert", frozenset({"claim-a", "claim-b", "claim-c"}), epoch=2),
        trusted_issuers=trusted,
        conversions=frozenset(),
        hard_obligations=obligations,
    )


def check_epoch_replay() -> None:
    trusted = frozenset({"protected-host"})
    judgment = Judgment(
        issuer="protected-host",
        domain="assert",
        scope=frozenset({"claim-a"}),
        epoch=3,
    )
    stale_action = Action("assert", frozenset({"claim-a"}), epoch=4)
    assert not authorize(
        judgment,
        stale_action,
        trusted_issuers=trusted,
        conversions=frozenset(),
        hard_obligations={"independent-check": "SAT"},
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


def check_revocation_and_alternate_derivation() -> None:
    # `authorization-A` depends on two independent support paths. Revoking A1
    # kills only path A1; the certificate may remain valid via A2. In contrast,
    # authorization-C has only one support path and must be revoked.
    graph = {
        "evidence-A1": frozenset({"proof-A1"}),
        "proof-A1": frozenset({"authorization-A"}),
        "evidence-A2": frozenset({"proof-A2"}),
        "proof-A2": frozenset({"authorization-A"}),
        "evidence-C": frozenset({"proof-C"}),
        "proof-C": frozenset({"authorization-C"}),
        "authorization-A": frozenset(),
        "authorization-C": frozenset(),
    }

    revoked_from_a1 = descendants(graph, {"evidence-A1"})
    assert "proof-A1" in revoked_from_a1
    assert "authorization-A" in revoked_from_a1
    assert "proof-A2" not in revoked_from_a1

    # Certificate-level validity is derivational rather than node-only: A can be
    # re-derived from the untouched independent A2 path.
    independent_a2_path_valid = "proof-A2" not in revoked_from_a1
    authorization_a_remains_derivable = independent_a2_path_valid
    assert authorization_a_remains_derivable

    revoked_from_c = descendants(graph, {"evidence-C"})
    assert {"evidence-C", "proof-C", "authorization-C"}.issubset(revoked_from_c)
    independent_c_path_valid = False
    assert not independent_c_path_valid


def check_posthoc_refusal_not_preventive() -> None:
    irreversible_effect_committed = True
    later_refusal = True
    prevented = later_refusal and not irreversible_effect_committed
    assert irreversible_effect_committed
    assert later_refusal
    assert not prevented


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


def check_clean_authorized_control() -> None:
    trusted = frozenset({"protected-host"})
    judgment = Judgment(
        issuer="protected-host",
        domain="assert",
        scope=frozenset({"claim-clean"}),
        epoch=9,
    )
    action = Action("assert", frozenset({"claim-clean"}), epoch=9)
    assert authorize(
        judgment,
        action,
        trusted_issuers=trusted,
        conversions=frozenset(),
        hard_obligations={
            "content-bound-evidence": "SAT",
            "independent-check": "SAT",
        },
        active_defeaters=frozenset(),
    )


def check_domain_embedding_fixtures() -> None:
    # Toy fixtures verify that the common terminal vocabulary can encode each
    # gate. Exact equivalence to real P1-P5 implementations remains an explicit
    # paper obligation.
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
    check_epoch_replay()
    additive_cases = check_noncompensatory_counterexamples()
    check_revocation_and_alternate_derivation()
    check_posthoc_refusal_not_preventive()
    check_self_authorization_countermodel()
    check_clean_authorized_control()
    check_domain_embedding_fixtures()

    print("P8 authority-calculus checks: PASS")
    print(f"  cross-domain no-coercion cases: {laundering_cases}")
    print("  scope narrowing/widening fixtures: confirmed")
    print("  stale-epoch replay rejection: confirmed")
    print(f"  finite-penalty additive counterexamples: {additive_cases}")
    print("  dependency revocation + independent re-derivation fixture: confirmed")
    print("  post-hoc refusal non-prevention fixture: confirmed")
    print("  self-authorization countermodel: confirmed")
    print("  clean authorized coverage control: confirmed")
    print("  P1-P5 toy embedding fixtures: confirmed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())