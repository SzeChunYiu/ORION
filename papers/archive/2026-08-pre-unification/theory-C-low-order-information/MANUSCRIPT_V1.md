# Low-Order Optimality Certificates Do Not Determine Optimization Value

**Paper C — publication-candidate manuscript**

## Abstract

Can a global combinatorial optimizer be decided from low-order information even when that same information cannot determine the value or structure of the optimum? We answer this exactly for a frozen Pauli partition compiler with structural `SELECT+PREP+WIDTH` cost. For every number of terms `m>=5`, equality between the full set-partition optimum and the unary compiler is characterized by two clause families involving at most four term indices: every pair gain is nonpositive, and every sum of two disjoint pair gains plus one is nonpositive. The threshold is sharp: an explicit four-term instance satisfies every such clause but improves from unary cost 27 to one-block cost 23. Decision simplicity does not extend to value. For every `t>=1`, two `5t`-term instances have identical ordered weights and the complete labeled pair-gain matrix, and both strictly beat unary, yet their exact improvements differ by `2t-1`; moreover, every optimum in one family contains a triple block while every optimum in the other uses only pairs and singletons. We strengthen the information separation to arbitrary fixed order. For every `m>=5` and `L>=1`, two instances agree on every labeled common-factor count through order `m-2` but have exact improvements separated by `[m(ceil(log2 m)+1)-1]L`. Finally, Boolean-lattice Möbius inversion proves that the exponential difference support of this construction is unavoidable: any nonzero integer trade preserving every proper labeled marginal is an integer multiple of the parity trade, occupies all `2^(m-1)` interaction cells, and has at least `2^(m-2)` columns on each signed side. Thus low-order information can be complete for a binary optimality decision while remaining arbitrarily incomplete for value and optimizer structure, and exact proper-marginal indistinguishability itself can require exponentially large witnesses.

## 1. Introduction

Optimization problems are often attacked by finding a compact certificate for a decision question rather than reconstructing the full optimum. A local certificate can be extremely useful: it may tell us that a baseline is optimal, that a proposed modification cannot help, or that a search can stop. But a decision certificate need not contain enough information to answer richer questions about the magnitude or structure of improvement.

This paper isolates that separation in one exact compiler model. The compiler partitions `m` Pauli terms into arbitrary blocks, may factor a common Pauli component inside each block, and pays a frozen structural `SELECT+PREP+WIDTH` objective. The optimizer ranges over all set partitions, whose number grows super-exponentially with `m`. Nevertheless, the question

> Is the unary compiler already globally optimal?

has an exact certificate whose largest clause touches only four indices.

That result raises a sharper information question. If all pair information is enough to decide optimality, is it also enough to determine how much the optimum improves or what the optimal partition looks like? The answer is no in a scalable way. We then ask the same question after giving the observer every labeled interaction through order `m-2`. Exact value is still not determined.

The final theorem explains why the high-order counterexample is necessarily large. The two instances differ by an integer table on the Boolean lattice of variable supports. Equality of all proper labeled marginals says exactly that the zeta transform of this difference vanishes away from the top element. Möbius inversion leaves a one-dimensional kernel: the parity vector. Consequently, every nonzero proper-marginal-preserving trade uses every Boolean cell, with equal positive and negative mass. The parity construction is therefore support-minimal.

The generic mathematics of marginal fibers, Markov bases, Möbius inversion and hierarchical interactions is established prior work. Our contribution is the exact compiler realization and the resulting hierarchy:

`constant-order decision certificate < pair information for value/optimizer < all proper interaction data for value`.

### 1.1 Contributions

**C1 — all-`m` low-order decision theorem.** For every `m>=5`, unary optimality is equivalent to pair nonpositivity plus two-disjoint-pair clauses. Maximum clause support is four term indices.

**C2 — sharp lower term-count boundary.** The certificate fails at `m=4` on an explicit exact instance.

**C3 — complete-pair-information separation.** Identical ordered weights and identical complete labeled pair gains leave unbounded exact-value ambiguity and force incompatible optimizer structures.

**C4 — arbitrary-order value separation.** Agreement on every labeled common-factor count through order `m-2` still leaves an exact-value gap growing linearly in a free scale parameter.

**C5 — sharp trade minimality.** Any nonzero integer trade preserving all proper labeled marginals is an integer multiple of the parity trade; the registered construction attains the minimum possible signed mass and cell support.

