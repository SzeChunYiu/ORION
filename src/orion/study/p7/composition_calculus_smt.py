"""A machine-checked composition calculus for P7, over arbitrary transformation chains.

P7's compositional result is currently a *registered navigation model*.
``research/claim_expansion/p7/check_p7_x2_closure_carrying.py`` --- the artifact
``P7-U-T1`` names --- is two functions::

    def carries(native_valid: bool, closure: tuple[bool, ...]) -> bool:
        return native_valid and all(closure)

    def compose(c1: bool, c2: bool, bridge_match: bool) -> bool:
        return c1 and c2 and bridge_match

and the published ``composition_successes: 25`` /
``composition_bridge_countermodels: 25`` come from a double loop over five donor
families in which neither donor is read, ``c1`` and ``c2`` are the same constant
``True``, and ``bridge_match`` is a literal. That is one fact counted 25 times at
two of the eight argument triples of ``compose``; ``orion.study.p7.closure_premises``
already measures it as such. ``P7-U-T1`` asks for something else:

    Define primitive transformation and obligation semantics, then prove or
    explicitly characterize identity, associativity and intermediate-contract
    composition.

This module is that. Transformations, contracts, closure coordinates and
obligations are **uninterpreted sorts**, so nothing here knows that there are
five donor families or five closure coordinates; the donor-native validity
predicate is an **uninterpreted function**, so the theorems hold for every donor
whose native predicate anyone might register rather than for the five that were.
Composition and identity are function symbols constrained only by the axioms
below, so a chain is any chain.

Two layers, and the second is the one that makes the first mean anything
-------------------------------------------------------------------------
**The checked calculus** (:func:`checker_axioms`) is P7's rule generalised. Its
one substantive axiom is *coordinate transport*: a composite holds a closure
coordinate exactly when both legs hold it, and the distinguished coordinate
``obligations_total`` additionally requires the intermediate contract to match.
From that, ``Carries(Comp(t,u)) <-> Carries(t) /\\ Carries(u) /\\ Match(Tgt t, Src u)``
is a **theorem** --- :data:`INTERMEDIATE_CONTRACT_COMPOSITION` --- and not an
axiom, which matters because that formula is exactly P7's ``compose`` and a
calculus that assumed it would be assuming its own conclusion.

**The obligation semantics** (:func:`semantic_axioms`) says what
``obligations_total`` *means*: every obligation demanded at a transformation's
target is demanded at its source, discharged by the transformation, or declared
new. That layer is defined without reference to composition rules, and it is
what decides whether the intermediate-contract test in the checked layer is the
right test. It reports two things:

* Matching intermediate contracts **suffice** (:data:`TOTALITY_COMPOSES_UNDER_MATCH`).
* They are **not necessary** (:data:`MATCH_IS_NOT_NECESSARY`). The exact
  condition is weaker --- containment of the second leg's source demands in the
  first leg's target demands (:data:`CONTAINMENT_IS_THE_EXACT_CONDITION`) --- so
  P7's rule is a *sound but incomplete, fail-closed* approximation of its own
  semantics. It refuses composites that are in fact total. That is a real gap
  and is reported as one rather than smoothed over.

Where the properties need a side condition
------------------------------------------
Identity and associativity hold **observationally** with nothing assumed of the
registered bridge relation --- no reflexivity, no symmetry, no transitivity ---
which is the non-obvious half, since bridges are registered one at a time and
compose in no way at all. Two conditions are nonetheless doing work, one on the
*test* rather than on the relation and one on the calculus itself, and each is
stated with the countermodel showing it is not decoration:

* Identity needs the intermediate-contract test to be **reflexive**. It is,
  because ``Match(a,b) := a = b \\/ Bridge(a,b)`` is how P7's own theorem
  statement reads ("exactly the same contract, **or** a registered bridge"). With
  the raw registered relation in its place the unit law fails --- see
  :data:`IDENTITY_NEEDS_A_REFLEXIVE_CONTRACT_TEST`.
* Strict equality of the two bracketings needs **extensionality**: that the
  calculus does not distinguish transformations agreeing on source, target,
  native validity and every closure coordinate. Without it the observable laws
  still hold and the equations do not --- see :data:`STRICT_LAWS_NEED_EXTENSIONALITY`.

The premise the committed checker was handed
--------------------------------------------
``research/failures/2026-08-supplied-premise-unbuilt-decision/`` records that
``bridge_match`` in P7's model is a **literal typed by the caller**, not a
quantity computed from the two transformations, and closes with an open item for
the theory lane: "give the closure-carrying model a contract object, so
``bridge_match`` is computed from the two transforms rather than typed. Both are
the theory lane's call and are **not** done here."

Here it is done. ``Match(Tgt(t), Src(u))`` is a function of the two
transformations and of the registered bridge relation --- ``Src`` and ``Tgt`` are
functions on ``Trans``, ``Bridge`` is a relation on ``Contract`` --- so the
intermediate-contract test is no longer an argument that can be supplied. There
is nothing left to type in: a chain either has matching hand-offs or it does not,
and which it is falls out of the transformations. That does not retroactively
repair the committed artifact, whose counts still come from an expression in
which no transform, contract or bridge appears; it means the calculus proved here
does not have the hole the committed model has.

What is machine-checked and how
-------------------------------
Validity claims are discharged as the unsatisfiability of their negation over
the uninterpreted signature, so they hold in *every* model. Independence claims
--- "this does not follow" --- are discharged by exhibiting a model, and are
checked in explicitly constructed **closed finite structures** whose function
tables are asserted as ground equations, so the solver verifies that the
structure satisfies every axiom rather than taking the construction on trust.

That split is not stylistic. Satisfiability queries over the uninterpreted
signature come back ``unknown`` every time: the quantified axioms defeat
model-based instantiation. Reporting those as anything but ``UNKNOWN`` would be
the failure :class:`orion.programme.mechanized.ProofOutcome` is three-valued to
prevent, so the finite structures exist to give the independence results an
answer that is actually an answer.

The same limitation has a consequence a reader of this report should have in
hand. Over the uninterpreted signature a **false** claim comes back ``UNKNOWN``
rather than ``COUNTEREXAMPLE``, because refuting it means building a model and
that is the thing the solver cannot do here. No ``PROVED`` line is weakened by
that --- ``unsat`` is sound, and a false claim can never produce one --- but the
failure mode to watch for in the validity half is a theorem that is *not
discharged*, not a printed countermodel. In the finite structures, where the
problem is decidable, countermodels are produced normally. Both behaviours are
pinned by tests.

Two formulation traps are recorded because they cost the same kind of time as
P8's missing rank axiom, and because in both cases the claim was right and the
*writing* of it was what the solver could not do.

* ``Carries`` and ``Total`` must be **declared function symbols with definitional
  axioms and explicit e-matching patterns**. Written inline as macros containing
  a nested ``ForAll``, three of the checked-calculus theorems and both obligation
  theorems time out to ``UNKNOWN``.
* The chain ladder must run **under the already-discharged one-step lemma**.
  Expanded straight from the coordinate transport axiom, lengths three, five,
  six, seven and eight all time out --- only two and four close. Under the lemma
  every length closes in milliseconds. :func:`prove_chain_ladder` therefore
  re-discharges the lemma from the axioms alone and uses it only if that run
  comes back ``PROVED``, so a lemma being used cannot quietly become an axiom
  being added.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Any

from orion.programme.mechanized import (
    DifferentialReport,
    ProofOutcome,
    ProofResult,
    Theorem,
    Z3Unavailable,
    discharge,
    load_executable_model as _load_model,
    require_z3,
)
from orion.programme.mechanized import z3

SCHEMA_VERSION = "orion.p7.composition-calculus-smt.v1"

#: The executable model ``P7-U-T1`` names, via ``P7_X2_CLOSURE_CARRYING_RESULT_V1.json``.
EXECUTABLE_MODEL = "research/claim_expansion/p7/check_p7_x2_closure_carrying.py"

#: The committed result artifact whose counts :func:`instantiation_check` re-derives.
COMMITTED_RESULT = "research/claim_expansion/p7/P7_X2_CLOSURE_CARRYING_RESULT_V1.json"

#: How far :func:`prove_chain_ladder` expands the chain theorem explicitly.
CHAIN_LADDER_BOUND = 8

#: P7's five registered closure coordinates, in the committed checker's order.
#: They appear only in the differential and the instantiation check; no theorem
#: below knows how many there are.
CLOSURE_COORDINATES: tuple[str, ...] = (
    "obligations_total",
    "obligations_unambiguous",
    "frontier_resolved",
    "objective_semantics_preserved",
    "closure_epoch_current",
)

#: Distinct names for the finite structures, so repeated calls do not collide on
#: z3's enumeration-sort namespace.
_WORLD_COUNTER = itertools.count()

__all__ = [
    "CHAIN_LADDER_BOUND",
    "CLOSURE_COORDINATES",
    "COMMITTED_RESULT",
    "DifferentialReport",
    "EXECUTABLE_MODEL",
    "ProofOutcome",
    "ProofResult",
    "SCHEMA_VERSION",
    "THEOREMS",
    "Theorem",
    "Z3Unavailable",
    "axiom_pin_bridge_soundness",
    "build_report",
    "checker_axiom_groups",
    "checker_axioms",
    "composition_lemma",
    "differential_check",
    "discharge",
    "extensionality_axiom",
    "instantiation_check",
    "main",
    "match",
    "prove_all",
    "prove_chain_ladder",
    "prove_hinge",
    "semantic_axioms",
    "signature",
]


# ---------------------------------------------------------------------------
# Primitive semantics. Nothing below names a donor family or a coordinate.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Signature:
    """The uninterpreted vocabulary every theorem is quantified over."""

    Trans: Any
    Contract: Any
    Coord: Any
    Obl: Any
    Native: Any
    Holds: Any
    Carries: Any
    Src: Any
    Tgt: Any
    Bridge: Any
    Comp: Any
    Ident: Any
    Totality: Any
    Diff: Any
    Demands: Any
    Discharged: Any
    Fresh: Any
    Total: Any


def signature() -> Signature:
    """Build the vocabulary. Sorts are uninterpreted, so cardinality is free.

    That is the whole force of the generalisation. ``Coord`` is not five values,
    it is a sort; ``Trans`` is not five donor families, it is a sort. A theorem
    discharged over this signature holds for a calculus with any number of
    closure coordinates, contracts and transformations, including infinitely
    many, and for every donor-native validity predicate --- ``Native`` is left
    uninterpreted because P7's own theorem family says it does not alter the
    donor's predicate.

    ``Totality`` is the one distinguished constant: the closure coordinate that
    the intermediate-contract test bears on. It is a constant of an
    uninterpreted sort, not an index into a list of five, so the theorems do not
    depend on which coordinate it is or on how many others there are.
    """

    solver = require_z3()
    Trans = solver.DeclareSort("P7Trans")
    Contract = solver.DeclareSort("P7Contract")
    Coord = solver.DeclareSort("P7Coord")
    Obl = solver.DeclareSort("P7Obl")
    boolean = solver.BoolSort()
    return Signature(
        Trans=Trans,
        Contract=Contract,
        Coord=Coord,
        Obl=Obl,
        # The donor's own validity/preservation/round-trip verdict, uninterpreted.
        Native=solver.Function("Native", Trans, boolean),
        # Per-coordinate closure status after a transformation.
        Holds=solver.Function("Holds", Trans, Coord, boolean),
        # The closure lift, as a declared symbol with a definitional axiom.
        Carries=solver.Function("Carries", Trans, boolean),
        Src=solver.Function("Src", Trans, Contract),
        Tgt=solver.Function("Tgt", Trans, Contract),
        # The registered bridge relation between obligation contracts.
        Bridge=solver.Function("Bridge", Contract, Contract, boolean),
        Comp=solver.Function("Comp", Trans, Trans, Trans),
        Ident=solver.Function("Ident", Contract, Trans),
        Totality=solver.Const("Totality", Coord),
        # Skolem witness for extensionality; see `extensionality_axiom`.
        Diff=solver.Function("Diff", Trans, Trans, Coord),
        # The obligation layer.
        Demands=solver.Function("Demands", Contract, Obl, boolean),
        Discharged=solver.Function("Discharged", Trans, Obl, boolean),
        Fresh=solver.Function("Fresh", Trans, Obl, boolean),
        Total=solver.Function("Total", Trans, boolean),
    )


def match(sig: Signature, left: Any, right: Any) -> Any:
    """The intermediate-contract test, verbatim from P7's own theorem statement.

    ``T5`` reads: two closure-carrying transforms compose only when the target
    obligation contract produced by the first *is exactly* the source obligation
    contract consumed by the second, **or a registered bridge witnesses their
    equivalence**. Both disjuncts are here, and the first is why the test is
    reflexive --- which :data:`IDENTITY_NEEDS_A_REFLEXIVE_CONTRACT_TEST` shows is
    the whole reason identity is a unit.
    """

    solver = require_z3()
    return solver.Or(left == right, sig.Bridge(left, right))


def structural_axioms(sig: Signature) -> list[Any]:
    """What composing does to endpoints and to the donor-native verdict.

    Shared by both layers, because both are talking about the same composite.
    The two endpoint clauses are what make a chain a chain: a composite starts
    where its first leg starts and ends where its last leg ends. The third is
    donor conservativity in its composite form --- the native verdict of a
    composite is the conjunction of the legs' native verdicts and depends on
    nothing else, so no closure coordinate and no bridge can alter a donor's own
    answer. :data:`DONOR_CONSERVATIVITY` is that clause turned into a claim
    about arbitrary transformations.
    """

    solver = require_z3()
    t, u = solver.Consts("ax_t ax_u", sig.Trans)
    return [
        solver.ForAll([t, u], sig.Src(sig.Comp(t, u)) == sig.Src(t)),
        solver.ForAll([t, u], sig.Tgt(sig.Comp(t, u)) == sig.Tgt(u)),
        solver.ForAll(
            [t, u], sig.Native(sig.Comp(t, u)) == solver.And(sig.Native(t), sig.Native(u))
        ),
    ]


def checker_axiom_groups(sig: Signature) -> dict[str, list[Any]]:
    """The checked calculus's axioms, kept in named groups.

    :func:`checker_axioms` is the concatenation. The groups exist so that a test
    can remove exactly one and watch a theorem stop being provable: an axiom
    nobody can remove is an axiom nobody has checked is doing anything, and
    slicing a flat list by index is a test that breaks the first time the list is
    reordered.
    """

    solver = require_z3()
    t, u = solver.Consts("ax_t ax_u", sig.Trans)
    a = solver.Const("ax_a", sig.Contract)
    c = solver.Const("ax_c", sig.Coord)
    return {
        "closure_lift": [
            solver.ForAll(
                [t],
                sig.Carries(t)
                == solver.And(sig.Native(t), solver.ForAll([c], sig.Holds(t, c))),
                patterns=[solver.MultiPattern(sig.Carries(t))],
            )
        ],
        "structural": structural_axioms(sig),
        "coordinate_transport": [
            solver.ForAll(
                [t, u, c],
                sig.Holds(sig.Comp(t, u), c)
                == solver.And(
                    sig.Holds(t, c),
                    sig.Holds(u, c),
                    solver.Implies(c == sig.Totality, match(sig, sig.Tgt(t), sig.Src(u))),
                ),
                patterns=[solver.MultiPattern(sig.Holds(sig.Comp(t, u), c))],
            )
        ],
        "identity": [
            solver.ForAll([a], sig.Src(sig.Ident(a)) == a),
            solver.ForAll([a], sig.Tgt(sig.Ident(a)) == a),
            solver.ForAll([a], sig.Native(sig.Ident(a))),
            solver.ForAll([a, c], sig.Holds(sig.Ident(a), c)),
        ],
    }


def checker_axioms(sig: Signature) -> list[Any]:
    """P7's checked rule, generalised: the closure lift, transport, and identity.

    Four groups, none of which is a theorem in disguise.

    1. **The closure lift.** ``Carries(t) <-> Native(t) /\\ forall c. Holds(t,c)``.
       This is ``ClosureCarries(T,o) := DonorPreserves(T) AND all(o)`` from
       ``P7_X2_CLOSURE_CARRYING_THEOREMS_V1.md``, with the five-tuple replaced by
       a quantifier over the coordinate sort.

    2. **Structural axioms**, from :func:`structural_axioms`.

    3. **Coordinate transport.** A composite holds a closure coordinate exactly
       when both legs hold it; the distinguished coordinate additionally
       requires the intermediate contract to match. This is the only place the
       bridge enters the checked calculus, and it enters at one coordinate --- it
       is ``obligations_total`` that an unbridged hand-off breaks, because
       obligations the first leg emits are then not the obligations the second
       leg consumes. Composition soundness is *derived* from this, not assumed.

    4. **Identity.** ``Ident(a)`` runs from ``a`` to ``a``, is natively valid, and
       holds every closure coordinate: it is the transformation that changes
       nothing, so there is nothing for it to lose.
    """

    groups = checker_axiom_groups(sig)
    return [axiom for group in groups.values() for axiom in group]


def extensionality_axiom(sig: Signature) -> list[Any]:
    """Declared, not assumed silently: observationally equal transformations are equal.

    The observable semantics of a transformation in this calculus is exactly its
    source, its target, its donor-native verdict and its closure coordinates.
    Extensionality says the calculus does not distinguish what it cannot
    observe. It is a modelling decision and it is kept in its own function so
    that the theorems needing it can be told apart from the ones that do not ---
    :data:`ASSOCIATIVITY_OBSERVABLE` and :data:`LEFT_IDENTITY` hold without it,
    :data:`ASSOCIATIVITY_STRICT` and :data:`IDENTITY_STRICT` do not, and
    :data:`STRICT_LAWS_NEED_EXTENSIONALITY` exhibits the model that separates
    them.

    Stated in **Skolemized** form: ``Diff(t,u)`` is the witnessing coordinate, so
    the antecedent is quantifier-free. The unskolemized version --- a nested
    ``forall c`` under an implication --- is equisatisfiable and, in practice,
    times the solver out on strict associativity.

    The e-matching trigger is the **pair of source contracts**, and it is not
    cosmetic. Without it the axiom has no head term to fire on, the solver falls
    back to model-based instantiation, and strict associativity takes anywhere
    between 0.0 seconds and longer than any timeout --- measured over repeated
    runs it was ``PROVED`` sometimes and ``UNKNOWN`` others, which is the worst
    possible behaviour for a claim in a report. With this trigger the axiom fires
    on exactly the pairs of transformations the query mentions and both strict
    laws close in hundredths of a second. Same axiom, same theory, same theorems;
    the fix is the trigger and not the time budget.
    """

    solver = require_z3()
    t, u = solver.Consts("ext_t ext_u", sig.Trans)
    return [
        solver.ForAll(
            [t, u],
            solver.Implies(
                solver.And(
                    sig.Src(t) == sig.Src(u),
                    sig.Tgt(t) == sig.Tgt(u),
                    sig.Native(t) == sig.Native(u),
                    sig.Holds(t, sig.Diff(t, u)) == sig.Holds(u, sig.Diff(t, u)),
                ),
                t == u,
            ),
            patterns=[solver.MultiPattern(sig.Src(t), sig.Src(u))],
        )
    ]


def obligation_axioms(sig: Signature) -> list[Any]:
    """What ``obligations_total`` means, defined without reference to any rule.

    ``obligations_total`` is registered in P7's theorem family as "every target
    scientific obligation has a mapped source/discharge or an explicit
    target-new obligation". Transcribed::

        Total(t)  <->  forall o. Demands(Tgt t, o)
                            -> Demands(Src t, o) \\/ Discharged(t,o) \\/ Fresh(t,o)

    ``Demands`` is the obligation contract itself --- what a contract requires be
    discharged --- and it is what makes a contract more than a label. The two
    composite clauses say a composite discharges what either leg discharges and
    declares new what either leg declares new, which is the only reading on
    which a chain is the transformation you get by running its legs.

    Nothing in this function mentions ``Match``, ``Bridge``, ``Carries`` or the
    coordinate transport rule. That independence is the point: whether the
    checked layer's intermediate-contract test is the right test is then a
    question this layer can answer rather than one it was built to confirm.
    """

    solver = require_z3()
    t, u = solver.Consts("ob_t ob_u", sig.Trans)
    o = solver.Const("ob_o", sig.Obl)
    return [
        *structural_axioms(sig),
        solver.ForAll(
            [t],
            sig.Total(t)
            == solver.ForAll(
                [o],
                solver.Implies(
                    sig.Demands(sig.Tgt(t), o),
                    solver.Or(
                        sig.Demands(sig.Src(t), o), sig.Discharged(t, o), sig.Fresh(t, o)
                    ),
                ),
            ),
            patterns=[solver.MultiPattern(sig.Total(t))],
        ),
        solver.ForAll(
            [t, u, o],
            sig.Discharged(sig.Comp(t, u), o)
            == solver.Or(sig.Discharged(t, o), sig.Discharged(u, o)),
            patterns=[solver.MultiPattern(sig.Discharged(sig.Comp(t, u), o))],
        ),
        solver.ForAll(
            [t, u, o],
            sig.Fresh(sig.Comp(t, u), o) == solver.Or(sig.Fresh(t, o), sig.Fresh(u, o)),
            patterns=[solver.MultiPattern(sig.Fresh(sig.Comp(t, u), o))],
        ),
    ]


def bridge_soundness_axiom(sig: Signature) -> list[Any]:
    """What it takes for a registered bridge to be a bridge.

    P7's ``T5`` licenses composition when a registered bridge "witnesses their
    equivalence". This axiom is that phrase: a registered bridge relates
    contracts demanding the same obligations. It is kept separate from
    :func:`obligation_axioms` because it is load-bearing and that is checkable
    --- :func:`axiom_pin_bridge_soundness` removes it and watches
    :data:`TOTALITY_COMPOSES_UNDER_MATCH` acquire a countermodel. A bridge that
    is merely *registered*, with no obligation-level obligation on the
    registrar, is a hole exactly the size of the theorem.
    """

    solver = require_z3()
    a, b = solver.Consts("br_a br_b", sig.Contract)
    o = solver.Const("br_o", sig.Obl)
    return [
        solver.ForAll(
            [a, b],
            solver.Implies(
                sig.Bridge(a, b),
                solver.ForAll([o], sig.Demands(a, o) == sig.Demands(b, o)),
            ),
        )
    ]


def semantic_axioms(sig: Signature) -> list[Any]:
    """The obligation layer with the bridge obligation attached."""

    return [*obligation_axioms(sig), *bridge_soundness_axiom(sig)]


# ---------------------------------------------------------------------------
# The theorems
# ---------------------------------------------------------------------------

IDENTITY_CARRIES = Theorem(
    name="IDENTITY_CARRIES",
    statement="the identity transformation on any contract carries closure",
    why_it_matters=(
        "a calculus needs an object that composes with everything and changes "
        "nothing; if the identity itself failed the closure lift there would be "
        "no unit to state a unit law about"
    ),
)

LEFT_IDENTITY = Theorem(
    name="LEFT_IDENTITY",
    statement=(
        "composing the identity on a transformation's source before it preserves "
        "its endpoints and its closure-carrying verdict exactly"
    ),
    why_it_matters=(
        "the left unit law, with no condition on the registered bridge relation; "
        "the finite model has no identity element at all, so this is not a "
        "generalisation of anything it checked"
    ),
)

RIGHT_IDENTITY = Theorem(
    name="RIGHT_IDENTITY",
    statement=(
        "composing a transformation with the identity on its target preserves its "
        "endpoints and its closure-carrying verdict exactly"
    ),
    why_it_matters="the right unit law; stated separately because composition is not symmetric",
)

IDENTITY_STRICT = Theorem(
    name="IDENTITY_STRICT",
    statement=(
        "under extensionality the unit laws are equations: composing with the "
        "identity on either side returns the same transformation"
    ),
    why_it_matters=(
        "the difference between 'agrees on every observable' and 'is equal' is "
        "the difference between a report and a calculus; this says which one "
        "extensionality buys and STRICT_LAWS_NEED_EXTENSIONALITY says what it costs"
    ),
)

ASSOCIATIVITY_OBSERVABLE = Theorem(
    name="ASSOCIATIVITY_OBSERVABLE",
    statement=(
        "the two bracketings of a three-transformation chain agree on source, "
        "target, donor-native validity and every closure coordinate, for any "
        "registered bridge relation"
    ),
    why_it_matters=(
        "associativity is what makes a chain a chain rather than a tree, and it "
        "is proved here with no reflexivity, symmetry or transitivity assumed of "
        "the bridge relation --- which is the non-obvious part, since bridges are "
        "registered one at a time and compose in no way at all"
    ),
)

ASSOCIATIVITY_CARRIES = Theorem(
    name="ASSOCIATIVITY_CARRIES",
    statement="the two bracketings of a three-transformation chain carry closure together or not at all",
    why_it_matters=(
        "the verdict-level consequence, stated on its own because it is the one "
        "a checker would rely on when it evaluates a chain in some order of its "
        "choosing"
    ),
)

ASSOCIATIVITY_STRICT = Theorem(
    name="ASSOCIATIVITY_STRICT",
    statement="under extensionality the two bracketings are the same transformation",
    why_it_matters="associativity as an equation, which is what the word means in a calculus",
)

INTERMEDIATE_CONTRACT_COMPOSITION = Theorem(
    name="INTERMEDIATE_CONTRACT_COMPOSITION",
    statement=(
        "a composite carries closure if and only if both legs carry it and the "
        "contract the first leg emits matches the contract the second consumes --- "
        "either identically or through a registered bridge"
    ),
    why_it_matters=(
        "this is the general form of P7's `compose`, and it is derived from "
        "coordinate transport rather than assumed. It holds for any number of "
        "closure coordinates over any transformation sort, which is what the "
        "committed 25 pairs -- five donor names crossed with themselves, neither "
        "read -- did not establish"
    ),
)

UNMATCHED_INTERMEDIATE_CONTRACT_BLOCKS = Theorem(
    name="UNMATCHED_INTERMEDIATE_CONTRACT_BLOCKS",
    statement=(
        "if the intermediate contract neither matches exactly nor is bridged, no "
        "composite carries closure, however good both legs are"
    ),
    why_it_matters=(
        "the general form of the 25 matched missing-bridge cases: donor-visible "
        "composability is insufficient, and it is insufficient for every pair of "
        "transformations rather than for five names crossed with themselves"
    ),
)

COMPOSITION_NON_AMPLIFICATION = Theorem(
    name="COMPOSITION_NON_AMPLIFICATION",
    statement="a composite that carries closure has legs that both carry closure",
    why_it_matters=(
        "composition must not manufacture closure out of legs that lack it, or "
        "chaining would be a laundering operation on scientific closure"
    ),
)

SINGLE_COORDINATE_SEPARATION = Theorem(
    name="SINGLE_COORDINATE_SEPARATION",
    statement=(
        "one failing closure coordinate, or a failing donor-native verdict, is "
        "enough to refuse: closure carrying is non-compensatory"
    ),
    why_it_matters=(
        "the general form of the 25 single-coordinate separation witnesses and "
        "the 31 product countermodels; those enumerate five coordinates, this "
        "holds for a coordinate sort of any size"
    ),
)

DONOR_CONSERVATIVITY = Theorem(
    name="DONOR_CONSERVATIVITY",
    statement=(
        "the donor-native verdict of a composite depends only on the legs' native "
        "verdicts --- no closure coordinate, contract or bridge changes it"
    ),
    why_it_matters=(
        "P7's T1: adding the closure carrier must never alter the donor's own "
        "preservation/refinement/round-trip answer, or the claim to absorb mature "
        "donor machinery unchanged is false"
    ),
)

IDENTITY_NEEDS_A_REFLEXIVE_CONTRACT_TEST = Theorem(
    name="IDENTITY_NEEDS_A_REFLEXIVE_CONTRACT_TEST",
    statement=(
        "the unit law is not a free consequence of composition: with the raw "
        "registered bridge relation in place of the reflexive match test there is "
        "a model in which a carrying transformation composed with the identity on "
        "its own source does not carry"
    ),
    why_it_matters=(
        "names the exact side condition identity rests on. P7's T5 says 'exactly "
        "the same contract, or a registered bridge'; this shows the first disjunct "
        "is doing work rather than being a convenience, because without it every "
        "identity would need a bridge registered from a contract to itself"
    ),
)

STRICT_LAWS_NEED_EXTENSIONALITY = Theorem(
    name="STRICT_LAWS_NEED_EXTENSIONALITY",
    statement=(
        "there is a model of the checked calculus in which the two bracketings of "
        "a chain agree on every observable and are not equal, so the strict laws "
        "genuinely rest on extensionality and not on the transport axioms"
    ),
    why_it_matters=(
        "keeps ASSOCIATIVITY_STRICT honest. A law proved under an axiom that was "
        "not needed is a law proved about something else, and here the axiom is "
        "needed --- the model tags each composite with a bit the observables "
        "cannot see, and the bracketings differ in it"
    ),
)

TOTALITY_COMPOSES_UNDER_MATCH = Theorem(
    name="TOTALITY_COMPOSES_UNDER_MATCH",
    statement=(
        "in the obligation semantics, if both legs account for every obligation "
        "their targets demand and the intermediate contract matches, so does the "
        "composite"
    ),
    why_it_matters=(
        "this is what justifies the checked calculus's intermediate-contract test "
        "instead of leaving it as a stipulation; the test is sound with respect to "
        "an obligation semantics defined without reference to it"
    ),
)

CONTAINMENT_IS_THE_EXACT_CONDITION = Theorem(
    name="CONTAINMENT_IS_THE_EXACT_CONDITION",
    statement=(
        "the weaker hypothesis suffices: if every obligation the second leg's "
        "source demands is demanded by the first leg's target, totality composes "
        "--- contract equality and registered bridges are two ways of getting this "
        "and not the only ones"
    ),
    why_it_matters=(
        "the explicit characterisation the unblock asks for where the property "
        "does not hold unconditionally. Containment is the side condition; match "
        "implies it, which is why match works"
    ),
)

MATCH_IS_NOT_NECESSARY = Theorem(
    name="MATCH_IS_NOT_NECESSARY",
    statement=(
        "there is a model in which both legs are total, the composite is total and "
        "demands something, the emitted and consumed contracts demand exactly the "
        "same obligations, and the intermediate contract test still fails because "
        "the two contracts are distinct and no bridge was registered between them"
    ),
    why_it_matters=(
        "the checked rule is sound but incomplete with respect to the semantics, "
        "and the witness says exactly where the gap is: two contracts can be "
        "obligation-equivalent and still be refused, because the test asks whether "
        "someone registered a bridge and not whether the obligations agree. "
        "Fail-closed is the paper's declared stance, so this is a cost rather than "
        "a defect --- but it is a cost, and it is named here rather than left for a "
        "reader to find"
    ),
)

CONTAINMENT_FAILURE_ADMITS_A_COUNTERMODEL = Theorem(
    name="CONTAINMENT_FAILURE_ADMITS_A_COUNTERMODEL",
    statement=(
        "drop containment and totality genuinely stops composing: there is a model "
        "with both legs total and the composite not total"
    ),
    why_it_matters=(
        "the converse half of the characterisation. A sufficient condition offered "
        "without a witness that it is needed is a condition nobody tested"
    ),
)

THEOREMS: tuple[Theorem, ...] = (
    IDENTITY_CARRIES,
    LEFT_IDENTITY,
    RIGHT_IDENTITY,
    IDENTITY_STRICT,
    ASSOCIATIVITY_OBSERVABLE,
    ASSOCIATIVITY_CARRIES,
    ASSOCIATIVITY_STRICT,
    INTERMEDIATE_CONTRACT_COMPOSITION,
    UNMATCHED_INTERMEDIATE_CONTRACT_BLOCKS,
    COMPOSITION_NON_AMPLIFICATION,
    SINGLE_COORDINATE_SEPARATION,
    DONOR_CONSERVATIVITY,
    IDENTITY_NEEDS_A_REFLEXIVE_CONTRACT_TEST,
    STRICT_LAWS_NEED_EXTENSIONALITY,
    TOTALITY_COMPOSES_UNDER_MATCH,
    CONTAINMENT_IS_THE_EXACT_CONDITION,
    MATCH_IS_NOT_NECESSARY,
    CONTAINMENT_FAILURE_ADMITS_A_COUNTERMODEL,
)


# ---------------------------------------------------------------------------
# Discharging them
# ---------------------------------------------------------------------------


def prove_hinge(sig: Signature, axioms: list[Any], *, timeout_ms: int = 30000) -> ProofResult:
    """Discharge :data:`INTERMEDIATE_CONTRACT_COMPOSITION` from ``axioms`` alone.

    Called the hinge because everything this calculus says about the verdict of a
    *composite* follows from it, and because the rest of the development is
    written to depend on it explicitly rather than to re-derive it in each query.
    See :func:`composition_lemma` for why that matters and what the gate is.

    The biconditional is discharged as **two implications, one solver call each**,
    and reported as ``PROVED`` only when both come back ``PROVED``. That is a
    propositional step --- from ``A -> B`` and ``B -> A`` to ``A <-> B`` --- and it
    is taken because as a single query the biconditional negates to a disjunction
    the solver has to case-split, which is measurably worse: over eight runs the
    combined form peaked at 1.19s in a quiet process and at 13.6s in a loaded one,
    while the split form peaked at 0.18s. The claim proved is the same claim.
    """

    solver = require_z3()
    t, u = solver.Consts("hinge_t hinge_u", sig.Trans)
    composite = sig.Carries(sig.Comp(t, u))
    decomposed = solver.And(
        sig.Carries(t), sig.Carries(u), match(sig, sig.Tgt(t), sig.Src(u))
    )
    forwards = discharge(
        INTERMEDIATE_CONTRACT_COMPOSITION,
        axioms,
        solver.Implies(composite, decomposed),
        timeout_ms=timeout_ms,
    )
    if not forwards.discharged:
        return ProofResult(
            INTERMEDIATE_CONTRACT_COMPOSITION,
            forwards.outcome,
            f"the left-to-right implication is not discharged: {forwards.detail}",
        )
    backwards = discharge(
        INTERMEDIATE_CONTRACT_COMPOSITION,
        axioms,
        solver.Implies(decomposed, composite),
        timeout_ms=timeout_ms,
    )
    if not backwards.discharged:
        return ProofResult(
            INTERMEDIATE_CONTRACT_COMPOSITION,
            backwards.outcome,
            f"the right-to-left implication is not discharged: {backwards.detail}",
        )
    return ProofResult(
        INTERMEDIATE_CONTRACT_COMPOSITION,
        ProofOutcome.PROVED,
        "both implications are discharged separately; the biconditional is their "
        "propositional conjunction",
    )


def _corollary_axioms(sig: Signature, *, timeout_ms: int) -> list[Any]:
    """``checker_axioms`` plus the hinge, if the hinge is actually proved.

    Used by the ground-world checks in :func:`differential_check` and
    :func:`instantiation_check`, which ask about a composite's verdict and so are
    corollary-shaped in exactly the way :func:`composition_lemma` explains. The
    lemma is a consequence of the axioms, so adding it changes nothing about what
    is provable and a good deal about whether the solver gets there --- and the
    gate means a run where the hinge did not discharge falls back to the axioms
    alone rather than proceeding on an unproved hypothesis.
    """

    axioms = checker_axioms(sig)
    hinge = prove_hinge(sig, axioms, timeout_ms=timeout_ms)
    return [*axioms, composition_lemma(sig)] if hinge.discharged else axioms


def prove_all(*, timeout_ms: int = 30000) -> tuple[ProofResult, ...]:
    """Discharge every theorem in :data:`THEOREMS`, in order.

    Validity claims go through :func:`orion.programme.mechanized.discharge` over
    the uninterpreted signature. Independence claims go through the finite-model
    helpers, where the proof *is* a model and ``unsat`` would refute the claim;
    those are kept in their own functions so a ``PROVED`` line never means two
    different things in one report.

    **The development has one hinge and three corollaries of it.**
    :data:`INTERMEDIATE_CONTRACT_COMPOSITION` is discharged first, from the
    axioms alone. The three theorems about a *composite's* verdict ---
    associativity of carrying, the unmatched-contract block, and
    non-amplification --- are then discharged under it, because they are
    corollaries of it and because asking the solver to re-derive it inside each
    of them is what it cannot reliably do: ``ASSOCIATIVITY_CARRIES`` from the
    axioms alone came back ``PROVED`` twice and ``UNKNOWN`` twice over four runs
    in a fresh process, and under the hinge it closes in a hundredth of a second
    every time. The instability is in the query, not in the claim.

    The gate is that the hinge must actually be ``PROVED`` before it is used. If
    it is not, the corollaries run against the axioms alone and report whatever
    the solver says --- which is the honest behaviour, because a corollary
    inheriting authority from an undischarged lemma is worth nothing.
    """

    solver = require_z3()
    sig = signature()
    checker = checker_axioms(sig)
    with_ext = [*checker, *extensionality_axiom(sig)]
    semantic = semantic_axioms(sig)

    hinge = prove_hinge(sig, checker, timeout_ms=timeout_ms)
    corollary = [*checker, composition_lemma(sig)] if hinge.discharged else checker

    t, u, v = solver.Consts("t0 u0 v0", sig.Trans)
    a = solver.Const("a0", sig.Contract)
    coordinate = solver.Const("c0", sig.Coord)

    left_unit = sig.Comp(sig.Ident(sig.Src(t)), t)
    right_unit = sig.Comp(t, sig.Ident(sig.Tgt(t)))
    left_bracket = sig.Comp(sig.Comp(t, u), v)
    right_bracket = sig.Comp(t, sig.Comp(u, v))
    composite = sig.Comp(t, u)

    results: list[ProofResult] = [
        discharge(IDENTITY_CARRIES, checker, sig.Carries(sig.Ident(a)), timeout_ms=timeout_ms),
        discharge(
            LEFT_IDENTITY,
            checker,
            solver.And(
                sig.Carries(left_unit) == sig.Carries(t),
                sig.Src(left_unit) == sig.Src(t),
                sig.Tgt(left_unit) == sig.Tgt(t),
            ),
            timeout_ms=timeout_ms,
        ),
        discharge(
            RIGHT_IDENTITY,
            checker,
            solver.And(
                sig.Carries(right_unit) == sig.Carries(t),
                sig.Src(right_unit) == sig.Src(t),
                sig.Tgt(right_unit) == sig.Tgt(t),
            ),
            timeout_ms=timeout_ms,
        ),
        discharge(
            IDENTITY_STRICT,
            with_ext,
            solver.And(left_unit == t, right_unit == t),
            timeout_ms=timeout_ms,
        ),
        discharge(
            ASSOCIATIVITY_OBSERVABLE,
            checker,
            solver.And(
                sig.Src(left_bracket) == sig.Src(right_bracket),
                sig.Tgt(left_bracket) == sig.Tgt(right_bracket),
                sig.Native(left_bracket) == sig.Native(right_bracket),
                sig.Holds(left_bracket, coordinate) == sig.Holds(right_bracket, coordinate),
            ),
            timeout_ms=timeout_ms,
        ),
        discharge(
            ASSOCIATIVITY_CARRIES,
            corollary,
            sig.Carries(left_bracket) == sig.Carries(right_bracket),
            timeout_ms=timeout_ms,
        ),
        discharge(
            ASSOCIATIVITY_STRICT,
            with_ext,
            left_bracket == right_bracket,
            timeout_ms=timeout_ms,
        ),
        hinge,
        discharge(
            UNMATCHED_INTERMEDIATE_CONTRACT_BLOCKS,
            corollary,
            solver.Implies(
                solver.Not(match(sig, sig.Tgt(t), sig.Src(u))),
                solver.Not(sig.Carries(composite)),
            ),
            timeout_ms=timeout_ms,
        ),
        discharge(
            COMPOSITION_NON_AMPLIFICATION,
            corollary,
            solver.Implies(sig.Carries(composite), solver.And(sig.Carries(t), sig.Carries(u))),
            timeout_ms=timeout_ms,
        ),
        discharge(
            SINGLE_COORDINATE_SEPARATION,
            checker,
            solver.Implies(
                solver.Or(solver.Not(sig.Holds(t, coordinate)), solver.Not(sig.Native(t))),
                solver.Not(sig.Carries(t)),
            ),
            timeout_ms=timeout_ms,
        ),
        _prove_donor_conservativity(sig, checker, timeout_ms=timeout_ms),
        _prove_identity_needs_reflexive_match(timeout_ms=timeout_ms),
        _prove_strict_laws_need_extensionality(timeout_ms=timeout_ms),
    ]

    # The obligation layer.
    obligation = solver.Const("o0", sig.Obl)
    containment = solver.ForAll(
        [obligation],
        solver.Implies(
            sig.Demands(sig.Src(u), obligation), sig.Demands(sig.Tgt(t), obligation)
        ),
    )
    results.append(
        discharge(
            TOTALITY_COMPOSES_UNDER_MATCH,
            semantic,
            solver.Implies(
                solver.And(sig.Total(t), sig.Total(u), match(sig, sig.Tgt(t), sig.Src(u))),
                sig.Total(composite),
            ),
            timeout_ms=timeout_ms,
        )
    )
    results.append(
        discharge(
            CONTAINMENT_IS_THE_EXACT_CONDITION,
            semantic,
            solver.Implies(
                solver.And(sig.Total(t), sig.Total(u), containment), sig.Total(composite)
            ),
            timeout_ms=timeout_ms,
        )
    )
    results.append(_prove_match_is_not_necessary(timeout_ms=timeout_ms))
    results.append(_prove_containment_failure(timeout_ms=timeout_ms))
    return tuple(results)


def _prove_donor_conservativity(
    sig: Signature, axioms: list[Any], *, timeout_ms: int
) -> ProofResult:
    """Two composites with the same native verdicts have the same native verdict.

    Stated as a frame condition rather than as the equation
    ``Native(Comp(t,u)) = Native(t) /\\ Native(u)``, which is an axiom and would
    prove itself. The claim is that nothing outside the two native verdicts can
    influence the composite's --- so a pair of transformations agreeing on native
    validity but disagreeing on every closure coordinate, contract and bridge
    still composes to the same native answer.
    """

    solver = require_z3()
    t1, u1, t2, u2 = solver.Consts("dc_t1 dc_u1 dc_t2 dc_u2", sig.Trans)
    return discharge(
        DONOR_CONSERVATIVITY,
        axioms,
        solver.Implies(
            solver.And(sig.Native(t1) == sig.Native(t2), sig.Native(u1) == sig.Native(u2)),
            sig.Native(sig.Comp(t1, u1)) == sig.Native(sig.Comp(t2, u2)),
        ),
        timeout_ms=timeout_ms,
    )


# ---------------------------------------------------------------------------
# Independence results, in explicitly constructed closed finite structures
# ---------------------------------------------------------------------------


def _finite_checker_world(
    *, reflexive_match: bool = True, tagged: bool = False, coordinates: int = 2, contracts: int = 2
) -> dict[str, Any]:
    """A closed finite model of the checked calculus, with its tables asserted.

    The carrier is the space of *observable profiles* --- a donor-native bit, one
    bit per closure coordinate, a source and a target --- optionally crossed with
    a tag the observables cannot see. That space is closed under the composition
    the transport axioms describe and contains an identity for every contract,
    which is why a finite countermodel exists at all; a carrier chosen smaller
    comes back ``unsat`` for the wrong reason.

    Every function is pinned by ground equations, so the solver checks that the
    structure really satisfies the axioms instead of taking the construction on
    trust. The only thing left free is ``Bridge``, which is what the independence
    queries solve for.

    ``tagged`` builds the non-extensional variant: ``Comp(x,y)`` carries a tag
    flipped from ``x``'s, so ``Comp(Comp(t,u),v)`` and ``Comp(t,Comp(u,v))``
    differ in a coordinate no observable exposes. Every axiom constrains
    observables only, so the tag is free to do this.
    """

    solver = require_z3()
    name = f"FC{next(_WORLD_COUNTER)}"
    profiles = list(itertools.product((0, 1), repeat=1 + coordinates))
    tags = (0, 1) if tagged else (0,)
    elements = [
        (profile, src, tgt, tag)
        for profile in profiles
        for src in range(contracts)
        for tgt in range(contracts)
        for tag in tags
    ]
    index = {element: position for position, element in enumerate(elements)}

    Trans, trans_consts = solver.EnumSort(
        f"{name}Trans", [f"e{i}" for i in range(len(elements))]
    )
    Contract, contract_consts = solver.EnumSort(
        f"{name}Contract", [f"k{i}" for i in range(contracts)]
    )
    Coord, coord_consts = solver.EnumSort(
        f"{name}Coord", [f"d{i}" for i in range(coordinates)]
    )
    boolean = solver.BoolSort()
    Native = solver.Function(f"{name}Native", Trans, boolean)
    Holds = solver.Function(f"{name}Holds", Trans, Coord, boolean)
    Src = solver.Function(f"{name}Src", Trans, Contract)
    Tgt = solver.Function(f"{name}Tgt", Trans, Contract)
    Bridge = solver.Function(f"{name}Bridge", Contract, Contract, boolean)
    Comp = solver.Function(f"{name}Comp", Trans, Trans, Trans)
    Ident = solver.Function(f"{name}Ident", Contract, Trans)
    totality = coord_consts[0]

    def match_in(left: Any, right: Any) -> Any:
        if reflexive_match:
            return solver.Or(left == right, Bridge(left, right))
        return Bridge(left, right)

    def carries_in(term: Any) -> Any:
        return solver.And(Native(term), *[Holds(term, d) for d in coord_consts])

    axioms: list[Any] = []
    for element, position in index.items():
        profile, src, tgt, _tag = element
        axioms.append(Native(trans_consts[position]) == solver.BoolVal(bool(profile[0])))
        for offset, coordinate in enumerate(coord_consts):
            axioms.append(
                Holds(trans_consts[position], coordinate)
                == solver.BoolVal(bool(profile[1 + offset]))
            )
        axioms.append(Src(trans_consts[position]) == contract_consts[src])
        axioms.append(Tgt(trans_consts[position]) == contract_consts[tgt])

    for left_element, left_position in index.items():
        left_profile, left_src, left_tgt, left_tag = left_element
        for right_element, right_position in index.items():
            right_profile, right_src, right_tgt, _ = right_element
            native = left_profile[0] & right_profile[0]
            tag = (1 - left_tag) if tagged else 0
            both = tuple(
                left_profile[1 + i] & right_profile[1 + i] for i in range(coordinates)
            )
            matched = ((native, *both), left_src, right_tgt, tag)
            unmatched_bits = tuple(bit if i else 0 for i, bit in enumerate(both))
            unmatched = ((native, *unmatched_bits), left_src, right_tgt, tag)
            axioms.append(
                Comp(trans_consts[left_position], trans_consts[right_position])
                == solver.If(
                    match_in(contract_consts[left_tgt], contract_consts[right_src]),
                    trans_consts[index[matched]],
                    trans_consts[index[unmatched]],
                )
            )

    for contract in range(contracts):
        unit = ((1, *((1,) * coordinates)), contract, contract, 0)
        axioms.append(Ident(contract_consts[contract]) == trans_consts[index[unit]])

    # The tables above are a hand construction. These are the axioms of
    # `checker_axioms` restated over the finite carrier, so the solver verifies
    # that the construction really is a model instead of taking it on trust --- a
    # wrong table makes the whole query unsat, and an independence result
    # discharged against a structure that was never a model would be worth
    # nothing at all.
    for left_term in trans_consts:
        for right_term in trans_consts:
            composite = Comp(left_term, right_term)
            axioms.append(Src(composite) == Src(left_term))
            axioms.append(Tgt(composite) == Tgt(right_term))
            axioms.append(
                Native(composite) == solver.And(Native(left_term), Native(right_term))
            )
            for coordinate in coord_consts:
                axioms.append(
                    Holds(composite, coordinate)
                    == solver.And(
                        Holds(left_term, coordinate),
                        Holds(right_term, coordinate),
                        solver.Implies(
                            coordinate == totality,
                            match_in(Tgt(left_term), Src(right_term)),
                        ),
                    )
                )
    for contract_term in contract_consts:
        unit_term = Ident(contract_term)
        axioms.append(Src(unit_term) == contract_term)
        axioms.append(Tgt(unit_term) == contract_term)
        axioms.append(Native(unit_term))
        for coordinate in coord_consts:
            axioms.append(Holds(unit_term, coordinate))

    return {
        "Trans": Trans,
        "Contract": Contract,
        "Coord": Coord,
        "Native": Native,
        "Holds": Holds,
        "Src": Src,
        "Tgt": Tgt,
        "Bridge": Bridge,
        "Comp": Comp,
        "Ident": Ident,
        "Totality": totality,
        "match": match_in,
        "carries": carries_in,
        "axioms": axioms,
    }


def _finite_semantic_world(
    *, bridge_sound: bool = True, obligations: int = 1, contracts: int = 2
) -> dict[str, Any]:
    """A closed finite model of the obligation semantics, with its tables asserted.

    The carrier is the space of (discharged set, declared-new set, source,
    target), which is closed under the composite clauses in
    :func:`obligation_axioms`. ``Demands`` and ``Bridge`` are left free; the
    bridge-soundness clause is asserted only when ``bridge_sound``, which is what
    :func:`axiom_pin_bridge_soundness` varies.
    """

    solver = require_z3()
    name = f"FS{next(_WORLD_COUNTER)}"
    elements = [
        (discharged, fresh, src, tgt)
        for discharged in itertools.product((0, 1), repeat=obligations)
        for fresh in itertools.product((0, 1), repeat=obligations)
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
    Obl, obl_consts = solver.EnumSort(f"{name}Obl", [f"o{i}" for i in range(obligations)])
    boolean = solver.BoolSort()
    Src = solver.Function(f"{name}Src", Trans, Contract)
    Tgt = solver.Function(f"{name}Tgt", Trans, Contract)
    Comp = solver.Function(f"{name}Comp", Trans, Trans, Trans)
    Demands = solver.Function(f"{name}Demands", Contract, Obl, boolean)
    Discharged = solver.Function(f"{name}Discharged", Trans, Obl, boolean)
    Fresh = solver.Function(f"{name}Fresh", Trans, Obl, boolean)
    Bridge = solver.Function(f"{name}Bridge", Contract, Contract, boolean)

    def match_in(left: Any, right: Any) -> Any:
        return solver.Or(left == right, Bridge(left, right))

    def total_in(term: Any) -> Any:
        return solver.And(
            *[
                solver.Implies(
                    Demands(Tgt(term), o),
                    solver.Or(Demands(Src(term), o), Discharged(term, o), Fresh(term, o)),
                )
                for o in obl_consts
            ]
        )

    axioms: list[Any] = []
    for element, position in index.items():
        discharged, fresh, src, tgt = element
        for offset, o in enumerate(obl_consts):
            axioms.append(
                Discharged(trans_consts[position], o) == solver.BoolVal(bool(discharged[offset]))
            )
            axioms.append(Fresh(trans_consts[position], o) == solver.BoolVal(bool(fresh[offset])))
        axioms.append(Src(trans_consts[position]) == contract_consts[src])
        axioms.append(Tgt(trans_consts[position]) == contract_consts[tgt])

    for left_element, left_position in index.items():
        left_discharged, left_fresh, left_src, _ = left_element
        for right_element, right_position in index.items():
            right_discharged, right_fresh, _, right_tgt = right_element
            composite = (
                tuple(a | b for a, b in zip(left_discharged, right_discharged)),
                tuple(a | b for a, b in zip(left_fresh, right_fresh)),
                left_src,
                right_tgt,
            )
            axioms.append(
                Comp(trans_consts[left_position], trans_consts[right_position])
                == trans_consts[index[composite]]
            )

    if bridge_sound:
        for left in range(contracts):
            for right in range(contracts):
                axioms.append(
                    solver.Implies(
                        Bridge(contract_consts[left], contract_consts[right]),
                        solver.And(
                            *[
                                Demands(contract_consts[left], o)
                                == Demands(contract_consts[right], o)
                                for o in obl_consts
                            ]
                        ),
                    )
                )

    # As in `_finite_checker_world`: the axioms of `obligation_axioms` restated
    # over the finite carrier, so the solver checks the construction rather than
    # trusting it. ``Native`` is carried here only so that the structural axiom
    # shared by both layers is checked too; the obligation layer never reads it.
    Native = solver.Function(f"{name}Native", Trans, boolean)
    for term in trans_consts:
        axioms.append(Native(term))
    for left_term in trans_consts:
        for right_term in trans_consts:
            composite = Comp(left_term, right_term)
            axioms.append(Src(composite) == Src(left_term))
            axioms.append(Tgt(composite) == Tgt(right_term))
            axioms.append(
                Native(composite) == solver.And(Native(left_term), Native(right_term))
            )
            for o in obl_consts:
                axioms.append(
                    Discharged(composite, o)
                    == solver.Or(Discharged(left_term, o), Discharged(right_term, o))
                )
                axioms.append(
                    Fresh(composite, o)
                    == solver.Or(Fresh(left_term, o), Fresh(right_term, o))
                )

    return {
        "Trans": Trans,
        "Contract": Contract,
        "Obl": Obl,
        "obl_consts": obl_consts,
        "Src": Src,
        "Tgt": Tgt,
        "Comp": Comp,
        "Demands": Demands,
        "Discharged": Discharged,
        "Fresh": Fresh,
        "Bridge": Bridge,
        "match": match_in,
        "total": total_in,
        "axioms": axioms,
    }


def _exhibit(
    theorem: Theorem, axioms: list[Any], witness: list[Any], *, timeout_ms: int, refuted: str
) -> ProofResult:
    """Discharge a claim by *satisfiability*: the model is the proof.

    Every other claim here is discharged by refuting a negation. These are the
    opposite polarity --- they assert that something is possible --- so ``sat`` is
    the proof and ``unsat`` refutes the claim. Kept in one place so the report's
    ``PROVED`` cannot silently mean two things.
    """

    solver_module = require_z3()
    checker = solver_module.Solver()
    checker.set("timeout", timeout_ms)
    for axiom in axioms:
        checker.add(axiom)
    for assertion in witness:
        checker.add(assertion)
    verdict = checker.check()
    if verdict == solver_module.sat:
        return ProofResult(
            theorem,
            ProofOutcome.PROVED,
            "a model satisfying the axioms and the stated situation exists",
        )
    if verdict == solver_module.unsat:
        return ProofResult(theorem, ProofOutcome.COUNTEREXAMPLE, refuted)
    return ProofResult(
        theorem,
        ProofOutcome.UNKNOWN,
        f"solver returned unknown ({checker.reason_unknown()}); NOT discharged",
    )


def _prove_identity_needs_reflexive_match(*, timeout_ms: int) -> ProofResult:
    """Replace the reflexive match test with the raw bridge and watch identity fail."""

    solver = require_z3()
    world = _finite_checker_world(reflexive_match=False)
    t = solver.Const("idrefl_t", world["Trans"])
    unit = world["Comp"](world["Ident"](world["Src"](t)), t)
    return _exhibit(
        IDENTITY_NEEDS_A_REFLEXIVE_CONTRACT_TEST,
        world["axioms"],
        [world["carries"](t), solver.Not(world["carries"](unit))],
        timeout_ms=timeout_ms,
        refuted=(
            "no such model exists, so the unit law would hold without the reflexive "
            "disjunct in the match test and that disjunct is doing no work"
        ),
    )


def _prove_strict_laws_need_extensionality(*, timeout_ms: int) -> ProofResult:
    """Exhibit a model where the bracketings agree observationally and differ."""

    solver = require_z3()
    world = _finite_checker_world(tagged=True)
    t, u, v = solver.Consts("ext_t ext_u ext_v", world["Trans"])
    left = world["Comp"](world["Comp"](t, u), v)
    right = world["Comp"](t, world["Comp"](u, v))
    return _exhibit(
        STRICT_LAWS_NEED_EXTENSIONALITY,
        world["axioms"],
        [
            left != right,
            world["Src"](left) == world["Src"](right),
            world["Tgt"](left) == world["Tgt"](right),
            world["Native"](left) == world["Native"](right),
        ],
        timeout_ms=timeout_ms,
        refuted=(
            "no such model exists, so strict associativity follows from the transport "
            "axioms alone and extensionality was not carrying it"
        ),
    )


def _prove_match_is_not_necessary(*, timeout_ms: int) -> ProofResult:
    """Exhibit a refused hand-off between two obligation-equivalent contracts.

    Two conjuncts beyond the bare claim, and both matter.

    ``demands_something`` is non-degeneracy: without it the witness could be a
    world in which nothing is required, everything is trivially total, and the
    gap the theorem names is an artefact of an empty obligation set.

    ``obligation_equivalent`` is what sharpens the finding. It is not enough to
    say the test is not necessary; the interesting question is *how* it fails,
    and the answer is that the emitted and consumed contracts can demand exactly
    the same obligations and still be refused --- because the test asks whether a
    bridge was registered, not whether the obligations agree. A registrar who has
    not got round to it is indistinguishable, to this rule, from a real
    obligation mismatch.
    """

    solver = require_z3()
    world = _finite_semantic_world()
    t, u = solver.Consts("mn_t mn_u", world["Trans"])
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
        MATCH_IS_NOT_NECESSARY,
        world["axioms"],
        [
            world["total"](t),
            world["total"](u),
            solver.Not(world["match"](world["Tgt"](t), world["Src"](u))),
            world["total"](composite),
            demands_something,
            obligation_equivalent,
        ],
        timeout_ms=timeout_ms,
        refuted=(
            "no such model exists, so the intermediate-contract test is necessary as "
            "well as sufficient and the checked rule is complete after all"
        ),
    )


def _prove_containment_failure(*, timeout_ms: int) -> ProofResult:
    """Exhibit two total legs whose composite is not total, containment having failed."""

    solver = require_z3()
    world = _finite_semantic_world()
    t, u = solver.Consts("cf_t cf_u", world["Trans"])
    containment = solver.And(
        *[
            solver.Implies(
                world["Demands"](world["Src"](u), o), world["Demands"](world["Tgt"](t), o)
            )
            for o in world["obl_consts"]
        ]
    )
    return _exhibit(
        CONTAINMENT_FAILURE_ADMITS_A_COUNTERMODEL,
        world["axioms"],
        [
            world["total"](t),
            world["total"](u),
            solver.Not(containment),
            solver.Not(world["total"](world["Comp"](t, u))),
        ],
        timeout_ms=timeout_ms,
        refuted=(
            "no such model exists, so totality would compose with no condition at all "
            "and the whole intermediate-contract apparatus is unnecessary"
        ),
    )


def axiom_pin_bridge_soundness(*, timeout_ms: int = 20000) -> dict[str, ProofResult]:
    """Remove the bridge-soundness axiom and watch the theorem stop holding.

    :data:`TOTALITY_COMPOSES_UNDER_MATCH` is the theorem that licenses the
    checked calculus's intermediate-contract test. It rests entirely on
    registered bridges being obligation-equivalences. This returns both runs ---
    with the axiom, where matching legs must compose, and without it, where a
    countermodel exists --- so "the axiom is load-bearing" is a measurement
    rather than a remark.

    Run in the finite structure rather than over the uninterpreted signature,
    because the ``without`` half is an independence claim and needs a model.
    """

    solver = require_z3()
    results: dict[str, ProofResult] = {}
    for label, sound in (("with_axiom", True), ("without_axiom", False)):
        world = _finite_semantic_world(bridge_sound=sound)
        t, u = solver.Consts(f"pin_{label}_t pin_{label}_u", world["Trans"])
        witness = [
            world["total"](t),
            world["total"](u),
            world["match"](world["Tgt"](t), world["Src"](u)),
            solver.Not(world["total"](world["Comp"](t, u))),
        ]
        theorem = Theorem(
            name=f"BRIDGE_SOUNDNESS_PIN__{label.upper()}",
            statement=(
                "a counterexample to totality-composes-under-match exists in the finite "
                f"obligation model, with bridge soundness {'asserted' if sound else 'removed'}"
            ),
            why_it_matters=(
                "with the axiom this must be unsatisfiable and without it satisfiable, "
                "or the axiom is decoration"
            ),
        )
        results[label] = _exhibit(
            theorem,
            world["axioms"],
            witness,
            timeout_ms=timeout_ms,
            refuted="no counterexample exists in this structure",
        )
    return results


# ---------------------------------------------------------------------------
# The chain theorem
# ---------------------------------------------------------------------------


def composition_lemma(sig: Signature) -> Any:
    """:data:`INTERMEDIATE_CONTRACT_COMPOSITION` as a universally quantified sentence.

    This is *not* an axiom. It is discharged from :func:`checker_axioms` alone by
    :func:`prove_hinge`, and both :func:`prove_all` and :func:`prove_chain_ladder`
    re-discharge it before using it, refusing to use it if that run does not come
    back ``PROVED``.

    It exists because the queries that need it cannot reliably re-derive it.
    Expanding a chain of length five directly from the coordinate transport axiom
    takes the solver past its timeout; ``ASSOCIATIVITY_CARRIES`` from the axioms
    alone came back ``PROVED`` twice and ``UNKNOWN`` twice over four runs in a
    fresh process. Under this lemma all of them close in a hundredth of a second.

    Using a proved lemma to prove the next thing is what a development is;
    asserting it would not be, which is why the re-discharge is a gate rather than
    a comment. Note also that this is not a case of a longer timeout being needed:
    a query that answers in 0.01s under the lemma and times out without it is a
    query the solver is doing differently, not one it is doing slowly.
    """

    solver = require_z3()
    t, u = solver.Consts("lemma_t lemma_u", sig.Trans)
    return solver.ForAll(
        [t, u],
        sig.Carries(sig.Comp(t, u))
        == solver.And(sig.Carries(t), sig.Carries(u), match(sig, sig.Tgt(t), sig.Src(u))),
        patterns=[solver.MultiPattern(sig.Carries(sig.Comp(t, u)))],
    )


def prove_chain_ladder(
    *, bound: int = CHAIN_LADDER_BOUND, timeout_ms: int = 30000
) -> tuple[ProofResult, ...]:
    """Expand the chain theorem explicitly at every length up to ``bound``.

    :data:`INTERMEDIATE_CONTRACT_COMPOSITION` is the induction step and the
    endpoint axioms supply what the step needs to iterate: the composite's target
    is its last leg's target, so the next link's intermediate-contract test is
    again a test between adjacent legs. Induction on chain length is the single
    meta-level step in this development.

    Discharging the fully expanded statement at each concrete length does not
    replace the schema --- no finite ladder does --- but a mistake in the
    expansion shows up here rather than in a reader's trust, and the blocker asks
    for a calculus over *arbitrary* chains rather than over pairs.

    The first result is the step lemma itself, re-discharged from the axioms
    alone. If it comes back anything but ``PROVED`` the ladder runs without it,
    which is the honest behaviour: the lengths would then report ``UNKNOWN``
    rather than inheriting authority from an unproved hypothesis.
    """

    solver = require_z3()
    sig = signature()
    axioms = checker_axioms(sig)
    results: list[ProofResult] = []

    hinge = prove_hinge(sig, axioms, timeout_ms=timeout_ms)
    results.append(
        ProofResult(
            Theorem(
                name="CHAIN_STEP_LEMMA",
                statement=(
                    "the one-step lemma the ladder runs under: a composite carries closure "
                    "exactly when both legs do and the intermediate contract matches"
                ),
                why_it_matters=(
                    "the ladder uses this as a hypothesis, so it is re-discharged from the "
                    "axioms alone here rather than assumed alongside them"
                ),
            ),
            hinge.outcome,
            hinge.detail,
        )
    )
    if hinge.discharged:
        axioms = [*axioms, composition_lemma(sig)]

    for length in range(2, bound + 1):
        legs = [solver.Const(f"chain_{length}_{i}", sig.Trans) for i in range(length)]
        folded = legs[0]
        for leg in legs[1:]:
            folded = sig.Comp(folded, leg)
        links = [
            match(sig, sig.Tgt(legs[i]), sig.Src(legs[i + 1])) for i in range(length - 1)
        ]
        claim = sig.Carries(folded) == solver.And(
            *[sig.Carries(leg) for leg in legs], *links
        )
        results.append(
            discharge(
                Theorem(
                    name=f"CHAIN_CARRIES_{length}",
                    statement=(
                        f"a chain of {length} transformations carries closure exactly when "
                        "every leg carries closure and every adjacent intermediate contract "
                        "matches"
                    ),
                    why_it_matters=(
                        "the expanded form of the induction the intermediate-contract "
                        "theorem supports; a calculus over arbitrary transformation chains "
                        "is what P7-U-T1 asks for and a pair is not a chain"
                    ),
                ),
                axioms,
                claim,
                timeout_ms=timeout_ms,
            )
        )
    return tuple(results)


# ---------------------------------------------------------------------------
# Is the sentence proved about the sentence the code computes?
# ---------------------------------------------------------------------------


def load_executable_model(repo_root: Any) -> Any:
    """Load P7's committed closure-carrying checker without importing it as a package."""

    from pathlib import Path

    return _load_model(Path(repo_root) / EXECUTABLE_MODEL, "p7_check_closure_carrying")


