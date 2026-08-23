"""The X4 donor model as an interpretation of the proved authority primitives.

``P8-U-T2`` asks for P8's finite result to follow as an instance of the general
theorem rather than standing beside it, and ``P8-U-T1``'s unblock names the one
step both need: interpret the donor model in the primitives
:mod:`orion.study.p8.authority_calculus_smt` proves about, and show the
interpretation sound.

This is that step. It is a *derivation*, not a second table: nothing here
restates an X4 outcome. Each of the seven arguments X4's terminal takes is
assigned to the calculus conjunct it means, the calculus's own rule is evaluated
under that assignment, and the two verdicts are compared.

The assignment
--------------
``TYPE_COORDS`` is ``('domain', 'kind', 'scope', 'content', 'epoch')`` --- the
five flags are type-coordinate agreement --- and ``protected_coercion`` is a
registered conversion. That is exactly the calculus's ``Reach``: authority
arrives in a domain either because the types already agree or because someone
registered a conversion. The correspondence was not forced; it is why this
interpretation is plausible at all.

===========================  ==================================================
X4 argument                  calculus conjunct
===========================  ==================================================
``native_valid``             the judgment is valid
``narrowing_ok``             the action's scope is contained in the judgment's
``all(flags) or coercion``   the action's domain is reachable from the judgment's
``blocker == 'REFUTED'``     every hard obligation is satisfied
``blocker == 'ESTABLISHED'`` a defeater is active
``support_a or support_b``   a further hard obligation: some support family carries
===========================  ==================================================

``Trusted`` and epoch equality are not separately modelled by X4 --- epoch is one
of the five type coordinates and enters through the flags --- so the
interpretation sets them true and says so rather than inventing arguments to
carry them.

Precedence is where a boolean rule becomes a four-valued one
-----------------------------------------------------------
``authorize`` is a conjunction and answers yes or no. X4 answers with four
values, and their order is load-bearing: a narrowing failure outranks an
undetermined blocker, so a case that both fails narrowing *and* has an
undetermined blocker is ``BLOCK`` and not ``CANNOT_CHECK``. That precedence is
stated here as part of the refinement, because it is a real commitment of the
model and not a consequence of the conjunction.
"""

from __future__ import annotations

from typing import Any

from orion.study.p8.authority_terminals import x4_donor_axis, x4_module, x4_space

SCHEMA_VERSION = "orion.p8.donor-interpretation.v1"

#: X4's four terminals.
NO_DONOR_AUTHORITY = "NO_DONOR_AUTHORITY"
BLOCK = "BLOCK"
CANNOT_CHECK = "CANNOT_CHECK"
DISCHARGE = "DISCHARGE"


def interpret(point: dict[str, Any]) -> dict[str, Any]:
    """Assign one X4 point to the calculus's conjuncts.

    Returns the conjuncts by the calculus's own names, so a reader can check the
    assignment against ``authority_calculus_smt.authorize`` line by line.
    """

    flags = tuple(bool(flag) for flag in point["scientific_type"])
    blocker = str(point["blocker"])
    return {
        "valid": bool(point["native_valid"]),
        # Not modelled separately by X4; declared rather than invented.
        "trusted_issuer": True,
        "epoch_matches": True,
        "action_scope_within_judgment_scope": bool(point["narrowing_ok"]),
        "action_domain_reachable": all(flags) or bool(point["protected_coercion"]),
        "obligations_all_sat": blocker == "REFUTED"
        and (bool(point["support_a"]) or bool(point["support_b"])),
        "defeater_active": blocker == "ESTABLISHED",
        # Retained for the refinement's precedence, not consulted by `authorize`.
        "_blocker": blocker,
    }


def authorize_under_interpretation(conjuncts: dict[str, Any]) -> bool:
    """The calculus's authorisation rule, evaluated on an interpreted point.

    Transcribed from ``authority_calculus_smt.authorize``'s conjunction in the
    same order, so the two cannot drift without this reading differently.
    """

    return bool(
        conjuncts["valid"]
        and conjuncts["trusted_issuer"]
        and conjuncts["epoch_matches"]
        and conjuncts["action_scope_within_judgment_scope"]
        and conjuncts["action_domain_reachable"]
        and conjuncts["obligations_all_sat"]
        and not conjuncts["defeater_active"]
    )


