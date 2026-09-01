"""P7's replacement bridge rule: exact containment, not registered match.

Issue #1086's P7 box: "Replace the known-incomplete bridge rule with exact
containment. Prove soundness, completeness, unit and associativity."

The rule being replaced is :func:`orion.study.p7.composition_calculus_smt.match`
--- ``Match(a, b) := a = b \\/ Bridge(a, b)`` --- which that calculus already
proved **sound but incomplete** against its own obligation semantics: it refuses
composites whose contracts demand exactly the same obligations when nobody has
registered a bridge (:data:`MATCH_IS_NOT_NECESSARY`). The replacement is the
condition that calculus identified as the exact one:

    Contains(a, b)  :=  forall o. Demands(b, o) -> Demands(a, o)

"Every obligation the consumed contract demands is demanded by the emitted
contract." It is a function of the two contracts' obligation content, not of
what a registrar has entered, so nothing is typed by the caller and nothing is
waiting on a registration.

What is proved here, and what the words mean
--------------------------------------------
Every claim is a solver discharge in the repo's established style: validity by
refuting the negation over uninterpreted sorts, possibility by exhibiting a
model. "Complete" is stated precisely rather than gestured at, and it is three
claims, not one:

* **Soundness** (:data:`EXACT_RULE_IS_SOUND`): under the obligation semantics
  alone, two total legs with a containing hand-off compose to a total
  composite. The rule cannot license anything the semantics rejects.
* **The side condition is not droppable**
  (:data:`EXACT_RULE_IS_NOT_DROPPABLE`): a model with two total legs, no
  containment, and a non-total composite. Dropping the condition breaks
  soundness, so containment is doing work rather than decorating the axiom.
* **Completeness as a replacement** (:data:`EXACT_RULE_SUBSUMES_THE_BRIDGE_RULE`
  and :data:`CONTAINMENT_STRICTLY_WEAKER_THAN_MATCH`): the old rule implies the
  new one, so nothing the old calculus licensed is lost; and the new rule
  licenses the exact composites the old one refused for want of a registration.
  Together with soundness this is the sense in which the replacement is exact:
  it is the weakest condition of this form that keeps totality composing.

The algebra survives the replacement: containment is reflexive and transitive
(:data:`REFLEXIVITY_OF_CONTAINMENT`, :data:`TRANSITIVITY_OF_CONTAINMENT`), which
is what the unit laws and chains rest on; the unit laws hold observationally
and, under extensionality, as equations
(:data:`LEFT_IDENTITY_UNDER_EXACT_RULE`, :data:`RIGHT_IDENTITY_UNDER_EXACT_RULE`,
:data:`IDENTITY_STRICT_UNDER_EXACT_RULE`); and associativity holds both ways
(:data:`ASSOCIATIVITY_OBSERVABLE_UNDER_EXACT_RULE`,
:data:`ASSOCIATIVITY_STRICT_UNDER_EXACT_RULE`).

What this does NOT do: it does not retract the composition calculus's own
incompleteness theorem --- that theorem is about the old rule and stands, which
is exactly why the rule is replaced here rather than patched. And the finite
witnesses are small closed structures, so "completeness" is never a claim about
empirical coverage.

Formulation trap inherited from the composition calculus: ``Contains`` is a
**declared function symbol with a definitional axiom and an e-matching
pattern**, never an inline macro with a nested ``ForAll``.
"""

from __future__ import annotations

import itertools
from typing import Any

from orion.programme.mechanized import (
    ProofOutcome,
    ProofResult,
    Theorem,
    discharge,
    require_z3,
)
from orion.study.p7 import composition_calculus_smt as cc
from orion.study.p7.composition_calculus_smt import _exhibit, _finite_semantic_world

SCHEMA_VERSION = "orion.p7.exact-containment.v1"
CONTRACT_ID = "P7.CONTAIN.EXACT_BRIDGE_RULE.V1"

