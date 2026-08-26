# Mathematical Extensions R7 — A Production-Instantiated Five-to-One Proof-Language Separation

Date: 2026-08-26

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md`, `MATHEMATICAL_EXTENSIONS_R4.md`, `MATHEMATICAL_EXTENSIONS_R5.md`, `MATHEMATICAL_EXTENSIONS_R6.md`, and the frozen Paper-B B1 result/dual-harness records.

Status: theorem and manuscript-correction addendum. It restores a repository result omitted from the earlier paper-level synthesis. The theorem is exact for the named R6I rank-only zero-sum-deletion proof class and the frozen unit objective. It is not a lower bound for every local or syndrome-aware proof system.

## 1. Correction to the earlier realization verdict

The repository contains a frozen production-instantiation record with the following checked facts.

- Each of the two R6I production change alphabets has rank five.
- Each contains an explicit five-vector basis.
- The basis word has nonzero total XOR and no nonempty zero-XOR subword.
- The corresponding rank-only deletion proof language therefore has exact certificate complexity five.
- An independently protected whole-system Tag-relocation theorem gives exact intrinsic support one; support zero is infeasible.
- Source, generic verifier, native verifier, and dual-harness decisions agree.

The correct paper-level statement is therefore the scoped theorem below.

## 2. Named proof class

The proof language `P_ZSD` may use equality and XOR in the frozen binary syndrome quotient, the premise that the total syndrome is nonzero, and deletion of a certified proper zero-XOR subword. It may not relocate Tags, relabel contributions outside deletion, invoke a whole-system normalization, or use acceptance semantics beyond the nonzero-total premise.

## 3. Exact single-copy separation

**Theorem B11 (R6I proof-language separation).** For the frozen R6I production change alphabets and unit objective,

`beta_{P_ZSD}=5`

while the intrinsic compiler support is

`kappa_R6I=1`.

Hence the exact scoped certificate/intrinsic ratio is five and the additive gap is four.

**Proof.** Linear dependence gives the rank-five upper certificate. The explicit basis word in each enumerated production alphabet is zero-sum-free and has nonzero total, so `P_ZSD` has no legal first step and cannot certify a smaller uniform bound. The protected support-one normalization relocates the shared Tags and removes every non-core frame letter without increasing cost. Support zero is infeasible because the independent frames must anticommute. ∎

The lower witness belongs to the named proof-state language over the enumerated production alphabet. It is not asserted to block a stronger production proof language.

## 4. Proof-language monotonicity and collapse

Let `P subseteq Q` mean that every `P` move and premise is available in `Q`.

**Theorem B12 (move-language monotonicity).**

`beta_Q <= beta_P`.

If `Q` additionally contains a sound whole-system support-one normalization and support zero is infeasible, then `beta_Q=1`.

**Proof.** Every reduction sequence available to `P` remains available to `Q`, so adding rules cannot increase the least certifiable terminal ceiling. The support-one normalization gives the upper bound one, and infeasibility of support zero gives equality. ∎

For R6I, adjoining the Tag-relocation rule collapses the exact certificate from five to one. The separation therefore identifies a missing proof operation, not merely a loose numerical estimate.

## 5. Direct products and applicability scopes

For `t` disjoint R6I components with additive support and no cross-component move,

`beta_{P_ZSD}^{(t)}=5t`

and

`kappa^{(t)}=t`.

Thus the additive gap is `4t`.

The R6 interaction-hypergraph theorem gives the correct generalization. Create a hyperedge containing every component whose state can affect the applicability or result of one proof move. The terminal budget is additive over connected components of this hypergraph. A shared Tag, global frame change, or global reconstruction must therefore be recorded in the move scope even when its output is written locally.

**Corollary B13 (auditable amplification).** A direct-product certificate amplification is valid only after all move-applicability dependencies have been included and the resulting interaction components have been frozen. Omitting a shared auxiliary can fabricate a false product theorem.

## 6. Search-volume consequence

For a direct support enumerator with `n` candidate coordinates per component and fixed local label alphabet, the certified polynomial degrees are `5t` under `P_ZSD` and `t` after the intrinsic theorem. The ratio is polynomial of degree `4t`, with the exact leading constant given in R5.

This is architecture-specific bookkeeping. It is not a complexity-class lower bound and does not constrain algorithms that avoid explicit support enumeration.

## 7. Applications

The theorem supports proof-language design, proof-carrying exact search, and modular certification. A certificate can be audited by asking which semantic operation is frozen. Search budgets can be attached to the proof language that justifies them rather than reported as intrinsic compiler constants. The interaction hypergraph determines which components may be certified independently and where shared auxiliaries invalidate product reasoning.

## 8. Ownership and limitations

Finite-field dependence, zero-sum-free basis words, and direct sums are donor mathematics. The residual contribution is the exact R6I production-alphabet instantiation, the independently verified support-one normalization, and the explicit separation between two proof languages on the same frozen compiler model.

No theorem is claimed for all local proof systems, all syndrome-preserving systems, another objective, another grammar, physical resources, or quantum advantage.

## 9. Atomic status

- Rank-five production alphabet and basis obstruction: `VERIFIED` by frozen source and dual records.
- Intrinsic support one: `VERIFIED` by protected generic/native acceptance and support-zero infeasibility.
- Exact `5 versus 1` separation: `VERIFIED` in `P_ZSD` and the frozen unit objective.
- Product gap `4t`: `VERIFIED` under the explicit no-cross-component scope.
- Lower bound for every production proof language: `NOT_CLAIMED`.
