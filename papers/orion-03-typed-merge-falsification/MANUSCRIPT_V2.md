# Typed Falsification-Aware Scientific Authority as a Least Fixed Point

**Paper D — hardened manuscript V2**
Scientific cut: D1 parent, R2 powerset-license calculus, and three scientific cases
Workflow cut: `academic-paper-skills@188e83e639571c435344630ae68fdc66072650d2`

## Abstract

A falsifier should retract claims by derivation and by evidence type. Boolean dependency graphs solve only the first problem: they can say whether a claim remains derivable, but not whether the surviving derivation licenses a theorem, a finite exact statement, a prospective claim, or a post-outcome repair. We introduce a finite typed authority calculus for positive conjunctive scientific rule systems. Let `Lambda` be a finite universe of authority licenses and label every claim by a subset of `Lambda`. Independent seeds carry declared licenses. Each rule has an explicit cap and may transmit only the intersection of its premises' licenses with that cap. Directly refuted claims are fixed at the empty label. The monotone operator

`F_R(x)_q = empty` for `q in R`,

and otherwise the union of the seed label and all capped rule transfers into `q`, has a least fixed point on the finite powerset lattice.

We prove finite convergence, rule-order independence, and a typed proof-tree theorem: a license reaches a claim exactly when some finite untainted proof tree carries that license in every leaf seed and every rule cap. Unsupported cycles remain bottom; seeded cycles may propagate; adding refutations can only remove licenses; alternative derivations preserve exactly their surviving licenses; and the removed claim-license pairs form the unique minimal typed retraction. The cap mechanism internalizes nonpromotion. A post-outcome repair rule cannot manufacture prospective authority, and bounded computational evidence cannot manufacture theorem authority even when its untyped claim is reachable.

Three cases demonstrate the calculus. A TARE forecast counterexample retracts universal equality and its regime label while preserving an independently constructive upper bound and all-size support theorem; a repaired forecaster remains post-outcome. Paper C's pair and high-order counterexamples retract value and optimizer sufficiency while preserving an independent four-index decision theorem. In the non-quantum `C_5^3` programme, a support-at-least-23 computational frontier remains bounded/external-replay evidence and cannot derive exact `D_4` or `C_0(31)`. Truth-maintenance systems, belief revision, positive Datalog, semiring provenance, minimal-support causality, and deletion robustness are direct donors. The contribution is the license-preserving scientific specialization and exact cross-family nonpromotion behavior.

## 1. Introduction

Scientific records mix claims supported in different ways:

- analytic theorem;
- constructive bound;
- finite exact computation;
- prospective prediction;
- forecast only;
- post-outcome repair;
- bounded computation pending external replay.

A single counterexample may invalidate one layer but not another. An untyped dependency graph can preserve independent derivations, yet it can still overpromote a surviving repair. If a post-outcome predictor becomes exact on the observed panel, it should not inherit prospective authority merely because the old prospective claim and the repair share a conclusion string.

This paper adds evidence licenses to the least-fixed-point calculus. The mathematical substrate is deliberately close to positive Datalog and provenance: finite claims, positive conjunctive rules, monotone iteration, and finite proof trees. The new requirement is scientific nonpromotion—derivability and license must travel together.

### 1.1 Contributions

1. **Powerset-license semantics:** claim authority is a subset of a finite license universe.
2. **Capped transfer:** a rule transmits only licenses present in all premises and permitted by the rule.
3. **Typed proof-tree characterization:** fixed-point licenses are exactly the licenses of finite untainted proof trees.
4. **Typed retraction:** refutation is pointwise monotone and removes the unique minimum set of unsupported claim-license pairs.
5. **Internal nonpromotion:** prospective and theorem licenses cannot appear without a fully licensed proof tree.
6. **Three scientific cases:** forecast falsification, query-specific information falsification, and bounded-computation nonpromotion.

## 2. Claims, licenses, and rules

Let `Q` be a finite claim set and `Lambda` a finite license universe. Example licenses include

`THEOREM`, `CONSTRUCTIVE_BOUND`, `FINITE_EXACT`, `PROSPECTIVE`, `FORECAST_ONLY`, `POST_OUTCOME`, `BOUNDED_COMPUTATION`, `EXTERNAL_REPLAY`.

A label is a subset of `Lambda`, ordered by inclusion. Join is union, bottom is the empty set.

Each claim `q` has an independent seed label `sigma(q) subseteq Lambda`. Each positive rule is a triple

`r=(A -> h, K_r)`,

where `A subseteq Q` is finite, `h in Q`, and `K_r subseteq Lambda` is the rule cap.

For premise labels `ell_a`, define

`tau_r((ell_a)_{a in A}) = K_r intersect intersection_{a in A} ell_a`.

