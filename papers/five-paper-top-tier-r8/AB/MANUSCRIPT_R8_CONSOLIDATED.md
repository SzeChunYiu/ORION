# Certified Normal Forms and Proof-Language Budgets for Exact Modular Optimization

**R8 consolidated research draft — 2026-08-26**

## Abstract

Support ceilings used by exact optimizers answer three different questions. A ceiling may be intrinsic to the production problem, reachable by a named normalization, or merely terminal inside a restricted proof language. Conflating these objects can produce valid but unnecessarily large searches and can turn an abstract obstruction into an unsupported production lower bound.

We develop a certificate calculus that keeps the three layers separate. Let `H` be a finite abelian signature group and `A subseteq H` the alphabet realized by admissible coordinates. Write `zsf(H;A)` for the maximum length of a zero-sum-free word over `A`. In any finite optimization grammar where nonempty zero-signature coordinate sets can be deleted with persistent semantic soundness and non-increasing cost, every instance has an exact optimum of support at most `zsf(H;A)`. The same invariant is exactly the maximum terminal length of the abstract proof language whose only shortening rule is proper zero-sum deletion. A production lower bound follows only after a terminal word is realized by a production state and every additional production rule is shown unable to shorten it.

The invariant composes exactly over axis-separated alphabets and over connected components of the complete semantic interaction hypergraph of a shortening system. For standard cyclic axes its value is the sum of the factor orders minus one. Quotient analysis gives both lower obstructions and upper bounds; a kernel-weighted refinement charges only source-realizable nonzero kernel sums and can be exact when a uniform quotient–kernel estimate is loose. Controlled violations of deletion dominance yield auditable additive-defect normal forms.

We give two complete separation models. In a Pauli grammar, whole-system auxiliary reconstruction reaches intrinsic support one although the corresponding rank-only language has a larger abstract terminal budget. In a non-Pauli XOR-aggregation production grammar, the basis word is a realized weak terminal of length `d`, while a sound production fusion rule reduces every nonzero-total state to one fragment. Thus the exact weak and strong budgets are `d` and `1`. For a declared direct support enumerator, the resulting certificate waste changes the polynomial degree of the visited support family; this is architecture-specific accounting, not an unrestricted time lower bound.

The resulting proof-carrying record binds every support claim to its representation, legal transformations, terminal witness, production realization, interaction scope, objective argument, and prohibited inferences. The framework applies to modular exact optimization, syndrome-preserving repair, parity aggregation, and compiler normal forms, but it grants no physical-resource, hardware, or generic runtime conclusion without a domain-specific realization.

**Keywords:** exact optimization; normal forms; zero-sum sequences; rewrite systems; proof complexity; certificate complexity; parity aggregation; compiler optimization

---

## 1. Introduction

Exact combinatorial optimizers often become finite only after a structural theorem proves that an optimum can be chosen with bounded support. Such a theorem may transform a search over arbitrary coordinate sets into an enumeration of supports of size at most `B`. The numerical ceiling `B` is operationally important, but its meaning is frequently ambiguous.

Three interpretations must be distinguished.

1. **Intrinsic support.** Every instance has an optimum of support at most `B`, and some instance requires support `B` in every optimum.
2. **Normalization ceiling.** A named sound transformation reaches support at most `B`, but a different transformation may do better.
3. **Proof-language budget.** A restricted inference system can certify termination by support `B`, even though the production optimizer admits moves invisible to that system.

These interpretations can coincide. They need not. A proof language may be exact for its own terminal states and still overestimate the support needed by production. Conversely, a production upper normal form is not intrinsic until a matching lower witness rules out all smaller optima.

This paper develops a unified theory of these distinctions. The mathematical core begins with an alphabet-restricted zero-sum invariant. Coordinates carry signatures in a finite abelian group. A zero-signature set is a candidate deletion because its aggregate semantic syndrome is unchanged. The finite-group argument guarantees only the existence of such a set. A compiler or optimizer theorem additionally needs a proof that deleting it is admissible, semantics-preserving, and non-increasing in the declared objective after every earlier deletion.

