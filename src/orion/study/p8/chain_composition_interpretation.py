"""P8's heterogeneous chain compositions, interpreted in the proved calculus.

``P8-U-T2`` asks whether P8's exhaustive finite result follows *as an instance*
of the general theorem. :mod:`orion.study.p8.donor_interpretation` answered that
for the 3,072-state X4 model. It did not answer it for the other object X4
publishes: the ``heterogeneous_chain_successes`` and
``heterogeneous_chain_widening_countermodels`` counts, 169 each, which the
ledger's blocker named as the remaining gap --- *"deriving them needs the chain
theorem instantiated at the donor level, which the calculus proves in general and
this interpretation does not yet map."*

This is that instantiation. It interprets P8's chain composition model into the
signature :mod:`orion.study.p8.authority_calculus_smt` proves theorems about, and
then

1. discharges seven theorems by Z3 over uninterpreted ``Domain``, ``Obj``,
   ``Issuer`` and ``Donor`` sorts --- so at arbitrary donor count, not thirteen
   --- plus the chain confinement statement fully expanded at every length up to
   :data:`CHAIN_LADDER_BOUND`; and
2. recomputes both 169s by composing two donor judgments through the
   interpretation and handing the composed state to the *committed*
   ``scientific_terminal``, rather than by evaluating a rule of this module's
   own.

The interpretation
------------------
A donor family is an element of an uninterpreted ``Donor`` sort. Its judgment
carries a domain, a scope, an epoch and an issuer; ``TypeAgree``, ``Coerce`` and
``Narrows`` are relations between two donors, standing for X4's five
type-coordinate flags, its ``protected_coercion`` and its ``narrowing_ok`` at one
hop. The load-bearing assignment is::

    a donor's *domain* is its scientific type profile

so ``TypeAgree(p, q)`` holds exactly when ``Dom(p) = Dom(q)``. That is stated as
two frame condition axioms, one per direction, and both are shown below to carry
theorems. It is what makes X4's ``all(flags) or protected_coercion`` the
calculus's ``Reach``: authority arrives in a domain either because it is already
that domain, or along a conversion someone registered.

An X4 chain hop ``p -> q`` is then exactly the calculus's ``delegates``, and that
is :data:`LINK_IS_A_DELEGATION` rather than an assertion.

What the 169 turns out to be
----------------------------
Three findings, each computed rather than argued, and none of them flattering.

**The shipped 169 is one evaluation counted 169 times.** ``check_p8_x4_authority_
lifting.py`` writes its chain claim as ``for _left in DONORS: for _right in
DONORS:`` with a loop body that mentions neither variable --- it asserts
``scientific_terminal(True, full, True, "REFUTED", True, False, False) ==
"DISCHARGE"`` and increments. Composed through this interpretation the 169
ordered pairs produce **one** distinct composed state, and that number is
reported by :func:`recompute_published_counts` as ``distinct_composed_states``.

**The heterogeneous chain is exercised only where it is homogeneous.** The
shipped state passes all five type flags true at every hop, which by the frame
conditions means both donors occupy the *same* domain, so the hop is discharged
by reflexivity of ``Reach`` and no conversion is ever consulted. That is
:data:`SHIPPED_STEP_IS_REFLEXIVE`. Read the thirteen families as type-distinct
instead --- a cross-family hop crosses a type boundary unless a protected bridge
is registered --- and the same committed rule returns **13**, not 169.

**Neither published count discriminates the interpretation.** All eight wrong
composition operators tried in :func:`counts_are_sensitive_to_the_interpretation`
reproduce 169 successes; six of the eight also reproduce 169 widening
countermodels. What does discriminate is the exhaustive identity
``compose(L, R) discharges  <->  L discharges and R discharges``, checked through
the committed rule on 36,864 representative pairs that
:func:`state_space_reduction_is_exact` shows stand in for all 9,437,184 pairs of
X4 states: it is exact on the baseline and broken by all eight variants.

What this does not establish
----------------------------
The interpretation is a map this lane wrote. Two things are done about that
rather than promised: every frame condition is stated as an explicit axiom and
each is shown load-bearing by exhibiting a countermodel to a theorem it carries,
and the counts come from the committed checker rather than from a rule defined
here. No evaluator outside this lane has checked any of it, which is
``P8-U-T5``.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from typing import Any, Callable

from orion.programme.mechanized import (
    ProofOutcome,
    ProofResult,
    Theorem,
    discharge,
    load_executable_model,
    require_z3,
)
from orion.study.p8.authority_calculus_smt import (
    Signature,
    authorize,
    closure_axioms,
    signature,
)

SCHEMA_VERSION = "orion.p8.chain-composition-interpretation.v1"

#: P8's shipped X4 checker. The chain counts this module derives are two of its
#: emitted fields, and the terminal function it computes them with is the one
#: called here.
X4_CHECKER = "research/claim_expansion/p8/check_p8_x4_authority_lifting.py"

#: The two counts under derivation, as the shipped checker publishes them.
PUBLISHED_CHAIN_SUCCESSES = 169
PUBLISHED_CHAIN_WIDENING_COUNTERMODELS = 169

#: How far the donor-level chain statement is expanded explicitly. The general
#: result rests on the one-step lemma plus induction on chain length, and the
#: induction schema is the single hand step, inherited from
#: :mod:`orion.study.p8.authority_calculus_smt`. The ladder corroborates it at
#: concrete lengths; no finite ladder replaces it.
#:
#: Six, and the number was measured rather than chosen. Lengths one through six
#: discharge in under three seconds across repeated runs. Beyond that the solver
#: becomes unreliable rather than slow: over three runs at a sixty-second
#: timeout, length seven took 3.8s, 9.2s and 13.7s; length eight took 0.9s, 6.0s
#: and 26.0s; length nine and above returned ``unknown`` on some runs and proved
#: in seconds on others. The bound was 8 until a length-eight query timed out
#: inside a loaded test run and the report correctly refused to call it proved.
#: A ladder rung that is sometimes ``unknown`` is not corroboration, it is a
#: coin toss reported as evidence, so the bound sits where the ladder is
#: reliable and this comment records what was tried past it.
CHAIN_LADDER_BOUND = 6

#: What was observed above :data:`CHAIN_LADDER_BOUND`, kept in the artifact so
#: the bound is a measured limit and not a silent one.
LADDER_BEYOND_THE_BOUND = (
    "lengths 7 to 12 were expanded and discharged three times each at a sixty-second "
    "timeout: 7 and 8 proved every time but took up to 13.7s and 26.0s, and 9, 10, 11 "
    "and 12 each returned unknown on at least one run. Nothing about the theorem "
    "changes at length nine -- the induction schema is what carries every length -- so "
    "the variance is the solver's and the bound is set where the ladder is a reliable "
    "corroboration rather than an intermittent one."
)

#: How long a proof may take before the solver is told to give up.
#:
#: Two minutes, and none of these proofs needs it: measured eight times in
#: isolation, every theorem here discharges in under two tenths of a second, and
#: the slowest ladder rung in under three. The budget is large because the
#: timeout is wall-clock, and on a loaded machine a two-tenths-of-a-second proof
#: came back ``unknown`` once inside a test run and the report correctly refused
#: to call it discharged. A generous budget costs nothing when a proof succeeds
#: and is the difference between a result and a coin toss when the machine is
#: busy.
PROOF_TIMEOUT_MS = 120000

#: How long a *refutation* search may take. Deliberately much shorter: a drop run
#: that exceeds it has not found a countermodel, which is the honest answer and
#: is recorded as ``UNKNOWN`` rather than as a theorem lost.
REFUTATION_TIMEOUT_MS = 20000

#: X4's blocker states, ordered by severity. Composing a chain takes the worst
#: blocker on it, which is the only order under which a chain is as blocked as
#: its most blocked link.
BLOCKER_SEVERITY: dict[str, int] = {"REFUTED": 0, "UNDETERMINED": 1, "ESTABLISHED": 2}

#: X4's four terminals.
DISCHARGE = "DISCHARGE"
BLOCK = "BLOCK"

__all__ = [
    "BLOCKER_SEVERITY",
    "CHAIN_LADDER_BOUND",
    "FRAME_CONDITION_IDS",
    "FRAME_CONDITION_REFUTATION_ORDER",
    "LADDER_BEYOND_THE_BOUND",
    "PROOF_TIMEOUT_MS",
    "PUBLISHED_CHAIN_SUCCESSES",
    "PUBLISHED_CHAIN_WIDENING_COUNTERMODELS",
    "REFUTATION_TIMEOUT_MS",
    "SCHEMA_VERSION",
    "THEOREMS",
    "X4_CHECKER",
    "build_report",
    "canonical_states",
    "compose",
    "counts_are_sensitive_to_the_interpretation",
    "frame_conditions_are_load_bearing",
    "main",
    "prove_all",
    "prove_chain_ladder",
    "recompute_published_counts",
]


# ---------------------------------------------------------------------------
# The theorems
# ---------------------------------------------------------------------------

LINK_IS_A_DELEGATION = Theorem(
    name="A_DONOR_LINK_IS_A_CALCULUS_DELEGATION",
    statement=(
        "the five conditions P8's chain interface puts on one hop -- the donor-native "
        "verdict passes, authority narrows, the scientific type matches or a protected "
        "coercion is registered, the blocker is refuted and a support family survives -- "
        "entail every conjunct of the calculus's delegation hypothesis: valid, trusted, "
        "scope contained, domain reachable, epoch carried"
    ),
    why_it_matters=(
        "This is the bridge the whole derivation crosses. Without it the chain theorem "
        "is a theorem about the calculus's delegation relation and P8's chain claim is a "
        "statement about seven booleans, and the two never meet."
    ),
)

CHAIN_CONFINES_TO_THE_ROOT = Theorem(
    name="A_CHAIN_HOP_CONFINES_THE_ACTION_TO_THE_ROOT",
    statement=(
        "if donor p's judgment delegates to donor q's and q's authorises an action, then "
        "the action's scope is inside p's scope, its domain is reachable from p's, and it "
        "carries p's epoch. Proved over an uninterpreted donor sort, so it holds for any "
        "number of donor families -- thirteen is an instance"
    ),
    why_it_matters=(
        "The general form of P8's T7, 'every ordered pair among the thirteen donor "
        "families composes scientifically'. Quantified over the sort, the pair count "
        "carries no information: 169 is 13 squared and the theorem never mentions 13."
    ),
)

WIDENING_HOP_IS_NEVER_AUTHORISED = Theorem(
    name="A_WIDENING_HOP_IS_NEVER_AUTHORISED",
    statement=(
        "if a hop does not narrow -- the downstream scope is not contained in the "
        "upstream one -- the calculus's rule refuses it, whatever the donor-native "
        "verdicts, the blocker, the support families or the registered coercions say"
    ),
    why_it_matters=(
        "The general form of P8's 169 widening countermodels, and of T7's second "
        "sentence: the widening pair fails 'while both local donor verdicts remain "
        "intact'. It holds at every hop of a chain of any length because p and q here "
        "are arbitrary donors, which is why the widening result needs no ladder."
    ),
)

UNBRIDGED_GAP_IS_NOT_A_REACH = Theorem(
    name="AN_UNBRIDGED_TYPE_GAP_IS_NOT_A_REACH",
    statement=(
        "with no protected coercion registered anywhere, one donor's domain is reachable "
        "from another's only when their scientific types agree -- so an unregistered "
        "similarity, however strong, moves no authority across a type gap"
    ),
    why_it_matters=(
        "P8's T4. It is the theorem that needs the well-founded rank clause in the "
        "calculus's closure axioms: without the rank, spurious reachability facts can "
        "justify each other in a cycle and an unbridged gap becomes reachable."
    ),
)

SHIPPED_STEP_IS_REFLEXIVE = Theorem(
    name="THE_SHIPPED_CHAIN_STEP_IS_THE_REFLEXIVE_ONE",
    statement=(
        "when the five type coordinates agree the two donors occupy one domain, so the "
        "hop is a reach by reflexivity and holds even with no conversion registered "
        "anywhere in the calculus"
    ),
    why_it_matters=(
        "This is the negative, stated as a theorem rather than as a caveat. P8's chain "
        "claim passes all five flags true and no coercion, so by this theorem it "
        "exercises only the identity step of Reach. Whatever the 169 measures, it is not "
        "cross-domain composition."
    ),
)

DONOR_ENTERS_ONLY_THROUGH_ITS_TYPE = Theorem(
    name="THE_DONOR_FAMILY_ENTERS_ONLY_THROUGH_ITS_TYPE",
    statement=(
        "two donors agreeing on scientific type, scope, epoch, issuer, native validity, "
        "blocker, support and registered coercions compose identically with any third: "
        "the family label is not a coordinate of the calculus"
    ),
    why_it_matters=(
        "The theorem behind the arithmetic. If donor identity cannot change a "
        "composition, then thirteen families presenting one profile give one composition "
        "counted 169 times, and reporting 169 as breadth reports a replication factor as "
        "a dimension."
    ),
)

THREE_STATE_BLOCKER_LAW = Theorem(
    name="THE_THREE_STATE_BLOCKER_LAW",
    statement=(
        "a refuted blocker with a surviving support family satisfies the hard obligations "
        "and activates no defeater, and an established blocker activates one -- the "
        "obligation and the defeater are the two halves of X4's blocker"
    ),
    why_it_matters=(
        "P8's T5. The 'no defeater' half is the one that needs the blocker to be in "
        "exactly one of its three states; without that condition a judgment could be "
        "refuted and established at once, and a chain could compose through a defeated "
        "link."
    ),
)

THEOREMS: tuple[Theorem, ...] = (
    LINK_IS_A_DELEGATION,
    CHAIN_CONFINES_TO_THE_ROOT,
    WIDENING_HOP_IS_NEVER_AUTHORISED,
    UNBRIDGED_GAP_IS_NOT_A_REACH,
    SHIPPED_STEP_IS_REFLEXIVE,
    DONOR_ENTERS_ONLY_THROUGH_ITS_TYPE,
    THREE_STATE_BLOCKER_LAW,
)


# ---------------------------------------------------------------------------
# The interpretation, as frame conditions on the calculus signature
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ChainSignature:
    """The donor vocabulary, layered over the calculus's own signature.

    ``Donor`` is an uninterpreted sort for the same reason ``Domain`` is in the
    calculus: nothing here knows that P8 registers thirteen families, so a
    theorem discharged over it is not a theorem about thirteen.
    """

    base: Signature
    Donor: Any
    Dom: Any
    Sc: Any
    Ep: Any
    Iss: Any
    Native: Any
    TypeAgree: Any
    Coerce: Any
    Narrows: Any
    Refuted: Any
    Established: Any
    SupportA: Any
    SupportB: Any


def chain_signature() -> ChainSignature:
    """Build the donor vocabulary over a fresh calculus signature."""

    solver = require_z3()
    base = signature()
    Donor = solver.DeclareSort("Donor")
    boolean = solver.BoolSort()
    return ChainSignature(
        base=base,
        Donor=Donor,
        Dom=solver.Function("Dom", Donor, base.Domain),
        Sc=solver.Function("Sc", Donor, base.Scope),
        Ep=solver.Function("Ep", Donor, solver.IntSort()),
        Iss=solver.Function("Iss", Donor, base.Issuer),
        Native=solver.Function("Native", Donor, boolean),
        TypeAgree=solver.Function("TypeAgree", Donor, Donor, boolean),
        Coerce=solver.Function("Coerce", Donor, Donor, boolean),
        Narrows=solver.Function("Narrows", Donor, Donor, boolean),
        Refuted=solver.Function("Refuted", Donor, boolean),
        Established=solver.Function("Established", Donor, boolean),
        SupportA=solver.Function("SupportA", Donor, boolean),
        SupportB=solver.Function("SupportB", Donor, boolean),
    )


#: The interpretation's frame conditions, each independently droppable.
#:
#: Eight, and every one of them carries a theorem --- see
#: :func:`frame_conditions_are_load_bearing`. That was not true of the first
#: draft. ``every_donor_family_is_a_trusted_issuer`` came back inert, and the
#: reason was worth keeping: the link predicate carried ``Trusted`` inside its
#: own hypothesis, so the theorem concluding ``Trusted`` concluded one of its
#: premises and no axiom was needed. X4's hop conditions do not mention trust, so
#: the fix was to take it out of the link and let the frame condition supply it,
#: which is also the more honest reading --- P8's model does not model trust, and
#: this says where the assumption enters.
FRAME_CONDITION_IDS: tuple[str, ...] = (
    "type_agreement_is_domain_identity",
    "distinct_domains_are_type_disagreement",
    "a_protected_coercion_is_a_registered_conversion",
    "every_conversion_is_a_registered_coercion",
    "narrowing_is_scope_containment",
    "a_widening_hop_does_not_narrow",
    "the_blocker_takes_one_of_three_states",
    "every_donor_family_is_a_trusted_issuer",
)

#: Countermodel searches share a Z3 process. The trusted-issuer drop is the
#: expensive one and became UNKNOWN when it ran after the other seven on a
#: loaded hosted runner, while the same finite witness is found immediately in
#: a fresh process. Search it first, but continue to report results in the
#: canonical :data:`FRAME_CONDITION_IDS` order below.
FRAME_CONDITION_REFUTATION_ORDER: tuple[str, ...] = (
    "every_donor_family_is_a_trusted_issuer",
    *(
        condition
        for condition in FRAME_CONDITION_IDS
        if condition != "every_donor_family_is_a_trusted_issuer"
    ),
)


def _frame_conditions(sig: ChainSignature, *, drop: str | None = None) -> list[Any]:
    """The interpretation, written as axioms rather than as an encoding.

    ``drop`` omits one named condition, which is how each is shown to be
    load-bearing. A frame condition no theorem needs is decoration, and proofs
    that survive dropping every condition were never about the interpretation.
    """

    if drop is not None and drop not in FRAME_CONDITION_IDS:
        raise ValueError(f"unknown frame condition {drop!r}")

    solver = require_z3()
    base = sig.base
    p, q = solver.Consts("fc_p fc_q", sig.Donor)
    a, b = solver.Consts("fc_a fc_b", base.Domain)

    axioms: dict[str, Any] = {
        # A donor's domain is its scientific type profile. Stated in two
        # directions because they are two commitments: the first says agreeing
        # types put two donors in one domain, the second says nothing else does.
        "type_agreement_is_domain_identity": solver.ForAll(
            [p, q], solver.Implies(sig.TypeAgree(p, q), sig.Dom(p) == sig.Dom(q))
        ),
        "distinct_domains_are_type_disagreement": solver.ForAll(
            [p, q], solver.Implies(sig.Dom(p) == sig.Dom(q), sig.TypeAgree(p, q))
        ),
        # X4's protected coercion is the calculus's registered conversion, and
        # -- the closure half -- nothing else is.
        "a_protected_coercion_is_a_registered_conversion": solver.ForAll(
            [p, q],
            solver.Implies(sig.Coerce(p, q), base.Conv(sig.Dom(p), sig.Dom(q))),
        ),
        "every_conversion_is_a_registered_coercion": solver.ForAll(
            [a, b],
            solver.Implies(
                base.Conv(a, b),
                solver.Exists(
                    [p, q],
                    solver.And(a == sig.Dom(p), b == sig.Dom(q), sig.Coerce(p, q)),
                ),
            ),
        ),
        # X4's narrowing_ok is scope containment, in both directions. Split for
        # the same reason: the forward half is what a composing chain uses, the
        # backward half is what makes a widening hop a real failure rather than
        # an unmodelled one.
        "narrowing_is_scope_containment": solver.ForAll(
            [p, q],
            solver.Implies(sig.Narrows(p, q), solver.IsSubset(sig.Sc(q), sig.Sc(p))),
        ),
        "a_widening_hop_does_not_narrow": solver.ForAll(
            [p, q],
            solver.Implies(solver.IsSubset(sig.Sc(q), sig.Sc(p)), sig.Narrows(p, q)),
        ),
        # The blocker is three-valued; REFUTED and ESTABLISHED are exclusive and
        # UNDETERMINED is neither.
        "the_blocker_takes_one_of_three_states": solver.ForAll(
            [p], solver.Not(solver.And(sig.Refuted(p), sig.Established(p)))
        ),
        # X4 does not model issuer trust. Declared here rather than invented as
        # an eighth argument, and droppable so the declaration can be measured.
        "every_donor_family_is_a_trusted_issuer": solver.ForAll(
            [p], base.Trusted(sig.Iss(p))
        ),
    }
    return [clause for name, clause in axioms.items() if name != drop]


def _obligations(sig: ChainSignature, donor: Any) -> Any:
    """X4's hard obligations: the blocker is refuted and some support survives."""

    solver = require_z3()
    return solver.And(
        sig.Refuted(donor), solver.Or(sig.SupportA(donor), sig.SupportB(donor))
    )


