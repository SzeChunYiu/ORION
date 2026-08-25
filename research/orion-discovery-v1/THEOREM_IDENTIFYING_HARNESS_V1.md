# Theorem-Identifying Harnesses V1

**Status:** prospective foundations successor.  
**Trigger:** repeated non-vacuity defects discovered during the completed #1234 execution wave.  
**Authority:** definitions and proofs for declared finite classes; no external scientific authority.

## 1. Problem

A conventional scientific harness asks whether a target implementation agrees with an evaluator on a set of cases.

That is insufficient. A harness can agree perfectly because:

- every case has the same terminal;
- the hard precondition never occurs;
- the evaluator computes its answer from the candidate output;
- a theorem premise is inserted into the generator by construction;
- the comparison class is too small for the algorithms to diverge;
- the outcome is hard-coded into an observable flag;
- a missing clause has no effect anywhere in the test support.

The correct question is:

> Does the harness induce observations that distinguish the target scientific claim from the strongest registered alternatives that would make the claim false, weaker, tautological, donor-equivalent, or vacuous?

## 2. Harness object

A scientific harness is

\[
\mathcal H=(G,S,E,A,C,K,\Gamma),
\]

where:

- `G` is a case/world generator;
- `S` is the frozen generated support or sampling law;
- `E` is the evaluator producing case-level observations;
- `A` is the aggregation/decision rule;
- `C` is the information, action, and resource contract;
- `K` is custody and chronology;
- `Γ` is the registered alternative-claim family.

A **claim model** `θ` determines the outcome that should be observed on each eligible case:

\[
O_\theta:S\to\mathcal Y.
\]

Examples of alternatives include:

- delete one theorem premise;
- replace the target with a constant-true or constant-false rule;
- replace an exact algorithm with a heuristic;
- define the reference object from the candidate;
- erase one authority, scope, epoch, or blocker coordinate;
- admit a hedge action;
- provide an information-equivalent donor implementation;
- use an outcome-leaking generator.

The harness signature of `θ` is

\[
\operatorname{Sig}_{\mathcal H}(\theta)
=(O_\theta(s))_{s\in S},
\]

or its probability law when `S` is sampled.

## 3. HIF-T1 — claim identifiability theorem

### Statement

For a finite alternative family `Γ`, the harness identifies the target `θ₀` relative to `Γ` if and only if

\[
\forall\theta\in\Gamma\setminus\{\theta_0\},
\quad
\operatorname{Sig}_{\mathcal H}(\theta)
\ne
\operatorname{Sig}_{\mathcal H}(\theta_0).
\]

The entire family is identifiable if and only if the signature map is injective on `Γ`.

### Proof

If an alternative shares the target signature, no decision rule consuming only the harness observations can distinguish them. Conversely, if every alternative has a different signature, exact signature lookup identifies the target on the finite registered family. ∎

### Meaning

A result can be correct on every generated case and still fail to identify the theorem. Agreement is evidence only against alternatives the harness is capable of separating.

## 4. HIF-T2 — observational-equivalence impossibility

If two claim models satisfy

\[
\operatorname{Sig}_{\mathcal H}(\theta_1)
=
\operatorname{Sig}_{\mathcal H}(\theta_2),
\]

then every deterministic or randomized adjudicator using only the harness record has the same output distribution under both models.

No amount of rerunning the same non-identifying support can resolve the ambiguity. The remedy must change at least one of:

- generated worlds;
- observables;
- interventions;
- evaluator independence;
- alternative family;
- custody.

## 5. HIF-T3 — constant-terminal and mixed-outcome criterion

For a binary theorem property `p:S→{0,1}`, suppose every generated case has `p(s)=1`. Then the target property and the constant-true alternative have identical signatures.

Therefore a harness cannot establish that `p` discriminates unless it contains at least one eligible negative world or another observable on which the target and constant alternative differ.

Likewise, an all-negative suite cannot distinguish the target from constant false.

### Scope

Mixed outcomes are sufficient to kill constant alternatives, not sufficient for complete theorem identification. Other alternatives may still agree.

### ORION examples

- The first T16 grid had only the compiled-dominant phase.
- The first P10 T22 grids contained no UNSAT formulas.
- T19 imposed equal transcripts, so the indistinguishability outcome was constant by construction.