The second layer studies the proof language itself. Proper zero-sum deletion has an exact terminal complexity equal to the longest zero-sum-free word over the realized alphabet. This statement belongs to the abstract language. It transfers to production only through a realization and irreducibility audit.

The third layer addresses composition. Nominal modules are insufficient: a move that reads a guard in one component and writes another is semantically cross-component even when its output is local. The correct decomposition is the connected-component structure of a hypergraph containing every coordinate read, tested, written, or guarded by every legal move.

The fourth layer makes the invariant computationally usable. Exact formulas hold for independent cyclic axes. Quotients provide lower obstructions and upper caps. A kernel-weighted quotient bound retains the actual source sum of each minimal image-zero block and avoids charging for image atoms whose lifts would already be illegal in a source terminal.

Finally, we give a complete non-Pauli production separation. The example is intentionally elementary enough to audit line by line: a parity-fragment aggregator over `F_2^d`. It supplies the production witness and full move inventory that the Pauli comparison leaves open. Its role is not to claim a new XOR compiler, but to show that the realization gate is substantive and exactly checkable.

### 1.1 Contributions

1. **Alphabet-restricted deletion theorem.** Persistent sound, non-increasing zero-signature deletion yields an exact optimum with support at most `zsf(H;A)`.
2. **Exact proof-language theorem.** Proper zero-sum deletion has maximum terminal length exactly `zsf(H;A)`.
3. **Realization gate.** A matching production lower bound requires a realized maximum terminal word and irreducibility under the complete named production move set.
4. **Composition.** Axis-separated alphabets and semantic interaction blocks have exact additive budgets.
5. **Exact and quotient computation.** Standard cyclic axes have an explicit formula; quotient lower and kernel-weighted upper bounds localize the remaining problem.
6. **Robustness.** Event- and coordinate-level objective defects give approximate normal forms outside an exact dominance cone.
7. **Realized separation.** A complete XOR-aggregation grammar has weak terminal budget `d` and strong production budget `1`.
8. **Search accounting.** For a named direct enumerator, certificate waste determines the lost polynomial degree and leading constant.
9. **Proof-carrying record.** A machine-readable contract states what owns a support number and which conclusions are forbidden.

### 1.2 Claim boundary

The generic languages of Davenport constants, restricted zero-sum problems, sparse optimization, rewrite systems, graph decomposition, and exact-search asymptotics are established. The paper-specific contribution is their conjunction in a calibrated certificate pipeline: realized alphabets, persistent edit semantics, production realization, semantic interaction blocks, weighted quotient accounting, and explicit separation records.

No theorem below implies a quantum advantage, gate-count reduction, hardware improvement, architecture-independent runtime lower bound, or production relevance for an optimizer whose move and objective semantics have not been audited.

---

## 2. Optimization grammars and three support quantities

An **optimization grammar** is a tuple

`G=(X, F, C, supp)`,

where `X` is a finite state space, `F subseteq X` is a nonempty feasible set, `C:F -> R` is an objective, and `supp:F -> N` is the support quantity of interest. Finiteness ensures that `C` attains a minimum.

A **sound production move** is a partial map `m:F -> F` that preserves the semantic target represented by the state. A **shortening proof language** `P` is a declared subset of sound moves such that every move strictly decreases an integer size. The language is terminating.

### 2.1 Intrinsic support

The intrinsic support of the family is the least `k` such that every instance has an exact optimum of support at most `k`, together with an instance on which every optimum has support at least `k`. We write this value as `kappa` only when both upper and lower directions are established.

### 2.2 Normalization ceiling

A normalization `N` proves that every feasible state has a no-more-expensive representative of support at most `B_N`. Without a lower witness, `B_N` belongs to the pair `(grammar, normalization)` rather than intrinsically to the grammar.

### 2.3 Certificate complexity

For a terminating proof language `P`, define

`beta(P)=max{|x|: x is terminal under P}`