def _defeater(sig: ChainSignature, donor: Any) -> Any:
    """X4's defeater: an established blocker."""

    return sig.Established(donor)


def _link(sig: ChainSignature, upstream: Any, downstream: Any) -> Any:
    """One hop of P8's chain, as its own interface states it.

    Exactly the five conditions in ``P8_X4_AUTHORITY_LIFTING_THEOREMS_V1.md``:
    the donor-native verdict passes, the scientific type matches directly or a
    protected coercion is registered, authority narrows, the blocker is refuted
    (and not established), and at least one support family survives. Trust is
    deliberately *not* here --- X4 has no argument for it, and putting it in the
    hypothesis is what made the trust frame condition inert in the first draft.
    """

    solver = require_z3()
    return solver.And(
        sig.Native(upstream),
        sig.Narrows(upstream, downstream),
        solver.Or(
            sig.TypeAgree(upstream, downstream), sig.Coerce(upstream, downstream)
        ),
        sig.Ep(downstream) == sig.Ep(upstream),
        _obligations(sig, upstream),
        solver.Not(_defeater(sig, upstream)),
    )


def _witness_world(sig: ChainSignature) -> list[Any]:
    """Finite bounds that make a countermodel findable, used only when refuting.

    Not part of the interpretation and never added to a proof. A model of the
    axioms together with these bounds and the negation of a claim *is* a
    countermodel to that claim under the axioms alone, so bounding the sorts is
    sound for refutation and unsound for proof --- which is why
    :func:`prove_all` never sees it and
    :func:`frame_conditions_are_load_bearing` reads only ``COUNTEREXAMPLE``
    outcomes from the runs that do.

    It exists because it is needed. Without it, dropping
    ``every_donor_family_is_a_trusted_issuer`` left Z3 at ``unknown`` after sixty
    seconds, and an ``unknown`` recorded as "the theorem was lost" would have
    turned a solver giving up into evidence that an axiom is load-bearing.
    """

    solver = require_z3()
    base = sig.base
    clauses: list[Any] = []
    for label, sort, size in (
        ("wd", base.Domain, 2),
        ("wo", base.Obj, 1),
        ("wi", base.Issuer, 2),
        ("wp", sig.Donor, 3),
    ):
        witness = solver.Const(f"{label}_free", sort)
        members = [solver.Const(f"{label}{index}", sort) for index in range(size)]
        clauses.append(
            solver.ForAll([witness], solver.Or(*[witness == item for item in members]))
        )
    left, right = solver.Consts("wrank_l wrank_r", base.Domain)
    clauses.append(solver.ForAll([left, right], base.Rank(left, right) <= 1))
    return clauses


