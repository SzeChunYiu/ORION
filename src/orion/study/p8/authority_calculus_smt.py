"""A machine-checked authority calculus for P8, over arbitrary delegation graphs.

P8's formal core is currently a *finite instance*. ``check_authority_calculus.py``
establishes non-laundering by enumerating six authored domains and asserting
``result is (source == target)`` on all thirty-six pairs, and establishes scope
monotonicity on two hand-picked judgments. Those are true statements about six
domains and two judgments. ``P8-U-T1`` asks for something else:

    Define primitive scientific authority and discharge semantics independent of
    the 13 donor types, then prove non-amplification for arbitrary acyclic
    graphs and characterize cycles.

This module is that. Domains, objects and issuers are **uninterpreted sorts**, so
nothing here knows how many domains exist or what they are called; the conversion
relation is an **uninterpreted predicate**, so nothing here knows which
conversions are registered. Every theorem below is discharged by Z3 as the
unsatisfiability of its negation under the axioms, which is a proof over *all*
models of the semantics rather than over an authored list of them.

Relation to the executable model
--------------------------------
The predicate proved about is the same one ``check_authority_calculus.authorize``
computes, transcribed into first-order logic:

    authorize(j, a)  <->  valid(j)
                          /\\ trusted(issuer(j))
                          /\\ epoch(j) = epoch(a)
                          /\\ scope(a) subset-of scope(j)
                          /\\ reach(domain(j), domain(a))
                          /\\ every hard obligation is SAT
                          /\\ no defeater is active

:func:`differential_check` re-executes the Python model against the SMT
predicate on a randomised finite corpus, so the transcription is checked rather
than asserted. A proof about a formula that is not the implemented rule proves
nothing about the implementation, and that gap is exactly what a "mechanized"
claim must not paper over.

What is and is not machine-checked
----------------------------------
Reachability is the reflexive-transitive closure of the conversion relation, and
RTC is not first-order definable. It is therefore *axiomatised* by the three
clauses in :func:`closure_axioms` --- reflexivity, the step rule, and
justification (every reachability fact is either reflexive or has a witnessing
predecessor). Those three are the definition this calculus uses; they are stated
as axioms and not derived.

The chain theorem is proved by induction on chain length. The induction *step* is
machine-checked (:data:`ONE_STEP_LEMMA`); the induction *schema* is the standard
one over the naturals and is the single meta-level step in this development. To
keep that step honest rather than merely asserted, :func:`prove_chain_ladder`
also discharges the fully expanded chain theorem for every length up to a bound,
each as its own Z3 query, so the schema is corroborated at concrete lengths as
well as argued in general.

Acyclicity is *not* assumed. The blocker asks for arbitrary acyclic graphs and a
characterisation of cycles; the non-amplification theorems below hold with or
without cycles, and :data:`CYCLE_COLLAPSE` states what a cycle does instead --- it
merges the domains of a strongly connected component into a single authority
class, so a registered cycle is an authority-equivalence declaration and not a
loophole.
"""

from __future__ import annotations

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

SCHEMA_VERSION = "orion.p8.authority-calculus-smt.v1"

#: How far :func:`prove_chain_ladder` expands the chain theorem explicitly.
#: The schema is what carries the general result; this is corroboration, and a
#: bound is declared rather than left to whatever the caller passes.
CHAIN_LADDER_BOUND = 8

__all__ = [
    "CHAIN_LADDER_BOUND",
    "DifferentialReport",
    "ProofOutcome",
    "ProofResult",
    "SCHEMA_VERSION",
    "THEOREMS",
    "Theorem",
    "Z3Unavailable",
    "build_report",
    "differential_check",
    "main",
    "prove_all",
    "prove_chain_ladder",
]


# ---------------------------------------------------------------------------
# Primitive semantics. Nothing below names a domain, an issuer or an object.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Signature:
    """The uninterpreted vocabulary every theorem is quantified over."""

    Domain: Any
    Obj: Any
    Issuer: Any
    Scope: Any
    Conv: Any
    Reach: Any
    Trusted: Any
    Rank: Any


