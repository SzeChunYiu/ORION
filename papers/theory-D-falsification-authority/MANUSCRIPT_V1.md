# Falsification-Aware Scientific Authority as a Least Fixed Point

**Paper D — publication-candidate manuscript**

## Abstract

Scientific evidence systems increasingly combine theorem-backed claims, finite benchmark results, constructive bounds, post-outcome repairs and derived conclusions. When one exact claim is falsified, a central problem is not merely to mark that claim false but to determine exactly which downstream authority must be withdrawn and which independently supported claims survive. We formalize this problem for finite positive conjunctive certificate systems. Claims are nodes, independent evidence supplies seeds, and registered derivations are positive rules `A_1 ∧ ... ∧ A_k -> h`. After a set of direct falsifiers `R`, post-falsifier scientific authority is the least fixed point of the monotone operator that starts from non-refuted seeds and repeatedly adds non-refuted rule heads whose antecedents are already authorized. This removes an acyclicity assumption from an earlier certificate-hypergraph calculus. We prove finite convergence and rule-order independence; equivalence between fixed-point authority and the existence of a finite untainted proof tree; failure of unsupported cycles to self-authorize; legitimate propagation through seeded cycles; monotonicity under added refutations; exact survival under alternative derivations; and uniqueness of the minimal well-founded retraction that preserves every safely derivable claim. Two compiler case studies illustrate why this matters. In a static TARE forecast, the exact `10<11` counterexample retracts the original closed-form equality and regime label while preserving a constructive upper bound and an independently proved all-size support theorem. In a distinct partition compiler, counterexamples showing that pair or low-order interaction data do not determine exact value or optimizer structure leave the independently proved low-order **decision** certificate untouched. The fixed-point and provenance mathematics are not claimed as new: truth-maintenance systems, belief revision, recursive Datalog provenance and deletion provenance are direct donors. The contribution is a typed scientific-authority calculus that makes falsification scope machine-checkable and demonstrates, across two compiler families, why evidence layers should retract by derivation rather than by rhetorical proximity.

## 1. Introduction

A counterexample can be mathematically decisive and scientifically local. If a static compiler forecast returns 11 where an exact optimizer returns 10, a claimed universal equality is false. It does not follow that every statement packaged with that forecast is false. The returned construction may still be feasible, so its cost remains an upper bound. An independent theorem may still prove that exact optima lie inside a larger family. A repaired post-outcome predictor may be valid as a repair without becoming prospective confirmation.

This problem is fundamentally one of **authority dependencies**. A scientific manuscript often contains claims of different epistemic types:

- independent theorem or construction;
- derived corollary;
- finite benchmark equality;
- prospective prediction;
- conjectural explanation;
- post-outcome repair;
- claim supported by more than one independent derivation.

When evidence changes, the update should follow those dependencies. Retracting every nearby claim is too destructive. Preserving every claim not directly contradicted is too permissive.

Truth-maintenance systems, belief-revision systems and provenance formalisms already provide mature machinery for dependency-aware updates. Recursive Datalog provenance, in particular, makes derivation trees and deletion behavior explicit. We therefore do not present least fixed points, proof trees or deletion provenance as novel mathematics. Instead, we ask what additional typing is needed when the objects are **scientific claims with heterogeneous authority** and a falsifier should retract exactly the unsupported layer.

An earlier ORION authority calculus assumed an acyclic certificate hypergraph. That restriction makes topological evaluation easy but excludes ordinary mutually dependent derivations and recursive reasoning. Here we remove it. Positive cycles are allowed, but they do not create authority from nothing: only claims grounded in non-refuted independent seeds and finite derivation trees enter the least fixed point.

### 1.1 Contributions

**D1 — cyclic positive authority semantics.** We define post-falsifier authority as the least fixed point of a finite positive conjunctive rule system.

**D2 — proof-tree characterization.** A claim is authorized exactly when it has a finite proof tree whose leaves are non-refuted seeds and whose internal rule applications avoid refuted heads.

**D3 — exact cycle behavior.** Unsupported cycles do not self-authorize; a cycle reachable from a valid seed may propagate authority.

**D4 — retraction calculus.** Added refutations cannot add authority, alternative derivations survive exactly when one untainted proof tree remains, and the pre/post difference is the unique minimal well-founded retraction that retains every safely derivable claim.

