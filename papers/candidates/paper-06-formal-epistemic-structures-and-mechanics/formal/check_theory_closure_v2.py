#!/usr/bin/env python3
"""Deterministic support checker for P6 formal core V2.

Standard-library only. This is proof-support/counterexample enumeration, not
novelty evidence or an empirical evaluation of scientific agents.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import combinations, product

NODES = ("a", "b", "c", "d")


def descendants(edges: frozenset[tuple[str, str]], roots: frozenset[str]) -> frozenset[str]:
    seen = set()
    frontier = list(roots)
    while frontier:
        x = frontier.pop()
        for u, v in edges:
            if u == x and v not in seen and v not in roots:
                seen.add(v)
                frontier.append(v)
    return frozenset(seen)


@dataclass(frozen=True)
class PreservationCertificate:
    claim: str
    changed: frozenset[str]
    trusted_issuer: bool
    valid: bool
    proves_invariance: bool


def affected(
    certified: frozenset[str],
    edges: frozenset[tuple[str, str]],
    changed: frozenset[str],
) -> frozenset[str]:
    """Root-inclusive affected closure."""
    return frozenset((certified & changed) | (certified & descendants(edges, changed)))


def preserved_by_certificate(
    claim: str,
    *,
    changed: frozenset[str],
    certificates: tuple[PreservationCertificate, ...],
) -> bool:
    # A changed certified root cannot certify its own continued status merely
    # because a downstream preservation witness exists.
    if claim in changed:
        return False
    return any(
        c.claim == claim
        and c.changed == changed
        and c.trusted_issuer
        and c.valid
        and c.proves_invariance
        for c in certificates
    )


def reopen_set(
    certified: frozenset[str],
    edges: frozenset[tuple[str, str]],
    changed: frozenset[str],
    certificates: tuple[PreservationCertificate, ...] = (),
) -> frozenset[str]:
    return frozenset(
        q for q in affected(certified, edges, changed)
        if not preserved_by_certificate(q, changed=changed, certificates=certificates)
    )


def all_forward_dags():
    possible = tuple((NODES[i], NODES[j]) for i in range(len(NODES)) for j in range(i + 1, len(NODES)))
    for bits in product((0, 1), repeat=len(possible)):
        yield frozenset(e for e, bit in zip(possible, bits) if bit)


def check_root_inclusive_reopening() -> tuple[int, int]:
    cases = 0
    changed_root_cases = 0
    certified = frozenset(NODES)
    for edges in all_forward_dags():
        for r in range(1, len(NODES) + 1):
            for combo in combinations(NODES, r):
                changed = frozenset(combo)
                expected = (certified & changed) | (certified & descendants(edges, changed))
                actual = reopen_set(certified, edges, changed)
                assert actual == expected
                assert certified & changed <= actual
                cases += 1
                changed_root_cases += len(certified & changed)
    return cases, changed_root_cases


def check_preservation_certificate_matrix() -> int:
    edges = frozenset({("a", "b"), ("b", "c"), ("a", "d")})
    certified = frozenset(NODES)
    changed = frozenset({"a"})
    cases = 0
    for claim in ("a", "b", "c", "d"):
        for trusted, valid, invariance, exact_change in product((False, True), repeat=4):
            cert = PreservationCertificate(
                claim=claim,
                changed=changed if exact_change else frozenset({"b"}),
                trusted_issuer=trusted,
                valid=valid,
                proves_invariance=invariance,
            )
            reopened = reopen_set(certified, edges, changed, (cert,))
            should_preserve = (
                claim != "a"
                and trusted
                and valid
                and invariance
                and exact_change
                and claim in affected(certified, edges, changed)
            )
            if claim in affected(certified, edges, changed):
                assert (claim not in reopened) == should_preserve
            else:
                assert claim not in reopened
            assert "a" in reopened
            cases += 1
    return cases


@dataclass(frozen=True)
class State:
    data: tuple[tuple[str, int], ...]
    obligations: frozenset[str] = frozenset()
    authority: frozenset[str] = frozenset()
    provenance: frozenset[str] = frozenset()
    history: tuple[str, ...] = ()

    def value(self, key: str) -> int:
        return dict(self.data)[key]

    def write(self, key: str, value: int, event: str) -> "State":
        d = dict(self.data)
        d[key] = value
        return replace(self, data=tuple(sorted(d.items())), history=self.history + (event,))


@dataclass(frozen=True)
class Mechanic:
    name: str
    reads: frozenset[str]
    writes: frozenset[str]
    delta: int

    def run(self, s: State) -> State:
        key = next(iter(self.writes))
        return s.write(key, s.value(key) + self.delta, self.name)


def strongly_separated(m: Mechanic, n: Mechanic) -> bool:
    return not (m.writes & (n.reads | n.writes) or n.writes & (m.reads | m.writes))


def trace_equivalent_independent(h1: tuple[str, ...], h2: tuple[str, ...]) -> bool:
    return len(h1) == len(h2) == 2 and set(h1) == set(h2)


def check_commutation_and_history() -> int:
    keys = ("x", "y", "z")
    base = State(tuple((k, 0) for k in keys))
    count = 0
    for wk1, wk2 in combinations(keys, 2):
        m = Mechanic("m", frozenset({wk1}), frozenset({wk1}), 1)
        n = Mechanic("n", frozenset({wk2}), frozenset({wk2}), 2)
        assert strongly_separated(m, n)
        mn = n.run(m.run(base))
        nm = m.run(n.run(base))
        assert mn.data == nm.data
        assert mn.obligations == nm.obligations
        assert mn.authority == nm.authority
        assert mn.provenance == nm.provenance
        assert mn.history != nm.history
        assert trace_equivalent_independent(mn.history, nm.history)
        count += 1
    return count


def conditional_compose(
    state: State,
    *,
    guard: bool,
    when_true: Mechanic,
    when_false: Mechanic,
    guard_authorized: bool,
) -> State:
    """Run exactly one branch of an authority-valid conditional contract."""

    if not guard_authorized:
        raise PermissionError("conditional guard is not authorized")
    branch = when_true if guard else when_false
    return branch.run(state)


def check_conditional_composition() -> int:
    base = State(
        (("x", 0), ("y", 0)),
        obligations=frozenset({"open-o"}),
        authority=frozenset({"root-a"}),
        provenance=frozenset({"source-p"}),
    )
    when_true = Mechanic("true", frozenset({"x"}), frozenset({"x"}), 1)
    when_false = Mechanic("false", frozenset({"y"}), frozenset({"y"}), 2)
    true_result = conditional_compose(
        base,
        guard=True,
        when_true=when_true,
        when_false=when_false,
        guard_authorized=True,
    )
    assert true_result.data == (("x", 1), ("y", 0))
    assert true_result.obligations == base.obligations
    assert true_result.authority == base.authority
    assert true_result.provenance == base.provenance
    false_result = conditional_compose(
        base,
        guard=False,
        when_true=when_true,
        when_false=when_false,
        guard_authorized=True,
    )
    assert false_result.data == (("x", 0), ("y", 2))
    assert false_result.obligations == base.obligations
    assert false_result.authority == base.authority
    assert false_result.provenance == base.provenance
    try:
        conditional_compose(
            base,
            guard=True,
            when_true=when_true,
            when_false=when_false,
            guard_authorized=False,
        )
    except PermissionError:
        pass
    else:
        raise AssertionError("unauthorized conditional guard was accepted")
    return 9


def compose_obligation(
    obligation_present: bool,
    *,
    authorized_discharge: bool,
    later_success: bool,
) -> tuple[bool, str]:
    if not obligation_present:
        return False, "OK"
    if authorized_discharge:
        return False, "OK"
    return True, "CANNOT_CHECK" if later_success else "OPEN"


def check_residual_obligation_preservation() -> int:
    count = 0
    for present, discharge, success in product((False, True), repeat=3):
        remains, terminal = compose_obligation(present, authorized_discharge=discharge, later_success=success)
        if present and not discharge:
            assert remains
            assert terminal in {"OPEN", "CANNOT_CHECK"}
        else:
            assert not remains
        count += 1
    return count


def authority_step(tokens: frozenset[str], output: frozenset[str], trusted_new: frozenset[str]) -> bool:
    return output - tokens <= trusted_new


def check_non_escalation() -> int:
    universe = ("A", "B", "C")
    count = 0
    for in_bits in product((0, 1), repeat=3):
        ins = frozenset(x for x, b in zip(universe, in_bits) if b)
        for out_bits in product((0, 1), repeat=3):
            outs = frozenset(x for x, b in zip(universe, out_bits) if b)
            new = outs - ins
            assert authority_step(ins, outs, new)
            assert authority_step(ins, outs, frozenset()) == (not bool(new))
            count += 1
    return count


@dataclass(frozen=True)
class BareTransition:
    input_value: int
    output_value: int


@dataclass(frozen=True)
class EpistemicContract:
    transition: BareTransition
    hard_obligation_satisfied: bool
    commit_authorized: bool

    @property
    def admissible(self) -> bool:
        return self.hard_obligation_satisfied and self.commit_authorized


def check_typed_erasure_separation() -> int:
    t = BareTransition(0, 1)
    a = EpistemicContract(t, True, True)
    b = EpistemicContract(t, False, True)
    c = EpistemicContract(t, True, False)
    assert a.transition == b.transition == c.transition
    assert a.admissible and not b.admissible and not c.admissible
    return 3


def audit_terminates(edges: dict[str, tuple[str, ...]], root: str) -> bool:
    active = set()
    done = set()

    def visit(x: str) -> bool:
        if x in active:
            return False
        if x in done:
            return True
        active.add(x)
        for y in edges.get(x, ()):
            if not visit(y):
                return False
        active.remove(x)
        done.add(x)
        return True

    return visit(root)


def check_recursive_audit() -> int:
    assert audit_terminates({"a": ("b",), "b": ("c",), "c": ()}, "a")
    assert not audit_terminates({"a": ("b",), "b": ("a",)}, "a")
    assert not audit_terminates({"a": ("a",)}, "a")
    return 3


def check_conservative_special_cases() -> int:
    edges = frozenset({("a", "b"), ("a", "c"), ("c", "d")})
    cert = frozenset(NODES)
    for changed in (frozenset({"a"}), frozenset({"c"}), frozenset({"b", "d"})):
        assert reopen_set(cert, edges, changed) == affected(cert, edges, changed)
    return 3


def main() -> int:
    totals = {
        "root_inclusive": check_root_inclusive_reopening(),
        "preservation_certificate": check_preservation_certificate_matrix(),
        "commutation": check_commutation_and_history(),
        "conditional_composition": check_conditional_composition(),
        "residual_obligation": check_residual_obligation_preservation(),
        "non_escalation": check_non_escalation(),
        "typed_erasure": check_typed_erasure_separation(),
        "recursive_audit": check_recursive_audit(),
        "conservative_special_cases": check_conservative_special_cases(),
    }
    print("P6 THEORY CLOSURE V2: PASS")
    for key, value in totals.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