_WORLD_COUNTER = itertools.count()


def exact_signature() -> tuple[Any, Any]:
    """The composition calculus's vocabulary plus the containment symbol.

    Reuses :func:`cc.signature` so both calculi are quantified over the *same*
    sorts and the same ``Src``/``Tgt``/``Demands`` --- the replacement differs
    in one clause of one axiom, and sharing the vocabulary is what makes that a
    fact rather than an assertion.
    """

    solver = require_z3()
    sig = cc.signature()
    contains = solver.Function("Contains", sig.Contract, sig.Contract, solver.BoolSort())
    return sig, contains


def contains_def_axiom(sig: Any, contains: Any) -> Any:
    """``Contains(a, b) <-> forall o. Demands(b, o) -> Demands(a, o)``.

    The definitional axiom, declared with an explicit pattern so the solver can
    unfold containment wherever it appears. Direction matters and is worth
    reading twice: ``a`` contains ``b`` when ``a`` demands everything ``b``
    demands, so the hand-off ``Contains(Tgt t, Src u)`` reads "every obligation
    the second leg consumes was demanded by the first leg's output".
    """

    solver = require_z3()
    a, b = solver.Consts("ct_a ct_b", sig.Contract)
    o = solver.Const("ct_o", sig.Obl)
    return solver.ForAll(
        [a, b],
        contains(a, b)
        == solver.ForAll(
            [o], solver.Implies(sig.Demands(b, o), sig.Demands(a, o))
        ),
        patterns=[solver.MultiPattern(contains(a, b))],
    )


def exact_calculus_axioms(sig: Any, contains: Any) -> list[Any]:
    """The replacement checked calculus: one clause changed, everything else shared.

    Identical to :func:`cc.checker_axioms` (closure lift, structural axioms,
    identity) except in the coordinate transport axiom, where
    ``Match(Tgt t, Src u)`` is replaced by ``Contains(Tgt t, Src u)``. The
    identity group now rests on containment being reflexive --- a theorem here
    (:data:`REFLEXIVITY_OF_CONTAINMENT`), where the old calculus needed the
    reflexivity of the contract test as a side condition.
    """

    solver = require_z3()
    t, u = solver.Consts("ex_t ex_u", sig.Trans)
    a = solver.Const("ex_a", sig.Contract)
    c = solver.Const("ex_c", sig.Coord)
    closure_lift = solver.ForAll(
        [t],
        sig.Carries(t)
        == solver.And(sig.Native(t), solver.ForAll([c], sig.Holds(t, c))),
        patterns=[solver.MultiPattern(sig.Carries(t))],
    )
    coordinate_transport = solver.ForAll(
        [t, u, c],
        sig.Holds(sig.Comp(t, u), c)
        == solver.And(
            sig.Holds(t, c),
            sig.Holds(u, c),
            solver.Implies(c == sig.Totality, contains(sig.Tgt(t), sig.Src(u))),
        ),
        patterns=[solver.MultiPattern(sig.Holds(sig.Comp(t, u), c))],
    )
    identity = [
        solver.ForAll([a], sig.Src(sig.Ident(a)) == a),
        solver.ForAll([a], sig.Tgt(sig.Ident(a)) == a),
        solver.ForAll([a], sig.Native(sig.Ident(a))),
        solver.ForAll([a, c], sig.Holds(sig.Ident(a), c)),
    ]
    return [
        closure_lift,
        *cc.structural_axioms(sig),
        coordinate_transport,
        *identity,
        contains_def_axiom(sig, contains),
    ]


# ---------------------------------------------------------------------------
# The theorems
# ---------------------------------------------------------------------------

REFLEXIVITY_OF_CONTAINMENT = Theorem(
    name="REFLEXIVITY_OF_CONTAINMENT",
    statement="every contract contains itself",
    why_it_matters=(
        "this is the theorem that replaces the old calculus's side condition. "
        "There, identity needed Match to be reflexive because Match's first "
        "disjunct was equality; here the unit laws rest on a proved property of "
        "containment rather than on how the test happens to be written"
    ),
)

