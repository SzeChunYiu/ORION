# Certifiable Support Budgets versus Intrinsic Support in Quantum Compilation

**ORION-01 Paper B — recursive academic-paper-pipeline final editorial master**  
**Scientific cut:** proof-system support budgets versus intrinsic optimal support under one frozen objective  
**Primary route:** Theoretical Computer Science  
**Specialist fallback:** Journal of Automated Reasoning / quantum-compilation theory venue  
**Authority:** `BOUNDED_PAPER_RETAINED__PROOF_LANGUAGE_SEPARATION__PRODUCTION_COMPLETENESS_SEPARATE`

## Abstract

A normal-form proof can certify that an exact optimum exists below a support ceiling without proving that the ceiling is necessary for the compiler. We formalize the distinction between **intrinsic optimal support** and the **certifiable support budget of a named proof system**.

For an instance family `F` and objective `C`, let `kappa(F;C)` be the smallest uniform support bound attained by some `C`-optimal solution for every admitted instance. This is a property of the compiler family. For a sound proof system `P`, let `beta_P(F;C)` be the smallest uniform support budget that `P` can prove from its declared premises and rules. Soundness gives

`kappa(F;C) <= beta_P(F;C)`.

Equality requires a separate compiler-side lower witness; strict inequality diagnoses incompleteness of the proof language rather than excess support in the compiler.

We instantiate `P` as a rank-only zero-sum deletion system over an elementary binary signature group. The rule may use ambient binary rank but no finer alphabet invariant or compiler-specific reconstruction. Under the same frozen weighted-support objective, the one-Tag three-block R6M family is a sharp control:

`kappa(R6M;C)=2=beta_P_rank(R6M;C)`.

For R6I, a whole-system compiler argument establishes intrinsic support one, while the rank-only proof language exposes a five-dimensional signature basis and certifies only budget five:

`kappa(R6I;C)=1<5=beta_P_rank(R6I;C)`.

A componentwise product statement amplifies this one-component gap only under explicit additive objectives and a no-cross-component rule; it is a definitional consequence, not independent evidence. The paper does not claim lower bounds against all proof systems, general certificate complexity, production move completeness, physical resource advantage, or a new zero-sum invariant. Its contribution is the exact same-objective separation between what a compiler needs and what a fixed proof language can certify.

## 1. Introduction

Support normal forms serve two scientific roles that are easily confused. They can reveal a structural property of exact optima, and they can bound the search space exposed by a particular proof or verification method. These roles coincide only when the proof's ceiling is sharp for the compiler.

Suppose a proof attaches a `d`-bit signature to each active coordinate and removes a zero-signature subset once support exceeds `d`. The resulting theorem may be exact and useful. It does not imply that the compiler sometimes needs support `d`. Another whole-system argument may show that every optimum can be represented with support one even though the rank-only proof cannot derive that fact.

This paper separates:

1. the compiler and its exact objective;
2. the mathematical minimum support among exact optima;
3. the uniform support budget certified by a named proof system.

The term **certifiable support budget** is deliberate. It is not the computational-complexity notion of certificate complexity, and it is not an empirical estimate of current proof search.

The paper contributes:

- exact definitions of intrinsic and proof-relative support;
- the soundness inequality `kappa<=beta`;
- a sharp equality control in R6M;
- a strict rank-only proof-language separation in R6I under the same objective;
- explicit restrictions under which componentwise product amplification is valid.

## 2. Fixed optimization semantics

Let `F` be a family of finite exact compilation instances. For instance `I`, let `X(I)` be the feasible set, `C_I:X(I)->R` the fixed objective, and `sigma_I(x)` the support statistic.

### Definition 1 — intrinsic optimal support

For one instance,

`kappa(I;C)=min{sigma_I(x): x in argmin_{y in X(I)} C_I(y)}`.

For the family,

`kappa(F;C)=sup_{I in F} kappa(I;C)`

when the supremum is finite.

The definition is mathematical. The value can be established by a theorem, exact search, or upper/lower witnesses, but it is not defined by what has currently been proved.

### Definition 2 — proof-system certifiable support budget

A proof system `P` is a fixed set of admissible premises, inference rules, and conclusion forms. Define