## 2. Frozen partition compiler

An instance consists of ordered nonidentity Pauli strings

`p_1,...,p_m in {I,X,Y,Z}^n \ {I^n}`.

Let `w_i` be the support weight of term `i`, `W=sum_i w_i`, and for any nonempty term set `S` let `f(S)` be the number of qubit columns on which every term in `S` carries the same nonidentity Pauli.

The compiler may choose any set partition `Pi` of `[m]`, independently enable common-factor extraction inside each block, and choose shared or dedicated index ancillas. Under the frozen equal-weight structural objective, factor extraction and shared width weakly dominate their alternatives. For a partition with at least two blocks the exact reduced cost is

`C(Pi)=2m+k-3 + sum_{S in Pi} d(|S|) + max_{S in Pi} b(|S|)`

`       + sum_{S in Pi} [2 f(S) + (b(|S|)+2)(w(S)-|S|f(S))]`,

where `k=|Pi|`, `b(s)=ceil(log2 s)` with `b(1)=0`, and the balanced PREP-depth recurrence is

`d(1)=0`,

`d(s)=d(ceil(s/2))+d(floor(s/2))+s-2`.

The unary incumbent costs

`C_U=2W+3m-3`.

The one-block partition has a separate flag convention and is handled explicitly in the theorem. These are structural compiler costs, not physical T counts, runtime, depth or fault-tolerant overhead.

## 3. A four-index certificate decides unary optimality

For each pair `{i,j}`, define the pair gain

`g_ij = 4 f({i,j}) - (w_i+w_j)`.

Let `P4(m)` consist of:

1. `g_ij <= 0` for every pair;
2. `g_ij + g_kl + 1 <= 0` for every two disjoint pairs.

**Theorem 1 (all-`m` decision certificate).** For every `m>=5` and every admitted instance,

`min_Pi C(Pi) = C_U`

if and only if `P4(m)` holds.

### 3.1 Gain decomposition

For a block `S` of size `s`, set

`T_s(S)=[s(b(s)+2)-2]f(S)-b(s)w(S)`.

For every partition with at least two blocks,

`C_U-C(Pi)=sum_{S in Pi} T_|S|(S)+c(Pi)`,

with

`c(Pi)=sum_{S in Pi} (|S|-1-d(|S|))-max_{S in Pi}b(|S|)`.

The recurrence gives `|S|-1-d(|S|)=1` for sizes two, three and four, zero at size five, and nonpositive thereafter.

### 3.2 Large blocks are controlled by pair clauses

For a block `S` of size at least three, sum pair nonpositivity over a perfect matching when `s` is even or an `s`-cycle when `s` is odd. Each selected pair has common factor at least `f(S)`, yielding

`w(S) >= 2s f(S)`.

Substitution gives

`T_s(S) <= [s(2-b(s))-2]f(S)`.

If `f(S)>=1`, this is at most `-2`; if `f(S)=0`, nonidentity terms make it at most `-b(s)s<=-6`. Thus every block of size at least three pays enough negative gain to offset the possible positive shape constant.

### 3.3 Arbitrarily many pair blocks collapse to four indices

Pair blocks in one partition are disjoint. Clause 1 makes every pair gain a nonpositive integer. Clause 2 prevents two disjoint pair gains from both being zero. Hence among `r>=2` pair blocks, at most one has gain zero and the rest are at most `-1`, so their total gain is at most `-(r-1)`, exactly offsetting the all-pair shape term. Mixed partitions are handled by the `-2` contribution of any block of size at least three.

### 3.4 One-block partition

For the exceptional one-block compiler, with `b=b(m)` and full common factor `F=f([m])`,

`C_U-C_single=(1-b)W+[m(b+1)-1]F+2m-2-d(m)-b`.

The same matching/cycle sum gives `W>=2mF`. Direct recurrence cases `5<=m<=8`, then `d(m)>=m-1` for `9<=m<=16`, and finally `b>=5`, show the gain is negative for every `m>=5`.

### 3.5 Converse

If a pair clause fails, the partition containing that pair and all other terms as singletons has positive gain. If a two-disjoint-pair clause fails, the partition containing those two pairs and remaining singletons has positive gain. This proves the equivalence. ∎

## 4. The threshold is sharp at four terms

At `m=4`, take

`XXII, XYII, XZII, XIXX`.

