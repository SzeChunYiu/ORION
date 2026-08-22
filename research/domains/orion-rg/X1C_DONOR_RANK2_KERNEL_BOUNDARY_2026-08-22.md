# X1-C donor absorption — 2009 inductive method already handles rank-2 lift kernels

Parent: #901. Committed before downstream use.

## Donor

Bhowmik, Halupczok and Schlage-Puchta, *Inductive Methods and Zero-Sum Free Sequences* (Integers 9, 2009).

## Relevant theorem/mechanism

Their Theorem 5 treats groups of the form

`C_3 ⊕ C_(3n)^2`

under a Property-B hypothesis on n (with n coprime to 6), and proves the expected Davenport value. The proof projects to `C_3^3` and retains a **rank-2 kernel/lift state** in `C_n^2`.

The exact proof architecture is strikingly close to X1-C:

1. project the hypothetical counterexample to `C_3^3`;
2. greedily remove zero-sums of length <=3 until the residual has fewer than 17 points;
3. store the lifted sums of removed quotient zero-sums in a zero-sum-free sequence `B` over `C_n^2`;
4. analyze residual sizes 16, 13 and 10;
5. ask whether residual quotient zero-sums can supply correction values that extend B without preserving zero-sum-freeness;
6. use inverse structure of near-maximal/maximal zero-sum-free sequences in the rank-2 kernel (Property B and explicit lemmas);
7. for the 13-point case, enumerate the quotient residuals and reduce lift compatibility to a graph-homomorphism / linear-equation obstruction, verified computationally.

Their Lemma 16 is a computer-verified 13-point compatibility obstruction for a multiset in `C_3^3` with no short zero-sum and no three disjoint zero-sums, together with a multi-function into `C_n^2`.

## Consequence for ORION-RG novelty boundary

The following are donor-owned and cannot be claimed as ORION-RG novelties:

- greedy reduction to residual sizes 16/13/10;
- keeping lifted block sums rather than only block counts;
- treating residual zero-sums as correction values into a kernel sequence;
- using inverse structure of near-maximal kernel zero-sum-free sequences;
- finite residual enumeration plus graph/constraint compatibility checking;
- the general idea of lifting the 2007 scalar method to a vector-valued kernel.

## Exact remaining gap

For C45, projection to `C_3^3` has kernel

`K=C_15^3`,

which has rank 3 and mixed exponent. The 2009 donor machinery stops one kernel dimension lower (`C_n^2`). Current inverse structure of maximal zero-sum-free sequences is substantially weaker in this rank-3 mixed kernel.

Thus the live residual is not “invent typed lifting.” It is:

> obtain a new rank-3 mixed-kernel inverse/compatibility theorem strong enough to replace the rank-2 Property-B/near-maximal structure used by the 2009 induction.

Any eventual C45 proof should explicitly recover the 2009 rank-2 method as donor precedent and identify the new rank-3 lemma that makes the extension possible.

## Next hostile check

Before committing to the rank-3 inverse route, test the reverse primary projection

`C_45^3 -> C_15^3`

with kernel `C_3^3`. A sufficiently strong known or newly cheap bound on `D_7(C_15^3)` could prove C45 directly and would supersede the more elaborate compatibility programme.

## Claim boundary

This file is donor subtraction only. It grants no novelty or theorem authority.