def signature() -> Signature:
    """Build the vocabulary. Sorts are uninterpreted, so cardinality is free.

    This is the whole force of the generalisation: ``Domain`` is not six values,
    it is *a sort*, so a proof discharged here holds for a calculus with any
    number of domains, including infinitely many.
    """

    solver = require_z3()
    Domain = solver.DeclareSort("Domain")
    Obj = solver.DeclareSort("Obj")
    Issuer = solver.DeclareSort("Issuer")
    return Signature(
        Domain=Domain,
        Obj=Obj,
        Issuer=Issuer,
        Scope=solver.SetSort(Obj),
        Conv=solver.Function("Conv", Domain, Domain, solver.BoolSort()),
        Reach=solver.Function("Reach", Domain, Domain, solver.BoolSort()),
        Trusted=solver.Function("Trusted", Issuer, solver.BoolSort()),
        Rank=solver.Function("Rank", Domain, Domain, solver.IntSort()),
    )


def closure_axioms(sig: Signature) -> list[Any]:
    """Reachability is the reflexive-transitive closure of the conversions.

    RTC is not first-order definable, so these three clauses *are* the
    definition used here, stated as axioms rather than derived:

    1. **Reflexive.** A domain reaches itself; authority in a domain authorises
       action in that domain with no conversion required.
    2. **Step.** Reachability extends along a registered conversion.
    3. **Transitive.** Reachability composes. Stated rather than derived: the
       step rule extends a reach by a *single* conversion, and getting from
       there to "any reach composed with any reach" is an induction over path
       length, which is not available inside first-order logic. Without this
       clause the one-step delegation lemma and the cycle characterisation both
       come back ``unknown`` --- which is how it was found, and is recorded here
       rather than quietly patched.
    4. **Well-founded justification.** Every non-reflexive reachability fact has
       a witnessing predecessor of strictly smaller rank, and ranks are
       non-negative. This is the clause that makes the closure the *least* one.

       The strictness is load-bearing and was not obvious. A first draft stated
       justification without a rank --- ``Reach(a,b)`` implies ``a = b`` or some
       ``c`` with ``Reach(a,c)`` and ``Conv(c,b)`` --- which reads like a
       definition of "least" and is not one. Transitive closure is famously not
       first-order definable, and unranked justification admits models where two
       spurious reach facts justify *each other* in a cycle. The differential
       check found exactly that: with conversions ``d0->d1``, ``d1->d0``,
       ``d1->d3`` the domain ``d3`` is a sink, the Python model correctly refused
       to reach ``d0`` from it, and the solver produced a model in which
       ``Reach(d3,d0)`` was supported by ``Reach(d3,d1)`` and vice versa. A
       decreasing rank forbids the cycle, because a finite descending chain of
       non-negative integers cannot close.
    """

    solver = require_z3()
    a, b, c = solver.Consts("a b c", sig.Domain)
    return [
        solver.ForAll([a], sig.Reach(a, a)),
        solver.ForAll(
            [a, b, c],
            solver.Implies(solver.And(sig.Reach(a, b), sig.Conv(b, c)), sig.Reach(a, c)),
        ),
        solver.ForAll(
            [a, b, c],
            solver.Implies(solver.And(sig.Reach(a, b), sig.Reach(b, c)), sig.Reach(a, c)),
        ),
        solver.ForAll([a, b], sig.Rank(a, b) >= 0),
        solver.ForAll(
            [a, b],
            solver.Implies(
                sig.Reach(a, b),
                solver.Or(
                    a == b,
                    solver.Exists(
                        [c],
                        solver.And(
                            sig.Reach(a, c),
                            sig.Conv(c, b),
                            sig.Rank(a, c) < sig.Rank(a, b),
                        ),
                    ),
                ),
            ),
        ),
    ]


def authorize(
    sig: Signature,
    *,
    valid: Any,
    issuer: Any,
    judgment_domain: Any,
    judgment_scope: Any,
    judgment_epoch: Any,
    action_domain: Any,
    action_scope: Any,
    action_epoch: Any,
    obligations_all_sat: Any,
    defeater_active: Any,
) -> Any:
    """The authorisation rule, as one conjunction.

    Transcribed from ``check_authority_calculus.authorize``. Every conjunct is
    necessary and none is compensatory: this is an ``And``, so no conjunct can be
    outweighed by the others being emphatically true. That structural fact is
    what :data:`NON_COMPENSATORY` turns into a theorem.
    """

    solver = require_z3()
    return solver.And(
        valid,
        sig.Trusted(issuer),
        judgment_epoch == action_epoch,
        solver.IsSubset(action_scope, judgment_scope),
        sig.Reach(judgment_domain, action_domain),
        obligations_all_sat,
        solver.Not(defeater_active),
    )


