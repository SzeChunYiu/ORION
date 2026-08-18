#!/usr/bin/env python3
"""Deterministic finite falsifiers for candidate P8."""
from collections import deque


def has_coercion_path(coercions, src, dst):
    if src == dst:
        return True
    q = deque([src])
    seen = {src}
    while q:
        d = q.popleft()
        for nxt in coercions.get(d, ()):
            if nxt == dst:
                return True
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return False


def check_no_authority_laundering():
    c = {"SEARCH_STOP": set(), "ASSERT": set()}
    assert not has_coercion_path(c, "SEARCH_STOP", "ASSERT")
    c["SEARCH_STOP"].add("ASSERT")
    assert has_coercion_path(c, "SEARCH_STOP", "ASSERT")


def check_scope_narrowing_not_widening():
    grant = {"claim:1", "claim:2"}
    narrow = {"claim:1"}
    widen = {"claim:1", "claim:2", "claim:3"}
    assert narrow <= grant
    assert not (widen <= grant)


def check_absolute_blocker_counterexample():
    theta, penalty, positive_weight = 10, 7, 2
    n = (theta + penalty + positive_weight - 1) // positive_weight
    score = n * positive_weight - penalty
    assert score >= theta


def descendants(graph, start):
    out = set()
    q = deque([start])
    while q:
        x = q.popleft()
        for y in graph.get(x, ()):
            if y not in out:
                out.add(y)
                q.append(y)
    return out


def check_dependency_revocation_with_independent_derivation():
    graph = {"e1": {"k1"}, "e2": {"k2"}}
    revoked = descendants(graph, "e1") | {"e1"}
    assert "k1" in revoked
    assert "k2" not in revoked


def check_epoch_replay_and_posthoc_refusal():
    cert_epoch, current_epoch = 3, 4
    assert cert_epoch != current_epoch
    effect_committed = True
    later_abstain = True
    preventive = not effect_committed and later_abstain
    assert preventive is False


def check_self_promotion_countermodel():
    candidate_controls_policy = True
    admission = (lambda _: True) if candidate_controls_policy else (lambda _: False)
    assert admission("unsafe_candidate") is True


def check_clean_authorized_control():
    hard = {"scope", "evidence", "independent_check"}
    satisfied = {"scope", "evidence", "independent_check"}
    blockers = set()
    assert hard <= satisfied and not blockers


def main():
    checks = [
        check_no_authority_laundering,
        check_scope_narrowing_not_widening,
        check_absolute_blocker_counterexample,
        check_dependency_revocation_with_independent_derivation,
        check_epoch_replay_and_posthoc_refusal,
        check_self_promotion_countermodel,
        check_clean_authorized_control,
    ]
    for check in checks:
        check()
        print(f"PASS {check.__name__}")
    print(f"P8_FINITE_FALSIFIERS_V1: {len(checks)}/{len(checks)} PASS")


if __name__ == "__main__":
    main()