**D5 — two-family falsifier study.** We instantiate the calculus on a TARE forecast refutation and a distinct partition-compiler information separation.

## 2. Certificate systems and evidence types

Let `Q` be a finite set of claims. A certificate system contains:

- an independent seed set `S subseteq Q`;
- a finite rule set `P` of positive conjunctive rules
  `A -> h`, where `A subseteq Q` is finite and `h in Q`;
- a directly refuted set `R subseteq Q`.

The mathematical rule system is intentionally simple. Scientific typing is carried by metadata attached to claims and evidence, for example:

- `THEOREM`;
- `CONSTRUCTIVE_BOUND`;
- `FINITE_EXACT`;
- `PROSPECTIVE_BOUNDED`;
- `FORECAST_ONLY`;
- `POST_OUTCOME_REPAIR`;
- `CANNOT_CHECK`.

These labels do not change the fixed-point mathematics. They prevent a derivation from silently promoting one kind of evidence into another. A post-outcome repair can derive a repaired claim but cannot thereby become a prospective result.

## 3. Least-fixed-point authority

For fixed refutations `R`, define

`T_R(X) = (S \ R) union {h in Q\R : exists (A -> h) in P with A subseteq X}`.

`T_R` is monotone on the finite lattice `2^Q`. Starting from the empty set, define

`X_0=empty`,

`X_{n+1}=T_R(X_n)`.

Because `Q` is finite and the sequence is monotone, it stabilizes. Define

`Auth(R)=lfp(T_R)`.

This is the post-falsifier authority set.

**Theorem 1 (finite convergence and order independence).** The iteration stabilizes after at most `|Q|+1` strict rounds. The resulting `Auth(R)` is independent of the order in which rules are scanned.

**Proof.** Every strict iteration adds at least one previously absent claim; no claim is ever removed during a fixed `R` computation. At most `|Q|` additions are possible. The limit is the least fixed point of the monotone operator `T_R`, which is defined by the rule set rather than a rule evaluation order. Any fair forward-chaining evaluation computes the same closure. ∎

## 4. Finite proof trees characterize authority

A finite **untainted proof tree** for claim `q` under `R` is defined recursively:

1. a one-node tree is valid if `q in S\R`;
2. otherwise its root is a non-refuted head `q` of a registered rule `A -> q`, and each `a in A` is the root of a finite untainted proof subtree.

**Theorem 2 (proof-tree equivalence).** A claim `q` lies in `Auth(R)` if and only if it has a finite untainted proof tree under `R`.

**Proof.** If `q` first appears in round `n`, induction on `n` constructs a proof tree: round-one claims are seeds; a later claim is added because every antecedent appeared earlier. Conversely, induction on proof-tree height shows every leaf belongs to the seed closure and every internal rule head is added after its children. ∎

This theorem supplies the well-founded semantics needed for cyclic rule systems.

## 5. Cycles do not manufacture scientific authority

Consider rules

`a -> b`,

`b -> a`.

With no seed, neither claim enters `Auth(empty)`: the least fixed point is empty. The cycle is a potential derivation structure, not evidence.

If `a` is an independent non-refuted seed, forward chaining authorizes `b` and the fixed point is `{a,b}`. The cycle is then harmless because both claims have finite proof trees grounded at `a`.

**Corollary 3 (unsupported-cycle exclusion).** Every strongly connected component with no incoming derivation from a non-refuted seed remains unauthorized.

This fail-closed behavior is one reason the least, rather than greatest, fixed point is appropriate for scientific authority.

## 6. Retraction properties

### 6.1 Refutation monotonicity

**Theorem 4.** If `R subseteq R'`, then

`Auth(R') subseteq Auth(R)`.

**Proof.** For every `X`, `T_R'(X) subseteq T_R(X)`. Monotone iteration from the same bottom element preserves this inclusion at every round, hence at the limits. ∎

Adding falsifiers can never manufacture authority.

### 6.2 Alternative derivations

**Corollary 5.** A claim survives a refutation exactly when at least one finite proof tree remains untainted.

Thus a refuted premise invalidates only the derivations that depend on it. A separate seed or alternative rule path can preserve the claim.

