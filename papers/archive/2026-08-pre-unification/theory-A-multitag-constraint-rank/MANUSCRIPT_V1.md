# Constraint-Rank Normal Forms for Multi-Tag TARE Compilation

**Paper A — publication-candidate manuscript**

## Abstract

A structural support theorem for a quantum compiler is useful only if the quantity bounding support is clearly separated from the proof used to obtain it. We study this question for an explicit extension of the Tag-and-Restore (TARE) block-encoding construction in which an arbitrary number of ordered two-target blocks share multiple Tag Paulis. For `b>=2` blocks and `s>=0` shared Tags, every active coordinate of a frame Pauli carries an `(s+1)`-bit symplectic signature recording partner anticommutation and Tag labels. We prove that, throughout the objective region

`mu >= (b-1) t_R`, 

every admitted instance has an exact optimum in which each frame Pauli `R` satisfies

`support(R) <= rank(V_R) <= s+1`,

where `V_R` is the realized signature multiset of that frame. The proof deletes a proper zero-signature subset whenever support exceeds realized rank. The only coupled objective change occurs in a `b`-way Restore term. A one-letter replacement increases the corresponding Restore functional by at most `b-1`, and this bound is exact, so a frame refund of at least `mu` makes every deletion non-increasing in the stated cone. The theorem is instance-adaptive: if only a lower-dimensional subset of signatures is realized, the guaranteed support decreases with the realized rank rather than the ambient number of Tags. For the frozen three-block, one-Tag R6M specialization, independent all-size upper and lower results give the sharp intrinsic support number `kappa_R6M=2`. We do not claim that `s+1` is intrinsically necessary for multiple Tags, nor that larger support is necessary outside the proof-validity cone. The result identifies constraint rank as a transferable exact **normal-form certificate** for this compiler grammar while keeping intrinsic support, objective dependence, and physical resource cost separate.

## 1. Introduction

TARE was introduced as a block-encoding construction for linear combinations of Pauli strings without conventional ancilla state preparation. That construction exposes auxiliary Pauli-frame, Tag, branch and Restore choices. Optimizing those choices is a separate problem from inventing TARE itself. The donor construction is therefore the starting point rather than the novelty claim of this paper.

Exact quantum synthesis and compilation contain many normal-form arguments: a large search is replaced by a theorem stating that an optimum has a representative in a smaller family. The bound in such a theorem can be tempting to read as an intrinsic complexity of the compiler. This interpretation is unsafe unless a matching lower witness is known. A support ceiling can instead be a certificate produced by a particular proof language.

The present paper asks a narrower structural question. Suppose a frame is constrained only through finitely many binary symplectic relations: one relation with its anticommuting partner and one relation with each shared Tag. When can coordinates that do not add independent constraint information be removed without making the structural objective worse?

The answer is exact for the grammar below. The number of blocks affects the **objective cone** because changing a frame letter can disrupt a coupled Restore pattern in several blocks. The number of independent symplectic constraints affects the **support ceiling** because it controls the dimension of the coordinate signatures. Those two roles separate cleanly:

- `b` controls the maximum local Restore penalty `b-1`;
- the realized signature rank controls the number of frame coordinates needed in a normal form.

This yields an all-size theorem for arbitrary `b` and `s`, while the older R6M result becomes a sharp binary specialization rather than the whole story.

### 1.1 Contributions

**A1 — arbitrary-block Restore sensitivity.** For the natural `b`-way Restore functional, changing one local letter increases the Restore cost by at most `b-1`, and the bound is attained.

**A2 — realized constraint-rank normal form.** In the region `mu >= (b-1)t_R`, every optimum has a representative with frame support at most its realized partner/Tag signature rank, hence at most `s+1`.

**A3 — sharp R6M specialization.** At `b=3`, `s=1`, `mu=2`, `t_R=1`, the normal form specializes to support at most two. Independent upper and necessity results establish `kappa_R6M=2`.

**A4 — explicit boundary semantics.** Outside the cone, only this deletion proof becomes unavailable. The paper does not infer a phase transition or higher-support necessity. For `s>=2`, ambient rank `s+1` is likewise an upper certificate rather than an intrinsic support number.

## 2. Compiler grammar

Fix integers `b>=2` and `s>=0`. There are `b` ordered two-target blocks. Block `j` contains an anticommuting frame pair `(R_j0,R_j1)`, a target assignment and a central branch. Across the blocks are shared Tag Paulis `S_1,...,S_s`. For each Tag, the prescribed branch label is common across blocks and opposite between the two branches of a block.