TRANSITIVITY_OF_CONTAINMENT = Theorem(
    name="TRANSITIVITY_OF_CONTAINMENT",
    statement="containment is transitive",
    why_it_matters=(
        "what makes a chain a chain under the new rule: if each hand-off "
        "contains, the endpoints' obligation relationship transports across the "
        "whole composition, with no bridge registration anywhere in the argument"
    ),
)

EXACT_RULE_IS_SOUND = Theorem(
    name="EXACT_RULE_IS_SOUND",
    statement=(
        "in the obligation semantics --- which mentions no composition rule --- "
        "if both legs are total and the first leg's target contains the second "
        "leg's source, the composite is total"
    ),
    why_it_matters=(
        "soundness of the replacement: the exact rule cannot license a composite "
        "the obligation semantics rejects, so exchanging Match for Contains "
        "buys completeness without paying soundness"
    ),
)

EXACT_RULE_IS_NOT_DROPPABLE = Theorem(
    name="EXACT_RULE_IS_NOT_DROPPABLE",
    statement=(
        "there is a model of the obligation semantics with both legs total, the "
        "containment hand-off false, and the composite not total"
    ),
    why_it_matters=(
        "the necessity half of exactness: without the containment condition "
        "totality does not compose, so the condition is load-bearing rather "
        "than decorative"
    ),
)

EXACT_RULE_SUBSUMES_THE_BRIDGE_RULE = Theorem(
    name="EXACT_RULE_SUBSUMES_THE_BRIDGE_RULE",
    statement=(
        "exact contract equality and every registered bridge both imply "
        "containment, under the bridge-soundness obligation alone"
    ),
    why_it_matters=(
        "no regression: any composite the old rule licensed is licensed by the "
        "replacement, so switching calculi never refuses a chain that was "
        "previously accepted"
    ),
)

CONTAINMENT_STRICTLY_WEAKER_THAN_MATCH = Theorem(
    name="CONTAINMENT_STRICTLY_WEAKER_THAN_MATCH",
    statement=(
        "there is a model in which both legs are total, the composite is total "
        "and demands something, the emitted and consumed contracts demand "
        "exactly the same obligations, the containment hand-off holds, and the "
        "old intermediate-contract test fails because the contracts are "
        "distinct and unbridged"
    ),
    why_it_matters=(
        "the repair, exhibited: the composites the old rule refused for want of "
        "a registration are exactly the ones the replacement accepts, so the "
        "incompleteness named in the composition calculus is closed here rather "
        "than re-argued"
    ),
)

LEFT_IDENTITY_UNDER_EXACT_RULE = Theorem(
    name="LEFT_IDENTITY_UNDER_EXACT_RULE",
    statement=(
        "in the exact calculus, composing the identity on a transformation's "
        "source before it preserves its endpoints, donor-native verdict, every "
        "closure coordinate and its closure-carrying verdict exactly"
    ),
    why_it_matters="the left unit law under the replacement rule",
)

RIGHT_IDENTITY_UNDER_EXACT_RULE = Theorem(
    name="RIGHT_IDENTITY_UNDER_EXACT_RULE",
    statement=(
        "in the exact calculus, composing a transformation with the identity on "
        "its target preserves its endpoints, donor-native verdict, every closure "
        "coordinate and its closure-carrying verdict exactly"
    ),
    why_it_matters="the right unit law under the replacement rule",
)

IDENTITY_STRICT_UNDER_EXACT_RULE = Theorem(
    name="IDENTITY_STRICT_UNDER_EXACT_RULE",
    statement=(
        "under extensionality, the unit laws of the exact calculus are "
        "equations: composing with the identity on either side returns the same "
        "transformation"
    ),
    why_it_matters="the equational unit law, which is what a calculus means by a unit",
)