# ---------------------------------------------------------------------------
# The theorems
# ---------------------------------------------------------------------------

SCOPE_NON_AMPLIFICATION = Theorem(
    name="SCOPE_NON_AMPLIFICATION",
    statement=(
        "for every judgment and action over any object universe, if the action "
        "is authorised then its scope is a subset of the judgment's scope"
    ),
    why_it_matters=(
        "the finite core checks this on two authored judgments over three named "
        "claims; this is the same statement with the universe left free"
    ),
)

DOMAIN_CONFINEMENT = Theorem(
    name="DOMAIN_CONFINEMENT",
    statement=(
        "an authorised action's domain is reachable from the judgment's domain "
        "through the registered conversion relation"
    ),
    why_it_matters=(
        "authority never arrives in a domain except along conversions someone "
        "registered; reaching a domain is always a licensed step, never a default"
    ),
)

NO_LAUNDERING_GENERAL = Theorem(
    name="NO_LAUNDERING_GENERAL",
    statement=(
        "if no conversion is registered, an authorised action's domain equals "
        "the judgment's domain, for a domain sort of any cardinality"
    ),
    why_it_matters=(
        "this is the generalisation of the thirty-six-pair enumeration: the "
        "finite core asserts result is (source == target) over six authored "
        "domains, and the same claim holds here over all of them"
    ),
)

NON_COMPENSATORY = Theorem(
    name="NON_COMPENSATORY",
    statement=(
        "if any hard obligation is unmet, no configuration of issuer, scope, "
        "domain or epoch authorises the action"
    ),
    why_it_matters=(
        "a non-compensatory gate is the paper's central structural claim; if a "
        "strong enough elsewhere could outweigh an unmet obligation the whole "
        "authority argument collapses into a score"
    ),
)

DEFEATER_MONOTONICITY = Theorem(
    name="DEFEATER_MONOTONICITY",
    statement="activating a defeater can only remove authorisations, never create one",
    why_it_matters=(
        "revocation must be monotone or a revoked authority could be restored by "
        "revoking something else, which is the laundering shape one level up"
    ),
)

EPOCH_ISOLATION = Theorem(
    name="EPOCH_ISOLATION",
    statement="an authorised action carries the judgment's epoch, so replay across epochs is impossible",
    why_it_matters="a judgment is authority about a state of the world, not a bearer token",
)

ONE_STEP_LEMMA = Theorem(
    name="ONE_STEP_LEMMA",
    statement=(
        "if a judgment delegates to a second and the second authorises an action, "
        "the first's scope contains the action's scope and the first's domain "
        "reaches the action's domain"
    ),
    why_it_matters=(
        "this is the induction step from which chain non-amplification follows "
        "for delegation graphs of unbounded depth"
    ),
)

CONV_IMPLIES_REACH = Theorem(
    name="CONV_IMPLIES_REACH",
    statement="a registered conversion is itself a reach",
    why_it_matters=(
        "the bridge from the conversion relation to reachability; stated as its "
        "own lemma because the cycle theorem needs it and, proved together, the "
        "two were more than the solver would discharge"
    ),
)

CYCLE_COLLAPSE = Theorem(
    name="CYCLE_COLLAPSE",
    statement=(
        "if two domains reach each other then they reach exactly the same "
        "domains, so a cycle merges its members into one authority class"
    ),
    why_it_matters=(
        "the requested characterisation of cycles: a registered cycle is not a "
        "loophole that manufactures authority, it is a declaration that the "
        "domains it joins are authority-equivalent, and it says so in advance"
    ),
)

ACYCLIC_STRICTNESS = Theorem(
    name="ACYCLIC_STRICTNESS",
    statement=(
        "if reachability is antisymmetric --- the acyclic case --- then two "
        "distinct domains cannot each authorise action in the other"
    ),
    why_it_matters=(
        "names what acyclicity buys, so the general theorems are not silently "
        "credited with it: non-amplification holds either way, and antisymmetry "
        "is what additionally forbids mutual authority"
    ),
)

