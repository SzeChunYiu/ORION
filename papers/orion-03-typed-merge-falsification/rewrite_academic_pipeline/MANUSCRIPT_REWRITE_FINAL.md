# Evidence-Licensed Scientific Retraction by Least Fixed Point

## Abstract

Scientific falsification should retract authority by derivation **and** by evidence type. A Boolean dependency graph can determine whether a conclusion remains derivable after a premise is refuted, but it cannot distinguish a surviving theorem from a finite exact result, a prospective prediction, a forecast, or a post-outcome repair. We introduce a finite typed authority calculus for positive conjunctive scientific rule systems. Each claim carries a subset of a finite license universe. Independent seeds introduce declared licenses; each rule has a cap and may transmit only licenses present in every premise and permitted by that cap; directly refuted claims are forced to the empty label. The resulting monotone operator has a least fixed point on the finite powerset lattice.

We prove finite convergence, rule-order independence, a typed proof-tree characterization, monotonicity under added refutation, and exact preservation of alternative derivations at the licenses supported by their surviving proof trees. Unsupported cycles remain at bottom. Rule caps enforce nonpromotion: a post-outcome repair cannot create prospective authority, and bounded computation cannot create theorem authority. We instantiate the calculus on three scientific cases and in a reusable evaluator. A third-party OpenSSL X.509 corpus supplies an external non-vacuity test: 46 hybrid merge obstructions occur among 1,962 merge tasks. Under the registered typed rule, zero unsafe typed merges is an analytic consequence of the semantics rather than a measured detector accuracy; the empirical content is obstruction occurrence and the different costs paid by alternative merge policies.

Truth-maintenance systems, positive Datalog, annotated provenance, minimal supports, and deletion robustness provide the mathematical donors. The residual contribution is the scientific evidence-license specialization, cap-preserving nonpromotion, executable typed retraction, and an external instantiation showing that the target obstruction occurs outside the originating scientific examples.

## 1. Introduction

Scientific records contain conclusions supported in qualitatively different ways. A theorem, finite exact computation, prospective prediction, retrospective repair, and forecast can all terminate in the same proposition while carrying different scientific authority. A falsifier should therefore answer two questions: does a valid derivation survive, and what evidence class does that surviving derivation license?

Untyped dependency tracking answers only the first. If a prospective claim is refuted and a post-outcome repair later reaches the same conclusion, an untyped graph may report the conclusion as restored. Scientifically, the repair has not recovered prospective authority. Likewise, repeated exact computations over a bounded domain do not become an all-size theorem merely because every recorded path agrees.

We formalize this distinction with a powerset-valued least-fixed-point semantics. The calculus deliberately reuses established monotone fixed-point and provenance machinery. Its purpose is narrower: make scientific nonpromotion explicit so that authority must travel through every seed and every rule supporting a conclusion.

### 1.1 Main contributions and assumptions

The paper makes four bounded contributions.

1. **Typed least-fixed-point authority.** Claims carry sets of evidence licenses, and positive rules transmit only licenses shared by every premise and admitted by a rule-specific cap.
2. **Proof-tree semantics and refutation.** A claim carries a license exactly when a finite untainted proof tree carries that license through every seed and rule cap; adding refutations can only remove licenses.
3. **Nonpromotion by construction.** Prospective, theorem, finite-exact, post-outcome, and other evidence classes cannot silently amplify into one another.
4. **Executable specialization and non-vacuity.** A reusable evaluator realizes the semantics, and a third-party X.509 corpus contains the registered hybrid obstruction.

The formal results assume a finite claim set, a finite license universe, and positive conjunctive rules. Negation, probabilistic belief, defaults, and inconsistency are outside the present calculus.

## 2. Claims, licenses, and capped rules

Let \(Q\) be a finite set of claims and \(\Lambda\) a finite set of authority licenses. A representative vocabulary can include `THEOREM`, `CONSTRUCTIVE_BOUND`, `FINITE_EXACT`, `PROSPECTIVE`, `FORECAST_ONLY`, `POST_OUTCOME`, `BOUNDED_COMPUTATION`, and `EXTERNAL_REPLAY`.