when the maximum is finite and attained. If `P` is implemented on production states, its exact production certificate budget is the maximum production support of a state terminal under every move in `P`.

Soundness gives `kappa <= beta(P)` whenever the quantities are defined on the same production scope. Equality is an additional theorem.

### 2.4 Reporting rule

Every support statement should name its owner:

| Quantity | Owner | Required lower witness |
|---|---|---|
| intrinsic support `kappa` | production family and objective | production instance whose optima require `kappa` |
| normalization ceiling `B_N` | production family, objective, and transformation | only for intrinsic interpretation |
| certificate complexity `beta(P)` | production scope and proof language | production state terminal under the complete named rule set |
| abstract terminal complexity | abstract state universe and rules | abstract terminal state only |

---

## 3. Alphabet-restricted zero-sum budgets

Let `H` be a finite abelian group written additively and `A subseteq H` a finite alphabet. A word over `A` may repeat letters. A nonempty subsequence is selected by positions and need not be contiguous.

A word is **zero-sum-free** when no nonempty subsequence has sum zero. Define

`zsf(H;A)=max{|W|: W is zero-sum-free over A}`.

For `A=H\{0}`, this is `D(H)-1`, where `D(H)` is the ordinary Davenport constant. Smaller realized alphabets may have smaller budgets.

### 3.1 Deletion theorem

For a constrained generator `R` in an optimization grammar, suppose every active coordinate `q` carries a signature `v_q in A_R subseteq H_R`. Assume the following hold initially and after every admitted deletion.

1. **Nonzero total:** `sum_q v_q != 0` for every feasible constrained generator.
2. **Deletion closure and soundness:** zero-signature coordinate sets may be replaced by identity while remaining feasible and preserving every semantic constraint represented by the signature.
3. **Persistent dominance:** the deletion does not increase the objective.

**Theorem 1 (alphabet-restricted normal form).** Every finite admitted instance has an exact optimum satisfying

`support(R) <= zsf(H_R;A_R)`

for every constrained generator.

**Proof.** Start from an optimum. If the current signature word of a generator is longer than `zsf(H_R;A_R)`, it contains a nonempty zero-sum subsequence. The nonzero total prevents that subsequence from being the whole word. Delete its coordinates. Closure and soundness preserve feasibility, dominance preserves optimality, and support strictly decreases. Recompute the current signature alphabet and repeat while any generator violates its current bound. Total support is a nonnegative integer and strictly decreases at each step, so the process terminates with all bounds satisfied simultaneously. ∎

The finite-group statement supplies the combinatorial certificate only. It does not prove any of the three production hypotheses.

### 3.2 Binary specialization

For `H=F_2^d`, every word longer than `d` is linearly dependent and therefore contains a nonempty zero-XOR subsequence. Hence `zsf(F_2^d;A)<=d`. If `A` spans `H`, it contains a basis, and the basis word is zero-sum-free. Therefore

`zsf(H;A)=rank(H)`

for an elementary binary group generated by its realized alphabet.

This equality makes the rank bound exact for the deletion language. It does not make rank an intrinsic production lower bound.

---

## 4. Exact terminal complexity of zero-sum deletion

Consider the abstract language whose states are nonzero-total words over `A` and whose only move deletes a nonempty proper zero-sum subsequence.

**Theorem 2 (exact deletion-language complexity).** The maximum terminal length is exactly `zsf(H;A)`.

**Proof.** Any word longer than `zsf(H;A)` contains a nonempty zero-sum subsequence. Because the total is nonzero, the subsequence is proper, so the word is reducible. Conversely, a longest zero-sum-free word has nonzero total and admits no legal deletion. ∎

The theorem has a matching upper and lower witness, but both live in the abstract word universe.

### 4.1 Production realization gate

Let `psi` map production states into abstract states and let support agree with abstract word length.

**Theorem 3 (exact production certificate criterion).** Suppose:

1. every production state has a represented `P`-normal form of size at most `beta(P)`;
2. a production state realizes a terminal abstract state `w` of size `beta(P)`;
3. every move in the named production proof language maps to a legal abstract move; and
4. no additional move in that proof language reduces the realizing production state.

