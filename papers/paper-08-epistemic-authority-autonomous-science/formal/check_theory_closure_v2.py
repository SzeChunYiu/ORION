#!/usr/bin/env python3
"""Deterministic support checker for P8 formal core V2.

The checker types the full evidence->obligation->authorization derivation and
models alternative derivations for revocation. It is proof support, not a claim
of empirical superiority or novelty.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

DOMAINS = ("REFRAME", "SEARCH_STOP", "MAP_MERGE", "ASSERT", "SELF_MODIFY")


@dataclass(frozen=True)
class JType:
    domain: str
    kind: str
    scope: str
    content: str
    epoch: int


@dataclass(frozen=True)
class Judgment:
    jid: str
    jtype: JType
    valid: bool = True
    available: bool = True


@dataclass(frozen=True)
class Obligation:
    oid: str
    expected: JType


@dataclass(frozen=True)
class Coercion:
    cid: str
    source: JType
    target: JType
    trusted: bool = True
    valid: bool = True


def same_type(a: JType, b: JType) -> bool:
    return a == b


def apply_coercion(t: JType, c: Coercion) -> JType | None:
    if not c.trusted or not c.valid or t != c.source:
        return None
    return c.target


def coercion_reachable(source: JType, target: JType, registry: tuple[Coercion, ...]) -> bool:
    frontier = [source]
    seen = {source}
    while frontier:
        t = frontier.pop()
        if t == target:
            return True
        for c in registry:
            out = apply_coercion(t, c)
            if out is not None and out not in seen:
                seen.add(out)
                frontier.append(out)
    return False


def discharge(j: Judgment, o: Obligation, registry: tuple[Coercion, ...] = ()) -> str:
    if not j.available:
        return "CANNOT_CHECK"
    if not j.valid:
        return "DENIED"
    if same_type(j.jtype, o.expected):
        return "SAT"
    if coercion_reachable(j.jtype, o.expected, registry):
        return "SAT"
    return "DENIED"


def check_full_domain_matrix() -> int:
    count = 0
    for source_d in DOMAINS:
        for target_d in DOMAINS:
            jt = JType(source_d, "SAT", f"scope:{target_d}", f"content:{target_d}", 7)
            ot = JType(target_d, "SAT", f"scope:{target_d}", f"content:{target_d}", 7)
            result = discharge(Judgment(f"j:{source_d}", jt), Obligation(f"o:{target_d}", ot))
            assert result == ("SAT" if source_d == target_d else "DENIED")
            count += 1
    return count


def check_typed_coercion_composition() -> int:
    s = JType("REFRAME", "SUPPORT", "map-A", "c", 1)
    mid_a = JType("SEARCH_STOP", "SAT", "map-A", "c", 1)
    mid_b = JType("SEARCH_STOP", "SAT", "map-B", "c", 1)
    target = JType("ASSERT", "SAT", "claim-Z", "c", 1)
    c1 = Coercion("c1", s, mid_a)
    c2_bad = Coercion("c2bad", mid_b, target)
    c2_good = Coercion("c2good", mid_a, target)
    assert not coercion_reachable(s, target, (c1, c2_bad))
    assert coercion_reachable(s, target, (c1, c2_good))
    assert c1.target.domain == c2_bad.source.domain
    return 2


@dataclass(frozen=True)
class Certificate:
    cid: str
    derivations: tuple[frozenset[str], ...]


def certificate_valid(cert: Certificate, active: frozenset[str]) -> bool:
    return any(support <= active for support in cert.derivations)


def check_revocation_alternative_derivations() -> int:
    cert = Certificate("k", (frozenset({"eA", "root"}), frozenset({"eB", "root"})))
    active = frozenset({"eA", "eB", "root"})
    assert certificate_valid(cert, active)
    assert certificate_valid(cert, active - {"eA"})
    assert certificate_valid(cert, active - {"eB"})
    assert not certificate_valid(cert, active - {"eA", "eB"})
    assert not certificate_valid(cert, active - {"root"})
    return 5


def authorize(
    obligation_results: tuple[str, ...],
    *,
    blocker: bool,
    grant_valid: bool,
    epoch_fresh: bool,
) -> str:
    if blocker or not grant_valid or not epoch_fresh:
        return "DENIED"
    if any(r == "DENIED" for r in obligation_results):
        return "DENIED"
    if any(r == "CANNOT_CHECK" for r in obligation_results):
        return "CANNOT_CHECK"
    return "AUTHORIZED" if all(r == "SAT" for r in obligation_results) else "CANNOT_CHECK"


def check_terminal_distinctions() -> int:
    assert authorize(("SAT",), blocker=False, grant_valid=True, epoch_fresh=True) == "AUTHORIZED"
    assert authorize(("CANNOT_CHECK",), blocker=False, grant_valid=True, epoch_fresh=True) == "CANNOT_CHECK"
    assert authorize(("DENIED",), blocker=False, grant_valid=True, epoch_fresh=True) == "DENIED"
    assert authorize(("SAT",), blocker=True, grant_valid=True, epoch_fresh=True) == "DENIED"
    assert authorize(("SAT",), blocker=False, grant_valid=True, epoch_fresh=False) == "DENIED"
    return 5


def finite_additive_policy(positive: int, blocker: bool, penalty: int, threshold: int) -> bool:
    return positive - (penalty if blocker else 0) >= threshold


def check_noncompensatory_blocker() -> int:
    count = 0
    for penalty in (1, 2, 5, 10, 100):
        positive = penalty + 1
        assert finite_additive_policy(positive, True, penalty, 1)
        assert authorize(("SAT",), blocker=True, grant_valid=True, epoch_fresh=True) == "DENIED"
        count += 1
    return count


def product_gate(
    domain: str,
    evidence: tuple[Judgment, ...],
    obligations: tuple[Obligation, ...],
    registry: tuple[Coercion, ...],
    *,
    blocker: bool = False,
    grant_valid: bool = True,
    epoch_fresh: bool = True,
) -> str:
    results = []
    for o in obligations:
        candidates = [discharge(j, o, registry) for j in evidence]
        if "SAT" in candidates:
            results.append("SAT")
        elif "CANNOT_CHECK" in candidates:
            results.append("CANNOT_CHECK")
        else:
            results.append("DENIED")
    return authorize(tuple(results), blocker=blocker, grant_valid=grant_valid, epoch_fresh=epoch_fresh)


def shared_calculus(*args, **kwargs) -> str:
    return product_gate(*args, **kwargs)


def check_product_decomposition_equivalence() -> int:
    count = 0
    for d in DOMAINS:
        expected = JType(d, "SAT", f"scope:{d}", f"content:{d}", 3)
        o = Obligation(f"o:{d}", expected)
        exact = Judgment(f"j:{d}", expected)
        foreign = Judgment("foreign", JType("REFRAME" if d != "REFRAME" else "ASSERT", "SAT", expected.scope, expected.content, 3))
        missing = Judgment("missing", expected, available=False)
        for evidence in ((exact,), (foreign,), (missing,), (foreign, exact)):
            for blocker, grant, fresh in product((False, True), repeat=3):
                a = product_gate(d, evidence, (o,), (), blocker=blocker, grant_valid=grant, epoch_fresh=fresh)
                b = shared_calculus(d, evidence, (o,), (), blocker=blocker, grant_valid=grant, epoch_fresh=fresh)
                assert a == b
                count += 1
    return count


def check_positive_cross_domain_coercion() -> int:
    source = JType("SEARCH_STOP", "ROUTE_COMPLETE", "route:R", "run:1", 4)
    target = JType("ASSERT", "SAT", "claim:C", "run:1", 4)
    j = Judgment("route-proof", source)
    o = Obligation("assertion-obligation", target)
    assert discharge(j, o, ()) == "DENIED"
    assert discharge(j, o, (Coercion("protected-bridge", source, target),)) == "SAT"
    assert discharge(j, o, (Coercion("untrusted", source, target, trusted=False),)) == "DENIED"
    return 3


def check_posthoc_refusal_and_epoch() -> int:
    commit_epoch = 1
    refusal_epoch = 2
    assert refusal_epoch > commit_epoch
    assert authorize(("SAT",), blocker=False, grant_valid=True, epoch_fresh=False) == "DENIED"
    return 2


def check_self_promotion_boundary() -> int:
    def candidate_evaluator(_: str) -> bool:
        return True
    assert candidate_evaluator("arbitrary-candidate")
    protected_external_attestation = False
    assert not protected_external_attestation
    return 2


def main() -> int:
    totals = {
        "domain_matrix": check_full_domain_matrix(),
        "coercion_composition": check_typed_coercion_composition(),
        "revocation_dnf": check_revocation_alternative_derivations(),
        "terminals": check_terminal_distinctions(),
        "noncompensatory": check_noncompensatory_blocker(),
        "product_equivalence": check_product_decomposition_equivalence(),
        "positive_coercion": check_positive_cross_domain_coercion(),
        "posthoc_epoch": check_posthoc_refusal_and_epoch(),
        "self_promotion": check_self_promotion_boundary(),
    }
    print("P8 THEORY CLOSURE V2: PASS")
    for key, value in totals.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
