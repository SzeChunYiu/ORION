# Certified Sparse Normal Forms: Zero-Sum Deletion, Production Realization, and Proof-Language Waste

**Integrated R9 research manuscript — 2026-08-26**

**Scope.** This manuscript consolidates the former Papers A and B. It is distinct from the ORION-Q1 support-two theorem: Q1 studies one frozen shared-Tag TARE compiler and proves its intrinsic uniform support number. The present paper studies the abstraction boundary itself—what a finite-signature deletion argument certifies, when that certificate is exact for a proof language, when it transfers to a production grammar, and how omitted interacting moves can destroy an apparent product lower bound.

## Abstract

Finite-support normal forms can turn an unbounded exact optimization into a finite search, but the number supplied by a proof is not automatically an intrinsic property of the production system. We develop a layered theory separating four objects: a finite signature invariant, a semantics-preserving normalization, a named proof language, and the complete production move system.

For a finite abelian group `H` and allowed alphabet `A`, let `zsf(H;A)` denote the maximum length of a zero-sum-free word over `A`. We prove that a finite optimization grammar has an optimum of support at most `zsf(H;A)` whenever every zero-signature deletion remains admissible, preserves the declared semantics, and is persistently non-increasing. The same invariant is the exact terminal complexity of the abstract language whose only shortening move removes a nonempty proper zero-sum subsequence from a nonzero-total word. These two facts do not identify a production lower bound. We give a realization theorem requiring a support-preserving representation map, sound lifting of the moves used for normalization, a production preimage of a maximum terminal word, and irreducibility under every move admitted by the named production proof system.

The theory is compositional only under an explicit interaction audit. Independent shortening systems have additive terminal complexity, but a single cross-component move can collapse a product witness. We therefore formulate a safe product criterion in which every production move either belongs to one component or is proved unable to reduce the product terminal state. For standard cyclic-axis alphabets the abstract budget is exactly the sum of the factor orders minus one. Quotient and kernel data give a two-sided computable bracket, while controlled deletion defects yield approximate normal forms outside the exact objective cone.

Two finite Pauli grammars illustrate different layers. An arbitrary-block multi-Tag grammar satisfies an alphabet-sensitive support ceiling in an explicit sufficient cone. A dependent-triple grammar admits a whole-system Tag reconstruction that reaches support one even though a five-bit abstract deletion language has terminal complexity five. The numerical difference exposes proof-language waste but is not promoted to a production certificate gap without a complete move registry and realizing terminal state. For direct support enumerators, a verified budget reduction from `B` to `K` changes the leading search volume from `(q^B/B!)n^B` to `(q^K/K!)n^K`; this is an architecture-specific statement, not an algorithm-independent lower bound.

The resulting framework supports proof-carrying exact optimization, certificate-aware branch and bound, abstraction audits for formal and AI systems, and modular search caps. Its principal reporting rule is strict: a support number belongs to the production system only after realization and complete-move irreducibility; otherwise it belongs to a named normalization or proof language.

## 1. Introduction

Exact optimizers often replace an unbounded representation by a bounded normal form. In compiler optimization, formal verification, modular repair, and finite-state synthesis, the proof usually attaches a finite signature to each active coordinate. Once support exceeds a signature threshold, a zero-signature subset can be removed. The resulting number may be called a compiler support, a sparsity theorem, or a search bound.

Three logically different conclusions are often conflated:

1. a transformation can reach support at most `B` without worsening the objective;
2. a restricted proof language cannot reduce every state below `B`;
3. the complete production system intrinsically requires support `B` on some instance.

Only the third is an intrinsic production statement. The first is an upper theorem owned by a transformation. The second is an exact lower theorem internal to a proof language. A production system may contain a global reconstruction, shared-auxiliary edit, or cross-component cancellation that the abstract language cannot express.

This paper gives a checkable boundary between these layers. The central objects are:

- a finite-group signature and its alphabet-restricted zero-sum threshold;
- persistent semantic and objective hypotheses that license deletion;
- an abstract shortening language and its terminal states;
- a production representation map and move registry;
- a critical-interaction audit for allegedly independent products; and
- an explicit search architecture to which a support budget is applied.