Then the production certificate complexity of that proof language equals `beta(P)`.

**Proof.** The represented normal-form theorem gives the upper bound. The realizing state has support `beta(P)` and is terminal under every named production move, giving the lower bound. ∎

The criterion catches four common failures: no production preimage, an abstract move that does not lift, a production move invisible to the abstraction, or a mismatch between word length and the claimed production support.

---

## 5. Exact composition and semantic interaction blocks

### 5.1 Axis-separated alphabets

Let `H=H_1 direct_sum H_2` and

`A=(A_1 x {0}) union ({0} x A_2)`.

**Theorem 4 (axis direct-sum additivity).**

`zsf(H;A)=zsf(H_1;A_1)+zsf(H_2;A_2)`.

**Proof.** Concatenating maximum zero-sum-free words on the two axes gives the lower bound: a zero sum would project to a nonempty zero sum on at least one axis. For the upper bound, the subword on each axis is itself zero-sum-free, so its length is bounded by the corresponding component invariant. ∎

The statement extends by induction to finite axis-separated sums.

### 5.2 General shortening systems

Let the state space be `X_1 x ... x X_t` with additive size. The **semantic support** of a move is the set of all coordinates it reads, tests, guards, or writes. Form a hypergraph on `{1,...,t}` with one hyperedge for each move support. Let `J_1,...,J_m` be its connected components.

**Theorem 5 (interaction-block additivity).**

`beta(P)=sum_j beta(P[J_j])`.

**Proof.** Every move has its full applicability and effect inside one connected component. A global state is terminal exactly when every block restriction is terminal. Sizes add, so independently chosen maximum terminal restrictions attain the sum and no terminal state can exceed it. ∎

Cross-component moves do not invalidate the theorem. They merge the components they connect and force their joint budget to be recomputed.

**Corollary 6 (proof-language monotonicity).** Adding sound shortening moves cannot increase terminal complexity.

A production amplification claim must therefore bind a complete move inventory and semantic support for every move. Module names, disjoint qubits, or separate source files are not proofs of independence.

---

## 6. Exact formulas and finite computation

### 6.1 Standard cyclic axes

Let

`H=C_{n_1} direct_sum ... direct_sum C_{n_r}`

and let `A_std={e_1,...,e_r}` be the standard generators.

**Theorem 7 (standard-generator formula).**

`zsf(H;A_std)=sum_i (n_i-1)`.

**Proof.** A zero-sum-free word uses at most `n_i-1` copies of `e_i`, giving the upper bound. Taking exactly `n_i-1` copies on every axis is zero-sum-free because a selected coordinate count can vanish modulo `n_i` only when it is zero. ∎

### 6.2 Multiplicity formulation

For `A={a_1,...,a_m}` and `o_i=ord(a_i)`, `zsf(H;A)` is the optimum of

`maximize sum_i u_i`

subject to `0<=u_i<=o_i-1`, integer, and no nonzero vector `v` with `0<=v_i<=u_i` satisfies `sum_i v_i a_i=0`.

This is finite but not asserted polynomial-time solvable.

---

## 7. Quotient bounds

Let `phi:H -> K` be a homomorphism, `N=ker(phi)`, and `B=phi(A)`.

### 7.1 Lower obstruction

**Theorem 8 (homomorphic lower bound).**

`zsf(H;A) >= zsf(K;B)`.

**Proof.** Lift every occurrence of a maximum zero-sum-free image word. A zero sum among the lifts would map to a zero sum in the image word. ∎

A quotient can therefore refute an over-aggressive source ceiling.

### 7.2 Uniform quotient–kernel upper bound

Let `atom(K;B)` be the maximum length of a minimal nonempty zero-sum word over `B`.

**Theorem 9 (uniform quotient–kernel upper bound).**

`zsf(H;A) <= zsf(K;B)+(D(N)-1) atom(K;B)`.