def _ground_world(
    sig: Signature,
    *,
    native_left: bool,
    closure_left: tuple[bool, ...],
    native_right: bool,
    closure_right: tuple[bool, ...],
    bridge_match: bool,
    exact: bool,
    tag: str,
) -> tuple[list[Any], Any, Any]:
    """Close the world to P7's five coordinates and one intermediate hand-off.

    The coordinate sort is pinned to exactly the committed checker's five, with
    ``Totality`` identified with ``obligations_total`` --- which is where it
    belongs, since that is the coordinate P7's own theorem family says an
    unbridged hand-off breaks. Without closing the sort the solver may invent a
    sixth coordinate and the two sides would be answering different questions.

    ``exact`` selects which disjunct of the match test realises a bridged
    hand-off: contract identity, or two distinct contracts joined by a registered
    bridge. Both are exercised, because a differential that only ever used
    identity would never test the bridge at all.
    """

    solver = require_z3()
    coords = [solver.Const(f"{tag}_coord_{name}", sig.Coord) for name in CLOSURE_COORDINATES]
    free_coord = solver.Const(f"{tag}_cv", sig.Coord)
    world: list[Any] = [
        solver.Distinct(*coords),
        solver.ForAll([free_coord], solver.Or(*[free_coord == c for c in coords])),
        sig.Totality == coords[0],
    ]
    left = solver.Const(f"{tag}_left", sig.Trans)
    right = solver.Const(f"{tag}_right", sig.Trans)
    world += [
        sig.Native(left) == solver.BoolVal(native_left),
        sig.Native(right) == solver.BoolVal(native_right),
    ]
    for position, coordinate in enumerate(coords):
        world.append(sig.Holds(left, coordinate) == solver.BoolVal(closure_left[position]))
        world.append(sig.Holds(right, coordinate) == solver.BoolVal(closure_right[position]))

    emitted = solver.Const(f"{tag}_emitted", sig.Contract)
    consumed = solver.Const(f"{tag}_consumed", sig.Contract)
    world += [sig.Tgt(left) == emitted, sig.Src(right) == consumed]
    if bridge_match and exact:
        world.append(emitted == consumed)
    elif bridge_match:
        world += [emitted != consumed, sig.Bridge(emitted, consumed)]
    else:
        first, second = solver.Consts(f"{tag}_ba {tag}_bb", sig.Contract)
        world += [
            emitted != consumed,
            solver.ForAll([first, second], solver.Not(sig.Bridge(first, second))),
        ]
    return world, left, right


