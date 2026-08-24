# Paper B / B1 — exact rank-only certificate gap

Date: 2026-08-24  
Base: `8ed6d54c66af4bf0404f833dc872a6db6d07a849`  
Status: **FROZEN BEFORE FORMAL B1 ANALYZER AND DUAL-HARNESS RUN**  
Primary owner: `PAPER_B`  
Parent results: QG6 production syndrome-rank inference and QG9 V6 `kappa_R6I=1`.  
Authority ceiling: frozen R6I unit objective plus the explicitly defined proof-system class.

## Scientific gap

The existing archive shows a sound rank-five syndrome certificate and an intrinsic support-one normalization. It does not yet prove that rank five is optimal for a meaningful certificate class, and it does not yet give a scalable separation.

## Rank-only zero-sum deletion proof system

Fix an alphabet `A` contained in `F_2^d`. A proof state is a finite word of active-coordinate syndrome contributions `v_1,...,v_s in A` whose total XOR is nonzero. The sole structural reduction rule deletes a nonempty zero-XOR subword when an attached compiler certificate proves semantics preservation and non-increasing cost (with a strict well-founded decrease on cost ties). The proof system may use vector equality, XOR, the nonzero-total premise, and the deletion certificate; it may not relocate shared state, change contributions, use acceptance semantics beyond the nonzero total, or introduce a whole-system normalization.

Define `beta_ZSD(A)` as the least uniform ceiling `B` derivable from this rule: every admitted nonzero-total word can be reduced to length at most `B`.

This is a deliberately important but limited class. It contains the QG6 rank argument. It does not contain every local proof system and does not contain V6 Tag relocation.

## Exact proof-system theorem

If `span(A)=F_2^d` and `A` contains a basis, then

`beta_ZSD(A)=d`.

Upper bound: any word longer than `d` is linearly dependent, hence contains a nonempty zero-XOR subword. Because the total XOR is nonzero, that subword is proper and the rule applies.

Lower bound: a word consisting of the `d` basis vectors has nonzero total and no nonempty zero-XOR subword. The proof system has no legal first step, so no smaller uniform ceiling is derivable from its rules.

The generic finite-group/matroid statement is donor mathematics (equivalently the zero-sum-free/Davenport boundary for `C_2^d`) and receives no novelty credit.

## Compiler instantiation

QG6 inferred, for each frozen R6I block, a rank-five production change alphabet with an explicit analytic basis contained in the enumerated change-vector set:

- block A: `1,68,136,272,544`;
- block B: `2,4,8,16,32`.

Therefore `beta_ZSD(R6I)=5` for the QG6 proof abstraction. QG9 V6 independently proves `kappa_R6I=1` exactly under the unit objective. The exact single-copy certificate/intrinsic gap is `5 versus 1`.

This means the QG6 proof abstraction is provably unable to derive a uniform ceiling below five without adding a rule or premise outside the defined class. It does **not** prove that every per-block, local, syndrome-aware, or future proof system must fail.

## Scalable direct-product theorem

For `t>=1`, take `t` independent frozen R6I components with additive objectives and direct-sum syndrome quotients. Measure the composite intrinsic budget as the sum of the component generator-support ceilings.

- V6 applied componentwise gives intrinsic total budget `kappa_sum(t)=t`; support zero is infeasible in every component, so this is exact.
- The direct-sum rank-only alphabet contains the union of `t` disjoint five-vector bases. That `5t`-vector word is zero-sum-free in `F_2^(5t)`, while linear dependence gives the matching upper bound. Hence `beta_ZSD_sum(t)=5t` exactly.

The additive certificate gap is `4t`, unbounded. The corresponding certified exhaustive-search polynomial degrees are `5t` versus `t`: `O(n^(5t) A^(5t))` for the rank-only certificate and `O(n^t A^t)` after the intrinsic theorem, within the certified product component.

This is direct-product amplification of the same R6I mechanism, not a second independent compiler mechanism and not a complexity-class lower bound.

## Machine obligations

Source and independent verifier must:

1. bind the positive QG6 and V6 protected receipts and their authority limits;
2. derive rank five from each listed production change alphabet;
3. verify each analytic basis is contained in that alphabet, independent, has nonzero total, and has no nonempty zero-XOR subset;
4. exhaust the abstract standard-basis theorem for `d=1,...,12`;
5. verify product formulas for `t=1,2,3,10,100`;
6. reject on any parent, proof-class, arithmetic, or scope disagreement.

## Authority boundary

No claim is made about all local proof systems, all syndrome-preserving systems, proof length, computational hardness, physical quantum cost, cross-objective behavior, cross-grammar transfer, generic novelty, or venue acceptance. The `t`-fold product uses an explicitly defined summed support budget and is not relabeled as the original single-copy `kappa`. CI is skipped by request and carries no scientific authority.