@lru_cache(maxsize=None)
def prove_all(
    *, timeout_ms: int = PROOF_TIMEOUT_MS, drop: str | None = None, witness_world: bool = False
) -> tuple[ProofResult, ...]:
    """Discharge every theorem in :data:`THEOREMS` under the interpretation.

    Identical queries are immutable, pure proof snapshots. Reuse them within a
    process so a report does not ask Z3 to re-prove a theorem after its fixture
    already established it. The cached value retains ``UNKNOWN`` exactly; this
    avoids load-dependent recomputation without turning a timeout into proof.
    """

    solver = require_z3()
    sig = chain_signature()
    base = sig.base
    axioms = closure_axioms(base) + _frame_conditions(sig, drop=drop)
    if witness_world:
        axioms = axioms + _witness_world(sig)

    root, hop = solver.Consts("root hop", sig.Donor)
    sibling = solver.Const("sibling", sig.Donor)
    other, further = solver.Consts("other further", sig.Donor)
    action_domain = solver.Const("chain_adom", base.Domain)
    action_scope = solver.Const("chain_ascope", base.Scope)
    action_epoch = solver.Int("chain_aepoch")
    no_coercion = solver.ForAll(
        [other, further], solver.Not(sig.Coerce(other, further))
    )

    results: list[ProofResult] = []

    # 1. An X4 hop is a calculus delegation.
    results.append(
        discharge(
            LINK_IS_A_DELEGATION,
            axioms,
            solver.Implies(
                _link(sig, root, hop),
                solver.And(
                    sig.Native(root),
                    base.Trusted(sig.Iss(root)),
                    solver.IsSubset(sig.Sc(hop), sig.Sc(root)),
                    base.Reach(sig.Dom(root), sig.Dom(hop)),
                    sig.Ep(hop) == sig.Ep(root),
                ),
            ),
            timeout_ms=timeout_ms,
        )
    )

    # 2. The one-step lemma at the donor level: the chain confines to its root.
    downstream_authorises = solver.And(
        solver.IsSubset(action_scope, sig.Sc(hop)),
        base.Reach(sig.Dom(hop), action_domain),
        action_epoch == sig.Ep(hop),
    )
    results.append(
        discharge(
            CHAIN_CONFINES_TO_THE_ROOT,
            axioms,
            solver.Implies(
                solver.And(_link(sig, root, hop), downstream_authorises),
                solver.And(
                    solver.IsSubset(action_scope, sig.Sc(root)),
                    base.Reach(sig.Dom(root), action_domain),
                    action_epoch == sig.Ep(root),
                ),
            ),
            timeout_ms=timeout_ms,
        )
    )

    # 3. A widening hop is refused by the calculus's own rule, with every other
    #    conjunct left free -- that is what "while both local donor verdicts
    #    remain intact" has to mean if it means anything.
    results.append(
        discharge(
            WIDENING_HOP_IS_NEVER_AUTHORISED,
            axioms,
            solver.Implies(
                solver.Not(sig.Narrows(root, hop)),
                solver.Not(
                    authorize(
                        base,
                        valid=sig.Native(root),
                        issuer=sig.Iss(root),
                        judgment_domain=sig.Dom(root),
                        judgment_scope=sig.Sc(root),
                        judgment_epoch=sig.Ep(root),
                        action_domain=sig.Dom(hop),
                        action_scope=sig.Sc(hop),
                        action_epoch=sig.Ep(hop),
                        obligations_all_sat=_obligations(sig, root),
                        defeater_active=_defeater(sig, root),
                    )
                ),
            ),
            timeout_ms=timeout_ms,
        )
    )

    # 4. Without a registered bridge, reach implies type agreement.
    results.append(
        discharge(
            UNBRIDGED_GAP_IS_NOT_A_REACH,
            [*axioms, no_coercion],
            solver.Implies(
                base.Reach(sig.Dom(root), sig.Dom(hop)), sig.TypeAgree(root, hop)
            ),
            timeout_ms=timeout_ms,
        )
    )

    # 5. And with agreement, the hop is reflexive -- the shipped chain's case.
    results.append(
        discharge(
            SHIPPED_STEP_IS_REFLEXIVE,
            [*axioms, no_coercion],
            solver.Implies(
                sig.TypeAgree(root, hop),
                solver.And(
                    sig.Dom(root) == sig.Dom(hop),
                    base.Reach(sig.Dom(root), sig.Dom(hop)),
                ),
            ),
            timeout_ms=timeout_ms,
        )
    )

    # 6. The donor label is not a coordinate.
    indistinguishable = solver.And(
        sig.TypeAgree(root, sibling),
        sig.Sc(root) == sig.Sc(sibling),
        sig.Ep(root) == sig.Ep(sibling),
        sig.Iss(root) == sig.Iss(sibling),
        sig.Native(root) == sig.Native(sibling),
        sig.Refuted(root) == sig.Refuted(sibling),
        sig.Established(root) == sig.Established(sibling),
        sig.SupportA(root) == sig.SupportA(sibling),
        sig.SupportB(root) == sig.SupportB(sibling),
        solver.ForAll([other], sig.Coerce(root, other) == sig.Coerce(sibling, other)),
    )
    results.append(
        discharge(
            DONOR_ENTERS_ONLY_THROUGH_ITS_TYPE,
            axioms,
            solver.Implies(
                indistinguishable, _link(sig, root, hop) == _link(sig, sibling, hop)
            ),
            timeout_ms=timeout_ms,
        )
    )

    # 7. The blocker's two halves.
    results.append(
        discharge(
            THREE_STATE_BLOCKER_LAW,
            axioms,
            solver.And(
                solver.Implies(
                    solver.And(
                        sig.Refuted(root),
                        solver.Or(sig.SupportA(root), sig.SupportB(root)),
                    ),
                    solver.And(
                        _obligations(sig, root), solver.Not(_defeater(sig, root))
                    ),
                ),
                solver.Implies(sig.Established(root), _defeater(sig, root)),
            ),
            timeout_ms=timeout_ms,
        )
    )

    return tuple(results)