**Proof.** In the image of a source zero-sum-free word, repeatedly extract minimal image-zero blocks until the remainder is image-zero-sum-free. The source sums of the extracted blocks are nonzero elements of `N` and form a zero-sum-free kernel word, so there are at most `D(N)-1` blocks. Each block has length at most `atom(K;B)`. ∎

### 7.3 Kernel-weighted refinement

For every nonzero `n in N`, define `omega(n)` as the maximum source length of a word `U` over `A` such that `phi(U)` is a minimal image-zero word and `sum U=n`. Omit unrealized kernel sums. For a zero-sum-free word `n_1...n_q` over the realized kernel alphabet, assign weight `sum_i omega(n_i)`. Let `Z_omega` be the maximum such score.

**Theorem 10 (kernel-weighted quotient bound).**

`zsf(H;A) <= zsf(K;B)+Z_omega`.

**Proof.** Use the same minimal image-block extraction. The source kernel sums form a zero-sum-free word. Each extracted block has length at most the weight of its actual kernel sum. The remainder has length at most `zsf(K;B)`. Summing gives the bound. ∎

The weighted bound implies Theorem 9 because a kernel zero-sum-free word has at most `D(N)-1` terms and every weight is at most `atom(K;B)`.

### 7.4 Strict example

Take `H=C_2 direct_sum C_4`, project onto `C_2`, and use the one-letter alphabet `A={(1,1)}`. The source letter has order four, so `zsf(H;A)=3`. The image budget is one. The unique minimal image-zero block has two source letters and source sum `(0,2)`, an order-two kernel element. Hence the weighted kernel can use the block once and `Z_omega=2`, giving the exact cap `1+2=3`. The uniform estimate gives `1+(4-1)2=7`.

---

## 8. Controlled objective defects

Exact deletion dominance may fail by a bounded amount while semantic soundness persists.

**Theorem 11 (event-defect normal form).** If every admitted zero-sum deletion increases cost by at most `epsilon`, an optimum of initial support `n` has a feasible representative of support at most `z=zsf(H;A)` and cost at most

`OPT + epsilon max(0,n-z)`.

**Proof.** Each deletion lowers support by at least one, so at most `n-z` deletions occur. Sum the defects. ∎

**Theorem 12 (coordinate-defect normal form).** If deleting a zero-sum set `T` increases cost by at most `delta |T|`, there is a support-`z` representative of cost at most `OPT+delta n`.

**Proof.** Deleted coordinate sets are disjoint over the descent. Telescope the objective changes. ∎

These are approximation guarantees for the declared objective only.

---

## 9. Two complete separation models

### 9.1 Whole-system reconstruction in a Pauli grammar

A separately declared two-block dependent-triple Pauli grammar uses two independent anticommuting frames per block, a dependent third frame, and two shared Tag strings. The rank-only proof language holds the auxiliary Tags fixed and sees a five-bit abstract basis obstruction. A whole-system reconstruction chooses one anticommuting core per block, deletes all other frame letters, recomputes the dependent frame, and relocates the Tags to canonical cores.

Finite local identities show that deleted non-core columns refund enough frame cost to pay every Restore and Tag realignment penalty. The transformation preserves feasibility and never increases the structural objective. Every frame therefore has a support-one representative, and support zero is infeasible. The intrinsic support of this explicit grammar is one.

The comparison diagnoses the missing proof operation: global auxiliary reconstruction. It does not establish that the abstract five-letter terminal is a production certificate lower bound.

### 9.2 Realized XOR-aggregation production separation

We now give a complete non-Pauli model in which the abstract terminal is a real production state.

Fix `d>=2`. A production state is a finite multiset `W` of nonzero vectors in `F_2^d` with nonzero total XOR. The objective and support are the number of live parity fragments.

The **weak language** permits deletion of any nonempty proper zero-XOR submultiset. The **strong production language** adds the fusion move

`{u,v} -> {u xor v}`

for distinct `u,v`. Equal pairs are already weakly deletable. Fusion preserves total parity and strictly reduces support.

**Theorem 13 (realized production gap).** The exact weak terminal budget is `d`, while the exact strong production budget is `1`.