THEOREMS: tuple[Theorem, ...] = (
    SCOPE_NON_AMPLIFICATION,
    DOMAIN_CONFINEMENT,
    NO_LAUNDERING_GENERAL,
    NON_COMPENSATORY,
    DEFEATER_MONOTONICITY,
    EPOCH_ISOLATION,
    ONE_STEP_LEMMA,
    CONV_IMPLIES_REACH,
    CYCLE_COLLAPSE,
    ACYCLIC_STRICTNESS,
)


# ---------------------------------------------------------------------------
# Discharging them
# ---------------------------------------------------------------------------


def _free_case(sig: Signature, tag: str) -> dict[str, Any]:
    """One judgment/action pair with every field a free variable."""

    solver = require_z3()
    return {
        "valid": solver.Bool(f"valid_{tag}"),
        "issuer": solver.Const(f"issuer_{tag}", sig.Issuer),
        "judgment_domain": solver.Const(f"jdom_{tag}", sig.Domain),
        "judgment_scope": solver.Const(f"jscope_{tag}", sig.Scope),
        "judgment_epoch": solver.Int(f"jepoch_{tag}"),
        "action_domain": solver.Const(f"adom_{tag}", sig.Domain),
        "action_scope": solver.Const(f"ascope_{tag}", sig.Scope),
        "action_epoch": solver.Int(f"aepoch_{tag}"),
        "obligations_all_sat": solver.Bool(f"obligations_{tag}"),
        "defeater_active": solver.Bool(f"defeater_{tag}"),
    }


def prove_all(*, timeout_ms: int = 20000) -> tuple[ProofResult, ...]:
    """Discharge every theorem in :data:`THEOREMS`, in order."""

    solver = require_z3()
    sig = signature()
    axioms = closure_axioms(sig)
    case = _free_case(sig, "0")
    authorized = authorize(sig, **case)
    results: list[ProofResult] = []

    results.append(
        discharge(
            SCOPE_NON_AMPLIFICATION,
            axioms,
            solver.Implies(authorized, solver.IsSubset(case["action_scope"], case["judgment_scope"])),
            timeout_ms=timeout_ms,
        )
    )
    results.append(
        discharge(
            DOMAIN_CONFINEMENT,
            axioms,
            solver.Implies(authorized, sig.Reach(case["judgment_domain"], case["action_domain"])),
            timeout_ms=timeout_ms,
        )
    )

    # No conversion is registered anywhere. This is the hypothesis the
    # thirty-six-pair enumeration ran under, stated over the whole sort.
    d1, d2 = solver.Consts("d1 d2", sig.Domain)
    no_conversions = solver.ForAll([d1, d2], solver.Not(sig.Conv(d1, d2)))
    results.append(
        discharge(
            NO_LAUNDERING_GENERAL,
            [*axioms, no_conversions],
            solver.Implies(authorized, case["judgment_domain"] == case["action_domain"]),
            timeout_ms=timeout_ms,
        )
    )
    results.append(
        discharge(
            NON_COMPENSATORY,
            axioms,
            solver.Implies(solver.Not(case["obligations_all_sat"]), solver.Not(authorized)),
            timeout_ms=timeout_ms,
        )
    )
    results.append(
        discharge(
            DEFEATER_MONOTONICITY,
            axioms,
            solver.Implies(case["defeater_active"], solver.Not(authorized)),
            timeout_ms=timeout_ms,
        )
    )
    results.append(
        discharge(
            EPOCH_ISOLATION,
            axioms,
            solver.Implies(authorized, case["judgment_epoch"] == case["action_epoch"]),
            timeout_ms=timeout_ms,
        )
    )
    results.append(discharge(ONE_STEP_LEMMA, axioms, _one_step_claim(sig), timeout_ms=timeout_ms))

    # Cycles. Two domains that convert to each other reach exactly the same set.
    # Free variables are already universally quantified for a validity check, so
    # claims are stated without a nested ForAll: a quantifier under an
    # implication is materially harder for the solver and buys nothing here.
    results.append(
        discharge(
            CONV_IMPLIES_REACH,
            axioms,
            solver.Implies(sig.Conv(d1, d2), sig.Reach(d1, d2)),
            timeout_ms=timeout_ms,
        )
    )

    # The cycle hypothesis is stated as mutual *reachability*, which is what a
    # strongly connected component is; CONV_IMPLIES_REACH is what turns a
    # literal two-edge cycle into that hypothesis. Split because the combined
    # statement exceeded what the solver would discharge once the rank axiom
    # was in play, and an undischarged theorem reported as proved is the failure
    # this module's three-valued outcome exists to prevent.
    x = solver.Const("x", sig.Domain)
    mutually_reachable = solver.And(sig.Reach(d1, d2), sig.Reach(d2, d1))
    results.append(
        discharge(
            CYCLE_COLLAPSE,
            axioms,
            solver.Implies(mutually_reachable, sig.Reach(d1, x) == sig.Reach(d2, x)),
            timeout_ms=timeout_ms,
        )
    )

    # Acyclicity, stated as antisymmetry of reachability.
    antisymmetric = solver.ForAll(
        [d1, d2],
        solver.Implies(solver.And(sig.Reach(d1, d2), sig.Reach(d2, d1)), d1 == d2),
    )
    e1, e2 = solver.Consts("e1 e2", sig.Domain)
    results.append(
        discharge(
            ACYCLIC_STRICTNESS,
            [*axioms, antisymmetric],
            solver.Implies(
                solver.And(sig.Reach(e1, e2), sig.Reach(e2, e1)),
                e1 == e2,
            ),
            timeout_ms=timeout_ms,
        )
    )
    return tuple(results)


