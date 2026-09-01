"""P7's donor stack, interpreted as a transformation family in the proved calculus.

``P7-U-T2`` asks for P7's finite composition result to follow *as a corollary* of
the general calculus ``P7-U-T1`` discharged. The blocker written against it says
what was wrong with the first attempt, and it is worth quoting because this
module is written against it:

    Instrumenting the shipped runner shows it evaluates ``compose`` at 2 of its 8
    possible argument triples --- ``(True, True, False)`` and ``(True, True,
    True)`` --- so both legs are constant and the 25 successes and 25
    countermodels are two values of ``bridge_match`` counted 25 times each by a
    5x5 donor loop in which the donor never enters the function. Deriving 50
    instances of two evaluations is not deriving 50 facts.

and the unblock names two jobs: vary the arguments the shipped loop holds
constant, and interpret the five donor families as models of the proved
primitives so the donor loop stops being a multiplier.

The interpretation
------------------
A donor family is a **transformation**, not a name. Under the interpretation each
of P7's five families ``d`` is a transformation ``T(d)`` in the calculus's
``Trans`` sort, carrying its own source and target obligation contracts
``Src(T(d))`` and ``Tgt(T(d))``, its own donor-native verdict ``Native(T(d))``
and its own closure coordinates ``Holds(T(d), c)``. The composition row for the
ordered pair ``(d1, d2)`` is the composite ``Comp(T(d1), T(d2))``, and the thing
the committed runner passes as the literal ``bridge_match`` is
``Match(Tgt(T(d1)), Src(T(d2)))`` --- a function of the two transformations and
of the registered bridge relation.

That is the whole of it, and it is what removes the multiplier. In the committed
loop ``d1`` and ``d2`` appear nowhere on the right-hand side of anything, so the
25 iterations pass identical arguments. Under the interpretation the third
argument is *indexed by the pair*: the loop visits 25 distinct hand-off contract
pairs and the registry decides each one separately. Whether the registry in fact
decides them differently is a question about the registry, and the answer for
P7's published registries is measured below rather than assumed.

Three frame conditions, and the first one is not a choice
--------------------------------------------------------
The interpretation is stated as three explicit axioms rather than as an
encoding, so each can be dropped and watched:

1. ``handoffs_are_never_contract_identities`` --- no donor's target contract is
   any donor's source contract, its own included.
2. ``distinct_donors_have_distinct_endpoints`` --- different families consume
   different contracts and emit different contracts.
3. ``the_donor_stack_is_inhabited`` --- there is at least one donor.

The first is **forced by the shipped result** and this is checkable rather than
argued. Once ``bridge_match`` is computed instead of typed, a row asserting
``not compose(c1, c2, False)`` is only realisable when the hand-off does not
match by contract equality. The committed runner asserts that row for all 25
ordered pairs, the diagonal included, so *any* contract assignment reproducing
P7's 25 bridge countermodels satisfies condition 1, and any assignment violating
it reproduces at most 24. The published count and the frame condition are the
same statement. :func:`counts_are_sensitive_to_the_interpretation` measures this.

The second is not forced by the counts, and that is the finding this module would
rather not have. Two readings that make the donor loop a pure multiplier ---
every family consuming one shared input contract and emitting one shared output
contract (1 distinct hand-off), and every family emitting one shared output
contract (5 distinct hand-offs) --- reproduce both published counts exactly. The
counts cannot tell them from the interpretation. What tells them apart is
:data:`THE_HANDOFF_IDENTIFIES_THE_DONOR_PAIR`, which is exactly the theorem that
dropping condition 2 loses, and the directly measured number of distinct
hand-offs the loop visits, which is 25 under the interpretation and 1 and 5 under
the two impostors.

What the arguments do once they vary
------------------------------------
The six argument triples the shipped loop never reaches are the ones where a leg
does not carry. Under the interpretation those are donors whose closure vector or
native verdict fails, and :data:`A_LEFT_LEG_THAT_DOES_NOT_CARRY_REFUSES` and
:data:`A_RIGHT_LEG_THAT_DOES_NOT_CARRY_REFUSES` cover them at arbitrary width, for
any number of donors and any number of closure coordinates.
:func:`argument_space_under_the_interpretation` then exercises them on the
committed functions: every ordered donor pair against every closure vector on
each side and both values of the registry bit, which reaches all 8 triples.

The honest residue
------------------
None of that changes what P7 *published*. Reproducing ``composition_successes:
25`` requires every hand-off bridged and every donor carrying, and reproducing
``composition_bridge_countermodels: 25`` requires no hand-off bridged and every
donor carrying. Both are uniform registries over an all-carrying stack, so the
published recomputation still reaches 2 of the 8 argument triples --- not because
the loop holds its arguments constant any more, but because the two registries
P7 shipped assign the same value to all 25 hand-offs. The 25 rows are now 25
distinct hand-offs rather than 25 copies of one argument; they are still 25
agreeing verdicts. A non-uniform registry would separate them and the committed
artifact contains none.

So: the composition half is an instance of theorems about donor stacks of any
size, the six unreached triples are covered by theorem and exercised on the
committed code, and the published pair of counts carries the information of one
frame condition and two uniform registries. All three of those are stated in the
report rather than left for a reader to work out.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from itertools import product
from typing import Any

from orion.programme.mechanized import (
    DifferentialReport,
    ProofOutcome,
    ProofResult,
    Theorem,
    discharge,
    load_executable_model,
    require_z3,
)
from orion.study.p7.composition_calculus_smt import (
    COMMITTED_RESULT,
    EXECUTABLE_MODEL,
    checker_axioms,
    composition_lemma,
    prove_hinge,
    signature,
)

SCHEMA_VERSION = "orion.p7.donor-stack-as-transformation-family.v1"

#: The two committed composition counts this module derives as instances.
PUBLISHED_COMPOSITION_SUCCESSES = 25
PUBLISHED_COMPOSITION_BRIDGE_COUNTERMODELS = 25

#: ``compose`` takes three booleans, so its whole input space is eight triples.
COMPOSE_ARITY = 3

__all__ = [
    "CANDIDATE_CONDITION_IDS",
    "COMMITTED_RESULT",
    "COMPOSE_ARITY",
    "CONTRACT_ASSIGNMENTS",
    "EXECUTABLE_MODEL",
    "FRAME_CONDITION_IDS",
    "PUBLISHED_COMPOSITION_BRIDGE_COUNTERMODELS",
    "PUBLISHED_COMPOSITION_SUCCESSES",
    "REGISTRIES",
    "SCHEMA_VERSION",
    "THEOREMS",
    "argument_space_under_the_interpretation",
    "build_report",
    "counts_are_sensitive_to_the_interpretation",
    "frame_conditions_are_load_bearing",
    "handoff_is_matched",
    "interpreted_stack",
    "main",
    "prove_all",
    "recompute_published_counts",
]


# ---------------------------------------------------------------------------
# The theorems the finite rows are instances of
# ---------------------------------------------------------------------------

BRIDGED_HANDOFF_COMPOSES = Theorem(
    name="BRIDGED_DONOR_HANDOFF_COMPOSES",
    statement=(
        "for any two donors that carry closure, a registered bridge between the "
        "contract the first emits and the contract the second consumes is enough for "
        "the composite to carry -- for a donor stack of any size over a coordinate "
        "sort of any size"
    ),
    why_it_matters=(
        "This is the general form of P7's 25 composition successes. The committed "
        "loop establishes it for one argument triple; here it is a statement about "
        "every pair of transformations in an uninterpreted sort, with the bridge read "
        "off the two transformations rather than supplied by the caller."
    ),
)

UNBRIDGED_HANDOFF_REFUSES = Theorem(
    name="UNBRIDGED_DONOR_HANDOFF_REFUSES",
    statement=(
        "for any two donors, if no bridge is registered between the contract the "
        "first emits and the contract the second consumes then the composite does not "
        "carry closure, however good both legs are"
    ),
    why_it_matters=(
        "The general form of P7's 25 bridge countermodels, and the half that carries "
        "the claim: donor-visible composability is not closure. Note the frame "
        "condition it needs -- without separated hand-offs the exact-contract disjunct "
        "of the match test fires and the refusal is false."
    ),
)

SELF_COMPOSITION_NEEDS_A_BRIDGE = Theorem(
    name="SELF_COMPOSITION_STILL_NEEDS_A_BRIDGE",
    statement=(
        "a donor composed with itself carries closure only if a bridge is registered "
        "from its own target contract back to its own source contract"
    ),
    why_it_matters=(
        "The five diagonal rows of P7's 5x5 loop. They are the rows most easily lost: "
        "under any reading in which a donor consumes what it produces, the match test "
        "succeeds by reflexivity and `assert not compose(c1, c2, False)` has no model "
        "at all. The shipped result asserts it for the diagonal too, which is why the "
        "interpretation has to separate the hand-offs and why that is not a free choice."
    ),
)

LEFT_LEG_REFUSES = Theorem(
    name="A_LEFT_LEG_THAT_DOES_NOT_CARRY_REFUSES",
    statement=(
        "if the first leg does not carry closure the composite does not carry it, "
        "whatever the second leg is and whatever the registry says"
    ),
    why_it_matters=(
        "Four of the six argument triples the shipped composition loop never "
        "evaluates. P7's published result contains no row in which a leg fails, so "
        "this is not a generalisation of anything it measured -- it is the part of the "
        "calculus that says what would have happened if it had."
    ),
)

RIGHT_LEG_REFUSES = Theorem(
    name="A_RIGHT_LEG_THAT_DOES_NOT_CARRY_REFUSES",
    statement=(
        "if the second leg does not carry closure the composite does not carry it, "
        "whatever the first leg is and whatever the registry says"
    ),
    why_it_matters=(
        "The remaining two unreached argument triples. Stated separately from the left "
        "leg because a composition rule that was asymmetric in its legs would fail "
        "exactly one of the two, and a single symmetric statement would hide which."
    ),
)

HANDOFF_IDENTIFIES_THE_PAIR = Theorem(
    name="THE_HANDOFF_IDENTIFIES_THE_DONOR_PAIR",
    statement=(
        "distinct ordered donor pairs present distinct hand-offs: if two pairs agree "
        "on the emitted contract and on the consumed contract then they are the same "
        "pair"
    ),
    why_it_matters=(
        "This is the formal content of 'the donor loop stops being a multiplier'. "
        "Without it the 5x5 loop can visit one hand-off twenty-five times and every "
        "published count comes out the same -- which two of the wrong interpretations "
        "below actually do. The counts cannot see the difference; this theorem can."
    ),
)

DISTINCT_HANDOFFS_CAN_DIFFER = Theorem(
    name="DISTINCT_HANDOFFS_CAN_DIFFER_IN_VERDICT",
    statement=(
        "two donor pairs whose hand-offs the registry decides differently have "
        "composites that carry differently: the verdict tracks the pair"
    ),
    why_it_matters=(
        "The other half of the same point. It is not enough that the loop visits "
        "distinct hand-offs; the verdict has to depend on which one it is at. Under "
        "the committed model it provably cannot, because `bridge_match` is a literal. "
        "Under the interpretation it does."
    ),
)

UNBRIDGED_REFUSAL_IS_NOT_VACUOUS = Theorem(
    name="UNBRIDGED_REFUSAL_IS_NOT_VACUOUS",
    statement=(
        "on an inhabited donor stack that carries closure and has no bridge registered "
        "between any of its hand-offs, some ordered pair of carrying donors has a "
        "composite that does not carry"
    ),
    why_it_matters=(
        "A refusal theorem quantified over an empty stack is a theorem about nothing, "
        "and that is the exact shape of failure this repository's guards are built "
        "for. This says the 25 countermodels have witnesses rather than assuming they do."
    ),
)

BRIDGED_SUCCESS_IS_NOT_VACUOUS = Theorem(
    name="BRIDGED_SUCCESS_IS_NOT_VACUOUS",
    statement=(
        "on an inhabited donor stack that carries closure and has every hand-off "
        "bridged, some ordered pair of donors has a composite that carries"
    ),
    why_it_matters=(
        "The same guard on the positive side. Kept separate because a stack can be "
        "inhabited by transformations that do not carry, in which case the successes "
        "would be vacuous while the refusals were not."
    ),
)

NO_IDENTITY_IS_A_DONOR = Theorem(
    name="NO_IDENTITY_IS_A_DONOR_IS_DERIVED",
    statement=(
        "no identity transformation is a donor. This was a candidate fourth frame "
        "condition; it is a consequence of separated hand-offs and is discharged here "
        "rather than assumed"
    ),
    why_it_matters=(
        "An axiom no theorem needs is decoration, and a redundant presentation of an "
        "axiom that is working looks identical to it from inside. Deriving this settles "
        "which: the interpretation rests on three conditions, and the plausible fourth "
        "is a theorem about them."
    ),
)

COMPOSITE_HANDOFFS_INHERIT_SEPARATION = Theorem(
    name="COMPOSITE_HANDOFFS_INHERIT_SEPARATION_IS_DERIVED",
    statement=(
        "the composite of two donors emits a contract that is no donor's source "
        "contract either, so a chain never acquires a hand-off the stack did not have"
    ),
    why_it_matters=(
        "The other candidate axiom, and the one that would have been tempting to state "
        "in order to reach the chain theorem. It is not needed: a composite's target is "
        "its last leg's target, which is a structural axiom of the calculus, so the "
        "separation transports for free."
    ),
)

THREE_DONOR_CHAIN = Theorem(
    name="A_THREE_DONOR_CHAIN_NEEDS_EVERY_BRIDGE",
    statement=(
        "a chain of three donors carries closure exactly when all three legs carry and "
        "both interior hand-offs are bridged -- one missing bridge anywhere in the "
        "chain refuses the whole chain"
    ),
    why_it_matters=(
        "P7's published composition result is about pairs. This is the first length at "
        "which a chain has an interior, and it is where a rule that checked only its "
        "endpoints would diverge from one that checks every hand-off."
    ),
)

THEOREMS: tuple[Theorem, ...] = (
    BRIDGED_HANDOFF_COMPOSES,
    UNBRIDGED_HANDOFF_REFUSES,
    SELF_COMPOSITION_NEEDS_A_BRIDGE,
    LEFT_LEG_REFUSES,
    RIGHT_LEG_REFUSES,
    HANDOFF_IDENTIFIES_THE_PAIR,
    DISTINCT_HANDOFFS_CAN_DIFFER,
    UNBRIDGED_REFUSAL_IS_NOT_VACUOUS,
    BRIDGED_SUCCESS_IS_NOT_VACUOUS,
    NO_IDENTITY_IS_A_DONOR,
    COMPOSITE_HANDOFFS_INHERIT_SEPARATION,
    THREE_DONOR_CHAIN,
)


# ---------------------------------------------------------------------------
# The interpretation, as frame conditions on the composition signature
# ---------------------------------------------------------------------------

#: The frame conditions, each independently droppable so its weight is measured.
#:
#: There are three, not five. ``no identity is a donor`` and ``a composite's
#: hand-off is separated too`` were both written as axioms first and both came
#: back inert; they are consequences of the first condition and of the calculus's
#: structural axioms respectively, and they are now discharged as theorems
#: instead. That is not a claim about a run nobody can repeat:
#: :data:`CANDIDATE_CONDITION_IDS` keeps them, and
#: :func:`frame_conditions_are_load_bearing` adds them back on every run and
#: reports which theorems that makes newly provable. The answer has to stay
#: none.
FRAME_CONDITION_IDS: tuple[str, ...] = (
    "handoffs_are_never_contract_identities",
    "distinct_donors_have_distinct_endpoints",
    "the_donor_stack_is_inhabited",
)


def _interpretation_axioms(
    sig: Any, donor: Any, witness: Any, *, drop: str | None = None
) -> list[Any]:
    """The donor stack, written as axioms rather than as an encoding.

    ``drop`` omits one named condition. A frame condition no theorem needs is not
    part of the interpretation, and a proof that survives dropping every condition
    was never about the interpretation in the first place.
    """

    if drop is not None and drop not in FRAME_CONDITION_IDS:
        raise ValueError(f"unknown frame condition {drop!r}")

    solver = require_z3()
    left, right = solver.Consts("frame_t frame_u", sig.Trans)

    axioms: dict[str, Any] = {
        # No donor's target contract is any donor's source contract. This is the
        # condition P7's own 25 bridge countermodels assert: once `bridge_match`
        # is computed rather than typed, a refused composite is one whose
        # hand-off does not match, and the exact-contract disjunct of the match
        # test is the only way it could have matched without a bridge.
        "handoffs_are_never_contract_identities": solver.ForAll(
            [left, right],
            solver.Implies(
                solver.And(donor(left), donor(right)), sig.Tgt(left) != sig.Src(right)
            ),
        ),
        # Distinct families consume distinct contracts and emit distinct
        # contracts. Nothing in the published counts asserts this, which is
        # exactly why it is stated: without it the 5x5 loop can be visiting one
        # hand-off twenty-five times.
        "distinct_donors_have_distinct_endpoints": solver.ForAll(
            [left, right],
            solver.Implies(
                solver.And(donor(left), donor(right), left != right),
                solver.And(
                    sig.Tgt(left) != sig.Tgt(right), sig.Src(left) != sig.Src(right)
                ),
            ),
        ),
        # P7 registers five families, so the stack is not empty. Carried by the
        # two non-vacuity theorems and by nothing else, which is the correct
        # amount of work for it to be doing.
        "the_donor_stack_is_inhabited": donor(witness),
    }
    return [clause for name, clause in axioms.items() if name != drop]


#: The two conditions that were written as frame conditions first and removed.
#:
#: They are kept here so that "they were inert" is a measurement this module can
#: still make rather than a claim about a run nobody can repeat.
CANDIDATE_CONDITION_IDS: tuple[str, ...] = (
    "no_identity_is_a_donor",
    "composite_handoffs_are_separated_too",
)


def _candidate_condition_axioms(sig: Any, donor: Any) -> list[Any]:
    """The two rejected conditions, as the axioms they would have been."""

    solver = require_z3()
    left, right, third = solver.Consts("cand_t cand_u cand_v", sig.Trans)
    contract = solver.Const("cand_a", sig.Contract)
    return [
        solver.ForAll([contract], solver.Not(donor(sig.Ident(contract)))),
        solver.ForAll(
            [left, right, third],
            solver.Implies(
                solver.And(donor(left), donor(right), donor(third)),
                sig.Tgt(sig.Comp(left, right)) != sig.Src(third),
            ),
        ),
    ]


def _base_axioms(sig: Any, *, timeout_ms: int) -> list[Any]:
    """The calculus's axioms plus its composition lemma, if the lemma is proved.

    The lemma is :data:`composition_calculus_smt.INTERMEDIATE_CONTRACT_COMPOSITION`
    and it is a *consequence* of the axioms, not an addition to them --- but the
    solver cannot reliably re-derive it inside each of the queries below, which is
    the behaviour the parent module documents at length. So it is re-discharged
    from the axioms alone here, on every call, and used only if that run comes
    back ``PROVED``. A lemma being used must not quietly become an axiom being
    added.
    """

    axioms = checker_axioms(sig)
    hinge = prove_hinge(sig, axioms, timeout_ms=timeout_ms)
    return [*axioms, composition_lemma(sig)] if hinge.discharged else axioms


#: Sizes tried in order when hunting for a countermodel. Escalation is not a
#: convenience: dropping ``distinct_donors_have_distinct_endpoints`` yields no
#: countermodel at all in worlds of three or four elements and a clean one at
#: five, so a single small bound would have reported a load-bearing condition as
#: inert. A theorem about telling two donor pairs apart needs enough elements to
#: build two of them. Used in one direction only -- a model of the axioms plus a
#: negated claim is a countermodel however small its universe, while failing to
#: find one proves nothing -- so a bound is never added to a proof query.
REFUTATION_WORLD_SIZES: tuple[int, ...] = (3, 4, 5, 6)
BOUNDED_SORTS: tuple[str, ...] = ("Trans", "Contract", "Coord", "Obl")


def _cardinality_axioms(sig: Any, size: int) -> list[Any]:
    """Confine each sort to at most ``size`` elements."""

    solver = require_z3()
    axioms = []
    for index, name in enumerate(BOUNDED_SORTS):
        sort = getattr(sig, name)
        members = [solver.Const(f"world_{name}_{n}", sort) for n in range(size)]
        x = solver.Const(f"bounded_{name}_{index}", sort)
        axioms.append(solver.ForAll([x], solver.Or(*[x == member for member in members])))
    return axioms


def _prove_all_timed(
    *,
    timeout_ms: int = 30000,
    drop: str | None = None,
    add_candidates: bool = False,
    bound: int | None = None,
    only: frozenset[str] | None = None,
) -> tuple[tuple[ProofResult, ...], dict[str, float]]:
    """Discharge every theorem, returning wall-clock seconds beside each result.

    The timings are not decoration. :func:`frame_conditions_are_load_bearing`
    re-runs this with a shorter budget, and a theorem that would have been proved
    but timed out under that budget would be reported as a lost theorem --- a
    frame condition looking load-bearing because the solver was rushed. Reporting
    the slowest successful proof makes the headroom a measurement.
    """

    solver = require_z3()
    sig = signature()
    donor = solver.Function("Donor", sig.Trans, solver.BoolSort())
    witness = solver.Const("StackWitness", sig.Trans)

    axioms = [
        *_base_axioms(sig, timeout_ms=timeout_ms),
        *_interpretation_axioms(sig, donor, witness, drop=drop),
    ]
    if add_candidates:
        axioms.extend(_candidate_condition_axioms(sig, donor))
    if bound is not None:
        # Refutation only. See REFUTATION_WORLD_SIZES.
        axioms.extend(_cardinality_axioms(sig, bound))

    t, u, v, w = solver.Consts("q_t q_u q_v q_w", sig.Trans)
    contract = solver.Const("q_contract", sig.Contract)

    def handoff(left: Any, right: Any) -> Any:
        return sig.Bridge(sig.Tgt(left), sig.Src(right))

    def carrying(*items: Any) -> Any:
        return solver.And(*[sig.Carries(item) for item in items])

    def donors(*items: Any) -> Any:
        return solver.And(*[donor(item) for item in items])

    claims: list[tuple[Theorem, Any]] = [
        (
            BRIDGED_HANDOFF_COMPOSES,
            solver.ForAll(
                [t, u],
                solver.Implies(
                    solver.And(donors(t, u), carrying(t, u), handoff(t, u)),
                    sig.Carries(sig.Comp(t, u)),
                ),
            ),
        ),
        (
            UNBRIDGED_HANDOFF_REFUSES,
            solver.ForAll(
                [t, u],
                solver.Implies(
                    solver.And(donors(t, u), solver.Not(handoff(t, u))),
                    solver.Not(sig.Carries(sig.Comp(t, u))),
                ),
            ),
        ),
        (
            SELF_COMPOSITION_NEEDS_A_BRIDGE,
            solver.ForAll(
                [t],
                solver.Implies(
                    solver.And(donor(t), solver.Not(handoff(t, t))),
                    solver.Not(sig.Carries(sig.Comp(t, t))),
                ),
            ),
        ),
        (
            LEFT_LEG_REFUSES,
            solver.ForAll(
                [t, u],
                solver.Implies(
                    solver.Not(sig.Carries(t)), solver.Not(sig.Carries(sig.Comp(t, u)))
                ),
            ),
        ),
        (
            RIGHT_LEG_REFUSES,
            solver.ForAll(
                [t, u],
                solver.Implies(
                    solver.Not(sig.Carries(u)), solver.Not(sig.Carries(sig.Comp(t, u)))
                ),
            ),
        ),
        (
            HANDOFF_IDENTIFIES_THE_PAIR,
            solver.ForAll(
                [t, u, v, w],
                solver.Implies(
                    solver.And(
                        donors(t, u, v, w),
                        sig.Tgt(t) == sig.Tgt(v),
                        sig.Src(u) == sig.Src(w),
                    ),
                    solver.And(t == v, u == w),
                ),
            ),
        ),
        (
            DISTINCT_HANDOFFS_CAN_DIFFER,
            solver.ForAll(
                [t, u, v, w],
                solver.Implies(
                    solver.And(
                        donors(t, u, v, w),
                        carrying(t, u, v, w),
                        handoff(t, u) != handoff(v, w),
                    ),
                    sig.Carries(sig.Comp(t, u)) != sig.Carries(sig.Comp(v, w)),
                ),
            ),
        ),
        (
            UNBRIDGED_REFUSAL_IS_NOT_VACUOUS,
            solver.Implies(
                solver.And(
                    sig.Carries(witness),
                    solver.ForAll(
                        [t, u],
                        solver.Implies(donors(t, u), solver.Not(handoff(t, u))),
                    ),
                ),
                solver.Exists(
                    [t, u],
                    solver.And(
                        donors(t, u),
                        carrying(t, u),
                        solver.Not(sig.Carries(sig.Comp(t, u))),
                    ),
                ),
            ),
        ),
        (
            BRIDGED_SUCCESS_IS_NOT_VACUOUS,
            solver.Implies(
                solver.And(
                    sig.Carries(witness),
                    solver.ForAll([t, u], solver.Implies(donors(t, u), handoff(t, u))),
                ),
                solver.Exists(
                    [t, u], solver.And(donors(t, u), sig.Carries(sig.Comp(t, u)))
                ),
            ),
        ),
        (
            NO_IDENTITY_IS_A_DONOR,
            solver.ForAll([contract], solver.Not(donor(sig.Ident(contract)))),
        ),
        (
            COMPOSITE_HANDOFFS_INHERIT_SEPARATION,
            solver.ForAll(
                [t, u, v],
                solver.Implies(donors(t, u, v), sig.Tgt(sig.Comp(t, u)) != sig.Src(v)),
            ),
        ),
        (
            THREE_DONOR_CHAIN,
            solver.ForAll(
                [t, u, v],
                solver.Implies(
                    donors(t, u, v),
                    sig.Carries(sig.Comp(sig.Comp(t, u), v))
                    == solver.And(
                        carrying(t, u, v), handoff(t, u), handoff(u, v)
                    ),
                ),
            ),
        ),
    ]

    results: list[ProofResult] = []
    seconds: dict[str, float] = {}
    for theorem, claim in claims:
        # `only` exists for the bounded refutation sweep. Re-asking a theorem
        # that is already refuted, or one the sweep is not looking for, costs a
        # full timeout each: twelve theorems at four world sizes for three
        # conditions is 144 queries, most of which have no model to find and
        # burn the whole budget.
        if only is not None and theorem.name not in only:
            continue
        started = time.monotonic()
        result = discharge(theorem, axioms, claim, timeout_ms=timeout_ms)
        seconds[theorem.name] = round(time.monotonic() - started, 4)
        results.append(result)
    return tuple(results), seconds


def prove_all(*, timeout_ms: int = 30000, drop: str | None = None) -> tuple[ProofResult, ...]:
    """Discharge every theorem in :data:`THEOREMS` under the interpretation."""

    return _prove_all_timed(timeout_ms=timeout_ms, drop=drop)[0]


def frame_conditions_are_load_bearing(
    *,
    timeout_ms: int = 30000,
    drop_timeout_ms: int = 3000,
    refutation_timeout_ms: int = 40000,
) -> dict[str, Any]:
    """Drop each frame condition and record which theorems are *refuted*.

    Not "stop being provable", which is what this measured first and what the
    paragraph below then argued was good enough. The argument is a headroom
    factor and it is still reported, but it is not a refutation: a claim can be
    true and hard, and over this signature a false claim usually cannot be
    refuted by a model at all, so the solver runs to the timeout either way.
    Bounding the sorts makes the search finite and turns eight of the ten
    reported losses into genuine countermodels.

    ``drop_timeout_ms`` is shorter than the baseline budget because the drop runs
    are dominated by claims that have become *false*, and over this uninterpreted
    signature a false claim cannot be refuted by a model --- the solver runs to
    the timeout and reports ``UNKNOWN``. Rather than assert that the shorter
    budget is safe, ``slowest_discharged_seconds`` reports the slowest proof that
    actually succeeded across every run; the ratio between that and the drop
    budget is the headroom, and a run where it stops being large is a run whose
    losses should not be believed.

    The reverse direction is measured here too. Two conditions were written as
    frame conditions first and removed as inert; they are added back to the axiom
    set on every run and the theorems that becomes newly provable are reported.
    Recording "they were inert" as history would make it a claim about a run
    nobody can repeat, and the two are exactly the kind of axiom that quietly
    becomes load-bearing when a theorem is added.
    """

    baseline_results, baseline_seconds = _prove_all_timed(timeout_ms=timeout_ms)
    baseline = {r.theorem.name for r in baseline_results if r.discharged}

    # The two conditions that were written as axioms first. Adding them back must
    # make nothing newly provable, or "inert" was a guess.
    with_candidates, _ = _prove_all_timed(timeout_ms=timeout_ms, add_candidates=True)
    gained = sorted(
        {r.theorem.name for r in with_candidates if r.discharged} - baseline
    )
    slowest = max(
        (seconds for name, seconds in baseline_seconds.items() if name in baseline),
        default=0.0,
    )

    slowest_bounded = 0.0
    refuted: dict[str, list[str]] = {}
    found_at: dict[str, dict[str, int]] = {}
    #: Per condition, the last verdict seen for each theorem, at the largest
    #: world size tried. Distinguishes "no countermodel exists there" from "the
    #: search ran out of budget", which the inert test used to conflate.
    settled: dict[str, dict[str, ProofOutcome]] = {
        condition: {} for condition in FRAME_CONDITION_IDS
    }
    unbounded_unknown: dict[str, list[str]] = {}
    outcomes: dict[str, dict[str, str]] = {}
    for condition in FRAME_CONDITION_IDS:
        open_results, open_seconds = _prove_all_timed(
            timeout_ms=drop_timeout_ms, drop=condition
        )
        slowest = max(
            slowest,
            max(
                (open_seconds[r.theorem.name] for r in open_results if r.discharged),
                default=0.0,
            ),
        )
        outcomes[condition] = {r.theorem.name: r.outcome.value for r in open_results}
        unbounded_unknown[condition] = sorted(
            r.theorem.name
            for r in open_results
            if r.theorem.name in baseline and r.outcome is ProofOutcome.UNKNOWN
        )
        hits: dict[str, int] = {
            r.theorem.name: 0
            for r in open_results
            if r.theorem.name in baseline and r.outcome is ProofOutcome.COUNTEREXAMPLE
        }
        outstanding = frozenset(baseline - set(hits))
        for size in REFUTATION_WORLD_SIZES:
            if not outstanding:
                break
            # A refutation is not a proof and must not share its budget. The
            # size-5 countermodel for `distinct_donors_have_distinct_endpoints`
            # is found in seconds on an idle machine and missed under load at
            # the 3s drop budget, which reported a load-bearing condition as
            # inert -- the failure this whole function exists to avoid.
            results, seconds = _prove_all_timed(
                timeout_ms=refutation_timeout_ms,
                drop=condition,
                bound=size,
                only=outstanding,
            )
            # Deliberately not folded into `slowest`. That number backs a claim
            # about the *drop* budget -- that an unknown there is not a rushed
            # proof -- and the bounded refutation runs are a different question
            # asked under a different budget. Mixing them would quietly turn the
            # headroom into a ratio between two unrelated things.
            slowest_bounded = max(
                slowest_bounded,
                max((seconds[r.theorem.name] for r in results if r.discharged), default=0.0),
            )
            for result in results:
                if result.theorem.name not in baseline:
                    continue
                # Keep the last verdict for every theorem still outstanding, at
                # the largest size tried. Without it, "no countermodel found"
                # cannot be told from "the search gave up", and only the first
                # is evidence that the condition carries nothing.
                settled[condition][result.theorem.name] = result.outcome
                if (
                    result.outcome is ProofOutcome.COUNTEREXAMPLE
                    and result.theorem.name not in hits
                ):
                    hits[result.theorem.name] = size
            outstanding = frozenset(baseline - set(hits))
        refuted[condition] = sorted(hits)
        found_at[condition] = dict(sorted(hits.items()))

    # A condition with no countermodel is inert only when every one of its
    # searches *settled* on not having one. The function's own docstring records
    # a load-bearing condition being reported inert because a countermodel was
    # missed under load, and the remedy taken then was a longer refutation
    # budget -- which lowers the odds without changing what an exhausted budget
    # is reported as. An unknown return is a fact about the search in this
    # direction too.
    gave_up = {
        condition: sorted(
            name
            for name, outcome in settled[condition].items()
            if outcome is ProofOutcome.UNKNOWN and name not in set(refuted[condition])
        )
        for condition in refuted
    }
    inert = sorted(
        name for name, lost in refuted.items() if not lost and not gave_up[name]
    )
    undecided_conditions = sorted(
        name for name, lost in refuted.items() if not lost and gave_up[name]
    )
    return {
        "baseline_discharged": sorted(baseline),
        "rejected_candidate_conditions": list(CANDIDATE_CONDITION_IDS),
        "theorems_gained_by_adding_the_candidates": gained,
        "the_rejected_candidates_are_inert": not gained,
        "theorems_refuted_by_dropping": refuted,
        "world_size_the_refutation_needed": found_at,
        "left_unknown_by_the_unbounded_search": unbounded_unknown,
        "world_sizes_tried": list(REFUTATION_WORLD_SIZES),
        "outcome_when_dropped": outcomes,
        "criterion": (
            "a condition is load-bearing only when dropping it yields an actual "
            "countermodel, searched for in bounded worlds of increasing size. A theorem "
            "that merely stops being provable is not counted: over this signature a "
            "false claim usually cannot be refuted by a model, so the solver runs to the "
            "timeout whether the claim is false or merely hard. Under the loose "
            "criterion this reported ten losses, of which two were countermodels and "
            "eight were unknown, and one condition's entire weight was a single unknown. "
            "Sizes escalate because that condition's countermodel appears only at five "
            "elements, and stopping at four would have called it inert -- the same "
            "mistake in the other direction."
        ),
        "inert_conditions": inert,
        "conditions_left_undecided": undecided_conditions,
        "theorems_the_search_gave_up_on": {k: v for k, v in gave_up.items() if v},
        "every_condition_carries_a_theorem": not inert and not undecided_conditions,
        "drop_timeout_ms": drop_timeout_ms,
        "refutation_timeout_ms": refutation_timeout_ms,
        "slowest_bounded_refutation_seconds": round(slowest_bounded, 4),
        "slowest_discharged_seconds": round(slowest, 4),
        "headroom_factor": round(drop_timeout_ms / 1000 / slowest, 1) if slowest else None,
        "headroom_note": (
            "Every theorem that is discharged anywhere in these runs is discharged in "
            f"{slowest:.4f}s against a drop budget of {drop_timeout_ms / 1000:.1f}s, a "
            f"factor of {drop_timeout_ms / 1000 / slowest:.0f}. A loss recorded here is "
            "a claim the solver could not close in that much more time than the proofs "
            "need, not a claim it was rushed on."
        )
        if slowest
        else "no theorem was discharged, so there is no headroom to report",
    }


# ---------------------------------------------------------------------------
# The interpretation as data: contracts, registries, and the committed functions
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DonorStack:
    """One reading of P7's five families as transformations.

    ``source`` and ``target`` are the obligation contracts each family consumes
    and emits. They are what the interpretation adds; everything else here is
    P7's own data.
    """

    donors: tuple[str, ...]
    source: dict[str, str]
    target: dict[str, str]

    def handoff(self, left: str, right: str) -> tuple[str, str]:
        return (self.target[left], self.source[right])

    def distinct_handoffs(self) -> int:
        return len({self.handoff(left, right) for left in self.donors for right in self.donors})


def _separated(donors: tuple[str, ...]) -> DonorStack:
    return DonorStack(
        donors=donors,
        source={donor: f"{donor}::consumes" for donor in donors},
        target={donor: f"{donor}::emits" for donor in donors},
    )


def _one_input_and_one_output(donors: tuple[str, ...]) -> DonorStack:
    return DonorStack(
        donors=donors,
        source=dict.fromkeys(donors, "STACK::consumes"),
        target=dict.fromkeys(donors, "STACK::emits"),
    )


def _one_shared_contract(donors: tuple[str, ...]) -> DonorStack:
    return DonorStack(
        donors=donors,
        source=dict.fromkeys(donors, "STACK::contract"),
        target=dict.fromkeys(donors, "STACK::contract"),
    )


def _endomorphic(donors: tuple[str, ...]) -> DonorStack:
    return DonorStack(
        donors=donors,
        source={donor: f"{donor}::contract" for donor in donors},
        target={donor: f"{donor}::contract" for donor in donors},
    )


def _pipeline_chained(donors: tuple[str, ...]) -> DonorStack:
    return DonorStack(
        donors=donors,
        source={donor: f"link{index}" for index, donor in enumerate(donors)},
        target={donor: f"link{index + 1}" for index, donor in enumerate(donors)},
    )


def _one_shared_output(donors: tuple[str, ...]) -> DonorStack:
    return DonorStack(
        donors=donors,
        source={donor: f"{donor}::consumes" for donor in donors},
        target=dict.fromkeys(donors, "STACK::emits"),
    )


#: Candidate readings of the donor stack. The first is the interpretation; the
#: rest are wrong on purpose, and two of them reproduce both published counts.
CONTRACT_ASSIGNMENTS: dict[str, Any] = {
    "separated_handoffs": _separated,
    "one_input_and_one_output_contract": _one_input_and_one_output,
    "one_shared_contract": _one_shared_contract,
    "endomorphic_donors": _endomorphic,
    "pipeline_chained": _pipeline_chained,
    "one_shared_output_contract": _one_shared_output,
}

INTERPRETATION = "separated_handoffs"


def _every_handoff(stack: DonorStack) -> frozenset[tuple[str, str]]:
    return frozenset(
        stack.handoff(left, right) for left in stack.donors for right in stack.donors
    )


def _no_handoff(stack: DonorStack) -> frozenset[tuple[str, str]]:
    return frozenset()


def _only_self_handoffs(stack: DonorStack) -> frozenset[tuple[str, str]]:
    return frozenset(stack.handoff(donor, donor) for donor in stack.donors)


def _one_handoff(stack: DonorStack) -> frozenset[tuple[str, str]]:
    return frozenset({stack.handoff(stack.donors[0], stack.donors[-1])})


#: Bridge registries. The first two are the only ones P7's published result
#: contains, and both are uniform over the stack.
REGISTRIES: dict[str, Any] = {
    "every_handoff_registered": _every_handoff,
    "no_handoff_registered": _no_handoff,
    "only_self_handoffs_registered": _only_self_handoffs,
    "one_handoff_registered": _one_handoff,
}

SUCCESS_REGISTRY = "every_handoff_registered"
COUNTERMODEL_REGISTRY = "no_handoff_registered"


def handoff_is_matched(
    stack: DonorStack, registry: frozenset[tuple[str, str]], left: str, right: str
) -> bool:
    """P7's ``bridge_match``, computed from the two donors instead of typed.

    This is ``Match(Tgt t, Src u) := Tgt t = Src u \\/ Bridge(Tgt t, Src u)``,
    transcribed. Both disjuncts are here because both are in P7's own theorem
    statement, and the first is the one that makes the diagonal rows delicate: a
    reading in which a donor consumes what it produces satisfies it by
    reflexivity and cannot refuse a self-composition at all.

    ``research/failures/2026-08-supplied-premise-unbuilt-decision/`` records the
    committed model's version of this as a literal typed by the caller, with an
    open item asking for exactly this substitution. This is where it happens for
    the finite result: the value handed to the committed ``compose`` below is
    computed here, from the interpretation, and is not available to be supplied.
    """

    emitted, consumed = stack.handoff(left, right)
    return emitted == consumed or (emitted, consumed) in registry


def interpreted_stack(repo_root: Any, *, assignment: str = INTERPRETATION) -> DonorStack:
    """The donor stack of the committed model, read under one contract assignment."""

    from pathlib import Path

    model = load_executable_model(
        Path(repo_root) / EXECUTABLE_MODEL, f"p7_stack_{assignment}"
    )
    return CONTRACT_ASSIGNMENTS[assignment](tuple(model.DONORS))


# ---------------------------------------------------------------------------
# The published counts, recomputed through the committed implementation
# ---------------------------------------------------------------------------


def _refinement_multiplier(model: Any) -> dict[str, Any]:
    """Run the committed refinement loop at one donor and at five, and compare.

    This is context rather than subject: P7's 155 full refinements and 1,055
    proper-subset failures are a different half of the artifact from the
    composition rows, and they are recomputed under ``P7-U-T1``. What is measured
    here is only whether their donor axis is a multiplier, because the same
    question is being asked of the composition rows two functions down and a
    claim about one should not be an assertion about the other. The loop is
    P7's own, transcribed with the donor count as a parameter.
    """

    from itertools import combinations

    coordinates = len(model.COORDS)

    def counts(donor_count: int) -> tuple[int, int]:
        successes = 0
        failures = 0
        for _donor in range(donor_count):
            for size in range(1, coordinates + 1):
                for changed in combinations(range(coordinates), size):
                    damaged = [True] * coordinates
                    for position in changed:
                        damaged[position] = False
                    for repaired_size in range(len(changed)):
                        for repaired in combinations(changed, repaired_size):
                            partial = damaged[:]
                            for position in repaired:
                                partial[position] = True
                            if not model.carries(True, tuple(partial)):
                                failures += 1
                    if model.carries(True, (True,) * coordinates):
                        successes += 1
        return successes, failures

    one_success, one_failure = counts(1)
    all_success, all_failure = counts(len(model.DONORS))
    return {
        "full_refinement_successes_at_one_donor": one_success,
        "proper_subset_failures_at_one_donor": one_failure,
        "full_refinement_successes_at_the_committed_stack": all_success,
        "proper_subset_failures_at_the_committed_stack": all_failure,
        "the_donor_axis_is_a_multiplier": (
            all_success == one_success * len(model.DONORS)
            and all_failure == one_failure * len(model.DONORS)
        ),
        "reading": (
            f"{all_success} and {all_failure} are {one_success} and {one_failure} "
            f"counted {len(model.DONORS)} times: the donor loop enters neither the "
            "closure vector nor the repair set, so the five families replicate the "
            "single-donor result rather than extending it. Measured by running the "
            "committed carries at both donor counts, not inferred from the loop's "
            "shape."
        ),
    }


def recompute_published_counts(repo_root: Any) -> dict[str, Any]:
    """Recompute 25 and 25 by running the committed ``carries`` and ``compose``.

    Not by evaluating a rule defined here. The two functions are P7's own, from
    the file the superiority ledger names for ``P7-U-T1``; what this module
    supplies is the third argument, which the committed runner supplies as a
    literal and which is computed here from the interpretation.

    Everything else is P7's data. Both legs carry because the shipped result
    contains no composition row in which a leg fails --- that is not a choice made
    here, it is the whole content of the two argument triples the loop reaches,
    and it is why the recomputation below still reaches exactly those two.
    """

    from pathlib import Path

    model = load_executable_model(
        Path(repo_root) / EXECUTABLE_MODEL, "p7_closure_carrying_donor_stack"
    )
    donors = tuple(model.DONORS)
    stack = CONTRACT_ASSIGNMENTS[INTERPRETATION](donors)
    full = (True,) * len(model.COORDS)

    reached: set[tuple[bool, bool, bool]] = set()
    visited: set[tuple[str, str]] = set()

    def compose_pair(left: str, right: str, registry_name: str) -> bool:
        registry = REGISTRIES[registry_name](stack)
        first = model.carries(True, full)
        second = model.carries(True, full)
        bridged = handoff_is_matched(stack, registry, left, right)
        reached.add((bool(first), bool(second), bool(bridged)))
        visited.add(stack.handoff(left, right))
        return bool(model.compose(first, second, bridged))

    successes = 0
    countermodels = 0
    success_failures: list[str] = []
    countermodel_failures: list[str] = []
    for left in donors:
        for right in donors:
            if compose_pair(left, right, SUCCESS_REGISTRY):
                successes += 1
            elif len(success_failures) < 20:
                success_failures.append(
                    f"({left}, {right}) did not compose with its hand-off registered"
                )
            if not compose_pair(left, right, COUNTERMODEL_REGISTRY):
                countermodels += 1
            elif len(countermodel_failures) < 20:
                countermodel_failures.append(
                    f"({left}, {right}) composed with no bridge registered"
                )

    possible = [tuple(item) for item in product((False, True), repeat=COMPOSE_ARITY)]
    return {
        "donors": len(donors),
        "closure_coordinates": len(model.COORDS),
        "the_refinement_counts_are_a_separate_object": _refinement_multiplier(model),
        "composition_successes": successes,
        "composition_bridge_countermodels": countermodels,
        "published_composition_successes": PUBLISHED_COMPOSITION_SUCCESSES,
        "published_composition_bridge_countermodels": (
            PUBLISHED_COMPOSITION_BRIDGE_COUNTERMODELS
        ),
        "success_failures": success_failures,
        "countermodel_failures": countermodel_failures,
        "counts_reproduced": (
            successes == PUBLISHED_COMPOSITION_SUCCESSES
            and countermodels == PUBLISHED_COMPOSITION_BRIDGE_COUNTERMODELS
            and not success_failures
            and not countermodel_failures
        ),
        "distinct_handoffs_visited": len(visited),
        "argument_triples_reached": [
            list(item) for item in sorted(tuple(int(value) for value in item) for item in reached)
        ],
        "argument_triples_possible": len(possible),
        "computed_by": (
            "the committed check_p7_x2_closure_carrying.carries and .compose, with "
            "bridge_match computed from the interpretation rather than supplied"
        ),
        "what_the_donor_loop_now_does": (
            f"The loop visits {len(visited)} distinct hand-off contract pairs and the "
            "registry decides each one separately, so the donor pair is an input to the "
            "verdict rather than an unused loop variable. It is still the case that "
            f"only {len(reached)} of {len(possible)} argument triples are reached, and "
            "that is now a fact about the registries rather than about the loop: "
            "reproducing 25 successes needs every hand-off bridged and reproducing 25 "
            "countermodels needs none bridged, and both of P7's published registries are "
            "uniform over an all-carrying stack. The 25 rows are 25 distinct hand-offs; "
            "they are still 25 agreeing verdicts."
        ),
    }


def argument_space_under_the_interpretation(
    repo_root: Any, *, model: Any | None = None
) -> dict[str, Any]:
    """Exercise the six argument triples the shipped composition loop never reaches.

    Every ordered donor pair, against every closure vector and both native
    verdicts on each leg, against both values of the registry bit at that
    hand-off. The verdicts are the committed ``carries`` and ``compose``; the
    specification compared against is the rule
    ``INTERMEDIATE_CONTRACT_COMPOSITION`` proves --- a composite carries exactly
    when both legs carry and the hand-off matches --- so this is a differential
    between P7's implementation and P7's theorem over the whole input space
    rather than over the corner of it the artifact happens to contain.

    ``model`` is injectable so a caller can hand in a module it has perturbed.
    Loading a fresh instance unconditionally would make a mutation test silently
    measure a different object than the one it sabotaged.
    """

    from pathlib import Path

    if model is None:
        model = load_executable_model(
            Path(repo_root) / EXECUTABLE_MODEL, "p7_argument_space"
        )
    donors = tuple(model.DONORS)
    stack = CONTRACT_ASSIGNMENTS[INTERPRETATION](donors)
    vectors = [tuple(item) for item in product((False, True), repeat=len(model.COORDS))]

    reached: dict[tuple[bool, bool, bool], int] = {}
    disagreements: list[str] = []
    trials = 0
    positives = 0
    for left in donors:
        for right in donors:
            emitted, consumed = stack.handoff(left, right)
            for registered in (False, True):
                registry = frozenset({(emitted, consumed)}) if registered else frozenset()
                bridged = handoff_is_matched(stack, registry, left, right)
                for left_native, left_closure in product((False, True), vectors):
                    first = model.carries(left_native, left_closure)
                    for right_native, right_closure in product((False, True), vectors):
                        second = model.carries(right_native, right_closure)
                        actual = model.compose(first, second, bridged)
                        expected = bool(
                            left_native
                            and all(left_closure)
                            and right_native
                            and all(right_closure)
                            and bridged
                        )
                        trials += 1
                        if actual:
                            positives += 1
                        key = (bool(first), bool(second), bool(bridged))
                        reached[key] = reached.get(key, 0) + 1
                        if actual != expected and len(disagreements) < 20:
                            disagreements.append(
                                f"({left}, {right}) left={left_native}/{left_closure} "
                                f"right={right_native}/{right_closure} "
                                f"bridged={bridged}: compose={actual} theorem={expected}"
                            )

    differential = DifferentialReport(
        trials=trials,
        agreements=trials - len(disagreements),
        disagreements=tuple(disagreements),
        positive_trials=positives,
    )
    possible = [tuple(item) for item in product((False, True), repeat=COMPOSE_ARITY)]
    unreached = [item for item in possible if item not in reached]
    return {
        "differential": differential.as_json(),
        "argument_triples_possible": len(possible),
        "argument_triples_reached": len(reached),
        "evaluations_per_triple": {
            "".join(str(int(value)) for value in key): count
            for key, count in sorted(reached.items())
        },
        "unreached": [
            list(item) for item in sorted(tuple(int(value) for value in item) for item in unreached)
        ],
        "every_triple_reached": not unreached,
        "reading": (
            f"{trials} evaluations of the committed compose over "
            f"{len(reached)} of {len(possible)} argument triples, against the rule the "
            "calculus proves. The shipped result reaches two of these triples; the six "
            "it does not are the ones where a leg fails to carry, and they are covered "
            "by A_LEFT_LEG_THAT_DOES_NOT_CARRY_REFUSES and "
            "A_RIGHT_LEG_THAT_DOES_NOT_CARRY_REFUSES at arbitrary width. The corpus is "
            f"heavily skewed: {positives} of {trials} rows compose successfully, one "
            "per ordered donor pair, because a leg carries only at the single "
            "all-holding closure vector. Both verdicts occur, which is what the "
            "differential needs, but the per-triple counts are reported rather than "
            "summarised so the skew is visible. This enumeration is not part of P7's "
            "published result and does not become part of it by being run here."
        ),
    }


def counts_are_sensitive_to_the_interpretation(repo_root: Any) -> dict[str, Any]:
    """Do the published counts identify the interpretation? Only partly.

    Six contract assignments are run against four bridge registries, and both
    published counts are recomputed in each cell through the committed functions.
    Two results come out and they point in opposite directions.

    **The countermodel count is exactly the first frame condition.** 25 bridge
    countermodels under an empty registry says no hand-off matches by contract
    equality, which is ``handoffs_are_never_contract_identities`` word for word.
    Every assignment violating it --- one shared contract, endomorphic donors, a
    chained pipeline --- returns 0, 20 and 21 instead. So that condition is not
    something this module chose; it is what P7's own published number asserts.

    **The counts cannot see the second frame condition at all.** Reading every
    family as consuming one shared input contract and emitting one shared output
    contract reproduces 25 and 25 exactly, and so does reading them as emitting
    one shared output contract. Those are the readings in which the 5x5 loop
    visits 1 and 5 distinct hand-offs --- precisely the multiplier this terminal
    exists to remove --- and both are invisible to the published pair. What
    separates them is measured directly here as the number of distinct hand-offs
    visited, and proved as :data:`THE_HANDOFF_IDENTIFIES_THE_DONOR_PAIR`, which
    is the theorem dropping that condition loses.

    **The success count discriminates nothing about the contracts.** Every
    assignment returns 25 under a registry that bridges everything, because a
    full registry makes the hand-off test true whatever the contracts are. It
    moves only under non-uniform registries, and P7's published result contains
    no non-uniform registry.
    """

    from pathlib import Path

    model = load_executable_model(
        Path(repo_root) / EXECUTABLE_MODEL, "p7_closure_carrying_sensitivity"
    )
    donors = tuple(model.DONORS)
    full = (True,) * len(model.COORDS)
    carrying = model.carries(True, full)

    outcomes: dict[str, dict[str, Any]] = {}
    for name, build in CONTRACT_ASSIGNMENTS.items():
        stack = build(donors)
        cells: dict[str, int] = {}
        for registry_name, registry_of in REGISTRIES.items():
            registry = registry_of(stack)
            cells[registry_name] = sum(
                1
                for left in donors
                for right in donors
                if model.compose(
                    carrying, carrying, handoff_is_matched(stack, registry, left, right)
                )
            )
        outcomes[name] = {
            "distinct_handoffs_visited": stack.distinct_handoffs(),
            "composites_that_carry_by_registry": cells,
            "composition_successes": cells[SUCCESS_REGISTRY],
            "composition_bridge_countermodels": (
                len(donors) * len(donors) - cells[COUNTERMODEL_REGISTRY]
            ),
        }

    reproduces = sorted(
        name
        for name, cell in outcomes.items()
        if cell["composition_successes"] == PUBLISHED_COMPOSITION_SUCCESSES
        and cell["composition_bridge_countermodels"]
        == PUBLISHED_COMPOSITION_BRIDGE_COUNTERMODELS
    )
    indistinguishable = [name for name in reproduces if name != INTERPRETATION]
    caught = sorted(
        name
        for name in indistinguishable
        if outcomes[name]["distinct_handoffs_visited"]
        != outcomes[INTERPRETATION]["distinct_handoffs_visited"]
    )
    moved = sorted(name for name in outcomes if name not in reproduces)
    registry_moves = sorted(
        registry_name
        for registry_name, count in outcomes[INTERPRETATION][
            "composites_that_carry_by_registry"
        ].items()
        if count != PUBLISHED_COMPOSITION_SUCCESSES
    )
    # Which registry, had P7 shipped one, would have told the interpretation from
    # the readings its counts cannot distinguish. Reported because "the artifact
    # does not contain the discriminating measurement" is a more useful finding
    # than "the artifact's measurements do not discriminate".
    separating_registries = sorted(
        registry_name
        for registry_name in REGISTRIES
        if all(
            outcomes[name]["composites_that_carry_by_registry"][registry_name]
            != outcomes[INTERPRETATION]["composites_that_carry_by_registry"][registry_name]
            for name in indistinguishable
        )
        and indistinguishable
    )
    return {
        "variants": outcomes,
        "wrong_assignments_that_move_a_published_count": moved,
        "wrong_assignments_the_counts_cannot_distinguish": sorted(indistinguishable),
        "of_those_caught_by_the_distinct_handoff_count": caught,
        "counts_alone_identify_the_interpretation": not indistinguishable,
        "every_indistinguishable_assignment_is_caught_by_a_theorem": (
            sorted(indistinguishable) == caught
        ),
        "registries_that_move_the_success_count": registry_moves,
        "registries_that_would_separate_the_indistinguishable_assignments": (
            separating_registries
        ),
        "what_the_countermodel_count_tests": (
            "Exactly the first frame condition and nothing more. 25 countermodels under "
            "an empty registry is the statement that no donor's target contract is any "
            "donor's source contract; one shared contract returns 0, endomorphic donors "
            "return 20 and a chained pipeline returns 21. P7's published number and the "
            "frame condition are the same assertion, which is why the condition is not a "
            "choice this module made."
        ),
        "what_the_success_count_tests": (
            "Nothing about the contracts. Every assignment tried returns 25 under a "
            "registry that bridges every hand-off, because a full registry satisfies the "
            "match test whatever the contracts are. What it tests is the registry: it "
            f"moves under every other registry tried -- {', '.join(registry_moves)} -- "
            "so 25 successes is the statement that the registry bridges all 25 hand-offs "
            "and says nothing about which hand-offs those are."
        ),
        "what_pins_the_donor_indexing": (
            "The theorem, not the counts. Two readings in which the 5x5 loop visits 1 "
            "and 5 distinct hand-offs reproduce both published counts exactly, so the "
            "counts do not establish that the donor axis indexes anything. "
            "THE_HANDOFF_IDENTIFIES_THE_DONOR_PAIR does, it is the theorem lost by "
            "dropping distinct_donors_have_distinct_endpoints, and the distinct hand-off "
            "count is reported per assignment above so this is a measurement rather than "
            "an argument. What would have settled it empirically is a registry that "
            "bridges some hand-offs and not others: "
            f"{', '.join(separating_registries) or 'none of those tried'} separates the "
            "interpretation from both impostors. P7 shipped neither."
        ),
    }


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------


def build_report(repo_root: Any, *, date: str) -> dict[str, Any]:
    """Everything this module establishes, with what it does not."""

    import z3 as _z3

    theorems = prove_all()
    counts = recompute_published_counts(repo_root)
    frames = frame_conditions_are_load_bearing()
    space = argument_space_under_the_interpretation(repo_root)
    sensitivity = counts_are_sensitive_to_the_interpretation(repo_root)
    undischarged = [r.theorem.name for r in theorems if not r.discharged]

    return {
        "schema_version": SCHEMA_VERSION,
        "record": "P7_DONOR_STACK_AS_TRANSFORMATION_FAMILY",
        "date": date,
        "solver": _z3.get_version_string(),
        "executable_model": EXECUTABLE_MODEL,
        "committed_result": COMMITTED_RESULT,
        "theorems": [r.as_json() for r in theorems],
        "all_discharged": not undischarged,
        "undischarged": undischarged,
        "frame_conditions": frames,
        "published_counts": counts,
        "argument_space": space,
        "interpretation_sensitivity": sensitivity,
        "what_this_establishes": (
            "P7's five donor families are interpreted as a transformation family in the "
            "calculus P7-U-T1 proved: each family is a transformation with its own "
            "source and target obligation contracts, and the bridge_match the committed "
            "runner types as a literal becomes Match(Tgt t, Src u), computed from the "
            "two transformations and the registered bridge relation. Under three frame "
            "conditions -- hand-offs are never contract identities, distinct families "
            "have distinct endpoints, the stack is inhabited -- twelve theorems are "
            "discharged by Z3 over uninterpreted transformation, contract, coordinate "
            "and obligation sorts, for a donor stack of any size: a bridged hand-off "
            "composes, an unbridged one refuses, a donor composed with itself still "
            "needs a bridge, either leg failing refuses, the hand-off identifies the "
            "donor pair, distinct hand-offs can differ in verdict, both halves are "
            "non-vacuous on an inhabited stack, and a three-donor chain needs every "
            "interior bridge. Two further conditions were written as axioms first, came "
            "back inert, and are discharged as theorems instead -- and adding them back "
            "is re-measured on every run, so that they make nothing newly provable is a "
            "result rather than a memory. P7's published 25 "
            "composition successes and 25 bridge countermodels are then recomputed by "
            "running the committed carries and compose with the hand-off computed rather "
            "than supplied, so the counts are output of the shipped implementation under "
            "the interpretation. The six argument triples the shipped loop never reaches "
            "are covered by theorem and exercised on the committed functions over "
            f"{space['differential']['trials']} evaluations spanning all eight triples. "
            "Three limits are measured rather than implied. The countermodel count is "
            "exactly the first frame condition, so that condition is P7's own assertion "
            "and not this module's choice. The success count discriminates nothing about "
            "the contracts: every assignment tried returns 25 under a full registry. And "
            "the counts cannot see the second frame condition at all -- two readings in "
            "which the 5x5 loop visits one and five distinct hand-offs reproduce both "
            "published numbers -- so what establishes that the donor axis indexes "
            "anything is THE_HANDOFF_IDENTIFIES_THE_DONOR_PAIR and the measured "
            "hand-off count, not the published pair."
        ),
        "not_licensed": [
            "any claim that the published counts reach more than two of compose's eight "
            "argument triples; reproducing 25 and 25 requires two uniform registries "
            "over an all-carrying stack, so the recomputation reaches exactly the two "
            "the shipped runner reaches. The other six are exercised here and are not "
            "part of P7's published result",
            "any claim that 25 successes tests the interpretation; every contract "
            "assignment tried returns 25 under a registry that bridges everything",
            "any claim that the published counts establish that the five families are "
            "distinct transformations; two readings collapsing the stack to one and to "
            "five distinct hand-offs reproduce both counts, and only the theorem "
            "separates them",
            "any claim that P7's other two donor-looped counts are what their size "
            "suggests; measured here by running the committed carries at one donor and "
            "at five, the 155 full refinements and 1,055 proper-subset failures are 31 "
            "and 211 replicated by a loop that enters neither the closure vector nor "
            "the repair set. That half of the artifact is P7-U-T1's and is context here",
            "any claim that this repairs the committed artifact; "
            f"{COMMITTED_RESULT} still records counts produced by a loop whose third "
            "argument is a literal, and no count in it moved. A later repair gave that "
            "file a donor-conservativity check that can fail and a donor_axis block "
            "carrying each count's multiplicity; the composition literal this record is "
            "about is untouched by it",
            "independent review: the interpretation, the theorems and the tests were "
            "written in the same lane as the model, which is P7-U-T5",
            "any empirical claim whatsoever; nothing here is measured on a pipeline",
        ],
    }


def main(argv: list[str]) -> int:
    """CLI entry point. ``argv`` is required: there is no implicit run."""

    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="orion-p7-donor-stack-as-transformation-family",
        description=(
            "Interpret P7's donor stack as a transformation family in the proved "
            "composition calculus."
        ),
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--date", required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    report = build_report(args.repo_root, date=args.date)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"written: {args.output}")

    for item in report["theorems"]:
        print(f"  {item['outcome']:15s} {item['name']}")
    counts = report["published_counts"]
    print(
        f"  counts: {counts['composition_successes']} successes, "
        f"{counts['composition_bridge_countermodels']} bridge countermodels, "
        f"reproduced={counts['counts_reproduced']}, "
        f"{counts['distinct_handoffs_visited']} distinct hand-offs, "
        f"{len(counts['argument_triples_reached'])} of "
        f"{counts['argument_triples_possible']} argument triples"
    )
    space = report["argument_space"]
    print(
        f"  argument space: {space['argument_triples_reached']} of "
        f"{space['argument_triples_possible']} triples over "
        f"{space['differential']['trials']} evaluations, "
        f"informative={space['differential']['informative']}"
    )
    frames = report["frame_conditions"]
    print(
        "  every frame condition carries a theorem: "
        f"{frames['every_condition_carries_a_theorem']}"
    )
    sens = report["interpretation_sensitivity"]
    print(
        "  counts alone identify the interpretation: "
        f"{sens['counts_alone_identify_the_interpretation']}; "
        "every indistinguishable assignment is caught by a theorem: "
        f"{sens['every_indistinguishable_assignment_is_caught_by_a_theorem']}"
    )

    # 2 = a finding, 3 = could not check, as scripts/audit_manuscript_clipping.py
    # already uses them. The distinction below between "inert" and "left
    # undecided" was already drawn in prose by whoever wrote those two messages;
    # it just could not reach the exit code while everything returned 3.
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
    if not counts["counts_reproduced"]:
        print("THE PUBLISHED COUNTS WERE NOT REPRODUCED UNDER THE INTERPRETATION")
        return 2
    if frames["inert_conditions"]:
        print(f"INERT FRAME CONDITIONS: {frames['inert_conditions']}")
        return 2
    if frames["conditions_left_undecided"]:
        # A different sentence from the one above, and it must stay different:
        # the countermodel search did not settle, so whether these carry a
        # theorem was not measured on this run.
        print(
            "FRAME CONDITIONS LEFT UNDECIDED (the countermodel search did not settle; "
            f"this is not a finding that they are inert): {frames['conditions_left_undecided']}"
        )
        return 3
    if not space["every_triple_reached"]:
        print(f"ARGUMENT TRIPLES STILL UNREACHED: {space['unreached']}")
        return 2
    if space["differential"]["disagreements"]:
        print("THE COMMITTED COMPOSE DISAGREES WITH THE PROVED RULE")
        return 2
    if not sens["every_indistinguishable_assignment_is_caught_by_a_theorem"]:
        print("A WRONG CONTRACT ASSIGNMENT ESCAPED BOTH THE COUNTS AND THE THEOREMS")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