`beta_P(F;C)=min{k: P proves uniformly that every I in F has some C-optimal x with sigma_I(x)<=k}`.

If no finite uniform bound is derivable, set `beta_P(F;C)=infinity`.

### Proposition 1 — soundness inequality

If `P` is sound for `(F,C)`, then

`kappa(F;C)<=beta_P(F;C)`.

**Proof.** Any sound uniform derivation of budget `k` establishes an exact optimum with support at most `k` for every admitted instance. The minimum support among exact optima is therefore at most `k` instancewise. Taking the family supremum and then the smallest provable `k` gives the inequality. ∎

The reverse inequality does not follow. A sound proof language can be incomplete.

## 3. Rank-only zero-sum deletion

Fix `H=F_2^d` and an admissible alphabet `A subseteq H`. A sequence is an ordered word over `A`; a subsequence may select arbitrary positions and need not be contiguous. Repetition is allowed.

The proof system `P_rank` contains one support-reduction rule. For a supported object with signature word `W`, it may use:

1. nonzero total signature;
2. a premise that deleting zero-signature coordinates preserves whole-instance feasibility;
3. a premise that the deletion does not increase the fixed objective `C`;
4. ambient binary rank `d`.

It may not use a smaller alphabet-sensitive zero-sum invariant, exact compiler enumeration, global reconstruction, or family-specific normal form beyond those premises.

If `|W|>d`, linear dependence supplies a nonempty zero-XOR subsequence. Because the total signature is nonzero, the subsequence is proper, so the declared deletion remains admissible.

### Theorem 2 — rank-only budget

When the rule's premises hold uniformly in a dimension-`d` family,

`beta_P_rank(F;C)<=d`.

If the proof-system model admits a zero-sum-free basis word and contains no additional reduction rule, then

`beta_P_rank(F;C)=d`.

The basis obstruction belongs to the proof abstraction. It is not automatically an intrinsic compiler lower bound because exact optima may avoid the obstructing signature pattern or admit a global transformation outside the proof language.

## 4. Sharpness and proof-language separation

### Definition 3 — support-sharp proof system

`P` is support-sharp for `(F,C)` when

`kappa(F;C)=beta_P(F;C)`.

### Definition 4 — strict proof-language separation

A strict support separation occurs when

`kappa(F;C)<beta_P(F;C)`.

The inequality says that the proof language certifies a weaker support budget than the compiler intrinsically needs. It is not a runtime-complexity separation and not a lower bound against every possible proof method.

## 5. R6M equality control

R6M and R6I are compared under the same frozen weighted-support objective `C`.

For the one-Tag, three-block R6M family, the rank-only signature group has dimension two. The compiler-specific semantic and objective premises establish the uniform rank-only budget

`beta_P_rank(R6M;C)=2`.

An independent all-size upper theorem shows that every admitted instance has an exact optimum with support at most two. A complete support-one referee supplies an exact witness for which support one is insufficient under the same objective. Consequently,

`kappa(R6M;C)=2=beta_P_rank(R6M;C)`.

This is the bounded equality control. It does not establish that rank-only deletion is sharp for arbitrary MultiTag grammars.

## 6. R6I strict separation

The R6I rank-only proof abstraction exposes a five-dimensional binary signature space and admits a zero-sum-free basis obstruction. Under the fixed proof language,

`beta_P_rank(R6I;C)=5`.

A separate whole-system compiler construction establishes that every admitted R6I instance has an exact optimum with support one, and support zero is infeasible. Thus

`kappa(R6I;C)=1`.

Therefore,

`kappa(R6I;C)=1<5=beta_P_rank(R6I;C)`.

The gap identifies information or transformations missing from rank-only deletion. The compiler argument can coordinate structure at the whole-system level in a way the fixed local signature rule cannot express.

The statement is proof-system-relative. It does not imply that every proof of the R6I normal form must pass through support five.

## 7. What the comparison establishes

R6M and R6I separate three possibilities.

1. A proof budget can be **sound and sharp**: R6M.
2. A proof budget can be **sound but loose**: R6I.
3. A smaller alphabet-sensitive certificate can improve ambient rank without necessarily reaching intrinsic support.

Reporting only `d` would hide these distinctions. The same numerical support ceiling can mean “the compiler needs this,” “this proof language certifies this,” or “a current proof has not exploited additional structure.”