@lru_cache(maxsize=None)
def prove_chain_ladder(
    *, bound: int = CHAIN_LADDER_BOUND, timeout_ms: int = PROOF_TIMEOUT_MS
) -> tuple[ProofResult, ...]:
    """Expand donor-level chain confinement explicitly at each length.

    P8 states its chain claim for ordered *pairs*, which is length two. The
    theorem it is an instance of holds at every length, and the induction schema
    that gets there is the single hand step this development inherits from the
    calculus. Discharging the fully expanded statement at each concrete length
    does not replace the schema; it means a mistake in the expansion shows up
    here rather than in a reader's trust. As with :func:`prove_all`, an identical
    query is evaluated once per process and its exact three-valued result is
    retained.
    """

    solver = require_z3()
    sig = chain_signature()
    base = sig.base
    axioms = closure_axioms(base) + _frame_conditions(sig)
    results: list[ProofResult] = []

    for length in range(1, bound + 1):
        donors = [
            solver.Const(f"ladder_p{index}", sig.Donor) for index in range(length + 1)
        ]
        action_domain = solver.Const("ladder_adom", base.Domain)
        action_scope = solver.Const("ladder_ascope", base.Scope)
        action_epoch = solver.Int("ladder_aepoch")

        hypothesis = [_link(sig, donors[i], donors[i + 1]) for i in range(length)]
        hypothesis += [
            solver.IsSubset(action_scope, sig.Sc(donors[length])),
            base.Reach(sig.Dom(donors[length]), action_domain),
            action_epoch == sig.Ep(donors[length]),
        ]
        claim = solver.Implies(
            solver.And(*hypothesis),
            solver.And(
                solver.IsSubset(action_scope, sig.Sc(donors[0])),
                base.Reach(sig.Dom(donors[0]), action_domain),
                action_epoch == sig.Ep(donors[0]),
            ),
        )
        results.append(
            discharge(
                Theorem(
                    name=f"DONOR_CHAIN_CONFINEMENT_{length}",
                    statement=(
                        f"a chain of {length} donor hops confines the action's scope to "
                        "the root donor's scope, its domain to the root's reach and its "
                        "epoch to the root's epoch"
                    ),
                    why_it_matters=(
                        "P8's chain claim is this statement at length two, over thirteen "
                        "named families; the ladder shows the length is not what carries "
                        "it either"
                    ),
                ),
                axioms,
                claim,
                timeout_ms=timeout_ms,
            )
        )
    return tuple(results)