The contribution is not the generic existence of Davenport constants, sparse optima, term-rewriting modularity, or proof-system lower bounds. Those are established subjects. The residual contribution is their exact conjunction in finite-signature optimization: a normal-form theorem, an exact proof-language theorem, a production-realization gate, a cross-move audit, and calibrated compiler examples.

### 1.1 Contributions

1. **Alphabet-sensitive deletion normal form.** A persistent sound and non-increasing zero-sum edit yields support at most `zsf(H;A)`.
2. **Exact abstract terminal complexity.** The same invariant is exact for the declared zero-sum deletion language.
3. **Computable structure.** Axis additivity, an exact cyclic-axis formula, a finite multiplicity formulation, and quotient–kernel brackets support exact cap computation.
4. **Robustness outside the cone.** Event- and coordinate-defect theorems quantify the objective loss of forced normalization.
5. **Production-realization gate.** Exact certificate transfer requires a realizing production state and irreducibility under the complete named move set.
6. **Interaction-safe composition.** Product exactness is valid only after a cross-move audit; a constructive collapse example shows the premise is necessary.
7. **Search consequence.** The verified support difference determines the exact leading exponent and constant for a declared direct enumerator.
8. **Pauli case studies.** Two explicit grammars separate a deletion ceiling from a stronger global reconstruction without claiming equivalence to a full production TARE implementation.

## 2. Four support quantities

Let `F` be a finite nonempty production family with objective `C` and support functional `k`.

### 2.1 Intrinsic production support

`kappa(F,C)` is the least `K` such that every instance has an exact optimum of support at most `K`, together with a production instance on which every optimum has support at least `K`.

### 2.2 Normalization ceiling

A transformation `N` establishes a ceiling `B_N` when every feasible state has a no-more-expensive `N`-normal representative of support at most `B_N`. Without a matching production lower witness, the number belongs to `(F,C,N)`.

### 2.3 Proof-language certificate complexity

A sound proof language `P` fixes visible information and legal moves. Its terminal complexity `beta_P` is the maximum support of a state terminal under `P`, on the declared production scope. Exactness requires both an upper normalization in `P` and a terminal state of matching size.

### 2.4 Abstract terminal complexity

An abstract shortening system may not have a faithful production preimage. Its terminal number is therefore denoted `beta_abs` until the realization gate is passed.

Sound production certification gives

`kappa(F,C) <= beta_P(F,C)`,

but there is no general equality. A comparison between `beta_abs` and `kappa` is a comparison of separately owned quantities unless production realization is proved.

## 3. Alphabet-restricted zero-sum invariant

Let `H` be a finite abelian group and `A` a finite subset. Words allow repetition. Define

`zsf(H;A) = max{|W| : W is zero-sum-free over A}`,

where a word is zero-sum-free when no nonempty subsequence sums to zero. For the unrestricted nonzero alphabet this equals the classical Davenport constant minus one; smaller alphabets can have smaller thresholds.

### Theorem 1 — deletion normal form

Consider a finite optimization grammar. Each active coordinate of a constrained generator `R` carries a letter in `A_R subset H_R`. Assume, initially and after every admitted deletion:

1. the total signature of every feasible constrained generator is nonzero;
2. deleting any nonempty zero-signature subsequence remains in the grammar and preserves every declared semantic constraint; and
3. the deletion does not increase the objective.

Then every instance has an exact optimum satisfying

`support(R) <= zsf(H_R;A_R)`

for every constrained generator.

**Proof.** Start from an optimum. A signature word longer than `zsf` contains a nonempty zero-sum subsequence. Its nonzero total prevents that subsequence from being the whole word. Delete it. Feasibility and semantics persist, cost does not increase, and support strictly decreases. Repeat while any generator violates its current bound. Total support is a strictly descending nonnegative integer, so the process terminates with all bounds satisfied simultaneously. ∎

The theorem deliberately localizes the production burden. The group invariant does not prove that a deletion is legal, semantics-preserving, or profitable.

### Theorem 2 — exact abstract deletion complexity

Let the abstract states be nonzero-total words over `A`; the only shortening move deletes a nonempty proper zero-sum subsequence. The maximum terminal length is exactly `zsf(H;A)`.