## 8. Definitional product amplification

Let `F_1` and `F_2` be independently composed families with additive objective

`C((x_1,x_2))=C_1(x_1)+C_2(x_2)`

and additive support

`sigma((x_1,x_2))=sigma_1(x_1)+sigma_2(x_2)`.

Assume:

- the compiler has no cross-component move;
- feasibility factors componentwise;
- the product proof system has no cross-component inference rule.

### Proposition 3 — componentwise product identity

Under those assumptions,

`kappa(F_1 x F_2;C)=kappa(F_1;C_1)+kappa(F_2;C_2)`

and

`beta_{P_1 x P_2}(F_1 x F_2;C)=beta_{P_1}(F_1;C_1)+beta_{P_2}(F_2;C_2)`.

For `m` independent R6I copies, intrinsic support is `m` and the rank-only budget is `5m`. The absolute gap is `4m` and the ratio is five.

This is a definitional amplification of the one-component separation. It is not a new empirical result or an unrestricted asymptotic theorem; changing the product grammar or allowing cross-component moves can invalidate the identity.

## 9. Fixed-size and growing-parameter regimes

Two asymptotic readings must remain separate.

- With fixed signature rank and growing system size, an all-size theorem can yield a support ceiling independent of size.
- If signature rank, shared-Tag count, or the number of independent components grows, the proof-system budget can grow as well.

A constant-support theorem for one fixed family parameter does not imply a uniform constant when that parameter is allowed to diverge.

## 10. Relation to prior work

Davenport and restricted zero-sum invariants, binary linear dependence, sparse optimum theorems, Pauli symplectic representations, proof systems, and the general distinction between a phenomenon and the strength of a proof method are donor-owned.

The residual is the exact same-objective pair of compiler controls:

- R6M equality between intrinsic and rank-only budgets;
- R6I strict separation between intrinsic support one and rank-only budget five.

The paper does not claim a general proof-complexity theory, a lower bound against all proof systems, a new certificate-complexity measure, or production move completeness.

## 11. Reproducibility and authority

A release must bind:

1. exact R6M and R6I family definitions and objective;
2. R6M all-size upper and complete support-one lower evidence;
3. R6I whole-system upper and support-zero obstruction;
4. the rank-only proof-system definition and basis obstructions;
5. an implementation-independent checker for the abstract definitions and arithmetic;
6. the active adverse `CANNOT_CHECK_MOVE_COMPLETENESS` terminal from the capped production search.

The checker does not import production compiler code and does not regenerate every parent witness. It tests the abstract proof logic and boundary cases. Parent compiler evidence must remain independently content-hash bound.

## 12. Limitations

`beta_P` is relative to a fixed proof language. A richer proof system can reduce it. A smaller alphabet-aware invariant may improve on ambient rank without reaching `kappa`. The exact values inherit the scope and assumptions of their parent proofs and referees. Product amplification requires additive semantics and no cross-component move. Support is not gate count, depth, runtime, qubit count, noise performance, or physical advantage.

No larger search under the old capped Round-3 identity is authorized, and the separate source-completeness programme contributes no outcome to this paper.

## 13. Conclusion

Intrinsic optimal support and a proof system's certifiable support budget answer different questions. Soundness gives `kappa<=beta`; equality requires an independent compiler lower witness, while strict inequality diagnoses a limitation of the proof language. R6M supplies the bounded equality control and R6I supplies a strict same-objective separation.

The result is deliberately narrow. It does not promote ambient rank into compiler complexity or one proof-system gap into a universal lower bound. It provides an exact vocabulary for saying what a compiler needs, what a proof language can certify, and when those two quantities diverge.

---

## Editorial production note — not manuscript prose

This master should be adopted as a separate Paper B rather than folded into the alphabet-sensitive MultiTag normal-form paper. Before filing, reconcile every `kappa` and `beta` statement with `theory-B-MANUSCRIPT_V3.md`, the parent evidence hashes and `proof_checker_v3.py`; refresh proof-system/zero-sum/compiler-normal-form literature; and rebuild the target source, figures, bibliography, PDF, manifest and archive. Preserve the capped production-completeness `CANNOT_CHECK` terminal.