def _one_step_claim(sig: Signature) -> Any:
    """Delegation composes without amplifying, in one step.

    ``delegates(j1, j2)`` says j2 was issued on j1's authority: j1 is valid and
    trusted, j2's scope is within j1's, j2's domain is reachable from j1's, and
    the epoch is carried. The claim is that authority granted through j2 is still
    within j1's scope and domain reach --- the property a chain needs at every
    link.
    """

    solver = require_z3()
    issuer1 = solver.Const("issuer1", sig.Issuer)
    dom1, dom2, adom = solver.Consts("dom1 dom2 adom", sig.Domain)
    scope1, scope2, ascope = solver.Consts("scope1 scope2 ascope", sig.Scope)
    epoch1, epoch2, aepoch = solver.Ints("epoch1 epoch2 aepoch")
    valid1 = solver.Bool("valid1")

    # Delegation carries the epoch as well as narrowing scope and stepping
    # domain, so the lemma confines all three and a chain cannot launder a
    # judgment forward in time any more than it can widen its scope.
    delegates = solver.And(
        valid1,
        sig.Trusted(issuer1),
        solver.IsSubset(scope2, scope1),
        sig.Reach(dom1, dom2),
        epoch2 == epoch1,
    )
    second_authorises = solver.And(
        solver.IsSubset(ascope, scope2),
        sig.Reach(dom2, adom),
        aepoch == epoch2,
    )
    return solver.Implies(
        solver.And(delegates, second_authorises),
        solver.And(
            solver.IsSubset(ascope, scope1),
            sig.Reach(dom1, adom),
            aepoch == epoch1,
        ),
    )


# ---------------------------------------------------------------------------
# Is the sentence proved about the sentence the code computes?
# ---------------------------------------------------------------------------

#: Where the executable model lives. A proof about a formula that is not the
#: implemented rule proves nothing about the implementation, so the two are
#: compared rather than assumed equal.
EXECUTABLE_MODEL = (
    "papers/orion-18-epistemic-authority-autonomous-science/formal/check_authority_calculus.py"
)


def load_executable_model(repo_root: Any) -> Any:
    """Load P8's committed Python model without importing it as a package."""

    from pathlib import Path

    return _load_model(Path(repo_root) / EXECUTABLE_MODEL, "p8_check_authority_calculus")


