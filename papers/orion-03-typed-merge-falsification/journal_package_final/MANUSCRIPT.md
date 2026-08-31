# Typed Scientific Authority with Fail-Closed Nonpromotion

## Abstract

Scientific falsification changes more than reachability. A claim may remain derivable after a counterexample while losing the evidence class needed to call it prospective, theorem-level, or externally reproduced. We formalize this bounded problem with a finite typed authority system. Claims carry subsets of a finite license universe. Independent seeds declare licenses; positive conjunctive rules transmit only licenses present in every premise and permitted by an explicit rule cap; directly refuted claims are fixed to the empty label. The resulting monotone operator has a finite least fixed point.

The generic mathematics of least fixed points, proof trees, truth maintenance and annotated provenance is donor-owned. The scientific contribution is the specialization to **nonpromotion between evidence classes** and its executable use on falsified records. We prove that a license reaches a claim exactly when a finite untainted proof tree carries that license through every seed and rule cap. Unsupported cycles remain bottom; adding refutations can only remove licenses; and a post-outcome repair cannot regain `PROSPECTIVE` authority when the repair cap excludes it. The removed claim-license pairs are exactly those with no surviving typed proof tree, relative to the declared authority algebra.

Three committed scientific cases exercise the policy boundary, and a reusable evaluator re-derives their verdicts. An external OpenSSL 3.6.4 X.509 instantiation contains 46 registered hybrid merge obstructions among 1,962 third-party certificate merge tasks. The externally measured content is obstruction occurrence and the cost of alternative merge policies. The typed evaluator's perfect agreement with the parent-authorized set is an analytic consequence of its definition and is not reported as detector accuracy. The paper therefore claims a scientific evidence-license specialization, fail-closed nonpromotion semantics, an executable evaluator, and a non-vacuous external instantiation—not a new general provenance theory or a security result.

**Keywords:** scientific authority; falsification; provenance; least fixed points; evidence licenses

## 1. Scientific question and novelty boundary

Scientific records distinguish at least the following evidence classes:

`THEOREM`, `CONSTRUCTIVE_BOUND`, `FINITE_EXACT`, `PROSPECTIVE`, `FORECAST_ONLY`, `POST_OUTCOME`, `BOUNDED_COMPUTATION`, `EXTERNAL_REPLAY`.

The central question is: **after falsification or repair, which evidence licenses still authorize which claims?**

A Boolean dependency graph can preserve or delete reachability but cannot by itself prevent a post-outcome repair from inheriting prospective authority. The present calculus attaches evidence licenses to derivations and makes that policy mechanically checkable.

The paper does not claim novelty for:

- finite least-fixed-point evaluation;
- positive Datalog-style rule systems;
- truth-maintenance or dependency-directed update;
- annotated/semiring provenance;
- generic minimal-support or deletion-robustness theory.

The residual is the scientific evidence-license vocabulary, cap-preserving nonpromotion rule, typed falsification semantics, reusable evaluator, and externally instantiated obstruction/cost behavior.

## 2. Finite typed authority system

Let `Q` be a finite claim set and `Lambda` a finite license universe. A claim label is a subset of `Lambda`, ordered by inclusion.

Each claim `q` has an independent seed label `sigma(q) subseteq Lambda`. Each positive rule is

`r=(A -> h, K_r)`,

where `A subseteq Q` is a finite antecedent set, `h in Q`, and `K_r subseteq Lambda` is a license cap.

For premise labels `ell_a`, the rule transfer is

`tau_r = K_r intersect intersection_{a in A} ell_a`.

Thus a license crosses a rule only when every premise carries it and the rule cap permits it. Zero-antecedent facts are represented as seeds rather than as rules.

Let `R subseteq Q` be the set of directly refuted claims. Define the synchronous operator

`F_R(x)_q = empty` for `q in R`,

and otherwise

`F_R(x)_q = sigma(q) union union_{r:head(r)=q} tau_r(x|body(r))`.

Starting from the all-empty assignment, iterate `F_R` to stabilization and write the result as `Auth_Lambda(R)`.

## 3. Finite convergence

**Theorem 1 (finite least fixed point).** Synchronous iteration of `F_R` from bottom reaches the least fixed point after at most `|Q||Lambda|` strict claim-license additions, plus the initial state.

**Proof.** `F_R` is monotone because union and intersection are monotone in every premise label and refuted nodes remain fixed at bottom. Starting from bottom, labels can only gain claim-license pairs. There are at most `|Q||Lambda|` such pairs, so only finitely many strict additions are possible. The stabilized value is a fixed point. By monotone induction, every iterate is contained in every fixed point of `F_R`; therefore the stabilized value is the least fixed point. ∎

