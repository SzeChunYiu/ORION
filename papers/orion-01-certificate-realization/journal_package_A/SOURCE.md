# Restore-Sensitive Support Normal Forms for Multi-Tag Quantum Compilation

**ORION-01A — scientific successor manuscript V3**  
**Supersedes for journal science:** `theory-A-MANUSCRIPT_V2.md`  
**Preserves:** all V2 results, negative boundaries, and frozen provenance

## Abstract

Support bounds in exact quantum compilation often arise from a restricted deletion proof rather than from an intrinsic lower bound of the compiler. We isolate that distinction for a MultiTag-TARE grammar. The combinatorial zero-sum invariant used in the proof is donor mathematics: for a finite abelian signature group `H` and a fixed allowed alphabet `A`, let `zsf(H;A)` be the longest zero-sum-free sequence over `A`. The new content is the compiler-side contract that makes this donor invariant usable.

We state the deletion theorem with the quantifiers needed by a real compiler: each generator has an instance-level alphabet fixed before optimization; a legal deletion preserves feasibility of the whole instance; and repeated deletions cannot increase any generator's support. Starting from an optimum and applying admissible zero-sum deletions until a global fixed point is reached gives one optimum satisfying the `zsf` ceiling simultaneously for every constrained generator. In an elementary binary quotient this implies the familiar rank ceiling, but that rank statement is explicitly binary-specific and is not itself novel.

For the registered arbitrary-block MultiTag grammar, one frame-support deletion changes one argument of one charged local `b`-way Restore term. The exact one-argument sensitivity of that term is `b-1`; therefore the objective-deletion cone is

`mu >= (b-1)t_R`.

Inside this cone, every admitted instance has an optimum with

`support(R) <= zsf(H_R;A_R) <= rank(H_R) <= s+1`

for every frame `R`, where `A_R` is the fixed instance-level signature alphabet and `H_R=<A_R>`. The frozen one-Tag, three-block R6M family is the sharp control: the certificate ceiling is two and independent compiler evidence establishes intrinsic support `kappa_R6M=2`. We do not claim general MultiTag sharpness, necessity outside the cone, or physical quantum advantage.

## 1. Scientific question and novelty boundary

The question is not whether Davenport-type zero-sum thresholds exist; they do, and that mathematics is prior work. The question is what a compiler must establish before such a threshold becomes a valid simultaneous normal form under its semantics and objective.

The surviving paper-level contributions are therefore:

1. an explicit whole-instance deletion contract and global fixed-point proof that yields simultaneous support ceilings;
2. the exact Restore sensitivity `b-1` and resulting objective cone for the stated MultiTag grammar;
3. the compiler-specific separation between certificate ceiling and intrinsic support, with R6M as a sharp control.

The following are **not** claimed as novel: Davenport constants, zero-sum-free sequence theory, the binary rank corollary, generic proof-system-relative complexity, or sparse-support theory.

## 2. Fixed alphabets and zero-sum-free sequences

Let `H` be a finite abelian group written additively and let `A subseteq H` be a finite alphabet fixed independently of the optimum being bounded. A **subsequence** means an arbitrary sub-multiset of positions; it need not be contiguous.

A sequence over `A` is zero-sum-free if no nonempty subsequence has sum zero. Define

`zsf(H;A) = max({0} union {|W| : W is zero-sum-free over A})`.

The explicit zero in the maximum handles degenerate alphabets. For the full nonzero alphabet the object reduces to the standard small-Davenport threshold; for restricted alphabets it is an alphabet-specific variant. We use `zsf` only as notation for this donor-owned combinatorial object.

## 3. Simultaneous deletion theorem

Fix one optimization instance. For each constrained generator `R`, let `A_R` be the set of signatures realizable by any admissible local state of that instance, fixed before optimization, and let every active coordinate of `R` carry `v_q in A_R subseteq H_R`.

Assume:

1. **nonzero total:** every feasible constrained generator satisfies `sum_q v_q != 0`;
2. **whole-instance deletion soundness:** deleting any nonempty zero-sum subsequence of coordinates of `R` preserves all constraints of the full instance, not only constraints local to `R`;
3. **objective dominance:** the same deletion does not increase the objective;
4. **support monotonicity:** deleting coordinates of one generator does not activate coordinates of another generator or otherwise increase any generator's support.

**Theorem 1 (simultaneous alphabet ceiling).** Every admitted instance has an exact optimum such that, simultaneously for every constrained generator `R`,

`support(R) <= zsf(H_R;A_R)`.

**Proof.** Start from any optimum. If some generator `R` has a signature sequence longer than `zsf(H_R;A_R)`, it contains a nonempty zero-sum subsequence. Since the total signature of `R` is nonzero, that subsequence cannot be the whole active sequence. Delete it. Assumptions 2 and 3 preserve feasibility and optimality, while total support strictly decreases and no other support increases by Assumption 4. Repeat whenever any generator remains reducible. Total support is a nonnegative integer, so the process terminates at a global fixed point. At that fixed point no generator contains a nonempty zero-sum subsequence; hence every generator's active signature sequence is zero-sum-free over its fixed alphabet and has length at most `zsf(H_R;A_R)`. This one terminal optimum satisfies all generator bounds simultaneously. ∎

This global fixed-point argument is the required quantifier step; a one-pass instruction to “repeat for every generator” is not sufficient when generators may share constraints.

## 4. Binary rank is only a corollary

If `H=F_2^d`, any sequence of more than `d` vectors is linearly dependent. The dependent positions form a nonempty zero-XOR subsequence, so

`zsf(F_2^d;A) <= d`.

If `A` contains a basis, equality holds for the abstract deletion language.