def differential_check(
    repo_root: Any, *, trials: int = 120, seed: int = 20260821, timeout_ms: int = 10000
) -> DifferentialReport:
    """Run P7's committed model and the SMT formula on the same finite worlds.

    Three parts, and the second exists because of what the prior audit found.

    * **The closure lift, exhaustively.** All 64 combinations of the donor-native
      verdict and the five closure coordinates, compared against
      ``check_p7_x2_closure_carrying.carries``. The committed enumeration reports
      320 rows, which is these 64 crossed with five donor names that nothing
      reads; the 64 are the whole content.
    * **``compose`` at all eight argument triples.** The committed loop evaluates
      it at two of the eight, so a differential that reproduced only the shipped
      corpus would inherit the same blind spot.
    * **Randomised composites.** Half drawn coherent and perturbed in one field,
      half drawn freely, with the bridged half split between contract identity
      and a registered bridge.

    Any disagreement is reported; none is tolerated.
    ``positive_trials`` counts the trials where the committed model returned
    ``True``, so a reader can see that agreement was not agreement about
    ``False``.

    The axiom set is ``checker_axioms`` plus the hinge, gated as described in
    :func:`_corollary_axioms`. The hinge is a derived consequence of those axioms,
    so nothing extra is assumed; what changes is that each trial is compared
    against the sentence the calculus proves rather than against a per-query
    re-derivation of it, which is both the more direct comparison and the one the
    solver can do in milliseconds.
    """

    import random

    solver = require_z3()
    model = load_executable_model(repo_root)
    sig = signature()
    axioms = _corollary_axioms(sig, timeout_ms=30000)
    rng = random.Random(seed)

    agreements = 0
    positives = 0
    total = 0
    disagreements: list[str] = []

    def run(tag: str, world: list[Any], claim: Any, expected: bool, described: str) -> None:
        nonlocal agreements, positives, total
        total += 1
        if expected:
            positives += 1
        outcome = discharge(
            Theorem(
                name=f"DIFFERENTIAL_{tag}",
                statement="the formula agrees with the committed model on this world",
                why_it_matters="a proof about the wrong sentence proves nothing",
            ),
            [*axioms, *world],
            claim,
            timeout_ms=timeout_ms,
        )
        if outcome.discharged:
            agreements += 1
        else:
            disagreements.append(
                f"{described}: python said {expected}, solver said {outcome.outcome.value}"
            )

    full = (True,) * len(CLOSURE_COORDINATES)

    # 1. The closure lift, exhaustively.
    for native in (False, True):
        for closure in itertools.product((False, True), repeat=len(CLOSURE_COORDINATES)):
            tag = f"lift_{int(native)}_{''.join(str(int(b)) for b in closure)}"
            world, left, _right = _ground_world(
                sig,
                native_left=native,
                closure_left=closure,
                native_right=True,
                closure_right=full,
                bridge_match=True,
                exact=True,
                tag=tag,
            )
            expected = model.carries(native, closure)
            run(tag, world, sig.Carries(left) == solver.BoolVal(expected), expected, tag)

    # 2. Every argument triple of `compose`, including the six the shipped loop skips.
    def realise(value: bool, alternate: bool) -> tuple[bool, tuple[bool, ...]]:
        if value:
            return True, full
        if alternate:
            return False, full
        spoiled = list(full)
        spoiled[0] = False
        return True, tuple(spoiled)

    for c_left in (False, True):
        for c_right in (False, True):
            for bridged in (False, True):
                native_left, closure_left = realise(c_left, alternate=bridged)
                native_right, closure_right = realise(c_right, alternate=not bridged)
                tag = f"triple_{int(c_left)}{int(c_right)}{int(bridged)}"
                world, left, right = _ground_world(
                    sig,
                    native_left=native_left,
                    closure_left=closure_left,
                    native_right=native_right,
                    closure_right=closure_right,
                    bridge_match=bridged,
                    exact=bool(c_left),
                    tag=tag,
                )
                expected = model.compose(
                    model.carries(native_left, closure_left),
                    model.carries(native_right, closure_right),
                    bridged,
                )
                run(
                    tag,
                    world,
                    sig.Carries(sig.Comp(left, right)) == solver.BoolVal(expected),
                    expected,
                    tag,
                )

    # 3. Randomised composites.
    for trial in range(trials):
        if rng.random() < 0.6:
            native_left, native_right = True, True
            closure_left, closure_right = list(full), list(full)
            bridged = rng.random() < 0.7
            spoil = rng.choice([None, None, "native_left", "closure_left", "native_right", "closure_right"])
            if spoil == "native_left":
                native_left = False
            elif spoil == "closure_left":
                closure_left[rng.randrange(len(full))] = False
            elif spoil == "native_right":
                native_right = False
            elif spoil == "closure_right":
                closure_right[rng.randrange(len(full))] = False
        else:
            native_left = rng.random() < 0.7
            native_right = rng.random() < 0.7
            closure_left = [rng.random() < 0.85 for _ in full]
            closure_right = [rng.random() < 0.85 for _ in full]
            bridged = rng.random() < 0.5
        exact = rng.random() < 0.5
        tag = f"rand_{trial}"
        world, left, right = _ground_world(
            sig,
            native_left=native_left,
            closure_left=tuple(closure_left),
            native_right=native_right,
            closure_right=tuple(closure_right),
            bridge_match=bridged,
            exact=exact,
            tag=tag,
        )
        expected = model.compose(
            model.carries(native_left, tuple(closure_left)),
            model.carries(native_right, tuple(closure_right)),
            bridged,
        )
        run(
            tag,
            world,
            sig.Carries(sig.Comp(left, right)) == solver.BoolVal(expected),
            expected,
            tag,
        )

    return DifferentialReport(
        trials=total,
        agreements=agreements,
        disagreements=tuple(disagreements[:20]),
        positive_trials=positives,
    )


