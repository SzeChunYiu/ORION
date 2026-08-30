# Typed Scientific Retraction by Evidence License: Least-Fixed-Point Semantics for Nonpromoting Scientific Authority

## Abstract

Scientific falsification should retract not only conclusion strings but also the *kind of evidence authority* attached to them. A theorem, finite exact computation, prospective prediction, forecast, and post-outcome repair may support the same proposition while licensing different scientific uses. Ordinary Boolean dependency graphs preserve alternative derivations but do not prevent a surviving repair from inheriting an authority class it did not earn.

We define a finite typed authority calculus for positive conjunctive scientific rule systems. Each claim carries a subset of a finite license universe. Independent seeds introduce declared licenses; each rule has an explicit cap and transmits only licenses present in every premise and permitted by that cap; directly refuted claims are forced to the empty label. The induced monotone operator has a least fixed point on the finite powerset lattice. We prove finite convergence, fair-order independence, a typed proof-tree characterization, monotonicity under additional refutation, and exact preservation of alternative derivations at the licenses supported by surviving proof trees. Unsupported cycles remain at bottom. Rule caps make nonpromotion structural: post-outcome repair cannot manufacture prospective authority, and bounded computation cannot manufacture theorem authority.

A deterministic evaluator re-derives the formal cases and exercises hostile mutations. Three scientific examples illustrate forecast falsification, query-specific survival of a decision theorem after value claims fail, and bounded-computation nonpromotion. A third-party OpenSSL X.509 corpus supplies an external-domain obstruction check: 46 hybrid merge cases occur among 1,962 trust-store merge tasks. Because the typed rule is definitionally the parent-authorized set, its zero unsafe merges are an analytic identity rather than detector-performance evidence; the empirical contribution of the corpus is obstruction occurrence and the costs incurred by alternative merge rules.

Truth maintenance, positive Datalog, annotated provenance, minimal supports and deletion robustness are direct mathematical donors. The residual contribution is a scientific evidence-license specialization in which proof search and falsification are explicitly prevented from escalating authority. The calculus is finite, positive and policy-indexed; it is not a universal theory of scientific truth.

## 1. Problem and contribution

Automated reasoning systems increasingly operate over scientific records containing heterogeneous evidence: formal proofs, exact finite computations, forecasts, prospective commitments, external replications and post-outcome repairs. The same conclusion may remain derivable after falsification even though the strongest surviving derivation is scientifically weaker.

This creates a reasoning problem rather than a prose problem. If a prospective rule is refuted and a retrospective repair later recovers the same value, a dependency graph may mark the proposition as restored. Scientifically, the repair has not restored *prospective* authority. Likewise, a bounded exact census does not become an all-size theorem when many independent code paths agree.

The contribution is a least-fixed-point semantics that makes evidence class part of derivation. The formal object is intentionally narrow enough to be checkable and to sit inside the scope of automated reasoning.

### Main results

1. **Least-fixed-point authority.** A finite positive rule system with powerset-valued licenses and capped transfer has a unique least fixed point reached by monotone iteration.
2. **Typed proof-tree equivalence.** A claim carries license `lambda` exactly when it has a finite unrefuted proof tree whose leaves and rule caps all carry `lambda`.
3. **Refutation monotonicity.** Adding direct refutations can only remove licenses.
4. **Nonpromotion.** No license can appear at a conclusion unless one complete supporting proof tree carries it through every seed and rule cap.
5. **Alternative-derivation preservation.** Refuting one path removes only the licenses dependent on that path; independently licensed derivations survive.

The results assume a finite claim set, a finite license set, positive conjunctive rules and explicitly declared caps. Negation, inconsistency and probabilistic belief are outside the present calculus.

## 2. Formal model

Let `Q` be a finite claim set and `Lambda` a finite authority-license universe. A label is an element of `2^Lambda`, ordered by inclusion. Representative licenses may include `THEOREM`, `CONSTRUCTIVE_BOUND`, `FINITE_EXACT`, `PROSPECTIVE`, `FORECAST_ONLY`, `POST_OUTCOME`, `BOUNDED_COMPUTATION`, and `EXTERNAL_REPLAY`.

Each claim `q` has an independent seed label `sigma(q)`. A rule is a triple `(A -> h, K_r)`, where `A` is a finite set of premises, `h` is the head claim and `K_r` is the rule cap. For premise labels `ell_a`, rule transfer is

`K_r ∩ ⋂_{a in A} ell_a`.

Let `R` be the set of directly refuted claims. For a label assignment `x`, define `F_R(x)_q = ∅` when `q in R`; otherwise join the seed label with every capped transfer into `q`. The scientific authority state is

`Auth_Lambda(R) = lfp(F_R)`.

This model separates *derivability* from *authority class*. A claim is untyped-reachable when its final label is nonempty, but the label records which scientific uses actually survive.

## 3. Least-fixed-point and proof-tree theorems

### Theorem 1 — finite convergence

Starting from the all-empty assignment, iteration reaches the least fixed point after at most `|Q||Lambda|` strict claim-license additions. Any fair rule-evaluation order yields the same result.

The proof follows from monotonicity and finiteness of the powerset product lattice. The theorem is ordinary fixed-point mathematics specialized to the present authority algebra; generic Datalog fixed-point theory is not claimed as new.

### Theorem 2 — typed proof-tree equivalence

For a claim `q` and license `lambda`,

`lambda in Auth_Lambda(R)_q`

if and only if there exists a finite proof tree rooted at `q` such that no node is directly refuted, every leaf seed contains `lambda`, every internal rule cap contains `lambda`, and every premise is supported by a child tree carrying the same license.