def derived_terminal(point: dict[str, Any]) -> str:
    """X4's terminal, derived from the calculus rather than looked up.

    The four-valued refinement, in the precedence the model commits to:

    1. an invalid judgment carries no authority at all;
    2. a scope that is not narrowed blocks, and outranks an undetermined
       obligation --- this is the ordering that has to be stated;
    3. an active defeater blocks;
    4. an undetermined obligation is undetermined, not refused;
    5. otherwise the calculus's own conjunction decides.
    """

    conjuncts = interpret(point)
    if not conjuncts["valid"]:
        return NO_DONOR_AUTHORITY
    if not conjuncts["action_scope_within_judgment_scope"]:
        return BLOCK
    if conjuncts["defeater_active"]:
        return BLOCK
    if conjuncts["_blocker"] == "UNDETERMINED":
        return CANNOT_CHECK
    return DISCHARGE if authorize_under_interpretation(conjuncts) else BLOCK


def distinct_states() -> tuple[dict[str, Any], ...]:
    """One representative per verdict-relevant state.

    The donor axis is inert --- ``scientific_terminal`` takes seven arguments and
    the donor is not among them --- so the 39,936 enumerated points are 3,072
    distinct states replayed thirteen times. Deriving all 39,936 would be
    deriving the same 3,072 thirteen times, so the instance count reported here
    is the honest one.
    """

    seen: set[tuple[Any, ...]] = set()
    out: list[dict[str, Any]] = []
    for point in x4_space():
        key = (
            bool(point["native_valid"]),
            tuple(bool(f) for f in point["scientific_type"]),
            bool(point["narrowing_ok"]),
            str(point["blocker"]),
            bool(point["support_a"]),
            bool(point["support_b"]),
            bool(point["protected_coercion"]),
        )
        if key not in seen:
            seen.add(key)
            out.append(point)
    return tuple(out)


def soundness_check() -> dict[str, Any]:
    """Does the calculus, under this interpretation, reproduce X4 exactly?

    Exhaustive over every distinct state. Disagreement anywhere means the
    interpretation is wrong and is reported as such rather than tolerated: an
    interpretation that matches on most states derives nothing.
    """

    from collections import Counter

    module = x4_module()
    states = distinct_states()
    disagreements: list[str] = []
    disagreement_count = 0
    by_terminal: Counter[str] = Counter()

    for point in states:
        shipped = module.scientific_terminal(
            point["native_valid"],
            point["scientific_type"],
            point["narrowing_ok"],
            point["blocker"],
            point["support_a"],
            point["support_b"],
            point["protected_coercion"],
        )
        derived = derived_terminal(point)
        by_terminal[shipped] += 1
        if shipped != derived:
            # Counted in full, exemplified up to twenty. The first version of
            # this derived the agreement count from the truncated list, so a
            # thousand disagreements would have been reported as twenty.
            disagreement_count += 1
        if shipped != derived and len(disagreements) < 20:
            disagreements.append(
                f"native={point['native_valid']} flags={point['scientific_type']} "
                f"narrowing={point['narrowing_ok']} blocker={point['blocker']} "
                f"support=({point['support_a']},{point['support_b']}) "
                f"coercion={point['protected_coercion']}: "
                f"shipped={shipped} derived={derived}"
            )

    axis = x4_donor_axis()
    return {
        "schema_version": SCHEMA_VERSION,
        "distinct_states": len(states),
        "total_enumerated_points": len(x4_space()),
        "donor_replication": axis.multiplier,
        "agreements": len(states) - disagreement_count,
        "disagreement_count": disagreement_count,
        "disagreement_examples": disagreements,
        "examples_truncated": disagreement_count > len(disagreements),
        "sound": disagreement_count == 0,
        "terminals_covered": dict(sorted(by_terminal.items())),
        "every_terminal_reached": len(by_terminal) == 4,
    }
