# Mathematical Extensions R6 — Exact R6I Rank-Only Certificate Complexity: Five Versus One

Date: 2026-08-26

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md`, `MATHEMATICAL_EXTENSIONS_R4.md`, `MATHEMATICAL_EXTENSIONS_R5.md`, and the frozen Paper-B/B1 protocol and report in `development/orion-qg-regime-geometry/`

Status: rigorous production-instantiated theorem addendum for one explicitly defined proof-system class and the frozen R6I unit objective. It does not lower-bound every local compiler proof system.

## 1. Status correction and contribution

R5 correctly warned that the abstract value five and the independently proved intrinsic value one did not, by themselves, establish a production certificate gap. A separately frozen B1 analysis subsequently supplied the missing realization for a precise class: the rank-only zero-sum-deletion proof system containing the QG6 rank argument.

This addendum integrates that already verified result into the paper. The central statement is now exact and scoped:

- certificate complexity in the named R6I rank-only proof abstraction: five;
- intrinsic support under the independently frozen V6 unit objective: one;
- exact single-copy gap: four;
- exact `t`-component direct-product budgets: `5t` and `t`.

The phrase “local proof systems fail” remains withdrawn. Only the declared class is covered.

## 2. The rank-only zero-sum-deletion class

Let `A subseteq F_2^d` be the production change alphabet. A proof state is a finite word of active-coordinate syndrome contributions with nonzero total XOR. The only structural reduction deletes a nonempty zero-XOR subword after an attached compiler certificate proves semantics preservation and non-increasing cost, with a strict well-founded decrease on cost ties.

The class may use vector equality, XOR, the nonzero-total premise, and the deletion certificate. It may not relocate shared state, replace contributions, invoke additional acceptance semantics, or introduce a whole-system normalization.

Write `beta_ZSD(A)` for the least uniform terminal-length ceiling derivable inside this class.

## 3. Exact abstract boundary

**Theorem B11 (rank-only certificate boundary).** If `span(A)=F_2^d` and `A` contains a basis, then

`beta_ZSD(A)=d`.

**Proof.** Any word of length greater than `d` is linearly dependent, so it contains a nonempty zero-XOR subword. Because the full word has nonzero total XOR, the deleted subword is proper; the declared reduction applies. This gives `beta_ZSD(A)<=d`.

For the reverse inequality, take a word consisting of the `d` basis vectors. Its total XOR is nonzero and no nonempty subword has zero XOR. The proof system has no legal first reduction, so no uniform ceiling below `d` can be derived from its rules. ∎

The finite-group and matroid content of this theorem is donor mathematics. Its role here is to make the proof-system boundary explicit enough to instantiate and falsify.

## 4. Frozen R6I instantiation

The QG6 production analysis identified rank-five change alphabets for both frozen R6I blocks and registered the following analytic bases inside those enumerated alphabets:

- block A: `1, 68, 136, 272, 544`;
- block B: `2, 4, 8, 16, 32`.

Each listed set has GF(2) rank five, nonzero total XOR, and no nonempty zero-XOR subset.

**Theorem B12 (exact R6I proof gap).** Under the frozen QG6 rank-only proof abstraction and the frozen V6 unit objective,

`beta_ZSD(R6I)=5`

and

`kappa_R6I=1`.

Consequently, the exact certificate-versus-intrinsic support gap is

`5-1=4`.

**Proof.** Theorem B11 applied to either registered production basis gives the matching upper and lower certificate bounds. The independent V6 receipt proves support one feasible and support zero infeasible under the unit objective. The two results concern the same frozen R6I component and the stated authority ceilings. ∎

This theorem says that the QG6-style abstraction cannot prove a uniform ceiling below five without adding a premise or move outside the class. V6 succeeds precisely by using a whole-system Tag relocation excluded from that class.

## 5. Direct-product amplification

Take `t` independent frozen R6I components with additive unit objectives and direct-sum syndrome quotients. Measure support by the sum of component generator supports.

**Theorem B13 (exact product separation).** For every `t>=1`,

`beta_ZSD_sum(t)=5t`

and

`kappa_sum(t)=t`.

Hence the additive gap is `4t`.

**Proof.** Componentwise V6 gives a support-one construction in every component, while support zero is infeasible in every component, so the intrinsic sum is exactly `t`. The direct-sum change alphabet contains `t` disjoint five-vector bases. Their union is a zero-sum-free word of length `5t`; linear dependence in `F_2^(5t)` supplies the matching upper bound. ∎

For a direct labeled-support enumerator, the certified polynomial degrees are therefore `5t` versus `t`. This is an architecture-specific enumeration statement, not a complexity-class or physical-runtime lower bound.

## 6. Receipt binding

The frozen report records agreement among the source analyzer, an independent generic verifier, and a native manifest. It also records four fresh-workspace reproductions and focused tests. The principal protected objects include:

- B1 protocol SHA-256 `30d18a0ec53027634fb48a460da4e20fede9092264515dc5d5b1af7153afa59c`;
- QG6 result-file SHA-256 `51d5ffcdd682384cc2259146d0c7e9a835c4644d1cffa36c6d9fca0d1c06f884`;
- V6 result-file SHA-256 `f8df10d5604267e43701adb032f33baf1dfaa5a6572e5bdeaeda7707c4100b66`.

The R6 portfolio verifier independently recomputes the ranks, nonzero totals, absence of zero-XOR subsets, abstract basis rows for `d=1,...,12`, and product arithmetic for `t=1,2,3,10,100`. It is corroboration, not a replacement for the protected production receipts.

## 7. What is now complete

Within the named class, Paper B now has all four pieces needed for an exact separation:

1. a formal proof language;
2. a production alphabet satisfying its hypotheses;
3. a matching irreducible terminal witness; and
4. an independently proved stronger production normalization outside the class.

This closes the paper's central rank-only proof-gap theorem. It does not establish optimality against a future proof system that adds other production semantics.

## 8. Prior-art and novelty calibration

Linear dependence, zero-sum-free basis words, direct sums, and sparsification are established mathematics. No generic novelty is assigned to `beta_ZSD(A)=d`. The residual contribution is the exact R6I production-alphabet instantiation, the formal identification of which QG6 proof rules are being lower-bounded, the exact `5` versus `1` separation under bound objectives, and its direct-product consequence.

## 9. Atomic status

- Abstract rank-only boundary: `VERIFIED`.
- R6I block-A and block-B basis properties: `MACHINE_CORROBORATED` and bound to protected receipts.
- Rank-only production certificate complexity five: `VERIFIED` inside the named class.
- Frozen V6 intrinsic support one: `VERIFIED` under the unit objective.
- Single-copy gap four and product gap `4t`: `VERIFIED`.
- Lower bound for every local or syndrome-aware proof system: `NOT_CLAIMED`.
- Physical T-count, depth, qubit, or runtime advantage: `NOT_CLAIMED`.

## 10. Remaining scientific frontier

Paper B no longer needs another abstract amplification. The next non-duplicative question is proof-language robustness: identify one additional production rule family not expressible as zero-sum deletion, determine whether it reduces the five-vector witness, and either enlarge the exact lower-bounded class or exhibit the rule that destroys the separation. The present theorem is complete at its declared boundary.