def frame_conditions_are_load_bearing(
    *, timeout_ms: int = REFUTATION_TIMEOUT_MS
) -> dict[str, Any]:
    """Drop each frame condition and record which theorems acquire a countermodel.

    Measured as refutation rather than as "stopped being proved", because those
    are different facts and only one of them is evidence. A theorem that comes
    back ``UNKNOWN`` after a condition is dropped has told us nothing: the
    solver gave up. So the runs that look for countermodels are given the finite
    witness world of :func:`_witness_world` --- sound for refutation, never used
    for proof --- and a condition counts as load-bearing only when at least one
    theorem it carries is genuinely refuted without it.
    """

    # The baseline is a proof and gets the proof budget; the drops are searches
    # for a countermodel and get a bounded one, because a search that exceeds it
    # has genuinely not found anything and must report so.
    baseline = {
        result.theorem.name for result in prove_all() if result.discharged
    }
    per_condition: dict[str, list[str]] = {}
    unknowns: dict[str, list[str]] = {}
    for condition in FRAME_CONDITION_REFUTATION_ORDER:
        dropped = prove_all(
            timeout_ms=timeout_ms, drop=condition, witness_world=True
        )
        per_condition[condition] = sorted(
            result.theorem.name
            for result in dropped
            if result.outcome is ProofOutcome.COUNTEREXAMPLE
            and result.theorem.name in baseline
        )
        undecided = sorted(
            result.theorem.name
            for result in dropped
            if result.outcome is ProofOutcome.UNKNOWN
        )
        if undecided:
            unknowns[condition] = undecided

    # Stable report order is part of deterministic JSON output; search order is
    # an operational detail, not a reclassification of the frame conditions.
    per_condition = {condition: per_condition[condition] for condition in FRAME_CONDITION_IDS}
    unknowns = {
        condition: unknowns[condition]
        for condition in FRAME_CONDITION_IDS
        if condition in unknowns
    }

    inert = sorted(name for name, refuted in per_condition.items() if not refuted)
    return {
        "baseline_discharged": sorted(baseline),
        "theorems_refuted_by_dropping": per_condition,
        "theorems_left_undecided_by_dropping": unknowns,
        "inert_conditions": inert,
        "every_condition_carries_a_theorem": not inert,
        "how_measured": (
            "a condition is load-bearing when dropping it yields a countermodel to a "
            "theorem it carried, found under finite sort bounds that are sound for "
            "refutation and never used for proof. An UNKNOWN is recorded and counts as "
            "nothing."
        ),
        "why_the_refuted_sets_vary_between_runs": (
            "dropping narrowing_is_scope_containment leaves the solver searching for a "
            "model of two closely related claims, and over repeated runs it refutes one "
            "and gives up on the other, in either order. Which one is not stable; that "
            "the condition is load-bearing is, and so is the third theorem it refutes "
            "every time. Recorded because a varying set read as a fixed one is how an "
            "intermittent UNKNOWN gets promoted to a finding."
        ),
    }


# ---------------------------------------------------------------------------
# The composition, and the published counts recomputed through it
# ---------------------------------------------------------------------------

#: One X4 state, in the argument order ``scientific_terminal`` takes.
X4State = tuple[bool, tuple[bool, ...], bool, str, bool, bool, bool]

#: All five type coordinates agree: the profile P8's chain claim passes.
AGREEING: tuple[bool, ...] = (True,) * 5

#: The ``domain`` coordinate disagrees and the rest agree: one type gap.
TYPE_GAP: tuple[bool, ...] = (False,) + (True,) * 4


def compose(left: X4State, right: X4State) -> X4State:
    """Compose two donor judgments into the state their chain presents.

    Every clause is read off the calculus, not chosen for convenience:

    * the chain is natively valid when both hops are, because
      :data:`LINK_IS_A_DELEGATION` needs the upstream judgment valid and the
      downstream one authorising;
    * the type coordinates agree on the chain where they agree at both hops,
      coordinate by coordinate;
    * the chain narrows when both hops narrow --- ``IsSubset`` composes by
      transitivity and by nothing weaker;
    * the chain's blocker is the worst on it, since a chain is as blocked as its
      most blocked link;
    * a support family survives the chain when some family survives at *each*
      hop, which is what P8's interface asks for ("at least one complete support
      family survives") applied at every link;
    * the chain's domain step is licensed when each hop's is, which is
      transitivity of ``Reach``. Written into X4's ``protected_coercion``
      argument because that is the only argument that can carry it once the
      coordinate-wise flags have been fixed.

    The composed ``support_b`` is ``False`` rather than a second family: the
    obligation P8 states is "some family carries", and a chain carries it when
    each hop does. Composing the two families separately is one of the wrong
    interpretations :func:`counts_are_sensitive_to_the_interpretation` tries.
    """

    l_native, l_flags, l_narrow, l_blocker, l_a, l_b, l_coerce = left
    r_native, r_flags, r_narrow, r_blocker, r_a, r_b, r_coerce = right
    flags = tuple(bool(x and y) for x, y in zip(l_flags, r_flags))
    bridged = (all(l_flags) or l_coerce) and (all(r_flags) or r_coerce)
    support = (l_a or l_b) and (r_a or r_b)
    blocker = (
        l_blocker
        if BLOCKER_SEVERITY[l_blocker] >= BLOCKER_SEVERITY[r_blocker]
        else r_blocker
    )
    return (
        bool(l_native and r_native),
        flags,
        bool(l_narrow and r_narrow),
        blocker,
        bool(support),
        False,
        bool(bridged),
    )


def _x4_model(repo_root: Any) -> Any:
    """Load P8's committed X4 checker without putting it on the import graph."""

    from pathlib import Path

    return load_executable_model(
        Path(repo_root) / X4_CHECKER, "p8_x4_chain_composition"
    )


def all_states(model: Any) -> tuple[X4State, ...]:
    """Every one of X4's 3,072 distinct states, in the checker's own loop order."""

    states: list[X4State] = []
    for native in (False, True):
        for flags in product((False, True), repeat=5):
            for narrowing in (False, True):
                for blocker in model.BLOCKERS:
                    for support_a in (False, True):
                        for support_b in (False, True):
                            for coercion in (False, True):
                                states.append(
                                    (
                                        native,
                                        flags,
                                        narrowing,
                                        blocker,
                                        support_a,
                                        support_b,
                                        coercion,
                                    )
                                )
    return tuple(states)


def canonical_states(model: Any) -> tuple[X4State, ...]:
    """One representative per verdict class of X4's state space.

    192 of them, and they stand in for all 3,072 exactly --- not approximately.
    :func:`state_space_reduction_is_exact` checks the two facts that make the
    substitution sound, over the full space, rather than assuming them.
    """

    states: list[X4State] = []
    for native in (False, True):
        for agreeing in (False, True):
            for narrowing in (False, True):
                for blocker in model.BLOCKERS:
                    for support_a in (False, True):
                        for support_b in (False, True):
                            for coercion in (False, True):
                                states.append(
                                    (
                                        native,
                                        AGREEING if agreeing else TYPE_GAP,
                                        narrowing,
                                        blocker,
                                        support_a,
                                        support_b,
                                        coercion,
                                    )
                                )
    return tuple(states)


