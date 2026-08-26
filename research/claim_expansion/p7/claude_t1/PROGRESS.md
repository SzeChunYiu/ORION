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

## Milestone 3 — module written and green (2026-08-21)

`src/orion/study/p7/composition_calculus_smt.py` — ruff clean, runner works:

    PYTHONPATH=src python3 -m orion.study.p7.composition_calculus_smt --repo-root . --output <path>

All 18 theorems PROVED; chain ladder 8/8 (CHAIN_STEP_LEMMA + lengths 2..8);
differential 192/192 agree with 22 positive, both verdicts exercised;
50/50 committed composition rows discharged as ground instances;
bridge-soundness axiom pin: with_axiom=COUNTEREXAMPLE (no counterexample exists),
without_axiom=PROVED (one does) -> load-bearing.
Published counts all recompute: 320 / 25 / 31 / 155 / 1055 / 25 / 25.

THIRD TRAP (cost a real UNKNOWN): the chain ladder expanded straight from the
coordinate-transport axiom returns UNKNOWN at lengths 3,5,6,7,8 (only 2 and 4 close).
Fix: `prove_chain_ladder` re-discharges CHAIN_STEP_LEMMA from the axioms alone and,
only if that comes back PROVED, adds it as a hypothesis for the ladder -- then every
length closes in milliseconds. This is a lemma being used, not an axiom being added,
and the re-discharge is a gate so it cannot silently become the latter.

FOURTH POINT worth keeping: the finite structures assert BOTH the hand-built function
tables AND the axiom statements restated over the finite carrier, so z3 verifies the
construction is a model rather than trusting it. An independence result discharged
against a structure that was never a model would be worth nothing.

## Sharpest finding

MATCH_IS_NOT_NECESSARY's witness is not degenerate. z3 returns:
  Src t = k1, Tgt t = k0, Src u = k1, Tgt u = k1, Demands(k0,o) = Demands(k1,o) = True.
Both legs total, composite total, composite demands o -- and the checked rule REFUSES,
because k0 != k1 and no bridge was registered, even though k0 and k1 demand *exactly the
same obligations*. So P7's composition rule is sound but incomplete w.r.t. its own
obligation semantics, and the gap is precisely: the test asks whether a registrar
registered a bridge, not whether the obligations agree.
The exact side condition that does hold is CONTAINMENT (Demands(Src u) subset of
Demands(Tgt t)); match implies containment via bridge soundness.

## Next
- tests at tests/unit/study/p7/test_p7_composition_calculus_smt.py
- artifact under papers/paper-07-.../formal/mechanized/

## Milestone 4 — tests (2026-08-21)

`tests/unit/study/p7/test_p7_composition_calculus_smt.py`.
First run: 24 passed, 1 failed. The failure was informative and is now a documented
limitation rather than a worked-around test:

  `discharge` over the UNINTERPRETED signature returns UNKNOWN, not COUNTEREXAMPLE,
  on a false claim -- refuting a claim means building a model, and that is exactly
  what the quantified axioms defeat. No PROVED line is weakened (unsat is sound and
  a false claim cannot produce one), but the failure mode in the validity half is
  "not discharged", not "here is your countermodel". Countermodels ARE produced
  normally in the finite structures, which are decidable.

Now pinned by three tests: `discharge` on bare arithmetic -> COUNTEREXAMPLE;
uninterpreted false claim -> not PROVED (written to hold whether UNKNOWN or
COUNTEREXAMPLE); finite-world false claim -> COUNTEREXAMPLE. Plus
`test_a_false_independence_claim_is_refuted_not_proved` for the satisfiability
polarity, and `test_the_finite_structures_are_checked_against_the_axioms` which
corrupts one table entry and requires unsat.

## Answered a recorded open item

`research/failures/2026-08-supplied-premise-unbuilt-decision/` item 9 asks the theory
lane to "give the closure-carrying model a contract object, so `bridge_match` is
computed from the two transforms rather than typed. ... **not** done here."
It is done here: `Match(Tgt(t), Src(u))` is a function of the two transformations and
the registered bridge relation, so there is no argument left to supply. Recorded in
the report as `bridge_match_is_no_longer_a_supplied_premise`, with the explicit limit
that this does NOT repair the committed artifact, whose counts still come from an
expression containing no transform, contract or bridge.

## Ledger recommendation (draft — do NOT edit research/paper-programme-v1/*)

RECOMMEND: file as a **predecessor artifact**, grade `MECHANIZED_THEOREM`, exactly as
P6 and P8 were. NOT as gate evidence closing P7-U-T1 or P7-U-T2. Reasons, in order of
weight:

1. P7 differs from P6/P8 on the axis the parent used for those two, and differs in
   the STRONGER direction: the blocker's own `refs` name
   `research/claim_expansion/p7/P7_X2_CLOSURE_CARRYING_RESULT_V1.json`, and that IS the
   model proved about here (differential against its own `carries`/`compose`, 50
   committed composition rows discharged as ground instances, 320-row lift check,
   all published counts recomputed). So "the finite result came from a different
   model" does not apply. That is worth saying in the ledger note.