Each claim \(q\in Q\) has an independent seed label \(\sigma(q)\subseteq\Lambda\). A positive conjunctive rule has a finite body \(A\subseteq Q\), a head \(h\in Q\), and a cap \(K_r\subseteq\Lambda\). Given premise labels \(\ell_a\), the rule may transfer only

\[
K_r\cap\bigcap_{a\in A}\ell_a.
\]

A license therefore crosses a rule only if every premise carries it and the rule itself permits it. Let \(R\subseteq Q\) be the set of directly refuted claims.

## 3. Least-fixed-point semantics

For an assignment \(x\in(2^\Lambda)^Q\), define \(F_R(x)_q=\varnothing\) for \(q\in R\). For every unrefuted claim, \(F_R\) joins its seed label with every capped rule transfer into that claim.

Because union and intersection are monotone on the finite powerset lattice, \(F_R\) is monotone. Iterating from the all-empty assignment reaches a least fixed point, denoted \(Auth_\Lambda(R)\).

**Theorem 1 (finite convergence and order independence).** Fixed-point iteration stabilizes after at most \(|Q||\Lambda|+1\) strict license-addition rounds, and every fair rule-evaluation order reaches the same least fixed point.

The bound follows because, for fixed \(R\), iteration only adds licenses and there are at most \(|Q||\Lambda|\) claim-license pairs.

## 4. Proof trees characterize authority

A finite proof tree for a claim-license pair \((q,\lambda)\) is valid when no node is directly refuted, every leaf seed contains \(\lambda\), and every internal rule cap contains \(\lambda\) while all premises are supported by child trees carrying the same license.

**Theorem 2 (typed proof-tree equivalence).** A license \(\lambda\) belongs to \(Auth_\Lambda(R)_q\) if and only if there exists a finite untainted proof tree for \((q,\lambda)\).

One direction follows by induction on the fixed-point round in which the license first appears; the other follows by induction on proof-tree height.

The theorem exposes the core scientific rule: a conclusion can carry only a license that survives along an entire evidence path. Unsupported cycles remain unsupported. Seeded cycles may propagate only the licenses admitted by every traversed rule.

## 5. Nonpromotion is a structural invariant

Rule caps convert several scientific norms into formal invariants.

A repair rule capped by `POST_OUTCOME` and `FINITE_EXACT` cannot transmit `PROSPECTIVE`, even if the repaired conclusion matches an earlier prediction. A bounded-computation rule capped below `THEOREM` cannot create theorem authority. A theorem license can traverse a path only when every seed and every cap on that path contains it.

This yields a license-conservation corollary: every license present at a conclusion appears in every leaf seed and every rule cap of at least one finite supporting proof tree. The calculus cannot infer a stronger evidence class from repeated agreement or from the wording of the conclusion.

## 6. Typed retraction

Adding a direct refutation can only remove authority.

