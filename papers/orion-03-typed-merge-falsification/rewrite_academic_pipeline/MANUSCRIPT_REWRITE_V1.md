# Typed Scientific Retraction by Evidence License and Least Fixed Point

## Abstract

Scientific falsification should retract claims by derivation and by evidence type. A Boolean dependency graph can determine whether a conclusion remains derivable after a premise is refuted, but it cannot distinguish a surviving theorem from a finite exact result, a prospective prediction, a forecast, or a post-outcome repair. We introduce a finite typed authority calculus for positive conjunctive scientific rule systems. Each claim carries a subset of a finite license universe. Independent seeds introduce declared licenses; each rule has a cap and can transmit only licenses present in every premise and permitted by that cap; directly refuted claims are forced to the empty label. The resulting monotone operator has a unique least fixed point on the finite powerset lattice.

We prove finite convergence, rule-order independence, a typed proof-tree characterization, monotonicity under additional refutation, and exact preservation of alternative derivations at the licenses their surviving proof trees support. Unsupported cycles remain at bottom. Rule caps enforce nonpromotion: post-outcome repair cannot create prospective authority, and bounded computation cannot create theorem authority. We instantiate the calculus on three scientific cases and in a reusable evaluator. A third-party OpenSSL X.509 corpus provides an external-domain obstruction test: 46 hybrid merge cases occur among 1,962 merge tasks. The evaluator's zero unsafe merges under the registered typed rule is an analytic consequence of the semantics rather than a measured detector accuracy; the empirical content is the occurrence of the obstruction and the different costs paid by naive merge policies.

Truth-maintenance systems, positive Datalog, annotated provenance, minimal supports and deletion robustness provide the mathematical donors. The contribution is the scientific evidence-license specialization, explicit nonpromotion across evidence classes, executable typed retraction, and an external instantiation showing that the merge obstruction is non-vacuous.

## 1. Introduction

Scientific records contain conclusions supported in qualitatively different ways. A theorem, finite exact computation, prospective prediction, retrospective repair and forecast can all end in the same proposition while carrying different authority. A falsifier should therefore answer two questions: does any valid derivation survive, and what evidence class does that surviving derivation license?

Untyped dependency tracking answers only the first. If a prospective claim is refuted and a post-outcome repair later reaches the same conclusion, an untyped graph may report the conclusion as restored. Scientifically, however, the repair has not recovered prospective authority. Likewise, repeated exact computations over a bounded domain do not become an all-size theorem merely because every path in a dependency graph agrees.

We formalize this distinction with a powerset-valued least-fixed-point semantics. The calculus deliberately reuses established monotone fixed-point and provenance machinery. Its purpose is to make scientific nonpromotion explicit: authority must travel through every seed and every rule that supports a conclusion.

## 2. Claims, licenses and capped rules

Let \(Q\) be a finite set of claims and \(\Lambda\) a finite set of authority licenses. A representative vocabulary can include `THEOREM`, `CONSTRUCTIVE_BOUND`, `FINITE_EXACT`, `PROSPECTIVE`, `FORECAST_ONLY`, `POST_OUTCOME`, `BOUNDED_COMPUTATION`, and `EXTERNAL_REPLAY`.

Each claim \(q\in Q\) has an independent seed label \(\sigma(q)\subseteq\Lambda\). A positive conjunctive rule has a finite body \(A\subseteq Q\), a head \(h\in Q\), and a cap \(K_r\subseteq\Lambda\). Given premise labels \(\ell_a\), the rule may transfer only

\[
K_r\cap\bigcap_{a\in A}\ell_a.
\]

A license therefore crosses a rule only if every premise carries it and the rule itself permits it. Let \(R\subseteq Q\) be the directly refuted claims.

## 3. Typed least-fixed-point semantics

For an assignment \(x\in(2^\Lambda)^Q\), define \(F_R(x)_q=\varnothing\) for \(q\in R\). For every unrefuted claim, \(F_R\) joins its seed label with every capped rule transfer into that claim.

Because union and intersection are monotone on the finite powerset lattice, \(F_R\) is monotone. Iterating from the all-empty assignment reaches a least fixed point, which we call \(Auth_\Lambda(R)\).

**Theorem 1 (finite convergence and order independence).** Fixed-point iteration stabilizes after at most \(|Q||\Lambda|+1\) strict license-addition rounds, and every fair rule-evaluation order reaches the same least fixed point.

The bound follows because a fixed refutation set permits only license additions during iteration and there are at most \(|Q||\Lambda|\) claim-license pairs.

## 4. Proof trees characterize authority

A finite proof tree for a claim-license pair \((q,\lambda)\) is valid when no node is directly refuted, every leaf seed contains \(\lambda\), and every internal rule cap contains \(\lambda\) while all of its premises are supported by child trees carrying the same license.

**Theorem 2 (typed proof-tree equivalence).** A license \(\lambda\) belongs to \(Auth_\Lambda(R)_q\) if and only if there exists a finite untainted proof tree for \((q,\lambda)\).

One direction follows by induction on the fixed-point round in which the license first appears. The other follows by induction on proof-tree height.

The theorem exposes the core scientific rule: a conclusion can carry only a license that survives along an entire evidence path. Cycles without seeded authority remain unsupported. Seeded cycles may propagate only the licenses allowed by their edges.

## 5. Nonpromotion is structural

The rule caps convert several publication norms into formal invariants.