# ---------------------------------------------------------------------------
# Are P7's committed results instances of this calculus?  (P7-U-T2)
# ---------------------------------------------------------------------------


def instantiation_check(repo_root: Any, *, timeout_ms: int = 10000) -> dict[str, Any]:
    """Derive the committed finite results as instances of the general theorems.

    ``P7-U-T2`` says the current results cannot be instances of a calculus that
    does not exist, and asks for them to be derived once it does. Three things
    are checked here and they are not the same strength.

    1. **The 25 successes and the 25 matched missing-bridge cases are discharged
       one at a time as ground instances**, each as its own Z3 query against the
       general axioms. The composite of two carrying legs with a bridged hand-off
       must be provably carrying; with an unbridged hand-off, provably not. Fifty
       queries, fifty instances.

    2. **The committed unit rule is the closure lift**, checked exhaustively over
       all 320 rows the artifact enumerates. If ``carries`` were anything other
       than ``Native /\\ all coordinates`` the theorems would be about a different
       function.

    3. **The published counts are reproduced** from the committed model's own
       functions, so the numbers this report speaks about are the numbers on
       disk.

    What this does *not* do is make the donors mean anything. Neither donor is
    read by the committed loop --- the 25 pairs are five names crossed with
    themselves and ``c1``, ``c2`` are the same constant --- so the instances are
    fifty copies of two facts. That is a fact about the committed artifact, not
    about this calculus, and it is reported rather than smoothed over: the
    general theorems cover arbitrary chains, and the finite result they cover is
    thin.
    """

    import json
    from pathlib import Path

    solver = require_z3()
    model = load_executable_model(repo_root)
    sig = signature()
    axioms = _corollary_axioms(sig, timeout_ms=30000)
    full = (True,) * len(CLOSURE_COORDINATES)

    # 1. The fifty composition rows, each as a ground instance.
    instances: list[ProofResult] = []
    for left_donor in model.DONORS:
        for right_donor in model.DONORS:
            for bridged in (True, False):
                tag = f"inst_{left_donor}_{right_donor}_{int(bridged)}"
                world, left, right = _ground_world(
                    sig,
                    native_left=True,
                    closure_left=full,
                    native_right=True,
                    closure_right=full,
                    bridge_match=bridged,
                    exact=bridged and (left_donor == right_donor),
                    tag=tag,
                )
                expected = model.compose(
                    model.carries(True, full), model.carries(True, full), bridged
                )
                claim = sig.Carries(sig.Comp(left, right)) == solver.BoolVal(expected)
                instances.append(
                    discharge(
                        Theorem(
                            name=f"INSTANCE__{left_donor}__{right_donor}__"
                            f"{'BRIDGED' if bridged else 'UNBRIDGED'}",
                            statement=(
                                f"the committed row for ({left_donor}, {right_donor}) with "
                                f"bridge_match={bridged} is an instance of "
                                "INTERMEDIATE_CONTRACT_COMPOSITION"
                            ),
                            why_it_matters=(
                                "P7-U-T2 asks for the finite results to be derived as "
                                "instances rather than to stand beside the general theorem"
                            ),
                        ),
                        [*axioms, *world],
                        claim,
                        timeout_ms=timeout_ms,
                    )
                )

    # 2. The unit rule, exhaustively over the artifact's own 320 rows.
    lift_disagreements: list[str] = []
    lift_rows = 0
    lift_positive = 0
    for donor in model.DONORS:
        for native in (False, True):
            for closure in itertools.product((False, True), repeat=len(CLOSURE_COORDINATES)):
                lift_rows += 1
                expected = model.carries(native, closure)
                if expected:
                    lift_positive += 1
                if expected != (native and all(closure)):
                    lift_disagreements.append(f"{donor} {native} {closure}")
    lift = DifferentialReport(
        trials=lift_rows,
        agreements=lift_rows - len(lift_disagreements),
        disagreements=tuple(lift_disagreements[:20]),
        positive_trials=lift_positive,
    )

    # 3. The published counts, recomputed from the committed functions.
    published = json.loads((Path(repo_root) / COMMITTED_RESULT).read_text(encoding="utf-8"))
    recomputed = _recompute_committed_counts(model)
    mismatched = {
        key: {"published": published.get(key), "recomputed": value}
        for key, value in recomputed.items()
        if published.get(key) != value
    }

    undischarged = [r.theorem.name for r in instances if not r.discharged]
    return {
        "composition_instances_attempted": len(instances),
        "composition_instances_discharged": len(instances) - len(undischarged),
        "composition_instances_undischarged": undischarged,
        "closure_lift_rows": lift.as_json(),
        "published_counts": {key: published.get(key) for key in recomputed},
        "recomputed_counts": recomputed,
        "counts_mismatched": mismatched,
        "instances_are_thin": (
            "neither donor is read by the committed composition loop and both legs are "
            "the same constant True, so the fifty instances above are fifty copies of "
            "two facts. They are genuine instances of the general theorem; the general "
            "theorem is what covers arbitrary chains"
        ),
    }