**Proof.** Every longer word contains a zero-sum subsequence, which is proper because the total is nonzero. Conversely, a longest zero-sum-free word has nonzero total and no legal deletion. ∎

Theorem 1 is an optimization upper theorem under semantic and objective premises. Theorem 2 is an exact combinatorial statement about a named shortening language. Neither alone proves an intrinsic production lower bound.

## 4. Computing and composing the invariant

### Theorem 3 — axis direct-sum additivity

For finite groups `H_i`, alphabets `A_i`, and the axis-separated alphabet in `direct_sum_i H_i`,

`zsf(direct_sum_i H_i; union_i A_i) = sum_i zsf(H_i;A_i)`.

Projection gives the upper bound; concatenating maximum zero-sum-free component words gives the lower bound.

### Corollary 4 — standard cyclic axes

For `H = direct_sum_{i=1}^r C_{n_i}` and the standard-generator alphabet `{e_1,...,e_r}`,

`zsf(H;A) = sum_i (n_i-1)`.

A zero-sum-free word contains at most `n_i-1` copies of `e_i`, and taking all those copies is zero-sum-free.

### Proposition 5 — finite multiplicity formulation

Write `A={a_1,...,a_m}` and let `o_i` be the order of `a_i`. Then `zsf(H;A)` is the optimum of

`maximize sum_i u_i`

subject to integer `0 <= u_i <= o_i-1` and

`sum_i v_i a_i != 0`

for every nonzero integer vector satisfying `0 <= v_i <= u_i`.

The formulation is exact and finite, not asserted polynomial-time.

### Theorem 6 — quotient–kernel bracket

Let `phi:H -> K`, `N=ker(phi)`, `B=phi(A)`, and let `atom(K;B)` be the maximum length of a minimal nonempty zero-sum word over `B`. Then

`zsf(K;B) <= zsf(H;A)`

and

`zsf(H;A) <= zsf(K;B) + (D(N)-1) atom(K;B)`.

The lower inequality lifts an image zero-sum-free word. For the upper inequality, repeatedly remove minimal image-zero-sum blocks. The image remainder has length at most `zsf(K;B)`. The lifted sums of removed blocks form a zero-sum-free word in the kernel and therefore number at most `D(N)-1`; each block has length at most `atom(K;B)`.

This is useful both as a fail-fast obstruction and as a computable support interval.

## 5. Controlled defects outside exact deletion dominance

Let an optimum have initial support `n` and threshold `z`.

### Theorem 7 — event-defect normalization

If each admitted zero-sum deletion increases cost by at most `epsilon`, then a feasible support-`z` state has cost at most

`OPT + epsilon max(0,n-z)`.

### Theorem 8 — coordinate-defect normalization

If deleting a zero-sum subsequence `T` increases cost by at most `delta |T|`, then a feasible support-`z` state has cost at most

`OPT + delta n`.

Both follow by the same terminating descent and telescoping. These theorems quantify a declared structural objective; they do not imply physical fidelity, gate count, depth, or runtime guarantees.

## 6. Production realization

Let `P` be an abstract shortening system with terminal complexity `beta(P)`. Let `psi` map production states into abstract states.

### Definition 9 — faithful production representation

A named production proof system is faithfully represented by `P` when:

1. support in production equals abstract size on the represented scope;
2. every production move maps to a legal abstract move or an abstract stutter that cannot invalidate terminality claims;
3. every abstract move used in the upper theorem has a sound admissible production lift from the relevant state; and
4. the semantic and objective relations claimed by the proof are preserved in both directions used.

### Theorem 10 — exact production certificate criterion

Suppose:

1. every production state has a represented `P`-normal form of size at most `beta(P)`;
2. a production state realizes a terminal abstract state `w` of size `beta(P)`;
3. every move admitted by the named production proof system is covered by the representation audit; and
4. no admitted production move reduces the realizing state.

Then the production certificate complexity of that proof system equals `beta(P)`.

The lower witness is not the abstract word alone. It is the production preimage together with a complete-move irreducibility proof.

### Failure modes

The criterion rejects four recurrent mistakes:

- the terminal abstract word has no feasible production preimage;
- an abstract deletion used for the upper theorem has no sound production lift;
- a stronger global production move reduces the alleged witness; or
- abstract length is not the production support functional being reported.

## 7. Interaction-safe products

For independent abstract shortening systems `P_i`, terminality is componentwise, so

`beta(product_i P_i)=sum_i beta(P_i)`.

Production composition is stricter. Shared auxiliaries, global reconstruction, or cross-component cancellation can reduce a tuple of component terminal states.

### Proposition 11 — cross-component collapse

There exist two component systems of terminal complexity one whose independent product has terminal complexity two, while adding one legal cross move sends the size-two tuple to the empty tuple and reduces terminal complexity to one.

Thus product additivity is a semantic theorem about the move registry, not a consequence of disjoint coordinate labels.

### Theorem 12 — safe realized product

Let each component pass Theorem 10 with terminal witness `x_i`. The production product has certificate complexity `sum_i beta_i` when every admitted production move either:

1. acts wholly within one component; or
2. is proved unable to reduce the product witness `(x_1,...,x_t)`.

A practical audit constructs a move-interaction graph. Vertices are move schemas; an edge records overlapping support, shared auxiliary state, shared objective term, or a precondition/effect dependency. Every connected cross-component region must be analyzed jointly. Absence of an edge is a proved noninteraction statement, not a naming convention.

## 8. Two Pauli grammar case studies

### 8.1 Multi-Tag deletion cone

In an explicit `b`-block grammar with `s` shared Tags, a frame coordinate carries its partner-anticommutation bit and `s` Tag-syndrome bits. Changing one argument of the local `b`-way Restore functional can increase it by at most `b-1`, sharply. If the minimum frame refund is `mu` and the Restore coefficient is `t_R`, then throughout

`mu >= (b-1)t_R`

every instance has an optimum satisfying

`support(R) <= zsf(H_R;A_R) = rank(H_R) <= s+1`.

The equality uses the elementary binary group generated by the realized alphabet. The result is for the displayed grammar and objective; it is not claimed for every TARE implementation.

Outside the cone, Theorem 8 applies with coordinate defect

`delta=max(0,(b-1)t_R-mu)`.

### 8.2 Dependent-triple reconstruction

A separate two-block grammar has two independent anticommuting frames per block, a dependent third frame, and two shared Tags. The abstract standard-basis deletion language in `F_2^5` has exact terminal complexity five. A whole-system production transformation chooses one anticommuting core per block, deletes all non-core frame letters, recomputes the dependent frame, and relocates the shared Tags canonically. Exact local inequalities show that the transformation never increases the declared objective and reaches support one. Support zero is infeasible, so the intrinsic support of this grammar is one.

This establishes a strict separation between an abstract five-bit deletion budget and a separately defined intrinsic production budget. It does **not** establish a production certificate gap of five versus one until a production state realizes the five-letter terminal word and the complete move registry is audited. The example identifies the missing operation—whole-system auxiliary reconstruction—that the rank-only language holds fixed.

## 9. Certificate waste and direct enumeration

Suppose a production proof language has exact budget `beta` and intrinsic production support is exactly `kappa`. Define certificate waste `w=beta-kappa`.

A direct enumerator on `n` coordinates with `q` local nonidentity labels visits

`V_B(n;q)=sum_{j=0}^B binom(n,j)q^j`.

For fixed `B` and `q`,

`V_B(n;q)=(q^B/B!)n^B+O(n^{B-1})`.

Therefore

`V_beta(n;q)/V_kappa(n;q) = q^w kappa!/beta! n^w (1+o(1))`.

For independent heterogeneous components, the ratios multiply after the safe-product premises have been established componentwise. The formula evaluates one declared architecture. It is not an algorithm-independent time lower bound and does not constrain dynamic programming, implicit search, symmetry quotienting, or other non-enumerative methods.

## 10. Applications

### 10.1 Proof-carrying exact optimization

An optimizer can publish a machine-readable certificate tuple:

`(production grammar, representation map, legal move registry, normalization proof, terminal witness, complete-move irreducibility audit)`.

The tuple prevents an abstract cap from being silently promoted to a production lower bound.

### 10.2 Certificate-aware branch and bound