A license can pass a rule only if every premise carries it and the rule cap permits it. A zero-antecedent rule is equivalent to an independent seed and is omitted from the core presentation.

Let `R subseteq Q` be directly refuted claims.

## 3. Typed least-fixed-point semantics

For a label assignment `x in (2^Lambda)^Q`, define

`F_R(x)_q = empty` if `q in R`,

and otherwise

`F_R(x)_q = sigma(q) union union_{r:head(r)=q} tau_r(x|body(r))`.

`F_R` is monotone. Starting from all-empty labels, iterate until stabilization and define

`Auth_Lambda(R)=lfp(F_R)`.

**Theorem 1 (finite convergence and order independence).** The iteration converges after at most `|Q||Lambda|+1` strict license additions. Every fair rule order reaches the same least fixed point.

**Proof.** Labels only gain licenses during an iteration with fixed `R`. There are at most `|Q||Lambda|` claim-license pairs. The operator, not the scan order, defines the least fixed point. ∎

## 4. Typed proof trees

A finite proof tree for `(q,lambda)` is valid under `R` when:

1. its root claim is `q` and no node claim is directly refuted;
2. a leaf `a` has `lambda in sigma(a)`;
3. an internal node applies a registered rule `A->h` whose cap contains `lambda`, and each antecedent has a child proof tree carrying `lambda`.

**Theorem 2 (typed proof-tree equivalence).** License `lambda` belongs to `Auth_Lambda(R)_q` if and only if there exists a finite untainted proof tree for `(q,lambda)`.

**Proof.** Induct on the first iteration round in which the license appears to construct a tree. Conversely, induct on tree height to show that every leaf license enters from a seed and every internal license passes its capped rule. ∎

An untyped authorization set is recovered by retaining claims with nonempty labels, but the typed object contains strictly more information.

## 5. Cycles and nonpromotion

### 5.1 Unsupported cycles

Rules `a->b` and `b->a` with no seed labels have all-empty least fixed point. A cycle is a derivation shape, not evidence.

If `a` has a theorem seed and both rule caps permit `THEOREM`, the license propagates to `b`. If one cap permits only `FINITE_EXACT`, no theorem license crosses that edge.

### 5.2 License conservation

**Corollary 3.** Every license at a conclusion appears in every leaf seed and every rule cap on at least one finite proof tree.

Thus the semantics cannot invent a stronger evidence class.

### 5.3 Post-outcome repair

A repair rule capped by

`{THEOREM, FINITE_EXACT, POST_OUTCOME}`

cannot transmit `PROSPECTIVE`, even if a premise happened to carry both. This makes “repair is not prospective confirmation” a theorem of the authority model rather than a prose convention.

## 6. Typed retraction

**Theorem 4 (refutation monotonicity).** If `R subseteq R'`, then for every claim

`Auth_Lambda(R')_q subseteq Auth_Lambda(R)_q`.

**Proof.** `F_R'(x)` is pointwise contained in `F_R(x)` for every `x`; monotone iteration from bottom preserves containment. ∎

Alternative derivations preserve the union of licenses carried by their surviving proof trees.

Define the pre-falsifier label assignment `A_pre=Auth_Lambda(empty)` and post-falsifier assignment `A_post=Auth_Lambda(R)`. The typed retraction is

`Ret_Lambda(R)={(q,lambda): lambda in A_pre(q)\A_post(q)}`.

**Theorem 5 (unique minimal typed retraction).** `A_post` is the unique assignment that retains every and only claim-license pair with a finite untainted proof tree. Hence `Ret_Lambda(R)` is the unique minimum well-founded typed retraction.

This is semantic minimality: no supported license may be removed and no unsupported license may remain.

## 7. Case I: TARE forecast falsification

The original TARE forecaster combined:

- explicit feasible constructions, licensing a constructive upper bound;
- an independent all-size support-two theorem;
- a compact equality and regime label supported by finite/prospective rows.

A fresh exact row gives `C_DP=10<F=11`. Direct refutation removes universal closed-form exactness and the old regime label. It does not remove the feasible upper-bound license or the independent support theorem.

A repaired support-two forecaster may receive `THEOREM` from the independent support theorem and `POST_OUTCOME` from its construction, but its repair rule cap excludes `PROSPECTIVE`. The original denominator remains 9,545/9,546; the repaired panel is a new evidence object.

## 8. Case II: decision survives value and witness falsifiers

Paper C proves a four-index unary-optimality decision theorem. Separate exact constructions show that complete pair information fails to determine exact value or triple-block presence, and that all proper interaction marginals fail to determine exact value.