This statement is specific to elementary binary groups. It must not be generalized to arbitrary finite abelian groups: for example, in `Z_n` with alphabet `{1}`, the sequence of `n-1` ones is zero-sum-free even though the group has rank one.

A rank ceiling becomes an intrinsic compiler statement only after a separate compiler lower witness.

## 5. MultiTag-TARE grammar and the nonzero-total invariant

Fix `b>=2` ordered blocks and `s>=0` shared Tag Paulis `S_1,...,S_s`. Each constrained frame Pauli `R` has an anticommuting partner `R'`. At an active frame coordinate `q`, define

`v_q=(<R_q,R'_q>,<S_1q,R_q>,...,<S_sq,R_q>) in F_2^(s+1)`.

The XOR of the first components equals the global binary symplectic product `<R,R'>`. Since `R` and `R'` anticommute, `<R,R'>=1`, and therefore the total signature is nonzero. This discharges Theorem 1's first assumption for the registered grammar.

For each frame `R`, define `A_R` at the instance level as the set of signatures realizable by any admissible local frame state, not the alphabet observed in a particular optimum. Set `H_R=<A_R>`.

## 6. Exact Restore sensitivity

The local Restore term is

`F_b(a_1,...,a_b)=1`

when all `b` letters are the same nonidentity Pauli, and otherwise equals the number of nonidentity letters.

**Lemma 2 (one-argument sensitivity).** Replacing one argument of `F_b` can increase its value by at most `b-1`, and the bound is attained whenever the local Pauli alphabet contains at least two distinct nonidentity letters.

**Proof.** Away from the all-equal nonidentity state, changing one argument changes ordinary nonidentity Hamming weight by at most one. Entering the special state lowers the value. Leaving the all-equal nonidentity state by replacing one letter with a different nonidentity letter changes the value from `1` to `b`, giving the exact increase `b-1`. ∎

The registered MultiTag incidence contract assigns a frame-support deletion to exactly one argument replacement in exactly one charged local `F_b` term. This incidence is part of the grammar; without it the following objective cone would have to be multiplied by the number of affected Restore terms.

## 7. Restore-sensitive MultiTag normal form

The objective charges each active frame coordinate by at least `mu`, includes arbitrary nonnegative Tag-support terms, and charges the local Restore term by `t_R>=0`.

Deleting `k` frame coordinates in a sound zero-sum subsequence refunds at least `k mu`. By the incidence contract and Lemma 2 it adds at most `k(b-1)t_R` in Restore cost. Hence deletion is non-increasing whenever

`mu >= (b-1)t_R`.

**Theorem 3 (MultiTag support normal form).** Under the registered grammar and incidence contract, if `mu >= (b-1)t_R`, every admitted instance has an exact optimum satisfying

`support(R) <= zsf(H_R;A_R) <= rank(H_R) <= s+1`

simultaneously for every frame `R`.

**Proof.** Zero signature preserves the partner and Tag constraints by the registered semantic map. The objective calculation above establishes deletion dominance. Theorem 1 then gives the simultaneous `zsf` ceiling. Because `H_R` is an elementary binary subgroup of `F_2^(s+1)`, Section 4 gives the rank bounds. ∎

The first inequality may be strictly stronger than rank when the fixed admissible alphabet does not realize a basis of its generated subgroup.

## 8. Sharp R6M control

For the frozen one-Tag, three-block R6M family,

`b=3`, `s=1`, `mu=2`, `t_R=1`.

The objective lies on the cone boundary. The registered signature alphabet realizes a basis of `F_2^2`, so the rank-only deletion ceiling is two. The commit-bound A1 parent evidence supplies the all-size upper result and the independent support-one obstruction needed to conclude

`kappa_R6M=2`,

where `kappa` denotes the mathematical minimum uniform support bound of the compiler family under the frozen objective. This exact value is a compiler result; the zero-sum/rank argument alone would not establish it.

No corresponding lower theorem is claimed for general MultiTag-TARE.

## 9. Relation to prior work

Zero-sum sequence theory owns Davenport-type thresholds and restricted-alphabet variants. Sparse integer optimization owns general support bounds for optimal solutions. Standard stabilizer formalism owns the binary symplectic signature machinery. Proof-complexity and formal-methods literatures own the general distinction between a proof system and the object it certifies.

The residual contribution is narrower: the registered TARE/MultiTag semantic signature, the exact Restore sensitivity and objective cone, the whole-instance simultaneous deletion contract, and the sharp R6M control.

## 10. Reproducibility and authority

The R6M parent theorem, objective ledger and necessity witness are commit-bound in the existing A1 evidence package. The finite verifiers test the local Restore function and small-group signature mechanisms, but all-size authority comes from the proofs above and from the cited R6M parent theorem. Internal independent implementations are not external replication.

## 11. Limitations

1. The zero-sum object is donor mathematics; novelty is not claimed for `zsf` itself.
2. The deletion theorem requires whole-instance soundness, objective dominance and support monotonicity.
3. The MultiTag cone uses the explicitly stated one-deletion/one-Restore-argument incidence contract.
4. Outside `mu >= (b-1)t_R`, the proof is silent; no larger-support necessity follows.
5. General MultiTag sharpness is open.
6. Structural support is not T count, depth, runtime, qubits, or quantum advantage.
7. Submission-date donor overlap and independent specialist proof review remain external scientific checks.

## 12. Conclusion

The scientifically defensible result is not a new zero-sum invariant. It is a compiler theorem specifying exactly when donor zero-sum mathematics can be converted into a simultaneous support normal form. The global fixed-point proof closes the multi-generator quantifier; the instance-level alphabet removes solution-relative circularity; the Restore incidence and exact `b-1` sensitivity expose the objective condition; and R6M shows one case where the certificate ceiling is genuinely intrinsic. That bounded result is the journal object.