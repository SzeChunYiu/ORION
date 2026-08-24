# P1–P15 paper theorem proofs V1

This appendix closes the paper-level theorem derivations. Each proof is conditional on the formal object and assumptions stated in `PAPER_THEOREM_PACKAGES_V1.md`. Empirical work tests whether external domains instantiate those assumptions; it does not supply the missing mathematics.

---

# P1 proofs

## P1-T1 — formulation insufficiency

A mixed cell of `Π_f` contains `ω,ω'` with equal formulation observables and different responsibility terminals. Every formulation-only policy returns one value on that cell and is wrong on at least one world. This is OSTC-T2.

## P1-T2 — minimal repair

`Rep_r(f)` is an upset because adequacy is preserved under partition refinement. In a finite poset, every nonempty upset has a minimal element. By minimality, no strict predecessor above `f` remains in the upset. Under the closure-operator assumption, extensivity gives `f≤cl_r(f)`, adequacy makes it a repair, and the principal-upset condition makes it below every repair; uniqueness follows by antisymmetry.

## P1-T3 — attribution identifiability

Restrict the intervention-response matrix to selected columns. Equal rows induce identical observation distributions and cannot be distinguished. Distinct rows define an inverse lookup from response signatures to causes. Minimum separation is a hitting-set instance over cause pairs and intervention columns.

## P1-T4 — recursive termination

An infinite adopted sequence would induce an infinite strict descent in the declared well-founded rank. This contradicts well-foundedness. OSTC-T21 gives the natural-number special case.

## P1-T5 — protected adoption

OSTC-T19 constructs a genuine and a gaming world with identical candidate-controlled evidence. Therefore proposal-local evidence cannot authorize adoption. The P5 evolution certificate supplies the missing protected root.

---

# P2 proofs

## P2-T1 — closure impossibility

Apply OSTC-T12 to the finite observable history and the Boolean task-closure terminal. Equal histories and different truth values defeat every history-only rule.

## P2-T2 — bounded-universe closure

Enumerate the finite protected registry `U`. Materiality and discharge are decidable by assumption. Task closure is the finite proposition `∀u∈U, Material(u)→Discharged(u)`, hence decidable. Soundness and completeness follow directly from the definition of the protected universe.

## P2-T3 — capture-model certificate

The certificate is a conditional theorem of the adopted statistical model: if the data-generating/censoring/dependence assumptions hold and the estimator’s coverage theorem applies, its interval or bound covers the residual target at the stated level. When transport assumptions fail, the premises are absent, so OSTC-T5 prohibits promotion of the certificate.

## P2-T4 — stopping hierarchy

Task closure quantifies over every mandatory route, so each mandatory route has no unresolved material obligation. The converse fails by adding an unobserved mandatory route. Population completeness plus materiality/processing coverage implies task closure by universal instantiation; without processing coverage it does not.

---

# P3 proofs

## P3-T1 — gluing existence

A global portrait is defined as an object with maps satisfying all diagram equations. Therefore existence is equivalent to satisfiability of the finite compatibility system. This is a representation theorem, not a computational claim about how the solution is found.

## P3-T2 — uniqueness

Let two global portraits induce equal local projections. Joint monicity says equality of all projections implies a unique isomorphism/equality of the global objects. Hence uniqueness up to the chosen notion of isomorphism.

## P3-T3 — pairwise/global separation

Use a three-object cycle with transition labels whose pairwise equations are satisfiable but whose composite is a nonidentity automorphism while the cycle law requires identity. Every edge is locally consistent; the full cycle is not. Thus pairwise compatibility is insufficient.

## P3-T4 — obstruction preservation

If the cone set is empty, any emitted global portrait would be a solution to an unsatisfiable system, contradiction. If the cone set has several non-isomorphic elements, a unique portrait cannot be inferred without a new selection principle. Therefore the sound terminals are obstruction/plurality/`CANNOT_CHECK`.

## P3-T5 — representation invariance

Two implementations exposing the same diagram quotient and compatibility equations factor every target judgment through that common quotient. OSTC-T9 makes their decisions extensionally equal.

---

# P4 proofs

## P4-T1 — evaluator attainability

OSTC-T2.

## P4-T2 — irreducible target risk

Decompose expected 0–1 loss by evaluator fibre. Decisions on different fibres are independent; the modal target minimizes each fibre’s error. Sum total fibre mass minus modal mass. Randomization cannot improve a linear objective beyond an extreme point.

## P4-T3 — data processing