No separate asynchronous “fair rule-order” theorem is needed for the scientific claims in this paper. Implementations may use any schedule only if they are verified to compute this same registered operator.

## 4. Typed proof-tree characterization

A finite proof tree for `(q,lambda)` is valid under `R` when:

1. no node claim is directly refuted;
2. every leaf `a` satisfies `lambda in sigma(a)`;
3. every internal node applies a specified rule whose cap contains `lambda` and has one child proof tree for each antecedent.

**Theorem 2 (typed proof-tree equivalence).** `lambda in Auth_Lambda(R)_q` if and only if there exists a finite valid proof tree for `(q,lambda)` under `R`.

**Proof.** For the forward direction, induct on the first synchronous iteration at which `(q,lambda)` appears. Seed appearances give leaves; rule-derived appearances give a capped rule whose antecedent licenses appeared earlier, hence finite child trees by induction. For the reverse direction, induct on tree height. Leaves are present from the seed labels, and an internal tree passes `lambda` through its specified capped rule once all child licenses are present. ∎

This theorem gives the exact scientific reading of the fixed point: derivability and evidence class travel together.

## 5. Fail-closed nonpromotion

### 5.1 Unsupported and seeded cycles

A cycle with no licensed seed remains bottom. A licensed seed can propagate around a cycle only through rules whose caps contain that license. Cyclic syntax is therefore not evidence.

### 5.2 License conservation

**Corollary 3.** Every license at a conclusion appears in every leaf seed and every rule cap on at least one finite proof tree supporting that license.

The system cannot invent a stronger evidence class than its registered derivation permits.

### 5.3 Post-outcome repair

If a repair rule cap excludes `PROSPECTIVE`, no repaired claim can obtain prospective authority through that rule, even if its premises carry prospective licenses elsewhere. This encodes “post-outcome exactness is not prospective confirmation” as a rule-level invariant rather than a prose convention.

Similarly, a rule capped at `FINITE_EXACT` or `BOUNDED_COMPUTATION` cannot manufacture `THEOREM` authority.

## 6. Typed falsification and retraction

**Theorem 4 (refutation monotonicity).** If `R subseteq R'`, then

`Auth_Lambda(R')_q subseteq Auth_Lambda(R)_q`

for every claim `q`.

**Proof.** Direct refutation can only replace labels by bottom and cannot add a rule or seed license. Hence `F_R'(x) subseteq F_R(x)` pointwise for every `x`; synchronous iteration from bottom preserves this containment through every round and therefore at the least fixed points. ∎

Let `A_pre=Auth_Lambda(empty)` and `A_post=Auth_Lambda(R)`. Define

`Ret_Lambda(R)={(q,lambda): lambda in A_pre(q)\A_post(q)}`.

**Corollary 5 (exact retraction relative to the declared algebra).** `Ret_Lambda(R)` contains exactly the claim-license pairs for which all valid typed proof trees are destroyed by the specified refutations. Any pair with at least one surviving typed proof tree remains licensed.

This is a semantic property of the declared seeds, rules, caps and refutations. It is not claimed as new generic minimal-support or truth-maintenance mathematics.

## 7. Scientific case boundaries

### 7.1 Forecast falsification

A fresh exact counterexample can remove a universal forecast/equality license while preserving a constructive upper bound or an independently proved support theorem. A repaired post-outcome forecaster may regain exactness under `POST_OUTCOME` but not `PROSPECTIVE` when the repair cap excludes that license.

### 7.2 Decision versus value/witness authority

A representation may retain theorem authority for a decision query while losing exact-value or witness authority. The case is represented by distinct claim nodes and rule paths; falsifying one query-specific sufficiency claim does not automatically erase a different theorem whose derivation survives.

### 7.3 Bounded computation versus theorem authority

A finite internal frontier computation can carry `BOUNDED_COMPUTATION` and a requirement for `EXTERNAL_REPLAY` without licensing an unresolved theorem. Repeated internal exact runs do not silently become theorem authority.

These cases are policy demonstrations bound to existing committed records. They do not claim generic human-science usability.

## 8. Reusable evaluator and external X.509 instantiation

The domain-agnostic evaluator in the accompanying artifact represents seeds, capped rules, refutations and expected verdicts, computes the registered least fixed point, and reconstructs typed proof-tree authorization. Its tests re-derive the committed scientific cases and verify source bindings.

The external instantiation uses third-party OpenSSL 3.6.4 X.509 test certificates. Across 1,962 registered trust-store merge tasks, 46 satisfy the hybrid obstruction condition: flat union authorizes a merge that neither parent-authorized result licenses.