## 6. HIF-T4 — clause-necessity theorem

Let the target decision rule be represented by clauses `c₁,…,c_k`. Let `θ_{-i}` be the mutation obtained by deleting clause `c_i` while preserving the rest.

If

\[
\operatorname{Sig}_{\mathcal H}(\theta_{-i})
=
\operatorname{Sig}_{\mathcal H}(\theta_0),
\]

then the harness provides no evidence that `c_i` is necessary.

A **clause witness** for `c_i` is a case on which the target and deletion mutation differ. Every claimed necessary clause requires at least one bound clause witness, or an independent formal proof outside the harness.

This gives a precise mutation-testing interpretation to OSTC factor independence and hostile premise deletion.

## 7. HIF-T5 — precondition-attainability theorem

Suppose a claim concerns an effect only on a precondition set

\[
P=\{s\in\mathcal S:q(s)=1\}.
\]

If the frozen support has

\[
S\cap P=\varnothing,
\]

then no statistic computed on `S` evaluates the conditional claim on `P`.

Reporting a value for the conditional estimand is unlicensed even if the implementation runs successfully.

### Consequences

- Presence of at least one UNSAT formula is a precondition for measuring SAT/UNSAT decision asymmetry.
- Presence of a greedy-suboptimal set-cover instance is a precondition for comparing greedy with exact minimum separation.
- Presence of both preserve and reopen cases is a precondition for testing a transport policy that claims to distinguish them.
- Presence of clean valid cases is a precondition for showing that a safety gate is not merely an always-refuse policy.

A harness protocol must classify each load-bearing precondition as:

```text
PROVED_BY_CONSTRUCTION
CHECKED_BEFORE_SCORING
OBSERVED_AFTER_SCORING_INVALID
CANNOT_CHECK
```

Only the first two permit the estimand to be reported as tested.

## 8. HIF-T6 — independent-reference construction

Let the claimed relation be `R(f,g)` between primitive transformations `f,g` and a declared reference composite `h`.

If the harness defines

\[
h:=g\circ f
\]

and then tests whether `h=g∘f`, the result is definitionally true and identifies no compositional law.

More generally, if the evaluator reference is a deterministic function of the exact candidate output it is meant to judge, any agreement theorem must prove that the function does not encode the target relation.

A noncircular reference must arise through at least one of:

- an independently generated object;
- an independently implemented semantics;
- a protected gold process that does not consume candidate decisions;
- a theorem proved from primitives without importing the candidate result;
- a perturbation family capable of disagreeing.

This formalizes the repair made in `EXEC-CM-01`, where the declared composite was enumerated independently and included single-point perturbations.

## 9. HIF-T7 — observable-cause requirement

A causal or adversarial variable may not be both:

1. the hidden condition the system is supposed to detect; and
2. the direct Boolean used by the evaluator to count detection or failure.

Let hidden cause `U` generate observables `Y`. Detection must be a function of `Y`, not of `U` itself:

\[
\widehat U=d(Y),
\qquad
Y\sim P(\cdot\mid U).
\]

An evaluator that increments success from `U` directly measures construction membership, not detection.

This is the formal defect in the first P15 key-compromise probe. The repaired arm derives detection from an observable-signal set and permits both detected and undetected capability combinations.

## 10. HIF-T8 — alternative-family adequacy

A harness may identify a target relative to a weak `Γ` and fail relative to a stronger one.

Define the surviving equivalence class

\[
[\theta_0]_{\mathcal H,\Gamma}
=
\{\theta\in\Gamma:
\operatorname{Sig}_{\mathcal H}(\theta)
=
\operatorname{Sig}_{\mathcal H}(\theta_0)\}.
\]

The correct result is not simply PASS/FAIL but:

```text
TARGET_IDENTIFIED_RELATIVE_TO_GAMMA
TARGET_EQUIVALENT_TO_<alternatives>
ALTERNATIVE_FAMILY_INCOMPLETE
PRECONDITION_UNATTAINED
REFERENCE_CIRCULAR
CANNOT_CHECK
```

A new stronger donor, theorem mutation, or attack legitimately reopens the equivalence class without rewriting the prior bounded result.