def differential_check(repo_root: Any, *, trials: int = 400, seed: int = 20260821) -> DifferentialReport:
    """Run the Python model and the SMT formula on the same finite worlds.

    Each trial builds a concrete world --- named domains, a concrete conversion
    relation asserted as closed, a trusted-issuer set, one judgment and one
    action --- then asks Z3 whether the ground authorisation formula holds and
    asks the committed Python function the same question. Any disagreement is
    reported; none is tolerated.
    """

    import random

    solver_module = require_z3()
    model = load_executable_model(repo_root)
    rng = random.Random(seed)

    domain_names = ["d0", "d1", "d2", "d3"]
    object_names = ["o0", "o1", "o2", "o-extra"]
    issuer_names = ["trusted-host", "other-host"]

    sig = signature()
    axioms = closure_axioms(sig)
    domain_consts = {name: solver_module.Const(name, sig.Domain) for name in domain_names}
    issuer_consts = {name: solver_module.Const(name, sig.Issuer) for name in issuer_names}
    object_consts = {name: solver_module.Const(name, sig.Obj) for name in object_names}
    distinct = [
        solver_module.Distinct(*domain_consts.values()),
        solver_module.Distinct(*issuer_consts.values()),
        solver_module.Distinct(*object_consts.values()),
    ]

    agreements = 0
    authorised_trials = 0
    disagreements: list[str] = []

    for trial in range(trials):
        # Half the trials are drawn coherent and then perturbed in at most one
        # field; the rest are drawn freely. A purely free draw satisfies all
        # seven conjuncts almost never -- the first version of this ran 60
        # trials and authorised on none of them, so it compared the two
        # implementations only on the constant False. Agreement on a corpus
        # that exercises one verdict is not agreement.
        conversions = frozenset(
            (left, right)
            for left in domain_names
            for right in domain_names
            if left != right and rng.random() < 0.25
        )
        if rng.random() < 0.5:
            trusted = frozenset(issuer_names)
            issuer = rng.choice(issuer_names)
            epoch = rng.randint(0, 2)
            judgment_scope = frozenset(
                name for name in object_names if rng.random() < 0.8
            ) or frozenset({object_names[0]})
            action_scope = frozenset(
                name for name in judgment_scope if rng.random() < 0.7
            )
            domain = rng.choice(domain_names)
            valid, obligation_status, defeaters = True, "SAT", frozenset()
            action_domain, action_epoch = domain, epoch
            # Perturb exactly one conjunct, sometimes, so the corpus contains
            # near-misses as well as clean passes and clean failures.
            spoil = rng.choice([None, "valid", "epoch", "scope", "domain", "obligation", "defeater"])
            if spoil == "valid":
                valid = False
            elif spoil == "epoch":
                action_epoch = epoch + 1
            elif spoil == "scope":
                action_scope = frozenset(object_names)
                if action_scope <= judgment_scope:
                    action_scope = frozenset(object_names) | {"o-extra"}
            elif spoil == "domain":
                others = [d for d in domain_names if d != domain]
                action_domain = rng.choice(others)
            elif spoil == "obligation":
                obligation_status = "UNKNOWN"
            elif spoil == "defeater":
                defeaters = frozenset({"d"})
            judgment = model.Judgment(
                issuer=issuer, domain=domain, scope=judgment_scope, epoch=epoch, valid=valid
            )
            action = model.Action(
                domain=action_domain, scope=action_scope, epoch=action_epoch
            )
            obligations = {"hard-1": obligation_status}
        else:
            trusted = frozenset(name for name in issuer_names if rng.random() < 0.5)
            judgment = model.Judgment(
                issuer=rng.choice(issuer_names),
                domain=rng.choice(domain_names),
                scope=frozenset(name for name in object_names if rng.random() < 0.6),
                epoch=rng.randint(0, 2),
                valid=rng.random() < 0.8,
            )
            action = model.Action(
                domain=rng.choice(domain_names),
                scope=frozenset(name for name in object_names if rng.random() < 0.6),
                epoch=rng.randint(0, 2),
            )
            obligations = {"hard-1": "SAT" if rng.random() < 0.75 else "UNKNOWN"}
            defeaters = frozenset({"d"} if rng.random() < 0.15 else set())

        expected = model.authorize(
            judgment,
            action,
            trusted_issuers=trusted,
            conversions=conversions,
            hard_obligations=obligations,
            active_defeaters=defeaters,
        )

        # Close the world: Conv holds exactly on the drawn edges, Trusted exactly
        # on the drawn issuers. Without closure the solver may invent an edge and
        # the two sides would be answering different questions.
        left, right = solver_module.Consts("cl cr", sig.Domain)
        edge_disjunction = solver_module.Or(
            *[
                solver_module.And(left == domain_consts[a], right == domain_consts[b])
                for a, b in sorted(conversions)
            ]
        ) if conversions else solver_module.BoolVal(False)
        who = solver_module.Const("who", sig.Issuer)
        trusted_disjunction = solver_module.Or(
            *[who == issuer_consts[name] for name in sorted(trusted)]
        ) if trusted else solver_module.BoolVal(False)
        world = [
            *axioms,
            *distinct,
            solver_module.ForAll([left, right], sig.Conv(left, right) == edge_disjunction),
            solver_module.ForAll([who], sig.Trusted(who) == trusted_disjunction),
        ]

        ground = authorize(
            sig,
            valid=solver_module.BoolVal(judgment.valid),
            issuer=issuer_consts[judgment.issuer],
            judgment_domain=domain_consts[judgment.domain],
            judgment_scope=_scope_term(sig, judgment.scope, object_consts),
            judgment_epoch=solver_module.IntVal(judgment.epoch),
            action_domain=domain_consts[action.domain],
            action_scope=_scope_term(sig, action.scope, object_consts),
            action_epoch=solver_module.IntVal(action.epoch),
            obligations_all_sat=solver_module.BoolVal(
                all(status == "SAT" for status in obligations.values())
            ),
            defeater_active=solver_module.BoolVal(bool(defeaters)),
        )

        claim = ground if expected else solver_module.Not(ground)
        outcome = discharge(
            Theorem(
                name=f"DIFFERENTIAL_{trial}",
                statement="the formula agrees with the executable model on this world",
                why_it_matters="a proof about the wrong sentence proves nothing",
            ),
            world,
            claim,
            timeout_ms=10000,
        )
        if outcome.discharged:
            agreements += 1
        else:
            disagreements.append(
                f"trial {trial}: python said {expected}, solver said {outcome.outcome.value}"
            )
        if expected:
            authorised_trials += 1

    return DifferentialReport(
        trials=trials,
        agreements=agreements,
        disagreements=tuple(disagreements),
        positive_trials=authorised_trials,
    )


