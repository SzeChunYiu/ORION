#!/usr/bin/env python3
"""Executable model of the A6 amplification counterexample.

A6_AMPLIFICATION_COUNTEREXAMPLE_V1.md argues from the definitions that ORION-16's
repair can promote CANNOT_CHECK to AUTHORIZED without new protected evidence, by
re-grounding a claim in an OBLIGATION_FREE domain. An argument from definitions is
not a check, so this encodes the scenario and runs it.

WHAT THIS CHECKS AND WHAT IT DOES NOT. It checks *my formalisation* of Definition 10
(permission), Definition 21 (root classes) and ORION-16 repair. It does NOT check the
papers' own implementations, and a disagreement between this model and them is a
finding about the model until shown otherwise. The model is deliberately small enough
to read in full.

It also runs the three refutations named in that document, so the output says not only
whether the attack lands but which proposed fix stops it.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

SCHEMA = "ORION.A6.AmplificationCheck.v1"

AUTHORIZED, DENIED, CANNOT_CHECK = "AUTHORIZED", "DENIED", "CANNOT_CHECK"

# Definition 21 root classes. Definition 21 gives NO ordering over these, which is
# itself one of the gaps the counterexample document names.
PROTECTED_CUSTODY = "PROTECTED_CUSTODY"
DELEGATED_GRANT = "DELEGATED_GRANT"
STANDING_POLICY = "STANDING_POLICY"
OBLIGATION_FREE = "OBLIGATION_FREE"


@dataclass(frozen=True)
class Domain:
    name: str
    obligations: frozenset[str]          # O_h
    root_class: str


@dataclass
class World:
    """Which evidence types are actually available. Never mutated by repair."""
    available_evidence: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class Certificate:
    claim: str
    domain: Domain


def discharged(o: str, world: World) -> bool:
    """An obligation is discharged iff the evidence its judgment type names exists."""
    return o in world.available_evidence


def permission(cert: Certificate, world: World, blockers_undetermined: bool = False) -> str:
    """Definition 10 clause 1 plus the V2.1 blocker correction.

    Clause 1: every obligation in scope is discharged.
    Blocker clause: any UNDETERMINED blocker forces CANNOT_CHECK.
    Confidence and expected utility appear nowhere, per Proposition 12.
    """
    if blockers_undetermined:
        return CANNOT_CHECK
    undischarged = [o for o in cert.domain.obligations if not discharged(o, world)]
    if undischarged:
        return CANNOT_CHECK
    return AUTHORIZED


def repair(cert: Certificate, target_domain: Domain, *,
           preserve_domain: bool = False,
           root_class_monotone: bool = False,
           root_rank: dict[str, int] | None = None) -> tuple[Certificate, str]:
    """ORION-16 re-certification, with the two proposed constraints as switches.

    Returns the new certificate and a note on which constraint (if any) bound.
    """
    if preserve_domain and target_domain.name != cert.domain.name:
        return cert, "REFUSED_domain_preservation"
    if root_class_monotone and root_rank is not None:
        if root_rank[target_domain.root_class] < root_rank[cert.domain.root_class]:
            return cert, "REFUSED_root_class_monotonicity"
    return Certificate(cert.claim, target_domain), "REGROUNDED"


def scenario(*, preserve_domain=False, root_class_monotone=False) -> dict:
    """The counterexample: q blocked on unavailable evidence, then repaired."""
    world = World(available_evidence=set())      # the evidence is NOT available

    h = Domain("h", frozenset({"PROTECTED_LAB_RESULT"}), PROTECTED_CUSTODY)
    h_free = Domain("h_free", frozenset(), OBLIGATION_FREE)

    # Ordering used only when root_class_monotone is on. Definition 21 supplies none;
    # this is a *proposed* ordering, and saying so is the point.
    rank = {OBLIGATION_FREE: 0, STANDING_POLICY: 1,
            DELEGATED_GRANT: 2, PROTECTED_CUSTODY: 3}

    before = Certificate("q", h)
    perm_before = permission(before, world)

    after, note = repair(before, h_free,
                         preserve_domain=preserve_domain,
                         root_class_monotone=root_class_monotone,
                         root_rank=rank)
    perm_after = permission(after, world)

    return {
        "evidence_available": sorted(world.available_evidence),
        "domain_before": before.domain.name,
        "obligations_before": sorted(before.domain.obligations),
        "perm_before": perm_before,
        "repair_note": note,
        "domain_after": after.domain.name,
        "obligations_after": sorted(after.domain.obligations),
        "perm_after": perm_after,
        "amplified": perm_before == CANNOT_CHECK and perm_after == AUTHORIZED,
        "new_evidence_supplied": False,
    }


def self_test() -> dict:
    """The model must discriminate, or its agreement means nothing."""
    world_with = World(available_evidence={"PROTECTED_LAB_RESULT"})
    h = Domain("h", frozenset({"PROTECTED_LAB_RESULT"}), PROTECTED_CUSTODY)
    cases = [
        ("obligation discharged by real evidence -> AUTHORIZED",
         permission(Certificate("q", h), world_with), AUTHORIZED),
        ("obligation undischarged -> CANNOT_CHECK",
         permission(Certificate("q", h), World()), CANNOT_CHECK),
        ("undetermined blocker forces CANNOT_CHECK even when discharged",
         permission(Certificate("q", h), world_with, blockers_undetermined=True), CANNOT_CHECK),
        ("obligation-free domain is vacuously discharged",
         permission(Certificate("q", Domain("f", frozenset(), OBLIGATION_FREE)), World()),
         AUTHORIZED),
    ]
    rows = [{"why": w, "got": g, "expected": e, "ok": g == e} for w, g, e in cases]
    return {"cases": rows, "all_ok": all(r["ok"] for r in rows),
            "distinct_verdicts": sorted({r["got"] for r in rows}),
            "discriminates": len({r["got"] for r in rows}) > 1}


if __name__ == "__main__":
    out = {
        "schema": SCHEMA,
        "checks_my_formalisation_not_the_papers_implementation": True,
        "self_test": self_test(),
        "attack_unconstrained": scenario(),
        "refutation_1_domain_preservation": scenario(preserve_domain=True),
        "refutation_2_root_class_monotonicity": scenario(root_class_monotone=True),
        "scientific_authority_delta": "NONE",
    }
    a = out["attack_unconstrained"]
    out["verdict"] = ("ATTACK_LANDS_UNCONSTRAINED" if a["amplified"]
                      else "ATTACK_DOES_NOT_LAND")
    out["refutations_that_stop_it"] = [
        k for k in ("refutation_1_domain_preservation", "refutation_2_root_class_monotonicity")
        if not out[k]["amplified"]
    ]
    print(json.dumps(out, indent=2, sort_keys=True))
