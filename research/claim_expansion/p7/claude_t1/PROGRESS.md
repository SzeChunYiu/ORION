# P7-U-T1 / P7-U-T2 lift — progress

## Status: STARTED (reading phase)

## Task
- P7-U-T1: no general compositional calculus/checker; 25 successful compositions vs 25
  matched missing-bridge cases is a registered navigation model, not a calculus.
  Unblock: define primitive transformation + obligation semantics, then prove or
  explicitly characterize identity, associativity, intermediate-contract composition.
- P7-U-T2: current P7 results cannot be instances of a calculus that does not exist.
  Unblock: derive the finite results as instances once mechanized.

## Done
- Read `src/orion/programme/mechanized.py` (harness: Theorem, ProofResult, ProofOutcome,
  discharge, DifferentialReport, load_executable_model).
- Read `src/orion/study/p6/separation_calculus_smt.py` (converse by satisfiability;
  instantiation_check turning bounded enumeration into instance).
- Read `src/orion/study/p8/authority_calculus_smt.py` (chain ladder + induction;
  closure_axioms with well-founded rank; differential_check with both-verdict corpus).

## Next
- Find P7 executable model in papers/paper-07-.../formal/.

## Milestone 1 — P7's executable model located (2026-08-21)

The model behind P7-U-T1 is **`research/claim_expansion/p7/check_p7_x2_closure_carrying.py`**
(the ledger's `refs` for P7-U-T1 name `research/claim_expansion/p7/P7_X2_CLOSURE_CARRYING_RESULT_V1.json`,
which that script prints). It is TWO functions:

    def carries(native_valid: bool, closure: tuple[bool, ...]) -> bool:
        return native_valid and all(closure)

    def compose(c1: bool, c2: bool, bridge_match: bool) -> bool:
        return c1 and c2 and bridge_match

The 25/25 numbers come from:

    for d1 in DONORS:            # 5
        for d2 in DONORS:        # 5
            c1 = carries(True, full); c2 = carries(True, full)
            assert compose(c1, c2, True);       composition_successes += 1
            assert not compose(c1, c2, False);  composition_bridge_countermodels += 1

Neither donor is read. `c1 == c2 == True` always. So the published 25 + 25 is
**one fact counted 25 times, at 2 of the 8 argument triples of `compose`**.
This is already recorded by `src/orion/study/p7/closure_premises.py` (a prior lane).

`papers/paper-07-.../formal/check_countermodels.py` and `check_theory_closure_v2.py`
are the *other* P7 formal core (transport theorem, 64 states). They are NOT the
compositional model P7-U-T1 names. check_countermodels has no composition operator.

Registered semantics from `research/claim_expansion/p7/P7_X2_CLOSURE_CARRYING_THEOREMS_V1.md`:
- `ClosureCarries(T,o) := DonorPreserves(T) AND all(o)`   (the "closure lift")
- T5: `T1:A->B` and `T2:B->C` compose closure-carryingly only when T1's emitted
  target obligation contract is exactly T2's consumed source contract, **or a
  registered bridge witnesses their equivalence**.

## Design (independent of the theorems)

Two layers, one signature, two axiom sets.

LAYER B — the checked calculus (what the code computes, generalised):
  sorts Trans, Contract, Coord (all uninterpreted -> any number of transforms,
  contracts, closure coordinates; not the 5 authored ones)
  Native : Trans -> Bool                (donor-native validity; uninterpreted --
                                         "P7 does not alter that predicate")
  Holds  : Trans x Coord -> Bool
  Carries(t) :== Native(t) AND forall c. Holds(t,c)          [the closure lift, verbatim]
  Src,Tgt : Trans -> Contract
  Bridge  : Contract x Contract -> Bool  (registered; uninterpreted)
  Match(a,b) :== a = b OR Bridge(a,b)                        [T5, verbatim]
  Comp : Trans x Trans -> Trans, Id : Contract -> Trans
  structural axioms: Src(Comp(t,u))=Src(t); Tgt(Comp(t,u))=Tgt(u);
                     Native(Comp(t,u)) <-> Native(t) AND Native(u)
  coordinate transport: distinguished coord `Totality`;
       Holds(Comp(t,u),Totality) <-> Holds(t,Tot) AND Holds(u,Tot) AND Match(Tgt t,Src u)
       c != Totality:  Holds(Comp(t,u),c) <-> Holds(t,c) AND Holds(u,c)
  identity axioms: Src(Id a)=Tgt(Id a)=a; Native(Id a); forall c. Holds(Id a, c)
  optional declared axiom: extensionality (transforms equal when observationally equal)

  => Carries(Comp(t,u)) <-> Carries(t) AND Carries(u) AND Match(...) is a THEOREM,
     not an axiom -- and it is exactly P7's `compose`.