def state_space_reduction_is_exact(repo_root: Any) -> dict[str, Any]:
    """Do 192 representatives really stand in for 3,072 states and 9,437,184 pairs?

    Two facts, both checked exhaustively rather than asserted:

    1. the committed rule reads the five flags only through ``all(flags)``, so
       states differing elsewhere in the flags share a verdict; and
    2. ``all`` distributes over the coordinate-wise conjunction
       :func:`compose` uses, so composing representatives composes classes.

    Together they mean a pair check over the 36,864 representative pairs decides
    the same question as one over all 9,437,184 state pairs. Without them the
    representative count would be a shortcut, and a shortcut is where a count
    stops being computed and starts being claimed.
    """

    model = _x4_model(repo_root)
    states = all_states(model)

    classes: dict[tuple[Any, ...], set[str]] = {}
    for state in states:
        native, flags, narrowing, blocker, support_a, support_b, coercion = state
        key = (native, all(flags), narrowing, blocker, support_a, support_b, coercion)
        classes.setdefault(key, set()).add(model.scientific_terminal(*state))
    split_classes = sorted(str(key) for key, seen in classes.items() if len(seen) > 1)

    conjunction_failures = 0
    for left in product((False, True), repeat=5):
        for right in product((False, True), repeat=5):
            joined = tuple(x and y for x, y in zip(left, right))
            if all(joined) != (all(left) and all(right)):
                conjunction_failures += 1

    return {
        "states_enumerated": len(states),
        "verdict_classes": len(classes),
        "classes_holding_more_than_one_terminal": split_classes,
        "flag_pairs_checked": 1024,
        "conjunction_distribution_failures": conjunction_failures,
        "state_pairs_represented": len(states) ** 2,
        "representative_pairs_checked": len(canonical_states(model)) ** 2,
        "reduction_is_exact": not split_classes and conjunction_failures == 0,
    }


def composition_soundness(
    repo_root: Any, *, composition: Callable[[X4State, X4State], X4State] | None = None
) -> dict[str, Any]:
    """Is composing two judgments the same as requiring both to discharge?

    This is the chain theorem, evaluated. :data:`CHAIN_CONFINES_TO_THE_ROOT` says
    a composing chain confines the action to its root; read on X4's terminals
    that is exactly ``compose(L, R)`` discharging when and only when ``L`` and
    ``R`` both do. Every verdict here comes from the committed
    ``scientific_terminal``; the only thing this module supplies is the composed
    state it is asked about.

    Also checked: with both native verdicts intact, a hop that fails to narrow
    makes the chain ``BLOCK`` --- the general form of P8's 169 widening
    countermodels, and the half of T7 that is supposed to carry the claim.

    The identity on its own is satisfiable by a rule that always refuses and by
    a rule that always discharges, in both cases vacuously, so the corpus is
    measured as well as the agreement: ``exercised_both_verdicts`` is false
    unless some representative discharges and some does not. That is the same
    discipline :class:`~orion.programme.mechanized.DifferentialReport` applies
    for the same reason, and it was added after a constant rule passed this
    check.
    """

    operator = compose if composition is None else composition
    model = _x4_model(repo_root)
    states = canonical_states(model)
    discharges = {state: model.scientific_terminal(*state) == DISCHARGE for state in states}

    unsound = 0
    unsound_examples: list[str] = []
    widening_failures = 0
    widening_examples: list[str] = []
    discharging_pairs = 0

    for left in states:
        for right in states:
            composed = operator(left, right)
            terminal = model.scientific_terminal(*composed)
            expected = discharges[left] and discharges[right]
            if terminal == DISCHARGE:
                discharging_pairs += 1
            if (terminal == DISCHARGE) != expected:
                unsound += 1
                if len(unsound_examples) < 5:
                    unsound_examples.append(
                        f"left={left} right={right}: composed={terminal}, "
                        f"both links discharge={expected}"
                    )
            if left[0] and right[0] and not (left[2] and right[2]) and terminal != BLOCK:
                widening_failures += 1
                if len(widening_examples) < 5:
                    widening_examples.append(
                        f"left={left} right={right}: a widening hop gave {terminal}"
                    )

    discharging_states = sum(1 for state in states if discharges[state])
    total_pairs = len(states) ** 2
    return {
        "representative_pairs_checked": total_pairs,
        "unsound_pairs": unsound,
        "unsound_examples": unsound_examples,
        "widening_hop_failures": widening_failures,
        "widening_examples": widening_examples,
        "discharging_representatives": discharging_states,
        "representatives_checked": len(states),
        "discharging_composed_pairs": discharging_pairs,
        "exercised_both_verdicts": (
            0 < discharging_states < len(states) and 0 < discharging_pairs < total_pairs
        ),
        "composition_is_sound": unsound == 0,
        "every_widening_hop_blocks": widening_failures == 0,
        "computed_by": (
            "the committed check_p8_x4_authority_lifting.scientific_terminal, on states "
            "this interpretation composes"
        ),
        "what_the_identity_does_not_test": (
            "the rule. compose is coordinate-wise, so a committed rule whose DISCHARGE "
            "stays a conjunction of the composed coordinates leaves this identity exact "
            "however else it changes; a rule that always refuses or always discharges "
            "satisfies it vacuously, which is what exercised_both_verdicts is for. What "
            "the identity tests is the composition operator, and every wrong operator "
            "tried moves it."
        ),
    }


def _homogeneous_hops(
    left: str, right: str, *, widen_downstream: bool = False
) -> tuple[X4State, X4State]:
    """The reading P8's shipped chain claim runs under.

    Every donor family presents a fully agreeing scientific type at every hop, so
    no bridge is ever needed. The donor names are accepted and, faithfully to the
    shipped checker, are not consulted --- which is the point
    :func:`recompute_published_counts` measures rather than asserts.
    """

    del left, right
    upstream: X4State = (True, AGREEING, True, "REFUTED", True, False, False)
    downstream: X4State = (
        True,
        AGREEING,
        not widen_downstream,
        "REFUTED",
        True,
        False,
        False,
    )
    return upstream, downstream


def _type_distinct_hops(
    left: str,
    right: str,
    *,
    widen_downstream: bool = False,
    bridges: frozenset[tuple[str, str]] = frozenset(),
) -> tuple[X4State, X4State]:
    """The reading under which thirteen *different* donor families are different.

    A hop between two families crosses a scientific type boundary unless a
    protected bridge is registered for that ordered pair. Same-family hops agree
    by construction. Nothing else changes.
    """

    upstream: X4State = (
        True,
        AGREEING if left == right else TYPE_GAP,
        True,
        "REFUTED",
        True,
        False,
        (left, right) in bridges,
    )
    downstream: X4State = (
        True,
        AGREEING,
        not widen_downstream,
        "REFUTED",
        True,
        False,
        False,
    )
    return upstream, downstream


def _count_pairs(
    model: Any,
    reading: Callable[..., tuple[X4State, X4State]],
    *,
    composition: Callable[[X4State, X4State], X4State],
    **kwargs: Any,
) -> dict[str, Any]:
    """Run one reading over every ordered donor pair, through the committed rule."""

    successes = 0
    widening_countermodels = 0
    composed_states: set[X4State] = set()
    for left in model.DONORS:
        for right in model.DONORS:
            upstream, downstream = reading(left, right, **kwargs)
            composed = composition(upstream, downstream)
            composed_states.add(composed)
            if model.scientific_terminal(*composed) == DISCHARGE:
                successes += 1
            widened_up, widened_down = reading(
                left, right, widen_downstream=True, **kwargs
            )
            if model.scientific_terminal(*composition(widened_up, widened_down)) == BLOCK:
                widening_countermodels += 1
    return {
        "ordered_pairs": len(model.DONORS) ** 2,
        "chain_successes": successes,
        "chain_widening_countermodels": widening_countermodels,
        "distinct_composed_states": len(composed_states),
    }