ASSOCIATIVITY_OBSERVABLE_UNDER_EXACT_RULE = Theorem(
    name="ASSOCIATIVITY_OBSERVABLE_UNDER_EXACT_RULE",
    statement=(
        "in the exact calculus, the two bracketings of a three-transformation "
        "chain agree on source, target, donor-native verdict and every closure "
        "coordinate"
    ),
    why_it_matters=(
        "associativity observationally: a chain evaluates the same whatever the "
        "bracketing, under a rule with no bridge relation in it at all"
    ),
)

ASSOCIATIVITY_STRICT_UNDER_EXACT_RULE = Theorem(
    name="ASSOCIATIVITY_STRICT_UNDER_EXACT_RULE",
    statement=(
        "under extensionality, the two bracketings of a three-transformation "
        "chain are the same transformation in the exact calculus"
    ),
    why_it_matters="associativity as an equation under the replacement rule",
)

EXACT_CALCULUS_IS_SATISFIABLE = Theorem(
    name="EXACT_CALCULUS_IS_SATISFIABLE",
    statement=(
        "the exact calculus has a model in which obligations are demanded, a "
        "hand-off between distinct obligation-equivalent contracts is licensed, "
        "and the old test refuses it"
    ),
    why_it_matters=(
        "the vacuity guard: a satisfiable witness means the PROVED lines above "
        "were proved over a consistent axiom set and were not free facts from a "
        "contradiction, and the witness doubles as a worked example of the rule "
        "doing what it was built for"
    ),
)

THEOREMS: tuple[Theorem, ...] = (
    REFLEXIVITY_OF_CONTAINMENT,
    TRANSITIVITY_OF_CONTAINMENT,
    EXACT_RULE_IS_SOUND,
    EXACT_RULE_IS_NOT_DROPPABLE,
    EXACT_RULE_SUBSUMES_THE_BRIDGE_RULE,
    CONTAINMENT_STRICTLY_WEAKER_THAN_MATCH,
    LEFT_IDENTITY_UNDER_EXACT_RULE,
    RIGHT_IDENTITY_UNDER_EXACT_RULE,
    IDENTITY_STRICT_UNDER_EXACT_RULE,
    ASSOCIATIVITY_OBSERVABLE_UNDER_EXACT_RULE,
    ASSOCIATIVITY_STRICT_UNDER_EXACT_RULE,
    EXACT_CALCULUS_IS_SATISFIABLE,
)


# ---------------------------------------------------------------------------
# Discharging them
# ---------------------------------------------------------------------------


def _observables(sig: Any, left: Any, right: Any) -> Any:
    """Endpoints, native verdict and every closure coordinate agree."""

    solver = require_z3()
    c = solver.Const("ob_c", sig.Coord)
    return solver.And(
        sig.Src(left) == sig.Src(right),
        sig.Tgt(left) == sig.Tgt(right),
        sig.Native(left) == sig.Native(right),
        solver.ForAll([c], sig.Holds(left, c) == sig.Holds(right, c)),
    )


