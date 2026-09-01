# Mathematical Extensions R4 — Compositional and Robust Zero-Sum Normal Forms

Date: 2026-08-25

Canonical predecessor: `MANUSCRIPT_V3_PIPELINE.md`

Status: theorem addendum for integration into the next manuscript version. The results below use the definitions and grammar of the V3 manuscript. They do not assert equivalence with a production TARE implementation or a physical resource advantage.

## 1. Purpose

The V3 manuscript proves an exact support normal form from three ingredients: a finite signature group, a persistent semantics-preserving zero-sum deletion, and an objective inequality making that deletion non-increasing. This addendum develops three consequences that make the theorem more useful outside a single monolithic instance:

1. exact composition across independent signature components;
2. quotient lower bounds and a finite integer formulation for the alphabet invariant; and
3. an approximate normal form when the objective cone is missed by a controlled amount.

These extensions separate the exact combinatorics from compiler-specific modeling assumptions and expose algorithmic uses of the normal form.

## 2. Direct-sum additivity for axis-separated alphabets

Let `H_1,H_2` be finite abelian groups, let `A_i subseteq H_i`, and set

`H = H_1 direct_sum H_2`,

`A = (A_1 x {0}) union ({0} x A_2)`.

Thus every allowed letter belongs to exactly one coordinate axis.

**Theorem A1 (axis direct-sum additivity).**

`zsf(H;A) = zsf(H_1;A_1) + zsf(H_2;A_2)`.

**Proof.** Choose zero-sum-free words `W_i` over `A_i` of maximum length. Embed `W_1` and `W_2` on the two axes and concatenate them. A zero-sum subsequence of the concatenation would project to a zero-sum subsequence in each component. Any nonempty selected part on either axis would contradict zero-sum-freeness of the corresponding `W_i`; hence no nonempty zero-sum subsequence exists. This gives the lower bound.

Conversely, let `W` be zero-sum-free over `A`, and split its positions into the two axes. If the first-axis subword had length greater than `zsf(H_1;A_1)`, it would contain a nonempty zero-sum subsequence, which would also be zero-sum in `H`. The same holds for the second axis. Therefore the two subword lengths are at most their respective invariants, and their sum is at most the stated right-hand side. ∎

**Corollary A2 (finite direct sums).** For finite groups `H_i` and the union of their coordinate-axis alphabets,

`zsf(direct_sum_i H_i; union_i A_i) = sum_i zsf(H_i;A_i)`.

The proof is induction on the number of components.

### Compiler consequence

Suppose a compiler instance decomposes into independent registered components, every semantic signature is axis-separated, the objective is additive, and admissible deletions do not cross components. Applying the V3 deletion theorem componentwise yields an optimum whose total support budget is the sum of the component alphabet budgets. A matching lower statement remains a certificate-language fact unless each component has a realized terminal witness and the production grammar forbids additional reductions.

This theorem gives a principled alternative to replacing a structured signature space by one large ambient rank. It also identifies exactly when componentwise preprocessing loses no certificate strength.

## 3. Quotient lower bounds

Let `phi:H -> K` be a homomorphism and put `B=phi(A)`.

**Theorem A3 (homomorphic lower bound).**

`zsf(H;A) >= zsf(K;B)`.

**Proof.** Let `b_1,...,b_r` be a zero-sum-free word over `B` of maximum length. For every occurrence choose a lift `a_i in A` with `phi(a_i)=b_i`. If a nonempty subsequence of the lifted word summed to zero in `H`, its image would be a nonempty zero-sum subsequence of the word over `B`, a contradiction. Thus the lift is zero-sum-free. ∎

The direction is important: a quotient can certify that the original alphabet invariant is at least a certain value. It does not supply an upper bound. In a compiler proof, this provides a cheap obstruction test against over-aggressive support claims. If a small quotient already contains a long zero-sum-free word, no deletion theorem using the original alphabet can have a smaller universal terminal budget.

## 4. A finite integer formulation

Write `A={a_1,...,a_m}` and let `o_i` be the order of `a_i` in `H`.

**Proposition A4 (multiplicity formulation).** `zsf(H;A)` is the optimum of

`maximize sum_i u_i`

subject to

`0 <= u_i <= o_i-1`, `u_i integer`,

and

`sum_i v_i a_i != 0`

for every nonzero integer vector `v` satisfying `0 <= v_i <= u_i`.

**Proof.** A word is determined up to order by its multiplicities `u_i`. If `u_i >= o_i`, then `o_i` copies of `a_i` form a zero-sum subsequence, so every zero-sum-free word satisfies the displayed box constraints. The remaining family of constraints says exactly that no nonempty submultiset has sum zero. Conversely, any feasible multiplicity vector defines a zero-sum-free word. ∎