The weights are `(2,2,2,3)`, every pair has exactly one common nonidentity column, and every one-pair and two-disjoint-pair clause holds. Yet

`C_U=27`,

while the one-block compiler has cost

`C_single=23`.

Thus the theorem begins sharply at `m=5`. This adverse instance is part of the result, not an excluded edge case.

## 5. Complete pair information does not determine value or optimizer

For each `t>=1`, build `t` disjoint five-term gadgets. In both members of the pair, every gadget has ordered weights `(4,4,4,2,2)` and the same complete labeled pair common-factor matrix. The two constructions differ only in a four-column marginal trade that changes triple structure while preserving degrees and pair codegrees.

Exact optimization gives

`Delta(A_t)=12t-2`,

`Delta(B_t)=10t-1`,

where `Delta=C_U-C_F`. Hence

`Delta(A_t)-Delta(B_t)=2t-1`.

The ambiguity is unbounded although the observer knows the term count, every ordered term weight and every labeled pair gain.

The optimizer structures also differ. Every optimum for `A_t` contains one distinguished triple block and one pair block per gadget. Every optimum for `B_t` uses pair blocks and singletons only. Complete pair information therefore does not determine even whether an optimal block of size three exists.

This separation lies inside one decision fiber: both members violate the unary-optimality certificate and both strictly improve.

## 6. All proper interaction data still does not determine exact value

Fix `m>=5` and write `q=m-1`, with one anchor term and `q` variable terms. For `L>=1`, construct two `X/I` instances whose trade columns consist of all anchor-plus-variable supports of one parity class versus the opposite parity class, each repeated `L` times, and add an identical common all-term padding that forces the one-block compiler to be the unique optimum.

For every labeled nonempty term subset of size at most `m-2`, the two instances have exactly the same common-factor count. They also have the same ordered weights and qubit count. Yet their unique one-block optima differ by

`Delta(A)-Delta(B)=[m(ceil(log2 m)+1)-1]L`.

For every fixed `m`, the exact-value ambiguity is therefore unbounded in `L`, despite complete labeled interaction data through order `m-2`.

The common padding in this construction is intentionally conservative. The theorem below closes a different question: whether the **difference trade itself** can be made smaller while preserving all proper marginals.

## 7. Möbius inversion makes the parity trade minimal

Represent one trade column by the subset of the `q` variable terms that accompany the anchor. Let

`delta:2^[q] -> Z`

be the signed difference between two multisets of trade columns. For `T subseteq [q]`, define the upper marginal

`M(T)=sum_{S supseteq T} delta(S)`.

Preserving every proper labeled marginal means

`M(T)=0`

for every proper `T subset [q]`. Let

`c=M([q])=delta([q])`.

**Theorem 2 (proper-marginal trade minimality).** If all proper upper marginals vanish, then for every `S subseteq [q]`,

`delta(S)=(-1)^(q-|S|)c`.

**Proof.** `M` is the zeta transform of `delta` on the Boolean lattice. Möbius inversion gives

`delta(S)=sum_{T supseteq S} (-1)^(|T|-|S|) M(T)`.

All terms vanish except `T=[q]`, so

`delta(S)=(-1)^(q-|S|)c`. ∎

### 7.1 Consequences

If `c!=0`, every one of the `2^q` cells has nonzero difference. Exactly half have the sign of `c` and half the opposite sign. Therefore the positive and negative masses are both

`2^(q-1)|c|`.

For an integer primitive trade, `|c|>=1`. Hence any nonzero trade preserving all proper labeled marginals must have at least

`2^(q-1)=2^(m-2)`

columns on each signed side and must touch all

`2^q=2^(m-1)`

Boolean cells. The registered parity construction uses `c=L`; at `L=1` it attains the primitive lower bound exactly.

Thus its exponential difference support is unavoidable. This statement does **not** prove that the identical common padding used to force one-block optimality is minimal.

### 7.2 Machine corroboration

The publication verifier performs downward Möbius reconstruction for `q=1,...,8`, checks every proper marginal, verifies the parity formula and confirms positive and negative mass `2^(q-1)`. The all-`q` authority is Theorem 2.

## 8. Relation to prior work

Marginal-preserving integer moves are central objects in algebraic statistics. Markov bases connect points in contingency-table fibers under fixed sufficient statistics, and hierarchical/log-linear models provide a mature language for lower- and higher-order interactions. Boolean-lattice Möbius inversion is likewise standard, as is the interpretation of highest-order parity interactions.