### 6.3 Exact retraction set

Let

`A_pre = Auth(empty)`

and

`A_post = Auth(R)`.

Define

`Ret(R)=A_pre \ A_post`.

By Theorem 4, `A_post subseteq A_pre`.

**Theorem 6 (unique minimal well-founded retraction).** Among post-falsifier authority assignments that (i) contain every non-refuted independent seed, (ii) retain every claim with a finite untainted proof tree, and (iii) authorize no claim lacking such a proof tree, the unique assignment is `Auth(R)`. Equivalently, `Ret(R)` is the unique minimal retraction from `A_pre` satisfying these conditions.

**Proof.** By Theorem 2, the set of claims with finite untainted proof trees is exactly `Auth(R)`. Condition (ii) requires every member of `Auth(R)` to be retained; condition (iii) forbids every claim outside it. Hence the authority set is unique and the removed set is exactly its complement in `A_pre`. ∎

The minimality is therefore semantic, not merely cardinal: no safely derivable claim may be removed and no unsupported claim may remain.

## 7. Case study I: one exact forecast counterexample

The first case is a static forecast in a frozen TARE compiler family. The original forecaster combined several authority layers:

1. minima over explicit feasible subfamilies, giving a constructive upper bound;
2. an independent all-size theorem proving that the unrestricted optimum lies in the full support-two family;
3. a compact closed-form equality observed on registered finite domains;
4. a regime label derived from that compact decomposition.

A prospectively generated exact row returns

`C_DP=10`,

while the original compact forecaster returns

`F=11`.

The original benchmark therefore remains exactly 9,545 correct rows out of 9,546 comparisons. One exact row is enough to falsify universal equality.

### 7.1 Retraction

Represent the constructive upper bound and support-two theorem as independent seeds. The closed-form equality depends on finite/conjectural evidence and is directly refuted by the `10<11` row. The original regime label depends on that equality/explanation layer.

The fixed point after the falsifier preserves:

- feasible-upper-bound authority, because `10<=11` and the construction remains valid;
- all-size support-two authority, because the exact optimum at 10 is itself realized in that theorem-backed family.

It retracts:

- original universal closed-form exactness;
- original regime label on the counterexample.

A separately frozen repaired forecaster may be authorized by its own post-outcome evidence, but its type remains `POST_OUTCOME_REPAIR`. It does not retroactively turn the failed prediction into prospective confirmation.

## 8. Case study II: decision survives value and optimizer falsifiers

Paper C supplies a structurally different compiler. Its all-`m>=5` theorem says unary optimality is decided by a four-index certificate. Later exact constructions establish two negative results about **richer outputs**:

- complete pair information does not determine the exact improvement value and does not determine whether an optimum contains a triple block;
- even all labeled interactions through order `m-2` do not determine exact improvement value.

If a scientific record had over-promoted pair-information sufficiency into “the pair representation determines the optimizer,” the first construction is a direct falsifier. The least-fixed-point update retracts the value/optimizer-sufficiency claims. It does **not** retract the independently proved decision theorem because that theorem has a separate proof tree and both counterexample members make the same decision: unary is not optimal.

This second family demonstrates that the calculus is not tied to one forecasting workflow. It handles a different form of epistemic separation: a representation can be sufficient for one query and falsified for another.

## 9. Relation to truth maintenance, belief revision and provenance

Doyle's truth-maintenance system established dependency-directed justification maintenance and contradiction handling. Martins and Shapiro developed a general model for belief revision using assumptions and environments. Database provenance gives a mature algebraic account of how derivations depend on input facts. Recent work revisiting semiring provenance for Datalog explicitly studies recursive programs, derivation-tree semantics and deletion behavior by zeroing annotations. Provenance-guided rollback systems likewise use dependency information to suggest repairs in evolving rule systems.

These are direct donors. Paper D does not claim novelty for:

- least-fixed-point semantics of positive rules;
- finite derivation/proof trees;
- dependency-directed truth maintenance;
- belief revision in general;
- Datalog provenance;
- deletion provenance;
- rollback based on dependency graphs.

The residual contribution is the **scientific-authority specialization**: evidence-type-preserving claim graphs, exact falsifier scope, explicit nonpromotion of post-outcome repair, and two machine-bound compiler case studies showing how theorem, constructive, finite, forecast and explanatory authority should retract independently.