`G∘Φ` identifies at least every pair identified by `Φ`, so its partition is coarser. Any decoder for `G∘Φ` is also a decoder from `Φ` via composition, hence the optimal risk from `Φ` is no larger.

## P4-T4 — promotion normal form

This is the four-factor quotient of SANF soundness/completeness after availability and target-required execution integrity are fixed. T6 gives sufficiency; T7 gives necessity for `W-dagger`.

## P4-T5 — nuisance identifiability

If the label is determined by nuisance within competence classes, systems can achieve benchmark success without resolving competence. Construct matched cases with equal nuisance and different competence; absence of such matches makes the competence relation nonidentifiable from the benchmark interface.

---

# P5 proofs

## P5-T1 — reflexive custody impossibility

OSTC-T19.

## P5-T2 — protected adoption sufficiency

Replay the evolution certificate: bind candidate and evaluator chronology, check isolation/replay/fresh transfer, protected assurance, history update, and external grant. These enable the operational `ADOPT_EXTERNAL` rule, so SANF soundness yields adoption within the declared class.

## P5-T3 — sequential false-adoption control

This theorem imports the exact guarantee of the frozen donor sequential-testing procedure. Since candidate selection may be adaptive but the donor guarantee is valid under that filtration/custody model, accepted candidates inherit the bound. No stronger guarantee is claimed.

## P5-T4 — causal credit

Under matched subject, evaluator, resources, and task distribution, randomization or an identified causal design makes the intervention the differing parent of the outcome. If several factors differ or intervention signatures collide, attribution is set-valued by OSTC-T14.

## P5-T5 — termination/history

OSTC-T21 proves termination. Append-only rejected/harmful history adds constraints that exclude exactly registered recurrent variants; it does not prove exclusion of unrepresented failure classes.

---

# P6 proofs

## P6-T1 — certificate survival

By OSTC-T11, a judgment survives exactly when one complete support family is disjoint from revoked/invalidated premises. Coordinate change invalidates precisely the bridge premises depending on changed coordinates by the declared dependency semantics.

## P6-T2 — selective revalidation

Revalidating the full backward slice restores every affected premise in the single support family, so the derivation replays. Omitting a load-bearing affected node admits a compatible semantics in which that premise is false while all others are true; the target cannot be derived.

## P6-T3 — alternative-support repair

With alternatives, a target is restored iff one family becomes complete. Therefore repair selection is exactly a search over families and actions covering their invalid premises. Full reset is one feasible solution, not generally minimal.

## P6-T4 — NP-hardness

Given set-cover instance `(U,S_1,…,S_m)`, create one invalid obligation per `u∈U` and one repair action per `S_i` that restores the obligations it contains. A target support family is complete iff every obligation is restored. A repair of size `k` exists iff a cover of size `k` exists.

## P6-T5 — mechanic commutation

Use induction on the state coordinates. Noninterfering read/write frames ensure each mechanic reads the same values in either order and writes disjoint/equivalent outputs. History traces differ only by swapping independent events, giving trace equivalence. A read-after-write dependency supplies the converse countermodel.

---

# P7 proofs

## P7-T1 — transport soundness

Transport each SANF witness through the regime morphism. Preserved coordinates remain valid; changed coordinates require bridge witnesses. If one load-bearing coordinate lacks preservation/bridge, factor independence T8 supplies a matched failure.

## P7-T2 — coherence

OSTC-T10 composes matching certificates. Commuting transport squares make the two composed witness maps equal up to isomorphism; structural induction over the certificate yields path equality.

## P7-T3 — path dependence

If one square fails, choose a witness supported on that coordinate. The two paths map it to different obligations/evidence meanings/terminals. Thus the composed certificates cannot be identified and closure must reopen.

## P7-T4 — maximal sound abstraction

Let an abstract cell be accepted only if every concrete member is closed. This rule is sound. Any more permissive rule accepts some mixed cell containing an open state and is unsound. Therefore it is the greatest sound rule ordered by accepted-cell inclusion.

## P7-T5 — opacity price

Closed states inside mixed cells cannot be accepted by any sound abstract rule, by T4. Their probability mass is therefore the irreducible false-refusal mass. Refining the abstraction can reduce the price only by splitting mixed cells.

---

# P8 proofs

## P8-T1 — no amplification

OSTC-T4/T5, with the authority type preorder enforcing that ordinary rule conclusions are no broader than their premises.

## P8-T2 — permission/discharge separation