def _recompute_committed_counts(model: Any) -> dict[str, int]:
    """Recompute the artifact's published counts from its own two functions.

    Deliberately not a re-run of the committed script: the point is that the
    numbers follow from ``carries`` and ``compose`` alone, so they are recomputed
    from those and compared against what was published.
    """

    full = (True,) * len(CLOSURE_COORDINATES)
    coordinates = len(CLOSURE_COORDINATES)
    counts = {
        "state_evaluations": 0,
        "single_coordinate_separation_witnesses": 0,
        "donor_product_nonclosure_countermodels": 0,
        "full_closure_refinement_successes": 0,
        "partial_closure_refinement_failures": 0,
        "composition_successes": 0,
        "composition_bridge_countermodels": 0,
    }
    for _donor in model.DONORS:
        for native in (False, True):
            for _closure in itertools.product((False, True), repeat=coordinates):
                counts["state_evaluations"] += 1
        for position in range(coordinates):
            broken = list(full)
            broken[position] = False
            if model.carries(True, full) and not model.carries(True, tuple(broken)):
                counts["single_coordinate_separation_witnesses"] += 1
    for closure in itertools.product((False, True), repeat=coordinates):
        if not all(closure) and not model.carries(True, closure):
            counts["donor_product_nonclosure_countermodels"] += 1
    for _donor in model.DONORS:
        for size in range(1, coordinates + 1):
            for changed in itertools.combinations(range(coordinates), size):
                damaged = [True] * coordinates
                for position in changed:
                    damaged[position] = False
                for partial_size in range(len(changed)):
                    for repaired in itertools.combinations(changed, partial_size):
                        partial = damaged[:]
                        for position in repaired:
                            partial[position] = True
                        if not model.carries(True, tuple(partial)):
                            counts["partial_closure_refinement_failures"] += 1
                if model.carries(True, full):
                    counts["full_closure_refinement_successes"] += 1
    for _left in model.DONORS:
        for _right in model.DONORS:
            carrying = model.carries(True, full)
            if model.compose(carrying, carrying, True):
                counts["composition_successes"] += 1
            if not model.compose(carrying, carrying, False):
                counts["composition_bridge_countermodels"] += 1
    return counts


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------