At a qubit coordinate, use local Pauli letters from `{I,X,Y,Z}`. Let `w(R)` be the support of a frame Pauli. The structural objective contains three terms relevant to the theorem:

1. each active frame coordinate is charged with branch multiplier `m_jk>=mu`;
2. Tag `S_l` is charged by an arbitrary nonnegative coefficient times `w(S_l)`;
3. Restore is charged by `t_R>=0` times the local `b`-way functional

`F_b(a_1,...,a_b) = 1`

when all `b` letters are the same nonidentity Pauli, and otherwise

`F_b(a_1,...,a_b) = # {i : a_i != I}`.

Tags are held fixed by the exchange below. The structural objective is not a physical T count, runtime, circuit depth or fault-tolerant resource estimator.

## 3. Local Restore lemma

**Lemma 1 (one-letter sensitivity).** For every `b>=2`, changing one argument of `F_b` can increase its value by at most `b-1`. The bound is exact.

**Proof.** If neither the old nor new tuple is the all-equal nonidentity special case, `F_b` is simply Hamming weight with respect to identity, so a one-letter change raises it by at most one. If the new tuple is all-equal nonidentity, the value becomes one and therefore does not create a larger increase. The only potentially larger increase occurs when the old tuple is all-equal nonidentity, with value one, and the changed letter breaks equality while remaining nonidentity. The new tuple then contains `b` nonidentity letters and is no longer special, so its value is `b`; the increase is exactly `b-1`. For `b=2`, the ordinary Hamming-weight case also attains one. ∎

A separate implementation exhausts every local old tuple, changed position and new Pauli letter for `b=2,...,7`; in each case the observed maximum is `b-1`. These finite checks corroborate the formula but are not the source of its all-`b` authority.

## 4. Realized signatures

Fix one frame `R` and its block partner `R'`. At every active coordinate `q`, define

`v_q = (<R_q,R'_q>, <S_1q,R_q>, ..., <S_sq,R_q>) in F_2^(s+1)`,

where `<.,.>` is the local binary symplectic product. Let `V_R` be the multiset of realized signatures and let

`d_R = rank(V_R)`.

The XOR of all signatures has first component one because `R` and `R'` must anticommute. Hence the total signature is nonzero.

The distinction between **ambient rank** and **realized rank** matters. A grammar with `s` Tags permits at most `s+1` independent bits, but a particular optimum may realize fewer independent signatures. The theorem adapts to that lower rank.

## 5. Constraint-rank normal form

**Theorem 2 (arbitrary-block MultiTag normal form).** Consider any admitted instance of the grammar above. If

`mu >= (b-1)t_R`,

then there exists an exact optimum in which every frame Pauli `R` satisfies

`support(R) <= d_R <= s+1`.

**Proof.** Start from an optimum. Suppose a frame `R` has weight greater than `d_R`. Its realized signatures are linearly dependent over `F_2`. Therefore a nonempty subset of active coordinates has zero signature XOR. Because the XOR of all active signatures is nonzero, that zero-signature subset is proper.

Set `R` to identity on this subset. The first signature coordinate sums to zero, so the partner-anticommutation parity is unchanged. Every Tag signature coordinate also sums to zero, so all required Tag labels are unchanged. Tags themselves are not edited.

At every deleted coordinate, the frame term refunds at least `mu`. The only coupled cost that can rise is Restore. Lemma 1 bounds the increase of the corresponding local Restore contribution by `(b-1)t_R`. Hence each deleted coordinate has net change at most

`-mu + (b-1)t_R <= 0`.

The transformed configuration is feasible and no more expensive. Repeating the operation strictly decreases support until `support(R)<=d_R`. Apply the same argument to every frame. Since `V_R` lies in `F_2^(s+1)`, `d_R<=s+1`. ∎

### 5.1 What the cone means

The inequalities define a **proof-validity cone**, not a globally sharp phase boundary. If `mu<(b-1)t_R`, the local accounting no longer guarantees that the deletion is non-increasing. This does not prove that a counterexample exists, and it does not prove that larger support becomes necessary.

### 5.2 Tag weights

Arbitrary nonnegative Tag weights do not change Theorem 2 because the exchange leaves every Tag Pauli unchanged. This observation is specific to objectives in which Tag cost depends only on the fixed Tag supports; it does not authorize arbitrary Tag-coupled objectives.

## 6. Sharp binary specialization

Set `b=3`, `s=1`, `mu=2` and `t_R=1`. The cone boundary is exact: `2=(3-1)1`. Theorem 2 gives frame support at most two.

The frozen R6M compiler has two independent parent results: an all-size support-two theorem and an exact instance for which support one is insufficient. Their combination yields