Construct an action with valid local grant but evidence of the wrong scientific scope; action permission is true and discharge false. Conversely, deny an action to one principal while an independently supported proposition remains true. Hence neither relation is the inverse of the other.

## P8-T3 — coercion composition

OSTC-T10. Type matching supplies the intermediate contract; authority attenuation composes transitively. Missing type or protected-root premises makes composition undefined.

## P8-T4 — exact revocation

OSTC-T11.

## P8-T5 — decentralized equivalence

Apply OSTC-T9 to the common typed state and bridge semantics. Operational organization does not change the quotient decision relation.

## P8-T6 — cycle safety

For a finite positive monotone rule graph, least-fixed-point iteration is well-defined. If cycle edges are attenuating, no iteration creates broader authority. Cycles with implicit widening violate T4 and are rejected. Nonmonotone cycles require an additional stable/fixed-point semantics and lie outside the base class until supplied.

---

# P9 proofs

## P9-T1 — diagnosis identifiability

OSTC-T14.

## P9-T2 — NP-hard minimum design

Create a universe of cause pairs. Each intervention covers the pairs it separates. Selecting interventions separating all pairs is exactly set cover/hitting set.

## P9-T3 — access deficiency

Define deficiency as the supremum, over registered responsibilities/losses, of optimal-risk difference between the candidate and reference interfaces. Nonnegativity follows because reference decisions are at least as informative under the comparison assumption. Zero deficiency means equal optimal risk for the family, not universal information equality.

## P9-T4 — compute non-substitution

A mixed interface fibre feeds identical input to every computation that acquires no new information. Determinism/randomization cannot choose different correct terminals for both worlds beyond the Bayes bound. OSTC-T2/T3.

## P9-T5 — vector accounting

A comparison under vector dominance is invariant to arbitrary post-hoc scalar weights. Scalar ranking is defined only after a price vector is fixed; otherwise incomparable vectors remain Pareto-incomparable.

---

# P10 proofs

## P10-T1 — exact obstruction

`Cl(L)` is the least set closed under legal operations. Induction on any search/synthesis/evolution derivation restricted to `L` places its output in `Cl(L)`. Therefore `t∉Cl(L)` is unreachable.

## P10-T2 — semantic expansion

The three membership conditions are definitionally sufficient: old closure excludes `t`, the primitive is not a macro, and the extended closure includes `t`. Necessity follows from the intended meaning of new behavioral reach.

## P10-T3 — macro rejection

If `e∈Cl(L)`, every extended derivation using `e` can inline its old-language derivation, so behavioral closure is unchanged. Cost may change, but reach does not.

## P10-T4 — minimal expansion

Inclusion-minimality is equivalent to every added primitive having a protected witness target lost when it is removed. Otherwise remove a redundant primitive and contradict minimality.

## P10-T5 — transfer

With origin-only selection and hidden targets, solving held-out instances demonstrates that the semantic primitive applies beyond the originating target within the frozen family. It does not establish transfer outside the family.

## P10-T6 — complexity separation

Checking a supplied derivation visits each node/premise once and is polynomial in certificate size. SAT reduces to synthesis by making assignments candidate witnesses and the bridge predicate CNF satisfaction; existence is NP-hard.

---

# P11 proofs

## P11-T1 — state lower bound

Distinct cells of `∨Π_r` must map to distinct exact stored states; otherwise two responsibility-distinct worlds collide and T2 is violated. Hence state cardinality is at least the number of cells and binary information at least its logarithm.

## P11-T2 — break-even

Compare costs `K+Uc` and `Ud`. For `d>c`, compilation wins iff `K<U(d-c)`. The least integer satisfying this is `floor(K/(d-c))+1`. Vector costs replace scalar `<` with Pareto or price-relative comparison.

## P11-T3 — optionality

Expected total value decomposes into present service, future responsibility service, drift recovery, and storage/update costs by linearity of expectation under the declared model. A responsibility-specific state can improve the present term while worsening future/recovery terms.

## P11-T4 — decoder boundary

If a stronger decoder with the same information reaches the same target at matched total resource vector, any claimed information advantage disappears; only placement/cost differences remain. A persistent mixed-fibre separation cannot be repaired by decoder strength.

## P11-T5 — phase diagram

For a finite policy family and fixed environment parameters/prices, choose the feasible policy minimizing objective. Boundaries occur where two policy cost functions tie or feasibility changes. Without prices the phase object is a Pareto cell decomposition.

---

# P12 proofs

## P12-T1 — exact-certificate optimality

