#!/usr/bin/env python3
"""Normative P8 V2.1 primitive-closure checker.

V2 states its authorization rule in terms of a *blocker* it never defines, is silent on
confidence and expected utility, never lifts its revocation machinery to a statement about
how authority behaves as premises arrive, and never says that protected custody is one root
class among several. `manuscript/FORMAL_CORE_V2_1.md` closes those four.

This checker discharges each V2.1 proposition against a finite model. Two of the checks are
countermodels rather than confirmations: the fail-open blocker reading and the
confidence/utility substitution both have to be exhibited as *wrong*, not merely asserted to
be. Standard library only; finite models are proof support, not unrestricted proofs.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import chain, combinations

AUTHORIZED = "AUTHORIZED"
DENIED = "DENIED"
CANNOT_CHECK = "CANNOT_CHECK"

ESTABLISHED = "ESTABLISHED"
REFUTED = "REFUTED"
UNDETERMINED = "UNDETERMINED"

PROTECTED_CUSTODY = "PROTECTED_CUSTODY"
DELEGATED_GRANT = "DELEGATED_GRANT"
STANDING_POLICY = "STANDING_POLICY"
OBLIGATION_FREE = "OBLIGATION_FREE"

ROOT_CLASSES = (PROTECTED_CUSTODY, DELEGATED_GRANT, STANDING_POLICY, OBLIGATION_FREE)


@dataclass(frozen=True)
class Context:
    """Definition 4, restricted to what Definition 10 actually reads.

    `available` are premises present and valid; `refuted` are premises the evidence
    positively excludes. A premise in neither is unknown, which is the case Definition 19
    calls `UNDETERMINED` and V2's prose silently merged into "no blocker applies".
    """

    available: frozenset[str] = frozenset()
    refuted: frozenset[str] = frozenset()
    revoked: frozenset[str] = frozenset()

    def valid(self, premise: str) -> bool:
        return premise in self.available and premise not in self.revoked

    def excluded(self, premise: str) -> bool:
        return premise in self.refuted or premise in self.revoked


@dataclass(frozen=True)
class Effect:
    """Definition 1 plus the two agent-internal quantities of Definition 20."""

    name: str
    obligations: tuple[tuple[str, tuple[frozenset[str], ...]], ...] = ()
    blockers: tuple[tuple[str, tuple[frozenset[str], ...]], ...] = ()
    root_class: str = DELEGATED_GRANT
    root_protected: bool = False
    reaches_own_policy: bool = False
    confidence: float = 0.5
    expected_utility: float = 0.0


def _derivable(support: tuple[frozenset[str], ...], context: Context) -> bool:
    """Theorem 4: derivable iff some complete support set survives."""

    return any(all(context.valid(p) for p in s) for s in support)


def _excluded(support: tuple[frozenset[str], ...], context: Context) -> bool:
    """Every support set is broken by a premise the evidence positively excludes."""

    return all(any(context.excluded(p) for p in s) for s in support)


def determination(support: tuple[frozenset[str], ...], context: Context) -> str:
    """Definition 19 — blocker determination."""

    if _derivable(support, context):
        return ESTABLISHED
    if _excluded(support, context):
        return REFUTED
    return UNDETERMINED


def permission(effect: Effect, context: Context, *, fail_open: bool = False) -> str:
    """Definition 10 + Definition 11, read fail-closed unless asked otherwise.

    `fail_open=True` is the unsound reading Proposition 10 rules out: it treats an
    `UNDETERMINED` blocker as satisfying clause 2. It exists so the countermodel can be
    exhibited rather than described.
    """

    blocker_states = [determination(support, context) for _, support in effect.blockers]
    if ESTABLISHED in blocker_states:
        return DENIED
    if UNDETERMINED in blocker_states and not fail_open:
        return CANNOT_CHECK
    for _, support in effect.obligations:
        if not _derivable(support, context):
            return CANNOT_CHECK
    if effect.reaches_own_policy and not effect.root_protected:
        # Proposition 7: an unprotected root cannot ground self-admission.
        return CANNOT_CHECK
    return AUTHORIZED


def _powerset(items: tuple[str, ...]) -> list[frozenset[str]]:
    return [frozenset(c) for c in chain.from_iterable(combinations(items, r) for r in range(len(items) + 1))]


# --- Proposition 10 -----------------------------------------------------------------


def check_fail_closed_blocker_determination() -> int:
    """An undetermined blocker yields CANNOT_CHECK, and the fail-open reading is unsound."""

    checks = 0
    effect = Effect(
        name="e",
        obligations=(("o", (frozenset({"ev"}),)),),
        blockers=(("b", (frozenset({"harm"}),)),),
    )

    # `harm` neither available nor refuted: the blocker is undetermined.
    undetermined = Context(available=frozenset({"ev"}))
    assert determination(effect.blockers[0][1], undetermined) == UNDETERMINED
    assert permission(effect, undetermined) == CANNOT_CHECK
    checks += 1

    # The fail-open reading authorizes the identical state. That is the defect.
    assert permission(effect, undetermined, fail_open=True) == AUTHORIZED
    checks += 1

    # And it is unsound: one more evidence item establishes the blocker, so the state the
    # fail-open reading called AUTHORIZED contains a derivable DENIED.
    established = Context(available=frozenset({"ev", "harm"}))
    assert determination(effect.blockers[0][1], established) == ESTABLISHED
    assert permission(effect, established) == DENIED
    checks += 1

    # No alarm: once the blocker is positively refuted, the fail-closed reading authorizes.
    refuted = Context(available=frozenset({"ev"}), refuted=frozenset({"harm"}))
    assert determination(effect.blockers[0][1], refuted) == REFUTED
    assert permission(effect, refuted) == AUTHORIZED
    checks += 1
    return checks


# --- Proposition 11 -----------------------------------------------------------------


def check_blockers_are_monotone_under_evidence() -> int:
    """Once established, no enlargement of the premise set clears a blocker."""

    checks = 0
    support = (frozenset({"h1"}), frozenset({"h2", "h3"}))
    extras = ("x1", "x2", "x3")
    for base in (frozenset({"h1"}), frozenset({"h2", "h3"})):
        for extra in _powerset(extras):
            context = Context(available=base | extra)
            assert determination(support, context) == ESTABLISHED
            checks += 1

    # Only revocation clears it, which is Theorem 4 rather than accumulation.
    cleared = Context(available=frozenset({"h1", "h2", "h3"}), revoked=frozenset({"h1", "h2"}))
    assert determination(support, cleared) != ESTABLISHED
    checks += 1
    return checks


# --- Proposition 12 ----------------------------------------------------------------


def check_permission_is_not_a_function_of_confidence_and_utility() -> int:
    """Exhibit two requests in one (Conf, EU) fibre with different terminals."""

    checks = 0
    discharged = Effect(
        name="e1",
        obligations=(("o", (frozenset({"ev"}),)),),
        confidence=0.99,
        expected_utility=1000.0,
    )
    undischarged = replace(discharged, name="e2", obligations=(("o", (frozenset({"missing"}),)),))
    context = Context(available=frozenset({"ev"}))

    assert discharged.confidence == undischarged.confidence
    assert discharged.expected_utility == undischarged.expected_utility
    assert permission(discharged, context) == AUTHORIZED
    assert permission(undischarged, context) == CANNOT_CHECK
    checks += 1

    # Corollary 12.1: sweeping confidence and utility never promotes the terminal.
    for confidence in (0.0, 0.5, 0.99, 1.0):
        for utility in (-1e9, 0.0, 1e9):
            candidate = replace(undischarged, confidence=confidence, expected_utility=utility)
            assert permission(candidate, context) == CANNOT_CHECK
            checks += 1

    # Corollary 12.2: utility ranks within the authorized fibre without changing it.
    ranked = sorted(
        (replace(discharged, expected_utility=u) for u in (3.0, 1.0, 2.0)),
        key=lambda e: e.expected_utility,
    )
    assert [e.expected_utility for e in ranked] == [1.0, 2.0, 3.0]
    assert all(permission(e, context) == AUTHORIZED for e in ranked)
    checks += 1
    return checks


# --- Proposition 13 ----------------------------------------------------------------


def check_authority_is_non_monotone_in_both_directions() -> int:
    """Adding a premise can deny; revoking one can withdraw to CANNOT_CHECK."""

    checks = 0
    effect = Effect(
        name="e",
        obligations=(("o", (frozenset({"ev"}),)),),
        blockers=(("b", (frozenset({"harm"}),)),),
    )
    start = Context(available=frozenset({"ev"}), refuted=frozenset({"harm"}))
    assert permission(effect, start) == AUTHORIZED
    checks += 1

    # (1) addition establishes a blocker.
    added = Context(available=frozenset({"ev", "harm"}))
    assert permission(effect, added) == DENIED
    checks += 1

    # (2) revocation breaks the only support set of the discharge.
    revoked = replace(start, revoked=frozenset({"ev"}))
    assert permission(effect, revoked) == CANNOT_CHECK
    checks += 1

    # Asymmetry: accumulation alone never restores authority once denied.
    for extra in _powerset(("p1", "p2", "p3")):
        assert permission(effect, Context(available=frozenset({"ev", "harm"}) | extra)) == DENIED
        checks += 1
    return checks


# --- Proposition 14 ----------------------------------------------------------------


def check_demotion_is_forward_only() -> int:
    """A pending effect is demoted; a committed one is neither un- nor retro-authorized."""

    checks = 0
    effect = Effect(name="e", obligations=(("o", (frozenset({"ev"}),)),))
    at_t = Context(available=frozenset({"ev"}))
    assert permission(effect, at_t) == AUTHORIZED
    checks += 1

    at_t_prime = replace(at_t, revoked=frozenset({"ev"}))
    # Pending: the epoch-t certificate does not transport (Definition 14).
    assert permission(effect, at_t_prime) == CANNOT_CHECK
    checks += 1

    # Committed: history records the epoch-t evaluation, which is unchanged by t'.
    history = {"epoch": "t", "terminal": permission(effect, at_t)}
    assert history["terminal"] == AUTHORIZED
    checks += 1

    # And the historical record is not forward authority. Reading "the commit was
    # authorized" as "it stands" is the fail-open error Proposition 14 clause 2 rules out:
    # the same effect evaluated at t' is not AUTHORIZED, committed or not.
    assert permission(effect, at_t_prime) != AUTHORIZED
    assert history["terminal"] != permission(effect, at_t_prime)
    checks += 1

    # Proposition 5, the other direction: a blocker found at t' does not retro-authorize.
    late_blocker = Effect(
        name="e",
        obligations=(("o", (frozenset({"ev"}),)),),
        blockers=(("b", (frozenset({"harm"}),)),),
    )
    assert permission(late_blocker, Context(available=frozenset({"ev", "harm"}))) == DENIED
    assert permission(late_blocker, Context(available=frozenset({"ev"}))) == CANNOT_CHECK
    checks += 1
    return checks


# --- Propositions 15 and 16 --------------------------------------------------------


def check_protected_custody_is_one_root_class() -> int:
    """A non-custody root can authorize; an unprotected self-admission cannot."""

    checks = 0
    context = Context(available=frozenset({"ev"}))

    # A delegated grant authorizes an effect that makes no custody claim at all.
    delegated = Effect(
        name="e",
        obligations=(("o", (frozenset({"ev"}),)),),
        root_class=DELEGATED_GRANT,
        root_protected=False,
        reaches_own_policy=False,
    )
    assert permission(delegated, context) == AUTHORIZED
    checks += 1

    # Every non-custody class can authorize, so custody is not the only source.
    for root_class in (DELEGATED_GRANT, STANDING_POLICY, OBLIGATION_FREE):
        candidate = replace(delegated, root_class=root_class)
        assert candidate.root_class != PROTECTED_CUSTODY
        assert permission(candidate, context) == AUTHORIZED
        checks += 1

    # Proposition 7 still bites where it should: self-admission on an unprotected root.
    self_admitting = replace(delegated, reaches_own_policy=True, root_protected=False)
    assert permission(self_admitting, context) == CANNOT_CHECK
    checks += 1

    # And is discharged by protection, not by the root's class label.
    protected = replace(self_admitting, root_class=PROTECTED_CUSTODY, root_protected=True)
    assert permission(protected, context) == AUTHORIZED
    checks += 1

    # Definition 15 is relative to the effect: one root, two verdicts.
    assert permission(replace(protected, reaches_own_policy=False), context) == AUTHORIZED
    assert permission(replace(protected, root_protected=False), context) == CANNOT_CHECK
    checks += 1

    assert len(set(ROOT_CLASSES)) == 4
    checks += 1
    return checks


# --- V2 compatibility --------------------------------------------------------------


def check_v2_results_still_hold() -> int:
    """The V2 results V2.1 leans on are unchanged by the additions."""

    checks = 0
    # Three distinct terminals remain reachable and distinguishable.
    effect = Effect(
        name="e",
        obligations=(("o", (frozenset({"ev"}),)),),
        blockers=(("b", (frozenset({"harm"}),)),),
    )
    terminals = {
        permission(effect, Context(available=frozenset({"ev"}), refuted=frozenset({"harm"}))),
        permission(effect, Context(available=frozenset({"ev", "harm"}))),
        permission(effect, Context(available=frozenset())),
    }
    assert terminals == {AUTHORIZED, DENIED, CANNOT_CHECK}
    checks += 1

    # Theorem 4: an independent complete support set survives revocation of another.
    two_derivations = Effect(
        name="e",
        obligations=(("o", (frozenset({"a"}), frozenset({"b"}))),),
    )
    context = Context(available=frozenset({"a", "b"}), revoked=frozenset({"a"}))
    assert permission(two_derivations, context) == AUTHORIZED
    checks += 1

    # Corollary 4.1 does not extend to revoking both.
    assert permission(two_derivations, replace(context, revoked=frozenset({"a", "b"}))) == CANNOT_CHECK
    checks += 1
    return checks


def main() -> int:
    totals = {
        "fail_closed_blocker_determination": check_fail_closed_blocker_determination(),
        "blocker_monotonicity": check_blockers_are_monotone_under_evidence(),
        "permission_not_confidence_or_utility": check_permission_is_not_a_function_of_confidence_and_utility(),
        "authority_non_monotonicity": check_authority_is_non_monotone_in_both_directions(),
        "forward_only_demotion": check_demotion_is_forward_only(),
        "protected_custody_one_root_class": check_protected_custody_is_one_root_class(),
        "v2_compatibility": check_v2_results_still_hold(),
    }
    for name, count in totals.items():
        print(f"{name}: {count} checks")
    print(f"total: {sum(totals.values())} checks")
    print("P8 THEORY CLOSURE V2.1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