def build_report(
    repo_root: Any, *, differential_trials: int = 120, chain_bound: int = CHAIN_LADDER_BOUND
) -> dict[str, object]:
    """Everything this module establishes, with what it does not establish."""

    theorems = prove_all()
    ladder = prove_chain_ladder(bound=chain_bound)
    pin = axiom_pin_bridge_soundness()
    differential = differential_check(repo_root, trials=differential_trials)
    instantiation = instantiation_check(repo_root)

    all_proofs = (*theorems, *ladder)
    undischarged = [r.theorem.name for r in all_proofs if not r.discharged]
    pin_holds = (
        pin["with_axiom"].outcome is ProofOutcome.COUNTEREXAMPLE
        and pin["without_axiom"].outcome is ProofOutcome.PROVED
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "record": "P7_COMPOSITION_CALCULUS_MECHANIZED",
        "solver": z3.get_version_string() if z3 is not None else None,
        "executable_model": EXECUTABLE_MODEL,
        "theorems": [r.as_json() for r in theorems],
        "chain_ladder": {"bound": chain_bound, "results": [r.as_json() for r in ladder]},
        "bridge_soundness_axiom_pin": {
            "with_axiom": pin["with_axiom"].as_json(),
            "without_axiom": pin["without_axiom"].as_json(),
            "axiom_is_load_bearing": pin_holds,
            "reading": (
                "with the axiom, no counterexample to TOTALITY_COMPOSES_UNDER_MATCH "
                "exists in the finite obligation model (COUNTEREXAMPLE here means the "
                "search for one came back unsat); without it, one does"
            ),
        },
        "differential_against_executable_model": differential.as_json(),
        "instantiation_of_the_committed_result": instantiation,
        "all_discharged": not undischarged,
        "undischarged": undischarged,
        "what_this_establishes": (
            "identity, associativity and intermediate-contract composition hold for "
            "transformation chains of any length over uninterpreted sorts of "
            "transformations, contracts, closure coordinates and obligations, with the "
            "donor-native validity predicate left uninterpreted; the exact side "
            "conditions are named and each is pinned by a countermodel; the proved "
            "formula agrees with P7's committed carries/compose on a corpus exercising "
            "both verdicts; and the committed composition rows are discharged one at a "
            "time as ground instances of the general theorem"
        ),
        "side_conditions": {
            "identity": (
                "the unit laws need the intermediate-contract test to be reflexive. It "
                "is, because P7's own T5 reads 'exactly the same contract, or a "
                "registered bridge', and the first disjunct gives reflexivity. With the "
                "raw registered relation in its place identity fails: "
                "IDENTITY_NEEDS_A_REFLEXIVE_CONTRACT_TEST exhibits the model"
            ),
            "associativity": (
                "holds observationally with no condition on the bridge relation at all "
                "-- no reflexivity, symmetry or transitivity. As an equation between "
                "transformations it needs extensionality, and "
                "STRICT_LAWS_NEED_EXTENSIONALITY exhibits the model where the "
                "observables agree and the equation fails"
            ),
            "intermediate_contract_composition": (
                "matching intermediate contracts are sufficient and are NOT necessary. "
                "The exact condition is containment: every obligation the second leg's "
                "source demands is demanded by the first leg's target. P7's rule is "
                "therefore sound but incomplete with respect to its own obligation "
                "semantics -- fail-closed, refusing composites that are in fact total. "
                "MATCH_IS_NOT_NECESSARY locates the gap precisely: two contracts can "
                "demand exactly the same obligations and still be refused, because the "
                "test asks whether a bridge was registered rather than whether the "
                "obligations agree"
            ),
        },
        "one_hinge_and_its_corollaries": (
            "INTERMEDIATE_CONTRACT_COMPOSITION is discharged from the axioms alone and "
            "is then used as a hypothesis for ASSOCIATIVITY_CARRIES, "
            "UNMATCHED_INTERMEDIATE_CONTRACT_BLOCKS, COMPOSITION_NON_AMPLIFICATION and "
            "every chain-ladder length, because those are corollaries of it and because "
            "asking the solver to re-derive it inside each of them is what it cannot do "
            "reliably: ASSOCIATIVITY_CARRIES from the axioms alone was PROVED twice and "
            "UNKNOWN twice over four runs in a fresh process, and closes in 0.01s under "
            "the hinge every time. The gate is that the hinge must come back PROVED "
            "before it is used; otherwise the corollaries run against the axioms alone "
            "and report whatever the solver says"
        ),
        "how_a_false_claim_would_report": (
            "over the uninterpreted signature a false claim comes back UNKNOWN, not "
            "COUNTEREXAMPLE: refuting it means building a model and the quantified "
            "axioms defeat model-based instantiation. No PROVED line is weakened by "
            "that -- unsat is sound and a false claim cannot produce one -- but the "
            "failure to watch for in the validity half is a theorem that is not "
            "discharged rather than a printed countermodel. In the finite structures, "
            "which are decidable, countermodels are produced normally"
        ),
        "bridge_match_is_no_longer_a_supplied_premise": (
            "research/failures/2026-08-supplied-premise-unbuilt-decision/ records that "
            "the committed model's bridge_match is a caller-typed literal and leaves an "
            "open item for the theory lane: make it computed from the two transforms. "
            "In this calculus it is. Match(Tgt(t), Src(u)) is a function of the two "
            "transformations and of the registered bridge relation, so there is no "
            "argument left to supply. The committed artifact's counts still come from an "
            "expression in which no transform, contract or bridge appears; what is "
            "claimed here is only that this calculus does not have that hole"
        ),
        "axioms_are_definitional": (
            "the closure lift, the coordinate transport rule, the identity clauses and "
            "the obligation-totality clause are stated as axioms and are not derived "
            "from anything more primitive. They are transcriptions of "
            "P7_X2_CLOSURE_CARRYING_THEOREMS_V1.md, and composition soundness is derived "
            "from them rather than assumed. Extensionality and bridge soundness are "
            "declared separately because they are the two conditions the results depend "
            "on, and both are pinned"
        ),
        "induction_is_meta": (
            "the chain theorem holds at unbounded length by induction on chain length "
            "over INTERMEDIATE_CONTRACT_COMPOSITION and the endpoint axioms. The step is "
            "machine-checked; the induction schema is standard and is the single hand "
            "step in this development, corroborated by the expanded ladder"
        ),
        "not_licensed": [
            "any claim that the committed 25 successes and 25 matched missing-bridge "
            "cases were more than they are; neither donor is read by that loop and both "
            "legs are the same constant, so deriving them as instances of this calculus "
            "makes them instances of a general theorem without making them 25 facts",
            "any claim that P7's other formal core -- the 64-state support-transport "
            "theorem in check_theory_closure_v2.py -- is lifted here; it is a different "
            "model and is untouched",
            "any claim of independent formal review; these proofs have been checked by a "
            "solver, not reviewed by a person outside this lane",
            "any empirical, pipeline or deployed-agent claim whatsoever",
        ],
    }