## 11. HIF-T9 — mutation completeness is class-relative

Let `M` be a registered mutation family. A mutation score of one means

\[
\forall m\in M,
\quad
\operatorname{Sig}_{\mathcal H}(m)
e
\operatorname{Sig}_{\mathcal H}(\theta_0).
\]

It does not mean every false scientific claim is distinguishable. The result is only as broad as `M`.

A scientifically useful mutation family should include at least:

- constant-terminal mutations;
- premise deletion;
- scope/epoch/content erasure;
- authority widening;
- blocker clearing;
- hidden-answer construction;
- evaluator leakage;
- donor-equivalent implementation;
- resource/accounting asymmetry;
- adversarial hedge actions where losses are non-binary;
- circular reference construction;
- precondition-empty generators.

## 12. HIF-T10 — adaptive protocol separation

Let a protocol be frozen at time `t₀`. If the case family, gate, estimand, or alternative set is changed after observing the protected result, the successor is a new harness identity:

\[
\mathcal H_{t_1}\ne\mathcal H_{t_0}.
\]

The old terminal remains attached to `H_{t₀}`. The new design may be scientifically better, but it cannot retroactively convert the old outcome.

This is why:

- P9's post-hoc 5×6 probe is design evidence, not a replacement result;
- P10's ratio correction required `EXEC-P10-02` rather than editing the old family;
- T17 narrowing lives in a successor theorem record.

## 13. HIF-T11 — custody and prediction

A prediction tournament requires the predictor not to control the hidden outcomes after the prediction is frozen.

If the same principal can read or modify both prediction and outcome stores before opening, a hash proves chronology of the bytes it sees but does not create independent custody.

Therefore structural theorem verification and a prospective prediction tournament are distinct terminals. `EXEC-XP-01` verified T23's structural coupling but correctly left held-out prediction authority blocked.

## 14. Harness-identifiability vector

Every result-bearing harness should publish:

\[
I(\mathcal H)=
(I_{claim},I_{clause},I_{precondition},I_{reference},
I_{alternative},I_{origin},I_{custody},I_{external}).
\]

Where:

- `I_claim`: target separated from registered claim alternatives;
- `I_clause`: every claimed necessary factor has a witness or proof;
- `I_precondition`: all estimand preconditions attained before scoring;
- `I_reference`: evaluator reference independently constructed;
- `I_alternative`: donor/mutation family coverage;
- `I_origin`: benchmark construction does not encode the answer;
- `I_custody`: protected outcomes outside candidate control;
- `I_external`: authority independent of the programme where claimed.

These coordinates are non-compensatory. A million cases do not compensate for a circular evaluator, an empty hard stratum, or missing custody.

## 15. Theorem-Identifying Harness Receipt

Every future ORION scientific execution should emit:

```text
THEOREM_IDENTIFYING_HARNESS_RECEIPT.json
```

with at least:

```text
harness_id
subject_commit
claim_id
registered_alternative_ids
case_generator_id
eligible_case_count
precondition_counts
signature_digest_by_alternative
separated_alternative_ids
surviving_equivalence_class
clause_witness_map
constant_mutation_results
reference_construction_lineage
candidate_visible_fields
protected_fields
custody_owner
vacuity_guards
negative_terminal
CANNOT_CHECK_terminal
scope_ceiling
```

## 16. Programme-level theorem

### HIF Fundamental Theorem

For finite registered alternative family `Γ`, a complete, correctly computed harness signature is sufficient to identify the target relative to `Γ` exactly when the signature map is injective at the target.

No increase in repeats, seeds, model size, or compute can repair non-injectivity without changing the scientific observation channel.

This is the harness analogue of OSTC target sufficiency.

## 17. Novelty boundary

Mutation testing, identifiability, test adequacy, experimental design, statistical power, benchmark leakage analysis, and independent evaluation are established fields.

The candidate ORION residual is the integration of those fields with:

- typed scientific claim authority;
- explicit `CANNOT_CHECK` terminals;
- theorem-premise ownership;
- proposal-origin lineage;
- scientific support families and revocation;
- chronology-safe historical reconstruction;
- protected discovery and novelty authority.

The residual remains a novelty hypothesis until it survives #287 and external review.