def recompute_published_counts(repo_root: Any) -> dict[str, Any]:
    """Recompute both 169s by composing donor judgments through the interpretation.

    Not by evaluating a rule defined here: the verdict on every composed state
    comes from the committed ``scientific_terminal``, the same function the
    shipped checker's chain loop calls.

    Three readings are run, because which one the 169 belongs to is the finding.
    """

    model = _x4_model(repo_root)
    donors = tuple(model.DONORS)
    every_bridge = frozenset((left, right) for left in donors for right in donors)

    homogeneous = _count_pairs(model, _homogeneous_hops, composition=compose)
    type_distinct = _count_pairs(model, _type_distinct_hops, composition=compose)
    bridged = _count_pairs(
        model, _type_distinct_hops, composition=compose, bridges=every_bridge
    )

    source = (
        __import__("pathlib").Path(repo_root) / X4_CHECKER
    ).read_text(encoding="utf-8")
    loop_ignores_its_variables = "for _left in DONORS:" in source

    reproduced = (
        homogeneous["chain_successes"] == PUBLISHED_CHAIN_SUCCESSES
        and homogeneous["chain_widening_countermodels"]
        == PUBLISHED_CHAIN_WIDENING_COUNTERMODELS
    )
    return {
        "donor_families": len(donors),
        "published_chain_successes": PUBLISHED_CHAIN_SUCCESSES,
        "published_chain_widening_countermodels": PUBLISHED_CHAIN_WIDENING_COUNTERMODELS,
        "homogeneous_reading": homogeneous,
        "type_distinct_reading": type_distinct,
        "type_distinct_with_every_bridge_registered": bridged,
        "counts_reproduced": reproduced,
        "shipped_chain_loop_ignores_its_donor_variables": loop_ignores_its_variables,
        "computed_by": (
            "the committed check_p8_x4_authority_lifting.scientific_terminal, on the "
            "state each donor pair composes to under this interpretation"
        ),
        "what_the_169_is": (
            "169 is one composition counted 169 times. The shipped chain loop is "
            "`for _left in DONORS: for _right in DONORS:` with a body that mentions "
            "neither variable, and under this interpretation the thirteen families "
            "present one profile, so all 169 ordered pairs compose to "
            f"{homogeneous['distinct_composed_states']} distinct state(s). The donor "
            "axis is a multiplier here exactly as it is in the 39,936-state count, and "
            "here it is squared."
        ),
        "what_heterogeneity_would_cost": (
            "Read the thirteen families as type-distinct -- a cross-family hop crosses a "
            "scientific type boundary unless a protected bridge is registered -- and the "
            "same committed rule returns "
            f"{type_distinct['chain_successes']} successes, not 169; registering every "
            "cross-family bridge returns "
            f"{bridged['chain_successes']}. The published 169 therefore records the "
            "reading in which no two of the thirteen donor families differ in scientific "
            "type, which is the reading in which the chain is not heterogeneous."
        ),
    }


def counts_are_sensitive_to_the_interpretation(repo_root: Any) -> dict[str, Any]:
    """Would a wrong composition give the same numbers?

    Eight wrong composition operators, each a single clause of :func:`compose`
    replaced by something a careless reading would accept. Three quantities are
    watched: the two published counts and the exhaustive soundness identity. The
    result is not flattering to the published counts and is reported as it came
    out.
    """

    model = _x4_model(repo_root)

    def ignore_downstream(left: X4State, right: X4State) -> X4State:
        del right
        return left

    def ignore_root(left: X4State, right: X4State) -> X4State:
        del left
        return right

    def _replaced(index: int, value: Any) -> Callable[[X4State, X4State], X4State]:
        def operator(left: X4State, right: X4State) -> X4State:
            composed = list(compose(left, right))
            composed[index] = value(left, right)
            return tuple(composed)  # type: ignore[return-value]

        return operator

    variants: dict[str, Callable[[X4State, X4State], X4State]] = {
        "composition_ignores_the_downstream_hop": ignore_downstream,
        "composition_ignores_the_root_hop": ignore_root,
        "native_validity_composes_by_disjunction": _replaced(
            0, lambda left, right: bool(left[0] or right[0])
        ),
        "the_downstream_type_gap_is_ignored": _replaced(
            1, lambda left, right: left[1]
        ),
        "narrowing_composes_by_disjunction": _replaced(
            2, lambda left, right: bool(left[2] or right[2])
        ),
        "the_blocker_composes_by_the_weakest_link": _replaced(
            3,
            lambda left, right: (
                left[3]
                if BLOCKER_SEVERITY[left[3]] <= BLOCKER_SEVERITY[right[3]]
                else right[3]
            ),
        ),
        "support_composes_by_disjunction": _replaced(
            4, lambda left, right: bool((left[4] or left[5]) or (right[4] or right[5]))
        ),
        "the_domain_step_composes_by_disjunction": _replaced(
            6,
            lambda left, right: bool(
                (all(left[1]) or left[6]) or (all(right[1]) or right[6])
            ),
        ),
    }

    baseline_counts = _count_pairs(model, _homogeneous_hops, composition=compose)
    baseline_sound = composition_soundness(repo_root)["unsound_pairs"]

    outcomes: dict[str, dict[str, Any]] = {}
    for name, operator in variants.items():
        counts = _count_pairs(model, _homogeneous_hops, composition=operator)
        type_distinct = _count_pairs(model, _type_distinct_hops, composition=operator)
        outcomes[name] = {
            "chain_successes": counts["chain_successes"],
            "chain_widening_countermodels": counts["chain_widening_countermodels"],
            "type_distinct_successes": type_distinct["chain_successes"],
            "unsound_pairs": composition_soundness(repo_root, composition=operator)[
                "unsound_pairs"
            ],
        }

    moved_successes = sorted(
        name
        for name, seen in outcomes.items()
        if seen["chain_successes"] != baseline_counts["chain_successes"]
    )
    moved_widening = sorted(
        name
        for name, seen in outcomes.items()
        if seen["chain_widening_countermodels"]
        != baseline_counts["chain_widening_countermodels"]
    )
    moved_soundness = sorted(
        name for name, seen in outcomes.items() if seen["unsound_pairs"] != baseline_sound
    )

    return {
        "baseline": {
            "chain_successes": baseline_counts["chain_successes"],
            "chain_widening_countermodels": baseline_counts[
                "chain_widening_countermodels"
            ],
            "unsound_pairs": baseline_sound,
        },
        "variants": outcomes,
        "variants_that_move_the_success_count": moved_successes,
        "variants_that_move_the_widening_count": moved_widening,
        "variants_that_move_the_soundness_count": moved_soundness,
        "every_wrong_composition_moves_the_soundness_count": len(moved_soundness)
        == len(variants),
        "the_success_count_does_not_discriminate": (
            f"{len(variants) - len(moved_successes)} of {len(variants)} wrong "
            "composition operators reproduce 169 successes exactly. The shipped chain "
            "state is clean at both hops, so every operator that is the identity on a "
            "clean pair -- which is all of them -- returns it. 169 tests nothing about "
            "how a chain composes."
        ),
        "the_widening_count_barely_discriminates": (
            f"{len(moved_widening)} of {len(variants)} wrong operators move the widening "
            "count, and both are operators that drop the downstream hop's narrowing. It "
            "is the better of the two published numbers and it still separates only two "
            "readings."
        ),
    }