def main(argv: list[str]) -> int:
    """CLI entry point. ``argv`` is required: there is no implicit run."""

    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="orion-p7-composition-calculus",
        description="Discharge P7's composition calculus over arbitrary transformation chains.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--differential-trials", type=int, default=120)
    parser.add_argument("--chain-bound", type=int, default=CHAIN_LADDER_BOUND)
    args = parser.parse_args(argv)

    report = build_report(
        args.repo_root,
        differential_trials=args.differential_trials,
        chain_bound=args.chain_bound,
    )
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"written: {args.output}")

    for item in report["theorems"]:
        print(f"  {item['outcome']:15s} {item['name']}")
    ladder = report["chain_ladder"]["results"]
    print(
        f"  chain ladder: {sum(1 for r in ladder if r['outcome'] == 'PROVED')}/{len(ladder)} "
        f"lengths discharged"
    )
    differential = report["differential_against_executable_model"]
    print(
        f"  differential: {differential['agreements']}/{differential['trials']} agree, "
        f"{differential['positive_trials']} positive, "
        f"both verdicts exercised: {differential['exercised_both_verdicts']}"
    )
    instantiation = report["instantiation_of_the_committed_result"]
    print(
        f"  instances: {instantiation['composition_instances_discharged']}/"
        f"{instantiation['composition_instances_attempted']} committed composition rows "
        "discharged as instances"
    )
    print(f"  bridge-soundness axiom is load-bearing: {report['bridge_soundness_axiom_pin']['axiom_is_load_bearing']}")

    if not report["all_discharged"]:
        print(f"UNDISCHARGED: {report['undischarged']}")
        return 3
    if not differential["agreed"]:
        print("THE FORMULA DISAGREES WITH THE COMMITTED MODEL")
        return 3
    if not differential["exercised_both_verdicts"]:
        print("THE DIFFERENTIAL CORPUS EXERCISED ONE VERDICT ONLY")
        return 3
    if instantiation["composition_instances_undischarged"]:
        print(f"UNDISCHARGED INSTANCES: {instantiation['composition_instances_undischarged']}")
        return 3
    if instantiation["counts_mismatched"]:
        print(f"PUBLISHED COUNTS DO NOT RECOMPUTE: {instantiation['counts_mismatched']}")
        return 3
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