**Proof.** The weak budget is Theorem 2 specialized to the full nonzero alphabet in `F_2^d`: every word longer than `d` is dependent, and a basis word of length `d` is zero-sum-free. The basis word is an admitted production state, so the weak lower witness is realized.

For the strong language, take any state of length at least two. If two fragments are equal, delete that pair. Otherwise choose two distinct fragments and fuse them; their XOR is nonzero. Every move preserves nonzero total and lowers support. Repetition terminates at one fragment, which must equal the original total XOR. A one-fragment state is terminal. ∎

The finite R8 artifact exhausts all nonzero-total multisets through length `d+1` for `d=2,3,4`. It tests 15, 280, and 14,535 multisets respectively, reproduces weak budgets `2,3,4`, strong budget `1`, and explicit reductions of the basis witnesses.

The example closes the logical production-realization gap outside Q1. Its external compiler significance remains a separate literature and systems question.

---

## 10. Search-volume accounting

A direct labeled-support enumerator on `n` coordinates with `q>=1` local labels and fixed budget `B` visits

`V_B(n;q)=sum_{j=0}^B binom(n,j)q^j`.

**Theorem 14 (sharp fixed-budget asymptotic).**

`V_B(n;q)=(q^B/B!) n^B + O(n^{B-1})`.

For exact certificate budget `beta` and intrinsic budget `kappa`, the ratio is

`V_beta/V_kappa = q^{beta-kappa} kappa!/beta! * n^{beta-kappa}(1+o(1))`.

For independent interaction blocks, multiply the component ratios. The exponent is the sum of blockwise certificate waste.

This statement belongs to the declared enumerator. Algorithms using dynamic programming, implicit states, branch-and-bound, algebraic elimination, or stronger production moves may have different behavior.

---

## 11. Proof-carrying normal-form record

A support claim should be accompanied by a record containing:

1. production grammar and immutable version;
2. objective and support functional;
3. representation map into the certificate state;
4. realized signature group and alphabet;
5. complete named proof-move inventory;
6. semantic read/test/write/guard support of every move;
7. interaction hypergraph and connected components;
8. upper normalization proof or replay trace;
9. terminal witness and production preimage;
10. exhaustive irreducibility audit under the named language;
11. intrinsic lower witness when `kappa` is claimed;
12. exact-search architecture and measured consequence;
13. evidence class of every statement;
14. prohibited inferences.

This record allows a verifier to distinguish a correct abstract theorem from an unsupported promotion.

---

## 12. Applications to AI, algorithms, and exact systems

### 12.1 Proof-carrying exact optimization

An optimizer can publish both its answer and the proof language that justified its finite search. The realization gate prevents an abstract quotient obstruction from being silently reported as a production lower bound.

### 12.2 Certificate-aware branch and bound

A sound move that lowers the certified support budget has an exact value for direct enumerators: it removes a polynomial degree equal to the certificate-waste reduction. The interaction graph identifies whether the gain composes.

### 12.3 Modular and syndrome-preserving repair

Coordinates may represent repair actions with finite-group syndromes. A zero-signature deletion is valid only after the domain proves closure, semantic preservation, and objective control. Quotient bounds can give fail-fast lower obstructions and computable upper caps.

### 12.4 Parity and XOR aggregation

The XOR model shows how a weak deletion proof can miss a sound compositional operation. In parity-network, coding, or linear-algebra pipelines, the analogous question is whether composite actions are legal and how their real objective is charged.

### 12.5 Multi-agent proof systems

Different agents may use different sound transformation languages. Terminal budgets provide a formal comparison of proof strength; adding verified moves can only reduce the budget. Average benchmark success is not a substitute for a strict terminal witness and reduction.

### 12.6 Safe approximation outside an exact cone

Defect normal forms permit a solver to report a sparse state together with an explicit objective allowance, rather than treating the exact theorem as all-or-nothing.

---

## 13. Related work and novelty subtraction