def build_report(repo_root: Any, *, date: str) -> dict[str, Any]:
    """Everything this module establishes, with what it does not."""

    import z3 as _z3

    theorems = prove_all()
    ladder = prove_chain_ladder()
    reduction = state_space_reduction_is_exact(repo_root)
    soundness = composition_soundness(repo_root)
    counts = recompute_published_counts(repo_root)
    frames = frame_conditions_are_load_bearing()
    sensitivity = counts_are_sensitive_to_the_interpretation(repo_root)
    undischarged = [
        result.theorem.name for result in (*theorems, *ladder) if not result.discharged
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "record": "P8_CHAIN_COMPOSITION_INTERPRETATION",
        "date": date,
        "solver": _z3.get_version_string(),
        "theorems": [result.as_json() for result in theorems],
        "chain_ladder": {
            "bound": CHAIN_LADDER_BOUND,
            "results": [result.as_json() for result in ladder],
            "beyond_the_bound": LADDER_BEYOND_THE_BOUND,
        },
        "all_discharged": not undischarged,
        "undischarged": undischarged,
        "frame_conditions": frames,
        "state_space_reduction": reduction,
        "composition_soundness": soundness,
        "published_counts": counts,
        "interpretation_sensitivity": sensitivity,
        "what_this_establishes": (
            "P8's heterogeneous chain composition model is an interpretation of the "
            "authority calculus already proved general. A donor family is an element of "
            "an uninterpreted sort, its domain is its scientific type profile, its "
            "protected coercion is the calculus's registered conversion and its "
            "narrowing is scope containment; under those frame conditions seven theorems "
            "are discharged by Z3 over uninterpreted domain, object, issuer and donor "
            "sorts, and donor-level chain confinement is expanded and discharged at "
            f"every length up to {CHAIN_LADDER_BOUND}. P8's chain hop is the calculus's "
            "delegation, so P8's 169 chain claims are instances of a theorem that never "
            "mentions thirteen or two. The counts are then recomputed by composing donor "
            "judgments through the interpretation and handing each composed state to the "
            "committed scientific_terminal, and the composition is shown exact against "
            "the chain theorem on every pair of X4 states: compose(L,R) discharges when "
            "and only when L and R both do. Each of the eight frame conditions is shown "
            "load-bearing by a countermodel to a theorem it carries."
        ),
        "what_the_169_costs": (
            "The derivation lands, and what it lands on is small. The shipped chain loop "
            "ignores both of its donor variables, and under this interpretation all 169 "
            "ordered pairs compose to "
            f"{counts['homogeneous_reading']['distinct_composed_states']} distinct "
            "state: 169 is one composition counted 13 squared times. Because the shipped "
            "state passes all five type flags, the hop is a reach by reflexivity and no "
            "conversion is consulted, so nothing heterogeneous is exercised -- read the "
            "thirteen families as type-distinct with no bridge registered and the same "
            "committed rule returns "
            f"{counts['type_distinct_reading']['chain_successes']}. And "
            f"{len(sensitivity['variants']) - len(sensitivity['variants_that_move_the_success_count'])}"
            f" of {len(sensitivity['variants'])} wrong composition operators reproduce "
            "169 exactly, so the published count does not test the interpretation. What "
            "does is the exhaustive soundness identity, which every wrong operator "
            "breaks."
        ),
        "not_licensed": [
            "any claim that 169 measures heterogeneity; the shipped chain state agrees "
            "on all five type coordinates, which by THE_SHIPPED_CHAIN_STEP_IS_THE_"
            "REFLEXIVE_ONE puts both donors in one domain and consults no conversion",
            "any claim that 169 is 169 results; the shipped loop ignores both donor "
            "variables and the 169 ordered pairs compose to one distinct state",
            "any claim that reproducing 169 validates this interpretation; "
            f"{len(sensitivity['variants']) - len(sensitivity['variants_that_move_the_widening_count'])}"
            f" of {len(sensitivity['variants'])} wrong composition operators reproduce "
            "both published counts, and it is the exhaustive soundness identity that "
            "separates them",
            "any claim that the soundness identity tests the committed rule; it tests "
            "the composition operator. A rule that always refuses satisfies it "
            "vacuously, which is why the corpus coverage is measured beside it, and a "
            "rule whose DISCHARGE stays a conjunction of the composed coordinates "
            "leaves it exact however else it changes",
            "any claim about chains longer than the ladder bound beyond what the "
            "induction schema gives; the schema is the single hand step, inherited from "
            "the calculus",
            "independent review: the interpretation, the theorems and the tests were "
            "written in the same lane as the model, which is P8-U-T5",
            "any empirical claim whatsoever",
        ],
    }


def main(argv: list[str]) -> int:
    """CLI entry point. ``argv`` is required: there is no implicit run."""

    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="orion-p8-chain-composition-interpretation",
        description=(
            "Instantiate the authority calculus's chain theorem at P8's donor level."
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
    ladder = report["chain_ladder"]["results"]
    proved = sum(1 for item in ladder if item["outcome"] == "PROVED")
    print(f"  chain ladder: {proved}/{len(ladder)} proved")
    counts = report["published_counts"]
    homogeneous = counts["homogeneous_reading"]
    print(
        f"  counts: {homogeneous['chain_successes']} chain successes, "
        f"{homogeneous['chain_widening_countermodels']} widening countermodels, "
        f"reproduced={counts['counts_reproduced']} "
        f"(from {homogeneous['distinct_composed_states']} distinct composed state)"
    )
    print(
        "  type-distinct reading: "
        f"{counts['type_distinct_reading']['chain_successes']} successes"
    )
    soundness = report["composition_soundness"]
    print(
        f"  composition sound on {soundness['representative_pairs_checked']} "
        f"representative pairs: {soundness['composition_is_sound']} "
        f"({soundness['discharging_representatives']}/"
        f"{soundness['representatives_checked']} representatives discharge)"
    )
    frames = report["frame_conditions"]
    print(
        "  every frame condition carries a theorem: "
        f"{frames['every_condition_carries_a_theorem']}"
    )
    sensitivity = report["interpretation_sensitivity"]
    print(
        "  every wrong composition moves the soundness count: "
        f"{sensitivity['every_wrong_composition_moves_the_soundness_count']}"
    )

    # A finding and an unmeasured run exit differently, because they are not the
    # same event. The convention is already the repo's own:
    # scripts/audit_manuscript_clipping.py ends `return 2 if (new or stale) else 0`
    # and reserves 3 for the runs it could not check, a split its workflow states
    # in words ("Exit 2 = new clipping or a stale baseline entry. Exit 3 = could
    # not check"). This CLI used to answer 3 to everything, so "the composition is
    # not sound" -- a real negative result about P8 -- left under the code meaning
    # "I could not measure". That is the confusion this module's own
    # _assert_all_discharged docstring refuses to make one layer up: "One says
    # P8's interpretation is false; the other says a measurement was not taken."
    if not report["all_discharged"]:
        graded = (*report["theorems"], *report["chain_ladder"]["results"])
        refuted = [i["name"] for i in graded if i["outcome"] == "COUNTEREXAMPLE"]
        undecided = [i["name"] for i in graded if i["outcome"] == "UNKNOWN"]
        if refuted:
            print(f"REFUTED: {refuted}")
            if undecided:
                print(f"  (also undecided, and not counted as refuted: {undecided})")
            return 2
        print(
            f"CANNOT CHECK: Z3 returned UNKNOWN for {undecided} within "
            f"{PROOF_TIMEOUT_MS}ms. These proofs run in well under a second when "
            "the solver is not starved, so an undecided run here is a measurement "
            "not taken, not a theorem lost."
        )
        return 3
    if not report["state_space_reduction"]["reduction_is_exact"]:
        print("THE 192 REPRESENTATIVES DO NOT STAND IN FOR THE 3,072 STATES")
        return 2
    if not soundness["composition_is_sound"]:
        print("THE COMPOSITION IS NOT SOUND AGAINST THE CHAIN THEOREM")
        return 2
    if not soundness["every_widening_hop_blocks"]:
        print("A WIDENING HOP DID NOT BLOCK")
        return 2
    if not soundness["exercised_both_verdicts"]:
        print("THE COMPOSITION CORPUS EXERCISED ONE VERDICT; THE IDENTITY IS VACUOUS")
        return 2
    if not counts["counts_reproduced"]:
        print("THE PUBLISHED CHAIN COUNTS WERE NOT REPRODUCED UNDER THE INTERPRETATION")
        return 2
    if not frames["every_condition_carries_a_theorem"]:
        print(f"INERT FRAME CONDITIONS: {frames['inert_conditions']}")
        return 2
    if not sensitivity["every_wrong_composition_moves_the_soundness_count"]:
        print("A WRONG COMPOSITION REPRODUCED THE SOUNDNESS COUNT")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