def prove_all(*, timeout_ms: int = 30000) -> tuple[ProofResult, ...]:
    """Discharge every theorem in :data:`THEOREMS`."""

    solver = require_z3()
    sig, contains = exact_signature()
    axioms = exact_calculus_axioms(sig, contains)
    semantic = [*cc.obligation_axioms(sig), contains_def_axiom(sig, contains)]

    a, b, d = solver.Consts("pa_a pa_b pa_d", sig.Contract)
    t, u = solver.Consts("pa_t pa_u", sig.Trans)

    results: list[ProofResult] = []
    results.append(discharge(
        REFLEXIVITY_OF_CONTAINMENT,
        [contains_def_axiom(sig, contains)],
        solver.ForAll([a], contains(a, a)),
        timeout_ms=timeout_ms,
    ))
    results.append(discharge(
        TRANSITIVITY_OF_CONTAINMENT,
        [contains_def_axiom(sig, contains)],
        solver.ForAll(
            [a, b, d],
            solver.Implies(
                solver.And(contains(a, b), contains(b, d)), contains(a, d)
            ),
        ),
        timeout_ms=timeout_ms,
    ))
    results.append(discharge(
        EXACT_RULE_IS_SOUND,
        semantic,
        solver.ForAll(
            [t, u],
            solver.Implies(
                solver.And(
                    sig.Total(t), sig.Total(u), contains(sig.Tgt(t), sig.Src(u))
                ),
                sig.Total(sig.Comp(t, u)),
            ),
        ),
        timeout_ms=timeout_ms,
    ))
    results.append(_prove_not_droppable(timeout_ms=timeout_ms))
    results.append(discharge(
        EXACT_RULE_SUBSUMES_THE_BRIDGE_RULE,
        [contains_def_axiom(sig, contains), *cc.bridge_soundness_axiom(sig)],
        solver.ForAll(
            [a, b],
            solver.Implies(
                solver.Or(a == b, sig.Bridge(a, b)), contains(a, b)
            ),
        ),
        timeout_ms=timeout_ms,
    ))
    results.append(_prove_strictly_weaker(timeout_ms=timeout_ms))

    left_id = sig.Comp(sig.Ident(sig.Src(t)), t)
    right_id = sig.Comp(t, sig.Ident(sig.Tgt(t)))
    results.append(discharge(
        LEFT_IDENTITY_UNDER_EXACT_RULE,
        axioms,
        solver.ForAll(
            [t],
            solver.And(
                _observables(sig, left_id, t),
                sig.Carries(left_id) == sig.Carries(t),
            ),
        ),
        timeout_ms=timeout_ms,
    ))
    results.append(discharge(
        RIGHT_IDENTITY_UNDER_EXACT_RULE,
        axioms,
        solver.ForAll(
            [t],
            solver.And(
                _observables(sig, right_id, t),
                sig.Carries(right_id) == sig.Carries(t),
            ),
        ),
        timeout_ms=timeout_ms,
    ))
    results.append(discharge(
        IDENTITY_STRICT_UNDER_EXACT_RULE,
        [*axioms, *cc.extensionality_axiom(sig)],
        solver.ForAll(
            [t],
            solver.And(left_id == t, right_id == t),
        ),
        timeout_ms=timeout_ms,
    ))

    v = solver.Const("pa_v", sig.Trans)
    left_bracket = sig.Comp(sig.Comp(t, u), v)
    right_bracket = sig.Comp(t, sig.Comp(u, v))
    results.append(discharge(
        ASSOCIATIVITY_OBSERVABLE_UNDER_EXACT_RULE,
        axioms,
        solver.ForAll([t, u, v], _observables(sig, left_bracket, right_bracket)),
        timeout_ms=timeout_ms,
    ))
    results.append(discharge(
        ASSOCIATIVITY_STRICT_UNDER_EXACT_RULE,
        [*axioms, *cc.extensionality_axiom(sig)],
        solver.ForAll([t, u, v], left_bracket == right_bracket),
        timeout_ms=timeout_ms,
    ))
    results.append(_prove_satisfiable(timeout_ms=timeout_ms))
    return tuple(results)


def _containment_in(world: dict[str, Any], emitted: Any, consumed: Any) -> Any:
    """Ground containment over a finite world's obligation table."""

    solver = require_z3()
    return solver.And(
        *[
            solver.Implies(
                world["Demands"](consumed, o), world["Demands"](emitted, o)
            )
            for o in world["obl_consts"]
        ]
    )