The action chosen is, by definition, the minimum feasible action under the exact cost/objective certificate, hence equals the hindsight oracle and has zero regret.

## P12-T2 — coarsening impossibility

OSTC-T17: two cases share one visible signal, so the policy selects one action; unique opposing optima force positive regret on one case.

## P12-T3 — value of certificate acquisition

Compare expected optimal loss after acquisition plus acquisition cost against optimal loss under the coarse signal. Acquisition is beneficial exactly when expected loss reduction exceeds cost. This is standard value-of-information algebra under the frozen distribution.

## P12-T4 — robust selection

An action is uniformly optimal on `Θ` iff it minimizes every objective instance. If minimizers differ across `Θ`, no single action has zero worst-case regret; the sound output is an action set, minimax policy, or further information request according to the declared decision rule.

## P12-T5 — online regret

The bound is inherited from the chosen donor online-learning theorem once its boundedness/feedback assumptions and typed action mapping are verified. ORION does not re-prove generic bandit results.

---

# P13 proofs

## P13-T1 — joint state

OSTC-T18: a representation is sufficient for the product of responsibilities iff sufficient for each; the coarsest such partition is their common refinement.

## P13-T2 — safe reuse

Necessity is T2: failure to refine `Π_r'` yields a collision. Sufficiency: a decoder exists on the refined partition, and valid regime/authority transport supplies admission premises.

## P13-T3 — drift transport

Redundant drift preserves every target-relevant equivalence class and support premise, so the certificate replays. Conflicting drift changes at least one required distinction/premise, so T8 blocks replay absent revalidation.

## P13-T4 — conditional reissue

Always-transport fails on conflicting cases; always-reissue pays extra cost on redundant cases. A perfect discriminator selects the exact branch and weakly dominates both, strictly when both strata have positive mass and costs differ.

## P13-T5 — revocation locality

OSTC-T11.

---

# P14 proofs

## P14-T1 — gate attainability

If the protocol’s statistic support lies wholly on one side of a threshold, only one terminal is reachable; no sampled policy can falsify the gate. Intersection with both regions is necessary for refutation capacity.

## P14-T2 — policy/gold separation

If policy reads or implements the gold function, agreement is construction identity rather than evidence. Withheld gold and independent implementation remove direct equality, though external validity still requires independent case/adjudication ownership.

## P14-T3 — abstention guard

A policy that rejects every transition can minimize false promotion trivially. Requiring valid-transition/useful-discovery noninferiority makes blanket refusal fail whenever valid cases have positive mass beyond the margin.

## P14-T4 — negative-history value

Expected net value equals expected avoided recurrence loss minus false-blocking, storage, and review costs. It is positive exactly when the first term exceeds the latter terms. This is conditional on recurrence predictiveness and no target leakage.

## P14-T5 — longitudinal reopening

Apply P6/P7/P13 transport theorems to changes in evidence, evaluator, responsibility, or regime. Missing transport witnesses prevent retention by T5.

---

# P15 proofs

## P15-T1 — noninterference

OSTC-T20: execution-only transformation is `(f,id,id)` on the product state, so validity and authority projections are unchanged.

## P15-T2 — receipt indistinguishability

Take two executions with identical occurrence/environment/output hashes but attach scientific payloads whose target premises differ outside the receipt schema. Receipts are identical while scientific validity differs, so no receipt-only classifier is sound on both.

## P15-T3 — attestation boundary

Under full key compromise, an adversary signs arbitrary forged facts with valid keys. Verification accepts, while fact truth can be false. Therefore signature validity entails neither custody nor truth without extra assumptions.

## P15-T4 — threshold trust

Threshold security is conditional on fewer than the tolerated signers/custody domains being compromised and on the threshold scheme’s model. If the threshold is compromised, forged chains verify. Even below threshold, signers attest statements, not scientific entailment absent a bridge.

## P15-T5 — publication linearizability

If every required record binds one content/occurrence and the chronology orders execution, reap/cleanup, validation, authority, and publication, the history has a linearization point after all prerequisites. Splice, stale replay, or premature finalization violates at least identity or order, so no such linearization exists.

## P15-T6 — provenance invariance

A lossless normalization is a bijection on the execution facts consumed by the decision rule; OSTC-T9 gives identical decisions. If a required fact is lost or invented, invariance is not licensed.

---

# Completion terminal

```text
P1_P15_PAPER_THEOREM_DERIVATIONS_COMPLETE
EMPIRICAL_INSTANTIATION_AND_EXTERNAL_AUTHORITY_PENDING
```