def _scope_term(sig: Signature, members: Any, object_consts: dict[str, Any]) -> Any:
    """Build a ground set term for a concrete scope."""

    solver = require_z3()
    term = solver.EmptySet(sig.Obj)
    for name in sorted(members):
        term = solver.SetAdd(term, object_consts[name])
    return term


# ---------------------------------------------------------------------------
# The chain theorem
# ---------------------------------------------------------------------------


def prove_chain_ladder(*, bound: int = CHAIN_LADDER_BOUND, timeout_ms: int = 20000) -> tuple[ProofResult, ...]:
    """Expand the chain theorem explicitly at each length up to ``bound``.

    :data:`ONE_STEP_LEMMA` plus induction on chain length gives the general
    result, and the induction schema is the one meta-level step in this
    development. Discharging the fully expanded statement at each concrete
    length does not replace the schema --- no finite ladder does --- but it does
    mean the general claim is corroborated at concrete lengths rather than
    resting on the schema alone, and a mistake in the expansion would show up
    here rather than in a reader's trust.
    """

    solver = require_z3()
    sig = signature()
    axioms = closure_axioms(sig)
    results: list[ProofResult] = []

    for length in range(1, bound + 1):
        domains = [solver.Const(f"chain_dom_{i}", sig.Domain) for i in range(length + 1)]
        scopes = [solver.Const(f"chain_scope_{i}", sig.Scope) for i in range(length + 1)]
        action_domain = solver.Const("chain_adom", sig.Domain)
        action_scope = solver.Const("chain_ascope", sig.Scope)

        links = []
        for i in range(length):
            links.append(solver.IsSubset(scopes[i + 1], scopes[i]))
            links.append(sig.Reach(domains[i], domains[i + 1]))
        final = [
            solver.IsSubset(action_scope, scopes[length]),
            sig.Reach(domains[length], action_domain),
        ]
        claim = solver.Implies(
            solver.And(*links, *final),
            solver.And(
                solver.IsSubset(action_scope, scopes[0]),
                sig.Reach(domains[0], action_domain),
            ),
        )
        results.append(
            discharge(
                Theorem(
                    name=f"CHAIN_NON_AMPLIFICATION_{length}",
                    statement=(
                        f"a delegation chain of length {length} confines the action's scope to "
                        "the root judgment's scope and its domain to the root's reach"
                    ),
                    why_it_matters=(
                        "the expanded form of the induction the one-step lemma supports"
                    ),
                ),
                axioms,
                claim,
                timeout_ms=timeout_ms,
            )
        )
    return tuple(results)