The decision claim and value/witness claims therefore occupy separate nodes with separate rules. Refuting pair-value sufficiency removes its licenses but leaves the decision theorem license untouched. Both members of each counterexample pair make the same decision.

This case demonstrates query typing: the same representation can have `THEOREM` authority for a decision query and no exact-value authority.

## 9. Case III: bounded computation cannot decide `D_4`

The non-quantum programme has analytic licenses for the one-unit generalized-Davenport corridor and saturation-defect lemma. An exact internal support-frontier computation reports no length-31 obstruction through support 22, but its own metadata explicitly denies theorem authority and requires external replay.

Assign that frontier licenses

`{BOUNDED_COMPUTATION, EXTERNAL_REPLAY}`.

Any rule from the frontier to “support at least 23” is capped by the same set. No proof tree carries `THEOREM` to exact `D_4(C_5^3)` or `31 in C_0(C_5^3)`. Those claims remain unlicensed at theorem level.

The case is a practical control against a common publication error: repeated internal exact implementations do not automatically become independent mathematical replication.

## 10. Relation to prior work

Doyle's truth-maintenance system, assumption-based truth maintenance, and belief-revision models own dependency-directed update. Positive Datalog owns least-fixed-point rule semantics. Semiring and annotated provenance own typed query annotations, alternative derivations, recursion, and deletion behavior. Recent recursive-Datalog causality work organizes minimal supports as hypergraphs and derives causes, responsibility, and deletion robustness; the 2026 stratified extension shows that negation changes this structure substantially.

The paper therefore claims no generic novelty for fixed points, proof trees, semiring labels, minimal supports, hitting sets, causality, or deletion robustness. Its residual is a deliberately small scientific layer:

- a finite license vocabulary tied to evidence classes;
- cap-preserving rule semantics that encodes nonpromotion;
- exact typed retraction under falsifiers;
- three machine-bound scientific cases in which the distinction changes manuscript claims.

## 11. Reproducibility

The R2 verifier represents licenses as bitsets, checks unsupported and seeded cycles, prospective and theorem caps, and refutation monotonicity. For hundreds of finite random systems, iterative evaluation is compared against exhaustive enumeration of all fixed points to identify the unique least one. The proofs carry general authority.

The three cases bind existing committed evidence objects. A reusable release should serialize claims, seed licenses, rules, caps, and refutations in a public schema and expose a deterministic evaluator.

## 12. Limitations

1. Rules are positive and conjunctive; stratified negation, defaults, probabilistic evidence, and inconsistency are out of scope.
2. The license universe and caps are curated scientific policy, not inferred automatically.
3. Powerset intersection is one useful distributive transfer algebra, not a universal authority algebra.
4. The case studies are scientific/compiler records, not a human-subject usability evaluation.
5. Generic provenance and causality mathematics is donor-owned.
6. Broader AI positioning would benefit from a reusable implementation and external domains.

## 13. Discussion and conclusion

Derivability alone is not scientific authority. A claim can remain derivable under a weaker license, or a repaired claim can regain exactness without regaining prospective status. The typed least fixed point makes those distinctions machine-checkable.

The calculus is fail-closed in two dimensions. Unsupported cycles cannot create claims, and underlicensed derivations cannot create stronger evidence types. At the same time it is minimally destructive: independent proof trees preserve exactly the licenses they still carry.

## Selected references

- J. Doyle, *A Truth Maintenance System*, Artificial Intelligence 12, 231–272 (1979), DOI `10.1016/0004-3702(79)90008-0`.
- J. P. Martins and S. C. Shapiro, *A Model for Belief Revision*, Artificial Intelligence 35, 25–79 (1988).
- C. Bourgaux, P. Bourhis, L. Peterfreund and M. Thomazo, *Revisiting Semiring Provenance for Datalog*, KR 2022, DOI `10.24963/kr.2022/10`.
- M. Abo Khamis et al., *Convergence of Datalog over (Pre-)Semirings*, arXiv:2105.14435.
- R. B. Thapa and S. Staab, *Causality and Minimal Supports in Recursive Datalog*, arXiv:2607.16443 (2026).
- R. B. Thapa and S. Staab, *Causal Explanations for Stratified Datalog*, arXiv:2608.21141 (2026).

## Publication decision record

**Primary targets:** `Journal of Automated Reasoning` or `ACM Transactions on Computational Logic`, resolved after implementation/scope review.
**R2 status:** `STRONG_FORMAL_METHODS_CANDIDATE__TYPE_SYSTEM_INTERNALIZED`.
**Broad-AI stretch:** requires external-domain deployment or evaluation, not stronger rhetoric.
**External-only gates:** primary reference verification, independent semantic review, reusable schema/tool, figures, archive and exact target formatting.