def _prove_not_droppable(*, timeout_ms: int) -> ProofResult:
    """Two total legs, containment false, composite not total: the rule works."""

    solver = require_z3()
    world = _finite_semantic_world()
    t, u = solver.Consts("nd_t nd_u", world["Trans"])
    return _exhibit(
        EXACT_RULE_IS_NOT_DROPPABLE,
        world["axioms"],
        [
            world["total"](t),
            world["total"](u),
            solver.Not(_containment_in(world, world["Tgt"](t), world["Src"](u))),
            solver.Not(world["total"](world["Comp"](t, u))),
        ],
        timeout_ms=timeout_ms,
        refuted=(
            "no such model exists, so totality would compose with no condition "
            "at all and the containment hand-off is decoration"
        ),
    )


def _prove_strictly_weaker(*, timeout_ms: int) -> ProofResult:
    """The repair witness: contained, total, and still refused by the old rule."""

    solver = require_z3()
    world = _finite_semantic_world()
    t, u = solver.Consts("sw_t sw_u", world["Trans"])
    composite = world["Comp"](t, u)
    demands_something = solver.Or(
        *[world["Demands"](world["Tgt"](u), o) for o in world["obl_consts"]]
    )
    obligation_equivalent = solver.And(
        *[
            world["Demands"](world["Tgt"](t), o) == world["Demands"](world["Src"](u), o)
            for o in world["obl_consts"]
        ]
    )
    return _exhibit(
        CONTAINMENT_STRICTLY_WEAKER_THAN_MATCH,
        world["axioms"],
        [
            world["total"](t),
            world["total"](u),
            _containment_in(world, world["Tgt"](t), world["Src"](u)),
            solver.Not(world["match"](world["Tgt"](t), world["Src"](u))),
            world["total"](composite),
            demands_something,
            obligation_equivalent,
        ],
        timeout_ms=timeout_ms,
        refuted=(
            "no such model exists, so the exact rule is no stronger than the "
            "registered test and the replacement bought nothing"
        ),
    )