A stronger sound proof language is valuable when it removes verified terminal states. Once exact old and new budgets are established, Section 9 prices the exponent removed from a direct support enumerator.

### 10.3 AI planning and formal agents

An AI system that proposes transformations can separate three claims: the edit is semantically sound, it is cost-nonincreasing, and the proof language is complete enough to own the resulting lower bound. The interaction graph also exposes when two apparently modular agent skills share hidden state or jointly create a stronger move.

### 10.4 Modular repair and synthesis

Finite-group signatures apply beyond Pauli grammars when a domain supplies a sound zero-signature edit. Quotients provide cheap obstruction tests; axis decomposition supports modular cap computation; defect theorems permit certified approximate repair.

These are theorem-to-system routes, not evidence of deployed speedup or hardware advantage.

## 11. Reproducibility and top-tier gate

The repository package must contain:

1. a frozen production grammar and objective;
2. an exhaustive move registry;
3. a representation/lifting checker;
4. a production preimage of every terminal witness used for a lower claim;
5. a critical-interaction graph and cross-move audit;
6. two structurally independent terminality/intrinsic-witness replays;
7. exact search-scaling measurements; and
8. a primary-source nearest-work matrix.

The current integrated theory is mathematically meaningful without a production separation. A broad compiler or algorithms submission, however, requires the receipt-bound programme registered in the companion harness issue. If realization fails, the correct paper is a pure abstraction-boundary theorem with calibrated Pauli examples. A failed realization narrows ownership; it does not invalidate Theorems 1–12.

## 12. Limitations

- `zsf(H;A)` may be computationally difficult.
- Deletion soundness and objective dominance are production-specific premises.
- The approximate theorems control only the declared objective.
- Product additivity fails under reducing cross moves.
- A proof-language terminal word need not be production-realizable.
- Structural support is not T count, circuit depth, qubit count, fidelity, runtime, or quantum advantage.
- The Pauli grammars are explicit mathematical models, not proved equivalents of every cited compiler.

## 13. Conclusion

A sparse certificate has an owner. The alphabet-restricted zero-sum invariant owns an exact abstract deletion threshold. A semantics-preserving, non-increasing edit turns that threshold into a normalization ceiling. A realizing production state and a complete-move irreducibility audit turn it into an exact production certificate. Only an independent production obstruction turns the smallest universal optimum into intrinsic support.

This layered view makes support claims compositional where interaction is genuinely absent, exposes proof-language waste where stronger moves exist, and gives exact search consequences only for the architectures that use the certified cap. It replaces a single ambiguous number by a chain of checkable obligations.

## Tool-use disclosure

A generative language model assisted organization, language revision, theorem cross-check planning, and preparation of executable research tasks. The author is responsible for every statement, proof, citation, code artifact, and final submission.

## References

1. I. Aliev, J. A. De Loera, F. Eisenbrand, T. Oertel, and R. Weismantel, “The Support of Integer Optimal Solutions,” *SIAM Journal on Optimization* 28, 2152–2157 (2018).
2. M. Freeze and W. A. Schmid, “Remarks on a Generalization of the Davenport Constant,” *Discrete Mathematics* 310, 3373–3389 (2010).
3. G. Wang, “The Universal Zero-Sum Invariant and Weighted Zero-Sum for Infinite Abelian Groups,” *Communications in Algebra* 53, 1581–1599 (2025).
4. A. Geroldinger and F. Halter-Koch, *Non-Unique Factorizations: Algebraic, Combinatorial and Analytic Theory*, Chapman & Hall/CRC (2006).
5. G. Li, A. Wu, Y. Shi, A. Javadi-Abhari, Y. Ding, and Y. Xie, “Paulihedral: A Generalized Block-Wise Compiler Optimization Framework for Quantum Simulation Kernels,” ASPLOS (2022).
6. N. Schillo, A. Sturm, and R. Quay, “TARE: Block Encoding Linear Combinations of Pauli Strings Without Ancilla State Preparation,” arXiv:2601.05740 (2026).
7. The final submission bibliography will incorporate the receipt-bound current primary-source audit for rewriting modularity, proof-language simulation, restricted zero-sum sequences, and production Pauli compilation.