The empirical quantities are:

- obstruction occurrence in third-party material;
- method-dependent unsafe-merge and needless-rejection costs of alternative policies;
- corpus invariants that could have failed.

The specified typed-witness policy returns exactly the parent-authorized set. Therefore its zero unsafe merges, zero needless rejections and corresponding perfect precision/recall are propositional consequences of the benchmark definition and **must not** be presented as detector-performance measurements.

In the registered parity-partition benchmark family, flat union incurs 4 unsafe merges; intersection and reject-all incur 63 needless rejections each; the bounded typed-witness policy incurs 14. These are genuine corpus-dependent measurements.

The X.509 study is not a security evaluation: no attack, threat model or deployed security guarantee is claimed.

## 9. Relation to prior work

Truth-maintenance systems and belief revision own dependency-directed update. Positive Datalog owns least-fixed-point rule semantics. Annotated and semiring provenance own derivation annotations and alternative paths. Minimal-support, causality and deletion-robustness literatures own generic support/retraction structure.

The paper's journal claim is narrower: a scientific evidence-license specialization with explicit nonpromotion caps, typed falsification on scientific records, an executable evaluator, and a third-party external instantiation showing the target obstruction is non-vacuous and carries policy-dependent cost.

## 10. Reproducibility and authority

Finite random-system tests compare iterative evaluation with independently constructed finite checks; the scientific cases are bound to committed evidence objects; and the X.509 corpus is source-digest bound. These are in-repository verification paths, not external institutional replication.

All general formal claims in the submission are limited to the finite positive conjunctive calculus defined above.

## 11. Limitations

1. Rules are positive and conjunctive; arbitrary negation, defaults, probabilistic evidence and inconsistency are out of scope.
2. The license vocabulary and caps are curated policy, not learned automatically.
3. The powerset/intersection transfer algebra is one design, not a universal authority algebra.
4. Generic fixed-point, provenance and retraction mathematics is donor-owned.
5. X.509 provides an external-domain obstruction/cost instantiation, not a security result.
6. Analytic identities are not empirical performance metrics.
7. Broad human-science usability or cross-institution deployment is not claimed.

## 12. Conclusion

The paper's scientific object is not a new least-fixed-point theory. It is a fail-closed scientific authority specialization: evidence licenses must survive every seed and rule cap along a finite proof tree, and falsification removes only the licenses whose typed derivations are destroyed. This prevents post-outcome repairs and bounded computations from laundering themselves into stronger evidence classes. The reusable evaluator makes the policy executable, and the OpenSSL-derived X.509 corpus shows that the merge obstruction and its policy costs occur outside the originating scientific records.

## Tool-use disclosure

A generative language model assisted manuscript organization, language revision,
adversarial review, and submission-package preparation. The listed author remains
responsible for the mathematical statements, proofs, references, executable claims,
and final text.

## Data and code availability

The source archive includes the JSON schema, deterministic Python evaluator, unit
tests, and bounded case fixtures required to reproduce the executable claims. The
external X.509 measurements remain bound to the committed corpus records; analytic
policy identities are not re-labelled as empirical detector performance.

## References

1. J. Doyle, “A Truth Maintenance System,” *Artificial Intelligence* **12**,
   231–272 (1979). DOI: 10.1016/0004-3702(79)90008-0.
2. J. P. Martins and S. C. Shapiro, “A Model for Belief Revision,”
   *Artificial Intelligence* **35**, 25–79 (1988).
   DOI: 10.1016/0004-3702(88)90031-8.
3. C. Bourgaux, P. Bourhis, L. Peterfreund, and M. Thomazo, “Revisiting
   Semiring Provenance for Datalog,” in *KR 2022* (2022).
   DOI: 10.24963/kr.2022/10.
4. M. Abo Khamis, H. Q. Ngo, R. Pichler, D. Suciu, and Y. R. Wang,
   “Convergence of Datalog over (Pre-)Semirings,” in *PODS 2022*, 105–117
   (2022). DOI: 10.1145/3517804.3524140.
5. T. J. Green, G. Karvounarakis, and V. Tannen, “Provenance Semirings,” in
   *PODS 2007*, 31–40 (2007). DOI: 10.1145/1265530.1265535.
6. P. A. Bonatti, A. Hogan, A. Polleres, and L. Sauro, “Robust and Scalable
   Linked Data Reasoning Incorporating Provenance and Trust Annotations,”
   *Journal of Web Semantics* **9**(2), 165–201 (2011).
   DOI: 10.1016/j.websem.2011.06.003.
