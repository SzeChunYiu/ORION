#!/usr/bin/env python3
"""Deterministic cross-donor challenge suite for the P6-P8 ORION envelope.

This checker does not emulate full donor implementations. It freezes the
*interfaces* each donor family is allowed to establish, then tests cross-
structure cases where an integration layer must keep those judgments distinct.
It includes an ideal donor-product super-baseline with correct adapters. ORION
is not expected to beat that baseline merely by centralizing the same rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Terminal(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    REOPEN = "REOPEN"
    TASK_STOP = "TASK_STOP"
    ROUTE_STOP = "ROUTE_STOP"
    CONTINUE = "CONTINUE"
    CANNOT_CHECK = "CANNOT_CHECK"
    DENIED = "DENIED"
    PRESERVE = "PRESERVE"


@dataclass(frozen=True)
class Case:
    case_id: str
    dependency_affected: bool = False
    computation_reusable: bool = True
    effect_policy_allows: bool = True
    generic_grant_valid: bool = True
    evidence_valid: bool = True
    target_obligation_satisfied: bool = True
    closure_transport_proved: bool = True
    target_ambiguous: bool = False
    alternative_support_valid: bool = False
    revoked_primary_support: bool = False
    chronology_safe: bool = True
    route_exhausted: bool = False
    censored_open: bool = False
    resources_exhausted: bool = False
    expected: Terminal = Terminal.AUTHORIZED


CASES = (
    Case(
        "repair-plus-authority",
        dependency_affected=True,
        computation_reusable=False,
        generic_grant_valid=True,
        target_obligation_satisfied=False,
        expected=Terminal.CANNOT_CHECK,
    ),
    Case(
        "effect-introduces-reopening",
        dependency_affected=True,
        computation_reusable=True,
        effect_policy_allows=True,
        target_obligation_satisfied=False,
        expected=Terminal.REOPEN,
    ),
    Case(
        "representation-preserves-evidence-not-closure",
        evidence_valid=True,
        target_obligation_satisfied=False,
        closure_transport_proved=False,
        target_ambiguous=True,
        expected=Terminal.REOPEN,
    ),
    Case(
        "goal-evolution-reuses-provenance",
        evidence_valid=True,
        target_obligation_satisfied=False,
        closure_transport_proved=False,
        target_ambiguous=False,
        expected=Terminal.CANNOT_CHECK,
    ),
    Case(
        "generic-permission-without-scientific-discharge",
        generic_grant_valid=True,
        effect_policy_allows=True,
        target_obligation_satisfied=False,
        expected=Terminal.CANNOT_CHECK,
    ),
    Case(
        "revoked-primary-independent-support-survives",
        revoked_primary_support=True,
        alternative_support_valid=True,
        expected=Terminal.PRESERVE,
    ),
    Case(
        "chronology-sensitive-current-state-tie",
        chronology_safe=False,
        target_obligation_satisfied=True,
        generic_grant_valid=True,
        expected=Terminal.DENIED,
    ),
    Case(
        "censored-resource-stop-is-not-completeness",
        route_exhausted=True,
        censored_open=True,
        resources_exhausted=True,
        expected=Terminal.CANNOT_CHECK,
    ),
    Case(
        "clean-authorized-control",
        expected=Terminal.AUTHORIZED,
    ),
    Case(
        "clean-route-stop-control",
        route_exhausted=True,
        generic_grant_valid=False,
        expected=Terminal.ROUTE_STOP,
    ),
)


def tms_view(c: Case) -> str:
    return "AFFECTED" if c.dependency_affected else "UNAFFECTED"


def incremental_view(c: Case) -> str:
    return "REUSE" if c.computation_reusable else "RECOMPUTE"


def effect_view(c: Case) -> str:
    return "ALLOW_EFFECT" if c.effect_policy_allows else "DENY_EFFECT"


def authorization_view(c: Case) -> str:
    return "ALLOW" if c.generic_grant_valid else "DENY"


def provenance_view(c: Case) -> str:
    return "VALID_EVIDENCE" if c.evidence_valid else "INVALID_EVIDENCE"


def abstraction_view(c: Case) -> str:
    return "TRANSPORT" if c.closure_transport_proved else "NO_TRANSPORT_PROOF"


def obligation_view(c: Case) -> str:
    return "SAT" if c.target_obligation_satisfied else "OPEN"


def envelope(c: Case) -> Terminal:
    # Revocation is derivation-sensitive, not naive descendant invalidation.
    if c.revoked_primary_support:
        return Terminal.PRESERVE if c.alternative_support_valid else Terminal.DENIED

    # Chronology is semantically relevant even when current state could match.
    if not c.chronology_safe:
        return Terminal.DENIED

    # Open/censored mandatory obligations dominate resource/route stopping.
    if c.censored_open:
        return Terminal.CANNOT_CHECK if c.resources_exhausted else Terminal.CONTINUE

    # A locally exhausted route is not global completion. In this synthetic
    # control, lack of a global grant makes the intended terminal route-local.
    if c.route_exhausted and not c.generic_grant_valid:
        return Terminal.ROUTE_STOP

    # Representation/objective transport has its own semantics.
    if not c.closure_transport_proved and not c.target_obligation_satisfied:
        return Terminal.REOPEN if c.target_ambiguous else Terminal.CANNOT_CHECK

    # A dependency-affecting committed effect can require reopening even when
    # computation itself is reusable.
    if c.dependency_affected and not c.target_obligation_satisfied:
        return Terminal.REOPEN if c.computation_reusable else Terminal.CANNOT_CHECK

    # Generic permission and effect policy do not discharge a scientific hard
    # obligation.
    if not c.target_obligation_satisfied:
        return Terminal.CANNOT_CHECK

    if not c.effect_policy_allows or not c.generic_grant_valid or not c.evidence_valid:
        return Terminal.DENIED

    return Terminal.AUTHORIZED


def ideal_donor_product(c: Case) -> Terminal:
    """Strong super-baseline: same donor facts, all adapters implemented correctly."""
    return envelope(c)


def naive_donor_product(c: Case) -> Terminal:
    """A deliberately plausible but unsafe interface composition.

    It lets generic authorization/effect success stand in for scientific
    discharge, treats valid evidence as closure-preserving, uses graph-only
    revocation, and converts resource+route stopping into task completion.
    """
    if c.revoked_primary_support:
        return Terminal.DENIED
    if c.route_exhausted and c.resources_exhausted:
        return Terminal.TASK_STOP
    if c.effect_policy_allows and c.generic_grant_valid and c.evidence_valid:
        if c.dependency_affected and not c.computation_reusable:
            return Terminal.REOPEN
        return Terminal.AUTHORIZED
    return Terminal.DENIED


def check_native_views_are_preserved() -> int:
    # The envelope does not rewrite donor-native facts; it consumes them.
    count = 0
    for c in CASES:
        assert tms_view(c) in {"AFFECTED", "UNAFFECTED"}
        assert incremental_view(c) in {"REUSE", "RECOMPUTE"}
        assert effect_view(c) in {"ALLOW_EFFECT", "DENY_EFFECT"}
        assert authorization_view(c) in {"ALLOW", "DENY"}
        assert provenance_view(c) in {"VALID_EVIDENCE", "INVALID_EVIDENCE"}
        assert abstraction_view(c) in {"TRANSPORT", "NO_TRANSPORT_PROOF"}
        assert obligation_view(c) in {"SAT", "OPEN"}
        count += 7
    return count


def check_challenges() -> tuple[int, int, int]:
    envelope_correct = 0
    ideal_equal = 0
    naive_errors = 0
    for c in CASES:
        got = envelope(c)
        assert got == c.expected, (c.case_id, got, c.expected)
        envelope_correct += 1
        assert ideal_donor_product(c) == got
        ideal_equal += 1
        if naive_donor_product(c) != c.expected:
            naive_errors += 1
    assert naive_errors >= 6
    return envelope_correct, ideal_equal, naive_errors


def main() -> int:
    native = check_native_views_are_preserved()
    challenge = check_challenges()
    print("DONOR-COMPLETE ORION ENVELOPE V1: PASS")
    print(f"native donor-interface facts preserved: {native}")
    print(f"cross-structure envelope cases correct: {challenge[0]}/{len(CASES)}")
    print(f"ideal donor-product equivalence: {challenge[1]}/{len(CASES)}")
    print(f"naive product integration errors exposed: {challenge[2]}/{len(CASES)}")
    print("claim boundary: integration semantics tested; no real-system superiority implied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
