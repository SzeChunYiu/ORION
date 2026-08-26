# Integrated AB R9 Addendum: A Realized 5-to-1 Certificate Gap in an Explicit XOR Production Grammar

## Scope

This addendum closes the production-realization gate for one deliberately explicit grammar. It does not claim equivalence to a full TARE compiler, a hardware resource model, or the dependent-triple Pauli case study.

The grammar consists of finite multisets of nonzero vectors in `F_2^5` whose total XOR is nonzero. Semantics is the total XOR, support and objective are multiset cardinality, and the complete production language is frozen to two universally quantified move schemas:

1. delete any nonempty proper zero-XOR submultiset;
2. fuse any two distinct letters into their XOR.

There is no hidden auxiliary state or additional move family.

## Exact weak certificate complexity

The weak proof language contains only zero-XOR deletion. Its terminal complexity is five. The standard basis word

`[1,2,4,8,16]`

is a realized production state of support five, has total XOR 31, and contains no nonempty zero-XOR submultiset. The usual finite-vector-space deletion theorem gives the matching upper bound.

## Exact intrinsic production support

Under the complete production language, every admissible state of support greater than one has a reducing move:

- an equal pair is a zero-XOR deletion;
- otherwise a distinct pair can be fused to its nonzero XOR.

Every move preserves the total XOR and strictly decreases support. Repetition reaches the unique singleton containing the original nonzero total. Support zero is infeasible. The intrinsic production support is therefore exactly one.

Consequently, on this same frozen state space, semantics, support functional, and objective,

`weak certificate complexity = 5`,

`intrinsic production support = 1`,

and certificate waste is four.

## Complete interaction audit

The move-interaction graph has three critical schema classes: deletion/deletion, deletion/fusion, and fusion/fusion. Every successor preserves the same nonzero total XOR, and every successor reduces to the singleton carrying that total. Thus all critical peaks join at a unique normal form.

A separate executable audit exhaustively checks every admissible multiset through length `d+1` in dimensions two, three, and four. It covers 14,830 states, 100,310 moves, and 344,526 local peaks with zero invariant or joinability mismatches. These bounded controls corroborate, but do not replace, the symbolic all-dimension argument.

## Direct-enumerator consequence

For a direct support enumerator over `n` coordinates and 31 local nonidentity labels, replacing cap five by cap one changes the exact candidate volume from

`sum_{j=0}^5 binom(n,j)31^j`

to

`1+31n`.

This is an exact architecture-specific volume statement and exhibits the predicted fourth-degree certificate waste. It is not a lower bound on all algorithms and does not by itself establish wall-time value in a production compiler.

## Authority boundary

The internal realization and complete-defined-move gates are closed for the XOR grammar. Remaining journal-significance gates are:

- current nearest-work and novelty review;
- structurally independent replay of the registries and terminality proof;
- evidence that the abstraction-boundary result matters beyond this intentionally clean grammar; and
- a production-derived search panel or a narrower theory venue decision.

The Pauli case studies remain separately scoped until their own move registries and realization maps pass the same audit.