def build_report(repo_root: Any, *, differential_trials: int = 400) -> dict[str, object]:
    """Everything this module establishes, with what it does not establish."""

    theorems = prove_all()
    ladder = prove_chain_ladder()
    differential = differential_check(repo_root, trials=differential_trials)
    all_proofs = (*theorems, *ladder)
    undischarged = [r.theorem.name for r in all_proofs if not r.discharged]

    return {
        "schema_version": SCHEMA_VERSION,
        "record": "P8_AUTHORITY_CALCULUS_MECHANIZED",
        "solver": z3.get_version_string() if z3 is not None else None,
        "theorems": [r.as_json() for r in theorems],
        "chain_ladder": {
            "bound": CHAIN_LADDER_BOUND,
            "results": [r.as_json() for r in ladder],
        },
        "differential_against_executable_model": differential.as_json(),
        "all_discharged": not undischarged,
        "undischarged": undischarged,
        "not_licensed": [
            "any claim that the 13 donor types or the 39,936-state instance are "
            "hereby re-derived; deriving those as instances of this calculus is a "
            "separate piece of work",
            "any claim of independent formal review; these proofs have been checked "
            "by a solver, not reviewed by a person outside this lane",
            "any empirical or systems claim whatsoever",
        ],
        "axioms_are_definitional": (
            "reachability is axiomatised as the reflexive-transitive closure by the "
            "four clauses in closure_axioms, including a well-founded rank on "
            "justification. Transitive closure is not first-order definable, so those "
            "clauses are the definition used here and are not derived from anything "
            "more primitive."
        ),
        "induction_is_meta": (
            "the chain theorem holds for unbounded length by induction on the "
            "one-step lemma. The step is machine-checked; the induction schema is "
            "standard and is the single hand step in this development."
        ),
    }


def main(argv: list[str]) -> int:
    """CLI entry point. ``argv`` is required: there is no implicit run."""

    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="orion-p8-authority-calculus",
        description="Discharge P8's authority calculus over arbitrary delegation graphs.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--differential-trials", type=int, default=400)
    args = parser.parse_args(argv)

    report = build_report(args.repo_root, differential_trials=args.differential_trials)
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"written: {args.output}")

    for item in report["theorems"]:
        print(f"  {item['outcome']:15s} {item['name']}")
    ladder = report["chain_ladder"]["results"]
    print(f"  chain ladder: {sum(1 for r in ladder if r['outcome'] == 'PROVED')}/{len(ladder)} proved")
    diff = report["differential_against_executable_model"]
    print(
        f"  differential: {diff['agreements']}/{diff['trials']} agree, "
        f"{diff['positive_trials']} authorised"
    )
    # Same split as the chain-composition CLI, for the same reason: the repo
    # reserves 3 for "could not check" (scripts/audit_manuscript_clipping.py)
    # and 2 for a finding. A refuted theorem is a finding about this calculus;
    # an undecided solver is a measurement that was not taken.
    if not report["all_discharged"]:
        graded = (*report["theorems"], *report["chain_ladder"]["results"])
        refuted = [i["name"] for i in graded if i["outcome"] == "COUNTEREXAMPLE"]
        undecided = [i["name"] for i in graded if i["outcome"] == "UNKNOWN"]
        if refuted:
            print(f"REFUTED: {refuted}")
            if undecided:
                print(f"  (also undecided, and not counted as refuted: {undecided})")
            return 2
        print(f"CANNOT CHECK: Z3 returned UNKNOWN for {undecided}")
        return 3
    if not diff["agreed"] or not diff["exercised_both_verdicts"]:
        print("DIFFERENTIAL DID NOT ESTABLISH AGREEMENT ON AN INFORMATIVE CORPUS")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