Accordingly, Paper C does not claim invention of marginal fibers, Markov moves, Möbius inversion, or the generic fact that lower-order marginals need not determine higher-order structure. The compiler-specific contribution is the conjunction of four facts:

1. global unary optimality has a uniform four-index certificate for every `m>=5`;
2. complete pair information is nevertheless insufficient for value and optimizer structure by an unbounded amount;
3. all labeled interactions through order `m-2` remain insufficient for exact value;
4. the exact compiler witness for the last separation is a primitive Boolean-lattice trade, making its exponential difference support sharp.

The final bibliography must replace discovery-level Markov-basis records with verified primary references before submission.

## 9. Reproducibility

The C1, C2 and C3 theorems are bound to separately frozen source, generic and native campaign records with deterministic replays. The new Möbius theorem is independently corroborated by `papers/verify_five_theory_upgrades.py`. No finite enumeration is used as the logical premise of the all-`m` or all-`q` proofs.

The publication package should archive the exact submission commit and include the complete finite witness instances for the `m=4`, pair-information and arbitrary-order separations.

## 10. Limitations

1. The compiler objective is the frozen structural `SELECT+PREP+WIDTH` grammar, not a physical end-to-end quantum resource metric.
2. The all-`m` theorem is a decision theorem; it does not reconstruct an optimizer.
3. The pair-information result proves additive, not multiplicative, value ambiguity.
4. The arbitrary-order construction uses common padding to force a unique one-block optimum; padding minimality remains open.
5. The Möbius theorem makes the **trade difference** minimal, not the complete padded instance.
6. Generic algebraic-statistics mathematics is donor-owned; novelty rests on the compiler realization and hierarchy.
7. Cross-objective and cross-grammar transfer are open.

## 11. Discussion

The results separate three notions of information sufficiency. The first is **decision sufficiency**: a constant-order certificate can decide whether a simple incumbent is globally optimal even though the candidate space contains every set partition. The second is **value sufficiency**: knowing enough to decide the sign of improvement does not determine its magnitude. The third is **witness sufficiency**: even complete pair data does not determine whether an optimal triple block exists.

The arbitrary-order result is stronger still. Increasing the observed interaction order all the way to `m-2` does not close exact value. The missing coordinate is genuinely top-order: Boolean-lattice inversion shows that the only signed direction invisible to every proper marginal is parity. There is no sparse alternative trade hiding in the same information fiber.

This gives a precise caution for compiler characterization and, more broadly, learned surrogates for combinatorial optimization. A compact feature set can be complete for one downstream query and provably incomplete for another. “The features determine whether optimization is needed” and “the features determine the result of optimization” are logically different claims.

## 12. Conclusion

A global Pauli partition optimizer admits an exact four-index unary-optimality certificate for every `m>=5`, but that simplicity stops at the decision boundary. Complete pair information leaves unbounded value ambiguity and different optimizer structures; all labeled interactions through order `m-2` still leave unbounded exact-value ambiguity. Möbius inversion then proves that the final separation cannot be represented by a smaller proper-marginal-preserving trade. Low-order information is therefore exactly sufficient for one important optimization decision and exactly insufficient for richer properties of the same optimizer.

## Selected references

Primary Markov-basis and hierarchical-model references are being field-verified before final bibliography freeze. Required donor families include Diaconis–Sturmfels algebraic statistics, Dobra-style graphical-model Markov bases, binary hierarchical-model circuits/Graver bases, and Boolean-lattice Möbius interaction decompositions.

---

## Publication decision record

**Primary target posture:** a strong combinatorial-optimization/quantum-algorithms venue selected after final primary-source novelty closure. `Quantum` is defensible if the compiler interpretation remains central; a combinatorics/optimization journal is preferable if the decision/value hierarchy is judged the dominant contribution.  
**Stretch posture:** a top specialist journal only after primary Markov-basis review confirms that the compiler theorem package is not a direct specialization of a known hierarchical-model result.  
**Internal status:** `STRONG_SPECIALIST_CANDIDATE__PRIMARY_SOURCE_ALGEBRAIC_STATISTICS_REVIEW_BLOCKING_TOP_TIER_LABEL`.  
**Remaining blockers:** primary-source donor cards; independent proof audit; target resolution; main figure/evidence design; final citation verification and archive.