Sparse optimal solutions in integer and combinatorial optimization, Davenport constants and restricted zero-sum invariants, weighted and quotient methods, terminating rewrite systems, proof complexity, exact synthesis, parity networks, and Pauli compilers are established areas. The final submission must verify every citation against primary sources and compare exact hypotheses and conclusions.

The residual contribution claimed here is narrower:

- one vocabulary separating intrinsic, normalization, and proof-language support;
- a realized-alphabet deletion theorem with persistent semantic and objective premises;
- a production realization gate and semantic interaction audit;
- kernel-weighted quotient accounting inside that pipeline;
- a complete realized production separation outside the Pauli/Q1 theorem;
- architecture-specific, blockwise search accounting;
- a proof-carrying record that binds claim ownership and prohibited inferences.

Generic zero-sum, quotient, graph-component, or asymptotic facts are not claimed as new merely because they are assembled here.

---

## 14. Reproducibility and limitations

The displayed proofs carry the all-parameter claims. Finite controls protect arithmetic, state-space definitions, and counterexamples; they do not replace symbolic proofs.

The R8 XOR artifact is deterministic and exhausts the declared bounded state spaces with a second strong-reduction reconstruction. The Pauli finite identities and the quotient examples have separate existing verifiers. A final submission package should include one command that runs all small controls and emits content hashes.

Limitations are substantive.

1. Production deletion semantics are domain-specific.
2. Computing `zsf(H;A)` or the weighted kernel budget can be difficult.
3. The XOR grammar is complete by definition and serves as a logical separation; broader compiler impact requires an external case.
4. Enumeration penalties are not complexity-class lower bounds.
5. Structural support is not physical cost unless a validated resource map says so.
6. Intrinsic language requires a lower witness under the complete production grammar.
7. Current novelty authority remains open pending primary-source and specialist review.

---

## 15. Conclusion

A finite support ceiling is not a self-interpreting number. It belongs to an optimization family, a normalization, or a proof language. The alphabet-restricted zero-sum budget gives a sharp terminal invariant for one important deletion language, but production use requires semantic soundness, objective control, realization, and a complete move audit.

Composition occurs over semantic interaction blocks, not nominal modules. Quotients are useful only when their realized source blocks are retained. A sound production move can collapse a sharp abstract terminal, as the Pauli reconstruction and complete XOR-aggregation separation show.

The practical reporting rule is therefore strict: bind every support claim to the language that owns it, supply a production witness before claiming a production lower bound, and name the algorithm architecture before turning certificate waste into search cost.

## Tool-use disclosure

A generative language model assisted theorem consolidation, manuscript organization, code generation, and language revision. Human authors remain responsible for every definition, proof, citation, executable claim, interpretation, and final submission.

## Provisional references requiring final primary-source audit

1. I. Aliev, J. A. De Loera, F. Eisenbrand, T. Oertel, and R. Weismantel, “The Support of Integer Optimal Solutions,” *SIAM Journal on Optimization* 28 (2018), 2152–2157.
2. M. Freeze and W. A. Schmid, “Remarks on a Generalization of the Davenport Constant,” *Discrete Mathematics* 310 (2010), 3373–3389.
3. G. Wang, “The universal zero-sum invariant and weighted zero-sum for infinite abelian groups,” *Communications in Algebra* 53 (2025), 1581–1599.
4. P. Diaconis and B. Sturmfels, “Algebraic Algorithms for Sampling from Conditional Distributions,” *Annals of Statistics* 26 (1998), 363–397.
5. G. Li et al., “Paulihedral: A Generalized Block-Wise Compiler Optimization Framework for Quantum Simulation Kernels,” ASPLOS 2022.
6. N. Schillo, A. Sturm, and R. Quay, “TARE: Block Encoding Linear Combinations of Pauli Strings Without Ancilla State Preparation,” arXiv:2601.05740 (2026).
7. Primary sources on parity-network and XOR-circuit synthesis to be added after the frozen nearest-work audit.
8. Primary sources on terminating rewrite-system derivational complexity and proof-language simulations to be added after the frozen nearest-work audit.
