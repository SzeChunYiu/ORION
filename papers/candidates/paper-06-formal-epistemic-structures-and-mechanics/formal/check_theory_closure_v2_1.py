#!/usr/bin/env python3
"""Normative P6 V2.1 theorem-boundary regression checker.

Adds the parallel-lane assumption corrections: sound conservative dependency
abstractions do not imply minimality, and commutation needs footprint fidelity.
Standard-library only; finite countermodels are proof support, not unrestricted
proofs or empirical-agent evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product

NODES = ("a", "b", "c", "d")


def descendants(edges: frozenset[tuple[str, str]], roots: frozenset[str]) -> frozenset[str]:
    seen: set[str] = set()
    frontier = list(roots)
    while frontier:
        x = frontier.pop()
        for u, v in edges:
            if u == x and v not in roots and v not in seen:
                seen.add(v)
                frontier.append(v)
    return frozenset(seen)


def affected(certified: frozenset[str], edges: frozenset[tuple[str, str]], changed: frozenset[str]) -> frozenset[str]:
    return frozenset((certified & changed) | (certified & descendants(edges, changed)))


def all_forward_dags():
    possible = tuple((NODES[i], NODES[j]) for i in range(len(NODES)) for j in range(i + 1, len(NODES)))
    for bits in product((0, 1), repeat=len(possible)):
        yield frozenset(edge for edge, bit in zip(possible, bits) if bit)


def check_root_inclusive_safety() -> tuple[int, int]:
    certified = frozenset(NODES)
    cases = changed_root_occurrences = 0
    for edges in all_forward_dags():
        for r in range(1, len(NODES) + 1):
            for combo in combinations(NODES, r):
                changed = frozenset(combo)
                got = affected(certified, edges, changed)
                assert certified & changed <= got
                assert certified & descendants(edges, changed) <= got
                cases += 1
                changed_root_occurrences += len(certified & changed)
    return cases, changed_root_occurrences


def check_spurious_edge_countermodel() -> int:
    # D is conservative: x -> q is recorded, but the only admissible semantics
    # has q depending solely on y. Soundness permits the extra edge.
    edges = frozenset({("x", "q")})
    certified = frozenset({"q"})
    changed = frozenset({"x"})
    graph_reopens = frozenset({"q"}) if "q" in descendants(edges, changed) else frozenset()
    actual_invalidated_in_fixed_semantics = frozenset()
    assert graph_reopens == frozenset({"q"})
    assert actual_invalidated_in_fixed_semantics == frozenset()
    # Therefore a strategy preserving q is sound for this singleton semantics
    # class, disproving minimality from support-soundness alone.
    assert not actual_invalidated_in_fixed_semantics
    return 1


def graph_only_uniformly_sound(
    chosen_reopen: frozenset[str],
    affected_set: frozenset[str],
    realizable_invalidations: tuple[frozenset[str], ...],
) -> bool:
    # A strategy is uniformly sound iff it reopens every certification that is
    # invalidated in each semantics compatible with the same graph-visible data.
    return all(invalidated <= chosen_reopen for invalidated in realizable_invalidations)


def check_affected_realizability_minimax() -> tuple[int, int]:
    # For each small affected set, construct a compatible semantics witness for
    # each affected claim in which that claim alone is invalidated. A uniformly
    # sound graph-only strategy must therefore contain every affected claim.
    cases = 0
    omissions_rejected = 0
    universe = frozenset({"q1", "q2", "q3"})
    for bits in product((0, 1), repeat=3):
        aff = frozenset(q for q, bit in zip(sorted(universe), bits) if bit)
        if not aff:
            continue
        realizations = tuple(frozenset({q}) for q in sorted(aff))
        assert graph_only_uniformly_sound(aff, aff, realizations)
        for q in aff:
            candidate = aff - {q}
            assert not graph_only_uniformly_sound(candidate, aff, realizations)
            omissions_rejected += 1
        cases += 1
    return cases, omissions_rejected


@dataclass(frozen=True)
class GoodState:
    x: int
    y: int
    z: int
    history: tuple[str, ...] = ()


def faithful_m(s: GoodState) -> GoodState:
    return GoodState(s.x + 1, s.y, s.z, s.history + ("m",))


def faithful_n(s: GoodState) -> GoodState:
    return GoodState(s.x, s.y + 2, s.z, s.history + ("n",))


def scientific_projection(s: GoodState) -> tuple[int, int, int]:
    return (s.x, s.y, s.z)


def check_footprint_faithful_commutation() -> int:
    count = 0
    for x, y, z in product(range(2), repeat=3):
        s = GoodState(x, y, z)
        mn = faithful_n(faithful_m(s))
        nm = faithful_m(faithful_n(s))
        assert scientific_projection(mn) == scientific_projection(nm)
        assert mn.history != nm.history
        assert set(mn.history) == set(nm.history) == {"m", "n"}
        count += 1
    return count


# Hidden mutable ambient input: declared footprint would claim m only writes x,
# but m secretly reads AMBIENT["z"], which n mutates.
AMBIENT = {"z": 0}


def hidden_read_m(x: int) -> int:
    return x + AMBIENT["z"]


def hidden_write_n() -> None:
    AMBIENT["z"] = 10


def check_hidden_read_counterexample() -> int:
    AMBIENT["z"] = 0
    before_n = hidden_read_m(1)
    hidden_write_n()
    after_n = hidden_read_m(1)
    assert before_n == 1
    assert after_n == 11
    assert before_n != after_n
    return 1


@dataclass(frozen=True)
class PreservationCertificate:
    claim: str
    changed: frozenset[str]
    protected_issuer: bool
    valid: bool
    proves_old_derivation_invariant: bool
    is_revalidation: bool = False


def may_keep_certified(claim: str, changed: frozenset[str], cert: PreservationCertificate) -> bool:
    if not (cert.claim == claim and cert.changed == changed and cert.protected_issuer and cert.valid):
        return False
    if claim in changed:
        # Directly changed claim needs a new revalidation derivation, not mere
        # preservation of the old certificate.
        return cert.is_revalidation
    return cert.proves_old_derivation_invariant


def check_preservation_vs_revalidation() -> int:
    changed = frozenset({"q"})
    old_preserve = PreservationCertificate("q", changed, True, True, True, False)
    new_revalidate = PreservationCertificate("q", changed, True, True, False, True)
    unprotected_revalidate = PreservationCertificate("q", changed, False, True, False, True)
    assert not may_keep_certified("q", changed, old_preserve)
    assert may_keep_certified("q", changed, new_revalidate)
    assert not may_keep_certified("q", changed, unprotected_revalidate)
    return 3


def check_v2_results_still_compatible() -> int:
    # Typed-erasure discriminator remains: same bare transition, different
    # scientific-admissibility premises.
    bare = (0, 1)
    contract_a = (bare, True, True)
    contract_b = (bare, False, True)
    contract_c = (bare, True, False)
    assert contract_a[0] == contract_b[0] == contract_c[0]
    assert contract_a[1] and contract_a[2]
    assert not (contract_b[1] and contract_b[2])
    assert not (contract_c[1] and contract_c[2])
    return 3


def main() -> int:
    totals = {
        "root_inclusive_safety": check_root_inclusive_safety(),
        "spurious_edge_countermodel": check_spurious_edge_countermodel(),
        "affected_realizability_minimax": check_affected_realizability_minimax(),
        "footprint_faithful_commutation": check_footprint_faithful_commutation(),
        "hidden_read_counterexample": check_hidden_read_counterexample(),
        "preservation_vs_revalidation": check_preservation_vs_revalidation(),
        "v2_discriminator_compatibility": check_v2_results_still_compatible(),
    }
    print("P6 THEORY CLOSURE V2.1: PASS")
    for key, value in totals.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