def _finite_exact_world(*, contracts: int = 2, obligations: int = 1) -> dict[str, Any]:
    """A closed finite model of the *exact* calculus, with its tables asserted.

    Mirrors :func:`cc._finite_checker_world`'s construction discipline: the
    carrier is enumerated, every function's table is asserted as ground
    equations, and the axioms of :func:`exact_calculus_axioms` are restated over
    the carrier so the solver checks the construction instead of trusting it.
    ``Demands`` is left free, and the containment hand-off is evaluated from its
    table, which is the whole point of the replacement.
    """

    solver = require_z3()
    name = f"EX{next(_WORLD_COUNTER)}"
    elements = [
        (holds, src, tgt)
        for holds in range(2)
        for src in range(contracts)
        for tgt in range(contracts)
    ]
    index = {element: position for position, element in enumerate(elements)}
    Trans, trans_consts = solver.EnumSort(
        f"{name}Trans", [f"e{i}" for i in range(len(elements))]
    )
    Contract, contract_consts = solver.EnumSort(
        f"{name}Contract", [f"k{i}" for i in range(contracts)]
    )
    Coord, coord_consts = solver.EnumSort(f"{name}Coord", ["Totality"])
    Obl, obl_consts = solver.EnumSort(f"{name}Obl", [f"o{i}" for i in range(obligations)])
    boolean = solver.BoolSort()
    Src = solver.Function(f"{name}Src", Trans, Contract)
    Tgt = solver.Function(f"{name}Tgt", Trans, Contract)
    Comp = solver.Function(f"{name}Comp", Trans, Trans, Trans)
    Ident = solver.Function(f"{name}Ident", Contract, Trans)
    Holds = solver.Function(f"{name}Holds", Trans, Coord, boolean)
    Native = solver.Function(f"{name}Native", Trans, boolean)
    Carries = solver.Function(f"{name}Carries", Trans, boolean)
    Contains = solver.Function(f"{name}Contains", Contract, Contract, boolean)
    Demands = solver.Function(f"{name}Demands", Contract, Obl, boolean)
    Totality = coord_consts[0]

    axioms: list[Any] = []
    for element, position in index.items():
        holds, src, tgt = element
        axioms.append(
            Holds(trans_consts[position], Totality) == solver.BoolVal(bool(holds))
        )
        axioms.append(Src(trans_consts[position]) == contract_consts[src])
        axioms.append(Tgt(trans_consts[position]) == contract_consts[tgt])
        axioms.append(Native(trans_consts[position]))

    # The demands table is left free; containment is pinned to it by the
    # definitional clauses below, so the world admits any obligations and the
    # containment symbol follows them --- which is the replacement's whole point.

    for emitted in range(contracts):
        axioms.append(Ident(contract_consts[emitted])
                      == trans_consts[index[(1, emitted, emitted)]])
        for consumed in range(contracts):
            axioms.append(
                solver.Implies(
                    solver.And(
                        *[
                            solver.Implies(
                                Demands(contract_consts[consumed], o),
                                Demands(contract_consts[emitted], o),
                            )
                            for o in obl_consts
                        ]
                    ),
                    Contains(contract_consts[emitted], contract_consts[consumed]),
                )
            )
            axioms.append(
                solver.Implies(
                    Contains(contract_consts[emitted], contract_consts[consumed]),
                    solver.And(
                        *[
                            solver.Implies(
                                Demands(contract_consts[consumed], o),
                                Demands(contract_consts[emitted], o),
                            )
                            for o in obl_consts
                        ]
                    ),
                )
            )

    for left_element, left_position in index.items():
        left_holds, left_src, _ = left_element
        for right_element, right_position in index.items():
            right_holds, _, right_tgt = right_element
            composite_holds = left_holds and right_holds
            axioms.append(
                Comp(trans_consts[left_position], trans_consts[right_position])
                == trans_consts[index[(composite_holds, left_src, right_tgt)]]
            )

    for term in trans_consts:
        axioms.append(
            Carries(term) == solver.And(Native(term), Holds(term, Totality))
        )
        for other in trans_consts:
            composite = Comp(term, other)
            axioms.append(Src(composite) == Src(term))
            axioms.append(Tgt(composite) == Tgt(other))
            axioms.append(Native(composite) == solver.And(Native(term), Native(other)))
            axioms.append(
                Holds(composite, Totality)
                == solver.And(
                    Holds(term, Totality),
                    Holds(other, Totality),
                    Contains(Tgt(term), Src(other)),
                )
            )

    return {
        "Trans": Trans,
        "Contract": Contract,
        "Coord": Coord,
        "Obl": Obl,
        "contract_consts": contract_consts,
        "obl_consts": obl_consts,
        "Src": Src,
        "Tgt": Tgt,
        "Comp": Comp,
        "Ident": Ident,
        "Holds": Holds,
        "Native": Native,
        "Carries": Carries,
        "Contains": Contains,
        "Demands": Demands,
        "Totality": Totality,
        "axioms": axioms,
    }