The formulation is finite because each multiplicity has a group-order bound. It is not asserted to be polynomial-time solvable. Its practical value is that `zsf(H;A)` can be computed once for a realized alphabet and then used as a compiler search cap. Quotient bounds from Theorem A3 can prune the calculation, while Theorem A1 decomposes it when the alphabet is axis-separated.

## 5. Approximate normal forms outside the exact cone

The exact V3 theorem assumes that every admitted zero-sum deletion is non-increasing. Two controlled relaxations remain possible.

Let an initial optimum have support `n` in one constrained generator and let `z=zsf(H;A)`. Assume the semantic and nonzero-total hypotheses persist after every deletion.

**Theorem A5 (event-defect normal form).** Suppose every admitted zero-sum deletion increases the objective by at most `epsilon`, independently of the number of deleted coordinates. Then there is a feasible state of support at most `z` and cost at most

`OPT + epsilon max(0,n-z)`.

**Proof.** While support exceeds `z`, the current word contains a nonempty proper zero-sum subsequence. Delete one. Every step lowers support by at least one, so there are at most `n-z` steps. Summing the per-step defect gives the result. ∎

**Theorem A6 (per-coordinate defect normal form).** Suppose deleting a zero-sum subsequence `T` increases the objective by at most `delta |T|`. Then there is a feasible state of support at most `z` and cost at most

`OPT + delta n`.

**Proof.** Run the same descent. Deleted coordinate sets are disjoint over time, so the total number of deleted coordinates is at most `n`. Telescope the objective changes. ∎

For the explicit multi-Tag Pauli grammar, one deleted frame coordinate refunds at least `mu` and can add at most `(b-1)t_R` to Restore cost. Therefore

`delta = max(0,(b-1)t_R-mu)`

is a valid per-coordinate defect. The exact cone is recovered at `delta=0`.

**Corollary A7 (robust MultiTag support cap).** If the V3 grammar is otherwise unchanged, every instance admits a support-normalized feasible state with

`support(R) <= rank(H_R) <= s+1`

and additive objective loss at most `delta N_R` for frame `R`, where `N_R` is its pre-normalization support and `delta` is defined above.

This is an approximation guarantee for the declared structural objective. It is not a statement about circuit fidelity, T count, depth, or hardware performance.

## 6. Algorithmic implications

### 6.1 Modular exact search

When signatures split into independent axes, Theorem A1 permits independent enumeration up to each exact component budget instead of one ambient support cap. For fixed component budgets, this can reduce a direct support search from a single high-dimensional enumeration to a product of smaller tables.

### 6.2 Quotient diagnostics

A quotient may expose a basis obstruction or another long zero-sum-free word before any compiler search begins. This is useful as a fail-fast check: a claimed support ceiling below the quotient invariant is impossible for the stated deletion language.

### 6.3 Graceful optimization outside a proof-validity cone

Theorems A5 and A6 turn a brittle exact-cone theorem into a quantitative tradeoff. A compiler designer can compare support reduction against a certified structural-cost defect rather than treating the theorem as either fully applicable or useless.

### 6.4 Transfer beyond Pauli grammars

The abstract results apply to any finite edit system in which coordinates carry finite-group signatures, a zero-signature edit preserves the declared semantics, and edit cost is controlled. Potential domains include modular constraint repair, syndrome-preserving sparse optimization, and finite-state normalization. These are mathematical transfer routes, not validated deployments.

## 7. Integration into the manuscript

The next integrated manuscript should make the following changes.

1. Add Theorems A1 and A3 after the binary-rank corollary to establish composition and lower-bound diagnostics.
2. Add Proposition A4 to the reproducibility or methods section as the exact finite computation problem for a realized alphabet.
3. Add Theorems A5 and A6 after the exact MultiTag theorem, clearly separated as approximate statements.
4. Replace a generic application paragraph by the four specific use cases in Section 6.
5. Preserve the V3 boundary that the Pauli grammar is motivated by TARE but is not proved equivalent to the full production construction.

## 8. Atomic claim status

- Axis direct-sum additivity: `VERIFIED` by the displayed two-sided proof.
- Homomorphic lower bound: `VERIFIED` by lifting a maximum image word.
- Multiplicity formulation: `VERIFIED` from the order bound and submultiset equivalence.
- Event-defect normal form: `VERIFIED` under the stated persistent deletion hypotheses.
- Per-coordinate defect normal form: `VERIFIED` under the stated telescoping hypothesis.
- MultiTag defect coefficient: `VERIFIED` from the V3 local sensitivity lemma.
- Production-compiler or physical-resource benefit: `NOT_CLAIMED`.

## 9. Editorial effect

The addendum changes Paper A from a single-instance normal-form result into a small compositional theory with an exact, computable invariant and a controlled approximation regime. The strongest remaining gate is external significance: a selective quantum-compilation venue may still require proof that the declared grammar captures a production-relevant optimization and that the support cap changes a meaningful compiler workload.