`kappa_R6M = 2`.

This is a statement about the intrinsic support number of that one-Tag grammar and objective. It is deliberately not transferred to general `s`.

## 7. Relation to neighboring work

TARE and its Tag-and-Restore construction are donor-owned. Binary symplectic representations of Pauli operators and global symplectic compiler simplification are likewise established tools. Recent global-BSF Hamiltonian compilers demonstrate that whole-program symplectic structure is an active contemporary optimization direction. Exact synthesis and canonical-form work already establish provable optimality for other gate families.

There is also a broader optimization literature on sparse optimal solutions. In particular, Aliev, De Loera, Eisenbrand, Oertel and Weismantel prove objective-independent support bounds for integer programs. The present theorem does not introduce sparsity as an optimization concept. Its residual contribution is the exact deletion-dominance law for this TARE-derived grammar, the realized symplectic-rank certificate, its arbitrary-block objective cone, and the sharp R6M specialization.

## 8. Reproducibility

The three-block parent theorem is bound to the committed Paper A A1 protocol, result, generic verification and native dual-harness records. The publication verifier in `papers/verify_five_theory_upgrades.py` independently enumerates the `b`-way Restore functional for `b=2,...,7` and checks the exact `b-1` local maximum. The all-`b` theorem itself is the analytic proof in Lemma 1 and Theorem 2.

A final submission should archive the exact submission commit and include a compact machine-readable theorem manifest. Internal dual implementations are not described as external replication.

## 9. Limitations

1. The theorem applies to the explicitly defined MultiTag-TARE grammar, not every possible multi-Tag compiler.
2. `s+1` is an ambient certificate ceiling; no general sharpness result is claimed for `s>=2`.
3. Outside `mu >= (b-1)t_R`, the proof is silent.
4. The structural objective is not an end-to-end physical resource model.
5. The result does not establish quantum advantage.
6. The novelty review is hostile and primary-source oriented but remains author-side; external referees may identify closer prior results.

## 10. Discussion

The theorem separates two sources of complexity that are easy to conflate. The number of blocks determines how expensive it can be to disturb a coupled Restore pattern; the realized symplectic rank determines how many frame coordinates are required to carry independent constraints. Increasing `b` therefore narrows the objective cone without increasing the support ceiling, whereas increasing independent Tags can raise the ceiling without changing the local Restore sensitivity.

This separation also motivates Paper B. A rank bound can be sharp for the certificate language that proves it and still fail to be intrinsic to the compiler. Paper A supplies the positive side: realized constraint rank is a clean, transferable and sometimes sharp normal-form certificate. The next question is when that certificate should be interpreted as a property of the proof rather than the optimized object.

## 11. Conclusion

For an arbitrary number of TARE-derived blocks sharing arbitrary many Tags, a simple local law controls the global normal form. A one-letter change in `b`-way Restore costs at most `b-1`; consequently, throughout `mu >= (b-1)t_R`, redundant zero-signature coordinates can be deleted until every frame has support no larger than its realized symplectic constraint rank. The one-Tag R6M case is sharply support two. Beyond that specialization, the theorem is intentionally one-sided: constraint rank is an exact certificate of sufficient support, not a claim of intrinsic necessity.

## Selected references

- N. Schillo, A. Sturm and R. Quay, _TARE: Block Encoding Linear Combinations of Pauli Strings Without Ancilla State Preparation_, arXiv:2601.05740v4 (2026).
- I. Aliev, J. A. De Loera, F. Eisenbrand, T. Oertel and R. Weismantel, _The Support of Integer Optimal Solutions_, SIAM J. Optim. 28, 2152–2157 (2018), DOI 10.1137/17M1162792.
- Z. Yang et al., _Efficient Compilation for Hamiltonian Simulation via Global Binary Symplectic Form Simplification_, arXiv:2608.11579 (2026).

---

## Publication decision record

**Primary target posture:** `Quantum` original research. Its current criteria explicitly permit narrow work if it is a very significant technical or conceptual advance and require correctness, significance, clarity, reproducibility and honest limitations.  
**Stretch:** `PRX Quantum`, but only if independent experts support an exceptional-connection/insight case connecting exact compiler normal forms, symplectic constraints and proof-language complexity.  
**Internal status:** `STRONG_SPECIALIST_SUBMISSION_CANDIDATE__PRX_STRETCH_REQUIRES_EXTERNAL_SIGNIFICANCE_REVIEW`.  
**Remaining blocking work before external submission:** full TARE-v4 donor PDF re-read; fresh exact-statement novelty search; final figures; journal-specific formatting; independent proof/replay audit.
