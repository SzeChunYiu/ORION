# QG-6 hostile novelty / donor-threat freeze — 2026-08-21

Status: FROZEN BEFORE QG-6 MACHINE OUTCOME.
Issue: #756
Literature cutoff: 2026-08-21.
Authority: novelty threat register only; absence of a close parent is not novelty authority.

## Candidate residual

The only candidate contribution under test is:

> From an exact quantum compiler's production transition semantics, automatically infer the minimum/relevant linear conserved-syndrome quotient for a proposed semantics-preserving deletion rewrite; combine that inferred dimension with an independently certified non-increasing rewrite to obtain a finite-support optimal normal form and bounded exact-search support space.

The elementary linear dependence theorem and every underlying Pauli/symplectic fact receive zero novelty credit.

## Mandatory absorbed parents

### Sparse-support / Carathéodory mathematics

Carathéodory-type support bounds are classical. Recent dyadic/integer programming literature explicitly studies bounds on support size of feasible/optimal solutions and uses dimension/pigeonhole arguments. QG-6 must not claim novelty for `dimension -> sparse representative` as abstract mathematics.

Representative donor:
- *Dyadic linear programming and extensions*, Mathematical Programming (2024/2025 online record), section on bounding support size of dyadic solutions.

Disposition: **ABSORB ABSTRACT SUPPORT-SPARSIFICATION PRINCIPLE**.

### Fixed-parameter compilation complexity

Quantum circuit mapping has already been studied under fixed parameters, including hardness/tractability changes when architecture/qubit/depth parameters are fixed.

Representative donor:
- Zhu et al., *The Complexity of Quantum Circuit Mapping with Fixed Parameters*, arXiv:2207.08438.

Disposition: **ABSORB FIXED-PARAMETER COMPLEXITY AS GENERAL METHODOLOGY**. QG-6's `O(n^d A^d)` corollary is not novel merely because it is parameterized.

### Pauli/symplectic compiler representations

Pauli-based and binary-symplectic compiler representations are established:
- PCOAST, arXiv:2305.10966;
- Reid, *A simple method for compiling quantum stabilizer circuits*, arXiv:2404.19408;
- Symphony / PHOENIX++, *Efficient Compilation for Hamiltonian Simulation via Global Binary Symplectic Form Simplification*, arXiv:2608.11579 (2026-08-12).

Disposition: **ABSORB PAULI/BINARY-SYMPLECTIC REPRESENTATION AND GLOBAL ALGEBRAIC SIMPLIFICATION**. QG-6 cannot claim novelty for representing compiler constraints over `F_2` or using symplectic tableaux.

### Stabilizer/QEC syndrome mathematics

Quantum-error-correction literature routinely represents Pauli syndromes as linear maps over binary symplectic vector spaces.

Disposition: **ABSORB LINEAR SYNDROME FORMALISM**.

## Search result

Current hostile search has **not found a close parent** that does all of the following as one quantum-compilation theorem pipeline:

1. start from a production exact compiler/DP transition signature;
2. infer the rank of the rewrite-relevant conserved state quotient rather than hand-declare it;
3. bind that quotient to a concrete semantics-preserving local compiler rewrite;
4. bind a local/nonlocal cost certificate proving zero-sum deletion non-increasing;
5. conclude a finite-support optimal normal form for that compilation family;
6. carry the inferred quotient/bound as a machine-checkable receipt that can be transferred only with an explicit correspondence witness.

This is a **candidate residual**, not a novelty verdict.

## Strong hostile falsifiers

QG-6 novelty collapses or narrows if any source is found that already provides, for materially comparable Pauli/symplectic compilation:

- automatic rank inference of a conserved rewrite quotient with an optimal-support theorem;
- a compiler-normal-form theorem whose support bound is exactly the rank/dimension of a production syndrome state and whose rewrite/cost obligations match QG-6;
- a general theorem that directly subsumes both the R6M and R6I instantiations without ORION-specific scientific residue.

A source that merely uses a binary tableau, dynamic programming, or fixed-parameter analysis does **not** by itself subsume the QG-6 object.

## Current terminal boundary

Allowed current language:

`NO_CLOSE_PARENT_FOUND_FOR_PRODUCTION_SYNDROME_QUOTIENT_TO_FINITE_SUPPORT_COMPILER_THEOREM_PIPELINE__NOVELTY_NOT_AUTHORIZED`

Forbidden without independent review:

- `NOVEL`;
- `FIRST`;
- `NEW_FIELD_ESTABLISHED`;
- any claim that Carathéodory/linear dependence/fixed-parameter complexity is an ORION invention.
