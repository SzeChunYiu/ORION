#!/usr/bin/env python3
"""Exhaustive support for the cross-paper preservation dichotomy V2.

Discharges seven laws over the general core by enumeration. Six are separations
or impossibilities; the seventh is the no-alarm case, asserted because a
transport rule that refuses everything satisfies the other six perfectly and is
worthless.

Exit codes: 0 every law discharged, 2 a law failed, 3 the check could not run.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from preservation_core import (  # noqa: E402
    CANNOT_CHECK,
    DENY,
    GRANT,
    LADDER,
    Donor,
    Model,
    canonical_rule,
    coordinate_exposing,
    is_decisive,
    separates,
    sound_decisive_join_exists,
)

RESULTS: dict[str, object] = {}
FAILURES: list[str] = []


def law(name: str, ok: bool, **evidence: object) -> None:
    RESULTS[name] = {"discharged": bool(ok), **evidence}
    if not ok:
        FAILURES.append(name)


def subsets(items: tuple[str, ...]):
    for size in range(len(items) + 1):
        yield from (frozenset(c) for c in itertools.combinations(items, size))


def law_determination() -> None:
    """Standing is decidable exactly when the retained coordinates separate it.

    Necessity is the donor-projection argument of
    DONOR_PROJECTION_SEPARATION_THEOREM_V1 Theorem 1. Sufficiency is the quotient
    construction: on a separating projection the standing value is constant on
    each fibre, so a correct rule exists. Checked in both directions over every
    (required, retained) pair rather than argued.
    """

    pairs = 0
    for required in subsets(LADDER):
        model = Model(LADDER, required)
        for retained in subsets(LADDER):
            pairs += 1
            decisive = is_decisive(model, retained)
            if not (decisive == separates(model, retained) == (required <= retained)):
                law("determination", False, failing_pair=[sorted(required), sorted(retained)])
                return
    law("determination", True, pairs_checked=pairs, states_per_model=2 ** len(LADDER))


def law_soundness_and_forced_abstention() -> None:
    """A system missing a required coordinate must abstain, and may never guess.

    This is P6.V4.3 / P7.V3.3 / P8.V3.7 -- non-laundering -- stated over the
    canonical maximally decisive rule, so it holds for every sound rule.
    """

    unsound = 0
    abstained_everywhere_required_missing = True
    for required in subsets(LADDER):
        model = Model(LADDER, required)
        for retained in subsets(LADDER):
            decide = canonical_rule(model, retained)
            verdicts = [(decide(s), model.standing(s)) for s in model.universe()]
            unsound += sum(1 for got, truth in verdicts if got != CANNOT_CHECK and got != truth)
            if not required <= retained:
                if not any(got == CANNOT_CHECK for got, _ in verdicts):
                    abstained_everywhere_required_missing = False
    law(
        "soundness_and_forced_abstention",
        unsound == 0 and abstained_everywhere_required_missing,
        unsound_verdicts=unsound,
        abstention_forced_whenever_a_required_coordinate_is_missing=abstained_everywhere_required_missing,
    )


def law_ladder_irredundancy() -> None:
    """Every level of the five-level ladder is load-bearing in its own model.

    Irredundancy here, not universal minimality: the ledgers of P6, P7 and P8 all
    forbid claiming the registered coordinates are minimal in every domain, and
    this does not claim it. The second half of the check is the point -- a model
    with an inert coordinate is shown redundant, so the engine decides
    irredundancy per model instead of assuming it.
    """

    full = frozenset(LADDER)
    model = Model(LADDER, full)
    load_bearing = [c for c in LADDER if not is_decisive(model, full - {c})]

    inert = LADDER + ("X_inert",)
    inert_model = Model(inert, full)
    redundant_detected = is_decisive(inert_model, frozenset(inert) - {"X_inert"})

    law(
        "ladder_irredundancy",
        len(load_bearing) == len(LADDER) and redundant_detected,
        load_bearing_levels=load_bearing,
        inert_coordinate_correctly_found_redundant=redundant_detected,
    )


def law_selective_revalidation() -> None:
    """Repairing a proper subset of what broke does not restore standing.

    P6.V4.4 and P7.V3.4, generalized: over every affected set and every repair
    of it, standing returns exactly when the repair is total.
    """

    full = frozenset(LADDER)
    model = Model(LADDER, full)
    decide = canonical_rule(model, full)
    partial_failures = total_successes = 0
    for affected in subsets(LADDER):
        if not affected:
            continue
        for repaired in subsets(tuple(sorted(affected))):
            state = tuple(
                (c not in affected) or (c in repaired) for c in LADDER
            )
            verdict = decide(state)
            if repaired == affected:
                total_successes += verdict == GRANT
                if verdict != GRANT:
                    law("selective_revalidation", False, failing_repair=sorted(repaired))
                    return
            else:
                partial_failures += verdict == DENY
                if verdict != DENY:
                    law("selective_revalidation", False, failing_partial=sorted(repaired))
                    return
    law(
        "selective_revalidation",
        True,
        total_revalidations_restoring_standing=total_successes,
        proper_subset_revalidations_denied=partial_failures,
    )


def law_ideal_product_equivalence() -> None:
    """An ideal coordinate-exposing product ties the centralized system exactly.

    This is P6.V4.5 / P7.V3.6 / P8.V3.10 recovered as one statement about donor
    interfaces. Centralization buys nothing when donors expose their coordinates.
    """

    mismatches = 0
    for required in subsets(LADDER):
        model = Model(LADDER, required)
        for observed in subsets(LADDER):
            product = sound_decisive_join_exists(model, coordinate_exposing("ideal", observed))
            if product != is_decisive(model, observed):
                mismatches += 1
    law("ideal_product_equivalence", mismatches == 0, centralized_vs_ideal_product_mismatches=mismatches)


def law_verdict_composition_insufficiency() -> None:
    """Donors that expose only their native verdicts are strictly weaker.

    The ideal-product tie above assumes donors report coordinates. Real parent
    mechanisms report their own local answer to their own question. Enumerating
    every two-donor stack whose observations cover the required coordinates, and
    every join over their verdicts, separates the two regimes: the tie is a
    property of the interface, not of decentralization.
    """

    required = frozenset({"L2_semantic", "L3_obligation"})
    model = Model(LADDER, required)
    indices = [model.index(c) for c in sorted(required)]

    def native(table: tuple[bool, ...]):
        return lambda mo, s: table[sum(bit << k for k, bit in enumerate(s[i] for i in indices))]

    tables = list(itertools.product((False, True), repeat=2 ** len(required)))
    informative = [t for t in tables if len(set(t)) > 1]
    joinable = blocked = 0
    informative_joinable = informative_blocked = 0
    witness = None
    for left, right in itertools.product(tables, repeat=2):
        donors = (
            Donor("donor_a", required, native(left)),
            Donor("donor_b", required, native(right)),
        )
        ok = sound_decisive_join_exists(model, donors)
        joinable += ok
        blocked += not ok
        # A constant donor is a trivial way to lose information, so the same
        # count is reported over donors that actually answer something.
        if left in informative and right in informative:
            informative_joinable += ok
            informative_blocked += not ok
            if not ok and witness is None and left != right:
                witness = {"donor_a_truth_table": list(left), "donor_b_truth_table": list(right)}

    # The interpretable instance: one donor answers "is any evidence still
    # applicable" (L2 or L3), the other "is it semantically applicable" (L2).
    # Between them they look at both required coordinates, and neither their
    # verdicts nor any function of them recovers whether the obligation is
    # discharged, because L2 alone already forces the first donor's answer.
    i2, i3 = model.index("L2_semantic"), model.index("L3_obligation")
    named = (
        Donor("any_evidence_applicable", required, lambda mo, st: st[i2] or st[i3]),
        Donor("semantically_applicable", required, lambda mo, st: st[i2]),
    )
    named_blocked = not sound_decisive_join_exists(model, named)

    ideal_ties = sound_decisive_join_exists(model, coordinate_exposing("ideal", required))
    law(
        "verdict_composition_insufficiency",
        informative_blocked > 0 and named_blocked and ideal_ties,
        stacks_enumerated=joinable + blocked,
        stacks_admitting_a_sound_decisive_join=joinable,
        stacks_where_no_join_over_all_joins_suffices=blocked,
        informative_stacks_enumerated=informative_joinable + informative_blocked,
        informative_stacks_admitting_a_sound_decisive_join=informative_joinable,
        informative_stacks_where_no_join_suffices=informative_blocked,
        named_witness_blocked=named_blocked,
        named_witness="donor A answers L2 or L3; donor B answers L2; both observe L2 and L3",
        every_stack_observes_all_required_coordinates=True,
        ideal_coordinate_exposing_stack_still_decides=ideal_ties,
        first_blocked_witness=witness,
    )


def law_no_alarm_transport_succeeds() -> None:
    """When every required coordinate holds and is retained, standing is granted.

    Cases 1-4 of CROSS_PAPER_PRESERVATION_THEORY_V1 section 10 are separations;
    case 5 is this one. A rule that always abstains passes the separations and
    is useless, so the productive case is asserted, not assumed.
    """

    grants = abstentions = 0
    for required in subsets(LADDER):
        model = Model(LADDER, required)
        for retained in subsets(LADDER):
            if not required <= retained:
                continue
            decide = canonical_rule(model, retained)
            all_true = tuple(True for _ in LADDER)
            verdict = decide(all_true)
            grants += verdict == GRANT
            abstentions += verdict == CANNOT_CHECK
            if verdict != GRANT:
                law("no_alarm_transport_succeeds", False, failing_contract=sorted(required))
                return
    law(
        "no_alarm_transport_succeeds",
        abstentions == 0,
        contracts_granted_when_fully_satisfied=grants,
        spurious_abstentions=abstentions,
    )


def main() -> int:
    for check in (
        law_determination,
        law_soundness_and_forced_abstention,
        law_ladder_irredundancy,
        law_selective_revalidation,
        law_ideal_product_equivalence,
        law_verdict_composition_insufficiency,
        law_no_alarm_transport_succeeds,
    ):
        check()

    receipt = {
        "schema": "orion.cross-paper-preservation.dichotomy-support.v2",
        "ladder": list(LADDER),
        "laws": RESULTS,
        "laws_discharged": len(RESULTS) - len(FAILURES),
        "laws_total": len(RESULTS),
        "failures": FAILURES,
        "scope": (
            "Exhaustive over the registered finite coordinate model. Proof support "
            "for that model; not an empirical claim about deployed donor stacks, and "
            "not a minimality claim outside the registered vocabulary."
        ),
    }
    print(json.dumps(receipt, indent=2))
    return 2 if FAILURES else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # an unrunnable check is not a passing check
        print(json.dumps({"status": "CANNOT_CHECK", "error": str(exc)}))
        sys.exit(3)