A repair rule capped by `POST_OUTCOME` and `FINITE_EXACT` cannot transmit `PROSPECTIVE`, even if the repaired conclusion matches an earlier prediction. A bounded-computation rule capped below `THEOREM` cannot create theorem authority. A theorem license can traverse a path only when every seed and every cap on that path contains it.

This gives a license-conservation corollary: every license present at a conclusion occurs in every leaf seed and every rule cap of at least one finite supporting proof tree. The calculus does not infer a stronger evidence class from repeated agreement or from the wording of the conclusion.

## 6. Typed retraction

Adding a direct refutation can only remove authority.

**Theorem 3 (refutation monotonicity).** If \(R\subseteq R'\), then

\[
Auth_\Lambda(R')_q\subseteq Auth_\Lambda(R)_q
\]

for every claim \(q\).

Alternative derivations survive exactly at the licenses carried by their untainted proof trees. Define the typed retraction as the claim-license pairs present before falsification and absent afterward. The proof-tree theorem implies that this removes every unsupported pair and retains every pair with a surviving licensed derivation.

The minimality claim is explicitly relative to the declared seed/rule/cap algebra. General dependency-directed revision and provenance minimality remain donor mathematics.

## 7. Scientific case studies

### 7.1 Forecast falsification and repair

A compact quantum-compilation forecaster combined feasible constructions, an independent structural theorem, and a prospective regime label. A fresh exact row refuted the compact equality. Typed retraction removes universal closed-form exactness and the old prospective regime license while preserving the constructive upper bound and independent theorem. A repaired predictor may regain finite-exact or post-outcome authority, but its rule cap prevents prospective authority from being retroactively restored.

### 7.2 Decision authority can survive value falsification

A separate representation supports an exact decision theorem while counterexamples show that the same information does not determine exact value or a witness property. The calculus assigns these statements to distinct claim nodes and rule paths. Refuting value sufficiency therefore does not retract the decision theorem. This is a concrete example of query-specific authority: the same representation can be theorem-sufficient for one question and insufficient for another.

### 7.3 Bounded computation cannot become a theorem by repetition

An internal exact frontier computation can carry `BOUNDED_COMPUTATION` and `EXTERNAL_REPLAY` while remaining unlicensed at `THEOREM`. Even repeated implementations or large enumerations cannot cross a rule cap that explicitly denies theorem authority. The case prevents a common escalation error in computational mathematics: internal exactness over a bounded frontier does not, by itself, close an all-size claim.

## 8. Reusable evaluator

The calculus is implemented as a domain-agnostic deterministic evaluator over serialized seeds, capped rules, and refutations. The evaluator is tested on unsupported cycles, seeded cycles, cap violations, alternative derivations, and monotonicity under refutation. It re-derives the registered scientific cases without depending on their development-specific implementations.

This implementation is a reproducibility layer, not independent external scientific validation. Its role is to make the declared authority policy executable and auditable.

## 9. External X.509 instantiation

To test whether the target merge obstruction is merely an artifact of the originating scientific examples, we instantiate the same typed merge semantics on third-party OpenSSL certificate material. Across 1,962 trust-store merge tasks, 46 cases satisfy the registered hybrid condition: authorization succeeds under a flat union even though neither parent-authorized result licenses the merged outcome.

The typed rule authorizes exactly the parent-authorized set. Under the registered benchmark definitions, zero unsafe typed merges and zero needless typed rejections therefore follow analytically; they are not empirical precision or recall estimates. The corpus contributes different evidence: the hybrid obstruction occurs in third-party material, and alternative merge policies incur measurable unsafe-merge or needless-rejection costs on those cases.

This is not a security evaluation. No attack success, exploitability or operational threat model is claimed.

## 10. Relation to prior work

Truth-maintenance systems and belief-revision mechanisms own dependency-directed update. Positive Datalog owns least-fixed-point semantics. Semiring and annotated provenance own algebraic annotation of recursive derivations, alternative supports and deletion behavior. Minimal-support and causality frameworks provide closely related support reasoning.

The residual contribution is smaller and scientific-specific: an evidence-license vocabulary, cap-preserving rule semantics that forbids authority promotion across evidence classes, typed falsification and repair of scientific records, a reusable evaluator, and an external-domain merge obstruction showing that the specialization is not vacuous.

## 11. Limitations

The current calculus is finite, positive and conjunctive. Stratified negation, default reasoning, inconsistent evidence, probabilities and graded belief are outside scope. The license universe and rule caps are declared policy rather than learned objects. Powerset intersection is one useful transfer algebra, not a universal model of scientific authority.

The case studies show how typed authority behaves; they do not establish that this exact license vocabulary is complete for science. The X.509 instantiation demonstrates obstruction occurrence and policy costs, not cybersecurity performance.

## 12. Reproducibility and availability

A submission package should expose the formal definitions, proofs, deterministic evaluator, serialized case studies, third-party corpus bindings and mutation controls. Analytic consequences must be labeled as such so that identities implied by the semantics are not reported as empirical detector performance. Development repository paths and internal workflow history belong in artifact documentation rather than the manuscript narrative.

## 13. Conclusion

Scientific falsification should retract evidence authority, not merely conclusion strings. The typed least-fixed-point calculus makes this distinction explicit: a license survives exactly when it has an untainted proof tree whose seeds and rule caps all permit that license. Refutation can remove authority but cannot create it, repairs cannot recover evidence classes they did not earn, and independent derivations survive at their own licensed strength. The result is an executable nonpromotion discipline for scientific records, grounded in established fixed-point and provenance mathematics and tested on both scientific cases and an external merge obstruction.