Induction on the first fixed-point round constructs a tree from a derived license. Induction on tree height proves the converse.

The theorem makes the scientific interpretation transparent: a strong license cannot be inferred from a weak path merely because the conclusion text matches a stronger historical claim.

## 4. Refutation and alternative derivations

### Theorem 3 — monotonicity under refutation

If `R ⊆ R'`, then `Auth_Lambda(R')_q ⊆ Auth_Lambda(R)_q` for every claim. Refutation can remove authority but cannot create it.

Define typed retraction as the claim-license pairs present before falsification and absent afterward. The proof-tree theorem implies that this retraction is exact relative to the declared algebra: it removes every pair with no surviving licensed proof tree and preserves every pair with one.

This relative qualifier is essential. The calculus can be wrong if its seeds, caps or claim graph omit a real scientific dependency. The theorem certifies the declared reasoning object, not the completeness of scientific modelling.

## 5. Nonpromotion as an invariant

The cap mechanism turns several publication disciplines into formal invariants.

A repair rule whose cap excludes `PROSPECTIVE` cannot restore prospective authority after the outcome is known. A rule fed only by `BOUNDED_COMPUTATION` cannot conclude `THEOREM`. An unsupported cycle cannot bootstrap authority from itself. A seeded cycle can propagate only the licenses admitted by every traversed cap.

The resulting license-conservation principle is stronger than a warning in manuscript prose: every license appearing at a conclusion must occur along at least one complete licensed proof tree.

## 6. Scientific instantiations

### 6.1 Forecast falsification

A quantum-compilation forecaster has three distinct scientific supports: feasible constructions, an independent support theorem, and a prospective regime claim. A fresh exact counterexample falsifies the compact equality. Typed retraction removes universal closed-form exactness and prospective regime authority but preserves the feasible upper bound and the independent theorem. A later repaired predictor can regain finite-exact or post-outcome status without retroactively becoming a prospective success.

### 6.2 Decision theorem survives value falsification

A second representation supports an exact decision theorem while exact counterexamples show that the same observable state cannot determine exact value or a witness property. These claims occupy different nodes and proof paths. Refuting value sufficiency therefore leaves the decision theorem intact. This is a query-specific survival result, not evidence that the representation is generically sufficient.

### 6.3 Bounded computation remains bounded

A large exact internal frontier computation may be reproducible and independently reimplemented while still carrying only `BOUNDED_COMPUTATION` and `EXTERNAL_REPLAY`. Repetition does not cross a theorem cap. This case prevents computational evidence from being silently promoted by accumulation.

## 7. Executable evaluator and hostile controls

A domain-agnostic evaluator serializes seeds, rules, caps and refutations and computes the least fixed point deterministically. Tests cover unsupported and seeded cycles, alternate derivations, cap violations, refutation monotonicity and mutation operators deliberately designed to change the verdict.

The evaluator checks the *implementation* of the semantics. It is not additional theorem authority and is not external replication. This separation is retained in the paper because automated-reasoning manuscripts are especially vulnerable to treating a successful executable as evidence for a stronger mathematical statement.

## 8. External merge obstruction

A separate instantiation uses third-party OpenSSL X.509 test material. Among 1,962 registered trust-store merge tasks, 46 exhibit the target hybrid obstruction: flat union authorizes a result that is not authorized by either parent result.

The typed rule is constructed to authorize exactly the parent-authorized set. Consequently its zero unsafe merges and zero needless rejections follow by proposition-level identity under the benchmark definitions. Those numbers are not empirical precision or recall.

The corpus contributes a different fact: the obstruction is non-vacuous in third-party material, and alternative policies pay measurable unsafe-merge or needless-rejection costs. No cybersecurity, exploitability or production-security claim follows.

## 9. Relation to automated reasoning and provenance

Truth-maintenance systems own dependency-directed revision. Positive Datalog owns least-fixed-point evaluation. Annotated and semiring provenance own algebraic labels, alternative derivations and recursive support. Minimal-support, causality and deletion-robustness frameworks own closely related support analyses.

The residual is therefore deliberately specific: scientific evidence licenses are treated as first-class proof annotations, and rule caps encode a nonpromotion policy between evidence classes. The contribution is the resulting reasoning discipline and its scientific falsification semantics, not a rediscovery of fixed points or provenance.

## 10. Limitations

The calculus is finite, positive and conjunctive. It does not yet model stratified negation, defaults, inconsistent evidence, probabilities, graded belief or uncertain rule validity. The license vocabulary and caps are scientific policy supplied to the reasoner rather than inferred automatically. Powerset intersection is one conservative transfer algebra, not a universal choice.

The external X.509 study establishes occurrence of the merge obstruction, not security performance. The scientific examples are bounded instantiations, and the model does not prove that its license vocabulary is complete for real scientific practice.

## 11. Reproducibility and availability

A JAR submission should expose the formal definitions, theorem statements and proofs, deterministic evaluator, mutation controls, serialized scientific cases and third-party corpus bindings. Analytic identities must be labelled separately from measured quantities. The reviewer-facing manuscript should keep repository history out of the scientific narrative while the artifact package preserves exact provenance.

## 12. Conclusion

Scientific falsification is incomplete when a reasoner tracks only whether a proposition remains reachable. Evidence authority must survive along the derivation as well. In the typed least-fixed-point calculus, a license reaches a conclusion exactly through a finite unrefuted proof tree whose seeds and rule caps carry that license. Refutation removes authority monotonically, independent derivations survive at their own strength, and repairs cannot manufacture evidence classes they did not earn. The resulting semantics turns scientific nonpromotion into an automated-reasoning property rather than an editorial convention.