# AB R9 Addendum: An Unbounded Family of Certificate Waste under Complete Fusion

## 1. Purpose

The registered five-bit XOR grammar exhibits a support-five terminal state for zero-sum deletion but a support-one normal form once pair fusion is admitted. This addendum proves that the phenomenon is not isolated.

For every finite abelian group, a complete binary-fusion grammar has intrinsic support one, while the zero-sum deletion proof language has exact terminal complexity equal to the Davenport constant minus one. The resulting certificate waste is `D(H)-2`, which is unbounded on elementary two-groups.

The theorem is a production-realization counterexample family. It is not a claim about every compiler or every Pauli grammar: complete fusion is an explicit production capability that must be justified in any application.

## 2. Two move systems over one production state space

Let `H` be a finite abelian group and let `A=H\{0}`. A production state is a finite nonempty word or multiset over `A` whose total sum is nonzero. Its declared semantics is the total group element and its support objective is its length.

### Weak certificate language `W_H`

A weak move deletes any nonempty zero-sum subsequence. Because the total state sum is nonzero, every such subsequence is automatically proper.

### Complete fusion language `F_H`

A fusion move selects two letters `x,y`.

- If `x+y != 0`, replace them by the single letter `x+y`.
- If `x+y = 0`, delete both letters.

The second case cannot empty a legal state: a two-letter state with sum zero would not belong to the production family. Every fusion preserves total semantics and strictly lowers support.

The move registry is complete by definition. No other production shortening move is admitted in this grammar.

## 3. Weak terminal complexity

Let `D(H)` denote the classical Davenport constant: the least integer such that every sequence of that length over `H` has a nonempty zero-sum subsequence.

### Theorem 1 — exact weak certificate complexity

The maximum support of a `W_H`-terminal production state is

`beta_W(H) = D(H)-1`.

**Proof.** Any state of length at least `D(H)` contains a nonempty zero-sum subsequence and is therefore reducible. Conversely, a maximum zero-sum-free sequence has length `D(H)-1`; its total is nonzero, since otherwise the whole sequence would be a nonempty zero-sum subsequence. It is a legal production state and terminal under `W_H`. ∎

This is exact for the named weak proof language. It is not yet an intrinsic production lower bound.

## 4. Complete fusion normal form

### Theorem 2 — unique singleton normal form

Every legal production state in `F_H` reduces to the singleton containing its total sum. This singleton is the unique normal form.

**Proof.** Every move preserves the total sum and strictly reduces support, so every reduction terminates. A terminal state cannot contain two letters, because every pair admits a fusion move. Hence every terminal state is a singleton. Its sole letter must equal the invariant total sum. The total is nonzero, so this singleton is legal. Thus all maximal reductions terminate at the same state. ∎

### Corollary 3 — confluence and complete interaction closure

`F_H` is confluent. Every deletion/deletion, deletion/fusion, and fusion/fusion peak in the combined language joins at the singleton total.

The conclusion follows from termination and the unique normal form. It is stronger than checking a bounded collection of local peaks, although bounded checks remain useful as implementation controls.

### Corollary 4 — intrinsic production support

The complete fusion grammar has intrinsic production support

`kappa_F(H)=1`.

Every state reaches support one, and support zero is infeasible because production states have nonzero total semantics.

## 5. Exact certificate waste

### Theorem 5 — all-group separation

For the common production state space above,

`beta_W(H) - kappa_F(H) = D(H)-2`.

A maximum zero-sum-free state realizes the weak terminal lower witness, but it is reducible under the complete production move registry whenever its support exceeds one. Therefore it fails the complete-move irreducibility clause of the production-realization gate.

### Corollary 6 — unbounded waste on elementary two-groups

For `H=C_2^r`, the classical identity `D(C_2^r)=r+1` gives

`beta_W(C_2^r)=r`,

`kappa_F(C_2^r)=1`,

and certificate waste `r-1`.

The registered `C_2^5` example is the case `5 -> 1`, with waste four. As `r` grows, the proof-language overestimate is unbounded.

## 6. Weak deletion is production-sound but incomplete

Every weak zero-sum deletion can be implemented by repeated fusions among the selected letters. Pair sums that become zero disappear; nonzero pair sums remain selected for subsequent fusion. Since the selected total is zero, the selected letters eventually vanish without changing letters outside the subsequence.

Thus the weak language is not unsound. It is incomplete as a normal-form language: it refuses nonzero pair aggregation even though the production grammar admits it.

This distinction is central. A certificate gap can arise from omitted sound moves, not only from invalid abstractions.

## 7. Direct-enumerator consequence

Consider a declared direct support enumerator with `n` coordinate positions and `q=|H|-1` nonzero labels per selected position.

Using the weak cap `D(H)-1`, its search volume is

`sum_{j=0}^{D(H)-1} binom(n,j) q^j`,

with leading term

`q^(D(H)-1) n^(D(H)-1) / (D(H)-1)!`.

Using the complete fusion cap one, the volume is

`1+qn`.

This is an exact consequence for the declared enumerator architecture. It is not an algorithm-independent lower bound and does not by itself establish runtime improvement in a production implementation.

## 8. Executable controls

The registered verifier implements finite abelian groups as coordinate tuples, independently constructs weak deletions and complete fusions, and checks:

1. the expected maximum weak terminal support;
2. preservation of total semantics by every move;
3. strict support descent;
4. the unique singleton normal form under every fusion path; and
5. agreement between the analytic and enumerated certificate gaps.

The bounded panel includes cyclic groups, elementary two-groups, `C_2 x C_4`, and `C_3 x C_3`. These computations corroborate the implementation only. The all-group result follows from Theorems 1 and 2.

## 9. Publication boundary

The theorem establishes an unbounded family of exact proof-language waste with a complete production move registry and a realizing weak terminal state. It does **not** establish that a particular quantum compiler, TARE grammar, or synthesis system has complete binary fusion.

Promotion to an application requires:

- an explicit representation map into the group grammar;
- a proof that every fusion is admissible and semantics-preserving in the production system;
- objective nonincrease for fusion;
- a complete registry of competing production moves; and
- a measured consequence in the named production search architecture.

Absent those items, the theorem is a sharp abstraction-boundary result rather than a production compiler theorem.