## 10. Reproducibility

The original acyclic authority result is bound to its committed source, generic and native campaign records. The cyclic extension is corroborated by `papers/verify_five_theory_upgrades.py`, which checks unsupported and seeded cycles explicitly and tests refutation monotonicity and finite convergence on 5,000 deterministic finite rule systems. The all-system authority of Theorems 1–6 comes from the written proofs, not the random test sample.

The two scientific case studies are bound to separately committed evidence from QG5/QG5B and Paper C. A submission archive should include a machine-readable claim/rule/refutation example for each case and the exact commit identity.

## 11. Limitations

1. Rules are positive and conjunctive. Negation, defaults, probabilistic support and inconsistent paraconsistent logics are not modeled.
2. Evidence-type metadata is enforced externally to the fixed-point logic; the current theorem does not provide a full type system.
3. The two empirical instantiations are compiler/scientific-reasoning cases, not a general user study of scientific provenance systems.
4. The fixed-point mathematics is donor-owned; novelty must remain in the scientific specialization and case-level consequences.
5. No claim is made that every scientific disagreement can be reduced to a monotone positive rule graph.
6. Independent external evaluation of the calculus and usability remains open.

## 12. Discussion

A falsifier should answer two questions: **what became false?** and **what authority depended on it?** The first is mathematical or empirical. The second is provenance. Collapsing the two causes two opposite failure modes. Over-retraction discards independently proved structure because it appeared in the same paper or forecast. Under-retraction preserves explanatory or derived claims whose only valid support has disappeared.

The least-fixed-point view is conservative in a precise sense. Cycles cannot manufacture authority, and every retained claim can be unfolded into a finite evidence-grounded proof tree. Yet the calculus is not maximally destructive: alternative derivations are preserved automatically, and a falsifier cannot erase an independent theorem merely because both were used in the same narrative.

Scientific typing adds a second safeguard. Even when a repaired claim re-enters the fixed point, its evidence class matters. A post-outcome repair remains post-outcome. A finite benchmark remains finite. A constructive upper bound remains a bound. The authority graph determines derivability; the evidence type determines what kind of scientific statement that derivability licenses.

## 13. Conclusion

Scientific claims should retract by evidence dependency rather than by narrative proximity. In a finite positive certificate system, the least fixed point of non-refuted seeds and registered rules gives an exact well-founded authority semantics even in the presence of cycles. It converges uniquely, excludes unsupported self-support, preserves seeded recursive derivations, shrinks monotonically under added refutations and retracts exactly those pre-falsifier claims that lose every safe proof tree. Applied to two compiler families, the calculus preserves theorem-backed structure while removing the specific equality, label, value or optimizer claims that exact counterexamples invalidate.

## Selected references

- J. Doyle, _A Truth Maintenance System_, Artificial Intelligence 12, 231–272 (1979), DOI 10.1016/0004-3702(79)90008-0.
- J. P. Martins and S. C. Shapiro, _A Model for Belief Revision_, Artificial Intelligence 35, 25–79 (1988).
- C. Bourgaux, P. Bourhis, L. Peterfreund and M. Thomazo, _Revisiting Semiring Provenance for Datalog_, KR 2022, DOI 10.24963/kr.2022/10.
- Provenance-guided rollback literature, including recent work on rollback suggestions for evolving Datalog systems, is treated as a direct methodological donor in the final related-work audit.

---

## Publication decision record

**Primary target posture:** formal reasoning / logic / provenance journal family, with `Journal of Automated Reasoning` or `ACM Transactions on Computational Logic` as target families to resolve exactly after final scope audit.  
**Stretch posture:** broader AI venue only if the scientific-authority type layer or independent third-domain evaluation grows beyond the present two compiler cases.  
**Internal status:** `METHODS_THEORY_SUBMISSION_CANDIDATE__GENERAL_FIXED_POINT_NOVELTY_SUBTRACTED`.  
**Remaining blockers:** primary-reference verification for belief-revision/provenance donors; exact target/article-type resolution; an independently reusable authority-type implementation or third-domain case if a broader venue is pursued; external review and final figures/archive.