**Theorem 3 (refutation monotonicity).** If \(R\subseteq R'\), then

\[
Auth_\Lambda(R')_q\subseteq Auth_\Lambda(R)_q
\]

for every claim \(q\).

Alternative derivations survive exactly at the licenses carried by their untainted proof trees. Define typed retraction as the claim-license pairs present before falsification and absent afterward. By Theorem 2, this removes every unsupported pair and retains every pair with a surviving licensed derivation.

This minimality is explicitly relative to the declared seed/rule/cap algebra. General dependency-directed revision and provenance minimality remain donor mathematics.

## 7. Scientific case studies

### 7.1 Forecast falsification and repair

A compact quantum-compilation forecaster combined feasible constructions, an independent structural theorem, and a prospective regime label. A fresh exact row refuted the compact equality. Typed retraction removes universal closed-form exactness and the old prospective regime license while preserving the constructive upper bound and independent theorem. A repaired predictor may regain finite-exact or post-outcome authority, but its cap prevents prospective authority from being retroactively restored.

### 7.2 Decision authority can survive value falsification

A separate representation supports an exact decision theorem while counterexamples show that the same information does not determine exact value or a witness property. These are distinct claim nodes with distinct rule paths. Refuting value sufficiency therefore does not retract the decision theorem. The same representation can be theorem-sufficient for one query and insufficient for another.

### 7.3 Bounded computation cannot become a theorem by repetition

An internal exact frontier computation can carry `BOUNDED_COMPUTATION` and `EXTERNAL_REPLAY` while remaining unlicensed at `THEOREM`. Repeated implementations or large enumerations cannot cross a cap that explicitly denies theorem authority. This prevents a common escalation error in computational mathematics: internal exactness over a bounded frontier does not close an all-size claim.

## 8. Reusable evaluator

The calculus is implemented as a domain-agnostic deterministic evaluator over serialized seeds, capped rules, and refutations. Tests cover unsupported and seeded cycles, cap violations, alternative derivations, and monotonicity under refutation. The evaluator re-derives the registered scientific cases without depending on their development-specific implementations.

This software is a reproducibility layer, not independent external scientific validation. Its role is to make the declared authority policy executable and auditable.

## 9. External X.509 instantiation

To test whether the merge obstruction is merely an artifact of the originating scientific records, we instantiate the typed merge semantics on third-party OpenSSL certificate material. Across 1,962 trust-store merge tasks, 46 cases satisfy the registered hybrid condition: authorization succeeds under a flat union even though neither parent-authorized result licenses the merged outcome.

The typed rule authorizes exactly the parent-authorized set. Under the registered benchmark definitions, zero unsafe typed merges and zero needless typed rejections therefore follow analytically; they are not empirical precision or recall estimates. The corpus contributes different evidence: the hybrid obstruction occurs in third-party material, and alternative merge policies incur measurable unsafe-merge or needless-rejection costs on those cases.

This is an external-domain instantiation, not a security evaluation. No exploitability, attack success, or operational threat model is claimed.

## 10. Relation to prior work and novelty boundary

Truth-maintenance systems and belief revision own dependency-directed update. Positive Datalog owns least-fixed-point semantics. Semiring and annotated provenance own algebraic annotation of recursive derivations, alternative supports, and deletion behavior. Minimal-support and causality frameworks provide closely related support reasoning.

The residual contribution is deliberately smaller: an evidence-license vocabulary for scientific authority, cap-preserving rule semantics that forbids promotion across evidence classes, typed falsification and repair of scientific records, a reusable evaluator, and an external merge obstruction showing that the specialization is non-vacuous.

The paper does not claim a new general theory of provenance minimality or truth maintenance.

## 11. Limitations

The calculus is finite, positive, and conjunctive. Stratified negation, default reasoning, inconsistent evidence, probabilities, and graded belief are outside scope. The license universe and rule caps are declared policy rather than learned objects. Powerset intersection is one useful transfer algebra, not a universal model of scientific authority.

The case studies demonstrate semantics rather than human-science usability. The X.509 instantiation establishes obstruction occurrence and policy costs, not cybersecurity performance or cross-ecosystem transfer. A broader transfer claim would require new native-verifier evidence in independent trust-policy ecosystems and is not part of the present paper.

## 12. Reproducibility and availability

The submission package should expose the formal definitions, proofs, deterministic evaluator, serialized case studies, third-party corpus bindings, and mutation controls. Analytic consequences must be labelled as such so that identities implied by the semantics are not reported as empirical detector performance. Development repository paths and internal workflow chronology belong in artifact documentation rather than the manuscript narrative.

## 13. Conclusion

Scientific falsification should retract evidence authority, not merely conclusion strings. The typed least-fixed-point calculus makes this distinction explicit: a license survives exactly when it has an untainted proof tree whose seeds and rule caps all permit that license. Refutation can remove authority but cannot create it; repairs cannot recover evidence classes they did not earn; and independent derivations survive at their own licensed strength. The result is an executable nonpromotion discipline for scientific records, grounded in established fixed-point and provenance mathematics and supported by an external non-vacuity instantiation.