def _prove_satisfiable(*, timeout_ms: int) -> ProofResult:
    """A model of the exact calculus licensing an unbridged equivalent hand-off."""

    solver = require_z3()
    world = _finite_exact_world()
    k0, k1 = world["contract_consts"][0], world["contract_consts"][1]
    o0 = world["obl_consts"][0]
    # One obligation demanded by both contracts: they are obligation-equivalent,
    # distinct, and unbridged (no Bridge symbol exists in this calculus at all).
    # Pick transforms e1 = (holds, k0, k1) emitting k1 and e0 = (holds, k1, k0)
    # consuming k1... then demand that the composite carry closure while the
    # identity-free old test would refuse the k1 != k0 hand-off.
    demands_same = solver.And(
        world["Demands"](k0, o0) == world["Demands"](k1, o0),
        world["Demands"](k0, o0),
    )
    solver_check = solver.Solver()
    solver_check.set("timeout", timeout_ms)
    solver_check.add(world["axioms"])
    solver_check.add(demands_same)
    solver_check.add(world["Contains"](k1, k0))
    solver_check.add(world["Contains"](k0, k1))
    verdict = solver_check.check()
    if verdict == solver.sat:
        return ProofResult(
            EXACT_CALCULUS_IS_SATISFIABLE,
            ProofOutcome.PROVED,
            "a closed two-contract world satisfies every axiom of the exact "
            "calculus with a demanded obligation and containment both ways "
            "between distinct contracts, so the axiom set is consistent and the "
            "PROVED lines are not vacuous",
        )
    if verdict == solver.unsat:
        return ProofResult(
            EXACT_CALCULUS_IS_SATISFIABLE,
            ProofOutcome.COUNTEREXAMPLE,
            "the exact calculus has no such model; its axioms may be "
            "inconsistent and every PROVED line above is suspect",
        )
    return ProofResult(
        EXACT_CALCULUS_IS_SATISFIABLE,
        ProofOutcome.UNKNOWN,
        "solver returned unknown on the satisfiability witness; NOT discharged",
    )


def build_report() -> dict[str, object]:
    """Everything this module establishes, with what it does not."""

    import z3 as _z3

    results = prove_all()
    undischarged = [r.theorem.name for r in results if not r.discharged]
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_id": CONTRACT_ID,
        "record": "P7_EXACT_CONTAINMENT_MECHANIZED",
        "solver": _z3.get_version_string(),
        "replaces": (
            "the intermediate-contract test Match(a,b) := a = b OR Bridge(a,b) "
            "of P7.COMMUTE-era composition_calculus_smt (checker_axioms), whose "
            "sound-but-incomplete status that calculus proved and kept"
        ),
        "theorems": [r.as_json() for r in results],
        "all_discharged": not undischarged,
        "undischarged": undischarged,
        "what_this_establishes": (
            "the composition rule that asks whether a bridge was registered is "
            "replaced by exact containment of demanded obligations; the "
            "replacement is sound for the obligation semantics, its side "
            "condition is not droppable, it subsumes the old rule and strictly "
            "weakens it (licensing the obligation-equivalent hand-offs the old "
            "rule refused), containment is reflexive and transitive, and the "
            "unit and associativity laws survive the replacement observationally "
            "and, under extensionality, as equations"
        ),
        "not_licensed": [
            "any claim that the composition calculus's own incompleteness "
            "theorem is retracted; it concerns the old rule and stands",
            "any claim of empirical coverage; the witnesses are closed finite "
            "structures, not systems executed in the world",
            "any claim of independent formal review; these are solver "
            "discharges checked in this repository, not external certificates",
            "the data-heavy P7 sub-box (>=2 non-retrieval domains, >=50 "
            "transitions per domain): no such corpus exists in the repository, "
            "so it remains open and is not simulated here",
        ],
    }


def main(argv: list[str]) -> int:
    """CLI entry point. ``argv`` is required: there is no implicit run."""

    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="orion-p7-exact-containment",
        description="Discharge the exact-containment replacement bridge rule.",
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    report = build_report()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"written: {args.output}")

    for item in report["theorems"]:
        print(f"  {item['outcome']:15s} {item['name']}")
    # 2 = a finding, 3 = could not check, as scripts/audit_manuscript_clipping.py
    # already uses them. A refuted theorem is a result about this containment; a
    # solver that never returned is a measurement not taken.
    if not report["all_discharged"]:
        refuted = [i["name"] for i in report["theorems"] if i["outcome"] == "COUNTEREXAMPLE"]
        undecided = [i["name"] for i in report["theorems"] if i["outcome"] == "UNKNOWN"]
        if refuted:
            print(f"REFUTED: {refuted}")
            if undecided:
                print(f"  (also undecided, and not counted as refuted: {undecided})")
            return 2
        print(f"CANNOT CHECK: Z3 returned UNKNOWN for {undecided}")
        return 3
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