2. But the finite result is nearly empty, and deriving it does not make it full.
   The 25 successes and 25 missing-bridge cases are `compose(True,True,True)` and
   `compose(True,True,False)` evaluated 25 times each; neither donor is read. Closing
   P7-U-T2 on "derived as instances" would credit the calculus with re-deriving a
   substantive result. It re-derives two evaluations, 50 times, correctly.

3. The gap that P8-U-T1's rewritten statement names is the same gap here and is NOT
   closed: `Native` is uninterpreted, which is what makes the theorems general, and
   nothing proves that PLANNING_REFINEMENT / CEGAR_REFINEMENT / BIDIRECTIONAL_MIGRATION
   / WORLD_MODEL_REPLAN / TERMINAL_COMMITMENT are interpretations of these primitives
   with the closure coordinates P7 assigns them. Donor semantics -> calculus is the
   remaining formal step.

4. P7's OTHER formal core is untouched: the 64-state support-transport theorem
   (`papers/paper-07-.../formal/check_theory_closure_v2.py`, the paper's C4), which
   carries its own supplied-premise finding. The terminal rests on both.

5. A SUBTRACTION was produced and must travel with the artifact: P7's composition rule
   is proved **incomplete** with respect to its own obligation semantics. It refuses
   composites whose emitted and consumed contracts demand exactly the same obligations,
   merely because no bridge was registered. Fail-closed is the paper's stance, so this
   is a cost rather than a defect — but the ledger should not describe the rule as
   characterising composability when it characterises registered composability.

6. P7-U-T5 (independent formal or empirical reproduction) is untouched; these proofs
   were checked by a solver, not reviewed by a person outside this lane.

Suggested rewrite of P7-U-T1's `statement`, in P8-U-T1's style: say that identity,
associativity and intermediate-contract composition are now machine-checked over
uninterpreted sorts (P7_COMPOSITION_CALCULUS_MECHANIZED_2026-08-21), that the exact
side conditions are recorded (reflexivity of the contract test for identity;
extensionality for the strict laws; containment, not match, as the exact condition for
obligation-totality composition), and that what remains absent is the interpretation of
the five donor families as models of these primitives. Keep actionability
BLOCKED_ON_PROOF. Leave P7-U-T2 blocked, noting that its composition half is discharged
50/50 as instances but that the target is two evaluations.

## Milestone 5 — a fragility found, being fixed properly (2026-08-21)

Second pytest run: 27 passed, 1 failed —
`TestLoadBearingAxioms::test_strict_associativity_needs_extensionality`, where the
*with_axiom* half came back UNKNOWN at 30s. Measured standalone, the same query
takes 0.0s / 0.7s / 0.0s / 0.0s / 5.9s / 1.0s across six runs in one process.

So ASSOCIATIVITY_STRICT is genuinely marginal, and the fix must NOT be "raise the
timeout until it goes green". Cause: the Skolemized extensionality axiom is an
unguarded implication over two universally quantified transformations with no
e-matching trigger, so z3 falls back to expensive search and the cost swings.
Testing pattern variants (none / Src,Src / Diff / Src,Tgt / Holds(t,Diff(t,u)))
over 8 repeats each to pick a formulation that is fast AND stable.

If no variant is stable, the honest outcome is to report ASSOCIATIVITY_STRICT as
whatever the solver says on the day and lean on ASSOCIATIVITY_OBSERVABLE, which is
unconditional and closes instantly.

### Fixed, and fixed the right way

Benchmarked 6 repeats per variant (`/tmp/.../scratchpad/extbench.py`), claim =
strict associativity AND both strict unit laws, 8s budget:

    none        max=8.07s mean=4.05s outcomes={PROVED, UNKNOWN}   <- the fragility
    src         max=0.01s mean=0.01s outcomes={PROVED}            <- fix, chosen
    diff        max=8.07s mean=2.81s outcomes={PROVED, UNKNOWN}
    holdsdiff   max=8.08s mean=7.29s outcomes={PROVED, UNKNOWN}
    none+hint   max=0.01s mean=0.01s outcomes={PROVED}            (ground instance as hint)
    diff+hint   max=0.01s mean=0.01s outcomes={PROVED}

`src` = give the Skolemized extensionality axiom the e-matching trigger
`MultiPattern(Src(t), Src(u))`. Without a trigger the axiom has no head term to
fire on and z3 falls back to model-based instantiation; with it the axiom fires on
exactly the pairs the query mentions. Re-verified 10/10 PROVED at 0.006-0.010s.

Same axiom, same theory, same theorems. The timeout was NOT raised.

## Milestone 6 — the real fragility, and the real fix (2026-08-21)

Third pytest run: 27 passed, 1 failed — `TestScope` on `all_discharged is False`.
Bisected with an instrumented `discharge`. The culprit is **ASSOCIATIVITY_CARRIES**,
and it is not context accumulation. In a FRESH process, 4 runs:

    from the axioms alone   [(0.10,PROVED), (15.07,UNKNOWN), (0.25,PROVED), (15.08,UNKNOWN)]
    under the one-step lemma[(0.01,PROVED), (0.01,PROVED),  (0.00,PROVED), (0.01,PROVED)]

and 12/12 PROVED at 0.01s under the lemma across three levels of process load.

FIX (structural, not budgetary): the development now has **one hinge and three
corollaries**. `prove_hinge()` discharges INTERMEDIATE_CONTRACT_COMPOSITION from
`checker_axioms` alone; ASSOCIATIVITY_CARRIES,
UNMATCHED_INTERMEDIATE_CONTRACT_BLOCKS and COMPOSITION_NON_AMPLIFICATION are then
discharged under it, as is the chain ladder. The gate: the hinge must come back
PROVED before it is used; otherwise the corollaries run against the axioms alone
and report whatever the solver says.

A query that answers in 0.01s under a proved lemma and times out without it is a
query the solver is doing DIFFERENTLY, not one it is doing slowly. The timeout was
not raised. Same for the earlier extensionality trigger.

### Stability after the fix

5 consecutive `build_report` runs, then 4 more after also routing the ground-world
queries through the gated hinge:

    undischarged: []  diff 80/80  instances 0 undischarged   (every run)
    worst query: 2.59s INSTANCE, 1.26s INTERMEDIATE_CONTRACT_COMPOSITION,
                 0.39s DIFFERENTIAL, everything else <= 0.04s
    full build_report: 7.3-12.9s (was 15-20s)

Budgets unchanged (30s theorems, 10s ground queries); margins are now 10x+.

### Second fragility, same shape, same kind of fix

After routing the ground-world queries through the gated hinge, the ONE remaining
unstable query was the hinge itself (13.62s worst against a 30s budget in a loaded
process). Benchmarked 8 runs per variant:

    v1  biconditional, one query          max=1.19s mean=0.22s   (13.6s under load)
    v2  two implications, one query each  max=0.18s mean=0.07s   <- chosen
    v3  extra AllHold predicate, iff      max=3.14s mean=0.62s
    v4  extra AllHold predicate, split    max=0.67s mean=0.22s

`prove_hinge` now discharges `A -> B` and `B -> A` in separate solver calls and
reports PROVED only if both are; the combination is the propositional step from
two implications to a biconditional. Reason: as one query the biconditional
negates to a disjunction the solver must case-split.

Final stability, 5 consecutive full `build_report` runs:
    undischarged [] every run, diff 80/80 every run, 0 undischarged instances
    worst query 0.71s INTERMEDIATE_CONTRACT_COMPOSITION, next 0.05s, rest <= 0.03s
    full report 7.3-8.0s
Budgets never raised. ~40x margin now.

## Milestone 7 — GREEN (2026-08-21)

    pytest tests/unit/study/p7/test_p7_composition_calculus_smt.py -q
    30 passed in 82.63s

Artifact written:
    papers/orion-17-epistemic-navigation-open-worlds/formal/mechanized/
        P7_COMPOSITION_CALCULUS_MECHANIZED_2026-08-21.json

    18/18 theorems PROVED
    chain ladder 8/8 (CHAIN_STEP_LEMMA + lengths 2..8)
    differential 192/192 agree, 22 positive, both verdicts exercised
    instances 50/50 committed composition rows
    bridge-soundness axiom load-bearing: True

## Milestone 8 — DONE (2026-08-21)

Deliverables:
1. research/claim_expansion/p7/claude_t1/PROGRESS.md          (this file)
2. src/orion/study/p7/composition_calculus_smt.py             (ruff clean)
3. papers/orion-17-epistemic-navigation-open-worlds/formal/mechanized/
       P7_COMPOSITION_CALCULUS_MECHANIZED_2026-08-21.json
4. tests/unit/study/p7/test_p7_composition_calculus_smt.py    (30 passed, ruff clean)

Regression: tests/unit/study/p6/test_p6_separation_calculus_smt.py +
tests/unit/candidates/test_p8_authority_calculus_smt.py -> 22 passed. Nothing shared
was touched; `orion/programme/mechanized.py` is unmodified.

No committed P7 result, receipt or evidence artifact was edited. The only file added
under a paper directory is the new mechanized/ JSON (stales P7's content binding, as
expected).

FINAL NUMBERS (with denominators)
  theorems                18/18 PROVED
  chain ladder             8/8  (CHAIN_STEP_LEMMA + lengths 2..8)
  differential           192/192 agree; 22/192 positive; both verdicts exercised
                          = 64 exhaustive closure-lift rows
                          + 8 exhaustive compose() argument triples
                          + 120 randomised composites
  committed instances     50/50 ground instances discharged (25 bridged + 25 unbridged)
  committed unit rule    320/320 rows are the closure lift; 5/320 positive
  published counts        7/7 recompute exactly (320/25/31/155/1055/25/25)
  bridge-soundness pin    with axiom: no counterexample (unsat);
                          without axiom: counterexample exists -> load-bearing