LAYER A — obligation semantics (why Match is the right test, and where it isn't):
  Obl sort; Demands : Contract x Obl -> Bool; Discharged, New : Trans x Obl -> Bool
  Total(t) :== forall o. Demands(Tgt t,o) -> (Demands(Src t,o) OR Discharged(t,o) OR New(t,o))
       [= `obligations_total`, verbatim from the theorem doc]
  bridge soundness axiom: Bridge(a,b) -> forall o. Demands(a,o) <-> Demands(b,o)
       ["a registered bridge witnesses their equivalence"]
  composite obligation axioms: Discharged(Comp) = or; New(Comp) = or
  => Total composes under Match (sufficiency), but Match is NOT necessary:
     the exact condition is CONTAINMENT  forall o. Demands(Src u,o) -> Demands(Tgt t,o).
     So P7's rule is SOUND but INCOMPLETE (fail-closed) w.r.t. the obligation semantics.

## Next
- Write src/orion/study/p7/composition_calculus_smt.py, prototype in scratchpad first.

## Milestone 2 — SMT prototypes all pass (scratchpad)

Validated in `/tmp/.../scratchpad/proto2,4,7,8.py`:

Layer B over UNINTERPRETED sorts (validity / unsat-of-negation):
  IDENTITY_CARRIES, COMPOSITION_SOUNDNESS, LEFT_IDENTITY_CARRIES,
  RIGHT_IDENTITY_CARRIES, ASSOC_OBSERVABLE, ASSOC_CARRIES, UNMATCHED_FAILS,
  NON_AMPLIFICATION  -> all PROVED.
  IDENTITY_STRICT_LEFT/RIGHT, ASSOC_STRICT (under Skolemized extensionality) -> PROVED.

Layer A over uninterpreted sorts:
  TOTALITY_COMPOSES_UNDER_MATCH, CONTAINMENT_IS_THE_EXACT_CONDITION -> PROVED.

TRAP FOUND (worth recording): satisfiability queries over uninterpreted sorts with
quantified axioms come back UNKNOWN (timeout) every time -- MBQI will not build the
model. Fix: every countermodel/independence result is checked in an explicitly
constructed CLOSED FINITE structure (EnumSort carrier, function tables asserted as
ground equations, axioms asserted over the finite carrier so z3 still verifies them).
All four finite countermodels run in <0.2s:
  IDENTITY_FAILS_WITHOUT_REFLEXIVE_MATCH        sat  (and unsat with reflexive Match)
  ASSOC_STRICT_FAILS_WITHOUT_EXTENSIONALITY     sat  (tagged carrier: Comp(x,y) carries
                                                      a tag flipped from x's, so the two
                                                      bracketings differ while every
                                                      observable agrees)
  MATCH_IS_NOT_NECESSARY                        sat  (and MATCH_SUFFICES unsat)
  CONTAINMENT_FAILURE_COUNTERMODEL              sat
  WITHOUT_BRIDGE_SOUNDNESS_MATCH_FAILS          sat  (axiom pin)

Second trap: `Carries` must be a DECLARED z3 function with a definitional axiom and an
explicit e-matching pattern. Written as an inline macro `And(Native(t), ForAll([c],
Holds(t,c)))` three of the eight Layer-B theorems time out to UNKNOWN. Same for
Total/SameDemands. Recorded because it is the same shape as P8's rank trap: the
formulation, not the claim, was what the solver could not do.

## Next
- Write the module + differential + result artifact + tests.
